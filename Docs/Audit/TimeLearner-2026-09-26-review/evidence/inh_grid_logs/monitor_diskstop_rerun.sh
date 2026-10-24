#!/usr/bin/env bash
# Monitor Classic disk_stop dual-host re-run (Elder-1 S25 + .17 S50).
set -euo pipefail
ROOT=/home/user/Nmsdk
EV=$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence
LOG=$EV/inh_grid_logs/monitor_diskstop_rerun.log
mkdir -p "$(dirname "$LOG")"
while true; do
  ts=$(date -u +%Y-%m-%dT%H:%MZ)
  avail=$(df -BG /home/user | awk 'NR==2{print $4}')
  vc=$(pgrep -c -f 'posttune_verify.py --case inh_c' || true)
  cc=$(pgrep -c -f '/NeuroModelerConsole' || true)
  loc_launch=$(pgrep -c -f 'INH_GRID_LAUNCH_CASES.sh' || true)
  # local S25 progress from TSV
  s25=$(python3 - <<'PY'
from pathlib import Path
from collections import Counter
want=set(Path('/tmp/inh_rerun_local_s25.txt').read_text().split()) if Path('/tmp/inh_rerun_local_s25.txt').exists() else set()
latest={}
for line in Path('/home/user/Nmsdk/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_COLD_LAUNCH.tsv').read_text().splitlines()[1:]:
    p=line.split('\t')
    if len(p)>=4 and p[0] in want:
        latest[p[0]]=p[3]
print(dict(Counter(latest.values())), f"{sum(1 for s in latest.values() if s.startswith('done'))}/{len(want)}")
PY
)
  echo "$ts Elder-1 avail=$avail verify=$vc console=$cc launch=$loc_launch s25=$s25" | tee -a "$LOG"

  ssh -o ConnectTimeout=12 -o BatchMode=yes user@10.245.1.17 bash -s <<'EOS' >>"$LOG" 2>&1 || echo "$ts REMOTE_SSH_FAIL" >>"$LOG"
avail=$(df -BG /home/user | awk 'NR==2{print $4}')
avail_n=${avail%G}
vc=$(pgrep -c -f 'posttune_verify.py --case inh_c' || true)
cc=$(pgrep -c -f NeuroModelerConsole || true)
ln=$(pgrep -c -f 'INH_GRID_LAUNCH_CASES.sh' || true)
if [[ "${avail_n:-0}" -lt 85 ]] && ! pgrep -f 'inh_b_dynamics_offload_once' >/dev/null; then
  echo "AUTO_OFFLOAD trigger avail=$avail"
  [[ -x /tmp/inh_b_dynamics_offload_once.sh ]] && nohup bash /tmp/inh_b_dynamics_offload_once.sh >/tmp/inh_b_dynamics_offload_wrap.log 2>&1 &
fi
s50=$(python3 - <<'PY'
from pathlib import Path
from collections import Counter
want=set(Path('/tmp/inh_rerun_17_s50.txt').read_text().split()) if Path('/tmp/inh_rerun_17_s50.txt').exists() else set()
latest={}
for line in Path('/home/user/tl-agent/Nmsdk/Docs/Audit/TimeLearner-2026-09-26-review/evidence/INH_GRID_COLD_LAUNCH.tsv').read_text().splitlines()[1:]:
    p=line.split('\t')
    if len(p)>=4 and p[0] in want:
        latest[p[0]]=p[3]
done=sum(1 for s in latest.values() if str(s).startswith('done'))
print(dict(Counter(latest.values())), f'{done}/{len(want)}')
PY
)
echo "M40 avail=$avail verify=$vc console=$cc launch=$ln s50=$s50"
EOS

  if [[ "$loc_launch" == "0" && "$vc" == "0" ]]; then
    rem=$(ssh -o ConnectTimeout=12 -o BatchMode=yes user@10.245.1.17 \
      "echo \$(pgrep -c -f 'INH_GRID_LAUNCH_CASES.sh' || true) \$(pgrep -c -f 'posttune_verify.py --case inh_c' || true)" 2>/dev/null || echo "1 1")
    set -- $rem
    if [[ "${1:-1}" == "0" && "${2:-1}" == "0" ]]; then
      echo "$ts DISKSTOP_RERUN_ALL_DONE" | tee -a "$LOG"
      exit 0
    fi
  fi
  sleep 300
done
