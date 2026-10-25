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
           be_transfer(default 0, EXPERIMENTAL - analyzer gives 0 rows): if C++ refused training, Test is still the template -> build OUT/be_Test from Train
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
from repro_cold_lib import get_tag, set_tag, set_tag_all, ensure_tag_after  # noqa
STEP = 2000
CONSOLE = os.environ.get("NMSDK_CONSOLE") or str(NM / "Bin/Platform/Linux/NeuroModelerConsole")
kind, span = SPEC["kind"], int(SPEC["span"])
mod, mode = SPEC.get("mod", "preinh"), SPEC.get("mode", "N1")
SRC = ST / "SelectivityTauCm" / f"EXP_{kind}_S{span}_{mod}_TauH0_{mode}"
TRAIN_T = {50: 640, 100: 1280}[span]
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
                  "OverrideExcSynapseResistance", "OverrideInhSynapseResistance", "DynamicsLogHead", "DynamicsLogEvery"):
            r[f"{rel[:-7]}.{k}"] = get_tag(t, k)
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
base_key = f"h0_{kind[0]}{span}_{mod}_{mode.lower()}_{SPEC.get('pt', 'pton')}"
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
def run_test(name, samples, classes, delay):
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
        p.write_text(t, encoding="utf-8")
    tsec = str(int(8 * (float(delay) + 0.05) + 15))
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
if work and (work / "Test" / "Parameters_00.xml").is_file():
    res["readback_train"] = readback(work / "Train"); res["readback_test"] = readback(work / "Test")
    res["final_L"] = get_tag((work / "Train" / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace"), "DendriteLength")
    res["test_L"] = get_tag((work / "Test" / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace"), "DendriteLength")
    ts = str(row.get("train_status") or "")
    res["train_valid"] = bool(ts) and not (ts.startswith("cpp_training") or "refus" in ts or "fail" in ts)
    res["test_is_trained"] = (res["test_L"] or "").split() == (res["final_L"] or "").split()
    TESTSRC = work / "Test"
    res["metrics_basis"] = "trained_test" if res["test_is_trained"] else "TEMPLATE_untrained"
    if not res["test_is_trained"] and int(SPEC.get("be_transfer", 0))  # default OFF: be_Test runs but PatternResponseAnalyzer writes no rows (overlay alone insufficient, needs phase9-style patching) - UNVERIFIED:
        # C++ refused -> posttune skipped the gate -> Test = template. Build a best-effort Test from the refused Train neuron.
        be = OUT / "be_Test"
        if be.exists():
            shutil.rmtree(be)
        shutil.copytree(work / "Test", be, ignore=shutil.ignore_patterns("SelectivityLog", "EventsLog", "StatisticLog", "*.log"))
        for rel in ("Parameters_00.xml", "Model_00.xml"):
            tr = (work / "Train" / rel).read_text(encoding="utf-8", errors="replace")
            te = (be / rel).read_text(encoding="utf-8", errors="replace")
            keep = {k: get_tag(te, k) for k in ("FixedLTZThreshold", "UseFixedLTZThreshold")}
            mn = re.search(r'(<Neuron Class="[^"]+">.*?</Neuron>)', tr, re.S)
            if mn:
                te, nsub = re.subn(r'<Neuron Class="[^"]+">.*?</Neuron>', lambda _m: mn.group(1), te, count=1, flags=re.S)
                log("BE_OVERLAY", rel, "neuron_block", nsub)
            # learner-level copies (as phase8 prepare_test): structure tags outside the Neuron block
            for k in ("NeuronClassName", "MembraneCapacity", "DendriteLength", "NumSynapse", "NormalizationMode", "NumDendriteMembranePartsVec",
                      "NumInputDendrite", "ResistanceMin", "ResistanceMax", "SynapseResistanceBase", "TipSynapseResistance"):
                v = get_tag(tr, k)
                if v is not None and get_tag(te, k) is not None:
                    te = set_tag_all(te, k, v)
            te = set_tag_all(te, "IsNeedToTrain", "0")
            for k, v in keep.items():
                if v is not None:
                    te = set_tag_all(te, k, v)
            (be / rel).write_text(te, encoding="utf-8")
        rbb = readback(be)
        res["be_readback"] = {k: rbb.get(k) for k in ("Parameters.DendriteLength", "Model.DendriteLength", "Model.TipSynapseResistance", "Model.MembraneCapacity", "Model.OverrideInhSynapseResistance")}
        if (rbb.get("Model.DendriteLength") or "").split() == (res["final_L"] or "").split():
            TESTSRC = be; res["metrics_basis"] = "BEST_EFFORT_refused_structure"
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
    for bn, batch in (("qA", A), ("qB", B)):
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
    perm = [3, tgt_i] + [i for i in range(8) if i not in (3, tgt_i)]
    rows, rb = run_test("iti6", [smp[i] for i in perm], [cls[i] for i in perm], "6.0")
    tg = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "1"]
    fo = [float(x["ltz_potential_max"]) for x in rows if x["target_class"] == "0"]
    res["iti6_perm"] = perm
    res["m8_iti6"] = (min(tg) - max(fo)) / min(tg) if tg and fo and min(tg) else None
    res["iti6_target_fired"] = [int(x["neuron_fired"]) for x in rows if x["target_class"] == "1"]
    res["iti6_foils_fired"] = sum(int(x["neuron_fired"]) for x in rows if x["target_class"] == "0")
    # gate05 (2026-10-25 02:30 MSK fix): phase8 gate forces Test GlobalTimeStep=20000 (dt 0.05 ms) -> m8_gate is NOT at dt 0.5 ms.
    # Re-run original samples at dt 0.5 ms (patch_ini), Delay 1.5, target at position 4 (not first).
    others = [i for i in range(8) if i != tgt_i]
    perm5 = others[:4] + [tgt_i] + others[4:]
    rows, rb = run_test("gate05", [smp[i] for i in perm5], [cls[i] for i in perm5], "1.5")
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
res["wall_total_s"] = round(time.time() - t0)
(OUT / "result.json").write_text(json.dumps(res, indent=1, default=str))
log("RESULT", json.dumps({k: res.get(k) for k in ("train_valid", "metrics_basis", "m_S4", "m_S8", "m8_gate05", "gate05_dt_ok", "m8_iti6", "m8_phase8_gate", "phase8_gate_GlobalTimeStep", "final_L", "dyn_now_min_step", "wall_total_s")}, default=str))
log("JOB_DONE")
