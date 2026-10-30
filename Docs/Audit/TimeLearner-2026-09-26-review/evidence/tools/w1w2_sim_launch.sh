#!/usr/bin/env bash
# PLAN 2026-10-25 W1/W2 (Q1 H-sim): SoftCold training of the br25 nextseg template
# scaled x k in ALL time quantities (w1w2_sim_template.py), vs naive brNN_nextseg
# and br25 control. Seeds = post-reset TipR tip jitter (as W0).
# usage: w1w2_sim_launch.sh <wave_tag> <limit> <job>...   job = label:case:k:jitter
#   case = sim (template x k, class Sim{k}) | any posttune_verify CASES key
set -uo pipefail
NMSDK_ROOT="${NMSDK_ROOT:-$HOME/Nmsdk}"
ST="$NMSDK_ROOT/Bin/Configs/SpikeSamples/StructTrain"
EV="$NMSDK_ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence"
RUNS_ROOT="${RUNS_ROOT:?set RUNS_ROOT}"
HOST_TAG="${HOST_TAG:-$(hostname)}"
WAVE="$1"; LIMIT="$2"; shift 2
KEEP_FREE="${KEEP_FREE:-2}"
MAX_SLOTS=$(( $(nproc) - KEEP_FREE ))
[[ "$LIMIT" -le "$MAX_SLOTS" ]] || LIMIT="$MAX_SLOTS"
OUT="$RUNS_ROOT/${WAVE}"
LOGDIR="$OUT/logs"; TSV="$OUT/launch.tsv"; REG="$EV/RUN_REGISTRY/runs.tsv"
mkdir -p "$LOGDIR" "$OUT/templates"
[[ -f "$TSV" ]] || echo -e "label\tcase\tk\tjitter\tstatus\tstarted\tfinished\tlog" >"$TSV"
export TIMELEARNER_MATRIX_RUNS_ROOT="$OUT/work"
mkdir -p "$TIMELEARNER_MATRIX_RUNS_ROOT"

# fixed: pgrep -c prints 0 AND exits 1 -> old "|| echo 0" produced "0\n0"
running_consoles() { local n; n=$(pgrep -c -f 'NeuroModelerConsole' 2>/dev/null); echo "${n:-0}"; }

for spec in "$@"; do
  IFS=: read -r label case k j <<<"$spec"
  if [[ "$case" == sim && ! -d "$OUT/templates/simk$k" ]]; then
    python3 "$EV/tools/w1w2_sim_template.py" --k "$k" --out "$OUT/templates/simk$k" >"$LOGDIR/template_k$k.log" 2>&1 \
      || { echo "TEMPLATE_FAIL k=$k"; exit 2; }
  fi
done

for spec in "$@"; do
  IFS=: read -r label case k j <<<"$spec"
  while [[ "$(jobs -rp | wc -l)" -ge "$LIMIT" ]]; do wait -n 2>/dev/null || sleep 5; done
  while [[ "$(running_consoles)" -ge "$MAX_SLOTS" ]]; do sleep 20; done
  scale=$(python3 -c "print(f'{1.0+(${j}):.8f}')")
  TS=$(date -u +%Y%m%dT%H%MZ)
  RUN_ID="${WAVE}.${label}-${TS}-${HOST_TAG}"
  LOG="$LOGDIR/${label}.log"
  START=$(date -u +%Y-%m-%dT%H:%MZ)
  echo -e "${label}\t${case}\t${k}\t${j}\trunning\t${START}\t\t${LOG}" >>"$TSV"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t\t\t\t%s\t%s\n' "$RUN_ID" "$HOST_TAG" "$case" "$WAVE" active "$OUT" "$START" \
    "k=${k};post_reset_TipR_tip_jitter=${j}" >>"$REG"
  (
    runner=$(mktemp /tmp/w1w2_run.XXXXXX.py)
    cat >"$runner" <<PY
import sys
from pathlib import Path
sys.path.insert(0, "$ST/scripts")
import posttune_verify as mod
from repro_cold_lib import get_tag, set_tag
case = "$case"; k = float("$k"); scale = float("$scale"); j = float("$j")
if case == "sim":
    tpl = Path("$OUT/templates/simk$k")
    case = "br25sim_k$k"
    mod.CASES[case] = mod._case(tpl, train_t=320, span_ms=int(round(25 * k)), kind="branch")
_orig = mod.soft_cold_reset_train
def soft_cold_then_jitter(train, **kw):
    _orig(train, **kw)
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = Path(train) / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        for tag in ("NeuronClassName", "SyncTolerance", "EstDelayPerSeg", "MembraneCapacity"):
            print("POST_RESET_CHECK", p.name, tag, get_tag(t, tag), flush=True)
        tip = get_tag(t, "TipSynapseResistance")
        if not tip or j == 0.0:
            continue
        vals = [float(x) for x in tip.replace(",", " ").split()]
        vals[-1] = vals[-1] * scale
        new = " ".join(f"{v:.17g}" for v in vals)
        t = set_tag(t, "TipSynapseResistance", new, 1)
        p.write_text(t, encoding="utf-8")
        print(f"POST_RESET_JITTER j={j} {p.name} TipR -> {new}", flush=True)
mod.soft_cold_reset_train = soft_cold_then_jitter
print("W1W2 case", case, "k", k, "jitter", j, flush=True)
row = mod.run_case(case)
print("W1W2_ROW", {x: row.get(x) for x in ("verdict", "result", "acc", "fires", "workdir", "run_dir", "status")}, flush=True)
PY
    cd "$ST"
    python3 "$runner" >"$LOG" 2>&1
    rc=$?
    rm -f "$runner"
    END=$(date -u +%Y-%m-%dT%H:%MZ)
    echo -e "${label}\t${case}\t${k}\t${j}\tdone_exit${rc}\t${START}\t${END}\t${LOG}" >>"$TSV"
  ) &
  sleep 5
done
echo "LAUNCHED $# LIMIT=$LIMIT MAX_SLOTS=$MAX_SLOTS"
wait || true
echo ALL_DONE_W1W2
