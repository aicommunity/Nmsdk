#!/usr/bin/env python3
"""Basic mermaid block sanity checks."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import AUDIT_DIR, iter_markdown_files, utc_now_iso, write_text  # noqa: E402

MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def main() -> int:
    issues = []
    total_blocks = 0
    for path in iter_markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for block in MERMAID_BLOCK.findall(text):
            total_blocks += 1
            stripped = block.strip()
            if not stripped:
                issues.append((path, "empty mermaid block"))
                continue
            if "<br/>" in stripped and " " in stripped.split("\n", 1)[0]:
                issues.append((path, "spaces in node id with <br/> label"))
    lines = [
        "# Mermaid Sanity Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        f"- Mermaid blocks scanned: **{total_blocks}**",
        f"- Potential issues: **{len(issues)}**",
        "",
    ]
    if issues:
        lines.append("## Issues")
        lines.append("")
        for path, reason in issues[:100]:
            rel = path.relative_to(path.parents[len(path.parents) - len(path.parts)])
            lines.append(f"- `{path}` — {reason}")
    else:
        lines.append("No obvious mermaid issues detected.")
    write_text(AUDIT_DIR / "Mermaid-Sanity-Report.md", "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
