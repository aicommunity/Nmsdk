"""Owned saved-state Phase A replay on the original immutable August Git closure."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from ..historical_selectivity import analyze_historical_csv
from ..native_evidence import load, require
from ..process_runner import execute, verify_runtime
from ..runtime import source_closure

ROOT = "de02a3809395dd0bbd11e2ba792bfc04a51c89f3"
BIN = "1c1464e248f8744e858bd66df0be99e39969fd65"
PULSE = "cbf76fbe077a7003dccf72b142d7136721fa1afb"
CASES = (("baseline", "EXP00_baseline/Test", 4),
         ("threshold0130", "EXP01_ltz_threshold_sweep/Test_thr00130", 5),
         ("threshold0135", "EXP01_ltz_threshold_sweep/Test_thr00135", 6))


def write(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def model_readback(path):
    root = ET.parse(path).getroot()
    graph = [];parameters = {}
    def walk(node, prefix):
        if "Class" in node.attrib:
            graph.append({"path": prefix, "class": node.attrib["Class"]})
            for prop in node.findall("./Parameters/*"):
                # Descriptive readback, not a complete physical-model fingerprint.
                if prop.tag in {"DendriteLength", "TipSynapseResistance", "IsNeedToTrain",
                                "FixedLTZThreshold", "UseFixedLTZThreshold", "Threshold",
                                "Resistance", "Capacity", "SecretionTC", "DissociationTC"}:
                    parameters[prefix+"/"+prop.tag] = " ".join((prop.text or "").split())
        for child in node.findall("./Components/*"):
            walk(child, prefix+"/"+child.tag)
    model = root.find("./Model")
    require(model is not None, "historical_model_root_missing")
    walk(model, "Model")
    return {"graph": graph, "selected_parameters": parameters, "full_physics_fingerprint": False}


def prepare_case(bin_repo, relative, directory):
    prefix = "Configs/SpikeSamples/StructTrain/SelectivityPhaseA/"+relative+"/"
    names = subprocess.check_output(["git", "-C", str(bin_repo), "ls-tree", "-r", "-z",
                                    "--name-only", BIN, "--", prefix]).decode().split("\0")
    inputs = directory/"inputs";work = directory/"work"
    inputs.mkdir(parents=True);work.mkdir()
    records = []
    for name in names:
        if not name:
            continue
        rel = Path(name).relative_to(prefix)
        if any(part in {"SelectivityLog", "StatisticLog", "EventsLog"} for part in rel.parts) or rel.name == "results.csv":
            continue
        raw = subprocess.check_output(["git", "-C", str(bin_repo), "show", BIN+":"+name])
        target = inputs/rel;target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(raw)
        dest = work/rel;dest.parent.mkdir(parents=True, exist_ok=True);dest.write_bytes(raw)
        records.append({"repository": "Bin", "commit": BIN, "path": name,
                        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    for filename in ("Model_00.xml", "Parameters_00.xml"):
        tree = ET.parse(inputs/filename).getroot()
        flag = tree.find(".//NeuronTimeLearner/Parameters/IsNeedToTrain")
        require(flag is not None and flag.text.strip() == "0", "replay_must_not_start_training")
    require("<GlobalTimeStep>2000</GlobalTimeStep>" in (inputs/"Project.ini").read_text(),
            "historical_frequency_mismatch")
    require(not list(work.rglob("results.csv")), "historical_results_copied_into_new_run")
    ref = directory/"reference.csv"
    ref.write_bytes(subprocess.check_output(["git", "-C", str(bin_repo), "show",
                                           BIN+":"+prefix+"SelectivityLog/results.csv"]))
    return inputs, work, ref, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_root.resolve(strict=True);runtime = load(args.runtime)
    closure = source_closure(source)
    require(closure["root"]["head"] == ROOT and closure["Bin"]["head"] == BIN
            and closure["Libraries/Nmsdk-PulseLib"]["head"] == PULSE, "historical_phasea_closure_mismatch")
    require(runtime["source_closure"] == closure, "historical_runtime_closure_mismatch")
    verify_runtime(runtime)
    args.output.mkdir(parents=True, exist_ok=False)
    rows = [];write(args.output/"closure.json", closure)
    for name, relative, old_correct in CASES:
        folder = args.output/name
        inputs, work, reference, records = prepare_case(source/"Bin", relative, folder)
        copied_ini = work/"NeuroModelerConsole.ini"
        shutil.copyfile(runtime["app_ini"]["path"], copied_ini)
        require(hashlib.sha256(copied_ini.read_bytes()).hexdigest() == runtime["app_ini"]["sha256"],
                "historical_cwd_runtime_ini_mismatch")
        before = model_readback(inputs/"Model_00.xml")
        write(folder/"inputs.json", records)
        print("REPLAY", name, flush=True)
        result = execute(runtime, ["-c", str(work/"Project.ini"), "-s", "-t", "40", "-x", "-S"],
                         work, folder/"process", 900)
        require(result["execution"] == "completed", "historical_replay_execution_failed:"+name)
        require(hashlib.sha256(copied_ini.read_bytes()).hexdigest() == runtime["app_ini"]["sha256"],
                "historical_cwd_ini_changed")
        actual_csv = work/"SelectivityLog/results.csv"
        original = analyze_historical_csv(reference, [str(i) for i in range(8)])
        actual = analyze_historical_csv(actual_csv, [str(i) for i in range(8)])
        require(original["native_match_count"] == old_correct, "wrong_original_phasea_reference")
        require([(r["trial_id"], r["label"], r["isis"]) for r in original["rows"]]
                == [(r["trial_id"], r["label"], r["isis"]) for r in actual["rows"]],
                "historical_order_labels_or_patterns_changed")
        after = model_readback(work/"Model_00.xml")
        differences = [{"parameter": key, "saved_source": value, "post_run": after["selected_parameters"].get(key)}
                       for key, value in before["selected_parameters"].items()
                       if value != after["selected_parameters"].get(key)]
        report = {"name": name, "protocol": "saved_state_replay_original_order_iti_native_reset",
                  "source_config": relative, "execution": result, "original": original, "replay": actual,
                  "same_reported_counts": original["reported_counts"] == actual["reported_counts"],
                  "saved_source_graph": before, "post_run_graph": after,
                  "graph_paths_classes_equal": before["graph"] == after["graph"],
                  "selected_parameter_differences": differences, "full_frozen_model_verified": False,
                  "temporal_report_complete": False, "scientific_verdict": None}
        write(folder/"comparison.json", report)
        rows.append({"name": name, "archived_correct": old_correct,
                     "replay_correct": actual["native_match_count"], "counts": actual["reported_counts"],
                     "same_reported_counts": report["same_reported_counts"],
                     "graph_paths_classes_equal": report["graph_paths_classes_equal"],
                     "selected_parameter_differences": len(differences)})
        write(args.output/"progress.json", rows)
    require(source_closure(source) == closure, "historical_source_changed_during_replay")
    write(args.output/"validation.json", {"kind": "phasea_historical_saved_state_replay", "rows": rows,
        "operations": len(rows), "historical_root": ROOT, "original_input_order_and_isis": True,
        "cold_retrain_performed": False, "robustness_controls_performed": False,
        "temporal_report_complete": False, "strict_evaluation_verdict": None,
        "source_unchanged": True, "limitations": "Legacy CSV has no complete-window/late-spike evidence; full soma/input traces still required. Selected XML readback is not a complete physics fingerprint."})


if __name__ == "__main__":
    main()
