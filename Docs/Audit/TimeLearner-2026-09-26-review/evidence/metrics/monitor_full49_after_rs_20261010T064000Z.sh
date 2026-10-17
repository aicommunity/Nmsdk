#!/usr/bin/env bash
ROOT=/home/user/Nmsdk
MET="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics"
STRUCT="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
TAG=after_rs_20261010T064000Z
RCS_DIR="$STRUCT/_repro/runs/rcs.d_${TAG}"
EXIT="$MET/SOFTCOLD_full_matrix_${TAG}.exit"
STATUS="$MET/SOFTCOLD_full_matrix_${TAG}.status.log"
while :; do
  {
    date -u -Iseconds
    printf 'rc_shards='; find "$RCS_DIR" -maxdepth 1 -type f -name '*.rc' 2>/dev/null | wc -l
    printf 'active_cases='; pgrep -af '[p]osttune_verify.py --case' | sed -E 's/.*--case ([^ ]+).*/\1/' | paste -sd, -
    printf 'console_processes='; pgrep -fc '[N]euroModelerConsole'
    printf 'disk='; df -h /home/user/Nmsdk | tail -1
    printf 'memory='; free -h | awk '/Mem:/ {print $0}'
    printf 'recent_event_logs='; find "$STRUCT/_repro/runs" -maxdepth 4 -type f -path '*/Train/EventsLog/*' -mmin -60 -printf '%s %p; ' 2>/dev/null | sort -nr | head -c 600; echo
    echo '---'
  } >> "$STATUS"
  [[ -f "$EXIT" ]] && break
  sleep 300
done
