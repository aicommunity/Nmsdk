#!/usr/bin/env python3
"""E1.5 — historical PASS fragility: Test-only under L ±1 and TipR ×0.8/×1.25.

Freeze known PASS (L, TipR, FixedLTZ), IsNeedToTrain=0, no SoftCold train.
TipR scale is **global** (all four tips × factor). L ±1 is one input at a time
(clamp ≥1). StructureBuildMode=1 when lengths differ from the template morphology
so Branch rebuilds dendrites; TipR-only keeps SBM=0 and patches tip Resistance.

Attempt-local overlays only (does not touch shared Train/Test inputs).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
NMSDK = HERE.parents[4]
ST = NMSDK / "Bin" / "Configs" / "SpikeSamples" / "StructTrain"
SCRIPTS = ST / "scripts"
sys.path.insert(0, str(SCRIPTS))
from repro_cold_lib import get_tag, set_tag, set_tag_all  # noqa: E402
from selectivity_metrics import classify  # noqa: E402

DEFAULT_CONSOLE = NMSDK / "Bin" / "Platform" / "Linux" / "NeuroModelerConsole"
DEFAULT_WORK = Path(os.environ.get("DATA", "/home/user/TLAgent-20261020")) / "scratch" / "E1_5_FRAGILITY"


@dataclass
class CaseSpec:
    case_id: str
    alias: str
    trainer_mode: str
    span_ms: int
    neuron_model: str
    mod: str
    template_test: Path
    train_link: str
    test_link: str
    baseline_L: list[int]
    baseline_TipR: list[float]
    fixed_ltz: float
    sim_t: float
    template_L: list[int]  # morphology baked in template Model


CASES: list[CaseSpec] = [
    CaseSpec(
        case_id="br480_tiprmin",
        alias="EXP_br480_tiprmin",
        trainer_mode="Branch×N1",
        span_ms=480,
        neuron_model="baseline",
        mod="tiprmin/gen",
        template_test=ST / "SelectivityBranch/EXP_br480_tiprmin/Test",
        train_link="Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br480_tiprmin/Train",
        test_link="Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br480_tiprmin/Test",
        baseline_L=[85, 46, 25, 1],
        baseline_TipR=[2e7, 2e7, 2e7, 8.6e7],
        fixed_ltz=0.05149,
        sim_t=120.0,
        template_L=[85, 46, 25, 1],
    ),
    CaseSpec(
        case_id="br25_nextseg",
        alias="W10_HIST_br25_nextseg / E2 PASS state",
        trainer_mode="Branch×N1",
        span_ms=25,
        neuron_model="AsymRm",
        mod="nextseg",
        template_test=ST / "SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test",
        train_link="Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train",
        test_link="Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test",
        # E2 / POSTTUNE_FIX PASS×3 converged state (not XML initial 13 11 7 1)
        baseline_L=[7, 6, 4, 1],
        baseline_TipR=[2e7, 2e7, 2e7, 8.6e7],
        fixed_ltz=0.10023275299347018,
        sim_t=40.0,
        template_L=[13, 11, 7, 1],
    ),
]


def fmt_tipr(vals: list[float]) -> str:
    return " ".join(format(v, ".17g") for v in vals)


def fmt_L(vals: list[int]) -> str:
    return " ".join(str(v) for v in vals)


def patch_tip_resistances(text: str, lengths: list[int], tipr: list[float], report: list[str]) -> str:
    """Best-effort: set ExcSynapse1 Resistance on Dendrite{d}_{L} tips."""
    for d, (L, r) in enumerate(zip(lengths, tipr), start=1):
        pat = re.compile(
            rf'(<Dendrite{d}_{L}\b[^>]*>.*?<ExcSynapse1\b[^>]*>.*?<Resistance\b[^>]*>)[^<]*(</Resistance>)',
            re.S,
        )
        text2, n = pat.subn(lambda m, rr=r: m.group(1) + repr(rr) + m.group(2), text, count=1)
        report.append(f"tip{d}_{L}_R={'set' if n else 'MISSING'}")
        text = text2
    return text


def apply_freeze(
    test_dir: Path,
    *,
    lengths: list[int],
    tipr: list[float],
    fixed_ltz: float,
    structure_build_mode: int,
) -> list[str]:
    report: list[str] = []
    tipr_s = fmt_tipr(tipr)
    L_s = fmt_L(lengths)
    mid = format(fixed_ltz, ".17g")
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = test_dir / rel
        t = p.read_text(encoding="utf-8", errors="replace")
        for name, val in (
            ("IsNeedToTrain", "0"),
            ("StructureBuildMode", str(structure_build_mode)),
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
            t = set_tag_all(t, name, val) if name in (
                "DendriteLength", "TipSynapseResistance", "IsNeedToTrain",
                "StructureBuildMode", "FixedLTZThreshold", "LTZThreshold",
            ) else set_tag(t, name, val, 0)
        if structure_build_mode == 0:
            t = patch_tip_resistances(t, lengths, tipr, report)
        p.write_text(t, encoding="utf-8")
        report.append(f"{rel}: L={L_s} TipR={tipr_s} SBM={structure_build_mode} mid={mid}")
    # clear stale SelectivityLog so classify sees fresh CSV
    slog = test_dir / "SelectivityLog"
    if slog.exists():
        for f in slog.glob("results*.csv"):
            f.unlink(missing_ok=True)
    return report


def csv_nrows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open(encoding="utf-8") as f:
            return max(0, sum(1 for _ in f) - 1)
    except OSError:
        return 0


def sep_from_csv(csv_path: Path) -> float | None:
    """(tgt − max_foil) / tgt from ltz_potential_max if present."""
    if not csv_path.exists():
        return None
    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 2:
        return None
    peaks: list[float] = []
    for r in rows[:8]:
        try:
            peaks.append(float(r.get("ltz_potential_max") or "nan"))
        except ValueError:
            peaks.append(float("nan"))
    if len(peaks) < 2 or not (peaks[0] > 0):
        return None
    foils = [p for p in peaks[1:] if p == p]
    if not foils:
        return None
    return (peaks[0] - max(foils)) / peaks[0]


def run_console(console: Path, ini: Path, csv_path: Path, sim_t: float, timeout_sec: int) -> tuple[int, str]:
    cmd = [str(console), "-c", str(ini), "-s", "-t", str(sim_t), "-x"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        return -1, str(e)
    hard = time.time() + timeout_sec
    err = ""
    while proc.poll() is None:
        if time.time() > hard:
            err = "timeout"
            proc.terminate()
            break
        if csv_nrows(csv_path) >= 8:
            time.sleep(2.0)
            if proc.poll() is None:
                err = "sigterm_csv8"
                proc.terminate()
            break
        time.sleep(1.5)
    try:
        rc = proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            rc = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            rc = -9
        err = err or "kill_after_term"
    return rc, err


def variants_for(case: CaseSpec) -> list[dict]:
    out: list[dict] = []
    out.append({"kind": "baseline", "L": list(case.baseline_L), "TipR": list(case.baseline_TipR), "label": "baseline"})
    for i in range(4):
        for delta, tag in ((+1, "p1"), (-1, "m1")):
            L = list(case.baseline_L)
            L[i] = max(1, L[i] + delta)
            if L == case.baseline_L:
                continue  # e.g. L4=1 with −1 clamped
            out.append({
                "kind": "L",
                "L": L,
                "TipR": list(case.baseline_TipR),
                "label": f"L{i}:{tag}",
                "input_idx": i,
                "delta": delta,
            })
    for fac, tag in ((0.8, "x0.8"), (1.25, "x1.25")):
        tipr = [v * fac for v in case.baseline_TipR]
        out.append({
            "kind": "TipR_global",
            "L": list(case.baseline_L),
            "TipR": tipr,
            "label": f"TipR_{tag}",
            "tipr_scale": fac,
        })
    return out


def need_sbm1(case: CaseSpec, lengths: list[int]) -> int:
    if lengths != case.template_L:
        return 1
    return 0


def run_one(
    case: CaseSpec,
    var: dict,
    *,
    work_root: Path,
    console: Path,
    timeout_floor: int,
) -> dict:
    run_id = f"{case.case_id}__{var['label']}"
    out_dir = work_root / case.case_id / var["label"]
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(case.template_test, out_dir, symlinks=False)
    sbm = need_sbm1(case, var["L"])
    # Always rebuild when baseline L differs from template (br25_nextseg)
    if var["L"] != case.template_L:
        sbm = 1
    report = apply_freeze(
        out_dir,
        lengths=var["L"],
        tipr=var["TipR"],
        fixed_ltz=case.fixed_ltz,
        structure_build_mode=sbm,
    )
    csv_path = out_dir / "SelectivityLog" / "results.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    timeout = max(timeout_floor, int(case.sim_t * 25), 900)
    t0 = time.time()
    rc, err = run_console(console, out_dir / "Project.ini", csv_path, case.sim_t, timeout)
    wall = round(time.time() - t0, 1)
    metrics: dict = {}
    fires = ""
    acc = ""
    cel = "—"
    mode = ""
    sep = sep_from_csv(csv_path)
    if csv_path.exists() and csv_nrows(csv_path) >= 1:
        try:
            with csv_path.open(encoding="utf-8", newline="") as f:
                crow = list(csv.DictReader(f))
            metrics = classify(crow)
            fires = str(metrics.get("fires", "") or "")
            acc_n = int(metrics.get("acc", 0) or 0)
            n = int(metrics.get("n", 0) or 0)
            acc = f"{acc_n}/{n}" if n else str(acc_n)
            target = int(metrics.get("target_hit", 0) or 0)
            mode = str(metrics.get("mode", metrics.get("mode_legacy", "")) or "")
            cel = "да" if target == 1 else ("нет" if n else "—")
        except Exception as e:  # noqa: BLE001
            err = (err + f"; classify:{e}").strip("; ")
            n = 0
            acc_n = 0
            mode = ""
    else:
        n = 0
        acc_n = 0
    # GoldTest-style PASS: selective 8/8 fires=10000000 (or selective ≥7 startswith 1)
    gate_ok = n >= 8 and err in ("", "sigterm_csv8")
    if not gate_ok or n == 0 or err in ("timeout", "missing_ini", "kill_after_term"):
        pass_flag = False
    elif mode == "selective" and acc_n == 8 and fires == "10000000":
        pass_flag = True
    elif mode == "selective" and acc_n >= 7 and fires.startswith("1"):
        pass_flag = True
    else:
        pass_flag = False
    return {
        "case_id": case.case_id,
        "alias": case.alias,
        "trainer_mode": case.trainer_mode,
        "span_ms": case.span_ms,
        "neuron_model": case.neuron_model,
        "mod": case.mod,
        "variant": var["label"],
        "kind": var["kind"],
        "L": fmt_L(var["L"]),
        "TipR": fmt_tipr(var["TipR"]),
        "tipr_scale_mode": "global" if var["kind"] == "TipR_global" else "baseline",
        "FixedLTZ": case.fixed_ltz,
        "SBM": sbm,
        "Acc": acc or "—",
        "Цель": cel,
        "fires": fires or "—",
        "sep_ltz": None if sep is None else round(sep, 6),
        "pass": pass_flag,
        "rc": rc,
        "err": err,
        "wall_s": wall,
        "n_csv": csv_nrows(csv_path),
        "train_config": case.train_link,
        "test_config": case.test_link,
        "workdir": str(out_dir),
        "patch_report": report,
        "metrics": {k: metrics.get(k) for k in ("ok", "acc", "fa", "target_hit", "mode", "fires") if metrics},
    }


def write_tsv(rows: list[dict], path: Path) -> None:
    cols = [
        "case_id", "trainer_mode", "span_ms", "neuron_model", "mod", "variant", "kind",
        "L", "TipR", "tipr_scale_mode", "FixedLTZ", "SBM", "Acc", "Цель", "fires",
        "sep_ltz", "pass", "rc", "err", "wall_s", "train_config", "test_config",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, default=DEFAULT_WORK)
    ap.add_argument("--console", type=Path, default=Path(os.environ.get("NM", str(DEFAULT_CONSOLE))))
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--cases", nargs="*", default=[c.case_id for c in CASES])
    ap.add_argument("--timeout-floor", type=int, default=900)
    ap.add_argument("--tsv", type=Path, default=EVIDENCE / "E1_5_FRAGILITY_2026-10-22.tsv")
    ap.add_argument("--json", type=Path, default=EVIDENCE / "E1_5_FRAGILITY_2026-10-22.json")
    ap.add_argument("--dry-prepare", action="store_true", help="only list variants")
    args = ap.parse_args()

    selected = [c for c in CASES if c.case_id in set(args.cases)]
    if not selected:
        raise SystemExit(f"no cases matched {args.cases}")
    jobs: list[tuple[CaseSpec, dict]] = []
    for c in selected:
        for v in variants_for(c):
            jobs.append((c, v))
    print(f"E1.5 fragility: {len(jobs)} runs, jobs={args.jobs}, console={args.console}", flush=True)
    if args.dry_prepare:
        for c, v in jobs:
            print(f"  {c.case_id}\t{v['label']}\tL={fmt_L(v['L'])}\tTipR={fmt_tipr(v['TipR'])}")
        return 0

    args.work.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = {
            ex.submit(
                run_one, c, v, work_root=args.work, console=args.console, timeout_floor=args.timeout_floor
            ): (c.case_id, v["label"])
            for c, v in jobs
        }
        for fut in as_completed(futs):
            cid, lab = futs[fut]
            try:
                row = fut.result()
            except Exception as e:  # noqa: BLE001
                row = {"case_id": cid, "variant": lab, "err": str(e), "pass": False, "Acc": "—", "Цель": "—", "fires": "—"}
            rows.append(row)
            print(
                f"  [{row.get('case_id')}/{row.get('variant')}] Acc={row.get('Acc')} "
                f"Цель={row.get('Цель')} fires={row.get('fires')} sep={row.get('sep_ltz')} "
                f"rc={row.get('rc')} {row.get('err','')}",
                flush=True,
            )

    rows.sort(key=lambda r: (r.get("case_id", ""), 0 if r.get("variant") == "baseline" else 1, r.get("variant", "")))
    write_tsv(rows, args.tsv)
    payload = {
        "date": "2026-10-22",
        "task": "E1.5 fragility",
        "tipr_scale_mode": "global (all 4 tips × 0.8 / × 1.25)",
        "console": str(args.console),
        "console_sha256": subprocess.check_output(["sha256sum", str(args.console)], text=True).split()[0]
        if args.console.exists() else None,
        "nmsdk_sha": subprocess.check_output(["git", "-C", str(NMSDK), "rev-parse", "HEAD"], text=True).strip(),
        "work": str(args.work),
        "rows": rows,
    }
    args.json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.tsv} and {args.json}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
