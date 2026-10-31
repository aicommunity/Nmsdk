"""Audit live finalization values against fresh Train primaries, not saved replay.

Runtime/owned-process receipts are separate. JSON alone cannot attest cold
construction or the native scheduler, and never supplies a scientific PASS.
"""
from .finalization_boundary_evidence import audit_boundary
from .learned_evidence import audit_learned_state
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, equal, number, require
from .owned_posttune_evidence import audit_owned_phase_execution
from .posttune_transaction_evidence import audit_posttune_transaction
from .recognition_trial_evidence import audit_recognition_trial_set
from .stopped_evidence import audit_stopped_state

FIELDS = {"kind", "schema_version", "scenario", "calculate_mode", "connected", "cold_training",
          "live", "training_summary", "final_package", "frozen_replay", "scientific_verdict"}
LIVE_FIELDS = {"kind", "schema_version", "plan", "training_request", "status", "reason", "boundary",
               "captured_model_time", "entry_model_time", "post_tune", "post_tune_execution",
               "dynamic_checkpoint", "evaluation_verdict", "sha256"}
PLAN_FIELDS = {"kind", "schema_version", "implementation_id", "conversion", "post_tune", "trials",
               "thresholds", "maximum_calibration_candidates", "confirmation", "sha256"}


def _signed(value, fields, kind):
    require(type(value) is dict and set(value) == fields and value["kind"] == kind and
            type(value["schema_version"]) is int and value["schema_version"] == 1,
            "unknown_live_finalization_schema:" + kind)
    require(value["sha256"] == sha({k: v for k, v in value.items() if k != "sha256"}),
            "live_finalization_digest_mismatch:" + kind)


def audit_completed_live_finalization(record, source_case):
    """Completed execution including negative calibration outcomes, not success."""
    try:
        require(type(record) is dict and set(record) == FIELDS and record["kind"] == "native_live_finalization_control"
                and type(record["schema_version"]) is int and record["schema_version"] == 1,
                "unknown_live_finalization_control")
        require(type(record["scenario"]) is int and record["scenario"] in (0, 1) and
                type(record["calculate_mode"]) is int and record["calculate_mode"] in (0, 1) and
                type(record["connected"]) is bool and record["cold_training"] is True and
                record["scientific_verdict"] is None, "unsupported_live_finalization_claim")
        live = record["live"]
        _signed(live, LIVE_FIELDS, "native_live_finalization")
        plan = live["plan"]
        _signed(plan, PLAN_FIELDS, "native_live_finalization_plan")
        require(live["status"] == "completed" and live["dynamic_checkpoint"] is False and
                live["evaluation_verdict"] is None, "live_finalization_not_completed")
        boundary = live["boundary"]
        audit_boundary(boundary)
        require(boundary["schema_version"] == 2 and boundary["diagnostic_only"] is False and
                boundary["training_request"] == live["training_request"] and
                boundary["implementation_id"] == plan["implementation_id"], "live_boundary_request_binding_changed")
        solo = boundary["source_solo"]
        require(solo == source_case[0] and record["training_summary"] == source_case[1],
                "live_training_source_changed")
        learned = audit_learned_state(*source_case)
        controls = boundary["controls"]["parameters"]
        binding = boundary["controls"]["bindings"]["IsNeedToTrain"]
        require(controls["ControllerVersion"] == 2 and controls["CalculateMode"] == record["calculate_mode"] and
                controls["EnablePostTrainTuning"] is True and controls["AutoCalibrateFixedLTZThreshold"] is False and
                controls["IsNeedToTrain"] is True and binding["connected"] is record["connected"],
                "live_public_control_mismatch")
        frequency = number(solo["configuration"]["model"]["frequency_hz"])
        capture, entry = number(live["captured_model_time"]), number(live["entry_model_time"])
        require(capture >= number(live["training_request"]["started_model_time"]) and frequency > 0 and
                equal(entry-capture, 1/frequency), "live_finalization_entry_not_next_tick")
        report, execution = live["post_tune"], live["post_tune_execution"]
        phase = audit_owned_phase_execution(execution, frequency)
        require(equal(execution["advance_times"][0], entry), "live_post_tune_start_clock_mismatch")
        require(report["source_recognition"]["source_solo"] == solo and
                report["source_recognition"]["conversion_spec"] == plan["conversion"],
                "live_conversion_source_changed")
        for key in ("mode", "metric", "canonical_floor", "canonical_last", "resistance_bounds", "search_passes",
                    "maximum_candidates", "maximum_recorded_samples", "minimum_positive_gap", "finalization"):
            require(report[key] == plan["post_tune"][key], "live_post_tune_plan_changed:" + key)
        require(report.get("weight_probe_threshold") == plan["post_tune"]["weight_probe_threshold"] and
                all(report[key] == plan[key] for key in ("trials", "thresholds", "maximum_calibration_candidates")) and
                report["confirmation_specification"] == plan["confirmation"], "live_post_tune_design_changed")
        transaction = audit_posttune_transaction(report, source_case)
        require(live["reason"] == report["status"], "live_terminal_result_changed")
        if report["status"] == "weights_selected":
            final = report["selected_package"]
        elif report["status"] == "calibrated":
            final = report["calibrated_package"]
        else:
            require(report["source_restored"] is True, "live_negative_result_not_restored")
            final = report["source_recognition"]
        require(record["final_package"] == final, "live_final_model_changed")
        matrix = record["frozen_replay"]
        require(type(matrix) is dict and set(matrix) == {"requests", "observations"} and
                len(matrix["requests"]) == len(plan["trials"]), "live_frozen_matrix_incomplete")
        for q, declared in zip(matrix["requests"], plan["trials"]):
            require({k: v for k, v in q.items() if k not in {"run_id", "trial_id"}} ==
                    {k: v for k, v in declared.items() if k not in {"run_id", "trial_id"}} and
                    q["trial_id"] == declared["trial_id"] + "/frozen-replay", "live_frozen_design_changed")
        expected = {(q["run_id"], q["trial_id"]): q for q in matrix["requests"]}
        require(len(expected) == len(plan["trials"]), "live_frozen_duplicate_trial")
        frozen = audit_recognition_trial_set(matrix["observations"], expected, final)
        require(frozen["all_observations_valid"], "invalid_live_frozen_observation")
        for observation in matrix["observations"]:
            q = expected[(observation["run_id"], observation["trial_id"])]
            require(all(observation[k] == q[k] for k in ("pattern_isi", "reset_policy", "maximum_samples")) and
                    equal(number(observation["end"])-number(observation["begin"]), number(q["duration"])),
                    "live_frozen_condition_mismatch")
        return {"schema_version": 1, "training_source_audit": learned, "phase_audit": phase,
                "transaction_audit": transaction, "frozen_replay_audit": frozen,
                "cold_construction_and_native_execution_attested": False,
                "statistical_independence_verified": False, "scientific_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_live_finalization:" + str(error)) from error


