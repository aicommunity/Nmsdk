"""Run declared historical Console controls through the production CLI.

Inputs are explicit, immutable jobs/controls and original Train primaries. This
is an acceptance corpus, not a new scientific experiment or automatic Train.
"""
import argparse
from copy import deepcopy
import contextlib
import json
from pathlib import Path

from ..__main__ import main as cli
from ..model_identity import canonical_model_sha256 as sha
from ..native_calibration_worker import audit_execution, audit_run_manifest
from ..native_evidence import load, require
from ..learned_evidence import load_case
from ..process_runner import execute, verify_runtime


def write(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def signed(value):
    value.pop("sha256",None);value["sha256"]=sha(value);return value


def run_corpus(jobs, controls_path, fixtures, runtime_path, output, wall_seconds):
    runtime = load(runtime_path); executable = verify_runtime(runtime)
    controls = load(controls_path)["records"]
    require(len(controls)==18 and len({c["name"] for c in controls})==18,"requires_eighteen_declared_controls")
    sources = {}
    for path in fixtures.rglob("*_learned_state.json"):
        digest = load(path)["sha256"]
        require(digest not in sources,"duplicate_corpus_source")
        sources[digest]=path
    require(len(sources)==2,"requires_two_original_train_sources")
    output.mkdir(parents=True,exist_ok=False)
    source_copy=output/"source-fixtures";source_copy.mkdir()
    # Retain a flat portable copy for the unchanged calibration regression suite.
    for digest,path in list(sources.items()):
        stem=path.name.removesuffix("_learned_state.json")
        paths=[path,path.with_name(stem+"_learned_summary.json")]
        for packet in sorted(path.parent.glob(stem+"_state_trial_*.json")):
            paths.extend((packet,packet.with_suffix(".csv")))
        for original in paths:
            require(original.is_file() and not original.is_symlink(),"corpus_primary_missing_or_symlink")
            target=source_copy/original.name;require(not target.exists(),"corpus_primary_collision")
            target.write_bytes(original.read_bytes())
        sources[digest]=source_copy/path.name
    declared=output/"jobs";declared.mkdir()
    runs=output/"runs";runs.mkdir()
    for control in controls:
        name=control["name"];job=load(jobs/(name+".json"))
        job["specification"]["attempt_id"]="owned-console/"+name;signed(job)
        source=sources[job["source_recognition"]["source_solo"]["sha256"]]
        path=declared/(name+".json");write(path,job)
        print("BEGIN",name,flush=True)
        with (output/(name+"-cli.log")).open("w") as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            code=cli(["posttune",str(path),"--source-solo",str(source),"--runtime-manifest",str(runtime_path),
                      "--wall-seconds",str(wall_seconds),"--output",str(runs/name)])
        require(code==0,"owned_console_cli_failed:"+name)
        audit_run_manifest(runs/name/"run-manifest.json",post_tune=True)
        execution=load(runs/name/"native/execution.json")
        require(execution["schema_version"]==2 and execution["post_tune_status"]==control["expected_status"],
                "owned_console_outcome_changed:"+name)
        print("DONE",name,execution["post_tune_status"],flush=True)
    write(runs/"controls.json",{"records":controls,"scientific_verdict":None})

    fixed=output/"fixed-runs";fixed.mkdir()
    calibration=output/"calibration-regressions";calibration.mkdir()
    (calibration/"runtime-before.json").write_bytes(runtime_path.read_bytes())
    for topology in ("Classic","Branch"):
        baseline=load(jobs/(topology+"-keep.json"))
        source=sources[baseline["source_recognition"]["source_solo"]["sha256"]]
        job=deepcopy(baseline);job["schema_version"]=3
        job["post_tune"].update(schema_version=3,finalization="keep_fixed_threshold",weight_probe_threshold=2.)
        job["thresholds"]=[];job["maximum_candidates"]=0
        job["specification"]["attempt_id"]="owned-console/"+topology+"-fixed";signed(job)
        path=declared/(topology+"-fixed.json");write(path,job)
        with (output/(topology+"-fixed-cli.log")).open("w") as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
            code=cli(["posttune",str(path),"--source-solo",str(source),"--runtime-manifest",str(runtime_path),
                      "--wall-seconds",str(wall_seconds),"--output",str(fixed/(topology+"-fixed"))])
        require(code==0,"owned_fixed_console_cli_failed:"+topology)
        audit_run_manifest(fixed/(topology+"-fixed")/"run-manifest.json",post_tune=True)
        print("FIXED DONE",topology,flush=True)
        for case,status in (("success","calibrated"),("nonseparable","nonseparable"),("budget","budget_exhausted")):
            job=deepcopy(baseline);job.pop("post_tune")
            job["kind"]="timelearner_native_calibration_job";job["schema_version"]=1
            job["specification"]["attempt_id"]="owned-console/calibration/"+topology+"-"+case
            if case=="nonseparable":job["thresholds"]=[1e9];job["maximum_candidates"]=1
            if case=="budget":job["thresholds"]=[1e9,5e8];job["maximum_candidates"]=1
            signed(job);path=calibration/(topology+"-"+case+"-job.json");write(path,job)
            directory=calibration/(topology+"-"+case)
            result=execute(runtime,["--app-ini",runtime["app_ini"]["path"],"--timelearner-calibrate",str(path),
                "--timelearner-output",str(directory)],executable.parent,calibration/(topology+"-"+case+"-process"),wall_seconds)
            require(result["execution"]=="completed","unchanged_calibration_execution_failed")
            audit_execution(directory,job,load_case(source))
            require(load(directory/"transaction.json")["status"]==status,"unchanged_calibration_status_changed")
            require(load(directory/"execution.json")["schema_version"]==1,"standalone_calibration_schema_changed")
            print("CALIBRATION DONE",topology,case,flush=True)
    verify_runtime(runtime)
    return {"post_tune_calibrated_controls":18,"fixed_probe_controls":2,"standalone_calibration_controls":6,
            "scientific_verdict":None,"live_train_handoff_implemented":False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("jobs","controls","fixtures","runtime","output"):
        parser.add_argument("--"+name,required=True,type=Path)
    parser.add_argument("--wall-seconds",type=float,required=True)
    args=parser.parse_args(argv)
    result=run_corpus(args.jobs.resolve(strict=True),args.controls.resolve(strict=True),args.fixtures.resolve(strict=True),
        args.runtime.resolve(strict=True),args.output.resolve(),args.wall_seconds)
    write(args.output/"corpus-summary.json",result)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
