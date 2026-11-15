"""Operational native process policy and portable cgroup evidence consistency.

A portable audit cannot attest the truth of an arbitrary saved kernel record.
It checks bindings and closure; scientific/model validity remains with callers.
Legacy run manifests retain their original launched-executable-only contract.
"""
import copy
import math
from pathlib import Path, PurePosixPath
import re
import uuid

from .native_evidence import load, load_json, require
from .runtime import digest_json, runtime_content_identity


POLICY_FIELDS = {"kind", "schema_version", "backend", "memory_bytes", "tasks", "cooperative_capture"}


def validate_policy(value, maximum_wall_seconds=None):
    if value is None:
        return None
    require(type(value) is dict and set(value) == POLICY_FIELDS | ({"reservation"} if value.get("schema_version") == 2 else set()) and
            value["kind"] == "timelearner_native_process_policy" and
            type(value["schema_version"]) is int and value["schema_version"] in (1, 2) and
            value["backend"] == "bound_cgroup", "unknown_native_process_policy")
    require(type(value["memory_bytes"]) is int and 0 < value["memory_bytes"] <= 2**63-1 and
            type(value["tasks"]) is int and 0 < value["tasks"] <= 2**31-1,
            "native_process_policy_limits_invalid")
    require(value["cooperative_capture"] is True, "native_containment_requires_cooperative_capture")
    if value["schema_version"] == 2:
        context = value["reservation"]
        require(type(context) is dict and set(context) == {"database", "capacity", "token"} and
                type(context["database"]) is str and PurePosixPath(context["database"]).is_absolute() and
                ".." not in PurePosixPath(context["database"]).parts and
                type(context["token"]) is str, "native_resource_context_schema")
        try:
            require(str(uuid.UUID(context["token"])) == context["token"], "native_resource_token_invalid")
        except ValueError as error:
            from .native_evidence import EvidenceError
            raise EvidenceError("native_resource_token_invalid") from error
        capacity = context["capacity"]
        require(type(capacity) is dict and set(capacity) == {"slots", "memory_bytes", "disk_bytes", "tasks"} and
                all(type(v) is int and 0 < v <= 2**63-1 for v in capacity.values()),
                "native_resource_context_capacity_invalid")
    if maximum_wall_seconds is not None:
        require(type(maximum_wall_seconds) in (int, float) and math.isfinite(maximum_wall_seconds) and
                1 <= maximum_wall_seconds <= 86400, "invalid_contained_wall_budget")
    return copy.deepcopy(value)


def execute_native(manifest, arguments, cwd, output, maximum_wall_seconds, policy):
    """Explicit production policy; no fallback after a contained launch failure."""
    policy = validate_policy(policy, maximum_wall_seconds)
    require(policy is not None, "native_process_policy_required")
    from .contained_runner import execute
    managed, lease = None, None
    if policy["schema_version"] == 2:
        managed, lease = _open_reservation(policy)
    result = execute(manifest, arguments, cwd, output, maximum_wall_seconds,
                     memory_bytes=policy["memory_bytes"], tasks=policy["tasks"], cooperative_capture=True,
                     managed_reservation=managed)
    if managed is not None:
        registry, token = managed
        target = str((Path(output).resolve()/"contained").resolve())
        rows = [v for v in registry.inspect()["managed_unit_intents"]
                if v["token"] == token and v["intent"]["directory"] == target]
        require(len(rows) <= 1, "native_managed_intent_duplicate")
        require(bool(rows) or not (Path(output)/"contained/request.json").exists(), "native_managed_intent_missing")
        from .process_runner import _write
        _write(Path(output)/"reservation-context.json", {
            "kind": "timelearner_native_resource_context", "schema_version": 1,
            "registry": policy["reservation"], "lease": lease, "intent": rows[0] if rows else None,
            "scientific_verdict": None})
    return result


