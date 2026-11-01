"""Full native cold-model transfer into original-protocol frozen Phase A tests."""
import argparse
import copy
import hashlib
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from ..historical_model import serialized_neuron
from ..historical_selectivity import analyze_historical_csv
from ..model_identity import canonical_model_sha256
from ..native_evidence import load, require
from ..process_runner import execute, verify_runtime
from ..runtime import source_closure
from .historical_phasea_replay import (ROOT, BIN, PULSE, CASES, prepare_case,
                                       add_native_temporal_observer, write)


def neuron_destination(connector):
    name = (connector.text or "").strip()
    return name == "NeuronTimeLearner.Neuron" or name.startswith("NeuronTimeLearner.Neuron.")


def transfer_model(work, cold_model, threshold):
    """Import the entire fresh learner graph; replace only declared probe data."""
    source = ET.parse(cold_model).getroot().find("./Model")
    tree = ET.parse(work/"Model_00.xml");model = tree.getroot().find("./Model")
    components = model.find("./Components")
    old = components.find("./NeuronTimeLearner")
    fresh = copy.deepcopy(source.find("./Components/NeuronTimeLearner"))
    require(fresh is not None and old is not None, "historical_transfer_learner_missing")
    require(fresh.find("./Parameters/IsNeedToTrain").text.strip() == "0", "historical_train_not_done")
    dataset = old.find("./Components/DatasetMatrix")
    children = fresh.find("./Components");previous = children.find("./DatasetMatrix")
    require(dataset is not None and previous is not None, "historical_probe_dataset_missing")
    position = list(children).index(previous);children.remove(previous)
    children.insert(position, copy.deepcopy(dataset))
    params = fresh.find("./Parameters")
    for key, value in {"StructureBuildMode": "0", "IsNeedToTrain": "0",
                       "LTZThreshold": str(threshold), "FixedLTZThreshold": str(threshold),
                       "UseFixedLTZThreshold": "0"}.items():
        matches = params.findall("./"+key)
        require(len(matches) == 1, "historical_frozen_parameter_ambiguous:"+key);matches[0].text = value
    position = list(components).index(old);components.remove(old);components.insert(position, fresh)
    links = model.find("./Links")
    require(links is not None, "historical_transfer_links_missing")
    # Preserve native monitoring links, replacing every neuron inbound edge with
    # the fresh trained export. There is no fallback to the template's graph.
    for link in list(links):
        for connector in list(link.findall("./Connector")):
            if neuron_destination(connector):link.remove(connector)
        if not link.findall("./Connector"):links.remove(link)
    for link in source.findall("./Links/*"):
        copied = copy.deepcopy(link)
        for connector in list(copied.findall("./Connector")):
            if not neuron_destination(connector):copied.remove(connector)
        if copied.findall("./Connector"):links.append(copied)
    links.set("Size", str(len(links)));tree.write(work/"Model_00.xml", encoding="utf-8")
    return fresh


def parameter_export(work):
    # Native parameter files contain the complete fresh component parameter tree,
    # not a template overlay with stale child Rs, C, morphology or dataset rows.
    root = ET.parse(work/"Parameters_00.xml").getroot()
    old = root.find("./Model");require(old is not None, "historical_parameters_root_missing")
    root.remove(old)
    model = copy.deepcopy(ET.parse(work/"Model_00.xml").getroot().find("./Model"))
    for node in model.iter():
        for child in list(node):
            if child.tag == "Links":node.remove(child)
    root.append(model);ET.ElementTree(root).write(work/"Parameters_00.xml", encoding="utf-8")


