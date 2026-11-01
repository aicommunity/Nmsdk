set -euo pipefail
src=/home/user/timelearner-refactor/source-order-fixed-a1
build=/home/user/timelearner-refactor/build-order-fixed-normal-a1
out=/home/user/timelearner-refactor/readbacks/s05-repeat-boundary-normal-a1
runtime=/home/user/timelearner-refactor/runtime-s05-repeat-boundary-normal-a1
trap 'status=$?; printf "%s\n" "$status" > "$out/process-exit-status.txt"' EXIT
test -z "$(git -C "$src" status --porcelain)"
git -C "$src" -c fetch.recurseSubmodules=false fetch origin codex/timelearner-repeat-boundary > "$out/checkout.log" 2>&1
git -C "$src" checkout --detach a6cfc24acf00f5bf8a235ad7872741bb9e05da3f >> "$out/checkout.log" 2>&1
git -C "$src" submodule update --init --recursive >> "$out/checkout.log" 2>&1
git -C "$src" submodule status --recursive > "$out/source-closure.txt"
cmake -S "$src" -B "$build" -DNMSDK_DEPLOY_ROOT="$runtime" -DNMSDK_REsource-order-fixed-a1_ROOT="$src/Bin" > "$out/configure.log" 2>&1
cmake --build "$build" --target Test_PulseLib_StorageComponents -j 2 > "$out/build.log" 2>&1
export QT_QPA_PLATFORM=offscreen ASAN_OPTIONS=detect_leaks=0 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$out/native"
cd "$src"
python3 -m Scripts.StructTrain.TimeLearner.runtime --root "$src" --executable "$runtime/Test_PulseLib_StorageComponents" --app-ini "$runtime/NeuroModelerConsole.ini" --cache "$build/CMakeCache.txt" --output "$out/runtime-before.json"
cd "$runtime"
export TIMELEARNER_EXECUTION_OUTPUT="$out/native"
set +e
./Test_PulseLib_StorageComponents --gtest_filter='NativeLearnedState.*N0Repeated*:NativeStoppedState.*N0Repeated*' --gtest_output="xml:$out/native.xml" > "$out/native.log" 2>&1
status=$?
set -e
printf '%s\n' "$status" > "$out/native-exit-status.txt"
cd "$src"
RUNTIME_MANIFEST="$out/runtime-before.json" python3 - <<'PY' > "$out/runtime-after.json"
import os,json
from pathlib import Path
from Scripts.StructTrain.TimeLearner.process_runner import verify_runtime
record=json.loads(Path(os.environ["RUNTIME_MANIFEST"]).read_text())
print(json.dumps(verify_runtime(record),indent=2))
PY
tail -n 8 "$out/native.log"
exit "$status"
