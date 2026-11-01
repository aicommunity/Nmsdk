"""Run the old public preparer in its own interpreter, without copying it."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--case", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.source_root.resolve(strict=True)))
    # Deliberately imported only after selecting the immutable baseline tree.
    from Scripts.StructTrain.TimeLearner.tests.live_pipeline_corpus import make_job
    from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError
    job = json.loads((args.case/"input/job.json").read_text(encoding="utf-8"))
    recognition = json.loads((args.case/"native/recognition-model.json").read_text(encoding="utf-8"))
    template = {"source_recognition": recognition, "owner_class": job["owner_class"],
                "implementation_id": job["implementation_id"]}
    try:
        make_job(template, "baseline-preserve", legacy=True)
    except EvidenceError as error:
        if str(error) != "corpus_explicit_n0_synapse_domain_required":
            raise
        print(json.dumps({"baseline_incompatibility_reproduced": True, "reason": str(error)}))
        return 0
    raise RuntimeError("expected baseline incompatibility absent")


if __name__ == "__main__":
    raise SystemExit(main())
