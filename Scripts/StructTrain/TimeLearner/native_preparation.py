"""Typed preparation of native checks; no execution or kernel attestation.

The first release accepts POSIX UTF-8/LF supervisors with one documented
literal WORKER.write_text/write_bytes call. Static byte consistency does not
prove that the call executes, its destination, or the physical worker bytes.
The launcher must still hash the actual written file before starting it.
"""
import ast
import base64
import hashlib
import json
import re

from .collector_provenance import capture_git_case_inventory, _signed
from .native_evidence import require
from .runtime import digest_json


_BINDING_KEYS = {"kind", "schema_version", "request_sha256", "unit", "invocation_id",
                 "control_group", "initial_main_pid", "initial_start_ticks", "sha256"}


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _copy_json(value):
    try:
        raw = json.dumps(value, ensure_ascii=False, allow_nan=False)
        raw.encode("utf-8")
        return json.loads(raw)
    except (TypeError, ValueError, UnicodeError):
        require(False, "native_preparation_invalid_json_data")


def _ids(value, reason):
    require(type(value) is list and value and all(type(v) is str and v for v in value)
            and len(value) == len(set(value)), reason)
    return value


def _label(value):
    return type(value) is str and bool(value) and not any(ord(c) < 32 for c in value)


def embedded_worker_bytes(supervisor, *, platform):
    """Read one literal writer statically; never interpret or execute Python."""
    require(platform == "posix" and type(supervisor) is bytes and
            len(supervisor) <= 8*1024**2 and b"\r" not in supervisor,
            "native_preparation_supervisor_platform_or_bytes")
    try:
        tree = ast.parse(supervisor.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError):
        require(False, "native_preparation_supervisor_syntax")
    writers = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and
               isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
               and n.func.value.id == "WORKER" and n.func.attr.startswith("write")]
    require(len(writers) == 1, "native_preparation_worker_writer_count")
    call = writers[0]
    require(len(call.args) == 1 and isinstance(call.args[0], ast.Constant),
            "native_preparation_worker_literal_required")
    value = call.args[0].value
    if call.func.attr == "write_bytes":
        require(type(value) is bytes and not call.keywords,
                "native_preparation_worker_bytes_writer")
        raw = value
    else:
        require(call.func.attr == "write_text" and type(value) is str and
                all(k.arg in {"encoding", "newline", "errors"} and
                    isinstance(k.value, ast.Constant) for k in call.keywords) and
                len({k.arg for k in call.keywords}) == len(call.keywords),
                "native_preparation_worker_text_writer")
        options = {k.arg: k.value.value for k in call.keywords}
        require(options.get("encoding") == "utf-8" and
                options.get("newline") in {None, "", "\n"} and
                options.get("errors", "strict") == "strict",
                "native_preparation_worker_encoding_or_newline")
        try:
            raw = value.encode("utf-8")
        except UnicodeEncodeError:
            require(False, "native_preparation_worker_encoding_or_newline")
    require(len(raw) <= 2*1024**2 and b"\r" not in raw,
            "native_preparation_worker_size_or_newline")
    return raw


def _prior_bindings(claims, originals):
    require(type(claims) is list and type(originals) is dict,
            "native_preparation_binding_collection")
    result, seen = [], set()
    for row in claims:
        require(type(row) is dict and set(row) == {"binding_path", "binding"} and
                _label(row["binding_path"]) and row["binding_path"] not in seen,
                "native_preparation_binding_claim")
        path = row["binding_path"]
        require(path in originals and type(originals[path]) is bytes and
                len(originals[path]) <= 64*1024, "native_preparation_binding_original_missing")
        raw = originals[path]
        original = _signed(raw)  # Existing strict JSON/content-integrity reader.
        require(set(original) == _BINDING_KEYS and
                original["kind"] == "timelearner_contained_binding" and
                type(original["schema_version"]) is int and original["schema_version"] == 1 and
                type(original["initial_main_pid"]) is int and original["initial_main_pid"] > 0 and
                all(type(original[k]) is str for k in ["initial_start_ticks", "request_sha256",
                    "invocation_id", "unit", "control_group", "sha256"]) and
                original["initial_start_ticks"].isdigit() and
                re.fullmatch(r"[0-9a-f]{64}", original["request_sha256"]) is not None and
                re.fullmatch(r"[0-9a-f]{32}", original["invocation_id"]) is not None and
                re.fullmatch(r"timelearner-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\.service",
                             original["unit"]) is not None and
                original["control_group"].startswith("/") and
                ".." not in original["control_group"].split("/") and
                original["control_group"].endswith("/"+original["unit"]),
                "native_preparation_binding_schema")
        require(row["binding"] == original, "native_preparation_binding_changed")
        result.append({"binding_path": path, "binding": original,
                       "original_bytes": len(raw), "original_sha256": _sha(raw),
                       "original_base64": base64.b64encode(raw).decode("ascii")})
        seen.add(path)
    require(seen == set(originals), "native_preparation_binding_original_set")
    return result


