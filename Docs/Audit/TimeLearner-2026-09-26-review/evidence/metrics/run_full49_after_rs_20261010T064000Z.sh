#!/usr/bin/env bash
set -u
ROOT=/home/user/Nmsdk
MET="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics"
STRUCT="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
TAG=after_rs_20261010T064000Z
LOG="$MET/SOFTCOLD_full_matrix_${TAG}.log"
META="$MET/SOFTCOLD_full_matrix_${TAG}.meta.txt"
EXIT="$MET/SOFTCOLD_full_matrix_${TAG}.exit"
RCS="$STRUCT/_repro/runs/SOFTCOLD_HEAD_rcs_${TAG}.txt"
RCS_DIR="$STRUCT/_repro/runs/rcs.d_${TAG}"
MANIFEST="$STRUCT/_repro/SOFTCOLD_QUEUE_manifest.txt"
if [[ -e "$LOG" || -e "$META" || -e "$EXIT" || -e "$RCS" || -e "$RCS_DIR" ]]; then
  echo "Refusing to reuse existing artifacts for $TAG" >&2
  exit 2
fi
{
  echo "run_tag=$TAG"
  date -u -Iseconds
  echo "root=$(git -C "$ROOT" rev-parse HEAD)"
  echo "Bin=$(git -C "$ROOT/Bin" rev-parse HEAD)"
  echo "PulseLib=$(git -C "$ROOT/Libraries/Nmsdk-PulseLib" rev-parse HEAD)"
  echo "manifest_sha256=$(sha256sum "$MANIFEST" | cut -d' ' -f1)"
  echo "console_sha256=$(sha256sum "$ROOT/Bin/Platform/Linux/NeuroModelerConsole" | cut -d' ' -f1)"
  echo "queue_count=$(grep -cvE '^[[:space:]]*(#|$)' "$MANIFEST")"
  echo "parallel=6 autosave_model_s=10 snap_every=20 stall_autosave_n=0 skip_registry_apply=1"
  echo "disk_before=$(df -h /home/user/Nmsdk | tail -1)"
  echo "memory_before=$(free -h | awk '/Mem:/ {print $0}')"
} > "$META"
cp "$META" "$LOG"
export METRICS_ROOT="$MET"
export LOG RCS RCS_DIR MANIFEST
export NM="$ROOT/Bin/Platform/Linux/NeuroModelerConsole"
export PARALLEL=6 AUTOSAVE_MODEL_S=10 SNAP_EVERY=20 STALL_AUTOSAVE_N=0
export SKIP_REGISTRY_APPLY=1
cd "$STRUCT"
set +e
bash scripts/softcold_full_matrix_parallel.sh > "$MET/SOFTCOLD_full_matrix_${TAG}.launcher.log" 2>&1
rc=$?
set -e
printf '%s\n' "$rc" > "$EXIT"
printf 'launcher_exit=%s finished=%s\n' "$rc" "$(date -u -Iseconds)" >> "$LOG"
exit "$rc"
