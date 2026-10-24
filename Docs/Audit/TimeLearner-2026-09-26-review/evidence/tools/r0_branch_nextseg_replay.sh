#!/usr/bin/env bash
# W0/R0: Train-replay vs Test LTZ on HIST br25_nextseg (IsNeedToTrain=0).
# PLAN 2026-10-25 F5 / W0 table (4th slot). Does not SoftCold-train.
set -euo pipefail
source "${HOME}/tl-agent/env.sh" 2>/dev/null || true
ROOT="$(cd "$(dirname "$0")/../../../../.." && pwd)"
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
CONSOLE="$ROOT/Bin/Platform/Linux/NeuroModelerConsole"
SRC="$ST/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9"
OUT_ROOT="${1:-${DATA:-/tmp}/runs/R0_br25_nextseg_$(date -u +%Y%m%dT%H%MZ)}"
HOSTTAG="$(hostname | tr -c 'A-Za-z0-9._-' '_')"
WD="$OUT_ROOT/R0_br25_nextseg_${HOSTTAG}"
LOGDIR="$OUT_ROOT/logs"
mkdir -p "$LOGDIR"
rm -rf "$WD"
mkdir -p "$WD"
cp -a "$SRC/Train" "$SRC/Test" "$WD/"
# ensure inference-only
python3 - <<PY
from pathlib import Path
import sys
sys.path.insert(0, "$ST/scripts")
from repro_cold_lib import set_tag
wd = Path("$WD")
for side in ("Train", "Test"):
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = wd / side / rel
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        t = set_tag(t, "IsNeedToTrain", "0", 1)
        t = set_tag(t, "EnablePostTrainTuning", "0", 1)
        p.write_text(t, encoding="utf-8")
PY
# overlay topology Train→Test (F3) via phase8-ish tags using r0 helper for asym path;
# Branch: copy NumSynapse/DendriteLength/TipR already in HIST gold.
run_one() {
  local side="$1"
  local ini="$WD/$side/Project.ini"
  local log="$LOGDIR/R0_${side}.log"
  echo "CONSOLE $side"
  "$CONSOLE" -c "$ini" -s -t 40 -x >"$log" 2>&1 || echo "rc=$? side=$side" >>"$log"
}
run_one Train
run_one Test
# Compare FixedLTZ + optional mid from flags
python3 - <<PY
from pathlib import Path
import re, math
wd = Path("$WD")

def ltz(side):
    p = wd/side/"Parameters_00.xml"
    t = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<FixedLTZThreshold[^>]*>([^<]+)</FixedLTZThreshold>", t)
    return float(m.group(1).replace(",", ".")) if m else float("nan")

a, b = ltz("Train"), ltz("Test")
rel = abs(a-b)/max(abs(a), 1e-12)
print(f"R0 FixedLTZ train={a} test={b} rel={rel:.6g}")
# Also dump SelectivityLog presence
for side in ("Train", "Test"):
    csv = list((wd/side).glob("SelectivityLog/**/results.csv")) + list((wd/side).glob("**/results.csv"))
    print(side, "csv", csv[:2])
status = "PASS" if rel <= 0.05 else "FAIL"
print(f"R0_VERDICT {status} tol=0.05")
Path("$OUT_ROOT/R0_SUMMARY.txt").write_text(
    f"workdir={wd}\nltz_train={a}\nltz_test={b}\nrel={rel}\nverdict={status}\n",
    encoding="utf-8",
)
raise SystemExit(0 if status == "PASS" else 1)
PY
echo "R0 done out=$OUT_ROOT"
