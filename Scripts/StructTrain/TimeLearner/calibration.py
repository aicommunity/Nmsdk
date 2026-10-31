"""Measured threshold selection and fresh-confirmation data contracts.

All responses are scored by recognition_metrics. Neither a perfect score nor
this consistency audit proves native execution, source provenance or scientific
generalisation; the runner must bind its execution manifests separately.
"""
import copy
import re

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, count, number, require
from .recognition_metrics import score_threshold_candidate
from .threshold_candidate_evidence import audit_threshold_candidate

ALGORITHM = "measured-threshold-grid-with-fresh-confirmation-v1"
RULE = "target_violations_then_foil_responses_then_declared_order_v1"
SPEC_FIELDS = {"kind", "schema_version", "calibration_id", "protocol", "data_partition_id",
               "source_recognition_sha256", "source_model_revision", "dataset_digest", "coverage_policy",
               "criterion", "trials", "thresholds", "maximum_candidates", "selection_rule"}
TRIAL_FIELDS = {"trial_id", "sample_id", "label", "pattern_isi", "reset_policy", "presentation_index", "duration"}
MEASUREMENT_FIELDS = {"candidate", "evaluation_spec", "observations", "execution"}
EXECUTION_FIELDS = {"attempt_id", "clock_id", "stage", "selection_sha256"}


def _text(value):
    require(type(value) is str and bool(value.strip()), "invalid_calibration_identifier")
    return value


def _digest(value):
    require(type(value) is str and re.fullmatch("[0-9a-f]{64}", value) is not None, "invalid_calibration_digest")
    return value


def calibration_dataset_digest(coverage_policy, criterion, trials):
    return canonical_model_sha256({"coverage_policy": coverage_policy, "criterion": criterion,
                                   "trials": sorted(trials, key=lambda trial: trial["presentation_index"])})


def validate_trial_design(trials):
    """Validate the shared target/foil probe design without inventing a threshold grid."""
    require(type(trials) is list and len(trials) >= 2, "incomplete_calibration_design")
    ids, positions, policies = set(), set(), {}
    for trial in trials:
        require(type(trial) is dict and set(trial) == TRIAL_FIELDS, "unknown_calibration_trial_fields")
        identity = _text(trial["trial_id"]);_text(trial["sample_id"])
        position = count(trial["presentation_index"])
        require(identity not in ids and position not in positions and trial["label"] in ("target", "foil")
                and trial["reset_policy"] in ("reset_per_trial", "preserve_neuron_dynamics"), "duplicate_or_invalid_calibration_trial")
        ids.add(identity);positions.add(position)
        pattern = trial["pattern_isi"]
        require(type(pattern) is list and bool(pattern) and all(number(value) >= 0 for value in pattern)
                and number(trial["duration"]) > sum(pattern), "invalid_calibration_stimulus_or_duration")
        policies.setdefault(trial["reset_policy"], set()).add(trial["label"])
    require(positions == set(range(len(trials))) and all(labels == {"target", "foil"} for labels in policies.values()),
            "calibration_requires_targets_and_foils_in_each_reset_policy")


def _validate_spec(spec):
    require(type(spec) is dict and set(spec) == SPEC_FIELDS and
            spec["kind"] == "timelearner_threshold_calibration_spec" and type(spec["schema_version"]) is int
            and spec["schema_version"] == 1, "unknown_calibration_spec")
    _text(spec["calibration_id"]);_text(spec["data_partition_id"])
    require(spec["protocol"] in ("historical_same_matrix", "frozen_independent_calibration"), "unknown_calibration_protocol")
    require(spec["selection_rule"] == RULE, "unknown_calibration_selection_rule")
    _digest(spec["source_recognition_sha256"]);_digest(spec["source_model_revision"])
    require(spec["coverage_policy"] in ("per_trial_windows", "continuous_native_stream"), "unknown_calibration_coverage")
    require(type(spec["thresholds"]) is list and bool(spec["thresholds"]), "empty_calibration_grid")
    thresholds = [number(value) for value in spec["thresholds"]]
    require(len(set(thresholds)) == len(thresholds), "invalid_calibration_threshold_grid")
    budget = count(spec["maximum_candidates"])
    require(budget > 0, "invalid_calibration_budget")
    trials = spec["trials"]
    validate_trial_design(trials)
    require(_digest(spec["dataset_digest"]) == calibration_dataset_digest(spec["coverage_policy"], spec["criterion"], trials),
            "calibration_dataset_digest_mismatch")
    # The common scorer validates the criterion enum/fields against actual
    # observations. Do not create a second response-window implementation here.
    semantic = {key: value for key, value in spec.items() if key not in ("calibration_id", "source_recognition_sha256")}
    semantic["trials"] = sorted(spec["trials"], key=lambda trial: trial["presentation_index"])
    return thresholds[:budget], {"spec_digest": canonical_model_sha256(spec),
        "conditions_digest": canonical_model_sha256({"algorithm": ALGORITHM, "specification": semantic})}


