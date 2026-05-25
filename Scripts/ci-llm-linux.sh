#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${ROOT}/build-llm-ci"
cmake -S "${ROOT}" -B "${BUILD_DIR}" -DRDK_USE_LLM=ON -DBUILD_TESTING=ON
cmake --build "${BUILD_DIR}" --target rdk.llm.core NeuroModeler llm_audit_verify -j"$(nproc)"
ctest --test-dir "${BUILD_DIR}/Rdk/Tests/Unit/LLM" --output-on-failure
if [ -f "${BUILD_DIR}/../Bin/Platform/Linux/llm_audit_verify" ]; then
  "${BUILD_DIR}/../Bin/Platform/Linux/llm_audit_verify" /tmp/rdk_llm_audit_ci.jsonl || true
fi
