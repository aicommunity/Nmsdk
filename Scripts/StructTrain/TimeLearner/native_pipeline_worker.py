"""Owned native Train/export/frozen evaluation, with portable primary evidence.

The Console validates and builds the effective native configuration. These
wrappers never synthesize a trained model. Stopped-state conversion requires
the explicit diagnostic-evaluate operation and retains diagnostic provenance.
Portable audits verify consistency; they do not attest arbitrary process records.
"""
from pathlib import Path, PurePosixPath
import hashlib

from .native_evidence import count, equal, load, number, require
from .model_identity import canonical_model_sha256 as sha
from .native_calibration_worker import _artifact_files, _digest, _evidence_boundary, _record, _signed, _write
from .process_runner import execute, verify_runtime
from .native_process_policy import validate_policy, execute_native, audit_contained_attempt
from .learned_evidence import load_case, audit_learned_state
from .recognition_evidence import audit_recognition_source
from .recognition_metrics import load_evaluation, score_recognition_evaluation


TRAINING_FIELDS = {"owner_class", "implementation_id", "configuration", "profile_archives", "optional_modes",
                   "calculate_mode", "structure_build_mode", "maximum_model_ticks"}
FIELDS = {
    "train": TRAINING_FIELDS,
    "preflight": TRAINING_FIELDS,
    "export": {"implementation_id", "source_solo", "conversion_spec"},
    "evaluate": {"owner_class", "implementation_id", "source_recognition", "maximum_model_ticks", "run_id",
                 "coverage_policy", "criterion", "trials"},
}
FIELDS["probe"] = {"owner_class", "implementation_id", "model", "profile_archives", "stimulus_profile", "probe",
                   "maximum_model_ticks", "maximum_wall_seconds"}
FIELDS["diagnostic-evaluate"] = (FIELDS["evaluate"] - {"source_recognition"}) | {"source_stopped", "conversion_spec"}
KINDS = {"preflight": "training", "train": "training", "export": "recognition_export", "evaluate": "evaluation", "diagnostic-evaluate": "diagnostic_evaluation"}
EXECUTION_KINDS = {"preflight": "preflight", "train": "training", "export": "conversion", "evaluate": "evaluation", "diagnostic-evaluate": "diagnostic_evaluation"}
COMMON_EXECUTION = {"kind", "schema_version", "execution", "job_sha256", "model_revision", "model_ticks",
                    "artifacts", "evaluation_verdict", "sha256"}
EXECUTION_FIELDS = {
    "preflight": {"frequency_hz", "model_time_begin", "model_time_end", "training_started", "controller_state",
                  "reference_probes", "observed_probes", "integration"},
    "train": {"attempt_id", "package_path", "package_sha256", "training_outcome", "completed_boundary",
              "frequency_hz", "model_time_begin", "model_time_end"},
    "export": {"source_solo_sha256", "model_sha256"},
    "evaluate": {"run_id", "model_sha256", "observed_trials", "expected_trials", "frequency_hz",
                 "model_time_begin", "model_time_end"},
}

EXECUTION_FIELDS["diagnostic-evaluate"] = EXECUTION_FIELDS["evaluate"] | {
    "diagnostic_only", "source_stopped_sha256", "training_outcome", "training_reason"}


def _load_source_case(mode, path):
    if mode in ("diagnostic-evaluate", "probe"):
        from .stopped_evidence import load_case as load_stopped
        return load_stopped(path)
    return load_case(path)


def _audit_source(job, source_case, mode):
    if mode == "export":
        require(job["source_solo"] == source_case[0], "pipeline_source_solo_changed")
        audit_learned_state(*source_case)
    elif mode == "diagnostic-evaluate":
        from .stopped_evidence import audit_stopped_state
        require(job["source_stopped"] == source_case[0], "pipeline_source_stopped_changed")
        audit_stopped_state(*source_case)
    elif mode == "evaluate":
        package = job["source_recognition"]
        if package.get("kind") == "timelearner_calibrated_recognition_state":
            from .calibrated_evidence import audit_calibrated_state
            audit_calibrated_state(package, source_case)
        else:
            audit_recognition_source(package, source_case)


