"""Cold native dimension controls; no synthetic peaks or imported learned state.

The single-input case checks identity convergence with a fresh physical final
probe. Larger cases intentionally fix geometry and keep widely spaced pulses:
they exercise dimensions and honest negative outcomes, not learnability of the
unrestricted physical model. Training tolerances are inherited unchanged.
"""
import argparse
import contextlib
from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import time

from ..__main__ import main as cli
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_execution, audit_run_manifest, validate_job
from .live_pipeline_corpus import signed, write


def make_dimension_job(template, topology, normalization, inputs):
    require(topology in ("Classic", "Branch") and normalization in ("N0", "N1")
            and type(inputs) is int and inputs in (1, 2, 4, 5), "dimension_control_factor")
    job = deepcopy(template)
    job.pop("finalization_plan", None)
    job["schema_version"] = 1  # Bare V2 Train: no recognition/calibration claim.
    job["calculate_mode"] = 0
    job["optional_modes"] = {"sync_capacitance_trim": 0,
                             "post_train_tuning": False, "auto_calibrate_threshold": False}
    config = job["configuration"]
    model, search = config["model"], config["search"]
    require(model["branch"] is (topology == "Branch"), "dimension_template_topology")
    config["schema_version"] = 1
    search.pop("n0_candidate_repeats", None)
    config["run_id"] = f"dimension-{topology}-{normalization}-N{inputs}"
    config["protocol_revision"] = "native_dimension_fixed_geometry_v1"
    model["normalization"] = normalization
    initial = deepcopy(model["inputs"][-1])
    initial.update(attachment=1, synapses=1)
    model["inputs"] = [deepcopy(initial) for _ in range(inputs)]
    model["initial_isi"] = [.01]+[.08]*(inputs-1)
    model["allocated_cable_lengths"] = [1]*(1 if model["branch"] else inputs)
    require(not model["inhibition"], "dimension_inhibition_profile_not_supported")
    model["preserve_allocated_cable"] = False
    duration = round(.18+.08*(inputs-1), 8)
    config["duration"] = duration
    config["windows"] = [{"begin": 0., "end": duration} for _ in range(inputs)]
    config["maximum_samples"] = int(duration*model["frequency_hz"])+20
    config["maximum_reference_probes"] = inputs
    config["maximum_model_seconds"] = 60.
    resistance = initial["resistance"]
    search["bounds"] = [dict(minimum_length=1, maximum_length=1,
                             minimum_synapses=1, maximum_synapses=1,
                             minimum_resistance=resistance, maximum_resistance=resistance)
                        for _ in range(inputs)]
    search.update(maximum_candidates_per_input=1, maximum_sweeps=1,
                  maximum_probes=64, maximum_edits=16, resistance_subdivision_depth=0)
    job["maximum_model_ticks"] = int(60*model["frequency_hz"])
    signed(job)
    validate_job("train", job)
    return job


def run(fixtures, runtime, output, dimensions, wall_seconds):
    fixtures, runtime, output = Path(fixtures), Path(runtime), Path(output)
    require(shutil.disk_usage(output.parent).free >= 2*1024**3, "dimension_primary_capacity")
    output.mkdir(exist_ok=False)
    (output/"jobs").mkdir()
    (output/"runs").mkdir()
    records = []
    started = time.time()
    for n in dimensions:
        for topology in ("Classic", "Branch"):
            template = load(fixtures/(topology+"-fixed")/"input/job.json")
            for normalization in ("N0", "N1"):
                job = make_dimension_job(template, topology, normalization, n)
                name = job["configuration"]["run_id"]
                path = output/"jobs"/(name+".json")
                write(path, job)
                print("BEGIN", name, flush=True)
                folder = output/"runs"/name
                with (output/(name+".log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                    code = cli(["train", str(path), "--runtime-manifest", str(runtime),
                                "--wall-seconds", str(wall_seconds), "--output", str(folder)])
                row = {"name": name, "inputs": n, "topology": topology,
                       "normalization": normalization, "cli_code": code}
                # Persist errors too; never replace failure by a fabricated observation.
                records.append(row)
                write(output/"progress.json", {"records": records})
                require(code == 0, "dimension_train_failed:"+name)
                row["manifest_audit"] = audit_run_manifest(folder/"run-manifest.json")
                row["execution_audit"] = audit_execution("train", folder/"native", job)
                execution = load(folder/"native/execution.json")
                require(execution["completed_boundary"], "dimension_training_not_finalized")
                summary = load(folder/"native/train_learned_summary.json")
                certificate = summary["certificate"]
                row.update(outcome=execution["training_outcome"], certificate=certificate,
                           actual_parameters=summary["actual_parameters"])
                require(len(certificate["residuals"]) == n and len(row["actual_parameters"]) == n,
                        "dimension_incomplete_final_gate")
                if n == 1:
                    require(certificate["exact"] and row["outcome"] == "exact",
                            "single_input_identity_failed_fresh_final_gate")
                write(output/"progress.json", {"records": records})
                print("END", name, row["outcome"], flush=True)
    result = {"kind": "native_dimension_controls", "schema_version": 1,
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "dimensions": dimensions, "records": records, "wall_seconds": time.time()-started,
              "scientific_classification_verdict": None,
              "single_input_control": "unchanged_model_fresh_final_measurement",
              "multiple_input_control": "fixed_geometry_spaced_burst"}
    write(output/"index.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dimensions", type=int, nargs="+", choices=(1, 2, 4, 5), default=[1])
    parser.add_argument("--wall-seconds", type=float, default=1800.)
    args = parser.parse_args()
    require(len(set(args.dimensions)) == len(args.dimensions), "duplicate_dimension")
    run(args.fixtures, args.runtime, args.output, args.dimensions, args.wall_seconds)


if __name__ == "__main__":
    main()
