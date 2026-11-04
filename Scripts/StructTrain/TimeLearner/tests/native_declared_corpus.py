"""Bind optional native ModelSpec2 cohorts to the actual completed gate declaration."""
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
