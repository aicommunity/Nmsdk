"""Recheck calibrated-state provenance with the common primary-data scorer.

This validates recorded evidence and sole metadata changes, not simulator
execution, grid selection, statistical independence or an independent Test.
"""
import copy

from .model_identity import canonical_model_sha256 as sha
from .native_evidence import EvidenceError, after, count, number, require
from .native_calibration_evidence import audit_native_calibration_assessment
from .threshold_candidate_evidence import audit_threshold_candidate

FIELDS = {"kind", "schema_version", "dynamic_checkpoint", "state_kind", "implementation_id",
          "source_candidate", "calibration_proof", "threshold", "model_revision",
          "recognition_certificate", "dataset", "neuron", "sha256"}
PROOF_FIELDS = {"kind", "schema_version", "algorithm", "specification", "candidate_sha256", "model_revision",
                "search", "confirmation", "search_assessment", "confirmation_assessment", "calibrated",
                "grid_selection_verified", "execution_attested", "statistical_independence_verified", "evaluation_verdict", "sha256"}
REQUEST_FIELDS = {"run_id", "trial_id", "sample_id", "label", "pattern_hash", "pattern_isi", "duration",
                  "maximum_samples", "reset_policy", "record_threshold_potential"}


def _signed(value):
    value.pop("sha256", None);value["sha256"] = sha(value)
    return value


def _digest(value):
    require(type(value) is dict and value["sha256"] == sha({k: v for k, v in value.items() if k != "sha256"}),
            "calibrated_state_digest_mismatch")


def _text(value):
    require(type(value) is str and bool(value.strip()), "invalid_calibration_proof_text")
    return value


def audit_native_calibration_matrix(matrix, assessment, criterion, candidate, source_case, *, require_success=True):
    require(type(matrix) is dict and set(matrix) == {"requests", "observations"}, "unknown_calibration_proof_matrix")
    requests, observations = matrix["requests"], matrix["observations"]
    require(type(requests) is list and 2 <= len(requests) <= 10000 and type(observations) is list
            and len(requests) == len(observations), "incomplete_calibration_proof_matrix")
    wanted, trials = {}, []
    run_id = _text(requests[0]["run_id"])
    for position, request in enumerate(requests):
        require(type(request) is dict and set(request) == REQUEST_FIELDS, "unknown_calibration_proof_request")
        for key in ("run_id", "trial_id", "sample_id", "label", "pattern_hash"): _text(request[key])
        require(request["run_id"] == run_id and request["trial_id"] not in wanted,
                "duplicate_or_invalid_calibration_proof_request")
        require(type(request["record_threshold_potential"]) is bool and 2 <= count(request["maximum_samples"]) <= 10000000
                and number(request["duration"]) > 0, "invalid_calibration_proof_request_budget")
        pattern = request["pattern_isi"]
        require(type(pattern) is list and 1 <= len(pattern) <= 10000 and all(number(v) >= 0 for v in pattern)
                and sha(pattern) == request["pattern_hash"], "invalid_calibration_proof_pattern")
        wanted[request["trial_id"]] = request
        trials.append({**{key: request[key] for key in ("trial_id", "sample_id", "label", "pattern_hash", "reset_policy", "duration")},
                       "presentation_index": position, "observation": "inline/"+request["trial_id"]})
    for observation in observations:
        require(type(observation) is dict and observation["trial_id"] in wanted, "unexpected_calibration_proof_observation")
        request = wanted[observation["trial_id"]]
        require(all(observation[key] == request[key] for key in
                    ("run_id", "trial_id", "sample_id", "label", "pattern_hash", "pattern_isi", "reset_policy"))
                and count(observation["maximum_samples"]) == count(request["maximum_samples"])
                and type(observation["schema_version"]) is int
                and observation["schema_version"] == (2 if request["record_threshold_potential"] else 1),
                "calibration_proof_observation_design_changed")
    spec = {"kind": "timelearner_recognition_evaluation_spec", "schema_version": 1, "run_id": run_id,
            "model_revision": candidate["model_revision"], "coverage_policy": "per_trial_windows",
            "criterion": {"id": "post_anchor_target_whole_window_foil_v1", **criterion}, "trials": trials}
    result = audit_native_calibration_assessment(assessment, spec, observations, candidate, source_case)
    if require_success:
        require(result["criterion_met"] is True, "native_confirmation_criterion_not_met")
    return run_id


