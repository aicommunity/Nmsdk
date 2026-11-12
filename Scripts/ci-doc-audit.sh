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

# Fail CI if mermaid or bilingual gates regress (outside allowlist)
python3 <<'PY'
import re
import sys
from pathlib import Path

ROOT = Path("Docs/Audit")

def parse_count(report: Path, pattern: str) -> int:
    if not report.exists():
        print(f"Missing report: {report}")
        return -1
    m = re.search(pattern, report.read_text(encoding="utf-8"))
    return int(m.group(1)) if m else -1

mermaid = parse_count(ROOT / "Mermaid-Sanity-Report.md", r"Potential issues: \*\*(\d+)\*\*")
missing_en = parse_count(ROOT / "Bilingual-Parity-Report.md", r'Files missing `## EN`: \*\*(\d+)\*\*')
missing_ru = parse_count(ROOT / "Bilingual-Parity-Report.md", r'Files missing `## RU`: \*\*(\d+)\*\*')

failed = False
for name, val in (
    ("mermaid issues", mermaid),
    ("missing EN", missing_en),
    ("missing RU", missing_ru),
):
    if val != 0:
        print(f"CI gate failed: {name} = {val} (expected 0)")
        failed = True

if failed:
    sys.exit(1)
print("Mermaid and bilingual gates OK")
PY

echo "CI doc-audit passed"
