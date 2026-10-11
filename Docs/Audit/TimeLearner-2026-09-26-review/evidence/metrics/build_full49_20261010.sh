#!/usr/bin/env bash
set -u
ROOT=/home/user/Nmsdk
MET="$ROOT/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics"
cd "$ROOT"
if cmake --preset linux-gcc-debug-tests > "$MET/build_full49_20261010.configure.log" 2>&1; then
  if cmake --build build/linux-gcc-debug-tests-make --target Test_PulseLib_StorageComponents NeuroModelerConsole --parallel 4 > "$MET/build_full49_20261010.build.log" 2>&1; then
    if QT_QPA_PLATFORM=offscreen ./Bin/Platform/Linux/Test_PulseLib_StorageComponents --gtest_filter='TimeLearnerResistanceTest.*' > "$MET/build_full49_20261010.tests.log" 2>&1; then rc=0; else rc=$?; fi
  else rc=$?; fi
else rc=$?; fi
printf '%s\n' "$rc" > "$MET/build_full49_20261010.exit"
if [ "$rc" -eq 0 ]; then sha256sum Bin/Platform/Linux/NeuroModelerConsole > "$MET/build_full49_20261010.console.sha256"; fi
exit "$rc"
