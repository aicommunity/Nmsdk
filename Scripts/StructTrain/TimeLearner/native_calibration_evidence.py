"""Compare native response decisions with the common scorer and primary data."""
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, count, number, require
from .recognition_metrics import score_threshold_candidate, score_recognition_evaluation
from .threshold_candidate_evidence import audit_threshold_candidate
from .recognition_evidence import audit_recognition_derivation


FIELDS = {"kind", "schema_version", "algorithm", "run_id", "model_revision", "training_pattern_hash", "criterion",
          "validity", "complete_observation_set", "criterion_met", "target_violations", "foil_responses",
          "pooled_counts", "by_reset_policy", "trials", "calibrated", "evaluation_verdict", "sha256"}
COUNT_FIELDS = {"TP", "FP", "FN", "TN", "targets", "foils", "target_trials_with_outside_spikes"}
RATE_FIELDS = {"accuracy", "target_hit_rate", "foil_response_rate"}


def _counts(value):
    require(type(value) is dict and set(value) == COUNT_FIELDS | RATE_FIELDS, "invalid_native_calibration_counts")
    for key in COUNT_FIELDS: count(value[key])
    for key in RATE_FIELDS:
        require(value[key] is None or 0 <= number(value[key]) <= 1, "invalid_native_calibration_rate")


def audit_native_calibration_assessment(assessment, expected_spec, observations, package, source_case=None):
    try:
        a = assessment
        require(type(a) is dict and set(a) == FIELDS and a["kind"] == "native_threshold_response_assessment" and
                type(a["schema_version"]) is int and a["schema_version"] == 1 and
                a["algorithm"] == "post-anchor-target-whole-window-foil-v1", "unknown_native_calibration_assessment")
        require(a["sha256"] == sha({k: v for k, v in a.items() if k != "sha256"}), "native_calibration_assessment_digest_mismatch")
        require(a["validity"] == "valid" and a["complete_observation_set"] is True and
                type(a["criterion_met"]) is bool and a["calibrated"] is False and a["evaluation_verdict"] is None,
                "unsupported_native_calibration_assessment_claim")
        candidate = package["kind"] == "timelearner_recognition_threshold_candidate"
        source_audit = audit_threshold_candidate(package, source_case) if candidate else audit_recognition_derivation(package, source_case)
        scorer = score_threshold_candidate if candidate else score_recognition_evaluation
        scored = scorer(expected_spec, observations, package)
        require(scored["validity"] == "valid", "native_calibration_requires_complete_primary_data")
        context = package["source_recognition"] if candidate else package
        require(a["run_id"] == scored["run_id"] and a["model_revision"] == scored["model_revision"] and
                a["training_pattern_hash"] == context["source_solo"]["protocol"]["pattern_hash"],
                "native_calibration_model_or_run_changed")
        require(type(a["criterion"]) is dict and a["criterion"] == expected_spec["criterion"] and
                type(a["criterion"]["reject_target_outside_window"]) is bool, "native_calibration_criterion_changed")
        number(a["criterion"]["begin_offset"])
        if a["criterion"]["end_offset"] is not None: number(a["criterion"]["end_offset"])
        target_violations = sum(row["label"] == "target" and (row["classification"] == "FN" or
            (expected_spec["criterion"]["reject_target_outside_window"] and bool(row["early_spikes"] or row["late_spikes"])))
            for row in scored["trials"])
        foil_responses = scored["pooled_counts"]["FP"]
        require(count(a["target_violations"]) == target_violations and count(a["foil_responses"]) == foil_responses and
                a["criterion_met"] is (target_violations == foil_responses == 0), "native_calibration_decision_disagrees_with_primary")
        _counts(a["pooled_counts"])
        require(a["pooled_counts"] == scored["pooled_counts"], "native_calibration_counts_disagree_with_primary")
        require(type(a["by_reset_policy"]) is dict and set(a["by_reset_policy"]) == set(scored["by_reset_policy"]),
                "native_calibration_reset_policies_changed")
        for policy, values in a["by_reset_policy"].items():
            _counts(values)
            common = scored["by_reset_policy"][policy]
            require(common["criterion_assessed"] is True and values == {key: common[key] for key in COUNT_FIELDS | RATE_FIELDS},
                    "native_calibration_policy_counts_disagree_with_primary")
        actual = {o["trial_id"]: o for o in observations}
        rows = []
        for row in scored["trials"]:
            o = actual[row["trial_id"]]
            violation = row["label"] == "target" and (row["classification"] == "FN" or
                (expected_spec["criterion"]["reject_target_outside_window"] and bool(row["early_spikes"] or row["late_spikes"])))
            rows.append({"run_id": o["run_id"], "trial_id": row["trial_id"], "sample_id": row["sample_id"],
                "label": row["label"], "pattern_hash": o["pattern_hash"], "reset_policy": row["reset_policy"],
                "begin": o["begin"], "end": o["end"], "response_begin": row["response_begin"], "response_end": row["response_end"],
                "spike_count": row["spike_count"], "inside_spikes": row["window_spikes"], "early_spikes": row["early_spikes"],
                "late_spikes": row["late_spikes"], "classification": row["classification"], "target_violation": violation,
                "observation_sha256": sha(o)})
        rows.sort(key=lambda row: (row["run_id"], row["trial_id"]))
        require(type(a["trials"]) is list and len(a["trials"]) == len(rows), "native_calibration_trials_changed")
        for row in a["trials"]:
            require(type(row) is dict and type(row["target_violation"]) is bool, "invalid_native_calibration_trial")
            count(row["spike_count"])
            for key in ("begin", "end", "response_begin", "response_end"): number(row[key])
            for key in ("inside_spikes", "early_spikes", "late_spikes"):
                require(type(row[key]) is list, "invalid_native_calibration_spike_array")
                for time in row[key]: number(time)
        require(a["trials"] == rows, "native_calibration_trials_disagree_with_primary")
        return {"schema_version": 1, "native_criterion_consistent": True, "source_audit": source_audit,
                "trials": len(rows), "criterion_met": a["criterion_met"], "target_violations": target_violations,
                "foil_responses": foil_responses, "native_execution_verified": False, "calibrated": False,
                "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_native_calibration_assessment:"+str(error)) from error
