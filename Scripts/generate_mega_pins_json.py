#!/usr/bin/env python3
"""Generate mega2560_pins.json with firmataPin and kind for all pins."""

import json
from pathlib import Path

def label_for_pin(pin: int) -> str:
    if pin >= 54:
        return f"A{pin - 54}"
    return f"D{pin}"

def kind_for_pin(pin: int) -> str:
    return "analog" if pin >= 54 else "digital"

def rect_for_pin(pin: int) -> list[float]:
    col = pin % 14
    row = pin // 14
    x = 0.02 + col * 0.068
    y = 0.05 + row * 0.12
    return [round(x, 4), round(y, 4), 0.05, 0.04]

def main() -> None:
    pins = []
    for pin in range(70):
        pins.append(
            {
                "id": label_for_pin(pin),
                "label": label_for_pin(pin),
                "firmataPin": pin,
                "kind": kind_for_pin(pin),
                "rect": rect_for_pin(pin),
            }
        )
    root = {"board": "mega2560", "pins": pins}
    out = Path(__file__).resolve().parents[1] / (
        "Libraries/Rdk-HardwareLib/GUI/Qt/Resources/boards/mega2560_pins.json"
    )
    out.write_text(json.dumps(root, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(pins)} pins)")

if __name__ == "__main__":
    main()
