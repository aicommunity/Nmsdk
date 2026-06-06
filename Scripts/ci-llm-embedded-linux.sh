#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${ROOT}/build-llm-embedded-ci"
LLAMA_DIR="${LLAMA_DIR:-${ROOT}/.cache/llama.cpp-b4533}"

if [ ! -f "${LLAMA_DIR}/include/llama.h" ]; then
  echo "Cloning llama.cpp b4533 into ${LLAMA_DIR}..."
  git clone --depth 1 --branch b4533 --recurse-submodules \
    https://github.com/ggml-org/llama.cpp.git "${LLAMA_DIR}"
fi

cmake -S "${ROOT}" -B "${BUILD_DIR}" \
  -DRDK_USE_LLM=ON \
  -DRDK_LLM_BUILD_EMBEDDED=ON \
  -DRDK_LLM_LLAMA_CPP_DIR="${LLAMA_DIR}" \
  -DBUILD_TESTING=ON

cmake --build "${BUILD_DIR}" --target rdk.llm.core rdk.llm.embedded llm_audit_verify -j"$(nproc)"
ctest --test-dir "${BUILD_DIR}/Rdk/Tests/Unit/LLM" --output-on-failure

echo "Embedded LLM build OK (inference requires GGUF at NMSDK_LLM_GGUF_PATH)"
