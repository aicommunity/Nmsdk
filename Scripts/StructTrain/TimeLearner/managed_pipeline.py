"""Managed phase orchestration with an auditable boundary journal.

A pipeline declaration is an operational identity, not a scientific ConditionSpec.
Only existing native workers execute physical components. An interrupted phase
requires explicit reconciliation; continuing a finished boundary never reruns it.
"""
from contextlib import contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path

from .native_evidence import load, parse_json_bytes, require
from .model_identity import canonical_model_sha256 as digest
from .native_process_policy import validate_policy
from .process_runner import verify_runtime


def signed(value):
    result = {k: v for k, v in value.items() if k != "sha256"}
    return {**result, "sha256": digest(result)}


def _sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write(path, value):
    with path.open("xb") as stream:
        stream.write((json.dumps(value, ensure_ascii=False, allow_nan=False)+"\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    _sync_directory(path.parent)


def _validate(spec, *, preflight=False):
    require(type(spec) is dict and set(spec) == {"kind", "schema_version", "attempt_id", "phases"}
            and spec["kind"] == "timelearner_managed_pipeline_job"
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1
            and type(spec["attempt_id"]) is str and bool(spec["attempt_id"].strip()),
            "unknown_managed_pipeline_job")
    phases = spec["phases"]
    require(type(phases) is list and all(type(p) is dict and set(p) == {"operation", "job", "wall_seconds"}
            for p in phases), "invalid_managed_pipeline_phases")
    order = [p["operation"] for p in phases]
    live = bool(phases) and phases[0]['operation'] == 'train' and \
        type(phases[0]['job']) is dict and phases[0]['job'].get('schema_version') == 2
    require(order == ['train', 'evaluate'] if live else order in (
                      ["train", "export", "evaluate"], ["train", "export", "calibrate", "evaluate"],
                      ["train", "export", "posttune", "evaluate"],
                      ["train", "export", "posttune", "calibrate", "evaluate"]),
            "managed_pipeline_phase_order")
    from .native_pipeline_worker import validate_job, FIELDS, KINDS
    from .native_calibration_worker import JOB_FIELDS
    validate_job("train", phases[0]["job"])
    implementation = phases[0]["job"]["implementation_id"]
    for phase in phases:
        wall = phase["wall_seconds"]
        require(type(wall) in (int, float) and 1 <= wall <= 86400, "invalid_pipeline_phase_budget")
        operation, job = phase["operation"], phase["job"]
        require(type(job) is dict and job.get("implementation_id") == implementation,
                "managed_pipeline_implementation_changed")
        if operation == "train":
            continue
        source = "source_solo" if operation == "export" else "source_recognition"
        require(job.get(source, "missing") is None, "managed_pipeline_source_must_be_unbound")
        expected = FIELDS[operation] | {"kind", "schema_version"} if operation in FIELDS else (
            JOB_FIELDS - {"sha256"}) | ({"post_tune"} if operation == "posttune" else set())
        require(set(job) == expected, "managed_pipeline_phase_fields")
        expected_kind = ("timelearner_native_"+KINDS[operation]+"_job" if operation in FIELDS else
                         "timelearner_native_post_tune_job" if operation == "posttune" else
                         "timelearner_native_calibration_job")
        require(job["kind"] == expected_kind and type(job["schema_version"]) is int and
                job["schema_version"] in ((1, 2, 3) if operation == "posttune" else (1,)),
                "managed_pipeline_phase_kind")
        if operation != "export":
            require(job["owner_class"] == phases[0]["job"]["owner_class"],
                    "managed_pipeline_owner_changed")
        # Reject malformed downstream factors before expensive cold Train.
        # Source-dependent validation still uses only the actual predecessor.
        if preflight:
            from .managed_declaration import validate_downstream_declaration
            validate_downstream_declaration(operation, job, phases[0]['job']['configuration']['model'])
    return deepcopy(spec)


@contextmanager
def _lock(root):
    import fcntl  # The production workers are Linux; no lock emulation.
    with (root/"coordinator.lock").open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def _events(root):
    path = root/"journal.jsonl"
    if not path.exists():
        return []
    data = path.read_bytes()
    require(not data or data.endswith(b"\n"), "pipeline_journal_torn_record")
    events = []
    for line in data.splitlines():
        event = parse_json_bytes(line)
        require(set(event) == {"sequence", "previous", "event", "phase", "payload", "sha256"}
                and type(event["sequence"]) is int and event["sequence"] == len(events)
                and event["previous"] == (events[-1]["sha256"] if events else None)
                and signed(event) == event, "pipeline_journal_integrity")
        events.append(event)
    return events


def _append(root, events, event, phase, payload):
    record = signed({"sequence": len(events), "previous": events[-1]["sha256"] if events else None,
                     "event": event, "phase": phase, "payload": payload})
    with (root/"journal.jsonl").open("ab") as stream:
        stream.write((json.dumps(record, ensure_ascii=False, allow_nan=False)+"\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    _sync_directory(root)
    events.append(record)


def _resolved_job(phase, root, completed, *, live_finalization=False):
    job = deepcopy(phase["job"])
    operation = phase["operation"]
    if operation != "train":
        predecessor = completed[-1]
        name = "train_learned_state.json" if operation == "export" else "model.json"
        if predecessor == 'train' and operation == 'evaluate' and live_finalization:
            # Native live finalization has already converted/tuned/calibrated
            # recognition state. Exporting solo again would discard its work.
            name = 'recognition-model.json'
        source_key = "source_solo" if operation == "export" else "source_recognition"
        job[source_key] = load(root/"phases"/predecessor/"native"/name)
    return signed(job)


def _audit_phase(root, operation, expected_job, runtime_fingerprint):
    directory = root/"phases"/operation
    manifest = load(directory/"run-manifest.json")
    from .native_pipeline_worker import audit_run_manifest as pipeline_audit
    from .native_calibration_worker import audit_run_manifest as calibration_audit
    audit = (calibration_audit(directory/"run-manifest.json", post_tune=operation == "posttune")
             if operation in ("calibrate", "posttune") else pipeline_audit(directory/"run-manifest.json"))
    require(audit["run_evidence_consistent"] and load(directory/"input/job.json") == expected_job
            and manifest["job_sha256"] == expected_job["sha256"]
            and manifest["runtime_fingerprint"] == runtime_fingerprint
            and manifest.get("process_policy", {}).get("schema_version") == 2,
            "managed_pipeline_phase_binding")
    return manifest


def _phase_ready(operation, manifest):
    ready = manifest["execution"] == "completed" and manifest["validity"] == "valid"
    if operation != 'train':
        return ready
    analysis = manifest['analysis']
    return ready and analysis['completed_boundary'] and analysis.get('recognition_available', True)


def _scan(root, spec, events, runtime_fingerprint):
    require(bool(events) and events[0]["event"] == "created" and events[0]["phase"] is None
            and events[0]["payload"] == {"specification_sha256": digest(spec),
                                       "runtime_fingerprint": runtime_fingerprint},
            "pipeline_journal_declaration_changed")
    completed, pending, halted = [], None, None
    for event in events[1:]:
        index = len(completed)
        require(index < len(spec["phases"]) and halted is None, "pipeline_journal_after_terminal")
        operation = spec["phases"][index]["operation"]
        require(event["phase"] == operation, "pipeline_journal_phase_order")
        if event["event"] == "started":
            require(pending is None and event["payload"] == {
                "job_sha256": _resolved_job(spec["phases"][index], root, completed,
                    live_finalization=spec["phases"][0]["job"]["schema_version"] == 2)["sha256"]},
                "pipeline_journal_started_binding")
            pending = operation
        else:
            require(pending == operation and event["event"] in
                    ("finished", "halted", "reconciled_finished", "reconciled_halted"),
                    "pipeline_journal_transition")
            job = _resolved_job(spec["phases"][index], root, completed,
                    live_finalization=spec["phases"][0]["job"]["schema_version"] == 2)
            manifest = _audit_phase(root, operation, job, runtime_fingerprint)
            reconciled = event["event"].startswith("reconciled_")
            payload = event["payload"]
            require(type(payload) is dict and set(payload) ==
                    ({"manifest_sha256", "closure"} if reconciled else {"manifest_sha256"}) and
                    payload["manifest_sha256"] == manifest["sha256"],
                    "pipeline_journal_manifest_changed")
            if reconciled:
                closure = payload["closure"]
                binding = load(root/"phases"/operation/"process/contained/owned-unit.json")
                require(type(closure) is dict and closure.get("all_processes_closed") is True and
                        closure.get("binding") == binding, "pipeline_reconciled_closure_changed")
            ready = _phase_ready(operation, manifest)
            require(ready == (event["event"] in ("finished", "reconciled_finished")),
                    "pipeline_journal_outcome_changed")
            pending = None
            if ready:
                completed.append(operation)
            else:
                halted = operation
    return completed, pending, halted


def audit_pipeline(root):
    root = Path(root).resolve(strict=True)
    spec = _validate(load(root/"specification.json"))
    runtime = load(root/"runtime.json")
    completed, pending, halted = _scan(root, spec, _events(root), runtime["runtime_fingerprint"])
    evaluation = None
    if len(completed) == len(spec["phases"]):
        from .recognition_metrics import load_evaluation, score_recognition_evaluation
        directory = root/"phases/evaluate/native"
        design, observations = load_evaluation(directory/"evaluation.json")
        evaluation = score_recognition_evaluation(design, observations, load(directory/"model.json"))
    return {"kind": "timelearner_managed_pipeline_audit", "schema_version": 1,
            "completed_phases": completed, "pending_phase": pending, "halted_phase": halted,
            "pipeline_complete": len(completed) == len(spec["phases"]), "evaluation": evaluation,
            "scientific_verdict": None, "condition_identity_attested": False}


def reconcile_pipeline(root):
    """Acknowledge one closed, fully audited native phase; never execute it.

    This does not release leases, repair torn journal records, or recover an
    unfinished physical probe. A stopped Train remains a halted pipeline.
    """
    root = Path(root).resolve(strict=True)
    with _lock(root):
        spec = _validate(load(root/"specification.json"))
        runtime = load(root/"runtime.json")
        events = _events(root)
        completed, pending, halted = _scan(root, spec, events, runtime["runtime_fingerprint"])
        require(pending is not None and halted is None, "pipeline_no_phase_to_reconcile")
        phase = spec["phases"][len(completed)]
        job = _resolved_job(phase, root, completed,
                live_finalization=spec["phases"][0]["job"]["schema_version"] == 2)
        require(load(root/(pending+"-resolved-job.json")) == job,
                "pipeline_prepared_job_changed")
        manifest = _audit_phase(root, pending, job, runtime["runtime_fingerprint"])
        directory = root/"phases"/pending/"process"
        context = load(directory/"reservation-context.json")
        origin = Path(context["intent"]["intent"]["directory"])
        require(tuple(origin.parts[-4:]) == ("phases", pending, "process", "contained"),
                "pipeline_reconciliation_origin_changed")
        owner = load(directory/"contained/request.json")["controller"]
        if origin.parents[3].resolve() != root and owner["pid"] != os.getpid():
            # A restored directory must not fork an attempt whose original
            # coordinator is still running elsewhere. At the original root,
            # the exclusive workflow lock already serializes its writers.
            try:
                fields = (Path("/proc")/str(owner["pid"])/"stat").read_text().rsplit(") ", 1)[1].split()
            except (FileNotFoundError, ProcessLookupError):
                fields = None
            require(fields is None or fields[19] != owner["start_ticks"] or fields[0] in ("Z", "X"),
                    "pipeline_reconciliation_original_controller_still_live")
        from .contained_process import inspect as inspect_contained
        closure = inspect_contained(directory/"contained")
        require(closure["all_processes_closed"], "pipeline_reconciliation_phase_still_live")
        _append(root, events, "reconciled_finished" if _phase_ready(pending, manifest)
                else "reconciled_halted", pending,
                {"manifest_sha256": manifest["sha256"], "closure": closure})
        return audit_pipeline(root)


def run_pipeline(specification, runtime_path, policy, output, *, resume=False, stop_after=None):
    spec = _validate(load(Path(specification)), preflight=True)
    require(stop_after is None or stop_after in [p["operation"] for p in spec["phases"]],
            "pipeline_unknown_stop_boundary")
    runtime = load(Path(runtime_path))
    verify_runtime(runtime)
    policy = validate_policy(policy)
    require(policy is not None and policy["schema_version"] == 2, "pipeline_requires_managed_reservation")
    root = Path(output).resolve()
    if not resume:
        root.mkdir(parents=True, exist_ok=False)
    else:
        require(root.is_dir(), "pipeline_resume_root_missing")
    with _lock(root):
        if not resume:
            _write(root/"specification.json", spec)
            _write(root/"runtime.json", runtime)
            (root/"phases").mkdir()
            events = []
            _append(root, events, "created", None, {"specification_sha256": digest(spec),
                                                  "runtime_fingerprint": runtime["runtime_fingerprint"]})
        else:
            require(load(root/"specification.json") == spec and load(root/"runtime.json") == runtime,
                    "pipeline_resume_inputs_changed")
            events = _events(root)
        completed, pending, halted = _scan(root, spec, events, runtime["runtime_fingerprint"])
        require(pending is None, "pipeline_interrupted_phase_requires_reconciliation")
        require(halted is None, "pipeline_halted_requires_new_attempt")
        from .contained_process import inspect as inspect_contained
        # Revalidate actual kernel closure of every boundary being continued.
        for operation in completed:
            require(inspect_contained(root/"phases"/operation/"process/contained")["all_processes_closed"],
                    "pipeline_previous_phase_still_live")
        runtime_path = root/"runtime.json"
        for phase in spec["phases"][len(completed):]:
            checked, pending, halted = _scan(root, spec, events, runtime["runtime_fingerprint"])
            require(checked == completed and pending is None and halted is None,
                    "pipeline_boundary_changed_before_next_phase")
            operation = phase["operation"]
            job = _resolved_job(phase, root, completed,
                live_finalization=spec["phases"][0]["job"]["schema_version"] == 2)
            path = root/(operation+"-resolved-job.json")
            if path.exists():
                require(load(path) == job, "pipeline_prepared_job_changed")
            else:
                _write(path, job)
            _append(root, events, "started", operation, {"job_sha256": job["sha256"]})
            solo = None if operation == "train" else root/"phases/train/native/train_learned_state.json"
            if operation in ("calibrate", "posttune"):
                from .native_calibration_worker import run_job
                run_job(path, solo, runtime_path, root/"phases"/operation, phase["wall_seconds"],
                        post_tune=operation == "posttune", process_policy=policy)
            else:
                from .native_pipeline_worker import run_job
                run_job(operation, path, solo, runtime_path, root/"phases"/operation,
                        phase["wall_seconds"], process_policy=policy)
            require(inspect_contained(root/"phases"/operation/"process/contained")["all_processes_closed"],
                    "pipeline_finished_phase_still_live")
            manifest = _audit_phase(root, operation, job, runtime["runtime_fingerprint"])
            ready = _phase_ready(operation, manifest)
            _append(root, events, "finished" if ready else "halted", operation,
                    {"manifest_sha256": manifest["sha256"]})
            if not ready:
                break
            completed.append(operation)
            if operation == stop_after:
                break
        return audit_pipeline(root)
