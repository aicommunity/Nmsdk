#!/usr/bin/env bash
# Print provenance block for a checkout + Console.  Usage: provenance.sh <NMSDK_ROOT> [CONSOLE_PATH]
# Output is KEY=VALUE lines; paste into the report (section "Provenance").
set -u
R="${1:?usage: provenance.sh NMSDK_ROOT [CONSOLE]}"
C="${2:-$R/Bin/Platform/Linux/NeuroModelerConsole}"
echo "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host=$(hostname)"
echo "os=$(. /etc/os-release 2>/dev/null; echo "${PRETTY_NAME:-unknown}")"
echo "gcc=$(gcc -dumpfullversion 2>/dev/null || echo none)"
echo "cmake=$(cmake --version 2>/dev/null | head -1)"
echo "python=$(python3 --version 2>&1)"
echo "nproc=$(nproc)"
for p in . Bin Libraries/Nmsdk-PulseLib Rdk; do
  echo "git[$p]=$(git -C "$R/$p" rev-parse HEAD 2>/dev/null) branch=$(git -C "$R/$p" rev-parse --abbrev-ref HEAD 2>/dev/null) dirty=$(git -C "$R/$p" status --porcelain 2>/dev/null | wc -l)"
done
echo "gitlinks=$(git -C "$R" ls-tree HEAD Bin Libraries/Nmsdk-PulseLib Rdk | awk '{print $4":"substr($3,1,10)}' | tr '\n' ' ')"
if [ -f "$C" ]; then echo "console=$C"; echo "console_sha256=$(sha256sum "$C" | cut -d' ' -f1)"; echo "console_mtime=$(date -u -r "$C" +%Y-%m-%dT%H:%M:%SZ)"; else echo "console=MISSING:$C"; fi
echo "console_procs_running=$(pgrep -c -f '[N]euroModelerConsole' || true)"
echo "load1=$(cut -d' ' -f1 /proc/loadavg)"
echo "runs_root=${TIMELEARNER_MATRIX_RUNS_ROOT:-UNSET}"
[ -n "${TIMELEARNER_MATRIX_RUNS_ROOT:-}" ] && echo "runs_root_free=$(df -h "$TIMELEARNER_MATRIX_RUNS_ROOT" | awk 'NR==2{print $4}')"
exit 0
