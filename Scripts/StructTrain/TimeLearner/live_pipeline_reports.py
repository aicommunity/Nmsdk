"""Temporal reports for genuine portable production Train/evaluate runs.

Run manifests supply the declared primary closure; no synthetic integration
scenario or reconstructed target matrix is introduced by this adapter.
"""
from pathlib import Path
import gzip
import hashlib
import html
import json
import re
import shutil

from .learned_evidence import load_case
from .native_evidence import load, number, require
from .native_pipeline_worker import audit_execution, audit_run_manifest
from .plotting import plotting_runtime
from .posttune_transaction_reports import render_posttune_transaction_data
from .probe_reports import render_probe_set
from .reports import render_evaluation, render_diagnostic_evaluation
from .stopped_evidence import load_case as load_stopped


def write(path, value):
    raw = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode("utf-8")
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == ".gz" else raw)


def read_pipeline_report(source):
    source = Path(source);audit = audit_run_manifest(source);root = source.parent
    manifest, job, execution = load(source), load(root/"input/job.json"), load(root/"native/execution.json")
    mode = manifest["operation"];require(mode in {"train", "evaluate", "diagnostic-evaluate"}, "pipeline_report_has_no_native_observations")
    native = root/"native";packets = [];case = live = None
    if mode == "train":
        # Also audit the typed schema1 partial result, whose historical process
        # manifest remains unverified after nonzero exit.
        audit_execution(mode, native, job)
        if execution["package_path"] is not None:
            path = native/execution["package_path"]
            case = (load_case if execution["completed_boundary"] else load_stopped)(path)
        prefix = "train_state_trial_" if execution["completed_boundary"] else "train_stopped_trial_"
        ordinal = re.compile(re.escape(prefix)+r"([1-9][0-9]*)\.json")
        names = [r["path"] for r in execution["artifacts"] if r["path"].startswith(prefix) and r["path"].endswith(".json")]
        require(all(ordinal.fullmatch(n) for n in names), "pipeline_report_invalid_trial_ordinal")
        names.sort(key=lambda n: int(ordinal.fullmatch(n)[1]))
        require([int(ordinal.fullmatch(n)[1]) for n in names] == list(range(1, len(names)+1)),
                "pipeline_report_missing_trial_ordinal")
        require(case is not None or not names, "pipeline_report_orphan_source_probes")
        last = None
        for n in names:
            p = native/n;r = load(p);observation = r.get("observation")
            if observation and observation.get("sample_count", 0):
                begin = number(observation["specification"]["begin"])
                require(last is None or begin > last, "pipeline_report_nonchronological_trials")
                last = begin
            packets.append(p)
        if job["schema_version"] == 2:
            live = load(native/"finalization.json")
    return manifest, job, execution, audit, case, live, packets


def render_pipeline_run(source, output):
    source, output = Path(source), Path(output);root = source.parent
    require(not output.resolve().is_relative_to(root.resolve()), "pipeline_report_must_be_outside_primary")
    manifest, job, execution, audit, case, live, packets = read_pipeline_report(source)
    runtime = plotting_runtime();output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary";primary.mkdir();links = [];training = posttune = evaluation = None
    write(primary/"run-manifest.json.gz", manifest)
    if manifest["operation"] == "train":
        if packets:
            inputs = primary/"training";inputs.mkdir();trials = []
            for p in packets:
                shutil.copyfile(p, inputs/p.name);shutil.copyfile(p.with_suffix(".csv"), inputs/p.with_suffix(".csv").name)
                trials.append({"trial_id": load(p)["requested_specification"]["trial_id"], "packet": p.name, "trace": p.with_suffix(".csv").name})
            write(inputs/"report-spec.json", {"kind": "timelearner_probe_report_spec", "schema_version": 2,
                  "observation_policy": "complete_or_partial", "trials": trials})
            training = render_probe_set(inputs/"report-spec.json", output/"training")
            links.append('<li><a href="training/index.html">All recorded Train probes and soma channels; partial windows explicit</a></li>')
        if live is not None:
            write(primary/"finalization.json.gz", live)
            if live["post_tune"]:
                posttune = render_posttune_transaction_data(live["post_tune"], case, output/"posttune")
                links.append('<li><a href="posttune/index.html">Actual PostTune/calibration matrices and final-threshold responses</a></li>')
    elif manifest["operation"] == "diagnostic-evaluate":
        evaluation = render_diagnostic_evaluation(root/"native/evaluation.json", root/"native/model.json",
                                                 root/"input/source/train_stopped_state.json", output/"evaluation")
        links.append('<li><a href="evaluation/index.html">Stopped Train: declared patterns, actual soma responses and missing observations</a></li>')
    else:
        evaluation = render_evaluation(root/"native/evaluation.json", root/"native/model.json", output/"evaluation")
        links.append('<li><a href="evaluation/index.html">Every declared frozen-evaluation pattern and soma channel</a></li>')
    result = {"kind": "timelearner_live_pipeline_visual_report", "schema_version": 1,
        "source_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "source_run_sha256": manifest["sha256"],
        "source_artifacts": manifest["artifacts"], "source_operation": manifest["operation"], "source_job_schema_version": job["schema_version"],
        "source_process_execution": manifest["execution"], "source_native_execution": execution["execution"],
        "source_training_outcome": execution.get("training_outcome"), "source_completed_boundary": execution.get("completed_boundary"),
        "source_recognition_available": execution.get("recognition_available"), "audit": audit,
        "training_report": training, "posttune_report": posttune, "evaluation_report": evaluation,
        "training_trial_soma_pairs": training["trial_soma_pairs"] if training else 0,
        "recognition_trial_soma_pairs": (posttune["trial_soma_pairs"] if posttune else 0)+(evaluation["trial_soma_pairs"] if evaluation else 0),
        "training_packet_order": [p.name for p in packets], "runtime": runtime,
        "native_execution_attested": False, "independent_partition_verified": False,
        "visual_acceptance_complete": False, "scientific_verdict": None}
    if manifest["operation"] == "diagnostic-evaluate":
        result.update(diagnostic_only=True, training_completed=False,
                      source_training_outcome=execution["training_outcome"])
    write(output/"manifest.json", result)
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>Production TimeLearner responses</title>'
        '<style>body{font:18px sans-serif;margin:2em}</style><h1>Production TimeLearner: actual responses</h1><p>'+
        html.escape(manifest["operation"])+" / "+html.escape(execution["execution"])+'.</p>'
        '<p>Original soma samples with actual input overlays, overview and readable zooms. Train, weight measurement, '
        'calibration and separately invoked frozen evaluation are distinct. Partial observations never become complete responses. '
        'Same-matrix data are not independent Test; a silent target is a false negative. SI units remain unverified.</p><ul>'+
        ''.join(links)+'</ul><p>No convergence or successful classification is inferred from execution completion.</p>', encoding="utf-8")
    write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(output.rglob("*")) if p.is_file()})
    return result
