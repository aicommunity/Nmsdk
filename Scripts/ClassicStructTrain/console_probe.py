#!/usr/bin/env python3
"""Run the unmodified console on an isolated copy of a prepared configuration."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

REPO = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=["learner", "trainer"], default="learner")
    parser.add_argument("--seconds", type=float, default=24)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("Probe directory already exists; preserve earlier evidence")
    source = REPO / "Bin/Configs/StructTrainClassic/Prepared" / args.kind
    shutil.copytree(source, output)
    binary = REPO / "Bin/Platform/Win/NeuroModelerConsole.exe"
    command = [str(binary), "--config", str(output/"project.ini"), "--start-calc", "--calc-time", str(args.seconds), "--exit-after-calc", "--save-project"]
    started = time.monotonic()
    with (output/"stdout.log").open("wb") as stdout, (output/"stderr.log").open("wb") as stderr:
        try:
            result = subprocess.run(command, cwd=binary.parent, stdout=stdout, stderr=stderr, timeout=180)
            status, exit_code = "completed", result.returncode
        except subprocess.TimeoutExpired:
            status, exit_code = "wall_timeout", None
    metadata = {"command": command, "cwd": str(binary.parent), "status": status, "exit_code": exit_code,
                "elapsed_wall_seconds": time.monotonic()-started, "kind": args.kind, "model_seconds": args.seconds}
    (output/"probe.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
