#!/usr/bin/env python3
"""Online SoftCold experiment monitor via model-time autosave XML.

Polls active SoftCold workdirs: Parameters_00.xml Need/TipR/L + mtime,
Console/posttune PIDs, matrix log tail, RCS progress. Writes:
  - last_sample.json (overwrite)
  - softcold_monitor.jsonl (append)
  - monitor_status.txt (human one-liner append)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

NMSDK = Path(__file__).resolve().parents[4]  # .../Nmsdk
STRUCT = Path("/home/user/Nmsdk/Bin/Configs/SpikeSamples/StructTrain")
RUNS = STRUCT / "_repro" / "runs"
METRICS = Path(
    "/home/user/Nmsdk/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics"
)
RUN_TAG: str | None = None
MATRIX_LOG: Path | None = None
RCS_DIR: Path | None = None
RCS: Path | None = None
MANIFEST: Path | None = None
EXIT: Path | None = None


def configure_run_tag(tag: str) -> None:
    global RUN_TAG, MATRIX_LOG, RCS_DIR, RCS, MANIFEST, EXIT
    if not re.fullmatch(r"[A-Za-z0-9._-]+", tag):
        raise ValueError(f"invalid run tag: {tag!r}")
    RUN_TAG = tag
    MATRIX_LOG = METRICS / f"SOFTCOLD_full_matrix_{tag}.log"
    RCS_DIR = RUNS / f"rcs.d_{tag}"
    RCS = RUNS / f"SOFTCOLD_HEAD_rcs_{tag}.txt"
    MANIFEST = STRUCT / "_repro" / "SOFTCOLD_QUEUE_manifest.txt"
    EXIT = METRICS / f"SOFTCOLD_full_matrix_{tag}.exit"


def get_tag(text: str, tag: str) -> str | None:
    m = re.search(rf"<{tag}\b[^>]*>([^<]*)</{tag}>", text)
    return m.group(1).strip() if m else None


def pgrep(pattern: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["pgrep", "-af", pattern], text=True, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return []
    lines = []
    for line in out.splitlines():
        if "pgrep" in line or "monitor_softcold" in line:
            continue
        lines.append(line.strip())
    return lines


def latest_workdir() -> Path | None:
    if not RUNS.is_dir():
        return None
    cands = sorted(
        [p for p in RUNS.iterdir() if p.is_dir() and p.name.endswith("_work")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return cands[0] if cands else None


def sample_train(train: Path) -> dict:
    params = train / "Parameters_00.xml"
    model = train / "Model_00.xml"
    flag = train / "posttune_complete.flag"
    ini = train / "Project.ini"
    text = params.read_text(encoding="utf-8", errors="replace") if params.exists() else ""
    tipr = " ".join((get_tag(text, "TipSynapseResistance") or "").split())
    length = " ".join((get_tag(text, "DendriteLength") or "").split())
    need = (get_tag(text, "IsNeedToTrain") or "").strip()
    autosave_s = get_tag(
        ini.read_text(encoding="utf-8", errors="replace") if ini.exists() else "",
        "ProjectAutoSaveModelTimeInterval",
    )
    try:
        mtime = params.stat().st_mtime if params.exists() else 0.0
    except OSError:
        mtime = 0.0
    slog_gib = 0.0
    slog = train / "StatisticLog"
    if slog.is_dir():
        for p in slog.rglob("*"):
            if p.is_file():
                try:
                    slog_gib += p.stat().st_size
                except OSError:
                    pass
        slog_gib /= 1 << 30
    return {
        "need": need,
        "tipr": tipr[:80],
        "L": length[:40],
        "params_mtime": mtime,
        "params_mtime_iso": datetime.fromtimestamp(mtime, timezone.utc).isoformat()
        if mtime
        else None,
        "flag": flag.exists(),
        "autosave_model_s": autosave_s,
        "slog_gib": round(slog_gib, 3),
        "model_exists": model.exists(),
    }


def matrix_tail(n: int = 8) -> list[str]:
    if not MATRIX_LOG.exists():
        return []
    lines = MATRIX_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-n:]


def _parse_rc_rows(path: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return rows
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and parts[1].lstrip("-").isdigit():
            rows.append((parts[0], int(parts[1])))
    return rows


def rcs_summary() -> dict:
    expected = None
    if MANIFEST is not None and MANIFEST.exists():
        expected = sum(
            1
            for line in MANIFEST.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )

    rows: list[tuple[str, int]] = []
    source = "unavailable"
    last = None
    if RCS_DIR is not None and RCS_DIR.is_dir():
        source = str(RCS_DIR)
        newest = None
        for shard in RCS_DIR.glob("*.rc"):
            parts = shard.read_text(encoding="utf-8", errors="replace").split()
            if len(parts) >= 2 and parts[1].lstrip("-").isdigit():
                row = (parts[0], int(parts[1]))
                rows.append(row)
                mtime = shard.stat().st_mtime
                if newest is None or mtime > newest[0]:
                    newest = (mtime, row)
        if newest:
            last = f"{newest[1][0]} rc={newest[1][1]}"
    elif EXIT is not None and EXIT.exists() and RCS is not None and RCS.exists():
        source = str(RCS)
        rows = _parse_rc_rows(RCS)
        if rows:
            last = f"{rows[-1][0]} rc={rows[-1][1]}"

    return {
        "run_tag": RUN_TAG,
        "source": source,
        "done": len(rows),
        "expected": expected,
        "pass": sum(1 for _, rc in rows if rc == 0),
        "fail": sum(1 for _, rc in rows if rc != 0),
        "last": last,
    }


def collect() -> dict:
    work = latest_workdir()
    case = None
    train_snap = None
    if work:
        # asym50_preinh_20261001T171957Z_work → case=asym50_preinh
        m = re.match(r"^(.+?)_\d{8}T\d{6}Z_work$", work.name)
        case = m.group(1) if m else work.name
        train = work / "Train"
        if train.is_dir():
            train_snap = sample_train(train)
    consoles = pgrep("NeuroModelerConsole")
    posttunes = pgrep("posttune_verify.py")
    matrix = pgrep("softcold_full_matrix")
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "local": now,
        "run_tag": RUN_TAG,
        "case": case,
        "workdir": str(work) if work else None,
        "train": train_snap,
        "procs": {
            "matrix": len(matrix) > 0,
            "posttune": len(posttunes) > 0,
            "console": len(consoles) > 0,
            "console_cmd": consoles[:2],
            "posttune_cmd": posttunes[:2],
        },
        "rcs": rcs_summary(),
        "matrix_tail": matrix_tail(6),
    }
    return payload


def write_sample(payload: dict) -> None:
    METRICS.mkdir(parents=True, exist_ok=True)
    # Do not use last_sample.json — reserved by sample_host_metrics.py
    (METRICS / "softcold_last_sample.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (METRICS / "softcold_monitor.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    t = payload.get("train") or {}
    line = (
        f"{payload['local']} case={payload.get('case')} "
        f"Need={t.get('need')} TipR={(t.get('tipr') or '')[:40]} "
        f"L={t.get('L')} flag={int(bool(t.get('flag')))} "
        f"slog={t.get('slog_gib')}G "
        f"matrix={int(payload['procs']['matrix'])} "
        f"posttune={int(payload['procs']['posttune'])} "
        f"console={int(payload['procs']['console'])} "
        f"rcs={payload['rcs']['done']}/{payload['rcs'].get('expected') or '?'} "
        f"run={payload['rcs'].get('run_tag')}"
    )
    with (METRICS / "monitor_status.txt").open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=30.0, help="seconds between samples")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--run-tag", default=os.environ.get("SOFTCOLD_RUN_TAG"))
    args = ap.parse_args()
    if not args.run_tag:
        ap.error("--run-tag is required; refusing to read an unscoped/stale matrix summary")
    configure_run_tag(args.run_tag)
    while True:
        write_sample(collect())
        if args.once:
            break
        time.sleep(max(5.0, args.interval))


if __name__ == "__main__":
    main()
