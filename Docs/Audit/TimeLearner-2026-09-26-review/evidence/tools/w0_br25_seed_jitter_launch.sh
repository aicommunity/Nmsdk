#!/usr/bin/env bash
# W0 stability SoftCold with TipR tip-channel jitter applied AFTER soft_cold_reset_train
# (plain TipR patch on archive is wiped by SoftCold → bit-identical runs).
set -euo pipefail
NMSDK_ROOT="${NMSDK_ROOT:-/home/user/Nmsdk}"
ST="$NMSDK_ROOT/Bin/Configs/SpikeSamples/StructTrain"
SRC="$ST/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9"
RUNS_ROOT="${RUNS_ROOT:-/home/user/TLAgent-20261020/runs}"
EV="$NMSDK_ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence"
LOGDIR="$EV/w0_br25_nextseg_logs"
TSV="$EV/W0_BR25_NEXTSEG_LAUNCH.tsv"
REG="$EV/RUN_REGISTRY/runs.tsv"
LIMIT="${1:-5}"
KEEP_FREE="${KEEP_FREE:-2}"
MAX_SLOTS=$((8 - KEEP_FREE))
[[ "$LIMIT" -le "$MAX_SLOTS" ]] || LIMIT="$MAX_SLOTS"
JITTERS=(-0.03 -0.02 -0.01 0.01 0.02)
mkdir -p "$LOGDIR" "$RUNS_ROOT"
[[ -f "$TSV" ]] || echo -e "rep\trun_id\tstatus\tstarted\tfinished\tnote" >"$TSV"

running_consoles() { pgrep -c -f NeuroModelerConsole 2>/dev/null || echo 0; }

idx=0
for j in "${JITTERS[@]}"; do
  while [[ "$(jobs -rp | wc -l)" -ge "$LIMIT" ]]; do wait -n 2>/dev/null || sleep 5; done
  while [[ "$(running_consoles)" -ge "$MAX_SLOTS" ]]; do sleep 20; done
  idx=$((idx + 1))
  scale=$(python3 -c "print(f'{1.0+(${j}):.8f}')")
  TS=$(date -u +%Y%m%dT%H%MZ)
  RUN_ID="W0.br25_nextseg.seed${idx}.j${j}-${TS}-$$"
  LOG="$LOGDIR/${RUN_ID}.log"
  START=$(date -u +%Y-%m-%dT%H:%MZ)
  echo -e "${idx}\t${RUN_ID}\trunning\t${START}\t\tpost_reset_tip_jitter=${j};scale=${scale}" >>"$TSV"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t\t\t\t%s\t%s\n' \
    "$RUN_ID" Elder-1 br25_nextseg W0_seed active "(workdir via SoftCold)" "$START" \
    "post_reset_TipR_tip_jitter=${j}" >>"$REG"
  (
    set +e
    runner=$(mktemp /tmp/w0_seed_run.XXXXXX.py)
    cat >"$runner" <<PY
import sys
from pathlib import Path
sys.path.insert(0, "$ST/scripts")
import posttune_verify as mod
from repro_cold_lib import get_tag, set_tag

scale = float("$scale")
j = float("$j")

_orig = mod.soft_cold_reset_train

def soft_cold_then_jitter(train, **kw):
    _orig(train, **kw)
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = Path(train) / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        tip = get_tag(t, "TipSynapseResistance")
        if not tip:
            continue
        vals = [float(x) for x in tip.replace(",", " ").split()]
        vals[-1] = vals[-1] * scale
        new = " ".join(f"{v:.17g}" for v in vals)
        t = set_tag(t, "TipSynapseResistance", new, 1)
        p.write_text(t, encoding="utf-8")
        print(f"POST_RESET_JITTER j={j} scale={scale} {p.name} TipR -> {new}", flush=True)

mod.soft_cold_reset_train = soft_cold_then_jitter
print(f"W0_SEED SoftCold + post-reset tip jitter j={j}", flush=True)
row = mod.run_case("br25_nextseg")
print("W0_SEED_ROW", {k: row.get(k) for k in ("verdict", "result", "acc", "fires", "workdir", "run_dir")}, flush=True)
PY
    cd "$ST"
    python3 "$runner" >"$LOG" 2>&1
    rc=$?
    rm -f "$runner"
    END=$(date -u +%Y-%m-%dT%H:%MZ)
    echo -e "${idx}\t${RUN_ID}\tdone_exit${rc}\t${START}\t${END}\texit_${rc};post_reset_tip_jitter=${j};scale=${scale}" >>"$TSV"
  ) &
  sleep 3
done
echo "LAUNCHED ${#JITTERS[@]} post-reset TipR-jitter SoftCold LIMIT=$LIMIT"
wait || true
echo ALL_DONE_W0_SEEDS
