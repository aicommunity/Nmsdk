#!/usr/bin/env bash
# Sync canonical Skills/Cursor/* → .cursor/skills/ for Cursor auto-invocation.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/Skills/Cursor"
DST="$ROOT/.cursor/skills"

mkdir -p "$DST"

# Copy each skill directory (SKILL.md + optional extras), skip infra files.
for dir in "$SRC"/*/; do
  name="$(basename "$dir")"
  [[ "$name" == .* ]] && continue
  if [[ ! -f "$dir/SKILL.md" ]]; then
    continue
  fi
  mkdir -p "$DST/$name"
  rsync -a --delete \
    --exclude '.git' \
    "$dir" "$DST/$name/"
  echo "synced $name"
done

echo "Done → $DST"
