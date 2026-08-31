"""UserPromptSubmit-Hook des Plugins nothing-missed: die Erinnerung vor der Arbeit.

Gibt vor jeder Nutzereingabe eine Ein-Zeilen-Erinnerung als Kontext aus, damit
die Eingangsliste gar nicht erst vergessen wird -- der Stop-Hook soll die
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
        "[nothing-missed] Entsteht ein Dokument aus diesem Gespräch: erst die "
        "nummerierte Eingangsliste aus dem Verlauf ziehen, dagegen schreiben, "
        "und die Übergabe trägt die Liste mit Fundstelle je Position -- in "
        "jeder Sprache mit den Token INTAKE: (Position) und REF: (Fundstelle)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
