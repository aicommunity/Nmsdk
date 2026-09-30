#!/usr/bin/env bash
set -uo pipefail
ROOT=/home/user/Nmsdk
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
LOG="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/phase5_defer.log"
MET="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/host_metrics.jsonl"
RCS="$ST/_repro/SOFTCOLD_DEFER_rcs.txt"
: > "$RCS"
export PYTHONUNBUFFERED=1
# C1 then C2
CASES=(
  phase6_thr_only phase6_preinh250 phase6_ltzcal_twin
  fs25_gen fs25_preinh fs50_preinh fs100_gen fs100_preinh
  ltz25_gen ltz25_preinh ltz50_gen ltz50_preinh ltz100_gen ltz100_preinh
  pa00_baseline pa01_ltz_sweep pa02_ltzone_avg pa06_ltzone_int tn_classic
  psi01_050 psi14_260 psi15_270 psi21_100
  psi31_200 psi32_300 psi33_300 psi34_400 psi35_400
)
{
  echo "=== phase5 defer queue start $(date -Is) n=${#CASES[@]} console=$(sha256sum "$ROOT/Bin/Platform/Linux/NeuroModelerConsole" | cut -c1-16) ==="
  for case in "${CASES[@]}"; do
    echo "=== CASE $case START $(date -Is) ==="
    echo "{\"event\":\"softcold_case_start\",\"case\":\"$case\",\"phase\":\"5\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> "$MET"
    sync
    python3 "$ST/scripts/posttune_verify.py" --case "$case"
    rc=$?
    echo "$case $rc" >> "$RCS"
    echo "=== CASE $case END rc=$rc $(date -Is) ==="
    echo "{\"event\":\"softcold_case_end\",\"case\":\"$case\",\"phase\":\"5\",\"rc\":$rc,\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> "$MET"
    sync
  done
  echo "=== phase5 defer queue done $(date -Is) ==="
} 2>&1 | tee -a "$LOG"
