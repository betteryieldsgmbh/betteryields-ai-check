"""Stop-Hook des Plugins source-required: keine Zahl ohne ihre Marke.

Läuft nach jeder fertigen Antwort. Steht im Antworttext eine Ziffer in Prosa,
ohne dass irgendwo eine der drei Marken (gemessen / Urteil / ungeprüft) steht,
wird die Antwort abgelehnt und die Sitzung muss die Marken nachtragen. Nennt
eine gemessen-Marke einen relativen Dateipfad als Quelle, wird zusätzlich
geprüft, ob der Pfad im Arbeitsverzeichnis existiert -- die richtige Zahl mit
erfundener Herkunft ist die gefährlichste Form.

Der Hook prüft Form, nicht Wahrheit: ob der Wert aus der Quelle korrekt
abgelesen wurde, kann ein lokales Skript nicht wissen.

Er fällt in jeder Zweifelslage OFFEN aus (Antwort passiert), denn ein Wächter,
der bei eigenem Versagen alles blockiert, legt jede Sitzung still: fehlendes
Python, unlesbare Eingabe, unbekanntes Protokollformat -- alles Exit 0.
Schleifenschutz: meldet die Eingabe stop_hook_active, wird nie erneut geblockt.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

MARKEN = ("gemessen", "urteil", "ungeprüft", "ungeprueft")

# Prosa ohne Code: gezäunte Blöcke und Backtick-Spannen tragen legitim nackte
# Ziffern (Versionsnummern, Befehle) und werden vor der Prüfung entfernt.
_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]*`")
# Kurze Spannen in Anfuehrungszeichen sind Zitate, keine eigenen Behauptungen --
# wer die Auslesewoerter des Waechters NENNT, soll nicht von ihm geblockt werden.
_ZITAT = re.compile(r'"[^"\n]{1,80}"')

# Ein relativer Pfad mit Dateiendung in einer gemessen-Klammer, z. B.
# "gemessen (docs/bericht.md, Zeile 12)". Absolute Pfade und URLs bleiben
# ungeprüft: sie können auf fremde Rechner oder das Netz zeigen. Der
# Rueckblick schliesst auch den Bindestrich aus, sonst wird aus dem absoluten
# "/pfad/zum/projekt/x.py" das scheinbar relative
# "quality-control/x.py" herausgelesen.
_GEMESSEN_KLAMMER = re.compile(r"gemessen\s*\(([^)]{1,300})\)", re.IGNORECASE)
_RELATIVER_PFAD = re.compile(r"(?<![\w/-])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]{1,8})")

# Eine Abwesenheits-Behauptung ("X existiert nicht", "nicht installierbar")
# ist nur so gut wie ihr Suchraum. Ohne die Angabe, WAS durchsucht wurde,
# ist sie eine Vermutung im Tatsachenkleid -- die Fehlerklasse, aus der
# dieser Skill entstand: aus "ich habe X nicht gefunden" wird "X gibt es
# nicht". Die Muster sind bewusst eng, damit Alltagssaetze ("keine
# Blockade protokolliert") nicht anschlagen.
_ABWESENHEIT = re.compile(
    r"(existiert nicht\b|existieren nicht\b|gibt es nicht\b|gibt es keine[nrs]?\b"
    r"|nicht installierbar|auf keinem (branch|zweig|stand)"
    r"|in keinem (repo|repository|ordner|verzeichnis)|nirgends vorhanden)",
    re.IGNORECASE,
)
_SUCHRAUM = re.compile(r"durchsucht|suchraum|gepr\u00fcfte orte", re.IGNORECASE)

# "Kann ich nicht" ist eine Behauptung, keine Tatsache -- sie gilt erst mit
# benannten Versuchen samt Fehlermeldung. Und ein Arbeitsschritt, der an den
# Nutzer weitergereicht wird, braucht denselben Nachweis: erst selbst
# versuchen, dann weiterreichen. Beides sind die Wiederholungsfehler, aus
# denen dieser Skill entstand.
_VERWEIGERUNG = re.compile(
    r"(kann ich nicht|geht nicht|ist nicht m\u00f6glich|habe keinen zugriff"
    r"|keine berechtigung daf\u00fcr|nicht in der lage)",
    re.IGNORECASE,
)
_ABWAELZEN = re.compile(
    r"(bitte f\u00fchre|f\u00fchre bitte|musst du selbst|musst du selber"
    r"|mach du das|kannst du bitte .{0,40}(ausf\u00fchren|starten|klicken|pushen|anlegen))",
    re.IGNORECASE,
)
# Uebergabe: eine Ausroll-Meldung haendigt einen Zugangspunkt aus. Sie gilt
# erst mit dem Klickweg-Nachweis ("geprueft: <Adresse> zeigt <was>") -- die
# Sitzung muss die Adresse selbst beschritten haben, bevor der Nutzer sie
# bekommt. Und ein ABGEKUERZTER Zugangspunkt (eine Adresse oder ein Pfad mit
# Auslassungspunkten) ist gar keiner: nicht klickbar, nicht kopierbar.
_AUSROLLUNG = re.compile(
    r"(ausgerollt|deployt|deployed|erreichbar unter|l\u00e4uft unter|aufrufbar unter)",
    re.IGNORECASE,
)
_KLICKNACHWEIS = re.compile(r"gepr\u00fcft:", re.IGNORECASE)
_VERSUCH = re.compile(
    r"(versucht:|versucht habe ich|fehlgeschlagen|fehlermeldung|exit-?code|abgewiesen mit)",
    re.IGNORECASE,
)

# Der sprachfreie Belegblock: eine winzige Kunstsprache aus festen Token,
# die in jeder Menschensprache gleich aussieht (dieselbe Bauidee wie die
# PUNKT:/ZITAT:-Zeilen des Checkers). Die Prosa darf Deutsch, Englisch oder
# Franzoesisch sein -- geprueft wird nur die Struktur des Blocks. In
# deutscher Prosa genuegen weiterhin die klassischen Marken; der Block ist
# der Weg fuer alle anderen Sprachen und wird, wenn vorhanden, streng
# geprueft.
_QC_BLOCK = re.compile(r"\[QC\](.*?)\[/QC\]", re.DOTALL | re.IGNORECASE)
_QC_MARKEN = {"MEASURED", "JUDGEMENT", "UNVERIFIED"}
_QC_ZEILENARTEN = {"CLAIM", "DENIAL", "ABSENT", "HANDOFF", "DEPLOYED"}


def _qc_felder(zeile: str) -> tuple[str, dict[str, str]] | None:
    """Split one block line into its type and key/value fields."""
    kopf, _, rest = zeile.partition(":")
    art = kopf.strip().upper()
    if art not in _QC_ZEILENARTEN:
        return None
    felder = {"TEXT": ""}
    teile = rest.split("|")
    felder["TEXT"] = teile[0].strip()
    for teil in teile[1:]:
        schluessel, _, wert = teil.partition(":")
        felder[schluessel.strip().upper()] = wert.strip()
    return art, felder


def qc_pruefen(block: str, arbeitsverzeichnis: Path) -> tuple[list[str], int]:
    """Validate a QC block; return (findings, number of valid lines)."""
    fehler: list[str] = []
    gueltig = 0
    for roh in block.splitlines():
        zeile = roh.strip()
        if not zeile:
            continue
        geparst = _qc_felder(zeile)
        if geparst is None:
            fehler.append(f"unbekannte Zeile: {zeile[:60]}")
            continue
        art, felder = geparst
        if art == "CLAIM":
            marke = felder.get("MARK", "").upper()
            if marke not in _QC_MARKEN:
                fehler.append(f"CLAIM ohne gueltige MARK (MEASURED|JUDGEMENT|UNVERIFIED): {felder['TEXT'][:50]}")
                continue
            if marke == "MEASURED":
                quelle = felder.get("SRC", "")
                if not quelle:
                    fehler.append(f"MEASURED ohne SRC: {felder['TEXT'][:50]}")
                    continue
                tote = [
                    p
                    for p in _RELATIVER_PFAD.findall(quelle)
                    if ".." not in p.split("/") and not (arbeitsverzeichnis / p).exists()
                ]
                if tote:
                    fehler.append("SRC-Pfad loest nicht auf: " + ", ".join(tote))
                    continue
        elif art in {"DENIAL", "HANDOFF"} and not felder.get("TRIED"):
            fehler.append(f"{art} ohne TRIED: {felder['TEXT'][:50]}")
            continue
        elif art == "ABSENT" and not felder.get("SEARCHED"):
            fehler.append(f"ABSENT ohne SEARCHED: {felder['TEXT'][:50]}")
            continue
        elif art == "DEPLOYED" and not felder.get("VERIFIED"):
            fehler.append(f"DEPLOYED ohne VERIFIED: {felder['TEXT'][:50]}")
            continue
        gueltig += 1
    return fehler, gueltig


def prosa(text: str) -> str:
    """Return the reply text with code and short quotations removed."""
    return _ZITAT.sub(" ", _INLINE_CODE.sub(" ", _CODE_FENCE.sub(" ", text)))


def fehlende_pfade(text: str, arbeitsverzeichnis: Path) -> list[str]:
    """Return relative file paths named inside gemessen(...) that do not exist."""
    fehlend: list[str] = []
    for klammer in _GEMESSEN_KLAMMER.findall(text):
        for pfad in _RELATIVER_PFAD.findall(klammer):
            # Pfade mit ..-Stufen bleiben ungeprueft: der Waechter tastet nie
            # ausserhalb des Arbeitsverzeichnisses nach Dateien (Review-Befund).
            if ".." in pfad.split("/"):
                continue
            if not (arbeitsverzeichnis / pfad).exists():
                fehlend.append(pfad)
    return fehlend


def abgekuerzte_zugangspunkte(klartext: str) -> list[str]:
    """Return URL- or path-shaped tokens that carry ellipsis dots."""
    funde: list[str] = []
    for token in klartext.split():
        gekuerzt = "\u2026" in token or "..." in token
        adressefoermig = "://" in token or token.count("/") >= 2
        if gekuerzt and adressefoermig:
            funde.append(token.strip(".,;:()"))
    return funde


def befund(text: str, arbeitsverzeichnis: Path) -> str | None:
    """Return the block reason for a reply, or None when the reply may pass."""
    # Erst Code entfernen, DANN nach dem Belegblock suchen: wer das
    # Blockformat in Backticks oder einem Zaun nur ERWAEHNT, hat keinen
    # Block geschrieben und wird nicht an ihm gemessen.
    text = _INLINE_CODE.sub(" ", _CODE_FENCE.sub(" ", text))
    # ALLE Belegbloecke pruefen, nicht nur den ersten (Review-Befund): ein
    # lueckenhafter Block irgendwo in der Antwort lehnt sie ab, jeder gueltige
    # zaehlt, und alle werden vor den Prosa-Pruefungen entfernt.
    qc_gueltig = 0
    blockteile: list[str] = []
    for treffer in _QC_BLOCK.finditer(text):
        qc_fehler, anzahl = qc_pruefen(treffer.group(1), arbeitsverzeichnis)
        if qc_fehler:
            return (
                "[source-required] Der QC-Belegblock ist unvollstaendig: "
                + "; ".join(qc_fehler[:3])
                + ". Jede CLAIM-Zeile braucht MARK (MEASURED|JUDGEMENT|UNVERIFIED), "
                "MEASURED braucht SRC, DENIAL/HANDOFF brauchen TRIED, ABSENT "
                "braucht SEARCHED, DEPLOYED braucht VERIFIED."
            )
        qc_gueltig += anzahl
        blockteile.append(treffer.group(0))
    if blockteile:
        text = _QC_BLOCK.sub(" ", text)
    blocktext = " ".join(blockteile)
    klartext = prosa(text)
    gekuerzt = abgekuerzte_zugangspunkte(prosa(blocktext)) + abgekuerzte_zugangspunkte(klartext)
    if gekuerzt:
        return (
            "[source-required] Die Antwort haendigt einen ABGEKUERZTEN "
            "Zugangspunkt aus: " + ", ".join(gekuerzt[:3]) + ". Eine Adresse "
            "mit Auslassungspunkten ist keine Adresse -- nicht klickbar, nicht "
            "kopierbar. Die vollstaendige Adresse einsetzen."
        )
    if _AUSROLLUNG.search(klartext) and not _KLICKNACHWEIS.search(klartext):
        return (
            "[source-required] Die Antwort meldet ein Ausrollen oder haendigt "
            "einen Zugangspunkt aus, ohne den Klickweg-Nachweis. Erst selbst "
            "aufrufen, dann uebergeben: 'geprueft: <exakte Adresse> zeigt "
            "<was dort sichtbar ist>'."
        )
    if _VERWEIGERUNG.search(klartext) and not _VERSUCH.search(klartext):
        return (
            "[source-required] Die Antwort sagt 'geht nicht' oder 'kann ich "
            "nicht', nennt aber keinen Versuch. Eine Verneinung gilt erst mit "
            "benannten Versuchen samt Fehlermeldung ('versucht: ..., "
            "abgewiesen mit ...') -- sonst ist sie eine ungepruefte Vermutung."
        )
    if _ABWAELZEN.search(klartext) and not _VERSUCH.search(klartext):
        return (
            "[source-required] Die Antwort reicht einen Arbeitsschritt an den "
            "Nutzer weiter, ohne eigene Versuche zu nennen. Die Arbeit gehoert "
            "der Sitzung: erst selbst versuchen und die Versuche samt Fehlern "
            "benennen ('versucht: ...'), erst dann weiterreichen."
        )
    if _ABWESENHEIT.search(klartext) and not _SUCHRAUM.search(klartext):
        return (
            "[source-required] Die Antwort behauptet, dass etwas NICHT existiert "
            "oder nicht geht, nennt aber keinen Suchraum. Eine Abwesenheits-"
            "Behauptung ist nur so weit gemessen, wie gesucht wurde: die Angabe "
            "'durchsucht: ...' (welche Orte, Dateien, Zweige) ergaenzen -- oder "
            "die Behauptung als ungeprueft markieren."
        )
    if not any(zeichen.isdigit() for zeichen in klartext):
        return None
    if qc_gueltig:
        return None
    if not any(marke in klartext.lower() for marke in MARKEN):
        return (
            "[source-required] Die Antwort nennt Zahlen oder Daten, trägt aber "
            "keine einzige Marke. Jede Behauptung über Dateien, Repositories oder "
            "Messungen braucht eine von drei Marken: gemessen (mit Quelle: Datei, "
            "Befehl, Commit), Urteil (als Einschätzung gekennzeichnet) oder "
            "ungeprüft (offen benannt) -- oder, in jeder Sprache, ein "
            "QC-Belegblock ([QC] CLAIM: ... | MARK: MEASURED | SRC: ... [/QC]). "
            "Marken oder Block nachtragen, dann erneut abschließen."
        )
    fehlend = fehlende_pfade(klartext, arbeitsverzeichnis)
    if fehlend:
        return (
            "[source-required] Eine gemessen-Marke nennt als Quelle einen Pfad, "
            "den es im Arbeitsverzeichnis nicht gibt: "
            + ", ".join(sorted(set(fehlend)))
            + ". Eine Quelle, die nicht auflöst, ist keine Quelle: Pfad "
            "korrigieren oder die Behauptung als ungeprüft markieren."
        )
    return None


# Obergrenze fuer das Einlesen des Gespraechsprotokolls: bei einem groesseren
# Protokoll wird nur das Ende gelesen (dort steht die letzte Antwort). Ohne
# Grenze koennte ein Riesenprotokoll den Hook am Speicher aufhaengen
# (Review-Befund). Eine angeschnittene erste Zeile faellt beim JSON-Parsen raus.
_LESEGRENZE = 8_000_000


def _protokollende(protokollpfad: Path, grenze: int = _LESEGRENZE) -> str:
    """Return at most the last `grenze` bytes of the transcript as text."""
    with protokollpfad.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        handle.seek(max(0, handle.tell() - grenze))
        return handle.read().decode("utf-8", errors="replace")


def letzter_assistententext(protokollpfad: Path) -> str:
    """Return the final assistant text from a transcript JSONL, or empty."""
    try:
        zeilen = _protokollende(protokollpfad).splitlines()
    except (OSError, ValueError):
        return ""
    for roh in reversed(zeilen):
        try:
            eintrag = json.loads(roh)
        except json.JSONDecodeError:
            continue
        nachricht = eintrag.get("message")
        if not isinstance(nachricht, dict) or nachricht.get("role") != "assistant":
            continue
        inhalt = nachricht.get("content")
        if isinstance(inhalt, str):
            return inhalt
        if isinstance(inhalt, list):
            teile = [
                block.get("text", "") for block in inhalt if isinstance(block, dict) and block.get("type") == "text"
            ]
            verbunden = "\n".join(teil for teil in teile if teil)
            if verbunden:
                return verbunden
    return ""


def protokolliere_blockade(grund: str, sitzung: object) -> None:
    """Append the block to the plugin's JSONL log; never raise, never block."""
    try:
        basis = os.environ.get("CLAUDE_PLUGIN_DATA")
        verzeichnis = Path(basis) if basis else Path.home() / ".claude" / "plugin-data" / "source-required"
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

    text = nutzlast.get("last_assistant_message")
    if not isinstance(text, str) or not text:
        protokoll = nutzlast.get("transcript_path")
        text = letzter_assistententext(Path(protokoll)) if isinstance(protokoll, str) else ""
    if not text:
        return 0

    arbeitsverzeichnis = nutzlast.get("cwd")
    wurzel = Path(arbeitsverzeichnis) if isinstance(arbeitsverzeichnis, str) else Path.cwd()

    try:
        grund = befund(text, wurzel)
    except Exception:  # noqa: BLE001 -- der Wächter fällt grundsätzlich offen aus
        return 0
    if grund is None:
        return 0
    protokolliere_blockade(grund, nutzlast.get("session_id"))
    print(grund, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
