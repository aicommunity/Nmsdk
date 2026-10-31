"""Ordered acceptance checks for a completed owned Console corpus.

The ordinary calibration class creates the two CLI probe runs used by the
provenance class. Run them explicitly in that order; module alphabetical order
can skip the dependent class and must never yield a positive gate.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import time
import unittest

from ..native_evidence import require


@contextmanager
def environment(values):
    saved={key:os.environ.get(key) for key in values}
    try:
        os.environ.update({key:str(value) for key,value in values.items()})
        yield
    finally:
        for key,value in saved.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value


def check_corpus(corpus, output):
    require((corpus/"corpus-summary.json").is_file(),"completed_corpus_summary_required")
    output.mkdir(parents=True,exist_ok=False)
    cli=output/"calibration-cli-probes"
    values={"TIMELEARNER_POSTTUNE_CONTROLLER_WORKER_DIR":corpus/"runs",
            "TIMELEARNER_OWNED_POSTTUNE_WORKER_DIR":corpus/"runs",
            "TIMELEARNER_NATIVE_CALIBRATION_WORKER_DIR":corpus/"calibration-regressions",
            "TIMELEARNER_CALIBRATION_OWNERSHIP_SOURCE":corpus/"source-fixtures",
            "TIMELEARNER_NATIVE_CALIBRATION_CLI_OUTPUT":cli,
            "TIMELEARNER_NATIVE_CALIBRATION_RUN_DIR":cli}
    groups=[("test_native_posttune_controller_worker.NativePostTuneControllerWorkerTest",4),
            ("test_owned_posttune_worker.OwnedPostTuneWorkerTest",3),
            ("test_native_calibration_worker.NativeCalibrationWorkerTest",8),
            ("test_native_calibration_worker.NativeCalibrationRunProvenanceTest",4)]
    start=time.monotonic();rows=[]
    report={"kind":"ordered_owned_console_acceptance","schema_version":1,"planned_tests":19,
            "execution":"running","groups":rows,"scientific_verdict":None,
            "driver_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    def save():
        report["seconds"]=time.monotonic()-start
        (output/"validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    save()
    with environment(values):
        for name,count in groups:
            # Provenance fixtures must have been created by the preceding class.
            if name.endswith("NativeCalibrationRunProvenanceTest"):
                require(all((cli/top/"run-manifest.json").is_file() for top in ("Classic","Branch")),
                        "provenance_checks_require_actual_cli_probe_runs")
            suite=unittest.defaultTestLoader.loadTestsFromName("Scripts.StructTrain.TimeLearner.tests."+name)
            result=unittest.TextTestRunner(verbosity=2).run(suite)
            rows.append({"class":name,"planned":count,"tests":result.testsRun,"failures":len(result.failures),
                         "errors":len(result.errors),"skipped":len(result.skipped)})
            passed=result.wasSuccessful() and result.testsRun==count and not result.skipped
            if not passed:report["execution"]="failed"
            save();require(passed,"incomplete_or_failed_owned_console_checks:"+name)
    report["execution"]="completed";report["tests"]=sum(r["tests"] for r in rows);save()
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args(argv)
    report=check_corpus(args.corpus.resolve(strict=True),args.output.resolve())
    print(json.dumps(report),flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
