"""Coverage report: which mined yClass have curated Watch presets."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def curated_classes(presets_root: Path) -> Set[str]:
    skip = {"meta", "draft"}
    out: Set[str] = set()
    if not presets_root.is_dir():
        return out
    for lib in presets_root.iterdir():
        if not lib.is_dir() or lib.name in skip:
            continue
        for f in lib.glob("*.json"):
            out.add(f.stem)
    return out


def load_bindings(bindings_path: Path) -> List[Dict[str, Any]]:
    rows = []
    if not bindings_path.is_file():
        return rows
    with bindings_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def compute_coverage(
    bindings: List[Dict[str, Any]],
    curated: Set[str],
    composition: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    y_hits: Counter = Counter()
    props: Dict[str, Counter] = defaultdict(Counter)
    total_with_class = 0
    covered_hits = 0

    # Classes reachable via family of a curated member
    family_cover: Set[str] = set(curated)
    if composition:
        for members in composition.get("families", {}).values():
            if any(m in curated for m in members):
                family_cover.update(members)
        # parents that only inherit — count as covered for hit metric if child curated
        for parent, slots in composition.get("parents", {}).items():
            if any(s.get("childClass") in curated for s in slots):
                family_cover.add(parent)

    for row in bindings:
        yc = row.get("yClass")
        if not yc:
            continue
        y = row.get("y") or {}
        prop = y.get("property") or ""
        # Numeric-only / unmatched BCB cannot form presets — exclude from coverage denom
        if not prop or row.get("unmatchedProperty"):
            continue
        total_with_class += 1
        y_hits[yc] += 1
        props[yc][prop] += 1
        if yc in curated or yc in family_cover:
            covered_hits += 1

    classes = []
    for cls, hits in y_hits.most_common():
        top = props[cls].most_common(3)
        classes.append(
            {
                "className": cls,
                "hits": hits,
                "curated": cls in curated,
                "reachable": cls in family_cover,
                "topProperties": [{"property": p, "hits": h} for p, h in top],
            }
        )

    missing_ge5 = [c for c in classes if c["hits"] >= 5 and not c["curated"]]
    hit_coverage = (covered_hits / total_with_class) if total_with_class else 1.0

    return {
        "totalSeriesWithClass": total_with_class,
        "coveredHits": covered_hits,
        "hitCoverage": hit_coverage,
        "distinctYClass": len(y_hits),
        "curatedCount": len(curated),
        "missingGe5": missing_ge5,
        "classes": classes,
    }


def write_coverage_reports(presets_root: Path, composition: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    meta = presets_root / "meta"
    bindings = load_bindings(meta / "bindings.jsonl")
    curated = curated_classes(presets_root)
    report = compute_coverage(bindings, curated, composition)
    meta.mkdir(parents=True, exist_ok=True)
    (meta / "coverage.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Watch presets coverage",
        "",
        f"- Series with yClass: **{report['totalSeriesWithClass']}**",
        f"- Hit coverage (curated|family|parent): **{report['hitCoverage']*100:.1f}%**",
        f"- Distinct yClass: **{report['distinctYClass']}**",
        f"- Curated files: **{report['curatedCount']}**",
        f"- Missing own file with ≥5 hits: **{len(report['missingGe5'])}**",
        "",
        "## Classes",
        "",
        "| Class | Hits | Curated | Reachable | Top props |",
        "|-------|------|---------|-----------|-----------|",
    ]
    for c in report["classes"]:
        tops = ", ".join(f"{t['property']}({t['hits']})" for t in c["topProperties"])
        lines.append(
            f"| `{c['className']}` | {c['hits']} | "
            f"{'yes' if c['curated'] else 'no'} | "
            f"{'yes' if c['reachable'] else 'no'} | {tops} |"
        )
    if report["missingGe5"]:
        lines += ["", "## Missing (≥5 hits, no own file)", ""]
        for c in report["missingGe5"]:
            lines.append(f"- `{c['className']}` hits={c['hits']}")
    (meta / "coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
