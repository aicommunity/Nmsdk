"""Declared public-Console regression; no generated campaign Python scripts.

Templates are historical inputs, not historical execution evidence. Every new
operation uses the production worker, captures its own runtime and is audited.
"""
from contextlib import contextmanager
import copy
import hashlib
import json
import os
from pathlib import Path

from .native_calibration_worker import _signed, _write
from .native_evidence import EvidenceError, load, number, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .runtime import snapshot, source_closure
from .process_runner import verify_runtime


POSITIVES = {f"pipeline-{topology}-N{n}" for topology in ("Classic", "Branch") for n in (0, 1)} | {
    f"live-{topology}-{mode}" for topology in ("Classic", "Branch")
    for mode in ("budget", "fixed", "grid", "legacy-budget", "stopped")}
NEGATIVES = {"invalid-legacy-factor": "native", "invalid-empty-windows": "native",
             "invalid-frequency-mismatch": "native", "invalid-zero-measurement-budget": "native",
             "invalid-unsupported-ctrim": "descriptor", "invalid-wrong-owner": "descriptor"}
DESCRIPTOR_REASONS = {"invalid-unsupported-ctrim": "training_optional_modes_not_yet_supported",
                      "invalid-wrong-owner": "pipeline_owner_or_tick_budget_invalid"}
SPEC_FIELDS = {"kind", "schema_version", "template_corpus", "source_root", "executable", "app_ini",
               "cmake_cache", "loader_environment", "maximum_wall_seconds"}


