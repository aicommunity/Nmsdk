#!/usr/bin/env bash
# Agent scenario matrix: deterministic (required) + e2e (skip when lab Ollama down).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-${ROOT}/build-llm-ci}"
if [[ "$(uname -s)" =~ ^(MINGW|MSYS|CYGWIN) ]]; then
  BIN_DIR="${ROOT}/Bin/Platform/Win"
else
  BIN_DIR="${ROOT}/Bin/Platform/Linux"
fi
EXE="${BIN_DIR}/Test_LLM_AgentScenarios"

if [[ ! -x "${EXE}" ]]; then
  echo "ci-llm-agent-scenarios: build Test_LLM_AgentScenarios first (${EXE})" >&2
  exit 1
fi

echo "ci-llm-agent-scenarios: deterministic suite"
"${EXE}" --gtest_filter='Deterministic/*:AgentScenarioLoader.*:AgentScenarioEvalUnit.*'

echo "ci-llm-agent-scenarios: e2e suite (GTEST_SKIP when lab unreachable)"
set +e
"${EXE}" --gtest_filter='E2e/*'
e2e_rc=$?
set -e
if [[ ${e2e_rc} -ne 0 ]]; then
  echo "ci-llm-agent-scenarios: e2e finished with failures (rc=${e2e_rc}); see log above" >&2
  exit "${e2e_rc}"
fi

echo "ci-llm-agent-scenarios: done"
