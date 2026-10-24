#!/usr/bin/env bash
# W0 stability: TipR tip-channel jitter on Test AFTER SoftCold (Train TipR converges
# and erases post-reset initial jitter — proven 2026-10-24 readback).
#
# Usage:
#   w0_br25_test_tipr_jitter.sh <softcold_work_or_run_dir> [LIMIT]
# SoftCold dir must contain Test/ with Model+Parameters TipR already finalized.
set -euo pipefail

NMSDK_ROOT="${NMSDK_ROOT:-/home/user/Nmsdk}"
CONSOLE="${NMSDK_CONSOLE:-$NMSDK_ROOT/Bin/Platform/Linux/NeuroModelerConsole}"
ST="$NMSDK_ROOT/Bin/Configs/SpikeSamples/StructTrain"
BASE_SRC="$ST/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9"
RUNS_ROOT="${RUNS_ROOT:-/home/user/TLAgent-20261020/runs}"
EV="$NMSDK_ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence"
LOGDIR="$EV/w0_br25_nextseg_logs"
TSV="$EV/W0_BR25_NEXTSEG_LAUNCH.tsv"
REG="$EV/RUN_REGISTRY/runs.tsv"
SRC_WORK="${1:?softcold work/run dir}"
LIMIT="${2:-5}"
KEEP_FREE="${KEEP_FREE:-2}"
MAX_SLOTS=$((8 - KEEP_FREE))
[[ "$LIMIT" -le "$MAX_SLOTS" ]] || LIMIT="$MAX_SLOTS"
read -r -a JITTERS <<<"${JITTERS_STR:--0.03 -0.02 -0.01 0.01 0.02}"
TSEC="${TSEC:-40}"
TIMEOUT="${TIMEOUT:-900}"

mkdir -p "$LOGDIR" "$RUNS_ROOT"
[[ -f "$TSV" ]] || echo -e "rep\trun_id\tstatus\tstarted\tfinished\tnote" >"$TSV"
[[ -d "$SRC_WORK/Test" ]] || { echo "ERROR: no Test/ in $SRC_WORK"; exit 2; }

running_consoles() { local n; n=$(pgrep -c -f NeuroModelerConsole 2>/dev/null); echo "${n:-0}"; }

idx=0
for j in "${JITTERS[@]}"; do
  while [[ "$(jobs -rp | wc -l)" -ge "$LIMIT" ]]; do wait -n 2>/dev/null || sleep 5; done
  while [[ "$(running_consoles)" -ge "$MAX_SLOTS" ]]; do sleep 15; done
  idx=$((idx + 1))
  scale=$(python3 -c "print(f'{1.0+(${j}):.8f}')")
  TS=$(date -u +%Y%m%dT%H%MZ)
  RUN_ID="W0.br25_nextseg.testjitter.seed${idx}.j${j}-${TS}-$$"
  OUT="$RUNS_ROOT/br25_nextseg_testjitter_seed${idx}_j${j}_${TS}"
  LOG="$LOGDIR/${RUN_ID}.log"
  START=$(date -u +%Y-%m-%dT%H:%MZ)
  echo -e "${idx}\t${RUN_ID}\trunning\t${START}\t\ttest_only_tip_jitter=${j};src=${SRC_WORK}" >>"$TSV"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t\t\t\t%s\t%s\n' \
    "$RUN_ID" Elder-1 br25_nextseg W0_testjitter active "$OUT" "$START" \
    "test_only_TipR_tip_jitter=${j};src=$(basename "$SRC_WORK")" >>"$REG"

  (
    set +e
    python3 - "$SRC_WORK" "$OUT" "$scale" "$j" "$CONSOLE" "$TSEC" "$TIMEOUT" "$BASE_SRC" "$LOG" <<'PY'
import hashlib, csv, json, shutil, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path("/home/user/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/scripts")))
from repro_cold_lib import get_tag, set_tag

src, out, scale, j, console, tsec, timeout, base_src, log_path = sys.argv[1:10]
src, out, base_src = Path(src), Path(out), Path(base_src)
scale, j = float(scale), float(j)
tsec, timeout = float(tsec), int(timeout)
log_path = Path(log_path)
log_path.parent.mkdir(parents=True, exist_ok=True)

def tipr(path: Path) -> str | None:
    if not path.is_file():
        return None
    return get_tag(path.read_text(encoding="utf-8", errors="replace"), "TipSynapseResistance")

def scale_tip(path: Path, scale: float) -> str:
    t = path.read_text(encoding="utf-8", errors="replace")
    tip = get_tag(t, "TipSynapseResistance")
    if not tip:
        raise SystemExit(f"no TipR in {path}")
    vals = [float(x) for x in tip.replace(",", " ").split()]
    vals[-1] *= scale
    new = " ".join(f"{v:.17g}" for v in vals)
    path.write_text(set_tag(t, "TipSynapseResistance", new, 0), encoding="utf-8")
    return new

