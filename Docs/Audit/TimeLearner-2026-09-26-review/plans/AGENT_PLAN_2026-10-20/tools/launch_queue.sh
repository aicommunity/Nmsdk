#!/usr/bin/env bash
# Launch one queue call in tmux with a fresh RUN_ID (rules 00_RULES §3).  Prints the RUN_ID on the last line.
# Usage: launch_queue.sh <TASK> <WAVE> "<CASE1 CASE2 ...>" <JOBS> [extra queue flags...]
# Env: ST (StructTrain dir to run from), TIMELEARNER_MATRIX_RUNS_ROOT, REPORTS, HOSTTAG; optional NMSDK_CONSOLE, HOST_LIMIT (default 12)
set -u
TASK="${1:?task}"; WAVE="${2:?wave}"; CASES="${3:?cases}"; JOBS="${4:?jobs}"; shift 4
: "${ST:?ST unset}" "${TIMELEARNER_MATRIX_RUNS_ROOT:?}" "${REPORTS:?}" "${HOSTTAG:?}"
LIMIT="${HOST_LIMIT:-12}"
LOCK="$ST/_repro/.timelearner_matrix_queue.lock"
if [ -e "$LOCK" ]; then echo "LANE_BUSY: $LOCK exists ($(cat "$LOCK" 2>/dev/null)). Use another lane (tools/make_lane.sh) or wait. Never delete the lock."; exit 4; fi
DIR=$(cd "$(dirname "$0")" && pwd)
bash "$DIR/cpu_gate.sh" "$JOBS" "$LIMIT" >/dev/null
RUN_ID="$TASK-$HOSTTAG-$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
LOG="$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.log"; EXITF="$TIMELEARNER_MATRIX_RUNS_ROOT/$RUN_ID.launch.exit"
mkdir -p "$TIMELEARNER_MATRIX_RUNS_ROOT" "$REPORTS"

# Stage0 wiring preflight (best-effort)
if [ -f "$DIR/check_model_wiring.py" ]; then
  for c in $CASES; do
    for side in Train Test; do
      m=$(find "$ST/TimeLearnerMatrix/$WAVE/inputs/$c/$side" -name Model_00.xml 2>/dev/null | head -1)
      if [ -n "$m" ]; then
        python3 "$DIR/check_model_wiring.py" "$m" >"$TIMELEARNER_MATRIX_RUNS_ROOT/${RUN_ID}.wiring_${c}_${side}.txt" 2>&1 || \
          echo "WIRING_FAIL $RUN_ID $c $side" >> "$REPORTS/ASSIGNMENTS.tsv"
      fi
    done
  done
fi

CONS="${NMSDK_CONSOLE:-}"
EXTRA="$*"
printf '%s\t%s\t%s\t%s\t%s\tst=%s\tconsole=%s\textra=%s\trunning\n' "$RUN_ID" "$(hostname)" "$(date -u +%FT%TZ)" "$WAVE" "$CASES" "$ST" "${CONS:-default}" "$EXTRA" >> "$REPORTS/ASSIGNMENTS.tsv"
tmux new-session -d -s "tl-$RUN_ID" "export TIMELEARNER_MATRIX_RUNS_ROOT='$TIMELEARNER_MATRIX_RUNS_ROOT'; ${CONS:+export NMSDK_CONSOLE='$CONS';} cd '$ST'; \
python3 -u scripts/run_timelearner_matrix_queue.py --run-id '$RUN_ID' --waves '$WAVE' --cases $CASES --jobs '$JOBS' --no-commit --allow-repeat $EXTRA > '$LOG' 2>&1; echo \$? > '$EXITF'"
sleep 90
if [ -f "$EXITF" ]; then echo "EARLY_EXIT rc=$(cat "$EXITF")"; tail -15 "$LOG"; fi
echo "consoles_now=$(pgrep -c -f '[N]euroModelerConsole' || true)"
echo "$RUN_ID"
