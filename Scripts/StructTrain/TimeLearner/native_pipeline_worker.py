"""Owned native Train/export/frozen evaluation, with portable primary evidence.

The Console validates and builds the effective native configuration. These
wrappers never synthesize a trained model or convert a stopped diagnostic state.
Portable audits verify consistency; they do not attest arbitrary process records.
"""
from pathlib import Path, PurePosixPath
import hashlib

from .native_evidence import count, equal, load, number, require
from .model_identity import canonical_model_sha256 as sha
from .native_calibration_worker import _digest, _evidence_boundary, _record, _signed, _write
from .process_runner import execute, verify_runtime
from .learned_evidence import load_case, audit_learned_state
from .recognition_evidence import audit_recognition_source
from .recognition_metrics import load_evaluation, score_recognition_evaluation


FIELDS = {
    "train": {"owner_class", "implementation_id", "configuration", "profile_archives", "optional_modes",
              "calculate_mode", "structure_build_mode", "maximum_model_ticks"},
    "export": {"implementation_id", "source_solo", "conversion_spec"},
    "evaluate": {"owner_class", "implementation_id", "source_recognition", "maximum_model_ticks", "run_id",
                 "coverage_policy", "criterion", "trials"},
}
KINDS = {"train": "training", "export": "recognition_export", "evaluate": "evaluation"}
EXECUTION_KINDS = {"train": "training", "export": "conversion", "evaluate": "evaluation"}
COMMON_EXECUTION = {"kind", "schema_version", "execution", "job_sha256", "model_revision", "model_ticks",
                    "artifacts", "evaluation_verdict", "sha256"}
EXECUTION_FIELDS = {
    "train": {"attempt_id", "package_path", "package_sha256", "training_outcome", "completed_boundary",
              "frequency_hz", "model_time_begin", "model_time_end"},
    "export": {"source_solo_sha256", "model_sha256"},
    "evaluate": {"run_id", "model_sha256", "observed_trials", "expected_trials", "frequency_hz",
                 "model_time_begin", "model_time_end"},
}


def _audit_source(job, source_case, mode):
    if mode == "export":
        require(job["source_solo"] == source_case[0], "pipeline_source_solo_changed")
        audit_learned_state(*source_case)
    elif mode == "evaluate":
        package = job["source_recognition"]
        if package.get("kind") == "timelearner_calibrated_recognition_state":
            from .calibrated_evidence import audit_calibrated_state
            audit_calibrated_state(package, source_case)
        else:
            audit_recognition_source(package, source_case)


@_evidence_boundary
def validate_job(mode, job, source_case=None):
    require(mode in FIELDS and type(job) is dict and set(job) == FIELDS[mode] | {"kind", "schema_version", "sha256"}
            and job["kind"] == "timelearner_native_"+KINDS[mode]+"_job" and
            type(job["schema_version"]) is int and job["schema_version"] == 1, "unknown_native_pipeline_job")
    _digest(job)
    require(type(job["implementation_id"]) is str and bool(job["implementation_id"].strip()), "pipeline_implementation_missing")
    if mode == "train":
        require(source_case is None, "cold_training_does_not_import_learned_state")
        config = job["configuration"]
        require(type(config) is dict and type(config["model"]) is dict and
                type(config["model"]["branch"]) is bool and type(config["run_id"]) is str and config["run_id"],
                "invalid_training_declaration")
        require(type(job["profile_archives"]) is list and len(job["profile_archives"]) <= 32 and
                all(type(p) is dict for p in job["profile_archives"]), "invalid_training_profiles")
        modes = job["optional_modes"]
        require(type(modes) is dict and set(modes) == {"sync_capacitance_trim", "post_train_tuning", "auto_calibrate_threshold"}
                and type(modes["sync_capacitance_trim"]) is int and modes["sync_capacitance_trim"] == 0 and
                modes["post_train_tuning"] is False and modes["auto_calibrate_threshold"] is False,
                "training_optional_modes_not_yet_supported")
        require(all(type(job[k]) is int and job[k] in (0, 1) for k in ("calculate_mode", "structure_build_mode")),
                "invalid_training_control_mode")
    else:
        require(source_case is not None, "pipeline_original_primary_source_required")
        _audit_source(job, source_case, mode)
        config = source_case[0]["configuration"]
        source = job["source_solo"] if mode == "export" else job["source_recognition"]
        require(job["implementation_id"] == source["implementation_id"], "pipeline_implementation_changed")
    if mode != "export":
        require(job["owner_class"] == "NNeuronTimeLearner"+("Branch" if config["model"]["branch"] else "") and
                1 <= count(job["maximum_model_ticks"]) <= 1000000000, "pipeline_owner_or_tick_budget_invalid")
    if mode == "evaluate":
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
    return {"job_sha256": job["sha256"], "primary_source_checked": mode != "train",
            "effective_model_checked": False, "native_configuration_validation_required": True}


