#!/usr/bin/env python3
"""C1 dose-response Console diagnostics (PLAN 2026-10-25 §2).

IsNeedToTrain=0, L=13 11 7 1, TipR br25 canon, AsymRm C1e9 base.
Attempt-local overlays only. Raw logs under --out-root; interpret after W0 ctrl PASS.

Series:
  psi     — NeuronClassName Preinh k∈{0,2.5,3.0,4.0} (k=0 → AsymRm)
  nextseg — EnableNextSegmentInhibition=1; Inh tip Resistance = TipR/w
  segei   — EnableSegExcInh + Delta/Alpha grid; optional inh_input_off
  combo   — PSI k=2.5 + nextseg w=1 (placeholder best until C1 scored)

Usage:
  python3 c1_dose_response_console.py --host-tag M40 --limit 8 \\
    --out-root $DATA/runs/C1_dose_20261024 --series all
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
from pathlib import Path

HERE = Path(__file__).resolve().parent
NMSDK = HERE.parents[4]
ST = NMSDK / "Bin" / "Configs" / "SpikeSamples" / "StructTrain"
SCRIPTS = ST / "scripts"
sys.path.insert(0, str(SCRIPTS))
from repro_cold_lib import get_tag, set_tag  # noqa: E402

CONSOLE = NMSDK / "Bin" / "Platform" / "Linux" / "NeuroModelerConsole"
BASE_NEXTSEG = ST / "SelectivityBranch" / "EXP_br_span25_packA_nextseginh_C1e9"
BASE_GEN = ST / "SelectivityBranch" / "EXP_br_span25_packA_gen_C1e9"
L_CANON = "13 11 7 1"
TIPR_CANON = "20000000 20000000 20000000 86000000"
TIPR_LAST = 8.6e7

# k=0 / 2.5 stay on AsymRm membrane family; 3.0/4.0 use library Preinh* classes
# (no Preinh3_0AsymRm / Preinh4_0AsymRm upload in PulseLib yet).
PSI_CLASSES = {
    0.0: "NSPNeuronGenAsymRmD001C1e9",
    2.5: "NSPNeuronGenPreinh2_5AsymRmD001C1e9",
    3.0: "NSPNeuronGenPreinh3_0",
    4.0: "NSPNeuronGenPreinh4_0",
}


def patch_xml(path: Path, **tags: str) -> None:
    t = path.read_text(encoding="utf-8", errors="replace")
    for k, v in tags.items():
        t = set_tag(t, k, v, 1)
    path.write_text(t, encoding="utf-8")


def scale_inh_resistances(model: Path, scale: float) -> None:
    """Set InhSynapse Resistance ≈ TipR_last/scale (w=TipR/R_inh → R_inh=TipR/w)."""
    if scale <= 0:
        # w=0 → disconnect Inh by huge R (near-open)
        r_inh = 1e15
    else:
        r_inh = TIPR_LAST / scale
    t = model.read_text(encoding="utf-8", errors="replace")

    def repl(m: re.Match[str]) -> str:
        block = m.group(0)
        return re.sub(
            r"(<Resistance\s+Type=\"d\"[^>]*>)([^<]*)(</Resistance>)",
            rf"\g<1>{r_inh:.17g}\g<3>",
            block,
            count=1,
        )

    t2, n = re.subn(
        r"<InhSynapse1\b[\s\S]*?</InhSynapse1>",
        repl,
        t,
        flags=re.I,
    )
    if n == 0:
        # Branch may name Inh differently
        t2, n = re.subn(
            r"<[^>]*InhSynapse[^>]*>[\s\S]*?</[^>]*InhSynapse[^>]*>",
            repl,
            t,
            flags=re.I,
        )
    model.write_text(t2, encoding="utf-8")


def unlink_inh_inputs(model: Path) -> None:
    """Drop Generator→Inh links for cable-load-only control."""
    t = model.read_text(encoding="utf-8", errors="replace")
    # remove Link elems whose Connector/Item mentions Inh
    def drop_inh_link(m: re.Match[str]) -> str:
        block = m.group(0)
        if re.search(r"Inh", block, re.I):
            return ""
        return block

    t2 = re.sub(r"<elem\s+Type=\"ULink\">[\s\S]*?</elem>", drop_inh_link, t)
    model.write_text(t2, encoding="utf-8")


def prepare_case(out: Path, *, template: Path, meta: dict) -> Path:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(
        template,
        out,
        ignore=shutil.ignore_patterns(
            "StatisticLog", "EventsLog", "SelectivityLog", "*.log", "posttune_mid_dbg.txt"
        ),
    )
    # Prefer Test side for inference-only; also patch Train for consistency
    for side in ("Test", "Train"):
        root = out / side
        if not root.is_dir():
            continue
        params = root / "Parameters_00.xml"
        model = root / "Model_00.xml"
        if params.is_file():
            patch_xml(
                params,
                IsNeedToTrain="0",
                DendriteLength=L_CANON,
                TipSynapseResistance=TIPR_CANON,
                EnablePostTrainTuning="0",
                NeuronClassName=meta.get("neuron", PSI_CLASSES[0.0]),
                EnableNextSegmentInhibition=meta.get("nextseg", "0"),
                EnableSegExcInh=meta.get("segei", "0"),
                SegExcInhDelta=meta.get("delta", "8"),
                SegExcInhAlpha=meta.get("alpha", "1.0"),
                FixedLTZThreshold=meta.get("ltz", "100"),
                UseFixedLTZThreshold="1",
                AutoCalibrateFixedLTZThreshold="0",
            )
        if model.is_file():
            patch_xml(
                model,
                NeuronClassName=meta.get("neuron", PSI_CLASSES[0.0]),
                EnableNextSegmentInhibition=meta.get("nextseg", "0"),
                EnableSegExcInh=meta.get("segei", "0"),
                SegExcInhDelta=meta.get("delta", "8"),
                SegExcInhAlpha=meta.get("alpha", "1.0"),
                IsNeedToTrain="0",
            )
            if "w" in meta:
                scale_inh_resistances(model, float(meta["w"]))
            if meta.get("inh_input_off") == "1":
                unlink_inh_inputs(model)
    (out / "c1_meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return out / "Test"


def run_console(test_dir: Path, *, tsec: float, log: Path, timeout_s: int) -> int:
    ini = test_dir / "Project.ini"
    if not ini.is_file():
        # synthesize minimal if missing
        raise SystemExit(f"no Project.ini in {test_dir}")
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(CONSOLE), "-c", str(ini), "-s", "-t", str(tsec), "-x"]
    with log.open("w") as f:
        f.write("CMD " + " ".join(cmd) + "\n")
        f.flush()
        try:
            p = subprocess.run(
                cmd, stdout=f, stderr=subprocess.STDOUT, timeout=timeout_s
            )
            return int(p.returncode)
        except subprocess.TimeoutExpired:
            f.write(f"\nTIMEOUT {timeout_s}s\n")
            return 124


def build_jobs(series: str) -> list[dict]:
    jobs: list[dict] = []
    if series in ("all", "psi"):
        for k, cls in PSI_CLASSES.items():
            jobs.append(
                {
                    "id": f"psi_k{k}",
                    "template": BASE_GEN,
                    "neuron": cls,
                    "nextseg": "0",
                    "segei": "0",
                    "psi_k": k,
                }
            )
    if series in ("all", "nextseg"):
        for w in (0.0, 0.25, 0.5, 1.0, 2.0, 4.0):
            jobs.append(
                {
                    "id": f"nextseg_w{w}",
                    "template": BASE_NEXTSEG,
                    "neuron": PSI_CLASSES[0.0],
                    "nextseg": "1",
                    "segei": "0",
                    "w": w,
                }
            )
    if series in ("all", "segei"):
        for d in (1, 2, 4, 8):
            for a in (0.5, 1.0, 2.0):
                jobs.append(
                    {
                        "id": f"segei_d{d}_a{a}",
                        "template": BASE_GEN,
                        "neuron": PSI_CLASSES[0.0],
                        "nextseg": "0",
                        "segei": "1",
                        "delta": str(d),
                        "alpha": str(a),
                    }
                )
            jobs.append(
                {
                    "id": f"segei_d{d}_a1_inhoff",
                    "template": BASE_GEN,
                    "neuron": PSI_CLASSES[0.0],
                    "nextseg": "0",
                    "segei": "1",
                    "delta": str(d),
                    "alpha": "1.0",
                    "inh_input_off": "1",
                }
            )
    if series in ("all", "combo"):
        jobs.append(
            {
                "id": "combo_psi2.5_nextseg_w1",
                "template": BASE_NEXTSEG,
                "neuron": PSI_CLASSES[2.5],
                "nextseg": "1",
                "segei": "0",
                "w": 1.0,
                "psi_k": 2.5,
            }
        )
        jobs.append(
            {
                "id": "combo_psi2.5_gen",
                "template": BASE_GEN,
                "neuron": PSI_CLASSES[2.5],
                "nextseg": "0",
                "segei": "0",
                "psi_k": 2.5,
            }
        )
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-root", type=Path, required=True)
    ap.add_argument("--series", default="all", choices=("all", "psi", "nextseg", "segei", "combo"))
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--tsec", type=float, default=40.0)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--host-tag", default="local")
    args = ap.parse_args()
    if not CONSOLE.is_file():
        raise SystemExit(f"missing Console {CONSOLE}")

    jobs = build_jobs(args.series)
    args.out_root.mkdir(parents=True, exist_ok=True)
    manifest = args.out_root / "C1_MANIFEST.tsv"
    rows: list[dict] = []

    def one(job: dict) -> dict:
        wid = f"C1_{job['id']}_{args.host_tag}"
        wd = args.out_root / wid
        test = prepare_case(wd, template=job["template"], meta=job)
        log = args.out_root / "logs" / f"{wid}.log"
        t0 = time.time()
        rc = run_console(test, tsec=args.tsec, log=log, timeout_s=args.timeout)
        return {
            "id": job["id"],
            "workdir": str(wd),
            "log": str(log),
            "rc": rc,
            "elapsed_s": round(time.time() - t0, 1),
            "meta": json.dumps(job, sort_keys=True),
        }

    print(f"C1 jobs={len(jobs)} limit={args.limit} out={args.out_root}")
    with ThreadPoolExecutor(max_workers=max(1, args.limit)) as ex:
        futs = [ex.submit(one, j) for j in jobs]
        for fut in as_completed(futs):
            row = fut.result()
            rows.append(row)
            print(f"DONE {row['id']} rc={row['rc']} et={row['elapsed_s']}s")

    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["id", "workdir", "log", "rc", "elapsed_s", "meta"]
        )
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["id"]):
            w.writerow(r)
    print(f"WROTE {manifest} n={len(rows)} — interpret after W0 ctrl PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
