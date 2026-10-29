"""Versioned experiment identities, independent of deployment paths and case labels.

This module validates descriptor integrity. Artifact semantics/effective Rdk
readback and resource availability belong to preflight, never to a hash.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
import json
import math
import re
from typing import Any, Iterable
import uuid

from .model_identity import canonical_model_sha256


class ConditionError(ValueError):
    pass


CONDITION_ROLES = (
    "algorithm", "model_spec", "storage_profiles", "initial_state", "training_plan",
    "input_data", "presentation_protocol", "calibration_spec", "evaluation_spec",
    "execution_policy", "randomness_spec",
)
ARTIFACT_ROLES = frozenset(CONDITION_ROLES + ("observations", "scorer", "calibration_result"))
MAX_EXACT_INTEGER = 2**53 - 1
# Attempt/deployment metadata must not accidentally enter a scientific payload
# when a caller passes an unprojected native run configuration.
PROVENANCE_KEYS = frozenset(name.replace("_", "").lower() for name in (
    "run_id", "trial_id", "attempt_id", "case_id", "worker", "host", "pid",
    "output_directory", "output_dir", "executable_path", "source_directory",
    "runtime_directory", "deploy_root", "resource_root", "wall_started_at",
))


def require(value: bool, reason: str) -> None:
    if not value:
        raise ConditionError(reason)


def digest(value: Any) -> str:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            "invalid_sha256_reference")
    return value


def normalized(value: Any, depth: int = 0) -> Any:
    require(depth <= 64, "condition_json_nesting_limit")
    if value is None or type(value) is bool:
        return value
    if type(value) is str:
        try:
            value.encode("utf-8")
        except UnicodeError as error:
            raise ConditionError("invalid_unicode_condition_string") from error
        return value
    if type(value) is int:
        require(abs(value) <= MAX_EXACT_INTEGER, "inexact_condition_integer")
        return value
    if type(value) is float:
        require(math.isfinite(value), "nonfinite_condition_number")
        if value == 0:
            return 0
        if value.is_integer() and abs(value) <= MAX_EXACT_INTEGER:
            return int(value)
        return value
    if type(value) is list:
        return [normalized(item, depth + 1) for item in value]
    if type(value) is dict:
        require(all(type(key) is str for key in value), "nonstring_condition_key")
        return {normalized(key, depth + 1): normalized(item, depth + 1)
                for key, item in value.items()}
    raise ConditionError("unsupported_condition_value")


def serialize(value: Any) -> str:
    return json.dumps(normalized(value), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def parse(text: str) -> dict:
    require(type(text) is str, "condition_text_required")
    try:
        size = len(text.encode("utf-8"))
    except UnicodeError as error:
        raise ConditionError("invalid_unicode_condition_string") from error
    require(size <= 16 * 1024 * 1024, "invalid_condition_document_size")

    def pairs(items: list[tuple[str, Any]]) -> dict:
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_condition_key")
            result[key] = value
        return result

    def constant(value: str) -> Any:
        raise ConditionError("nonfinite_condition_number")

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, RecursionError) as error:
        raise ConditionError("invalid_condition_json") from error
    require(type(value) is dict, "condition_object_required")
    return normalized(value)


def keys(value: dict, expected: set[str]) -> None:
    require(type(value) is dict and set(value) == expected, "unknown_or_missing_condition_field")


def check_scientific_payload(value: Any) -> None:
    if type(value) is dict:
        for key, child in value.items():
            require(key.replace("_", "").lower() not in PROVENANCE_KEYS,
                    "provenance_field_in_condition_artifact:" + key)
            check_scientific_payload(child)
    elif type(value) is list:
        for child in value:
            check_scientific_payload(child)


def artifact(role: str, payload: dict) -> dict:
    require(type(role) is str and role in ARTIFACT_ROLES and type(payload) is dict, "invalid_condition_artifact_role")
    payload = normalized(payload)
    if role in CONDITION_ROLES:
        check_scientific_payload(payload)
    body = {"kind": "timelearner_condition_artifact", "schema_version": 1,
            "role": role, "payload": payload}
    return {**body, "sha256": canonical_model_sha256(body)}


def validate_artifact(value: dict, role: str, expected: str | None = None) -> dict:
    keys(value, {"kind", "schema_version", "role", "payload", "sha256"})
    require(value["kind"] == "timelearner_condition_artifact" and
            type(value["schema_version"]) is int and value["schema_version"] == 1,
            "unsupported_condition_artifact_schema")
    digest(value["sha256"])
    rebuilt = artifact(role, value["payload"])
    require(normalized(value) == rebuilt, "condition_artifact_digest_or_role_mismatch")
    require(expected is None or value["sha256"] == digest(expected), "condition_artifact_reference_mismatch")
    return rebuilt


@dataclass(frozen=True, slots=True)
class ConditionSpec:
    controller_version: int
    amplitude_goal: str
    algorithm: str
    model_spec: str
    storage_profiles: str
    initial_state: str
    training_plan: str
    input_data: str
    presentation_protocol: str
    calibration_spec: str
    evaluation_spec: str
    execution_policy: str
    randomness_spec: str

    def __post_init__(self) -> None:
        require(type(self.controller_version) is int and self.controller_version in (1, 2),
                "unsupported_condition_controller_version")
        require(type(self.amplitude_goal) is str and self.amplitude_goal == "captured_per_input",
                "unsupported_condition_amplitude_goal")
        for role in CONDITION_ROLES:
            digest(getattr(self, role))

    def to_object(self) -> dict:
        return {"kind": "timelearner_condition", "schema_version": 1,
                **{field.name: getattr(self, field.name) for field in fields(self)}}

    def dumps(self) -> str:
        return serialize(self.to_object())

    @property
    def fingerprint(self) -> str:
        return canonical_model_sha256(self.to_object())

    @classmethod
    def loads(cls, text: str) -> ConditionSpec:
        value = parse(text)
        names = {field.name for field in fields(cls)}
        keys(value, names | {"kind", "schema_version"})
        require(value["kind"] == "timelearner_condition" and
                type(value["schema_version"]) is int and value["schema_version"] == 1,
                "unsupported_condition_schema")
        return cls(**{name: value[name] for name in names})

    def resolve(self, artifacts: dict[str, dict]) -> dict[str, dict]:
        """Check all content references; this is not semantic/Rdk preflight."""
        require(type(artifacts) is dict, "condition_artifact_map_required")
        result = {}
        for role in CONDITION_ROLES:
            sha256 = getattr(self, role)
            require(sha256 in artifacts, "missing_condition_artifact:" + role)
            result[role] = validate_artifact(artifacts[sha256], role, sha256)["payload"]
        return result


def matrix_fingerprint(cases: Iterable[tuple[str, ConditionSpec]]) -> str:
    values = {}
    for case_id, condition in cases:
        require(type(case_id) is str and bool(case_id), "invalid_matrix_case_id")
        require(case_id not in values, "duplicate_matrix_case_id")
        require(isinstance(condition, ConditionSpec), "invalid_matrix_condition")
        values[case_id] = condition.fingerprint
    require(bool(values), "empty_condition_matrix")
    return canonical_model_sha256({"kind": "timelearner_condition_matrix", "schema_version": 1,
                                   "cases": normalized(values)})


def analysis_fingerprint(condition: ConditionSpec, *, model: str, runtime: str,
                         observations: str, scorer: str, calibration_result: str) -> str:
    return canonical_model_sha256({"kind": "timelearner_analysis_identity", "schema_version": 1,
                                   "condition": condition.fingerprint, "model": digest(model),
                                   "runtime": digest(runtime), "observations": digest(observations),
                                   "scorer": digest(scorer), "calibration_result": digest(calibration_result)})


def new_attempt_id() -> str:
    return str(uuid.uuid4())
