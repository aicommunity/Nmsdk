"""Measured native N0 proposal-path control with unchanged target/tolerances.

A shorter declared ISI and bounded L/Ns domain make timing-ready geometry a
possibility to measure, not an assumed observation. This reports whether the
physical run exercises nearby-Ns priority; neither a missing control nor an
unresolved search is turned into scientific success.
"""
import argparse
import contextlib
from pathlib import Path

from ..__main__ import main as cli
from ..native_evidence import load, require
from ..native_pipeline_worker import audit_execution, audit_run_manifest
from .live_pipeline_corpus import signed, write
from .native_dimension_corpus import make_dimension_job


def run(fixtures, runtime, output, normalization="N0"):
    require(normalization in ("N0", "N1"), "native_proposal_normalization")
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for topology in ("Classic", "Branch"):
        original = load(fixtures/(topology+"-fixed")/"input/job.json")
        job = make_dimension_job(original, topology, normalization, 2)
        config = job["configuration"]
        name = ("native-priority-" if normalization == "N0" else "native-n1-mesh-")+topology+"-isi030"
        config["run_id"] = name
        config["protocol_revision"] = "native_"+normalization.lower()+"_measured_proposal_isi030_v1"
        config["model"]["initial_isi"] = [.01, .03]
        config["search"]["bounds"][0].update(maximum_length=4, maximum_synapses=4)
        config["search"]["maximum_candidates_per_input"] = 4
        if normalization == "N1":
            # Explicit narrow physical search box, retaining the initial Rs
            # and fixed anchor. The native adapter derives its effective domain.
            config["search"]["bounds"][0].update(maximum_length=3, maximum_synapses=1,
                                                   minimum_resistance=43000000.)
            config["search"].update(maximum_candidates_per_input=80, maximum_probes=256,
                                    maximum_edits=128, resistance_subdivision_depth=4)
            config["maximum_model_seconds"] = 180.
            job["maximum_model_ticks"] = 360000
        signed(job)
        path = output/(name+".json")
        write(path, job)
        folder = output/name
        print("BEGIN", name, flush=True)
        with (output/(name+".log")).open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = cli(["train", str(path), "--runtime-manifest", str(runtime),
                        "--wall-seconds", "1800", "--output", str(folder)])
        require(code == 0, "native_proposal_control_failed:"+name)
        manifest = audit_run_manifest(folder/"run-manifest.json")
        audit = audit_execution("train", folder/"native", job)
        summary = load(folder/"native/train_learned_summary.json")
        candidates = summary["candidates"]
        pairs = []
        for before, after in zip(candidates, candidates[1:]):
            a, b = before["parameters"], after["parameters"]
            if (before["within_timing"] and not before["within_amplitude"] and
                    a["length"] > 1 and a["length"] == b["length"] and
                    a["synapses"] != b["synapses"]):
                pairs.append({"geometry_trial": before["trial_id"],
                              "neighbor_trial": after["trial_id"],
                              "geometry": a, "neighbor": b})
        row = {"name": name, "manifest_audit": manifest, "execution_audit": audit,
               "candidates": candidates, "measured_timing_ready_ns_pairs": pairs,
               "physical_priority_path_exercised": bool(pairs),
               "certificate": summary["certificate"], "scientific_verdict": None}
        if normalization == "N1":
            row.pop("measured_timing_ready_ns_pairs")
            row.pop("physical_priority_path_exercised")
            row["resistance_domains"] = summary["resistance_domains"]
        records.append(row)
        write(output/"progress.json", records)
        print("END", name, audit["training_outcome"], flush=True)
    write(output/"index.json", {"kind": "native_"+normalization.lower()+"_proposal_controls", "schema_version": 1,
          "records": records, "scientific_verdict": None,
          "limits": "two inputs; 2000 Hz; declared ISI .01/.03; bare Train, no classification"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--normalization", choices=("N0", "N1"), default="N0")
    args = parser.parse_args()
    run(args.fixtures, args.runtime, args.output, args.normalization)


if __name__ == "__main__":
    main()
