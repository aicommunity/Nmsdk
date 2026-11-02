"""Declared cold burst A/B for the measured-length candidate policy.

This experiment keeps captured per-input amplitude targets and original
tolerances. A real measured jump exercises a proposal, not recognition success.
Both immutable runtimes receive byte-identical jobs through the production
native pipeline. No process runs on import.
"""
import argparse
import copy
from pathlib import Path

from .native_calibration_worker import _signed, _write
from .native_evidence import load, require
from .native_pipeline_worker import run_job, audit_run_manifest, audit_execution
from .process_runner import verify_runtime


def _progress(output, records):
    pending = output/"progress.pending.json"
    _write(pending, {"kind": "native_measured_length_progress", "schema_version": 1, "records": records})
    pending.replace(output/"progress.json")


def make_job(template, topology, normalization):
    job = copy.deepcopy(template)
    require(job.get("schema_version") == 1 and topology in ("Classic", "Branch")
            and normalization in ("N0", "N1"), "length_experiment_template_schema")
    config = job["configuration"]
    model = config["model"]
    require(model["branch"] is (topology == "Branch") and model["normalization"] == normalization
            and model["frequency_hz"] == 2000 and len(model["inputs"]) == 2
            and not model["inhibition"], "length_experiment_template_scope")
    require(len(config["search"]["bounds"]) == 2
            and [p["attachment"] for p in model["inputs"]] == [2, 1]
            and all(p["synapses"] == 1 for p in model["inputs"]), "length_experiment_initial_geometry")
    model["initial_isi"] = [.01, .08]
    model["maximum_cable_length"] = 16
    config["run_id"] = "measured-length-"+topology+"-"+normalization+"-isi080"
    config["protocol_revision"] = "measured_length_native_burst_isi080_v1"
    # Ordered whole-burst assignment selects the actual stimulus wave. The
    # same broad declared window covers its legal delay before/after growth.
    config["duration"] = .5
    config["windows"] = [{"begin": .005, "end": .49} for _ in range(2)]
    config["maximum_samples"] = 1001
    config["maximum_sample_gap"] = .0005
    config["maximum_model_seconds"] = 20.
    config["maximum_wall_seconds"] = 1800.
    search = config["search"]
    search.update(maximum_candidates_per_input=4 if normalization == "N0" else 5,
                  maximum_edits=32, maximum_probes=64, maximum_sweeps=1)
    for index, bound in enumerate(search["bounds"]):
        resistance = model["inputs"][index]["resistance"]
        bound.update(minimum_length=2 if index == 0 else 1,
                     maximum_length=16 if index == 0 else 1,
                     minimum_synapses=1, maximum_synapses=1,
                     minimum_resistance=resistance, maximum_resistance=resistance)
    job["maximum_model_ticks"] = 40000
    # Profiles, actual initial L/Ns/Rs, reference policy, tolerances and all
    # optional mode declarations are inherited intact from the accepted inputs.
    return _signed({k: v for k, v in job.items() if k != "sha256"})


def run(templates, baseline_runtime, current_runtime, output):
    runtimes = {"baseline": load(baseline_runtime), "current": load(current_runtime)}
    for runtime in runtimes.values():
        verify_runtime(runtime)
    output.mkdir(parents=True, exist_ok=False)
    (output/"jobs").mkdir()
    records = []
    for topology in ("Classic", "Branch"):
        for normalization in ("N0", "N1"):
            name = topology+"-"+normalization
            template = load(templates/(name+"-inputs2-f2000.json"))
            job = make_job(template, topology, normalization)
            path = output/"jobs"/(name+".json")
            _write(path, job)
            versions = {}
            for version, runtime_path in (("baseline", baseline_runtime), ("current", current_runtime)):
                folder = output/(version+"-"+name)
                print("BEGIN", version, name, flush=True)
                result = run_job("train", path, None, runtime_path, folder, 1800)
                record = {"name": name, "version": version, "result": result, "scientific_verdict": None}
                records.append(record)
                _progress(output, records)
                require(result["execution"] == "completed" and result["validity"] == "valid",
                        "length_experiment_incomplete_native_train:"+version+":"+name)
                audit_run_manifest(folder/"run-manifest.json")
                audit_execution("train", folder/"native", job)
                summary = load(folder/"native/train_learned_summary.json")
                unique = []
                for candidate in summary["candidates"]:
                    length = candidate["parameters"]["length"]
                    if length not in unique:
                        unique.append(length)
                jumps = [[a, b] for a, b in zip(unique, unique[1:]) if abs(b-a) > 1]
                versions[version] = {"unique_measured_lengths": unique, "measured_jumps": jumps,
                                     "outcome": summary["outcome"], "certificate": summary["certificate"]}
                record["measured"] = versions[version]
                _progress(output, records)
                print("END", version, name, unique, flush=True)
            require(not versions["baseline"]["measured_jumps"] and versions["current"]["measured_jumps"],
                    "length_experiment_measured_proposal_not_exercised:"+name)
    for runtime in runtimes.values():
        verify_runtime(runtime)
    _write(output/"index.json", {"kind": "native_measured_length_ab", "schema_version": 1,
                               "records": records, "scientific_verdict": None,
                               "limits": "2 inputs; 2000 Hz; fixed Rs/Ns; original tolerances; no classification"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", type=Path, required=True)
    parser.add_argument("--baseline-runtime", type=Path, required=True)
    parser.add_argument("--current-runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.templates, args.baseline_runtime, args.current_runtime, args.output)


if __name__ == "__main__":
    main()
