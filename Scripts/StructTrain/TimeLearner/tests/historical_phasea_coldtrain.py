"""Bounded historical cold Train after the actual native pre-stimulus gate."""
import argparse
import hashlib
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from ..native_evidence import load, require
from ..process_runner import execute, verify_runtime
from ..runtime import source_closure
from .historical_phasea_replay import ROOT, BIN, PULSE, write
from .historical_phasea_coldstart import prepare, readback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--coldstart-gate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args();runtime = load(args.runtime)
    source = args.source_root.resolve(strict=True);closure = source_closure(source)
    require(closure["root"]["head"] == ROOT and closure["Bin"]["head"] == BIN and
            closure["Libraries/Nmsdk-PulseLib"]["head"] == PULSE, "historical_coldtrain_closure_mismatch")
    require(runtime["source_closure"] == closure, "historical_runtime_closure_mismatch")
    verify_runtime(runtime)
    gate = load(args.coldstart_gate/"validation.json")
    require(gate["native_cold_start_verified"] and gate["parent_only_overlay_rejected"] and
            gate["source_unchanged"] and gate["operations"] == 4, "native_coldstart_gate_not_completed")
    preflight = args.coldstart_gate/"native_state_reset"
    require(load(preflight/"process/runtime.json") == runtime, "coldstart_gate_runtime_changed")
    state = load(preflight/"readback.json")
    require(state["effective_dendrite_segments"] == 4 and state["generator_pulse_counter"] == 0 and
            state["reset_flag"] == "0", "coldstart_gate_effective_state_invalid")
    # Prevent unrestricted output on a nearly full filesystem; this is an
    # engineering minimum, not a scheduler reservation or arbitrary-run estimate.
    ancestor = args.output.parent
    while not ancestor.exists():ancestor = ancestor.parent
    require(shutil.disk_usage(ancestor).free >= 2*1024**3, "historical_coldtrain_storage_budget")
    args.output.mkdir(parents=True, exist_ok=False)
    work = prepare(source/"Bin", args.output/"train", "native_state_reset")
    declared = load(preflight/"pre-run-files.json")
    for record in declared:
        relative = Path(record["path"]).relative_to("work")
        require(hashlib.sha256((work/relative).read_bytes()).hexdigest() == record["sha256"],
                "coldtrain_input_differs_from_verified_gate:"+str(relative))
    shutil.copyfile(runtime["app_ini"]["path"], work/"NeuroModelerConsole.ini")
    require(hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest() ==
            runtime["app_ini"]["sha256"], "historical_coldtrain_app_ini_mismatch")
    write(args.output/"closure.json", closure)
    write(args.output/"protocol.json", {"kind": "historical_phasea_native_cold_train",
        "historical_root": ROOT, "normalization": "N1", "inputs": 4, "frequency_hz": 2000,
        "model_seconds_budget": 160, "wall_seconds_limit": 1800,
        "initial_state_operation": "StatesFile ResetToUntrainedState=1 before native Init/Reset",
        "prestimulus_gate": str(args.coldstart_gate), "initial_parent_and_effective_graph_verified": True,
        "calibration_or_test_performed": False, "series_d_resumed": False})
    print("COLD_TRAIN160 native reset, verified gate", flush=True)
    result = execute(runtime, ["-c", str(work/"Project.ini"), "-s", "-t", "160", "-x", "-S"],
                     work, args.output/"train/process", 1800)
    write(args.output/"execution.json", result)
    require(result["execution"] == "completed", "historical_cold_train_process_not_completed")
    require(hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest() ==
            runtime["app_ini"]["sha256"], "historical_coldtrain_app_ini_changed")
    actual = readback(work);write(args.output/"final-readback.json", actual)
    states = ET.parse(work/"States_00.xml").getroot()
    phase = states.find(".//NeuronTimeLearner/State/TrainingPhase")
    iteration = states.find(".//NeuronTimeLearner/State/CountIteration")
    need = actual["learner"]["IsNeedToTrain"]
    require(need in ([0.0], [1.0]), "historical_coldtrain_invalid_training_flag")
    require(source_closure(source) == closure, "historical_source_changed_during_coldtrain")
    write(args.output/"validation.json", {"kind": "historical_phasea_native_cold_train_outcome",
        "execution": result["execution"], "model_budget": 160, "native_cold_start_verified": True,
        "legacy_is_need_to_train": need[0], "legacy_phase": phase.text if phase is not None else None,
        "legacy_iteration": iteration.text if iteration is not None else None,
        "training_outcome": "legacy_done_uncertified" if need == [0.0] else "unfinished_at_model_budget",
        "dendrite_lengths": actual["learner"]["DendriteLength"],
        "references": actual["learner"]["InitialSomaPotential"],
        "effective_dendrite_segments": actual["effective_dendrite_segments"],
        "calibration_or_test_performed": False, "source_unchanged": True,
        "training_certificate": None, "scientific_verdict": None})


if __name__ == "__main__":
    main()
