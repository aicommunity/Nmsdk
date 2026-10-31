"""Clock-only entry seam; imported finished state, not live Train dispatch."""
from copy import deepcopy

from .finalization_boundary_evidence import _comparable, audit_boundary
from .finalization_ownership_evidence import _replay_source
from .native_evidence import EvidenceError, equal, number, require
from .recognition_evidence import audit_recognition_source

FIELDS={"kind","schema_version","boundary","recognition_package","calculate_mode","capture_time","entry_time",
        "clock_only_advance","live_train_handoff_implemented","scientific_verdict"}


def audit_clock_projection(record, projection):
    """Allow only the existing empty feedback-cache transition before the clock.

    Clock advancement itself must preserve the complete serialized boundary.
    Hash validation precedes the narrowly shared XML normalization.
    """
    try:
        require(type(projection) is dict and set(projection) ==
                {"initial", "repeat_without_clock", "after_clock"}, "unknown_clock_projection")
        initial, repeated, after = (projection[key] for key in
                                   ("initial", "repeat_without_clock", "after_clock"))
        for boundary in (initial, repeated, after):
            audit_boundary(boundary)
        require(initial == record["boundary"], "clock_projection_source_mismatch")
        require(repeated == after, "clock_advance_changed_boundary")
        before, repeat = deepcopy(initial), deepcopy(repeated)
        before["source_solo"] = _comparable(before["source_solo"])
        repeat["source_solo"] = _comparable(repeat["source_solo"])
        del before["sha256"], repeat["sha256"]
        require(before == repeat, "repeated_capture_changed_model")
        return {"boundary_projections_checked": 3, "clock_boundary_byte_values_equal": True,
                "repeated_export_cache_rule": "existing_empty_feedback_to_zero_only",
                "scientific_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise EvidenceError("malformed_clock_projection:" + str(error)) from error


def audit_clock_handoff(record, original_source_case):
    try:
        require(type(record) is dict and set(record)==FIELDS and record["kind"]=="native_finalization_clock_handoff" and
                type(record["schema_version"]) is int and record["schema_version"]==1,"unknown_clock_handoff_record")
        require(record["clock_only_advance"] is True and record["live_train_handoff_implemented"] is False and
                record["scientific_verdict"] is None,"unsupported_clock_handoff_claim")
        require(type(record["calculate_mode"]) is int and record["calculate_mode"] in (0,1),"invalid_clock_handoff_mode")
        boundary=record["boundary"];audit_boundary(boundary)
        require(boundary["diagnostic_only"] is False,"clock_handoff_requires_completed_boundary")
        solo=boundary["source_solo"];frequency=number(solo["configuration"]["model"]["frequency_hz"])
        begin,end=number(record["capture_time"]),number(record["entry_time"])
        require(begin>=0 and frequency>0 and equal(end-begin,1/frequency),"clock_handoff_not_one_outer_step")
        require(boundary["controls"]["parameters"]["CalculateMode"]==record["calculate_mode"] and
                solo["calculate_mode"]==record["calculate_mode"],"clock_handoff_mode_mismatch")
        require(_replay_source(solo)==_replay_source(original_source_case[0],record["calculate_mode"]),
                "clock_handoff_original_source_mismatch")
        package=record["recognition_package"]
        require(package["source_solo"]==solo,"clock_handoff_conversion_source_changed")
        audit=audit_recognition_source(package,(solo,*original_source_case[1:]))
        return {"schema_version":1,"clock_record_consistent":True,"conversion_audit":audit,
                "native_clock_only_execution_attested":False,"live_train_handoff_implemented":False,"scientific_verdict":None}
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,OverflowError,ZeroDivisionError) as error:
        raise EvidenceError("malformed_clock_handoff_record:"+str(error)) from error
