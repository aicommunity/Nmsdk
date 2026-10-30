"""Independently derive the native nonspiking LTZone bracket from primary frames."""
from fractions import Fraction
import math

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, number, require
from .recognition_metrics import score_threshold_candidate
from .threshold_candidate_evidence import audit_threshold_candidate

FIELDS = {"kind", "schema_version", "algorithm", "model_revision", "training_pattern_hash",
          "threshold_potential_path", "threshold_potential_class", "minimum_threshold", "maximum_threshold",
          "anchor", "begin_offset", "end_offset", "reject_target_outside_window", "target_minimum_inside",
          "foil_maximum_full", "target_maximum_outside", "lower_bound", "upper_bound", "threshold", "status",
          "trials", "calibrated", "evaluation_verdict", "sha256"}


def audit_threshold_proposal(proposal, expected_spec, observations, characterization, source_case, *, minimum_threshold, maximum_threshold):
    try:
        require(type(proposal) is dict and set(proposal) == FIELDS and
                proposal["kind"] == "timelearner_threshold_proposal" and type(proposal["schema_version"]) is int and
                proposal["schema_version"] == 1 and proposal["algorithm"] == "nonspiking-native-ltz-bracket-v1" and
                proposal["calibrated"] is False and proposal["evaluation_verdict"] is None, "unknown_threshold_proposal")
        require(proposal["sha256"] == canonical_model_sha256({k: v for k, v in proposal.items() if k != "sha256"}),
                "threshold_proposal_digest_mismatch")
        source_audit = audit_threshold_candidate(characterization, source_case)
        scored = score_threshold_candidate(expected_spec, observations, characterization)
        require(scored["validity"] == "valid" and all(o["schema_version"] == 2 and o["spike_count"] == 0 for o in observations),
                "threshold_proposal_requires_complete_nonspiking_characterization")
        criterion = expected_spec["criterion"]
        require(type(proposal["reject_target_outside_window"]) is bool, "invalid_threshold_proposal_boolean")
        require(all(proposal[key] == criterion[key] for key in ("anchor", "begin_offset", "end_offset", "reject_target_outside_window")),
                "threshold_proposal_criterion_changed")
        require(proposal["model_revision"] == characterization["model_revision"] and
                proposal["training_pattern_hash"] == characterization["source_recognition"]["source_solo"]["protocol"]["pattern_hash"],
                "threshold_proposal_source_mismatch")
        lower_limit, upper_limit = number(proposal["minimum_threshold"]), number(proposal["maximum_threshold"])
        require(0 < lower_limit <= upper_limit and lower_limit == number(minimum_threshold) and upper_limit == number(maximum_threshold),
                "invalid_threshold_proposal_bounds")
        for key in ("target_minimum_inside", "foil_maximum_full", "target_maximum_outside", "lower_bound", "upper_bound", "threshold"):
            if proposal[key] is not None:number(proposal[key])
        require(type(proposal["trials"]) is list and all(type(row) is dict for row in proposal["trials"]), "invalid_threshold_proposal_trials")
        for row in proposal["trials"]:
            for key in ("begin", "end", "response_begin", "response_end", "maximum_inside", "maximum_outside", "maximum_full"):
                if row[key] is not None:number(row[key])
        target_inside, foil_full, target_outside, records = [], [], [], []
        for observation in sorted(observations, key=lambda o: (o["run_id"], o["trial_id"])):
            source = observation["threshold_potential_source"]
            require(source["path"] == proposal["threshold_potential_path"] and source["class"] == proposal["threshold_potential_class"],
                    "threshold_proposal_metric_source_changed")
            anchor = observation["stimulus_times"][0 if criterion["anchor"] == "onset" else -1]
            begin = anchor+number(criterion["begin_offset"])
            end = observation["end"] if criterion["end_offset"] is None else anchor+number(criterion["end_offset"])
            inside, outside, full = [], [], []
            for sample in observation["samples"]:
                value = number(sample["lt_potential"]);full.append(value)
                (outside if after(begin, sample["time"]) or after(sample["time"], end) else inside).append(value)
            require(bool(inside), "missing_threshold_proposal_response_samples")
            if observation["label"] == "target":
                target_inside.append(max(inside));target_outside.extend(outside)
            else:foil_full.extend(full)
            records.append({"run_id": observation["run_id"], "trial_id": observation["trial_id"],
                "sample_id": observation["sample_id"], "label": observation["label"], "pattern_hash": observation["pattern_hash"],
                "begin": observation["begin"], "end": observation["end"], "response_begin": begin, "response_end": end,
                "maximum_inside": max(inside), "maximum_outside": max(outside) if outside else None,
                "maximum_full": max(full), "observation_sha256": canonical_model_sha256(observation)})
        require(bool(target_inside) and bool(foil_full), "incomplete_threshold_proposal_labels")
        target, foil = min(target_inside), max(foil_full)
        outside = max(target_outside) if target_outside else None
        lower = max(lower_limit, foil, outside if criterion["reject_target_outside_window"] and outside is not None else lower_limit)
        upper = min(upper_limit, target)
        # Correctly rounded binary64 midpoint without overflowing a+b.
        middle = float((Fraction(lower)+Fraction(upper))/2)
        def permitted(value):
            return (math.isfinite(value) and lower_limit <= value <= upper_limit and value > foil and value < target and
                    (not criterion["reject_target_outside_window"] or outside is None or value > outside))
        threshold = next((value for value in (middle, lower_limit, upper_limit) if permitted(value)), None)
        status = "proposed" if threshold is not None else "no_representable_threshold" if lower < upper else "no_measured_gap"
        expected = {"target_minimum_inside": target, "foil_maximum_full": foil, "target_maximum_outside": outside,
                    "lower_bound": lower, "upper_bound": upper, "threshold": threshold, "status": status, "trials": records}
        require(all(proposal[key] == value for key, value in expected.items()), "threshold_proposal_not_derived_from_primary_potential")
        return {"schema_version": 1, "proposal_math_verified": True, "source_audit": source_audit,
                "trials": len(records), "status": status, "threshold": threshold,
                "native_execution_verified": False, "calibrated": False, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_threshold_proposal:"+str(error)) from error
