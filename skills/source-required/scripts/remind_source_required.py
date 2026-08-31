"""UserPromptSubmit-Hook des Plugins source-required: die Erinnerung vor der Arbeit.

Gibt vor jeder Nutzereingabe eine Ein-Zeilen-Erinnerung als Kontext aus, damit
die Marken gar nicht erst vergessen werden -- der Stop-Hook soll die Ausnahme
bleiben, nicht der Normalfall. Reine Ausgabe, blockiert nie.
"""

from __future__ import annotations

import contextlib
import sys


def main() -> int:
    """Emit the one-line reminder and consume stdin."""
    with contextlib.suppress(OSError):
        sys.stdin.read()
    print(
        "[source-required] Jede Zahl, jedes Datum, jeder Zustand über Dateien, "
        "Repositories oder Messungen trägt eine Marke: gemessen (mit Quelle), "
        "Urteil oder ungeprüft -- oder, in jeder Sprache, einen QC-Belegblock "
        "([QC] CLAIM: ... | MARK: MEASURED | SRC: ... [/QC]). "
        "Eine Zahl ohne Marke wird abgelehnt."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
