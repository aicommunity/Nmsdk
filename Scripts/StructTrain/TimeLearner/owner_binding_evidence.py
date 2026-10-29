"""Validate editor ownership readbacks; this never yields a science verdict."""
from __future__ import annotations

import re
from pathlib import Path

from .native_evidence import count, load, number, require, audit_probe


def _parameters(values):
    require(isinstance(values, list) and len(values) == 2, "owner_fixture_requires_two_inputs")
    result = []
    for value in values:
        require(isinstance(value, dict) and set(value) == {"length", "synapses", "resistance"},
                "invalid_owner_parameter_fields")
        length, synapses, resistance = count(value["length"]), count(value["synapses"]), number(value["resistance"])
        require(length > 0 and 0 < synapses <= 128 and resistance > 0, "invalid_owner_parameter")
        result.append({"length": length, "synapses": synapses, "resistance": resistance})
    return result


def audit_editor_binding(record: dict) -> dict:
    require(record.get("kind") == "native_owner_editor_binding" and type(record.get("schema_version")) is int
            and record["schema_version"] == 1,
            "unknown_owner_binding_schema")
    require("evaluation_verdict" in record and record["evaluation_verdict"] is None, "unexpected_science_verdict")
    require(type(record.get("matching")) is bool and type(record.get("model_may_have_changed")) is bool,
            "invalid_owner_binding_flags")
    fields = {"DendriteLength": "length", "NumSynapse": "synapses", "TipSynapseResistance": "resistance"}
    require(record.get("property") in fields, "unknown_owner_binding_property")
    field = fields[record["property"]]
    previous, requested = _parameters(record["previous"]), _parameters(record["requested"])
    for key in ("source_integers", "source_resistances", "owner_lengths", "owner_counts", "owner_resistances"):
        values = record[key]
        require(isinstance(values, list) and len(values) == 2, "invalid_owner_vector:" + key)
        for value in values:
            if key in ("source_resistances", "owner_resistances"):
                require(number(value) > 0, "invalid_owner_resistance")
            else:
                require(count(value) > 0, "invalid_owner_integer")
    for key in ("model_before", "model_after"):
        require(isinstance(record.get(key), str) and re.fullmatch("[0-9a-f]{64}", record[key]) is not None,
                "invalid_owner_model_revision")
    expected_source = [v["length" if field == "length" else "synapses"] for v in previous]
    require(record["source_integers"] == expected_source, "owner_integer_source_changed")
    require(record["source_resistances"] == [v["resistance"] for v in previous], "owner_resistance_source_changed")
    require(previous != requested, "owner_fixture_has_no_actual_edit")
    equal_bound_values = [v[field] for v in previous] == [v[field] for v in requested]
    require(equal_bound_values == record["matching"], "owner_binding_control_not_applied")
    if record["matching"]:
        require(record["status"] == "applied" and record["reason"] == "", "matching_owner_binding_rejected")
        require(record["model_may_have_changed"] and record["model_before"] != record["model_after"],
                "owner_matching_edit_not_materialized")
        require(_parameters(record["effective"]) == requested, "owner_edit_effective_mismatch")
        expected = requested
    else:
        require(record["status"] == "rejected", "conflicting_owner_binding_accepted")
        require(record["reason"] == "native_model_owner_assignment_is_external:" + record["property"],
                "wrong_owner_rejection_reason")
        require(not record["model_may_have_changed"] and record["model_before"] == record["model_after"],
                "owner_conflict_changed_model")
        require(record["effective"] == [], "rejected_owner_edit_has_effective_state")
        expected = previous
    for key, name in (("owner_lengths", "length"), ("owner_counts", "synapses"), ("owner_resistances", "resistance")):
        require(record[key] == [v[name] for v in expected], "owner_metadata_physics_mismatch:" + key)
    return {"property": record["property"], "matching": record["matching"], "valid": True,
            "evaluation_verdict": None}


def audit_editor_directory(directory: Path) -> dict:
    expected = {f"{topology}_2000_N{1 if prop == 'TipSynapseResistance' else 0}_editor_binding_"
                f"{prop}_{control}_editor_binding.json"
                for topology in ("Classic", "Branch")
                for prop in ("DendriteLength", "NumSynapse", "TipSynapseResistance")
                for control in ("conflict", "matching")}
    paths = sorted(directory.glob("*_editor_binding.json"))
    require({p.name for p in paths} == expected, "incomplete_owner_editor_matrix")
    results, samples = [], 0
    for path in paths:
        results.append(audit_editor_binding(load(path)))
        prefix = path.name.removesuffix("_editor_binding.json")
        packets = list(directory.glob(prefix + "_probe_*_evidence.json"))
        require(len(packets) == 1, "owner_edit_requires_one_primary_boundary_probe")
        packet = packets[0]
        report = audit_probe(load(packet), packet.with_name(packet.name.replace("_evidence.json", ".csv")))
        samples += report["sample_count"]
    return {"schema_version": 1, "cases": len(results), "matching": sum(r["matching"] for r in results),
            "boundary_samples": samples, "evaluation_verdict": None}