def _open_reservation(policy):
    from .resource_reservations import Reservations, ReservationError
    from .native_evidence import EvidenceError
    context = policy["reservation"]
    database = Path(context["database"])
    require(database.is_file() and not database.is_symlink(), "native_resource_registry_missing_or_alias")
    try:
        registry = Reservations(database, capacity=context["capacity"], managed_units=True)
        registry.validate_paths(context["token"])
        rows = [v for v in registry.inspect()["leases"] if v["token"] == context["token"]]
        require(len(rows) == 1 and rows[0]["state"] == "held", "native_resource_lease_not_held")
        lease = {k: rows[0][k] for k in ("token", "job_id", "owner", "resources", "state", "demands", "controller")}
        require(lease["controller"]["memory_bytes"]+policy["memory_bytes"] <= lease["demands"]["memory_bytes"] and
                lease["controller"]["tasks"]+policy["tasks"] <= lease["demands"]["tasks"],
                "native_resource_context_budget_exhausted")
    except ReservationError as error:
        raise EvidenceError("native_resource_context:"+str(error)) from error
    return (registry, context["token"]), lease


def policy_for_reservation(registry, token, *, memory_bytes, tasks):
    """Create a per-attempt operational policy for this exact owning process."""
    require(registry.managed_units is True, "managed_unit_ledger_v3_required")
    value = {"kind": "timelearner_native_process_policy", "schema_version": 2, "backend": "bound_cgroup",
             "memory_bytes": memory_bytes, "tasks": tasks, "cooperative_capture": True,
             "reservation": {"database": str(registry.path), "capacity": registry.capacity, "token": token}}
    value = validate_policy(value)
    _open_reservation(value)
    return value


def _audit_resource_context(directory, runtime, policy, *, auditable):
    context = load(directory/"reservation-context.json")
    require(set(context) == {"kind", "schema_version", "registry", "lease", "intent", "scientific_verdict"} and
            context["kind"] == "timelearner_native_resource_context" and type(context["schema_version"]) is int and
            context["schema_version"] == 1 and context["registry"] == policy["reservation"] and
            context["scientific_verdict"] is None, "native_resource_context_changed")
    lease = context["lease"]
    require(lease["token"] == policy["reservation"]["token"] and lease["state"] == "held" and
            set(lease["demands"]) == {"slots", "memory_bytes", "disk_bytes", "tasks"} and
            all(type(v) is int and v >= 0 for v in lease["demands"].values()), "native_resource_lease_changed")
    require(lease["demands"]["slots"] > 0 and
            all(lease["demands"][k] <= policy["reservation"]["capacity"][k] for k in lease["demands"]),
            "native_resource_capacity_changed")
    controller, owner = lease["controller"], lease["owner"]
    require(controller["binding"]["sha256"] == digest_json({k: v for k, v in controller["binding"].items() if k != "sha256"}) and
            type(owner["pid"]) is int and owner["pid"] > 0 and type(owner["uid"]) is int and owner["uid"] >= 0,
            "native_resource_controller_binding_changed")
    require(controller["binding"]["initial_main_pid"] == owner["pid"] and
            controller["binding"]["initial_start_ticks"] == owner["start_ticks"] and
            type(controller["memory_bytes"]) is int and controller["memory_bytes"] > 0 and
            type(controller["tasks"]) is int and controller["tasks"] > 0 and
            controller["memory_bytes"]+policy["memory_bytes"] <= lease["demands"]["memory_bytes"] and
            controller["tasks"]+policy["tasks"] <= lease["demands"]["tasks"], "native_resource_controller_or_budget_changed")
    row = context["intent"]
    if row is None:
        require(not auditable and not (directory/"contained/request.json").exists(), "native_managed_intent_missing")
        return
    require(set(row) == {"token", "state", "intent"} and row["token"] == lease["token"] and
            row["state"] in ("registered", "submitted", "bound", "aborted"), "native_managed_intent_state_changed")
    intent = row["intent"]
    require(intent["sha256"] == digest_json({k: v for k, v in intent.items() if k != "sha256"}) and
            intent["token"] == lease["token"] and intent["owner"] == owner and
            intent["memory_bytes"] == policy["memory_bytes"] and intent["tasks"] == policy["tasks"],
            "native_managed_intent_changed")
    if auditable:
        request = _signed(directory/"contained/request.json")
        binding = _signed(directory/"contained/owned-unit.json")
        require(row["state"] == "bound" and intent["attempt_id"] == request["attempt_id"] and
                intent["unit"] == binding["unit"] == request["unit"] and
                request["controller"] == {"pid": owner["pid"], "start_ticks": owner["start_ticks"]} and
                request["uid"] == owner["uid"] and request["boot_id"] == owner["boot_id"] and
                intent["directory"] == str(PurePosixPath(load(directory/"request.json")["cancel_file"]).parent/"contained") and
                any(v["access"] == "write" and
                    (PurePosixPath(intent["directory"]) == PurePosixPath(v["canonical_path"]) or
                     PurePosixPath(intent["directory"]).is_relative_to(PurePosixPath(v["canonical_path"])))
                    for v in lease["resources"]), "native_managed_unit_lease_binding_changed")


