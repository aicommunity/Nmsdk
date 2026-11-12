#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  /home/user/Nmsdk/Scripts/llm_phase_commit.sh \
    --phase "PR0" \
    --rdk-message-file /abs/path/to/rdk_commit_message.txt \
    --nmsdk-message-file /abs/path/to/nmsdk_commit_message.txt

Notes:
  - This script does NOT stage files for you. Stage changes before calling it.
  - It creates two commits:
      1) in /home/user/Nmsdk/Rdk
      2) in /home/user/Nmsdk (root) to bump the subrepo pointer
EOF
}

phase=""
rdk_message_file=""
nmsdk_message_file=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --phase)
      phase="${2:-}"; shift 2;;
    --rdk-message-file)
      rdk_message_file="${2:-}"; shift 2;;
    --nmsdk-message-file)
      nmsdk_message_file="${2:-}"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 2;;
  esac
done

if [[ -z "$phase" || -z "$rdk_message_file" || -z "$nmsdk_message_file" ]]; then
  usage
  exit 2
fi

if [[ ! -f "$rdk_message_file" ]]; then
  echo "Missing rdk message file: $rdk_message_file" >&2
  exit 2
fi

if [[ ! -f "$nmsdk_message_file" ]]; then
  echo "Missing nmsdk message file: $nmsdk_message_file" >&2
  exit 2
fi

RDK_DIR="/home/user/Nmsdk/Rdk"
ROOT_DIR="/home/user/Nmsdk"

git -C "$RDK_DIR" rev-parse --is-inside-work-tree >/dev/null
git -C "$ROOT_DIR" rev-parse --is-inside-work-tree >/dev/null

if git -C "$RDK_DIR" diff --cached --quiet; then
  echo "Rdk has no staged changes. Stage changes in $RDK_DIR first." >&2
  exit 3
fi

git -C "$RDK_DIR" commit -F "$rdk_message_file"

rdk_head="$(git -C "$RDK_DIR" rev-parse HEAD)"
echo "Rdk committed at $rdk_head (phase=$phase)"

if git -C "$ROOT_DIR" diff --cached --quiet; then
  echo "Nmsdk root has no staged changes. Stage the bump (submodule/subrepo pointer) in $ROOT_DIR first." >&2
  exit 4
fi

git -C "$ROOT_DIR" commit -F "$nmsdk_message_file"

root_head="$(git -C "$ROOT_DIR" rev-parse HEAD)"
echo "Nmsdk committed at $root_head (phase=$phase)"

