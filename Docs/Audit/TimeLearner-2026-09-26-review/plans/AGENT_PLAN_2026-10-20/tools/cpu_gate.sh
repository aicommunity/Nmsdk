#!/usr/bin/env bash
# Block until it is safe to start N more Console processes (runbook §4).
# Usage: cpu_gate.sh N [HOST_LIMIT]   HOST_LIMIT default: 12 (.17); use 8 on .11.
# Rules: total Console on this host + N <= HOST_LIMIT; CPU busy < 85% (resume after 2 samples < 70%).
set -u
N="${1:?usage: cpu_gate.sh N [HOST_LIMIT]}"; LIMIT="${2:-12}"
busy() { read -r _ a b c d e f g h _ < /proc/stat; t1=$((a+b+c+d+e+f+g+h)); i1=$((d+e)); sleep 5
         read -r _ a b c d e f g h _ < /proc/stat; t2=$((a+b+c+d+e+f+g+h)); i2=$((d+e))
         echo $(( 100 * ( (t2-t1) - (i2-i1) ) / (t2-t1) )); }
ok=0
while :; do
  # Count real Console binaries only (not cmake/gmake lines that mention the target name).
  running=$(pgrep -c -f '/Bin/Platform/.*/NeuroModelerConsole( |$)' || true); u=$(busy)
  if [ $((running + N)) -le "$LIMIT" ] && [ "$u" -lt 70 ]; then ok=$((ok+1)); else ok=0; fi
  if [ "$u" -ge 85 ]; then echo "$(date -u +%T) PAUSE cpu=${u}% consoles=$running"; fi
  [ "$ok" -ge 2 ] && { echo "GO consoles=$running cpu=${u}%"; exit 0; }
  sleep 25
done
