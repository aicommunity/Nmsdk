#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "== doc-audit: inventory =="
python3 Scripts/doc-audit/inventory.py
python3 Scripts/doc-audit/regenerate-markdown-index.py

echo "== doc-audit: links =="
python3 Scripts/doc-audit/check-links.py || true

echo "== doc-audit: bilingual =="
python3 Scripts/doc-audit/bilingual-inventory.py
python3 Scripts/doc-audit/check-bilingual.py

echo "== doc-audit: mermaid =="
python3 Scripts/doc-audit/check-mermaid.py

echo "== doc-audit: gaps =="
python3 Scripts/doc-audit/gap-report.py

echo "Reports written to Docs/Audit/"
