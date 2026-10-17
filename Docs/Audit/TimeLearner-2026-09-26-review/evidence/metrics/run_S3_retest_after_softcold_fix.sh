#!/usr/bin/env bash
# SoftCold retest queue after softcold_fix (S3.a → S3.b → optional S3.c).
# Writes rc lines to SOFTCOLD_DEFER_rcs_after_softcold_fix.txt
set -uo pipefail
ROOT=/home/user/Nmsdk
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
PV="$ST/scripts/posttune_verify.py"
RC_OUT="$ST/_repro/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt"
LOG="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/S3_retest_after_softcold_fix.log"
EV="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence"

mkdir -p "$(dirname "$LOG")" "$ST/_repro"
: >"$RC_OUT"
echo "=== SoftCold retest after softcold_fix $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee "$LOG"

# S3.a timing_softcold_desync then S3.b control/affected
CASES=(
  asym50_preinh
  asym100_preinh
  asym100_gen
  asym25_preinh
  br25_on
  fs25_gen
  phase6_thr_only
  phase6_preinh250
  phase6_ltzcal_twin
)

cd "$ROOT"
for c in "${CASES[@]}"; do
  echo "" | tee -a "$LOG"
  echo ">>> START $c $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
  set +e
  python3 -u "$PV" --case "$c" >>"$LOG" 2>&1
  rc=$?
  set -e
  echo "$c rc=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RC_OUT" | tee -a "$LOG"
  echo ">>> END $c rc=$rc" | tee -a "$LOG"
done

echo "DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
cp -f "$RC_OUT" "$EV/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt" 2>/dev/null || true
