#!/usr/bin/env python3
"""E1.1e multi-pulse tip IR: NextSegInh / PSI vs passive (scoped offline).

Extends E1.1d dual-channel Euler with Pack-A-like tip trains (2–4 pulses at
span-25 ISI, plus Pack-A target absolute times). Goal: does multi-pulse yield
effective narrowing toward the E1.4 ideal_inh_proxy band (τ≈0.5 ms /
FWHM/span ≲ 0.13 ⇒ FWHM ≲ 3.25 ms @ span 25)?

Usage:
  python3 e1_1e_multipulse_ir.py --out ../E1_1e_MULTIPULSE_IR_2026-10-22.tsv
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

# --- kinetics (AsymRm W01/W10 class; same as E1.1d) ---
TAU_S = 0.01
D_S = 0.001
TSEC = 0.001
TPULSE = 0.001
F_HZ = 20000
RM_EXC = 1.0e7
RM_INH = 1.0e8
C_F = TAU_S / RM_EXC
R_INH_SYN = 8.6e7
SUB = 2
DT = SUB / F_HZ

L_GRID = (1, 7, 10, 25)
RS_PRIMARY = 8.6e7
RS_GRID = (8.6e7,)  # cheap; TipR focus for island / E1.4
PSI_K = 2.5
SPAN_MS = 25.0
FWHM_SPAN_GATE = 0.13  # audit: positive margin needs FWHM/span ≲ 0.13
FWHM_PROXY_MS = SPAN_MS * FWHM_SPAN_GATE  # ≈ 3.25 ms
TAU_IDEAL_MS = 0.5

NEURON_MODEL = "NSPNeuronGenAsymRmD001C1e9"

# Pack-A mid ISIs (library pats_isi @ S=25 ms): 4.167 / 8.333 / 12.5 ms
ISI_MS_GRID = (4.16667, 8.33333, 12.5)
N_PULSE_GRID = (1, 2, 3, 4)
# Absolute Pack-A target spike times (pattern 0 @ span 25): 0, 4.17, 12.5, 25 ms
PACKA_TARGET_MS = (0.0, 4.16667, 12.5, 25.0)


def psi_conductance(output_const: float, k: float, pre: float, input_active: bool) -> float:
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


def metrics_trace(trace: np.ndarray) -> tuple[float, float, float]:
    peak = float(trace.max())
    if peak <= 0 or not np.isfinite(peak):
        return 0.0, float("nan"), float("nan")
    t_peak_ms = float(trace.argmax() * DT * 1000.0)
    half = peak / 2.0
    idx = np.where(trace >= half)[0]
    fwhm_ms = float((idx[-1] - idx[0]) * DT * 1000.0) if len(idx) else float("nan")
    return peak, t_peak_ms, fwhm_ms


def last_pulse_metrics(
    trace: np.ndarray, last_pulse_s: float
) -> tuple[float, float, float, float, float]:
    """Metrics of the response segment starting at last pulse onset.

    Returns: last_peak, last_t_peak_ms (abs), last_fwhm_ms, half_decay_ms, late50_rel.
    last_fwhm is FWHM of the positive excursion after last pulse (baseline=0).
    half_decay_ms = time from last_peak to amp=peak/2 on falling edge (narrowness proxy).
    """
    i0 = int(round(last_pulse_s / DT))
    if i0 >= len(trace):
        return 0.0, float("nan"), float("nan"), float("nan"), float("nan")
    seg = trace[i0:].copy()
    # remove residual DC just before last pulse (if any) so FWHM is local
    baseline = float(trace[max(0, i0 - 1)]) if i0 > 0 else 0.0
    seg = seg - baseline
    peak = float(seg.max())
    if peak <= 1e-15 or not np.isfinite(peak):
        return 0.0, float("nan"), float("nan"), float("nan"), float("nan")
    i_pk = int(seg.argmax())
    t_peak_ms = (i0 + i_pk) * DT * 1000.0
    half = peak / 2.0
    above = np.where(seg >= half)[0]
    fwhm_ms = float((above[-1] - above[0]) * DT * 1000.0) if len(above) else float("nan")
    # falling-edge half-decay from peak
    fall = seg[i_pk:]
    below = np.where(fall <= half)[0]
    half_decay_ms = float(below[0] * DT * 1000.0) if len(below) else float("nan")
    # amp at +50 ms after local peak, relative
    i50 = i_pk + int(round(0.050 / DT))
    late50 = float(seg[i50] / peak) if i50 < len(seg) else float("nan")
    return peak, t_peak_ms, fwhm_ms, half_decay_ms, late50


def _horizon_s(L: int, last_pulse_s: float) -> float:
    return min(
        6.0,
        last_pulse_s
        + 0.05
        + L * TAU_S
        + 8 * TAU_S * math.sqrt(max(L, 1))
        + 0.15,
    )


def sim_passive_or_psi(
    L: int,
    Rs: float,
    pulse_times_s: list[float],
    *,
    psi_k: float = 0.0,
    T: float | None = None,
) -> np.ndarray:
    n = L
    last = pulse_times_s[-1] if pulse_times_s else 0.0
    if T is None:
        T = _horizon_s(n, last)
    steps = int(T * F_HZ)
    S = n + 1
    V = np.full(S, -1.0)
    p = 0.0
    cnt = 0
    nx = 0
    out = []
    pc = int(TPULSE * F_HZ)
    use_psi = psi_k > 0.0
    c_out = (4.0 * psi_k / Rs) if use_psi else (1.0 / Rs)

    for k in range(steps):
        t = k / F_HZ
        while nx < len(pulse_times_s) and pulse_times_s[nx] <= t + 1e-12:
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
    pulse_times_s: list[float],
    *,
    Rs_inh: float = R_INH_SYN,
    T: float | None = None,
) -> np.ndarray:
    n_tot = L + 1
    last = pulse_times_s[-1] if pulse_times_s else 0.0
    if T is None:
        T = _horizon_s(n_tot, last)
    steps = int(T * F_HZ)
    S = n_tot + 1
    Vexc = np.full(S, -1.0)
    Vinh = np.full(S, 1.0)
    p_exc = 0.0
    p_inh = 0.0
    cnt = 0
    nx = 0
    out = []
    pc = int(TPULSE * F_HZ)
    tip_stage = n_tot - L
    inh_stage = 0

    for k in range(steps):
        t = k / F_HZ
        while nx < len(pulse_times_s) and pulse_times_s[nx] <= t + 1e-12:
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
            out.append(Vexc[S - 1] + Vinh[S - 1])
    return np.asarray(out, float)


def protocols() -> list[tuple[str, list[float]]]:
    """Named tip-drive protocols: (proto_id, pulse_times_s)."""
    out: list[tuple[str, list[float]]] = []
    for isi_ms in ISI_MS_GRID:
        for n in N_PULSE_GRID:
            if n == 1 and isi_ms != ISI_MS_GRID[0]:
                continue  # N=1 once
            times = [i * (isi_ms / 1000.0) for i in range(n)]
            pid = f"n{n}_isi{isi_ms:.3f}ms" if n > 1 else "n1_single"
            out.append((pid, times))
    # Pack-A target absolute times (4 pulses, irregular)
    out.append(("packA_tgt4", [t / 1000.0 for t in PACKA_TARGET_MS]))
    return out


def row_for(
    L: int,
    Rs: float,
    mod: str,
    proto: str,
    pulse_times: list[float],
    K: np.ndarray,
    Kp: np.ndarray,
) -> dict:
    peak, tp, fw = metrics_trace(K)
    peak_p, _, fw_p = metrics_trace(Kp)
    last_s = pulse_times[-1]
    lp, ltp, lfw, hd, late50 = last_pulse_metrics(K, last_s)
    lp_p, _, lfw_p, hd_p, late50_p = last_pulse_metrics(Kp, last_s)

    d_peak = (peak - peak_p) / peak_p if peak_p > 0 else float("nan")
    d_env_fwhm = (fw - fw_p) / fw_p if fw_p and fw_p > 0 else float("nan")
    d_last_fwhm = (lfw - lfw_p) / lfw_p if lfw_p and lfw_p > 0 else float("nan")
    d_half_decay = (hd - hd_p) / hd_p if hd_p and hd_p > 0 else float("nan")

    fwhm_span = (lfw / SPAN_MS) if lfw == lfw else float("nan")
    meets_proxy = bool(lfw == lfw and lfw <= FWHM_PROXY_MS)
    # sep-relevant peak: local last-pulse peak vs passive (island cares about shape)
    return {
        "neuron_model": NEURON_MODEL,
        "mod": mod,
        "L": L,
        "TipR": f"{Rs:.6g}",
        "protocol": proto,
        "n_pulses": len(pulse_times),
        "isi_ms": (
            f"{(pulse_times[1] - pulse_times[0]) * 1000:.5g}"
            if len(pulse_times) > 1 and proto != "packA_tgt4"
            else ("packA_irreg" if proto == "packA_tgt4" else "")
        ),
        "psi_k": PSI_K if mod.startswith("psi") else 0.0,
        "R_inh": R_INH_SYN if mod == "nextseg" else "",
        "env_peak": f"{peak:.8g}",
        "env_t_peak_ms": f"{tp:.4f}" if tp == tp else "",
        "env_fwhm_ms": f"{fw:.4f}" if fw == fw else "",
        "last_peak": f"{lp:.8g}",
        "last_t_peak_ms": f"{ltp:.4f}" if ltp == ltp else "",
        "last_fwhm_ms": f"{lfw:.4f}" if lfw == lfw else "",
        "half_decay_ms": f"{hd:.4f}" if hd == hd else "",
        "late50_rel": f"{late50:.6f}" if late50 == late50 else "",
        "last_fwhm_passive_ms": f"{lfw_p:.4f}" if lfw_p == lfw_p else "",
        "half_decay_passive_ms": f"{hd_p:.4f}" if hd_p == hd_p else "",
        "delta_env_peak_rel": f"{d_peak:.6f}" if d_peak == d_peak else "",
        "delta_env_fwhm_rel": f"{d_env_fwhm:.6f}" if d_env_fwhm == d_env_fwhm else "",
        "delta_last_fwhm_rel": f"{d_last_fwhm:.6f}" if d_last_fwhm == d_last_fwhm else "",
        "delta_half_decay_rel": f"{d_half_decay:.6f}" if d_half_decay == d_half_decay else "",
        "last_fwhm_over_span25": f"{fwhm_span:.6f}" if fwhm_span == fwhm_span else "",
        "meets_e14_fwhm_gate": int(meets_proxy),
        "e14_fwhm_gate_ms": f"{FWHM_PROXY_MS:.4f}",
        "tau_ideal_ms": TAU_IDEAL_MS,
        "source": "offline_dual_euler_multipulse",
        "validity": "model_only",
        "train_config": "N/A",
        "test_config": "N/A",
        "notes": (
            "br25_nextseg_tip"
            if L == 7
            else "AsymRm multi-pulse tip IR; last_* = post-last-pulse local"
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "E1_1e_MULTIPULSE_IR_2026-10-22.tsv",
    )
    args = ap.parse_args()

    protos = protocols()
    rows: list[dict] = []
    for L in L_GRID:
        for Rs in RS_GRID:
            for proto, times in protos:
                Kp = sim_passive_or_psi(L, Rs, times, psi_k=0.0)
                for mod, runner in (
                    ("passive", lambda t=times: sim_passive_or_psi(L, Rs, t, psi_k=0.0)),
                    ("psi_k2_5", lambda t=times: sim_passive_or_psi(L, Rs, t, psi_k=PSI_K)),
                    ("nextseg", lambda t=times: sim_nextseg(L, Rs, t)),
                ):
                    if mod == "passive":
                        K = Kp
                    else:
                        K = runner()
                    rows.append(row_for(L, Rs, mod, proto, times, K, Kp))

    cols = list(rows[0].keys())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in cols) + "\n")
    print(f"wrote {len(rows)} rows → {args.out}")

    # Focus summary: L=7 TipR=8.6e7, nextseg vs passive, last_fwhm
    print("\n# L=7 TipR=8.6e7  last_fwhm / half_decay  (nextseg vs passive; gate "
          f"FWHM≤{FWHM_PROXY_MS:.2f} ms)")
    for r in rows:
        if r["L"] != 7 or r["mod"] not in ("nextseg", "psi_k2_5"):
            continue
        if r["TipR"] != "8.6e+07":
            continue
        print(
            f"  {r['protocol']:16s} {r['mod']:10s}  "
            f"last_fwhm={r['last_fwhm_ms']:>8} (pas {r['last_fwhm_passive_ms']})  "
            f"Δ={r['delta_last_fwhm_rel']:>9}  "
            f"half_dec={r['half_decay_ms']:>7} (pas {r['half_decay_passive_ms']})  "
            f"fwhm/span={r['last_fwhm_over_span25']}  "
            f"gate={r['meets_e14_fwhm_gate']}"
        )

    # Count how many meet gate
    meet = [r for r in rows if r["meets_e14_fwhm_gate"] == 1]
    print(f"\n# rows meeting E1.4 FWHM gate (≤{FWHM_PROXY_MS:.2f} ms): {len(meet)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