@_evidence_boundary
def validate_job(mode, job, source_case=None):
    require(mode in FIELDS and type(job) is dict, "unknown_native_pipeline_job")
    if mode == "probe":
        from .native_characterization import validate_job as validate_probe_job
        result = validate_probe_job(job)
        if job['schema_version'] >= 2:
            from .stopped_evidence import audit_stopped_state
            require(source_case is not None and source_case[0] == job['source_stopped'], 'probe_original_stopped_primary_required')
            audit_stopped_state(*source_case)
            result['source_primary_checked'] = True
        else:
            require(source_case is None, "cold_probe_does_not_import_learned_state")
        return result
    live = mode in ("train", "preflight") and type(job.get("schema_version")) is int and job["schema_version"] == 2
    require(set(job) == FIELDS[mode] | {"kind", "schema_version", "sha256"} | ({"finalization_plan"} if live else set())
            and job["kind"] == "timelearner_native_"+KINDS[mode]+"_job" and
            type(job["schema_version"]) is int and job["schema_version"] == (2 if live else 1), "unknown_native_pipeline_job")
    _digest(job)
    require(type(job["implementation_id"]) is str and bool(job["implementation_id"].strip()), "pipeline_implementation_missing")
    if mode in ("train", "preflight"):
        require(source_case is None, "cold_training_does_not_import_learned_state")
        config = job["configuration"]
        from .composite_configuration import project_training_configuration
        # Validate the policy envelope, but execute/hash the original record.
        # Effective support still requires the native strict codec/readback.
        project_training_configuration(config)
        from .native_model_spec import validate_model_spec
        validate_model_spec(config['model'])
        require(type(config) is dict and type(config["model"]) is dict and
                type(config["model"]["branch"]) is bool and type(config["run_id"]) is str and config["run_id"],
                "invalid_training_declaration")
        require(type(job["profile_archives"]) is list and len(job["profile_archives"]) <= 32 and
                all(type(p) is dict for p in job["profile_archives"]), "invalid_training_profiles")
        modes = job["optional_modes"]
        require(type(modes) is dict and set(modes) == {"sync_capacitance_trim", "post_train_tuning", "auto_calibrate_threshold"}
                and type(modes["sync_capacitance_trim"]) is int and modes["sync_capacitance_trim"] == 0 and
                modes["post_train_tuning"] is live and modes["auto_calibrate_threshold"] is False,
                "training_optional_modes_not_yet_supported")
        require(all(type(job[k]) is int and job[k] in (0, 1) for k in ("calculate_mode", "structure_build_mode")),
                "invalid_training_control_mode")
    else:
        require(source_case is not None, "pipeline_original_primary_source_required")
        _audit_source(job, source_case, mode)
        config = source_case[0]["configuration"]
        source = job["source_solo"] if mode == "export" else job["source_stopped"] if mode == "diagnostic-evaluate" else job["source_recognition"]
        require(job["implementation_id"] == source["implementation_id"], "pipeline_implementation_changed")
    if mode != "export":
        require(job["owner_class"] == "NNeuronTimeLearner"+("Branch" if config["model"]["branch"] else "") and
                1 <= count(job["maximum_model_ticks"]) <= 1000000000, "pipeline_owner_or_tick_budget_invalid")
    if mode in ("evaluate", "diagnostic-evaluate"):
        # Version 1 deliberately supports only the verified reset-per-trial path.
        # The native continuous option remains outside this production wrapper.
        require(job["coverage_policy"] == "per_trial_windows", "pipeline_continuous_stream_not_yet_verified")
        trials = job["trials"]
        require(type(trials) is list and 1 <= len(trials) <= 10000 and type(job["run_id"]) is str and job["run_id"],
                "invalid_evaluation_trial_design")
        from .calibrated_evidence import REQUEST_FIELDS
        require(all(type(t) is dict and set(t) == REQUEST_FIELDS and t["run_id"] == job["run_id"] for t in trials),
                "invalid_evaluation_trial_scope")
        require(len({t["trial_id"] for t in trials}) == len(trials), "duplicate_evaluation_trial")
        if mode == "diagnostic-evaluate":
            require(len(trials) >= 2 and {t["label"] for t in trials} == {"target", "foil"},
                    "incomplete_diagnostic_evaluation_labels")
    result = {"job_sha256": job["sha256"], "primary_source_checked": mode not in ("train", "preflight"),
              "effective_model_checked": False, "native_configuration_validation_required": True}
    if mode in ('train', 'preflight') and job['configuration'].get('schema_version') == 6:
        from .composite_configuration import composite_declaration_scope
        result['composite_measurement_declaration'] = composite_declaration_scope(job['configuration'])
    elif mode in ('train', 'preflight') and job['configuration'].get('schema_version') == 7:
        from .candidate_window_contract import configuration_view
        configuration_view(job['configuration'])
        result['composite_measurement_declaration'] = dict(configuration_schema=7,protocol_schema=5,
            native_effective_preflight_required=True,live_measurement_admission_verified=False,
            training_certificate_verified=False)
    if live:
        from .live_training_worker import validate_live_plan
        result["finalization"] = validate_live_plan(job["finalization_plan"], config, job["implementation_id"])
    return result