def _signed(path):
    value = load(path)
    require(value.get("sha256") == digest_json({k: v for k, v in value.items() if k != "sha256"}),
            "native_contained_record_digest_changed")
    return value


def audit_contained_attempt(directory, runtime, policy, *, auditable):
    """Return normalized native arguments after checking portable OS evidence.

    Recorded original paths are compared to one another, never resolved on the
    analysis machine. No local /proc, systemd or executable is required here.
    A failed launch may have incomplete closure evidence; it cannot authorize
    native analysis or be promoted to successful execution.
    """
    directory = Path(directory)
    policy = validate_policy(policy)
    require(policy is not None and type(auditable) is bool, "native_process_policy_required")
    process, request = load(directory/"result.json"), load(directory/"request.json")
    if policy["schema_version"] == 2:
        _audit_resource_context(directory, runtime, policy, auditable=auditable)
    require(set(request) == {"arguments", "working_directory", "maximum_wall_seconds", "cancel_file",
                            "memory_bytes", "tasks", "cooperative_capture"}, "native_contained_request_schema_changed")
    validate_policy(policy, request["maximum_wall_seconds"])
    require(type(request["arguments"]) is list and all(type(a) is str for a in request["arguments"]) and
            request["cooperative_capture"] is True and
            request["memory_bytes"] == policy["memory_bytes"] and request["tasks"] == policy["tasks"] and
            type(request["memory_bytes"]) is int and type(request["tasks"]) is int,
            "native_contained_policy_request_changed")
    fingerprint = digest_json(runtime_content_identity(runtime))
    require(runtime["runtime_fingerprint"] == process["runtime_fingerprint"] == fingerprint and
            type(process["schema_version"]) is int and process["schema_version"] == 2 and
            process["kind"] == "timelearner_process_result" and process["ownership_scope"] == "bound_cgroup" and
            type(process["all_processes_closed"]) is bool and process["scientific_verdict"] is None and
            process["model_time"] is None, "native_contained_result_scope_changed")
    require(process["execution"] in ("completed", "timeout", "interrupted", "process_error") and
            (auditable or process["execution"] != "completed"), "native_contained_result_status_changed")
    normalized = {**request, "model_time": None}
    normalized["arguments"] = request["arguments"] + ["--timelearner-capture-directory", str(PurePosixPath(request["cancel_file"]).parent)]
    if not auditable and not (directory/"whole-group-closure.json").exists():
        require(process["execution"] == "process_error" and not process["all_processes_closed"] and
                process["runtime_provenance"] == "invalid_or_incomplete_runtime",
                "native_contained_failed_launch_claims_closure")
        return normalized
    inner = directory/"contained"
    launch = _signed(inner/"request.json")
    binding = _signed(inner/"owned-unit.json")
    require(launch["kind"] == "timelearner_contained_request" and type(launch["schema_version"]) is int and
            launch["schema_version"] == 1 and binding["kind"] == "timelearner_contained_binding" and
            type(binding["schema_version"]) is int and binding["schema_version"] == 1 and
            re.fullmatch(r"timelearner-[0-9a-f-]{36}\.service", launch["unit"]) is not None and
            binding["unit"] == launch["unit"] and binding["request_sha256"] == launch["sha256"] and
            binding["control_group"].endswith("/"+binding["unit"]) and
            re.fullmatch("[0-9a-f]{32}", binding["invocation_id"]) is not None,
            "native_contained_unit_binding_changed")
    require(launch["executable"] == runtime["executable"]["path"] and
            launch["runtime_fingerprint"] == fingerprint and
            launch["arguments"] == normalized["arguments"] and
            launch["working_directory"] == request["working_directory"] and
            launch["maximum_wall_seconds"] == request["maximum_wall_seconds"] and
            launch["memory_bytes"] == policy["memory_bytes"] and launch["tasks"] == policy["tasks"] and
            all(launch["environment"].get(k) == v for k, v in runtime["loader_environment"].items()),
            "native_contained_launch_request_changed")
    closed = load(directory/"whole-group-closure.json")
    require(closed["binding"] == binding and closed["all_processes_closed"] is True and
            process["all_processes_closed"] is True, "native_contained_whole_group_closure_missing")
    limits_path = inner/"limits-readback.json"
    if auditable or limits_path.exists():
        limits = load(limits_path)
        require(limits["unit"] == binding["unit"] and limits["invocation_id"] == binding["invocation_id"] and
                limits["control_group"] == binding["control_group"] and
                limits["memory.max"] == str(policy["memory_bytes"]) and limits["memory.swap.max"] == "0" and
                limits["pids.max"] == str(policy["tasks"]) and
                binding["initial_main_pid"] in limits["initial_members"] and
                limits["systemd"]["KillMode"] == "control-group" and limits["systemd"]["Restart"] == "no",
                "native_contained_kernel_limits_changed")
    if auditable:
        owned = load(directory/"owned-process.json")
        require(owned["pid"] == binding["initial_main_pid"] and
                owned["start_ticks"] == binding["initial_start_ticks"] and owned["boot_id"] == launch["boot_id"] and
                all(owned[k] == binding[k] for k in ("unit", "invocation_id", "control_group")),
                "native_contained_main_identity_changed")
        terminal = load(directory/"terminal-unit-state.json")
        require(terminal["binding"] == binding and terminal["all_processes_closed"] is True and
                terminal["state"]["ExecMainCode"] == "1" and
                terminal["state"]["ExecMainStatus"] == str(process["returncode"]) and
                type(process["returncode"]) is int and
                process["runtime_provenance"] == "loaded_files_captured",
                "native_contained_terminal_status_changed")
        for name, kind in (("capture-ready.json", "native_runtime_capture_ready"),
                           ("capture-ack.json", "native_runtime_capture_ack")):
            record = load(directory/name)
            require(record == {"kind": kind, "schema_version": 1, "pid": owned["pid"],
                               "start_ticks": owned["start_ticks"]} and
                    type(record["schema_version"]) is int and type(record["pid"]) is int,
                    "native_contained_cooperative_identity_changed")
        loaded = load_json(directory/"loaded-files.json")
        require(type(loaded) is list and all(type(v) is dict and set(v) == {"path", "size", "sha256"} and
                type(v["path"]) is str and PurePosixPath(v["path"]).is_absolute() and
                type(v["size"]) is int and v["size"] >= 0 and type(v["sha256"]) is str and
                re.fullmatch("[0-9a-f]{64}", v["sha256"]) is not None for v in loaded) and
                len({v["path"] for v in loaded}) == len(loaded) and
                {k: runtime["executable"][k] for k in ("path", "size", "sha256")} in loaded,
                "native_contained_loaded_files_changed")
    return normalized
