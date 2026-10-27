"""Audit completed learned-state evidence against original native CSV trials.

This is an evidence audit, not a replacement for native archive import, storage
validation, cryptographic package validation or recognition evaluation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .native_evidence import audit_probe, audit_training_summary, load, require

AUDITOR_VERSION = 1


def audit_learned_state(package: dict[str, Any], summary: dict[str, Any],
                        packets: dict[str, dict[str, Any]],
                        traces: dict[str, Path]) -> dict[str, Any]:
    require(package.get("kind") == "timelearner_completed_state" and
            package.get("schema_version") == 1, "unknown_learned_state_schema")
    require(package["state_kind"] == "learned_solo" and package["dynamic_checkpoint"] is False,
            "unsupported_learned_state_kind")
    require(package["training_outcome"] in {"exact", "search_unresolved"}, "unsupported_completed_outcome")
    require(bool(packets) and set(packets) == set(traces), "missing_primary_trace")
    audits = {trial: audit_probe(packet, traces[trial]) for trial, packet in packets.items()}
    require(package["model_revision"] == summary["actual_model_revision"] and
            package["model_epoch"] == summary["model_epoch"] and
            package["trained_inputs"] == summary["actual_parameters"] and
            package["certificate"] == summary["certificate"] and
            package["training_outcome"] == summary["outcome"], "package_summary_mismatch")
    certificate = package["certificate"]
    protocol = package["protocol"]
    require(protocol["schema_version"] == 3 and protocol["revision"] == certificate["protocol_revision"],
            "package_protocol_mismatch")
    config = package["configuration"]
    require(config["search"]["tolerances"] == summary["tolerances"] and
            config["search"]["bounds"] == summary["configuration"]["bounds"], "package_configuration_mismatch")
    reference_ids = {ref["trial_id"] for ref in summary["references"]}
    final_ids = {item["trial_id"] for item in certificate["residuals"]}
    embedded: dict[str, set[str]] = {}
    for field, expected in (("reference_packets", reference_ids), ("final_packets", final_ids)):
        require(isinstance(package[field], list) and bool(package[field]), "missing_embedded_evidence")
        seen: set[str] = set()
        for packet in package[field]:
            requested = packet["requested_specification"]
            require(isinstance(requested, dict), "missing_embedded_trial_identity")
            trial = requested["trial_id"]
            require(trial not in seen, "duplicate_embedded_trial")
            seen.add(trial)
            require(trial in packets and packet == packets[trial], "embedded_primary_evidence_mismatch")
        require(expected <= seen, "incomplete_embedded_evidence")
        embedded[field] = seen
    require(not embedded["reference_packets"] & embedded["final_packets"], "reference_final_identity_overlap")
    for ref in summary["references"]:
        require(audits[ref["trial_id"]]["valid_observation"] is True, "invalid_reference_primary")
    for trial in final_ids:
        require(audits[trial]["valid_observation"] is True, "invalid_final_primary")
    archive = package["neuron"]
    require(archive["graph"]["identity"]["sha256"] == package["model_revision"], "archive_revision_mismatch")
    metadata = archive["metadata"]
    require(metadata["state_kind"] == "learned_solo" and metadata["conversion"]["mode"] == "none" and
            metadata["calibration"]["status"] == "fixed" and
            metadata["training"]["status"] == package["training_outcome"], "archive_state_mismatch")
    native = audit_training_summary(summary, packets, protocol["origin_stimulus_id"])
    return {"auditor_version": AUDITOR_VERSION, "certificate_consistent": True,
            "primary_trials": len(packets), "embedded_trials": sum(map(len, embedded.values())),
            "exact": native["exact"], "model_revision": package["model_revision"],
            "native_import_verified": False, "package_digest_verified": False,
            "evaluation_verdict": None}


def load_case(package_path: Path) -> tuple[dict, dict, dict, dict]:
    require(package_path.name.endswith("_learned_state.json"), "unexpected_package_filename")
    stem = package_path.name.removesuffix("_learned_state.json")
    summary = load(package_path.with_name(stem + "_learned_summary.json"))
    packets, traces = {}, {}
    for path in sorted(package_path.parent.glob(stem + "_state_trial_*.json")):
        packet = load(path)
        trial = packet["requested_specification"]["trial_id"]
        require(trial not in packets, "duplicate_primary_trial")
        packets[trial], traces[trial] = packet, path.with_suffix(".csv")
    return load(package_path), summary, packets, traces


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_learned_state(*load_case(args.package)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