def _artifact_records(directory, execution):
    records = execution["artifacts"]
    require(type(records) is list and all(type(r) is dict and set(r) == {"path", "bytes", "sha256"} and
            type(r["path"]) is str for r in records), "pipeline_artifact_schema")
    names = {r["path"] for r in records}
    require(len(names) == len(records), "duplicate_pipeline_artifact")
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
    directory = Path(directory)
    execution = load(directory/"execution.json");_digest(execution)
    require(set(execution) == COMMON_EXECUTION | EXECUTION_FIELDS[mode] and
            execution["kind"] == "timelearner_native_"+EXECUTION_KINDS[mode]+"_execution" and
            type(execution["schema_version"]) is int and execution["schema_version"] == 1 and
            execution["job_sha256"] == job["sha256"] and load(directory/"job.json") == job and
            execution["evaluation_verdict"] is None, "pipeline_execution_scope_changed")
    names = _artifact_records(directory, execution)
    require(execution["execution"] in ("completed", "cancelled", "model_tick_budget_exhausted"), "pipeline_execution_status_unknown")
    ticks = count(execution["model_ticks"])
    if mode != "export":
        config = job["configuration"] if mode == "train" else source_case[0]["configuration"]
        frequency = count(execution["frequency_hz"])
        require(frequency == config["model"]["frequency_hz"] and ticks <= job["maximum_model_ticks"] and
                equal(number(execution["model_time_end"])-number(execution["model_time_begin"]), ticks/frequency),
                "pipeline_clock_changed")
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
        require(package["configuration"] == job["configuration"] and package["implementation_id"] == job["implementation_id"] and
                execution["package_sha256"] == package["sha256"] and execution["model_revision"] == package["model_revision"] and
                execution["training_outcome"] == package["training_outcome"] and
                execution["attempt_id"] == job["configuration"]["run_id"], "pipeline_training_model_changed")
        initial = load(directory/"initial-state.json");_digest(initial)
        require(initial["training_started"] is False and initial["dynamics_checkpoint"] is False and
                initial["configuration_sha256"] == sha(job["configuration"]) and
                initial["identity"]["valid"] is True and
                initial["identity"]["sha256"] == sha(initial["identity"]["model"]), "pipeline_cold_initial_state_invalid")
        inputs = job["configuration"]["model"]["inputs"]
        require(len(initial["parameters"]) == len(inputs) and all(
            p["length"] == declared["attachment"] and p["synapses"] == declared["synapses"] and
            (declared["resistance"] is None or p["resistance"] == declared["resistance"])
            for p, declared in zip(initial["parameters"], inputs)), "pipeline_cold_parameters_changed")
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
    require(model == job["source_recognition"] == load(directory/"model-after.json") and
            execution["run_id"] == job["run_id"] and count(execution["expected_trials"]) == len(job["trials"]) and
            count(execution["observed_trials"]) <= len(job["trials"]), "pipeline_frozen_model_or_design_changed")
    spec = load(directory/"evaluation.json")
    design = []
    for index, q in enumerate(job["trials"]):
        design.append({**{k: v for k, v in q.items() if k not in
            ("run_id", "pattern_isi", "maximum_samples", "record_threshold_potential")},
            "presentation_index": index, "observation": f"trial-{index}.json"})
    require(spec == {"kind": "timelearner_recognition_evaluation_spec", "schema_version": 1, "run_id": job["run_id"],
            "model_revision": model["model_revision"], "coverage_policy": job["coverage_policy"],
            "criterion": job["criterion"], "trials": design}, "pipeline_evaluation_design_changed")
    metrics = None
    if execution["execution"] == "completed":
        require(execution["observed_trials"] == len(design), "pipeline_evaluation_incomplete")
        metrics = score_recognition_evaluation(*load_evaluation(directory/"evaluation.json"), model)
        require(metrics["validity"] == "valid", "pipeline_evaluation_invalid")
    return {"frozen_model_verified": True, "metrics": metrics, "native_execution_verified": False, "evaluation_verdict": None}


