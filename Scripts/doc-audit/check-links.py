#!/usr/bin/env python3
"""Validate relative markdown links."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import (  # noqa: E402
    AUDIT_DIR,
    LINK_PATTERN,
    ROOT,
    BrokenLink,
    iter_markdown_files,
    utc_now_iso,
    write_text,
)


def resolve_target(source: Path, target: str) -> Path | None:
    target = target.strip()
    if not target or target.startswith("#"):
        return None
    if target.startswith(("http://", "https://", "mailto:", "ftp://")):
        return None
    if target.startswith("/"):
        return None
    target = unquote(target.split("#", 1)[0].strip())
    if not target:
        return None
    return (source.parent / target).resolve()


def check_links() -> list[BrokenLink]:
    broken: list[BrokenLink] = []
    for md in iter_markdown_files():
        text = md.read_text(encoding="utf-8", errors="replace")
        for _label, raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1].strip()
            resolved = resolve_target(md, target)
            if resolved is None:
                continue
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                broken.append(
                    BrokenLink(
                        source=md.relative_to(ROOT).as_posix(),
                        target=target,
                        reason="points outside repository root",
                    )
                )
                continue
            if not resolved.exists():
                broken.append(
                    BrokenLink(
                        source=md.relative_to(ROOT).as_posix(),
                        target=target,
                        reason="target does not exist",
                    )
                )
    return broken


def render_report(broken: list[BrokenLink], total_files: int) -> str:
    lines = [
        "# Link Health Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        "## Summary",
        "",
        f"- Markdown files scanned: **{total_files}**",
        f"- Broken relative links: **{len(broken)}**",
        "",
    ]
    if not broken:
        lines.append("No broken relative links found.")
        return "\n".join(lines) + "\n"

    lines.extend(["## Broken links", ""])
    for item in broken:
        lines.append(f"- `{item.source}` → `{item.target}` — {item.reason}")
    return "\n".join(lines) + "\n"


def main() -> int:
    files = iter_markdown_files()
    broken = check_links()
    report = render_report(broken, len(files))
    write_text(AUDIT_DIR / "Link-Health-Report.md", report)
    print(report)
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
