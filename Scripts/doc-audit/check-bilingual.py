#!/usr/bin/env python3
"""Report markdown files missing bilingual RU/EN sections."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import (  # noqa: E402
    AUDIT_DIR,
    detect_bilingual,
    iter_markdown_files,
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


def main() -> int:
    missing_en = []
    missing_ru = []
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        if is_allowlisted(rel):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lang = detect_bilingual(text)
        if lang in ("ru", "unknown"):
            missing_en.append(rel)
        if lang in ("en", "unknown"):
            missing_ru.append(rel)

    lines = [
        "# Bilingual Parity Report",
        "",
        f"Generated: {utc_now_iso()}",
        "",
        "## Summary",
        "",
        f"- Files missing `## EN`: **{len(missing_en)}**",
        f"- Files missing `## RU`: **{len(missing_ru)}**",
        "",
        "RU-only allowlist prefixes:",
        "",
    ]
    for prefix in RU_ONLY_ALLOWLIST_PREFIXES:
        lines.append(f"- `{prefix}*`")
    lines.extend(["", "## Missing EN section", ""])
    for rel in missing_en[:200]:
        lines.append(f"- `{rel}`")
    if len(missing_en) > 200:
        lines.append(f"- ... and {len(missing_en) - 200} more")
    write_text(AUDIT_DIR / "Bilingual-Parity-Report.md", "\n".join(lines) + "\n")
    print("\n".join(lines[:20]))
    return 0


if __name__ == "__main__":
    from lib_doc_audit import ROOT  # noqa: E402

    raise SystemExit(main())
