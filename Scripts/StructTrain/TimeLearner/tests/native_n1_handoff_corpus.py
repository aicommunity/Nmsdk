"""Actual Exact N1 Solo export and fixed-threshold frozen order controls.

New foils are declared before evaluation. No Train, threshold selection, test
tuning, analytic response or successful classification is manufactured here.
"""
import argparse
import contextlib
from pathlib import Path
import shutil
import time

from ..__main__ import main as cli
from ..learned_evidence import audit_learned_state, load_case
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_execution, audit_run_manifest
from .live_pipeline_corpus import signed, write
from .native_dimension_reports import inventory


FOIL_SECOND_ISI = (.015, .02, .025, .04, .05, .08, .15)
CRITERION = {"id": "post_anchor_target_whole_window_foil_v1", "anchor": "onset",
             "begin_offset": 0., "end_offset": None, "reject_target_outside_window": True}


def trial_design(run_id, target, frequency):
    require(target == [.01, .03] and frequency == 2000, "n1_handoff_protocol_scope")
    patterns = [("target", "target", target)] + [
        ("foil-"+str(i), "foil", [.01, interval]) for i, interval in enumerate(FOIL_SECOND_ISI)]
    trials = []
    for rotation in range(8):
        order = patterns[rotation:]+patterns[:rotation]
        for position, (sample, label, pattern) in enumerate(order):
            trials.append({"run_id": run_id, "trial_id": f"{run_id}/rotation-{rotation}/{position}",
                "sample_id": sample, "label": label, "pattern_hash": sha(pattern), "pattern_isi": pattern,
                "duration": .4, "maximum_samples": 805, "reset_policy": "reset_per_trial",
                "record_threshold_potential": True})
    return trials


def run(primary, runtime, output):
    before = inventory(primary)
    index = load(primary/"index.json")
    require(index["kind"] == "native_n1_proposal_controls" and len(index["records"]) == 2,
            "n1_handoff_requires_two_physical_sources")
    sources = []
    for row in index["records"]:
        folder = primary/row["name"]
        audit_run_manifest(folder/"run-manifest.json")
        source = folder/"native/train_learned_state.json"
        case = load_case(source)
        require(audit_learned_state(*case)["exact"] is True and case[0]["training_outcome"] == "exact",
                "n1_handoff_requires_fresh_exact_source")
        job = load(folder/"input/job.json")
        native = audit_execution("train", folder/"native", job)
        require(native["completed_boundary"], "n1_handoff_source_incomplete")
        solo = case[0]
        target = solo["neuron"]["metadata"]["training"]["target_pattern"]
        frequency = solo["configuration"]["model"]["frequency_hz"]
        # The protocol comes from the genuine model, not the old profile fixture.
        require(sha(target) == solo["protocol"]["pattern_hash"], "n1_handoff_target_provenance")
        topology = "Branch" if solo["configuration"]["model"]["branch"] else "Classic"
        trials = trial_design(topology+"/frozen-fixed-eight-orders", target, frequency)
        sources.append((topology, source, case, trials))
    require({r[0] for r in sources} == {"Classic", "Branch"}, "n1_handoff_topology_coverage")
    require(shutil.disk_usage(output.parent).free >= 2*1024**3, "n1_handoff_capacity")
    output.mkdir(parents=True, exist_ok=False)
    (output/"jobs").mkdir();(output/"runs").mkdir()
    write(output/"design.json", {"schema_version": 1, "criterion": CRITERION,
          "rows": [{"topology": top, "trials": trials, "source_solo_sha256": case[0]["sha256"]}
                   for top, _, case, trials in sources],
          "threshold_policy": "unchanged_source_fixed", "statistical_independence_verified": False,
          "limits": "reset-per-trial; deterministic rotations are not independent training replicates"})
    rows = [];started = time.time()
    def invoke(mode, name, job, source, case):
        path = output/"jobs"/(name+".json");write(path, signed(job))
        folder = output/"runs"/name
        print("BEGIN", name, flush=True)
        with (output/(name+".log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = cli([mode, str(path), "--source-solo", str(source), "--runtime-manifest", str(runtime),
                        "--wall-seconds", "1800", "--output", str(folder)])
        require(code == 0, "n1_handoff_phase_failed:"+name)
        manifest_audit = audit_run_manifest(folder/"run-manifest.json")
        native = audit_execution(mode, folder/"native", load(path), case)
        require(load(folder/"native/execution.json")["execution"] == "completed", "n1_handoff_phase_incomplete")
        print("END", name, flush=True)
        return folder, manifest_audit, native
    for top, source, case, trials in sources:
        solo = case[0]
        export, export_audit, _ = invoke("export", top+"-export", {
            "kind": "timelearner_native_recognition_export_job", "schema_version": 1,
            "implementation_id": solo["implementation_id"], "source_solo": solo,
            "conversion_spec": {"schema_version": 1, "mode": "identity", "resistance_bounds": []}}, source, case)
        model = load(export/"native/model.json")
        name = top+"-frozen"
        folder, manifest_audit, native = invoke("evaluate", name, {
            "kind": "timelearner_native_evaluation_job", "schema_version": 1,
            "owner_class": "NNeuronTimeLearner"+("Branch" if top == "Branch" else ""),
            "implementation_id": solo["implementation_id"], "source_recognition": model,
            "maximum_model_ticks": 200000, "run_id": trials[0]["run_id"],
            "coverage_policy": "per_trial_windows", "criterion": CRITERION, "trials": trials}, source, case)
        require(native["frozen_model_verified"] and native["metrics"]["validity"] == "valid",
                "n1_handoff_invalid_frozen_evaluation")
        rows.append({"name": name, "operation": "evaluate", "source": str(source),
            "source_solo_sha256": solo["sha256"], "source_model_revision": solo["model_revision"],
            "export_name": top+"-export", "export_manifest_audit": export_audit,
            "manifest_audit": manifest_audit, "execution_audit": native,
            "training_outcome": solo["training_outcome"], "scientific_verdict": None})
        write(output/"progress.json", rows)
    require(before == inventory(primary), "n1_handoff_original_train_changed")
    write(output/"index.json", {"kind": "native_n1_exact_handoff_controls", "schema_version": 1,
        "records": rows, "operations": 4, "observed_trials": 128, "source_files_unchanged": len(before),
        "wall_seconds": time.time()-started, "threshold_policy": "unchanged_source_fixed",
        "statistical_independence_verified": False, "scientific_verdict": None,
        "limits": "two physical Exact Solo sources;identity export;2000Hz;reset-per-trial;no calibration/continuous-stream claim"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("primary", "runtime", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    run(args.primary, args.runtime, args.output)


if __name__ == "__main__":
    main()
