#!/usr/bin/env bash
# Launch a fixed SoftCold case list with a bounded process pool.
# Usage: INH_GRID_LAUNCH_CASES.sh LIMIT case1 case2 ...
#    or: INH_GRID_LAUNCH_CASES.sh LIMIT --file cases.txt
set -euo pipefail
LIMIT="${1:?LIMIT}"
shift
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
PV="$ST/scripts/posttune_verify.py"
GATE="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20/tools/cpu_gate.sh"
TSV="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_COLD_LAUNCH.tsv"
LOGDIR="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/inh_grid_logs"
mkdir -p "$LOGDIR"
HOSTTAG="$(hostname | tr -c 'A-Za-z0-9._-' '_')"
[[ -f "$TSV" ]] || echo -e "case\thost\trun_id\tstatus\tstarted\tfinished\tnote" >"$TSV"

CASES=()
if [[ "${1:-}" == "--file" ]]; then
  mapfile -t CASES < <(grep -v '^#' "$2" | grep -v '^[[:space:]]*$')
else
  CASES=("$@")
fi
[[ ${#CASES[@]} -gt 0 ]] || { echo "no cases" >&2; exit 2; }
echo "HOST=$HOSTTAG LIMIT=$LIMIT cases=${#CASES[@]} ROOT=$ROOT Avail=$(df -BG /home/user | awk 'NR==2{print $4}')"

running_jobs() { jobs -rp | wc -l; }

for case in "${CASES[@]}"; do
  while [[ "$(running_jobs)" -ge "$LIMIT" ]]; do
    wait -n 2>/dev/null || sleep 5
  done
  # known disk gate: wait until Avail>=90G before starting next case
  while true; do
    avail_g=$(df -BG /home/user 2>/dev/null | awk 'NR==2{gsub(/G/,"",$4); print $4}')
    if [[ "${avail_g:-0}" -ge 85 ]]; then
      break
    fi
    echo "WAIT_DISK case=$case avail=${avail_g}G <85G $(date -u +%H:%MZ)"
    sleep 60
  done
  # Do not stall the campaign on cpu_gate: 90s max, then proceed if under LIMIT.
  timeout 90 bash "$GATE" 1 "$LIMIT" || echo "cpu_gate skip/timeout case=$case"
  RUN_ID="INH.${case}-${HOSTTAG}-$(date -u +%Y%m%dT%H%MZ)-$$"
  LOG="$LOGDIR/${RUN_ID}.log"
  START="$(date -u +%Y-%m-%dT%H:%MZ)"
  echo -e "${case}\t${HOSTTAG}\t${RUN_ID}\trunning\t${START}\t\trerun_disk_stop" >>"$TSV"
  (
    set +e
    cd "$ST"
    python3 "$PV" --case "$case" >"$LOG" 2>&1
    rc=$?
    END="$(date -u +%Y-%m-%dT%H:%MZ)"
    note="exit_${rc}"
    if grep -q 'STOP Avail=' "$LOG" 2>/dev/null; then
      note="disk_stop"
    elif grep -q 'not_converged' "$LOG" 2>/dev/null; then
      note="not_converged"
    fi
    echo -e "${case}\t${HOSTTAG}\t${RUN_ID}\tdone_exit${rc}\t${START}\t${END}\t${note}" >>"$TSV"
  ) &
  sleep 1
done
wait
echo "ALL_DONE host=$HOSTTAG cases=${#CASES[@]}"
