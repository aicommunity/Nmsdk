#!/usr/bin/env python3
"""E1.1c scoped FastSpan library: L=1..100 timing + Rs×8 + N multiplicity (offline cable).

NeuronModel (matrix FastSpan / SelectivityBranchFastSpan / FastSpanLtzCal gen):
  NSPNeuronGenD002C25e11 — τ=Rm·C=2.5 ms (C=2.5e-10, Rm=1e7), D=2 ms, f=2000 Hz.
Preinh class NSPNeuronGenPreinh2_5D002C25e11 shares the same passive excitatory cable
params for a single tip EPSP; not swept separately here.

Reset-before-pulse: each (L, Rs|N) is an independent cable run from rest.
No Console amp calibration for FastSpan in E1.0 → peak_calibrated = peak_model
(cal_mode=none_pending_console). Timing is model_only (C2 OK for τ=2.5/D=2).

Usage:
  python3 e1_1c_fastspan_library.py --out ../E1_1c_FASTSPAN_LIBRARY_2026-10-22.tsv
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

TL_REVIEW = Path(__file__).resolve().parents[2]
CABLE_DIR = TL_REVIEW / "plans/AGENT_PLAN_2026-10-20/tools/cable_model"
SIM = os.environ.get("CABLE_SIM", str(CABLE_DIR / "cable"))

RS_GRID = np.geomspace(2.0e6, 8.6e7, 8)
N_GRID = (1, 2, 4, 8, 16, 32, 64, 128)
L_TIMING = range(1, 101)
L_RS = (1, 10, 25)  # truncated vs E1.1b (no L=50)
L_N = (1, 10, 25)

# Canonical matrix FastSpan kinetics (SelectivityFastSpan / BranchFastSpan / FastSpanLtzCal)
MODELS = {
    "NSPNeuronGenD002C25e11": {
        "tau_s": 0.0025,
        "D_s": 0.002,
        "f_hz": 2000,
        "Rm": 1e7,
        "cal_mode": "none_pending_console",
        "cal_factor": 1.0,
        "notes_base": "FastSpan; C=2.5e-10 Rm=1e7; Project.ini 2000 Hz",
    },
}


def sim_kernel(
    L: int,
    Rs: float,
    *,
    tau: float,
    D: float,
    f: float,
    Rm: float,
    Nsyn: int = 1,
) -> np.ndarray:
    sub = 2
    C = tau / Rm
    T = min(4.0, 0.03 + L * tau + 8 * tau * (L**0.5) + 0.05)
    lines = [str(L), str(Nsyn)]
    for _ in range(Nsyn):
        lines.append(f"{L} {Rs} 1 0.0")
    inp = "\n".join(lines) + "\n"
    out = subprocess.run(
        [SIM, str(f), str(C), str(Rm), str(D), "0.001", "0.001", str(T), str(sub)],
        input=inp,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return np.array(out.split(), float)


def metrics(K: np.ndarray, f: float) -> tuple[float, float, float]:
    dt = 2.0 / f
    peak = float(K.max())
    t_peak_ms = float(K.argmax() * dt * 1000.0)
    half = K.max() / 2.0
    idx = np.where(K >= half)[0]
    fwhm_ms = float((idx[-1] - idx[0]) * dt * 1000.0) if len(idx) else float("nan")
    return peak, t_peak_ms, fwhm_ms


def gamma_vs_L1(peak_L: float, peak_1: float, L: int) -> float | str:
    if L <= 1 or peak_L <= 0 or peak_1 <= 0:
        return ""
    return float(-np.log(peak_L / peak_1) / (L - 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    if not Path(SIM).is_file():
        print(f"Missing cable binary: {SIM} (gcc -O2 -o cable cable.c -lm)", file=sys.stderr)
        sys.exit(1)

    header = (
        "slice\tNeuronModel\tL\tTipR\tN\tpeak_model\tpeak_calibrated\t"
        "t_peak_ms\tFWHM_ms\tgamma_vs_L1\tdelta_vs_L1_ms\tcal_mode\tvalidity\tnotes"
    )
    rows: list[str] = [header]

    for model, p in MODELS.items():
        tau, D, f, Rm = p["tau_s"], p["D_s"], p["f_hz"], p["Rm"]
        cal_mode, cal_factor = p["cal_mode"], p["cal_factor"]
        tip_canon = 8.6e7

        # --- Timing L=1..100 @ TipR=8.6e7, N=1 ---
        K1 = sim_kernel(1, tip_canon, tau=tau, D=D, f=f, Rm=Rm, Nsyn=1)
        peak_1, t1, _ = metrics(K1, f)

        for L in L_TIMING:
            K = sim_kernel(L, tip_canon, tau=tau, D=D, f=f, Rm=Rm, Nsyn=1)
            peak_m, t_peak, fwhm = metrics(K, f)
            peak_c = peak_m * cal_factor
            g = gamma_vs_L1(peak_m, peak_1, L)
            g_s = f"{g:.6g}" if isinstance(g, float) else ""
            if L > 1:
                delta = (t_peak - t1) / (L - 1)
                d_s = f"{delta:.6g}"
            else:
                d_s = ""
            rows.append(
                f"timing\t{model}\t{L}\t{tip_canon:.6e}\t1\t{peak_m:.10g}\t{peak_c:.10g}\t"
                f"{t_peak:.4f}\t{fwhm:.4f}\t{g_s}\t{d_s}\t{cal_mode}\tmodel_valid\t"
                f"{p['notes_base']}; Reset-before-pulse; TipR=8.6e7"
            )

        # --- Rs grid at N=1 (truncated L) ---
        peak_at_L1: dict[float, float] = {}
        t_at_L1: dict[float, float] = {}
        for Rs in RS_GRID:
            K1r = sim_kernel(1, float(Rs), tau=tau, D=D, f=f, Rm=Rm, Nsyn=1)
            pk, tp, _ = metrics(K1r, f)
            peak_at_L1[float(Rs)] = pk
            t_at_L1[float(Rs)] = tp

        for L in L_RS:
            for Rs in RS_GRID:
                Rs_f = float(Rs)
                K = sim_kernel(L, Rs_f, tau=tau, D=D, f=f, Rm=Rm, Nsyn=1)
                peak_m, t_peak, fwhm = metrics(K, f)
                peak_c = peak_m * cal_factor
                g = gamma_vs_L1(peak_m, peak_at_L1[Rs_f], L)
                g_s = f"{g:.6g}" if isinstance(g, float) else ""
                if L > 1:
                    delta = (t_peak - t_at_L1[Rs_f]) / (L - 1)
                    d_s = f"{delta:.6g}"
                else:
                    d_s = ""
                rows.append(
                    f"Rs\t{model}\t{L}\t{Rs_f:.6e}\t1\t{peak_m:.10g}\t{peak_c:.10g}\t"
                    f"{t_peak:.4f}\t{fwhm:.4f}\t{g_s}\t{d_s}\t{cal_mode}\tmodel_valid\t"
                    f"Reset-before-pulse; N=1; L-grid truncated vs E1.1b (no L=50)"
                )

        # --- N multiplicity at TipR=8.6e7 ---
        for L in L_N:
            for N in N_GRID:
                K = sim_kernel(L, tip_canon, tau=tau, D=D, f=f, Rm=Rm, Nsyn=N)
                peak_m, t_peak, fwhm = metrics(K, f)
                peak_c = peak_m * cal_factor
                # Short-τ FastSpan + large N: Euler cable can blow past membrane bound
                if peak_m > 1.0 or not (peak_m == peak_m):
                    validity = "model_unstable"
                    notes = (
                        "Reset-before-pulse; N=co-located; peak>1 — Euler/Q unstable; "
                        "do not use for controller amp"
                    )
                else:
                    validity = "model_valid"
                    notes = "Reset-before-pulse; N=co-located synapses; TipR fixed"
                rows.append(
                    f"N\t{model}\t{L}\t{tip_canon:.6e}\t{N}\t{peak_m:.10g}\t{peak_c:.10g}\t"
                    f"{t_peak:.4f}\t{fwhm:.4f}\t\t\t{cal_mode}\t{validity}\t{notes}"
                )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    n_data = len(rows) - 1
    print(f"Wrote {n_data} rows -> {args.out}", file=sys.stderr)
    n_t = 100 * len(MODELS)
    n_rs = len(L_RS) * len(RS_GRID) * len(MODELS)
    n_n = len(L_N) * len(N_GRID) * len(MODELS)
    print(
        f"slices: timing={n_t} Rs={n_rs} N={n_n}; "
        f"RS_GRID={[float(f'{x:.6e}') for x in RS_GRID]}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