def _expected_trials(spec):
    result = []
    for trial in sorted(spec["trials"], key=lambda item: item["presentation_index"]):
        item = {key: value for key, value in trial.items() if key != "pattern_isi"}
        item["pattern_hash"] = canonical_model_sha256(trial["pattern_isi"])
        result.append(item)
    return result


def _measurement(spec, measurement, source_case, stage, selection_sha256=None):
    require(type(measurement) is dict and set(measurement) == MEASUREMENT_FIELDS, "unknown_calibration_measurement")
    execution = measurement["execution"]
    require(type(execution) is dict and set(execution) == EXECUTION_FIELDS and execution["stage"] == stage
            and execution["selection_sha256"] == selection_sha256, "calibration_execution_scope_mismatch")
    _text(execution["attempt_id"]);_text(execution["clock_id"])
    package, evaluation, observations = (measurement[key] for key in ("candidate", "evaluation_spec", "observations"))
    audit = audit_threshold_candidate(package, source_case)
    source = package["source_recognition"]
    require(source["sha256"] == spec["source_recognition_sha256"] and source["model_revision"] == spec["source_model_revision"],
            "calibration_source_model_changed")
    require(type(evaluation) is dict and evaluation["coverage_policy"] == spec["coverage_policy"]
            and evaluation["criterion"] == spec["criterion"], "calibration_measurement_criterion_changed")
    require(type(evaluation["trials"]) is list and all(type(trial) is dict for trial in evaluation["trials"]) and sorted(
        [{key: value for key, value in trial.items() if key != "observation"} for trial in evaluation["trials"]],
        key=lambda trial: trial["presentation_index"]) == _expected_trials(spec), "calibration_measurement_design_changed")
    scored = score_threshold_candidate(evaluation, observations, package)
    require(scored["validity"] == "valid", "calibration_incomplete_or_invalid_observations")
    require(all(item["criterion_assessed"] for item in scored["by_reset_policy"].values()), "calibration_unassessed_reset_policy")
    target_bad = sum(row["label"] == "target" and (row["classification"] == "FN" or
        (spec["criterion"]["reject_target_outside_window"] and bool(row["early_spikes"] or row["late_spikes"])))
        for row in scored["trials"])
    foil_bad = scored["pooled_counts"]["FP"]
    ordered = sorted(observations, key=lambda observation: observation["trial_id"])
    return {"threshold": number(package["threshold"]), "candidate_sha256": package["sha256"],
            "model_revision": package["model_revision"], "run_id": scored["run_id"],
            "attempt_id": execution["attempt_id"], "clock_id": execution["clock_id"],
            "begin": min(number(o["begin"]) for o in observations), "end": max(number(o["end"]) for o in observations),
            "observation_set_digest": canonical_model_sha256(ordered), "target_violations": target_bad,
            "foil_responses": foil_bad, "separable": target_bad == foil_bad == 0,
            "source_audit": audit, "score": scored}


