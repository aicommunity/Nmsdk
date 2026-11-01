"""Render all original dimension-control Train probes to a worker cache."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time

from ..live_pipeline_reports import render_pipeline_run
from ..native_evidence import load, require
from .live_pipeline_corpus import write


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, required=True,
                        help="restored proof root with a1/corpus and a2/corpus")
    parser.add_argument("--output", type=Path, required=True, help="new full report cache")
    parser.add_argument("--receipts", type=Path, required=True, help="new compact receipt directory")
    args = parser.parse_args()
    before = inventory(args.primary)
    args.output.mkdir(parents=True, exist_ok=False)
    args.receipts.mkdir(parents=True, exist_ok=False)
    start = time.time()
    rows = []
    for attempt in ("a1", "a2"):
        corpus = args.primary/attempt/"corpus"
        reports = args.output/attempt
        reports.mkdir()
        for record in load(corpus/"index.json")["records"]:
            name = record["name"]
            print("RENDER", attempt, name, flush=True)
            result = render_pipeline_run(corpus/"runs"/name/"run-manifest.json", reports/name)
            rows.append({"attempt": attempt, "name": name,
                         "training_trial_soma_pairs": result["training_trial_soma_pairs"]})
            write(args.receipts/"progress.json", rows)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   TIMELEARNER_NATIVE_DIMENSION_CORPUS=str(corpus),
                   TIMELEARNER_NATIVE_DIMENSION_REPORTS=str(reports))
        with (args.receipts/(attempt+"-reader.log")).open("w") as log:
            result = subprocess.run([sys.executable, "-m", "unittest", "-v",
                                     "Scripts.StructTrain.TimeLearner.tests.test_native_dimension_reports"],
                                    env=env, stdout=log, stderr=subprocess.STDOUT)
        text = (args.receipts/(attempt+"-reader.log")).read_text()
        require(result.returncode == 0 and "Ran 3 tests" in text and text.rstrip().endswith("OK")
                and "skipped" not in text, "dimension_temporal_checks_failed:"+attempt)
    require(len(rows) == 16, "dimension_report_case_count")
    require(before == inventory(args.primary), "dimension_primary_changed_during_render")
    write(args.receipts/"validation.json", {"status": 0, "reports": len(rows), "rows": rows,
          "source_files_unchanged": len(before), "wall_seconds": time.time()-start,
          "temporal_tests_per_attempt": 3, "manual_visual_review_complete": False,
          "scientific_verdict": None})


if __name__ == "__main__":
    main()
