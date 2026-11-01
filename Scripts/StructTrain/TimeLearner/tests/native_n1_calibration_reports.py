"""Render every measured threshold/pattern/soma of positive N1 calibration."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

from ..calibration_transaction_reports import render_calibration_run
from ..native_evidence import load, require
from .live_pipeline_corpus import write
from .native_dimension_reports import inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("primary", "output", "receipts"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    index = load(args.primary/"index.json")
    require(index["kind"] == "positive_n1_measured_calibration_controls" and len(index["records"]) == 2,
            "positive_n1_calibration_report_scope")
    before = inventory(args.primary)
    args.output.mkdir(parents=True, exist_ok=False)
    args.receipts.mkdir(parents=True, exist_ok=False)
    started = time.time();rows = []
    for row in index["records"]:
        name = row["name"]
        print("RENDER", name, flush=True)
        result = render_calibration_run(args.primary/"runs"/name/"run-manifest.json", args.output/name)
        rows.append({"name": name, "status": row["status"], "matrices": result["completed_matrices"],
                     "trial_soma_pairs": result["trial_soma_pairs"]})
        write(args.receipts/"progress.json", rows)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               TIMELEARNER_POSITIVE_N1_CALIBRATION=str(args.primary),
               TIMELEARNER_POSITIVE_N1_CALIBRATION_REPORTS=str(args.output))
    with (args.receipts/"reader.log").open("w") as log:
        result = subprocess.run([sys.executable, "-m", "unittest", "-v",
                 "Scripts.StructTrain.TimeLearner.tests.test_native_n1_calibration_reports"],
                 env=env, stdout=log, stderr=subprocess.STDOUT)
    text = (args.receipts/"reader.log").read_text()
    require(result.returncode == 0 and "Ran 3 tests" in text and text.rstrip().endswith("OK")
            and "skipped" not in text, "positive_n1_calibration_temporal_checks_failed")
    require(before == inventory(args.primary), "positive_n1_calibration_primary_changed_during_render")
    write(args.receipts/"validation.json", {"status": 0, "rows": rows,
        "source_files_unchanged": len(before), "temporal_tests": 3, "wall_seconds": time.time()-started,
        "manual_visual_review_complete": False, "scientific_verdict": None})


if __name__ == "__main__":
    main()
