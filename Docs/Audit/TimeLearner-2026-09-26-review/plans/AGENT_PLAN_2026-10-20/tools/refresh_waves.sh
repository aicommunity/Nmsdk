#!/usr/bin/env bash
# A0 step 8: refresh matrix input manifests for the given waves on a LOCAL Bin branch.
# Needed because Bin e7509263 changed TimeLearnerMatrix/matrix.json (W48, 19.10) after the input
# manifests were written, so `--prepare` refuses every wave ("matrix definition differs").
# --refresh rewrites only matrix_input_manifest.json (checked below) and may add newly registered case dirs.
# Usage: refresh_waves.sh <StructTrain dir> W01 W02 ...
set -u
ST="${1:?StructTrain dir}"; shift
cd "$ST" || exit 2
br=$(git rev-parse --abbrev-ref HEAD)
case "$br" in agent/*) ;; *) echo "STOP: current Bin branch is '$br'; create agent/tl-audit-20261020 first"; exit 2;; esac
[ -z "$(git status --porcelain -- TimeLearnerMatrix)" ] || { echo "STOP: TimeLearnerMatrix has uncommitted changes"; git status --short -- TimeLearnerMatrix | head; exit 2; }
fail=0
for w in "$@"; do
  python3 scripts/timelearner_matrix.py --prepare "$w" --refresh > "/tmp/refresh_$w.$$.log" 2>&1; rc=$?
  other=$(git diff --name-only -- "TimeLearnerMatrix/$w" | grep -v 'matrix_input_manifest.json$' || true)
  man=$(git diff --name-only -- "TimeLearnerMatrix/$w" | grep -c 'matrix_input_manifest.json$')
  new=$(git status --porcelain -- "TimeLearnerMatrix/$w" | grep '^??' | awk '{print $2}' | tr '\n' ' ')
  echo "$w rc=$rc manifests_changed=$man other_files_changed=$(echo -n "$other" | grep -c . ) new_case_dirs=[${new}]"
  if [ "$rc" -ne 0 ] || [ -n "$other" ]; then
    echo "STOP: wave $w refresh changed non-manifest files or failed; log /tmp/refresh_$w.$$.log"; echo "$other" | head; fail=1
  fi
done
[ "$fail" -eq 0 ] || exit 1
git add -A TimeLearnerMatrix
git -c user.name="tl-agent" -c user.email="tl-agent@localhost" commit -q -m "agent: refresh matrix input manifests ($*) for current matrix.json [AGENT_PLAN_2026-10-20 A0.8]" && git log -1 --format='refresh commit %H'
