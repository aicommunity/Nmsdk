#!/usr/bin/env python3
"""E1.3 soma relaxation after EPSP pack (Reset vs pause / no-Reset bias).

Probe-only (IsNeedToTrain=0). Primary: AsymRm L=10 @ TipR=8.6e7.
Measures τ_relax, t_to_1%, t_to_noise from single-pulse decay, and dual-pulse
amp ratio pack1/pack0 vs inter-pack pause (does membrane residual explain E1.2 −28%?).

Reuses e1_2 prepare (MaxSpikesPerFeature raised) via import.

Subcommands
  prepare-decay   --template … --out … [--lengths] [--tipr] [--post-s 5]
  prepare-dual    --template … --out … --pause P [--lengths] [--tipr]
  run             --probe … --console BIN [--t T]
  analyze-decay   --trace CSV|probe-dir --tsv … --json … [--stim 0.0005] [--soma 0]
  analyze-dual    --probe … --pause P --tsv-append … [--soma 0]
  sweep-dual      --template … --workdir … --console BIN --pauses 0.1,0.25,… \
                  [--lengths] [--tipr] [--tsv] [--json]
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_e12():
    path = HERE / "e1_2_repeatability.py"
    spec = importlib.util.spec_from_file_location("e1_2_repeatability", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


e12 = _load_e12()


def load_trace_rows(path: Path):
    rows = []
    with path.open(encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        for line in f:
            p = line.strip().split(",")
            if len(p) == len(header):
                rows.append(dict(zip(header, p)))
    if not rows:
        raise SystemExit(f"empty trace {path}")
    trial0 = rows[0]["trial"]
    return [r for r in rows if r["trial"] == trial0]


def find_trace(probe: Path) -> Path:
    traces = sorted(probe.rglob("test_trace.csv"))
    if not traces:
        raise SystemExit(f"NO_TRACE under {probe}")
    return traces[0]


def run_console(console: Path, probe: Path, t_s: int, log: Path, wall_timeout_s: int | None = None) -> int:
    """Run Console; wall_timeout defaults to max(120, 30+4*t_s).

    Some probe configs finish the analyzer trace then spin on posttune_mid_dbg;
    timeout keeps the sweep moving — trace is usually already on disk.
    """
    cmd = [str(console), "-c", str(probe / "Project.ini"), "-s", "-t", str(t_s), "-x", "-S"]
    env = os.environ.copy()
    # Elder-matched glog 0.4 pin (see tl-agent/lib)
    pin = Path.home() / "tl-agent" / "lib"
    if pin.is_dir():
        env["LD_LIBRARY_PATH"] = f"{pin}:{env.get('LD_LIBRARY_PATH', '')}"
    if wall_timeout_s is None:
        # Console may linger after the analyzer trace; keep generous headroom.
        wall_timeout_s = max(300, 60 + 20 * int(t_s))
    # Prefer GNU timeout so hung post-sim loops cannot block the sweep.
    full = ["timeout", "--signal=TERM", "--kill-after=15", str(wall_timeout_s), *cmd]
    with log.open("w", encoding="utf-8") as fh:
        p = subprocess.run(full, cwd=str(probe), stdout=fh, stderr=subprocess.STDOUT, env=env)
    # 124 = timeout; accept if trace exists
    if p.returncode in (0, 124) and list(probe.rglob("test_trace.csv")):
        return 0
    return p.returncode


def linreg_tau(xs, ys):
    """Fit log|dv| = a + b*t → τ = -1/b. Returns (tau, n, r2) or (None,…)."""
    if len(xs) < 8:
        return None, len(xs), None
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None, n, None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    if b >= 0:
        return None, n, None
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys) or 1.0
    return -1.0 / b, n, 1.0 - ss_res / ss_tot


def analyze_decay(times, vals, stim: float, f_hz: int, noise_floor: float = 1e-6):
    """Return peak / τ / t_to_* from absolute soma voltage after stim onset."""
    idx = [i for i, t in enumerate(times) if t >= stim]
    if not idx:
        raise SystemExit("no samples after stim")
    # baseline: mean near stim
    pre = [i for i, t in enumerate(times) if stim - 2.0 / f_hz <= t < stim + 2.0 / f_hz]
    if not pre:
        pre = [idx[0]]
    base = sum(vals[i] for i in pre) / len(pre)
    # peak in first 0.8 s after stim (EPSP window)
    win = [i for i in idx if times[i] < stim + 0.8]
    if not win:
        win = idx[: max(1, f_hz // 2)]
    peak_i = max(win, key=lambda i: vals[i] - base)
    peak_abs = vals[peak_i]
    amp = peak_abs - base
    t_peak = times[peak_i] - stim
    if amp <= 0:
        return {
            "ok": False,
            "note": "non_positive_amp",
            "baseline": base,
            "amp": amp,
            "t_peak_s": t_peak,
        }

    thr_1 = 0.01 * abs(amp)
    thr_noise = max(noise_floor, 0.001 * abs(amp))
    t_to_1 = None
    t_to_noise = None
    xs, ys = [], []
    for i in range(peak_i, len(times)):
        dv = vals[i] - base
        dt = times[i] - times[peak_i]
        if t_to_1 is None and abs(dv) <= thr_1:
            t_to_1 = dt
        if t_to_noise is None and abs(dv) <= thr_noise:
            t_to_noise = dt
        # mid-decay fit window (exclude near-peak and near-floor)
        if 0.05 * abs(amp) < abs(dv) < 0.7 * abs(amp) and dt > 0:
            xs.append(dt)
            ys.append(math.log(abs(dv)))

    tau, n_fit, r2 = linreg_tau(xs, ys)

    # residual amp fraction at fixed delays after stim
    residuals = {}
    for dt in (0.1, 0.25, 0.5, 1.0, 1.55, 2.0, 3.0, 5.0):
        tt = stim + dt
        if tt > times[-1] + 1.0 / f_hz:
            residuals[f"res_frac_at_{dt}"] = None
            residuals[f"res_abs_at_{dt}"] = None
            continue
        i = min(range(len(times)), key=lambda j: abs(times[j] - tt))
        dv = vals[i] - base
        residuals[f"res_abs_at_{dt}"] = dv
        residuals[f"res_frac_at_{dt}"] = dv / amp

    return {
        "ok": True,
        "baseline": base,
        "amp": amp,
        "abs_peak": peak_abs,
        "t_peak_s": t_peak,
        "tau_relax_s": tau,
        "tau_fit_n": n_fit,
        "tau_fit_r2": r2,
        "t_to_1pct_s": t_to_1,
        "t_to_noise_s": t_to_noise,
        "noise_floor": thr_noise,
        "t_end_s": times[-1],
        "t_after_peak_s": times[-1] - times[peak_i],
        **residuals,
    }


def peak_in_window(times, vals, t0, t1, f_hz):
    idx = [i for i, t in enumerate(times) if t0 <= t < t1]
    if not idx:
        return None
    pre = [i for i, t in enumerate(times) if t0 - 2.0 / f_hz <= t < t0 + 2.0 / f_hz]
    if not pre:
        pre = [idx[0]]
    base = sum(vals[i] for i in pre) / len(pre)
    best_i = max(idx, key=lambda i: vals[i] - base)
    return {
        "peak": vals[best_i] - base,
        "t_peak_s": times[best_i] - t0,
        "baseline": base,
        "abs_peak": vals[best_i],
    }


def analyze_dual_probe(probe: Path, pause: float, soma: int = 0):
    man = json.loads((probe / "probe_manifest.json").read_text(encoding="utf-8"))
    ini = (probe / "Project.ini").read_text(encoding="utf-8", errors="replace")
    import re

    f_hz = int(re.search(r"<DefaultTimeStep>(\d+)<", ini).group(1))
    rows = load_trace_rows(find_trace(probe))
    col = f"soma_{soma}"
    times = [float(r["time_rel_s"]) for r in rows]
    vals = [float(r[col]) for r in rows]
    t0 = float(man.get("first_pulse_s", 0.0005))
    packs = []
    for k in range(2):
        stim = t0 + k * pause
        m = peak_in_window(times, vals, stim, stim + min(0.95 * pause, 0.8), f_hz)
        if m is None:
            packs.append({"pack": k, "valid": 0, "peak": None, "t_peak_s": None})
        else:
            packs.append(
                {
                    "pack": k,
                    "valid": 1 if m["peak"] > 1e-6 else 0,
                    "peak": m["peak"],
                    "t_peak_s": m["t_peak_s"],
                    "baseline": m["baseline"],
                }
            )
    p0, p1 = packs[0], packs[1]
    ratio = None
    bias_pct = None
    if p0.get("valid") and p1.get("valid") and p0["peak"]:
        ratio = p1["peak"] / p0["peak"]
        bias_pct = 100.0 * (p1["peak"] - p0["peak"]) / p0["peak"]
    return {
        "pause_s": pause,
        "f_hz": f_hz,
        "lengths": man.get("lengths"),
        "tipr": man.get("tipr_ohm"),
        "pack0": p0,
        "pack1": p1,
        "amp_ratio_1_over_0": ratio,
        "amp_bias_pct": bias_pct,
        "t_end_s": times[-1],
        "trace": str(find_trace(probe)),
    }


def cmd_prepare_decay(a):
    # single pack; post-window encoded as isi so console_t covers decay
    class NS:
        pass

    ns = NS()
    ns.template = a.template
    ns.out = a.out
    ns.lengths = a.lengths
    ns.tipr = a.tipr
    ns.isi = max(a.post_s, 2.0)  # unused for 1 pack pattern, but console_t uses it
    e12.cmd_prepare(ns, n_packs=1)
    # bump console_t for long decay observation
    out = Path(a.out)
    man = json.loads((out / "probe_manifest.json").read_text(encoding="utf-8"))
    man["console_t_s"] = int(math.ceil(a.post_s + 2.0))
    man["post_s"] = a.post_s
    man["tool"] = "e1_3_relaxation.py prepare-decay"
    (out / "probe_manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(out), "console_t_s": man["console_t_s"]}, indent=1))


def cmd_prepare_dual(a):
    class NS:
        pass

    ns = NS()
    ns.template = a.template
    ns.out = a.out
    ns.lengths = a.lengths
    ns.tipr = a.tipr
    ns.isi = a.pause
    e12.cmd_prepare(ns, n_packs=2)
    out = Path(a.out)
    man = json.loads((out / "probe_manifest.json").read_text(encoding="utf-8"))
    man["console_t_s"] = int(math.ceil(2 * a.pause + 3.0))
    man["pause_s"] = a.pause
    man["tool"] = "e1_3_relaxation.py prepare-dual"
    (out / "probe_manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(out), "pause_s": a.pause, "console_t_s": man["console_t_s"]}, indent=1))


def cmd_run(a):
    probe = Path(a.probe)
    man = json.loads((probe / "probe_manifest.json").read_text(encoding="utf-8"))
    t_s = a.t if a.t else int(man.get("console_t_s", 8))
    for p in probe.rglob("test_trace.csv"):
        p.unlink()
    log = probe / "console.log"
    rc = run_console(Path(a.console), probe, t_s, log)
    tr = str(find_trace(probe)) if rc == 0 else None
    print(json.dumps({"rc": rc, "t_s": t_s, "trace": tr}))


def cmd_analyze_decay(a):
    path = Path(a.trace)
    if path.is_dir():
        path = find_trace(path)
    rows = load_trace_rows(path)
    col = f"soma_{a.soma}"
    times = [float(r["time_rel_s"]) for r in rows]
    vals = [float(r[col]) for r in rows]
    # infer f from median dt
    dts = [times[i + 1] - times[i] for i in range(min(1000, len(times) - 1))]
    dt = statistics.median(dts) if dts else 5e-5
    f_hz = int(round(1.0 / dt))
    m = analyze_decay(times, vals, a.stim, f_hz)
    m["trace"] = str(path)
    m["soma"] = a.soma
    m["stim_s"] = a.stim
    m["f_hz"] = f_hz
    m["NeuronModel"] = a.model
    m["L"] = a.L
    m["TipR"] = a.tipr
    tsv = Path(a.tsv)
    fields = [
        "NeuronModel",
        "L",
        "TipR",
        "soma",
        "amp",
        "t_peak_s",
        "tau_relax_s",
        "tau_fit_r2",
        "t_to_1pct_s",
        "t_to_noise_s",
        "res_frac_at_0.5",
        "res_frac_at_1.0",
        "res_frac_at_1.55",
        "res_frac_at_2.0",
        "res_frac_at_5.0",
        "t_end_s",
        "trace",
    ]
    write_header = not tsv.exists()
    with tsv.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        if write_header:
            w.writeheader()
        w.writerow(m)
    Path(a.json).write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(m, indent=1, ensure_ascii=False))


def cmd_analyze_dual(a):
    row = analyze_dual_probe(Path(a.probe), a.pause, a.soma)
    row["NeuronModel"] = a.model
    tsv = Path(a.tsv_append)
    fields = [
        "NeuronModel",
        "pause_s",
        "amp_ratio_1_over_0",
        "amp_bias_pct",
        "pack0_peak",
        "pack1_peak",
        "pack0_t_peak_s",
        "pack1_t_peak_s",
        "pack0_valid",
        "pack1_valid",
        "t_end_s",
        "trace",
    ]
    flat = {
        "NeuronModel": row["NeuronModel"],
        "pause_s": row["pause_s"],
        "amp_ratio_1_over_0": row["amp_ratio_1_over_0"],
        "amp_bias_pct": row["amp_bias_pct"],
        "pack0_peak": row["pack0"].get("peak"),
        "pack1_peak": row["pack1"].get("peak"),
        "pack0_t_peak_s": row["pack0"].get("t_peak_s"),
        "pack1_t_peak_s": row["pack1"].get("t_peak_s"),
        "pack0_valid": row["pack0"].get("valid"),
        "pack1_valid": row["pack1"].get("valid"),
        "t_end_s": row["t_end_s"],
        "trace": row["trace"],
    }
    write_header = not tsv.exists()
    with tsv.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        if write_header:
            w.writeheader()
        w.writerow(flat)
    print(json.dumps(row, indent=1, ensure_ascii=False))


def cmd_sweep_dual(a):
    pauses = [float(x) for x in a.pauses.split(",")]
    work = Path(a.workdir)
    work.mkdir(parents=True, exist_ok=True)
    tsv = Path(a.tsv)
    if tsv.exists():
        tsv.unlink()
    results = []
    for p in pauses:
        tag = f"dual_p{p:g}".replace(".", "p")
        out = work / tag
        if out.exists():
            shutil.rmtree(out)
        class NS:
            pass

        ns = NS()
        ns.template = a.template
        ns.out = str(out)
        ns.lengths = a.lengths
        ns.tipr = a.tipr
        ns.pause = p
        # prepare
        sys.argv  # silence
        ns_prep = argparse.Namespace(
            template=a.template, out=str(out), lengths=a.lengths, tipr=a.tipr, pause=p
        )
        cmd_prepare_dual(ns_prep)
        man = json.loads((out / "probe_manifest.json").read_text(encoding="utf-8"))
        t_s = int(man["console_t_s"])
        log = out / "console.log"
        for tr in out.rglob("test_trace.csv"):
            tr.unlink()
        rc = run_console(Path(a.console), out, t_s, log)
        if rc != 0:
            results.append({"pause_s": p, "rc": rc, "ok": False})
            print(f"FAIL pause={p} rc={rc}", flush=True)
            continue
        row = analyze_dual_probe(out, p, a.soma)
        row["NeuronModel"] = a.model
        row["rc"] = rc
        row["ok"] = True
        results.append(row)
        # append tsv
        ns_an = argparse.Namespace(
            probe=str(out), pause=p, tsv_append=str(tsv), soma=a.soma, model=a.model
        )
        cmd_analyze_dual(ns_an)
        print(
            f"pause={p}: ratio={row.get('amp_ratio_1_over_0')} bias%={row.get('amp_bias_pct')}",
            flush=True,
        )

    # verdict helpers
    ratios = [r["amp_ratio_1_over_0"] for r in results if r.get("ok") and r.get("amp_ratio_1_over_0") is not None]
    summary = {
        "NeuronModel": a.model,
        "L": a.lengths,
        "TipR": a.tipr,
        "pauses_s": pauses,
        "results": results,
        "at_pause_2s_bias_pct": next(
            (r.get("amp_bias_pct") for r in results if r.get("pause_s") == 2.0 and r.get("ok")), None
        ),
        "membrane_explains_E1_2": None,
    }
    # If at pause≥1.55s |bias| still ≫ few % while decay τ≪1s → membrane does NOT explain
    Path(a.json).write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"n_ok": sum(1 for r in results if r.get("ok")), "tsv": str(tsv), "json": a.json}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_struct(p):
        p.add_argument("--lengths", default="10,10,10,10")
        p.add_argument("--tipr", type=float, default=8.6e7)

    pd = sub.add_parser("prepare-decay")
    pd.add_argument("--template", required=True)
    pd.add_argument("--out", required=True)
    pd.add_argument("--post-s", type=float, default=5.0)
    add_struct(pd)

    pu = sub.add_parser("prepare-dual")
    pu.add_argument("--template", required=True)
    pu.add_argument("--out", required=True)
    pu.add_argument("--pause", type=float, required=True)
    add_struct(pu)

    rr = sub.add_parser("run")
    rr.add_argument("--probe", required=True)
    rr.add_argument("--console", required=True)
    rr.add_argument("--t", type=int, default=0)

    ad = sub.add_parser("analyze-decay")
    ad.add_argument("--trace", required=True)
    ad.add_argument("--tsv", required=True)
    ad.add_argument("--json", required=True)
    ad.add_argument("--stim", type=float, default=0.0005)
    ad.add_argument("--soma", type=int, default=0)
    ad.add_argument("--model", default="NSPNeuronGenAsymRmD001C1e9")
    ad.add_argument("--L", type=int, default=10)
    ad.add_argument("--tipr", type=float, default=8.6e7)

    an = sub.add_parser("analyze-dual")
    an.add_argument("--probe", required=True)
    an.add_argument("--pause", type=float, required=True)
    an.add_argument("--tsv-append", required=True)
    an.add_argument("--soma", type=int, default=0)
    an.add_argument("--model", default="NSPNeuronGenAsymRmD001C1e9")

    sw = sub.add_parser("sweep-dual")
    sw.add_argument("--template", required=True)
    sw.add_argument("--workdir", required=True)
    sw.add_argument("--console", required=True)
    sw.add_argument("--pauses", default="0.1,0.25,0.5,1.0,1.55,2.0,5.0")
    sw.add_argument("--tsv", required=True)
    sw.add_argument("--json", required=True)
    sw.add_argument("--soma", type=int, default=0)
    sw.add_argument("--model", default="NSPNeuronGenAsymRmD001C1e9")
    add_struct(sw)

    a = ap.parse_args()
    if a.cmd == "prepare-decay":
        cmd_prepare_decay(a)
    elif a.cmd == "prepare-dual":
        cmd_prepare_dual(a)
    elif a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "analyze-decay":
        cmd_analyze_decay(a)
    elif a.cmd == "analyze-dual":
        cmd_analyze_dual(a)
    else:
        cmd_sweep_dual(a)


if __name__ == "__main__":
    main()
