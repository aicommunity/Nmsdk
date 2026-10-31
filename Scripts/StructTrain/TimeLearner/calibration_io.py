"""Portable calibration measurements; references must remain inside the bundle."""
from pathlib import Path

from .native_evidence import EvidenceError, load, require
from .recognition_metrics import load_evaluation


def _reference(root, name):
    require(type(name) is str and bool(name) and "\\" not in name,
            "invalid_calibration_file_reference")
    relative = Path(name)
    require(not relative.is_absolute() and ":" not in name and ".." not in relative.parts,
            "invalid_calibration_file_reference")
    target = (root/relative).resolve(strict=True)
    require(target.is_relative_to(root) and target.is_file(), "calibration_file_reference_escapes_bundle")
    return target


def load_measurements(path):
    """Load actual candidate/evaluation/primary files, not serialized score claims."""
    try:
        path = Path(path).resolve(strict=True)
        value = load(path)
        require(type(value) is dict and set(value) == {"kind", "schema_version", "measurements"} and
                value["kind"] == "timelearner_threshold_measurement_set" and
                type(value["schema_version"]) is int and value["schema_version"] == 1 and
                type(value["measurements"]) is list and bool(value["measurements"]),
                "unknown_calibration_measurement_set")
        result = []
        for row in value["measurements"]:
            require(type(row) is dict and set(row) == {"candidate", "evaluation", "execution"},
                    "unknown_calibration_measurement_reference")
            evaluation, observations = load_evaluation(_reference(path.parent, row["evaluation"]))
            result.append({"candidate": load(_reference(path.parent, row["candidate"])),
                           "evaluation_spec": evaluation, "observations": observations,
                           "execution": row["execution"]})
        return result
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise EvidenceError("malformed_calibration_measurement_set:"+str(error)) from error