def _layout(inventory, selected_ids, runplan, partitions):
    require("Libraries/Nmsdk-PulseLib" in inventory["source_closure"],
            "native_preparation_pulse_closure_missing")
    _ids(selected_ids, "native_preparation_selected_ids")
    require(set(selected_ids) <= set(inventory["ids"]), "native_preparation_unknown_case")
    require(type(runplan) is list and runplan, "native_preparation_runplan")
    flattened, names = [], set()
    for row in runplan:
        require(type(row) is dict and set(row) == {"name", "expected_ids", "wall_seconds"}
                and type(row["name"]) is str and
                re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", row["name"]) is not None and
                row["name"] not in names and
                type(row["wall_seconds"]) is int and row["wall_seconds"] > 0,
                "native_preparation_leaf")
        flattened += _ids(row["expected_ids"], "native_preparation_leaf_ids")
        names.add(row["name"])
    require(flattened == selected_ids, "native_preparation_leaf_union_or_order")
    require(type(partitions) is list and partitions, "native_preparation_partitions")
    partition_ids, names = [], set()
    for row in partitions:
        require(type(row) is dict and set(row) == {"name", "ids", "count"} and
                _label(row["name"]) and row["name"] not in names and
                type(row["count"]) is int, "native_preparation_partition")
        ids = _ids(row["ids"], "native_preparation_partition_ids")
        require(row["count"] == len(ids), "native_preparation_partition_count")
        partition_ids += ids
        names.add(row["name"])
    require(len(partition_ids) == len(set(partition_ids)) and
            set(partition_ids) == set(selected_ids), "native_preparation_partition_union")
    files = {}
    for path, row in inventory["files"].items():
        ids = [v for v in selected_ids if v in row["ids"]]
        if ids:
            files[path] = {"sha256": row["sha256"], "count": len(ids), "ids": ids}
    return {"root": inventory["root_commit"],
            "pulse": inventory["source_closure"]["Libraries/Nmsdk-PulseLib"]["head"],
            "inventory": {"root": inventory["root_commit"], "total": len(selected_ids),
                          "unique": len(selected_ids), "files": files},
            "runplan": runplan, "partitions": partitions,
            "counts": {"selected_cases": len(selected_ids), "leaf_gates": len(runplan)}}


def _claims(claims, expected, inventory):
    claims = _copy_json(claims)
    require(type(claims) is dict and set(expected) <= set(claims) and
            set(claims) <= set(expected) | {"source_claims", "root_claims", "pulse_claims"},
            "native_preparation_claim_schema")
    require(all(digest_json(claims[k]) == digest_json(v) for k, v in expected.items()),
            "native_preparation_current_claim_mismatch")
    for key, value in [("root_claims", expected["root"]), ("pulse_claims", expected["pulse"])]:
        rows = claims.get(key, {})
        require(type(rows) is dict and all(_label(k) and v == value for k, v in rows.items()),
                "native_preparation_named_source_claim_mismatch")
    rows, labels = claims.get("source_claims", []), set()
    require(type(rows) is list, "native_preparation_source_claim_schema")
    for row in rows:
        require(type(row) is dict and set(row) == {"label", "source_path", "sha256"} and
                _label(row["label"]) and row["label"] not in labels and
                type(row["source_path"]) is str and
                row["source_path"] in inventory["files"], "native_preparation_source_claim_schema")
        require(row["sha256"] == inventory["files"][row["source_path"]]["sha256"],
                "native_preparation_source_hash_mismatch")
        labels.add(row["label"])


def prepare_native_checks(source_root, *, selections, selected_ids, runplan, partitions,
                          claims=None, prior_bindings, prior_originals, worker_bytes,
                          supervisor_bytes, supervisor_platform="posix", historical=None):
    """Capture once and fail before a launcher updates/builds/runs anything.

    claims contains all exposed current metadata; historical is preserved as
    JSON data without reinterpreting its old roots/hashes/counts as active.
    This function neither starts processes nor checks/reconciles reservations.
    """
    inventory = capture_git_case_inventory(source_root, selections=selections)
    expected = _layout(inventory, selected_ids, runplan, partitions)
    if claims is None:
        claims = _copy_json(expected)
    _claims(claims, expected, inventory)
    require(type(worker_bytes) is bytes and worker_bytes ==
            embedded_worker_bytes(supervisor_bytes, platform=supervisor_platform),
            "native_preparation_embedded_worker_changed")
    prior = _prior_bindings(prior_bindings, prior_originals)
    spec = {"kind": "timelearner_native_preparation", "schema_version": 1,
            "source_inventory": inventory, "current": expected, "current_claims": claims,
            "prior_bindings": prior,
            "worker": {"bytes": len(worker_bytes), "sha256": _sha(worker_bytes)},
            "supervisor": {"bytes": len(supervisor_bytes), "sha256": _sha(supervisor_bytes),
                           "platform": supervisor_platform},
            "static_embedded_worker_bytes_equal": True, "historical": historical,
            "physical_worker_bytes_verified": False, "compiled_inventory_verified": False,
            "kernel_closure_attested": False, "test_success_attested": False,
            "scientific_verdict": None}
    # Roundtrip removes caller-owned mutable references and rejects NaN/Inf.
    spec = _copy_json(spec)
    return {**spec, "sha256": digest_json(spec)}


def current_claims(inventory, *, selected_ids, runplan, partitions):
    """Canonical current fields for maintained declarative frontends."""
    return _copy_json(_layout(inventory, selected_ids, runplan, partitions))


def serialize_preparation(spec):
    spec = _copy_json(spec)
    require(type(spec) is dict and spec.get("kind") == "timelearner_native_preparation" and
            spec.get("sha256") == digest_json({k: v for k, v in spec.items() if k != "sha256"}),
            "native_preparation_content_changed")
    require(type(spec.get("schema_version")) is int and spec["schema_version"] == 1 and
            spec.get("static_embedded_worker_bytes_equal") is True and
            all(spec.get(k) is False for k in ["physical_worker_bytes_verified",
                "compiled_inventory_verified", "kernel_closure_attested", "test_success_attested"])
            and spec.get("scientific_verdict", "missing") is None,
            "native_preparation_attestation_outside_scope")
    return (json.dumps(spec, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")
