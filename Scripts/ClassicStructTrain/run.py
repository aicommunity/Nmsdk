#!/usr/bin/env python3
"""Supervise native replay processes and preserve every result and failure."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[2]
DEFAULT_BINARY = REPO / "Bin/Platform/Win/ClassicStructTrainReplay.exe"
MANIFEST = REPO / "Bin/Configs/StructTrainClassic/Prepared/manifest.json"
SUITES = ["cold", "warm", "structures", "recognition", "two_examples", "modes", "diagnostics"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def supervise(binary, manifest, output, suite, repeat, only_id, idle_timeout):
    output.mkdir(parents=True, exist_ok=True)
    status_file = output / "process.json"
    command = [str(binary), "--manifest", str(manifest), "--output", str(output),
               "--suite", suite, "--repeat", str(repeat)]
    if only_id:
        command += ["--only-id", str(only_id)]
    metadata = {"command": command, "cwd": str(binary.parent), "suite": suite, "repeat": repeat,
                "binary_sha256": digest(binary), "manifest_sha256": digest(manifest),
                "started_utc": datetime.now(timezone.utc).isoformat(), "status": "running"}
    save(status_file, metadata)
    env = os.environ.copy()
    env.pop("QT_PLUGIN_PATH", None)
    env.pop("QML2_IMPORT_PATH", None)
    env["QT_QPA_PLATFORM"] = "offscreen"
    start = last_progress = time.monotonic()
    previous_sizes = (-1, -1)
    timed_out = False
    print(f"Starting {suite}, repeat {repeat}", flush=True)
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        # Use the same scheduler class across independently started controllers.
        creation_flags = subprocess.NORMAL_PRIORITY_CLASS if os.name == 'nt' else 0
        proc = subprocess.Popen(command, cwd=binary.parent, env=env, stdout=stdout, stderr=stderr,
                                creationflags=creation_flags)
        metadata["pid"] = proc.pid
        metadata["process_priority"] = "Normal" if os.name == 'nt' else "default"
        save(status_file, metadata)
        while proc.poll() is None:
            paths = [output / "results.jsonl", output / "iterations.jsonl"]
            sizes = tuple(p.stat().st_size if p.exists() else 0 for p in paths)
            if sizes != previous_sizes:
                last_progress, previous_sizes = time.monotonic(), sizes
            if time.monotonic() - last_progress > idle_timeout:
                proc.kill()
                timed_out = True
                break
            time.sleep(0.5)
        return_code = proc.wait()
    metadata.update({"exit_code": return_code, "status": "idle_timeout" if timed_out else "completed" if return_code == 0 else "process_error",
                     "elapsed_wall_seconds": time.monotonic()-start, "finished_utc": datetime.now(timezone.utc).isoformat()})
    save(status_file, metadata)
    print(f"Finished {suite}, repeat {repeat}: {metadata['status']} ({metadata['elapsed_wall_seconds']:.1f}s)", flush=True)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=DEFAULT_BINARY)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--suite", choices=["all", "smoke"] + SUITES, default="smoke")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--only-id", type=int, default=0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--idle-timeout", type=float, default=660)
    parser.add_argument("--jobs", type=int, default=1, help="Independent native processes; all run from Bin/Platform/Win")
    args = parser.parse_args()
    if args.repeats < 1 or args.repeats > 3 or args.idle_timeout <= 0 or not 1 <= args.jobs <= 4:
        parser.error("repeats must be 1..3; idle timeout must be positive")
    binary, manifest = args.binary.resolve(), args.manifest.resolve()
    if any(part.lower() == "debug" for part in binary.parts):
        parser.error("Classic experiments must use Release; Debug binaries are not allowed")
    if not binary.is_file() or not manifest.is_file():
        parser.error("Build the replay binary and run prepare.py first")
    output = (args.output or REPO / "Reports/StructTrainClassic" / ("run-" + datetime.now().strftime("%Y%m%d-%H%M%S"))).resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Output directory is not empty; use a new run directory to preserve evidence")
    output.mkdir(parents=True, exist_ok=True)
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    tasks = [(suite, repeat, only_id)
             for suite in (SUITES if args.suite == "all" else [args.suite])
             for repeat in range(1, (1 if suite == "smoke" else args.repeats) + 1)
             for only_id in (manifest_data["selected_ids"] if suite == "recognition" and not args.only_id else [args.only_id])]
    def execute(task):
        suite, repeat, only_id = task
        name = f"{suite}" + (f"-id{only_id}" if only_id else "") + f"-r{repeat}"
        return supervise(binary, manifest, output / name, suite, repeat, only_id, args.idle_timeout)
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        jobs = list(executor.map(execute, tasks))
    save(output / "run.json", {"jobs": jobs, "complete": all(j["status"] == "completed" for j in jobs),
                               "binary": str(binary), "manifest": str(manifest)})
    print(output, flush=True)
    return 0 if all(j["status"] == "completed" for j in jobs) else 1


if __name__ == "__main__":
    sys.exit(main())