def _artifact_records(directory, execution):
    records = execution["artifacts"]
    require(type(records) is list and all(type(r) is dict and set(r) == {"path", "bytes", "sha256"} and
            type(r["path"]) is str for r in records), "pipeline_artifact_schema")
    names = {r["path"] for r in records}
    require(len(names) == len(records), "duplicate_pipeline_artifact")
    composite = execution.get('schema_version') in (3,4)
    if composite:
        from .composite_primary import _paths, filesystem_primary_resolver
        _paths(list(names)); resolve = filesystem_primary_resolver(directory)
        for record in records:
            raw = resolve(record['path'])
            require(count(record['bytes']) == len(raw) and hashlib.sha256(raw).hexdigest() == record['sha256'],
                    'pipeline_artifact_changed')
        actual = set()
        for path in directory.rglob('*'):
            require(not path.is_symlink(), 'pipeline_artifact_symlink')
            if path.is_file() and path != directory/'execution.json':
                actual.add(path.relative_to(directory).as_posix())
        require(actual == names, 'pipeline_native_artifact_closure_changed')
        return names
    for r in records:
        path = PurePosixPath(r["path"])
        require(len(path.parts) == 1 and not path.is_absolute() and path.name not in (".", "..") and
                "\\" not in r["path"] and r == _record(directory/r["path"], directory), "pipeline_artifact_changed")
    require(names == {p.name for p in directory.iterdir() if p.is_file() and p.name != "execution.json"},
            "pipeline_native_artifact_closure_changed")
    return names


