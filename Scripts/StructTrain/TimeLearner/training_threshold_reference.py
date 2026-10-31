"""Independent target-only Solo threshold proposal replay; no calibration PASS."""
import math

from .model_identity import canonical_model_sha256
from .native_evidence import number, require
from .solo_threshold_evidence import audit_solo_threshold_trace


def audit_training_threshold_reference(proposal, trace):
    audit = audit_solo_threshold_trace(trace)
    p = proposal
    require(type(p) is dict and p.get("kind") == "native_training_threshold_reference"
            and type(p.get("schema_version")) is int and p["schema_version"] == 1,
            "unknown_training_threshold_reference")
    require(p.get("mode") in ("gap_fraction", "peak_fraction"), "unknown_training_threshold_mode")
    fraction, minimum, maximum = (number(p[k]) for k in ("fraction", "minimum_threshold", "maximum_threshold"))
    require(minimum <= maximum and type(p.get("current_model_revision")) is str
            and bool(p["current_model_revision"]), "invalid_training_threshold_specification")
    expected = {"kind": "native_training_threshold_reference", "schema_version": 1,
                "source_trace_sha256": trace["sha256"],
                "source_model_revision": trace["source"].get("base_model_revision", ""),
                "current_model_revision": p["current_model_revision"], "mode": p["mode"],
                "fraction": fraction, "minimum_threshold": minimum, "maximum_threshold": maximum,
                "sample_selection": "strictly_positive_after_children", "minimum_span": 1e-9,
                "positive_samples": 0, "positive_minimum": None, "positive_maximum": None,
                "unclamped_threshold": None, "threshold": None, "clipped": False,
                "reason": "source_not_eligible", "requires_spiking_confirmation": True,
                "calibrated": False, "evaluation_verdict": None}
    if audit["proposal_eligible"]:
        if p["current_model_revision"] != expected["source_model_revision"]:
            expected["reason"] = "source_model_changed"
        else:
            positive = [f["lt_potential"] for f in trace["samples"] if f["lt_potential"] > 0]
            low, high = (min(positive), max(positive)) if positive else (None, None)
            expected.update(positive_samples=len(positive), positive_minimum=low, positive_maximum=high)
            if low is None or high <= low+1e-9:
                expected["reason"] = "insufficient_positive_span"
            else:
                raw = high*fraction if p["mode"] == "peak_fraction" else low+fraction*(high-low)
                if not math.isfinite(raw):
                    expected["reason"] = "nonfinite_threshold_proposal"
                else:
                    value = max(minimum, min(maximum, raw))
                    expected.update(unclamped_threshold=raw, threshold=value, clipped=value != raw,
                                    reason="proposed_unconfirmed")
    expected["sha256"] = canonical_model_sha256(expected)
    require(p == expected, "training_threshold_reference_replay_mismatch")
    return {"schema_version": 1, "threshold": expected["threshold"], "reason": expected["reason"],
            "source_trace_sha256": trace["sha256"], "requires_spiking_confirmation": True,
            "native_execution_attested": False, "calibrated": False, "evaluation_verdict": None}


def audit_solo_threshold_confirmation(proposal, source_trace, confirmation):
    result = audit_training_threshold_reference(proposal, source_trace)
    actual = audit_solo_threshold_trace(confirmation)
    require(result["threshold"] is not None and actual["complete"] and actual["valid"],
            "incomplete_solo_threshold_confirmation")
    require(confirmation["source"]["threshold"] == result["threshold"], "confirmation_threshold_mismatch")
    q, c = source_trace["requested_specification"], confirmation["requested_specification"]
    require(q["pattern_hash"] == c["pattern_hash"] and q["sample_id"] == c["sample_id"]
            and q["windows"] == c["windows"] and q["stimulus_profile"] == c["stimulus_profile"]
            and q["end"]-q["begin"] == c["end"]-c["begin"]
            and (q["run_id"], q["trial_id"]) != (c["run_id"], c["trial_id"]),
            "confirmation_protocol_mismatch")
    return {"schema_version": 1, "scope": "solo_training_burst", "threshold": result["threshold"],
            "spikes": actual["spikes"], "source_trace_sha256": source_trace["sha256"],
            "confirmation_trace_sha256": confirmation["sha256"],
            "same_physics_except_threshold_attested": False,
            "recognition_confirmation_required": True, "calibrated": False, "evaluation_verdict": None}
