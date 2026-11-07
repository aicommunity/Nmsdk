"""Bind recorded recovery decisions to primary probes and budget increments.

The attempt total is producer-reported: non-recovery failures can include
preparation failures without a physical CSV. Do not pretend to recount those
from the number of rejections or recorded probes.
"""
from .candidate_recovery import RECOVERY_MODE, project_recovery_summary
from .candidate_recovery_evidence import audit_unassigned_burst
from .native_evidence import EvidenceError, count, number, require, validate_search_history_availability


_FIELDS = {"action_serial", "input_index", "candidate_input_index", "sweep", "model_epoch",
           "invalid_before", "invalid_after", "run_id", "trial_id", "base_model_revision",
           "effective_model_revision", "phase", "validity", "full_parameters", "capacitance",
           "disposition", "status_after", "reason_after"}


def _audit(summary, packets, traces, protocol):
    projected, mode = project_recovery_summary(summary)
    require(mode == RECOVERY_MODE, "recovery_history_requires_opt_in")
    validate_search_history_availability(projected)
    events = summary["candidate_recovery_events"]
    retained = summary["search_history_retained"]
    recovery_rejections = {}
    for row in summary["rejections"]:
        require(type(row) is dict and set(row) == {"trial_id", "reason"} and
                type(row["trial_id"]) is str and type(row["reason"]) is str, "invalid_recovery_rejection_row")
        if row["reason"].startswith("unassigned_burst_candidate:"):
            require(row["trial_id"] and row["trial_id"] not in recovery_rejections and
                    row["reason"] in ("unassigned_burst_candidate:missing", "unassigned_burst_candidate:ambiguous"),
                    "duplicate_or_unknown_recovery_rejection")
            recovery_rejections[row["trial_id"]] = row["reason"]
    if not retained:
        require(not recovery_rejections, "unretained_recovery_contains_rejections")
        return {"history_retained": False, "recorded_events_checked": 0, "invalid_observations": None,
                "all_invalid_observations_independently_recounted": False, "evaluation_verdict": None}
    cfg = summary["configuration"]
    allowance, total = count(cfg["maximum_invalid_observations"]), count(summary["invalid_observations"])
    require(total <= allowance+1 and (total <= allowance or summary["outcome"] == "invalid_observation"),
            "recovery_attempt_charge_exceeds_declared_budget")
    c_history = projected["schema_version"] in (3, 4)
    if c_history:
        from .training_capacitance_history import audit_training_capacitance_history
        from .training_capacitance_witness import validate_witness_input_parameters
        audit_training_capacitance_history(projected, packets)
    inputs = protocol["inputs"];n = len(inputs)
    seen = set();previous_serial = previous_charge = previous_sweep = previous_epoch = 0
    for position, event in enumerate(events):
        require(type(event) is dict and set(event) == _FIELDS | ({"capacitance_witness_id"} if c_history else set()),
                "unknown_recovery_event_fields")
        trial = event["trial_id"];serial = count(event["action_serial"])
        require(type(trial) is str and trial not in seen and serial > previous_serial and
                event["run_id"] == cfg["run_id"] and trial == cfg["run_id"]+"/search/"+str(serial) and
                trial in recovery_rejections and trial in packets and trial in traces,
                "recovery_event_trial_or_order_mismatch")
        seen.add(trial)
        measured = audit_unassigned_burst(packets[trial], traces[trial], protocol)
        prepared = packets[trial]["prepared"]
        require(packets[trial]["requested_specification"]["run_id"] == cfg["run_id"] and
                packets[trial]["requested_specification"]["trial_id"] == trial and
                measured["input_index"] == count(event["input_index"]) and
                measured["validity"] == event["validity"] and
                recovery_rejections[trial] == "unassigned_burst_candidate:"+event["validity"] and
                prepared["base_model_revision"] == event["base_model_revision"] and
                prepared["effective_model_revision"] == event["effective_model_revision"] and
                prepared["model_epoch"] == count(event["model_epoch"]), "recovery_event_primary_context_mismatch")
        candidate = count(event["candidate_input_index"]);sweep = count(event["sweep"])
        require(candidate < n-1 and previous_sweep <= sweep < count(cfg["maximum_sweeps"]) and
                previous_epoch <= count(event["model_epoch"]) <= count(summary["model_epoch"]) and
                event["phase"] in ("anchor", "input") and measured["input_index"] ==
                (n-1 if event["phase"] == "anchor" else candidate), "recovery_event_search_phase_mismatch")
        parameters = event["full_parameters"]
        require(type(parameters) is list and len(parameters) == len(cfg["bounds"]) == n,
                "recovery_parameter_dimensions_mismatch")
        for value, bound in zip(parameters, cfg["bounds"]):
            require(type(value) is dict and set(value) == {"length", "synapses", "resistance"} and
                    1 <= count(bound["minimum_length"]) <= count(value["length"]) <= count(bound["maximum_length"]) and
                    1 <= count(bound["minimum_synapses"]) <= count(value["synapses"]) <= count(bound["maximum_synapses"]) <= 128 and
                    0 < number(bound["minimum_resistance"]) <= number(value["resistance"]) <= number(bound["maximum_resistance"]),
                    "recovery_parameters_outside_declared_bounds")
        if c_history:
            history = projected["capacitance_history"];key = event["capacitance_witness_id"]
            require(history["trial_witness_ids"].get(trial) == key and key in history["witnesses"],
                    "recovery_capacitance_witness_missing")
            witness = history["witnesses"][key]
            require(witness["model_revision"] == event["base_model_revision"] and
                    witness["controller_parameters"] == event["capacitance"], "recovery_capacitance_context_mismatch")
            validate_witness_input_parameters(witness, parameters)
        else:
            require(event["capacitance"] is None, "unversioned_recovery_capacitance")
        before, after = count(event["invalid_before"]), count(event["invalid_after"])
        require(previous_charge <= before and after == before+1 and after <= total,
                "recovery_invalid_charge_increment_mismatch")
        disposition = event["disposition"]
        if disposition == "cursor_advanced":
            require(before < allowance and event["status_after"] == "searching" and event["reason_after"] == "",
                    "recovery_cursor_advanced_without_budget")
        else:
            require(position+1 == len(events) and after == total and
                    summary["state"] == "finished" and event["status_after"] == summary["outcome"] and
                    event["reason_after"] == summary["reason"], "recovery_terminal_event_mismatch")
            if disposition == "invalid_budget_stop":
                require(before == allowance and event["status_after"] == "invalid_observation" and
                        event["reason_after"] == recovery_rejections[trial], "recovery_invalid_budget_stop_mismatch")
            else:
                require(disposition == "restored_best_stop" and before < allowance and
                        event["status_after"] == "search_unresolved" and
                        event["reason_after"] == "restored_best_candidate_has_unassigned_burst",
                        "recovery_restored_best_stop_mismatch")
        previous_serial, previous_charge, previous_sweep, previous_epoch = serial, after, sweep, count(event["model_epoch"])
    require(seen == set(recovery_rejections), "recovery_event_rejection_coverage_mismatch")
    return {"history_retained": True, "recorded_events_checked": len(events), "invalid_observations": total,
            "allowance": allowance, "recovery_increments_primary_consistent": True,
            "all_invalid_observations_independently_recounted": False, "evaluation_verdict": None}


def audit_recovery_history(summary, packets, traces, protocol):
    try:
        return _audit(summary, packets, traces, protocol)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError, ValueError, OverflowError) as error:
        raise EvidenceError("malformed_candidate_recovery_history:"+str(error)) from error
