#!/usr/bin/env python3
"""E1.1d scoped NextSegInh / PSI impulse-response library vs passive baseline.

Offline dual-channel Euler matching NPulseChannel/NPulseSynapse (PulseLib):
  - passive: Exc cascade only (≡ cable_model), soma_dev = Vexc_soma + 1
  - psi:     Exc conductance = PresynapticInhibitionConductance (k=2.5 default)
  - nextseg: Exc tip @ L + Inh @ L+1 (Rm_inh=1e8 → τ_inh=100 ms); soma SumPotential
             = Vexc + Vinh  (rest 0; Exc rest −1, Inh rest +1)

Scoped grid (PARTIAL): AsymRm D001C1e9, L∈{1,4,10,25,7}, Rs few log points, N=1.
No Console in this tool (model_only); see evidence note for Console vs offline.

Usage:
  python3 e1_1d_nextseg_psi_library.py --out ../E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.tsv
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

# --- kinetics (AsymRm W01/W10 class) ---
TAU_S = 0.01
D_S = 0.001  # DissociationTC Exc/Inh synapse
TSEC = 0.001  # SecretionTC
TPULSE = 0.001
F_HZ = 20000
RM_EXC = 1.0e7
RM_INH = 1.0e8  # InhMembraneResistance → τ_inh = Rm·C = 100 ms @ C=1e-9
C_F = TAU_S / RM_EXC  # 1e-9
R_INH_SYN = 8.6e7  # SynapseResistanceBase for NextSeg Inh on L+1
SUB = 2
DT = SUB / F_HZ

L_GRID = (1, 4, 7, 10, 25)  # 7 = tip of br25_nextseg PASS state
RS_GRID = (2.0e6, 2.0e7, 8.6e7)
PSI_K = 2.5  # Classic PSI25 / Preinh2_5

NEURON_MODEL = "NSPNeuronGenAsymRmD001C1e9"


def psi_conductance(output_const: float, k: float, pre: float, input_active: bool) -> float:
    """Mirror NPulseSynapse::PresynapticInhibitionConductance."""
    if k <= 0.0:
        return output_const * pre
    gate = 1.0 - k * pre
    if gate >= 0.0:
        return output_const * gate * pre
    if not input_active:
        return 0.0
    min_gate = 0.05
    if k > 2.0:
        min_gate = 0.05 * (2.0 / k)
    return output_const * min_gate * pre


def metrics(trace: np.ndarray) -> tuple[float, float, float]:
    peak = float(trace.max())
    if peak <= 0 or not np.isfinite(peak):
        return 0.0, float("nan"), float("nan")
    t_peak_ms = float(trace.argmax() * DT * 1000.0)
    half = peak / 2.0
    idx = np.where(trace >= half)[0]
    fwhm_ms = float((idx[-1] - idx[0]) * DT * 1000.0) if len(idx) else float("nan")
    return peak, t_peak_ms, fwhm_ms


def sim_passive_or_psi(
    L: int,
    Rs: float,
    *,
    psi_k: float = 0.0,
    T: float | None = None,
) -> np.ndarray:
    """Single Exc cascade; optional PSI on tip synapse. Returns soma deviation (V+1)."""
    n = L
    if T is None:
        T = min(4.0, 0.03 + L * TAU_S + 8 * TAU_S * math.sqrt(L) + 0.05)
    steps = int(T * F_HZ)
    S = n + 1  # stages 0..n-1 dendrite distal→proximal, n = soma
    V = np.full(S, -1.0)
    p = 0.0
    cnt = 0
    nx = 0
    pulse_times = [0.0]
    out = []
    pc = int(TPULSE * F_HZ)
    use_psi = psi_k > 0.0
    c_out = (4.0 * psi_k / Rs) if use_psi else (1.0 / Rs)

    for k in range(steps):
        t = k / F_HZ
        while nx < len(pulse_times) and pulse_times[nx] <= t + 1e-12:
            cnt = pc
            nx += 1
        input_active = cnt > 0
        if input_active:
            p += (1.0 - p) / (TSEC * F_HZ)
            cnt -= 1
        else:
            p -= p / (D_S * F_HZ)

        G = np.zeros(S)
        if use_psi:
            g = psi_conductance(c_out, psi_k, p, input_active)
        else:
            g = c_out * p
        if g < 0:
            g = 0.0
        # tip at distal stage 0 = segment L
        G[0] += g

        for i in range(S):
            inp = -1.0 if i == 0 else V[i - 1]
            Ti = C_F / (G[i] + 1.0 / RM_EXC)
            su = 1.0 + G[i] * RM_EXC
            V[i] += (inp - V[i] * su) / (Ti * F_HZ)
        if k % SUB == 0:
            out.append(V[S - 1] + 1.0)
    return np.asarray(out, float)


def sim_nextseg(
    L: int,
    Rs_exc: float,
    *,
    Rs_inh: float = R_INH_SYN,
    T: float | None = None,
) -> np.ndarray:
    """Exc tip @ L, Inh @ L+1 distal; soma SumPotential = Vexc + Vinh."""
    n_exc = L  # segments 1..L for Exc tip
    n_tot = L + 1  # distal-most = L+1 for Inh
    if T is None:
        T = min(4.0, 0.03 + n_tot * TAU_S + 8 * TAU_S * math.sqrt(n_tot) + 0.05)
    steps = int(T * F_HZ)
    # stages: 0 = distal L+1, ..., n_tot-1 = segment 1, n_tot = soma
    S = n_tot + 1
    Vexc = np.full(S, -1.0)
    Vinh = np.full(S, 1.0)
    p_exc = 0.0
    p_inh = 0.0
    cnt = 0
    nx = 0
    pulse_times = [0.0]
    out = []
    pc = int(TPULSE * F_HZ)
    tip_stage = n_tot - L  # segment L → stage index (distal=0 is L+1)
    inh_stage = 0  # segment L+1

    for k in range(steps):
        t = k / F_HZ
        while nx < len(pulse_times) and pulse_times[nx] <= t + 1e-12:
            cnt = pc
            nx += 1
        if cnt > 0:
            p_exc += (1.0 - p_exc) / (TSEC * F_HZ)
            p_inh += (1.0 - p_inh) / (TSEC * F_HZ)
            cnt -= 1
        else:
            p_exc -= p_exc / (D_S * F_HZ)
            p_inh -= p_inh / (D_S * F_HZ)

        Gexc = np.zeros(S)
        Ginh = np.zeros(S)
        Gexc[tip_stage] += p_exc / Rs_exc
        Ginh[inh_stage] += p_inh / Rs_inh

        # membrane competition (soft): active Inh syn holds Exc at rest on that stage
        # NPulseSynChannel::ResetOut is a no-op stub; still clamp distal Exc open-end.
        # Dual cascade with independent Rm.
        for i in range(S):
            inp_e = -1.0 if i == 0 else Vexc[i - 1]
            Ti_e = C_F / (Gexc[i] + 1.0 / RM_EXC)
            su_e = 1.0 + Gexc[i] * RM_EXC
            Vexc[i] += (inp_e - Vexc[i] * su_e) / (Ti_e * F_HZ)

            inp_i = 1.0 if i == 0 else Vinh[i - 1]
            Ti_i = C_F / (Ginh[i] + 1.0 / RM_INH)
            su_i = 1.0 + Ginh[i] * RM_INH
            Vinh[i] += (inp_i - Vinh[i] * su_i) / (Ti_i * F_HZ)

        if k % SUB == 0:
            # SumPotential = Exc + Inh; rest = 0
            out.append(Vexc[S - 1] + Vinh[S - 1])
    return np.asarray(out, float)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "E1_1d_NEXTSEG_PSI_LIBRARY_2026-10-22.tsv",
    )
    args = ap.parse_args()

    rows: list[dict] = []
    for L in L_GRID:
        for Rs in RS_GRID:
            Kp = sim_passive_or_psi(L, Rs, psi_k=0.0)
            peak_p, tp_p, fw_p = metrics(Kp)

            for mod, runner in (
                ("passive", lambda: Kp),
                ("psi_k2_5", lambda: sim_passive_or_psi(L, Rs, psi_k=PSI_K)),
                ("nextseg", lambda: sim_nextseg(L, Rs)),
            ):
                if mod == "passive":
                    K = Kp
                    peak, tp, fw = peak_p, tp_p, fw_p
                else:
                    K = runner()
                    peak, tp, fw = metrics(K)
                d_peak = (peak - peak_p) / peak_p if peak_p > 0 else float("nan")
                d_fwhm = (fw - fw_p) / fw_p if fw_p and fw_p > 0 else float("nan")
                d_tp = (tp - tp_p) if (tp == tp and tp_p == tp_p) else float("nan")
                rows.append(
                    {
                        "neuron_model": NEURON_MODEL,
                        "mod": mod,
                        "L": L,
                        "TipR": f"{Rs:.6g}",
                        "N": 1,
                        "psi_k": PSI_K if mod.startswith("psi") else 0.0,
                        "R_inh": R_INH_SYN if mod == "nextseg" else "",
                        "peak": f"{peak:.8g}",
                        "t_peak_ms": f"{tp:.4f}" if tp == tp else "",
                        "fwhm_ms": f"{fw:.4f}" if fw == fw else "",
                        "peak_passive": f"{peak_p:.8g}",
                        "fwhm_passive_ms": f"{fw_p:.4f}",
                        "delta_peak_rel": f"{d_peak:.6f}" if d_peak == d_peak else "",
                        "delta_fwhm_rel": f"{d_fwhm:.6f}" if d_fwhm == d_fwhm else "",
                        "delta_t_peak_ms": f"{d_tp:.4f}" if d_tp == d_tp else "",
                        "source": "offline_dual_euler",
                        "validity": "model_only",
                        "train_config": "N/A",
                        "test_config": "N/A",
                        "notes": (
                            "br25_nextseg_tip"
                            if L == 7
                            else ("AsymRm τ=10ms D=1ms f=20k" if L in (1, 4, 10, 25) else "")
                        ),
                    }
                )

    cols = list(rows[0].keys())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"wrote {len(rows)} rows → {args.out}")

    # quick summary vs passive @ TipR=8.6e7
    print("\n# delta FWHM / peak @ TipR=8.6e7 (vs passive)")
    for L in L_GRID:
        for mod in ("psi_k2_5", "nextseg"):
            r = next(
                x
                for x in rows
                if x["L"] == L and x["mod"] == mod and x["TipR"] == "8.6e+07"
            )
            print(
                f"  L={L:2d} {mod:10s}  Δpeak={r['delta_peak_rel']:>9}  "
                f"ΔFWHM={r['delta_fwhm_rel']:>9}  FWHM={r['fwhm_ms']}  "
                f"FWHM_pas={r['fwhm_passive_ms']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
