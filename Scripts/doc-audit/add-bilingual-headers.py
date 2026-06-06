#!/usr/bin/env python3
"""Insert ## RU / --- / ## EN structure into markdown files missing bilingual headers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import detect_bilingual, iter_markdown_files  # noqa: E402

RU_ONLY_ALLOWLIST_PREFIXES = (
    "Bin/Configs/SpikeSamples/",
    "Reports/",
    "Docs/Audit/",
)

RU_ONLY_ALLOWLIST_EXACT = (
    "Docs/Overview/Markdown-Files-Index.md",
)

SEP_EN_PATTERN = re.compile(r"\n---\n", re.MULTILINE)
H1_PATTERN = re.compile(r"^#\s+.+$", re.MULTILINE)


def is_allowlisted(rel: str) -> bool:
    if rel in RU_ONLY_ALLOWLIST_EXACT:
        return True
    return rel.startswith(RU_ONLY_ALLOWLIST_PREFIXES)


def insert_ru_header(text: str) -> str:
    if re.search(r"^##\s+RU\b", text, re.MULTILINE):
        return text
    m = H1_PATTERN.search(text)
    if not m:
        return "## RU\n\n" + text
    insert_at = m.end()
    return text[:insert_at] + "\n\n## RU" + text[insert_at:]


def restructure_sep_en(text: str) -> tuple[str, bool]:
    """MotionControlLib pattern: RU body, ---, second H1 EN block without ## EN."""
    if re.search(r"^##\s+EN\b", text, re.MULTILINE):
        return text, False
    parts = SEP_EN_PATTERN.split(text, maxsplit=1)
    if len(parts) != 2:
        return text, False
    ru_part, en_part = parts
    ru_part = insert_ru_header(ru_part.rstrip())
    en_part = en_part.strip()
    en_part = re.sub(r"^#\s+", "", en_part, count=1)
    new_text = ru_part + "\n\n---\n\n## EN\n\n" + en_part + "\n"
    return new_text, True


def add_en_skeleton(text: str) -> tuple[str, bool]:
    if re.search(r"^##\s+EN\b", text, re.MULTILINE):
        return text, False
    text = insert_ru_header(text.rstrip())
    skeleton = (
        "\n\n---\n\n## EN\n\n"
        "<!-- TODO: English translation pending -->\n"
    )
    return text + skeleton, True


def process_file(path: Path, apply: bool) -> tuple[str, bool]:
    from lib_doc_audit import ROOT  # noqa: E402

    rel = path.relative_to(ROOT).as_posix()
    if is_allowlisted(rel):
        return rel, False
    text = path.read_text(encoding="utf-8", errors="replace")
    if detect_bilingual(text) == "both":
        return rel, False

    new_text, changed = restructure_sep_en(text)
    if not changed:
        new_text, changed = add_en_skeleton(text)

    if changed and apply:
        path.write_text(new_text, encoding="utf-8")
    return rel, changed


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--zone", help="Filter by zone prefix (motion|rdk|pulse|...)")
    parser.add_argument("--path", help="Single file relative to repo root")
    args = parser.parse_args()

    zone_prefixes = {
        "motion": "Libraries/Nmsdk-MotionControlLib/",
        "pulse": "Libraries/Nmsdk-PulseLib/",
        "hardware": "Libraries/Rdk-HardwareLib/",
        "cvbasic": "Libraries/Rdk-CvBasicLib/",
        "basic": "Libraries/Rdk-BasicLib/",
        "rdk": "Rdk/",
        "bin": "Bin/",
        "docs": "Docs/",
        "tests": "Tests/",
    }

    files = iter_markdown_files()
    if args.path:
        files = [ROOT / args.path]
    elif args.zone:
        prefix = zone_prefixes.get(args.zone, args.zone)
        files = [p for p in files if p.relative_to(ROOT).as_posix().startswith(prefix)]

    changed_count = 0
    for path in files:
        rel, changed = process_file(path, args.apply)
        if changed:
            changed_count += 1
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel}")

    print(f"Files changed: {changed_count}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
