"""Audit actual graph reconstruction and complete parallel waveform transport."""
from __future__ import annotations

import csv
import math
from pathlib import Path

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, count, equal, load, number, require


def _window(spec: dict, observation: dict, path: Path, revision: str, frequency: int) -> list[list[float]]:
    require(set(spec) == {"kind", "schema_version", "trial_id", "model_revision", "begin", "end",
            "maximum_sample_gap", "maximum_samples", "channels", "record_spikes", "input_isi", "dataset_delay", "pattern_hash",
            "generation_mode", "advance_sample_after_burst", "loop_samples"},
            "posttune_spec_field_set")
    require(set(observation) == {"kind", "schema_version", "trial_id", "model_revision", "frozen_after", "complete",
            "sample_count", "last_sample_time", "emitted", "soma_variation", "scientific_verdict"}, "posttune_observation_field_set")
    for item, kind in ((spec, "posttune_parallel_transport_spec"), (observation, "posttune_parallel_transport_observation")):
        require(item["kind"] == kind and type(item["schema_version"]) is int and item["schema_version"] == 1,
                "unknown_posttune_transport_schema")
    require(bool(spec["trial_id"]) and spec["trial_id"] == observation["trial_id"] and
            spec["model_revision"] == observation["model_revision"] == observation["frozen_after"] == revision,
            "posttune_frozen_identity_mismatch")
    require(observation["complete"] is True and observation["emitted"] is True and
            observation["scientific_verdict"] is None and spec["record_spikes"] is False and count(spec["channels"]) == 1,
            "incomplete_posttune_transport")
    require(count(spec["generation_mode"]) == 2 and spec["advance_sample_after_burst"] is True and
            spec["loop_samples"] is False, "posttune_requires_declared_single_presentation")
    begin, end, gap = (number(spec[key]) for key in ("begin", "end", "maximum_sample_gap"))
    require(end > begin and equal(gap, 1 / frequency) and
            gap > 64 * math.ulp(1.) * max(1., abs(begin), abs(end)), "invalid_posttune_window")
    pattern = [number(value) for value in spec["input_isi"]]
    require(bool(pattern) and all(value >= 0 for value in pattern) and
            canonical_model_sha256(pattern) == spec["pattern_hash"], "invalid_posttune_pattern")
    delay = number(spec["dataset_delay"])
    require(delay >= 0, "negative_posttune_dataset_delay")
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    require(bool(rows) and rows[0] == ["time", "stimulus", "soma0"] and
            all(len(row) == 3 for row in rows[1:]), "damaged_posttune_csv")
    values = [[float(value) for value in row] for row in rows[1:]]
    require(3 <= len(values) == count(observation["sample_count"]) <= count(spec["maximum_samples"]) and
            all(math.isfinite(value) for row in values for value in row), "invalid_posttune_samples")
    require(equal(values[0][0], begin) and not after(end, values[-1][0]) and not after(values[-1][0], end + gap) and
            equal(observation["last_sample_time"], values[-1][0]), "incomplete_posttune_window")
    require(all(b[0] > a[0] and not after(b[0], a[0] + gap) for a, b in zip(values, values[1:])), "posttune_sample_gap")
    previous = 0.
    onsets = []
    for time, stimulus, _ in values:
        if stimulus > 0 and previous <= 0:
            onsets.append(time)
        previous = stimulus
    require(len(onsets) == len(pattern), "posttune_stimulus_count_mismatch")
    onset = begin + delay
    for actual, isi in zip(onsets, pattern):
        onset += isi
        require(not after(abs(actual - onset), gap), "posttune_stimulus_timestamp_mismatch")
    variation = max(row[2] for row in values) - min(row[2] for row in values)
    require(variation > 1e-6 and equal(variation, observation["soma_variation"]), "posttune_constant_or_wrong_response")
    return values


def audit_reconstruction(record: dict, before: tuple, after_case: tuple) -> dict:
    try:
        require(set(record) == {"kind", "schema_version", "mode", "frequency", "reconstructed", "injected_attach_failure",
                "external_listener", "before_model", "after_model", "samples", "waveform_exact", "evaluation_verdict"},
                "posttune_reconstruction_field_set")
        require(record["kind"] == "posttune_native_reconstruction" and type(record["schema_version"]) is int and
                record["schema_version"] == 1, "unknown_posttune_reconstruction_schema")
        require(count(record["mode"]) in range(5) and record["evaluation_verdict"] is None and
                all(type(record[key]) is bool for key in ("reconstructed", "injected_attach_failure", "external_listener", "waveform_exact")),
                "invalid_posttune_reconstruction_claim")
        require(record["reconstructed"] is (not record["injected_attach_failure"] and not record["external_listener"]),
                "posttune_reconstruction_outcome_mismatch")
        identity = record["before_model"]
        require(identity == record["after_model"] and identity["kind"] == "semantic_model_identity" and identity["valid"] is True and
                type(identity["schema_version"]) is int and identity["schema_version"] == 2 and
                type(identity["model"]["schema_version"]) is int and identity["model"]["schema_version"] == 2 and
                identity["diagnostics"] == [] and canonical_model_sha256(identity["model"]) == identity["sha256"], "posttune_graph_changed")
        nodes = {node["path"]: node for node in identity["model"]["nodes"]}
        require(len(nodes) == len(identity["model"]["nodes"]), "duplicate_posttune_graph_node")
        frequency = count(record["frequency"])
        require(frequency > 0 and all(node["frequency_hz"] == str(frequency) for node in nodes.values()), "posttune_frequency_mismatch")
        require(before[0]["trial_id"].endswith("/before") and after_case[0]["trial_id"] ==
                before[0]["trial_id"].removesuffix("/before") + "/after" and
                before[0]["pattern_hash"] == after_case[0]["pattern_hash"], "posttune_trial_pair_mismatch")
        a = _window(*before, identity["sha256"], frequency)
        b = _window(*after_case, identity["sha256"], frequency)
        require(a == b and len(a) == count(record["samples"]) and record["waveform_exact"] is True,
                "posttune_transport_waveform_mismatch")
        return {"auditor_version": 1, "graph_and_waveform_exact": True, "sample_count": len(a),
                "reconstructed": record["reconstructed"], "native_execution_verified": False,
                "whole_posttune_selection_verified": False, "spikes_known": False, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError("malformed_posttune_reconstruction:" + str(error)) from error


def load_case(path: Path) -> tuple:
    require(path.name.endswith("_reconstruction.json"), "unexpected_posttune_reconstruction_filename")
    stem = path.name.removesuffix("_reconstruction.json")
    def window(phase):
        return (load(path.with_name(stem + "_" + phase + "_spec.json")),
                load(path.with_name(stem + "_" + phase + "_observation.json")), path.with_name(stem + "_" + phase + ".csv"))
    return load(path), window("before"), window("after")
