#!/usr/bin/env python3
"""Q1 H-sim (PLAN 2026-10-25 W1/W2): build an exactly time-scaled twin of the
br25 nextseg template (all time quantities x k) outside the repo.

Scaled: pattern times (MatrixData/InputPattern/TrainingPattern), Cm, synaptic
Secretion/Dissociation TC, TypicalPulseDuration, generator PulseLength,
learner SyncTolerance/PeakMeasureMargin/DelayAgreeMarginMin, EstDelayPerSeg
(inserted = 0.005*k; C++ default kDelayPerSegDefault=0.005 otherwise).
Unchanged (dimensionless or period-level): resistances, thresholds, Delay/
IterationGap (trial period 1.5 s), DendriteLength. NeuronClassName ->
NSPNeuronGenAsymRmD001C1e9Sim{k} (PulseLib 5834f28).
Known non-scaled C++ literals (Q1 suspects): Branch peak band guard 0.002 s,
gap_guard<=0.002 s, IterationGap+0.001 sentinels.
"""
from __future__ import annotations
import argparse, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NMSDK = HERE.parents[4]
ST = NMSDK / "Bin" / "Configs" / "SpikeSamples" / "StructTrain"
sys.path.insert(0, str(ST / "scripts"))
from repro_cold_lib import ensure_tag_after, get_tag, set_tag  # noqa: E402

SRC = ST / "SelectivityBranch" / "EXP_br_span25_packA_nextseginh_C1e9"
PATTERN_TAGS = ("MatrixData", "InputPattern", "TrainingPattern")
CONST_TAGS = ("MembraneCapacity", "SynapseSecretionTC", "SynapseDissociationTC",
              "SynapseTypicalPulseDuration", "Capacity", "SecretionTC",
              "DissociationTC", "TypicalPulseDuration", "PulseLength",
              "SyncTolerance", "PeakMeasureMargin", "DelayAgreeMarginMin",
              "EstDelayPerSeg")
CLASS = {1.0: "NSPNeuronGenAsymRmD001C1e9Sim1", 2.0: "NSPNeuronGenAsymRmD001C1e9Sim2",
         4.0: "NSPNeuronGenAsymRmD001C1e9Sim4", 19.2: "NSPNeuronGenAsymRmD001C1e9Sim19_2"}


def scale_file(p: Path, k: float) -> dict:
    t = p.read_text(encoding="utf-8", errors="replace")
    cnt = {}

    def mul(m):
        vals = m.group(2).replace(",", ".").split()
        try:
            new = [f"{float(v) * k:.12g}" for v in vals]
        except ValueError:
            return m.group(0)
        sep = "\n" if "\n" in m.group(2) else " "
        return m.group(1) + sep.join(new) + m.group(3)

    for tag in PATTERN_TAGS + CONST_TAGS:
        t, n = re.subn(rf"(<{tag}\b[^>]*>)([^<]*)(</{tag}>)", mul, t)
        cnt[tag] = n
    if get_tag(t, "NeuronClassName") is not None:
        t = set_tag(t, "NeuronClassName", CLASS[k], 0)
        cnt["NeuronClassName"] = 1
    attrs = ' Type="d" PType="257" IoType="17"'
    if "<SynapseSecretionTC" in t and "<SynapseTypicalPulseDuration" not in t:
        t = ensure_tag_after(t, "SynapseSecretionTC", "SynapseTypicalPulseDuration",
                             f"{0.001 * k:.12g}", attrs=attrs)
        cnt["SynapseTypicalPulseDuration+"] = 1
    if "<SyncTolerance" in t and "<EstDelayPerSeg" not in t:
        t = ensure_tag_after(t, "SyncTolerance", "EstDelayPerSeg", f"{0.005 * k:.12g}",
                             attrs=attrs)
        cnt["EstDelayPerSeg+"] = 1
    p.write_text(t, encoding="utf-8")
    return cnt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=float, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.out.exists():
        shutil.rmtree(a.out)
    shutil.copytree(SRC, a.out, ignore=shutil.ignore_patterns(
        "StatisticLog", "EventsLog", "SelectivityLog", "*.log", "*.bak*", "diagnostics"))
    for side in ("Train", "Test"):
        for rel in ("Parameters_00.xml", "Model_00.xml"):
            p = a.out / side / rel
            if p.is_file():
                print(side, rel, scale_file(p, a.k))
    (a.out / "SIM_TEMPLATE.txt").write_text(f"k={a.k}\nsrc={SRC}\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
