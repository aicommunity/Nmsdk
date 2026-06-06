#!/usr/bin/env python3
"""Migrate legacy HardwareLib ClassName values in Model XML files."""
import re
import sys
from pathlib import Path

REPLACEMENTS = [
    (re.compile(r'ClassName="Arduino"'), 'ClassName="ArduinoSensorSketch"'),
    (re.compile(r'<PortToConnect>'), '<PortName>'),
    (re.compile(r'</PortToConnect>'), '</PortName>'),
    (re.compile(r'ClassName="ADC"'), 'ClassName="ArduinoAdc"'),
    (re.compile(r'ClassName="DC"'), 'ClassName="ArduinoDcDemo"'),
]


def migrate_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    original = text
    for pattern, repl in REPLACEMENTS:
        text = pattern.sub(repl, text)
    if text != original:
        path.write_text(text, encoding='utf-8')
        return True
    return False


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('Bin/Configs')
    changed = 0
    for xml in root.rglob('*.xml'):
        if migrate_file(xml):
            print('updated', xml)
            changed += 1
    print('files changed:', changed)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