@_evidence_boundary
def audit_execution(mode, directory, job, source_case=None):
    validate_job(mode, job, source_case)
    if mode == "probe":
        from .native_characterization import audit_execution as audit_probe_execution
        require(load(Path(directory)/"job.json") == job, "pipeline_probe_job_changed")
        return audit_probe_execution(directory)
    directory = Path(directory)
    execution = load(directory/"execution.json");_digest(execution)
    live = mode == "train" and job["schema_version"] == 2
    adaptive = mode in ('train', 'preflight') and job['configuration'].get('schema_version') == 7
    composite = mode in ('train', 'preflight') and job['configuration'].get('schema_version') in (6,7)
    if composite:
        from .composite_measurement_contract import integral_number_view
        execution = integral_number_view(execution)
    from .composite_execution_evidence import EXTRA_FIELDS, audit_composite_execution
    if adaptive:
        from .candidate_window_execution_evidence import audit_candidate_window_execution as audit_composite_execution
    from .live_training_worker import EXECUTION_FIELDS as LIVE_EXECUTION_FIELDS
    require(set(execution) == COMMON_EXECUTION | EXECUTION_FIELDS[mode] | (LIVE_EXECUTION_FIELDS if live else set()) | (EXTRA_FIELDS if composite else set()) and
            execution["kind"] == "timelearner_native_"+EXECUTION_KINDS[mode]+"_execution" and
            type(execution["schema_version"]) is int and execution["schema_version"] == (4 if adaptive else 3 if composite else 2 if live else 1) and
            execution["job_sha256"] == job["sha256"] and load(directory/"job.json") == job and
            execution["evaluation_verdict"] is None, "pipeline_execution_scope_changed")
    names = _artifact_records(directory, execution)
    statuses = (("completed", "cancelled", "model_tick_budget_exhausted", "finalization_failed") if live else
                ("completed", "cancelled", "model_tick_budget_exhausted"))
    if composite and mode == 'train' and not live:
        statuses += ('training_start_failed',)
    require(execution["execution"] in statuses, "pipeline_execution_status_unknown")
    ticks = count(execution["model_ticks"])
    if mode != "export":
        config = job["configuration"] if mode in ("train", "preflight") else source_case[0]["configuration"]
        frequency = count(execution["frequency_hz"])
        require(frequency == config["model"]["frequency_hz"] and ticks <= job["maximum_model_ticks"] and
                equal(number(execution["model_time_end"])-number(execution["model_time_begin"]), ticks/frequency),
                "pipeline_clock_changed")
    if mode == "preflight":
        if composite:
            audit_composite_execution(execution, directory, names, mode=mode, base_version=1)
        require(execution["execution"] == "completed" and ticks == 0 and
                execution["training_started"] is False and execution["controller_state"] == "idle" and
                count(execution["reference_probes"]) == count(execution["observed_probes"]) == 0 and
                names == {"job.json", "initial-state.json"}, "preflight_started_training_or_has_extra_artifacts")
        initial = load(directory/"initial-state.json");_digest(initial)
        require(set(initial) == {"kind", "schema_version", "identity", "parameters", "configuration_sha256",
                "training_started", "dynamics_checkpoint", "sha256"} and
                initial["kind"] == "native_training_initial_state" and type(initial["schema_version"]) is int and
                initial["schema_version"] == 1 and initial["training_started"] is False and
                initial["dynamics_checkpoint"] is False and initial["configuration_sha256"] == sha(job["configuration"]),
                "preflight_initial_state_changed")
        identity = initial["identity"]
        require(identity["kind"] == "semantic_model_identity" and type(identity["schema_version"]) is int and
                identity["schema_version"] == 2 and identity["valid"] is True and identity["diagnostics"] == [] and
                identity["sha256"] == sha(identity["model"]) == execution["model_revision"],
                "preflight_model_binding_changed")
        from .native_model_spec import audit_initial_threshold
        audit_initial_threshold(job['configuration']['model'], identity)
        parameters, inputs = initial["parameters"], job["configuration"]["model"]["inputs"]
        require(type(parameters) is list and len(parameters) == len(inputs) and all(
                type(p) is dict and set(p) == {"length", "synapses", "resistance"} and
                count(p["length"]) == q["attachment"] and count(p["synapses"]) == q["synapses"] and
                number(p["resistance"]) > 0 and (q["resistance"] is None or p["resistance"] == q["resistance"])
                for p, q in zip(parameters, inputs)), "preflight_effective_parameters_changed")
        integration = execution["integration"]
        require(type(integration) is dict and set(integration) == {"valid", "reason", "channels"} and
                integration["valid"] is True and integration["reason"] == "", "preflight_integration_not_valid")
        channels = integration["channels"]
        require(type(channels) is list and bool(channels) and all(type(c) is dict and
                set(c) == {"path", "maximum_conductance", "maximum_step_gain"} and
                type(c["path"]) is str and bool(c["path"]) and number(c["maximum_conductance"]) >= 0 and
                0 <= number(c["maximum_step_gain"]) < 2 for c in channels) and
                len({c["path"] for c in channels}) == len(channels), "preflight_integration_channels_changed")
        return {"effective_initial_model_checked": True, "model_revision": execution["model_revision"],
                "input_count": len(parameters), "integration_channels": len(channels), "training_started": False,
                "native_execution_verified": False, "evaluation_verdict": None}
    if composite and mode == 'train' and execution['execution'] == 'training_start_failed':
        from .composite_execution_evidence import audit_composite_start_failure
        if adaptive:
            from .candidate_window_execution_evidence import audit_candidate_window_start_failure as audit_composite_start_failure
        return audit_composite_start_failure(execution, directory, names, job)
    if live:
        from .live_training_worker import audit_live_training
        from .native_model_spec import audit_initial_threshold
        audit_initial_threshold(job['configuration']['model'], load(directory/'initial-state.json')['identity'])
        return audit_live_training(directory, job, execution, names)
    if mode == "train":
        completed = execution["completed_boundary"]
        require(type(completed) is bool, "invalid_training_boundary")
        filename = "train_learned_state.json" if completed else "train_stopped_state.json"
        require(execution["package_path"] == filename and filename in names, "pipeline_training_package_missing")
        package = load(directory/filename)
        if completed:
            audit = audit_learned_state(*load_case(directory/filename))
        else:
            from .stopped_evidence import audit_stopped_state, load_case as load_stopped
            audit = audit_stopped_state(*load_stopped(directory/filename))
        # A fresh service gives the first attempt its native session/1 identity.
        # The declared attempt id remains in execution.json; no physics changes.
        effective_config = {**job["configuration"], "run_id": job["configuration"]["run_id"]+"/session/1"}
        require((composite or package["configuration"] == effective_config) and package["implementation_id"] == job["implementation_id"] and
                execution["package_sha256"] == package["sha256"] and execution["model_revision"] == package["model_revision"] and
                execution["training_outcome"] == package["training_outcome"] and
                execution["attempt_id"] == job["configuration"]["run_id"], "pipeline_training_model_changed")
        initial = load(directory/"initial-state.json");_digest(initial)
        require(initial["training_started"] is False and initial["dynamics_checkpoint"] is False and
                initial["configuration_sha256"] == sha(job["configuration"]) and
                initial["identity"]["valid"] is True and
                initial["identity"]["sha256"] == sha(initial["identity"]["model"]), "pipeline_cold_initial_state_invalid")
        from .native_model_spec import audit_initial_threshold
        audit_initial_threshold(job['configuration']['model'], initial['identity'])
        inputs = job["configuration"]["model"]["inputs"]
        require(len(initial["parameters"]) == len(inputs) and all(
            p["length"] == declared["attachment"] and p["synapses"] == declared["synapses"] and
            (declared["resistance"] is None or p["resistance"] == declared["resistance"])
            for p, declared in zip(initial["parameters"], inputs)), "pipeline_cold_parameters_changed")
        if composite:
            from .composite_execution_evidence import audit_initial_planning_configuration
            audit_initial_planning_configuration(package, job, initial)
            audit_composite_execution(execution, directory, names, mode=mode, base_version=1, package=package)
        require(execution["execution"] == "completed" or not completed, "interrupted_training_claims_completion")
        return {"training_audit": audit, "completed_boundary": completed, "training_outcome": package["training_outcome"],
                "native_execution_verified": False, "evaluation_verdict": None}
    model = load(directory/"model.json")
    require(execution["model_sha256"] == model["sha256"] and execution["model_revision"] == model["model_revision"],
            "pipeline_model_binding_changed")
    if mode == "export":
        require(execution["execution"] == "completed" and ticks == 0 and
                execution["source_solo_sha256"] == job["source_solo"]["sha256"] and
                model["source_solo"] == job["source_solo"] and model["conversion_spec"] == job["conversion_spec"],
                "pipeline_conversion_changed")
        return {"recognition_source_audit": audit_recognition_source(model, source_case),
                "native_execution_verified": False, "evaluation_verdict": None}
    diagnostic = mode == "diagnostic-evaluate"
    diagnostic_audit = None
    if diagnostic:
        from .diagnostic_recognition_evidence import audit_diagnostic_recognition
        require(model["source_solo"] == job["source_stopped"] and model["conversion_spec"] == job["conversion_spec"]
                and execution["diagnostic_only"] is True and execution["source_stopped_sha256"] == job["source_stopped"]["sha256"]
                and execution["training_outcome"] == job["source_stopped"]["training_outcome"]
                and execution["training_reason"] == job["source_stopped"]["reason"], "pipeline_diagnostic_model_changed")
        diagnostic_audit = audit_diagnostic_recognition(model, source_case)
    else:
        require(model == job["source_recognition"], "pipeline_frozen_source_changed")
    require(model == load(directory/"model-after.json") and
            execution["run_id"] == job["run_id"] and count(execution["expected_trials"]) == len(job["trials"]) and
            count(execution["observed_trials"]) <= len(job["trials"]), "pipeline_frozen_model_or_design_changed")
    spec = load(directory/"evaluation.json")
    design = []
    for index, q in enumerate(job["trials"]):
        design.append({**{k: v for k, v in q.items() if k not in
            ("run_id", "pattern_isi", "maximum_samples", "record_threshold_potential")},
            "presentation_index": index, "observation": f"trial-{index}.json"})
    expected_spec = {"kind": "timelearner_diagnostic_recognition_evaluation_spec" if diagnostic else "timelearner_recognition_evaluation_spec",
                     "schema_version": 1, "run_id": job["run_id"], "model_revision": model["model_revision"],
                     "coverage_policy": job["coverage_policy"], "criterion": job["criterion"], "trials": design}
    if diagnostic:
        expected_spec.update(diagnostic_only=True, source_stopped_sha256=job["source_stopped"]["sha256"], training_outcome=job["source_stopped"]["training_outcome"])
    require(spec == expected_spec, "pipeline_evaluation_design_changed")
    metrics = None
    if execution["execution"] == "completed":
        require(execution["observed_trials"] == len(design), "pipeline_evaluation_incomplete")
        if diagnostic:
            from .recognition_metrics import load_diagnostic_evaluation, score_diagnostic_recognition_evaluation
            metrics = score_diagnostic_recognition_evaluation(*load_diagnostic_evaluation(directory/"evaluation.json"), model, source_case)
        else:
            metrics = score_recognition_evaluation(*load_evaluation(directory/"evaluation.json"), model)
        require(metrics["validity"] == "valid", "pipeline_evaluation_invalid")
    return {"frozen_model_verified": True, **({"diagnostic_only": True, "source_diagnostic_audit": diagnostic_audit} if diagnostic else {}), "metrics": metrics, "native_execution_verified": False, "evaluation_verdict": None}


