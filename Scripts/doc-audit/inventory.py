#!/usr/bin/env python3
"""Generate documentation and code inventories for the audit."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib_doc_audit import (  # noqa: E402
    AUDIT_DIR,
    LIBRARY_REGISTRATION_FILES,
    ROOT,
    collect_cmake_metadata,
    detect_bilingual,
    has_mermaid,
    iter_markdown_files,
    parse_upload_classes,
    submodule_for,
    utc_now_iso,
    write_json,
)


def build_doc_inventory() -> dict:
    entries = []
    for path in iter_markdown_files():
        rel = path.relative_to(ROOT).as_posix()
        stat = path.stat()
        text = path.read_text(encoding="utf-8", errors="replace")
        entries.append(
            {
                "path": rel,
                "submodule": submodule_for(path),
                "language": detect_bilingual(text),
                "has_mermaid": has_mermaid(text),
                "size_bytes": stat.st_size,
                "mtime_iso": utc_now_iso(),
            }
        )
    return {
        "generated_at": utc_now_iso(),
        "total_files": len(entries),
        "files": entries,
    }


def build_code_inventory() -> dict:
    libraries = {}
    for lib, files in LIBRARY_REGISTRATION_FILES.items():
        libraries[lib] = {
            "registration_files": [f.relative_to(ROOT).as_posix() for f in files],
            "upload_classes": parse_upload_classes(files),
        }
    cmake_meta = collect_cmake_metadata()
    return {
        "generated_at": utc_now_iso(),
        "libraries": libraries,
        "cmake": cmake_meta,
    }


def main() -> int:
    doc_inv = build_doc_inventory()
    code_inv = build_code_inventory()
    write_json(AUDIT_DIR / "Documentation-Inventory.json", doc_inv)
    write_json(AUDIT_DIR / "Code-Inventory.json", code_inv)
    print(f"Wrote {doc_inv['total_files']} markdown entries")
    print(f"Wrote code inventory for {len(code_inv['libraries'])} libraries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
