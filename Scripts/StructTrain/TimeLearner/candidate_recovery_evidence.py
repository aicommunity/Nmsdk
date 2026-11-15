"""Check an unassigned burst against its actual trace, never accept its peak.

This establishes the observation class only. Whether a controller may advance
also depends on its declared policy, remaining budget and current search phase.
"""
from .native_evidence import EvidenceError, after, count, equal, number, require, require_primary_trace_clock
from .probe_diagnostics import audit_recorded_wave_diagnostics, read_partial_probe


def _audit(packet, trace, protocol):
    require(type(protocol) is dict and type(protocol.get("schema_version")) is int and
            protocol["schema_version"] == 3, "recovery_requires_protocol3")
    inputs, ids = protocol["inputs"], protocol["stimulus_ids"]
    require(type(inputs) is list and type(ids) is list and len(inputs) == len(ids) > 0 and
            all(type(v) is str and v for v in ids) and len(set(ids)) == len(ids) and
            all(type(v) is dict and set(v) == {"id", "stimulus_id"} and
                type(v["id"]) is str and v["id"] and v["stimulus_id"] == ids[i]
                for i, v in enumerate(inputs)) and
            len({v["id"] for v in inputs}) == len(inputs) and protocol["origin_stimulus_id"] in ids,
            "invalid_recovery_protocol_inputs")
    require(all(type(protocol[k]) is str and protocol[k] for k in ("revision", "sample_id", "pattern_hash")),
            "missing_recovery_protocol_identity")
    routing = protocol["routing"]
    require(routing in ("classic_burst", "branch_solo_burst") and
            protocol["wave_assignment"] == "ordered_whole_burst" and
            protocol["peak_selection"] in ("isolated_window", "assigned_burst_wave"),
            "unsupported_recovery_protocol")
    require(number(protocol["maximum_sample_gap"]) > 0 and number(protocol["minimum_amplitude"]) > 0,
            "invalid_recovery_protocol_sampling")
    require(packet["native_status"] == "completed" and packet["reasons"] == [] and
            packet["requires_fresh_verification"] is False, "recovery_native_context_not_completed")
    observation, spec, frequency, samples, channels, quality = read_partial_probe(packet, trace)
    require(observation is not None and observation["valid"] is False and
            observation["complete"] is True and observation["end_reason"] == "window_closed" and
            quality["recorded_window_complete"] and not quality["nonfinite_cells"],
            "recovery_requires_closed_finite_invalid_observation")
    requested, prepared = packet["requested_specification"], packet["prepared"]
    require(prepared["routing"] == routing and prepared["protocol_revision"] == protocol["revision"] and
            prepared["base_model_revision"] == packet["current_base_revision"] and
            bool(prepared["effective_model_revision"]), "recovery_prepared_protocol_mismatch")
    count(prepared["model_epoch"])
    selected = [i for i, v in enumerate(inputs) if v["id"] == prepared["input_id"]]
    require(len(selected) == 1, "recovery_prepared_input_unknown")
    index = selected[0]
    require(channels == (len(inputs) if routing == "classic_burst" else 1) and
            (prepared["selected_input_index"] is None if routing == "classic_burst" else
             count(prepared["selected_input_index"]) == index), "recovery_physical_input_mismatch")
    baseline = [number(v) for v in spec["baseline"]]
    for key in ("maximum_samples", "maximum_sample_gap", "minimum_amplitude", "record_spikes",
                "expected_stimulus_ids", "wave_assignment", "peak_selection"):
        require(requested[key] == spec[key], "recovery_requested_specification_mismatch:"+key)
    require(requested["baseline"] == [] or requested["baseline"] == baseline,
            "recovery_requested_baseline_mismatch")
    require(requested["effective_model_revision"] in ("", spec["effective_model_revision"]),
            "recovery_requested_revision_mismatch")
    require(spec["sample_id"] == protocol["sample_id"] and spec["pattern_hash"] == protocol["pattern_hash"] and
            spec["stimulus_profile"] == protocol["stimulus_profile"] and
            spec["wave_assignment"] == protocol["wave_assignment"] and
            spec["peak_selection"] == protocol["peak_selection"] and
            spec["expected_stimulus_ids"] == ids and
            spec["minimum_amplitude"] == protocol["minimum_amplitude"] and
            not after(number(spec["maximum_sample_gap"]), number(protocol["maximum_sample_gap"])),
            "recovery_observation_protocol_mismatch")
    profile = spec["stimulus_profile"]
    require(type(profile["generator_class"]) is str and profile["generator_class"] and
            number(profile["amplitude"]) > 0 and frequency > 0 and
            number(profile["pulse_length"]) >= 1/frequency and number(profile["frequency_deviation"]) == 0 and
            profile["use_transit_signal"] is False and profile["use_pattern_output"] is False,
            "unsupported_recovery_stimulus_profile")
    begin, end = number(spec["begin"]), number(spec["end"])
    require(len(spec["windows"]) == len(requested["windows"]) == len(observation["peaks"]) ==
            len(observation["burst_assignments"]) == 1, "recovery_requires_one_selected_window")
    window, relative = spec["windows"][0], requested["windows"][0]
    channel = index if routing == "classic_burst" else 0
    require(window["input_id"] == inputs[index]["id"] and window["stimulus_id"] == ids[index] and
            count(window["channel"]) == channel and
            all(relative[k] == window[k] for k in ("input_id", "stimulus_id", "channel")) and
            equal(begin+number(relative["begin"]), window["begin"]) and
            equal(begin+number(relative["end"]), window["end"]) and
            number(window["end"]) > number(window["begin"]) and
            not after(begin, number(window["begin"])) and not after(number(window["end"]), end),
            "recovery_selected_window_mismatch")
    assignment, peak = observation["burst_assignments"][0], observation["peaks"][0]
    validity = assignment["validity"]
    require(validity in ("missing", "ambiguous") and count(assignment["channel"]) == channel and
            peak["input_id"] == window["input_id"] and peak["stimulus_id"] == window["stimulus_id"] and
            peak["validity"] == validity and count(peak["candidate_count"]) == 0 and
            all(peak[k] is None for k in ("amplitude", "raw_potential", "time", "plateau_end",
                                          "delay_from_stimulus", "relative_to_trial_start")),
            "recovery_unassigned_peak_mismatch")
    reasons = observation["reasons"]
    require(type(reasons) is list and len(reasons) == 2 and set(reasons) ==
            {f"burst_{validity}:{channel}", f"peak_{validity}:{inputs[index]['id']}"},
            "recovery_contains_other_failure_causes")
    events = observation["stimuli"]
    require([event["id"] for event in events] == ids, "recovery_stimulus_set_or_order_mismatch")
    event_times = [number(event["time"]) for event in events]
    require(all(b > a for a, b in zip(event_times, event_times[1:])) and
            all(not after(begin, t) and not after(t, end) for t in event_times) and
            all(equal(event["relative_to_trial_start"], t-begin) for event, t in zip(events, event_times)) and
            equal(observation["first_stimulus_time"], event_times[0]), "recovery_stimulus_clock_mismatch")
    times = [number(s["time"]) for s in samples]
    require_primary_trace_clock(spec, observation["sample_count"], times)
    onsets = [s["time"] for i, s in enumerate(samples)
              if number(s["stimulus"]) > 0 and (i == 0 or number(samples[i-1]["stimulus"]) <= 0)]
    require(len(onsets) == len(event_times) and all(equal(a, b) for a, b in zip(onsets, event_times)),
            "recovery_stimulus_trace_mismatch")
    waves = assignment["waves"]
    require(type(waves) is list and len(waves) <= (len(samples)-1)//2 and
            (len(waves) < len(ids) if validity == "missing" else len(waves) >= len(ids)),
            "recovery_wave_count_inconsistent")
    previous = None
    minimum = number(spec["minimum_amplitude"])
    for wave in waves:
        start, finish = number(wave["time"]), number(wave["plateau_end"])
        require(wave["stimulus_id"] == "" and number(wave["amplitude"]) >= minimum and
                equal(wave["amplitude"], number(wave["raw_potential"])-baseline[channel]) and
                finish >= start and not after(begin, start) and not after(finish, end) and
                (previous is None or start > previous) and
                equal(wave["relative_to_trial_start"], start-begin), "recovery_invalid_wave")
        previous = finish
    signal = [number(s["soma"][channel])-baseline[channel] for s in samples]
    require(not (signal[0] >= minimum and signal[0] >= signal[1]) and
            not (signal[-1] >= minimum and signal[-1] >= signal[-2]), "recovery_clipped_trace_wave")
    diagnostic = audit_recorded_wave_diagnostics(observation, spec, samples, quality)
    require(diagnostic["recorded_waves_checked"], "recovery_wave_primary_unavailable")
    return {"unassigned_burst_classified": True, "valid_observation": False, "trace_checked": True,
            "trial_id": spec["trial_id"], "input_index": index, "input_id": inputs[index]["id"],
            "validity": validity, "sample_count": len(samples), "measured_wave_count": len(waves),
            "expected_stimulus_count": len(ids), "model_revision": prepared["base_model_revision"],
            "model_epoch": count(prepared["model_epoch"]), "training_transition_verified": False,
            "certificate_consistent": False, "evaluation_verdict": None}


def audit_unassigned_burst(packet, trace, protocol):
    try:
        return _audit(packet, trace, protocol)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError, ValueError, OverflowError) as error:
        raise EvidenceError("malformed_candidate_recovery_evidence:"+str(error)) from error
