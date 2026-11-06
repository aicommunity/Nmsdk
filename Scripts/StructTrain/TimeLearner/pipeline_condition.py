"""Bind a managed declaration to ConditionSpec; never infer native execution."""
from copy import deepcopy

from .condition import ConditionSpec, PROVENANCE_KEYS, artifact
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import require
from .runtime import digest_json, runtime_content_identity


def _semantic(value, omitted, path=""):
    if type(value) is dict:
        result = {}
        for key, child in value.items():
            require(type(key) is str, "nonstring_pipeline_condition_key")
            location = path + "/" + key
            if key.replace("_", "").lower() in PROVENANCE_KEYS:
                omitted.append(location)
            else:
                result[key] = _semantic(child, omitted, location)
        return result
    if type(value) is list:
        return [_semantic(child, omitted, path+"/"+str(i)) for i, child in enumerate(value)]
    return deepcopy(value)


def build_binding(specification, runtime):
    # Import here: the coordinator invokes this only after its own validation.
    from .managed_pipeline import _validate
    spec = _validate(specification, preflight=True)
    content = runtime_content_identity(runtime)
    require(runtime.get("runtime_identity") == content and
            runtime.get("runtime_fingerprint") == digest_json(content),
            "pipeline_condition_runtime_identity_changed")
    # The signed Train job includes its run_id in sha256. Remove only this
    # operational envelope digest, not referenced model/profile digests.
    unsigned = {"phases": deepcopy(spec["phases"])}
    unsigned["phases"][0]["job"].pop("sha256")
    omitted = ["/kind", "/schema_version", "/attempt_id", "/phases/0/job/sha256"]
    semantic = _semantic(unsigned, omitted)
    phases = semantic["phases"]
    train = phases[0]["job"]
    config = train["configuration"]
    model = config["model"]
    downstream = [{"operation": p["operation"], "trials": p["job"].get("trials", [])}
                  for p in phases[1:]]
    payloads = {
        "algorithm": {"implementation_id": train["implementation_id"],
                      "owner_class": train["owner_class"], "native_runtime_content": content},
        "model_spec": {"declaration": model},
        "storage_profiles": {"archives": train["profile_archives"]},
        "initial_state": {"policy": "declared_cold_model", "model": model},
        # Keep the entire semantic declaration as well as role projections:
        # an unclassified scientific field must not silently disappear.
        "training_plan": {"complete_declaration": semantic},
        "input_data": {"training_isi": model["initial_isi"], "downstream": downstream},
        "presentation_protocol": {"training": config, "downstream": downstream},
        "calibration_spec": {"phases": [p for p in phases if p["operation"] in ("calibrate", "posttune")],
                             "live_finalization": train.get("finalization_plan")},
        "evaluation_spec": {"phases": [p for p in phases if p["operation"] == "evaluate"]},
        "execution_policy": {"phase_limits": [{"operation": p["operation"], "wall_seconds": p["wall_seconds"]}
                                              for p in phases],
                             "calculate_mode": train["calculate_mode"],
                             "structure_build_mode": train["structure_build_mode"]},
        "randomness_spec": {"stimulus_profile": config["stimulus_profile"],
                            "independent_seed_replicates_attested": False},
    }
    artifacts = {role: artifact(role, value) for role, value in payloads.items()}
    condition = ConditionSpec(controller_version=2, amplitude_goal="captured_per_input",
                              **{role: value["sha256"] for role, value in artifacts.items()})
    return {"kind": "timelearner_managed_condition_binding", "schema_version": 1,
            "pipeline_specification_sha256": digest(spec),
            "runtime_fingerprint": runtime["runtime_fingerprint"],
            "condition": condition.to_object(), "condition_fingerprint": condition.fingerprint,
            "artifacts": {value["sha256"]: value for value in artifacts.values()},
            "omitted_metadata_paths": sorted(omitted), "declaration_only": True,
            "effective_model_verified": False, "native_execution_verified": False,
            "scientific_verdict": None}


def audit_binding(binding, specification, runtime):
    expected = build_binding(specification, runtime)
    require(binding == expected, "pipeline_condition_binding_changed")
    return expected["condition_fingerprint"]