def _structured_live_exit(mode, job, process, directory):
    """Historical schema-1 run-manifest policy; preserve archived interpretation."""
    return (mode == "train" and job["schema_version"] == 2 and process["execution"] == "process_error" and
            type(process["returncode"]) is int and process["returncode"] == 2 and
            (Path(directory)/"execution.json").is_file())


def _structured_training_exit(mode, job, process, directory):
    """A nonzero native Train result is auditable, never automatically successful.

    The caller must still audit signed native data, owned runtime and the stopped
    boundary, and reject a completed-execution claim paired with exit code 2.
    """
    return (mode in ("train", "diagnostic-evaluate", "probe") and type(job.get("schema_version")) is int and
            job["schema_version"] in ((1, 2, 3, 4, 5, 6) if mode == "probe" else (1, 2))
            and process["execution"] == "process_error" and type(process["returncode"]) is int
            and process["returncode"] == 2 and (Path(directory)/"execution.json").is_file())


def _snapshot_source(source, destination, *, diagnostic=False):
    source = Path(source).resolve(strict=True)
    stem = source.name.removesuffix("_stopped_state.json" if diagnostic else "_learned_state.json")
    package = load(source)
    if package.get('schema_version') in (5,6):
        from .composite_package_evidence import audit_composite_package
        from .composite_primary import capture_primary_blobs, write_primary_snapshot, _paths
        summary_path = source.with_name(stem + ('_stopped_summary.json' if diagnostic else '_learned_summary.json'))
        summary = load(summary_path) if summary_path.exists() else None
        audit_composite_package(package, summary)
        archive = package['measurement_archive']
        references = [trial['primary_ref'] for group in archive['records'] for trial in group['raw_trials']]
        primary = capture_primary_blobs(archive['primary_blobs'], references, archive['maximum_total_primary_bytes'])
        _paths(list(primary) + [source.name] + ([summary_path.name] if summary is not None else []))
        write_primary_snapshot(primary, destination)
        (destination/source.name).write_bytes(source.read_bytes())
        if summary is not None:
            (destination/summary_path.name).write_bytes(summary_path.read_bytes())
        return destination/source.name
    files = [source, source.with_name(stem+("_stopped_summary.json" if diagnostic else "_learned_summary.json"))]
    for p in sorted(source.parent.glob(stem+("_stopped_trial_*.json" if diagnostic else "_state_trial_*.json"))):
        files.extend((p, p.with_suffix(".csv")))
    destination.mkdir()
    for p in files:
        require(not p.is_symlink() and p.is_file(), "pipeline_source_missing_or_symlink")
        (destination/p.name).write_bytes(p.read_bytes())
    return destination/source.name


