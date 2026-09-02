"""Stop-Hook des Plugins show-your-work: kein Nachweis ohne Gegenstand.

Läuft nach jeder fertigen Antwort. Wurde in diesem Zug etwas ÜBERGEBEN -- ein
Artefakt veröffentlicht, eine Datei an den Nutzer geschickt, ein Zweig
gepusht, ein Pull Request eröffnet oder gemergt -- dann muss irgendwo im Zug
der Lieferblock stehen: welcher Gegenstand übergeben wird, welche Prüfung an
GENAU DIESEM Gegenstand lief und was sie auf ihrer ganzen Skala gemeldet hat.
Fehlt der Block oder ist er lückenhaft, wird die Antwort abgelehnt und die
Sitzung muss den Nachweis nachreichen.

Warum: ein Assistent sagt "geprüft" mit derselben Sicherheit, ob die Prüfung an
dem lief, was vor dem Leser liegt, oder an einer älteren Fassung; und "in
Ordnung" klingt gleich, ob alle Stufen gemeint sind oder nur die schlimmste.
Ein Prüfbericht ohne Kennzeichen und ohne Prüfpunkte ist kein Prüfbericht.

Der Lieferblock ist sprachfrei, feste Token wie beim QC-Block::

    [SHIPPED]
    OBJECT: posts/0091.md @ 4914da3 | branch skill-seiten-vorlage
    CHECK: gate register, 47 gates | ON: SAME | RESULT: 0 blocking red, 9 watching | SCALE: blocking, watching
    CHECK: pytest tools/ | ON: SAME | RESULT: 1381 passed, 0 failed | SCALE: passed, failed
    [/SHIPPED]

Pflichtfelder: genau eine OBJECT-Zeile; mindestens eine CHECK-Zeile; jede
CHECK-Zeile trägt ON (entweder das Token SAME oder wörtlich den OBJECT-Text),
RESULT und SCALE. SCALE nennt jede Stufe, die die Prüfung kennt -- wer nur
"errors" nennt, wo die Prüfung auch "warnings" kennt, hat die Skala verengt.
Der Hook prüft, dass SCALE mindestens zwei Stufen nennt (Komma-getrennt).

Der Hook prüft Form, nicht Wahrheit: ob die Prüfung wirklich an diesem
Gegenstand lief, kann nur ein Leser mit Zugriff nachvollziehen. Aber die
Form zwingt der Assistent, Gegenstand und Skala hinzuschreiben -- und ein
hingeschriebener falscher Gegenstand ist eine sichtbare Lüge, kein Versehen.

Er fällt in jeder Zweifelslage OFFEN aus (Antwort passiert): fehlendes
Python, unlesbare Eingabe, ein Protokollformat, das er nicht versteht --
alles Exit 0. Schleifenschutz: meldet die Eingabe stop_hook_active, wird nie
erneut geblockt.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

# Werkzeuge, deren Aufruf eine Übergabe IST -- unabhängig von Endung oder Inhalt.
UEBERGABEWERKZEUGE = {
    "SendUserFile",
    "mcp__github__create_pull_request",
    "mcp__github__merge_pull_request",
    "mcp__github__push_files",
    "mcp__github__create_or_update_file",
}
# Artifact übergibt nur beim Veröffentlichen (kein action oder action=publish);
# lesen, auflisten und kommentieren sind keine Übergabe.
_ARTIFACT = "Artifact"
# Ein Push zaehlt nur als Befehl, nicht als Text: erst fallen Heredocs und
# Anfuehrungszeichen weg, dann muss "git push" am Anfang eines Befehlsglieds
# stehen. Ein Testskript, das den String "git push" nur als Eingabe traegt,
# ist keine Uebergabe.
_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?\n.*?\n\1\b", re.DOTALL)
_ZITAT = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"")
_GIT_PUSH = re.compile(r"(?:^|[;&|(]\s*|\n\s*)git\s+push\b")

_SHIPPED_BLOCK = re.compile(r"\[SHIPPED\](.*?)\[/SHIPPED\]", re.DOTALL | re.IGNORECASE)
_SAME = "SAME"

BLOCKGRUND = (
    "[show-your-work] In diesem Zug wurde etwas übergeben (Artefakt, Datei, Push oder "
    "Pull Request), aber nirgends im Zug steht der Lieferblock. Vor der Übergabe gehört in die "
    "Antwort: [SHIPPED] OBJECT: <der Gegenstand, der übergeben wird: Pfad, Adresse, Commit> "
    "und je Prüfung CHECK: <Prüfung> | ON: SAME | RESULT: <Ergebnis> | SCALE: <jede Stufe, "
    "die die Prüfung kennt, Komma-getrennt> [/SHIPPED]. Ein Nachweis ohne Gegenstand ist "
    "ein Satz über etwas anderes; eine Skala mit einer Stufe ist die halbe Skala. Block "
    "nachreichen, dann erneut abschließen."
)

_LESEGRENZE = 8_000_000


def _protokollende(protokollpfad: Path, grenze: int = _LESEGRENZE) -> str:
    """Return the last `grenze` bytes of the transcript, decoded leniently."""
    with protokollpfad.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        handle.seek(max(0, handle.tell() - grenze))
        return handle.read().decode("utf-8", errors="replace")


def _eintraege(protokollpfad: Path) -> list[dict[str, object]]:
    aus: list[dict[str, object]] = []
    for zeile in _protokollende(protokollpfad).splitlines():
        zeile = zeile.strip()
        if not zeile:
            continue
        try:
            eintrag = json.loads(zeile)
        except json.JSONDecodeError:
            continue
        if isinstance(eintrag, dict):
            aus.append(eintrag)
    return aus


def _ist_echte_nutzereingabe(inhalt: object) -> bool:
    if isinstance(inhalt, str):
        return bool(inhalt.strip())
    if isinstance(inhalt, list):
        return any(isinstance(block, dict) and block.get("type") == "text" for block in inhalt)
    return False


def ist_uebergabe(name: object, eingabe: object) -> bool:
    """Return True when this tool call hands something to the user or the world."""
    if name in UEBERGABEWERKZEUGE:
        return True
    if name == _ARTIFACT:
        aktion = eingabe.get("action") if isinstance(eingabe, dict) else None
        return aktion in (None, "", "publish")
    if name == "Bash" and isinstance(eingabe, dict):
        befehl = eingabe.get("command")
        return isinstance(befehl, str) and ist_push_befehl(befehl)
    return False


def ist_push_befehl(befehl: str) -> bool:
    """Return True when the shell text RUNS git push, not when it merely mentions it."""
    bereinigt = _ZITAT.sub("", _HEREDOC.sub("", befehl))
    return bool(_GIT_PUSH.search(bereinigt))


def zug_auswerten(protokollpfad: Path) -> tuple[str, bool]:
    """Return (all assistant text of the current turn, was something handed over)."""
    texte: list[str] = []
    uebergeben = False
    for eintrag in _eintraege(protokollpfad):
        nachricht = eintrag.get("message")
        if not isinstance(nachricht, dict):
            continue
        inhalt = nachricht.get("content")
        if nachricht.get("role") == "user" and _ist_echte_nutzereingabe(inhalt):
            texte = []
            uebergeben = False
            continue
        if nachricht.get("role") != "assistant":
            continue
        if isinstance(inhalt, str):
            texte.append(inhalt)
            continue
        if not isinstance(inhalt, list):
            continue
        for block in inhalt:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                texte.append(str(block.get("text", "")))
            elif block.get("type") == "tool_use" and ist_uebergabe(block.get("name"), block.get("input")):
                uebergeben = True
    return "\n\n".join(teil for teil in texte if teil), uebergeben


def _felder(zeile: str) -> dict[str, str]:
    """Split 'KEY: value | KEY: value' into a dict; keys upper-cased."""
    aus: dict[str, str] = {}
    for teil in zeile.split("|"):
        if ":" not in teil:
            continue
        schluessel, wert = teil.split(":", 1)
        aus[schluessel.strip().upper()] = wert.strip()
    return aus


def block_pruefen(text: str) -> str | None:
    """Return None when a complete [SHIPPED] block exists; else the reason."""
    bloecke = _SHIPPED_BLOCK.findall(text)
    if not bloecke:
        return BLOCKGRUND
    fehler: list[str] = []
    for block in bloecke:
        objekt: str | None = None
        checks = 0
        for roh in block.splitlines():
            zeile = roh.strip()
            if not zeile:
                continue
            felder = _felder(zeile)
            if "OBJECT" in felder and not zeile.upper().startswith("CHECK"):
                if objekt is not None:
                    fehler.append("mehr als eine OBJECT-Zeile; ein Lieferblock nennt genau einen Gegenstand")
                objekt = felder["OBJECT"]
                if not objekt:
                    fehler.append("OBJECT ist leer")
                continue
            if zeile.upper().startswith("CHECK"):
                checks += 1
                if objekt is None:
                    fehler.append("CHECK vor OBJECT; erst der Gegenstand, dann die Prüfung daran")
                on = felder.get("ON", "")
                if not on:
                    fehler.append(f"CHECK ohne ON: {zeile[:80]}")
                elif on.upper() != _SAME and (objekt is None or on != objekt):
                    fehler.append(f"ON nennt einen anderen Gegenstand als OBJECT: {on[:80]}")
                if not felder.get("RESULT"):
                    fehler.append(f"CHECK ohne RESULT: {zeile[:80]}")
                stufen = [s.strip() for s in felder.get("SCALE", "").split(",") if s.strip()]
                if len(stufen) < 2:
                    fehler.append(f"SCALE nennt weniger als zwei Stufen: {zeile[:80]}")
        if objekt is None:
            fehler.append("Lieferblock ohne OBJECT-Zeile")
        if checks == 0:
            fehler.append("Lieferblock ohne CHECK-Zeile")
    if not fehler:
        return None
    return (
        "[show-your-work] Lieferblock lückenhaft: "
        + "; ".join(fehler[:6])
        + ". Block vervollständigen, dann erneut abschließen."
    )


def protokolliere_blockade(grund: str, sitzung: object) -> None:
    """Append the block to the plugin's JSONL log; never raise, never block."""
    try:
        basis = os.environ.get("CLAUDE_PLUGIN_DATA")
        verzeichnis = Path(basis) if basis else Path.home() / ".claude" / "plugin-data" / "show-your-work"
        verzeichnis.mkdir(parents=True, exist_ok=True)
        eintrag = {
            "zeit": datetime.now(UTC).isoformat(timespec="seconds"),
            "sitzung": sitzung if isinstance(sitzung, str) else "",
            "ereignis": "block",
            "grund": grund,
        }
        with (verzeichnis / "blockprotokoll.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001 -- das Protokoll ist Beigabe, nie Blocker
        return


def main() -> int:
    """Read the Stop-hook payload from stdin and allow or block the reply."""
    try:
        nutzlast = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError, OSError):
        return 0
    if not isinstance(nutzlast, dict) or nutzlast.get("stop_hook_active"):
        return 0

    protokoll = nutzlast.get("transcript_path")
    letzte = nutzlast.get("last_assistant_message")
    try:
        if isinstance(protokoll, str):
            zugtext, uebergeben = zug_auswerten(Path(protokoll))
        else:
            zugtext, uebergeben = "", False
        if not zugtext and isinstance(letzte, str):
            zugtext = letzte
        if not uebergeben:
            return 0
        grund = block_pruefen(zugtext)
    except Exception:  # noqa: BLE001 -- der Wächter fällt grundsätzlich offen aus
        return 0
    if grund is None:
        return 0
    protokolliere_blockade(grund, nutzlast.get("session_id"))
    print(grund, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