def audit_pre_entry_live_finalization(record, source_case=None):
    """A stopped or rejected entry supplies no trained recognition evaluation."""
    try:
        require(type(record) is dict and set(record) == FIELDS and record["kind"] == "native_live_finalization_control"
                and type(record["schema_version"]) is int and record["schema_version"] == 1,
                "unknown_live_finalization_control")
        scenario = record["scenario"]
        require(type(scenario) is int and scenario in range(2, 8) and
                type(record["calculate_mode"]) is int and record["calculate_mode"] in (0, 1) and
                type(record["connected"]) is bool and record["cold_training"] is True and
                record["scientific_verdict"] is None, "unsupported_live_rejection_claim")
        live = record["live"]
        _signed(live, LIVE_FIELDS, "native_live_finalization")
        _signed(live["plan"], PLAN_FIELDS, "native_live_finalization_plan")
        require(live["dynamic_checkpoint"] is False and live["evaluation_verdict"] is None and
                live["entry_model_time"] is None and live["post_tune"] == {} and live["post_tune_execution"] == {} and
                record["final_package"] == {} and record["frozen_replay"] == {"requests": [], "observations": []},
                "rejected_live_entry_has_recognition_evidence")
        status, reason = {
            2: ("stopped_diagnostic", "training_has_no_completed_certificate"),
            3: ("failed", "live_finalization_public_mode_mismatch"),
            4: ("interrupted", "learner_reset"),
            5: ("failed", "native_finalization_external_stop"),
            6: ("failed", "unbalanced_live_finalization_design"),
            7: ("failed", "native_owned_post_tune_requires_uniform_frequency_tree"),
        }[scenario]
        require((live["status"], live["reason"]) == (status, reason), "live_rejection_reason_mismatch")
        if scenario in (6, 7):
            require(source_case is None and live["boundary"] is None and live["training_request"] == {} and
                    record["training_summary"] == {} and live["captured_model_time"] is None,
                    "preflight_rejection_has_training_boundary")
            if scenario == 6:
                require({q["label"] for q in live["plan"]["trials"]} == {"target"},
                        "invalid_design_rejection_source_changed")
            source = None
        else:
            boundary = live["boundary"]
            audit_boundary(boundary)
            require(boundary["schema_version"] == 2 and boundary["training_request"] == live["training_request"] and
                    boundary["implementation_id"] == live["plan"]["implementation_id"] and
                    boundary["source_solo"] == source_case[0] and record["training_summary"] == source_case[1],
                    "live_rejection_training_source_changed")
            require(number(live["captured_model_time"]) >= number(live["training_request"]["started_model_time"]),
                    "invalid_live_rejection_capture_time")
            p, bindings = boundary["controls"]["parameters"], boundary["controls"]["bindings"]
            require(p["CalculateMode"] == record["calculate_mode"] and
                    bindings["IsNeedToTrain"]["connected"] is record["connected"], "live_rejection_controls_changed")
            if scenario == 2:
                require(boundary["diagnostic_only"] is True and source_case[0]["certificate"] is None and
                        boundary["training_outcome"] == "budget_exhausted", "invalid_live_stopped_certificate")
                source = audit_stopped_state(*source_case)
            else:
                require(boundary["diagnostic_only"] is False, "queued_rejection_requires_completed_source")
                source = audit_learned_state(*source_case)
        return {"schema_version": 1, "scenario": scenario, "training_source_audit": source,
                "no_recognition_evidence": True, "actual_control_and_physics_interventions_attested": False,
                "scientific_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_live_rejection:" + str(error)) from error
