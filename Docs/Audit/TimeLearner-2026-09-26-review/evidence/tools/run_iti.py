import sys, shutil, subprocess, time, csv, hashlib, re, os, json
from pathlib import Path
NM = Path(os.environ.get("NMREPO", os.path.expanduser("~/Nmsdk")))
sys.path.insert(0, str(NM/"Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools"))
sys.path.insert(0, str(NM/"Bin/Configs/SpikeSamples/StructTrain/scripts"))
from c1_dose_response_console import apply_trial_order
from repro_cold_lib import set_tag
console = str(NM/"Bin/Platform/Linux/NeuroModelerConsole")
# usage: run_iti.py OUT JOBS.json ; job = [name, src_test_dir, perm|null, delay, ns_on(bool)]
out = Path(sys.argv[1]); jobs = json.load(open(sys.argv[2]))
procs = {}
for name, src, perm, dl, ns in jobs:
    d = out/name
    shutil.copytree(src, d/"Test", ignore=shutil.ignore_patterns("SelectivityLog","EventsLog","StatisticLog","*.log"))
    if perm: apply_trial_order(d/"Test"/"Parameters_00.xml", perm)
    for rel in ("Parameters_00.xml","Model_00.xml"):
        p = d/"Test"/rel; t = p.read_text(encoding="utf-8", errors="replace")
        t, n = re.subn(r'(<Delay Type="d" PType="257" IoType="17">)1\.5(</Delay>)', r'\g<1>%s\g<2>' % dl, t)
        if not ns: t = set_tag(t, "EnableNextSegmentInhibition", "0", 0)
        p.write_text(t, encoding="utf-8"); print(name, rel, "Delay_patched", n, flush=True)
    tsec = str(int(8*(float(dl)+0.05)+15))
    f = open(d/"console.log","w")
    procs[name] = subprocess.Popen([console,"-c",str(d/"Test"/"Project.ini"),"-s","-t",tsec,"-x"], stdout=f, stderr=subprocess.STDOUT)
    print("START", name, "tsec", tsec, flush=True); time.sleep(2)
for name, p in procs.items():
    try: rc = p.wait(timeout=5400)
    except subprocess.TimeoutExpired: p.kill(); rc = 124
    r = out/name/"Test"/"SelectivityLog"/"results.csv"
    if not r.is_file(): print("DONE", name, rc, "NO_RESULTS", flush=True); continue
    rows = list(csv.DictReader(r.open()))
    tg=[float(x["ltz_potential_max"]) for x in rows if x["target_class"]=="1"]; fo=[float(x["ltz_potential_max"]) for x in rows if x["target_class"]=="0"]
    sep=(min(tg)-max(fo))/min(tg) if tg and fo else float("nan")
    print("DONE", name, rc, hashlib.md5(r.read_bytes()).hexdigest()[:8], "sep=%.4f"%sep, "obs_end", [x["actual_observe_end"] for x in rows][:2], " ".join(f"{x['trial']}:{x['target_class']}:{x['neuron_fired']}:{float(x['ltz_potential_max']):.4f}" for x in rows), flush=True)
print("ALL_DONE")