def _snapshot_source(source, destination):
    source = Path(source).resolve(strict=True)
    stem = source.name.removesuffix("_learned_state.json")
    files = [source, source.with_name(stem+"_learned_summary.json")]
    for p in sorted(source.parent.glob(stem+"_state_trial_*.json")):
        files.extend((p, p.with_suffix(".csv")))
    destination.mkdir()
    for p in files:
        require(not p.is_symlink() and p.is_file(), "pipeline_source_missing_or_symlink")
        (destination/p.name).write_bytes(p.read_bytes())
    return destination/source.name


@_evidence_boundary
def run_job(mode, job_path, source_path, runtime_path, output, maximum_wall_seconds):
    job = load(Path(job_path).resolve(strict=True))
    source_case = load_case(Path(source_path).resolve(strict=True)) if source_path is not None else None
    preflight = validate_job(mode, job, source_case)
    runtime = load(Path(runtime_path).resolve(strict=True));executable = verify_runtime(runtime)
    require(number(maximum_wall_seconds) > 0, "invalid_pipeline_wall_budget")
    output = Path(output).resolve();output.mkdir(parents=True, exist_ok=False)
    inputs = output/"input";inputs.mkdir();source_relative = None
    if source_path is not None:
        snapshot = _snapshot_source(source_path, inputs/"source")
        source_case = load_case(snapshot);source_relative = snapshot.relative_to(output).as_posix()
        require(validate_job(mode, job, source_case) == preflight, "pipeline_source_changed_during_snapshot")
    _write(inputs/"job.json", job)
    process = execute(runtime, ["--app-ini", str(Path(runtime["app_ini"]["path"]).resolve(strict=True)),
        "--timelearner-"+mode, str(inputs/"job.json"), "--timelearner-output", str(output/"native")],
        executable.parent, output/"process", maximum_wall_seconds)
    verify_runtime(runtime)
    audit = None
    if process["execution"] == "completed":
        require(process["runtime_provenance"] == "loaded_files_captured", "pipeline_loaded_runtime_missing")
        audit = audit_execution(mode, output/"native", job, source_case)
    result = {"kind": "timelearner_native_pipeline_run_manifest", "schema_version": 1, "operation": mode,
        "execution": process["execution"], "validity": "valid" if audit else "unverified_execution",
        "job_sha256": job["sha256"], "source_package_path": source_relative,
        "runtime_fingerprint": runtime["runtime_fingerprint"], "source_closure": runtime["source_closure"],
        "preflight": preflight, "analysis": audit,
        "analysis_code": [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(Path(__file__).parent.glob("*.py"))],
        "artifacts": [_record(p, output) for p in sorted(output.rglob("*")) if p.is_file()],
        "independent_partition_verified": False, "evaluation_verdict": None}
    _write(output/"run-manifest.json", _signed(result))
    return result


