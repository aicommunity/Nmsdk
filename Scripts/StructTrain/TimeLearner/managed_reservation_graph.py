"""Lease schema3: registered managed units and conservative aggregate budgets.

This layer covers units created by the framework, including siblings of the
controller's cgroup. Registration precedes submission. Unknown launch/closure
keeps both paths and resource budgets held. Legacy ledgers are never upgraded.
"""
import json
import math
from pathlib import Path
import uuid

from .resource_reservations import _require, _json
from .runtime import digest_json


def validate_controller(value, owner, demands):
    _require(type(value) is dict and set(value) == {"directory", "binding", "memory_bytes", "tasks"} and
             type(value["directory"]) is str and Path(value["directory"]).is_absolute() and
             type(value["memory_bytes"]) is int and 0 < value["memory_bytes"] <= demands["memory_bytes"] and
             type(value["tasks"]) is int and 0 < value["tasks"] <= demands["tasks"] and
             value["binding"]["initial_main_pid"] == owner["pid"] and
             value["binding"]["initial_start_ticks"] == owner["start_ticks"], "managed_controller_budget_or_identity_invalid")


def capture_controller(directory, owner, demands):
    from . import contained_process as backend
    _require(directory is not None, "managed_controller_directory_required")
    directory = Path(directory).resolve(strict=True)
    state = backend.inspect(directory)
    binding = state["binding"]
    _require(not state["all_processes_closed"] and binding["initial_main_pid"] == owner["pid"] and
             binding["initial_start_ticks"] == owner["start_ticks"], "managed_controller_not_lease_owner")
    group = backend._group_path(binding["control_group"])
    memory, tasks = (group/"memory.max").read_text().strip(), (group/"pids.max").read_text().strip()
    _require(memory.isdigit() and tasks.isdigit() and
             (group/"memory.swap.max").read_text().strip() == "0", "managed_controller_kernel_limits_required")
    value = {"directory": str(directory), "binding": binding, "memory_bytes": int(memory), "tasks": int(tasks)}
    validate_controller(value, owner, demands)
    return value


def _directory(lease, value):
    path = Path(value)
    _require(path.is_absolute() and ".." not in path.parts and not path.is_symlink() and
             str(path.resolve(strict=False)) == str(path), "managed_intent_directory_alias")
    _require(any(r["access"] == "write" and
                 (path == Path(r["canonical_path"]) or path.is_relative_to(Path(r["canonical_path"])))
                 for r in lease["resources"]), "managed_intent_outside_owned_output")
    return path


def _rows(connection, lease):
    values = []
    for row in connection.execute('SELECT * FROM managed_unit_intents WHERE token=? ORDER BY attempt_id', (lease["token"],)):
        value = json.loads(row["intent"])
        _require(value["sha256"] == digest_json({k: v for k, v in value.items() if k != "sha256"}) and
                 row["state"] in ("registered", "submitted", "bound", "aborted") and
                 row["attempt_id"] == value["attempt_id"] and row["token"] == value["token"] == lease["token"] and
                 row["directory"] == value["directory"] and value["owner"] == lease["owner"] and
                 str(uuid.UUID(value["attempt_id"])) == value["attempt_id"] and
                 value["unit"] == "timelearner-"+value["attempt_id"]+".service", "managed_intent_record_changed")
        _directory(lease, value["directory"])
        values.append({**value, "state": row["state"]})
    return values


def _request(intent):
    from . import contained_process as backend
    directory, request = backend._request(intent["directory"])
    owner = intent["owner"]
    _require(request["attempt_id"] == intent["attempt_id"] and request["unit"] == intent["unit"] and
             request["controller"] == {"pid": owner["pid"], "start_ticks": owner["start_ticks"]} and
             request["uid"] == owner["uid"] and request["boot_id"] == owner["boot_id"] and
             request["memory_bytes"] == intent["memory_bytes"] and request["tasks"] == intent["tasks"] and
             request["maximum_wall_seconds"] == intent["maximum_wall_seconds"], "managed_intent_request_changed")
    return directory, request


def _unit_status(intent, *, owner_closed):
    from . import contained_process as backend
    directory = Path(intent["directory"])
    state = backend._show(intent["unit"])
    if intent["state"] in ("registered", "aborted"):
        # Framework submission must atomically change registry state first.
        # While the controller is alive, a registered intent may still launch.
        _require(state.get("LoadState") == "not-found" and not (directory/"owned-unit.json").exists(),
                 "managed_unsubmitted_unit_exists")
        return {"attempt_id": intent["attempt_id"], "unit": intent["unit"],
                "all_processes_closed": owner_closed or intent["state"] == "aborted",
                "reason": "unsubmitted_controller_closed" if owner_closed else "unsubmitted_launch_pending"}
    _request(intent)
    # A submitted request with no bound helper is conservatively unresolved.
    # A fresh inspect can adopt a surviving helper after controller death.
    observed = backend.inspect(directory)
    _require(observed["binding"]["unit"] == intent["unit"], "managed_unit_binding_changed")
    return {"attempt_id": intent["attempt_id"], "unit": intent["unit"],
            "all_processes_closed": observed["all_processes_closed"], "observation": observed}


