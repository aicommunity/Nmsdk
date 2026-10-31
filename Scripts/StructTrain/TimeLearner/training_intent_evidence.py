"""Read-only request provenance checks; no execution or finalization certificate."""
from .model_identity import canonical_model_sha256
from .native_evidence import count, number, require


def audit_training_intent(value):
    fields = {"kind", "schema_version", "controls", "run_id", "session_attempt", "model_epoch",
              "initial_model_revision", "protocol_revision", "pattern_hash", "started_model_time",
              "dynamic_checkpoint", "calibrated", "evaluation_verdict", "sha256"}
    require(type(value) is dict and set(value) == fields and value["kind"] == "native_training_request_intent"
            and type(value["schema_version"]) is int and value["schema_version"] == 1, "unknown_training_intent")
    require(value["sha256"] == canonical_model_sha256({k: v for k, v in value.items() if k != "sha256"}),
            "training_intent_digest_mismatch")
    require(value["dynamic_checkpoint"] is False and value["calibrated"] is False
            and value["evaluation_verdict"] is None, "unsupported_training_intent_claim")
    require(count(value["session_attempt"]) > 0, "missing_training_intent_attempt")
    count(value["model_epoch"])
    number(value["started_model_time"])
    for key in ("run_id", "initial_model_revision", "protocol_revision", "pattern_hash"):
        require(type(value[key]) is str and bool(value[key]), "missing_training_intent_binding:"+key)
    controls = value["controls"]
    require(type(controls) is dict and set(controls) == {"parameters", "bindings"}
            and type(controls["parameters"]) is dict and type(controls["bindings"]) is dict
            and set(controls["parameters"]) == set(controls["bindings"]), "training_intent_control_bindings_missing")
    require({"IsNeedToTrain", "CalculateMode", "ControllerVersion", "CalibrateLTZThresholdFraction"}
            <= set(controls["parameters"]), "training_intent_required_controls_missing")
    for name, parameter in controls["parameters"].items():
        require(type(parameter) in (bool, int, float, str), "invalid_training_intent_control:"+name)
        if type(parameter) in (int, float):
            number(parameter)
        binding = controls["bindings"][name]
        require(type(binding) is dict and set(binding) == {"connected", "external_data_source", "sources"}
                and type(binding["connected"]) is bool and type(binding["external_data_source"]) is bool
                and type(binding["sources"]) is list, "invalid_training_intent_source:"+name)
        require(bool(binding["sources"]) == (binding["connected"] or binding["external_data_source"]),
                "unresolved_training_intent_source:"+name)
        for source in binding["sources"]:
            require(type(source) is dict and set(source) == {"owner_path", "property"}
                    and all(type(s) is str and bool(s) for s in source.values()), "invalid_training_intent_source_path")
    return {"schema_version": 1, "session_attempt": value["session_attempt"],
            "run_id": value["run_id"], "native_execution_attested": False,
            "calibrated": False, "evaluation_verdict": None}


def audit_training_intent_lifecycle(record):
    require(record["kind"] == "native_training_request_intent_lifecycle"
            and type(record["schema_version"]) is int and record["schema_version"] in (1, 2),
            "unknown_training_intent_lifecycle")
    require(type(record["calculate_mode"]) is int and record["calculate_mode"] in (0, 1)
            and type(record["connected"]) is bool, "invalid_training_intent_lifecycle_condition")
    rows = [audit_training_intent(record[k]) for k in ("first", "second", "third")]
    require(rows[0]["session_attempt"] < rows[1]["session_attempt"] < rows[2]["session_attempt"]
            and len({r["run_id"] for r in rows}) == 3, "training_intent_sessions_not_distinct")
    for key, fraction in (("first", .37), ("second", .63), ("third", .63)):
        controls = record[key]["controls"]
        require(controls["parameters"]["CalculateMode"] == record["calculate_mode"]
                and controls["parameters"]["CalibrateLTZThresholdFraction"] == fraction
                and controls["parameters"]["IsNeedToTrain"] is True
                and controls["bindings"]["IsNeedToTrain"]["connected"] is record["connected"],
                "training_intent_original_controls_mismatch")
    require(record["after_retarget"] == {} and record["final_outcome"] == "invalid_model"
            and record["final_reason"] == "training_target_changed_requires_new_plan",
            "training_intent_retarget_not_invalidated")
    require(record["calibrated"] is False and record["evaluation_verdict"] is None, "unsupported_intent_lifecycle_claim")
    imported = False
    if record["schema_version"] == 2:
        from .finalization_boundary_evidence import audit_boundary
        b = record["stopped_boundary"]
        audit_boundary(b)
        require(b["schema_version"] == 2 and b["training_request"] == record["second"]
                and b["diagnostic_only"] is True and b["training_outcome"] == "external_stop",
                "intent_lifecycle_boundary_mismatch")
        require(record["control_drift_reason"] == "native_training_request_controls_changed"
                and record["import_adopted"] is True and record["after_import"] == {},
                "intent_lifecycle_import_or_drift_not_checked")
        imported = True
    return {"schema_version": 1, "requests": 3, "calculate_mode": record["calculate_mode"],
            "connected": record["connected"], "execution_and_intermediate_assertions_attested": False,
            "successful_import_recorded": imported,
            "calibrated": False, "evaluation_verdict": None}
