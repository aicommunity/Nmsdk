#!/usr/bin/env bash
# PLAN 2026-10-25 E-series queue dispatcher (one per host). Survives ssh loss (start with setsid nohup).
# usage: e05_dispatch.sh ROOT      ROOT/queue.tsv lines: "label<TAB>json_spec" ('#' = comment); append any time.
# control: touch ROOT/STOP (no new starts; running jobs finish) ; ROOT/dispatch.log ; ROOT/launch.tsv
# limits: slots = nproc (counting ALL NeuroModelerConsole incl. other campaigns, plus own jobs between Consoles)
#         MemAvailable >= MIN_MEM_MB, no active swapping (vmstat si+so <= MAX_SWAP_PGS), df: / < SYS_MAX_PCT used,
#         DATA_DIR (opt) >= DATA_MIN_FREE_PCT free. Disk low -> DISK_LOW signal in log, no start (no deletion here).
set -u
ROOT="$1"; Q="$ROOT/queue.tsv"; LOG="$ROOT/dispatch.log"; TSV="$ROOT/launch.tsv"
NMSDK_ROOT="${NMSDK_ROOT:-$HOME/Nmsdk}"; export NMSDK_ROOT
JOB="${JOB:-$NMSDK_ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools/e05_job.py}"
SLOTS="${SLOTS:-$(nproc)}"; MIN_MEM_MB="${MIN_MEM_MB:-4000}"; MAX_SWAP_PGS="${MAX_SWAP_PGS:-200}"
SYS_MAX_PCT="${SYS_MAX_PCT:-90}"; DATA_DIR="${DATA_DIR:-}"; DATA_MIN_FREE_PCT="${DATA_MIN_FREE_PCT:-5}"
POLL="${POLL:-30}"
mkdir -p "$ROOT/state/started" "$ROOT/state/done" "$ROOT/jobs"
[[ -f "$TSV" ]] || echo -e "label\thost\tstatus\tstart_local\tend_local\tpid\tout" >"$TSV"
log() { echo "$(date '+%F %T %Z') $*" >>"$LOG"; }
echo $$ >"$ROOT/dispatch.pid"
log "DISPATCH_START pid=$$ host=$(hostname) slots=$SLOTS min_mem=${MIN_MEM_MB}MB sys_max=${SYS_MAX_PCT}% data=${DATA_DIR:-none} console=${NMSDK_CONSOLE:-default}"
mine_alive() { local n=0 f p; for f in "$ROOT"/state/started/*; do [[ -e "$f" ]] || continue; p=$(cut -f1 "$f"); [[ -e "$ROOT/state/done/$(basename "$f")" ]] && continue; kill -0 "$p" 2>/dev/null && n=$((n+1)); done; echo $n; }
others() { local n; n=$(pgrep -f NeuroModelerConsole -a 2>/dev/null | grep -v -F "$ROOT/" | wc -l); echo "${n:-0}"; }
mem_ok() { local a; a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [[ "$a" -ge "$MIN_MEM_MB" ]] || { echo "mem_avail=${a}MB"; return 1; }
  local sw; sw=$(vmstat 2 2 | tail -1 | awk '{print $7+$8}'); [[ "$sw" -le "$MAX_SWAP_PGS" ]] || { echo "swapping si+so=$sw"; return 1; }; return 0; }
disk_ok() { local u; u=$(df -P / | awk 'NR==2{gsub("%","",$5);print $5}'); [[ "$u" -lt "$SYS_MAX_PCT" ]] || { echo "DISK_LOW sys_used=${u}%"; return 1; }
  if [[ -n "$DATA_DIR" ]]; then local f; f=$(df -P "$DATA_DIR" | awk 'NR==2{print int(100*$4/$2)}'); [[ "$f" -ge "$DATA_MIN_FREE_PCT" ]] || { echo "DISK_LOW data_free=${f}% (rule: offload/old-archive review by agent, dispatcher only signals)"; return 1; }; fi; return 0; }
reap() { local f l p rc; for f in "$ROOT"/state/started/*; do [[ -e "$f" ]] || continue; l=$(basename "$f"); [[ -e "$ROOT/state/done/$l" ]] && continue
  p=$(cut -f1 "$f"); kill -0 "$p" 2>/dev/null && continue
  rc=$(cat "$ROOT/jobs/$l/exit_code" 2>/dev/null || echo NA); date '+%F %T' >"$ROOT/state/done/$l"
  echo -e "$l\t$(hostname)\tdone_rc$rc\t$(cut -f2 "$f")\t$(date '+%F %T')\t$p\t$ROOT/jobs/$l" >>"$TSV"
  log "JOB_END $l rc=$rc $(grep '^RESULT' "$ROOT/jobs/$l.log" 2>/dev/null | tail -1 | cut -c1-300)"; done; }
last_wait=""
while :; do
  reap
  if [[ -e "$ROOT/STOP" ]]; then [[ "$(mine_alive)" -eq 0 ]] && { log "STOP_FILE all own jobs finished -> exit"; break; }; sleep "$POLL"; continue; fi
  next=""; spec=""
  while IFS=$'\t' read -r l s; do [[ -z "$l" || "$l" == \#* ]] && continue; [[ -e "$ROOT/state/started/$l" ]] && continue; next="$l"; spec="$s"; break; done <"$Q"
  if [[ -z "$next" ]]; then [[ "$last_wait" != idle ]] && log "QUEUE_EMPTY (append to queue.tsv to continue)"; last_wait=idle; sleep "$POLL"; continue; fi
  m=$(mine_alive); o=$(others); why=""
  if [[ $((m+o)) -ge "$SLOTS" ]]; then why="slots busy own=$m other=$o slots=$SLOTS"; fi
  [[ -z "$why" ]] && { r=$(mem_ok) || why="$r"; }
  [[ -z "$why" ]] && { r=$(disk_ok) || why="$r"; }
  if [[ -n "$why" ]]; then [[ "$last_wait" != "$why" ]] && log "WAIT $next: $why"; last_wait="$why"; sleep "$POLL"; continue; fi
  last_wait=""
  mkdir -p "$ROOT/jobs/$next"; echo "$spec" >"$ROOT/jobs/$next/spec.json"
  setsid nohup bash -c "nice -n 5 python3 '$JOB' '$ROOT/jobs/$next' '$ROOT/jobs/$next/spec.json' >'$ROOT/jobs/$next.log' 2>&1; echo \$? >'$ROOT/jobs/$next/exit_code'" </dev/null >/dev/null 2>&1 &
  pid=$!
  echo -e "$pid\t$(date '+%F %T')" >"$ROOT/state/started/$next"
  echo -e "$next\t$(hostname)\tstarted\t$(date '+%F %T')\t\t$pid\t$ROOT/jobs/$next" >>"$TSV"
  log "JOB_START $next pid=$pid own=$((m+1)) other=$o"
  sleep 20
done
