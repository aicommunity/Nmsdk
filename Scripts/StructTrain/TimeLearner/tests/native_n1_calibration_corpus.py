"""Actual same-matrix threshold grid on genuinely trained positive N1 models.

Subthreshold LTZ traces propose candidates only. Every threshold is measured by
the native calibration runner; a finite grid cannot establish global infeasibility.
"""
import argparse
import contextlib
from copy import deepcopy
import math
from pathlib import Path
import shutil
import time

from ..__main__ import main as cli
from ..learned_evidence import audit_learned_state, load_case
from ..native_calibration_worker import audit_execution, audit_run_manifest
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_run_manifest as audit_pipeline
from ..recognition_metrics import load_evaluation, score_recognition_evaluation
from .live_pipeline_corpus import signed, write
from .native_dimension_reports import inventory


def prepare(handoff, row):
    folder = handoff/"runs"/row["name"]
    audit_pipeline(folder/"run-manifest.json")
    manifest = load(folder/"run-manifest.json")
    source = folder/manifest["source_package_path"]
    case = load_case(source)
    require(audit_learned_state(*case)["exact"], "n1_calibration_source_not_exact")
    model = load(folder/"native/model.json")
    spec, observations = load_evaluation(folder/"native/evaluation.json")
    require(score_recognition_evaluation(spec, observations, model)["validity"] == "valid"
            and len(observations) == 64, "n1_calibration_frozen_source_incomplete")
    original = load(folder/"input/job.json")
    by_id = {o["trial_id"]: o for o in observations}
    requests = original["trials"][:8]
    require(len({q["pattern_hash"] for q in requests}) == 8 and
            sum(q["label"] == "target" for q in requests) == 1, "n1_calibration_matrix_scope")
    peaks = []
    for q in requests:
        o = by_id[q["trial_id"]]
        require(o["schema_version"] == 2 and o["spike_count"] == 0,
                "n1_calibration_requires_measured_nonspiking_ltz_trace")
        peak = max(s["lt_potential"] for s in o["samples"] if s["time"] >= o["stimulus_onset"])
        require(math.isfinite(peak) and peak > 0., "n1_calibration_invalid_peak")
        peaks.append({"sample_id": q["sample_id"], "trial_id": q["trial_id"],
                      "pattern_hash": q["pattern_hash"], "label": q["label"], "ltz_raw_max": peak})
    unique = sorted({p["ltz_raw_max"] for p in peaks})
    inherited = model["neuron"]["metadata"]["calibration"]["threshold"]
    thresholds = sorted(set([.9*unique[0], 1.1*unique[-1], inherited]+
                            [a+.5*(b-a) for a, b in zip(unique, unique[1:])]))
    require(all(math.isfinite(t) and t > 0 for t in thresholds) and len(thresholds) <= 11,
            "n1_calibration_invalid_grid")
    top = "Branch" if case[0]["configuration"]["model"]["branch"] else "Classic"
    attempt = top+"/positive-n1-same-matrix-grid-v1"
    trials = deepcopy(requests)
    for i, q in enumerate(trials):
        q.update(run_id=attempt+"/search", trial_id=attempt+"/search/"+str(i))
    job = signed({"kind": "timelearner_native_calibration_job", "schema_version": 1,
        "owner_class": original["owner_class"], "implementation_id": original["implementation_id"],
        "frequency_hz": 2000, "maximum_model_ticks": 200000,
        "source_recognition": model, "thresholds": thresholds, "maximum_candidates": len(thresholds),
        "specification": {"protocol": "historical_same_matrix", "data_partition_id": "positive-n1-eight-patterns-v1",
            "attempt_id": attempt, "clock_id": "native-2000Hz",
            "criterion": {k: v for k, v in original["criterion"].items() if k != "id"}}, "trials": trials})
    proposal = {"schema_version": 1, "rule": "measured-nonspiking-ltz-peak-brackets-v1",
        "source_frozen_run": manifest["sha256"], "peaks": peaks, "thresholds": thresholds,
        "interpretation": "candidate proposal only; native measured grid and fresh selected-threshold confirmation required"}
    return top, source, case, job, proposal


def run(handoff, runtime, output):
    before = inventory(handoff)
    index = load(handoff/"index.json")
    require(index["kind"] == "native_n1_exact_handoff_controls" and len(index["records"]) == 2,
            "n1_calibration_handoff_scope")
    jobs = [prepare(handoff, row) for row in index["records"]]
    require({item[0] for item in jobs} == {"Classic", "Branch"}, "n1_calibration_topology_coverage")
    require(shutil.disk_usage(output.parent).free >= 2*1024**3, "n1_calibration_storage_capacity")
    output.mkdir(parents=True, exist_ok=False)
    (output/"jobs").mkdir();(output/"runs").mkdir()
    rows = [];started = time.time()
    for top, source, case, job, proposal in jobs:
        name = top+"-grid";path = output/"jobs"/(name+".json");write(path, job)
        write(output/"jobs"/(name+"-proposal.json"), proposal)
        folder = output/"runs"/name
        print("BEGIN", name, "thresholds", len(job["thresholds"]), flush=True)
        with (output/(name+".log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = cli(["calibrate", "run", str(path), "--source-solo", str(source),
                "--runtime-manifest", str(runtime), "--wall-seconds", "1800", "--output", str(folder)])
        require(code == 0, "n1_calibration_worker_failed:"+name)
        manifest_audit = audit_run_manifest(folder/"run-manifest.json")
        execution_audit = audit_execution(folder/"native", job, case)
        transaction = load(folder/"native/transaction.json")
        rows.append({"name": name, "status": transaction["status"], "source_solo_sha256": case[0]["sha256"],
            "declared_thresholds": job["thresholds"], "measured_candidates": len(transaction["candidates"]),
            "manifest_audit": manifest_audit, "execution_audit": execution_audit, "scientific_verdict": None})
        write(output/"progress.json", rows)
        print("END", name, transaction["status"], flush=True)
    require(before == inventory(handoff), "n1_calibration_frozen_source_changed")
    write(output/"index.json", {"kind": "positive_n1_measured_calibration_controls", "schema_version": 1,
        "records": rows, "source_files_unchanged": len(before), "wall_seconds": time.time()-started,
        "protocol": "historical_same_matrix", "statistical_independence_verified": False,
        "scientific_verdict": None, "limits": "declared finite threshold grid;two inputs;2000Hz;identity conversion;no global nonseparability or independent Test claim"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("handoff", "runtime", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    run(args.handoff, args.runtime, args.output)


if __name__ == "__main__":
    main()
