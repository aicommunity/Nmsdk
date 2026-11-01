#!/usr/bin/env python3
"""Run a fixed-threshold C++ inference grid on independent Test copies.

This is an experiment orchestrator: it copies one prepared Test project,
changes only inference threshold/harness fields, invokes NeuroModelerConsole,
and records the resulting CSVs and metrics. It does not run or implement
training logic.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def set_tag(text: str, tag: str, value: str, *, required: bool = True) -> str:
    pattern = re.compile(rf"(<{re.escape(tag)}\b[^>]*>)[^<]*(</{re.escape(tag)}>)")
    updated, count = pattern.subn(lambda match: match.group(1) + value + match.group(2), text)
    if count == 0 and required:
        raise ValueError(f"required XML tag not found: {tag}")
    return updated


def patch_project(project: Path, threshold: str, name: str) -> None:
    for filename in ("Parameters_00.xml", "Model_00.xml"):
        path = project / filename
        text = path.read_text(encoding="utf-8")
        for tag, value in (
            ("FixedLTZThreshold", threshold),
            ("LTZThreshold", threshold),
            ("UseFixedLTZThreshold", "1"),
            ("IsNeedToTrain", "0"),
            ("EnablePostTrainTuning", "0"),
        ):
            text = set_tag(text, tag, value)
        for tag in ("AutoCalibrateFixedLTZThreshold", "EnablePostTrainMidThreshold"):
            text = set_tag(text, tag, "0", required=False)
        path.write_text(text, encoding="utf-8")

    ini = project / "Project.ini"
    text = ini.read_text(encoding="utf-8")
    text = set_tag(text, "ProjectName", name)
    for tag in ("DebugModeFlag", "EventsLogMode", "DebugSysEventsMask"):
        pattern = re.compile(rf"(<{tag}\b[^>]*>)[^<]*(</{tag}>)")
        text = pattern.sub(lambda match: match.group(1) + "0" + match.group(2), text)
    ini.write_text(text, encoding="utf-8")

    for stale_name in ("posttune_complete.flag", "run_infer_mid.log", "run_posttune_gate.log"):
        (project / stale_name).unlink(missing_ok=True)


def csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))
    except (OSError, csv.Error):
        return []


def terminate(proc: subprocess.Popen[Any]) -> int:
    if proc.poll() is not None:
        return int(proc.returncode)
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        return int(proc.wait(timeout=30))
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return int(proc.wait(timeout=30))


def run_one(
    *,
    source_test: Path,
    output: Path,
    console: Path,
    threshold: str,
    time_s: float,
    max_wall_s: float,
    stop_rows: int,
    min_wall_s: float,
    analyzer: Path | None,
) -> dict[str, Any]:
    label = threshold.replace(".", "p").replace("-", "m")
    project = output / f"thr_{label}"
    shutil.copytree(source_test, project)
    patch_project(project, threshold, f"TimeLearnerThresholdProbe_{label}")

    stale_flag = project / "posttune_complete.flag"
    stale_flag.unlink(missing_ok=True)
    csv_path = project / "SelectivityLog" / "results.csv"
    if csv_path.parent.exists():
        shutil.rmtree(csv_path.parent)

    log_path = project / "threshold_inference.log"
    cmd = [str(console), "-c", str(project / "Project.ini"), "-s", "-t", str(time_s), "-x"]
    started = time.monotonic()
    status = "exited"
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=project,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        while proc.poll() is None:
            elapsed = time.monotonic() - started
            rows_now = csv_rows(csv_path)
            if len(rows_now) >= stop_rows and elapsed >= min_wall_s:
                status = "stopped_after_rows"
                return_code = terminate(proc)
                break
            if elapsed >= max_wall_s:
                status = "wall_timeout"
                return_code = terminate(proc)
                break
            time.sleep(2)
        else:
            return_code = int(proc.returncode)

    rows = csv_rows(csv_path)
    fires = "".join("1" if row.get("neuron_fired") == "1" else "0" for row in rows)
    result: dict[str, Any] = {
        "threshold": threshold,
        "project": str(project),
        "status": status,
        "return_code": return_code,
        "wall_seconds": round(time.monotonic() - started, 2),
        "rows": len(rows),
        "fires": fires,
        "target_class": [row.get("target_class", "") for row in rows],
        "neuron_fired": [row.get("neuron_fired", "") for row in rows],
        "soma_amp_sum": [row.get("soma_amp_sum", "") for row in rows],
        "csv": str(csv_path) if csv_path.is_file() else None,
        "csv_sha256": sha256(csv_path) if csv_path.is_file() else None,
        "log": str(log_path),
    }
    if analyzer and csv_path.is_file():
        analyzed = subprocess.run(
            [sys.executable, str(analyzer), "-v", str(csv_path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        result["metrics_return_code"] = analyzed.returncode
        result["metrics"] = analyzed.stdout.strip()
    # Console writes bulky per-step traces and verbose event logs even for
    # inference. The CSV, metrics, hashes, and stdout log above are the evidence.
    for generated_logs in ("StatisticLog", "EventsLog"):
        log_dir = project / generated_logs
        if log_dir.is_dir():
            shutil.rmtree(log_dir)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-test", type=Path, required=True)
    parser.add_argument("--console", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--analyzer", type=Path)
    parser.add_argument("--thresholds", required=True, help="comma-separated fixed LTZ thresholds")
    parser.add_argument("--time-s", type=float, default=40.0)
    parser.add_argument("--parallel", type=int, default=8)
    parser.add_argument("--max-wall-s", type=float, default=900.0)
    parser.add_argument("--stop-rows", type=int, default=8)
    parser.add_argument("--min-wall-s", type=float, default=180.0)
    args = parser.parse_args()

    source_test = args.source_test.resolve()
    console = args.console.resolve()
    output = args.output_dir.resolve()
    thresholds = [part.strip() for part in args.thresholds.split(",") if part.strip()]
    if not source_test.is_dir() or not console.is_file():
        parser.error("source Test directory and Console binary must exist")
    if not thresholds or len(set(thresholds)) != len(thresholds):
        parser.error("threshold list must be nonempty and unique")
    if not 1 <= args.parallel <= 8:
        parser.error("parallelism must be between 1 and 8")
    if output.exists():
        parser.error(f"output directory already exists: {output}")
    output.mkdir(parents=True)

    manifest: dict[str, Any] = {
        "schema": 1,
        "source_test": str(source_test),
        "console": str(console),
        "console_sha256": sha256(console),
        "source_hashes": {
            name: sha256(source_test / name)
            for name in ("Project.ini", "Parameters_00.xml", "Model_00.xml", "Interface.xml")
        },
        "orchestrator": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "thresholds": thresholds,
        "time_s": args.time_s,
        "parallel": args.parallel,
        "stop_rows": args.stop_rows,
        "min_wall_s": args.min_wall_s,
        "max_wall_s": args.max_wall_s,
        "training": "disabled; fixed-threshold C++ Test inference only",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {
            pool.submit(
                run_one,
                source_test=source_test,
                output=output,
                console=console,
                threshold=threshold,
                time_s=args.time_s,
                max_wall_s=args.max_wall_s,
                stop_rows=args.stop_rows,
                min_wall_s=args.min_wall_s,
                analyzer=args.analyzer.resolve() if args.analyzer else None,
            ): threshold
            for threshold in thresholds
        }
        for future in concurrent.futures.as_completed(futures):
            threshold = futures[future]
            try:
                current = future.result()
            except Exception as exc:  # retain partial batch evidence per threshold
                current = {"threshold": threshold, "status": "orchestrator_error", "error": repr(exc)}
            results.append(current)
            results.sort(key=lambda row: float(row["threshold"]))
            (output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(current, ensure_ascii=False), flush=True)

    complete = all(
        row.get("rows", 0) >= args.stop_rows
        and (
            row.get("status") == "stopped_after_rows"
            or (row.get("status") == "exited" and row.get("return_code") == 0)
        )
        for row in results
    )
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
