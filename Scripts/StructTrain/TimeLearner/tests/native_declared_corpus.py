"""Bind optional native ModelSpec2 cohorts to the actual completed gate declaration."""
import os
from pathlib import Path

from ..native_evidence import load
from ..native_gate import supported_specification


def model_spec2_cohort(root, group):
    declaration = load(root.parent/"specification.json")
    ids = declaration.get("expected_test_ids")
    if (not supported_specification(declaration) or type(ids) is not list or
            not all(type(v) is str for v in ids) or len(ids) != len(set(ids))):
        raise RuntimeError("requires an explicit native gate declaration")
    if group in ("Off", "On"):
        prefix = "NativeCapacitanceModelSpec2Boundary/"
        expected = {prefix+top+"N"+norm+"C"+group for top in ("Classic", "Branch") for norm in ("0", "1")}
        selected = {v for v in ids if v.startswith(prefix) and v.endswith("C"+group)}
        keys = {(branch, norm, 2000) for branch in (False, True) for norm in ("N0", "N1")}
    elif group == "codec":
        prefix = "NativeCapacitanceModelSpec2Codec/"
        expected = {prefix+top+"N"+norm+"_"+str(hz) for top in ("Classic", "Branch")
                    for norm in ("0", "1") for hz in (2000, 20000)}
        selected = {v for v in ids if v.startswith(prefix)}
        keys = {(branch, norm, hz) for branch in (False, True) for norm in ("N0", "N1") for hz in (2000, 20000)}
    else:
        raise ValueError("unknown native ModelSpec2 cohort")
    if selected and selected != expected:
        raise RuntimeError("partial declared native ModelSpec2 cohort")
    return keys if selected else set()


def require_model_spec2_records(records, expected):
    keys = []
    for value in records:
        model = value.get("configuration", value)["model"]
        if model["schema_version"] != 2 or model["initial_threshold"] != 100.:
            raise RuntimeError("unexpected ModelSpec2 threshold cohort")
        keys.append((model["branch"], model["normalization"], model["frequency_hz"]))
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise RuntimeError("missing, duplicate or undeclared native ModelSpec2 record")


def audit_model_spec2_recognition_replay(path, solo):
    """New recognition cases require their actual eight-process replay corpus."""
    from ..recognition_owner_replay import audit_case_replay
    value = os.environ.get("TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY")
    if not value:
        raise RuntimeError("requires actual ModelSpec2 fresh-process owner replay")
    replay, root = Path(value), path.parent
    index = load(replay/"index.json")
    expected = {(branch, norm, hz, mode) for mode in ("Off", "On")
                for branch, norm, hz in model_spec2_cohort(root, mode)}
    observed = []
    for row in index["cases"]:
        name = row["source_filename"]
        if Path(name).name != name or not name.endswith("_owner_recognition_state.json"):
            raise RuntimeError("invalid ModelSpec2 replay source filename")
        source = load(root/name)["source_solo"]
        c, m = source["configuration"], source["configuration"]["model"]
        if c["schema_version"] not in (3, 4) or m["schema_version"] != 2 or m["initial_threshold"] != 100.:
            raise RuntimeError("unexpected ModelSpec2 recognition replay cohort")
        observed.append((m["branch"], m["normalization"], m["frequency_hz"], "On" if c["schema_version"] == 4 else "Off"))
    if len(observed) != len(set(observed)) or set(observed) != expected:
        raise RuntimeError("requires exactly the complete declared ModelSpec2 replay matrix")
    package_path = path.with_name(path.name.removesuffix("_learned_state.json")+"_owner_recognition_state.json")
    if load(package_path)["source_solo"] != solo:
        raise RuntimeError("ModelSpec2 owner replay substituted another solo source")
    return audit_case_replay(package_path, replay)
