"""Explicit CLI entry point; commands have no import-time side effects."""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="TimeLearner reproducible experiment tools")
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="inventory source properties and tracked historical tools")
    inventory.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    inventory.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "inventory":
        from .inventory import write_inventory
        write_inventory(args.root.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
