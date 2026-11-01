"""Replay exact physical N1 seed-mesh job declarations on a new runtime.

Only implementation/runtime changes. The old job, storage profiles, reference
capture protocol, bounds and original tolerances are read unchanged. This does
not assume convergence or run classification/calibration behind the scenes.
"""
import argparse
import contextlib
from pathlib import Path
import shutil
import time

from ..__main__ import main as cli
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_execution, audit_run_manifest, validate_job
from .live_pipeline_corpus import write
from .native_dimension_reports import inventory


def run(baseline, runtime, output):
    before = inventory(baseline)
    index = load(baseline/"index.json")
    require(index["kind"] == "native_n1_proposal_controls" and len(index["records"]) == 2,
            "n1_comparison_baseline_scope")
    require(shutil.disk_usage(output.parent).free >= 1024**3, "n1_comparison_primary_capacity")
    jobs = []
    for row in index["records"]:
        name = row["name"]
        job = load(baseline/(name+".json"))
        require(job == load(baseline/name/"input/job.json"), "n1_comparison_baseline_job_changed")
        validate_job("train", job)
        require(job["configuration"]["model"]["normalization"] == "N1", "n1_comparison_not_n1")
        audit_run_manifest(baseline/name/"run-manifest.json")
        previous = audit_execution("train", baseline/name/"native", job)
        require(previous["completed_boundary"], "n1_comparison_baseline_incomplete")
        jobs.append((name, job, previous))
    require(len({name for name, _, _ in jobs}) == 2, "n1_comparison_duplicate_case")
    output.mkdir(parents=True, exist_ok=False)
    records = []
    start = time.time()
    for name, job, previous in jobs:
        write(output/(name+".json"), job)
        folder = output/name
        print("BEGIN", name, flush=True)
        with (output/(name+".log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = cli(["train", str(output/(name+".json")), "--runtime-manifest", str(runtime),
                        "--wall-seconds", "1800", "--output", str(folder)])
        require(code == 0, "n1_comparison_training_failed:"+name)
        manifest = audit_run_manifest(folder/"run-manifest.json")
        audit = audit_execution("train", folder/"native", job)
        require(audit["completed_boundary"], "n1_comparison_training_incomplete")
        summary = load(folder/"native/train_learned_summary.json")
        initial = load(folder/"native/initial-state.json")
        original = load(baseline/name/"native/initial-state.json")
        require(initial["identity"]["sha256"] == original["identity"]["sha256"] and
                initial["parameters"] == original["parameters"], "n1_comparison_cold_model_changed")
        require(job == load(folder/"input/job.json"), "n1_comparison_new_job_changed")
        row = {"name": name, "manifest_audit": manifest, "execution_audit": audit,
               "candidates": summary["candidates"], "certificate": summary["certificate"],
               "resistance_domains": summary["resistance_domains"], "scientific_verdict": None,
               "comparison": {"job_sha256": job["sha256"],
                              "initial_model_revision": initial["identity"]["sha256"],
                              "baseline_training_outcome": previous["training_outcome"],
                              "current_training_outcome": audit["training_outcome"]}}
        records.append(row)
        write(output/"progress.json", records)
        print("END", name, previous["training_outcome"], "->", audit["training_outcome"], flush=True)
    require(before == inventory(baseline), "n1_comparison_baseline_primary_changed")
    write(output/"index.json", {"kind": "native_n1_proposal_controls", "schema_version": 1,
          "records": records, "baseline_files_unchanged": len(before),
          "wall_seconds": time.time()-start, "scientific_verdict": None,
          "limits": "exact baseline job replay; two inputs; 2000 Hz; bare Train; no classification"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.baseline, args.runtime, args.output)


if __name__ == "__main__":
    main()
