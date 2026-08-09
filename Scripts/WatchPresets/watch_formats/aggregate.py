"""Aggregate normalized series into draft preset JSON files."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

from .common import NormalizedSerie
from .cldesc_libs import build_class_to_library
from .model_map import common_anchor, deepest_class, load_project_class_map


def _slug(parts: Sequence[str]) -> str:
    raw = "_".join(p for p in parts if p)
    raw = re.sub(r"[^A-Za-z0-9_]+", "_", raw)
    raw = re.sub(r"_+", "_", raw).strip("_").lower()
    return raw or "preset"


def annotate_with_classes(
    series: List[NormalizedSerie], project_dir: Path
) -> None:
    class_map = load_project_class_map(project_dir)
    # group by graph for anchors
    by_graph: Dict[Tuple[str, str, str], List[NormalizedSerie]] = defaultdict(list)
    for s in series:
        by_graph[(s.project, s.container, s.graph_id)].append(s)

    for _key, group in by_graph.items():
        y_names = [s.y.long_name for s in group if s.y and s.y.long_name]
        anchor_long, anchor_class = common_anchor(y_names, class_map)
        for s in group:
            if not s.y:
                continue
            y_class, prefix, rel = deepest_class(s.y.long_name, class_map)
            s.y_class = y_class
            if anchor_long and s.y.long_name.startswith(anchor_long):
                s.anchor_long_name = anchor_long
                s.anchor_class = anchor_class
                rest = s.y.long_name[len(anchor_long) :].lstrip(".")
                s.rel_path = rest
            else:
                s.anchor_long_name = prefix
                s.anchor_class = y_class
                s.rel_path = rel


def aggregate_drafts(
    all_series: List[NormalizedSerie],
    cldesc_root: Path,
    out_root: Path,
    min_hits: int = 3,
    min_cooccur: int = 2,
) -> Dict[str, Any]:
    lib_map = build_class_to_library(cldesc_root)
    single: Counter = Counter()
    single_examples: Dict[Tuple[str, str, str], List[str]] = defaultdict(list)
    single_formats: Dict[Tuple[str, str, str], set] = defaultdict(set)

    # (anchor_class, frozenset of (relPath, property)) -> count
    multi: Counter = Counter()
    multi_examples: Dict[Any, List[str]] = defaultdict(list)
    multi_formats: Dict[Any, set] = defaultdict(set)
    multi_series_map: Dict[Any, List[Tuple[str, str, int, int]]] = {}

    by_graph: Dict[Tuple[str, str, str], List[NormalizedSerie]] = defaultdict(list)
    for s in all_series:
        by_graph[(s.project, s.container, s.graph_id)].append(s)
        if s.y and s.y_class and s.y.property and not s.unmatched_property:
            # single keyed by leaf class + rel from leaf (usually "")
            key = (s.y_class, "", s.y.property)
            # Prefer path relative to leaf: always "" for deepest class property
            single[key] += 1
            if len(single_examples[key]) < 5:
                single_examples[key].append(s.project)
            single_formats[key].add(s.format)

            if s.anchor_class and s.rel_path is not None:
                key2 = (s.anchor_class, s.rel_path, s.y.property)
                if s.anchor_class != s.y_class or s.rel_path:
                    single[key2] += 1
                    if len(single_examples[key2]) < 5:
                        single_examples[key2].append(s.project)
                    single_formats[key2].add(s.format)

    for _key, group in by_graph.items():
        if len(group) < 2:
            continue
        anchor = group[0].anchor_class
        if not anchor or any(s.anchor_class != anchor for s in group):
            continue
        sig_list = []
        for s in group:
            if not s.y or not s.y.property or s.unmatched_property:
                continue
            sig_list.append((s.rel_path, s.y.property, s.y.jx, s.y.jy))
        if len(sig_list) < 2:
            continue
        frozen = frozenset((p, prop) for p, prop, _jx, _jy in sig_list)
        mkey = (anchor, frozen)
        multi[mkey] += 1
        multi_series_map[mkey] = sig_list
        if len(multi_examples[mkey]) < 5:
            multi_examples[mkey].append(group[0].project)
        multi_formats[mkey].add(group[0].format)

    # Build per-class draft files
    drafts: Dict[str, Dict[str, Any]] = {}

    def ensure_class(class_name: str) -> Dict[str, Any]:
        if class_name not in drafts:
            lib = lib_map.get(class_name, "Unassigned")
            drafts[class_name] = {
                "schemaVersion": 1,
                "library": lib,
                "className": class_name,
                "presets": [],
            }
        return drafts[class_name]

    for (anchor, frozen), count in multi.most_common():
        if count < min_cooccur:
            continue
        doc = ensure_class(anchor)
        series_specs = []
        seen = set()
        for path, prop, jx, jy in multi_series_map[(anchor, frozen)]:
            t = (path, prop)
            if t in seen:
                continue
            seen.add(t)
            series_specs.append(
                {"path": path, "property": prop, "jx": jx, "jy": jy}
            )
        title_bits = [
            f"{s['path'] + '.' if s['path'] else ''}{s['property']}"
            for s in series_specs
        ]
        pid = _slug(["multi"] + title_bits)
        doc["presets"].append(
            {
                "id": pid,
                "title": " + ".join(title_bits),
                "description": f"Auto-mined co-occurrence (hits={count})",
                "vizKind": "TimeSeries",
                "series": series_specs,
                "evidence": {
                    "hitCount": count,
                    "formats": sorted(multi_formats[(anchor, frozen)]),
                    "exampleProjects": multi_examples[(anchor, frozen)],
                },
            }
        )

    for (cls, path, prop), count in single.most_common():
        if count < min_hits:
            continue
        doc = ensure_class(cls)
        # skip if already covered as lone series of a multi with same id
        pid = _slug([path, prop])
        if any(p["id"] == pid for p in doc["presets"]):
            continue
        # skip singles that are exact one-item subset of existing multi? keep for leaf UX
        doc["presets"].append(
            {
                "id": pid,
                "title": f"{path + '.' if path else ''}{prop}",
                "description": f"Auto-mined property (hits={count})",
                "vizKind": "TimeSeries",
                "series": [{"path": path, "property": prop, "jx": 0, "jy": 0}],
                "evidence": {
                    "hitCount": count,
                    "formats": sorted(single_formats[(cls, path, prop)]),
                    "exampleProjects": single_examples[(cls, path, prop)],
                },
            }
        )

    # Write draft tree
    draft_root = out_root / "draft"
    for class_name, doc in drafts.items():
        lib = doc["library"]
        dest_dir = draft_root / lib
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / f"{class_name}.json"
        path.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    report = {
        "classes": len(drafts),
        "presets": sum(len(d["presets"]) for d in drafts.values()),
        "singleKeys": sum(1 for _, c in single.items() if c >= min_hits),
        "multiKeys": sum(1 for _, c in multi.items() if c >= min_cooccur),
        "topSingles": [
            {"class": a, "path": b, "property": c, "hits": n}
            for (a, b, c), n in single.most_common(30)
        ],
        "topMulti": [
            {
                "class": a,
                "signature": sorted(list(f)),
                "hits": n,
            }
            for (a, f), n in multi.most_common(20)
        ],
    }
    return report