@contextmanager
def _environment(values):
    previous = {key: os.environ.get(key) for key in values}
    try:
        os.environ.update(values)
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def run_preflight_regression(specification, output):
    specification = Path(specification).resolve(strict=True)
    spec = load(specification)
    require(type(spec) is dict and set(spec) == SPEC_FIELDS
            and spec["kind"] == "timelearner_public_preflight_regression"
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1,
            "unknown_public_preflight_regression_spec")

    def path(key):
        value = spec[key]
        require(type(value) is str and bool(value), "invalid_preflight_regression_path:"+key)
        candidate = Path(value)
        return (candidate if candidate.is_absolute() else specification.parent/candidate).resolve(strict=True)

    template, source = path("template_corpus"), path("source_root")
    executable, app_ini, cache = path("executable"), path("app_ini"), path("cmake_cache")
    wall = number(spec["maximum_wall_seconds"])
    require(wall > 0, "invalid_preflight_regression_wall_budget")
    environment = spec["loader_environment"]
    require(type(environment) is dict and set(environment) == {"QT_QPA_PLATFORM", "ASAN_OPTIONS"}
            and all(type(v) is str and "\x00" not in v for v in environment.values()),
            "invalid_preflight_regression_environment")
    output = Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(template) and not output.is_relative_to(source)
            and not template.is_relative_to(output) and not source.is_relative_to(output),
            "preflight_regression_output_overlaps_sources")
    corpus = load(template/"corpus.json")
    require(set(corpus["positive"]) == POSITIVES and len(corpus["positive"]) == len(POSITIVES)
            and set(corpus["negative"]) == set(NEGATIVES)
            and all(corpus["negative"][k]["stage"] == stage for k, stage in NEGATIVES.items()),
            "incomplete_preflight_regression_templates")
    jobs, origins = {}, {}
    for name in sorted(POSITIVES | {k for k, v in NEGATIVES.items() if v == "native"}):
        file = template/"runs"/name/"input/job.json"
        jobs[name] = load(file)
        origins[name] = {"path": str(file), "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                         "job_sha256": jobs[name]["sha256"]}
        validate_job("preflight", jobs[name])
    for name in DESCRIPTOR_REASONS:
        value = copy.deepcopy(jobs["pipeline-Classic-N1"])
        if name == "invalid-unsupported-ctrim":
            value["optional_modes"]["sync_capacitance_trim"] = 1
        else:
            value["owner_class"] = "WrongOwner"
        jobs[name] = _signed({k: v for k, v in value.items() if k != "sha256"})
        try:
            validate_job("preflight", jobs[name])
        except EvidenceError as error:
            require(DESCRIPTOR_REASONS[name] in str(error), "unexpected_descriptor_rejection:"+name)
        else:
            raise EvidenceError("negative_descriptor_was_accepted:"+name)
    for topology in ("Classic", "Branch"):
        job = jobs[f"live-{topology}-legacy-budget"]
        require(job["schema_version"] == 1 and job["maximum_model_ticks"] == 1,
                "regression_requires_schema1_one_tick_control")
    before = source_closure(source)
    output.mkdir(parents=True, exist_ok=False)
    _write(output/"specification.json", spec)
    _write(output/"template-sources.json", origins)
    _write(output/"source.json", before)
    inputs, results = output/"jobs", output/"corpus"
    inputs.mkdir(); results.mkdir()
    for name, job in jobs.items():
        _write(inputs/(name+".json"), job)
    # Set the declared environment BEFORE snapshot. A snapshot of different
    # loader conditions must never be repaired after a failed launch.
    with _environment(environment):
        runtime = snapshot(source, executable, app_ini, cache)
        _write(output/"runtime.json", runtime)
        positive, negative, controls = {}, {}, {}
        for name in sorted(POSITIVES):
            run = results/"runs"/name
            record = run_job("preflight", inputs/(name+".json"), None, output/"runtime.json", run, wall)
            require(record["execution"] == "completed" and record["validity"] == "valid",
                    "positive_preflight_failed:"+name)
            positive[name] = audit_run_manifest(run/"run-manifest.json")
        for name, stage in NEGATIVES.items():
            run = results/"runs"/name
            if stage == "descriptor":
                try:
                    run_job("preflight", inputs/(name+".json"), None, output/"runtime.json", run, wall)
                except EvidenceError as error:
                    require(DESCRIPTOR_REASONS[name] in str(error) and not run.exists(),
                            "descriptor_rejection_created_run:"+name)
                    negative[name] = {"stage": stage, "reason": str(error), "scientific_verdict": None}
                else:
                    raise EvidenceError("descriptor_created_positive_run:"+name)
            else:
                record = run_job("preflight", inputs/(name+".json"), None, output/"runtime.json", run, wall)
                process = load(run/"process/result.json")
                require(record["execution"] == "process_error" and record["analysis"] is None
                        and record["validity"] == "unverified_execution" and process["returncode"] == 2
                        and not (run/"native/execution.json").exists(), "native_negative_preflight_mismatch:"+name)
                audit_run_manifest(run/"run-manifest.json")
                negative[name] = {"stage": stage, "reason": "native_configuration_rejected", "scientific_verdict": None}
        for topology in ("Classic", "Branch"):
            name = f"live-{topology}-legacy-budget"
            run = results/"runs"/f"train-{topology}-legacy-budget"
            record = run_job("train", inputs/(name+".json"), None, output/"runtime.json", run, wall)
            native = load(run/"native/execution.json")
            require(record["execution"] == "process_error" and record["validity"] == "valid"
                    and record["analysis"]["completed_boundary"] is False
                    and record["analysis"]["evaluation_verdict"] is None
                    and native["execution"] == "model_tick_budget_exhausted" and native["model_ticks"] == 1,
                    "schema1_structured_stop_not_audited:"+topology)
            require(load(run/"native/initial-state.json") ==
                    load(results/"runs"/name/"native/initial-state.json"), "train_preflight_initial_model_changed")
            controls[topology] = audit_run_manifest(run/"run-manifest.json")
        require(source_closure(source) == before, "preflight_regression_source_changed")
        verify_runtime(runtime)
    _write(results/"corpus.json", {"kind": corpus["kind"], "schema_version": 1, "cooperative_capture": True,
                                 "positive": sorted(POSITIVES), "negative": negative, "train_controls": controls,
                                 "sources": origins, "scientific_verdict": None})
    report = {"kind": "timelearner_public_preflight_regression_result", "schema_version": 1,
              "execution": "completed", "positive": positive, "negative": negative, "train_controls": controls,
              "wall_policy_scope": "default negative limits; positive public override not attested",
              "scientific_verdict": None}
    _write(output/"result.json", report)
    return report
