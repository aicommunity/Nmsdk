"""Audit native training evidence against primary traces; no selectivity verdict.

This format is independent of the recognition CSV schemas. It supports the
version-1 C++ ProbeEvidenceJson producer and schema-3 training observations.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

AUDITOR_VERSION = 1


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


def load(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result

    def invalid_constant(token: str) -> None:
        raise EvidenceError("nonfinite_json_token:" + token)

    result = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                        parse_constant=invalid_constant)
    require(isinstance(result, dict), "not_an_object")
    return result


def _audit_probe(packet: dict[str, Any], trace: Path | None = None) -> dict[str, Any]:
    require(packet.get("kind") == "timelearner_native_probe_evidence" and
            packet.get("evidence_schema_version") == 1, "unknown_native_evidence_schema")
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
    require(number(spec["minimum_amplitude"]) > 0, "invalid_minimum_amplitude")
    require(requested is not None and requested["time_frame"] == "relative_to_trial_start" and
            number(requested["begin"]) == 0 and equal(requested["end"], end - begin), "requested_window_mismatch")
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
    require(len(values) == count(observation["sample_count"]) >= 3, "sample_count_mismatch")
    times = [row[0] for row in values]
    gap = number(spec["maximum_sample_gap"])
    require(gap > 0 and count(spec["maximum_samples"]) >= len(values), "invalid_sample_budget")
    require(equal(times[0], begin) and equal(times[-1], end), "incomplete_trace_coverage")
    require(all(b > a and not after(b - a, gap) for a, b in zip(times, times[1:])), "sample_gap_or_duplicate")

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
        measured_waves: list[tuple[int, int]] = []
        index = 1
        while index + 1 < len(signal):
            last = index
            while last + 1 < len(signal) and signal[last + 1] == signal[index]:
                last += 1
            if last + 1 < len(signal) and signal[index] >= minimum and signal[index] > signal[index - 1] and signal[last] > signal[last + 1]:
                measured_waves.append((index, last))
            index = last + 1
        require(len(measured_waves) == len(assignment["waves"]), "trace_wave_count_mismatch")
        for wave, (first, last) in zip(assignment["waves"], measured_waves):
            require(equal(wave["time"], times[first]) and equal(wave["plateau_end"], times[last]),
                    "wave_is_not_the_measured_trace_maximum")
            require(equal(at(number(wave["time"]))[channel + 2], wave["raw_potential"]), "raw_peak_trace_mismatch")
            require(equal(at(number(wave["plateau_end"]))[channel + 2], wave["raw_potential"]), "plateau_trace_mismatch")
    return {"valid_observation": True, "trace_checked": True, "trial_id": spec["trial_id"],
            "sample_count": len(values), "native_status": status, "evaluation_verdict": None}


def audit_probe(packet: dict[str, Any], trace: Path | None = None) -> dict[str, Any]:
    try:
        return _audit_probe(packet, trace)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError, ValueError, OverflowError) as error:
        raise EvidenceError("malformed_native_evidence:" + str(error)) from error


def audit_training_summary(summary: dict[str, Any], packets: dict[str, dict[str, Any]],
                           origin_stimulus_id: str) -> dict[str, Any]:
    """Compare exported certificate/candidates with independently audited probes.

    The caller supplies the declared protocol origin; row position is not a
    target/anchor label. ``packets`` contains unique trial IDs from this attempt.
    This checks a training certificate, never recognition/selectivity success.
    """
    require(summary.get("kind") == "native_training_state_summary" and summary.get("schema_version") == 1,
            "unknown_training_summary_schema")
    require(summary["contains_evaluation_verdict"] is False and summary["model_state_kind"] == "learned_solo",
            "unsupported_summary_state_kind")
    refs = summary["references"]
    require(bool(refs) and len({r["input_id"] for r in refs}) == len(refs), "duplicate_or_missing_reference")
    targets: dict[str, float] = {}
    indices: dict[int, str] = {}

    def measured(trial: str, input_id: str) -> tuple[dict[str, Any], float, float, float]:
        require(trial in packets, "missing_trial:" + trial)
        packet = packets[trial]
        observation = packet["observation"]
        require(packet["native_status"] == "completed" and observation is not None and
                observation["complete"] is True and observation["valid"] is True, "unusable_measurement")
        require(packet["prepared"]["input_id"] == input_id, "measured_input_mismatch")
        peaks = [p for p in observation["peaks"] if p["input_id"] == input_id]
        origins = [event for event in observation["stimuli"] if event["id"] == origin_stimulus_id]
        require(len(peaks) == len(origins) == 1 and peaks[0]["validity"] == "valid", "missing_peak_or_protocol_origin")
        peak, origin = peaks[0], number(origins[0]["time"])
        return packet, number(peak["raw_potential"]), number(peak["time"]) - origin, number(peak["plateau_end"]) - origin

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
    require(certificate is not None and certificate["schema_version"] == 1, "missing_or_unknown_certificate")
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
    return {"auditor_version": AUDITOR_VERSION, "certificate_consistent": True, "exact": exact,
            "model_revision": certificate["model_revision"], "reference_count": len(refs),
            "candidate_count": len(summary["candidates"]), "evaluation_verdict": None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("probe", type=Path)
    parser.add_argument("--trace", type=Path)
    args = parser.parse_args()
    print(json.dumps({"auditor_version": AUDITOR_VERSION, **audit_probe(load(args.probe), args.trace)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
