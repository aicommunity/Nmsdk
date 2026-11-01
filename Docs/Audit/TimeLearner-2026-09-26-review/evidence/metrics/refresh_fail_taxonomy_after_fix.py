#!/usr/bin/env python3
"""Write FAIL_TAXONOMY after softcold_fix campaign (S3.a–d + AmpNorm diag)."""
from __future__ import annotations

import json
from pathlib import Path

EV = Path(__file__).resolve().parents[1]
OUT = EV / "FAIL_TAXONOMY.json"

PRE = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
# Drop prior after_softcold_fix / ampnorm_diag duplicates if re-run
PRE = [
    r
    for r in PRE
    if r.get("campaign") not in ("after_softcold_fix", "ampnorm_diag")
]

FIX = "2026-09-27_sbm2_strip_tip1"


def row(
    case: str,
    bundle: str,
    *,
    fc: str,
    subtype: str,
    timing_tag: str,
    train_t: int,
    need_xml: str = "1",
    tipr_class_xml: str = "flat",
    tipr_live: str | None = None,
    L_live: str | None = None,
    L_params: str | None = None,
    note: str = "",
    campaign: str = "after_softcold_fix",
) -> dict:
    d: dict = {
        "campaign": campaign,
        "softcold_fix": FIX,
        "case": case,
        "bundle": bundle,
        "fc": fc,
        "subtype": subtype,
        "timing_tag": timing_tag,
        "tipr_class_xml": tipr_class_xml,
        "need_xml": need_xml,
        "train_t": train_t,
    }
    if tipr_live:
        d["tipr_live"] = tipr_live
    if L_live:
        d["L_live"] = L_live
    if L_params:
        d["L_params"] = L_params
    if note:
        d["note"] = note
    return d


