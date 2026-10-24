#!/usr/bin/env python3
"""E0 (plan 2026-10-25 dendrite limits): Console Branch kernel probe vs discrete chain theory.

Test-only, dt=0.5 ms (DefaultTimeStep 2000). Dendrite 0 has L segments and gets the only
early stimulus (t=2 ms); dendrites 1..3 (L=1) get late stimuli (1.0-1.1 s); soma_0 (dendrite 0 only) is analysed.
Measures soma_sum peak time / amplitude / FWHM in [0, 1.1 s] and compares with the
discrete chain kernel h = conv^L of a(1-a)^n, a = dt/tau (segsim formulation).
Private console via NMSDK_CONSOLE. Writes OUT/e0_summary.tsv.
"""
import os, sys, csv, json, re, shutil, subprocess, time
from pathlib import Path
NM = Path(os.environ.get("NMREPO", str(Path.home() / "Nmsdk")))
ST = NM / "Bin/Configs/SpikeSamples/StructTrain"
sys.path.insert(0, str(ST / "scripts"))
from repro_cold_lib import get_tag, set_tag, set_tag_all, ensure_tag_after, enable_pattern_response_trace
CONSOLE = os.environ.get("NMSDK_CONSOLE", str(NM / "Bin/Platform/Linux/NeuroModelerConsole"))
TPL = ST / "SelectivityTauCm/EXP_branch_S100_gen_TauH0/Test"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "e05_runs/E0"))
STEP = int(os.environ.get("E0_STEP", "2000"))
DT = 1.0 / STEP
RM = 1e7
CASES = [(c, L) for c in (2.5e-10, 1e-10, 7.5e-11) for L in (1, 50, 200, 400)]
if os.environ.get("E0_CASES"):
    CASES = [tuple(json.loads(x)) for x in os.environ["E0_CASES"].split(";")]
WIN = 0.98
T0 = 0.005

TIPR0 = os.environ.get("E0_TIPR0", "20000000")  # dendrite-0 tip Rs; 1e15 = reference run (no d0 input)
TIPR_REST = os.environ.get("E0_TIPR_REST", "20000000")  # tip Rs of dendrites 1..3; 1e15 = silence them
EXTRA = json.loads(os.environ.get("E0_EXTRA", "{}"))  # e.g. {"OverrideInhSynapseResistance": 1e15} = inhibition off


def prep(d, cap, L):
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(TPL, d, ignore=shutil.ignore_patterns("SelectivityLog", "EventsLog", "ltz_sweep", ".cache", "*.flag", "posttune_mid_dbg.txt"))
    (d / "SelectivityLog").mkdir()
    ini = (d / "Project.ini").read_text()
    ini = re.sub(r"<DefaultTimeStep>\d+</DefaultTimeStep>", f"<DefaultTimeStep>{STEP}</DefaultTimeStep>", ini)
    ini = re.sub(r"<GlobalTimeStep>\d+</GlobalTimeStep>", f"<GlobalTimeStep>{STEP}</GlobalTimeStep>", ini)
    (d / "Project.ini").write_text(ini)
    samples = "\n".join(["0.00208333\n1.0\n0.05\n0.05"] * 8)  # col0 offset, then ISIs: stims 0, 1.0, 1.05, 1.1 s
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = d / rel
        t = p.read_text(encoding="utf-8", errors="replace")
        t = re.sub(r'(<MatrixData Type="MDMatrix&lt;d&gt;" Rows="32" Cols="1"[^>]*>)[^<]*(</MatrixData>)', lambda m: m.group(1) + samples + m.group(2), t)
        for name, val in (("IsNeedToTrain", "0"), ("StructureBuildMode", "1"), ("DendriteLength", f"{L} 1 1 1"),
                          ("TipSynapseResistance", f"{TIPR0} {TIPR_REST} {TIPR_REST} {TIPR_REST}"), ("MaxDendriteLength", "450"),
                          ):
            if name in ("StructureBuildMode",):
                t = set_tag(t, name, val, 1)
            else:
                t = set_tag_all(t, name, val)
        # LTZ thresholds left as in template: editing them aborts the Test phase (bisected 2026-10-25)
        for name, val in (("UseFixedLTZThreshold", "1"), ("AutoCalibrateFixedLTZThreshold", "0"), ("EnablePostTrainTuning", "0"), ("EnablePostTrainMidThreshold", "0")):
            if get_tag(t, name) is not None:
                t = set_tag(t, name, val, 1)
        if abs(cap - 2.5e-10) > 1e-16 and get_tag(t, "EnableDebug") is not None:
            t = ensure_tag_after(t, "EnableDebug", "OverrideMembraneCapacity", repr(cap), ' Type="d" PType="257" IoType="17"')
        for k, v in EXTRA.items():
            t = ensure_tag_after(t, "EnableDebug", k, repr(v), ' Type="d" PType="257" IoType="17"')
        t = set_tag(t, "EnableDebug", "0", 1) if get_tag(t, "EnableDebug") is not None else t
        p.write_text(t, encoding="utf-8")
    enable_pattern_response_trace(d / "Model_00.xml")

def run(d, wall=900):
    log = d / "console.log"
    t0 = time.time()
    with log.open("w") as fh:
        pr = subprocess.Popen([CONSOLE, "-c", str(d / "Project.ini"), "-s", "-t", "4", "-x", "-S"], cwd=str(d), stdout=fh, stderr=subprocess.STDOUT)
    err = ""
    while pr.poll() is None:
        if time.time() - t0 > wall:
            err = "wall"; pr.terminate(); break
        tr = sorted(d.rglob("test_trace.csv"))
        if tr:
            try:
                with tr[0].open() as f:
                    n = sum(1 for _ in f)
                if n > int(1.8 / DT):  # sample 0 complete
                    time.sleep(2); 
                    if pr.poll() is None:
                        err = "term_trace_done"; pr.terminate()
                    break
            except OSError:
                pass
        time.sleep(1)
    try:
        pr.wait(timeout=30)
    except subprocess.TimeoutExpired:
        pr.kill(); pr.wait()
    return err, round(time.time() - t0, 1)

