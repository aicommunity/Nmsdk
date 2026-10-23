#!/usr/bin/env bash
# Launch InhGrid SoftCold with a bounded process pool.
# Usage: INH_GRID_LAUNCH.sh classic|branch [LIMIT]
set -euo pipefail
ROLE="${1:?classic|branch}"
LIMIT="${2:-}"
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
PV="$ST/scripts/posttune_verify.py"
GATE="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20/tools/cpu_gate.sh"
TSV="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_COLD_LAUNCH.tsv"
LOGDIR="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/inh_grid_logs"
mkdir -p "$LOGDIR"
HOSTTAG="$(hostname | tr -c 'A-Za-z0-9._-' '_')"
if [[ "$ROLE" == "classic" ]]; then
  LIMIT="${LIMIT:-8}"
  PREFIX="inh_c"
elif [[ "$ROLE" == "branch" ]]; then
  LIMIT="${LIMIT:-12}"
  PREFIX="inh_b"
else
  echo "usage: $0 classic|branch [LIMIT]" >&2
  exit 2
fi
[[ -f "$TSV" ]] || echo -e "case\thost\trun_id\tstatus\tstarted\tfinished\tnote" >"$TSV"
mapfile -t CASES < <(python3 - <<PY
import sys
sys.path.insert(0, "$ST/scripts")
import posttune_verify as pv
print("\n".join(sorted(k for k in pv.CASES if k.startswith("$PREFIX"))))
PY
)
echo "ROLE=$ROLE LIMIT=$LIMIT cases=${#CASES[@]} ROOT=$ROOT"

running_jobs() { jobs -rp | wc -l; }

for case in "${CASES[@]}"; do
  while [[ "$(running_jobs)" -ge "$LIMIT" ]]; do
    wait -n 2>/dev/null || sleep 5
  done
  bash "$GATE" 1 "$LIMIT" || true
  RUN_ID="INH.${case}-${HOSTTAG}-$(date -u +%Y%m%dT%H%MZ)-$$"
  LOG="$LOGDIR/${RUN_ID}.log"
  START="$(date -u +%Y-%m-%dT%H:%MZ)"
  echo -e "${case}\t${HOSTTAG}\t${RUN_ID}\trunning\t${START}\t\t" >>"$TSV"
  (
    set +e
    cd "$ST"
    python3 "$PV" --case "$case" >"$LOG" 2>&1
    rc=$?
    END="$(date -u +%Y-%m-%dT%H:%MZ)"
    note="exit_${rc}"
    grep -q 'not_converged' "$LOG" 2>/dev/null && note="not_converged"
    echo -e "${case}\t${HOSTTAG}\t${RUN_ID}\tdone_exit${rc}\t${START}\t${END}\t${note}" >>"$TSV"
  ) &
  sleep 1
done
wait
echo "ALL_DONE ROLE=$ROLE host=$HOSTTAG"
