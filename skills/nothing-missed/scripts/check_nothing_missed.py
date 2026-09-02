"""Stop-Hook des Plugins nothing-missed: kein Dokument ohne Abnahme.

Läuft nach jeder fertigen Antwort. Wurde in diesem Zug ein Dokument
geschrieben (eine Markdown-, Text- oder HTML-Datei über die Schreibwerkzeuge),
etwas übergeben (ein Artefakt veröffentlicht, eine Datei geschickt -- egal
welcher Art) oder liefert der Zug selbst ein langes, gegliedertes Dokument im
Chat, dann muss
irgendwo im Zug die Eingangsliste mit Fundstellen stehen -- sonst wird die
Antwort abgelehnt und die Sitzung muss die Abnahme nachreichen.

Geprüft wird der GANZE Zug (alle Assistententexte seit der letzten echten
Nutzereingabe), nicht nur die letzte Nachricht: ein Dokument steht oft in
einer früheren Nachricht desselben Zuges, gefolgt von einem kurzen Nachtrag.
Als Gliederung zählen Markdown-Überschriften und fett gesetzte Titelzeilen.

Der Hook prüft Form, nicht Vollständigkeit: ob die Eingangsliste wirklich
alles Besprochene enthält, kann nur ein Leser beurteilen.

Er fällt in jeder Zweifelslage OFFEN aus (Antwort passiert): fehlendes Python,
unlesbare Eingabe, ein Protokollformat, das er nicht versteht -- alles Exit 0.
Schleifenschutz: meldet die Eingabe stop_hook_active, wird nie erneut geblockt.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

SCHREIBWERKZEUGE = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
DOKUMENT_ENDUNGEN = (".md", ".rst", ".txt", ".adoc", ".html", ".htm")

# Werkzeuge, deren Aufruf eine Übergabe IST -- unabhängig von der Endung
# (die Frage ist nicht "welche Endung", sondern "übergibst du gerade
# etwas"). Eine HTML-Seite ist ein Dokument wie jedes andere. Artifact zählt
# nur beim Veröffentlichen; lesen, auflisten und kommentieren nicht.
UEBERGABEWERKZEUGE = {"SendUserFile"}
_ARTIFACT = "Artifact"

# Ein Chat-Dokument: lang und gegliedert. Die Schwellen sind bewusst hoch,
# damit gewöhnliche lange Antworten nicht getroffen werden.
MINDESTLAENGE = 3000
MINDEST_ABSCHNITTE = 4

# Eine Titelzeile: Markdown-Überschrift oder eine Zeile, die nur aus fett
# gesetztem Text besteht (so setzen Modelle Kapiteltitel, wenn sie keine
# #-Überschriften verwenden).
_TITELZEILE = re.compile(r"^(#{1,4}\s+\S|\*\*[^*\n]{2,120}\*\*:?\s*$)")

PFLICHTWOERTER = ("eingangsliste", "fundstelle")

# Der sprachfreie Weg (dieselbe Bauidee wie der QC-Belegblock von
# source-required): feste Token statt deutscher Vokabeln. Eine Abnahme in
# beliebiger Sprache traegt die Zeilenmarken INTAKE: (je Position der
# Eingangsliste) und REF: (die Fundstelle dazu). Beide muessen vorkommen,
# mit Doppelpunkt; die Schreibung ist frei (Review-Befund: "Intake:" ist
# dieselbe Abnahme wie "INTAKE:", eine Blockade dafuer waere Schikane).
_INTAKE_TOKEN = re.compile(r"\bINTAKE:", re.IGNORECASE)
_REF_TOKEN = re.compile(r"\bREF:", re.IGNORECASE)

BLOCKGRUND = (
    "[nothing-missed] In diesem Zug wurde ein Dokument übergeben, aber nirgends "
    "im Zug steht die Abnahme. Vor der Übergabe gehört die Eingangsliste in die "
    "Antwort: jede Forderung aus dem Gespräch als nummerierte Position, und zu "
    "jeder Position die Fundstelle im Dokument. Eine Position ohne Fundstelle "
    "ist ein roter Befund. In jeder Sprache gelten die Token INTAKE: (Position) "
    "und REF: (Fundstelle) als Abnahme. Liste nachreichen, dann erneut "
    "abschließen."
)


# Obergrenze fuer das Einlesen des Gespraechsprotokolls: bei einem groesseren
# Protokoll wird nur das Ende gelesen -- der aktuelle Zug steht dort. Ohne
# Grenze koennte ein Riesenprotokoll den Hook am Speicher aufhaengen
# (Review-Befund). Eine angeschnittene erste Zeile faellt beim JSON-Parsen raus.
_LESEGRENZE = 8_000_000


def _protokollende(protokollpfad: Path, grenze: int = _LESEGRENZE) -> str:
    """Return at most the last `grenze` bytes of the transcript as text."""
    with protokollpfad.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        handle.seek(max(0, handle.tell() - grenze))
        return handle.read().decode("utf-8", errors="replace")


def _eintraege(protokollpfad: Path) -> list[dict[str, object]]:
    """Return the parsed transcript entries, oldest first; empty on any problem."""
    try:
        zeilen = _protokollende(protokollpfad).splitlines()
    except (OSError, ValueError):
        return []
    eintraege: list[dict[str, object]] = []
    for roh in zeilen:
        try:
            eintrag = json.loads(roh)
        except json.JSONDecodeError:
            continue
        if isinstance(eintrag, dict):
            eintraege.append(eintrag)
    return eintraege


def _ist_echte_nutzereingabe(inhalt: object) -> bool:
    """Return True for a typed user message (not a relayed tool result)."""
    if isinstance(inhalt, str):
        return bool(inhalt.strip())
    if isinstance(inhalt, list):
        return any(isinstance(block, dict) and block.get("type") == "text" for block in inhalt)
    return False


def _schreibt_dokument(eingabe: object) -> bool:
    """Return True when a tool input names a document file path."""
    if not isinstance(eingabe, dict):
        return False
    pfad = eingabe.get("file_path")
    return isinstance(pfad, str) and pfad.lower().endswith(DOKUMENT_ENDUNGEN)


def _uebergibt(name: object, eingabe: object) -> bool:
    """Return True when a tool call hands something to the user, whatever its type."""
    if name in UEBERGABEWERKZEUGE:
        return True
    if name == _ARTIFACT:
        aktion = eingabe.get("action") if isinstance(eingabe, dict) else None
        return aktion in (None, "", "publish")
    return False


def zug_auswerten(protokollpfad: Path) -> tuple[str, bool]:
    """Return (all assistant text of the current turn, was a document written).

    The current turn is everything after the last real user message. Any parse
    problem yields ("", False) -- the guard fails open.
    """
    texte: list[str] = []
    geschrieben = False
    for eintrag in _eintraege(protokollpfad):
        nachricht = eintrag.get("message")
        if not isinstance(nachricht, dict):
            continue
        inhalt = nachricht.get("content")
        if nachricht.get("role") == "user" and _ist_echte_nutzereingabe(inhalt):
            texte = []
            geschrieben = False
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
            elif block.get("type") == "tool_use" and (
                (block.get("name") in SCHREIBWERKZEUGE and _schreibt_dokument(block.get("input")))
                or _uebergibt(block.get("name"), block.get("input"))
            ):
                geschrieben = True
    return "\n\n".join(teil for teil in texte if teil), geschrieben


def chat_dokument(text: str) -> bool:
    """Return True when the turn text is a long, sectioned document."""
    if len(text) < MINDESTLAENGE:
        return False
    abschnitte = sum(1 for zeile in text.splitlines() if _TITELZEILE.match(zeile.strip()))
    return abschnitte >= MINDEST_ABSCHNITTE


def abnahme_fehlt(text: str) -> bool:
    """Return True when the turn text lacks the input list with locations."""
    klein = text.lower()
    if all(wort in klein for wort in PFLICHTWOERTER):
        return False
    return not (_INTAKE_TOKEN.search(text) and _REF_TOKEN.search(text))


def protokolliere_blockade(grund: str, sitzung: object) -> None:
    """Append the block to the plugin's JSONL log; never raise, never block."""
    try:
        basis = os.environ.get("CLAUDE_PLUGIN_DATA")
        verzeichnis = Path(basis) if basis else Path.home() / ".claude" / "plugin-data" / "nothing-missed"
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
            zugtext, geschrieben = zug_auswerten(Path(protokoll))
        else:
            zugtext, geschrieben = "", False
        if not zugtext and isinstance(letzte, str):
            zugtext = letzte
        if not zugtext:
            return 0
        if (geschrieben or chat_dokument(zugtext)) and abnahme_fehlt(zugtext):
            protokolliere_blockade(BLOCKGRUND, nutzlast.get("session_id"))
            print(BLOCKGRUND, file=sys.stderr)
            return 2
    except Exception:  # noqa: BLE001 -- der Wächter fällt grundsätzlich offen aus
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