def sep_margin(csv_path: Path):
    rows = list(csv.DictReader(csv_path.open()))
    tgt = [float(r["ltz_potential_max"]) for r in rows if r.get("target_class") == "1"]
    foil = [float(r["ltz_potential_max"]) for r in rows if r.get("target_class") == "0"]
    if not tgt or not foil:
        return None
    mn, mx = min(tgt), max(foil)
    return (mn - mx) / mn if abs(mn) > 1e-18 else None

if out.exists():
    shutil.rmtree(out)
out.mkdir(parents=True)
# Copy only Test side for inference
shutil.copytree(src / "Test", out / "Test", ignore=shutil.ignore_patterns(
    "StatisticLog", "EventsLog", "SelectivityLog", "*.log", "results.csv"
))

base_train = tipr(base_src / "Train" / "Model_00.xml")
base_test = tipr(base_src / "Test" / "Model_00.xml")
src_train = tipr(src / "Train" / "Model_00.xml") if (src / "Train" / "Model_00.xml").is_file() else tipr(src / "Train" / "Parameters_00.xml")
src_test_before = tipr(out / "Test" / "Model_00.xml")

new_model = scale_tip(out / "Test" / "Model_00.xml", scale)
new_params = scale_tip(out / "Test" / "Parameters_00.xml", scale)
src_test_after_m = tipr(out / "Test" / "Model_00.xml")
src_test_after_p = tipr(out / "Test" / "Parameters_00.xml")

readback = {
    "base_train_model_tipr": base_train,
    "base_test_model_tipr": base_test,
    "src_train_tipr": src_train,
    "test_tipr_before": src_test_before,
    "test_model_tipr_after": src_test_after_m,
    "test_params_tipr_after": src_test_after_p,
    "jitter": j,
    "scale": scale,
    "tipr_changed_vs_before": src_test_after_m != src_test_before,
    "tipr_changed_vs_base_test": src_test_after_m != base_test,
}
(out / "tipr_readback.json").write_text(json.dumps(readback, indent=2) + "\n", encoding="utf-8")
print("READBACK", json.dumps(readback), flush=True)
if not readback["tipr_changed_vs_before"]:
    raise SystemExit("READBACK_FAIL TipR unchanged after patch")

ini = out / "Test" / "Project.ini"
cmd = [console, "-c", str(ini), "-s", "-t", str(tsec), "-x"]
t0 = time.time()
with log_path.open("w") as f:
    f.write("CMD " + " ".join(cmd) + "\n")
    f.write("READBACK " + json.dumps(readback) + "\n")
    f.flush()
    try:
        p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
        rc = int(p.returncode)
    except subprocess.TimeoutExpired:
        f.write(f"\nTIMEOUT {timeout}s\n")
        rc = 124
et = round(time.time() - t0, 1)

# find results
cand = None
for c in (out / "Test" / "SelectivityLog" / "results.csv", out / "Test" / "results.csv"):
    if c.is_file():
        cand = c
        break
md5 = hashlib.md5(cand.read_bytes()).hexdigest() if cand else None
sep = sep_margin(cand) if cand else None
# baseline md5 from src if present
base_md5 = None
for c in (src / "Test" / "SelectivityLog" / "results.csv", src / "Test" / "results.csv"):
    if c.is_file():
        base_md5 = hashlib.md5(c.read_bytes()).hexdigest()
        break
differs = (md5 is not None and base_md5 is not None and md5 != base_md5)
summary = {
    "rc": rc,
    "elapsed_s": et,
    "results_md5": md5,
    "baseline_md5": base_md5,
    "results_differ_from_baseline": differs,
    "sep_margin": sep if differs else None,
    "sep_margin_raw": sep,
    "note": "sep_margin counted only when results.csv differs from SoftCold baseline",
}
(out / "jitter_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print("SUMMARY", json.dumps(summary), flush=True)
with log_path.open("a") as f:
    f.write("SUMMARY " + json.dumps(summary) + "\n")
raise SystemExit(0 if rc == 0 and differs else (1 if rc == 0 else rc))
PY
    rc=$?
    END=$(date -u +%Y-%m-%dT%H:%MZ)
    echo -e "${idx}\t${RUN_ID}\tdone_exit${rc}\t${START}\t${END}\texit_${rc};test_only_tip_jitter=${j};scale=${scale}" >>"$TSV"
  ) >>"$LOG" 2>&1 &
  sleep 2
done
echo "LAUNCHED ${#JITTERS[@]} Test-only TipR jitter jobs from $SRC_WORK LIMIT=$LIMIT"
