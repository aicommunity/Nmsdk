#!/usr/bin/env bash
# Create an extra checkout ("lane") so that several queue calls can run at the same time.
# Why: the queue holds <checkout>/Bin/.../_repro/.timelearner_matrix_queue.lock for the whole run, so a second
# call in the same checkout fails at once with "another matrix launch owns ...".
# Usage: make_lane.sh <lane_name> [SRC_ROOT=$NMSDK]
# The lane gets exactly the same commits as SRC_ROOT (root, Bin, PulseLib, Rdk ...). No build: run it with
# NMSDK_CONSOLE pointing at the Console built from SRC_ROOT (same PulseLib commit => honest provenance).
# Prints: export ST=<lane StructTrain dir>
set -eu
NAME="${1:?lane name}"; SRC="${2:-${NMSDK:?NMSDK unset}}"
L="$HOME/tl-agent/lanes/$NAME"
[ -e "$L" ] && { echo "lane exists: $L (reuse it; do not delete)"; echo "export ST=$L/Nmsdk/Bin/Configs/SpikeSamples/StructTrain"; exit 0; }
mkdir -p "$L"; cd "$L"
git clone -q "$SRC" Nmsdk; cd Nmsdk
git checkout -q --detach "$(git -C "$SRC" rev-parse HEAD)"
for p in $(git config --file .gitmodules --get-regexp path | awk '{print $2}'); do git config "submodule.$p.url" "$SRC/$p"; done
git -c protocol.file.allow=always submodule update --init -q
for p in $(git config --file .gitmodules --get-regexp path | awk '{print $2}'); do
  want=$(git -C "$SRC/$p" rev-parse HEAD); git -C "$p" checkout -q --detach "$want"
  [ "$(git -C "$p" rev-parse HEAD)" = "$want" ] || { echo "STOP: $p not at $want"; exit 1; }
done
echo "lane $NAME: root=$(git rev-parse --short HEAD) Bin=$(git -C Bin rev-parse --short HEAD) PulseLib=$(git -C Libraries/Nmsdk-PulseLib rev-parse --short HEAD)"
echo "export ST=$L/Nmsdk/Bin/Configs/SpikeSamples/StructTrain"
