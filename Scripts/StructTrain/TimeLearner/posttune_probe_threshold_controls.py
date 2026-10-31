"""Regression controls for explicit measurement physics; no prescribed science outcome."""
import argparse
import copy
import json
from pathlib import Path

from .model_identity import canonical_model_sha256 as sha
from .native_calibration_worker import audit_run_manifest
from .native_evidence import load, number, require
from .process_runner import execute, verify_runtime


CASES = {"Classic": "Classic-auto_metric", "Branch": "Branch-synthetic"}
VARIANTS = ("legacy", "inherited", "fixed-probe", "calibrated-probe")


def derive_jobs(original, probe_threshold=2.):
    """Keep original trials/budgets; declare each independent change explicitly."""
    number(probe_threshold)
    result = {}
    for variant in VARIANTS:
        job = copy.deepcopy(original)
        if variant != "legacy":
            job["schema_version"] = 3
            job["post_tune"].update(schema_version=3, finalization="calibrate", weight_probe_threshold=None)
        if variant in {"fixed-probe", "calibrated-probe"}:
            job["post_tune"].update(weight_probe_threshold=probe_threshold, mode="keep_done",
                                    canonical_floor=0., canonical_last=0., resistance_bounds=[])
            if variant == "fixed-probe":
                job["post_tune"]["finalization"] = "keep_fixed_threshold"
                job.update(thresholds=[], maximum_candidates=0)
        job["sha256"] = sha({k: v for k, v in job.items() if k != "sha256"})
        result[variant] = job
    return result


def audit_cases(runs, original_runs, probe_threshold=2.):
    """Replay actual portable runs and A/B bytes, without predicting Branch success."""
    runs, original_runs = Path(runs), Path(original_runs)
    records = []
    for topology, source_name in CASES.items():
        source = original_runs/(source_name+"-legacy")
        audit_run_manifest(source/"run-manifest.json", post_tune=True)
        jobs = derive_jobs(load(source/"input/job.json"), probe_threshold)
        for variant, expected in jobs.items():
            folder = runs/(topology+"-"+variant)
            proof = audit_run_manifest(folder/"run-manifest.json", post_tune=True)
            manifest = load(folder/"run-manifest.json")
            require(manifest["execution"] == "completed" and proof["run_evidence_consistent"], "incomplete_probe_threshold_control")
            require(load(folder/"input/job.json") == expected, "probe_threshold_control_conditions_changed")
            report = load(folder/"native/transaction.json")
            if variant in {"legacy", "inherited"}:
                for name in ("transaction.json", "model.json"):
                    require((folder/"native"/name).read_bytes() == (source/"native"/name).read_bytes(),
                            "probe_threshold_legacy_or_inherited_bytes_changed")
            # The production auditor already checks model/observation identity,
            # fresh confirmation, budget, rollback and final-state binding.
            # Calibrated/nonseparable outcomes belong to the recorded model;
            # topology alone never determines which outcome is acceptable.
            records.append({"case": topology+"-"+variant, "status": report["status"],
                            "report_schema": report["schema_version"], "run_evidence_consistent": True})
    return {"kind": "post_tune_probe_threshold_control_audit", "schema_version": 1,
            "records": records, "predetermined_recognition_outcome": False,
            "independent_evaluation_verified": False, "scientific_verdict": None}


def malformed_controls(runs, runtime_path, output):
    """Exercise the actual Console parser; reject before a model output is reserved."""
    runs, output = Path(runs).resolve(strict=True), Path(output)
    runtime = load(Path(runtime_path));executable = verify_runtime(runtime)
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for topology in CASES:
        original = load(runs/(topology+"-fixed-probe")/"input/job.json")
        for name, value in (("bool", True), ("string", "2")):
            job = copy.deepcopy(original);job["post_tune"]["weight_probe_threshold"] = value
            job["sha256"] = sha({k: v for k, v in job.items() if k != "sha256"})
            path = output/(topology+"-"+name+".json")
            path.write_text(json.dumps(job, indent=2, allow_nan=False)+"\n", encoding="utf-8")
            target = output/(topology+"-"+name+"-native")
            process = execute(runtime, ["--app-ini", runtime["app_ini"]["path"], "--timelearner-posttune", str(path),
                                       "--timelearner-output", str(target)], executable.parent,
                              output/(topology+"-"+name+"-process"), 120)
            require(process["execution"] == "process_error" and process["returncode"] == 2 and not target.exists(),
                    "malformed_weight_threshold_was_not_rejected_before_output")
            records.append({"topology": topology, "invalid_type": name, "returncode": process["returncode"], "native_output_created": False})
    verify_runtime(runtime)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path)
    parser.add_argument("original_runs", type=Path)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--probe-threshold", type=float, default=2.)
    args = parser.parse_args()
    result = audit_cases(args.runs, args.original_runs, args.probe_threshold)
    args.output.mkdir(parents=True, exist_ok=False)
    result["malformed_controls"] = malformed_controls(args.runs, args.runtime, args.output/"negative")
    (args.output/"validation.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps(result, allow_nan=False))


if __name__ == "__main__":
    main()
