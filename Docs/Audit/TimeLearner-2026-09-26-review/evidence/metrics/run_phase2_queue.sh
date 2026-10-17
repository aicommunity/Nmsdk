#!/usr/bin/env bash
set -uo pipefail
ROOT=/home/user/Nmsdk
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
LOG="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/phase2_queue.log"
SUMMARY="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/P2_asymrm_ab.md"
export PYTHONUNBUFFERED=1
{
  echo "=== phase2 queue start $(date -Is) console=$(sha256sum "$ROOT/Bin/Platform/Linux/NeuroModelerConsole" | cut -c1-16) ==="
  for case in asym50_preinh asym100_preinh asym100_gen; do
    echo "=== CASE $case START $(date -Is) ==="
    # marker into metrics stream
    echo "{\"event\":\"softcold_case_start\",\"case\":\"$case\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
      >> "$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/host_metrics.jsonl"
    sync
    python3 "$ST/scripts/posttune_verify.py" --case "$case"
    rc=$?
    echo "=== CASE $case END rc=$rc $(date -Is) ==="
    echo "{\"event\":\"softcold_case_end\",\"case\":\"$case\",\"rc\":$rc,\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
      >> "$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/host_metrics.jsonl"
    sync
    # append short note
    latest=$(ls -1dt "$ST/_repro/runs/${case}_"*[Z] 2>/dev/null | head -1 || true)
    echo "- $case rc=$rc bundle=$latest" >> "$SUMMARY.partial"
  done
  echo "=== phase2 queue done $(date -Is) ==="
} 2>&1 | tee -a "$LOG"
