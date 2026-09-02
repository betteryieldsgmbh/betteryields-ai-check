"""UserPromptSubmit-Hook des Plugins show-your-work: die Erinnerung vor der Arbeit.

Gibt vor jeder Nutzereingabe eine Ein-Zeilen-Erinnerung als Kontext aus, damit
der Lieferblock gar nicht erst vergessen wird -- der Stop-Hook soll die
Ausnahme bleiben, nicht der Normalfall. Reine Ausgabe, blockiert nie.
"""

from __future__ import annotations

import contextlib
import sys


def main() -> int:
    """Emit the one-line reminder and consume stdin."""
    with contextlib.suppress(OSError):
        sys.stdin.read()
    print(
        "[show-your-work] Vor jeder Übergabe (Artefakt, Datei, Push, Pull Request) "
        "steht der Lieferblock: [SHIPPED] OBJECT: <der übergebene Gegenstand> und je Prüfung "
        "CHECK: ... | ON: SAME | RESULT: ... | SCALE: <jede Stufe der Prüfung> [/SHIPPED]. "
        "Ein Nachweis ohne Gegenstand oder mit halber Skala wird abgelehnt."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
