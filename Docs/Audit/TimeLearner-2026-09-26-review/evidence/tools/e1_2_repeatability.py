#!/usr/bin/env python3
"""E1.2 Console repeatability: N packs with cold Reset vs N packs without Reset.

Probe-only (IsNeedToTrain=0). One fixed structure (default AsymRm L=10 @ TipR=8.6e7).
Uses tl_probe_kernels prepare patterns; measures soma peak / t_peak per pack window.

Subcommands
  prepare-reset   --template … --out … --lengths 10,10,10,10 [--tipr 8.6e7] [--isi 2.0]
  prepare-norese  --template … --out … --n-packs 20 --lengths … [--isi 2.0]
  run-reset       --probe … --n-packs 20 --console BIN --traces-dir …
  analyze         --reset-dir … --noreset-probe … --tsv OUT.tsv --json OUT.json
                  [--n-packs 20] [--isi 2.0] [--soma 0]

Reset arm: N independent Console cold starts on the same prepared single-pulse probe
(each process start ≡ Neuron Reset from rest). No-Reset arm: one Console run with
N pulses spaced by ISI; windows analyzed without inter-pack Reset.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / "plans" / "AGENT_PLAN_2026-10-20" / "tools"
sys.path.insert(0, str(TOOLS))
import tl_probe_kernels as tpk  # noqa: E402


def edit_n_pulses(path: Path, lengths, isi: float, tipr: float, n_packs: int, report: dict):
    """Like tpk.edit_file but with n_packs pulse onsets (first at 0.0005)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    onsets = [0.0005 + k * isi for k in range(n_packs)]
    # Classic InputPattern is a column of spike times (rows = pulses).
    pattern = "\n".join(repr(x) if isinstance(x, float) else str(x) for x in onsets)
    # Use high-precision repr for floats
    pattern = "\n".join(f"{x:.6f}" for x in onsets)
    lm = tpk.LEARNER_BLOCK.search(text)
    if not lm:
        raise SystemExit(f"{path}: no NNeuronTimeLearner block")
    body = lm.group(2)
    learner_props = [
        ("IsNeedToTrain", "0", "b", ""),
        ("StructureBuildMode", "1", "i", ""),
        ("NormalizationMode", "1", "i", ""),
        ("UseFixedLTZThreshold", "1", "b", ""),
        ("FixedLTZThreshold", "100", "d", ""),
        ("LTZThreshold", "100", "d", ""),
        ("AutoCalibrateFixedLTZThreshold", "0", "b", ""),
        ("EnablePostTrainTuning", "0", "b", ""),
        ("EnablePostTrainMidThreshold", "0", "b", ""),
        (
            "DendriteLength",
            " ".join(map(str, lengths)),
            None,
            ' Type="simplevector" Size="4" elemType="i" PType="257" IoType="33"',
        ),
        (
            "NumSynapse",
            "1 1 1 1",
            None,
            ' Type="simplevector" Size="4" elemType="i" PType="257" IoType="33"',
        ),
        (
            "TipSynapseResistance",
            " ".join([repr(tipr)] * 4),
            None,
            ' Type="simplevector" Size="4" elemType="d" PType="259" IoType="33"',
        ),
        ("InputPattern", pattern, None, tpk.matrix_attrs(n_packs, 1)),
    ]
    for name, val, typ, attrs in learner_props:
        body, existed = tpk.set_prop(body, name, val, typ, attrs)
        report.setdefault(path.name, []).append(f"{name}={'set' if existed else 'added'}")
    text = text[: lm.start(2)] + body + text[lm.end(2) :]
    dm = tpk.DATASET_BLOCK.search(text)
    if dm:
        db = dm.group(2)
        for name, val, attrs in [
            ("MatrixData", pattern, tpk.matrix_attrs(n_packs, 1)),
            ("MatrixClasses", "1", tpk.matrix_attrs(1, 1, "i")),
            ("NumSamples", "1", ""),
            ("LoopSamples", "0", ""),
            # W01 template defaults to 4; without this only the first 4 onsets fire.
            ("MaxSpikesPerFeature", str(max(4, n_packs)), ""),
        ]:
            typ = "i" if name in ("NumSamples", "MaxSpikesPerFeature") else "b"
            db, existed = tpk.set_prop(db, name, val, typ, attrs)
            report.setdefault(path.name, []).append(f"Dataset.{name}={'set' if existed else 'added'}")
        text = text[: dm.start(2)] + db + text[dm.end(2) :]
    for d, L in enumerate(lengths, start=1):
        pat = re.compile(
            rf'(<Dendrite{d}_{L} Class="[^"]+">.*?<ExcSynapse1 Class="[^"]+">.*?<Resistance Type="d"[^>]*>)[^<]*(</Resistance>)',
            re.S,
        )
        text, n = pat.subn(lambda m: m.group(1) + repr(tipr) + m.group(2), text, count=1)
        report.setdefault(path.name, []).append(f"tip{d}_{L}_resistance={'set' if n else 'MISSING_SEGMENT'}")
    path.write_text(text, encoding="utf-8")


