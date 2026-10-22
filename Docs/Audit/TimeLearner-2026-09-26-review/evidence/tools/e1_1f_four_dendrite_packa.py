#!/usr/bin/env python3
"""E1.1f — 4-dendrite Pack-A superposition IR (offline dual-Euler).

Follow-up to E1.1e (tip multi-pulse negative): drive all four island inputs
of br25_nextseg (L=7 6 4 1, TipR=20M×3+86M) with Pack-A patterns under
passive / nextseg / PSI, and ask whether multi-dendrite + NextSegInh yields
narrow effective kernel / positive sep_margin like E1.4 ideal_inh_proxy
(τ=0.5 ms, margin≈+0.074).

Drive modes:
  per_input  — dendrite k receives only spike at pattern time p[k] (TL semantics)
  full_train — each dendrite receives the full 4-spike train (classic_full / E1.4 cable)

Usage (from Nmsdk root or tools/):
  python3 e1_1f_four_dendrite_packa.py \\
    --out ../E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.tsv
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CABLE_DIR = (
    EVIDENCE.parent
    / "plans"
    / "AGENT_PLAN_2026-10-20"
    / "tools"
    / "cable_model"
)

# --- kinetics (AsymRm; same as E1.1d/e) ---
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

PSI_K = 2.5
SPAN_MS = 25.0
FWHM_SPAN_GATE = 0.13
FWHM_PROXY_MS = SPAN_MS * FWHM_SPAN_GATE  # ≈ 3.25
TAU_IDEAL_MS = 0.5
TAU_IDEAL_S = 0.0005
SYNC_CV_GATE = 0.25
NEURON_MODEL = "NSPNeuronGenAsymRmD001C1e9"

# Pack-A ISI library (cable_model.library.pats_isi), span-scaled
PATS_ISI = [
    0.000520833,
    0.00416667,
    0.00833333,
    0.0125,
    0.000520833,
    0.0125,
    0.00833333,
    0.00416667,
    0.000520833,
    0.00833333,
    0.00416667,
    0.0125,
    0.000520833,
    0.00833333,
    0.00833333,
    0.00833333,
    0.000520833,
    0.00104167,
    0.0114583,
    0.0125,
    0.000520833,
    0.0125,
    0.0114583,
    0.00104167,
    0.000520833,
    0.00208333,
    0.00208333,
    0.0208333,
    0.000520833,
    0.0208333,
    0.00208333,
    0.00208333,
]

CASES = [
    {
        "case_id": "br25_island",
        "L": [7, 6, 4, 1],
        "TipR": [2.0e7, 2.0e7, 2.0e7, 8.6e7],
        "notes": "br25_nextseg / br25_gen island L+TipR from E2",
        "train_config": (
            "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/"
            "EXP_br_span25_packA_nextseginh_C1e9/Train"
        ),
        "test_config": (
            "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/"
            "EXP_br_span25_packA_nextseginh_C1e9/Test"
        ),
        "console_nextseg": "PASS",
        "console_gen": "FAIL",
        "e14_proxy_margin": 0.074,
        "e14_cable_margin": -0.033,
    },
]


def patterns(span_s: float) -> list[np.ndarray]:
    out = []
    for i in range(8):
        isi = PATS_ISI[i * 4 + 1 : (i + 1) * 4]
        t = np.concatenate([[0.0], np.cumsum(isi)]) / 0.025 * span_s
        out.append(t)
    return out


def length_sync_cv(span_ms: float, Ls: list[int]) -> float:
    pats = patterns(span_ms / 1000.0)
    t = pats[0]
    need = np.array([t[3] - t[k] for k in range(3)], float)
    Ldm = np.array([max(L - 1, 0) for L in Ls[:3]], float)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = Ldm / np.maximum(need, 1e-9)
    r = r[np.isfinite(r) & (need > 1e-9)]
    if len(r) == 0 or float(np.mean(r)) == 0.0:
        return 9.0
    return float(np.std(r) / np.mean(r))


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


def _horizon_s(L: int, last_pulse_s: float) -> float:
    return min(
        6.0,
        last_pulse_s + 0.05 + L * TAU_S + 8 * TAU_S * math.sqrt(max(L, 1)) + 0.15,
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


def sim_mod(mod: str, L: int, Rs: float, pulses: list[float], T: float | None = None) -> np.ndarray:
    if mod == "passive":
        return sim_passive_or_psi(L, Rs, pulses, psi_k=0.0, T=T)
    if mod == "psi_k2_5":
        return sim_passive_or_psi(L, Rs, pulses, psi_k=PSI_K, T=T)
    if mod == "nextseg":
        return sim_nextseg(L, Rs, pulses, T=T)
    raise ValueError(mod)


def metrics_trace(trace: np.ndarray) -> tuple[float, float, float]:
    peak = float(trace.max())
    if peak <= 0 or not np.isfinite(peak):
        return 0.0, float("nan"), float("nan")
    t_peak_ms = float(trace.argmax() * DT * 1000.0)
    half = peak / 2.0
    idx = np.where(trace >= half)[0]
    fwhm_ms = float((idx[-1] - idx[0]) * DT * 1000.0) if len(idx) else float("nan")
    return peak, t_peak_ms, fwhm_ms


def sep_from_peaks(P: np.ndarray) -> dict:
    tgt = float(P[0])
    max_foil = float(P[1:].max()) if len(P) > 1 else 0.0
    if tgt <= 0:
        margin = float("nan")
        mid = 1.0
        fires = "00000000"
        pred = "FAIL"
    else:
        margin = (tgt - max_foil) / tgt
        if margin > 0:
            mid = 0.5 * (tgt + max_foil)
            fires = "".join("1" if x > mid else "0" for x in P)
            pred = "PASS"
        else:
            mid = 1.0
            fires = "00000000"
            pred = "FAIL"
    return {
        "sep_margin": margin,
        "tgt_peak": tgt,
        "max_foil": max_foil,
        "mid": mid,
        "pred_fires": fires,
        "pred_label": pred,
    }


def align_add(acc: np.ndarray, tr: np.ndarray, shift_s: float = 0.0) -> np.ndarray:
    s = int(round(shift_s / DT))
    need = s + len(tr)
    if need > len(acc):
        acc = np.concatenate([acc, np.zeros(need - len(acc))])
    acc[s : s + len(tr)] += tr
    return acc


def soma_for_pattern(
    Ls: list[int],
    Rs: list[float],
    mod: str,
    pat: np.ndarray,
    drive: str,
    T: float,
    kernel_cache: dict,
) -> np.ndarray:
    """Build soma deviation for one Pack-A pattern."""
    acc = np.zeros(1)
    if drive == "per_input":
        for k, (L, rs) in enumerate(zip(Ls, Rs)):
            key = (mod, L, rs, "ir")
            if key not in kernel_cache:
                kernel_cache[key] = sim_mod(mod, L, rs, [0.0], T=_horizon_s(L + (1 if mod == "nextseg" else 0), 0.0))
            acc = align_add(acc, kernel_cache[key], float(pat[k]))
    elif drive == "full_train":
        pulses = [float(x) for x in pat]
        for L, rs in zip(Ls, Rs):
            # nonlinear full train on each tip (classic_full semantics)
            tr = sim_mod(mod, L, rs, pulses, T=T)
            acc = align_add(acc, tr, 0.0)
    else:
        raise ValueError(drive)
    return acc


def _ideal_epsp_kernel(tau: float) -> np.ndarray:
    """Alpha-function EPSP when cable binary unavailable (relative margins OK)."""
    T = max(0.05, 12 * tau + 0.02)
    n = int(T / DT) + 1
    t = np.arange(n) * DT
    return (t / tau * np.exp(1.0 - t / tau)).astype(float)


def ideal_inh_proxy_peaks(span_ms: float) -> tuple[np.ndarray, float]:
    """Matched-filter ideal_delay τ=0.5 ms (E1.4); returns peaks + K1 FWHM ms."""
    import os

    K1: np.ndarray
    cand = CABLE_DIR / "cable"
    if cand.is_file() and os.access(cand, os.X_OK):
        if str(CABLE_DIR) not in sys.path:
            sys.path.insert(0, str(CABLE_DIR))
        os.environ["CABLE_SIM"] = str(cand)
        from library import sim as lib_sim

        K1 = np.asarray(
            lib_sim(
                1,
                [(1, 8.6e7, [0.0])],
                TAU_IDEAL_S,
                D_S,
                max(0.05, 12 * TAU_IDEAL_S + 0.02),
            ),
            float,
        )
    else:
        K1 = _ideal_epsp_kernel(TAU_IDEAL_S)

    fw = metrics_trace(K1)[2]
    pats = patterns(span_ms / 1000.0)
    t0 = pats[0]
    delays = [t0[3] - tk for tk in t0]
    P = []
    for p in pats:
        n = len(K1) + int((span_ms / 1000.0 * 2) / DT) + 10
        R = np.zeros(n)
        for dk in delays:
            for tj in p:
                s = int(round((tj + dk) / DT))
                end = s + len(K1)
                if end > len(R):
                    R = np.concatenate([R, np.zeros(end - len(R))])
                R[s:end] += K1
        P.append(float(R.max()))
    return np.asarray(P, float), fw


def run_case(case: dict, drive: str, mods: tuple[str, ...]) -> list[dict]:
    Ls = list(case["L"])
    Rs = list(case["TipR"])
    span = SPAN_MS
    pats = patterns(span / 1000.0)
    cv = length_sync_cv(span, Ls)
    T = span / 1000.0 + max(Ls) * TAU_S * 1.6 + 10 * TAU_S + 0.05
    kernel_cache: dict = {}
    rows: list[dict] = []

    # E1.4 proxy reference (once per case/drive)
    P_proxy, fw_proxy = ideal_inh_proxy_peaks(span)
    sep_proxy = sep_from_peaks(P_proxy)
    rows.append(
        _row(
            case,
            drive,
            "ideal_inh_proxy",
            cv,
            sep_proxy,
            fw_proxy,
            P_proxy,
            kernel_note=f"tau={TAU_IDEAL_MS}ms matched-filter",
        )
    )

    for mod in mods:
        peaks = []
        tgt_trace = None
        for pi, pat in enumerate(pats):
            tr = soma_for_pattern(Ls, Rs, mod, pat, drive, T, kernel_cache)
            peaks.append(float(tr.max()) if len(tr) else 0.0)
            if pi == 0:
                tgt_trace = tr
        P = np.asarray(peaks, float)
        sep = sep_from_peaks(P)
        fw = metrics_trace(tgt_trace)[2] if tgt_trace is not None else float("nan")
        rows.append(
            _row(
                case,
                drive,
                mod,
                cv,
                sep,
                fw,
                P,
                kernel_note="dual_euler_4dend",
            )
        )
    return rows


def _row(
    case: dict,
    drive: str,
    mod: str,
    cv: float,
    sep: dict,
    fwhm_ms: float,
    P: np.ndarray,
    *,
    kernel_note: str,
) -> dict:
    margin = sep["sep_margin"]
    fwhm_span = (fwhm_ms / SPAN_MS) if fwhm_ms == fwhm_ms else float("nan")
    meets = bool(fwhm_ms == fwhm_ms and fwhm_ms <= FWHM_PROXY_MS)
    pos_sep = bool(margin == margin and margin > 0)
    # retire gate: nextseg must give positive sep AND approach proxy margin or FWHM gate
    proxy_m = case["e14_proxy_margin"]
    close_to_proxy = bool(margin == margin and margin >= 0.5 * proxy_m)
    return {
        "case_id": case["case_id"],
        "neuron_model": NEURON_MODEL,
        "span_ms": SPAN_MS,
        "L_str": " ".join(str(x) for x in case["L"]),
        "TipR_str": " ".join(f"{x:.3g}" for x in case["TipR"]),
        "length_sync_cv": f"{cv:.4f}",
        "drive": drive,
        "mod": mod,
        "kernel_note": kernel_note,
        "sep_margin": f"{margin:.6f}" if margin == margin else "",
        "tgt_peak": f"{sep['tgt_peak']:.8g}",
        "max_foil": f"{sep['max_foil']:.8g}",
        "pred_fires": sep["pred_fires"],
        "pred_label": sep["pred_label"],
        "tgt_fwhm_ms": f"{fwhm_ms:.4f}" if fwhm_ms == fwhm_ms else "",
        "tgt_fwhm_over_span25": f"{fwhm_span:.6f}" if fwhm_span == fwhm_span else "",
        "meets_e14_fwhm_gate": int(meets),
        "e14_fwhm_gate_ms": f"{FWHM_PROXY_MS:.4f}",
        "e14_proxy_margin_ref": f"{proxy_m:.4f}",
        "e14_cable_margin_ref": f"{case['e14_cable_margin']:.4f}",
        "positive_sep": int(pos_sep),
        "sep_ge_half_proxy": int(close_to_proxy),
        "console_nextseg": case["console_nextseg"],
        "console_gen": case["console_gen"],
        "train_config": case["train_config"],
        "test_config": case["test_config"],
        "source": "offline_dual_euler_4dend_packa",
        "validity": "model_only",
        "peaks_csv": ",".join(f"{x:.6g}" for x in P),
        "notes": case["notes"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=Path,
        default=EVIDENCE / "E1_1f_FOUR_DENDRITE_PACKA_2026-10-22.tsv",
    )
    ap.add_argument(
        "--drives",
        default="per_input,full_train",
        help="comma list: per_input,full_train",
    )
    args = ap.parse_args()
    drives = [d.strip() for d in args.drives.split(",") if d.strip()]
    mods = ("passive", "psi_k2_5", "nextseg")

    rows: list[dict] = []
    for case in CASES:
        for drive in drives:
            rows.extend(run_case(case, drive, mods))

    cols = list(rows[0].keys())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows → {args.out}")

    print("\n# Focus: br25_island sep_margin / tgt_fwhm (retire? nextseg ≈ proxy)")
    for r in rows:
        print(
            f"  {r['drive']:11s} {r['mod']:16s}  "
            f"sep={r['sep_margin']:>10}  fires={r['pred_fires']}  "
            f"fwhm={r['tgt_fwhm_ms']:>8}  fwhm/span={r['tgt_fwhm_over_span25']}  "
            f"gate={r['meets_e14_fwhm_gate']}  pos={r['positive_sep']}  "
            f"half_proxy={r['sep_ge_half_proxy']}"
        )

    # Verdict helpers
    nextseg_rows = [r for r in rows if r["mod"] == "nextseg"]
    any_pos = any(int(r["positive_sep"]) for r in nextseg_rows)
    any_gate = any(int(r["meets_e14_fwhm_gate"]) for r in nextseg_rows)
    any_half = any(int(r["sep_ge_half_proxy"]) for r in nextseg_rows)
    print(
        f"\n# retire signals: nextseg positive_sep={any_pos} "
        f"fwhm_gate={any_gate} sep≥½·proxy={any_half}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
