"""Strict full-window recognition observations; consistency is not execution proof.

The native run/runtime and source training evidence are audited separately.
Silence is a valid response. No training/convergence/selectivity PASS is inferred.
"""
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, count, equal, number, require

FIELDS = {"kind", "schema_version", "run_id", "trial_id", "sample_id", "label", "pattern_hash",
          "pattern_isi", "reset_policy", "frequency_hz", "begin", "end", "closed_at", "maximum_samples",
          "model_before", "model_after", "armed", "complete", "censored", "valid", "reason", "stimulus_onset",
          "stimulus_times", "spike_times", "relative_stimulus_times", "relative_spike_times", "spike_count",
          "samples", "evaluation_verdict"}


def _events(values, begin, closed):
    require(type(values) is list, "recognition_events_not_array")
    result = [number(value) for value in values]
    require(all(not after(begin, value) and not after(value, closed) for value in result)
            and all(b > a for a, b in zip(result, result[1:])), "invalid_recognition_event_times")
    return result


def audit_recognition_trial(observation, package):
    try:
        o = observation
        require(type(package) is dict, "unsupported_trial_model_package")
        candidate = package.get("kind") == "timelearner_recognition_threshold_candidate"
        if candidate:
            from .threshold_candidate_evidence import audit_threshold_candidate
            audit_threshold_candidate(package)
        context = package["source_recognition"] if candidate else package
        require(set(o) == FIELDS, "recognition_trial_field_set_mismatch")
        require(o["kind"] == "native_recognition_trial" and type(o["schema_version"]) is int
                and o["schema_version"] == 1, "unknown_recognition_trial_schema")
        require((candidate or package["kind"] == "timelearner_recognition_state") and type(package["schema_version"]) is int
                and package["schema_version"] == 1 and package["state_kind"] == "recognition"
                and package["dynamic_checkpoint"] is False and package["recognition_certificate"] is None,
                "unsupported_trial_model_package")
        require(package["sha256"] == canonical_model_sha256({k: v for k, v in package.items() if k != "sha256"}),
                "recognition_package_digest_mismatch")
        identity = package["neuron"]["graph"]["identity"]
        require(canonical_model_sha256(identity["model"]) == identity["sha256"] == package["model_revision"],
                "recognition_model_digest_mismatch")
        require(o["evaluation_verdict"] is None, "unsupported_trial_verdict")
        for name in ("run_id", "trial_id", "sample_id", "pattern_hash", "reason"):
            require(type(o[name]) is str and bool(o[name]), "invalid_recognition_identity")
        require(o["label"] in ("target", "foil") and o["reset_policy"] in
                ("reset_per_trial", "preserve_neuron_dynamics"), "invalid_recognition_label_or_reset")
        require(type(o["pattern_isi"]) is list and len(o["pattern_isi"]) == len(context["recognition_inputs"])
                and bool(o["pattern_isi"]) and all(number(v) >= 0 for v in o["pattern_isi"]),
                "invalid_recognition_pattern")
        require(canonical_model_sha256(o["pattern_isi"]) == o["pattern_hash"], "recognition_pattern_hash_mismatch")
        for key in ("armed", "complete", "censored", "valid"):
            require(type(o[key]) is bool, "invalid_recognition_boolean")
        require(o["censored"] is (not o["complete"]) and (not o["complete"] or o["armed"])
                and (not o["valid"] or (o["complete"] and o["armed"])), "contradictory_recognition_validity")
        begin, end, closed = (number(o[k]) for k in ("begin", "end", "closed_at"))
        frequency = number(o["frequency_hz"])
        budget = count(o["maximum_samples"])
        require(budget >= 2 and type(o["samples"]) is list and len(o["samples"]) <= budget, "invalid_recognition_budget")
        source_model = context["source_solo"]["configuration"]["model"]
        channels = 1 if source_model["branch"] else len(o["pattern_isi"])
        if o["armed"]:
            require(frequency > 0 and frequency == number(source_model["frequency_hz"]) and end > begin,
                    "invalid_recognition_clock")
        actual_events = {"stimulus_history": [], "spike_history": []}
        watermarks = {key: None for key in actual_events}
        for i, sample in enumerate(o["samples"]):
            require(type(sample) is dict and set(sample) == {"time", "stimulus", "soma", "lt_output", "stimulus_history", "spike_history"},
                    "invalid_recognition_sample_fields")
            time = number(sample["time"]);number(sample["stimulus"]);number(sample["lt_output"])
            for key in actual_events:
                history = sample[key]
                require(type(history) is list, "recognition_history_not_array")
                history = [number(v) for v in history]
                require(all(not after(t, time) for t in history) and all(b > a for a, b in zip(history, history[1:])),
                        "invalid_recognition_raw_history")
                for t in history:
                    if (watermarks[key] is None or t > watermarks[key]) and not after(begin, t):
                        actual_events[key].append(t)
                if history and (watermarks[key] is None or history[-1] > watermarks[key]):
                    watermarks[key] = history[-1]
            require(type(sample["soma"]) is list and len(sample["soma"]) == channels, "invalid_recognition_soma_dimensions")
            for v in sample["soma"]:
                number(v)
            require(o["armed"] and not after(begin, time) and not after(time, end), "recognition_sample_outside_window")
            if i == 0:
                require(equal(time, begin), "recognition_missing_first_sample")
            else:
                previous = number(o["samples"][i-1]["time"])
                require(time > previous and not after(time, previous + 1/frequency), "recognition_sample_gap")
        if o["samples"]:
            require(equal(closed, o["samples"][-1]["time"]), "recognition_closure_mismatch")
        stimuli = _events(o["stimulus_times"], begin, closed)
        spikes = _events(o["spike_times"], begin, closed)
        require(stimuli == actual_events["stimulus_history"] and spikes == actual_events["spike_history"],
                "recognition_events_disagree_with_primary_samples")
        require(count(o["spike_count"]) == len(spikes), "recognition_spike_count_mismatch")
        if stimuli:
            require(equal(o["stimulus_onset"], stimuli[0]), "recognition_onset_mismatch")
            for absolute, relative in ((stimuli, o["relative_stimulus_times"]), (spikes, o["relative_spike_times"])):
                require(type(relative) is list and len(relative) == len(absolute)
                        and all(equal(value, expected-stimuli[0]) for value, expected in zip(relative, absolute)),
                        "recognition_relative_times_mismatch")
        else:
            require(o["stimulus_onset"] is None and o["relative_stimulus_times"] == []
                    and o["relative_spike_times"] == [], "recognition_unknown_onset_mismatch")
        if o["complete"]:
            require(bool(o["samples"]) and equal(closed, end), "incomplete_recognition_window")
        if o["valid"]:
            require(o["reason"] == "window_closed" and o["model_before"] == o["model_after"] == package["model_revision"],
                    "recognition_frozen_model_changed")
            require(len(stimuli) == len(o["pattern_isi"]), "recognition_stimulus_count_mismatch")
            planned = begin
            for isi, actual in zip(o["pattern_isi"], stimuli):
                planned += number(isi)
                require(not after(planned, actual) and not after(actual, planned + 1/frequency),
                        "recognition_stimulus_timestamp_mismatch")
        return {"schema_version": 1, "valid_observation": o["valid"], "complete": o["complete"],
                "run_id": o["run_id"], "trial_id": o["trial_id"], "sample_id": o["sample_id"], "label": o["label"],
                "samples": len(o["samples"]), "spike_count": len(spikes), "reason": o["reason"],
                "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_recognition_trial:" + str(error)) from error


def audit_recognition_trial_set(observations, expected, package):
    """Expected keys are (run_id, trial_id); metadata comes from the job spec."""
    result = {}
    for observation in observations:
        item = audit_recognition_trial(observation, package)
        key = (item["run_id"], item["trial_id"])
        require(key not in result and key in expected, "duplicate_or_unexpected_recognition_trial")
        wanted = expected[key]
        require((item["sample_id"], item["label"], observation["pattern_hash"]) ==
                (wanted["sample_id"], wanted["label"], wanted["pattern_hash"]), "recognition_trial_metadata_mismatch")
        result[key] = item
    require(set(result) == set(expected), "missing_recognition_trial")
    return {"schema_version": 1, "trials": len(result),
            "all_observations_valid": all(item["valid_observation"] for item in result.values()),
            "evaluation_verdict": None}
