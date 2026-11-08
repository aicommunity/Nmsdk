"""Production cold Train with a declared, learner-owned finalization phase.

This audits the real source Train and native phase separately. It neither
constructs integration-control scenarios nor invents a frozen evaluation.
"""
from .native_evidence import count, equal, load, number, require
from .model_identity import canonical_model_sha256 as sha
from .live_finalization_evidence import LIVE_FIELDS, PLAN_FIELDS, _signed
from .native_calibration_worker import POST_TUNE_FIELDS, SPEC_FIELDS
from .calibrated_evidence import REQUEST_FIELDS
from .calibration import validate_trial_design
from .finalization_boundary_evidence import audit_boundary
from .learned_evidence import load_case, audit_learned_state
from .stopped_evidence import load_case as load_stopped, audit_stopped_state
from .owned_posttune_evidence import audit_owned_phase_execution
from .posttune_transaction_evidence import audit_posttune_transaction

EXECUTION_FIELDS = {"training_started", "finalization_path", "finalization_sha256", "finalization_status",
                    "recognition_available", "recognition_package_path", "recognition_package_sha256",
                    "recognition_model_revision"}


def validate_live_plan(plan, configuration, implementation):
    _signed(plan, PLAN_FIELDS, "native_live_finalization_plan")
    require(plan["implementation_id"] == implementation, "live_job_implementation_changed")
    conversion = plan["conversion"]
    require(type(conversion) is dict and set(conversion) == {"schema_version", "mode", "resistance_bounds"} and
            type(conversion["schema_version"]) is int and conversion["schema_version"] == 1 and
            conversion["mode"] in {"identity", "historical_branch_n1_v1"} and
            type(conversion["resistance_bounds"]) is list and all(type(b) is dict and
            set(b) == {"minimum", "maximum"} and 0 < number(b["minimum"]) <= number(b["maximum"])
            for b in conversion["resistance_bounds"]), "live_job_nested_post_tune_forbidden")
    confirmation = plan["confirmation"]
    require(type(confirmation) is dict and set(confirmation) == SPEC_FIELDS and all(
            type(confirmation[k]) is str and confirmation[k].strip() for k in SPEC_FIELDS-{"criterion"}) and
            confirmation["protocol"] in {"historical_same_matrix", "frozen_independent_calibration"},
            "invalid_live_job_confirmation")
    criterion = confirmation["criterion"]
    require(type(criterion) is dict and set(criterion) == {"anchor", "begin_offset", "end_offset", "reject_target_outside_window"} and
            criterion["anchor"] in {"onset", "last_stimulus"} and type(criterion["reject_target_outside_window"]) is bool and
            number(criterion["begin_offset"]) >= 0 and (criterion["end_offset"] is None or
            number(criterion["end_offset"]) >= number(criterion["begin_offset"])), "invalid_live_job_response_window")
    p = plan["post_tune"]
    require(type(p) is dict and set(p) == POST_TUNE_FIELDS | {"schema_version", "finalization", "weight_probe_threshold"}
            and type(p["schema_version"]) is int and p["schema_version"] == 3 and
            p["mode"] in {"off", "keep_done", "canon_rmin", "flat_last_r", "search_synthetic"} and
            p["metric"] in {"auto", "ltzone", "soma_sum"} and
            p["finalization"] in {"calibrate", "keep_fixed_threshold"}, "invalid_live_job_post_tune_controls")
    if p["weight_probe_threshold"] is not None:
        number(p["weight_probe_threshold"])
    require(1 <= count(p["search_passes"]) <= 128 and 1 <= count(p["maximum_candidates"]) <= 4096 and
            1 <= count(p["maximum_recorded_samples"]) <= 100000000 and number(p["minimum_positive_gap"]) >= 0,
            "invalid_live_job_post_tune_budget")
    for k in ("canonical_floor", "canonical_last"):
        require(number(p[k]) >= 0, "invalid_live_job_canonical_resistance")
    bounds = p["resistance_bounds"]
    require(type(bounds) is list and all(type(b) is dict and set(b) == {"minimum", "maximum"} and
            0 < number(b["minimum"]) <= number(b["maximum"]) for b in bounds), "invalid_live_job_resistance_bounds")
    model = configuration["model"];dimension = len(model["inputs"])
    require(len(bounds) == (dimension if p["mode"] in {"canon_rmin", "flat_last_r", "search_synthetic"} else 0),
            "live_job_resistance_bound_dimension")
    trials, thresholds = plan["trials"], plan["thresholds"]
    require(type(trials) is list and 2 <= len(trials) <= 10000 and
            all(type(q) is dict and set(q) == REQUEST_FIELDS for q in trials), "invalid_live_job_trials")
    design = [{**{k: q[k] for k in ("trial_id", "sample_id", "label", "pattern_isi", "reset_policy", "duration")},
               "presentation_index": i} for i, q in enumerate(trials)]
    validate_trial_design(design)
    sample_ids = {}
    target_hash = sha(model["initial_isi"])
    for q in trials:
        require(len(q["pattern_isi"]) == dimension and q["pattern_hash"] == sha(q["pattern_isi"]) and
                type(q["run_id"]) is str and bool(q["run_id"].strip()) and
                type(q["record_threshold_potential"]) is bool and 2 <= count(q["maximum_samples"]) <= 10000000,
                "invalid_live_job_trial_identity")
        require(((q["label"] == "target") == (q["pattern_hash"] == target_hash)) and
                sample_ids.setdefault(q["sample_id"], (q["label"], q["pattern_hash"])) == (q["label"], q["pattern_hash"]),
                "live_job_target_or_sample_collision")
        ticks = number(q["duration"])*number(model["frequency_hz"])
        require(equal(ticks, round(ticks)) and ticks+1 <= q["maximum_samples"], "invalid_live_job_trial_budget")
        if p["metric"] == "ltzone" or p["metric"] == "auto" and not model["branch"]:
            require(q["record_threshold_potential"], "live_job_threshold_samples_required")
    require(type(thresholds) is list and len(thresholds) <= 256 and
            0 <= count(plan["maximum_calibration_candidates"]) <= 256, "invalid_live_job_grid_budget")
    for t in thresholds:
        number(t)
    if p["finalization"] == "keep_fixed_threshold":
        require(not thresholds and plan["maximum_calibration_candidates"] == 0, "live_fixed_job_has_unused_grid")
    else:
        require(bool(thresholds) and plan["maximum_calibration_candidates"] > 0, "live_calibration_grid_missing")
    # Native codecs also validate conversion/confirmation and effective target
    # matching, physics and public controls before any actual Train probe.
    return {"plan_sha256": plan["sha256"], "native_effective_preflight_required": True}


