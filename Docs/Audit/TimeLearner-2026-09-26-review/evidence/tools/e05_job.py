#!/usr/bin/env python3
"""PLAN 2026-10-25 series E1-E5: one job = SoftCold Train (posttune_verify.run_case) of a TauH0 template
with per-config neuron-class overrides, dt = 0.5 ms (DefaultTimeStep 2000) in Train AND Test, then extra
Console tests of the trained Test model:
  q    : shifted-spike foils (spike j=1,2 by +-S/4 and +-S/8, as fastmodels/sim/evalset.foils_shift),
         2 batches x 8, target not first, Delay(ITI) 1.5 s
  iti6 : original 8-sample MatrixData, permuted (target not first), Delay 6.0 s
Metrics -> OUT/result.json (sep_margin audit, m(S/4), m(S/8), m8 (gate + iti6), detection, done_be, final L).
usage: e05_job.py OUT JSON_SPEC
spec keys: label kind(classic|branch) span(50|100) mod(preinh|gen) mode(N0|N1) L "a b c d" maxdl est(opt)
           ov{OverrideMembraneCapacity..} jitter dlog{DynamicsLogHead,DynamicsLogEvery,DynamicsLogComponentState}
           reuse_work(opt: existing *_work dir -> skip training, re-test only) reuse_result(opt: old result.json for row)
           be_transfer(default 0): if C++ refused training, Test is still the template -> build OUT/be_Test from Train via be_prep.py (phase9 recipe);
           metrics_basis=be_transfer_rejected_structure (NOT valid training). tests(opt list: q iti6 gate05 itiS; default q iti6 gate05)
2026-10-25 03:40 MSK fixes: train_valid / test_is_trained flags (Classic refusals tested the TEMPLATE before),
  best-effort transfer of refused structure, phase8 gate keys renamed (dt 0.05 ms), gate05 dt check,
  jitter documented as ineffective (C++ canonicalises last tip to TipResistanceCanonLast; Console deterministic).
"""
import sys, os, json, re, shutil, subprocess, time, csv, glob
from pathlib import Path
NM = Path(os.environ.get("NMSDK_ROOT", os.path.expanduser("~/Nmsdk")))
ST = NM / "Bin/Configs/SpikeSamples/StructTrain"
sys.path.insert(0, str(ST / "scripts"))
sys.path.insert(0, str(NM / "Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools"))
OUT = Path(sys.argv[1]); SPEC = json.loads(Path(sys.argv[2]).read_text()) if Path(sys.argv[2]).is_file() else json.loads(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
os.environ["TIMELEARNER_MATRIX_RUNS_ROOT"] = str(OUT / "work")  # always inside the job dir (dispatcher accounting, offload)
Path(os.environ["TIMELEARNER_MATRIX_RUNS_ROOT"]).mkdir(parents=True, exist_ok=True)
# 2026-10-25 09:40 MSK fix: the per-job console must be set BEFORE importing repro_cold_lib, because
# repro_cold_lib.NM (= Train console used by posttune_verify) is resolved at import time. Before this fix
# spec "console" reached only the extra tests; Train ran on the dispatcher console (e05b).
if SPEC.get("console"):  # per-job console (e.g. PulseLib e05c with RminNoImproveMinProgress); also seen by posttune_verify
    os.environ["NMSDK_CONSOLE"] = os.path.expanduser(SPEC["console"])
from repro_cold_lib import get_tag, set_tag, set_tag_all, ensure_tag_after  # noqa
STEP = 2000
CONSOLE = os.environ.get("NMSDK_CONSOLE") or str(NM / "Bin/Platform/Linux/NeuroModelerConsole")
kind, span = SPEC["kind"], int(SPEC["span"])
mod, mode = SPEC.get("mod", "preinh"), SPEC.get("mode", "N1")
# 2026-10-25 (plan A/D/E): spec "src" (path rel. to StructTrain or absolute) and "base_case" (posttune_verify CASES key)
# allow non-TauH0 sources (SelectivityInhGrid); "train_t" overrides the sim-time budget.
SRC = (Path(SPEC["src"]) if os.path.isabs(SPEC["src"]) else ST / SPEC["src"]) if SPEC.get("src") else ST / "SelectivityTauCm" / f"EXP_{kind}_S{span}_{mod}_TauH0_{mode}"
TRAIN_T = int(SPEC.get("train_t") or {50: 640, 100: 1280}[span])
DTYPE = ' Type="d" PType="257" IoType="17"'
ITYPE = ' Type="i" PType="257" IoType="17"'
BTYPE = ' Type="b" PType="257" IoType="17"'
def log(*a):
    print(*a, flush=True)

def patch_ini(p):
    t = p.read_text()
    t = re.sub(r"<DefaultTimeStep>\d+</DefaultTimeStep>", f"<DefaultTimeStep>{STEP}</DefaultTimeStep>", t)
    t = re.sub(r"<GlobalTimeStep>\d+</GlobalTimeStep>", f"<GlobalTimeStep>{STEP}</GlobalTimeStep>", t)
    p.write_text(t)

def patch_xml(t, with_L=True):
    if SPEC.get("neuron"):  # D: PSI only via neuron class (BuildStructure rebuilds synapses from NeuronClassName; XML synapse flags are overwritten)
        t = set_tag_all(t, "NeuronClassName", SPEC["neuron"])
    if with_L and SPEC.get("L_init"):
        t = set_tag_all(t, "DendriteLength", SPEC["L_init"])
    if SPEC.get("maxdl"):
        t = set_tag_all(t, "MaxDendriteLength", str(int(SPEC["maxdl"])))
    if SPEC.get("est") and get_tag(t, "EstDelayPerSeg") is not None:
        t = set_tag_all(t, "EstDelayPerSeg", repr(float(SPEC["est"])))
    if get_tag(t, "EnableDebug") is not None:
        if SPEC.get("est") and get_tag(t, "EstDelayPerSeg") is None and SPEC.get("kind") == "branch":
            t = ensure_tag_after(t, "EnableDebug", "InitEstDelayPerSeg", repr(float(SPEC["est"])), DTYPE)  # Branch: initial adaptive estimate (PulseLib e05b)
        for k, v in SPEC.get("ov", {}).items():
            t = ensure_tag_after(t, "EnableDebug", k, repr(float(v)), DTYPE)
        for k, v in SPEC.get("lset", {}).items():  # learner property {name: [value, d|i|b]} (e.g. RminNoImproveMinProgress, PulseLib e05c)
            t = ensure_tag_after(t, "EnableDebug", k, str(v[0]), {"d": DTYPE, "i": ITYPE, "b": BTYPE}[v[1]])
        for k, v in SPEC.get("dlog", {}).items():
            t = ensure_tag_after(t, "EnableDebug", k, str(int(v)), BTYPE if k == "DynamicsLogComponentState" else ITYPE)
    return t

def readback(d):
    r = {}
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = d / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for k in ("NeuronClassName", "DendriteLength", "MaxDendriteLength", "EstDelayPerSeg", "InitEstDelayPerSeg", "MembraneCapacity", "TipSynapseResistance",
                  "OverrideMembraneCapacity", "OverrideExcMembraneResistance", "OverrideInhMembraneResistance",
                  "OverrideExcSynapseResistance", "OverrideInhSynapseResistance", "DynamicsLogHead", "DynamicsLogEvery",
                  "RminNoImproveMinProgress", "NormalizationMode", "EnablePostTrainTuning", "EnableNextSegmentInhibition", "EnableSegExcInh"):
            r[f"{rel[:-7]}.{k}"] = get_tag(t, k)
        # inhibition readback (D): presynaptic inhibition lives in the synapse flags, not in InhSynapse overrides
        r[f"{rel[:-7]}.UsePresyn_n1"] = len(re.findall(r"<UsePresynapticInhibition\b[^>]*>\s*1\s*<", t))
        r[f"{rel[:-7]}.UsePresyn_n"] = len(re.findall(r"<UsePresynapticInhibition\b", t))
        r[f"{rel[:-7]}.InhCoeff_nz"] = len([x for x in re.findall(r"<InhibitionCoeff\b[^>]*>([^<]*)<", t) if x.strip() and float(x.split()[0].replace(",", ".")) != 0.0])
    ini = (d / "Project.ini").read_text() if (d / "Project.ini").is_file() else ""
    m = re.search(r"<DefaultTimeStep>(\d+)<", ini); r["DefaultTimeStep"] = m.group(1) if m else None
    m = re.search(r"<GlobalTimeStep>(\d+)<", ini); r["GlobalTimeStep"] = m.group(1) if m else None
    ov = []
    for f in sorted(glob.glob(str(d / "EventsLog" / "*INFO*"))) + [str(x) for x in d.glob("*.log")]:
        try:
            for line in open(f, errors="replace"):
                if "NeuronClassOverrides" in line:
                    ov.append(line.strip()[-220:])
        except OSError:
            pass
    r["override_log"] = ov[:2] + (ov[-2:] if len(ov) > 2 else [])
    built = []
    for f in sorted(glob.glob(str(d / "EventsLog" / "*INFO*"))):
        try:
            for line in open(f, errors="replace"):
                m = re.search(r"NeuronClass=(\S+)", line)
                if m:
                    built.append(m.group(1))
        except OSError:
            pass
    r["built_neuron_class"] = sorted(set(built))  # what BuildStructure actually instantiated (authoritative for PSI)
    r["override_log_n"] = len(ov)
    return r

# ---------- template ----------
tpl = OUT / "template"
if not tpl.exists():
    shutil.copytree(SRC, tpl, ignore=shutil.ignore_patterns("SelectivityLog", "EventsLog", "StatisticLog", "ltz_sweep", "*.log", "*.bak", "save.tmp", "*.flag"))
    for side in ("Train", "Test"):
        patch_ini(tpl / side / "Project.ini")
        for rel in ("Parameters_00.xml", "Model_00.xml"):
            p = tpl / side / rel
            p.write_text(patch_xml(p.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
log("TEMPLATE", SRC.name, "->", tpl, json.dumps(readback(tpl / "Train")))

import posttune_verify as mod_pv
case = f"e05_{SPEC['label']}"
base_key = SPEC.get("base_case") or f"h0_{kind[0]}{span}_{mod}_{mode.lower()}_{SPEC.get('pt', 'pton')}"
mod_pv.CASES[case] = dict(mod_pv.CASES[base_key]); mod_pv.CASES[case]["root"] = tpl
log("BASE_CASE", base_key, {k: v for k, v in mod_pv.CASES[case].items() if k != "h0_meta"})
_orig = mod_pv.soft_cold_reset_train
J = float(SPEC.get("jitter", 0.0))
def reset_then_patch(train, **kw):
    _orig(train, **kw)
    train = Path(train)
    patch_ini(train / "Project.ini")
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = train / rel
        if not p.is_file():
            continue
        t = patch_xml(p.read_text(encoding="utf-8", errors="replace"), with_L=False)
        tip = get_tag(t, "TipSynapseResistance")
        if tip and J:
            # NOTE: ineffective - C++ reset canonicalises the last tip (TipResistanceCanonLast); kept only for audit
            vals = [float(x.replace(",", ".")) for x in tip.split()]
            vals[-1] *= (1.0 + J)
            t = set_tag(t, "TipSynapseResistance", " ".join(f"{v:.17g}" for v in vals), 1)
        p.write_text(t, encoding="utf-8")
    log("POST_RESET", json.dumps(readback(train)))
mod_pv.soft_cold_reset_train = reset_then_patch
t0 = time.time()
if SPEC.get("reuse_work"):
    work = Path(SPEC["reuse_work"])
    old = json.loads(Path(SPEC["reuse_result"]).read_text()) if SPEC.get("reuse_result") else {}
    row = dict(old.get("row") or {})
    log("REUSE", work, "old_row", json.dumps(row, default=str)[:400])
else:
    row = mod_pv.run_case(case, train_t=TRAIN_T)
wall_train = time.time() - t0
if not SPEC.get("reuse_work"):
    cands = sorted(Path(os.environ["TIMELEARNER_MATRIX_RUNS_ROOT"]).glob(f"{case}_*_work"))
    work = cands[-1] if cands else None
log("ROW", json.dumps({k: row.get(k) for k in ("verdict", "train_status", "training_convergence", "separation_quality", "detection_quality",
                                                  "target_detected", "fires", "metrics", "sep_margin", "done_be", "run_dir")}, default=str))


# ---------- gate: Train console + expected learner flags in Train XML (2026-10-25) ----------
def _sha(p):
    import hashlib
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except OSError:
        return None
def train_gate():
    g = {"ok": True, "reasons": []}
    used = str(getattr(mod_pv, "NM", ""))  # posttune_verify builds the Train cmd from this module global
    g["train_console"] = used
    if SPEC.get("console"):
        want = os.path.expanduser(SPEC["console"])
        g["spec_console"] = want
        if os.path.realpath(used) != os.path.realpath(want) and _sha(used) != _sha(want):
            g["ok"] = False; g["reasons"].append(f"train console {used} != spec console {want}")
    exp = dict(SPEC.get("lset", {}))
    exp.update({k: [v, "d"] for k, v in SPEC.get("expect_train_tags", {}).items()})
    g["flags"] = {}
    if exp:
        if not work or not (work / "Train").is_dir():
            g["ok"] = False; g["reasons"].append("no Train work dir"); return g
        for k, v in exp.items():
            seen = []
            for rel in ("Model_00.xml", "Parameters_00.xml"):
                p = work / "Train" / rel
                if p.is_file():
                    seen += re.findall(r"<%s\b[^>]*>([^<]*)</%s>" % (k, k), p.read_text(encoding="utf-8", errors="replace"))
            vals = sorted(set(x.strip() for x in seen))
            g["flags"][k] = vals
            def same(x):
                try:
                    return abs(float(x) - float(v[0])) <= 1e-12 * max(1.0, abs(float(v[0])))
                except ValueError:
                    return x == str(v[0])
            if not vals:
                g["ok"] = False; g["reasons"].append(f"{k} missing in Train XML")
            elif not all(same(x) for x in vals):
                g["ok"] = False; g["reasons"].append(f"{k}={vals} in Train XML, expected {v[0]}")
    return g
if not SPEC.get("reuse_work"):
    GATE = train_gate()
    log("TRAIN_GATE", json.dumps(GATE))
    if not GATE["ok"]:
        bad = {"job_valid": False, "invalid_reasons": GATE["reasons"], "train_gate": GATE, "console": os.environ.get("NMSDK_CONSOLE", ""),
               "spec": SPEC, "work": str(work), "row": {k: row.get(k) for k in ("train_status", "training_convergence")},
               "metrics_basis": "INVALID_train_gate", "wall_total_s": round(time.time() - t0)}
        (OUT / "result.json").write_text(json.dumps(bad, indent=1, default=str))
        (OUT / "INVALID").write_text("\n".join(GATE["reasons"]) + "\n")
        log("RESULT", json.dumps({"job_valid": False, "invalid_reasons": GATE["reasons"]}))
        sys.exit(3)
else:
    GATE = {"ok": None, "reasons": ["reuse_work: training not re-run, gate not applied"]}

# ---------- extra tests ----------
ISI = [[0.000520833, 0.00416667, 0.00833333, 0.0125]]
def times_target():
    s = span / 1000.0 / 0.025
    v = [x * s for x in ISI[0]]
    return [0.0, v[1], v[1] + v[2], v[1] + v[2] + v[3]], v[0]
def foils(D):
    tt, _ = times_target(); out = []
    for j in (1, 2):
        for sg in (-1, 1):
            q = list(tt); q[j] += sg * D; mn = min(0.0, min(q)); q = sorted(x - mn for x in q); out.append(((j, sg), q))
    return out
def row_of(times, off):
    return [off + times[0]] + [times[i] - times[i - 1] for i in range(1, 4)]

TESTSRC = None  # set below: work/Test (trained) or OUT/be_Test (best-effort transfer of refused structure)
INH_OFF = {"UsePresynapticInhibition": "0", "InhibitionCoeff": "0", "EnableNextSegmentInhibition": "0", "EnableSegExcInh": "0"}
def run_test(name, samples, classes, delay, inh_off=False):
    src = TESTSRC
    d = OUT / "xt" / name
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(src, d / "Test", ignore=shutil.ignore_patterns("SelectivityLog", "EventsLog", "StatisticLog", "*.log"))
    (d / "Test" / "SelectivityLog").mkdir(exist_ok=True)
    patch_ini(d / "Test" / "Project.ini")
    data = "\n".join(f"{x:.9g}" for r in samples for x in r)
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = d / "Test" / rel; t = p.read_text(encoding="utf-8", errors="replace")
        if samples is not None:
            t = re.sub(r'(<MatrixData Type="MDMatrix&lt;d&gt;" Rows="32" Cols="1"[^>]*>)[^<]*(</MatrixData>)', lambda m: m.group(1) + data + m.group(2), t)
            t = re.sub(r'(<MatrixClasses Type="MDMatrix&lt;i&gt;" Rows="1" Cols="8"[^>]*>)[^<]*(</MatrixClasses>)', lambda m: m.group(1) + "\n".join(map(str, classes)) + m.group(2), t)
        t = re.sub(r'(<Delay Type="d" PType="257" IoType="17">)1\.5(</Delay>)', r'\g<1>%s\g<2>' % delay, t)
        if inh_off:  # all inhibition mechanisms off in the trained Test (structure unchanged)
            for k, v in INH_OFF.items():
                t = set_tag_all(t, k, v)
            if SPEC.get("neuron_off"):  # PSI off = same structure, non-Preinh class of the same family
                t = set_tag_all(t, "NeuronClassName", SPEC["neuron_off"])
        p.write_text(t, encoding="utf-8")
    tsec = str(int(8 * (float(delay) + 0.05) + 15 if float(delay) >= 1.0 else 8 * (float(delay) + 0.2) + 25))  # short ITI: ~13 s warm-up before trial 0 (itiS 17 s gave 2 rows)
    with open(d / "console.log", "w") as f:
        pr = subprocess.Popen([CONSOLE, "-c", str(d / "Test" / "Project.ini"), "-s", "-t", tsec, "-x"], stdout=f, stderr=subprocess.STDOUT, cwd=str(d / "Test"))
        try:
            rc = pr.wait(timeout=5400)
        except subprocess.TimeoutExpired:
            pr.kill(); rc = 124
    r = d / "Test" / "SelectivityLog" / "results.csv"
    rows = list(csv.DictReader(r.open())) if r.is_file() else []
    log("XT", name, "rc", rc, "rows", len(rows), " ".join(f"{x['trial']}:{x['target_class']}:{x['neuron_fired']}:{float(x['ltz_potential_max']):.5f}" for x in rows))
    return rows, readback(d / "Test")

def orig_samples():
    t = (TESTSRC / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace")
    vals = [float(x) for x in get_tag(t, "MatrixData").split()]
    cls = [int(float(x)) for x in get_tag(t, "MatrixClasses").split()]
    return [vals[i * 4:(i + 1) * 4] for i in range(8)], cls

res = {"console": os.environ.get("NMSDK_CONSOLE", ""), "spec": SPEC, "src": SRC.name, "train_t": TRAIN_T, "wall_train_s": round(wall_train), "work": str(work),
       "row": {k: row.get(k) for k in ("verdict", "train_status", "training_convergence", "separation_quality", "detection_quality",
                                       "target_detected", "fires", "metrics", "delay_residue", "amp_over_target", "sync_exit", "amp_be",
                                       "done_be", "sep_margin", "sep_gap", "sep_tgt", "sep_max_foil", "run_dir", "gate_ok")}}
res["jitter"] = J; res["jitter_effective"] = False if J else None
res["train_gate"] = GATE; res["job_valid"] = GATE["ok"] is not False
if work and (work / "Test" / "Parameters_00.xml").is_file():
    res["readback_train"] = readback(work / "Train"); res["readback_test"] = readback(work / "Test")
    res["final_L"] = get_tag((work / "Train" / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace"), "DendriteLength")
    res["test_L"] = get_tag((work / "Test" / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace"), "DendriteLength")
    ts = str(row.get("train_status") or "")
    res["train_valid"] = bool(ts) and not (ts.startswith("cpp_training") or "refus" in ts or "fail" in ts)
    res["test_is_trained"] = (res["test_L"] or "").split() == (res["final_L"] or "").split()
    TESTSRC = work / "Test"
    res["metrics_basis"] = "trained_test" if res["test_is_trained"] else "TEMPLATE_untrained"
    if not res["test_is_trained"] and int(SPEC.get("be_transfer", 0)):
        # 2026-10-25 04:00 MSK: be_transfer = phase9 Test preparation (be_prep.py: overlay_train_params + PostTune off +
        # fixed silent threshold + enable_pattern_response_trace). Verified on E4off_c_s0: analyzer writes 8 rows.
        import be_prep
        be = OUT / "be_Test"
        res["be_info"] = be_prep.prepare(work / "Train", work / "Test", be)
        rbb = readback(be)
        res["be_readback"] = {k: rbb.get(k) for k in ("Parameters.DendriteLength", "Model.DendriteLength", "Model.TipSynapseResistance", "Model.MembraneCapacity",
                                                      "Model.OverrideInhSynapseResistance", "Model.OverrideMembraneCapacity", "DefaultTimeStep", "GlobalTimeStep")}
        rbt = res["readback_train"]
        res["be_check"] = {"L": (rbb.get("Model.DendriteLength") or "").split() == (res["final_L"] or "").split(),
                           "C": rbb.get("Model.MembraneCapacity") == rbt.get("Model.MembraneCapacity"),
                           "tips": rbb.get("Model.TipSynapseResistance") == rbt.get("Model.TipSynapseResistance")}
        if all(res["be_check"].values()):
            TESTSRC = be; res["metrics_basis"] = "be_transfer_rejected_structure"
    if res["metrics_basis"] == "TEMPLATE_untrained":
        res["skip_tests"] = "Test is the untrained template (training refused, best-effort transfer unavailable) -> no metrics"
    log("VALIDITY", json.dumps({k: res.get(k) for k in ("train_valid", "test_is_trained", "metrics_basis", "final_L", "test_L")}))
if work and (work / "Test" / "Parameters_00.xml").is_file() and not res.get("skip_tests"):
    smp, cls = orig_samples(); off = smp[0][0]
    tgt_i = cls.index(1) if 1 in cls else 0
    tt, _ = times_target()
    T = row_of(tt, off)
    f4 = foils(span / 1000.0 / 4); f8 = foils(span / 1000.0 / 8)
    A = [("f4", f4[0]), ("T", None), ("f4", f4[1]), ("f4", f4[2]), ("f4", f4[3]), ("f8", f8[0]), ("f8", f8[1]), ("T", None)]
    B = [("f8", f8[2]), ("f8", f8[3]), ("T", None), ("f8", f8[0]), ("f4", f4[0]), ("f8", f8[1]), ("f4", f4[3]), ("T", None)]
    q = {"f4": [], "f8": [], "T": [], "Tfired": []}
    TESTS = SPEC.get("tests", ["q", "iti6", "gate05"])
    for bn, batch in ((("qA", A), ("qB", B)) if "q" in TESTS else ()):
        samples = [T if k == "T" else row_of(v[1], off) for k, v in batch]
        classes = [1 if k == "T" else 0 for k, _ in batch]
        rows, rb = run_test(bn, samples, classes, "1.5")
        res[f"readback_{bn}"] = {"DefaultTimeStep": rb.get("DefaultTimeStep"), "GlobalTimeStep": rb.get("GlobalTimeStep")}
        for (k, v), r in zip(batch, rows):
            pv = float(r["ltz_potential_max"])
            q[k].append(pv)
            if k == "T":
                q["Tfired"].append(int(r["neuron_fired"]))
    if q["T"] and q["f4"]:
        pt = min(q["T"])
        res["m_S4"] = (pt - max(q["f4"])) / pt if pt else None
        res["m_S8"] = (pt - max(q["f8"])) / pt if pt else None
        res["q_target_min"] = pt; res["q_target_fired"] = q["Tfired"]
        res["q_f4"] = q["f4"]; res["q_f8"] = q["f8"]
    others = [i for i in range(8) if i != tgt_i]
    if "itiS" in TESTS:  # approved short-ITI control: Delay 0.3 s (S100) / 0.2 s (S50), target at position 4
        dS = "0.3" if span == 100 else "0.2"
        permS = others[:3] + [tgt_i] + others[3:]
        rows, rb = run_test("itiS", [smp[i] for i in permS], [cls[i] for i in permS], dS)
        tg = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "1"]
        fo = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "0"]
        res["itiS_delay"] = dS; res["itiS_perm"] = permS; res["itiS_rows"] = len(rows)
        res["readback_itiS"] = {"DefaultTimeStep": rb.get("DefaultTimeStep"), "GlobalTimeStep": rb.get("GlobalTimeStep")}
        res["m8_itiS"] = (min(tg) - max(fo)) / min(tg) if tg and fo and min(tg) else None
        res["itiS_target_fired"] = [int(x["neuron_fired"]) for x in rows if x["target_class"] == "1"]
        res["itiS_foils_fired"] = sum(int(x["neuron_fired"]) for x in rows if x["target_class"] == "0")
    perm = [3, tgt_i] + [i for i in range(8) if i not in (3, tgt_i)]
    rows, rb = (run_test("iti6", [smp[i] for i in perm], [cls[i] for i in perm], "6.0")) if "iti6" in TESTS else ([], {})
    tg = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "1"]
    fo = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "0"]
    res["iti6_perm"] = perm
    res["m8_iti6"] = (min(tg) - max(fo)) / min(tg) if tg and fo and min(tg) else None
    res["iti6_target_fired"] = [int(x["neuron_fired"]) for x in rows if x["target_class"] == "1"]
    res["iti6_foils_fired"] = sum(int(x["neuron_fired"]) for x in rows if x["target_class"] == "0")
    # gate05 (2026-10-25 02:30 MSK fix): phase8 gate forces Test GlobalTimeStep=20000 (dt 0.05 ms) -> m8_gate is NOT at dt 0.5 ms.
    # Re-run original samples at dt 0.5 ms (patch_ini), Delay 1.5, target at position 4 (not first).
    perm5 = others[:4] + [tgt_i] + others[4:]
    rows, rb = run_test("gate05", [smp[i] for i in perm5], [cls[i] for i in perm5], "1.5") if "gate05" in TESTS else ([], {})
    res["readback_gate05"] = {"DefaultTimeStep": rb.get("DefaultTimeStep"), "GlobalTimeStep": rb.get("GlobalTimeStep")}
    tg = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "1"]
    fo = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "0"]
    res["gate05_perm"] = perm5
    res["m8_gate05"] = (min(tg) - max(fo)) / min(tg) if tg and fo and min(tg) else None
    res["gate05_target_fired"] = [int(x["neuron_fired"]) for x in rows if x["target_class"] == "1"]
    res["gate05_foils_fired"] = sum(int(x["neuron_fired"]) for x in rows if x["target_class"] == "0")
    res["gate05_dt_ok"] = rb.get("GlobalTimeStep") == str(STEP) and rb.get("DefaultTimeStep") == str(STEP)
    res["phase8_gate_GlobalTimeStep"] = readback(work / "Test").get("GlobalTimeStep")  # phase8/9 gate Test (20000 = 0.05 ms): NOT the series dt
    # gate test m8 (posttune_verify Test as run, Delay 1.5, original order; dt per gate_GlobalTimeStep, 20000 = 0.05 ms -> diagnostic only)
    g = work / "Test" / "SelectivityLog" / "results.csv"
    if g.is_file():
        rows = list(csv.DictReader(g.open()))
        tg = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "1"]
        fo = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "0"]
        res["m8_phase8_gate"] = (min(tg) - max(fo)) / min(tg) if tg and fo and min(tg) else None  # diagnostic only (dt per phase8_gate_GlobalTimeStep)
    # dynamics log: 'now' step check
    dyn = sorted(work.glob("Train/**/*TrainingDynamics*"))
    res["dyn_logs"] = [(str(p.relative_to(work)), p.stat().st_size) for p in dyn][:4]
    nows = []
    for p in dyn[:1]:
        with open(p, errors="replace") as f:
            for i, line in enumerate(f):
                m = re.search(r"[;\s]now=([0-9.eE+-]+)", line)
                if m:
                    nows.append(float(m.group(1)))
                if len(nows) > 4000:
                    break
    steps = sorted({round(b - a, 7) for a, b in zip(nows, nows[1:]) if b > a})
    res["dyn_now_min_step"] = steps[0] if steps else None
    # D extras (2026-10-25): second target position (last, pos 7) and inhibition on/off pairs
    def m8_run(name, pm, delay, inh_off=False):
        rows, rb = run_test(name, [smp[i] for i in pm], [cls[i] for i in pm], delay, inh_off)
        tg = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "1"]
        fo = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "0"]
        res[f"{name}_perm"] = pm; res[f"{name}_rows"] = len(rows)
        res[f"m8_{name}"] = (min(tg) - max(fo)) / min(tg) if tg and fo and min(tg) else None
        res[f"{name}_target_max"] = tg; res[f"{name}_foil_max"] = max(fo) if fo else None
        res[f"{name}_target_fired"] = [int(x["neuron_fired"]) for x in rows if x["target_class"] == "1"]
        res[f"{name}_foils_fired"] = sum(int(x["neuron_fired"]) for x in rows if x["target_class"] == "0")
        res[f"readback_{name}"] = {k: rb.get(k) for k in rb if k.split(".")[-1] in ("NeuronClassName", "built_neuron_class", "DefaultTimeStep", "GlobalTimeStep", "UsePresyn_n1", "UsePresyn_n", "InhCoeff_nz", "EnableNextSegmentInhibition", "EnableSegExcInh")}
        res[f"readback_{name}"].update({"DefaultTimeStep": rb.get("DefaultTimeStep"), "GlobalTimeStep": rb.get("GlobalTimeStep")})
        return tg, fo
    perm7 = others + [tgt_i]
    if "gate05_t7" in TESTS:
        m8_run("gate05_t7", perm7, "1.5")
    if "gate05_off" in TESTS:
        m8_run("gate05_off", perm5, "1.5", True)
    if "iti6_off" in TESTS:
        m8_run("iti6_off", perm, "6.0", True)
    if "iti6_t7" in TESTS:
        m8_run("iti6_t7", perm7, "6.0")
    if "itiS" in TESTS and "itiS_off" in TESTS:
        m8_run("itiS_off", others[:3] + [tgt_i] + others[3:], "0.3" if span == 100 else "0.2", True)
res["wall_total_s"] = round(time.time() - t0)
(OUT / "result.json").write_text(json.dumps(res, indent=1, default=str))
log("RESULT", json.dumps({k: res.get(k) for k in ("job_valid", "train_valid", "metrics_basis", "be_check", "m_S4", "m_S8", "m8_gate05", "gate05_dt_ok", "m8_iti6", "m8_itiS", "m8_gate05_t7", "m8_gate05_off", "m8_iti6_off", "m8_phase8_gate", "phase8_gate_GlobalTimeStep", "final_L", "dyn_now_min_step", "wall_total_s")}, default=str))
log("JOB_DONE")
