"""Build longName → className map from Model_00.xml / model.xml."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Structural containers that must not appear in component long names.
SKIP_PATH_TAGS = {
    "Parameters",
    "Links",
    "Components",
    "elem",
    "Item",
    "Connector",
    "Save",
}


def _walk(el: ET.Element, path: List[str], out: Dict[str, str]) -> None:
    tag = el.tag.split("}")[-1] if "}" in el.tag else el.tag
    class_attr = el.attrib.get("Class")
    next_path = path

    if class_attr is not None and tag not in SKIP_PATH_TAGS and tag not in ("Model",):
        # Component instance node
        next_path = path + [tag]
        long_name = ".".join(next_path)
        out[long_name] = class_attr
    elif tag in ("Components",) or tag in SKIP_PATH_TAGS:
        next_path = path
    elif tag == "Model":
        next_path = path
    else:
        # Non-class nested tags under a component (rare) — do not extend path
        # unless they look like components without Class (skip)
        next_path = path

    for child in list(el):
        ctag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if ctag in ("Parameters", "Links"):
            continue
        _walk(child, next_path, out)


def load_class_map_from_xml(path: Path) -> Dict[str, str]:
    from .common import sanitize_numeric_tags

    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
        root = ET.fromstring(sanitize_numeric_tags(raw))
    except ET.ParseError:
        return {}
    out: Dict[str, str] = {}
    model = None
    tag0 = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    if tag0 == "Model":
        model = root
    else:
        for el in root.iter():
            tag = el.tag.split("}")[-1]
            if tag == "Model":
                model = el
                break
    if model is None:
        model = root
    _walk(model, [], out)
    return out


def find_model_files(project_dir: Path) -> List[Path]:
    found: List[Path] = []
    # Prefer Model_00, Model_01, ...
    numbered = sorted(project_dir.glob("Model_*.xml"))
    found.extend(numbered)
    legacy = project_dir / "model.xml"
    if legacy.is_file() and legacy not in found:
        found.append(legacy)
    return found


def load_project_class_map(project_dir: Path) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    for f in find_model_files(project_dir):
        m = load_class_map_from_xml(f)
        # later files don't override earlier (Model_00 first)
        for k, v in m.items():
            merged.setdefault(k, v)
    return merged


def deepest_class(
    long_name: str, class_map: Dict[str, str]
) -> Tuple[str, str, str]:
    """Return (className, matchedPrefix, relPathAfterPrefix)."""
    if not long_name:
        return "", "", ""
    if long_name in class_map:
        return class_map[long_name], long_name, ""
    parts = long_name.split(".")
    for i in range(len(parts) - 1, 0, -1):
        prefix = ".".join(parts[:i])
        if prefix in class_map:
            return class_map[prefix], prefix, ".".join(parts[i:])
    return "", "", ""


def common_anchor(
    long_names: List[str], class_map: Dict[str, str]
) -> Tuple[str, str]:
    """Largest common prefix present in class_map. Returns (anchorLong, anchorClass)."""
    names = [n for n in long_names if n]
    if not names:
        return "", ""
    split = [n.split(".") for n in names]
    min_len = min(len(s) for s in split)
    common: List[str] = []
    for i in range(min_len):
        token = split[0][i]
        if all(s[i] == token for s in split):
            common.append(token)
        else:
            break
    # shrink until in class_map
    while common:
        prefix = ".".join(common)
        if prefix in class_map:
            return prefix, class_map[prefix]
        common.pop()
    # try each name's deepest alone — no shared anchor
    return "", ""
