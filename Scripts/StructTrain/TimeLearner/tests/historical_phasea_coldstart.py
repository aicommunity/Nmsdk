"""Native pre-stimulus cold-start gate on the unmodified August executable."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

from ..native_evidence import load, require
from ..process_runner import execute, verify_runtime
from ..runtime import source_closure
from .historical_phasea_replay import ROOT, BIN, PULSE, write

PREFIX = "Configs/SpikeSamples/StructTrain/SelectivityPhaseA/EXP00_baseline/Train/"
COLD = {"DendriteLength": "1 1 1 1", "NumSynapse": "1 1 1 1",
        "InitialSomaPotential": "0 0 0 0", "TipSynapseResistance": "86000000 86000000 86000000 86000000",
        "AttenuationGamma": "-1", "IsNeedToTrain": "1"}


def prepare(bin_repo, folder, mode):
    inputs, work = folder/"inputs", folder/"work"
    inputs.mkdir(parents=True);work.mkdir()
    records = []
    names = subprocess.check_output(["git", "-C", str(bin_repo), "ls-tree", "-r", "--name-only",
                                     BIN, "--", PREFIX], text=True).splitlines()
    require(len(names) == 6, "historical_train_input_set_changed")
    for name in names:
        raw = subprocess.check_output(["git", "-C", str(bin_repo), "show", BIN+":"+name])
        rel = Path(name).relative_to(PREFIX)
        require(len(rel.parts) == 1, "unexpected_historical_train_subdirectory")
        (inputs/rel).write_bytes(raw);(work/rel).write_bytes(raw)
        records.append({"repository": "Bin", "commit": BIN, "path": name,
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    model = ET.parse(work/"Model_00.xml")
    learner = model.getroot().find("./Model/Components/NeuronTimeLearner")
    require(learner is not None, "historical_learner_missing")
    require(learner.find("./Parameters/IsNeedToTrain").text.strip() == "0",
            "phasea_train_directory_is_not_saved_trained_control")
    if mode == "explicit_cold":
        for name in ("Model_00.xml", "Parameters_00.xml"):
            tree = ET.parse(work/name)
            params = tree.getroot().find("./Model/Components/NeuronTimeLearner/Parameters")
            require(params is not None, "historical_learner_parameters_missing")
            for key, value in COLD.items():
                prop = params.findall("./"+key)
                require(len(prop) == 1, "historical_cold_assignment_cardinality:"+key)
                prop[0].text = value
            tree.write(work/name, encoding="utf-8")
    # Real project dialect contains <00>; keep it lossless instead of XML parsing.
    project = (work/"Project.ini").read_text()
    enabled = mode != "state_disabled"
    project, count = re.subn(r"(<ProjectAutoSaveStateFlag>)0(</ProjectAutoSaveStateFlag>)",
                            lambda m: m[1]+str(int(enabled))+m[2], project)
    require(count == 1 and "<StatesFileName>" not in project, "historical_state_load_switch_ambiguous")
    project, count = re.subn(r"(</ParametersFileName>)", r"\1\n<StatesFileName>States_00.xml</StatesFileName>", project)
    require(count == 1 and "<GlobalTimeStep>2000</GlobalTimeStep>" in project,
            "historical_project_channel_mismatch")
    (work/"Project.ini").write_text(project)
    root = ET.Element("SaveProperties", {"ModelName": "Model"})
    native_model = ET.SubElement(root, "Model", {"Class": model.getroot().find("./Model").get("Class")})
    children = ET.SubElement(native_model, "Components")
    node = ET.SubElement(children, "NeuronTimeLearner", {"Class": learner.get("Class")})
    state = ET.SubElement(node, "State")
    if mode in ("native_state_reset", "state_disabled"):
        ET.SubElement(state, "ResetToUntrainedState", {"Type": "b", "PType": "258"}).text = "1"
    ET.ElementTree(root).write(work/"States_00.xml", encoding="utf-8")
    write(folder/"source-inputs.json", records)
    write(folder/"pre-run-files.json", [{"path": str(p.relative_to(folder)),
        "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(work.iterdir()) if p.is_file()])
    return work


def readback(work):
    root = ET.parse(work/"Model_00.xml").getroot()
    learner = root.find("./Model/Components/NeuronTimeLearner")
    params = learner.find("./Parameters")
    values = {key: [float(t.replace(",", ".")) for t in params.find(key).text.split()]
              for key in COLD}
    neuron = learner.find("./Components/Neuron")
    require(neuron is not None, "historical_effective_neuron_missing")
    graph, physics = {}, {}
    def walk(node, prefix):
        graph[prefix] = node.get("Class")
        for p in node.findall("./Parameters/*"):
            if p.tag in {"Resistance", "Capacity", "RestingResistance", "FBResistance", "SecretionTC",
                         "DissociationTC", "Type", "Weight", "InhibitionCoeff", "UsePresynapticInhibition"}:
                physics[prefix+"/"+p.tag] = " ".join((p.text or "").split()).replace(",", ".")
        for child in node.findall("./Components/*"):walk(child, prefix+"/"+child.tag)
    walk(neuron, "Neuron")
    tips = {}
    for child in neuron.findall("./Components/*"):
        if re.fullmatch(r"Dendrite\d+_\d+", child.tag):
            tip = child.find("./Components/ExcSynapse1/Parameters/Resistance")
            require(tip is not None, "historical_tip_synapse_missing")
            tips[child.tag] = float(tip.text.replace(",", "."))
    states = ET.parse(work/"States_00.xml").getroot()
    counter = states.find(".//Generator1/State/PulseCounter")
    reset = states.find(".//NeuronTimeLearner/State/ResetToUntrainedState")
    return {"learner": values, "tip_resistances": tips, "graph": graph, "selected_physics": physics,
            "generator_pulse_counter": int(counter.text) if counter is not None else None,
            "reset_flag": reset.text.strip() if reset is not None else None,
            "scope": "native graph/classes and selected child physics; not complete dynamic checkpoint"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args();runtime = load(args.runtime)
    source = args.source_root.resolve(strict=True);closure = source_closure(source)
    require(closure["root"]["head"] == ROOT and closure["Bin"]["head"] == BIN
            and closure["Libraries/Nmsdk-PulseLib"]["head"] == PULSE,
            "historical_coldstart_source_closure_mismatch")
    require(runtime["source_closure"] == closure, "historical_runtime_closure_mismatch")
    verify_runtime(runtime);args.output.mkdir(parents=True, exist_ok=False)
    write(args.output/"closure.json", closure);rows = {}
    for mode in ("trained_control", "native_state_reset", "explicit_cold", "state_disabled"):
        folder = args.output/mode;work = prepare(source/"Bin", folder, mode)
        shutil.copyfile(runtime["app_ini"]["path"], work/"NeuroModelerConsole.ini")
        require(hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest() ==
                runtime["app_ini"]["sha256"], "historical_runtime_ini_mismatch")
        print("COLDSTART", mode, flush=True)
        result = execute(runtime, ["-c", str(work/"Project.ini"), "-s", "-t", "0.0005", "-x", "-S"],
                         work, folder/"process", 120)
        require(result["execution"] == "completed", "historical_coldstart_process_failed:"+mode)
        actual = readback(work);write(folder/"readback.json", actual)
        if mode != "state_disabled":
            require(actual["generator_pulse_counter"] == 0, "preflight_already_presented_stimulus:"+mode)
        cold = mode in ("native_state_reset", "explicit_cold")
        require(actual["learner"]["DendriteLength"] == ([1]*4 if cold else [49, 41, 25, 1]),
                "historical_coldstart_length_mismatch:"+mode)
        if cold:
            for key, value in COLD.items():
                require(actual["learner"][key] == [float(t) for t in value.split()],
                        "historical_coldstart_parameter_mismatch:"+mode+":"+key)
            require(actual["tip_resistances"] == {"Dendrite"+str(i)+"_1": 86000000.0 for i in range(1, 5)},
                    "historical_coldstart_effective_tips_mismatch:"+mode)
        rows[mode] = {"execution": result, "readback": actual}
        write(args.output/"progress.json", rows)
    a, b = rows["native_state_reset"]["readback"], rows["explicit_cold"]["readback"]
    require(a["graph"] == b["graph"] and a["selected_physics"] == b["selected_physics"],
            "native_reset_explicit_cold_effective_model_disagree")
    require(source_closure(source) == closure, "historical_source_changed")
    write(args.output/"validation.json", {"kind": "historical_phasea_prestimulus_coldstart_gate",
        "operations": 4, "source_unchanged": True, "native_and_explicit_cold_agree": True,
        "state_load_switch_negative_control": True, "all_completed_before_first_input": True,
        "training_performed": False, "scientific_verdict": None})


if __name__ == "__main__":
    main()
