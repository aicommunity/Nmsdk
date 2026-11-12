#!/usr/bin/env python3
"""Validate Libraries/Rdk-HardwareLib/Catalog (and optional Bin sync copy)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "Libraries/Rdk-HardwareLib/Catalog"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(root: Path) -> list[str]:
    errors: list[str] = []
    index_path = root / "catalog.json"
    if not index_path.is_file():
        return [f"missing {index_path}"]
    index = load_json(index_path)
    if index.get("schemaVersion") != 1:
        errors.append("catalog.json schemaVersion must be 1")

    for section in ("boards", "shields", "modules", "firmwares"):
        entries = index.get(section, [])
        if not isinstance(entries, list):
            errors.append(f"{section} must be a list")
            continue
        for rel in entries:
            path = root / rel
            if not path.is_file():
                errors.append(f"missing {section} entry: {rel}")
                continue
            try:
                obj = load_json(path)
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON {rel}: {exc}")
                continue
            if "id" not in obj:
                errors.append(f"{rel}: missing id")
            if section == "firmwares" and "available" not in obj:
                errors.append(f"{rel}: missing available")
            layout = obj.get("layoutAsset") or obj.get("asset")
            if layout:
                asset = root / layout
                if not asset.is_file():
                    errors.append(f"{rel}: missing asset {layout}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_CATALOG,
        help="Catalog root (default: Libraries/Rdk-HardwareLib/Catalog)",
    )
    args = parser.parse_args()
    errors = validate_catalog(args.root)
    if errors:
        print("Hardware catalog validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: catalog valid at {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
