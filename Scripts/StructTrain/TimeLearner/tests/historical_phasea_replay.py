"""Owned saved-state Phase A replay on the original immutable August Git closure."""
import argparse
import copy
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


def add_native_temporal_observer(bin_repo, work):
    """Use the historical registered Rdk recorder; never calculate a neuron here."""
    raw = subprocess.check_output(["git", "-C", str(bin_repo), "show", BIN+
        ":Configs/SpikeSamples/StructTrain/SelectivityPhaseA/EXP00_baseline/Train/Model_00.xml"])
    template = ET.fromstring(raw).find(".//StatisticDoubleMatrix")
    require(template is not None and template.get("Class") == "UStatisticDoubleMatrix",
            "historical_stock_statistic_template_missing")
    path = work/"Model_00.xml";tree = ET.parse(path);model = tree.getroot().find("./Model")
    links = model.find("./Links");components = model.find("./Components")
    require(links is not None and components is not None
            and components.find("./ReplayTemporalStatistic") is None, "historical_observer_graph_invalid")
    observer = copy.deepcopy(template);observer.tag = "ReplayTemporalStatistic"
    for name, value in {"Activity": "1", "SavePath": "TemporalTrace", "SubFolderAfterResetFlag": "0",
                        "ForceCreateSavePath": "1", "TimeInterval": "0", "AverageMode": "0", "SaveMode": "0",
                        "WriteIndexFlag": "1", "WriteModelTimeStampFlag": "1"}.items():
        prop = observer.find("./Parameters/"+name)
        require(prop is not None, "historical_statistic_property_missing:"+name);prop.text = value
    components.append(observer)
    # Historical SumPotential is ptPubState, not ptOutput. UStatisticMatrix
    # opens files through FindOutputProperty, so a state-only connection
    # silently produces no file. Record the two native channel outputs instead;
    # NPulseMembraneCommon::ACalculate defines SumPotential as their sum.
    # Preserve the unmodified historical executable and expose this derivation.
    descriptors = [("NeuronTimeLearner.Neuron.Soma"+str(i)+"."+channel, "Output",
                    "soma"+str(i)+"_"+role)
                   for i in range(1, 5)
                   for channel, role in (("ExcChannel", "exc"), ("InhChannel", "inh"))]
    descriptors += [("NeuronTimeLearner.Neuron", "SomaSumPotential", "neuron_soma_sum")]
    descriptors += [("NeuronTimeLearner.DatasetMatrix.Generator1", "Output", "stimulus"),
                    ("NeuronTimeLearner.Neuron.LTZone", "Output", "lt_spikes"),
                    ("NeuronTimeLearner", "SomaNeuronAmplitude", "learner_cached_somas")]
    for owner, prop, role in descriptors:
        link = ET.SubElement(links, "elem", {"Type": "ULink"})
        ET.SubElement(link, "Item", {"Type": "ULinkSide", "Index": "-1", "Name": prop}).text = owner
        ET.SubElement(link, "Connector", {"Type": "ULinkSide", "Index": "-1", "Name": "InputMatrixData"}).text = observer.tag
    links.set("Size", str(len(links)))
    tree.write(path, encoding="utf-8", xml_declaration=False)
    return {"component": observer.tag, "class": observer.get("Class"), "streams":
            [{"source": owner+"."+prop, "role": role} for owner, prop, role in descriptors],
            "source_code_patched": False, "sampling": "native scheduler, TimeInterval0; no averaging",
            "soma_derivation": "soma_i = Soma_i.ExcChannel.Output + Soma_i.InhChannel.Output; "
                "historical NPulseMembraneCommon::ACalculate; state-only SumPotential cannot be recorded "
                "by historical UStatisticMatrix::FindOutputProperty"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--observe", action="store_true", help="add historical stock UStatisticDoubleMatrix")
    parser.add_argument("--baseline", type=Path, help="untouched completed replay required for observer comparison")
    args = parser.parse_args()
    source = args.source_root.resolve(strict=True);runtime = load(args.runtime)
    closure = source_closure(source)
    require(closure["root"]["head"] == ROOT and closure["Bin"]["head"] == BIN
            and closure["Libraries/Nmsdk-PulseLib"]["head"] == PULSE, "historical_phasea_closure_mismatch")
    require(runtime["source_closure"] == closure, "historical_runtime_closure_mismatch")
    verify_runtime(runtime)
    require(args.observe == (args.baseline is not None), "observer_requires_untouched_baseline")
    args.output.mkdir(parents=True, exist_ok=False)
    rows = [];write(args.output/"closure.json", closure)
    for name, relative, old_correct in CASES:
        folder = args.output/name
        inputs, work, reference, records = prepare_case(source/"Bin", relative, folder)
        observer = add_native_temporal_observer(source/"Bin", work) if args.observe else None
        write(folder/"observer.json", observer)
        copied_ini = work/"NeuroModelerConsole.ini"
        shutil.copyfile(runtime["app_ini"]["path"], copied_ini)
        require(hashlib.sha256(copied_ini.read_bytes()).hexdigest() == runtime["app_ini"]["sha256"],
                "historical_cwd_runtime_ini_mismatch")
        before = model_readback(work/"Model_00.xml")
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
        passive = None
        if args.observe:
            prior = args.baseline/name/"work/SelectivityLog/results.csv"
            require(prior.is_file(), "untouched_baseline_missing")
            passive = prior.read_bytes() == actual_csv.read_bytes()
            trace_files = []
            for stream in observer["streams"]:
                matches = [p for p in (work/"TemporalTrace").glob("*.txt")
                           if p.name.endswith(stream["source"]+".txt")]
                require(len(matches) == 1 and matches[0].stat().st_size > 0,
                        "historical_native_trace_missing:"+stream["role"])
                trace_files.append({**stream, "path": str(matches[0].relative_to(folder)),
                    "bytes": matches[0].stat().st_size,
                    "sha256": hashlib.sha256(matches[0].read_bytes()).hexdigest()})
            write(folder/"trace-files.json", trace_files)
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
                  "native_observer": observer, "csv_byte_equal_to_untouched_replay": passive,
                  "temporal_report_complete": False, "scientific_verdict": None}
        write(folder/"comparison.json", report)
        rows.append({"name": name, "archived_correct": old_correct,
                     "replay_correct": actual["native_match_count"], "counts": actual["reported_counts"],
                     "same_reported_counts": report["same_reported_counts"],
                     "graph_paths_classes_equal": report["graph_paths_classes_equal"],
                     "selected_parameter_differences": len(differences)})
        rows[-1]["csv_byte_equal_to_untouched_replay"] = passive
        write(args.output/"progress.json", rows)
    require(source_closure(source) == closure, "historical_source_changed_during_replay")
    write(args.output/"validation.json", {"kind": "phasea_historical_saved_state_replay", "rows": rows,
        "operations": len(rows), "historical_root": ROOT, "original_input_order_and_isis": True,
        "cold_retrain_performed": False, "robustness_controls_performed": False,
        "temporal_report_complete": False, "strict_evaluation_verdict": None,
        "source_unchanged": True, "limitations": "Legacy CSV has no complete-window/late-spike evidence; full soma/input traces still required. Selected XML readback is not a complete physics fingerprint."})


if __name__ == "__main__":
    main()
