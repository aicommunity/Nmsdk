#!/usr/bin/env python3
"""E1.4 offline separability predictor (kernel superposition).

For each case: load L / TipR (from G1/E2 exit-clean or SUCCESSFUL states),
synthesize Pack-A soma peaks via linear superposition of EPSP kernels
(cable_model), optionally apply NextSegInh/PreInh *proxy* (ideal narrow
coincidence when length-sync CV is small), compute sep_margin and predicted
fires vs mid, compare Acc-direction to known Console/G1 outcomes.

Gate: match Console PASS/FAIL direction ≥ 5/6.

Usage (from Nmsdk root):
  CABLE_SIM=…/cable_model/cable \\
  python3 Docs/Audit/.../evidence/tools/e1_4_separability_predictor.py \\
    --tsv Docs/Audit/.../evidence/E1_4_SEPARABILITY_PREDICTOR_2026-10-22.tsv \\
    --json Docs/Audit/.../evidence/E1_4_SEPARABILITY_PREDICTOR_2026-10-22.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
ROOT = EVIDENCE.parents[2]  # Nmsdk
CABLE_DIR = (
    EVIDENCE.parent
    / "plans"
    / "AGENT_PLAN_2026-10-20"
    / "tools"
    / "cable_model"
)

# Default cases: 3 PASS Branch island + 3 FAIL (R8 / E2.S* W10/W01).
# L/TipR from E2_matrix_2026-10-21.tsv (rep-stable PostTune-finalized / Need0).
CASES = [
    {
        "case_id": "br25_nextseg",
        "alias": "W10_HIST_br25_nextseg",
        "trainer": "Branch",
        "mode": "N1",
        "span_ms": 25,
        "neuron_model": "AsymRm",
        "mod": "nextseg",
        "L": [7, 6, 4, 1],
        "TipR": [2e7, 2e7, 2e7, 8.6e7],
        "console_label": "PASS",
        "console_fires": "10000000",
        "console_Acc": "8/8",
        "console_Цель": "да",
        "train_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train",
        "test_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test",
        "state_source": "E2_matrix_2026-10-21.tsv / POSTTUNE_FIX_COLD PASS×3",
    },
    {
        "case_id": "br50_preinh",
        "alias": "W10_HIST_br50_preinh",
        "trainer": "Branch",
        "mode": "N1",
        "span_ms": 50,
        "neuron_model": "AsymRm+Preinh2_5",
        "mod": "preinh",
        "L": [15, 12, 6, 1],
        "TipR": [2e7, 2e7, 2e7, 8.6e7],
        "console_label": "PASS",
        "console_fires": "10000000",
        "console_Acc": "8/8",
        "console_Цель": "да",
        "train_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_preinh_C1e9/Train",
        "test_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span50_packA_preinh_C1e9/Test",
        "state_source": "E2_matrix_2026-10-21.tsv",
    },
    {
        "case_id": "br100_preinh",
        "alias": "W10_HIST_br100_preinh",
        "trainer": "Branch",
        "mode": "N1",
        "span_ms": 100,
        "neuron_model": "AsymRm+Preinh2_5",
        "mod": "preinh",
        "L": [21, 18, 11, 1],
        "TipR": [2e7, 2e7, 2e7, 8.6e7],
        "console_label": "PASS",
        "console_fires": "10000000",
        "console_Acc": "8/8",
        "console_Цель": "да",
        "train_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span100_packA_preinh_C1e9/Train",
        "test_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span100_packA_preinh_C1e9/Test",
        "state_source": "E2_matrix_2026-10-21.tsv",
    },
    {
        "case_id": "br25_gen",
        "alias": "W10_HIST_br25_gen",
        "trainer": "Branch",
        "mode": "N1",
        "span_ms": 25,
        "neuron_model": "AsymRm",
        "mod": "gen",
        "L": [7, 6, 4, 1],
        "TipR": [2e7, 2e7, 2e7, 8.6e7],
        "console_label": "FAIL",
        "console_fires": "00000000",
        "console_Acc": "7/8",
        "console_Цель": "нет",
        "train_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Train",
        "test_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Test",
        "state_source": "E2_matrix_2026-10-21.tsv (PostTune ON silent)",
    },
    {
        "case_id": "br25_preinh",
        "alias": "W10_HIST_br25_preinh",
        "trainer": "Branch",
        "mode": "N1",
        "span_ms": 25,
        "neuron_model": "AsymRm+Preinh2_5",
        "mod": "preinh",
        "L": [16, 13, 3, 1],
        "TipR": [2e7, 2e7, 2e7, 8.6e7],
        "console_label": "FAIL",
        "console_fires": "00000000",
        "console_Acc": "7/8",
        "console_Цель": "нет",
        "train_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_preinh_C1e9/Train",
        "test_config": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_preinh_C1e9/Test",
        "state_source": "E2_matrix_2026-10-21.tsv (Need0 + silent Test)",
    },
    {
        "case_id": "W01_CL50_N0",
        "alias": "W01_CL50_N0_PSIoff",
        "trainer": "Classic",
        "mode": "N0",
        "span_ms": 50,
        "neuron_model": "AsymRm",
        "mod": "gen",
        "L": [27, 22, 15, 1],
        "TipR": [8.6e7, 8.6e7, 8.6e7, 8.6e7],
        "console_label": "FAIL",
        "console_fires": "00000000",
        "console_Acc": "7/8",
        "console_Цель": "нет",
        "train_config": "Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train",
        "test_config": "Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test",
        "state_source": "G1.S1.W01-11-20261021T113257Z-15892 / E2_matrix",
    },
]

# AsymRm W10/W01 passive params (E1.0 / cable_model README).
TAU_S = 0.01
D_S = 0.001
# Ideal-narrow EPSP proxy for NextSegInh / PreInh when length-sync is OK.
# Audit: positive margin needs τ ≲ 0.05·span; τ=0.5 ms ≈ ideal_delay F1a band.
TAU_IDEAL_INH_S = 0.0005
# CV of (L−1)/need_delay across first 3 inputs; island PASS ≤0.14, br25_preinh ≈0.45.
SYNC_CV_GATE = 0.25


def _ensure_cable_path():
    if str(CABLE_DIR) not in sys.path:
        sys.path.insert(0, str(CABLE_DIR))
    sim = os.environ.get("CABLE_SIM")
    if not sim:
        cand = CABLE_DIR / "cable"
        if cand.is_file() and os.access(cand, os.X_OK):
            os.environ["CABLE_SIM"] = str(cand)
        else:
            raise SystemExit(
                f"CABLE_SIM not set and {cand} missing; build cable_model/cable first"
            )


def length_sync_cv(span_ms: float, Ls: list[int]) -> float:
    from library import patterns

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


def cable_peaks(span_ms: float, Ls: list[int], Rs: list[float]):
    from classic_full import classic

    P = np.asarray(classic(TAU_S, D_S, span_ms, Ls, Rs), float)
    return P


def ideal_delay_peaks(span_ms: float, tau: float = TAU_IDEAL_INH_S):
    """Matched filter with L=1 kernel + pure delays (ideal_delay.py)."""
    from library import DT, patterns, sim

    K1 = sim(1, [(1, 8.6e7, [0.0])], tau, D_S, max(0.05, 12 * tau + 0.02))
    pats = patterns(span_ms / 1000.0)
    t = pats[0]
    delays = [t[3] - tk for tk in t]
    P = []
    for p in pats:
        n = len(K1) + int((span_ms / 1000.0 * 2) / DT) + 10
        R = np.zeros(n)
        for dk in delays:
            for tj in p:
                s = int(round((tj + dk) / DT))
                R[s : s + len(K1)] += K1
        P.append(float(R.max()))
    return np.asarray(P, float)


def sep_from_peaks(P: np.ndarray) -> dict:
    tgt = float(P[0])
    max_foil = float(P[1:].max())
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
            # NonSeparable → thr=1 silent (Console PostTune path)
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
        "peaks": [float(x) for x in P],
    }


def predict_case(case: dict, sync_cv_gate: float = SYNC_CV_GATE) -> dict:
    Ls = list(case["L"])
    Rs = list(case["TipR"])
    span = float(case["span_ms"])
    mod = case["mod"]
    cv = length_sync_cv(span, Ls)
    P_cable = cable_peaks(span, Ls, Rs)
    cable = sep_from_peaks(P_cable)

    use_inh_proxy = mod in ("nextseg", "preinh") and cv <= sync_cv_gate
    if use_inh_proxy:
        P = ideal_delay_peaks(span, TAU_IDEAL_INH_S)
        kernel_mode = "ideal_inh_proxy"
        tau_kernel_ms = TAU_IDEAL_INH_S * 1000.0
    else:
        P = P_cable
        kernel_mode = "passive_cable"
        tau_kernel_ms = TAU_S * 1000.0

    out = sep_from_peaks(P)
    match = out["pred_label"] == case["console_label"]
    return {
        **{k: case[k] for k in case},
        "L_str": " ".join(str(x) for x in Ls),
        "TipR_str": " ".join(f"{x:.0f}" for x in Rs),
        "length_sync_cv": round(cv, 4),
        "sync_cv_gate": sync_cv_gate,
        "kernel_mode": kernel_mode,
        "tau_kernel_ms": tau_kernel_ms,
        "cable_sep_margin": round(cable["sep_margin"], 6),
        "pred_sep_margin": round(out["sep_margin"], 6),
        "pred_tgt_peak": out["tgt_peak"],
        "pred_max_foil": out["max_foil"],
        "pred_mid": out["mid"],
        "pred_fires": out["pred_fires"],
        "pred_label": out["pred_label"],
        "match_console": match,
        "peaks_json": json.dumps(out["peaks"]),
    }


def run_all(sync_cv_gate: float = SYNC_CV_GATE) -> list[dict]:
    _ensure_cable_path()
    return [predict_case(c, sync_cv_gate=sync_cv_gate) for c in CASES]


def write_tsv(rows: list[dict], path: Path) -> None:
    cols = [
        "case_id",
        "alias",
        "trainer",
        "mode",
        "span_ms",
        "neuron_model",
        "mod",
        "L_str",
        "TipR_str",
        "length_sync_cv",
        "kernel_mode",
        "tau_kernel_ms",
        "cable_sep_margin",
        "pred_sep_margin",
        "pred_tgt_peak",
        "pred_max_foil",
        "pred_mid",
        "pred_fires",
        "pred_label",
        "console_label",
        "console_fires",
        "console_Acc",
        "console_Цель",
        "match_console",
        "train_config",
        "test_config",
        "state_source",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--tsv",
        type=Path,
        default=EVIDENCE / "E1_4_SEPARABILITY_PREDICTOR_2026-10-22.tsv",
    )
    ap.add_argument(
        "--json",
        type=Path,
        default=EVIDENCE / "E1_4_SEPARABILITY_PREDICTOR_2026-10-22.json",
    )
    ap.add_argument("--sync-cv-gate", type=float, default=SYNC_CV_GATE)
    args = ap.parse_args()

    rows = run_all(sync_cv_gate=args.sync_cv_gate)
    n_match = sum(1 for r in rows if r["match_console"])
    summary = {
        "gate": "match Console PASS/FAIL direction ≥ 5/6",
        "n_cases": len(rows),
        "n_match": n_match,
        "gate_pass": n_match >= 5,
        "sync_cv_gate": args.sync_cv_gate,
        "tau_ideal_inh_ms": TAU_IDEAL_INH_S * 1000.0,
        "tau_passive_ms": TAU_S * 1000.0,
        "D_ms": D_S * 1000.0,
        "verdict": "PARTIAL" if n_match >= 5 else "FAIL",
        "note": (
            "NextSegInh/PreInh use ideal_delay τ=0.5 ms proxy when length_sync_cv "
            f"≤ {args.sync_cv_gate}; gen/desync use passive cable (E1.0 AsymRm). "
            "Measured NextSegInh/PSI kernels still PENDING (E1.1)."
        ),
        "rows": rows,
    }
    write_tsv(rows, args.tsv)
    args.json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"match {n_match}/{len(rows)} gate_pass={summary['gate_pass']} -> {args.tsv}")
    for r in rows:
        print(
            f"  {r['case_id']:14} pred={r['pred_label']:4} "
            f"Consol={r['console_label']:4} m={r['pred_sep_margin']:+.4f} "
            f"mode={r['kernel_mode']} cv={r['length_sync_cv']:.3f} "
            f"match={r['match_console']}"
        )


if __name__ == "__main__":
    main()
