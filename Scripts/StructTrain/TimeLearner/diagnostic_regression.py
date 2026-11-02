"""Declared fresh-process diagnostics of actual public stopped Train runs.

This is a pipeline regression, not a scientific classification campaign.
"""
import copy
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

from .native_calibration_worker import _signed, _write
from .native_evidence import load, number, require
from .native_pipeline_worker import audit_run_manifest, run_job
from .process_runner import execute, verify_runtime
from .stopped_evidence import audit_stopped_state, load_case


def run_diagnostic_regression(specification, output):
    specification = Path(specification).resolve(strict=True); spec = load(specification)
    require(set(spec) == {"kind", "schema_version", "training_runs", "runtime_manifest", "maximum_wall_seconds"}
            and spec["kind"] == "timelearner_diagnostic_evaluation_regression"
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1
            and type(spec["training_runs"]) is dict and set(spec["training_runs"]) == {"Classic", "Branch"},
            "unknown_diagnostic_regression_spec")
    def path(value):
        require(type(value) is str and bool(value), "invalid_diagnostic_regression_path")
        actual = Path(value)
        return (actual if actual.is_absolute() else specification.parent/actual).resolve(strict=True)
    runtime = load(path(spec["runtime_manifest"])); executable = verify_runtime(runtime)
    wall = number(spec["maximum_wall_seconds"]); require(wall > 0, "invalid_diagnostic_wall_budget")
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=False)
    inputs = output/"input"; inputs.mkdir(); results = output/"runs"; results.mkdir()
    _write(output/"runtime.json", runtime); _write(output/"specification.json", spec)
    positive, interrupted, negative = {}, {}, {}
    for topology in ("Classic", "Branch"):
        original = path(spec["training_runs"][topology])
        source_audit = audit_run_manifest(original)
        require(source_audit["operation"] == "train", "diagnostic_source_is_not_train")
        manifest = load(original)
        require(manifest["analysis"]["completed_boundary"] is False, "diagnostic_source_train_is_completed")
        source_root = original.parent
        require(all(not p.is_symlink() for p in source_root.rglob("*")), "diagnostic_source_contains_symlinks")
        copied = inputs/("source-"+topology); shutil.copytree(source_root, copied)
        audit_run_manifest(copied/original.name)
        source = copied/"native/train_stopped_state.json"; source_case = load_case(source)
        audit_stopped_state(*source_case); package = source_case[0]
        require(package["configuration"]["model"]["branch"] is (topology == "Branch"), "diagnostic_source_topology_changed")
        frequency = package["configuration"]["model"]["frequency_hz"]
        target = package["configuration"]["model"]["initial_isi"]
        foil = list(target); foil[-1] += .01
        requests = []
        from .model_identity import canonical_model_sha256
        for i, pattern in enumerate((target, foil, foil, target)):
            duration = math.ceil((sum(pattern)+.06)*frequency)/frequency
            requests.append({"run_id": "diagnostic-"+topology, "trial_id": "trial-"+str(i),
                "sample_id": "target" if i in (0, 3) else "foil", "label": "target" if i in (0, 3) else "foil",
                "pattern_isi": pattern, "pattern_hash": canonical_model_sha256(pattern), "duration": duration,
                "maximum_samples": round(duration*frequency)+2, "reset_policy": "reset_per_trial",
                "record_threshold_potential": False})
        base = {"kind": "timelearner_native_diagnostic_evaluation_job", "schema_version": 1,
            "owner_class": "NNeuronTimeLearner"+("Branch" if topology == "Branch" else ""),
            "implementation_id": package["implementation_id"], "source_stopped": package,
            "conversion_spec": {"schema_version": 1, "mode": "identity", "resistance_bounds": []},
            "maximum_model_ticks": sum(round(t["duration"]*frequency)+4 for t in requests),
            "run_id": "diagnostic-"+topology, "coverage_policy": "per_trial_windows",
            "criterion": {"id": "post_anchor_target_whole_window_foil_v1", "anchor": "last_stimulus",
                "begin_offset": 0., "end_offset": None, "reject_target_outside_window": True}, "trials": requests}
        for stop in (False, True):
            job = copy.deepcopy(base)
            if stop: job["maximum_model_ticks"] = 1
            job = _signed(job); name = topology+("-interrupted" if stop else "-completed")
            job_file = inputs/(name+".json"); _write(job_file, job); run = results/name
            if topology == "Classic" and not stop:
                # Exercise the public CLI from outside its repository too.
                foreign = output/"foreign-cwd"; foreign.mkdir()
                environment = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[3]))
                arguments = [sys.executable, "-m", "Scripts.StructTrain.TimeLearner", "diagnostic-evaluate", str(job_file),
                    "--source-stopped", str(source), "--runtime-manifest", str(output/"runtime.json"),
                    "--wall-seconds", str(wall), "--output", str(run)]
                _write(output/"cli-request.json", {"arguments": arguments, "cwd": str(foreign), "PYTHONPATH": environment["PYTHONPATH"]})
                with (output/"cli-stdout.log").open("xb") as so, (output/"cli-stderr.log").open("xb") as se:
                    process = subprocess.run(arguments, cwd=foreign, env=environment, stdout=so, stderr=se, timeout=wall+120)
                require(process.returncode == 0, "diagnostic_public_cli_failed")
                result = load(run/"run-manifest.json")
            else:
                result = run_job("diagnostic-evaluate", job_file, source, output/"runtime.json", run, wall)
            check = audit_run_manifest(run/"run-manifest.json")
            require(result["schema_version"] == 3 and result["analysis"]["diagnostic_only"] is True
                    and result["analysis"]["source_diagnostic_audit"]["training_outcome"] == package["training_outcome"]
                    and result["validity"] == "valid" and result["evaluation_verdict"] is None,
                    "diagnostic_run_lost_stopped_provenance")
            if stop:
                require(result["execution"] == "process_error" and result["analysis"]["metrics"] is None
                        and load(run/"native/execution.json")["execution"] == "model_tick_budget_exhausted",
                        "diagnostic_partial_execution_claimed_completion")
                interrupted[topology] = check
            else:
                metrics = result["analysis"]["metrics"]
                require(result["execution"] == "completed" and metrics["validity"] == "valid"
                        and metrics["diagnostic_only"] is True and metrics["training_completed"] is False
                        and metrics["training_certificate_present"] is False and metrics["evaluation_verdict"] is None,
                        "diagnostic_response_claimed_completed_training")
                positive[topology] = check
        # The real ordinary Console entry point must reject the diagnostic model.
        normal = {k: v for k, v in base.items() if k not in {"source_stopped", "conversion_spec"}}
        normal["kind"] = "timelearner_native_evaluation_job"
        normal["source_recognition"] = load(results/(topology+"-completed")/"native/model.json")
        ordinary = inputs/(topology+"-ordinary-rejected.json"); _write(ordinary, _signed(normal))
        destination = results/(topology+"-ordinary-rejected")
        process = execute(runtime, ["--app-ini", runtime["app_ini"]["path"], "--timelearner-evaluate", str(ordinary),
            "--timelearner-output", str(destination)], executable.parent, results/(topology+"-rejection-process"), wall)
        stderr = (results/(topology+"-rejection-process")/"stderr.log").read_text()
        require(process["execution"] == "process_error" and process["returncode"] == 2
                and "evaluation_requires_frozen_model_not_candidate" in stderr and not destination.exists(),
                "ordinary_console_accepted_diagnostic_model")
        negative[topology] = {"ordinary_native_rejected": True, "scientific_verdict": None}
    verify_runtime(runtime)
    result = {"kind": spec["kind"]+"_result", "schema_version": 1, "execution": "completed",
        "complete_diagnostic": positive, "interrupted_diagnostic": interrupted, "ordinary_rejections": negative,
        "diagnostic_only": True, "scientific_verdict": None}
    _write(output/"result.json", result)
    return result