def cmd_prepare(a, n_packs: int):
    tpl, out = Path(a.template), Path(a.out)
    lengths = [int(x) for x in a.lengths.split(",")]
    if len(lengths) != 4 or min(lengths) < 1:
        raise SystemExit("--lengths must be four positive integers")
    mt = (tpl / "Model_00.xml").read_text(encoding="utf-8", errors="replace")
    avail = [
        max([int(x) for x in re.findall(rf"<Dendrite{d}_(\d+) Class", mt)] or [0]) for d in range(1, 5)
    ]
    bad = [(d + 1, L, avail[d]) for d, L in enumerate(lengths) if L > avail[d]]
    if bad:
        raise SystemExit(f"LENGTH_TOO_LONG: available={avail} requested={lengths} bad={bad}")
    if out.exists():
        raise SystemExit(f"{out} exists")
    shutil.copytree(tpl, out)
    for junk in ("SelectivityLog", "StatisticLog", "EventsLog", "posttune_complete.flag", "test_trace.csv"):
        p = out / junk
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    report = {}
    for f in ("Parameters_00.xml", "Model_00.xml"):
        edit_n_pulses(out / f, lengths, a.isi, a.tipr, n_packs, report)
    tpk.enable_trace(out / "Model_00.xml")
    import check_model_wiring
    import repair_model_wiring

    rep_stats = []
    with (out / "Model_00.xml").open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    new, st = repair_model_wiring.repair(text, lengths)
    with (out / "Model_00.xml").open("w", encoding="utf-8", newline="") as fh:
        fh.write(new)
    rep_stats.append(st)
    chk = check_model_wiring.analyze(str(out / "Model_00.xml"), str(out / "Parameters_00.xml"))
    console_t = int(math.ceil(n_packs * a.isi + 2.0))
    man = {
        "tool": "e1_2_repeatability.py prepare",
        "arm": "reset" if n_packs == 1 else "noreset",
        "template": str(tpl),
        "lengths": lengths,
        "n_packs": n_packs,
        "isi_s": a.isi,
        "tipr_ohm": a.tipr,
        "first_pulse_s": 0.0005,
        "console_t_s": console_t,
        "wiring_ok": chk["ok"],
        "edits": report,
        "wiring_repair": rep_stats,
    }
    (out / "probe_manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(out),
                "arm": man["arm"],
                "n_packs": n_packs,
                "wiring_ok": chk["ok"],
                "console_cmd": (
                    f'"$NMSDK_CONSOLE" -c "{out}/Project.ini" -s -t {console_t} -x -S '
                    f'> "{out}/console.log" 2>&1'
                ),
            },
            ensure_ascii=False,
            indent=1,
        )
    )


def run_console(console: Path, probe: Path, t_s: int, log: Path) -> int:
    cmd = [str(console), "-c", str(probe / "Project.ini"), "-s", "-t", str(t_s), "-x", "-S"]
    with log.open("w", encoding="utf-8") as fh:
        p = subprocess.run(cmd, cwd=str(probe), stdout=fh, stderr=subprocess.STDOUT)
    return p.returncode


