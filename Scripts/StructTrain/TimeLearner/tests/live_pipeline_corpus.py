"""Explicit acceptance corpus using production CLI and fresh native cold Train.

Historical jobs supply immutable physical profiles and declared designs only.
No saved learned graph, references or controller are installed in the learner.
"""
from copy import deepcopy
import contextlib
import json
from pathlib import Path
import shutil

from ..__main__ import main as cli
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_execution, audit_run_manifest


def signed(value):
    value.pop("sha256", None);value["sha256"] = sha(value);return value


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def make_job(template, name, *, calibrate=False, legacy=False, budget=False, stopped=False,
             normalization=None, n0_candidate_repeats=1, n0_maximum_synapses=None):
    solo = template["source_recognition"]["source_solo"]
    config = deepcopy(solo["configuration"]);config["run_id"] = name
    require(normalization in (None, "N0", "N1"), "corpus_unknown_normalization")
    require(type(n0_candidate_repeats) is int and 1 <= n0_candidate_repeats <= 128,
            "corpus_invalid_candidate_repeats")
    selected = normalization or config["model"]["normalization"]
    if selected == "N0":
        require(type(n0_maximum_synapses) is int and 2 <= n0_maximum_synapses <= 128,
                "corpus_explicit_n0_synapse_domain_required")
        require(len(config["search"]["bounds"]) == len(config["model"]["inputs"]),
                "corpus_input_bounds_shape_changed")
        require(template["source_recognition"]["conversion_spec"]["mode"] == "identity",
                "corpus_n0_requires_declared_identity_conversion")
        config["model"]["normalization"] = "N0"
        # The final input remains the fixed reference. N0 varies counts on the
        # other inputs and keeps their declared individual resistances fixed.
        for i, (bound, initial) in enumerate(zip(config["search"]["bounds"], config["model"]["inputs"])):
            require(type(initial["resistance"]) in (int, float) and initial["resistance"] > 0,
                    "corpus_explicit_n0_resistance_required")
            bound["minimum_resistance"] = bound["maximum_resistance"] = initial["resistance"]
            if i + 1 < len(config["model"]["inputs"]):
                bound["maximum_synapses"] = n0_maximum_synapses
        config["schema_version"] = 2 if n0_candidate_repeats > 1 else 1
        config["search"].pop("n0_candidate_repeats", None)
        if n0_candidate_repeats > 1:
            config["search"]["n0_candidate_repeats"] = n0_candidate_repeats
    else:
        require(n0_candidate_repeats == 1 and n0_maximum_synapses is None,
                "corpus_n0_factors_on_n1")
        require(config["model"]["normalization"] == "N1", "corpus_n1_template_required")
    if stopped:
        config["maximum_model_seconds"] = 1/config["model"]["frequency_hz"]
    job = {"kind": "timelearner_native_training_job", "schema_version": 1 if legacy else 2,
           "owner_class": template["owner_class"], "implementation_id": template["implementation_id"],
           "configuration": config, "profile_archives": [deepcopy(solo["neuron"])],
           "optional_modes": {"sync_capacitance_trim": 0, "post_train_tuning": not legacy, "auto_calibrate_threshold": False},
           "calculate_mode": int(calibrate), "structure_build_mode": 1, "maximum_model_ticks": 1 if budget else 200000}
    if not legacy:
        controls = deepcopy(template["post_tune"])
        controls.update(schema_version=3, mode="keep_done", canonical_floor=0., canonical_last=0., resistance_bounds=[],
                        finalization="calibrate" if calibrate else "keep_fixed_threshold", weight_probe_threshold=2.)
        confirmation = deepcopy(template["specification"]);confirmation["attempt_id"] = name+"/finalization"
        plan = {"kind": "native_live_finalization_plan", "schema_version": 1, "implementation_id": job["implementation_id"],
                "conversion": deepcopy(template["source_recognition"]["conversion_spec"]), "post_tune": controls,
                "trials": deepcopy(template["trials"]), "thresholds": deepcopy(template["thresholds"]) if calibrate else [],
                "maximum_calibration_candidates": template["maximum_candidates"] if calibrate else 0, "confirmation": confirmation}
        job["finalization_plan"] = signed(plan)
    return signed(job)


