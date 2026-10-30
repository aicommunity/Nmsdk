#!/usr/bin/env python3
"""E1.1g — Console Branch soma IR at island L/TipR: nextseg vs gen Pack-A TRACE.

Test-only (IsNeedToTrain=0), PostTune OFF, short -t, wall kill ≤3 min to avoid
posttune_mid_dbg / TRACE hang (DEBT-A3 / E1.1d). Measures soma_sum peak / t_peak /
FWHM per Pack-A sample and sep_margin vs E1.4 ideal_inh_proxy (τ=0.5 ms, +0.074).

Attempt-local overlays only — does not touch shared Train/Test inputs.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
NMSDK = HERE.parents[4]
ST = NMSDK / "Bin" / "Configs" / "SpikeSamples" / "StructTrain"
SCRIPTS = ST / "scripts"
TOOLS_PLAN = (
    NMSDK
    / "Docs"
    / "Audit"
    / "TimeLearner-2026-09-26-review"
    / "plans"
    / "AGENT_PLAN_2026-10-20"
    / "tools"
)
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TOOLS_PLAN))
from repro_cold_lib import (  # noqa: E402
    enable_pattern_response_trace,
    get_tag,
    set_tag,
    set_tag_all,
)
from selectivity_metrics import classify  # noqa: E402

DEFAULT_CONSOLE = NMSDK / "Bin" / "Platform" / "Linux" / "NeuroModelerConsole"
DEFAULT_WORK = Path.home() / "TLAgent-20261020" / "scratch" / "E1_1g_CONSOLE_IR"

ISLAND_L = [7, 6, 4, 1]
ISLAND_TIPR = [2e7, 2e7, 2e7, 8.6e7]
# E1.5 / E2 PASS FixedLTZ for br25_nextseg at island (Acc arm)
NEXTSEG_LTZ = 0.10023275299347018
# IR arm: high threshold so soma EPSP is not collapsed by LTZ spike (FWHM artifact)
IR_LTZ = 100.0
PROXY_SEP = 0.074361
PROXY_FWHM_MS = 2.1  # E1.1f / E1.4 τ=0.5 ms matched-filter
FWHM_GATE_MS = 3.25  # FWHM/span25 ≤ 0.13
SPAN_MS = 25.0

CASES = {
    "nextseg": {
        "mod": "nextseg",
        "trainer_mode": "Branch×N1",
        "neuron_model": "AsymRm",
        "template": ST
        / "SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test",
        "train_link": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/"
        "EXP_br_span25_packA_nextseginh_C1e9/Train",
        "test_link": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/"
        "EXP_br_span25_packA_nextseginh_C1e9/Test",
        "template_L": [13, 11, 7, 1],
        "fixed_ltz": IR_LTZ,
        "acc_ltz": NEXTSEG_LTZ,
    },
    "gen": {
        "mod": "gen",
        "trainer_mode": "Branch×N1",
        "neuron_model": "AsymRm",
        "template": ST / "SelectivityBranch/EXP_br_span25_packA_gen_C1e9/Test",
        "train_link": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/"
        "EXP_br_span25_packA_gen_C1e9/Train",
        "test_link": "Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/"
        "EXP_br_span25_packA_gen_C1e9/Test",
        "template_L": [13, 11, 7, 1],
        "fixed_ltz": IR_LTZ,
        "acc_ltz": NEXTSEG_LTZ,
    },
}


def fmt_tipr(vals: list[float]) -> str:
    return " ".join(format(v, ".17g") for v in vals)


def fmt_L(vals: list[int]) -> str:
    return " ".join(str(v) for v in vals)


def apply_freeze(test_dir: Path, *, lengths: list[int], tipr: list[float], fixed_ltz: float) -> list[str]:
    report: list[str] = []
    tipr_s = fmt_tipr(tipr)
    L_s = fmt_L(lengths)
    mid = format(fixed_ltz, ".17g")
    sbm = "1"  # island L ≠ template morphology
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = test_dir / rel
        t = p.read_text(encoding="utf-8", errors="replace")
        for name, val in (
            ("IsNeedToTrain", "0"),
            ("StructureBuildMode", sbm),
            ("DendriteLength", L_s),
            ("TipSynapseResistance", tipr_s),
            ("FixedLTZThreshold", mid),
            ("LTZThreshold", mid),
            ("UseFixedLTZThreshold", "1"),
            ("AutoCalibrateFixedLTZThreshold", "0"),
            ("EnablePostTrainTuning", "0"),
            ("EnablePostTrainMidThreshold", "0"),
        ):
            if get_tag(t, name) is None and name.startswith("EnablePost"):
                continue
            if name in (
                "DendriteLength",
                "TipSynapseResistance",
                "IsNeedToTrain",
                "StructureBuildMode",
                "FixedLTZThreshold",
                "LTZThreshold",
            ):
                t = set_tag_all(t, name, val)
            else:
                t = set_tag(t, name, val, 0)
        p.write_text(t, encoding="utf-8")
        report.append(f"{rel}: L={L_s} TipR={tipr_s} SBM={sbm} mid={mid} PT=0")
    for junk in ("SelectivityLog", "StatisticLog", "EventsLog", "posttune_complete.flag", "posttune_mid_dbg.txt"):
        jp = test_dir / junk
        if jp.is_dir():
            shutil.rmtree(jp)
        elif jp.exists():
            jp.unlink()
    (test_dir / "SelectivityLog").mkdir(parents=True, exist_ok=True)
    enable_pattern_response_trace(test_dir / "Model_00.xml")
    report.append("TRACE_ENABLED")
    return report


def find_trace(probe: Path) -> Path | None:
    traces = sorted(probe.rglob("test_trace.csv"))
    return traces[0] if traces else None


def csv_nrows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open(encoding="utf-8") as f:
            return max(0, sum(1 for _ in f) - 1)
    except OSError:
        return 0


def run_console(
    console: Path,
    probe: Path,
    sim_t: float,
    wall_timeout_s: int,
) -> dict:
    """Run Console; kill when results.csv has ≥8 rows or wall timeout (TRACE hang)."""
    ini = probe / "Project.ini"
    csv_path = probe / "SelectivityLog" / "results.csv"
    log = probe / "console.log"
    pin = Path.home() / "tl-agent" / "lib"
    env = os.environ.copy()
    if pin.is_dir():
        env["LD_LIBRARY_PATH"] = f"{pin}:{env.get('LD_LIBRARY_PATH', '')}"
    cmd = [str(console), "-c", str(ini), "-s", "-t", str(sim_t), "-x", "-S"]
    t0 = time.time()
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen(
            cmd, cwd=str(probe), stdout=fh, stderr=subprocess.STDOUT, env=env
        )
    err = ""
    mid_dbg = probe / "posttune_mid_dbg.txt"
    mid_grow_t0: float | None = None
    mid_last_sz = -1
    while proc.poll() is None:
        elapsed = time.time() - t0
        if elapsed > wall_timeout_s:
            err = "wall_timeout"
            proc.terminate()
            break
        # Kill if mid_dbg grows for >90s (E1.1d hang signature)
        if mid_dbg.exists():
            sz = mid_dbg.stat().st_size
            if sz > mid_last_sz:
                mid_last_sz = sz
                if mid_grow_t0 is None:
                    mid_grow_t0 = time.time()
            if mid_grow_t0 is not None and (time.time() - mid_grow_t0) > 90:
                err = "mid_dbg_hang"
                proc.terminate()
                break
        if csv_nrows(csv_path) >= 8:
            # allow TRACE flush; then kill (known TRACE hang after CSV)
            time.sleep(3.0)
            if proc.poll() is None:
                err = "sigterm_csv8"
                proc.terminate()
            break
        tr = find_trace(probe)
        # Pack-A IR: ~8 × 30k rows; if TRACE already has sample_id 0..7, kill even if CSV lags
        if tr and csv_nrows(tr) >= 8 * 28000:
            time.sleep(2.0)
            if proc.poll() is None:
                err = "sigterm_trace8"
                proc.terminate()
            break
        time.sleep(1.0)
    try:
        rc = proc.wait(timeout=25)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            rc = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            rc = -9
        err = err or "kill_after_term"
    wall = round(time.time() - t0, 1)
    return {
        "rc": rc,
        "err": err,
        "wall_s": wall,
        "csv_rows": csv_nrows(csv_path),
        "trace": str(find_trace(probe) or ""),
        "mid_dbg_bytes": mid_dbg.stat().st_size if mid_dbg.exists() else 0,
    }


def fwhm_ms(times: list[float], vals: list[float]) -> tuple[float | None, float, float | None]:
    """Baseline-subtract peak / t_peak / FWHM (ms) on soma_sum window."""
    if not vals:
        return None, 0.0, None
    base = vals[0]
    vv = [x - base for x in vals]
    k = max(range(len(vv)), key=lambda i: vv[i])
    pk = vv[k]
    if pk <= 1e-12:
        return 0.0, times[k] if times else 0.0, None
    half = pk / 2.0
    lo = next((i for i in range(len(vv)) if vv[i] >= half), None)
    hi = next((i for i in range(len(vv) - 1, -1, -1) if vv[i] >= half), None)
    if lo is None or hi is None or hi <= lo:
        return pk, times[k], None
    return pk, times[k], (times[hi] - times[lo]) * 1000.0


def analyze_trace(trace: Path) -> list[dict]:
    rows_by_sample: dict[int, list[dict]] = {}
    with trace.open(encoding="utf-8") as f:
        hdr = f.readline().strip().split(",")
        for line in f:
            p = line.strip().split(",")
            if len(p) != len(hdr):
                continue
            r = dict(zip(hdr, p))
            try:
                sid = int(float(r["sample_id"]))
            except (KeyError, ValueError):
                continue
            rows_by_sample.setdefault(sid, []).append(r)
    out = []
    for sid in sorted(rows_by_sample):
        rs = rows_by_sample[sid]
        times = [float(r["time_rel_s"]) for r in rs]
        soma = [float(r["soma_sum"]) for r in rs]
        ltz = [float(r["ltz_potential"]) for r in rs]
        pk, tpk, fwhm = fwhm_ms(times, soma)
        lpk = max(ltz) if ltz else 0.0
        tc = rs[0].get("target_class", "")
        out.append(
            {
                "sample_id": sid,
                "target_class": tc,
                "n_samples": len(rs),
                "soma_peak": pk,
                "t_peak_s": tpk,
                "fwhm_ms": fwhm,
                "ltz_peak": lpk,
                "t_end_s": times[-1] if times else None,
            }
        )
    return out


def sep_margin(peaks: list[float]) -> float | None:
    if len(peaks) < 2 or not (peaks[0] == peaks[0] and peaks[0] > 0):
        return None
    foils = [p for p in peaks[1:] if p == p]
    if not foils:
        return None
    return (peaks[0] - max(foils)) / peaks[0]


def prepare_one(mod: str, work: Path) -> Path:
    spec = CASES[mod]
    out = work / mod
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(spec["template"], out, symlinks=False)
    apply_freeze(out, lengths=ISLAND_L, tipr=ISLAND_TIPR, fixed_ltz=spec["fixed_ltz"])
    return out


def run_one(mod: str, work: Path, console: Path, sim_t: float, wall: int) -> dict:
    spec = CASES[mod]
    probe = prepare_one(mod, work)
    run = run_console(console, probe, sim_t, wall)
    csv_path = probe / "SelectivityLog" / "results.csv"
    metrics: dict = {}
    fires = acc = cel = mode = ""
    sep_csv = None
    if csv_path.exists() and csv_nrows(csv_path) >= 1:
        with csv_path.open(encoding="utf-8", newline="") as f:
            crow = list(csv.DictReader(f))
        try:
            metrics = classify(crow)
            fires = str(metrics.get("fires", "") or "")
            acc_n = int(metrics.get("acc", 0) or 0)
            n = int(metrics.get("n", 0) or 0)
            acc = f"{acc_n}/{n}" if n else str(acc_n)
            cel = "да" if int(metrics.get("target_hit", 0) or 0) == 1 else "нет"
            mode = str(metrics.get("mode", "") or "")
        except Exception as e:  # noqa: BLE001
            run["err"] = (run.get("err") or "") + f";classify:{e}"
        peaks_ltz = []
        for r in crow[:8]:
            try:
                peaks_ltz.append(float(r.get("ltz_potential_max") or "nan"))
            except ValueError:
                peaks_ltz.append(float("nan"))
        sep_csv = sep_margin(peaks_ltz)
    trace_path = find_trace(probe)
    samples = analyze_trace(trace_path) if trace_path else []
    soma_peaks = [s["soma_peak"] for s in samples[:8] if s.get("soma_peak") is not None]
    sep_soma = sep_margin(soma_peaks) if len(soma_peaks) >= 2 else None
    tgt = samples[0] if samples else {}
    return {
        "mod": mod,
        "trainer_mode": spec["trainer_mode"],
        "span_ms": int(SPAN_MS),
        "neuron_model": spec["neuron_model"],
        "L": fmt_L(ISLAND_L),
        "TipR": fmt_tipr(ISLAND_TIPR),
        "FixedLTZ": spec["fixed_ltz"],
        "probe": str(probe),
        "train_config": spec["train_link"],
        "test_config": spec["test_link"],
        **run,
        "Acc": acc or "—",
        "Цель": cel or "—",
        "fires": fires,
        "mode": mode,
        "sep_ltz_csv": sep_csv,
        "sep_soma_trace": sep_soma,
        "tgt_soma_peak": tgt.get("soma_peak"),
        "tgt_t_peak_s": tgt.get("t_peak_s"),
        "tgt_fwhm_ms": tgt.get("fwhm_ms"),
        "tgt_ltz_peak": tgt.get("ltz_peak"),
        "n_trace_samples": len(samples),
        "samples": samples,
        "proxy_sep": PROXY_SEP,
        "proxy_fwhm_ms": PROXY_FWHM_MS,
        "fwhm_gate_ms": FWHM_GATE_MS,
        "fwhm_gate_ok": (
            tgt.get("fwhm_ms") is not None and tgt["fwhm_ms"] <= FWHM_GATE_MS
        ),
        "narrowing_vs_proxy": (
            None
            if tgt.get("fwhm_ms") is None
            else tgt["fwhm_ms"] / PROXY_FWHM_MS
        ),
    }


def write_tsv(rows: list[dict], path: Path) -> None:
    cols = [
        "mod",
        "trainer_mode",
        "span_ms",
        "neuron_model",
        "L",
        "TipR",
        "FixedLTZ",
        "Acc",
        "Цель",
        "fires",
        "sep_ltz_csv",
        "sep_soma_trace",
        "tgt_soma_peak",
        "tgt_t_peak_s",
        "tgt_fwhm_ms",
        "fwhm_gate_ok",
        "narrowing_vs_proxy",
        "proxy_sep",
        "proxy_fwhm_ms",
        "rc",
        "err",
        "wall_s",
        "csv_rows",
        "n_trace_samples",
        "mid_dbg_bytes",
        "trace",
        "train_config",
        "test_config",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in cols})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", type=Path, default=DEFAULT_WORK)
    ap.add_argument("--console", type=Path, default=DEFAULT_CONSOLE)
    ap.add_argument("--mods", default="nextseg,gen")
    ap.add_argument("--sim-t", type=float, default=40.0, help="Console -t seconds")
    ap.add_argument(
        "--wall",
        type=int,
        default=180,
        help="wall timeout seconds (kill TRACE/mid_dbg hang)",
    )
    ap.add_argument(
        "--tsv",
        type=Path,
        default=EVIDENCE / "E1_1g_CONSOLE_BRANCH_IR_2026-10-22.tsv",
    )
    ap.add_argument(
        "--json",
        type=Path,
        default=EVIDENCE / "E1_1g_CONSOLE_BRANCH_IR_2026-10-22.json",
    )
    ap.add_argument("--prepare-only", action="store_true")
    a = ap.parse_args()
    a.workdir.mkdir(parents=True, exist_ok=True)
    mods = [m.strip() for m in a.mods.split(",") if m.strip()]
    if a.prepare_only:
        for m in mods:
            p = prepare_one(m, a.workdir)
            print(json.dumps({"mod": m, "probe": str(p)}, ensure_ascii=False))
        return
    if not a.console.is_file():
        raise SystemExit(f"NO_CONSOLE {a.console}")
    rows = []
    for m in mods:
        print(f"RUN {m} …", flush=True)
        r = run_one(m, a.workdir, a.console, a.sim_t, a.wall)
        rows.append(r)
        print(
            json.dumps(
                {
                    "mod": m,
                    "err": r["err"],
                    "wall_s": r["wall_s"],
                    "Acc": r["Acc"],
                    "fires": r["fires"],
                    "tgt_fwhm_ms": r["tgt_fwhm_ms"],
                    "sep_soma_trace": r["sep_soma_trace"],
                    "sep_ltz_csv": r["sep_ltz_csv"],
                    "n_trace_samples": r["n_trace_samples"],
                    "trace": r["trace"],
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    write_tsv(rows, a.tsv)
    a.json.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"TSV {a.tsv}", flush=True)
    print(f"JSON {a.json}", flush=True)


if __name__ == "__main__":
    main()
