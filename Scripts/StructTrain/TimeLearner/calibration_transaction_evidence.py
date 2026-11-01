"""Independently recheck a complete native threshold transaction's measured grid.

Recorded consistency cannot attest process execution or physical rollback.
Only complete search/confirmation matrices can support a calibrated claim;
cancelled or recovery-required reports remain diagnostic evidence.
"""
from .calibrated_evidence import (REQUEST_FIELDS, audit_calibrated_state,
                                  audit_native_calibration_matrix)
from .calibration import RULE, _validate_spec, calibration_dataset_digest
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, after, count, number, require

FIELDS = {"kind", "schema_version", "algorithm", "source_recognition_sha256", "source_recognition",
          "thresholds", "maximum_candidates", "trials", "attempt_id", "clock_id", "protocol",
          "data_partition_id", "status", "reason", "candidates", "selected_index", "confirmation",
          "active_matrix", "criterion", "calibrated_package", "calibrated", "source_restored",
          "dynamic_checkpoint", "grid_selection_embedded_in_model_proof", "statistical_independence_verified",
          "evaluation_verdict", "sha256"}


def _semantic(requests):
    return [{k: v for k, v in q.items() if k != "run_id"} for q in requests]


def audit_native_calibration_transaction(report, source_case=None):
    try:
        r = report
        require(type(r) is dict and set(r) == FIELDS and
                r["kind"] == "native_threshold_calibration_transaction" and
                type(r["schema_version"]) is int and r["schema_version"] == 1 and
                r["algorithm"] == "declared-grid-fresh-confirmation-native-driver-v1", "unknown_calibration_transaction")
        require(r["sha256"] == sha({k: v for k, v in r.items() if k != "sha256"}), "calibration_transaction_digest_mismatch")
        status = r["status"]
        require(status in {"calibrated", "nonseparable", "budget_exhausted", "confirmation_failed", "cancelled", "failed", "recovery_required"},
                "calibration_transaction_not_terminal")
        require(type(r["reason"]) is str and type(r["calibrated"]) is bool and
                r["calibrated"] is (status == "calibrated") and type(r["source_restored"]) is bool and
                r["source_restored"] is (status in {"nonseparable", "budget_exhausted", "confirmation_failed", "cancelled", "failed"}) and
                r["dynamic_checkpoint"] is False and r["grid_selection_embedded_in_model_proof"] is False and
                r["statistical_independence_verified"] is False and r["evaluation_verdict"] is None,
                "unsupported_calibration_transaction_claim")
        source = r["source_recognition"]
        require(type(source) is dict and source["kind"] == "timelearner_recognition_state" and
                source["sha256"] == r["source_recognition_sha256"] == sha({k: v for k, v in source.items() if k != "sha256"}),
                "calibration_transaction_source_changed")
        criterion = r["criterion"]
        require(type(criterion) is dict and set(criterion) == {"anchor", "begin_offset", "end_offset", "reject_target_outside_window"} and
                criterion["anchor"] in {"onset", "last_stimulus"} and type(criterion["reject_target_outside_window"]) is bool and
                number(criterion["begin_offset"]) >= 0 and (criterion["end_offset"] is None or
                number(criterion["end_offset"]) >= number(criterion["begin_offset"])), "invalid_calibration_transaction_criterion")
        design = r["trials"]
        require(type(design) is list and all(type(q) is dict and set(q) == REQUEST_FIELDS for q in design),
                "unknown_calibration_transaction_design")
        trials = [{**{k: q[k] for k in ("trial_id", "sample_id", "label", "pattern_isi", "reset_policy", "duration")},
                   "presentation_index": i} for i, q in enumerate(design)]
        full_criterion = {"id": "post_anchor_target_whole_window_foil_v1", **criterion}
        spec = {"kind": "timelearner_threshold_calibration_spec", "schema_version": 1,
                "calibration_id": r["attempt_id"], "protocol": r["protocol"], "data_partition_id": r["data_partition_id"],
                "source_recognition_sha256": source["sha256"], "source_model_revision": source["model_revision"],
                "coverage_policy": "per_trial_windows", "criterion": full_criterion, "trials": trials,
                "thresholds": r["thresholds"], "maximum_candidates": r["maximum_candidates"], "selection_rule": RULE}
        spec["dataset_digest"] = calibration_dataset_digest(spec["coverage_policy"], full_criterion, trials)
        thresholds, _ = _validate_spec(spec)
        require(len(r["thresholds"]) <= 256 and count(r["maximum_candidates"]) <= 256 and
                type(r["clock_id"]) is str and bool(r["clock_id"].strip()), "invalid_calibration_transaction_budget_or_clock")
        for q in design:
            require(type(q["record_threshold_potential"]) is bool and 2 <= count(q["maximum_samples"]) <= 10000000 and
                    q["pattern_hash"] == sha(q["pattern_isi"]), "invalid_calibration_transaction_request")
        rows = r["candidates"]
        require(type(rows) is list and len(rows) <= len(thresholds), "calibration_transaction_grid_over_budget")
        successful, previous_end = [], None
        for index, row in enumerate(rows):
            require(type(row) is dict and set(row) == {"candidate_index", "candidate", "matrix", "assessment"} and
                    count(row["candidate_index"]) == index and
                    number(row["candidate"]["threshold"]) == number(thresholds[index]) and
                    row["candidate"]["source_recognition"] == source, "calibration_transaction_grid_changed")
            matrix = row["matrix"]
            require(_semantic(matrix["requests"]) == _semantic(design), "calibration_transaction_measurement_design_changed")
            run_id = audit_native_calibration_matrix(matrix, row["assessment"], criterion,
                row["candidate"], source_case, require_success=False)
            require(run_id == r["attempt_id"]+"/search/"+str(index), "calibration_transaction_run_scope_changed")
            begin = min(number(o["begin"]) for o in matrix["observations"])
            end = max(number(o["end"]) for o in matrix["observations"])
            require(previous_end is None or after(begin, previous_end), "calibration_transaction_grid_overlaps")
            previous_end = end
            if row["assessment"]["criterion_met"]: successful.append(index)
        complete = status in {"calibrated", "nonseparable", "budget_exhausted", "confirmation_failed"}
        require(not complete or len(rows) == len(thresholds), "calibration_transaction_missing_candidates")
        selected = r["selected_index"]
        if selected is not None:
            require(count(selected) in successful and selected == successful[0], "calibration_transaction_wrong_selection")
        if status in {"calibrated", "confirmation_failed"}:
            require(selected is not None, "calibration_transaction_missing_selection")
        if status in {"nonseparable", "budget_exhausted"}:
            require(not successful and selected is None and
                    (status == "nonseparable") is (len(thresholds) == len(r["thresholds"])),
                    "calibration_transaction_wrong_negative_status")
        package_audit = None
        if status == "calibrated":
            package = r["calibrated_package"]
            package_audit = audit_calibrated_state(package, source_case)
            proof = package["calibration_proof"]
            require(package["source_candidate"] == rows[selected]["candidate"] and
                    proof["search"] == rows[selected]["matrix"] and proof["confirmation"] == r["confirmation"] and
                    proof["specification"] == {"protocol": r["protocol"], "data_partition_id": r["data_partition_id"],
                        "attempt_id": r["attempt_id"], "clock_id": r["clock_id"], "criterion": criterion},
                    "calibration_transaction_confirmation_changed")
            require(proof["confirmation"]["requests"][0]["run_id"] == r["attempt_id"]+"/confirmation" and
                    after(min(number(o["begin"]) for o in proof["confirmation"]["observations"]), previous_end),
                    "calibration_transaction_confirmation_precedes_grid")
        else:
            require(r["calibrated_package"] is None, "calibration_transaction_uncommitted_package_claim")
        if status in {"nonseparable", "budget_exhausted"}:
            require(r["confirmation"] == {"requests": [], "observations": []}, "calibration_transaction_unexpected_confirmation")
        require(type(r["active_matrix"]) is dict and set(r["active_matrix"]) == {"requests", "observations"} and
                all(type(r["active_matrix"][key]) is list for key in ("requests", "observations")),
                "unknown_calibration_transaction_active_matrix")
        if status == "calibrated":
            require(r["active_matrix"] == r["confirmation"], "calibration_transaction_active_confirmation_changed")
        elif status in {"nonseparable", "budget_exhausted"}:
            require(r["active_matrix"] == {"requests": [], "observations": []}, "calibration_transaction_unexpected_active_matrix")
        return {"schema_version": 1, "transaction_evidence_consistent": True, "status": status,
                "diagnostic_only": status in {"confirmation_failed", "cancelled", "failed", "recovery_required"},
                "negative_status_verified": status in {"nonseparable", "budget_exhausted"},
                "calibrated": status == "calibrated", "measured_candidates": len(rows), "selected_index": selected,
                "package_audit": package_audit, "native_execution_verified": False, "owner_restoration_verified": False,
                "partial_observations_validated": False, "statistical_independence_verified": False,
                "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_calibration_transaction:"+str(error)) from error
