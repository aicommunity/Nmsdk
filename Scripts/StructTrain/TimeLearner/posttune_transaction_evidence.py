"""Independent native weight-search/threshold-confirmation evidence replay.

This validates recorded conditions and observations, not arbitrary-file origin,
foreign process ownership, native integrator capability or global optimality.
"""
import copy

from .calibrated_evidence import REQUEST_FIELDS
from .calibration_transaction_evidence import audit_native_calibration_transaction
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, after, count, equal, number, require
from .recognition_evidence import audit_recognition_derivation, _derive_post_tune
from .recognition_trial_evidence import audit_recognition_trial

FIELDS = {"kind", "schema_version", "algorithm", "source_recognition", "mode", "metric", "canonical_floor",
          "canonical_last", "resistance_bounds", "minimum_positive_gap", "search_passes", "maximum_candidates",
          "maximum_recorded_samples", "recorded_weight_samples", "proposals", "search_termination", "trials",
          "candidates", "rejected_proposals", "active_matrix", "thresholds", "maximum_calibration_candidates",
          "confirmation_specification", "selected_index", "calibration", "status", "reason", "source_restored",
          "calibrated_package", "dynamic_checkpoint", "statistical_independence_verified", "evaluation_verdict", "sha256"}


def _semantic(rows):
    return [{k: v for k, v in q.items() if k != "run_id"} for q in rows]


def _matrix(row, design, run_id, metric):
    package, matrix = row["candidate"], row["matrix"]
    require(set(matrix) == {"requests", "observations"} and _semantic(matrix["requests"]) == _semantic(design),
            "post_tune_measurement_design_changed")
    requests = matrix["requests"]
    wanted = {(q["run_id"], q["trial_id"]): q for q in requests}
    observed = {(o["run_id"], o["trial_id"]): o for o in matrix["observations"]}
    require(len(wanted) == len(requests) == len(observed) == len(matrix["observations"]) and
            set(wanted) == set(observed) and all(q["run_id"] == run_id for q in requests), "incomplete_post_tune_matrix")
    targets, foils, samples, begin, end = [], [], 0, None, None
    for key, q in wanted.items():
        o = observed[key]
        audit_recognition_trial(o, package)
        require(o["valid"] is True and o["complete"] is True and o["censored"] is False and
                all(o[k] == q[k] for k in ("sample_id", "label", "pattern_hash", "pattern_isi", "reset_policy", "maximum_samples")) and
                equal(number(o["end"]), number(o["begin"])+number(q["duration"])) and
                o["schema_version"] == (2 if q["record_threshold_potential"] else 1), "invalid_post_tune_observation")
        values = [number(s["lt_potential"]) if metric == "ltzone" else number(sum(number(v) for v in s["soma"]))
                  for s in o["samples"]]
        require(bool(values), "missing_post_tune_peak")
        (targets if q["label"] == "target" else foils).append(max(values))
        samples += len(values)
        begin = number(o["begin"]) if begin is None else min(begin, number(o["begin"]))
        end = number(o["end"]) if end is None else max(end, number(o["end"]))
    require(targets and foils, "unbalanced_post_tune_matrix")
    gap = number(min(targets)-max(foils))
    require(equal(gap, number(row["measured_gap"])), "post_tune_gap_not_replayed")
    return gap, samples, begin, end


