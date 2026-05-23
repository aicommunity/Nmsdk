#!/usr/bin/env python3
"""
Миграция старых имен компонентов PulseLib в XML-конфигах.

Цель: заменить PosChannel/NegChannel на InhChannel/ExcChannel корректно, опираясь на знак параметра Type.
Важно: нельзя маппить по имени (Pos/Neg) — в архивах встречается инверсия. Надежное правило:
  - канал с Type > 0  -> InhChannel
  - канал с Type < 0  -> ExcChannel

Обрабатывает:
  - model.xml (Save/Model/Links + Components)
  - Parameters.xml (SaveProperties/Model/Components)

По умолчанию делает резервные копии рядом: *.bak-YYYYmmdd_HHMMSS
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def backup_file(path: Path) -> None:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(path.name + f".bak-{ts}")
    shutil.copy2(path, backup)


def parse_float(text: str | None) -> float | None:
    if text is None:
        return None
    t = text.strip().replace(",", ".")
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def find_channel_type(channel_elem: ET.Element) -> float | None:
    # Expected: <Parameters><Type>...</Type></Parameters>
    params = channel_elem.find("Parameters")
    if params is None:
        return None
    t_elem = params.find("Type")
    if t_elem is None:
        return None
    return parse_float(t_elem.text)


def decide_mapping(pos_type: float | None, neg_type: float | None) -> dict[str, str]:
    """
    Returns mapping for element/tag names and link path fragments:
      {"PosChannel": "ExcChannel" or "InhChannel", "NegChannel": "..."}
    """
    mapping: dict[str, str] = {}

    def name_for_type(t: float | None) -> str | None:
        if t is None:
            return None
        if t > 0:
            return "InhChannel"
        if t < 0:
            return "ExcChannel"
        return None

    pos_new = name_for_type(pos_type)
    neg_new = name_for_type(neg_type)

    # Fallbacks (should be rare): keep old if cannot decide
    mapping["PosChannel"] = pos_new or "PosChannel"
    mapping["NegChannel"] = neg_new or "NegChannel"
    return mapping


def rename_channel_tags(container: ET.Element) -> dict[str, str] | None:
    """
    Find PosChannel/NegChannel direct children under <Components> of a membrane, decide mapping by Type,
    and rename tags accordingly.
    Returns mapping used or None if no legacy channels found.
    """
    comps = container.find("Components")
    if comps is None:
        return None

    pos = None
    neg = None
    for child in list(comps):
        if child.tag == "PosChannel":
            pos = child
        elif child.tag == "NegChannel":
            neg = child

    if pos is None and neg is None:
        return None

    mapping = decide_mapping(find_channel_type(pos) if pos is not None else None,
                             find_channel_type(neg) if neg is not None else None)

    # Rename tags in-place (ElementTree supports changing .tag)
    if pos is not None:
        pos.tag = mapping["PosChannel"]
    if neg is not None:
        neg.tag = mapping["NegChannel"]

    return mapping


def replace_text_paths(elem: ET.Element, mapping: dict[str, str]) -> None:
    """
    Replace occurrences in text nodes:
      .PosChannel -> .<mapped>
      .NegChannel -> .<mapped>
    and also path fragments without dot if present (rare).
    """
    # Precompile replacements for speed and correctness
    rep = [
        (".PosChannel", "." + mapping["PosChannel"]),
        (".NegChannel", "." + mapping["NegChannel"]),
        ("PosChannel.", mapping["PosChannel"] + "."),
        ("NegChannel.", mapping["NegChannel"] + "."),
    ]

    for node in elem.iter():
        if node.text:
            text = node.text
            for a, b in rep:
                text = text.replace(a, b)
            node.text = text
        if node.tail:
            tail = node.tail
            for a, b in rep:
                tail = tail.replace(a, b)
            node.tail = tail


def migrate_one_xml(path: Path) -> bool:
    tree = ET.parse(path)
    root = tree.getroot()

    changed = False
    mappings_used: list[dict[str, str]] = []

    # Traverse all components; whenever we see a container with legacy channels, rename them and collect mapping.
    for model in root.findall(".//Model"):
        for container in model.iter():
            mapping = rename_channel_tags(container)
            if mapping:
                mappings_used.append(mapping)
                changed = True

    # If multiple mappings differ inside one file, we still can safely do text replacement
    # by applying replacements conservatively per mapping (order matters only if mapping keeps old names).
    if mappings_used:
        for mapping in mappings_used:
            replace_text_paths(root, mapping)

    if changed:
        backup_file(path)
        tree.write(path, encoding="utf-8", xml_declaration=False)

    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="Paths to model.xml/Parameters.xml or directories containing them")
    args = ap.parse_args()

    files: list[Path] = []
    for p in args.paths:
        path = Path(p)
        if path.is_dir():
            # Рекурсивно ищем стандартные имена файлов в подкаталогах конфигураций
            for name in ("model.xml", "Parameters.xml"):
                files.extend(sorted(path.rglob(name)))
        else:
            if path.exists():
                files.append(path)

    if not files:
        print("No files found to migrate.", file=sys.stderr)
        return 2

    any_changed = False
    for f in files:
        try:
            changed = migrate_one_xml(f)
            print(f"{'CHANGED' if changed else 'OK'}: {f}")
            any_changed |= changed
        except Exception as e:
            print(f"ERROR: {f}: {e}", file=sys.stderr)
            return 1

    return 0 if any_changed else 0


if __name__ == "__main__":
    raise SystemExit(main())

