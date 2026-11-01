"""Audit managed request records against original training and actual responses.

Saved-state replay may reset native dynamics; its semantic graph, image physics
and complete training evidence must still match the original source. This is
distinct from zero-tick capture invariance and does not attest process ownership.
"""
from copy import deepcopy
from hashlib import sha256

from .finalization_boundary_evidence import audit_boundary
from .learned_evidence import audit_learned_state
from .model_identity import canonical_model_sha256
from .native_evidence import require
from .posttune_transaction_evidence import audit_posttune_transaction


FIELDS = {"kind", "schema_version", "boundary", "transaction", "selected_package", "external_stop_reason",
          "calculate_mode", "provider_after_stop", "configured_phase_dispatch_implemented", "scientific_verdict"}


def _snapshot(value):
    require(sha256(value["native_xml"].encode("utf-8")).hexdigest() == value["native_xml_sha256"],
            "managed_source_xml_digest_mismatch")
    identity = value["identity"]
    require(canonical_model_sha256(identity["model"]) == identity["sha256"], "managed_source_identity_digest_mismatch")
    return {k: v for k, v in value.items() if k not in {"native_xml", "native_xml_sha256"}}


def _replay_source(value, calculate_mode=None):
    result = deepcopy(value)
    require(canonical_model_sha256({k: v for k, v in result.items() if k != "sha256"}) == result["sha256"],
            "managed_source_digest_mismatch")
    result.pop("sha256")
    require(type(result["calculate_mode"]) is int and result["calculate_mode"] in (0, 1), "invalid_replay_source_calculate_mode")
    if calculate_mode is not None:
        # The declared runtime control is changed AFTER importing saved Train.
        # Keep its original value in the audit result; do not relabel Train.
        result["calculate_mode"] = calculate_mode
    archive = result["neuron"]
    require(canonical_model_sha256({k: v for k, v in archive.items() if k != "sha256"}) == archive["sha256"],
            "managed_source_archive_digest_mismatch")
    archive.pop("sha256")
    archive["graph"] = _snapshot(archive["graph"])
    for definition in archive["class_definitions"]:
        definition["snapshot"] = _snapshot(definition["snapshot"])
    result["dataset"] = _snapshot(result["dataset"])
    return result


def audit_managed_finalization(record, original_source_case):
    require(type(record) is dict and set(record) == FIELDS and record["kind"] == "native_managed_finalization_control"
            and type(record["schema_version"]) is int and record["schema_version"] == 1, "unknown_managed_finalization_record")
    require(record["scientific_verdict"] is None and record["configured_phase_dispatch_implemented"] is False,
            "unsupported_managed_finalization_claim")
    require(type(record["calculate_mode"]) is int and record["calculate_mode"] in (0, 1), "invalid_managed_calculate_mode")
    boundary = record["boundary"]
    audit_boundary(boundary)
    require(boundary["diagnostic_only"] is False, "stopped_managed_finalization_source")
    p = boundary["controls"]["parameters"]
    binding = boundary["controls"]["bindings"]["IsNeedToTrain"]
    require(p["IsNeedToTrain"] is True and p["CalculateMode"] == record["calculate_mode"]
            and p["EnablePostTrainTuning"] is True and p["AutoCalibrateFixedLTZThreshold"] is True,
            "managed_finalization_intent_mismatch")
    require((binding["connected"] is True or binding["external_data_source"] is True) and bool(binding["sources"]),
            "managed_finalization_requires_declared_external_request")
    require(record["provider_after_stop"] is False and record["external_stop_reason"] == "native_finalization_external_stop",
            "managed_finalization_external_stop_mismatch")
    solo = boundary["source_solo"]
    require(solo["calculate_mode"] == record["calculate_mode"], "managed_replay_calculate_mode_mismatch")
    require(_replay_source(solo) == _replay_source(original_source_case[0], record["calculate_mode"]),
            "managed_original_source_lineage_mismatch")
    # The original packets/CSVs and summary are retained verbatim. Audit the
    # re-exported package against those primaries, never fabricate new Train.
    source_case = (solo, *original_source_case[1:])
    learned = audit_learned_state(*source_case)
    report = record["transaction"]
    require(report["source_recognition"]["source_solo"] == solo and report["status"] == "weights_selected"
            and record["selected_package"] == report["selected_package"], "managed_finalization_selected_source_mismatch")
    transaction = audit_posttune_transaction(report, source_case)
    return {"schema_version": 1, "calculate_mode": record["calculate_mode"], "training_source_audit": learned,
            "original_training_calculate_mode": original_source_case[0]["calculate_mode"],
            "original_training_source_sha256": original_source_case[0]["sha256"], "replayed_source_sha256": solo["sha256"],
            "transaction_audit": transaction, "external_stop_record_consistent": True,
            "native_control_execution_attested": False, "scientific_verdict": None}
