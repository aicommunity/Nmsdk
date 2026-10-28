"""Verify a transient PostTune stimulus without treating it as a training target."""
from __future__ import annotations

import csv
import math
from pathlib import Path

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, count, equal, load, number, require


def audit_transient_presentation(spec: dict, observation: dict, trace: Path) -> dict:
    try:
        require(set(spec) == {"kind", "schema_version", "trial_id", "training_goal", "presented_isi", "pattern_hash",
                "begin", "end", "maximum_sample_gap", "maximum_samples", "channels", "generation_mode",
                "advance_sample_after_burst", "loop_samples", "model_revision", "record_spikes", "topology"}, "transient_spec_field_set")
        require(set(observation) == {"kind", "schema_version", "trial_id", "complete", "sample_count", "last_sample_time",
                "onsets", "expected_relative_times", "training_goal_after", "material_goal_after", "goal_preserved",
                "frozen_after", "scientific_verdict", "presented_at_first", "presented_after", "phase_at_first", "phase_after"}, "transient_observation_field_set")
        for item, kind in ((spec, "posttune_transient_presentation"), (observation, "posttune_transient_observation")):
            require(item["kind"] == kind and type(item["schema_version"]) is int and item["schema_version"] == 1,
                    "unknown_transient_schema")
        require(bool(spec["trial_id"]) and spec["trial_id"] == observation["trial_id"] and
                observation["complete"] is True and observation["scientific_verdict"] is None and spec["record_spikes"] is False,
                "incomplete_transient_presentation")
        require(observation["frozen_after"] == spec["model_revision"] and bool(spec["model_revision"]), "transient_model_changed")
        goal = [number(value) for value in spec["training_goal"]]
        pattern = [number(value) for value in spec["presented_isi"]]
        require(bool(pattern) and len(pattern) == len(goal) and all(value >= 0 for value in pattern + goal) and
                canonical_model_sha256(pattern) == spec["pattern_hash"], "invalid_transient_pattern")
        require(observation["goal_preserved"] is True and
                [number(value) for value in observation["training_goal_after"]] == goal and
                [number(value) for value in observation["material_goal_after"]] == goal, "training_goal_modified_by_probe")
        require(spec["topology"] in {"classic", "branch"}, "unknown_transient_topology")
        phase = 4 if spec["topology"] == "branch" else 3
        require([number(value) for value in observation["presented_at_first"]] == pattern and
                [number(value) for value in observation["presented_after"]] == pattern and
                count(observation["phase_at_first"]) == count(observation["phase_after"]) == phase,
                "transient_presented_state_changed")
        require(count(spec["generation_mode"]) == 2 and spec["advance_sample_after_burst"] is True and spec["loop_samples"] is False,
                "transient_one_pass_policy_missing")
        begin, end, gap = (number(spec[key]) for key in ("begin", "end", "maximum_sample_gap"))
        require(end > begin and gap > 64 * math.ulp(1.) * max(1., abs(begin), abs(end)), "invalid_transient_window")
        channels = count(spec["channels"])
        require(channels == (1 if spec["topology"] == "branch" else len(goal)), "wrong_transient_channel_dimension")
        with trace.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream))
        header = (["time", "stimulus"] + [f"soma{i}" for i in range(channels)] +
                  [f"training_goal{i}" for i in range(len(goal))] + [f"presented_isi{i}" for i in range(len(pattern))])
        require(bool(rows) and rows[0] == header and all(len(row) == len(header) for row in rows[1:]), "damaged_transient_csv")
        values = [[float(value) for value in row] for row in rows[1:]]
        require(3 <= len(values) == count(observation["sample_count"]) <= count(spec["maximum_samples"]) and
                all(math.isfinite(value) for row in values for value in row), "invalid_transient_samples")
        require(equal(values[0][0], begin) and not after(end, values[-1][0]) and not after(values[-1][0], end + gap) and
                equal(values[-1][0], observation["last_sample_time"]), "incomplete_transient_window")
        require(all(b[0] > a[0] and not after(b[0], a[0] + gap) for a, b in zip(values, values[1:])), "transient_sample_gap")
        offset = 2 + channels
        require(all(row[offset:offset+len(goal)] == goal and row[offset+len(goal):] == pattern for row in values),
                "transient_goal_or_stimulus_changed_during_trial")
        previous = 0.
        onsets = []
        for row in values:
            if row[1] > 0 and previous <= 0:
                onsets.append(row[0])
            previous = row[1]
        require(len(onsets) == len(pattern) and [number(value) for value in observation["onsets"]] == onsets,
                "transient_stimulus_count_or_timestamps_mismatch")
        relative = [0.]
        for value in pattern[1:]:
            relative.append(relative[-1] + value)
        declared = [number(value) for value in observation["expected_relative_times"]]
        require(declared == relative, "measurement_windows_use_wrong_pattern")
        for actual, expected in zip(onsets, relative):
            require(not after(abs((actual - onsets[0]) - expected), gap), "transient_stimulus_spacing_mismatch")
        require(max(max(row[2+i] for row in values) - min(row[2+i] for row in values) for i in range(channels)) > 1e-6,
                "constant_transient_response")
        return {"auditor_version": 1, "training_goal_preserved": True, "measurement_uses_presented_pattern": True,
                "complete": True, "sample_count": len(values), "stimulus_count": len(onsets), "channels": channels,
                "native_execution_verified": False, "measured_training_certificate_verified": False,
                "spikes_known": False, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError("malformed_transient_evidence:" + str(error)) from error


def load_case(path: Path) -> tuple:
    require(path.name.endswith("_spec.json"), "unexpected_transient_spec_filename")
    stem = path.name.removesuffix("_spec.json")
    return load(path), load(path.with_name(stem + "_observation.json")), path.with_name(stem + ".csv")
