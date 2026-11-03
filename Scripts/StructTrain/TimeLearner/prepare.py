"""Declarative native cold-job matrices; preparation never runs a component."""
import copy
import math
from pathlib import Path

from .native_evidence import EvidenceError, count, load, number, require
from .native_calibration_worker import _record, _signed, _write
from .native_pipeline_worker import validate_job
from .model_identity import canonical_model_sha256 as sha


def _prepare_matrix(specification):
    require(type(specification) is dict and set(specification) == {
        "kind", "schema_version", "templates", "input_counts", "frequencies_hz",
        "isi_seconds", "probe_duration", "window_width", "n0_candidate_repeats", "run_prefix"} and
        specification["kind"] == "timelearner_native_matrix_preparation" and
        type(specification["schema_version"]) is int and specification["schema_version"] == 1,
        "unknown_native_preparation_schema")
    templates = specification["templates"]
    require(type(templates) is dict and set(templates) == {
        t+"-N"+n for t in ("Classic", "Branch") for n in ("0", "1")}, "preparation_template_set")
    axes = []
    for field, maximum in (("input_counts", 128), ("frequencies_hz", 1000000)):
        values = specification[field]
        require(type(values) is list and bool(values) and all(type(x) is int and 1 <= x <= maximum for x in values)
                and len(set(values)) == len(values), "invalid_preparation_axis:"+field)
        axes.append(values)
    require(len(axes[0])*len(axes[1])*4 <= 4096, "preparation_case_budget")
    isi, duration, width = (number(specification[k]) for k in ("isi_seconds", "probe_duration", "window_width"))
    require(isi > 0 and width > 0 and duration > 0 and
            max(axes[0])*isi+width <= duration, "preparation_clipped_window")
    require(math.isfinite(duration*max(axes[1])) and duration*max(axes[1]) < 100000000,
            "preparation_sample_budget")
    repeats = count(specification["n0_candidate_repeats"])
    require(2 <= repeats <= 128 and type(specification["run_prefix"]) is str and
            bool(specification["run_prefix"].strip()), "invalid_preparation_policy")
    jobs = {}
    for template_name, template in templates.items():
        validate_job("train", template)
        require(template["schema_version"] == 1, "preparation_requires_cold_template_without_finalization")
        branch = template_name.startswith("Branch")
        normalization = template_name.rsplit("-", 1)[1]
        model = template["configuration"]["model"]
        require(model["branch"] is branch and model["normalization"] == normalization and
                len(model["inputs"]) == 2 and len(template["configuration"]["search"]["bounds"]) == 2 and
                model["inhibition"] == [], "preparation_requires_two_input_uninhibited_template")
        for inputs in axes[0]:
            for frequency in axes[1]:
                name = template_name+"-inputs"+str(inputs)+"-f"+str(frequency)
                job = copy.deepcopy(template);c = job["configuration"];m = c["model"]
                # Preserve the original last/reference input and its domain.
                # Replicate only the declared nonreference input for larger N.
                m["inputs"] = [copy.deepcopy(model["inputs"][0]) for _ in range(inputs-1)]+[copy.deepcopy(model["inputs"][-1])]
                original_bounds = template["configuration"]["search"]["bounds"]
                c["search"]["bounds"] = [copy.deepcopy(original_bounds[0]) for _ in range(inputs-1)]+[copy.deepcopy(original_bounds[-1])]
                lengths = [p["attachment"] for p in m["inputs"]]
                m["allocated_cable_lengths"] = [max(lengths)] if branch else lengths
                m["frequency_hz"] = frequency;m["initial_isi"] = [isi]*inputs
                c["stimulus_profile"]["frequency_hz"] = frequency
                c["duration"] = duration;c["maximum_sample_gap"] = 1./frequency
                c["maximum_samples"] = math.ceil(duration*frequency)+1
                c["windows"] = [{"begin": (i+1)*isi, "end": (i+1)*isi+width} for i in range(inputs)]
                c["maximum_reference_probes"] = max(c["maximum_reference_probes"], 2*inputs)
                c["run_id"] = specification["run_prefix"]+"/"+name
                if normalization == "N0":
                    if c["schema_version"] != 3:
                        c["schema_version"] = 2
                    c["search"]["n0_candidate_repeats"] = repeats
                job = _signed({k: v for k, v in job.items() if k != "sha256"})
                validate_job("train", job);jobs[name] = job
    return jobs


def prepare_matrix(specification):
    try:
        return _prepare_matrix(specification)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError, ZeroDivisionError) as error:
        raise EvidenceError("malformed_preparation_specification:"+str(error)) from error


def write_prepared_matrix(specification_path, output):
    specification = load(Path(specification_path).resolve(strict=True))
    jobs = prepare_matrix(specification)
    output = Path(output).resolve();output.mkdir(parents=True, exist_ok=False)
    _write(output/"specification.json", specification)
    (output/"jobs").mkdir()
    for name, job in jobs.items():
        _write(output/"jobs"/(name+".json"), job)
    manifest = _signed({"kind": "timelearner_prepared_matrix", "schema_version": 1,
        "specification_sha256": sha(specification), "job_sha256": {name: job["sha256"] for name, job in jobs.items()},
        "reference_policy": "repeat_nonreference_keep_last", "runtime_checked": False,
        "effective_model_checked": False, "training_started": False,
        "artifacts": [_record(p, output) for p in sorted(output.rglob("*")) if p.is_file()],
        "evaluation_verdict": None})
    _write(output/"manifest.json", manifest)
    return manifest
