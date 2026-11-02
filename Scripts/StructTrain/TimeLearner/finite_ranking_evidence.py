"""Primary-derived timing-rank evidence for the explicit native engineering fixture.

This is not a general training certificate or a scientific selectivity scorer.
An old algorithm's valid but worse selection remains a measured negative result.
"""
import re
from pathlib import Path

from .native_evidence import count, equal, load, measured_training_probe, number, require
from .stopped_evidence import audit_stopped_state


def load_case(directory, prefix):
    require(re.fullmatch(r"(Classic|Branch)_2000_N[01]_finite_ranking_zero_sync", prefix) is not None,
            "unsupported_finite_ranking_fixture")
    directory = Path(directory)
    package = load(directory/(prefix+"_stopped_package.json"))
    summary = load(directory/(prefix+"_ranking_summary.json"))
    expected = {directory/(prefix+f"_training_proof_{i}.json") for i in range(1, len(package["observed_packets"])+1)}
    require(set(directory.glob(prefix+"_training_proof_*.json")) == expected,
            "finite_ranking_primary_inventory_mismatch")
    require(set(directory.glob(prefix+"_training_proof_*.csv")) == {p.with_suffix(".csv") for p in expected},
            "finite_ranking_trace_inventory_mismatch")
    packets, traces = {}, {}
    for p in sorted(expected):
        packet = load(p);trial = packet["requested_specification"]["trial_id"]
        require(trial not in packets, "duplicate_primary_trial")
        packets[trial], traces[trial] = packet, p.with_suffix(".csv")
    return package, summary, packets, traces


def audit_finite_timing_ranking(package, summary, packets, traces):
    source_audit = audit_stopped_state(package, summary, packets, traces)
    require(package["implementation_id"] == "native-finite-ranking-fixture-v1"
            and package["reference_complete"] is True and len(package["protocol"]["inputs"]) == 2
            and package["training_outcome"] == "budget_exhausted"
            and package["reason"] == "maximum_sweeps_exhausted", "unsupported_finite_ranking_source")
    require(summary["tolerances"] == {"amplitude_absolute": 1., "amplitude_relative": 0., "sync": 0.},
            "finite_ranking_is_not_declared_engineering_protocol")
    inputs = package["protocol"]["inputs"];origin = package["protocol"]["origin_stimulus_id"];selections = set()
    refs = {r["input_id"]: r for r in summary["references"]}
    reference = measured_training_probe(packets, refs[inputs[0]["id"]]["trial_id"], inputs[0]["id"], origin, selections)[1]
    rows = []
    for candidate in summary["candidates"]:
        require(count(candidate["input_index"]) == 0, "finite_ranking_changed_fixed_anchor")
        packet, raw, arrival, end = measured_training_probe(packets, candidate["trial_id"], inputs[0]["id"], origin, selections)
        anchor, _, anchor_arrival, anchor_end = measured_training_probe(packets, candidate["anchor_trial_id"], inputs[1]["id"], origin, selections)
        for p in (packet, anchor):
            require(p["prepared"]["base_model_revision"] == candidate["model_revision"]
                    and p["prepared"]["model_epoch"] == candidate["model_epoch"], "stale_finite_ranking_candidate")
        low, high, amplitude = arrival-anchor_end, end-anchor_arrival, raw-reference
        require(equal(candidate["timing_low"], low) and equal(candidate["timing_high"], high)
                and equal(candidate["amplitude_residual"], amplitude), "finite_rank_residual_not_derived_from_primary")
        error = max(abs(low), abs(high))
        require(candidate["within_timing"] is (error <= 0.)
                and candidate["within_amplitude"] is (abs(amplitude) <= 1.), "finite_rank_flag_mismatch")
        full = candidate["full_parameters"]
        require(len(full) == 2 and candidate["parameters"] == full[0]
                and count(full[0]["length"]) in (1, 2, 3) and full[1] == package["trained_inputs"][1],
                "finite_rank_parameter_context_mismatch")
        for p, final in zip(full, package["trained_inputs"]):
            require(count(p["synapses"]) == 1 and p["synapses"] == final["synapses"]
                    and number(p["resistance"]) > 0. and p["resistance"] == final["resistance"],
                    "finite_rank_changed_fixed_normalizer")
        require(candidate["within_amplitude"] is True, "finite_rank_amplitude_control_not_ready")
        rows.append({"trial_id": candidate["trial_id"], "anchor_trial_id": candidate["anchor_trial_id"],
                     "begin": number(packet["observation"]["specification"]["begin"]),
                     "model_revision": candidate["model_revision"], "model_epoch": count(candidate["model_epoch"]),
                     "full_parameters": full, "timing_low": low, "timing_high": high,
                     "timing_error": error, "amplitude_residual": amplitude})
    require({r["full_parameters"][0]["length"] for r in rows} == {1, 2, 3}, "finite_rank_missing_geometry")
    rows.sort(key=lambda r: (r["begin"], r["trial_id"]))
    initial = [r for r in rows if r["model_revision"] == package["capture_revision"]
               and r["model_epoch"] == package["capture_epoch"]]
    selected = [r for r in rows if r["full_parameters"] == package["trained_inputs"]]
    require(bool(initial) and bool(selected), "finite_rank_unmeasured_initial_or_selected_model")
    minimum = min(r["timing_error"] for r in rows)
    initial_error = min(r["timing_error"] for r in initial)
    selected_error = min(r["timing_error"] for r in selected)
    require(minimum < initial_error-1e-12, "finite_rank_positive_control_has_no_improvement")
    return {"kind": "timelearner_finite_timing_rank_audit", "schema_version": 1,
            "source_stopped_sha256": package["sha256"], "source_audit": source_audit,
            "initial_timing_error": initial_error, "minimum_measured_timing_error": minimum,
            "selected_timing_error": selected_error, "selected_is_measured_minimum": selected_error == minimum,
            "rows": rows, "training_completed": False, "certificate_present": False,
            "native_execution_verified": False, "evaluation_verdict": None}
