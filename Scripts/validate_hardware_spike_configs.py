#!/usr/bin/env python3
"""Validate SpikeSamples Hardware JSON/XML against the hardware catalog.

Does not require a live board. Checks setup JSON ids, HardwareSetupPath
resolution, BoardProfile vs JSON board, and StandardFirmata on Firmata labs.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "Libraries/Rdk-HardwareLib/Catalog"
DEFAULT_HARDWARE = ROOT / "Bin/Configs/SpikeSamples/Hardware"

FIRMATA_LABS = (
    "03-ArduinoFirmata",
    "08-ArduinoFirmata-AnalogLink",
    "09-HardwareSetup-SensorShield",
    "10-DeviceIO-Potentiometer",
    "11-DeviceIO-Servo",
    "12-MotorShield-R3",
    "13-Sensors-To-Pulse",
    "17-DeviceIO-LED",
    "18-DeviceIO-PotToPwmLed",
)

BOARD_PROFILE = {"uno": 0, "mega2560": 1}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_ids(catalog_root: Path) -> dict[str, set[str]]:
    index = load_json(catalog_root / "catalog.json")
    out: dict[str, set[str]] = {}
    for section in ("boards", "shields", "modules", "firmwares"):
        ids: set[str] = set()
        for rel in index.get(section, []):
            obj = load_json(catalog_root / rel)
            ids.add(obj["id"])
        out[section] = ids
    return out


def xml_texts(root: ET.Element, tag: str) -> list[str]:
    return [el.text or "" for el in root.iter(tag)]


def validate_setup(path: Path, ids: dict[str, set[str]]) -> list[str]:
    errors: list[str] = []
    rel = path.name
    try:
        obj = load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{rel}: invalid JSON: {exc}"]
    board = obj.get("board")
    if board not in ids["boards"]:
        errors.append(f"{rel}: unknown board {board!r}")
    fw = obj.get("firmwareId")
    if fw not in ids["firmwares"]:
        errors.append(f"{rel}: unknown firmwareId {fw!r}")
    stack = obj.get("stack", [])
    if not isinstance(stack, list):
        errors.append(f"{rel}: stack must be a list")
    else:
        for shield in stack:
            if shield not in ids["shields"]:
                errors.append(f"{rel}: unknown shield {shield!r}")
    devices = obj.get("devices", [])
    if not isinstance(devices, list):
        errors.append(f"{rel}: devices must be a list")
    else:
        for i, dev in enumerate(devices):
            module = (dev or {}).get("module")
            if module not in ids["modules"]:
                errors.append(f"{rel}: devices[{i}] unknown module {module!r}")
    return errors


def validate_project(folder: Path, ids: dict[str, set[str]], require_firmata: bool) -> list[str]:
    errors: list[str] = []
    label = folder.name
    model_path = folder / "Model_00.xml"
    interface_path = folder / "Interface.xml"
    if not model_path.is_file():
        return [f"{label}: missing Model_00.xml"]
    try:
        tree = ET.parse(model_path)
    except ET.ParseError as exc:
        return [f"{label}: Model_00.xml parse error: {exc}"]
    root = tree.getroot()
    if require_firmata:
        bundled = xml_texts(root, "BundledFirmwareId")
        if not bundled:
            errors.append(f"{label}: missing BundledFirmwareId")
        elif any(v != "standard_firmata" for v in bundled):
            errors.append(f"{label}: BundledFirmwareId must be standard_firmata, got {bundled}")
        if "LastProjectPath" in model_path.read_text(encoding="utf-8"):
            errors.append(f"{label}: Model_00.xml contains LastProjectPath")

    if interface_path.is_file():
        try:
            iface = ET.parse(interface_path)
        except ET.ParseError as exc:
            errors.append(f"{label}: Interface.xml parse error: {exc}")
        else:
            text = interface_path.read_text(encoding="utf-8")
            if "LastProjectPath" in text:
                errors.append(f"{label}: Interface.xml contains LastProjectPath")
            if iface.getroot().find("UGEngineControlForm") is None:
                errors.append(f"{label}: Interface.xml missing UGEngineControlForm")
    else:
        errors.append(f"{label}: missing Interface.xml")

    profiles = xml_texts(root, "BoardProfile")
    int_profiles: list[int] = []
    for raw in profiles:
        try:
            int_profiles.append(int(raw))
        except ValueError:
            errors.append(f"{label}: non-integer BoardProfile {raw!r}")
    if int_profiles and len(set(int_profiles)) > 1:
        errors.append(f"{label}: mixed BoardProfile values {sorted(set(int_profiles))}")

    setup_paths = [p for p in xml_texts(root, "HardwareSetupPath") if p.strip()]
    for rel in setup_paths:
        resolved = (folder / rel).resolve()
        if not resolved.is_file():
            errors.append(f"{label}: HardwareSetupPath does not resolve: {rel}")
            continue
        setup_errs = validate_setup(resolved, ids)
        errors.extend(f"{label} -> {e}" for e in setup_errs)
        try:
            setup = load_json(resolved)
        except json.JSONDecodeError:
            continue
        expected = BOARD_PROFILE.get(str(setup.get("board")))
        if expected is None:
            continue
        if int_profiles and any(p != expected for p in int_profiles):
            errors.append(
                f"{label}: BoardProfile {sorted(set(int_profiles))} "
                f"does not match setup board {setup.get('board')!r} (expected {expected})"
            )
    return errors


def validate(catalog_root: Path, hardware_root: Path) -> list[str]:
    errors: list[str] = []
    ids = catalog_ids(catalog_root)
    shared = hardware_root / "_shared"
    if not shared.is_dir():
        return [f"missing {shared}"]
    for path in sorted(shared.glob("*.json")):
        errors.extend(validate_setup(path, ids))
    for lab in FIRMATA_LABS:
        folder = hardware_root / lab
        if not folder.is_dir():
            errors.append(f"missing Firmata lab {lab}")
            continue
        errors.extend(validate_project(folder, ids, require_firmata=True))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--hardware", type=Path, default=DEFAULT_HARDWARE)
    args = parser.parse_args()
    errors = validate(args.catalog, args.hardware)
    if errors:
        print("Hardware spike config validation FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"OK: spike hardware configs valid at {args.hardware}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
