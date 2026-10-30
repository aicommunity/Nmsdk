#!/usr/bin/env python3
"""Build E1.1 timing library TSV: cable_model L=1..100 + Console anchors from C1/E1_0 kernels.

Usage:
  python3 e1_1_timing_library.py [--reports DIR] [--out TSV]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

TL_REVIEW = Path(__file__).resolve().parents[2]
CABLE_DIR = TL_REVIEW / "plans/AGENT_PLAN_2026-10-20/tools/cable_model"
SIM = os.environ.get("CABLE_SIM", str(CABLE_DIR / "cable"))

MODELS = {
    "NSPNeuronGen": {"tau_s": 0.01, "D_s": 0.005, "f_hz": 2000, "Rs": 8.6e7},
    "NSPNeuronGenAsymRmD001C1e9": {
        "tau_s": 0.01,
        "D_s": 0.001,
        "f_hz": 20000,
        "Rs": 8.6e7,
    },
}

KERNEL_GLOBS = [
    "C1_20261020_11/kernel_1.json",
    "C1_20261020_11/kernel_2.json",
    "C1_20261020_11/kernel_4.json",
    "E1_0_20261022/kernel_gen_grid.json",
    "E1_0_20261022/kernel_asym_L50_w11.json",
]


def sim_kernel(L: int, tau: float, D: float, f: float, Rm: float = 1e7) -> np.ndarray:
    sub = 2
    C = tau / Rm
    T = min(4.0, 0.03 + L * tau + 8 * tau * (L**0.5) + 0.05)
    inp = f"{L}\n1\n{L} 8.6e7 1 0.0\n"
    out = subprocess.run(
        [SIM, str(f), str(C), str(Rm), str(D), "0.001", "0.001", str(T), str(sub)],
        input=inp,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return np.array(out.split(), float)


def timing_row(K: np.ndarray, f: float) -> tuple[float, float, float]:
    dt = 2.0 / f
    peak = float(K.max())
    t_peak = float(K.argmax() * dt)
    half = K.max() / 2
    idx = np.where(K >= half)[0]
    fwhm = float((idx[-1] - idx[0]) * dt) if len(idx) else float("nan")
    return peak, t_peak, fwhm


def model_grid(name: str, Lmax: int = 100) -> dict[int, dict]:
    p = MODELS[name]
    f, tau, D = p["f_hz"], p["tau_s"], p["D_s"]
    rows = {}
    for L in range(1, Lmax + 1):
        K = sim_kernel(L, tau, D, f)
        peak, t_peak, fwhm = timing_row(K, f)
        rows[L] = {
            "peak_model": peak,
            "t_peak_ms": t_peak * 1000,
            "fwhm_ms": fwhm * 1000,
        }
    return rows


def load_console_anchors(report_dir: Path) -> dict[str, dict[int, dict]]:
    """NeuronModel -> L -> {peak, t_peak_ms, fwhm_ms, source, silent}."""
    by_model: dict[str, dict[int, dict]] = {}
    for rel in KERNEL_GLOBS:
        path = report_dir / rel
        if not path.is_file():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        # infer model from tau/D/f
        tau, D, f = d["tau_s"], d["D_s"], d["f_hz"]
        if D == 0.005 and f == 2000:
            model = "NSPNeuronGen"
        elif D == 0.001 and f == 20000:
            model = "NSPNeuronGenAsymRmD001C1e9"
        else:
            continue
        by_model.setdefault(model, {})
        for x in d["dendrites"]:
            L = int(x["L"])
            c = x["compare"]
            meas_peak = c["peak"]["measured"]
            silent = meas_peak in (0, None) or (
                c["peak"]["rel_err"] is not None and c["peak"]["rel_err"] <= -0.99
            )
            t_m = c["t_peak_s"]["measured"]
            f_m = c["fwhm_s"]["measured"]
            entry = {
                "peak_console": meas_peak,
                "peak_model_json": c["peak"]["predicted"],
                "t_peak_ms_console": t_m * 1000 if t_m is not None else None,
                "fwhm_ms_console": f_m * 1000 if f_m is not None else None,
                "source_json": rel,
                "silent": silent,
            }
            # prefer non-silent re-measure; E1_0 over C1 for same L
            prev = by_model[model].get(L)
            if prev is None or (prev["silent"] and not silent):
                by_model[model][L] = entry
            elif not prev["silent"] and silent:
                pass
            elif "E1_0" in rel:
                by_model[model][L] = entry
    return by_model


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--reports",
        type=Path,
        default=Path.home() / "TLAgent-20261020/agent-reports",
    )
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--Lmax", type=int, default=100)
    args = ap.parse_args()

    anchors = load_console_anchors(args.reports)
    lines = [
        "NeuronModel\tL\tt_peak_ms\tFWHM_ms\tpeak_console\tpeak_model\t"
        "t_peak_source\tFWHM_source\tpeak_source\tconsole_json"
    ]

    for model in MODELS:
        grid = model_grid(model, args.Lmax)
        for L in range(1, args.Lmax + 1):
            g = grid[L]
            a = anchors.get(model, {}).get(L)
            if a and not a["silent"]:
                t_src = "console+model"
                t_val = g["t_peak_ms"]
                if a["t_peak_ms_console"] is not None:
                    t_val = a["t_peak_ms_console"]
                fw_src = "console+model"
                fw_val = g["fwhm_ms"]
                if a["fwhm_ms_console"] is not None:
                    fw_val = a["fwhm_ms_console"]
                pk_c = a["peak_console"]
                pk_src = "console+model"
                json_ref = a["source_json"]
            elif a and a["silent"]:
                t_src = "model_only(E1.0_invalid_console)"
                t_val = g["t_peak_ms"]
                fw_src = t_src
                fw_val = g["fwhm_ms"]
                pk_c = ""
                pk_src = "model_only(silent_console)"
                json_ref = a["source_json"]
            else:
                t_src = "model_only(E1.0_timing_proxy)"
                t_val = g["t_peak_ms"]
                fw_src = t_src
                fw_val = g["fwhm_ms"]
                pk_c = ""
                pk_src = "model_only"
                json_ref = ""

            lines.append(
                f"{model}\t{L}\t{t_val:.4f}\t{fw_val:.4f}\t{pk_c}\t{g['peak_model']:.10f}\t"
                f"{t_src}\t{fw_src}\t{pk_src}\t{json_ref}"
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)-1} rows -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