def run_corpus(fixtures, runtime, output, wall_seconds, *, normalization=None,
               n0_candidate_repeats=1, n0_maximum_synapses=None,
               minimum_free_bytes=512*1024**2):
    fixtures, runtime, output = Path(fixtures), Path(runtime), Path(output)
    # Measured two-protocol N0 primary data occupy about404 MB. This lower
    # bound protects this engineering corpus only; it is not a reservation,
    # a general job estimator, or a substitute for scheduler resource leases.
    require(type(minimum_free_bytes) is int and minimum_free_bytes >= 512*1024**2,
            "corpus_invalid_storage_budget")
    require(shutil.disk_usage(output.parent).free >= minimum_free_bytes,
            "corpus_insufficient_primary_storage")
    output.mkdir(parents=True, exist_ok=False);jobs = output/"jobs";jobs.mkdir();runs = output/"runs";runs.mkdir()
    rows = []
    factors = dict(normalization=normalization, n0_candidate_repeats=n0_candidate_repeats,
                   n0_maximum_synapses=n0_maximum_synapses)
    def invoke(name, mode, job, *, source=None, expected=0):
        path = jobs/(name+".json");write(path, job)
        args = [mode, str(path), "--runtime-manifest", str(runtime), "--wall-seconds", str(wall_seconds), "--output", str(runs/name)]
        if source is not None:
            args += ["--source-solo", str(source)]
        print("BEGIN", name, flush=True)
        with (output/(name+"-cli.log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = cli(args)
        require(code == expected, "live_pipeline_cli_code:"+name)
        audit = audit_run_manifest(runs/name/"run-manifest.json")
        execution = load(runs/name/"native/execution.json")
        # Schema1 nonzero-exit compatibility is audited explicitly, retaining
        # its historical unverified process manifest instead of rewriting it.
        native = audit_execution(mode, runs/name/"native", job)
        rows.append({"name": name, "operation": mode, "schema_version": job["schema_version"], "expected_cli_code": expected,
                     "manifest_audit": audit, "native_audit": native, "execution": execution["execution"]})
        write(output/"progress.json", {"records": rows})
        print("END", name, execution["execution"], flush=True)
        return runs/name
    for top, old in (("Classic", "Classic-auto_metric"), ("Branch", "Branch-synthetic")):
        template = load(fixtures/old/"input/job.json")
        for calibrate in (False, True):
            name = top+("-grid" if calibrate else "-fixed")
            job = make_job(template, name, calibrate=calibrate, **factors)
            train = invoke(name, "train", job)
            e = load(train/"native/execution.json")
            require(e["completed_boundary"] and e["recognition_available"], "live_pipeline_completed_recognition_missing")
            final = load(train/"native/recognition-model.json")
            trials = deepcopy(job["finalization_plan"]["trials"])
            for i, q in enumerate(trials):
                q["run_id"] = name+"/frozen-same-matrix";q["trial_id"] = q["run_id"]+"/"+str(i)
            evaluation = signed({"kind": "timelearner_native_evaluation_job", "schema_version": 1,
                "owner_class": job["owner_class"], "implementation_id": job["implementation_id"], "source_recognition": final,
                "maximum_model_ticks": 200000, "run_id": name+"/frozen-same-matrix", "coverage_policy": "per_trial_windows",
                "criterion": {"id": "post_anchor_target_whole_window_foil_v1", **job["finalization_plan"]["confirmation"]["criterion"]},
                "trials": trials})
            # Evaluation requires the genuine new Train source, not the old profile fixture.
            path = jobs/(name+"-evaluate.json");write(path, evaluation)
            print("BEGIN", name+"-evaluate", flush=True)
            with (output/(name+"-evaluate-cli.log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                code = cli(["evaluate", str(path), "--runtime-manifest", str(runtime), "--source-solo", str(train/"native/train_learned_state.json"),
                            "--wall-seconds", str(wall_seconds), "--output", str(runs/(name+"-evaluate"))])
            require(code == 0, "live_pipeline_frozen_cli_failed")
            audit = audit_run_manifest(runs/(name+"-evaluate")/"run-manifest.json")
            rows.append({"name": name+"-evaluate", "operation": "evaluate", "schema_version": 1, "expected_cli_code": 0, "manifest_audit": audit})
            write(output/"progress.json", {"records": rows});print("END", name+"-evaluate", flush=True)
        for scenario in ("budget", "stopped", "legacy-budget"):
            name = top+"-"+scenario
            job = make_job(template, name, legacy=scenario=="legacy-budget", budget=scenario!="stopped", stopped=scenario=="stopped", **factors)
            invoke(name, "train", job, expected=0 if scenario=="stopped" else 2)
    require(len(rows)==14, "live_pipeline_operation_count")
    value = {"kind": "native_live_pipeline_corpus", "schema_version": 1, "records": rows,
             "operations": len(rows), "cold_live_finalization_runs": 4, "frozen_same_matrix_evaluations": 4,
             "partial_v2_controls": 4, "legacy_v1_controls": 2, "independent_partition_verified": False, "scientific_verdict": None}
    if normalization is not None:
        value["experiment_factors"] = factors
    write(output/"index.json", value);return value
