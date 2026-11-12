#!/usr/bin/env python3
"""Promote draft Watch preset JSON into curated library folders."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from watch_formats.coverage import curated_classes, load_bindings
from watch_formats.cldesc_libs import build_class_to_library


def _human_title(prop: str, path: str) -> str:
    base = prop
    if path:
        return f"{path} {prop}"
    # CamelCase → words
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", base)
    return spaced


def promote_class(draft_doc: dict, max_presets: int = 4) -> dict:
    presets = sorted(
        draft_doc.get("presets", []),
        key=lambda p: -(p.get("evidence", {}) or {}).get("hitCount", 0),
    )
    out_presets = []
    for p in presets[:max_presets]:
        series = p.get("series") or []
        if not series:
            continue
        # Skip huge multi with >4 series unless hitCount high
        if len(series) > 4 and (p.get("evidence") or {}).get("hitCount", 0) < 3:
            continue
        path0 = series[0].get("path") or ""
        prop0 = series[0].get("property") or ""
        title = p.get("title") or _human_title(prop0, path0)
        if title.startswith("multi_") or " + " in title and len(title) > 80:
            title = " + ".join(
                f"{s.get('path') + '.' if s.get('path') else ''}{s.get('property')}"
                for s in series[:3]
            )
            if len(series) > 3:
                title += f" +{len(series)-3}"
        out_presets.append(
            {
                "id": p.get("id") or "preset",
                "title": title[:120],
                "description": p.get("description")
                or f"Promoted from mining ({(p.get('evidence') or {}).get('hitCount', 0)} hits).",
                "vizKind": p.get("vizKind") or "TimeSeries",
                "series": series,
                "evidence": p.get("evidence") or {},
            }
        )
    return {
        "schemaVersion": 1,
        "library": draft_doc.get("library") or "Unassigned",
        "className": draft_doc.get("className"),
        "presets": out_presets,
    }


def thin_from_bindings(class_name: str, lib: str, bindings: list, max_props: int = 2):
    from collections import Counter

    props = Counter()
    for row in bindings:
        if row.get("yClass") != class_name:
            continue
        y = row.get("y") or {}
        prop = y.get("property") or ""
        if prop:
            props[prop] += 1
    if not props:
        return None
    presets = []
    for prop, hits in props.most_common(max_props):
        presets.append(
            {
                "id": re.sub(r"[^A-Za-z0-9_]+", "_", prop).strip("_").lower() or "prop",
                "title": _human_title(prop, ""),
                "description": f"Top watched property (hits={hits}).",
                "vizKind": "TimeSeries",
                "series": [{"path": "", "property": prop, "jx": 0, "jy": 0}],
                "evidence": {"hitCount": hits, "formats": [], "exampleProjects": []},
            }
        )
    return {
        "schemaVersion": 1,
        "library": lib,
        "className": class_name,
        "presets": presets,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True, help="Bin/WatchPresets root")
    ap.add_argument("--cldesc", type=Path, required=True)
    ap.add_argument("--min-hits", type=int, default=1)
    ap.add_argument("--force", action="store_true", help="Overwrite existing curated")
    args = ap.parse_args()

    draft_root = args.out / "draft"
    bindings = load_bindings(args.out / "meta" / "bindings.jsonl")
    lib_map = build_class_to_library(args.cldesc)
    existing = curated_classes(args.out)

    from collections import Counter

    y_hits = Counter()
    for row in bindings:
        yc = row.get("yClass")
        if yc:
            y_hits[yc] += 1

    written = 0
    for cls, hits in y_hits.most_common():
        if hits < args.min_hits:
            continue
        if cls in existing and not args.force:
            continue
        # Need at least one named property in bindings
        has_prop = any(
            ((row.get("y") or {}).get("property") or "")
            and not row.get("unmatchedProperty")
            and row.get("yClass") == cls
            for row in bindings
        )
        if not has_prop:
            continue
        lib = lib_map.get(cls, "Unassigned")
        draft_path = draft_root / lib / f"{cls}.json"
        if not draft_path.is_file():
            # try any lib folder
            found = list(draft_root.glob(f"*/{cls}.json"))
            draft_path = found[0] if found else None
        if draft_path and draft_path.is_file():
            doc = promote_class(json.loads(draft_path.read_text(encoding="utf-8")))
        else:
            doc = thin_from_bindings(cls, lib, bindings)
        if not doc or not doc.get("presets"):
            continue
        dest_dir = args.out / doc["library"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{cls}.json"
        dest.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written += 1
        print(f"Wrote {dest.relative_to(args.out)} (hits={hits})")

    print(f"Promoted {written} class files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
