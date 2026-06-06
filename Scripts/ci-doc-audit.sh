#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "== CI doc-audit =="
Scripts/doc-audit/run-all.sh

# Fail CI if critical root-doc links to Docs/ are broken (subset check)
python3 <<'PY'
import re
import sys
from pathlib import Path

ROOT = Path(".")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
critical = [
    "Docs/README.md",
    "Docs/Components-And-Configuration/Component-System.md",
    "Docs/Build-And-Deploy/Build-System.md",
    "README.md",
]
broken = []
for rel in critical:
    p = ROOT / rel
    if not p.exists():
        broken.append((rel, rel, "missing file"))
        continue
    for m in LINK.finditer(p.read_text(encoding="utf-8")):
        t = m.group(1).strip().split("#")[0]
        if not t or t.startswith(("http", "mailto", "#")):
            continue
        target = (p.parent / t).resolve()
        if not target.exists():
            broken.append((rel, t, "missing target"))

if broken:
    print("Critical doc link failures:", len(broken))
    for b in broken[:20]:
        print(" ", b)
    sys.exit(1)
print("Critical doc links OK")
PY

echo "CI doc-audit passed"
