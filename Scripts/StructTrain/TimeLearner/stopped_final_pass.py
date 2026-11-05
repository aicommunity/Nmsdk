"""Measured residuals of a complete negative final pass, never a certificate.

The native service deliberately keeps budget-exhausted models diagnostic.
This reader recovers the separately retained final observations without
authorizing recognition or changing the original training outcome.
"""
from pathlib import Path, PurePosixPath
import math

from .native_evidence import count, load, measured_training_probe, number, require
from .stopped_evidence import audit_stopped_state


def audit_negative_final_pass(package, summary, packets, traces):
    require(type(summary) is dict and summary.get("kind") == "native_training_state_summary"
            and type(summary.get("schema_version")) is int and summary["schema_version"] in (1, 2),
            "unknown_negative_final_summary_schema")
    source_audit = audit_stopped_state(package, summary, packets, traces)
    require(package["training_outcome"] == "budget_exhausted"
            and package["reason"] == "maximum_sweeps_exhausted"
            and package["reference_complete"] is True,
            "unsupported_negative_final_pass_source")
    protocol = package["protocol"]
    require(type(protocol.get("schema_version")) is int and protocol["schema_version"] == 3
            and protocol.get("routing") in ("classic_burst", "branch_solo_burst"),
            "unknown_negative_final_protocol_schema")
    inputs = protocol["inputs"]
    ids = [item["id"] for item in inputs]
    require(bool(ids) and len(set(ids)) == len(ids), "invalid_final_pass_inputs")
    tolerances = summary["tolerances"]
    require(set(tolerances) == {"amplitude_absolute", "amplitude_relative", "sync"}
            and tolerances == package["configuration"]["search"]["tolerances"],
            "final_pass_tolerances_changed")
    absolute, relative, sync = (number(tolerances[key]) for key in
                                ("amplitude_absolute", "amplitude_relative", "sync"))
    require(min(absolute, relative, sync) >= 0, "negative_final_pass_tolerance")
    selections = set()

    def measure(packet, index, revision, epoch):
        trial = packet["requested_specification"]["trial_id"]
        require(packets.get(trial) == packet, "final_pass_primary_packet_changed")
        prepared = packet["prepared"]
        spec = packet["observation"]["specification"]
        require(packet["current_base_revision"] == prepared["base_model_revision"] == revision
                and count(prepared["model_epoch"]) == epoch
                and prepared["protocol_revision"] == protocol["revision"]
                and prepared["routing"] == protocol["routing"], "final_pass_context_mismatch")
        selected = index if protocol["routing"] == "branch_solo_burst" else None
        require(prepared.get("selected_input_index") == selected,
                "final_pass_selected_input_mismatch")
        require(type(spec["schema_version"]) is int and spec["schema_version"] == protocol["schema_version"]
                and spec["sample_id"] == protocol["sample_id"]
                and spec["pattern_hash"] == protocol["pattern_hash"]
                and spec["expected_stimulus_ids"] == protocol["stimulus_ids"]
                and spec.get("stimulus_profile") == protocol.get("stimulus_profile")
                and spec.get("wave_assignment") == protocol.get("wave_assignment")
                and spec.get("peak_selection", "isolated_window") ==
                    protocol.get("peak_selection", "isolated_window")
                and spec["minimum_amplitude"] == protocol["minimum_amplitude"]
                and number(spec["maximum_sample_gap"]) <= number(protocol["maximum_sample_gap"]),
                "final_pass_protocol_changed")
        _, raw, arrival, end = measured_training_probe(
            packets, trial, ids[index], protocol["origin_stimulus_id"], selections)
        return {"trial_id": trial, "effective_model_revision": prepared["effective_model_revision"],
                "raw_potential": raw, "arrival": arrival, "plateau_end": end}

    references = {}
    for index, packet in enumerate(package["reference_packets"]):
        references[ids[index]] = measure(packet, index, package["capture_revision"], package["capture_epoch"])
    require(set(references) == set(ids), "incomplete_final_pass_references")
    finals = package["final_packets"]
    require(len(finals) == len(ids), "incomplete_negative_final_pass")
    measured = {}
    runs = set()
    for packet in finals:
        input_id = packet["prepared"]["input_id"]
        require(input_id in ids and input_id not in measured, "duplicate_or_unknown_final_input")
        measured[input_id] = measure(packet, ids.index(input_id), package["model_revision"], package["model_epoch"])
        runs.add(packet["observation"]["specification"]["run_id"])
    require(set(measured) == set(ids) and len(runs) == 1, "mixed_or_incomplete_negative_final_pass")
    sweeps = count(summary["configuration"]["maximum_sweeps"])
    require(sweeps == count(package["configuration"]["search"]["maximum_sweeps"])
            and sweeps > 0 and next(iter(runs)) ==
            summary["configuration"]["run_id"] + "/final/" + str(sweeps - 1),
            "negative_final_pass_attempt_mismatch")
    anchor = measured[ids[-1]]
    residuals = []
    for input_id in ids:
        sample = measured[input_id]
        target = references[input_id]["raw_potential"]
        error = sample["raw_potential"] - target
        low = sample["arrival"] - anchor["plateau_end"] if input_id != ids[-1] else 0.
        high = sample["plateau_end"] - anchor["arrival"] if input_id != ids[-1] else 0.
        tolerance = absolute + relative * abs(target)
        require(all(math.isfinite(value) for value in (error, low, high, tolerance)),
                "nonfinite_negative_final_residual")
        residuals.append({"input_id": input_id, "trial_id": sample["trial_id"],
                          "anchor_trial_id": anchor["trial_id"],
                          "effective_model_revision": sample["effective_model_revision"],
                          "target_raw_potential": target, "measured_raw_potential": sample["raw_potential"],
                          "amplitude_residual": error, "amplitude_tolerance": tolerance,
                          "timing_low": low, "timing_high": high,
                          "within_amplitude": abs(error) <= tolerance,
                          "within_timing": max(abs(low), abs(high)) <= sync})
    require(any(not row["within_amplitude"] or not row["within_timing"] for row in residuals),
            "sweep_budget_stop_has_no_measured_final_violation")
    return {"kind": "timelearner_negative_final_pass_diagnostics", "schema_version": 1,
            "source_stopped_sha256": package["sha256"], "source_audit": source_audit,
            "training_outcome": package["training_outcome"], "training_reason": package["reason"],
            "model_revision": package["model_revision"], "model_epoch": package["model_epoch"],
            "tolerances": dict(tolerances), "residuals": residuals,
            "complete_measured_final_pass": True, "certificate_present": False,
            "training_completed": False, "diagnostic_only": True,
            "native_execution_verified": False, "evaluation_verdict": None}


