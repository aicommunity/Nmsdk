#!/usr/bin/env python3
"""Regenerate Docs/Overview/Markdown-Files-Index.md from Documentation-Inventory.json."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import AUDIT_DIR, ROOT, utc_now_iso, write_text  # noqa: E402

OUT = ROOT / "Docs" / "Overview" / "Markdown-Files-Index.md"
INV = AUDIT_DIR / "Documentation-Inventory.json"


def main() -> int:
    inv = json.loads(INV.read_text(encoding="utf-8"))
    by_zone: dict[str, list[str]] = defaultdict(list)
    for entry in inv["files"]:
        path = entry["path"]
        if path.startswith("Docs/"):
            zone = "Docs"
        elif path.startswith("Reports/"):
            zone = "Reports"
        else:
            zone = path.split("/", 1)[0]
        by_zone[zone].append(path)

    lines = [
        "# Markdown Files Index",
        "",
        "Auto-generated from `Docs/Audit/Documentation-Inventory.json`.",
        "",
        f"Total: **{inv['total_files']}** files.",
        "",
        "Run `Scripts/doc-audit/regenerate-markdown-index.py` after `inventory.py`.",
        "",
    ]
    for zone in sorted(by_zone):
        lines.append(f"## {zone}")
        lines.append("")
        for path in sorted(by_zone[zone]):
            lines.append(f"- {path}")
        lines.append("")

    write_text(OUT, "\n".join(lines))
    print(f"Wrote {OUT.relative_to(ROOT)} ({inv['total_files']} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
