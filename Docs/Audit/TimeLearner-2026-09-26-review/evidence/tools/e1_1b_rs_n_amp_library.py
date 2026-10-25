#!/usr/bin/env python3
"""E1.1b scoped amp library: Rs×8 log + N multiplicity at fixed L (offline cable_model).

Reset-before-pulse: each (model, L, Rs|N) is an independent cable run from rest
(V=-1), single simultaneous spike train onset at t=0. N = co-located synapses
(multiplicity), not a pulse train without Reset.

Calibration (E1.0 PARTIAL):
  Gen:     peak_cal = peak_model / GEN_BIAS   (GEN_BIAS≈1.067; Console < model)
  AsymRm:  peak_cal = peak_model * ASYM_ORACLE (≈1.46; Console > passive Rm=1e7)

Usage:
  python3 e1_1b_rs_n_amp_library.py --out ../E1_1b_RS_N_AMP_LIBRARY_2026-10-22.tsv
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

# TipR log grid: typical derived Rmin (~2e6, F5/W01 lows) … default TipR 8.6e7
RS_GRID = np.geomspace(2.0e6, 8.6e7, 8)
N_GRID = (1, 2, 4, 8, 16, 32, 64, 128)
L_RS = (1, 10, 25, 50)
L_N = (1, 10, 25)

GEN_BIAS = 1.067  # model/console ≈; peak_cal = model / GEN_BIAS
ASYM_ORACLE = 1.46  # console/model ≈ at L≥4

MODELS = {
    "NSPNeuronGen": {
        "tau_s": 0.01,
        "D_s": 0.005,
        "f_hz": 2000,
        "Rm": 1e7,
        "cal_mode": "gen_bias",
        "cal_factor": GEN_BIAS,
    },
    "NSPNeuronGenAsymRmD001C1e9": {
        "tau_s": 0.01,
        "D_s": 0.001,
        "f_hz": 20000,
        "Rm": 1e7,
        "cal_mode": "asym_oracle",
        "cal_factor": ASYM_ORACLE,
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
    """Independent run from rest; Nsyn co-located tip synapses, one spike at t=0."""
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


def calibrate(peak_model: float, cal_mode: str, cal_factor: float) -> float:
    if cal_mode == "gen_bias":
        return peak_model / cal_factor
    if cal_mode == "asym_oracle":
        return peak_model * cal_factor
    return peak_model


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
        "t_peak_ms\tFWHM_ms\tgamma_vs_L1\tcal_mode\tvalidity\tnotes"
    )
    rows: list[str] = [header]

    for model, p in MODELS.items():
        tau, D, f, Rm = p["tau_s"], p["D_s"], p["f_hz"], p["Rm"]
        cal_mode, cal_factor = p["cal_mode"], p["cal_factor"]

        # --- Rs grid at N=1 ---
        peak_at_L1: dict[float, float] = {}
        for Rs in RS_GRID:
            K1 = sim_kernel(1, float(Rs), tau=tau, D=D, f=f, Rm=Rm, Nsyn=1)
            peak_at_L1[float(Rs)] = metrics(K1, f)[0]

        for L in L_RS:
            for Rs in RS_GRID:
                Rs_f = float(Rs)
                K = sim_kernel(L, Rs_f, tau=tau, D=D, f=f, Rm=Rm, Nsyn=1)
                peak_m, t_peak, fwhm = metrics(K, f)
                peak_c = calibrate(peak_m, cal_mode, cal_factor)
                g = gamma_vs_L1(peak_m, peak_at_L1[Rs_f], L)
                g_s = f"{g:.6g}" if isinstance(g, float) else ""

                if model == "NSPNeuronGen" and L == 50:
                    validity = "model_only_silent_debt"
                    notes = "DEBT-C1-silent-soma; Console amp invalid; timing/amp from cable"
                else:
                    validity = "model_valid"
                    notes = "Reset-before-pulse; N=1; offline cable_model"

                rows.append(
                    f"Rs\t{model}\t{L}\t{Rs_f:.6e}\t1\t{peak_m:.10g}\t{peak_c:.10g}\t"
                    f"{t_peak:.4f}\t{fwhm:.4f}\t{g_s}\t{cal_mode}\t{validity}\t{notes}"
                )

        # --- N multiplicity at TipR=8.6e7 ---
        tip = 8.6e7
        for L in L_N:
            for N in N_GRID:
                K = sim_kernel(L, tip, tau=tau, D=D, f=f, Rm=Rm, Nsyn=N)
                peak_m, t_peak, fwhm = metrics(K, f)
                peak_c = calibrate(peak_m, cal_mode, cal_factor)
                rows.append(
                    f"N\t{model}\t{L}\t{tip:.6e}\t{N}\t{peak_m:.10g}\t{peak_c:.10g}\t"
                    f"{t_peak:.4f}\t{fwhm:.4f}\t\t{cal_mode}\tmodel_valid\t"
                    f"Reset-before-pulse; N=co-located synapses; TipR fixed"
                )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    n_data = len(rows) - 1
    print(f"Wrote {n_data} rows -> {args.out}", file=sys.stderr)
    print(
        f"RS_GRID={[float(f'{x:.6e}') for x in RS_GRID]} N_GRID={list(N_GRID)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
