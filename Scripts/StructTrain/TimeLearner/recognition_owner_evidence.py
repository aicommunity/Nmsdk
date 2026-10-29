"""Read native learner recognition evidence through the common conversion audit.

The owner observation adds actual before/after model readbacks. Its explicitly
mapped paired-waveform fields retain the existing transport semantics; missing
measurements are never reconstructed from a package or a predicted model.
"""
from pathlib import Path

from .native_evidence import EvidenceError, count, equal, load, require
from .learned_evidence import load_case as load_solo
from .recognition_evidence import audit_recognition_state


def audit_owner_recognition(package, source_case, spec, observation, trace, imported, guard):
    try:
        require(observation.get("kind") == "native_recognition_owner_observation"
                and type(observation.get("schema_version")) is int and observation["schema_version"] == 1,
                "unknown_recognition_owner_schema")
        require(observation["recognition_certificate"] is None and observation["evaluation_verdict"] is None
                and observation["training_controller_installed"] is False and observation["need"] is False
                and observation["record_spikes"] is False, "recognition_owner_scope_mismatch")
        source = source_case[0]
        require(observation["source_solo_revision"] == source["model_revision"]
                and observation["source_solo_sha256"] == source["sha256"], "recognition_owner_source_mismatch")
        require(observation["frozen_before"] == observation["frozen_after_owner"]
                == observation["frozen_after_reference"] == observation["model_revision"] == package["model_revision"],
                "recognition_owner_physical_model_changed")
        require(count(observation["inputs"]) == len(package["recognition_inputs"])
                and count(observation["channels"]) == count(spec["channels"]), "recognition_owner_dimensions_mismatch")
        for key in ("begin", "end", "maximum_sample_gap"):
            require(equal(observation[key], spec[key]), "recognition_owner_window_mismatch")
        require(imported.get("kind") == "native_recognition_owner_import" and type(imported.get("schema_version")) is int
                and imported["schema_version"] == 1 and imported["status"] == "adopted" and imported["reason"] == ""
                and imported["installed"] is True and imported["model_may_have_changed"] is True
                and imported["evaluation_verdict"] is None, "recognition_owner_import_not_confirmed")
        require(guard.get("kind") == "native_recognition_owner_guard" and type(guard.get("schema_version")) is int
                and guard["schema_version"] == 1 and guard["physical_edit_detected"] is True
                and guard["reason"] == "native_recognition_model_changed" and guard["evaluation_verdict"] is None,
                "recognition_owner_negative_control_missing")
        require(observation["rejected_certificate_reason"] == "unsupported_recognition_state_claim",
                "recognition_owner_certificate_guard_missing")
        # Every mapped value is present in the original owner observation.
        # In particular, no frozen hash is inferred from the expected package.
        paired = {key: observation[key] for key in ("schema_version", "model_revision", "trial_id", "complete",
                  "sample_count", "last_sample_time", "emitted", "soma_variation", "maximum_soma")}
        paired.update(kind="native_recognition_roundtrip_observation", frozen_after=observation["frozen_after_owner"],
                      frozen_after_b=observation["frozen_after_reference"], scientific_verdict=observation["evaluation_verdict"])
        result = audit_recognition_state(package, source_case, spec, paired, trace)
        return {"schema_version": 1, "owner_readback_consistent": True,
                "conversion": result, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError("malformed_recognition_owner_evidence:" + str(error)) from error


def load_case(path: Path):
    require(path.name.endswith("_owner_recognition_state.json"), "unexpected_owner_recognition_filename")
    stem = path.name.removesuffix("_owner_recognition_state.json")
    base = stem + "_owner_recognition_"
    return (load(path), load_solo(path.with_name(stem + "_learned_state.json")),
            load(path.with_name(base + "probe_spec.json")), load(path.with_name(base + "observation.json")),
            path.with_name(base + "wave.csv"), load(path.with_name(base + "import.json")),
            load(path.with_name(base + "guard.json")))
