#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/user/Nmsdk
EV=$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence
LOG=$EV/inh_grid_logs/monitor.log
while true; do
  ts=$(date -u +%Y-%m-%dT%H:%MZ)
  vc=$(pgrep -c -f 'posttune_verify.py --case inh_c' || true)
  cc=$(pgrep -c -f '/NeuroModelerConsole' || true)
  done_n=$(grep -c 'done_exit' "$EV/INH_GRID_COLD_LAUNCH.tsv" 2>/dev/null || echo 0)
  run_n=$(grep -c $'\trunning\t' "$EV/INH_GRID_COLD_LAUNCH.tsv" 2>/dev/null || echo 0)
  echo "$ts local verify=$vc console=$cc done=$done_n running_rows=$run_n" | tee -a "$LOG"
  # remote snapshot
  ssh -o ConnectTimeout=10 -o BatchMode=yes user@10.245.1.17 \
    "cd /home/user/tl-agent/Nmsdk; echo REMOTE verify=\$(pgrep -c -f 'posttune_verify.py --case inh_b' || true) console=\$(pgrep -c -f NeuroModelerConsole || true) done=\$(grep -c done_exit Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_COLD_LAUNCH.tsv 2>/dev/null || echo 0) launcher=\$(pgrep -c -f 'INH_GRID_LAUNCH.sh branch' || true)" \
    >>"$LOG" 2>&1 || echo "$ts REMOTE_SSH_FAIL" >>"$LOG"
  # stop when both launchers gone and no verifies
  if ! pgrep -f 'INH_GRID_LAUNCH.sh classic' >/dev/null \
     && ! pgrep -f 'posttune_verify.py --case inh_c' >/dev/null; then
    # check remote too
    rem=$(ssh -o ConnectTimeout=10 -o BatchMode=yes user@10.245.1.17 \
      "pgrep -c -f 'INH_GRID_LAUNCH.sh branch' || true; pgrep -c -f 'posttune_verify.py --case inh_b' || true" 2>/dev/null || echo "1 1")
    set -- $rem
    if [[ "${1:-1}" == "0" && "${2:-1}" == "0" ]]; then
      echo "$ts BOTH_IDLE" | tee -a "$LOG"
      exit 0
    fi
  fi
  sleep 300
done
