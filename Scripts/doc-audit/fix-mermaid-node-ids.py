#!/usr/bin/env python3
"""Quote flowchart node labels that contain <br/> inside braces."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import ROOT, iter_markdown_files  # noqa: E402

MERMAID_BLOCK = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)

SKIP_PREFIXES = (
    "Bin/Configs/SpikeSamples/",
    "Docs/Audit/",
    "Reports/",
)

BRACE_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\{([^{}]*<br/[^}]*)\}")
BRACKET_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[([^\[\]]*<br/[^\[\]]*)\]")


def fix_block(block: str) -> tuple[str, int]:
    count = 0

    def quote_label(node_id: str, label: str, open_c: str, close_c: str) -> str:
        nonlocal count
        if label.startswith('"') or label.startswith("'"):
            return f"{node_id}{open_c}{label}{close_c}"
        count += 1
        escaped = label.replace('"', "#quot;")
        return f'{node_id}["{escaped}"]'

    def repl_brace(m: re.Match[str]) -> str:
        return quote_label(m.group(1), m.group(2), "{", "}")

    def repl_bracket(m: re.Match[str]) -> str:
        label = m.group(2)
        if label.startswith("("):
            return m.group(0)
        return quote_label(m.group(1), label, "[", "]")

    new_block = BRACE_PATTERN.sub(repl_brace, block)
    new_block = BRACKET_PATTERN.sub(repl_bracket, new_block)
    return new_block, count


def fix_text(text: str) -> tuple[str, int]:
    total = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal total
        opener, body, closer = m.group(1), m.group(2), m.group(3)
        new_body, n = fix_block(body)
        total += n
        return opener + new_body + closer

    return MERMAID_BLOCK.sub(repl, text), total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--prefix", action="append", default=[])
    args = parser.parse_args()

    prefixes = tuple(args.prefix) if args.prefix else (
        "Libraries/Nmsdk-MotionControlLib/",
        "Libraries/Nmsdk-PulseLib/",
        "Libraries/Rdk-HardwareLib/",
        "Libraries/Rdk-CvBasicLib/",
        "Rdk/Docs/",
        "Docs/",
        "Bin/Docs/",
    )

    files_changed = 0
    fixes = 0
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(SKIP_PREFIXES):
            continue
        if prefixes and not any(rel.startswith(p) for p in prefixes):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text, n = fix_text(text)
        if n:
            fixes += n
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
            files_changed += 1
            print(f"{rel}: {n} fix(es)")

    print(f"Files: {files_changed}, fixes: {fixes}, apply={args.apply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
