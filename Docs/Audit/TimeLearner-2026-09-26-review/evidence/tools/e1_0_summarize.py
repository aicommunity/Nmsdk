#!/usr/bin/env python3
"""Aggregate E1.0 cable_model vs Console kernel JSONs (5% tolerance on peak, t_peak, FWHM).

Expects tl-agent agent-reports from C1 (2026-10-20) and E1_0 (2026-10-22) runs.
Usage:
  python3 e1_0_summarize.py [--reports DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TOL = 0.05

# L -> (json path relative to reports dir, dendrite index 1..4)
GEN = {
    1: ("C1_20261020_11/kernel_2.json", 4),
    4: ("E1_0_20261022/kernel_gen_grid.json", 2),
    10: ("C1_20261020_11/kernel_2.json", 3),
    25: ("E1_0_20261022/kernel_gen_grid.json", 3),
    50: ("E1_0_20261022/kernel_gen_grid.json", 1),
}
ASYM = {
    1: ("C1_20261020_11/kernel_4.json", 4),
    4: ("C1_20261020_11/kernel_4.json", 3),
    10: ("C1_20261020_11/kernel_4.json", 2),
    25: ("C1_20261020_11/kernel_4.json", 1),
    50: ("E1_0_20261022/kernel_asym_L50_w11.json", 1),
}


def load_row(report_dir: Path, rel: str, dend: int) -> dict:
    d = json.loads((report_dir / rel).read_text(encoding="utf-8"))
    x = next(y for y in d["dendrites"] if y["dendrite"] == dend)
    c = x["compare"]
    silent = c["peak"]["measured"] in (0, None) or (
        c["peak"]["rel_err"] is not None and c["peak"]["rel_err"] <= -0.99
    )
    ok = not silent
    for key in ("peak", "t_peak_s", "fwhm_s"):
        re_ = c[key]["rel_err"]
        if re_ is None or c[key]["predicted"] in (None, 0) or c[key]["measured"] is None:
            ok = False
        elif abs(re_) > TOL:
            ok = False
    return {"L": x["L"], "silent": silent, "e1_0_row_ok": ok, "compare": c, "source": rel}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--reports",
        type=Path,
        default=Path.home() / "TLAgent-20261020/agent-reports",
    )
    args = ap.parse_args()
    for name, spec in ("NSPNeuronGen", GEN), ("NSPNeuronGenAsymRmD001C1e9", ASYM):
        print(f"\n=== {name} (tol={TOL:.0%}) ===")
        for L in sorted(spec):
            rel, dend = spec[L]
            r = load_row(args.reports, rel, dend)
            c = r["compare"]
            if r["silent"]:
                print(f"L={L}: SILENT/INVALID ({rel})")
                continue
            print(
                f"L={L}: peak {c['peak']['rel_err']:+.2%} "
                f"t_peak {c['t_peak_s']['rel_err']:+.2%} "
                f"fwhm {c['fwhm_s']['rel_err']:+.2%} "
                f"{'OK' if r['e1_0_row_ok'] else 'FAIL'}"
            )


if __name__ == "__main__":
    main()
