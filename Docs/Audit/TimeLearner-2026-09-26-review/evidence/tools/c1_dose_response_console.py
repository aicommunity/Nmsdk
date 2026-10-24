#!/usr/bin/env python3
"""C1 dose-response Console diagnostics (PLAN 2026-10-25 §2).

IsNeedToTrain=0, L=13 11 7 1, TipR br25 canon, AsymRm C1e9 base.
Attempt-local overlays only. Raw logs under --out-root.

IMPORTANT (2026-10-24): do NOT interpret dose curves until mechanism probe PASSes
(--series mech or auto before nextseg/segei dose). SegEI tags must be inserted
(ensure_tag_after) — set_tag alone is a no-op when tags are absent from gen XML.

Usage:
  python3 c1_dose_response_console.py --host-tag M40 --limit 8 \\
    --out-root $DATA/runs/C1_dose --series mech
  python3 c1_dose_response_console.py ... --series nextseg  # only after mech OK
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
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
from repro_cold_lib import ensure_tag_after, get_tag, set_tag  # noqa: E402

CONSOLE = NMSDK / "Bin" / "Platform" / "Linux" / "NeuroModelerConsole"
BASE_NEXTSEG = ST / "SelectivityBranch" / "EXP_br_span25_packA_nextseginh_C1e9"
BASE_GEN = ST / "SelectivityBranch" / "EXP_br_span25_packA_gen_C1e9"
L_CANON = "13 11 7 1"
TIPR_CANON = "20000000 20000000 20000000 86000000"
TIPR_LAST = 8.6e7
# Gold nextseg Test FixedLTZ (do NOT use 100 — that was a bogus C1 default)
LTZ_GOLD_TEST = "0.0475917"

PSI_CLASSES = {
    0.0: "NSPNeuronGenAsymRmD001C1e9",
    2.5: "NSPNeuronGenPreinh2_5AsymRmD001C1e9",
    3.0: "NSPNeuronGenPreinh3_0",
    4.0: "NSPNeuronGenPreinh4_0",
}


def jsonable(obj: object) -> object:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    return obj


def patch_or_insert(text: str, tag: str, value: str, *, after: str, attrs: str) -> str:
    if get_tag(text, tag) is not None:
        return set_tag(text, tag, value, 0)
    return ensure_tag_after(text, after, tag, value, attrs=attrs)


def write_neuron_params(path: Path, meta: dict) -> None:
    """Write/insert learner tags that may be absent from gen/nextseg archives."""
    t = path.read_text(encoding="utf-8", errors="replace")
    # always present-ish
    for tag, val in (
        ("IsNeedToTrain", "0"),
        ("DendriteLength", L_CANON),
        ("TipSynapseResistance", TIPR_CANON),
        ("NeuronClassName", meta.get("neuron", PSI_CLASSES[0.0])),
        ("EnableNextSegmentInhibition", meta.get("nextseg", "0")),
        ("FixedLTZThreshold", meta.get("ltz", LTZ_GOLD_TEST)),
        ("UseFixedLTZThreshold", "1"),
        ("AutoCalibrateFixedLTZThreshold", "0"),
    ):
        if get_tag(t, tag) is not None:
            t = set_tag(t, tag, val, 0)
        else:
            t = ensure_tag_after(
                t,
                "DendriteLength" if tag != "DendriteLength" else "NeuronClassName",
                tag,
                val,
                attrs=' Type="d" PType="257" IoType="17"'
                if tag in ("FixedLTZThreshold", "SegExcInhAlpha", "SegExcInhDelta")
                or "Resistance" in tag
                else ' Type="b" PType="257" IoType="17"',
            )
    # PostTune off
    t = patch_or_insert(
        t,
        "EnablePostTrainTuning",
        "0",
        after="IsNeedToTrain",
        attrs=' Type="b" PType="257" IoType="17"',
    )
    # SegEI — often ABSENT on gen XML; set_tag alone was a silent no-op (C1 bug)
    t = patch_or_insert(
        t,
        "EnableSegExcInh",
        meta.get("segei", "0"),
        after="EnableNextSegmentInhibition",
        attrs=' Type="b" PType="257" IoType="17"',
    )
    t = patch_or_insert(
        t,
        "SegExcInhDelta",
        meta.get("delta", "8"),
        after="EnableSegExcInh",
        attrs=' Type="i" PType="257" IoType="17"',
    )
    t = patch_or_insert(
        t,
        "SegExcInhAlpha",
        meta.get("alpha", "1.0"),
        after="SegExcInhDelta",
        attrs=' Type="d" PType="257" IoType="17"',
    )
    # NextSeg Inh weight: runtime override (XML InhSynapse Resistance is rewritten
    # by EnsureNextSegInhSynapseOnSegment, so the old block patch was a no-op).
    if "nextseg_r" in meta:  # needs Console with NextSegInhResistance (2026-10-24)
        t = patch_or_insert(
            t,
            "NextSegInhResistance",
            meta["nextseg_r"],
            after="SegExcInhAlpha",
            attrs=' Type="d" PType="257" IoType="17"',
        )
    path.write_text(t, encoding="utf-8")


def scale_inh_resistances(model: Path, scale: float) -> int:
    """Set every InhSynapse* Resistance ≈ TipR_last/scale. Returns #blocks patched."""
    if scale <= 0:
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
        r"<InhSynapse\d*\b[\s\S]*?</InhSynapse\d*>",
        repl,
        t,
        flags=re.I,
    )
    model.write_text(t2, encoding="utf-8")
    return int(n)


