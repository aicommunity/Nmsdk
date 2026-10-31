"""Value-boundary consistency checks; no execution or convergence attestation."""
from copy import deepcopy
from hashlib import sha256

from .model_identity import canonical_model_sha256
from .native_evidence import equal, require
from .recognition_trial_evidence import audit_recognition_trial_set


def _digest(value):
    require(value.get("sha256") == canonical_model_sha256(
        {k: v for k, v in value.items() if k != "sha256"}), "boundary_digest_mismatch")


def audit_boundary(boundary):
    require(boundary["kind"] == "timelearner_finalization_boundary" and
            type(boundary["schema_version"]) is int and boundary["schema_version"] == 1,
            "unknown_finalization_boundary_schema")
    _digest(boundary)
    solo = boundary["source_solo"]
    _digest(solo)
    require(boundary["dynamic_checkpoint"] is False and boundary["mid_probe_resume_supported"] is False
            and boundary["recognition_success"] is None, "unsupported_boundary_claim")
    require(boundary["training_outcome"] == solo["training_outcome"], "boundary_outcome_mismatch")
    stopped = solo["kind"] == "timelearner_stopped_state"
    require(solo["kind"] in {"timelearner_completed_state", "timelearner_stopped_state"}
            and boundary["diagnostic_only"] is stopped, "boundary_diagnostic_mismatch")
    if stopped:
        require(solo["certificate"] is None, "stopped_boundary_certificate")
    controls = boundary["controls"]
    require(set(controls["parameters"]) == set(controls["bindings"]), "boundary_control_bindings_missing")
    p = controls["parameters"]
    require(boundary["phase_requests"] == {
        "target_reference": p["AutoCalibrateFixedLTZThreshold"], "post_tune": p["EnablePostTrainTuning"],
        "post_train_mid": p["EnablePostTrainMidThreshold"],
        "legacy_parallel_peak": solo["configuration"]["model"]["branch"] and not p["EnablePostTrainTuning"]},
        "boundary_phase_request_mismatch")
    return {"diagnostic_only": stopped, "training_evidence_checked": False, "scientific_verdict": None}


def _comparable(package):
    result = deepcopy(package)
    _digest(result)
    _digest(result["neuron"])
    for definition in result["neuron"]["class_definitions"]:
        snapshot = definition["snapshot"]
        xml = snapshot["native_xml"]
        require(sha256(xml.encode("utf-8")).hexdigest() == snapshot["native_xml_sha256"],
                "boundary_xml_digest_mismatch")
        if snapshot["component_class"] == "NPMembraneBio":
            empty = '<InputFeedbackSignal Type="MDMatrix&lt;d&gt;" Rows="0" Cols="0" PType="266" IoType="17"></InputFeedbackSignal>'
            zero = '<InputFeedbackSignal Type="MDMatrix&lt;d&gt;" Rows="1" Cols="1" PType="266" IoType="17">0</InputFeedbackSignal>'
            snapshot["native_xml"] = xml.replace(empty, zero)
            snapshot["native_xml_sha256"] = sha256(snapshot["native_xml"].encode("utf-8")).hexdigest()
    del result["sha256"], result["neuron"]["sha256"]
    return result


def audit_capture(comparison, boundary):
    audit_boundary(boundary)
    require(comparison["kind"] == "native_finalization_capture_comparison" and
            comparison["schema_version"] == 1 and comparison["semantic_equal"] is True,
            "unknown_boundary_comparison")
    require(comparison["captured"] == boundary["source_solo"], "boundary_capture_source_mismatch")
    require(_comparable(comparison["before"]) == _comparable(comparison["captured"]) ==
            _comparable(comparison["after"]), "boundary_export_changed")
    return {"exports_checked": 3, "scientific_verdict": None}


def audit_replay(replay, job, run_id):
    require(replay["kind"] == "native_finalization_boundary_replay" and replay["schema_version"] == 1
            and replay["recognition_success"] is None, "unknown_boundary_replay")
    audit_boundary(replay["boundary"])
    require(replay["recognition"] == job["source_recognition"] and
            replay["boundary"]["implementation_id"] == job["implementation_id"], "boundary_replay_source_mismatch")
    require(not replay["boundary"]["diagnostic_only"], "diagnostic_boundary_replay")
    expected = {(run_id, q["trial_id"]): q for q in job["trials"]}
    require(len(expected) == len(job["trials"]), "duplicate_boundary_job_trial")
    result = audit_recognition_trial_set(replay["observations"], expected, replay["recognition"])
    require(result["all_observations_valid"], "invalid_boundary_replay_observation")
    for observation in replay["observations"]:
        q = expected[(observation["run_id"], observation["trial_id"])]
        require(all(observation[k] == q[k] for k in ("pattern_isi", "reset_policy", "maximum_samples"))
                and equal(observation["end"] - observation["begin"], q["duration"])
                and observation["frequency_hz"] == job["frequency_hz"], "boundary_replay_condition_mismatch")
    return result
