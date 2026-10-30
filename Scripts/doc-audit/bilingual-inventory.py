#!/usr/bin/env python3
"""CSV inventory of bilingual RU/EN coverage across markdown files."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import (  # noqa: E402
    AUDIT_DIR,
    detect_bilingual,
    iter_markdown_files,
    submodule_for,
    utc_now_iso,
    write_text,
)

RU_ONLY_ALLOWLIST_PREFIXES = (
    "Bin/Configs/SpikeSamples/",
    "Reports/",
    "Docs/Audit/",
)

RU_ONLY_ALLOWLIST_EXACT = (
    "Docs/Overview/Markdown-Files-Index.md",
)


def is_allowlisted(rel: str) -> bool:
    if rel in RU_ONLY_ALLOWLIST_EXACT:
        return True
    return rel.startswith(RU_ONLY_ALLOWLIST_PREFIXES)


def zone_for(rel: str) -> str:
    if rel.startswith("Libraries/Nmsdk-MotionControlLib/"):
        return "motion"
    if rel.startswith("Libraries/Nmsdk-PulseLib/"):
        return "pulse"
    if rel.startswith("Libraries/Rdk-HardwareLib/"):
        return "hardware"
    if rel.startswith("Libraries/Rdk-CvBasicLib/"):
        return "cvbasic"
    if rel.startswith("Libraries/Rdk-BasicLib/"):
        return "basic"
    if rel.startswith("Rdk/"):
        return "rdk"
    if rel.startswith("Bin/"):
        return "bin"
    if rel.startswith("Docs/"):
        return "docs"
    if rel.startswith("Tests/"):
        return "tests"
    return "misc"


def en_fragment_bytes(text: str) -> int:
    if "## EN" in text:
        _, _, tail = text.partition("## EN")
        return len(tail.encode("utf-8"))
    if "\n---\n" in text:
        return len(text.split("\n---\n", 1)[1].encode("utf-8"))
    return 0


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    rows: list[dict[str, str | int | bool]] = []
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        has_ru = bool(re.search(r"^##\s+RU\b", text, re.MULTILINE))
        has_en = bool(re.search(r"^##\s+EN\b", text, re.MULTILINE))
        rows.append(
            {
                "path": rel,
                "zone": zone_for(rel),
                "submodule": submodule_for(path),
                "allowlisted": is_allowlisted(rel),
                "has_ru_header": has_ru,
                "has_en_header": has_en,
                "lang_detect": detect_bilingual(text),
                "en_fragment_bytes": en_fragment_bytes(text),
                "has_mermaid": "```mermaid" in text,
            }
        )

    csv_path = AUDIT_DIR / "Bilingual-Inventory.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "path",
                "zone",
                "submodule",
                "allowlisted",
                "has_ru_header",
                "has_en_header",
                "lang_detect",
                "en_fragment_bytes",
                "has_mermaid",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    missing_en = [r for r in rows if not r["allowlisted"] and not r["has_en_header"]]
    lines = [
        "# Bilingual Inventory Summary",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        f"- Total markdown files: **{len(rows)}**",
        f"- Missing `## EN` (outside allowlist): **{len(missing_en)}**",
        f"- CSV: [Bilingual-Inventory.csv](Bilingual-Inventory.csv)",
        "",
    ]
    write_text(AUDIT_DIR / "Bilingual-Inventory-Summary.md", "\n".join(lines) + "\n")
    print(lines[-3])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