def apply_trial_order(params: Path, perm: list[int]) -> None:
    """Reorder Test dataset samples (MatrixData rows x4 + MatrixClasses) by perm.
    new sample i = old sample perm[i]. Used for trial-order controls (C1b)."""
    t = params.read_text(encoding="utf-8", errors="replace")

    def fix_data(m: re.Match[str]) -> str:
        vals = m.group(2).split()
        n = len(perm)
        if len(vals) % n:
            return m.group(0)
        k = len(vals) // n
        rows = [vals[i * k:(i + 1) * k] for i in range(n)]
        new = [x for i in perm for x in rows[i]]
        return m.group(1) + "\n".join(new) + m.group(3)

    def fix_cls(m: re.Match[str]) -> str:
        vals = m.group(2).split()
        if len(vals) != len(perm):
            return m.group(0)
        return m.group(1) + "\n".join(vals[i] for i in perm) + m.group(3)

    t = re.sub(r"(<MatrixData\b[^>]*>)([^<]*)(</MatrixData>)", fix_data, t)
    t = re.sub(r"(<MatrixClasses\b[^>]*>)([^<]*)(</MatrixClasses>)", fix_cls, t)
    params.write_text(t, encoding="utf-8")


SIM_TIME_TAGS = (
    "MembraneCapacity", "SynapseSecretionTC", "SynapseDissociationTC",
    "SynapseTypicalPulseDuration", "Capacity", "SecretionTC", "DissociationTC",
    "TypicalPulseDuration", "PulseLength",
)


def scale_time_xml(path: Path, k: float, *, pattern: bool, constants: bool) -> dict:
    """Q1 H-sim: multiply pattern times (MatrixData) and/or every time constant by k."""
    t = path.read_text(encoding="utf-8", errors="replace")
    counts: dict = {}

    def mul(m: re.Match[str]) -> str:
        vals = m.group(2).split()
        try:
            new = [f"{float(v) * k:.12g}" for v in vals]
        except ValueError:
            return m.group(0)
        return m.group(1) + "\n".join(new) + m.group(3)

    if pattern:
        t, n = re.subn(r"(<MatrixData\b[^>]*>)([^<]*)(</MatrixData>)", mul, t)
        counts["MatrixData"] = n
    if constants:
        for tag in SIM_TIME_TAGS:
            t, n = re.subn(rf"(<{tag}\b[^>]*>)([^<]*)(</{tag}>)", mul, t)
            counts[tag] = n
        if "<SynapseTypicalPulseDuration" not in t and "<SynapseSecretionTC" in t:
            t = ensure_tag_after(t, "SynapseSecretionTC", "SynapseTypicalPulseDuration",
                                 f"{0.001 * k:.12g}", attrs=' Type="d" PType="257" IoType="17"')
            counts["SynapseTypicalPulseDuration_inserted"] = 1
    path.write_text(t, encoding="utf-8")
    return counts


