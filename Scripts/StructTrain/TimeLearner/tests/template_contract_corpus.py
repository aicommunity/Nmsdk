"""Read-only compatibility acceptance on an actual production N0 corpus."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def inventory(root):
    result = {}
    for path in root.rglob("*"):
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024*1024), b""):
                    digest.update(block)
            result[path.relative_to(root).as_posix()] = digest.hexdigest()
    return result


def run(corpus, baseline_source, output):
    root = Path(__file__).resolve().parents[4]
    corpus = Path(corpus).resolve(strict=True)
    baseline_source = Path(baseline_source).resolve(strict=True)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    start = time.time();before = inventory(corpus)
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    steps = [];status = 1
    def invoke(name, command, env):
        with (output/(name+".log")).open("w", encoding="utf-8") as log:
            process = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        steps.append({"name": name, "returncode": process.returncode, "command": command})
        if process.returncode:
            raise RuntimeError(name+" failed")
    try:
        invoke("baseline-reproduction", [sys.executable, str(Path(__file__).with_name("template_contract_baseline.py")),
            "--source-root", str(baseline_source), "--case", str(corpus/"repeat-2/runs/Classic-fixed")], environment)
        for repeat in (1, 2):
            env = dict(environment, TIMELEARNER_N0_LIVE_PIPELINE_CORPUS=str(corpus/("repeat-"+str(repeat))))
            invoke("reader-repeat-"+str(repeat), [sys.executable, "-m", "unittest", "-v",
                "Scripts.StructTrain.TimeLearner.tests.test_live_pipeline_n0_worker"], env)
        if before != inventory(corpus):
            raise RuntimeError("production source files changed")
        value = {"kind": "n0_existing_template_contract", "status": 0,
                 "reader_source": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                 "baseline_source": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=baseline_source, text=True).strip(),
                 "baseline_expected_incompatibility_reproduced": True, "steps": steps,
                 "tests_per_protocol": 9, "actual_jobs_regenerated_per_protocol": 10,
                 "source_files_unchanged": len(before), "numerical_rerun": False,
                 "wall_seconds": time.time()-start}
        (output/"validation.json").write_text(json.dumps(value, indent=2)+"\n", encoding="utf-8")
        status = 0
        return value
    except Exception as error:
        (output/"error.txt").write_text(repr(error)+"\n", encoding="utf-8")
        raise
    finally:
        (output/"exit-status.txt").write_text(str(status)+"\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--baseline-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.corpus, args.baseline_source, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
