#!/usr/bin/env python3
"""Merge RU content wrongly placed under ## EN after premature --- split."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BROKEN = (
    "Rdk/LLM/Docs/Architecture.md",
    "Rdk/LLM/Docs/Conversation-State.md",
    "Rdk/LLM/Docs/Domain-Layer.md",
    "Rdk/LLM/Docs/Project-Context-NMSDK.md",
    "Libraries/Nmsdk-PulseLib/Docs/Docs-Enrichment-Plan.md",
)


def fix_content(text: str) -> tuple[str, bool]:
    if "## RU" not in text or "## EN" not in text:
        return text, False
    before_en, en_body = text.split("## EN", 1)
    # Only fix if EN starts with Russian numbered section
    if not re.search(r"^##\s+[0-9]+\.\s+[А-Яа-яЁё]", en_body.strip(), re.M):
        return text, False
    # Remove trailing --- before ## EN in RU part
    ru_part = before_en.rstrip()
    if ru_part.endswith("---"):
        ru_part = ru_part[:-3].rstrip()
    merged_ru = ru_part + "\n\n" + en_body.strip() + "\n\n---\n\n## EN\n\n<!-- EN translation pending restructure -->\n"
    return merged_ru, True


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    for rel in BROKEN:
        path = root / rel
        if not path.exists():
            print(f"skip missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        new, changed = fix_content(text)
        if changed:
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel}")
            if args.apply:
                path.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