def unlink_inh_inputs(model: Path) -> None:
    t = model.read_text(encoding="utf-8", errors="replace")

    def drop_inh_link(m: re.Match[str]) -> str:
        block = m.group(0)
        if re.search(r"Inh", block, re.I):
            return ""
        return block

    t2 = re.sub(r"<elem\s+Type=\"ULink\">[\s\S]*?</elem>", drop_inh_link, t)
    model.write_text(t2, encoding="utf-8")


def readback(test_dir: Path, meta: dict) -> dict:
    params = (test_dir / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace")
    model = (test_dir / "Model_00.xml").read_text(encoding="utf-8", errors="replace")
    inh_r = re.findall(
        r"<InhSynapse\d*\b[\s\S]*?<Resistance[^>]*>([^<]+)", model, flags=re.I
    )
    rb = {
        "expect": {
            "neuron": meta.get("neuron"),
            "nextseg": meta.get("nextseg"),
            "segei": meta.get("segei"),
            "delta": meta.get("delta"),
            "alpha": meta.get("alpha"),
            "w": meta.get("w"),
        },
        "Parameters": {
            "EnableSegExcInh": get_tag(params, "EnableSegExcInh"),
            "SegExcInhDelta": get_tag(params, "SegExcInhDelta"),
            "SegExcInhAlpha": get_tag(params, "SegExcInhAlpha"),
            "EnableNextSegmentInhibition": get_tag(params, "EnableNextSegmentInhibition"),
            "NeuronClassName": get_tag(params, "NeuronClassName"),
            "DendriteLength": get_tag(params, "DendriteLength"),
            "TipSynapseResistance": get_tag(params, "TipSynapseResistance"),
            "FixedLTZThreshold": get_tag(params, "FixedLTZThreshold"),
        },
        "Model": {
            "EnableSegExcInh": get_tag(model, "EnableSegExcInh"),
            "SegExcInhDelta": get_tag(model, "SegExcInhDelta"),
            "SegExcInhAlpha": get_tag(model, "SegExcInhAlpha"),
            "EnableNextSegmentInhibition": get_tag(model, "EnableNextSegmentInhibition"),
            "NextSegInhResistance": get_tag(model, "NextSegInhResistance"),
            "NeuronClassName": get_tag(model, "NeuronClassName"),
            "DendriteLength": get_tag(model, "DendriteLength"),
            "TipSynapseResistance": get_tag(model, "TipSynapseResistance"),
            "InhResistance_sample": inh_r[:6],
            "InhResistance_n": len(inh_r),
        },
    }
    ok = True
    errs: list[str] = []
    if meta.get("segei") == "1":
        for side in ("Parameters", "Model"):
            if rb[side]["EnableSegExcInh"] != "1":
                ok = False
                errs.append(f"{side}.EnableSegExcInh!={rb[side]['EnableSegExcInh']}")
            if rb[side]["SegExcInhDelta"] != str(meta.get("delta", "8")):
                ok = False
                errs.append(f"{side}.Delta mismatch")
            if rb[side]["SegExcInhAlpha"] != str(meta.get("alpha", "1.0")):
                ok = False
                errs.append(f"{side}.Alpha mismatch")
    if meta.get("nextseg") == "1":
        for side in ("Parameters", "Model"):
            if rb[side]["EnableNextSegmentInhibition"] != "1":
                ok = False
                errs.append(f"{side}.NextSeg off")
        if "w" in meta and meta["w"] is not None:
            if len(inh_r) < 1:
                ok = False
                errs.append("no Inh Resistance in Model")
    rb["readback_ok"] = ok
    rb["readback_errors"] = errs
    return rb


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
    for side in ("Test", "Train"):
        root = out / side
        if not root.is_dir():
            continue
        params = root / "Parameters_00.xml"
        model = root / "Model_00.xml"
        if params.is_file():
            write_neuron_params(params, meta)
        if model.is_file():
            write_neuron_params(model, meta)
            if "w" in meta:
                n = scale_inh_resistances(model, float(meta["w"]))
                meta = dict(meta)
                meta["inh_blocks_patched"] = n
            if meta.get("inh_input_off") == "1":
                unlink_inh_inputs(model)
        if meta.get("time_k"):
            k = float(meta["time_k"])
            sc = {}
            if params.is_file():
                sc["Parameters"] = scale_time_xml(params, k, pattern=True,
                                                  constants=meta.get("sim_xml") == "1")
            if model.is_file():
                sc["Model"] = scale_time_xml(model, k, pattern=True,
                                             constants=meta.get("sim_xml") == "1")
            meta = dict(meta)
            meta.setdefault("time_scale_counts", {})[side] = sc
        if params.is_file() and side == "Test" and meta.get("order"):
            apply_trial_order(params, [int(x) for x in meta["order"]])
    test = out / "Test"
    rb = readback(test, meta)
    (out / "c1_meta.json").write_text(
        json.dumps(jsonable({**meta, "readback": rb}), indent=2) + "\n", encoding="utf-8"
    )
    (out / "c1_readback.json").write_text(json.dumps(rb, indent=2) + "\n", encoding="utf-8")
    if not rb["readback_ok"]:
        raise SystemExit(f"READBACK_FAIL {out.name}: {rb['readback_errors']}")
    return test


def run_console(test_dir: Path, *, tsec: float, log: Path, timeout_s: int) -> int:
    ini = test_dir / "Project.ini"
    if not ini.is_file():
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


def results_md5(wd: Path) -> str | None:
    for c in (wd / "Test" / "SelectivityLog" / "results.csv", wd / "Test" / "results.csv"):
        if c.is_file():
            return hashlib.md5(c.read_bytes()).hexdigest()
    return None


def sep_margin(wd: Path) -> float | None:
    for c in (wd / "Test" / "SelectivityLog" / "results.csv", wd / "Test" / "results.csv"):
        if not c.is_file():
            continue
        rows = list(csv.DictReader(c.open()))
        tgt = [float(r["ltz_potential_max"]) for r in rows if r.get("target_class") == "1"]
        foil = [float(r["ltz_potential_max"]) for r in rows if r.get("target_class") == "0"]
        if not tgt or not foil:
            return None
        mn, mx = min(tgt), max(foil)
        return (mn - mx) / mn if abs(mn) > 1e-18 else None
    return None


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
    if series in ("all", "nextseg", "mech"):
        # mech probe uses w=0 vs w=4 only; full nextseg grid when series=nextseg/all
        weights = (0.0, 4.0) if series == "mech" else (0.0, 0.25, 0.5, 1.0, 2.0, 4.0)
        for w in weights:
            jobs.append(
                {
                    "id": f"nextseg_w{w}",
                    "template": BASE_NEXTSEG,
                    "neuron": PSI_CLASSES[0.0],
                    "nextseg": "1" if w > 0 else "0",
                    "segei": "0",
                    "w": w,
                    "nextseg_r": f"{TIPR_LAST / w:.17g}" if w > 0 else "0",
                }
            )
    if series in ("all", "segei", "mech"):
        # mech: one segei on vs gen baseline delta mismatch check
        deltas = (1, 8) if series == "mech" else (1, 2, 4, 8)
        alphas = (1.0,) if series == "mech" else (0.5, 1.0, 2.0)
        for d in deltas:
            for a in alphas:
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
            if series != "mech":
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
    if series == "onoff":
        # inhibition on/off controls (bot takeover 2026-10-24)
        jobs += [
            {"id": "onoff_nextseg_on_legacyR", "template": BASE_NEXTSEG,
             "neuron": PSI_CLASSES[0.0], "nextseg": "1", "segei": "0"},
            {"id": "onoff_nextseg_off", "template": BASE_NEXTSEG,
             "neuron": PSI_CLASSES[0.0], "nextseg": "0", "segei": "0"},
            {"id": "onoff_nextseg_on_inhinputoff", "template": BASE_NEXTSEG,
             "neuron": PSI_CLASSES[0.0], "nextseg": "1", "segei": "0",
             "inh_input_off": "1"},
            {"id": "onoff_gen_noinh", "template": BASE_GEN,
             "neuron": PSI_CLASSES[0.0], "nextseg": "0", "segei": "0"},
            {"id": "onoff_segei_d8_on", "template": BASE_GEN,
             "neuron": PSI_CLASSES[0.0], "nextseg": "0", "segei": "1",
             "delta": "8", "alpha": "1.0"},
            {"id": "onoff_segei_d1_on", "template": BASE_GEN,
             "neuron": PSI_CLASSES[0.0], "nextseg": "0", "segei": "1",
             "delta": "1", "alpha": "1.0"},
        ]
    if series == "c1b":
        # C1b (2026-10-24 21:xx): fine nextseg weights, pure cable-load control,
        # trial-order controls (target not first). Needs NextSegInhResistance Console.
        def ns(w, **kw):
            j = {"id": f"nextseg_w{w}", "template": BASE_NEXTSEG,
                 "neuron": PSI_CLASSES[0.0], "nextseg": "1" if w > 0 else "0",
                 "segei": "0", "w": w}
            if w > 0:
                j["nextseg_r"] = f"{TIPR_LAST / w:.17g}"
            j.update(kw)
            return j
        rot4 = [4, 5, 6, 7, 0, 1, 2, 3]
        last = [1, 2, 3, 4, 5, 6, 7, 0]
        jobs += [
            ns(0.75), ns(1.25), ns(1.5),
            {"id": "nextseg_load_only_R1e15", "template": BASE_NEXTSEG,
             "neuron": PSI_CLASSES[0.0], "nextseg": "1", "segei": "0",
             "nextseg_r": "1e15"},
            ns(1.0, id="nextseg_w1.0_tpos4", order=rot4),
            ns(1.0, id="nextseg_w1.0_tlast", order=last),
            ns(0.0, id="nextseg_w0.0_tpos4", order=rot4),
            {"id": "segei_d1_a1.0_tpos4", "template": BASE_GEN,
             "neuron": PSI_CLASSES[0.0], "nextseg": "0", "segei": "1",
             "delta": "1", "alpha": "1.0", "order": rot4},
        ]
    if series == "q1sim":
        # Q1 H-sim Console probe: trained S25 structure (L=13 11 7 1, nextseg w=1)
        # replayed with every time constant x k and pattern x k (exact similarity),
        # vs naive (pattern x k only, original neuron) and Sim1 identity control.
        def q(id_, k, cls, nextseg_w, sim):
            j = {"id": id_, "template": BASE_NEXTSEG if nextseg_w > 0 else BASE_GEN,
                 "neuron": cls, "nextseg": "1" if nextseg_w > 0 else "0",
                 "segei": "0"}
            if nextseg_w > 0:
                j["w"] = nextseg_w
                j["nextseg_r"] = f"{TIPR_LAST / nextseg_w:.17g}"
            if k != 1.0:
                j["time_k"] = k
            if sim:
                j["sim_xml"] = "1"
            return j
        jobs += [
            q("sim_k1_identity_ns_w1", 1.0, "NSPNeuronGenAsymRmD001C1e9Sim1", 1.0, False),
            q("sim_k2_ns_w1", 2.0, "NSPNeuronGenAsymRmD001C1e9Sim2", 1.0, True),
            q("sim_k4_ns_w1", 4.0, "NSPNeuronGenAsymRmD001C1e9Sim4", 1.0, True),
            q("sim_k2_gen", 2.0, "NSPNeuronGenAsymRmD001C1e9Sim2", 0.0, True),
            q("sim_k4_gen", 4.0, "NSPNeuronGenAsymRmD001C1e9Sim4", 0.0, True),
            q("naive_k2_ns_w1", 2.0, PSI_CLASSES[0.0], 1.0, False),
            q("naive_k4_ns_w1", 4.0, PSI_CLASSES[0.0], 1.0, False),
            q("sim_k2_ns_w0.5", 2.0, "NSPNeuronGenAsymRmD001C1e9Sim2", 0.5, True),
            q("sim_k2_ns_w2.0", 2.0, "NSPNeuronGenAsymRmD001C1e9Sim2", 2.0, True),
            q("sim_k4_ns_w0.5", 4.0, "NSPNeuronGenAsymRmD001C1e9Sim4", 0.5, True),
            q("sim_k4_ns_w2.0", 4.0, "NSPNeuronGenAsymRmD001C1e9Sim4", 2.0, True),
        ]
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
    ap.add_argument(
        "--series",
        default="mech",
        choices=("all", "psi", "nextseg", "segei", "combo", "mech", "onoff", "c1b", "q1sim"),
        help="Default mech=prove nextseg/segei write+effect before dose grids",
    )
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--tsec", type=float, default=40.0)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--host-tag", default="local")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    if not CONSOLE.is_file():
        raise SystemExit(f"missing Console {CONSOLE}")

    jobs = build_jobs(args.series)
    if args.only.strip():
        want = {x.strip() for x in args.only.split(",") if x.strip()}
        jobs = [j for j in jobs if j["id"] in want]
        if not jobs:
            raise SystemExit(f"--only matched nothing; want={sorted(want)}")
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
        md5 = results_md5(wd)
        sep = sep_margin(wd)
        return {
            "id": job["id"],
            "workdir": str(wd),
            "log": str(log),
            "rc": rc,
            "elapsed_s": round(time.time() - t0, 1),
            "results_md5": md5 or "",
            "sep_margin": "" if sep is None else f"{sep:.6f}",
            "meta": json.dumps(jsonable(job), sort_keys=True),
        }

    print(
        f"C1 jobs={len(jobs)} limit={args.limit} timeout={args.timeout}s "
        f"series={args.series} out={args.out_root}",
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=max(1, args.limit)) as ex:
        futs = [ex.submit(one, j) for j in jobs]
        for fut in as_completed(futs):
            row = fut.result()
            rows.append(row)
            print(
                f"DONE {row['id']} rc={row['rc']} et={row['elapsed_s']}s "
                f"md5={row['results_md5'][:8]} sep={row['sep_margin']}",
                flush=True,
            )

    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "workdir",
                "log",
                "rc",
                "elapsed_s",
                "results_md5",
                "sep_margin",
                "meta",
            ],
        )
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["id"]):
            w.writerow(r)

    # Mechanism verdict for nextseg / segei
    by_id = {r["id"]: r for r in rows}
    mech = {"nextseg": None, "segei": None}
    if "nextseg_w0.0" in by_id and "nextseg_w4.0" in by_id:
        a, b = by_id["nextseg_w0.0"], by_id["nextseg_w4.0"]
        mech["nextseg"] = {
            "md5_w0": a["results_md5"],
            "md5_w4": b["results_md5"],
            "differ": a["results_md5"] != b["results_md5"] and bool(a["results_md5"]),
            "sep_w0": a["sep_margin"],
            "sep_w4": b["sep_margin"],
            "verdict": "PASS"
            if a["results_md5"]
            and b["results_md5"]
            and a["results_md5"] != b["results_md5"]
            else "FAIL_no_effect",
        }
    if "segei_d1_a1.0" in by_id and "segei_d8_a1.0" in by_id:
        a, b = by_id["segei_d1_a1.0"], by_id["segei_d8_a1.0"]
        mech["segei"] = {
            "md5_d1": a["results_md5"],
            "md5_d8": b["results_md5"],
            "differ": a["results_md5"] != b["results_md5"] and bool(a["results_md5"]),
            "verdict": "PASS"
            if a["results_md5"]
            and b["results_md5"]
            and a["results_md5"] != b["results_md5"]
            else "FAIL_no_effect_or_write",
        }
    mech_path = args.out_root / "C1_MECH_VERDICT.json"
    mech_path.write_text(json.dumps(mech, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {manifest} n={len(rows)}")
    print(f"WROTE {mech_path} {json.dumps(mech)}")
    if args.series == "mech":
        bad = [
            k
            for k, v in mech.items()
            if v is not None and v.get("verdict", "").startswith("FAIL")
        ]
        if bad:
            print(f"MECH_FAIL {bad} — do not run dose grids yet", flush=True)
            return 2
        print("MECH_PASS — dose grids may proceed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