def _selection(spec, measurements, source_case):
    thresholds, identity = _validate_spec(spec)
    require(type(measurements) is list and len(measurements) == len(thresholds), "calibration_missing_expected_candidates")
    records, runs = {}, set()
    for measurement in measurements:
        row = _measurement(spec, measurement, source_case, "search")
        threshold = row["threshold"]
        require(threshold in thresholds and threshold not in records and row["run_id"] not in runs,
                "calibration_unexpected_or_duplicate_candidate")
        records[threshold] = row;runs.add(row["run_id"])
    rows = [{"candidate_index": i, **records[threshold]} for i, threshold in enumerate(thresholds)]
    by_clock = {}
    for row in rows:by_clock.setdefault(row["clock_id"], []).append(row)
    for group in by_clock.values():
        ordered = sorted(group, key=lambda row: row["begin"])
        require(all(after(b["begin"], a["end"]) for a, b in zip(ordered, ordered[1:])), "calibration_search_measurements_overlap")
    ranked = sorted(rows, key=lambda row: (row["target_violations"], row["foil_responses"], row["candidate_index"]))
    good = [row for row in ranked if row["separable"]]
    complete_grid = len(thresholds) == len(spec["thresholds"])
    selected = good[0] if good else None
    status = "pending_confirmation" if selected else "nonseparable" if complete_grid else "budget_exhausted"
    result = {"kind": "timelearner_threshold_selection", "schema_version": 1, "algorithm": ALGORITHM,
              "calibration_id": spec["calibration_id"], "protocol": spec["protocol"],
              "data_partition_id": spec["data_partition_id"], **identity,
              "source_recognition_sha256": spec["source_recognition_sha256"], "source_model_revision": spec["source_model_revision"],
              "status": status, "grid_complete": complete_grid, "candidates": rows,
              "next_action": "rebuild_and_confirm_selected" if selected else "restore_source_without_calibration",
              "selected_candidate": None if selected is None else selected["candidate_sha256"],
              "selected_model_revision": None if selected is None else selected["model_revision"],
              "selected_threshold": None if selected is None else selected["threshold"],
              "best_measured_candidate": ranked[0]["candidate_sha256"], "calibrated": False,
              "native_execution_verified": False, "evaluation_verdict": None}
    result["sha256"] = canonical_model_sha256(result)
    return result


def select_threshold(spec, measurements, source_case):
    """Select from the entire declared budget prefix, never a partial good CSV."""
    try:
        return _selection(spec, measurements, source_case)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_threshold_selection:"+str(error)) from error


def confirm_threshold(spec, measurements, source_case, selection, confirmation):
    """Require a separately acquired full matrix for the independently rebuilt candidate.

    Same-clock confirmation must occur after search. A new clock requires a new
    attempt ID; absolute model times from different clocks are not compared.
    Native execution/import itself is established by the runner, not a JSON flag.
    """
    try:
        expected = _selection(spec, measurements, source_case)
        require(selection == expected and selection["sha256"] == canonical_model_sha256(
            {key: value for key, value in selection.items() if key != "sha256"}), "calibration_selection_mismatch")
        require(selection["status"] == "pending_confirmation", "calibration_has_no_separable_selection")
        confirmed = _measurement(spec, confirmation, source_case, "confirmation", selection["sha256"])
        rows = selection["candidates"]
        require(confirmed["candidate_sha256"] == selection["selected_candidate"] and
                confirmed["model_revision"] == selection["selected_model_revision"] and
                confirmed["threshold"] == selection["selected_threshold"], "calibration_confirmation_model_changed")
        require(confirmed["run_id"] not in {row["run_id"] for row in rows} and
                confirmed["observation_set_digest"] not in {row["observation_set_digest"] for row in rows},
                "calibration_confirmation_reuses_search")
        same_clock = [row for row in rows if row["clock_id"] == confirmed["clock_id"]]
        if same_clock:
            require(after(confirmed["begin"], max(row["end"] for row in same_clock)), "calibration_confirmation_precedes_selection")
        else:
            require(confirmed["attempt_id"] not in {row["attempt_id"] for row in rows}, "calibration_new_clock_requires_new_attempt")
        result = {"kind": "timelearner_calibration_result", "schema_version": 1, "algorithm": ALGORITHM,
                  "selection": copy.deepcopy(selection), "confirmation": confirmed,
                  "status": "confirmed" if confirmed["separable"] else "confirmation_failed",
                  "next_action": "commit_confirmed_model" if confirmed["separable"] else "restore_source_without_calibration",
                  "calibrated": confirmed["separable"], "model_revision": confirmed["model_revision"],
                  "threshold": confirmed["threshold"], "native_execution_verified": False,
                  "statistical_independence_verified": False, "evaluation_verdict": None}
        result["sha256"] = canonical_model_sha256(result)
        return result
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_threshold_confirmation:"+str(error)) from error
