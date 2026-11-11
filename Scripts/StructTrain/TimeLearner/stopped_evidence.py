"""Audit diagnostic stopped-state provenance without a convergence verdict."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model_identity import canonical_model_sha256
from .capacitance_evidence import audit_package_capacitance
from .capacitance_boundary_evidence import audit_package_capacitance_history
from .native_evidence import (audit_probe, count, load, number, require,
                              validate_configured_repeat_policy, validate_search_history_availability)

OUTCOMES = {"external_stop", "budget_exhausted", "invalid_model", "invalid_observation", "search_unresolved"}


def audit_stopped_state(package: dict, summary: dict, packets: dict, traces: dict) -> dict:
    if package.get('schema_version') in (5,6,7):
        from .composite_package_evidence import audit_composite_package
        require(package.get('kind') == 'timelearner_stopped_state', 'unknown_stopped_state_schema')
        require(not packets and not traces, 'composite_package_legacy_primary_overlay')
        return audit_composite_package(package, summary)
    require(package.get("kind") == "timelearner_stopped_state" and type(package.get("schema_version")) is int
            and package["schema_version"] in (1, 2, 3, 4)
            and len(package) == {1: 26, 2: 27, 3: 28, 4: 28}[package['schema_version']], "unknown_stopped_state_schema")
    require(package["state_kind"] == "diagnostic" and package["dynamic_checkpoint"] is False,
            "unsupported_stopped_state_kind")
    require(package["certificate"] is None and package["training_outcome"] in OUTCOMES,
            "false_stopped_certificate_or_outcome")
    require(package["sha256"] == canonical_model_sha256({k: v for k, v in package.items() if k != "sha256"}),
            "package_digest_mismatch")
    require(isinstance(package["reason"], str) and bool(package["reason"])
            and isinstance(package["capture_revision"], str) and bool(package["capture_revision"]),
            "missing_stop_or_capture_identity")
    count(package["capture_epoch"]); count(package["model_epoch"])
    require(count(package["session_attempt"]) > 0, "missing_attempt")
    require(summary["state"] == "finished" and summary["model_state_kind"] == "diagnostic" and summary["certificate"] is None
            and summary["certificate_matches_actual_model"] is False
            and package["model_revision"] == summary["actual_model_revision"]
            and package["model_epoch"] == summary["model_epoch"]
            and package["trained_inputs"] == summary["actual_parameters"]
            and package["training_outcome"] == summary["outcome"]
            and package["reason"] == summary["reason"], "package_summary_mismatch")
    from .native_model_spec import validate_model_spec
    validate_model_spec(package['configuration']['model'])
    repeats = validate_configured_repeat_policy(package["configuration"], summary)
    from .candidate_recovery import RETRY_MODE, project_recovery_summary
    projected, recovery_mode = project_recovery_summary(summary)
    retained = validate_search_history_availability(projected)
    require(set(packets) == set(traces), "missing_primary_trace")
    if not packets:
        require(package['reference_packets'] == [] and package['final_packets'] == [] and
                package['reference_complete'] is False, 'empty_stopped_attempt_contains_measurements')
    observed = package["observed_packets"]
    require(isinstance(observed, list) and len(observed) == len(packets), "missing_observed_attempt")
    seen = set()
    audits = {}
    for packet in observed:
        requested = packet["requested_specification"]
        require(isinstance(requested, dict) and bool(requested["trial_id"]), "missing_trial_identity")
        trial = requested["trial_id"]
        require(trial not in seen and packets.get(trial) == packet, "duplicate_or_changed_primary_packet")
        seen.add(trial)
        require(traces[trial].is_file(), "missing_primary_trace")
        audits[trial] = audit_probe(packet, traces[trial])
    require(seen == set(packets), "primary_packet_set_mismatch")
    protocol = package["protocol"]
    require(protocol["schema_version"] == 3, "unknown_protocol_schema")
    recovery = None
    if recovery_mode != RETRY_MODE:
        from .candidate_recovery_history import audit_recovery_history
        from .probe_diagnostics import read_partial_probe
        for trial, packet in packets.items():
            if not audits[trial]["valid_observation"]:
                read_partial_probe(packet, traces[trial])
        recovery = audit_recovery_history(summary, packets, traces, protocol)
    references = package["reference_packets"]
    require(isinstance(references, list) and type(package["reference_complete"]) is bool
            and len(references) <= len(protocol["inputs"])
            and package["reference_complete"] == (len(references) == len(protocol["inputs"])),
            "false_reference_completion")
    reference_ids = set()
    raw = []
    for index, packet in enumerate(references):
        trial = packet["requested_specification"]["trial_id"]
        require(trial not in reference_ids and packets.get(trial) == packet
                and audits[trial]["valid_observation"] is True, "unusable_reference_packet")
        reference_ids.add(trial)
        prepared = packet["prepared"]
        require(packet["current_base_revision"] == prepared["base_model_revision"] == package["capture_revision"]
                and prepared["model_epoch"] == package["capture_epoch"], "reference_capture_binding_mismatch")
        peaks = packet["observation"]["peaks"]
        require(len(peaks) == 1 and peaks[0]["input_id"] == protocol["inputs"][index]["id"], "reference_input_order_mismatch")
        raw.append(number(peaks[0]["raw_potential"]))
    final_ids = set()
    for packet in package["final_packets"]:
        trial = packet["requested_specification"]["trial_id"]
        require(trial not in final_ids and trial not in reference_ids and packets.get(trial) == packet,
                "duplicate_or_unavailable_final_packet")
        final_ids.add(trial)
    archive = package["neuron"]
    require(archive["sha256"] == canonical_model_sha256({k: v for k, v in archive.items() if k != "sha256"}),
            "archive_digest_mismatch")
    identity = archive["graph"]["identity"]
    require(identity["sha256"] == canonical_model_sha256(identity["model"])
            and identity["sha256"] == package["model_revision"], "model_digest_mismatch")
    metadata = archive["metadata"]; training = metadata["training"]
    require(metadata["state_kind"] == "diagnostic" and training["certificate"] is None
            and metadata["conversion"]["mode"] == "none" and metadata["calibration"]["status"] == "fixed",
            "archive_state_mismatch")
    for field in ("status", "reason", "capture_revision", "capture_epoch", "reference_complete"):
        require(training[field] == package["training_outcome" if field == "status" else field],
                "archive_training_mismatch:" + field)
    require(training["captured_per_input"] == raw
            and training["target_pattern"] == package["configuration"]["model"]["initial_isi"],
            "archive_target_or_reference_mismatch")
    capacitance = audit_package_capacitance(package)
    capacitance_history = audit_package_capacitance_history(package, summary)
    return {"auditor_version": 5 if recovery is not None else 4, "state_kind": "diagnostic", "training_outcome": package["training_outcome"],
            "n0_candidate_repeats": repeats, "search_history_retained": retained,
            "primary_trials": len(packets), "reference_trials": len(references), "final_trials": len(final_ids),
            "invalid_or_censored_trials": sum(not a["valid_observation"] for a in audits.values()),
            "certificate_present": False, "native_import_verified": False,
            "capacitance_state": capacitance, **({"capacitance_history": capacitance_history} if capacitance_history is not None else {}),
            **({"candidate_recovery": recovery} if recovery is not None else {}),
            "evaluation_verdict": None}


def load_case(path: Path) -> tuple[dict, dict, dict, dict]:
    require(path.name.endswith("_stopped_state.json"), "unexpected_stopped_filename")
    stem = path.name.removesuffix("_stopped_state.json")
    package = load(path)
    if package.get('schema_version') in (5,6,7):
        summary_path = path.with_name(stem + '_stopped_summary.json')
        return package, load(summary_path) if summary_path.exists() else None, {}, {}
    packets, traces = {}, {}
    for trial_path in sorted(path.parent.glob(stem + "_stopped_trial_*.json")):
        packet = load(trial_path); trial = packet["requested_specification"]["trial_id"]
        require(trial not in packets, "duplicate_primary_trial")
        packets[trial], traces[trial] = packet, trial_path.with_suffix(".csv")
    return load(path), load(path.with_name(stem + "_stopped_summary.json")), packets, traces


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("package", type=Path)
    print(json.dumps(audit_stopped_state(*load_case(parser.parse_args().package)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
