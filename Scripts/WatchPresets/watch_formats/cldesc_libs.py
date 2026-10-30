"""ClDesc library folder lookup for class → library name."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


def build_class_to_library(cldesc_root: Path) -> Dict[str, str]:
    """Map ClassName → library folder (e.g. PulseLibrary)."""
    mapping: Dict[str, str] = {}
    if not cldesc_root.is_dir():
        return mapping
    for lib_dir in sorted(cldesc_root.iterdir()):
        if not lib_dir.is_dir():
            continue
        # Bin/ClDesc/PulseLibrary/ru-RU/*.xml
        for xml in lib_dir.rglob("*.xml"):
            name = xml.stem
            mapping.setdefault(name, lib_dir.name)
    return mapping
