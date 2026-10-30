import sys, shutil, subprocess, time, csv, hashlib, os
from pathlib import Path
sys.path.insert(0, os.path.expanduser("~/Nmsdk/Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools"))
sys.path.insert(0, os.path.expanduser("~/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/scripts"))
from c1_dose_response_console import apply_trial_order
from repro_cold_lib import set_tag, get_tag
out = Path(sys.argv[1]); maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 7
console = os.path.expanduser("~/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole")
W = Path("/home/user/TLAgent-20261020/runs/W1_sim_k2_20261024T1830Z/work")
SRC = {"simk2": W/"br25sim_k2_20261024T183005Z_1170354_0b2b9da6_work",
       "ctrlbr25": W/"br25_nextseg_20261024T183525Z_1179425_1007f080_work"}
ROT4=[4,5,6,7,0,1,2,3]; TLAST=[1,2,3,4,5,6,7,0]
jobs = [("simk2","ref",None,True),("simk2","tpos4",ROT4,True),("simk2","tlast",TLAST,True),
        ("simk2","nsoff",None,False),("simk2","nsoff_tpos4",ROT4,False),
        ("ctrlbr25","tpos4",ROT4,True),("ctrlbr25","tlast",TLAST,True)]
procs = {}
for src, name, perm, ns in jobs:
    key = f"{src}_{name}"; d = out/key
    shutil.copytree(SRC[src]/"Test", d/"Test", ignore=shutil.ignore_patterns("SelectivityLog","EventsLog","StatisticLog","*.log"))
    if perm: apply_trial_order(d/"Test"/"Parameters_00.xml", perm)
    if not ns:
        for rel in ("Parameters_00.xml","Model_00.xml"):
            p = d/"Test"/rel; t = p.read_text(encoding="utf-8", errors="replace")
            p.write_text(set_tag(t,"EnableNextSegmentInhibition","0",0), encoding="utf-8")
    t = (d/"Test"/"Parameters_00.xml").read_text(encoding="utf-8", errors="replace")
    m = (d/"Test"/"Model_00.xml").read_text(encoding="utf-8", errors="replace")
    print(key, "classes", " ".join(get_tag(t,"MatrixClasses").split()), "nsP", get_tag(t,"EnableNextSegmentInhibition"), "nsM", get_tag(m,"EnableNextSegmentInhibition"), flush=True)
    while int(subprocess.run("pgrep -c -f NeuroModelerConsole", shell=True, capture_output=True, text=True).stdout.strip() or 0) >= maxc: time.sleep(15)
    f = open(d/"console.log","w")
    procs[key] = subprocess.Popen([console,"-c",str(d/"Test"/"Project.ini"),"-s","-t","40","-x"], stdout=f, stderr=subprocess.STDOUT)
    time.sleep(2)
for key, p in procs.items():
    try: rc = p.wait(timeout=1800)
    except subprocess.TimeoutExpired: p.kill(); rc = 124
    r = out/key/"Test"/"SelectivityLog"/"results.csv"
    if not r.is_file(): print("DONE", key, rc, "NO_RESULTS", flush=True); continue
    rows = list(csv.DictReader(r.open()))
    tg=[float(x["ltz_potential_max"]) for x in rows if x["target_class"]=="1"]; fo=[float(x["ltz_potential_max"]) for x in rows if x["target_class"]=="0"]
    fo1=[float(x["ltz_potential_max"]) for x in rows if x["target_class"]=="0" and x["trial"]!="0"]
    sep=(min(tg)-max(fo))/min(tg); sep1=(min(tg)-max(fo1))/min(tg)
    print("DONE", key, rc, hashlib.md5(r.read_bytes()).hexdigest()[:8], "sep=%.4f sep_excl0=%.4f"%(sep,sep1), " ".join(f"{x['trial']}:{x['target_class']}:{x['neuron_fired']}:{float(x['ltz_potential_max']):.4f}" for x in rows), flush=True)
print("ALL_DONE")
