"""Verify the single permitted threshold edit; never certify calibration.

Source training/conversion execution is checked separately against primary data.
This module compares semantic physics, storage images and native serialized data.
"""
import copy
import hashlib
import struct

from .config_document import ConfigDocument, ConfigDocumentError, TextEdit
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, number, require
from .recognition_evidence import _physical, audit_recognition_derivation

FIELDS = {"kind", "schema_version", "dynamic_checkpoint", "state_kind", "implementation_id",
          "source_recognition", "threshold", "candidate_record", "model_revision",
          "recognition_certificate", "dataset", "neuron", "sha256"}
BASE_FIELDS = {"kind", "schema_version", "dynamic_checkpoint", "state_kind", "implementation_id",
               "source_solo", "conversion_spec", "conversion_record", "recognition_inputs", "model_revision",
               "recognition_certificate", "dataset", "neuron", "sha256"}


def _digest(envelope):
    require(type(envelope) is dict and envelope["sha256"] == canonical_model_sha256(
        {k: v for k, v in envelope.items() if k != "sha256"}), "threshold_candidate_digest_mismatch")


def _graph(archive, revision):
    require(archive["kind"] == "timelearner_model_archive" and type(archive["schema_version"]) is int
            and archive["schema_version"] == 2 and archive["dynamic_checkpoint"] is False,
            "unsupported_threshold_candidate_archive")
    _digest(archive)
    graph = archive["graph"]
    identity = graph["identity"]
    require(identity["valid"] is True and type(identity["model"]["schema_version"]) is int
            and identity["model"]["schema_version"] == 2 and
            canonical_model_sha256(identity["model"]) == identity["sha256"] == revision,
            "threshold_candidate_model_digest_mismatch")
    require(type(graph["native_xml"]) is str and hashlib.sha256(graph["native_xml"].encode("utf-8")).hexdigest()
            == graph["native_xml_sha256"], "threshold_candidate_xml_digest_mismatch")
    return graph


def audit_threshold_candidate(package, source_case=None):
    try:
        require(type(package) is dict and set(package) == FIELDS and
                package["kind"] == "timelearner_recognition_threshold_candidate" and
                type(package["schema_version"]) is int and package["schema_version"] == 1 and
                package["state_kind"] == "recognition" and package["dynamic_checkpoint"] is False and
                package["recognition_certificate"] is None, "unsupported_threshold_candidate_claim")
        _digest(package)
        source = package["source_recognition"]
        require(type(source) is dict and set(source) == BASE_FIELDS and
                source["kind"] == "timelearner_recognition_state" and type(source["schema_version"]) is int and
                source["schema_version"] == 1 and source["state_kind"] == "recognition" and
                source["dynamic_checkpoint"] is False and source["recognition_certificate"] is None,
                "threshold_candidate_requires_base_recognition")
        _digest(source)
        source_audit = None if source_case is None else audit_recognition_derivation(source, source_case)
        require(type(package["implementation_id"]) is str and bool(package["implementation_id"])
                and package["implementation_id"] == source["implementation_id"] and
                package["dataset"] == source["dataset"], "threshold_candidate_context_changed")
        threshold = number(package["threshold"])
        actual_record = package["candidate_record"]
        require(type(actual_record) is dict and actual_record.get("algorithm") in
                ("explicit-native-threshold-v1", "explicit-native-threshold-v2"), "unknown_threshold_candidate_algorithm")
        algorithm = actual_record["algorithm"]
        require(algorithm == "explicit-native-threshold-v2" or threshold > 0, "invalid_threshold_candidate_value")
        base, archive = source["neuron"], package["neuron"]
        before = _graph(base, source["model_revision"])
        after = _graph(archive, package["model_revision"])
        require(set(archive) == set(base) and all(archive[key] == base[key] for key in base
                if key not in {"sha256", "metadata", "graph"}), "threshold_candidate_storage_or_encoding_changed")
        require(set(after) == set(before) and all(after[key] == before[key] for key in before
                if key not in {"native_xml", "native_xml_sha256", "identity"}), "threshold_candidate_graph_context_changed")
        path = base["metadata"]["calibration"]["ltzone_path"]
        require(type(path) is str and path.startswith("$.") and path in
                {item.get("cached_ltzone") for item in before["identity"]["model"]["caches"]},
                "threshold_candidate_invalid_ltzone_path")
        expected_identity = copy.deepcopy(before["identity"])
        zones = [node for node in expected_identity["model"]["nodes"] if node["path"] == path]
        require(len(zones) == 1, "threshold_candidate_ambiguous_ltzone")
        original = _physical(zones[0], "Threshold")
        zones[0]["parameters"]["Threshold"]["data"]["value"] = struct.pack(">d", threshold).hex()
        expected_identity["sha256"] = canonical_model_sha256(expected_identity["model"])
        require(after["identity"] == expected_identity, "threshold_candidate_changed_other_physics")
        record = {"schema_version": 1, "algorithm": algorithm,
                  "source_recognition_sha256": source["sha256"], "source_model_revision": source["model_revision"],
                  "model_revision": package["model_revision"], "ltzone_path": path,
                  "original_threshold": original, "threshold": threshold, "calibrated": False}
        require(type(actual_record) is dict and actual_record == record and
                type(actual_record["schema_version"]) is int and actual_record["calibrated"] is False,
                "threshold_candidate_record_mismatch")
        metadata = copy.deepcopy(base["metadata"])
        metadata["calibration"].update(status="fixed", protocol="threshold-candidate-not-calibrated",
                                       threshold=threshold, candidate_record=record)
        metadata["recognition_verification"]["model_identity"] = package["model_revision"]
        require(archive["metadata"] == metadata, "threshold_candidate_metadata_changed")
        # Use the production parser for the actual Rdk dialect. Preserve every
        # other byte; missing/duplicated LTZone/Threshold cannot be substituted.
        before_xml = ConfigDocument(before["native_xml"].encode("utf-8"))
        after_xml = ConfigDocument(after["native_xml"].encode("utf-8"))
        location = (before_xml.root.name, before["component_name"])
        for part in path[2:].split("."):
            location += ("Components", part)
        location += ("Parameters", "Threshold")
        old_text, new_text = before_xml.text(location), after_xml.text(location)
        require(number(float(old_text)) == original and number(float(new_text)) == threshold,
                "threshold_candidate_xml_threshold_mismatch")
        expected_xml = before_xml.edited([TextEdit(location, old_text, new_text)])
        require(expected_xml == after_xml.raw, "threshold_candidate_changed_other_serialized_data")
        return {"schema_version": 1, "source_recognition_sha256": source["sha256"],
                "model_revision": package["model_revision"], "threshold": threshold,
                "threshold_derivation_verified": True, "source_training_and_conversion_checked": source_audit is not None,
                "source_audit": source_audit,
                "native_import_verified": False, "calibrated": False, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, struct.error, ConfigDocumentError) as error:
        raise EvidenceError("malformed_threshold_candidate:" + str(error)) from error