def load_inputs(path):
    """Read explicit relative artifact paths; no glob, CSV row or cwd inference."""
    path = Path(path).resolve(strict=True)
    description = load(path)
    require(type(description) is dict and set(description) == {"kind", "schema_version", "package", "summary", "trials"}
            and description["kind"] == "timelearner_stopped_final_pass_inputs"
            and type(description["schema_version"]) is int and description["schema_version"] == 1,
            "unknown_stopped_final_pass_inputs")

    def artifact(name):
        require(type(name) is str and name and "\\" not in name and ":" not in name
                and not PurePosixPath(name).is_absolute()
                and all(part not in ("", ".", "..") for part in name.split("/")),
                "invalid_final_pass_artifact_path")
        resolved = (path.parent / name).resolve(strict=True)
        require(resolved.is_file() and resolved.is_relative_to(path.parent), "final_pass_artifact_outside_inputs")
        return resolved

    require(type(description["trials"]) is list and description["trials"], "missing_final_pass_primary_trials")
    packets, traces, seen_paths = {}, {}, set()
    for item in description["trials"]:
        require(type(item) is dict and set(item) == {"packet", "trace"}, "invalid_final_pass_trial_paths")
        packet_path, trace_path = artifact(item["packet"]), artifact(item["trace"])
        require(packet_path not in seen_paths and trace_path not in seen_paths and packet_path != trace_path,
                "duplicate_final_pass_primary_path")
        seen_paths.update((packet_path, trace_path))
        packet = load(packet_path)
        trial = packet["requested_specification"]["trial_id"]
        require(trial not in packets, "duplicate_final_pass_primary_trial")
        packets[trial], traces[trial] = packet, trace_path
    return load(artifact(description["package"])), load(artifact(description["summary"])), packets, traces
