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
series_rc=0
for i in $(seq 1 "$REP"); do
  out=$(bash "$DIR/launch_queue.sh" "$TASK" "$WAVE" "$CASES" "$JOBS" "$@"); rc=$?
  rid=$(echo "$out" | tail -1)
  echo "$(date -u +%FT%TZ) lane=$LANE task=$TASK rep=$i rc=$rc run_id=$rid" | tee -a "$REPORTS/${TASK%%.*}_series.log"
  [ $rc -eq 0 ] || { echo "$out"; echo "STOP: launch failed"; exit 1; }
  echo "$rid" >> "$REPORTS/${TASK%%.*}_runs.txt"
  bash "$DIR/wait_run.sh" "$rid" "${TASK%%.*}" > /dev/null
  wr=$?
  if [ "$wr" -ne 0 ]; then
    echo "STOP: wait/launch.exit failed for $rid (wait_rc=$wr)"
    # Keep going through remaining reps only if CONTINUE_ON_LAUNCH_EXIT=1; default stop.
    if [ "${CONTINUE_ON_LAUNCH_EXIT:-0}" = "1" ]; then
      series_rc=$wr
      continue
    fi
    echo "SERIES_DONE $TASK EXIT=$wr"
    exit "$wr"
  fi
done
echo "SERIES_DONE $TASK"
exit "$series_rc"
