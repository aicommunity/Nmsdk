#!/usr/bin/env bash
# S3.d then remaining S3.c (C1+C2 minus already retested in S3.a/b).
set -uo pipefail
ROOT=/home/user/Nmsdk
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
PV="$ST/scripts/posttune_verify.py"
RC_OUT="$ST/_repro/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt"
LOG="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/S3cd_tails.log"
EV="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence"
MAN="$ST/_repro/EXTENDED_TIME_MANIFEST.txt"

mkdir -p "$(dirname "$LOG")"
echo "=== SoftCold S3.c/d tails start $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$LOG"

cd "$ROOT"

# --- S3.d extended-time ---
echo ">>> S3.d extended-time" | tee -a "$LOG"
while read -r case tt polls rest; do
  [[ -z "${case:-}" || "$case" =~ ^# ]] && continue
  echo "" | tee -a "$LOG"
  echo ">>> START extended $case -t $tt polls=$polls $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
  set +e
  python3 -u "$PV" --case "$case" --train-t "$tt" --max-polls "$polls" >>"$LOG" 2>&1
  rc=$?
  set -e
  echo "${case}_ext${tt} rc=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RC_OUT" | tee -a "$LOG"
  echo ">>> END extended $case rc=$rc" | tee -a "$LOG"
done < "$MAN"

# --- S3.c remaining DEFER (skip cases already in S3.a/b) ---
echo ">>> S3.c remaining C1+C2" | tee -a "$LOG"
CASES=(
  fs25_preinh fs50_preinh fs100_gen fs100_preinh
  ltz25_gen ltz25_preinh ltz50_gen ltz50_preinh ltz100_gen ltz100_preinh
  pa00_baseline pa01_ltz_sweep pa02_ltzone_avg pa06_ltzone_int tn_classic
  psi01_050 psi14_260 psi15_270 psi21_100
  psi31_200 psi32_300 psi33_300 psi34_400 psi35_400
)
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

echo "DONE_TAILS $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
cp -f "$RC_OUT" "$EV/SOFTCOLD_DEFER_rcs_after_softcold_fix.txt"
