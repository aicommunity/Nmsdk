#!/usr/bin/env python3
"""be_transfer (PLAN 2026-10-25 E-series, 2026-10-25 MSK): build a Test of a Train structure that C++ REFUSED
(train_status cpp_training_*), reproducing the phase9 (phase9_preinh_bc_gate.py --skip-tipr-mid --diagnostic-threshold)
Test preparation: overlay_train_params (Model neuron overlay + TipR/ResistanceMin/DendriteLength/topology,
IsNeedToTrain=0, StructureBuildMode=1), then PostTune OFF + fixed threshold, + enable_pattern_response_trace
(PatternResponseAnalyzer rows). Metrics from such a Test are labelled metrics_basis=be_transfer_rejected_structure.
"""
import sys, shutil, re
from pathlib import Path
import os
NM = Path(os.environ.get("NMSDK_ROOT", os.path.expanduser("~/Nmsdk")))
ST = NM / "Bin/Configs/SpikeSamples/StructTrain"
sys.path.insert(0, str(ST / "scripts")); sys.path.insert(0, str(ST / "SelectivityAsymRm/scripts"))
from repro_cold_lib import get_tag, set_tag, set_tag_all, ensure_tag_after, enable_pattern_response_trace  # noqa
import phase9_preinh_bc_gate as p9  # noqa

COPY_EXTRA = ("MembraneCapacity", "OverrideMembraneCapacity", "OverrideExcMembraneResistance", "OverrideInhMembraneResistance",
              "OverrideExcSynapseResistance", "OverrideInhSynapseResistance", "MaxDendriteLength", "SynapseResistanceBase",
              "ResistanceMax", "NextSegInhResistance")

def prepare(train: Path, test_src: Path, be: Path, silent_thr="1.0"):
    if be.exists():
        shutil.rmtree(be)
    shutil.copytree(test_src, be, ignore=shutil.ignore_patterns("SelectivityLog", "EventsLog", "StatisticLog", "*.log", "posttune_complete.flag", "save.tmp"))
    thr = p9.overlay_train_params(train, be)
    try:
        thr_v = float(str(thr).replace(",", "."))
    except ValueError:
        thr_v = 1.0
    thr_used = str(thr) if thr_v < 0.9 else silent_thr  # refused training -> usually silent; metrics use ltz_potential_max
    for rel in ("Parameters_00.xml", "Model_00.xml"):
        tr = (train / rel).read_text(encoding="utf-8", errors="replace")
        p = be / rel
        t = p.read_text(encoding="utf-8", errors="replace")
        for k in COPY_EXTRA:
            v = get_tag(tr, k)
            if v is not None and get_tag(t, k) is not None:
                t = set_tag_all(t, k, v)
        t = set_tag_all(t, "IsNeedToTrain", "0")
        t = set_tag(t, "EnablePostTrainTuning", "0", 1)
        if get_tag(t, "EnablePostTrainMidThreshold") is None:
            t = ensure_tag_after(t, "EnablePostTrainTuning", "EnablePostTrainMidThreshold", "0", attrs=' Type="b" PType="257" IoType="17"')
        else:
            t = set_tag(t, "EnablePostTrainMidThreshold", "0", 1)
        p.write_text(t, encoding="utf-8")
        p9.set_fixed_thr(p, thr_used)
    enable_pattern_response_trace(be / "Model_00.xml")
    (be / "SelectivityLog").mkdir(exist_ok=True)
    return {"be_thr_train": thr, "be_thr_used": thr_used, "be_recipe": "phase9 overlay_train_params + diag-threshold + pattern_response_trace"}

if __name__ == "__main__":
    print(prepare(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
