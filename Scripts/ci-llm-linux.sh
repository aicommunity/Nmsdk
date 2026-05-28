#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${ROOT}/build-llm-ci"
cmake -S "${ROOT}" -B "${BUILD_DIR}" -DRDK_USE_LLM=ON -DBUILD_TESTING=ON
cmake --build "${BUILD_DIR}" --target rdk.llm.core NeuroModeler llm_audit_verify -j"$(nproc)"
ctest --test-dir "${BUILD_DIR}/Rdk/Tests/Unit/LLM" --output-on-failure
# P0/P1 agentic-risk matrix (Post-Audit Phase 2)
BUILD_DIR="${BUILD_DIR}" "${ROOT}/Scripts/ci-llm-agentic-risk.sh"
# Hash-chain coverage: Test_LLM_AuditChain (in-process ULLMAuditLog)
