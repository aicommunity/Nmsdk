"""Render every actual proposal-control probe and run production report checks."""
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
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipts", type=Path, required=True)
    args = parser.parse_args()
    index = load(args.primary/"index.json")
    require(len(index["records"]) == 2, "proposal_report_case_count")
    before = inventory(args.primary)
    args.output.mkdir(parents=True, exist_ok=False)
    args.receipts.mkdir(parents=True, exist_ok=False)
    start = time.time()
    rows = []
    for record in index["records"]:
        name = record["name"]
        print("RENDER", name, flush=True)
        result = render_pipeline_run(args.primary/name/"run-manifest.json", args.output/name)
        rows.append({"name": name, "training_trial_soma_pairs": result["training_trial_soma_pairs"]})
        write(args.receipts/"progress.json", rows)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               TIMELEARNER_NATIVE_PROPOSAL_CORPUS=str(args.primary),
               TIMELEARNER_NATIVE_PROPOSAL_REPORTS=str(args.output))
    with (args.receipts/"reader.log").open("w") as log:
        result = subprocess.run([sys.executable, "-m", "unittest", "-v",
                                 "Scripts.StructTrain.TimeLearner.tests.test_native_proposal_reports"],
                                env=env, stdout=log, stderr=subprocess.STDOUT)
    text = (args.receipts/"reader.log").read_text()
    require(result.returncode == 0 and "Ran 3 tests" in text and text.rstrip().endswith("OK")
            and "skipped" not in text, "proposal_temporal_checks_failed")
    require(before == inventory(args.primary), "proposal_primary_changed_during_render")
    write(args.receipts/"validation.json", {"status": 0, "reports": len(rows), "rows": rows,
          "source_files_unchanged": len(before), "wall_seconds": time.time()-start,
          "temporal_tests": 3, "manual_visual_review_complete": False, "scientific_verdict": None})


if __name__ == "__main__":
    main()
