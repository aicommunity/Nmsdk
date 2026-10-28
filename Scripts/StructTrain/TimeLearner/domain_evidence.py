"""Recompute native N1 domain bounds from an immutable physical preview.

This audits a derived decision, not convergence, recognition or a live graph.
Schema 1 has no complete preview and cannot prove physical bounds. The caller
must explicitly request its descriptive adapter; it never returns verified=True.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, count, load, number, require

AUDITOR_VERSION = 1


def _same(actual: Any, expected: float) -> bool:
    # Relative binary64 roundoff only, including quantities much smaller than 1.
    actual = number(actual)
    return abs(actual - expected) <= 64 * sys.float_info.epsilon * max(
        abs(actual), abs(expected), sys.float_info.min)


def _positive(value: Any) -> float:
    value = number(value)
    require(value > 0, "nonpositive_domain_quantity")
    return value


def _property(node: dict, name: str) -> Any:
    prop = node["parameters"][name]
    require(prop["binding"] is False, "connected_domain_parameter")
    data = prop["data"]
    if data["type"] == "binary64":
        encoded = data["value"]
        require(isinstance(encoded, str) and len(encoded) == 16, "invalid_binary64_parameter")
        return number(struct.unpack(">d", bytes.fromhex(encoded))[0])
    if data["type"] == "boolean":
        require(type(data["value"]) is bool, "invalid_boolean_parameter")
        return data["value"]
    raise EvidenceError("unsupported_domain_parameter_type:" + name)


def _audit(record: dict, allow_legacy: bool) -> dict:
    require(record.get("kind") == "native_resistance_domain_evidence", "unknown_domain_kind")
    version = record.get("schema_version")
    require(type(version) is int and version in (1, 2), "unknown_domain_schema")
    status = record["status"]
    require(status in {"available", "unavailable", "unsupported", "failed"}, "unknown_domain_status")
    if version == 1:
        require(allow_legacy, "legacy_domain_has_no_physical_preview")
        return {"auditor_version": AUDITOR_VERSION, "schema_version": 1,
                "physics_verified": False, "reason": "legacy_domain_has_no_physical_preview",
                "evaluation_verdict": None}
    require(type(record["model_may_have_changed"]) is bool, "invalid_model_change_flag")
    if status != "available":
        return {"auditor_version": AUDITOR_VERSION, "schema_version": 2,
                "physics_verified": False, "reason": "domain_not_available:" + status,
                "evaluation_verdict": None}
    require(record["model_may_have_changed"] is False, "domain_changed_live_model")
    model = record["preview_model"]
    require(isinstance(model, dict) and model["schema_version"] == 2, "missing_domain_preview")
    require(canonical_model_sha256(model) == record["preview_model_revision"], "preview_identity_mismatch")
    require(isinstance(record["base_model_revision"], str) and bool(record["base_model_revision"]),
            "missing_domain_base_identity")
    policy = record["policy"]
    require(policy["equations"] == "explicit_npulsechannel_npulsesynapse_v1", "unsupported_domain_equations")
    ratio = _positive(policy["maximum_resistance_ratio"])
    floor = number(policy["configured_minimum_resistance"])
    require(ratio >= 1 and floor >= 0, "invalid_domain_policy")
    amplitude = number(record["source_amplitude"])
    require(type(record["branch"]) is bool and type(record["locked_by_shared_bank"]) is bool,
            "invalid_domain_flags")
    geometry = record["geometry"]
    index = count(record["input_index"])
    require(isinstance(geometry, list) and 0 <= index < len(geometry) - 1, "domain_input_is_not_tunable")
    for item in geometry:
        require(count(item["length"]) >= 1 and count(item["synapses"]) == 1, "invalid_n1_domain_geometry")
        _positive(item["resistance"])
    nodes = {node["path"]: node for node in model["nodes"]}
    require(len(nodes) == len(model["nodes"]), "duplicate_domain_node")
    bindings: dict[str, list[dict]] = {}
    for binding in model["bindings"]:
        bindings.setdefault(binding["target"], []).append(binding)

    def sources(path: str, name: str) -> list[dict]:
        return bindings.get(path + ":" + name, [])

    controls: dict[str, set[int]] = {}
    for control in record["controls"]:
        path = "$." + control["synapse_path"]
        owners = [count(value) for value in control["input_indices"]]
        require(path in nodes and path not in controls and bool(owners) and len(set(owners)) == len(owners)
                and max(owners) < len(geometry), "invalid_domain_control")
        controls[path] = set(owners)
    for owner, item in enumerate(geometry):
        path = f"$.Dendrite{1 if record['branch'] else owner + 1}_{item['length']}.ExcSynapse1"
        require(owner in controls.get(path, set()) and
                _property(nodes[path], "Resistance") == item["resistance"], "excitation_control_mismatch")
    locked = any(index in owners and len(owners) > 1 for owners in controls.values())
    require(record["locked_by_shared_bank"] is locked, "shared_bank_lock_mismatch")

    def conductance(path: str) -> float:
        node = nodes[path]
        require(not sources(path, "WeightInput"), "dynamic_synapse_weight")
        resistance = _positive(_property(node, "Resistance"))
        secretion, dissociation = (_positive(_property(node, key)) for key in ("SecretionTC", "DissociationTC"))
        frequency = _positive(int(node["frequency_hz"]))
        alpha, beta = 1 / (secretion * frequency), 1 / (dissociation * frequency)
        require(0 < alpha < 2 and 0 < beta < 2, "unstable_domain_synapse")
        weight = number(_property(node, "Weight"))
        pulse = _positive(_property(node, "PulseAmplitude"))
        require(weight >= 0, "negative_domain_weight")
        is_pulse = _property(node, "UsePulseSignal")
        drive_amplitude = amplitude
        inputs = sources(path, "Input")
        if not is_pulse and inputs:
            require(len(inputs) == 1, "unsupported_analog_domain_input")
            source = inputs[0]
            if source["kind"] == "stimulus_port":
                require(source["source"] == "burst", "unknown_domain_stimulus_port")
            else:
                origin, output = source["source"].rsplit(":", 1)
                require(output == "Output", "unsupported_analog_domain_output")
                generator = nodes[origin]
                # Internal constants have the native constant's Amplitude;
                # transit generators additionally carry the bounded-mode flags.
                if "UseTransitSignal" in generator["parameters"]:
                    require(not _property(generator, "UseTransitSignal") and
                            not _property(generator, "UsePatternOutput") and
                            _property(generator, "FrequencyDeviation") == 0, "unbounded_domain_stimulus")
                    drive_amplitude = _property(generator, "Amplitude")
                else:
                    drive_amplitude = max(0., _property(generator, "Amplitude"))
        drive = 1. if is_pulse else drive_amplitude / pulse
        maximum = drive
        if alpha > 1 or beta > 1:
            maximum = alpha * drive / (1 - max(abs(1 - alpha), abs(1 - beta)))
        require(math.isfinite(maximum) and maximum >= 0, "invalid_domain_secretion")
        normalized = maximum
        if _property(node, "UsePresynapticInhibition"):
            k = number(_property(node, "InhibitionCoeff"))
            require(k >= 0, "negative_domain_psi")
            if k > 0 and maximum > 0:
                normalized = max(1., (.4 if k > 2 else .2 * k) * maximum)
        result = normalized / resistance * weight
        require(math.isfinite(result), "nonfinite_domain_conductance")
        return result

    target = f"$.Dendrite{1 if record['branch'] else index + 1}_{geometry[index]['length']}.ExcChannel"
    rm = _positive(_property(nodes[target], "RestingResistance"))
    lower, upper = max(rm / ratio, floor), rm * ratio
    expected = {}
    for path, node in nodes.items():
        if not {"Capacity", "FBResistance", "UseAverageSynapsis"} <= node["parameters"].keys():
            continue
        capacity, frequency = _positive(_property(node, "Capacity")), _positive(int(node["frequency_hz"]))
        variable, fixed = 0., 0.
        inputs = sources(path, "SynapticInputs")
        for binding in inputs:
            origin, output = binding["source"].rsplit(":", 1)
            require(binding["kind"] == "property_pointer" and output == "Output", "unsupported_domain_conductance_source")
            g = conductance(origin)
            if index in controls.get(origin, set()):
                variable += g * geometry[index]["resistance"]
            else:
                fixed += g
        if _property(node, "UseAverageSynapsis") and inputs:
            variable, fixed = variable / len(inputs), fixed / len(inputs)
        channel_lower = 0.
        for key in ("Resistance", "RestingResistance", "FBResistance"):
            r = _positive(_property(node, key))
            q = _positive(capacity * r * frequency)
            if variable == 0:
                require((1 + fixed * r) ** 2 / q < 2, "available_domain_has_unstable_fixed_channel")
            else:
                available = (math.sqrt(q) - 1) / r - fixed
                require(available > 0, "available_domain_has_no_finite_floor")
                channel_lower = max(channel_lower, _positive(variable / available))
        if variable > 0:
            channel_lower = math.nextafter(channel_lower, math.inf)
            lower = max(lower, channel_lower)
            expected[path.removeprefix("$.")] = (variable, fixed, channel_lower)
    actual = {item["path"]: item for item in record["channels"]}
    require(len(actual) == len(record["channels"]) and set(actual) == set(expected), "domain_channel_set_mismatch")
    for path, values in expected.items():
        require(all(_same(actual[path][key], value) for key, value in zip(
            ("variable_coefficient", "fixed_conductance", "minimum_resistance"), values)), "domain_channel_coefficient_mismatch")
    if locked:
        value = geometry[index]["resistance"]
        lower, upper = max(lower, value), min(upper, value)
    require(math.isfinite(lower) and math.isfinite(upper) and 0 < lower <= upper, "empty_available_domain")
    require(_same(record["minimum_resistance"], lower) and _same(record["maximum_resistance"], upper),
            "domain_endpoint_mismatch")
    return {"auditor_version": AUDITOR_VERSION, "schema_version": 2, "physics_verified": True,
            "preview_model_revision": record["preview_model_revision"], "controlled_channels": len(expected),
            "minimum_resistance": lower, "maximum_resistance": upper, "evaluation_verdict": None}


def audit_resistance_domain(record: dict, *, allow_legacy: bool = False) -> dict:
    try:
        return _audit(record, allow_legacy)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError, ValueError, OverflowError, struct.error) as error:
        raise EvidenceError("malformed_domain_evidence:" + str(error)) from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--allow-legacy", action="store_true")
    args = parser.parse_args()
    print(json.dumps(audit_resistance_domain(load(args.record), allow_legacy=args.allow_legacy), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
