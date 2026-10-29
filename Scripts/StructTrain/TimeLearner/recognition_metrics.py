"""Versioned label/ID based metrics over a declared complete frozen trial set.

Computes response criteria, not simulator execution/provenance or convergence.
Historical CSV scores remain separate; this format never rewrites their meaning.
"""
from collections import defaultdict
from pathlib import Path

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, after, count, equal, load, number, require
from .recognition_trial_evidence import audit_recognition_trial
from .recognition_evidence import _physical

SPEC_FIELDS = {"kind", "schema_version", "run_id", "model_revision", "coverage_policy", "criterion", "trials"}
TRIAL_FIELDS = {"trial_id", "sample_id", "label", "pattern_hash", "reset_policy", "presentation_index", "duration", "observation"}
CRITERION_FIELDS = {"id", "anchor", "begin_offset", "end_offset", "reject_target_outside_window"}


def _counts(rows):
    counts = {key: sum(row["classification"] == key for row in rows) for key in ("TP", "FP", "FN", "TN")}
    targets, foils = counts["TP"]+counts["FN"], counts["FP"]+counts["TN"]
    outside = sum(row["label"] == "target" and bool(row["early_spikes"] or row["late_spikes"]) for row in rows)
    return {**counts, "targets": targets, "foils": foils, "target_trials_with_outside_spikes": outside,
            "accuracy": (counts["TP"]+counts["TN"])/len(rows),
            "target_hit_rate": counts["TP"]/targets if targets else None,
            "foil_response_rate": counts["FP"]/foils if foils else None}


