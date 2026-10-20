#!/usr/bin/env bash
# Find root (Nmsdk) commits whose gitlink pins a given PulseLib commit.
# Usage: find_root_for_pulselib.sh <NMSDK_ROOT> <PULSELIB_SHA_PREFIX> [MAX=400]
# Prints "<root_sha> <date> <Rdk_gitlink> <Bin_gitlink>" newest first. Empty output = no exact pin.
set -u
R="${1:?root}"; P="${2:?pulselib sha}"; MAX="${3:-400}"
git -C "$R" rev-list --all --max-count="$MAX" | while read -r c; do
  pl=$(git -C "$R" ls-tree "$c" Libraries/Nmsdk-PulseLib 2>/dev/null | awk '{print $3}')
  case "$pl" in "$P"*)
    echo "$c $(git -C "$R" show -s --format=%cI "$c") rdk=$(git -C "$R" ls-tree "$c" Rdk | awk '{print substr($3,1,10)}') bin=$(git -C "$R" ls-tree "$c" Bin | awk '{print substr($3,1,10)}')";;
  esac
done
