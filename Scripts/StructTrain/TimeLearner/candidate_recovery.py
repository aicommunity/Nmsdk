"""Validate the flat candidate-recovery declaration, without certifying probes.

Projection is only a view for existing base-schema validators. Callers must
retain the original record for hashing, native execution and publication.
"""
from copy import deepcopy

from .native_evidence import count, require


RECOVERY_MODE = "advance_unassigned_burst"
RETRY_MODE = "retry_same_candidate"
_ENVELOPE_FIELDS = {"base_schema_version", "invalid_measurement_recovery"}


def _project(record, *, kind, configuration_field):
    require(type(record) is dict and record.get("kind") == kind,
            "invalid_candidate_recovery_record")
    version = record.get("schema_version")
    require(type(version) is int and version in (1, 2, 3, 4, 5),
            "unknown_candidate_recovery_schema")
    if version != 5:
        require(not _ENVELOPE_FIELDS.intersection(record),
                "unversioned_candidate_recovery_declaration")
        return deepcopy(record), RETRY_MODE
    base = record.get("base_schema_version")
    require(type(base) is int and base in (1, 2, 3, 4) and
            record.get("invalid_measurement_recovery") == RECOVERY_MODE,
            "unsupported_candidate_recovery_envelope")
    configuration = record.get(configuration_field)
    require(type(configuration) is dict and
            "maximum_invalid_observations" in configuration,
            "missing_candidate_recovery_invalid_allowance")
    require(count(configuration["maximum_invalid_observations"]) > 0,
            "candidate_recovery_requires_invalid_allowance")
    projected = deepcopy(record)
    for field in _ENVELOPE_FIELDS:
        projected.pop(field)
    projected["schema_version"] = base
    return projected, RECOVERY_MODE


def project_recovery_configuration(configuration):
    """Keep unknown base fields: the native strict codec must still check them."""
    return _project(configuration, kind="timelearner_native_cold_configuration",
                    configuration_field="search")


def project_recovery_summary(summary):
    return _project(summary, kind="native_training_state_summary",
                    configuration_field="configuration")


def bind_recovery_policy(configuration, summary):
    """Bind declared policy and allowance; this is not a primary-data audit."""
    declared, mode = project_recovery_configuration(configuration)
    measured, measured_mode = project_recovery_summary(summary)
    require(mode == measured_mode and
            declared["schema_version"] == measured["schema_version"],
            "configuration_summary_recovery_schema_mismatch")
    if mode == RECOVERY_MODE:
        require(count(declared["search"]["maximum_invalid_observations"]) ==
                count(measured["configuration"]["maximum_invalid_observations"]),
                "configuration_summary_recovery_allowance_mismatch")
    return declared, measured
