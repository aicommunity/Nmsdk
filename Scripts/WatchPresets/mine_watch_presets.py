#!/usr/bin/env python3
"""Mine Watch series bindings from Bin/Configs Interface.xml files."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

# Allow running as script from repo root
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from watch_formats.aggregate import aggregate_drafts, annotate_with_classes
from watch_formats.bcb_watch import parse_bcb_watch
from watch_formats.common import parse_xml_file
from watch_formats.composition import load_composition, write_composition_json
from watch_formats.coverage import write_coverage_reports
from watch_formats.qt_watch import parse_qt_mdi, parse_qt_tabs


def project_rel(configs_root: Path, iface: Path) -> str:
    try:
        return str(iface.parent.relative_to(configs_root))
    except ValueError:
        return str(iface.parent)


def parse_interface(iface: Path, project: str):
    try:
        root = parse_xml_file(iface)
    except ET.ParseError as e:
        return [], f"parse_error: {e}"
    graphs = []
    graphs.extend(parse_bcb_watch(root, project))
    graphs.extend(parse_qt_tabs(root, project))
    graphs.extend(parse_qt_mdi(root, project))
    return graphs, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--configs", type=Path, required=True)
    ap.add_argument("--also-backup", type=Path, default=None)
    ap.add_argument("--cldesc", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-hits", type=int, default=3)
    ap.add_argument("--min-hits-internal", type=int, default=2)
    ap.add_argument("--min-cooccur", type=int, default=2)
    args = ap.parse_args()

    roots = [args.configs]
    if args.also_backup and args.also_backup.is_dir():
        roots.append(args.also_backup)

    args.out.mkdir(parents=True, exist_ok=True)
    meta = args.out / "meta"
    meta.mkdir(parents=True, exist_ok=True)

    # Ensure composition map exists at catalog root
    composition_path = args.out / "composition.json"
    if not composition_path.is_file():
        write_composition_json(composition_path)
    composition = load_composition(composition_path)

    all_series: list = []
    format_counts = Counter()
    errors = []
    projects_scanned = 0

    for root in roots:
        for iface in sorted(root.rglob("Interface.xml")):
            projects_scanned += 1
            project = project_rel(root, iface)
            try:
                graphs, err = parse_interface(iface, project)
                if err:
                    errors.append({"project": project, "error": err})
                    continue
                series = []
                for g in graphs:
                    format_counts[g.format] += 1
                    series.extend(g.series)
                if series:
                    annotate_with_classes(series, iface.parent)
                    all_series.extend(series)
            except Exception as e:
                errors.append(
                    {
                        "project": project,
                        "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc(limit=3),
                    }
                )

    # bindings.jsonl
    bindings_path = meta / "bindings.jsonl"
    with bindings_path.open("w", encoding="utf-8") as f:
        for s in all_series:
            f.write(json.dumps(s.to_dict(), ensure_ascii=False) + "\n")

    unmatched = [
        s.to_dict()
        for s in all_series
        if (s.y and not s.y_class) or s.unmatched_property
    ]
    (meta / "unmatched-bindings.json").write_text(
        json.dumps(unmatched[:500], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    report = aggregate_drafts(
        all_series,
        args.cldesc,
        args.out,
        min_hits=args.min_hits,
        min_cooccur=args.min_cooccur,
        min_hits_internal=args.min_hits_internal,
    )
    report["projectsScanned"] = projects_scanned
    report["seriesTotal"] = len(all_series)
    report["formatGraphCounts"] = dict(format_counts)
    report["errors"] = errors[:50]
    report["errorCount"] = len(errors)
    report["unmatchedCount"] = len(unmatched)

    (meta / "mining-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    md_lines = [
        "# Watch presets mining report",
        "",
        f"- Projects scanned: **{projects_scanned}**",
        f"- Series extracted: **{len(all_series)}**",
        f"- Draft classes: **{report['classes']}**",
        f"- Draft presets: **{report['presets']}**",
        f"- Unmatched: **{len(unmatched)}**",
        f"- Errors: **{len(errors)}**",
        "",
        "## Format graph counts",
        "",
    ]
    for k, v in sorted(format_counts.items()):
        md_lines.append(f"- `{k}`: {v}")
    md_lines += ["", "## Top singles", ""]
    for row in report.get("topSingles", [])[:20]:
        md_lines.append(
            f"- `{row['class']}` `{row['path'] or '.'}`.`{row['property']}` hits={row['hits']}"
        )
    md_lines += ["", "## Top multi", ""]
    for row in report.get("topMulti", [])[:15]:
        md_lines.append(
            f"- `{row['class']}` {row['signature']} hits={row['hits']}"
        )
    (meta / "mining-report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    cov = write_coverage_reports(args.out, composition)
    print(f"Wrote {bindings_path}")
    print(f"Draft presets under {args.out / 'draft'}")
    print(f"Report: {meta / 'mining-report.md'}")
    print(f"Coverage: {meta / 'coverage.md'} ({cov['hitCoverage']*100:.1f}%)")
    return 0 if not errors else 0  # non-fatal errors


if __name__ == "__main__":
    raise SystemExit(main())
