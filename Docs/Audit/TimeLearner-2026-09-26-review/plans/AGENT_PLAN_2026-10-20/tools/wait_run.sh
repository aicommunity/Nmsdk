#!/usr/bin/env bash
# Wait for a queue RUN_ID to finish (checks every 10 min, gives up after MAX_H hours, default 48), then summarize.
# Usage: wait_run.sh <RUN_ID> <REPORT_SUBDIR>
set -u
RUN_ID="${1:?run id}"; SUB="${2:?report subdir}"; MAX_H="${MAX_H:-48}"
EXITF="$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit"; DIR=$(cd "$(dirname "$0")" && pwd)
t=0
while [ ! -f "$EXITF" ]; do
  sleep 600; t=$((t+600))
  if [ $t -ge $((MAX_H*3600)) ]; then echo "TIMEOUT_WAITING $RUN_ID (still running? check tmux ls / pgrep)"; exit 3; fi
done
OUT="$REPORTS/$SUB/$RUN_ID"; mkdir -p "$OUT"
qex="$(tr -d '[:space:]' < "$EXITF" 2>/dev/null || true)"
case "$qex" in
  ''|*[!0-9]*) echo "STOP: bad launch.exit content for $RUN_ID: '$qex'" | tee "$OUT/queue_exit.txt"; exit 2 ;;
esac
echo "queue_exit=$qex" | tee "$OUT/queue_exit.txt"
python3 "$DIR/summarize_run.py" "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID" --json "$OUT/summary.json" | tee "$OUT/summary.tsv"
sha256sum "$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log" > "$OUT/launch_log.sha256"
printf '%s\t%s\tdone\tqueue_exit=%s\n' "$RUN_ID" "$(hostname)" "$qex" >> "$REPORTS/ASSIGNMENTS.tsv"
# DEBT-G1-exit-gate: presence of launch.exit is not success — propagate nonzero queue rc.
if [ "$qex" -ne 0 ]; then
  echo "STOP: launch.exit=$qex for $RUN_ID (drv must not treat as green)"
  exit "$qex"
fi
