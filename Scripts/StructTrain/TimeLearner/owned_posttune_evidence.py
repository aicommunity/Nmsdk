"""Audit owner-driven phase receipts and replay the actual measured matrices.

A JSON receipt does not independently attest scheduler execution or process origin.
Original Train primaries remain required; an interrupted phase is never success.
"""
from .finalization_boundary_evidence import audit_boundary
from .finalization_ownership_evidence import _replay_source
from .learned_evidence import audit_learned_state
from .native_evidence import EvidenceError, equal, number, require
from .posttune_transaction_evidence import audit_posttune_transaction

FIELDS = {"kind", "schema_version", "boundary", "transaction", "execution", "selected_package",
          "calculate_mode", "connected", "interrupted", "configured_phase_dispatch_implemented", "scientific_verdict"}
EXECUTION = {"kind", "schema_version", "advance_phase", "frequency_hz", "advance_times", "internal_lifecycle",
             "done", "dynamic_checkpoint", "evaluation_verdict"}


def audit_owned_phase_execution(execution, frequency_hz, *, ticks=None, begin=None, end=None):
    """Validate a receipt; optional worker clock binds every recorded tick count.

    An unbound wrapper requires at least one tick. A cancelled production job
    can have zero ticks, but still requires the exact declared begin/end clock.
    This does not independently attest native scheduling or process origin.
    """
    require(type(execution) is dict and set(execution) == EXECUTION and
            execution["kind"] == "native_owned_post_tune_execution" and type(execution["schema_version"]) is int and
            execution["schema_version"] == 1 and execution["advance_phase"] == "owner_before_children" and
            execution["done"] is True and execution["dynamic_checkpoint"] is False and
            execution["evaluation_verdict"] is None, "invalid_owned_post_tune_execution")
    frequency = number(execution["frequency_hz"])
    require(frequency > 0 and frequency == number(frequency_hz), "owned_post_tune_frequency_mismatch")
    times = execution["advance_times"]
    require(type(times) is list and (bool(times) or ticks == 0), "missing_owned_post_tune_ticks")
    times = [number(t) for t in times]
    require((not times or times[0] >= 0) and all(b > a and equal(b-a, 1/frequency) for a, b in zip(times, times[1:])),
            "owned_post_tune_tick_sequence_mismatch")
    if ticks is not None:
        require(type(ticks) is int and ticks >= 0 and len(times) == ticks and
                equal(number(end)-number(begin), ticks/frequency) and
                (equal(times[0], begin) and equal(times[-1]+1/frequency, end) if times else equal(begin, end)),
                "owned_post_tune_worker_clock_mismatch")
    else:
        require(begin is None and end is None, "incomplete_owned_post_tune_worker_clock")
    internal = execution["internal_lifecycle"]
    require(type(internal) is dict and set(internal) <= {"learner_build", "learner_init", "learner_reset", "learner_uninit"}
            and all(type(n) is int and n > 0 for n in internal.values()), "invalid_owned_post_tune_internal_lifecycle")
    return {"recorded_phase_sequence_consistent": True, "ticks": len(times),
            "worker_clock_bound": ticks is not None, "native_scheduler_execution_attested": False}


def audit_owned_posttune(record, original_source_case):
    try:
        require(type(record) is dict and set(record) == FIELDS and
                record["kind"] == "native_owned_post_tune_control" and type(record["schema_version"]) is int and
                record["schema_version"] == 1, "unknown_owned_post_tune_record")
        require(record["scientific_verdict"] is None and record["configured_phase_dispatch_implemented"] is False,
                "unsupported_owned_post_tune_claim")
        require(type(record["calculate_mode"]) is int and record["calculate_mode"] in (0, 1) and
                type(record["connected"]) is bool and type(record["interrupted"]) is bool,
                "invalid_owned_post_tune_controls")
        boundary = record["boundary"]
        audit_boundary(boundary)
        controls = boundary["controls"]["parameters"]
        binding = boundary["controls"]["bindings"]["IsNeedToTrain"]
        require(boundary["diagnostic_only"] is False and controls["CalculateMode"] == record["calculate_mode"] and
                controls["IsNeedToTrain"] is True and controls["EnablePostTrainTuning"] is True and
                controls["AutoCalibrateFixedLTZThreshold"] is True,
                "owned_post_tune_request_mismatch")
        require(binding["connected"] is record["connected"] and
                (bool(binding["sources"]) if record["connected"] else not binding["external_data_source"]),
                "owned_post_tune_request_binding_mismatch")
        solo = boundary["source_solo"]
        require(solo["calculate_mode"] == record["calculate_mode"] and
                _replay_source(solo) == _replay_source(original_source_case[0], record["calculate_mode"]),
                "owned_post_tune_original_source_mismatch")
        source_case = (solo, *original_source_case[1:])
        learned = audit_learned_state(*source_case)
        execution = record["execution"]
        audit_owned_phase_execution(execution, solo["configuration"]["model"]["frequency_hz"])
        times, internal = execution["advance_times"], execution["internal_lifecycle"]
        report = record["transaction"]
        require(report["source_recognition"]["source_solo"] == solo, "owned_post_tune_transaction_source_mismatch")
        transaction = audit_posttune_transaction(report, source_case)
        if record["interrupted"]:
            require(len(times) == 3 and report["status"] == "recovery_required" and report["reason"] == "learner_reset" and
                    report["source_restored"] is False and record["selected_package"] == {},
                    "owned_post_tune_interrupt_claim_mismatch")
        else:
            require(bool(internal) and report["status"] == "weights_selected" and
                    record["selected_package"] == report["selected_package"], "owned_post_tune_selection_mismatch")
        return {"schema_version": 1, "recorded_phase_sequence_consistent": True, "ticks": len(times),
                "training_source_audit": learned, "transaction_audit": transaction,
                "native_scheduler_execution_attested": False, "scientific_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_owned_post_tune_record:"+str(error)) from error