def find_trace(probe: Path) -> Path:
    traces = sorted(probe.rglob("test_trace.csv"))
    if not traces:
        raise SystemExit(f"NO_TRACE under {probe}")
    return traces[0]


def load_trace(path: Path):
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
    rows = [r for r in rows if r["trial"] == trial0]
    return rows


def peak_in_window(rows, soma: int, t0: float, t1: float, f_hz: int):
    """Peak above local baseline at window start; t_peak relative to pack onset t0."""
    col = f"soma_{soma}"
    times = [float(r["time_rel_s"]) for r in rows]
    vals = [float(r[col]) for r in rows]
    # samples in [t0, t1)
    idx = [i for i, t in enumerate(times) if t0 <= t < t1]
    if not idx:
        return None
    # baseline: mean of first few samples at/after t0 (or last sample before t0)
    pre = [i for i, t in enumerate(times) if t0 - 2.0 / f_hz <= t < t0 + 2.0 / f_hz]
    if not pre:
        pre = [idx[0]]
    base = sum(vals[i] for i in pre) / len(pre)
    best_i = max(idx, key=lambda i: vals[i] - base)
    peak = vals[best_i] - base
    t_peak = times[best_i] - t0
    return {"peak": peak, "t_peak_s": t_peak, "baseline": base, "abs_peak": vals[best_i]}


def analyze_multi(probe: Path, n_packs: int, isi: float, soma: int, arm: str, pack_offset: int = 0):
    """t_peak_s is latency from stimulus onset (first_pulse + k*ISI), not from EPSP rise detect."""
    man = json.loads((probe / "probe_manifest.json").read_text(encoding="utf-8"))
    ini = (probe / "Project.ini").read_text(encoding="utf-8", errors="replace")
    f_hz = int(re.search(r"<DefaultTimeStep>(\d+)<", ini).group(1))
    rows = load_trace(find_trace(probe))
    times = [float(r["time_rel_s"]) for r in rows]
    t0_nom = float(man.get("first_pulse_s", 0.0005))
    # Map stimulus times into trace time_rel: assume sample clock aligns so pulse 0 is at t0_nom.
    # If analyzer shifts the grid, detect offset so that peak of pack0 lands near E1.0 (~0.1 s for L=10).
    packs = []
    for k in range(n_packs):
        stim = t0_nom + k * isi
        pack_t0 = stim
        pack_t1 = stim + 0.95 * isi
        m = peak_in_window(rows, soma, pack_t0, pack_t1, f_hz)
        if m is None:
            packs.append(
                {
                    "arm": arm,
                    "pack": pack_offset + k,
                    "peak": None,
                    "t_peak_s": None,
                    "valid": 0,
                    "note": "empty_window",
                }
            )
        else:
            packs.append(
                {
                    "arm": arm,
                    "pack": pack_offset + k,
                    "peak": m["peak"],
                    "t_peak_s": m["t_peak_s"],
                    "baseline": m["baseline"],
                    "valid": 1 if m["peak"] > 0 else 0,
                    "note": "",
                    "L": man["lengths"][soma],
                    "tipr": man["tipr_ohm"],
                    "isi_s": isi,
                    "f_hz": f_hz,
                }
            )
    return packs, {"t_origin": t0_nom, "f_hz": f_hz, "manifest": man}


def cmd_run_reset(a):
    probe = Path(a.probe)
    man = json.loads((probe / "probe_manifest.json").read_text(encoding="utf-8"))
    t_s = int(man.get("console_t_s", math.ceil(a.isi + 2)))
    traces = Path(a.traces_dir)
    traces.mkdir(parents=True, exist_ok=True)
    console = Path(a.console)
    rcs = []
    for i in range(a.n_packs):
        # wipe previous trace
        for p in probe.rglob("test_trace.csv"):
            p.unlink()
        log = traces / f"reset_{i:02d}.console.log"
        rc = run_console(console, probe, t_s, log)
        rcs.append(rc)
        tr = find_trace(probe)
        dest = traces / f"reset_{i:02d}.csv"
        shutil.copy2(tr, dest)
        print(f"reset pack {i}: rc={rc} trace={dest}", flush=True)
    (traces / "reset_rcs.json").write_text(json.dumps({"rcs": rcs, "console": str(console)}, indent=1))
    print(json.dumps({"n": a.n_packs, "rcs": rcs, "ok": all(r == 0 for r in rcs)}))


