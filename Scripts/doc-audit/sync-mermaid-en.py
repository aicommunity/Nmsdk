#!/usr/bin/env python3
"""Sync mermaid blocks RU->EN and translate Cyrillic labels in EN diagrams only."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import importlib.util

sys.path.insert(0, str(Path(__file__).resolve().parent))

_spec = importlib.util.spec_from_file_location(
    "complete_bilingual_en",
    Path(__file__).resolve().parent / "complete-bilingual-en.py",
)
_cbe = importlib.util.module_from_spec(_spec)
assert _spec.loader
_spec.loader.exec_module(_cbe)

sync_mermaid_by_section = _cbe.sync_mermaid_by_section
from lib_doc_audit import iter_markdown_files  # noqa: E402

SKIP_PREFIXES = ("Bin/Configs/SpikeSamples/", "Reports/", "Docs/Audit/")
SKIP_EXACT = {"Docs/Overview/Markdown-Files-Index.md"}


def process_file(path: Path, apply: bool) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "## RU" not in text or "## EN" not in text:
        return False
    prefix, en_old = text.split("## EN", 1)
    ru_body = prefix.split("## RU", 1)[1].strip()
    en_new = sync_mermaid_by_section(ru_body, en_old.strip())
    if en_new.strip() == en_old.strip():
        return False
    if apply:
        path.write_text(prefix + "## EN\n\n" + en_new.strip() + "\n", encoding="utf-8")
    return True


def main() -> int:
    from lib_doc_audit import ROOT  # noqa: E402

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path-prefix", default="")
    args = parser.parse_args()

    n = 0
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(SKIP_PREFIXES) or rel in SKIP_EXACT:
            continue
        if args.path_prefix and not rel.startswith(args.path_prefix):
            continue
        if process_file(path, args.apply):
            n += 1
            print(f"{'APPLY' if args.apply else 'DRY'}: {rel}")
    print(f"Updated: {n}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
