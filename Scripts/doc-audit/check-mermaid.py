#!/usr/bin/env python3
"""Basic mermaid block sanity checks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import AUDIT_DIR, ROOT, iter_markdown_files, utc_now_iso, write_text  # noqa: E402

MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)

MERMAID_SKIP_PREFIXES = (
    "Bin/Configs/SpikeSamples/",
    "Docs/Audit/",
    "Reports/",
)

# flowchart node: Id{label with <br/>} without quoted label
UNQUOTED_BRACE_BR = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\{([^{}]*<br/[^}]*)\}")
UNQUOTED_BRACKET_BR = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\[([^\[\]]*<br/[^\[\]]*)\]")


def should_skip(rel: str) -> bool:
    return rel.startswith(MERMAID_SKIP_PREFIXES)


def scan_block(block: str) -> list[str]:
    issues: list[str] = []
    if not block.strip():
        issues.append("empty mermaid block")
        return issues
    first = block.strip().split("\n", 1)[0].strip().lower()
    if first.startswith("classdiagram") or first.startswith("sequencediagram"):
        return issues
    for line_no, line in enumerate(block.splitlines(), 1):
        if "<br/" not in line:
            continue
        for pat in (UNQUOTED_BRACE_BR, UNQUOTED_BRACKET_BR):
            if pat.search(line):
                m = pat.search(line)
                if m and not m.group(2).startswith(('"', "'", "(")):
                    issues.append(f"line {line_no}: unquoted node label with <br/>")
                    break
    return issues


def main() -> int:
    issues: list[tuple[str, str]] = []
    total_blocks = 0
    skipped_files = 0
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if should_skip(rel):
            skipped_files += 1
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for block_idx, block in enumerate(MERMAID_BLOCK.findall(text), 1):
            total_blocks += 1
            for reason in scan_block(block):
                issues.append((rel, f"block {block_idx}: {reason}"))
    lines = [
        "# Mermaid Sanity Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        f"- Mermaid blocks scanned: **{total_blocks}**",
        f"- Files skipped (allowlist): **{skipped_files}**",
        f"- Potential issues: **{len(issues)}**",
        "",
        "Allowlist prefixes:",
        "",
    ]
    for prefix in MERMAID_SKIP_PREFIXES:
        lines.append(f"- `{prefix}*`")
    if issues:
        lines.extend(["", "## Issues", ""])
        for rel, reason in issues[:150]:
            lines.append(f"- `{rel}` — {reason}")
        if len(issues) > 150:
            lines.append(f"- ... and {len(issues) - 150} more")
    else:
        lines.append("")
        lines.append("No mermaid issues detected outside allowlist.")
    write_text(AUDIT_DIR / "Mermaid-Sanity-Report.md", "\n".join(lines) + "\n")
    print("\n".join(lines[:25]))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