def cmd_run_noreset(a):
    probe = Path(a.probe)
    man = json.loads((probe / "probe_manifest.json").read_text(encoding="utf-8"))
    t_s = int(man.get("console_t_s", math.ceil(a.n_packs * a.isi + 2)))
    console = Path(a.console)
    for p in probe.rglob("test_trace.csv"):
        p.unlink()
    log = probe / "console.log"
    rc = run_console(console, probe, t_s, log)
    print(json.dumps({"rc": rc, "trace": str(find_trace(probe) if rc == 0 else None), "t_s": t_s}))


def summarize(packs, arm: str):
    vals_p = [x["peak"] for x in packs if x.get("valid") and x["peak"] is not None]
    vals_t = [x["t_peak_s"] for x in packs if x.get("valid") and x["t_peak_s"] is not None]
    def stats(xs):
        if not xs:
            return {"n": 0, "mean": None, "stdev": None, "min": None, "max": None}
        if len(xs) == 1:
            return {"n": 1, "mean": xs[0], "stdev": 0.0, "min": xs[0], "max": xs[0]}
        return {
            "n": len(xs),
            "mean": statistics.mean(xs),
            "stdev": statistics.stdev(xs),  # sample σ
            "min": min(xs),
            "max": max(xs),
        }

    sp, st = stats(vals_p), stats(vals_t)
    return {
        "arm": arm,
        "peak": sp,
        "t_peak_s": st,
        "eps_amp_3sigma": (3.0 * sp["stdev"]) if sp["stdev"] is not None else None,
        "eps_amp_rel_3sigma": (
            (3.0 * sp["stdev"] / abs(sp["mean"])) if sp["stdev"] is not None and sp["mean"] else None
        ),
        "lat_tol_s_3sigma": (3.0 * st["stdev"]) if st["stdev"] is not None else None,
    }


