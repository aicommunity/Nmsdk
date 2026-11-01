"""Distinct Test-owner and fresh-process transport evidence; no science verdict."""
from .native_evidence import EvidenceError, count, require
from .recognition_owner_evidence import audit_owner_recognition, paired_owner_observation
from .recognition_evidence import audit_fresh_recognition_transport


def audit_fresh_destination(case, transfer):
    result = audit_owner_recognition(*case)
    require(set(transfer) == {"kind", "schema_version", "source_owner", "test_owner", "distinct_owners",
            "target_controller_version_before", "target_inputs_before", "target_controller_version_after",
            "target_inputs_after", "source_model_before", "source_model_after", "target_model", "evaluation_verdict"},
            "fresh_owner_transfer_field_set_mismatch")
    require(transfer["kind"] == "native_recognition_fresh_owner_transfer" and type(transfer["schema_version"]) is int
            and transfer["schema_version"] == 1, "unknown_fresh_owner_transfer")
    require(transfer["distinct_owners"] is True and isinstance(transfer["source_owner"], str)
            and isinstance(transfer["test_owner"], str) and transfer["source_owner"] and transfer["test_owner"]
            and transfer["source_owner"] != transfer["test_owner"], "fresh_owner_not_distinct")
    package = case[0]
    require(transfer["source_model_before"] == transfer["source_model_after"] == package["source_solo"]["model_revision"]
            and transfer["target_model"] == package["model_revision"], "fresh_owner_changed_source_or_target")
    require(count(transfer["target_controller_version_before"]) == 1
            and count(transfer["target_controller_version_after"]) == package["source_solo"]["controller_version"]
            and count(transfer["target_inputs_before"]) > 0
            and count(transfer["target_inputs_after"]) == len(package["recognition_inputs"]), "fresh_owner_defaults_or_readback_mismatch")
    require(transfer["evaluation_verdict"] is None, "unexpected_fresh_owner_science_claim")
    return {"distinct_destination_verified": True, "source_model_preserved": True,
            "owner_audit": result, "evaluation_verdict": None}


def audit_fresh_owner_process(case, observation, trace):
    try:
        audit_owner_recognition(*case)
        require(set(observation) == {"kind", "schema_version", "trial_id", "model_revision", "complete", "sample_count",
                "last_sample_time", "emitted", "soma_variation", "frozen_before", "frozen_after",
                "controller_version_before", "controller_version_after", "scientific_verdict"}, "fresh_owner_process_field_set_mismatch")
        require(observation["kind"] == "native_recognition_owner_fresh_process_observation"
                and type(observation["schema_version"]) is int and observation["schema_version"] == 1,
                "unknown_fresh_owner_process_schema")
        package, source, spec, paired, paired_trace, _, _ = case
        require(observation["frozen_before"] == observation["frozen_after"] == package["model_revision"], "fresh_owner_process_model_changed")
        require(count(observation["controller_version_before"]) == 1
                and count(observation["controller_version_after"]) == package["source_solo"]["controller_version"],
                "fresh_owner_process_controller_readback_mismatch")
        converted = {key: value for key, value in observation.items()
                     if key not in ("frozen_before", "controller_version_before", "controller_version_after")}
        converted["kind"] = "native_recognition_fresh_process_observation"
        source_case = package, source, spec, paired_owner_observation(paired), paired_trace
        result = audit_fresh_recognition_transport(source_case, converted, trace)
        require(result["waveform_bytes_exact"], "fresh_owner_process_bytes_differ")
        return result
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError("malformed_fresh_owner_process:" + str(error)) from error
