"""Validate raw partial traces for display, without certifying their measurements."""
import csv
import math
from pathlib import Path

from .native_evidence import EvidenceError, after, count, equal, number, require


def read_partial_probe(packet: dict, trace: Path):
    try:
        return _read_partial_probe(packet, trace)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError, ValueError, OverflowError) as error:
        raise EvidenceError("malformed_partial_probe:"+str(error)) from error


def _read_partial_probe(packet, trace):
    require(type(packet["evidence_schema_version"]) is int and packet["evidence_schema_version"] == 2,
            "unsupported_partial_probe_evidence_schema")
    require(packet["kind"] == "timelearner_native_probe_evidence" and
            packet["native_status"] in ("rejected", "cancelled", "running", "queued", "idle", "completed"),
            "unknown_partial_probe_kind_or_status")
    requested = packet["requested_specification"]
    require(type(requested) is dict and type(requested["schema_version"]) is int and
            requested["schema_version"] == 3 and requested["time_frame"] == "relative_to_trial_start",
            "unsupported_partial_probe_request")
    require(requested["record_spikes"] is False, "native_training_probe_spike_capture_not_supported")
    require(equal(requested["begin"], 0) and number(requested["end"]) > 0, "invalid_partial_requested_window")
    for name in ("run_id", "trial_id", "sample_id", "pattern_hash"):
        require(type(requested[name]) is str and bool(requested[name]), "missing_partial_probe_identity:"+name)
    observation = packet["observation"]
    spec = observation["specification"] if observation is not None else requested
    with trace.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    require(rows and len(rows[0]) >= 2 and rows[0] == ["time", "stimulus"]+
            [f"soma{i}" for i in range(len(rows[0])-2)], "unknown_partial_trace_schema")
    require(all(len(row) == len(rows[0]) for row in rows[1:]), "ragged_partial_trace")
    try:
        values = [[float(token) for token in row] for row in rows[1:]]
    except ValueError as error:
        raise EvidenceError("invalid_partial_trace_token") from error
    if observation is None:
        # A request is relative to a proposed start, not an observed clock.
        # No axes or soma response may be invented for an unprepared trial.
        require(not values, "samples_without_observed_probe_context")
        return observation, spec, None, [], 0, {
            "context_observed": False, "raw_trace_checked": True, "sample_count": 0,
            "recorded_header_channels": len(rows[0])-2, "recorded_window_complete": False,
            "first_sample_time": None, "last_sample_time": None,
            "unobserved_intervals": [], "nonfinite_cells": [], "reason": "no_observed_context"}
    require(type(observation["schema_version"]) is int and observation["schema_version"] == 3 and
            type(spec["schema_version"]) is int and spec["schema_version"] == 3 and
            spec["time_frame"] == "absolute_model_time", "unsupported_partial_observation_schema")
    require(type(observation["valid"]) is type(observation["complete"]) is bool,
            "invalid_partial_observation_flags")
    require(not (packet["native_status"] == "completed" and observation["valid"] and observation["complete"]),
            "complete_probe_requires_full_primary_audit")
    require(observation["spike_count"] is None and observation["spikes"] == [],
            "unsupported_partial_native_spike_claim")
    for key in ("schema_version", "run_id", "trial_id", "sample_id", "pattern_hash", "record_spikes"):
        require(requested[key] == spec[key], "partial_request_identity_mismatch:"+key)
    require(spec["record_spikes"] is False, "native_training_probe_spike_capture_not_supported")
    begin, end = number(spec["begin"]), number(spec["end"])
    require(end > begin and equal(requested["begin"], 0) and equal(end-begin, requested["end"]),
            "partial_requested_window_mismatch")
    prepared = packet["prepared"]
    require(type(prepared) is dict and prepared["effective_model_revision"] == spec["effective_model_revision"] and
            bool(prepared["base_model_revision"]) and bool(prepared["protocol_revision"]),
            "missing_partial_prepared_context")
    profile = spec["stimulus_profile"]
    require(type(profile) is dict and type(profile["generator_class"]) is str and bool(profile["generator_class"]),
            "missing_partial_stimulus_profile")
    frequency = number(profile["frequency_hz"])
    require(frequency > 0 and (requested["stimulus_profile"] is None or requested["stimulus_profile"] == profile),
            "partial_stimulus_profile_mismatch")
    require(type(spec["baseline"]) is list, "invalid_partial_baseline_dimensions")
    channels = len(spec["baseline"])
    require(channels > 0 and len(rows[0])-2 == channels, "partial_trace_channel_dimension_mismatch")
    require(len(values) == count(observation["sample_count"]), "partial_sample_count_mismatch")
    times = [row[0] for row in values]
    require(all(math.isfinite(t) for t in times) and all(b > a for a, b in zip(times, times[1:])) and
            all(not after(begin, t) and not after(t, end) for t in times), "invalid_partial_trace_clock")
    missing = []
    if not times:
        missing.append([begin, end])
    else:
        if after(times[0], begin+1.5/frequency):missing.append([begin, times[0]])
        missing.extend([a, b] for a, b in zip(times, times[1:]) if after(b, a+1.5/frequency))
        if after(end, times[-1]):missing.append([times[-1], end])
    nonfinite = [{"csv_row": i+2, "column": rows[0][j]} for i, row in enumerate(values)
                 for j, value in enumerate(row[1:], 1) if not math.isfinite(value)]
    # Inf is a missing ordinate, never a drawable value or a clipped maximum.
    samples = [{"time": row[0], "stimulus": row[1] if math.isfinite(row[1]) else math.nan,
                "soma": [v if math.isfinite(v) else math.nan for v in row[2:]]} for row in values]
    covered = (bool(times) and not after(times[0], begin+1.5/frequency) and
        not after(end, times[-1]+1.5/frequency) and not any(
            after(b, a+1.5/frequency) for a, b in zip(times, times[1:])))
    quality = {"context_observed": True, "raw_trace_checked": True, "sample_count": len(samples),
               "recorded_header_channels": channels, "first_sample_time": times[0] if times else None,
               "last_sample_time": times[-1] if times else None, "unobserved_intervals": missing,
               "nonfinite_cells": nonfinite,
               "current_base_revision": packet.get("current_base_revision"),
               "base_revision_changed": (prepared["base_model_revision"] != packet["current_base_revision"]
                                         if packet.get("current_base_revision") else None),
               "recorded_window_complete": bool(observation["complete"] and covered and not nonfinite),
               "reason": observation.get("end_reason", "invalid_or_incomplete_observation")}
    return observation, spec, frequency, samples, channels, quality