@_evidence_boundary
def run_job(mode, job_path, source_path, runtime_path, output, maximum_wall_seconds, *, process_policy=None):
    job = load(Path(job_path).resolve(strict=True))
    source_case = _load_source_case(mode, Path(source_path).resolve(strict=True)) if source_path is not None else None
    preflight = validate_job(mode, job, source_case)
    policy = validate_policy(process_policy, maximum_wall_seconds)
    runtime = load(Path(runtime_path).resolve(strict=True));executable = verify_runtime(runtime)
    require(number(maximum_wall_seconds) > 0, "invalid_pipeline_wall_budget")
    from .native_cli import inspect_native_cli
    cli = inspect_native_cli(runtime, [mode])
    output = Path(output).resolve();output.mkdir(parents=True, exist_ok=False)
    _write(output/"runtime-cli-interface.json", cli)
    inputs = output/"input";inputs.mkdir();source_relative = None
    if source_path is not None:
        snapshot = _snapshot_source(source_path, inputs/"source", diagnostic=mode == "diagnostic-evaluate" or mode == "probe")
        source_case = _load_source_case(mode, snapshot);source_relative = snapshot.relative_to(output).as_posix()
        require(validate_job(mode, job, source_case) == preflight, "pipeline_source_changed_during_snapshot")
    _write(inputs/"job.json", job)
    if policy is not None:
        _write(inputs/"process-policy.json", policy)
    executor = execute if policy is None else execute_native
    options = ({"cooperative_capture": mode in ("preflight", "probe")} if policy is None else {"policy": policy})
    process = executor(runtime, ["--app-ini", str(Path(runtime["app_ini"]["path"]).resolve(strict=True)),
        "--timelearner-"+mode, str(inputs/"job.json"), "--timelearner-output", str(output/"native")],
        executable.parent, output/"process", maximum_wall_seconds, **options)
    verify_runtime(runtime)
    audit = None
    from .operational_diagnostics import permits_positive_audit
    operational_clear = permits_positive_audit(output/'process', process.get('operational_diagnostics'))
    if operational_clear and (process["execution"] == "completed" or _structured_training_exit(mode, job, process, output/"native")):
        require(process["runtime_provenance"] == "loaded_files_captured", "pipeline_loaded_runtime_missing")
        audit = audit_execution(mode, output/"native", job, source_case)
        if process["execution"] != "completed":
            require(load(output/"native/execution.json")["execution"] != "completed", "pipeline_nonzero_claims_completed_execution")
    result = {"kind": "timelearner_native_pipeline_run_manifest", "schema_version": 4 if policy is not None else 3 if mode == "diagnostic-evaluate" else 2, "operation": mode,
        **({"process_policy": policy} if policy is not None else {}),
        "execution": process["execution"], "validity": "valid" if audit else "unverified_execution",
        "job_sha256": job["sha256"], "source_package_path": source_relative,
        "runtime_fingerprint": runtime["runtime_fingerprint"], "source_closure": runtime["source_closure"],
        "preflight": preflight, "analysis": audit,
        "analysis_code": [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(Path(__file__).parent.glob("*.py"))],
        "artifacts": [_record(p, output) for p in _artifact_files(output)],
        "independent_partition_verified": False, "evaluation_verdict": None}
    _write(output/"run-manifest.json", _signed(result))
    return result


