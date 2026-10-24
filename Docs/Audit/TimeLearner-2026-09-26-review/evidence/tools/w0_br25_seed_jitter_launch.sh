#!/usr/bin/env bash
# W0 stability: SoftCold br25_nextseg with TipR tip-channel jitter.
# SoftCold is deterministic (bit-identical results.csv on plain repeats);
# tip jitter is the practical seed/input perturbation for a sep_margin distribution.
#
# Usage: w0_br25_seed_jitter_launch.sh [LIMIT]
set -euo pipefail

NMSDK_ROOT="${NMSDK_ROOT:-/home/user/Nmsdk}"
ST="$NMSDK_ROOT/Bin/Configs/SpikeSamples/StructTrain"
PV="$ST/scripts/posttune_verify.py"
SRC="$ST/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9"
RUNS_ROOT="${RUNS_ROOT:-/home/user/TLAgent-20261020/runs}"
EV="$NMSDK_ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence"
LOGDIR="$EV/w0_br25_nextseg_logs"
TSV="$EV/W0_BR25_NEXTSEG_LAUNCH.tsv"
REG="$EV/RUN_REGISTRY/runs.tsv"
LIMIT="${1:-5}"
KEEP_FREE="${KEEP_FREE:-2}"
HOST_CAP=8
MAX_SLOTS=$((HOST_CAP - KEEP_FREE))
[[ "$LIMIT" -le "$MAX_SLOTS" ]] || LIMIT="$MAX_SLOTS"

JITTERS=(-0.03 -0.02 -0.01 0.01 0.02)

mkdir -p "$LOGDIR" "$RUNS_ROOT"
[[ -f "$TSV" ]] || echo -e "rep\trun_id\tstatus\tstarted\tfinished\tnote" >"$TSV"

running_consoles() { pgrep -c -f NeuroModelerConsole 2>/dev/null || echo 0; }
bg_jobs() { jobs -rp | wc -l; }

patch_tipr() {
  local root="$1" scale="$2"
  python3 - "$root" "$scale" "$ST/scripts" <<'PY'
import sys
from pathlib import Path
root = Path(sys.argv[1])
scale = float(sys.argv[2])
sys.path.insert(0, sys.argv[3])
from repro_cold_lib import get_tag, set_tag
for side in ("Train", "Test"):
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = root / side / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        tip = get_tag(t, "TipSynapseResistance")
        if not tip:
            continue
        vals = [float(x) for x in tip.split()]
        vals[-1] = vals[-1] * scale
        new = " ".join(f"{v:.17g}" for v in vals)
        t = set_tag(t, "TipSynapseResistance", new, 1)
        p.write_text(t, encoding="utf-8")
        print(f"patched {p} TipR -> {new}")
PY
}

run_one() {
  local idx="$1" j="$2" scale="$3" arch="$4" log="$5"
  python3 - "$PV" "$arch" <<'PY' >>"$log" 2>&1
import importlib.util
import sys
from pathlib import Path

pv_path = Path(sys.argv[1])
arch = Path(sys.argv[2]).resolve()
spec = importlib.util.spec_from_file_location("posttune_verify", pv_path)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)
c = dict(mod.CASES["br25_nextseg"])
c["root"] = arch
c["gold"] = arch
mod.CASES["br25_nextseg"] = c
print(f"W0_SEED SoftCold root={arch}", flush=True)
row = mod.run_case("br25_nextseg")
print("W0_SEED_ROW", {k: row.get(k) for k in ("verdict", "result", "acc", "fires", "workdir") if k in row or True}, flush=True)
PY
}

idx=0
for j in "${JITTERS[@]}"; do
  while [[ "$(bg_jobs)" -ge "$LIMIT" ]]; do wait -n 2>/dev/null || sleep 5; done
  while [[ "$(running_consoles)" -ge "$MAX_SLOTS" ]]; do sleep 20; done

  idx=$((idx + 1))
  scale=$(python3 -c "print(f'{1.0+(${j}):.8f}')")
  TS=$(date -u +%Y%m%dT%H%MZ)
  RUN_ID="W0.br25_nextseg.seed${idx}.j${j}-${TS}-$$"
  ARCH="$RUNS_ROOT/br25_nextseg_seed${idx}_j${j}_${TS}_tmpl"
  LOG="$LOGDIR/${RUN_ID}.log"
  START=$(date -u +%Y-%m-%dT%H:%MZ)

  rm -rf "$ARCH"
  mkdir -p "$ARCH"
  cp -a "$SRC/Train" "$SRC/Test" "$ARCH/"
  : >"$LOG"
  patch_tipr "$ARCH" "$scale" | tee -a "$LOG"

  echo -e "${idx}\t${RUN_ID}\trunning\t${START}\t\tjitter_tip=${j};scale=${scale};arch=${ARCH}" >>"$TSV"
  if [[ -f "$REG" ]]; then
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$RUN_ID" "Elder-1" "br25_nextseg" "W0_seed" "active" "$ARCH" "" "" "" "$START" \
      "TipR_tip_jitter=${j}" >>"$REG"
  fi

  (
    set +e
    run_one "$idx" "$j" "$scale" "$ARCH" "$LOG"
    rc=$?
    END=$(date -u +%Y-%m-%dT%H:%MZ)
    note="exit_${rc};jitter_tip=${j};scale=${scale}"
    grep -q 'not_converged' "$LOG" 2>/dev/null && note="${note};not_converged"
    echo -e "${idx}\t${RUN_ID}\tdone_exit${rc}\t${START}\t${END}\t${note}" >>"$TSV"
  ) &
  sleep 2
done

echo "LAUNCHED ${#JITTERS[@]} TipR-jitter SoftCold jobs LIMIT=$LIMIT MAX_SLOTS=$MAX_SLOTS"
