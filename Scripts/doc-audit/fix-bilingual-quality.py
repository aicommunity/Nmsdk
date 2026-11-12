#!/usr/bin/env python3
"""Fix common bilingual doc quality issues: diagram placeholders, RU headings in EN."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import iter_markdown_files  # noqa: E402

PLACEHOLDER = "[Same as RU section]"
MERMAID_BLOCK = re.compile(r"```mermaid\n([\s\S]*?)```", re.MULTILINE)

EN_HEADING_FIXES = (
    (re.compile(r"^## Источники\s*$", re.M), "## References"),
    (re.compile(r"^## Литература\s*$", re.M), "## Literature"),
    (re.compile(r"^### Источники\s*$", re.M), "### References"),
)


def extract_ru_mermaids(text: str) -> list[str]:
    if "## RU" not in text:
        return []
    ru_part = text.split("## EN")[0].split("## RU", 1)[-1]
    return [m.group(0) for m in MERMAID_BLOCK.finditer(ru_part)]


def replace_diagram_placeholders(en_text: str, mermaids: list[str]) -> tuple[str, int]:
    if PLACEHOLDER not in en_text:
        return en_text, 0
    idx = 0
    count = 0

    def repl(_: re.Match[str]) -> str:
        nonlocal idx, count
        if idx < len(mermaids):
            block = mermaids[idx]
            idx += 1
            count += 1
            return block
        return PLACEHOLDER

    new_en = re.sub(re.escape(PLACEHOLDER), repl, en_text)
    return new_en, count


def fix_en_section_headings(en_text: str) -> tuple[str, int]:
    fixes = 0
    for pat, repl in EN_HEADING_FIXES:
        new, n = pat.subn(repl, en_text)
        if n:
            fixes += n
            en_text = new
    return en_text, fixes


def process_file(path: Path, apply: bool) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "## EN" not in text:
        return {}

    prefix, en_part = text.split("## EN", 1)
    mermaids = extract_ru_mermaids(text)
    new_en, ph = replace_diagram_placeholders(en_part, mermaids)
    new_en, hd = fix_en_section_headings(new_en)

    stats = {}
    if ph:
        stats["placeholders"] = ph
    if hd:
        stats["headings"] = hd
    if not stats:
        return {}

    if apply:
        path.write_text(prefix + "## EN" + new_en, encoding="utf-8")
    return stats


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path-prefix", default="")
    args = parser.parse_args()

    totals: dict[str, int] = {}
    files = 0
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if args.path_prefix and not rel.startswith(args.path_prefix):
            continue
        stats = process_file(path, args.apply)
        if stats:
            files += 1
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel} {stats}")
            for k, v in stats.items():
                totals[k] = totals.get(k, 0) + v

    print(f"Files: {files}, totals: {totals}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
