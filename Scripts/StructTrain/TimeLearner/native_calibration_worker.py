"""Production Console calibration, owned execution and full-grid model binding.

This runs a saved recognition model. It does not perform Train, prove independent
data partitioning or replace the full experiment scheduler/ConditionSpec pipeline.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
from functools import wraps

from .calibrated_evidence import REQUEST_FIELDS
from .calibration import RULE, _validate_spec, calibration_dataset_digest, validate_trial_design
from .calibration_transaction_evidence import audit_native_calibration_transaction
from .learned_evidence import load_case
from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, count, equal, load, load_json, number, require
from .process_runner import execute, verify_runtime
from .recognition_evidence import audit_recognition_source

JOB_FIELDS = {"kind", "schema_version", "owner_class", "implementation_id", "frequency_hz",
              "maximum_model_ticks", "source_recognition", "thresholds", "maximum_candidates",
              "specification", "trials", "sha256"}
SPEC_FIELDS = {"protocol", "data_partition_id", "attempt_id", "clock_id", "criterion"}
POST_TUNE_FIELDS = {"mode", "metric", "canonical_floor", "canonical_last", "resistance_bounds", "search_passes",
                    "maximum_candidates", "maximum_recorded_samples", "minimum_positive_gap"}
EXECUTION_FIELDS = {"kind", "schema_version", "execution", "job_sha256", "attempt_id",
                    "source_recognition_sha256", "model_sha256", "model_revision", "transaction_sha256",
                    "calibration_status", "frequency_hz", "model_ticks", "model_time_begin", "model_time_end",
                    "artifacts", "runtime_provenance_external", "evaluation_verdict", "sha256"}


def _evidence_boundary(function):
    @wraps(function)
    def checked(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except EvidenceError:
            raise
        except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
            raise EvidenceError("malformed_native_calibration_worker:"+str(error)) from error
    return checked


def _signed(value):
    return {**value, "sha256": sha(value)}


def _digest(value):
    require(value.get("sha256") == sha({k: v for k, v in value.items() if k != "sha256"}), "worker_digest_mismatch")


def _write(path, value):
    with path.open("xb") as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode("utf-8"))


def _record(path, root):
    require(not path.is_symlink() and path.is_file(), "worker_artifact_missing_or_symlink")
    raw = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


@_evidence_boundary
def validate_job(job, source_case, *, post_tune=False):
    fields = JOB_FIELDS | ({"post_tune"} if post_tune else set())
    kind = "timelearner_native_post_tune_job" if post_tune else "timelearner_native_calibration_job"
    require(type(job) is dict and set(job) == fields and job["kind"] == kind
            and type(job["schema_version"]) is int and job["schema_version"] in ((1, 2) if post_tune else (1,)), "unknown_native_calibration_job")
    _digest(job)
    controls_v2 = post_tune and job["schema_version"] == 2
    if controls_v2:
        require(type(job["post_tune"]) is dict and
                set(job["post_tune"]) == POST_TUNE_FIELDS | {"schema_version", "finalization"} and
                type(job["post_tune"]["schema_version"]) is int and job["post_tune"]["schema_version"] == 2 and
                job["post_tune"]["finalization"] in {"calibrate", "keep_fixed_threshold"},
                "unknown_worker_post_tune_v2_specification")
    fixed = controls_v2 and job["post_tune"]["finalization"] == "keep_fixed_threshold"
    source = job["source_recognition"]
    audit_recognition_source(source, source_case)
    model = source["source_solo"]["configuration"]["model"]
    require(job["owner_class"] == "NNeuronTimeLearner"+("Branch" if model["branch"] else "")
            and job["implementation_id"] == source["implementation_id"], "worker_source_owner_mismatch")
    require(1 <= count(job["frequency_hz"]) <= 1000000000 and job["frequency_hz"] == model["frequency_hz"]
            and 1 <= count(job["maximum_model_ticks"]) <= 1000000000, "worker_clock_or_tick_budget_mismatch")
    declaration = job["specification"]
    require(type(declaration) is dict and set(declaration) == SPEC_FIELDS and
            all(type(declaration[k]) is str and declaration[k].strip() for k in SPEC_FIELDS-{"criterion"}),
            "unknown_worker_calibration_specification")
    criterion = declaration["criterion"]
    require(type(criterion) is dict and set(criterion) == {"anchor", "begin_offset", "end_offset", "reject_target_outside_window"}
            and criterion["anchor"] in ("onset", "last_stimulus") and
            type(criterion["reject_target_outside_window"]) is bool and number(criterion["begin_offset"]) >= 0 and
            (criterion["end_offset"] is None or number(criterion["end_offset"]) >= number(criterion["begin_offset"])),
            "invalid_worker_response_window")
    trials = job["trials"]
    require(type(trials) is list and 2 <= len(trials) <= 10000 and
            all(type(q) is dict and set(q) == REQUEST_FIELDS for q in trials), "unknown_worker_trial_design")
    design = [{**{k: q[k] for k in ("trial_id", "sample_id", "label", "pattern_isi", "reset_policy", "duration")},
               "presentation_index": i} for i, q in enumerate(trials)]
    full_criterion = {"id": "post_anchor_target_whole_window_foil_v1", **criterion}
    spec = {"kind": "timelearner_threshold_calibration_spec", "schema_version": 1,
            "calibration_id": declaration["attempt_id"], "protocol": declaration["protocol"],
            "data_partition_id": declaration["data_partition_id"], "source_recognition_sha256": source["sha256"],
            "source_model_revision": source["model_revision"], "coverage_policy": "per_trial_windows",
            "criterion": full_criterion, "trials": design, "thresholds": job["thresholds"],
            "maximum_candidates": job["maximum_candidates"], "selection_rule": RULE}
    spec["dataset_digest"] = calibration_dataset_digest("per_trial_windows", full_criterion, design)
    if fixed:
        require(job["thresholds"] == [] and count(job["maximum_candidates"]) == 0,
                "fixed_post_tune_has_unused_calibration_grid")
        number(source["neuron"]["metadata"]["calibration"]["threshold"])
        require(declaration["protocol"] in {"historical_same_matrix", "frozen_independent_calibration"},
                "unknown_worker_probe_protocol")
        validate_trial_design(design)
        # This is probe-design identity, not a fabricated threshold-calibration spec.
        spec = {"kind": "timelearner_fixed_weight_probe_design", "schema_version": 1,
                "source_recognition_sha256": source["sha256"], "source_model_revision": source["model_revision"],
                "coverage_policy": "per_trial_windows", "criterion": full_criterion, "trials": design,
                "protocol": declaration["protocol"], "data_partition_id": declaration["data_partition_id"]}
        identity = {"conditions_digest": sha(spec)}
    else:
        _, identity = _validate_spec(spec)
    require(len(job["thresholds"]) <= 256 and count(job["maximum_candidates"]) <= 256, "worker_grid_budget_limit")
    target = source["source_solo"]["protocol"]["pattern_hash"]
    samples = {}
    for q in trials:
        require(type(q["run_id"]) is str and bool(q["run_id"].strip()) and
                type(q["record_threshold_potential"]) is bool and 2 <= count(q["maximum_samples"]) <= 10000000 and
                len(q["pattern_isi"]) == len(source["recognition_inputs"]) and
                q["pattern_hash"] == sha(q["pattern_isi"]) and ((q["label"] == "target") == (q["pattern_hash"] == target)),
                "worker_trial_identity_or_shape_mismatch")
        ticks = number(q["duration"])*job["frequency_hz"]
        require(equal(ticks, round(ticks)) and ticks+1 <= q["maximum_samples"], "worker_trial_window_or_sample_budget")
        signature = (q["label"], q["pattern_hash"])
        require(samples.setdefault(q["sample_id"], signature) == signature, "worker_sample_collision")
    result = {"job_sha256": job["sha256"], "primary_source_checked": True, "effective_model_checked": False,
              "specification_sha256": sha(spec), "conditions_digest": identity["conditions_digest"]}
    if post_tune:
        p = job["post_tune"]
        require(source["kind"] == "timelearner_recognition_state" and source["conversion_spec"]["schema_version"] == 1,
                "post_tune_worker_requires_unmodified_base_recognition")
        require(type(p) is dict and set(p) == POST_TUNE_FIELDS | ({"schema_version", "finalization"} if controls_v2 else set()) and
                p["mode"] in {"off", "keep_done", "canon_rmin", "flat_last_r", "search_synthetic"} and
                p["metric"] in {"auto", "ltzone", "soma_sum"}, "unknown_worker_post_tune_specification")
        edit = p["mode"] in {"canon_rmin", "flat_last_r", "search_synthetic"}
        floor = p["mode"] in {"canon_rmin", "search_synthetic"}
        require((number(p["canonical_floor"]) > 0 if floor else number(p["canonical_floor"]) == 0) and
                (number(p["canonical_last"]) > 0 if edit else number(p["canonical_last"]) == 0),
                "unused_or_invalid_worker_post_tune_physics")
        bounds = p["resistance_bounds"]
        require(type(bounds) is list and len(bounds) == (len(source["recognition_inputs"]) if edit else 0) and
                all(type(b) is dict and set(b) == {"minimum", "maximum"} and
                    0 < number(b["minimum"]) <= number(b["maximum"]) for b in bounds), "invalid_worker_post_tune_bounds")
        require(1 <= count(p["search_passes"]) <= 128 and 1 <= count(p["maximum_candidates"]) <= 4096 and
                1 <= count(p["maximum_recorded_samples"]) <= 100000000 and number(p["minimum_positive_gap"]) >= 0,
                "invalid_worker_post_tune_budget")
        if p["metric"] == "ltzone" or (p["metric"] == "auto" and not model["branch"]):
            require(all(q["record_threshold_potential"] for q in trials), "post_tune_metric_samples_required")
        result["conditions_digest"] = sha({"grid_conditions_digest": identity["conditions_digest"], "post_tune": p,
                                           "maximum_model_ticks": job["maximum_model_ticks"]})
        result["post_tune_specification_sha256"] = sha(p)
    return result


@_evidence_boundary
def audit_execution(directory, job, source_case, *, post_tune=False):
    directory = Path(directory)
    execution = load(directory/"execution.json")
    fields = (EXECUTION_FIELDS-{"calibration_status"})|{"post_tune_status"} if post_tune else EXECUTION_FIELDS
    kind = "timelearner_native_post_tune_execution" if post_tune else "timelearner_native_calibration_execution"
    require(set(execution) == fields and execution["kind"] == kind
            and type(execution["schema_version"]) is int and execution["schema_version"] == 1,
            "unknown_native_calibration_execution")
    _digest(execution)
    require(type(execution["artifacts"]) is list and len(execution["artifacts"]) == 3,
            "worker_artifact_closure_incomplete")
    records = {r["path"]: r for r in execution["artifacts"]}
    require(set(records) == {"job.json", "model.json", "transaction.json"} and
            all(records[name] == _record(directory/name, directory) for name in records), "worker_artifact_content_changed")
    require(load(directory/"job.json") == job and execution["job_sha256"] == job["sha256"] and
            execution["attempt_id"] == job["specification"]["attempt_id"] and
            execution["source_recognition_sha256"] == job["source_recognition"]["sha256"] and
            execution["frequency_hz"] == job["frequency_hz"] and execution["runtime_provenance_external"] is True and
            execution["evaluation_verdict"] is None, "worker_execution_scope_changed")
    ticks = count(execution["model_ticks"])
    require(ticks <= job["maximum_model_ticks"] and equal(number(execution["model_time_end"])-number(execution["model_time_begin"]),
            ticks/job["frequency_hz"]), "worker_model_clock_changed")
    report, model = load(directory/"transaction.json"), load(directory/"model.json")
    if post_tune:
        from .posttune_transaction_evidence import audit_posttune_transaction
        audit = audit_posttune_transaction(report, source_case)
    else:
        audit = audit_native_calibration_transaction(report, source_case)
    maximum_field = "maximum_calibration_candidates" if post_tune else "maximum_candidates"
    declaration = report["confirmation_specification"] if post_tune else {key: report[key] for key in SPEC_FIELDS}
    require(report["source_recognition"] == job["source_recognition"] and report["thresholds"] == job["thresholds"] and
            report[maximum_field] == job["maximum_candidates"] and report["trials"] == job["trials"] and
            declaration == job["specification"], "worker_declared_design_changed")
    if post_tune:
        require({key: report[key] for key in POST_TUNE_FIELDS} ==
                {key: job["post_tune"][key] for key in POST_TUNE_FIELDS}, "worker_post_tune_conditions_changed")
        fixed = job["schema_version"] == 2 and job["post_tune"]["finalization"] == "keep_fixed_threshold"
        require(report["schema_version"] == (2 if fixed else 1) and
                (not fixed or report["finalization"] == job["post_tune"]["finalization"]),
                "worker_post_tune_finalization_changed")
    require(execution["post_tune_status" if post_tune else "calibration_status"] == report["status"] and execution["transaction_sha256"] == report["sha256"] and
            execution["model_sha256"] == model["sha256"] and execution["model_revision"] == model["model_revision"],
            "worker_model_result_binding_changed")
    if report["status"] == "calibrated":
        require(model == report["calibrated_package"], "worker_committed_model_changed")
    elif post_tune and report["status"] == "weights_selected":
        require(model == report["selected_package"], "worker_selected_model_changed")
    elif report["source_restored"]:
        require(model == job["source_recognition"], "worker_restored_model_changed")
    require(execution["execution"] in {"completed", "cancelled", "model_tick_budget_exhausted"}, "unknown_worker_execution_status")
    require(execution["execution"] == "completed" or (report["status"] in {"cancelled", "recovery_required"} and
            (execution["execution"] != "model_tick_budget_exhausted" or ticks == job["maximum_model_ticks"])),
            "worker_interrupted_positive_claim")
    return {"execution_evidence_consistent": True, "full_grid_model_binding_verified": report["status"] == "calibrated",
            "transaction_audit": audit, "native_execution_verified": False, "evaluation_verdict": None}


@_evidence_boundary
def run_job(job_path, source_path, runtime_path, output, maximum_wall_seconds, *, post_tune=False):
    job_path, source_path = Path(job_path).resolve(strict=True), Path(source_path).resolve(strict=True)
    job = load(job_path)
    preflight = validate_job(job, load_case(source_path), post_tune=post_tune)
    runtime = load(Path(runtime_path).resolve(strict=True)); executable = verify_runtime(runtime)
    require(number(maximum_wall_seconds) > 0, "invalid_worker_wall_budget")
    output = Path(output).resolve();output.mkdir(parents=True, exist_ok=False)
    inputs = output/"input";inputs.mkdir();primaries = inputs/"source";primaries.mkdir()
    stem = source_path.name.removesuffix("_learned_state.json")
    paths = [source_path, source_path.with_name(stem+"_learned_summary.json")]
    for path in sorted(source_path.parent.glob(stem+"_state_trial_*.json")):
        paths.extend((path, path.with_suffix(".csv")))
    for path in paths:
        require(not path.is_symlink() and path.is_file(), "worker_primary_missing_or_symlink")
        (primaries/path.name).write_bytes(path.read_bytes())
    source_case = load_case(primaries/source_path.name)
    require(validate_job(job, source_case, post_tune=post_tune) == preflight, "worker_source_changed_during_snapshot")
    _write(inputs/"job.json", job)
    process = execute(runtime, ["--app-ini", str(Path(runtime["app_ini"]["path"]).resolve(strict=True)),
        "--timelearner-posttune" if post_tune else "--timelearner-calibrate", str(inputs/"job.json"), "--timelearner-output", str(output/"native")],
        executable.parent, output/"process", maximum_wall_seconds)
    verify_runtime(runtime)
    require(process["execution"] != "completed" or process["runtime_provenance"] == "loaded_files_captured",
            "worker_loaded_runtime_provenance_missing")
    audit = audit_execution(output/"native", job, source_case, post_tune=post_tune) if process["execution"] == "completed" else None
    analysis_code = [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                     for p in sorted(Path(__file__).parent.glob("*.py"))]
    result = {"kind": "timelearner_post_tune_run_manifest" if post_tune else "timelearner_calibration_run_manifest", "schema_version": 1,
              "execution": process["execution"], "validity": "valid" if audit else "unverified_execution",
              "attempt_id": job["specification"]["attempt_id"], "job_sha256": job["sha256"],
              "source_package_path": (primaries/source_path.name).relative_to(output).as_posix(),
              "runtime_fingerprint": runtime["runtime_fingerprint"], "source_closure": runtime["source_closure"],
              "preflight": preflight, "analysis": audit, "analysis_code": analysis_code,
              "artifacts": [_record(p, output) for p in sorted(output.rglob("*")) if p.is_file()],
              "independent_partition_verified": False, "evaluation_verdict": None}
    _write(output/"run-manifest.json", _signed(result))
    return result


@_evidence_boundary
def audit_run_manifest(path, *, post_tune=False):
    """Portable artifact audit; does not attest an arbitrary process record."""
    path = Path(path).resolve(strict=True);root = path.parent
    manifest = load(path);_digest(manifest)
    require(set(manifest) == {"kind", "schema_version", "execution", "validity", "attempt_id", "job_sha256",
            "source_package_path", "runtime_fingerprint", "source_closure", "preflight", "analysis", "analysis_code",
            "artifacts", "independent_partition_verified", "evaluation_verdict", "sha256"} and
            manifest["kind"] == ("timelearner_post_tune_run_manifest" if post_tune else "timelearner_calibration_run_manifest") and type(manifest["schema_version"]) is int and
            manifest["schema_version"] == 1 and manifest["independent_partition_verified"] is False and
            manifest["evaluation_verdict"] is None, "unknown_calibration_run_manifest")
    records = manifest["artifacts"]
    require(type(records) is list and all(type(r) is dict and set(r) == {"path", "bytes", "sha256"} and
            type(r["path"]) is str and type(r["bytes"]) is int and r["bytes"] >= 0 and
            type(r["sha256"]) is str and len(r["sha256"]) == 64 for r in records), "unknown_worker_artifact_record")
    names = {r["path"] for r in records}
    require(len(names) == len(records) and names == {p.relative_to(root).as_posix() for p in root.rglob("*")
            if p.is_file() and p != path}, "worker_run_artifact_closure_changed")
    for record in records:
        relative = PurePosixPath(record["path"])
        require(not relative.is_absolute() and ".." not in relative.parts and "\\" not in record["path"],
                "worker_artifact_path_escape")
        actual = root/record["path"]
        require(actual.resolve(strict=True).is_relative_to(root) and _record(actual, root) == record,
                "worker_run_artifact_content_changed")
    require(type(manifest["source_package_path"]) is str and manifest["source_package_path"] in names and
            PurePosixPath(manifest["source_package_path"]).parent == PurePosixPath("input/source"),
            "worker_source_package_path_changed")
    job = load(root/"input/job.json");source_case = load_case(root/manifest["source_package_path"])
    require(validate_job(job, source_case, post_tune=post_tune) == manifest["preflight"] and manifest["job_sha256"] == job["sha256"] and
            manifest["attempt_id"] == job["specification"]["attempt_id"], "worker_run_job_scope_changed")
    process, runtime = load(root/"process/result.json"), load(root/"process/runtime.json")
    from .runtime import digest_json, runtime_content_identity
    require(manifest["execution"] == process["execution"] and manifest["runtime_fingerprint"] ==
            process["runtime_fingerprint"] == runtime["runtime_fingerprint"] == digest_json(runtime_content_identity(runtime))
            and manifest["source_closure"] == runtime["source_closure"], "worker_run_runtime_scope_changed")
    request = load(root/"process/request.json")
    arguments = request["arguments"]
    require(type(arguments) is list and len(arguments) == 6 and all(type(v) is str for v in arguments) and
            arguments[::2] == ["--app-ini", "--timelearner-posttune" if post_tune else "--timelearner-calibrate", "--timelearner-output"] and
            arguments[1] == runtime["app_ini"]["path"], "worker_run_process_arguments_changed")
    original_output = PurePosixPath(arguments[5])
    require(original_output.is_absolute() and original_output.name == "native" and
            PurePosixPath(arguments[3]) == original_output.parent/"input/job.json" and
            request["working_directory"] == str(PurePosixPath(runtime["executable"]["path"]).parent) and
            number(request["maximum_wall_seconds"]) > 0 and request["model_time"] is None,
            "worker_run_process_scope_changed")
    if process["execution"] == "completed":
        owned = load(root/"process/owned-process.json")
        loaded = load_json(root/"process/loaded-files.json")
        expected_executable = {key: runtime["executable"][key] for key in ("path", "size", "sha256")}
        require(owned["executable"] == runtime["executable"]["path"] and
                owned["executable_sha256"] == runtime["executable"]["sha256"] and
                owned["runtime_fingerprint"] == runtime["runtime_fingerprint"] and count(owned["pid"]) > 0 and
                type(loaded) is list and expected_executable in loaded and process["returncode"] == 0 and
                process["ownership_scope"] == "launched_executable_only", "worker_run_owned_runtime_changed")
    audit = audit_execution(root/"native", job, source_case, post_tune=post_tune) if process["execution"] == "completed" else None
    require(manifest["analysis"] == audit and manifest["validity"] == ("valid" if audit else "unverified_execution") and
            (not audit or process["runtime_provenance"] == "loaded_files_captured"), "worker_run_analysis_changed")
    return {"run_evidence_consistent": True, "full_grid_model_binding_verified": bool(audit and
            audit["full_grid_model_binding_verified"]), "native_execution_verified": False,
            "independent_partition_verified": False, "evaluation_verdict": None}
