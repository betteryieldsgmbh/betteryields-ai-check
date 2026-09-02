#!/usr/bin/env python3
"""Baut die .skill-Pakete aus skills/ und schreibt dist/manifest.json.

Ein .skill ist ein Zip mit GENAU EINEM Ordner auf oberster Ebene, darin direkt
die SKILL.md; so verlangt es der Skill-Upload der Assistenten. Die Zips sind
deterministisch (feste Zeitstempel, feste Rechte): zwei Baeume mit gleichem
Inhalt ergeben bytegleiche Pakete, und die Pruefsumme im Manifest bleibt
nachrechenbar.

Aufruf:  python3 tools/paketiere.py            baut alle Pakete nach dist/
         python3 tools/paketiere.py --check    prueft, ob dist/ zum Baum passt

Das Manifest nennt je Skill Datei, Version (aus der SKILL.md) und SHA-256. Wer
die Pakete ausliefert, prueft die Datei gegen diese Summe.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
SKILLS = ("source-required", "nothing-missed", "show-your-work")
_VERSION = re.compile(r'^\s*version:\s*"?([0-9][0-9.]*)"?\s*$', re.MULTILINE)


def version_von(skill_md: str) -> str:
    """Return the version named in the SKILL.md front matter."""
    m = _VERSION.search(skill_md.split("\n---", 2)[0] if skill_md.startswith("---") else skill_md)
    if not m:
        raise SystemExit("SKILL.md ohne version im Kopfblock")
    return m.group(1)


def paket_bytes(name: str) -> bytes:
    """The deterministic zip of skills/<name>, as bytes."""
    quelle = WURZEL / "skills" / name
    if not (quelle / "SKILL.md").is_file():
        raise SystemExit(f"{name}: SKILL.md fehlt")
    dateien = sorted(p for p in quelle.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    import io
    puffer = io.BytesIO()
    with zipfile.ZipFile(puffer, "w", zipfile.ZIP_DEFLATED) as paket:
        for p in dateien:
            info = zipfile.ZipInfo(f"{name}/{p.relative_to(quelle).as_posix()}", date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            paket.writestr(info, p.read_bytes())
    return puffer.getvalue()


def manifest() -> dict:
    eintraege = {}
    for name in SKILLS:
        roh = paket_bytes(name)
        eintraege[name] = {
            "artifact": f"{name}.skill",
            "version": version_von((WURZEL / "skills" / name / "SKILL.md").read_text(encoding="utf-8")),
            "sha256": hashlib.sha256(roh).hexdigest(),
            "bytes": len(roh),
        }
    return {"skills": eintraege}


def main(argv: list[str]) -> int:
    dist = WURZEL / "dist"
    m = manifest()
    if "--check" in argv:
        alt = json.loads((dist / "manifest.json").read_text(encoding="utf-8")) if (dist / "manifest.json").is_file() else {}
        schlecht = [n for n, e in m["skills"].items()
                    if alt.get("skills", {}).get(n) != e
                    or not (dist / e["artifact"]).is_file()
                    or hashlib.sha256((dist / e["artifact"]).read_bytes()).hexdigest() != e["sha256"]]
        if schlecht:
            print(f"[FAIL] dist/ passt nicht zum Baum: {', '.join(schlecht)}. Neu bauen: python3 tools/paketiere.py")
            return 1
        print("[OK] dist/ passt zum Baum")
        return 0
    dist.mkdir(exist_ok=True)
    for name, e in m["skills"].items():
        (dist / e["artifact"]).write_bytes(paket_bytes(name))
        print(f"[OK] dist/{e['artifact']}  {e['version']}  {e['sha256'][:8]}  {e['bytes']} bytes")
    (dist / "manifest.json").write_text(json.dumps(m, indent=2) + "\n", encoding="utf-8")
    print("[OK] dist/manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