AFTER: list[dict] = [
    # --- S3.a/b core after-fix (not B_tipr_frozen_cold) ---
    row(
        "asym50_preinh",
        "asym50_preinh_20260927T071438Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=640,
        tipr_live="20000000 20000000 20000000 86000000",
        L_live="29 22 15 1",
        note="desync lifted; AmpNorm(b) TipR@Rmin Need=1; XML flat no Save",
    ),
    row(
        "asym100_preinh",
        "asym100_preinh_20260927T103846Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=640,
        tipr_live="20000000 20000000 20000000 86000000",
        L_live="52 43 30 1",
        note="desync lifted; AmpNorm(b); XML flat",
    ),
    row(
        "asym100_gen",
        "asym100_gen_20260927T140235Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=640,
        tipr_live="20000000 20000000 20000000 86000000",
        L_live="52 43 30 1",
        note="desync lifted; AmpNorm(b); XML flat",
    ),
    row(
        "asym25_preinh",
        "asym25_preinh_20260927T172618Z",
        fc="gate_fail",
        subtype="A_nonseparable_mid",
        timing_tag="timing_n/a_quality",
        train_t=160,
        need_xml="0",
        tipr_class_xml="canon",
        note="Train Done preserved; NonSeparable mid",
    ),
    row(
        "br25_on",
        "br25_on_20260927T173802Z",
        fc="gate_fail",
        subtype="A_nonseparable_mid",
        timing_tag="timing_n/a_quality",
        train_t=320,
        need_xml="0",
        tipr_class_xml="canon",
        note="Train Done preserved; NonSeparable",
    ),
    row(
        "fs25_gen",
        "fs25_gen_20260927T174820Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=160,
        tipr_class_xml="other",
        L_params="6 5 4 1",
        note="near-gold L; AmpNorm(a) TipR mid-band dend2 on ext/diag",
    ),
    row(
        "phase6_thr_only",
        "phase6_thr_only_20260927T183618Z",
        fc="train_incomplete",
        subtype="B_runaway_length",
        timing_tag="timing_est_delay_vs_span",
        train_t=900,
        L_params="97 81 49 1",
        note="EstDelay vs span480; not SoftCold SBM",
    ),
    row(
        "phase6_preinh250",
        "phase6_preinh250_20260927T204043Z",
        fc="train_incomplete",
        subtype="B_runaway_length",
        timing_tag="timing_est_delay_vs_span",
        train_t=900,
        L_params="100 81 53 1",
    ),
    row(
        "phase6_ltzcal_twin",
        "phase6_ltzcal_twin_20260927T222127Z",
        fc="train_incomplete",
        subtype="B_runaway_length",
        timing_tag="timing_est_delay_vs_span",
        train_t=900,
        L_params="97 81 49 1",
    ),
    # --- S3.d extended P0 ---
    row(
        "fs25_gen_ext640",
        "fs25_gen_20260928T065707Z",
        fc="train_incomplete",
        subtype="AmpNorm_a_tipr_midband",
        timing_tag="timing_ok_budget",
        train_t=640,
        tipr_live="2e7 2e7 ~3.4e7 8.6e7",
        L_live="6 5 4 1",
        note="TipR dend2 mid-band freeze; L gold-like",
    ),
    row(
        "asym50_preinh_ext1280",
        "asym50_preinh_20260928T085626Z",
        fc="train_incomplete",
        subtype="AmpNorm_b_rmin_need1",
        timing_tag="timing_ok_budget",
        train_t=1280,
        tipr_live="20000000 20000000 20000000 86000000",
        note="TipR@Rmin live; Need=1; XML flat",
    ),
    row(
        "asym100_preinh_ext1280",
        "asym100_preinh_20260928T154111Z",
        fc="train_incomplete",
        subtype="AmpNorm_b_rmin_need1",
        timing_tag="timing_ok_budget",
        train_t=1280,
        tipr_live="20000000 20000000 20000000 86000000",
        note="TipR@Rmin; Need=1",
    ),
    row(
        "asym100_gen_ext1280",
        "asym100_gen_20260928T222626Z",
        fc="train_incomplete",
        subtype="AmpNorm_b_rmin_need1",
        timing_tag="timing_ok_budget",
        train_t=1280,
        tipr_live="20000000 20000000 20000000 86000000",
        note="TipR@Rmin; Need=1",
    ),
    # --- S3.c remaining C1 fs* ---
    row(
        "fs25_preinh",
        "fs25_preinh_20260929T051117Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=160,
        note="S3.c rc=1; likely AmpNorm-family",
    ),
    row(
        "fs50_preinh",
        "fs50_preinh_20260929T061018Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=320,
        note="S3.c rc=1",
    ),
    row(
        "fs100_gen",
        "fs100_gen_20260929T075107Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=640,
        note="S3.c rc=1",
    ),
    row(
        "fs100_preinh",
        "fs100_preinh_20260929T111612Z",
        fc="train_incomplete",
        subtype="B_partial_growth_need1",
        timing_tag="timing_ok_budget",
        train_t=640,
        note="S3.c rc=1",
    ),
    # --- S3.c C2 ---
    row("ltz25_gen", "ltz25_gen_20260929T144056Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("ltz25_preinh", "ltz25_preinh_20260929T144904Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("ltz50_gen", "ltz50_gen_20260929T150948Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=320, note="S3.c C2 rc=1"),
    row("ltz50_preinh", "ltz50_preinh_20260929T183328Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=320, note="S3.c C2 rc=1"),
    row("ltz100_gen", "ltz100_gen_20260929T201038Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1"),
    row("ltz100_preinh", "ltz100_preinh_20260929T233538Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1"),
    row("pa00_baseline", "pa00_baseline_20260930T014534Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("pa01_ltz_sweep", "pa01_ltz_sweep_20260930T020253Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("pa02_ltzone_avg", "pa02_ltzone_avg_20260930T022016Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("pa06_ltzone_int", "pa06_ltzone_int_20260930T023740Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("tn_classic", "tn_classic_20260930T025513Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("psi01_050", "psi01_050_20260930T031202Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("psi14_260", "psi14_260_20260930T032936Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("psi15_270", "psi15_270_20260930T034744Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=160, note="S3.c C2 rc=1"),
    row("psi21_100", "psi21_100_20260930T040548Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=320, note="S3.c C2 rc=1"),
    row("psi31_200", "psi31_200_20260930T044113Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1"),
    row("psi32_300", "psi32_300_20260930T052628Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1"),
    row("psi33_300", "psi33_300_20260930T062024Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1"),
    row("psi34_400", "psi34_400_20260930T071455Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1"),
    row("psi35_400", "psi35_400_20260930T084038Z", fc="train_incomplete", subtype="B_partial_growth_need1", timing_tag="timing_ok_budget", train_t=640, note="S3.c C2 rc=1 DONE_TAILS"),
    # --- AmpNorm diag keep-slog precursor ---
    row(
        "fs25_gen",
        "fs25_gen_20260930T101032Z",
        fc="train_incomplete",
        subtype="AmpNorm_a_tipr_midband",
        timing_tag="timing_ok_budget",
        train_t=640,
        tipr_live="2e7 2e7 ~3.45e7 8.6e7",
        L_live="6 5 4 1",
        note="no-prune diag; dend2 mid-band 34–35M; StatisticLog wiped without --keep-slog",
        campaign="ampnorm_diag",
    ),
]

OUT.write_text(json.dumps(PRE + AFTER, indent=2) + "\n", encoding="utf-8")
print("WROTE", OUT, "n=", len(PRE) + len(AFTER), "after=", len(AFTER))
