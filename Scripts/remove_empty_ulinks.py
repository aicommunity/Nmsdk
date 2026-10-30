#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility to remove ULink elements with empty Item (source component) from specific Model_00.xml files.

Target configs (from plan):
 - Bin/Configs/!OldConfigs/NewCodeTest/Model_00.xml
 - Bin/Configs/!OldConfigs/NewCodeTest1/Model_00.xml
 - Bin/Configs/!OldConfigs/SpikeANPA1+2/Model_00.xml
 - Bin/Configs/!OldConfigs/SpikeEEG/Model_00.xml
"""

from pathlib import Path
import xml.etree.ElementTree as ET


TARGET_FILES = [
    Path("Bin/Configs/!OldConfigs/NewCodeTest/Model_00.xml"),
    Path("Bin/Configs/!OldConfigs/NewCodeTest1/Model_00.xml"),
    Path("Bin/Configs/!OldConfigs/SpikeANPA1+2/Model_00.xml"),
    Path("Bin/Configs/!OldConfigs/SpikeEEG/Model_00.xml"),
]


def is_empty_item(elem: ET.Element) -> bool:
    """
    Return True if elem is <elem Type="ULink"> whose first <Item> child
    has empty or whitespace-only text.
    """
    if elem.tag != "elem" or elem.get("Type") != "ULink":
        return False
    # find first direct Item child
    for child in list(elem):
        if child.tag == "Item":
            text = (child.text or "").strip()
            return text == ""
    return False


def process_file(path: Path) -> bool:
    if not path.exists():
        return False

    tree = ET.parse(path)
    root = tree.getroot()
    removed = 0

    # Walk all parents and remove matching child elems
    for parent in root.iter():
        children = list(parent)
        for child in children:
            if is_empty_item(child):
                parent.remove(child)
                removed += 1

    if removed:
        tree.write(path, encoding="utf-8", xml_declaration=True)
    print(f"{path}: removed {removed} empty-source ULink(s)")
    return True


def main() -> None:
    for rel in TARGET_FILES:
        path = Path(rel)
        process_file(path)


if __name__ == "__main__":
    main()

