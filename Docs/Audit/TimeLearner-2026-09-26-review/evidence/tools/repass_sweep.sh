#!/usr/bin/env bash
# REPASS: re-test every historical trained Test dir at ITI=6s with trial-order control (ref + target at pos4)
set -uo pipefail
RUNS="$1"; BATCH="$2"; TAG="$3"
OUT="$RUNS/REPASS_ITI6_${TAG}_$(date -u +%Y%m%dT%H%MZ)"; mkdir -p "$OUT"
cd "$RUNS"
find . -maxdepth 5 -path '*_work/Test/Project.ini' 2>/dev/null | grep -v -e REPASS -e ITI_ctrl -e _h2_src | sed 's#/Test/Project.ini##' | sort > "$OUT/all_dirs.txt"
python3 - "$OUT" "$RUNS" "$BATCH" <<'PY'
import sys, json, re, os
out, runs, batch = sys.argv[1], sys.argv[2], int(sys.argv[3])
last = {}
for l in open(out + "/all_dirs.txt"):
    p = l.strip(); n = os.path.basename(p); c = re.sub(r"_20261.*", "", n)
    last[c] = p  # sorted -> keeps lexicographically last (latest ts within same parent)
jobs = []
for c, p in sorted(last.items()):
    src = os.path.normpath(os.path.join(runs, p, "Test"))
    jobs.append([c + "__ref", src, None, "6.0", True])
    jobs.append([c + "__tpos4", src, [4,5,6,7,0,1,2,3], "6.0", True])
json.dump(jobs, open(out + "/jobs_all.json", "w"), indent=0)
for i in range(0, len(jobs), batch):
    json.dump(jobs[i:i+batch], open(out + "/jobs_%03d.json" % (i // batch), "w"))
print("CASES", len(last), "JOBS", len(jobs))
PY
for j in "$OUT"/jobs_[0-9]*.json; do
  b=$(basename "$j" .json); mkdir -p "$OUT/$b"
  nice -n 5 python3 "$RUNS/run_iti.py" "$OUT/$b" "$j" > "$OUT/$b/launcher.log" 2>&1
  grep -h DONE "$OUT/$b/launcher.log" >> "$OUT/DONE_all.txt"
done
echo ALL_DONE_REPASS >> "$OUT/DONE_all.txt"
