#!/usr/bin/env bash
# W0/R0: Train-replay vs Test LTZ on HIST br25_nextseg (IsNeedToTrain=0).
# 2026-10-24 fix: overlay Train FixedLTZ (+ Use/AutoCal) onto Test BEFORE Console.
# Gold pack already has Train LTZ=0.0115 vs Test=0.0476 — comparing as-is is not R0.
set -euo pipefail
source "${HOME}/tl-agent/env.sh" 2>/dev/null || true
ROOT="$(cd "$(dirname "$0")/../../../../.." && pwd)"
ST="$ROOT/Bin/Configs/SpikeSamples/StructTrain"
CONSOLE="$ROOT/Bin/Platform/Linux/NeuroModelerConsole"
SRC="$ST/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9"
OUT_ROOT="${1:-${DATA:-/tmp}/runs/R0_br25_nextseg_$(date -u +%Y%m%dT%H%MZ)}"
HOSTTAG="$(hostname -s 2>/dev/null || hostname | cut -d. -f1)"
HOSTTAG="$(printf '%s' "$HOSTTAG" | tr -c 'A-Za-z0-9._-' '_' | sed 's/_\+$//')"
WD="$OUT_ROOT/R0_br25_nextseg_${HOSTTAG}"
LOGDIR="$OUT_ROOT/logs"
mkdir -p "$LOGDIR"
rm -rf "$WD"
mkdir -p "$WD"
cp -a "$SRC/Train" "$SRC/Test" "$WD/"

python3 - <<PY
from pathlib import Path
import sys
sys.path.insert(0, "$ST/scripts")
from repro_cold_lib import get_tag, set_tag, ensure_tag_after
wd = Path("$WD")
# Read Train FixedLTZ
tp = (wd / "Train" / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace")
ltz = get_tag(tp, "FixedLTZThreshold")
use = get_tag(tp, "UseFixedLTZThreshold") or "1"
auto = get_tag(tp, "AutoCalibrateFixedLTZThreshold") or "0"
if not ltz:
    raise SystemExit("Train FixedLTZThreshold missing")
print(f"R0_OVERLAY Train FixedLTZ={ltz} Use={use} AutoCal={auto} -> Test")
for side in ("Train", "Test"):
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        p = wd / side / rel
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        t = set_tag(t, "IsNeedToTrain", "0", 0) if get_tag(t, "IsNeedToTrain") is not None else t
        if get_tag(t, "EnablePostTrainTuning") is not None:
            t = set_tag(t, "EnablePostTrainTuning", "0", 0)
        if side == "Test":
            if get_tag(t, "FixedLTZThreshold") is not None:
                t = set_tag(t, "FixedLTZThreshold", ltz, 0)
            else:
                t = ensure_tag_after(t, "DendriteLength", "FixedLTZThreshold", ltz,
                                     attrs=' Type="d" PType="257" IoType="17"')
            if get_tag(t, "UseFixedLTZThreshold") is not None:
                t = set_tag(t, "UseFixedLTZThreshold", use, 0)
            else:
                t = ensure_tag_after(t, "FixedLTZThreshold", "UseFixedLTZThreshold", use,
                                     attrs=' Type="b" PType="257" IoType="17"')
            if get_tag(t, "AutoCalibrateFixedLTZThreshold") is not None:
                t = set_tag(t, "AutoCalibrateFixedLTZThreshold", auto, 0)
        p.write_text(t, encoding="utf-8")
# readback
for side in ("Train", "Test"):
    t = (wd / side / "Parameters_00.xml").read_text(encoding="utf-8", errors="replace")
    print(f"READBACK {side} FixedLTZ={get_tag(t, 'FixedLTZThreshold')}")
PY

run_one() {
  local side="$1"
  local ini="$WD/$side/Project.ini"
  local log="$LOGDIR/R0_${side}.log"
  echo "CONSOLE $side"
  nice -n 19 ionice -c3 "$CONSOLE" -c "$ini" -s -t 40 -x >"$log" 2>&1 || echo "rc=$? side=$side" >>"$log"
}
run_one Train
run_one Test

python3 - <<PY
from pathlib import Path
import re, math, hashlib, csv
wd = Path("$WD")

def ltz(side):
    p = wd / side / "Parameters_00.xml"
    t = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<FixedLTZThreshold[^>]*>([^<]+)</FixedLTZThreshold>", t)
    return float(m.group(1).replace(",", ".")) if m else float("nan")

a, b = ltz("Train"), ltz("Test")
rel = abs(a - b) / max(abs(a), 1e-12)
print(f"R0 FixedLTZ train={a} test={b} rel={rel:.6g}")
peaks = {}
for side in ("Train", "Test"):
    csvs = list((wd / side).glob("SelectivityLog/**/results.csv")) + list((wd / side).glob("**/results.csv"))
    print(side, "csv", csvs[:2])
    if csvs:
        rows = list(csv.DictReader(csvs[0].open()))
        tgt = [float(r["ltz_potential_max"]) for r in rows if r.get("target_class") == "1"]
        peaks[side] = tgt[0] if tgt else float("nan")
peak_rel = None
if "Train" in peaks and "Test" in peaks:
    peak_rel = abs(peaks["Train"] - peaks["Test"]) / max(abs(peaks["Train"]), 1e-12)
    print(f"R0 peak_ltz train={peaks['Train']} test={peaks['Test']} rel={peak_rel:.6g}")
status = "PASS" if rel <= 0.05 else "FAIL"
print(f"R0_VERDICT {status} tol=0.05 overlay=TrainFixedLTZ->Test")
Path("$OUT_ROOT/R0_SUMMARY.txt").write_text(
    f"workdir={wd}\nltz_train={a}\nltz_test={b}\nrel={rel}\n"
    f"peak_train={peaks.get('Train')}\npeak_test={peaks.get('Test')}\npeak_rel={peak_rel}\n"
    f"verdict={status}\noverlay=Train_FixedLTZ_to_Test\n",
    encoding="utf-8",
)
raise SystemExit(0 if status == "PASS" else 1)
PY
echo "R0 done out=$OUT_ROOT"