def register_intent(connection, lease, directory, attempt_id, *, memory_bytes, tasks, maximum_wall_seconds):
    _require(type(attempt_id) is str and str(uuid.UUID(attempt_id)) == attempt_id and
             type(memory_bytes) is int and 0 < memory_bytes <= 2**63-1 and
             type(tasks) is int and 0 < tasks <= 2**31-1 and
             type(maximum_wall_seconds) in (int, float) and math.isfinite(maximum_wall_seconds) and
             1 <= maximum_wall_seconds <= 86400, "managed_intent_limits_invalid")
    path = _directory(lease, str(Path(directory).absolute()))
    _require(not path.exists(), "managed_intent_directory_already_exists")
    _require(connection.execute('SELECT 1 FROM managed_unit_intents WHERE attempt_id=? OR directory=?',
                               (attempt_id, str(path))).fetchone() is None, "managed_intent_already_registered")
    # Parent cap includes all ordinary forked descendants. Separate managed
    # units consume additional declared budget, even before submission.
    memory, task_count = lease["controller"]["memory_bytes"], lease["controller"]["tasks"]
    for old in _rows(connection, lease):
        try:
            closed = _unit_status(old, owner_closed=False)["all_processes_closed"]
        except Exception:
            closed = False  # Missing/unverifiable state still consumes budget.
        if not closed:
            memory += old["memory_bytes"]
            task_count += old["tasks"]
    _require(memory+memory_bytes <= lease["demands"]["memory_bytes"] and
             task_count+tasks <= lease["demands"]["tasks"], "managed_aggregate_budget_exhausted")
    value = {"kind": "timelearner_managed_unit_intent", "schema_version": 1,
             "token": lease["token"], "attempt_id": attempt_id, "unit": "timelearner-"+attempt_id+".service",
             "directory": str(path), "owner": lease["owner"], "memory_bytes": memory_bytes,
             "tasks": tasks, "maximum_wall_seconds": maximum_wall_seconds}
    value["sha256"] = digest_json(value)
    connection.execute('INSERT INTO managed_unit_intents VALUES (?,?,?,?,?)',
                       (attempt_id, lease["token"], str(path), "registered", _json(value)))
    return value


def transition(connection, lease, attempt_id, target):
    rows = [r for r in _rows(connection, lease) if r["attempt_id"] == attempt_id]
    _require(len(rows) == 1, "managed_intent_unknown")
    value = rows[0]
    if target == "submitted":
        _require(value["state"] == "registered", "managed_intent_not_unsubmitted")
        _request(value)
    elif target == "bound":
        _require(value["state"] == "submitted", "managed_intent_not_submitted")
        observed = _unit_status(value, owner_closed=False)
        _require(not observed["all_processes_closed"], "managed_unit_not_live_at_binding")
        from .contained_process import _group_path
        binding = observed["observation"]["binding"]
        group = _group_path(binding["control_group"])
        _require((group/"memory.max").read_text().strip() == str(value["memory_bytes"]) and
                 (group/"pids.max").read_text().strip() == str(value["tasks"]) and
                 (group/"memory.swap.max").read_text().strip() == "0", "managed_unit_kernel_limits_changed")
    elif target == "aborted":
        if value["state"] != "registered":
            return value  # Submitted/bound launches cannot be called unsubmitted.
        from .contained_process import _show
        _require(_show(value["unit"]).get("LoadState") == "not-found", "managed_abort_unit_exists")
    else:
        _require(False, "unknown_managed_intent_transition")
    connection.execute('UPDATE managed_unit_intents SET state=? WHERE attempt_id=? AND token=?',
                       (target, attempt_id, lease["token"]))
    return {**value, "state": target}


def require_closed_graph(connection, lease, *, owner_closed):
    observations = []
    for intent in _rows(connection, lease):
        try:
            observed = _unit_status(intent, owner_closed=owner_closed)
        except Exception as error:
            from .resource_reservations import ReservationError
            raise ReservationError("managed_unit_closure_unproven:"+intent["attempt_id"]+":"+str(error)) from error
        _require(observed["all_processes_closed"] is True, "managed_unit_still_live_or_pending:"+intent["attempt_id"])
        observations.append(observed)
    return {"kind": "timelearner_managed_unit_graph_closure", "schema_version": 1,
            "all_registered_units_closed": True, "units": observations, "scientific_verdict": None}