def recognition_identity(solo, threshold):
    snapshot = copy.deepcopy(solo["snapshot"])
    nodes = [n for n in snapshot["nodes_in_native_order"] if n["path"] == "NeuronTimeLearner.Neuron.LTZone"]
    require(len(nodes) == 1, "historical_ltz_node_ambiguous")
    props = [p for p in nodes[0]["parameters"] if p["tag"] == "Threshold"]
    require(len(props) == 1 and props[0]["value"]["kind"] == "binary64", "historical_ltz_threshold_unsupported")
    props[0]["value"]["values"] = [float(threshold).hex()]
    return canonical_model_sha256(snapshot)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--cold-train", type=Path, required=True)
    parser.add_argument("--untouched-replay", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args();runtime = load(args.runtime)
    source = args.source_root.resolve(strict=True);closure = source_closure(source)
    require(closure["root"]["head"] == ROOT and closure["Bin"]["head"] == BIN and
            closure["Libraries/Nmsdk-PulseLib"]["head"] == PULSE, "historical_coldtest_closure_mismatch")
    require(runtime["source_closure"] == closure, "historical_runtime_closure_mismatch");verify_runtime(runtime)
    train = load(args.cold_train/"validation.json")
    require(train["execution"] == "completed" and train["training_outcome"] == "legacy_done_uncertified"
            and train["native_cold_start_verified"] is True, "historical_coldtrain_not_completed")
    cold_model = args.cold_train/"train/work/Model_00.xml"
    raw_sha = hashlib.sha256(cold_model.read_bytes()).hexdigest()
    solo = serialized_neuron(cold_model)
    original = serialized_neuron(args.untouched_replay/"baseline/inputs/Model_00.xml")
    require(solo["snapshot"] == original["snapshot"], "cold_model_differs_from_untouched_replay_model")
    args.output.mkdir(parents=True, exist_ok=False);rows = []
    write(args.output/"closure.json", closure)
    write(args.output/"train-model-identity.json", {"source_model_sha256": raw_sha,
        "serialized_neuron_sha256": solo["sha256"], "nodes": solo["nodes"], "edges": solo["inbound_edges"],
        "trained_model_equals_original_serialized_neuron": True, "training_certificate": None})
    for (name, relative, correct), threshold in zip(CASES, (.0115, .0130, .0135)):
        folder = args.output/name
        inputs, work, reference, records = prepare_case(source/"Bin", relative, folder)
        transfer_model(work, cold_model, threshold)
        observer = add_native_temporal_observer(source/"Bin", work)
        parameter_export(work)
        require(serialized_neuron(work/"Model_00.xml")["sha256"] == solo["sha256"],
                "historical_full_model_transfer_changed_neuron")
        write(folder/"observer.json", observer);write(folder/"inputs.json", records)
        shutil.copyfile(runtime["app_ini"]["path"], work/"NeuroModelerConsole.ini")
        copied = hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest()
        require(copied == runtime["app_ini"]["sha256"], "historical_coldtest_ini_mismatch")
        prepared = folder/"prepared";prepared.mkdir()
        for p in work.iterdir():
            if p.is_file():shutil.copyfile(p, prepared/p.name)
        print("COLD_FROZEN_TEST", name, flush=True)
        result = execute(runtime, ["-c", str(work/"Project.ini"), "-s", "-t", "40", "-x", "-S"],
                         work, folder/"process", 900)
        require(result["execution"] == "completed", "historical_coldtest_execution_failed:"+name)
        require(hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest() == copied,
                "historical_coldtest_ini_changed")
        identity = serialized_neuron(work/"Model_00.xml")
        require(identity["sha256"] == recognition_identity(solo, threshold),
                "historical_frozen_neuron_or_native_threshold_changed:"+name)
        for key, expected in (("StructureBuildMode", "0"), ("IsNeedToTrain", "0")):
            actual = ET.parse(work/"Model_00.xml").getroot().find(".//NeuronTimeLearner/Parameters/"+key)
            require(actual is not None and actual.text.strip() == expected, "historical_frozen_control_changed:"+key)
        actual_csv = work/"SelectivityLog/results.csv"
        actual = analyze_historical_csv(actual_csv, [str(i) for i in range(8)])
        archived = analyze_historical_csv(reference, [str(i) for i in range(8)])
        prior = args.untouched_replay/name/"work/SelectivityLog/results.csv"
        passive = prior.read_bytes() == actual_csv.read_bytes()
        require(passive, "cold_frozen_csv_differs_from_equal_model_untouched_replay")
        traces = []
        for stream in observer["streams"]:
            matches = [p for p in (work/"TemporalTrace").glob("*.txt") if p.name.endswith(stream["source"]+".txt")]
            require(len(matches) == 1 and matches[0].stat().st_size > 0, "historical_coldtest_trace_missing:"+stream["role"])
            p = matches[0];traces.append({**stream, "path": str(p.relative_to(folder)),
                "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
        write(folder/"trace-files.json", traces)
        write(folder/"comparison.json", {"name": name, "original": archived, "replay": actual,
            "csv_byte_equal_to_untouched_replay": passive, "frozen_neuron_sha256": identity["sha256"],
            "source_cold_neuron_sha256": solo["sha256"], "threshold": threshold,
            "full_cold_graph_imported": True, "scientific_verdict": None})
        rows.append({"name": name, "correct": actual["native_match_count"], "counts": actual["reported_counts"],
                     "csv_byte_equal_to_untouched_replay": passive, "frozen_neuron_sha256": identity["sha256"]})
        write(args.output/"progress.json", rows)
    require(hashlib.sha256(cold_model.read_bytes()).hexdigest() == raw_sha, "historical_train_export_changed")
    require(source_closure(source) == closure, "historical_source_changed_during_coldtest")
    write(args.output/"validation.json", {"kind": "historical_cold_model_full_import_frozen_test",
        "rows": rows, "operations": 3, "full_cold_graph_imported": True, "train_export_unchanged": True,
        "source_unchanged": True, "all_neuron_serialized_state_frozen_at_declared_threshold": True,
        "independent_evaluation": False, "temporal_report_complete": False, "scientific_verdict": None})


if __name__ == "__main__":
    main()