def audit_live_training(directory, job, execution, names):
    live = load(directory/"finalization.json")
    _signed(live, LIVE_FIELDS, "native_live_finalization")
    require(execution["finalization_path"] == "finalization.json" and "finalization.json" in names and
            execution["finalization_sha256"] == live["sha256"] and live["plan"] == job["finalization_plan"] and
            execution["finalization_status"] == live["status"] and live["status"] in
            {"completed", "stopped_diagnostic", "cancelled", "failed", "interrupted", "recovery_required"} and
            live["dynamic_checkpoint"] is False and live["evaluation_verdict"] is None,
            "live_job_finalization_binding_changed")
    started = bool(live["training_request"])
    require(type(execution["training_started"]) is bool and execution["training_started"] is started and
            type(execution["completed_boundary"]) is bool and type(execution["recognition_available"]) is bool,
            "live_job_training_axis_changed")
    initial = load(directory/"initial-state.json")
    require(initial["sha256"] == sha({k: v for k, v in initial.items() if k != "sha256"}) and
            initial["training_started"] is False and initial["dynamics_checkpoint"] is False and
            initial["configuration_sha256"] == sha(job["configuration"]) and initial["identity"]["valid"] is True and
            initial["identity"]["sha256"] == sha(initial["identity"]["model"]), "live_job_cold_initial_state_invalid")
    declared = job["configuration"]["model"]["inputs"]
    require(len(initial["parameters"]) == len(declared) and all(
        p["length"] == d["attachment"] and p["synapses"] == d["synapses"] and
        (d["resistance"] is None or p["resistance"] == d["resistance"])
        for p, d in zip(initial["parameters"], declared)), "live_job_cold_parameters_changed")
    source = audit = transaction = phase = None
    boundary = live["boundary"]
    if boundary is None:
        if job['configuration'].get('schema_version') == 6:
            from .composite_execution_evidence import audit_composite_execution
            audit_composite_execution(execution, directory, names, mode='train', base_version=2)
        require(not execution["completed_boundary"] and all(execution[k] is None for k in
                ("package_path", "package_sha256", "model_revision", "training_outcome")) and
                live["captured_model_time"] is None and live["entry_model_time"] is None and
                live["post_tune"] == {} and live["post_tune_execution"] == {}, "live_job_no_train_boundary_fabricated")
        require(not ({"train_learned_state.json", "train_stopped_state.json", "train_learned_summary.json",
                      "train_stopped_summary.json"} & names), "live_job_template_source_forbidden")
    else:
        require(started, "live_job_boundary_without_training")
        audit_boundary(boundary)
        completed = boundary["source_solo"]["kind"] == "timelearner_completed_state"
        filename = "train_learned_state.json" if completed else "train_stopped_state.json"
        require(execution["package_path"] == filename and filename in names and
                execution["completed_boundary"] is completed, "live_job_source_package_missing")
        source = load_case(directory/filename) if completed else load_stopped(directory/filename)
        audit = audit_learned_state(*source) if completed else audit_stopped_state(*source)
        package = source[0]
        require(boundary["schema_version"] == 2 and boundary["source_solo"] == package and
                boundary["training_request"] == live["training_request"] and
                boundary["implementation_id"] == job["implementation_id"], "live_job_source_boundary_changed")
        expected = {**job["configuration"], "run_id": job["configuration"]["run_id"]+"/session/1"}
        composite = job['configuration'].get('schema_version') == 6
        require((composite or package["configuration"] == expected) and package["implementation_id"] == job["implementation_id"] and
                execution["package_sha256"] == package["sha256"] and execution["model_revision"] == package["model_revision"] and
                execution["training_outcome"] == package["training_outcome"], "live_job_training_source_changed")
        if composite:
            from .composite_execution_evidence import audit_initial_planning_configuration, audit_composite_execution
            audit_initial_planning_configuration(package, job, initial)
            audit_composite_execution(execution, directory, names, mode='train', base_version=2, package=package)
        controls = boundary["controls"]["parameters"];binding = boundary["controls"]["bindings"]["IsNeedToTrain"]
        p = job["finalization_plan"]["post_tune"]
        require(controls["CalculateMode"] == job["calculate_mode"] and controls["StructureBuildMode"] == job["structure_build_mode"] and
                controls["ControllerVersion"] == 2 and controls["EnablePostTrainTuning"] is True and
                controls["AutoCalibrateFixedLTZThreshold"] is False and controls["UseCandidateMidOnNonSeparableTest"] is False and
                controls["EnablePostTrainMidThreshold"] is (p["finalization"] == "calibrate") and
                binding["connected"] is False, "live_job_effective_controls_changed")
        mode = {"off": 0, "canon_rmin": 1, "flat_last_r": 2, "keep_done": 3, "search_synthetic": 4}[p["mode"]]
        metric = {"auto": 0, "ltzone": 1, "soma_sum": 2}[p["metric"]]
        require(controls["PostTrainTipResistanceMode"] == mode and controls["PostTrainMidMetric"] == metric and
                (p["weight_probe_threshold"] is None or controls["PostTrainSilentThreshold"] == p["weight_probe_threshold"]),
                "live_job_public_post_tune_mode_changed")
        capture = number(live["captured_model_time"])
        require(number(execution["model_time_begin"]) <= capture <= number(execution["model_time_end"]),
                "live_job_capture_outside_execution")
    report = live["post_tune"]
    if report:
        require(source is not None and execution["completed_boundary"] and live["entry_model_time"] is not None,
                "live_job_phase_without_completed_source")
        frequency = number(execution["frequency_hz"]);entry = number(live["entry_model_time"])
        require(equal(entry-number(live["captured_model_time"]), 1/frequency) and
                entry < number(execution["model_time_end"]), "live_job_entry_clock_changed")
        end = number(execution["model_time_end"])
        phase_ticks = round((end-entry)*frequency)
        phase = audit_owned_phase_execution(live["post_tune_execution"], frequency,
                                           ticks=phase_ticks, begin=entry, end=end)
        require(equal(live["post_tune_execution"]["advance_times"][0], entry), "live_job_first_phase_tick_changed")
        plan = job["finalization_plan"]
        require(report["source_recognition"]["source_solo"] == source[0] and
                report["source_recognition"]["conversion_spec"] == plan["conversion"], "live_job_conversion_changed")
        for k in POST_TUNE_FIELDS:
            require(report[k] == plan["post_tune"][k], "live_job_phase_controls_changed:"+k)
        require(report.get("finalization", "calibrate") == plan["post_tune"]["finalization"] and
                report.get("weight_probe_threshold") == plan["post_tune"]["weight_probe_threshold"],
                "live_job_optional_phase_controls_changed")
        require(all(report[k] == plan[k] for k in ("trials", "thresholds", "maximum_calibration_candidates")) and
                report["confirmation_specification"] == plan["confirmation"], "live_job_phase_design_changed")
        transaction = audit_posttune_transaction(report, source)
        require(live["reason"] == report["status"], "live_job_phase_terminal_changed")
    else:
        require(live["post_tune_execution"] == {} and
                (live["entry_model_time"] is None or live["status"] == "recovery_required"), "live_job_missing_phase_receipt")
    available = (execution["execution"] == "completed" and execution["completed_boundary"] and
                 live["status"] == "completed" and report.get("status") in
                 {"weights_selected", "calibrated", "search_unresolved", "budget_exhausted"})
    require(execution["recognition_available"] is available, "live_job_recognition_availability_changed")
    if available:
        final = (report["selected_package"] if report["status"] == "weights_selected" else
                 report["calibrated_package"] if report["status"] == "calibrated" else report["source_recognition"])
        require(execution["recognition_package_path"] == "recognition-model.json" and "recognition-model.json" in names and
                load(directory/"recognition-model.json") == final and execution["recognition_package_sha256"] == final["sha256"] and
                execution["recognition_model_revision"] == final["model_revision"], "live_job_final_recognition_changed")
    else:
        require("recognition-model.json" not in names and all(execution[k] is None for k in
                ("recognition_package_path", "recognition_package_sha256", "recognition_model_revision")),
                "live_job_diagnostic_has_recognition_model")
    require(execution["attempt_id"] == job["configuration"]["run_id"], "live_job_attempt_changed")
    return {"training_audit": audit, "phase_audit": phase, "transaction_audit": transaction,
            "completed_boundary": execution["completed_boundary"], "recognition_available": available,
            "training_outcome": execution["training_outcome"], "finalization_status": live["status"],
            "native_execution_verified": False, "independent_partition_verified": False, "evaluation_verdict": None}
