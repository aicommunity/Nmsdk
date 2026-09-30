#!/usr/bin/env python3
"""Write FAIL_TAXONOMY after softcold_fix campaign (S3.a+b)."""
from __future__ import annotations

import json
from pathlib import Path

EV = Path(__file__).resolve().parents[1]
OUT = EV / "FAIL_TAXONOMY.json"
RUNS = Path(
    "/home/user/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/_repro/runs"
)

# Keep pre-fix rows, append after_fix campaign.
PRE = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
# Drop prior after_softcold_fix duplicates if re-run
PRE = [r for r in PRE if r.get("campaign") != "after_softcold_fix"]

AFTER = [
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "asym50_preinh",
        "bundle": "asym50_preinh_20260927T071438Z",
        "fc": "train_incomplete",
        "subtype": "B_partial_growth_need1",
        "timing_tag": "timing_ok_budget",
        "tipr_class_xml": "flat",
        "tipr_live": "20000000 20000000 20000000 86000000",
        "L_live": "29 22 15 1",
        "need_xml": "1",
        "note": "desync lifted; EOL/Save missing within poll401",
        "train_t": 640,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "asym100_preinh",
        "bundle": "asym100_preinh_20260927T103846Z",
        "fc": "train_incomplete",
        "subtype": "B_partial_growth_need1",
        "timing_tag": "timing_ok_budget",
        "tipr_class_xml": "flat",
        "tipr_live": "20000000 20000000 20000000 86000000",
        "L_live": "52 43 30 1",
        "need_xml": "1",
        "note": "desync lifted; EOL/Save missing",
        "train_t": 640,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "asym100_gen",
        "bundle": "asym100_gen_20260927T140235Z",
        "fc": "train_incomplete",
        "subtype": "B_partial_growth_need1",
        "timing_tag": "timing_ok_budget",
        "tipr_class_xml": "flat",
        "tipr_live": "20000000 20000000 20000000 86000000",
        "L_live": "52 43 30 1",
        "need_xml": "1",
        "note": "desync lifted; EOL/Save missing",
        "train_t": 640,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "asym25_preinh",
        "bundle": "asym25_preinh_20260927T172618Z",
        "fc": "gate_fail",
        "subtype": "A_nonseparable_mid",
        "timing_tag": "timing_n/a_quality",
        "tipr_class_xml": "canon",
        "need_xml": "0",
        "note": "Train Done preserved; NonSeparable mid",
        "train_t": 160,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "br25_on",
        "bundle": "br25_on_20260927T173802Z",
        "fc": "gate_fail",
        "subtype": "A_nonseparable_mid",
        "timing_tag": "timing_n/a_quality",
        "tipr_class_xml": "canon",
        "need_xml": "0",
        "note": "Train Done preserved; NonSeparable",
        "train_t": 320,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "fs25_gen",
        "bundle": "fs25_gen_20260927T174820Z",
        "fc": "train_incomplete",
        "subtype": "B_partial_growth_need1",
        "timing_tag": "timing_ok_budget",
        "tipr_class_xml": "other",
        "L_params": "6 5 4 1",
        "need_xml": "1",
        "note": "near-gold L; Need≠0 — P0 extended",
        "train_t": 160,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "phase6_thr_only",
        "bundle": "phase6_thr_only_20260927T183618Z",
        "fc": "train_incomplete",
        "subtype": "B_runaway_length",
        "timing_tag": "timing_est_delay_vs_span",
        "L_params": "97 81 49 1",
        "need_xml": "1",
        "note": "EstDelay vs span480; not SoftCold SBM",
        "train_t": 900,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "phase6_preinh250",
        "bundle": "phase6_preinh250_20260927T204043Z",
        "fc": "train_incomplete",
        "subtype": "B_runaway_length",
        "timing_tag": "timing_est_delay_vs_span",
        "L_params": "100 81 53 1",
        "need_xml": "1",
        "train_t": 900,
    },
    {
        "campaign": "after_softcold_fix",
        "softcold_fix": "2026-09-27_sbm2_strip_tip1",
        "case": "phase6_ltzcal_twin",
        "bundle": "phase6_ltzcal_twin_20260927T222127Z",
        "fc": "train_incomplete",
        "subtype": "B_runaway_length",
        "timing_tag": "timing_est_delay_vs_span",
        "L_params": "97 81 49 1",
        "need_xml": "1",
        "train_t": 900,
    },
]

OUT.write_text(json.dumps(PRE + AFTER, indent=2) + "\n", encoding="utf-8")
print("WROTE", OUT, "n=", len(PRE) + len(AFTER))
