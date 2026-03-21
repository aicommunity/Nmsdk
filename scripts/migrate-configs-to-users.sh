#!/usr/bin/env bash
# Migrate user config folders from Bin/Configs/<UserName> to Bin/Configs/Users/<UserName>.
# Run once from repository root (or set CONFIGS_ROOT to Bin/Configs).
# User list: a.demcheva, Alexab, Boiko, Demcheva, ivan, User, user

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIGS_ROOT="${CONFIGS_ROOT:-$REPO_ROOT/Bin/Configs}"

USERS=(a.demcheva Alexab Boiko Demcheva ivan User user)

if [[ ! -d "$CONFIGS_ROOT" ]]; then
  echo "Configs root not found: $CONFIGS_ROOT" >&2
  exit 1
fi

USERS_DIR="$CONFIGS_ROOT/Users"
if [[ ! -d "$USERS_DIR" ]]; then
  mkdir -p "$USERS_DIR"
  echo "Created $USERS_DIR"
fi

for name in "${USERS[@]}"; do
  src="$CONFIGS_ROOT/$name"
  dst="$USERS_DIR/$name"
  if [[ -d "$src" ]]; then
    if [[ -e "$dst" ]]; then
      echo "Skip $name: destination already exists: $dst"
      continue
    fi
    echo "Moving $src -> $dst"
    mv "$src" "$dst"
  else
    echo "Skip $name: source not found or not a directory: $src"
  fi
done

echo "Done."