@_evidence_boundary
def audit_run_manifest(path, *, historical_analysis=None):
    """Recompute portable source, native result and process/runtime bindings."""
    require(historical_analysis in (None, 'learned-v2-no-capacitance',
                                   'training-v3-no-capacitance-history'), 'unknown_pipeline_historical_adapter')
    path = Path(path).resolve(strict=True);root = path.parent
    manifest = load(path);_digest(manifest)
    contained = type(manifest.get("schema_version")) is int and manifest["schema_version"] == 4
    require(set(manifest) == {"kind", "schema_version", "operation", "execution", "validity", "job_sha256",
            "source_package_path", "runtime_fingerprint", "source_closure", "preflight", "analysis", "analysis_code",
            "artifacts", "independent_partition_verified", "evaluation_verdict", "sha256"} | ({"process_policy"} if contained else set()) and
            manifest["kind"] == "timelearner_native_pipeline_run_manifest" and
            type(manifest["schema_version"]) is int and manifest["schema_version"] in (1, 2, 3, 4) and
            (contained or (manifest["schema_version"] == 3) == (manifest["operation"] == "diagnostic-evaluate")) and
            manifest["operation"] in FIELDS and manifest["independent_partition_verified"] is False and
            manifest["evaluation_verdict"] is None, "unknown_native_pipeline_run_manifest")
    records = manifest["artifacts"]
    require(type(records) is list and all(type(r) is dict and set(r) == {"path", "bytes", "sha256"} and
            type(r["path"]) is str for r in records), "pipeline_run_artifact_schema")
    names = {r["path"] for r in records}
    require(len(names) == len(records) and names == {p.relative_to(root).as_posix() for p in _artifact_files(root)
            if p != path}, "pipeline_run_artifact_closure_changed")
    for r in records:
        relative = PurePosixPath(r["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and "\\" not in r["path"], "pipeline_artifact_escape")
        actual = root/r["path"]
        require(actual.resolve(strict=True).is_relative_to(root) and _record(actual, root) == r, "pipeline_run_artifact_changed")
    mode = manifest["operation"];source = manifest["source_package_path"];source_case = None
    job = load(root/"input/job.json")
    if mode in ("train", "preflight") or (mode == "probe" and job['schema_version'] == 1):
        require(source is None, "pipeline_cold_training_has_source")
    else:
        require(type(source) is str and source in names and PurePosixPath(source).parent == PurePosixPath("input/source"),
                "pipeline_source_path_changed")
        source_case = _load_source_case(mode, root/source)
    job = load(root/"input/job.json")
    require(manifest["job_sha256"] == job["sha256"] and validate_job(mode, job, source_case) == manifest["preflight"],
            "pipeline_run_preflight_changed")
    process, runtime = load(root/"process/result.json"), load(root/"process/runtime.json")
    from .runtime import digest_json, runtime_content_identity
    require(manifest["execution"] == process["execution"] and manifest["runtime_fingerprint"] ==
            process["runtime_fingerprint"] == runtime["runtime_fingerprint"] == digest_json(runtime_content_identity(runtime)) and
            manifest["source_closure"] == runtime["source_closure"], "pipeline_run_runtime_changed")
    if contained:
        policy = validate_policy(manifest["process_policy"])
        require(policy is not None and load(root/"input/process-policy.json") == policy, "pipeline_process_policy_changed")
        auditable = process["execution"] == "completed" or _structured_training_exit(mode, job, process, root/"native")
        request = audit_contained_attempt(root/"process", runtime, policy, auditable=auditable)
    else:
        request = load(root/"process/request.json")
    arguments = request["arguments"]
    capture_arguments = (type(arguments) is list and len(arguments) == 8 and (contained or mode in ("preflight", "probe")) and
                         arguments[6] == "--timelearner-capture-directory")
    require(type(arguments) is list and len(arguments) == (8 if capture_arguments else 6) and all(type(a) is str for a in arguments) and
            arguments[:6:2] == ["--app-ini", "--timelearner-"+mode, "--timelearner-output"] and
            arguments[1] == runtime["app_ini"]["path"], "pipeline_process_arguments_changed")
    output = PurePosixPath(arguments[5])
    require(output.is_absolute() and output.name == "native" and
            PurePosixPath(arguments[3]) == output.parent/"input/job.json" and
            request["working_directory"] == str(PurePosixPath(runtime["executable"]["path"]).parent) and
            number(request["maximum_wall_seconds"]) > 0 and request["model_time"] is None, "pipeline_process_scope_changed")
    structured_exit = _structured_live_exit if manifest["schema_version"] == 1 else _structured_training_exit
    from .operational_diagnostics import permits_positive_audit
    operational_clear = permits_positive_audit(root/'process', process.get('operational_diagnostics'))
    auditable = operational_clear and (process["execution"] == "completed" or structured_exit(mode, job, process, root/"native"))
    if auditable:
        from .native_evidence import load_json
        owned = load(root/"process/owned-process.json");loaded = load_json(root/"process/loaded-files.json")
        require(type(loaded) is list and all(type(r) is dict and set(r) == {"path", "size", "sha256"} and
                type(r["path"]) is str and PurePosixPath(r["path"]).is_absolute() and
                type(r["size"]) is int and r["size"] >= 0 and type(r["sha256"]) is str and
                len(r["sha256"]) == 64 and all(c in "0123456789abcdef" for c in r["sha256"]) for r in loaded),
                "pipeline_loaded_files_schema_changed")
        require(len({r["path"] for r in loaded}) == len(loaded) and
                {k: runtime["executable"][k] for k in ("path", "size", "sha256")} in loaded and
                owned["executable"] == runtime["executable"]["path"] and
                owned["executable_sha256"] == runtime["executable"]["sha256"] and
                owned["runtime_fingerprint"] == runtime["runtime_fingerprint"] and count(owned["pid"]) > 0 and
                process["returncode"] == (0 if process["execution"] == "completed" else 2) and process["ownership_scope"] == ("bound_cgroup" if contained else "launched_executable_only") and
                process["runtime_provenance"] == "loaded_files_captured", "pipeline_owned_runtime_changed")
    audit = audit_execution(mode, root/"native", job, source_case) if auditable else None
    if mode in ("preflight", "probe") and auditable:
        arguments = request["arguments"]
        if "--timelearner-capture-directory" in arguments:
            require(arguments.count("--timelearner-capture-directory") == 1,
                    "cooperative_capture_argument_changed")
            index = arguments.index("--timelearner-capture-directory")
            require(index+1 < len(arguments) and PurePosixPath(arguments[index+1]).name == "process",
                    "cooperative_capture_argument_changed")
            require(type(arguments) is list and len(arguments) == 8 and
                    arguments[::2] == ["--app-ini", "--timelearner-"+mode, "--timelearner-output",
                                      "--timelearner-capture-directory"] and
                    arguments[1] == runtime["app_ini"]["path"] and
                    PurePosixPath(arguments[3]).name == "job.json" and
                    PurePosixPath(arguments[3]).parent.name == "input" and
                    PurePosixPath(arguments[5]).name == "native" and
                    PurePosixPath(arguments[3]).parents[1] == PurePosixPath(arguments[5]).parent ==
                    PurePosixPath(arguments[7]).parent, "cooperative_capture_argument_changed")
            for filename, kind in (("capture-ready.json", "native_runtime_capture_ready"),
                                   ("capture-ack.json", "native_runtime_capture_ack")):
                record = load(root/"process"/filename)
                require(type(record) is dict and type(record.get("schema_version")) is int and
                        type(record.get("pid")) is int and record == {"kind": kind, "schema_version": 1,
                        "pid": owned["pid"], "start_ticks": owned["start_ticks"]}, "cooperative_capture_identity_changed")
        else:
            require(not (root/"process/capture-ready.json").exists() and not (root/"process/capture-ack.json").exists(),
                    "cooperative_capture_argument_missing")
    if auditable and process["execution"] != "completed":
        require(load(root/"native/execution.json")["execution"] != "completed", "pipeline_nonzero_claims_completed_execution")
    comparison = audit
    adapter_used = False
    if historical_analysis is not None:
        # Recompute with the current auditor first. Only an explicitly selected,
        # known schema transition may project its result into the archived shape.
        # The final equality still checks every other field and all native/runtime
        # bindings above remain mandatory. Do not strip arbitrary version fields.
        require(mode == 'train' and type(audit) is dict and
                type(manifest['analysis']) is dict and type(audit.get('training_audit')) is dict and
                type(manifest['analysis'].get('training_audit')) is dict,
                'unsupported_pipeline_historical_analysis')
        old, current = manifest['analysis']['training_audit'], audit['training_audit']
        require(type(old.get('auditor_version')) is int and
                type(current.get('auditor_version')) is int and
                'capacitance_history' not in old and 'capacitance_history' not in current,
                'unsupported_pipeline_historical_analysis')
        if historical_analysis == 'learned-v2-no-capacitance':
            require(manifest['schema_version'] == 1 and audit.get('completed_boundary') is True and
                    old['auditor_version'] == 2 and 'capacitance_state' not in old and
                    current['auditor_version'] in (3, 5) and 'capacitance_state' in current and
                    current['capacitance_state'] is None, 'unsupported_pipeline_historical_analysis')
            projected = {**current, 'auditor_version': 2};projected.pop('capacitance_state')
        else:
            completed = audit.get('completed_boundary')
            require(type(completed) is bool and old['auditor_version'] == 3 and
                    current['auditor_version'] == (5 if completed else 4) and
                    'capacitance_state' in old and 'capacitance_state' in current,
                    'unsupported_pipeline_historical_analysis')
            projected = {**current, 'auditor_version': 3}
        comparison = {**audit, 'training_audit': projected};adapter_used = True
    require(manifest["analysis"] == comparison and manifest["validity"] == ("valid" if audit else "unverified_execution"),
            "pipeline_run_analysis_changed")
    result = {"run_evidence_consistent": True, "operation": mode, "native_execution_verified": False,
            "independent_partition_verified": False, "evaluation_verdict": None}
    if adapter_used:result['historical_analysis_adapter'] = historical_analysis
    return result
