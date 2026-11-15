"""Native historical Phase A config/model helpers, without import-time work.

Shared by the original replay harness and explicit frozen protocol controls.
These routines prepare native objects; they do not calculate a model, tune a
threshold, infer trial completeness, or create a training certificate.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from .native_evidence import require
from .model_identity import canonical_model_sha256

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
    # Preserve the original historical load protocol: Model mode1 initializes
    # dimensioned learner caches, followed by Parameters mode0. Mode0 in both
    # files leaves the old learner's default two-row amplitude buffer for N4.
    model_mode = old.find("./Parameters/StructureBuildMode").text.strip()
    require(model_mode == "1", "historical_model_load_mode_changed")
    for key, value in {"StructureBuildMode": model_mode, "IsNeedToTrain": "0",
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
    mode = old.find("./Components/NeuronTimeLearner/Parameters/StructureBuildMode")
    require(mode is not None and mode.text.strip() == "0", "historical_parameter_load_mode_changed")
    root.remove(old)
    model = copy.deepcopy(ET.parse(work/"Model_00.xml").getroot().find("./Model"))
    for node in model.iter():
        for child in list(node):
            if child.tag == "Links":node.remove(child)
    model.find("./Components/NeuronTimeLearner/Parameters/StructureBuildMode").text = "0"
    root.append(model);ET.ElementTree(root).write(work/"Parameters_00.xml", encoding="utf-8")

def recognition_identity(solo, threshold):
    snapshot = copy.deepcopy(solo["snapshot"])
    nodes = [n for n in snapshot["nodes_in_native_order"] if n["path"] == "NeuronTimeLearner.Neuron.LTZone"]
    require(len(nodes) == 1, "historical_ltz_node_ambiguous")
    props = [p for p in nodes[0]["parameters"] if p["tag"] == "Threshold"]
    require(len(props) == 1 and props[0]["value"]["kind"] == "binary64", "historical_ltz_threshold_unsupported")
    props[0]["value"]["values"] = [float(threshold).hex()]
    return canonical_model_sha256(snapshot)
