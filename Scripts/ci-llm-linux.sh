#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${ROOT}/build-llm-ci"
cmake -S "${ROOT}" -B "${BUILD_DIR}" -DRDK_USE_LLM=ON -DBUILD_TESTING=ON
cmake --build "${BUILD_DIR}" --target rdk.llm.core NeuroModeler llm_audit_verify -j"$(nproc)"
ctest --test-dir "${BUILD_DIR}/Rdk/Tests/Unit/LLM" --output-on-failure
AUDIT_SAMPLE="${BUILD_DIR}/rdk_llm_audit_ci.jsonl"
printf '{"event":"ci_sample","ts":"2026-05-25T00:00:00Z"}\n' > "${AUDIT_SAMPLE}"
if command -v llm_audit_verify >/dev/null 2>&1; then
  llm_audit_verify "${AUDIT_SAMPLE}"
elif [ -x "${BUILD_DIR}/llm_audit_verify" ]; then
  "${BUILD_DIR}/llm_audit_verify" "${AUDIT_SAMPLE}"
elif [ -f "${ROOT}/Bin/Platform/Linux/llm_audit_verify" ]; then
  "${ROOT}/Bin/Platform/Linux/llm_audit_verify" "${AUDIT_SAMPLE}"
fi