def score_recognition_evaluation(spec, observations, package):
    try:
        require(set(spec) == SPEC_FIELDS and spec["kind"] == "timelearner_recognition_evaluation_spec"
                and type(spec["schema_version"]) is int and spec["schema_version"] == 1, "unknown_evaluation_spec")
        require(type(spec["run_id"]) is str and bool(spec["run_id"]) and spec["model_revision"] == package["model_revision"],
                "evaluation_model_or_run_mismatch")
        require(spec["coverage_policy"] in ("per_trial_windows", "continuous_native_stream"), "unknown_evaluation_coverage")
        criterion = spec["criterion"]
        require(type(criterion) is dict and set(criterion) == CRITERION_FIELDS and
                criterion["id"] == "post_anchor_target_whole_window_foil_v1" and
                criterion["anchor"] in ("onset", "last_stimulus") and
                type(criterion["reject_target_outside_window"]) is bool, "unknown_response_criterion")
        start = number(criterion["begin_offset"])
        stop = None if criterion["end_offset"] is None else number(criterion["end_offset"])
        require(start >= 0 and (stop is None or stop >= start), "invalid_response_window")
        require(type(spec["trials"]) is list and len(spec["trials"]) >= 2, "incomplete_evaluation_design")
        expected, positions, samples = {}, set(), {}
        target_hash = canonical_model_sha256(package["source_solo"]["configuration"]["model"]["initial_isi"])
        for trial in spec["trials"]:
            require(type(trial) is dict and set(trial) == TRIAL_FIELDS, "unknown_expected_trial_fields")
            for key in ("trial_id", "sample_id", "pattern_hash", "observation"):
                require(type(trial[key]) is str and bool(trial[key]), "invalid_expected_trial_identity")
            require(trial["trial_id"] not in expected and trial["label"] in ("target", "foil")
                    and trial["reset_policy"] in ("reset_per_trial", "preserve_neuron_dynamics"), "invalid_or_duplicate_expected_trial")
            require((trial["label"] == "target") == (trial["pattern_hash"] == target_hash), "target_label_pattern_mismatch")
            position = count(trial["presentation_index"])
            require(position not in positions and number(trial["duration"]) > 0, "invalid_evaluation_position_or_duration")
            positions.add(position);expected[trial["trial_id"]] = trial
            signature = trial["label"], trial["pattern_hash"]
            require(trial["sample_id"] not in samples or samples[trial["sample_id"]] == signature, "sample_id_collision")
            samples[trial["sample_id"]] = signature
        require(positions == set(range(len(expected))) and {t["label"] for t in expected.values()} == {"target", "foil"},
                "incomplete_evaluation_positions_or_labels")
        actual, audits = {}, {}
        for observation in observations:
            audit = audit_recognition_trial(observation, package)
            trial_id = audit["trial_id"]
            require(audit["run_id"] == spec["run_id"] and trial_id in expected and trial_id not in actual,
                    "unexpected_or_duplicate_evaluation_trial")
            wanted = expected[trial_id]
            require(all(observation[key] == wanted[key] for key in ("sample_id", "label", "pattern_hash", "reset_policy")),
                    "evaluation_trial_metadata_mismatch")
            if observation["armed"]:
                require(equal(observation["end"], number(observation["begin"])+number(wanted["duration"])),
                        "evaluation_trial_duration_mismatch")
            actual[trial_id], audits[trial_id] = observation, audit
        require(set(actual) == set(expected), "missing_evaluation_trial")
        invalid = sorted(key for key, audit in audits.items() if not audit["valid_observation"])
        calibration = package["neuron"]["metadata"]["calibration"]
        source = package["source_solo"]
        require(calibration["status"] == "fixed" and calibration["protocol"] == "fixed-inherited-from-solo"
                and calibration["source_solo_sha256"] == source["sha256"], "unsupported_evaluation_calibration_claim")
        zones = [node for node in package["neuron"]["graph"]["identity"]["model"]["nodes"]
                 if node["path"] == calibration["ltzone_path"]]
        require(len(zones) == 1 and equal(_physical(zones[0], "Threshold"), calibration["threshold"]),
                "evaluation_effective_threshold_mismatch")
        # File locations and row order are not the semantic identity of the spec.
        semantic = {**spec, "trials": [{key: t[key] for key in t if key != "observation"}
                                       for t in sorted(expected.values(), key=lambda t: t["trial_id"])]}
        result = {"schema_version": 1, "criterion": criterion, "evaluation_spec_digest": canonical_model_sha256(semantic),
                  "coverage_policy": spec["coverage_policy"], "run_id": spec["run_id"], "model_revision": spec["model_revision"],
                  "declared_training_outcome": source["training_outcome"], "source_training_evidence_checked": False,
                  "calibration": calibration, "native_execution_verified": False,
                  "evaluation_verdict": None, "invalid_trial_ids": invalid}
        if invalid:
            return {**result, "validity": "invalid", "reason": "invalid_or_censored_trial", "pooled_counts": None,
                    "by_reset_policy": {}, "trials": []}
        ordered = sorted(expected.values(), key=lambda t: t["presentation_index"])
        rows, previous = [], None
        for wanted in ordered:
            observation = actual[wanted["trial_id"]]
            if previous is not None:
                require(after(observation["begin"], previous["end"]), "overlapping_or_reordered_evaluation_windows")
                if spec["coverage_policy"] == "continuous_native_stream":
                    require(equal(observation["frequency_hz"], previous["frequency_hz"]) and
                            equal(observation["begin"], number(previous["end"])+1/number(previous["frequency_hz"])),
                            "unobserved_continuous_stream_gap")
            previous = observation
            anchor = observation["stimulus_times"][0 if criterion["anchor"] == "onset" else -1]
            begin = number(anchor)+start
            end = number(observation["end"]) if stop is None else number(anchor)+stop
            require(not after(begin, end) and not after(end, observation["end"]), "response_window_outside_observation")
            early = [t for t in observation["spike_times"] if after(begin, t)]
            late = [t for t in observation["spike_times"] if after(t, end)]
            hits = [t for t in observation["spike_times"] if not after(begin, t) and not after(t, end)]
            target = wanted["label"] == "target"
            classification = ("TP" if hits else "FN") if target else ("FP" if observation["spike_times"] else "TN")
            rows.append({"trial_id": wanted["trial_id"], "sample_id": wanted["sample_id"], "label": wanted["label"],
                         "presentation_index": wanted["presentation_index"], "reset_policy": wanted["reset_policy"],
                         "response_begin": begin, "response_end": end, "spike_count": observation["spike_count"],
                         "window_spikes": hits, "early_spikes": early, "late_spikes": late, "classification": classification})
        groups = defaultdict(list)
        for row in rows:
            groups[row["reset_policy"]].append(row)
        metrics = {}
        for policy, items in groups.items():
            counts = _counts(items)
            supported = bool(counts["targets"] and counts["foils"])
            satisfied = (counts["FN"] == counts["FP"] == 0 and
                         (not criterion["reject_target_outside_window"] or counts["target_trials_with_outside_spikes"] == 0))
            metrics[policy] = {**counts, "criterion_satisfied": satisfied if supported else None,
                               "criterion_assessed": supported}
        return {**result, "validity": "valid", "reason": "complete_declared_evaluation",
                "pooled_counts": _counts(rows), "by_reset_policy": dict(metrics), "trials": rows}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_recognition_evaluation:" + str(error)) from error


def load_evaluation(path: Path):
    spec = load(path)
    require(set(spec) == SPEC_FIELDS and spec.get("kind") == "timelearner_recognition_evaluation_spec"
            and type(spec.get("schema_version")) is int and spec["schema_version"] == 1
            and type(spec.get("trials")) is list, "unknown_evaluation_spec")
    root = path.resolve(strict=True).parent
    observations = []
    for trial in spec.get("trials", []):
        require(type(trial) is dict, "invalid_evaluation_trial")
        relative = trial.get("observation")
        require(type(relative) is str and relative and "\\" not in relative and ":" not in relative
                and not Path(relative).is_absolute() and ".." not in Path(relative).parts, "invalid_evaluation_artifact_path")
        actual = (root/relative).resolve(strict=True)
        require(actual.is_relative_to(root), "evaluation_artifact_outside_root")
        observations.append(load(actual))
    return spec, observations
