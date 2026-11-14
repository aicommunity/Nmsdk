"""Audit native training evidence against primary traces; no selectivity verdict.

This format is independent of the recognition CSV schemas. It supports the
version-1/2 C++ ProbeEvidenceJson producer and schema-3 training observations.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import json
import math
import sys
import zlib
from pathlib import Path
from typing import Any

AUDITOR_VERSION = 7


class EvidenceError(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise EvidenceError(reason)


def number(value: Any) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), "not_a_number")
    require(math.isfinite(value), "nonfinite_number")
    return float(value)


def count(value: Any) -> int:
    actual = number(value)
    require(0 <= actual <= 2**53 - 1 and actual.is_integer(), "invalid_count")
    return int(actual)


def after(a: float, b: float) -> bool:
    # Same floating roundoff allowance as NumericChecks.h; no physical tolerance.
    return a > b + 32 * sys.float_info.epsilon * max(1.0, abs(a), abs(b))


def equal(a: Any, b: Any) -> bool:
    a, b = number(a), number(b)
    return not after(a, b) and not after(b, a)


def measured_wave_plateaus(signal, minimum):
    """Interior positive plateaus in actual sample order; no inferred peaks."""
    measured, index = [], 1
    while index + 1 < len(signal):
        last = index
        while last + 1 < len(signal) and signal[last + 1] == signal[index]:
            last += 1
        if last + 1 < len(signal) and signal[index] >= minimum and signal[index] > signal[index - 1] and signal[last] > signal[last + 1]:
            measured.append((index, last))
        index = last + 1
    return measured


def parse_json_bytes(raw: bytes) -> Any:
    """The same strict decoder for files and already snapshotted archive bytes."""
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result

    def invalid_constant(token: str) -> None:
        raise EvidenceError("nonfinite_json_token:" + token)

    result = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                        parse_constant=invalid_constant)
    return result


def load_json(path: Path) -> Any:
    """Strict JSON value reader, including runtime mapping arrays."""
    physical = path
    if not path.is_file() and path.with_name(path.name+'.archive.json').is_file():
        from .external_archive import locate
        physical = locate(path)
    raw = physical.read_bytes()
    if path.suffix == ".gz":
        try:
            raw = gzip.decompress(raw)
        except (gzip.BadGzipFile, EOFError, zlib.error) as error:
            raise EvidenceError("invalid_compressed_json") from error
    return parse_json_bytes(raw)


def load(path: Path) -> dict[str, Any]:
    result = load_json(path)
    require(isinstance(result, dict), "not_an_object")
    return result


def require_primary_trace_clock(spec: dict[str, Any], sample_count: Any, times: list[float]) -> None:
    """Shared strict whole-window clock check for valid and diagnostic probes."""
    require(len(times) == count(sample_count) >= 3, "sample_count_mismatch")
    begin, end = number(spec["begin"]), number(spec["end"])
    gap = number(spec["maximum_sample_gap"])
    require(gap > 0 and count(spec["maximum_samples"]) >= len(times), "invalid_sample_budget")
    require(equal(times[0], begin) and equal(times[-1], end), "incomplete_trace_coverage")
    roundoff = 32 * sys.float_info.epsilon * max(1., abs(begin), abs(end))
    require(gap > 2 * roundoff, "insufficient_probe_timestamp_resolution")
    require(all(b > a and not after(b, a + gap) for a, b in zip(times, times[1:])), "sample_gap_or_duplicate")


def _audit_probe(packet: dict[str, Any], trace: Path | None = None) -> dict[str, Any]:
    require(packet.get("kind") == "timelearner_native_probe_evidence" and
            packet.get("evidence_schema_version") in (1, 2), "unknown_native_evidence_schema")
    status = packet["native_status"]
    require(status in {"idle", "queued", "running", "completed", "rejected", "cancelled"}, "unknown_native_status")
    observation = packet["observation"]
    requested = packet.get("requested_specification")
    if observation is None:
        require(status != "completed", "completed_without_observation")
        return {"valid_observation": False, "trace_checked": False,
                "trial_id": requested["trial_id"] if requested else None, "native_status": status,
                "reason": "missing_observation", "evaluation_verdict": None}
    spec = observation["specification"]
    require(observation["schema_version"] == spec["schema_version"] == 3, "unsupported_observation_schema")
    require(spec["time_frame"] == "absolute_model_time", "unknown_observation_time_frame")
    require(type(observation["complete"]) is bool and type(observation["valid"]) is bool, "invalid_validity_flags")
    begin, end = number(spec["begin"]), number(spec["end"])
    require(end > begin and bool(spec["run_id"]) and bool(spec["trial_id"]), "invalid_probe_identity_or_window")
    valid = status == "completed" and observation["complete"] and observation["valid"]
    if not valid:
        return {"valid_observation": False, "trace_checked": False,
                "trial_id": spec["trial_id"], "native_status": status,
                "reason": "incomplete_observation" if not observation["complete"] else "invalid_observation",
                "evaluation_verdict": None}
    require(not packet["reasons"] and not observation["reasons"] and
            not packet["requires_fresh_verification"], "contradictory_validity")
    require(spec["wave_assignment"] == "ordered_whole_burst", "unsupported_wave_assignment")
    if packet["evidence_schema_version"] == 1:
        require("peak_selection" not in spec and (requested is None or "peak_selection" not in requested),
                "unknown_peak_selection_for_legacy_evidence")
        selection = "isolated_window"
    else:
        selection = spec.get("peak_selection")
        require(selection in {"isolated_window", "assigned_burst_wave"} and requested is not None and
                requested.get("peak_selection") == selection, "unknown_or_changed_peak_selection")
    require(number(spec["minimum_amplitude"]) > 0, "invalid_minimum_amplitude")
    require(requested is not None and requested["time_frame"] == "relative_to_trial_start" and
            number(requested["begin"]) == 0 and equal(end, begin + number(requested["end"])), "requested_window_mismatch")
    for key in ("schema_version", "run_id", "trial_id", "sample_id", "pattern_hash", "maximum_samples",
                "maximum_sample_gap", "minimum_amplitude", "record_spikes", "expected_stimulus_ids", "wave_assignment"):
        require(requested[key] == spec[key], "requested_specification_mismatch:" + key)
    profile = spec["stimulus_profile"]
    require(profile is not None and bool(profile["generator_class"]) and number(profile["frequency_hz"]) > 0 and
            number(profile["amplitude"]) > 0 and number(profile["pulse_length"]) >= 1 / number(profile["frequency_hz"]) and
            number(profile["frequency_deviation"]) == 0 and profile["use_transit_signal"] is False and
            profile["use_pattern_output"] is False, "unsupported_stimulus_profile")
    require(requested["stimulus_profile"] is None or requested["stimulus_profile"] == profile, "requested_profile_mismatch")
    prepared = packet["prepared"]
    require(prepared is not None, "missing_prepared_context")
    require(prepared["effective_model_revision"] == spec["effective_model_revision"] and
            packet["current_base_revision"] == prepared["base_model_revision"], "revision_mismatch")
    require(bool(prepared["base_model_revision"]) and bool(prepared["protocol_revision"]), "missing_revision")
    baseline = [number(value) for value in spec["baseline"]]
    require(bool(baseline), "missing_baseline")
    ids = spec["expected_stimulus_ids"]
    require(bool(ids) and len(set(ids)) == len(ids) and all(ids), "duplicate_or_missing_stimulus_id")
    events = observation["stimuli"]
    require([event["id"] for event in events] == ids, "stimulus_set_or_order_mismatch")
    event_times = [number(event["time"]) for event in events]
    require(all(b > a for a, b in zip(event_times, event_times[1:])), "nonmonotonic_stimuli")
    require(all(not after(begin, value) and not after(value, end) for value in event_times), "stimulus_outside_window")
    for event in events:
        require(equal(event["relative_to_trial_start"], number(event["time"]) - begin), "relative_stimulus_time_mismatch")
    windows = spec["windows"]
    require(bool(windows) and len({w["input_id"] for w in windows}) == len(windows), "duplicate_or_missing_input_window")
    require(prepared["input_id"] in {w["input_id"] for w in windows}, "prepared_input_not_measured")
    require(len(requested["windows"]) == len(windows), "requested_window_count_mismatch")
    for expected, actual in zip(requested["windows"], windows):
        require(all(expected[key] == actual[key] for key in ("input_id", "stimulus_id", "channel")) and
                equal(number(expected["begin"]) + begin, actual["begin"]) and
                equal(number(expected["end"]) + begin, actual["end"]), "requested_peak_window_mismatch")
    peaks = {peak["input_id"]: peak for peak in observation["peaks"]}
    require(len(peaks) == len(observation["peaks"]) == len(windows), "peak_window_set_mismatch")
    assignments = {count(item["channel"]): item for item in observation["burst_assignments"]}
    channels = {count(w["channel"]) for w in windows}
    require(len(assignments) == len(observation["burst_assignments"]) and set(assignments) == channels,
            "assignment_channel_set_mismatch")
    for channel, assignment in assignments.items():
        require(channel < len(baseline) and assignment["validity"] == "valid", "invalid_assignment")
        waves = assignment["waves"]
        require([wave["stimulus_id"] for wave in waves] == ids, "wave_stimulus_order_mismatch")
        previous = None
        for event_time, wave in zip(event_times, waves):
            start, finish = number(wave["time"]), number(wave["plateau_end"])
            require(finish >= start and not after(event_time, start) and not after(finish, end), "invalid_wave_time")
            require(previous is None or start > previous, "overlapping_wave_plateaus")
            require(equal(wave["amplitude"], number(wave["raw_potential"]) - baseline[channel]), "wave_amplitude_mismatch")
            require(number(wave["amplitude"]) >= number(spec["minimum_amplitude"]), "unmeasurable_wave")
            previous = finish
    for window in windows:
        peak = peaks[window["input_id"]]
        require(peak["validity"] == "valid" and count(peak["candidate_count"]) == 1, "invalid_peak")
        index = ids.index(window["stimulus_id"])
        channel = count(window["channel"])
        require(peak["stimulus_id"] == window["stimulus_id"], "peak_stimulus_mismatch")
        wave = assignments[channel]["waves"][index]
        for key in ("amplitude", "raw_potential", "time", "plateau_end"):
            require(equal(peak[key], wave[key]), "peak_wave_mismatch:" + key)
        require(number(window["begin"]) < number(peak["time"]) <= number(peak["plateau_end"]) < number(window["end"]), "clipped_peak")
        require(equal(peak["delay_from_stimulus"], number(peak["time"]) - event_times[index]), "peak_delay_mismatch")
        require(equal(peak["relative_to_trial_start"], number(peak["time"]) - begin), "relative_peak_time_mismatch")
        if prepared["routing"] == "classic_burst":
            require(channel == index and prepared["selected_input_index"] is None, "classic_channel_mismatch")
        else:
            require(prepared["routing"] == "branch_solo_burst" and channel == 0 and
                    count(prepared["selected_input_index"]) == index, "branch_selector_mismatch")
    require(type(spec["record_spikes"]) is bool, "invalid_spike_policy")
    if spec["record_spikes"]:
        require(count(observation["spike_count"]) == len(observation["spikes"]), "spike_count_mismatch")
        seen_spikes: set[tuple[int, float]] = set()
        previous = None
        for spike in observation["spikes"]:
            channel, time = count(spike["channel"]), number(spike["time"])
            require(channel < len(baseline) and not after(begin, time) and not after(time, end), "invalid_spike")
            require(previous is None or time >= previous, "nonmonotonic_spikes")
            require((channel, time) not in seen_spikes, "duplicate_spike")
            require(equal(spike["relative_to_trial_start"], time - begin), "relative_spike_time_mismatch")
            seen_spikes.add((channel, time))
            previous = time
    else:
        require(observation["spike_count"] is None and not observation["spikes"], "unknown_spikes_became_zero")
    require(trace is not None, "missing_primary_trace")
    with trace.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    require(bool(rows) and rows[0] == ["time", "stimulus"] + [f"soma{i}" for i in range(len(baseline))], "unknown_trace_schema")
    require(all(len(row) == len(rows[0]) for row in rows[1:]), "ragged_trace")
    try:
        values = [[float(token) for token in row] for row in rows[1:]]
    except ValueError as error:
        raise EvidenceError("damaged_numeric_token") from error
    require(all(math.isfinite(value) for row in values for value in row), "nonfinite_trace")
    times = [row[0] for row in values]
    require_primary_trace_clock(spec, observation["sample_count"], times)

    def at(time: float) -> list[float]:
        index = bisect.bisect_left(times, time)
        matches = [i for i in (index - 1, index) if 0 <= i < len(times) and equal(times[i], time)]
        require(len(matches) == 1, "timestamp_missing_or_ambiguous_in_trace")
        return values[matches[0]]

    for event_time in event_times:
        require(at(event_time)[1] > 0, "stimulus_timestamp_not_observed")
    for channel, assignment in assignments.items():
        signal = [row[channel + 2] - baseline[channel] for row in values]
        minimum = number(spec["minimum_amplitude"])
        require(not (signal[0] >= minimum and signal[0] >= signal[1]) and
                not (signal[-1] >= minimum and signal[-1] >= signal[-2]), "clipped_trace_wave")
        measured_waves = measured_wave_plateaus(signal, minimum)
        require(len(measured_waves) == len(assignment["waves"]), "trace_wave_count_mismatch")
        for wave, (first, last) in zip(assignment["waves"], measured_waves):
            require(equal(wave["time"], times[first]) and equal(wave["plateau_end"], times[last]),
                    "wave_is_not_the_measured_trace_maximum")
            require(equal(at(number(wave["time"]))[channel + 2], wave["raw_potential"]), "raw_peak_trace_mismatch")
            require(equal(at(number(wave["plateau_end"]))[channel + 2], wave["raw_potential"]), "plateau_trace_mismatch")
    # Both policies require actual samples around the selected plateau.
    # Only explicit assigned_burst_wave permits several maxima in a window.
    for window in windows:
        channel = count(window["channel"])
        indices = [i for i, time in enumerate(times)
                   if not after(number(window["begin"]), time) and not after(time, number(window["end"]))]
        require(len(indices) >= 3, "incomplete_peak_window")
        peak = peaks[window["input_id"]]
        if selection == "assigned_burst_wave":
            first = next((i for i in indices if equal(times[i], peak["time"])), None)
            finish = next((i for i in indices if equal(times[i], peak["plateau_end"])), None)
            require(first is not None and finish is not None and
                    first - 1 in indices and finish + 1 in indices, "clipped_assigned_wave")
            continue
        signal = [values[i][channel + 2] - baseline[channel] for i in indices]
        maximum = max(range(len(signal)), key=signal.__getitem__)
        last = maximum
        while last + 1 < len(signal) and signal[last + 1] == signal[maximum]:
            last += 1
        require(maximum > 0 and last + 1 < len(signal), "clipped_window_maximum")
        candidates, index = 0, 1
        while index + 1 < len(signal):
            finish = index
            while finish + 1 < len(signal) and signal[finish + 1] == signal[index]:
                finish += 1
            if finish + 1 < len(signal) and signal[index] >= number(spec["minimum_amplitude"]) and signal[index] > signal[index - 1] and signal[finish] > signal[finish + 1]:
                candidates += 1
            index = finish + 1
        require(candidates == 1, "ambiguous_isolated_peak_window")
        require(equal(times[indices[maximum]], peak["time"]) and equal(times[indices[last]], peak["plateau_end"]),
                "isolated_window_peak_mismatch")
    return {"valid_observation": True, "trace_checked": True, "trial_id": spec["trial_id"],
            "sample_count": len(values), "native_status": status, "evaluation_verdict": None}


def audit_probe(packet: dict[str, Any], trace: Path | None = None) -> dict[str, Any]:
    try:
        return _audit_probe(packet, trace)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError, ValueError, OverflowError) as error:
        raise EvidenceError("malformed_native_evidence:" + str(error)) from error


def validate_search_history_availability(summary: dict[str, Any]) -> bool | None:
    """Absent legacy marker means unknown, never a fabricated retained search."""
    retained = summary.get("search_history_retained")
    if "search_history_retained" in summary:
        require(type(retained) is bool, "invalid_search_history_marker")
    if summary.get("schema_version") in (2, 3, 4):
        require(type(summary.get("candidate_repeat_groups")) is list, "invalid_candidate_repeat_groups")
    if retained is False:
        require(all(summary[name] == [] for name in ("candidates", "rejections", "resistance_domains")) and
                not any(name in summary for name in ("accepted_parameters", "search_probes", "applied_edits")),
                "unretained_search_contains_history")
        require(not summary.get("candidate_repeat_groups"), "unretained_search_contains_repeat_groups")
    return retained


def validate_configured_repeat_policy(configuration: dict[str, Any], summary: dict[str, Any]) -> int:
    """Bind the declared repeat factor to evidence, without replacing the native codec."""
    from .candidate_recovery import bind_recovery_policy
    configuration, summary = bind_recovery_policy(configuration, summary)
    schema = configuration.get("schema_version")
    require(configuration.get("kind") == "timelearner_native_cold_configuration" and
            type(schema) is int and schema in (1, 2, 3, 4), "unknown_repeat_configuration_schema")
    require(type(summary.get("schema_version")) is int and summary["schema_version"] == schema,
            "configuration_summary_repeat_schema_mismatch")
    search, measured = configuration["search"], summary["configuration"]
    if schema == 4:
        from .capacitance_policy import audit_capacitance_search_policy
        policy = configuration.get('capacitance_search')
        require(policy == measured.get('capacitance_search'), 'configuration_summary_capacitance_search_mismatch')
        audit_capacitance_search_policy(policy, configuration=search)
    else:
        require('capacitance_search' not in configuration and 'capacitance_search' not in measured,
                'unversioned_configured_capacitance_search')
    normalization = configuration["model"]["normalization"]
    require(normalization in ("N0", "N1") and
            measured["normalization"] == {"N0": "synapse_count", "N1": "tip_resistance"}[normalization],
            "configuration_summary_normalization_mismatch")
    if schema == 1:
        require("n0_candidate_repeats" not in search and "n0_candidate_repeats" not in measured,
                "legacy_configuration_contains_repeat_factor")
        return 1
    repeats = count(search["n0_candidate_repeats"])
    if schema in (3, 4):
        history = configuration.get('capacitance_history'); source = summary.get('capacitance_history')
        require(type(history) is dict and set(history) == {'record', 'maximum_relative_change'}
                and history['record'] is True and number(history['maximum_relative_change']) >= 0,
                'invalid_configured_capacitance_history')
        require(type(source) is dict and type(source.get('witnesses')) is dict and
                type(source.get('capture_witness_id')) is str and source['capture_witness_id'] in source['witnesses'],
                'missing_configured_capacitance_capture')
        capture = source['witnesses'][source['capture_witness_id']]
        if schema == 4:
            audit_capacitance_search_policy(policy, maximum_relative_change=history['maximum_relative_change'])
        require(history['maximum_relative_change'] == capture['controller_parameters']['maximum_relative_change']
                and 1 <= repeats <= 128 and (normalization == 'N0' or repeats == 1)
                and count(measured['n0_candidate_repeats']) == repeats, 'configuration_summary_capacitance_policy_mismatch')
        return repeats
    require(normalization == "N0" and 2 <= repeats <= 128 and
            count(measured["n0_candidate_repeats"]) == repeats, "configuration_summary_repeat_policy_mismatch")
    return repeats


def measured_training_probe(packets, trial, input_id, origin_stimulus_id, selections):
    """Shared measured arrival relative to the declared whole-burst origin."""
    require(trial in packets, "missing_trial:" + trial)
    packet = packets[trial]
    observation = packet["observation"]
    require(packet["native_status"] == "completed" and isinstance(observation, dict) and
            observation["complete"] is True and observation["valid"] is True, "unusable_measurement")
    selection = observation["specification"].get("peak_selection", "isolated_window")
    require(selection in {"isolated_window", "assigned_burst_wave"}, "unknown_peak_selection")
    selections.add(selection)
    require(len(selections) == 1, "training_peak_selection_changed")
    require(packet["prepared"]["input_id"] == input_id, "measured_input_mismatch")
    peaks = [p for p in observation["peaks"] if p["input_id"] == input_id]
    origins = [event for event in observation["stimuli"] if event["id"] == origin_stimulus_id]
    require(len(peaks) == len(origins) == 1 and peaks[0]["validity"] == "valid", "missing_peak_or_protocol_origin")
    peak, origin = peaks[0], number(origins[0]["time"])
    return packet, number(peak["raw_potential"]), number(peak["time"]) - origin, number(peak["plateau_end"]) - origin


def _audit_training_summary(summary: dict[str, Any], packets: dict[str, dict[str, Any]],
                           origin_stimulus_id: str, *, require_certificate: bool = True) -> dict[str, Any]:
    """Compare exported certificate/candidates with independently audited probes.

    The caller supplies the declared protocol origin; row position is not a
    target/anchor label. ``packets`` contains unique trial IDs from this attempt.
    This checks a training certificate, never recognition/selectivity success.
    """
    schema = summary.get("schema_version")
    require(summary.get("kind") == "native_training_state_summary" and type(schema) is int and schema in (1, 2),
            "unknown_training_summary_schema")
    if schema == 1:
        require("candidate_repeat_groups" not in summary and "n0_candidate_repeats" not in summary["configuration"],
                "repeat_policy_requires_summary_schema_2")
    require(summary["contains_evaluation_verdict"] is False and (summary["model_state_kind"] == "learned_solo" or
            (not require_certificate and summary["model_state_kind"] == "diagnostic")),
            "unsupported_summary_state_kind")
    history_retained = validate_search_history_availability(summary)
    refs = summary["references"]
    require(bool(refs) and len({r["input_id"] for r in refs}) == len(refs), "duplicate_or_missing_reference")
    targets: dict[str, float] = {}
    indices: dict[int, str] = {}
    selections: set[str] = set()

    def measured(trial: str, input_id: str) -> tuple[dict[str, Any], float, float, float]:
        return measured_training_probe(packets, trial, input_id, origin_stimulus_id, selections)

    for ref in refs:
        input_id = ref["input_id"]
        packet, raw, _, _ = measured(ref["trial_id"], input_id)
        observation, prepared = packet["observation"], packet["prepared"]
        require(observation["specification"]["run_id"] == ref["run_id"] and
                prepared["effective_model_revision"] == ref["effective_model_revision"] and
                prepared["base_model_revision"] == summary["reference_model_revision"] and
                count(prepared["model_epoch"]) == count(summary["reference_model_epoch"]), "reference_context_mismatch")
        require(equal(raw, ref["raw_potential"]), "reference_raw_potential_mismatch")
        windows = [w for w in observation["specification"]["windows"] if w["input_id"] == input_id]
        require(len(windows) == 1, "missing_reference_window")
        index = observation["specification"]["expected_stimulus_ids"].index(windows[0]["stimulus_id"])
        require(index not in indices, "duplicate_physical_reference_index")
        indices[index], targets[input_id] = input_id, raw
    require(set(indices) == set(range(len(refs))), "incomplete_physical_reference_order")
    anchor_id = indices[len(refs) - 1]
    tolerances = summary["tolerances"]
    absolute, relative, sync = (number(tolerances[key]) for key in ("amplitude_absolute", "amplitude_relative", "sync"))
    require(min(absolute, relative, sync) >= 0, "negative_tolerance")

    def check_residual(item: dict[str, Any], input_id: str, trial: str, anchor_trial: str) -> bool:
        packet, raw, arrival, end = measured(trial, input_id)
        anchor_packet, _, anchor_arrival, anchor_end = measured(anchor_trial, anchor_id)
        require(packet["prepared"]["base_model_revision"] == anchor_packet["prepared"]["base_model_revision"] and
                packet["prepared"]["model_epoch"] == anchor_packet["prepared"]["model_epoch"], "stale_anchor_probe")
        error, low, high = raw - targets[input_id], arrival - anchor_end, end - anchor_arrival
        tolerance = absolute + relative * abs(targets[input_id])
        require(math.isfinite(tolerance), "nonfinite_amplitude_tolerance")
        require(equal(item["amplitude_residual"], error) and equal(item["timing_low"], low) and
                equal(item["timing_high"], high), "residual_not_derived_from_measurement")
        within_amp, within_time = abs(error) <= tolerance, max(abs(low), abs(high)) <= sync
        require(item["within_amplitude"] is within_amp and item["within_timing"] is within_time, "residual_flag_mismatch")
        return within_amp and within_time

    certificate = summary["certificate"]
    if certificate is None:
        require(not require_certificate and summary["certificate_matches_actual_model"] is False
                and summary["outcome"] != "exact", "missing_or_unknown_certificate")
        exact = None
    else:
        require(certificate is not None and certificate["schema_version"] == 1, "missing_or_unknown_certificate")
        require(certificate.get("peak_selection", "isolated_window") in selections, "certificate_peak_selection_mismatch")
        require(certificate["model_revision"] == summary["actual_model_revision"] and
                certificate["model_epoch"] == summary["model_epoch"] and
                certificate["reference_model_revision"] == summary["reference_model_revision"] and
                certificate["reference_model_epoch"] == summary["reference_model_epoch"], "certificate_model_binding_mismatch")
        require(summary["certificate_matches_actual_model"] is True, "certificate_failed_native_binding_check")
        residuals = {r["input_id"]: r for r in certificate["residuals"]}
        require(len(residuals) == len(certificate["residuals"]) and set(residuals) == set(targets), "incomplete_certificate_residuals")
        exact = True
        for input_id, residual in residuals.items():
            packet, raw, _, _ = measured(residual["trial_id"], input_id)
            prepared = packet["prepared"]
            require(prepared["base_model_revision"] == certificate["model_revision"] and
                    prepared["model_epoch"] == certificate["model_epoch"] and
                    prepared["effective_model_revision"] == residual["effective_model_revision"] and
                    prepared["protocol_revision"] == certificate["protocol_revision"], "final_probe_context_mismatch")
            require(equal(residual["measured_raw_potential"], raw) and
                    equal(residual["target_raw_potential"], targets[input_id]) and
                    equal(residual["amplitude_tolerance"], absolute + relative * abs(targets[input_id])), "certificate_amplitude_mismatch")
            exact = check_residual(residual, input_id, residual["trial_id"], residuals[anchor_id]["trial_id"]) and exact
        require(certificate["exact"] is exact, "certificate_exact_mismatch")
        require((summary["outcome"] == "exact") == exact, "outcome_certificate_mismatch")
    # Restored model boundaries carry reference/final proof and actual graph
    # parameters, not an accepted search snapshot. All proof, bounds and primary
    # measurement checks still apply; missing history is never called measured.
    if history_retained is not False:
        require("accepted_parameters" in summary, "missing_retained_search_parameters")
        require(summary["actual_parameters"] == summary["accepted_parameters"], "accepted_actual_parameters_mismatch")
    configuration = summary["configuration"]
    bounds = configuration["bounds"]
    require(len(bounds) == len(summary["actual_parameters"]) == len(refs), "parameter_dimension_mismatch")
    require(configuration["normalization"] in {"synapse_count", "tip_resistance"}, "unknown_normalization")

    def parameters_legal(parameters: dict[str, Any], index: int) -> None:
        bound = bounds[index]
        length, synapses, resistance = count(parameters["length"]), count(parameters["synapses"]), number(parameters["resistance"])
        require(count(bound["minimum_length"]) <= length <= count(bound["maximum_length"]) and length >= 1,
                "length_outside_search_domain")
        require(1 <= synapses <= 128 and count(bound["minimum_synapses"]) <= synapses <= count(bound["maximum_synapses"]),
                "synapses_outside_search_domain")
        require(0 < number(bound["minimum_resistance"]) <= resistance <= number(bound["maximum_resistance"]),
                "resistance_outside_search_domain")
        require(configuration["normalization"] != "tip_resistance" or synapses == 1, "parametric_bank_has_multiple_synapses")

    for index, parameters in enumerate(summary["actual_parameters"]):
        parameters_legal(parameters, index)
    for candidate in summary["candidates"]:
        index = count(candidate["input_index"])
        require(index in indices and index + 1 < len(refs), "unknown_or_fixed_candidate_input")
        parameters_legal(candidate["parameters"], index)
        packet, _, _, _ = measured(candidate["trial_id"], indices[index])
        require(packet["prepared"]["base_model_revision"] == candidate["model_revision"] and
                packet["prepared"]["model_epoch"] == candidate["model_epoch"], "candidate_context_mismatch")
        check_residual(candidate, indices[index], candidate["trial_id"], candidate["anchor_trial_id"])
        require(number(candidate["parameter_change_cost"]) >= 0, "invalid_candidate_change_cost")
    if schema == 2:
        repeats = count(configuration["n0_candidate_repeats"])
        require(configuration["normalization"] == "synapse_count" and 2 <= repeats <= 128,
                "invalid_n0_repeat_policy")
        candidates = {c["trial_id"]: c for c in summary["candidates"]}
        require(len(candidates) == len(summary["candidates"]), "duplicate_candidate_trial")
        covered, anchors_used = set(), set()
        for group in summary["candidate_repeat_groups"]:
            require(type(group) is dict and set(group) == {"input_index", "model_epoch", "model_revision", "full_parameters",
                    "trial_ids", "anchor_trial_ids", "minimum_raw_potential", "maximum_raw_potential", "within_timing",
                    "within_amplitude", "raw_potentials", "valid", "complete", "reason"}, "unknown_candidate_repeat_fields")
            require(group["valid"] is True and type(group["complete"]) is bool and type(group["reason"]) is str
                    and bool(group["reason"]), "invalid_candidate_repeat_status")
            trials, anchors, values = group["trial_ids"], group["anchor_trial_ids"], group["raw_potentials"]
            require(type(trials) is type(anchors) is type(values) is list and
                    len(trials) == len(anchors) == len(values) and 0 < len(trials) <= repeats,
                    "invalid_candidate_repeat_dimensions")
            require(len(trials) == repeats if group["complete"] else len(trials) < repeats,
                    "candidate_repeat_completeness_mismatch")
            require(not group["complete"] or group["reason"] == "required_measurements_collected",
                    "invalid_complete_repeat_reason")
            require(len(set(trials)) == len(trials) and len(set(anchors)) == len(anchors)
                    and not covered.intersection(trials) and not anchors_used.intersection(anchors), "reused_candidate_repeat_trial")
            index = count(group["input_index"])
            count(group["model_epoch"])
            require(all(type(t) is str and t for t in trials+anchors), "invalid_candidate_repeat_trial_id")
            require(index in indices and index + 1 < len(refs) and len(group["full_parameters"]) == len(refs),
                    "invalid_candidate_repeat_input")
            for i, parameters in enumerate(group["full_parameters"]):
                parameters_legal(parameters, i)
            expected_raw, timing_flags, amplitude_flags = [], [], []
            for trial, anchor_trial, value in zip(trials, anchors, values):
                require(trial in candidates, "repeat_trial_not_in_candidates")
                candidate = candidates[trial]
                require(candidate["input_index"] == index and candidate["model_epoch"] == group["model_epoch"]
                        and candidate["model_revision"] == group["model_revision"]
                        and candidate["full_parameters"] == group["full_parameters"]
                        and candidate["anchor_trial_id"] == anchor_trial, "candidate_repeat_context_mismatch")
                _, raw, _, _ = measured(trial, indices[index])
                require(equal(value, raw), "candidate_repeat_raw_not_measured")
                expected_raw.append(raw);timing_flags.append(candidate["within_timing"]);amplitude_flags.append(candidate["within_amplitude"])
            require(equal(group["minimum_raw_potential"], min(expected_raw)) and
                    equal(group["maximum_raw_potential"], max(expected_raw)), "candidate_repeat_range_mismatch")
            require(group["within_timing"] is all(timing_flags) and group["within_amplitude"] is all(amplitude_flags),
                    "candidate_repeat_residual_flags_mismatch")
            covered.update(trials);anchors_used.update(anchors)
        require(covered == set(candidates), "candidate_repeat_coverage_incomplete")
    repeat_validation = ({"training_summary_schema": 2, "candidate_repeat_groups_checked": len(summary["candidate_repeat_groups"])}
                         if schema == 2 else {})
    return {"auditor_version": AUDITOR_VERSION, "certificate_consistent": certificate is not None, "exact": exact, **repeat_validation,
            "search_history_retained": history_retained,
            "model_revision": certificate["model_revision"] if certificate is not None else summary["actual_model_revision"], "reference_count": len(refs),
            "candidate_count": len(summary["candidates"]), "evaluation_verdict": None}


def audit_training_summary(summary: dict[str, Any], packets: dict[str, dict[str, Any]],
                           origin_stimulus_id: str, *, require_certificate: bool = True,
                           traces: dict[str, Path] | None = None, protocol: dict[str, Any] | None = None) -> dict[str, Any]:
    """Audit physical C contexts before reusing the measured residual validator."""
    from .candidate_recovery import RETRY_MODE, project_recovery_summary
    projected, recovery_mode = project_recovery_summary(summary)
    if recovery_mode != RETRY_MODE:
        require(type(traces) is dict and type(protocol) is dict and
                protocol.get("origin_stimulus_id") == origin_stimulus_id and set(traces) == set(packets),
                "candidate_recovery_primary_context_required")
        from .candidate_recovery_history import audit_recovery_history
        from .probe_diagnostics import read_partial_probe
        search_trials = reference_trials = 0
        run_id = summary["configuration"]["run_id"]
        reference_ids = {r["trial_id"] for r in summary["references"]}
        for trial, packet in packets.items():
            require(type(packet) is dict and type(packet.get("requested_specification")) is dict and
                    type(trial) is str and trial and packet["requested_specification"].get("trial_id") == trial and
                    isinstance(traces[trial], Path), "recovery_primary_trial_mismatch")
            requested_run = packet["requested_specification"]["run_id"]
            require(type(requested_run) is str and requested_run, "recovery_primary_run_missing")
            if requested_run == run_id or requested_run.startswith(run_id+"/final/"):
                search_trials += 1
            elif requested_run.startswith(run_id+"/capture/"):
                reference_trials += 1
            elif require_certificate and summary["search_history_retained"]:
                require(trial in reference_ids, "recovery_contains_unrelated_attempt_primary")
            primary = audit_probe(packet, traces[trial])
            if not primary["valid_observation"]:
                _, _, _, _, _, quality = read_partial_probe(packet, traces[trial])
                if require_certificate:
                    require(quality["recorded_window_complete"] and not quality["nonfinite_cells"],
                            "completed_recovery_contains_incomplete_or_nonfinite_primary")
        if require_certificate and summary["search_history_retained"]:
            # Old captured references can be reused by a declared warm attempt.
            # Count current search/final and current capture separately; never
            # infer completeness from the subset that produced candidates.
            require(search_trials == count(summary["search_probes"]) and
                    reference_trials == count(summary["reference_probes"]),
                    "recovery_primary_attempt_coverage_mismatch")
        recovery = audit_recovery_history(summary, packets, traces, protocol)
        measured = audit_training_summary(projected, packets, origin_stimulus_id,
                                          require_certificate=require_certificate)
        return {**measured, "auditor_version": 8, "training_summary_schema": 5,
                "base_training_summary_schema": projected["schema_version"], "candidate_recovery": recovery}
    version = summary.get('schema_version')
    require(type(version) is int and version in (1, 2, 3, 4), 'unknown_training_summary_schema')
    c_fields = {'capacitance_history', 'actual_capacitance_witness_id', 'accepted_capacitance'}
    require(type(summary.get('configuration')) is dict, 'missing_training_summary_configuration')
    if version != 4:
        require('capacitance_search' not in summary['configuration'], 'unversioned_training_capacitance_search')
    if version not in (3, 4):
        require(not c_fields.intersection(summary) and
                all('capacitance_witness_id' not in r for r in summary.get('references', [])) and
                all(not {'capacitance', 'capacitance_witness_id'}.intersection(c)
                    for c in summary.get('candidates', [])) and
                all(not {'capacitance', 'capacitance_witness_ids', 'anchor_capacitance_witness_ids'}.intersection(g)
                    for g in summary.get('candidate_repeat_groups', [])) and
                all(d.get('schema_version') != 3 for d in summary.get('resistance_domains', [])),
                'unversioned_training_summary_capacitance')
        return _audit_training_summary(summary, packets, origin_stimulus_id, require_certificate=require_certificate)
    from .training_capacitance_history import audit_training_capacitance_history
    import copy
    physical = audit_training_capacitance_history(summary, packets)
    if version == 4:
        from .capacitance_policy import audit_capacitance_search_policy
        source = summary['capacitance_history'];capture = source['witnesses'][source['capture_witness_id']]
        audit_capacitance_search_policy(summary['configuration'].get('capacitance_search'),
            maximum_relative_change=capture['controller_parameters']['maximum_relative_change'],
            configuration=summary['configuration'])
    require(physical['actual_state_verified'], 'unverified_training_summary_actual_capacitance')
    projected = copy.deepcopy(summary)
    if version == 4:projected['configuration'].pop('capacitance_search')
    for field in c_fields:
        projected.pop(field, None)
    for r in projected['references']:
        r.pop('capacitance_witness_id')
    for candidate in projected['candidates']:
        candidate.pop('capacitance');candidate.pop('capacitance_witness_id')
    for group in projected['candidate_repeat_groups']:
        for field in ('capacitance', 'capacitance_witness_ids', 'anchor_capacitance_witness_ids'):
            group.pop(field)
    repeats = count(projected['configuration']['n0_candidate_repeats'])
    projected['schema_version'] = 2 if repeats > 1 else 1
    if repeats == 1:
        require(projected['candidate_repeat_groups'] == [], 'unexpected_single_repeat_groups')
        projected.pop('candidate_repeat_groups');projected['configuration'].pop('n0_candidate_repeats')
    measured = _audit_training_summary(projected, packets, origin_stimulus_id, require_certificate=require_certificate)
    return {**measured, 'training_summary_schema': version, 'capacitance_history': physical}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe", type=Path)
    parser.add_argument("--trace", type=Path)
    args = parser.parse_args()
    print(json.dumps({"auditor_version": AUDITOR_VERSION, **audit_probe(load(args.probe), args.trace)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