def audit_posttune_transaction(report, source_case):
    try:
        r = report
        require(type(r) is dict and set(r) == FIELDS and r["kind"] == "native_post_tune_transaction" and
                type(r["schema_version"]) is int and r["schema_version"] == 1 and
                r["algorithm"] == "bounded-coordinate-full-pattern-native-calibration-v1", "unknown_post_tune_transaction")
        require(r["sha256"] == sha({k: v for k, v in r.items() if k != "sha256"}), "post_tune_digest_mismatch")
        source = r["source_recognition"];audit_recognition_derivation(source, source_case)
        require(source["conversion_spec"]["schema_version"] == 1, "unsupported_post_tune_source_continuation")
        status = r["status"]
        require(status in {"calibrated", "search_unresolved", "budget_exhausted", "cancelled", "failed", "recovery_required"} and
                type(r["source_restored"]) is bool and r["source_restored"] is (status not in {"calibrated", "recovery_required"}) and
                type(r["reason"]) is str and r["dynamic_checkpoint"] is False and
                r["statistical_independence_verified"] is False and r["evaluation_verdict"] is None, "unsupported_post_tune_claim")
        require(r["mode"] in {"off", "keep_done", "canon_rmin", "flat_last_r", "search_synthetic"} and
                r["metric"] in {"auto", "ltzone", "soma_sum"}, "unknown_post_tune_algorithm_or_metric")
        require(1 <= count(r["maximum_candidates"]) <= 4096 and 1 <= count(r["search_passes"]) <= 128 and
                1 <= count(r["maximum_recorded_samples"]) <= 100000000 and number(r["minimum_positive_gap"]) >= 0,
                "invalid_post_tune_budget")
        design = r["trials"]
        require(type(design) is list and 2 <= len(design) <= 10000 and
                all(type(q) is dict and set(q) == REQUEST_FIELDS for q in design) and
                len({q["trial_id"] for q in design}) == len(design), "invalid_post_tune_design")
        labels = {};sample_ids = {};target_hash = source["source_solo"]["protocol"]["pattern_hash"]
        for q in design:
            require(q["label"] in {"target", "foil"} and q["pattern_hash"] == sha(q["pattern_isi"]) and
                    ((q["label"] == "target") is (q["pattern_hash"] == target_hash)), "post_tune_label_or_hash_changed")
            labels.setdefault(q["reset_policy"], set()).add(q["label"])
            signature = (q["label"], q["pattern_hash"])
            require(q["sample_id"] not in sample_ids or sample_ids[q["sample_id"]] == signature, "post_tune_sample_collision")
            sample_ids[q["sample_id"]] = signature
        require(all(v == {"target", "foil"} for v in labels.values()), "unbalanced_post_tune_design")
        branch = source["source_solo"]["configuration"]["model"]["branch"]
        metric = ("soma_sum" if branch else "ltzone") if r["metric"] == "auto" else r["metric"]
        frequency = number(source["source_solo"]["configuration"]["model"]["frequency_hz"])
        for q in design:
            require(all(type(q[k]) is str and q[k] for k in ("run_id", "trial_id", "sample_id")) and
                    type(q["pattern_isi"]) is list and len(q["pattern_isi"]) == len(source["recognition_inputs"]) and
                    all(number(v) >= 0 for v in q["pattern_isi"]) and q["reset_policy"] in {"reset_per_trial", "preserve_neuron_dynamics"} and
                    type(q["record_threshold_potential"]) is bool and (metric != "ltzone" or q["record_threshold_potential"]),
                    "invalid_post_tune_request")
            ticks = number(q["duration"])*frequency
            require(q["duration"] > sum(q["pattern_isi"]) and equal(ticks, round(ticks)) and
                    2 <= count(q["maximum_samples"]) <= 10000000 and ticks+1 <= q["maximum_samples"], "invalid_post_tune_window_budget")
        confirmation = r["confirmation_specification"]
        require(set(confirmation) == {"protocol", "data_partition_id", "attempt_id", "clock_id", "criterion"} and
                confirmation["protocol"] in {"historical_same_matrix", "frozen_independent_calibration"} and
                all(type(confirmation[k]) is str and confirmation[k].strip() for k in ("data_partition_id", "attempt_id", "clock_id")),
                "invalid_post_tune_confirmation_scope")
        require(type(r["thresholds"]) is list and 1 <= len(r["thresholds"]) <= 256 and
                len({number(t) for t in r["thresholds"]}) == len(r["thresholds"]) and
                1 <= count(r["maximum_calibration_candidates"]) <= 256, "invalid_post_tune_threshold_grid")
        rows, gaps, samples, previous_end = r["candidates"], [], 0, None
        for i, row in enumerate(rows):
            require(type(row) is dict and set(row) == {"candidate", "matrix", "measured_gap"} and
                    row["candidate"]["source_solo"] == source["source_solo"], "invalid_post_tune_candidate")
            audit_recognition_derivation(row["candidate"], source_case)
            gap, n, begin, end = _matrix(row, design, r["confirmation_specification"]["attempt_id"]+"/weights/"+str(i), metric)
            require(previous_end is None or after(begin, previous_end), "post_tune_weight_matrices_overlap")
            previous_end = end;gaps.append(gap);samples += n
        selected = max(range(len(gaps)), key=gaps.__getitem__) if gaps else None
        require(r["selected_index"] == selected and (selected is None or type(r["selected_index"]) is int), "wrong_post_tune_selection")
        proposals = count(r["proposals"]);rejected = r["rejected_proposals"]
        require(proposals <= count(r["maximum_candidates"]) and len(rows)+len(rejected) <= proposals and
                len({count(q["proposal"]) for q in rejected}) == len(rejected) and
                all(set(q) == {"proposal", "reason"} and count(q["proposal"]) < proposals and
                    type(q["reason"]) is str and q["reason"] for q in rejected), "invalid_post_tune_rejections")
        closed = r["search_termination"] in {"declared_schedule_complete", "candidate_budget_exhausted"}
        schedule = 1+3*len(source["recognition_inputs"])*count(r["search_passes"]) if r["mode"] == "search_synthetic" else 1
        require(proposals <= schedule and (not closed or proposals == min(schedule, r["maximum_candidates"])) and
                (not closed or (r["search_termination"] == "declared_schedule_complete") is (schedule <= r["maximum_candidates"])),
                "post_tune_schedule_or_budget_changed")
        sequence_verified, physics_rejections_verified = False, closed
        if closed:
            require(len(rows)+len(rejected) == proposals and count(r["recorded_weight_samples"]) == samples,
                    "incomplete_closed_post_tune_search")
            rejects = {q["proposal"]: q["reason"] for q in rejected};seen=set();measured=0;best=None
            for i in range(proposals):
                mode = "canon_rmin" if r["mode"] == "search_synthetic" and i == 0 else (
                    "search_synthetic_candidate" if r["mode"] == "search_synthetic" else r["mode"])
                requested = []
                if i and r["mode"] == "search_synthetic":
                    base = rows[best]["candidate"] if best is not None else source
                    requested = [p["resistance"] for p in base["recognition_inputs"]]
                    coordinate, factor = ((i-1)//3) % len(requested), (.5, 1., 2.)[(i-1) % 3]
                    requested[coordinate] *= factor
                p = {"mode": mode, "source_model_revision": source["model_revision"],
                     "canonical_floor": r["canonical_floor"] if mode == "canon_rmin" else 0.,
                     "canonical_last": r["canonical_last"] if mode in {"canon_rmin", "flat_last_r"} else 0.,
                     "requested_resistances": requested, "resistance_bounds": r["resistance_bounds"]}
                if i in rejects:
                    if rejects[i] == "duplicate_effective_model":
                        model = copy.deepcopy(source["neuron"]["graph"]["identity"]["model"])
                        _derive_post_tune(p, model, source["recognition_inputs"], source["source_solo"]["configuration"]["model"])
                        require(sha(model) in seen, "post_tune_false_duplicate")
                    else:
                        physics_rejections_verified = False
                    continue
                expected_spec = {**source["conversion_spec"], "schema_version": 2, "post_tune": p}
                require(rows[measured]["candidate"]["conversion_spec"] == expected_spec, "post_tune_proposal_sequence_changed")
                identity = rows[measured]["candidate"]["model_revision"]
                require(identity not in seen, "post_tune_remeasured_duplicate");seen.add(identity)
                if best is None or gaps[measured] > gaps[best]:best=measured
                measured += 1
            sequence_verified = True
        require(samples <= count(r["recorded_weight_samples"]) <= count(r["maximum_recorded_samples"]), "post_tune_sample_budget_changed")
        child = r["calibration"];child_audit = None
        if child:
            child_audit = audit_native_calibration_transaction(child, source_case)
            require(selected is not None and gaps[selected] > number(r["minimum_positive_gap"]) and
                    child["source_recognition"] == rows[selected]["candidate"] and child["trials"] == design and
                    child["thresholds"] == r["thresholds"] and child["maximum_candidates"] == r["maximum_calibration_candidates"] and
                    child["criterion"] == r["confirmation_specification"]["criterion"] and
                    all(child[k] == r["confirmation_specification"][k] for k in
                        ("protocol", "data_partition_id", "attempt_id", "clock_id")), "post_tune_calibration_handoff_changed")
        if status == "calibrated":
            require(sequence_verified and child_audit is not None and child["status"] == "calibrated" and
                    r["calibrated_package"] == child["calibrated_package"], "post_tune_unconfirmed_commit")
        else:
            require(r["calibrated_package"] == {}, "post_tune_noncommitted_package_claim")
        if r["reason"] == "no_positive_measured_gap":
            require(selected is None or gaps[selected] <= number(r["minimum_positive_gap"]), "post_tune_false_no_gap")
        return {"schema_version": 1, "recorded_search_consistent": True, "status": status,
                "measured_candidates": len(rows), "selected_index": selected, "complete_weight_samples": samples,
                "proposal_sequence_verified": sequence_verified, "native_physics_rejections_verified": physics_rejections_verified,
                "calibration_audit": child_audit, "native_execution_verified": False, "owner_restoration_verified": False,
                "partial_observations_validated": False, "statistical_independence_verified": False, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_post_tune_transaction:"+str(error)) from error
