"""All-pattern soma/input reports from actual fixed-threshold N1 handoffs."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

from ..live_pipeline_reports import render_pipeline_run
from ..native_evidence import load, require
from .live_pipeline_corpus import write
from .native_dimension_reports import inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("primary", "output", "receipts"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    index = load(args.primary/"index.json")
    require(index["kind"] == "native_n1_exact_handoff_controls" and len(index["records"]) == 2,
            "n1_handoff_report_scope")
    before = inventory(args.primary)
    args.output.mkdir(parents=True, exist_ok=False)
    args.receipts.mkdir(parents=True, exist_ok=False)
    started = time.time();rows = []
    for row in index["records"]:
        name = row["name"]
        print("RENDER", name, flush=True)
        result = render_pipeline_run(args.primary/"runs"/name/"run-manifest.json", args.output/name)
        rows.append({"name": name, "trial_soma_pairs": result["recognition_trial_soma_pairs"]})
        write(args.receipts/"progress.json", rows)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               TIMELEARNER_NATIVE_N1_HANDOFF_CORPUS=str(args.primary),
               TIMELEARNER_NATIVE_N1_HANDOFF_REPORTS=str(args.output))
    with (args.receipts/"reader.log").open("w") as log:
        result = subprocess.run([sys.executable, "-m", "unittest", "-v",
                 "Scripts.StructTrain.TimeLearner.tests.test_native_n1_handoff_reports"],
                 env=env, stdout=log, stderr=subprocess.STDOUT)
    text = (args.receipts/"reader.log").read_text()
    require(result.returncode == 0 and "Ran 3 tests" in text and text.rstrip().endswith("OK")
            and "skipped" not in text, "n1_handoff_temporal_checks_failed")
    require(before == inventory(args.primary), "n1_handoff_primary_changed_during_render")
    write(args.receipts/"validation.json", {"status": 0, "rows": rows,
        "source_files_unchanged": len(before), "temporal_tests": 3,
        "wall_seconds": time.time()-started, "manual_visual_review_complete": False,
        "scientific_verdict": None})


if __name__ == "__main__":
    main()
