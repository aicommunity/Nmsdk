#!/usr/bin/env python3
"""Migrate legacy ArduinoDcDemo configs (SensorSketch + DcDemo) to a single ArduinoDcDemo node."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = ROOT / "Bin/Configs/SpikeSamples/Hardware/05-ArduinoDcDemo/Model_00.xml"

SKETCH_BLOCK_RE = re.compile(
    r"\s*<SensorSketch Class=\"ArduinoSensorSketch\">.*?</SensorSketch>\s*",
    re.DOTALL,
)
LINKED_SKETCH_RE = re.compile(
    r"\s*<LinkedSketchName Type=\"std::string\" PType=\"257\" IoType=\"17\">[^<]*</LinkedSketchName>\s*",
)


def migrate_model_xml(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    if "<SensorSketch Class=\"ArduinoSensorSketch\">" in text:
        text = SKETCH_BLOCK_RE.sub("\n", text)
        notes.append("removed SensorSketch component")
    if "<LinkedSketchName " in text:
        text = LINKED_SKETCH_RE.sub("\n", text)
        notes.append("removed LinkedSketchName")
    return text, notes


def migrate_file(path: Path, dry_run: bool) -> bool:
    if not path.is_file():
        print(f"skip (missing): {path}", file=sys.stderr)
        return False
    original = path.read_text(encoding="utf-8")
    updated, notes = migrate_model_xml(original)
    if updated == original:
        print(f"unchanged: {path}")
        return True
    if dry_run:
        print(f"would update: {path} ({', '.join(notes)})")
        return True
    path.write_text(updated, encoding="utf-8")
    print(f"updated: {path} ({', '.join(notes)})")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Model_00.xml or directories containing it (default: 05-ArduinoDcDemo)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    targets: list[Path] = []
    if args.paths:
        for p in args.paths:
            if p.is_dir():
                targets.append(p / "Model_00.xml")
                params = p / "Parameters_00.xml"
                if params.exists():
                    targets.append(params)
            else:
                targets.append(p)
    else:
        targets = [DEFAULT_TARGET, DEFAULT_TARGET.parent / "Parameters_00.xml"]

    ok = True
    for path in targets:
        ok = migrate_file(path, args.dry_run) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