@_evidence_boundary
def audit_run_manifest(path):
    """Recompute portable source, native result and process/runtime bindings."""
    path = Path(path).resolve(strict=True);root = path.parent
    manifest = load(path);_digest(manifest)
    require(set(manifest) == {"kind", "schema_version", "operation", "execution", "validity", "job_sha256",
            "source_package_path", "runtime_fingerprint", "source_closure", "preflight", "analysis", "analysis_code",
            "artifacts", "independent_partition_verified", "evaluation_verdict", "sha256"} and
            manifest["kind"] == "timelearner_native_pipeline_run_manifest" and
            type(manifest["schema_version"]) is int and manifest["schema_version"] == 1 and
            manifest["operation"] in FIELDS and manifest["independent_partition_verified"] is False and
            manifest["evaluation_verdict"] is None, "unknown_native_pipeline_run_manifest")
    records = manifest["artifacts"]
    require(type(records) is list and all(type(r) is dict and set(r) == {"path", "bytes", "sha256"} and
            type(r["path"]) is str for r in records), "pipeline_run_artifact_schema")
    names = {r["path"] for r in records}
    require(len(names) == len(records) and names == {p.relative_to(root).as_posix() for p in root.rglob("*")
            if p.is_file() and p != path}, "pipeline_run_artifact_closure_changed")
    for r in records:
        relative = PurePosixPath(r["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and "\\" not in r["path"], "pipeline_artifact_escape")
        actual = root/r["path"]
        require(actual.resolve(strict=True).is_relative_to(root) and _record(actual, root) == r, "pipeline_run_artifact_changed")
    mode = manifest["operation"];source = manifest["source_package_path"];source_case = None
    if mode == "train":
        require(source is None, "pipeline_cold_training_has_source")
    else:
        require(type(source) is str and source in names and PurePosixPath(source).parent == PurePosixPath("input/source"),
                "pipeline_source_path_changed")
        source_case = load_case(root/source)
    job = load(root/"input/job.json")
    require(manifest["job_sha256"] == job["sha256"] and validate_job(mode, job, source_case) == manifest["preflight"],
            "pipeline_run_preflight_changed")
    process, runtime = load(root/"process/result.json"), load(root/"process/runtime.json")
    from .runtime import digest_json, runtime_content_identity
    require(manifest["execution"] == process["execution"] and manifest["runtime_fingerprint"] ==
            process["runtime_fingerprint"] == runtime["runtime_fingerprint"] == digest_json(runtime_content_identity(runtime)) and
            manifest["source_closure"] == runtime["source_closure"], "pipeline_run_runtime_changed")
    request = load(root/"process/request.json");arguments = request["arguments"]
    require(type(arguments) is list and len(arguments) == 6 and all(type(a) is str for a in arguments) and
            arguments[::2] == ["--app-ini", "--timelearner-"+mode, "--timelearner-output"] and
            arguments[1] == runtime["app_ini"]["path"], "pipeline_process_arguments_changed")
    output = PurePosixPath(arguments[5])
    require(output.is_absolute() and output.name == "native" and
            PurePosixPath(arguments[3]) == output.parent/"input/job.json" and
            request["working_directory"] == str(PurePosixPath(runtime["executable"]["path"]).parent) and
            number(request["maximum_wall_seconds"]) > 0 and request["model_time"] is None, "pipeline_process_scope_changed")
    if process["execution"] == "completed":
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
                process["returncode"] == 0 and process["ownership_scope"] == "launched_executable_only" and
                process["runtime_provenance"] == "loaded_files_captured", "pipeline_owned_runtime_changed")
    audit = audit_execution(mode, root/"native", job, source_case) if process["execution"] == "completed" else None
    require(manifest["analysis"] == audit and manifest["validity"] == ("valid" if audit else "unverified_execution"),
            "pipeline_run_analysis_changed")
    return {"run_evidence_consistent": True, "operation": mode, "native_execution_verified": False,
            "independent_partition_verified": False, "evaluation_verdict": None}
