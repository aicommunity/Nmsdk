#!/usr/bin/env bash
# Run REPEATS sequential queue calls of one variant in one lane (each with a new RUN_ID), waiting for each.
# Start it inside its own tmux session so it survives SSH loss, e.g.:
#   tmux new -d -s drv-D2.1 "source ~/tl-agent/env.sh; bash $TOOLS/run_series.sh d2-1 D2.1 W01 W01_CL50_N1_PSIoff 1 3 --train-param EstDelayPerSeg=0.01"
# Usage: run_series.sh <LANE> <TASK> <WAVE> "<CASES>" <JOBS> <REPEATS> [extra queue flags...]
# Env: NMSDK (source for the lane), NMSDK_CONSOLE (Console to use), TIMELEARNER_MATRIX_RUNS_ROOT, REPORTS, HOSTTAG
set -u
LANE="$1"; TASK="$2"; WAVE="$3"; CASES="$4"; JOBS="$5"; REP="$6"; shift 6
DIR=$(cd "$(dirname "$0")" && pwd)
eval "$(bash "$DIR/make_lane.sh" "$LANE" | grep '^export ST=')"
: "${NMSDK_CONSOLE:?set NMSDK_CONSOLE to the Console built from the lane source}"
for i in $(seq 1 "$REP"); do
  out=$(bash "$DIR/launch_queue.sh" "$TASK" "$WAVE" "$CASES" "$JOBS" "$@"); rc=$?
  rid=$(echo "$out" | tail -1)
  echo "$(date -u +%FT%TZ) lane=$LANE task=$TASK rep=$i rc=$rc run_id=$rid" | tee -a "$REPORTS/${TASK%%.*}_series.log"
  [ $rc -eq 0 ] || { echo "$out"; echo "STOP: launch failed"; exit 1; }
  echo "$rid" >> "$REPORTS/${TASK%%.*}_runs.txt"
  bash "$DIR/wait_run.sh" "$rid" "${TASK%%.*}" > /dev/null || { echo "STOP: wait failed or launch.exit≠0 for $rid"; exit 1; }
  EXITF="$TIMELEARNER_MATRIX_RUNS_ROOT/$rid.launch.exit"
  [ -f "$EXITF" ] || { echo "STOP: missing launch.exit for $rid"; exit 1; }
  qe=$(cat "$EXITF"); [ "$qe" = "0" ] || { echo "STOP: launch.exit=$qe for $rid (expected 0)"; exit 1; }
done
echo "SERIES_DONE $TASK"
