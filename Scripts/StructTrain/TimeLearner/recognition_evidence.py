"""Audit recognition conversion, its solo proof and declared frozen transport.

This checks data consistency, not the authenticity of an arbitrary file or
recognition selectivity. Native XML import remains a separate component check.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import struct
from pathlib import Path

from .learned_evidence import audit_learned_state, load_case as load_solo
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, count, equal, load, number, require

AUDITOR_VERSION = 1


def _digest(envelope: dict) -> None:
    require(envelope["sha256"] == canonical_model_sha256({k: v for k, v in envelope.items() if k != "sha256"}),
            "recognition_digest_mismatch")


def _physical(node: dict, name: str) -> float:
    prop = node["parameters"][name]
    require(prop["binding"] is False and prop["data"]["type"] == "binary64", "unsupported_recognition_physics")
    bits = bytes.fromhex(prop["data"]["value"])
    require(len(bits) == 8, "invalid_recognition_binary64")
    return number(struct.unpack(">d", bits)[0])


def _audit(package: dict, source_case: tuple, spec: dict, observation: dict, trace: Path) -> dict:
    require(set(package) == {"kind", "schema_version", "dynamic_checkpoint", "state_kind", "implementation_id",
                            "source_solo", "conversion_spec", "conversion_record", "recognition_inputs", "model_revision",
                            "recognition_certificate", "dataset", "neuron", "sha256"}, "recognition_field_set_mismatch")
    require(package["kind"] == "timelearner_recognition_state" and type(package["schema_version"]) is int
            and package["schema_version"] == 1 and package["state_kind"] == "recognition"
            and package["dynamic_checkpoint"] is False and package["recognition_certificate"] is None,
            "unsupported_recognition_claim")
    _digest(package)
    source, summary, _, _ = source_case
    source_audit = audit_learned_state(*source_case)
    require(isinstance(package["implementation_id"], str) and bool(package["implementation_id"].strip()), "missing_recognition_implementation")
    require(package["source_solo"] == source and package["implementation_id"] == source["implementation_id"]
            and package["dataset"] == source["dataset"], "recognition_source_mismatch")
    archive = package["neuron"]
    require(archive.get("kind") == "timelearner_model_archive" and type(archive.get("schema_version")) is int
            and archive["schema_version"] == 2, "unknown_recognition_archive_schema")
    _digest(archive)
    model = archive["graph"]["identity"]["model"]
    require(type(model.get("schema_version")) is int and model["schema_version"] == 2, "unknown_recognition_graph_schema")
    require(canonical_model_sha256(model) == package["model_revision"] == archive["graph"]["identity"]["sha256"],
            "recognition_model_digest_mismatch")
    graph = archive["graph"]
    require(hashlib.sha256(graph["native_xml"].encode("utf-8")).hexdigest() == graph["native_xml_sha256"],
            "recognition_xml_digest_mismatch")
    require(archive["class_definitions"] == source["neuron"]["class_definitions"], "recognition_images_changed")
    conversion = package["conversion_spec"]
    require(set(conversion) == {"schema_version", "mode", "resistance_bounds"} and
            type(conversion["schema_version"]) is int and conversion["schema_version"] == 1, "unknown_conversion_spec")
    mode = conversion["mode"]
    require(mode in {"identity", "historical_branch_n1_v1"}, "unknown_conversion_mode")
    params = source["trained_inputs"]
    n = len(params)
    declaration = source["configuration"]["model"]
    require(type(declaration["branch"]) is bool and n > 0, "invalid_conversion_topology")
    refs = {item["input_id"]: number(item["raw_potential"]) for item in summary["references"]}
    amplitudes = [refs[item["id"]] for item in source["protocol"]["inputs"]]
    factors = [1.] * n
    bounds = conversion["resistance_bounds"]
    if mode == "identity":
        require(bounds == [], "identity_has_unused_bounds")
    else:
        require(declaration["branch"] and declaration["normalization"] == "N1" and len(bounds) == n,
                "unsupported_historical_conversion")
        if n > 1:
            require(all(value > 0 for value in amplitudes), "nonpositive_conversion_reference")
            mean = 0.
            for value in amplitudes[:-1]:
                mean += value / (n - 1)
            require(math.isfinite(mean) and mean > 0, "invalid_conversion_mean")
            factors = [number(n * (value / mean)) for value in amplitudes]
    original_model = source["neuron"]["graph"]["identity"]["model"]
    require(type(original_model.get("schema_version")) is int and original_model["schema_version"] == 2,
            "unknown_source_graph_schema")
    expected_model = copy.deepcopy(original_model)
    nodes = {node["path"]: node for node in expected_model["nodes"]}
    original_nodes = {node["path"]: node for node in original_model["nodes"]}
    require(len(nodes) == len(expected_model["nodes"]), "duplicate_recognition_node")
    decisions = package["conversion_record"]["decisions"]
    require(len(decisions) == n and len(package["recognition_inputs"]) == n, "conversion_dimension_mismatch")
    banks: dict[str, float] = {}
    expected_parameters = []
    for i, p in enumerate(params):
        root = f"$.Dendrite{1 if declaration['branch'] else i + 1}_{count(p['length'])}"
        original, factor = number(p["resistance"]), number(factors[i])
        require(original > 0 and factor > 0, "invalid_conversion_resistance")
        requested = number(original * factor)
        low = high = applied = original
        if mode != "identity":
            require(set(bounds[i]) == {"minimum", "maximum"}, "unknown_conversion_bounds")
            declared_low, declared_high = number(bounds[i]["minimum"]), number(bounds[i]["maximum"])
            ratio = number(declaration["maximum_resistance_ratio"])
            floor = number(declaration["configured_minimum_resistance"])
            rm = _physical(nodes[root + ".ExcChannel"], "RestingResistance")
            require(0 < declared_low <= declared_high and ratio >= 1 and floor >= 0 and rm > 0, "invalid_conversion_bounds")
            low, high = max(declared_low, rm / ratio, floor), min(declared_high, rm * ratio)
            require(0 < low <= high and (n > 1 or low <= original <= high), "empty_conversion_bounds")
            applied = max(low, min(high, requested))
        expected = {"input_index": i, "original_resistance": original, "factor": factor,
                    "requested_resistance": requested, "minimum_resistance": low, "maximum_resistance": high,
                    "applied_resistance": applied, "clipped": applied != requested}
        d = decisions[i]
        require(set(d) == set(expected) and count(d["input_index"]) == i and
                type(d["clipped"]) is bool and d["clipped"] is expected["clipped"] and
                all(equal(d[key], value) for key, value in expected.items() if key not in {"clipped", "input_index"}),
                "conversion_decision_not_derived_from_solo")
        expected_parameters.append({**p, "resistance": applied})
        for k in range(1, count(p["synapses"]) + 1):
            path = root + ".ExcSynapse" + str(k)
            require(path not in banks or banks[path] == applied, "conflicting_shared_recognition_bank")
            banks[path] = applied
            require(_physical(original_nodes[path], "Resistance") == original, "source_bank_readback_mismatch")
            nodes[path]["parameters"]["Resistance"]["data"]["value"] = struct.pack(">d", applied).hex()
    require(package["recognition_inputs"] == expected_parameters, "recognition_parameter_mismatch")
    original_edges = original_model["bindings"]
    activated = []
    for path in sorted(banks):
        target = path + ":Input"
        existing = [edge for edge in original_edges if edge["target"] == target]
        wanted = {"kind": "stimulus_port", "slot": "0", "source": "burst", "target": target}
        require(not existing or existing == [wanted], "conversion_replaces_unowned_binding")
        if not existing:
            activated.append(path.removeprefix("$."))
            require([edge for edge in model["bindings"] if edge["target"] == target] == [wanted], "missing_activated_input")
    added_targets = {"$." + path + ":Input" for path in activated}
    require([edge for edge in model["bindings"] if edge["target"] not in added_targets] == original_edges,
            "conversion_changed_other_bindings")
    expected_model["bindings"] = model["bindings"]
    require(expected_model == model, "conversion_changed_other_physics_or_structure")
    record = package["conversion_record"]
    require(set(record) == {"schema_version", "algorithm", "source_solo_sha256", "source_solo_identity", "result_identity",
                           "decisions", "activated_synapses", "inhibition_policy"} and type(record["schema_version"]) is int and record["schema_version"] == 1 and
            record["algorithm"] == mode and record["source_solo_sha256"] == source["sha256"] and
            record["source_solo_identity"] == source["model_revision"] and record["result_identity"] == package["model_revision"] and
            record["activated_synapses"] == activated and record["inhibition_policy"] == "preserve_source", "conversion_record_mismatch")
    metadata = copy.deepcopy(source["neuron"]["metadata"])
    metadata["state_kind"], metadata["recognition_schema_version"] = "recognition", 1
    metadata["training"]["scope"] = "source_solo"
    metadata["calibration"]["protocol"] = "fixed-inherited-from-solo"
    metadata["calibration"]["source_solo_sha256"] = source["sha256"]
    metadata["conversion"] = {"mode": "parallel", "source_solo_identity": source["model_revision"],
                              "source_solo_sha256": source["sha256"], "factors": factors, "record": record}
    metadata["recognition_verification"] = {"status": "unverified", "model_identity": package["model_revision"], "certificate": None}
    require(type(archive["metadata"]["recognition_schema_version"]) is int and
            all(number(value) > 0 for value in archive["metadata"]["conversion"]["factors"]), "invalid_recognition_metadata_types")
    require(metadata == archive["metadata"], "recognition_certificate_or_calibration_scope_mismatch")
    frozen = audit_frozen_transport(package, source, spec, observation, trace)
    return {"auditor_version": AUDITOR_VERSION, "conversion_math_verified": True, "source_audit": source_audit,
            "other_physics_preserved": True, "native_import_verified": False, "frozen_transport": frozen,
            "evaluation_verdict": None}


def audit_frozen_transport(package: dict, source: dict, spec: dict, observation: dict, trace: Path) -> dict:
    require(spec.get("kind") == "native_recognition_frozen_probe" and type(spec.get("schema_version")) is int
            and spec["schema_version"] == 1 and observation.get("kind") == "native_recognition_roundtrip_observation"
            and type(observation.get("schema_version")) is int and observation["schema_version"] == 1,
            "unknown_frozen_transport_schema")
    require(spec["measurement"] == "paired_soma_transport" and spec["record_spikes"] is False and
            observation["scientific_verdict"] is None and observation["complete"] is True, "incomplete_frozen_transport")
    require(bool(spec["run_id"]) and bool(spec["trial_id"]) and observation["trial_id"] == spec["trial_id"] and
            spec["pattern_hash"] == source["protocol"]["pattern_hash"], "frozen_transport_identity_mismatch")
    require(spec["model_revision"] == observation["model_revision"] == observation["frozen_after"] ==
            observation["frozen_after_b"] == package["model_revision"], "frozen_model_changed")
    begin, end, gap = (number(spec[key]) for key in ("begin", "end", "maximum_sample_gap"))
    require(end > begin and gap > 64 * math.ulp(1.) * max(1., abs(begin), abs(end)), "unresolvable_frozen_window")
    channels = count(spec["channels"])
    expected_channels = 1 if source["configuration"]["model"]["branch"] else len(package["recognition_inputs"])
    require(channels == expected_channels, "frozen_channel_dimension_mismatch")
    with trace.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.reader(stream))
    header = ["time", "stimulus_a", "stimulus_b"] + [name for i in range(channels) for name in (f"soma_a{i}", f"soma_b{i}")]
    require(bool(rows) and rows[0] == header and all(len(row) == len(header) for row in rows[1:]), "damaged_frozen_csv")
    values = [[float(item) for item in row] for row in rows[1:]]
    require(3 <= len(values) == count(observation["sample_count"]) <= count(spec["maximum_samples"]) and
            all(math.isfinite(item) for row in values for item in row), "invalid_frozen_samples")
    require(equal(values[0][0], begin) and not after(end, values[-1][0]) and not after(values[-1][0], end + gap) and
            equal(observation["last_sample_time"], values[-1][0]), "incomplete_frozen_coverage")
    require(all(b[0] > a[0] and not after(b[0], a[0] + gap) for a, b in zip(values, values[1:])), "frozen_sample_gap_or_duplicate")
    require(all(row[1] == row[2] and all(row[3 + 2*i] == row[4 + 2*i] for i in range(channels)) for row in values),
            "frozen_pair_waveform_mismatch")
    variation = max(max(row[3 + 2*i] for row in values) - min(row[3 + 2*i] for row in values) for i in range(channels))
    maximum = max(abs(row[3 + 2*i]) for row in values for i in range(channels))
    require(variation > 1e-6 and equal(variation, observation["soma_variation"]) and
            equal(maximum, observation["maximum_soma"]) and observation["emitted"] is True and any(row[1] > 0 for row in values),
            "constant_or_unstimulated_frozen_pair")
    return {"complete": True, "sample_count": len(values), "paired_values_exact": True,
            "soma_variation": variation, "spikes_known": False, "evaluation_verdict": None}


def audit_recognition_state(package: dict, source_case: tuple, spec: dict, observation: dict, trace: Path) -> dict:
    try:
        return _audit(package, source_case, spec, observation, trace)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, struct.error) as error:
        raise EvidenceError("malformed_recognition_evidence:" + str(error)) from error


def load_case(path: Path) -> tuple:
    require(path.name.endswith("_recognition_state.json"), "unexpected_recognition_filename")
    stem = path.name.removesuffix("_recognition_state.json")
    return (load(path), load_solo(path.with_name(stem + "_learned_state.json")),
            load(path.with_name(stem + "_recognition_probe_spec.json")),
            load(path.with_name(stem + "_recognition_roundtrip.json")), path.with_name(stem + "_recognition_roundtrip.csv"))