def audit_calibrated_state(package, source_case=None):
    try:
        require(type(package) is dict and set(package) == FIELDS
                and package["kind"] == "timelearner_calibrated_recognition_state"
                and type(package["schema_version"]) is int and package["schema_version"] == 1
                and package["state_kind"] == "recognition" and package["dynamic_checkpoint"] is False
                and package["recognition_certificate"] is None, "unsupported_calibrated_state_claim")
        _digest(package)
        candidate, proof = package["source_candidate"], package["calibration_proof"]
        source_audit = audit_threshold_candidate(candidate, source_case)
        require(type(proof) is dict and set(proof) == PROOF_FIELDS
                and proof["kind"] == "native_selected_threshold_confirmation"
                and type(proof["schema_version"]) is int and proof["schema_version"] == 1
                and proof["algorithm"] == "selected-candidate-fresh-confirmation-v1"
                and proof["calibrated"] is True and proof["grid_selection_verified"] is False
                and proof["execution_attested"] is False and proof["statistical_independence_verified"] is False
                and proof["evaluation_verdict"] is None and proof["candidate_sha256"] == candidate["sha256"]
                and proof["model_revision"] == candidate["model_revision"], "unsupported_calibration_proof_claim")
        _digest(proof)
        specification = proof["specification"]
        require(type(specification) is dict and set(specification) ==
                {"protocol", "data_partition_id", "attempt_id", "clock_id", "criterion"}
                and specification["protocol"] in ("historical_same_matrix", "frozen_independent_calibration"),
                "unknown_native_confirmation_spec")
        for key in ("data_partition_id", "attempt_id", "clock_id"): _text(specification[key])
        criterion = specification["criterion"]
        require(type(criterion) is dict and set(criterion) ==
                {"anchor", "begin_offset", "end_offset", "reject_target_outside_window"}, "unknown_confirmation_criterion")
        search_id = audit_native_calibration_matrix(proof["search"], proof["search_assessment"], criterion, candidate, source_case)
        confirmation_id = audit_native_calibration_matrix(proof["confirmation"], proof["confirmation_assessment"], criterion, candidate, source_case)
        require(search_id != confirmation_id, "native_confirmation_requires_fresh_run")
        search, confirmation = proof["search"], proof["confirmation"]
        semantic = lambda rows: [{k: v for k, v in row.items() if k not in {"run_id", "trial_id"}} for row in rows]
        require(semantic(search["requests"]) == semantic(confirmation["requests"]), "native_confirmation_design_changed")
        require(after(min(number(o["begin"]) for o in confirmation["observations"]),
                      max(number(o["end"]) for o in search["observations"])), "native_confirmation_reused_or_overlapping_measurements")
        expected_archive = copy.deepcopy(candidate["neuron"])
        expected_archive["metadata"]["calibration"].update(status="calibrated", protocol=specification["protocol"],
                                                         confirmation_sha256=proof["sha256"])
        _signed(expected_archive)
        expected = {"kind": "timelearner_calibrated_recognition_state", "schema_version": 1,
                    "dynamic_checkpoint": False, "state_kind": "recognition", "implementation_id": candidate["implementation_id"],
                    "source_candidate": candidate, "calibration_proof": proof, "threshold": candidate["threshold"],
                    "model_revision": candidate["model_revision"], "recognition_certificate": None,
                    "dataset": candidate["dataset"], "neuron": expected_archive}
        require(package == _signed(expected), "native_calibrated_state_derivation_mismatch")
        return {"schema_version": 1, "calibration_evidence_consistent": True, "calibrated": True,
                "model_revision": package["model_revision"], "threshold": number(package["threshold"]),
                "source_audit": source_audit, "native_execution_verified": False, "native_import_verified": False,
                "grid_selection_verified": False, "statistical_independence_verified": False, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_calibrated_state:"+str(error)) from error