def analyze(d):
    tr = sorted(d.rglob("test_trace.csv"))
    if not tr:
        return None
    ts, vs = [], []
    with tr[0].open() as f:
        hdr = f.readline().strip().split(",")
        for line in f:
            p = line.strip().split(",")
            if len(p) != len(hdr):
                continue
            r = dict(zip(hdr, p))
            if int(float(r.get("sample_id", 0))) != 0:
                break
            t = float(r["time_rel_s"])
            if t > WIN:
                break
            ts.append(t); vs.append(float(r["soma_sum"]))
    if not vs:
        return None
    early = [(t, x) for t, x in zip(ts, vs) if t <= T0]
    v = [(t, x) for t, x in zip(ts, vs) if t > T0]
    if not v:
        return None
    kmax = max(range(len(v)), key=lambda i: v[i][1]); kmin = min(range(len(v)), key=lambda i: v[i][1])
    k = kmax if abs(v[kmax][1]) >= abs(v[kmin][1]) else kmin
    pk = v[k][1]; half = pk / 2
    idx = [i for i in range(len(v)) if (v[i][1] >= half if pk > 0 else v[i][1] <= half)]
    return {"t_peak_ms": v[k][0] * 1000, "peak": pk, "fwhm_ms": (v[idx[-1]][0] - v[idx[0]][0]) * 1000 if idx else None,
            "pos_max": v[kmax][1], "t_pos_ms": v[kmax][0] * 1000, "neg_min": v[kmin][1], "t_neg_ms": v[kmin][0] * 1000,
            "early_min": min(x for _, x in early) if early else None, "early_max": max(x for _, x in early) if early else None, "n": len(ts)}

def theory(tau, L, nsteps):
    a = DT / tau
    h = [a * (1 - a) ** n for n in range(nsteps)]
    y = h[:]
    for _ in range(L - 1):
        z = [0.0] * nsteps
        acc = 0.0
        # recursive chain stage: z[n] = (1-a) z[n-1] + a y[n]
        for n in range(nsteps):
            acc = (1 - a) * acc + a * y[n]
            z[n] = acc
        y = z
    k = max(range(nsteps), key=lambda i: y[i]); half = y[k] / 2
    lo = next(i for i in range(nsteps) if y[i] >= half); hi = max(i for i in range(nsteps) if y[i] >= half)
    return {"t_peak_ms": k * DT * 1000, "peak_rel": y[k] / max(h), "fwhm_ms": (hi - lo) * DT * 1000}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for cap, L in CASES:
        name = f"C{cap:.3g}_L{L}"
        d = OUT / name
        prep(d, cap, L)
        err, wall = run(d)
        m = analyze(d) or {}
        tau = cap * RM
        th = theory(tau, L, int(WIN / DT))
        txt = (d / "console.log").read_text(errors="replace") + "".join(x.read_text(errors="replace") for x in (d / "EventsLog").glob("*INFO*"))
        ov = "|".join(sorted(set(re.findall(r"NeuronClassOverrides:[^\n]*", txt))))[:300]
        step = "5e-4" if re.search(r"0\.0005\b|5e-0?4", txt) else "?"
        r = {"case": name, "C": cap, "tau_ms": tau * 1000, "L": L, "err": err, "wall_s": wall,
             "t_peak_ms": m.get("t_peak_ms"), "peak": m.get("peak"), "fwhm_ms": m.get("fwhm_ms"), "pos_max": m.get("pos_max"), "t_pos_ms": m.get("t_pos_ms"), "neg_min": m.get("neg_min"), "t_neg_ms": m.get("t_neg_ms"), "early_min": m.get("early_min"), "early_max": m.get("early_max"), "step": STEP,
             "th_t_peak_ms": th["t_peak_ms"], "th_fwhm_ms": th["fwhm_ms"], "th_peak_rel": th["peak_rel"],
             "override_log": ov, "step_in_log": step}
        rows.append(r)
        print(json.dumps(r), flush=True)
    # relative to L=1 of same C
    for r in rows:
        base = next((x for x in rows if x["C"] == r["C"] and x["L"] == 1 and x.get("t_peak_ms") is not None), None)
        if base and r.get("t_peak_ms") is not None and r["L"] > 1:
            r["delay_per_seg_ms"] = (r["t_peak_ms"] - base["t_peak_ms"]) / (r["L"] - 1)
            r["th_delay_per_seg_ms"] = (r["th_t_peak_ms"] - next(x for x in rows if x["C"] == r["C"] and x["L"] == 1)["th_t_peak_ms"]) / (r["L"] - 1)
            r["amp_ratio_vs_L1"] = r["peak"] / base["peak"] if base["peak"] else None
    cols = ["case", "step", "C", "tau_ms", "L", "t_peak_ms", "th_t_peak_ms", "delay_per_seg_ms", "th_delay_per_seg_ms", "fwhm_ms", "th_fwhm_ms", "peak", "amp_ratio_vs_L1", "th_peak_rel", "pos_max", "t_pos_ms", "neg_min", "t_neg_ms", "early_min", "early_max", "err", "wall_s", "step_in_log", "override_log"]
    with (OUT / "e0_summary.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore"); w.writeheader(); [w.writerow(r) for r in rows]
    print("E0_DONE", flush=True)

if __name__ == "__main__":
    main()
