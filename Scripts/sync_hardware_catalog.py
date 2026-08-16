#!/usr/bin/env python3
"""Sync Libraries/Rdk-HardwareLib/Catalog -> Bin/HardwareCatalog and refresh legacy firmware manifest."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Libraries" / "Rdk-HardwareLib" / "Catalog"
DST = ROOT / "Bin" / "HardwareCatalog"
FW_MANIFEST_LIB = ROOT / "Libraries" / "Rdk-HardwareLib" / "Firmware" / "manifest.json"
FW_MANIFEST_BIN = ROOT / "Bin" / "ArduinoFirmware" / "manifest.json"


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"missing catalog source: {SRC}")
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)

    index = json.loads((SRC / "catalog.json").read_text(encoding="utf-8"))
    bundled = []
    for rel in index.get("firmwares", []):
        entry = json.loads((SRC / rel).read_text(encoding="utf-8"))
        if not entry.get("available", True):
            continue
        boards = {}
        for board_key, hex_rel in entry.get("hex", {}).items():
            boards[board_key] = {"hex": hex_rel}
        item = {
            "id": entry["id"],
            "name": entry.get("title", entry["id"]),
            "transport": entry.get("transport", "custom"),
            "boards": boards,
            "runtimeBaud": entry.get("runtimeBaud", 57600),
        }
        if entry.get("defaultPins"):
            item["defaultPins"] = entry["defaultPins"]
        if entry.get("sketch"):
            item["sketch"] = entry["sketch"]
        bundled.append(item)

    manifest = {"bundled": bundled}
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    FW_MANIFEST_LIB.write_text(text, encoding="utf-8")
    FW_MANIFEST_BIN.parent.mkdir(parents=True, exist_ok=True)
    FW_MANIFEST_BIN.write_text(text, encoding="utf-8")
    print(f"synced catalog -> {DST}")
    print(f"updated {FW_MANIFEST_LIB}")
    print(f"updated {FW_MANIFEST_BIN}")


if __name__ == "__main__":
    main()