def cmd_analyze(a):
    reset_dir = Path(a.reset_dir)
    noreset = Path(a.noreset_probe)
    soma = a.soma
    n = a.n_packs
    isi = a.isi
    all_rows = []
    # reset: each csv is a 1-pack probe copy
    for i in range(n):
        csv_path = reset_dir / f"reset_{i:02d}.csv"
        if not csv_path.exists():
            raise SystemExit(f"missing {csv_path}")
        # temporary probe dir pointing at this csv via symlink into a stub
        # Analyze by building a mini env: copy manifest from reset probe parent
        # The reset probe dir is a.parent of traces? We store probe path in --reset-probe
        pass

    reset_probe = Path(a.reset_probe)
    # For each reset csv, temporarily place as test_trace under reset_probe and analyze n_packs=1
    man = json.loads((reset_probe / "probe_manifest.json").read_text(encoding="utf-8"))
    saved = list(reset_probe.rglob("test_trace.csv"))
    for p in saved:
        p.unlink()
    reset_packs = []
    for i in range(n):
        csv_path = reset_dir / f"reset_{i:02d}.csv"
        dest = reset_probe / "test_trace.csv"
        shutil.copy2(csv_path, dest)
        packs, meta = analyze_multi(reset_probe, 1, isi, soma, "reset", pack_offset=i)
        # override pack index
        for p in packs:
            p["pack"] = i
            p["source_trace"] = str(csv_path)
        reset_packs.extend(packs)
        dest.unlink()
    noreset_packs, noreset_meta = analyze_multi(noreset, n, isi, soma, "noreset", pack_offset=0)
    for p in noreset_packs:
        p["source_trace"] = str(find_trace(noreset))

    all_rows = reset_packs + noreset_packs
    # write TSV
    fields = [
        "arm",
        "pack",
        "peak",
        "t_peak_s",
        "baseline",
        "valid",
        "L",
        "tipr",
        "isi_s",
        "f_hz",
        "note",
        "source_trace",
    ]
    tsv = Path(a.tsv)
    with tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in all_rows:
            w.writerow(r)

    s_reset = summarize(reset_packs, "reset")
    s_nore = summarize(noreset_packs, "noreset")
    # Proposed F4 tolerances: max over arms of 3σ, and floor 1% of mean target (reset mean)
    mean_amp = s_reset["peak"]["mean"] or s_nore["peak"]["mean"] or 0.0
    sig_amp = max(s_reset["peak"]["stdev"] or 0.0, s_nore["peak"]["stdev"] or 0.0)
    sig_lat = max(s_reset["t_peak_s"]["stdev"] or 0.0, s_nore["t_peak_s"]["stdev"] or 0.0)
    # also include mean shift between arms as systematic (not for σ tol, but report)
    mean_shift = None
    if s_reset["peak"]["mean"] and s_nore["peak"]["mean"]:
        mean_shift = s_nore["peak"]["mean"] - s_reset["peak"]["mean"]
    eps_amp_abs = max(3.0 * sig_amp, 0.01 * abs(mean_amp))
    eps_amp_rel = eps_amp_abs / abs(mean_amp) if mean_amp else None
    lat_tol = max(3.0 * sig_lat, 1.0 / (man.get("f_hz") or noreset_meta["f_hz"]))  # ≥1 sample

    out = {
        "model_L_tipr": {
            "NeuronModel": "from_template",
            "L": man["lengths"][soma],
            "TipR": man["tipr_ohm"],
            "soma_channel": soma,
            "isi_s": isi,
            "n_packs": n,
        },
        "reset": s_reset,
        "noreset": s_nore,
        "mean_shift_noreset_minus_reset": mean_shift,
        "proposed_F4": {
            "eps_amp_abs": eps_amp_abs,
            "eps_amp_rel": eps_amp_rel,
            "latency_tol_s": lat_tol,
            "rule": "max(3σ_across_arms, 1%·|mean_amp_reset|, 1/f_hz for latency)",
            "sigma_amp_used": sig_amp,
            "sigma_lat_used": sig_lat,
        },
        "tsv": str(tsv),
        "reset_meta_origin": None,
        "noreset_t_origin": noreset_meta["t_origin"],
    }
    Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_prep(p):
        p.add_argument("--template", required=True)
        p.add_argument("--out", required=True)
        p.add_argument("--lengths", default="10,10,10,10")
        p.add_argument("--isi", type=float, default=2.0)
        p.add_argument("--tipr", type=float, default=8.6e7)

    pr = sub.add_parser("prepare-reset")
    add_prep(pr)
    pn = sub.add_parser("prepare-noreset")
    add_prep(pn)
    pn.add_argument("--n-packs", type=int, default=20)

    rr = sub.add_parser("run-reset")
    rr.add_argument("--probe", required=True)
    rr.add_argument("--n-packs", type=int, default=20)
    rr.add_argument("--console", required=True)
    rr.add_argument("--traces-dir", required=True)
    rr.add_argument("--isi", type=float, default=2.0)

    rn = sub.add_parser("run-noreset")
    rn.add_argument("--probe", required=True)
    rn.add_argument("--console", required=True)
    rn.add_argument("--n-packs", type=int, default=20)
    rn.add_argument("--isi", type=float, default=2.0)

    an = sub.add_parser("analyze")
    an.add_argument("--reset-probe", required=True)
    an.add_argument("--reset-dir", required=True)
    an.add_argument("--noreset-probe", required=True)
    an.add_argument("--tsv", required=True)
    an.add_argument("--json", required=True)
    an.add_argument("--n-packs", type=int, default=20)
    an.add_argument("--isi", type=float, default=2.0)
    an.add_argument("--soma", type=int, default=0)

    a = ap.parse_args()
    if a.cmd == "prepare-reset":
        cmd_prepare(a, n_packs=1)
    elif a.cmd == "prepare-noreset":
        cmd_prepare(a, n_packs=a.n_packs)
    elif a.cmd == "run-reset":
        cmd_run_reset(a)
    elif a.cmd == "run-noreset":
        cmd_run_noreset(a)
    else:
        cmd_analyze(a)


if __name__ == "__main__":
    main()
