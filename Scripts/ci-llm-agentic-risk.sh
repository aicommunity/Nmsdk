#!/usr/bin/env bash
# Runs P0/P1 agentic-risk matrix suites from manifest (Post-Audit Phase 2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-${ROOT}/build-llm-ci}"
MANIFEST="${ROOT}/Rdk/Tests/Fixtures/LLM/agentic-risk/manifest.json"
LLM_TEST_DIR="${BUILD_DIR}/Rdk/Tests/Unit/LLM"
if [[ "$(uname -s)" =~ ^(MINGW|MSYS|CYGWIN) ]]; then
  BIN_DIR="${ROOT}/Bin/Platform/Win"
else
  BIN_DIR="${ROOT}/Bin/Platform/Linux"
fi

if [[ ! -f "${MANIFEST}" ]]; then
  echo "ci-llm-agentic-risk: manifest not found: ${MANIFEST}" >&2
  exit 1
fi

if [[ ! -d "${LLM_TEST_DIR}" ]]; then
  echo "ci-llm-agentic-risk: build LLM tests first (BUILD_DIR=${BUILD_DIR})" >&2
  exit 1
fi

export PYTHONPATH=""
python3 - "${MANIFEST}" "${LLM_TEST_DIR}" "${BIN_DIR}" <<'PY'
import json
import os
import re
import subprocess
import sys

manifest_path, test_dir, bin_dir = sys.argv[1], sys.argv[2], sys.argv[3]
with open(manifest_path, encoding="utf-8") as f:
    data = json.load(f)

ctest_exe = {}
ctest_file = os.path.join(test_dir, "CTestTestfile.cmake")
if os.path.isfile(ctest_file):
    with open(ctest_file, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'add_test\((\S+)\s+"([^"]+)"\)', line.strip())
            if m:
                ctest_exe[m.group(1)] = m.group(2)

failed = []
for suite in data.get("suites", []):
    sid = suite["id"]
    priority = suite.get("priority", "?")
    ctest = suite["ctest"]
    gfilter = suite["gtest_filter"]
    exe = ctest_exe.get(ctest) or os.path.join(bin_dir, ctest)
    if not os.path.isfile(exe):
        failed.append((sid, priority, gfilter))
        sys.stderr.write(f"ci-llm-agentic-risk: executable not found: {exe}\n")
        continue
    print(f"[agentic-risk] {priority} {sid} ({gfilter})")
    proc = subprocess.run(
        [exe, f"--gtest_filter={gfilter}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        failed.append((sid, priority, gfilter))
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.stderr.write(
            f"ci-llm-agentic-risk: FAILED suite id={sid} priority={priority} filter={gfilter}\n"
        )

if failed:
    sys.stderr.write(
        f"ci-llm-agentic-risk: {len(failed)} suite(s) failed: "
        + ", ".join(f"{s[0]}({s[1]})" for s in failed)
        + "\n"
    )
    sys.exit(1)

print(f"ci-llm-agentic-risk: all {len(data.get('suites', []))} suites passed")
PY
