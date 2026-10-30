#!/usr/bin/env python3
"""Fail if Watch preset hit-coverage is below threshold."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from watch_formats.composition import load_composition
from watch_formats.coverage import write_coverage_reports


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-hit-coverage", type=float, default=0.95)
    ap.add_argument("--require-ge5-own", action="store_true", default=True)
    args = ap.parse_args()

    composition = load_composition(args.out / "composition.json")
    report = write_coverage_reports(args.out, composition)
    cov = report["hitCoverage"]
    missing = report["missingGe5"]
    print(f"Hit coverage: {cov*100:.1f}% (min {args.min_hit_coverage*100:.1f}%)")
    print(f"Missing ≥5 own files: {len(missing)}")
    ok = cov >= args.min_hit_coverage
    if args.require_ge5_own and missing:
        print("Missing classes:")
        for c in missing:
            print(f"  {c['className']} hits={c['hits']}")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
