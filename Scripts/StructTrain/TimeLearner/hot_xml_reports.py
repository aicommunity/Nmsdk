"""Phase-matched graph and complete waveform audit of native warm XML loads."""
import argparse
import copy
import csv
from decimal import Decimal, InvalidOperation
import io
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from .hot_readout_reports import read_case as read_warm
from .loaded_readout_reports import graph_projection, render, snapshot
from .native_evidence import EvidenceError, parse_json_bytes, require
from .plotting import plotting_runtime


def conditions():
    for branch, count, frequency, state in itertools.product((False, True), (1, 2, 4, 6), (2000, 20000), (False, True)):
        yield ("Branch" if branch else "Classic")+f"-N{count}-f{frequency}-state{int(state)}", branch, count, frequency, state


def read_case(folder, branch, count, frequency, state):
    warm = read_warm(folder, branch, count, frequency, kind="native_hot_xml_reset", schema_version=3,
                     duration_denominator=10)
    summary = warm["summary"];observation = summary["observation"];records = summary["primary"]
    def raw(name):
        data, record = snapshot(folder, name);records.append(record);return data
    require(observation.get("serialized_while_warm") is True and observation.get("include_state") is state
            and type(observation.get("warm_sample_count")) is int and observation["warm_sample_count"] == frequency//10
            and type(observation.get("warm_duration_s")) is float and observation["warm_duration_s"] == .1,
            "hot_xml_wrong_protocol")
    require(summary["observed_lifecycle"] == "consistent_readout", "hot_xml_stale_loaded_readout")
    require(raw("load-errors.txt").strip() == b"", "hot_xml_native_load_errors")
    rest, source, loaded = [parse_json_bytes(raw(n)) for n in
                              ("source-rest-model.json", "source-model.json", "loaded-model.json")]
    rest_projection, rest_hash = graph_projection(rest, frequency)
    source_projection, _ = graph_projection(source, frequency)
    loaded_projection, loaded_hash = graph_projection(loaded, frequency)
    require(rest_projection == loaded_projection and rest_hash == loaded_hash, "hot_xml_rest_graph_changed")
    # TimeConstant is ptPubState in NPulseChannel. Preserve this diagnostic;
    # compare warm parameters/links without treating it as persistent physics.
    def persistent_projection(graph, projection):
        result = copy.deepcopy(projection);states = {};nodes = {n["path"]: n for n in graph["nodes"]}
        for node in result["nodes"]:
            if "time_constant_s" in node["physics"]:
                prop = nodes[node["path"]]["properties"]["TimeConstant"]
                require(prop["mask"] & 2 and not prop["mask"] & 1, "hot_xml_tau_not_state")
                states[node["path"]] = node["physics"].pop("time_constant_s")
        return result, states
    persistent, rest_tau = persistent_projection(rest, rest_projection)
    warm_persistent, warm_tau = persistent_projection(source, source_projection)
    require(persistent == warm_persistent, "hot_xml_warm_parameters_changed")
    learners = [n for n in rest_projection["nodes"] if n["path"].endswith(".Learner")]
    require(len(learners) == 1 and learners[0]["class"] ==
            ("NNeuronTimeLearnerBranch" if branch else "NNeuronTimeLearner"), "hot_xml_wrong_learner")
    p = learners[0]["parameters"]
    require(p["NumInputDendrite"]["rdk_value"].strip() == str(count)
            and p["ControllerVersion"]["rdk_value"].strip() == "1"
            and p["StructureBuildMode"]["rdk_value"].strip() == "0"
            and p["IsNeedToTrain"]["rdk_value"].strip() in {"false", "0"}, "hot_xml_wrong_frozen_configuration")
    xml = ET.fromstring(raw("hot-model.xml"));saved = xml.find("./Model/Components/Learner/State")
    require((saved is not None) == state, "hot_xml_state_flag_mismatch")
    rounding = []
    if state:
        matrix = saved.find("SomaNeuronAmplitude")
        require(matrix is not None and matrix.get("Rows") == str(count+1) and matrix.get("Cols") == "1",
                "hot_xml_saved_readout_dimension")
        history = observation["warm"].get("per_input_soma_readout")
        require(type(history) is list and len(history) == count and
                all(type(v) in (int,float) and math.isfinite(v) for v in history), "hot_xml_invalid_saved_history")
        tokens = (matrix.text or "").split();expected = [observation["warm"]["cached_total"]]+history
        require(len(tokens) == len(expected), "hot_xml_saved_readout_dimension")
        for token, value in zip(tokens, expected):
            try:decimal = Decimal(token);number = float(decimal)
            except (ValueError, InvalidOperation) as error:raise EvidenceError("hot_xml_invalid_saved_number") from error
            require(math.isfinite(number), "hot_xml_invalid_saved_number")
            # Native XML text uses limited decimal precision. This bound only
            # checks that saved dynamic text represents the actual warm state.
            bound = 0.0 if number == 0 else min(float(Decimal(1).scaleb(decimal.as_tuple().exponent))/2,
                                               .5*10**(math.floor(math.log10(abs(number)))-5))
            require(abs(number-value) <= bound+max(1e-15, abs(value)*1e-14), "hot_xml_saved_state_not_warm")
            rounding.append(bound)
    somas = summary["somas"];header = ["time_s", "warm_input", "replay_input"]
    for i in range(1, somas+1):header += [f"warm_soma{i}", f"replay_soma{i}"]
    reader = csv.reader(io.StringIO(raw("replay.csv").decode("utf-8"), newline=""))
    require(next(reader, None) == header, "hot_xml_replay_schema")
    rows = []
    for index, fields in enumerate(reader):
        require(len(fields) == len(header), "hot_xml_replay_width")
        try:values = [float(v) for v in fields]
        except ValueError as error:raise EvidenceError("hot_xml_invalid_replay_number") from error
        require(all(math.isfinite(v) for v in values), "hot_xml_invalid_replay_number")
        require(index < len(warm["rows"]) and abs(values[0]-index/frequency) < 1e-12, "hot_xml_replay_clock")
        original = warm["rows"][index]
        require(values[1] == values[2] == original[2], "hot_xml_replay_stimulus_changed")
        for i in range(somas):
            require(abs(values[3+2*i]-original[3+2*i]) <= 1e-12, "hot_xml_source_waveform_changed")
            require(abs(values[3+2*i]-values[4+2*i]) <= 1e-12, "hot_xml_replay_waveform_changed")
        rows.append(values)
    require(len(rows) == frequency//10, "hot_xml_incomplete_replay")
    summary.update(saved_state=state, rest_graph_sha256=rest_hash, loaded_graph_sha256=loaded_hash,
                   warm_time_constants=warm_tau, rest_time_constants=rest_tau, saved_state_decimal_bounds=rounding)
    return {"rows": rows, "summary": summary}


def audit_run(root):
    validation = parse_json_bytes(snapshot(root, "validation.json")[0]);g = validation["gtest"];e = validation["execution"]
    require(g["tests"] == "32" and g["failures"] == g["errors"] == g["disabled"] == "0"
            and e["execution"] == "completed" and e["returncode"] == 0, "hot_xml_native_not_passed")
    tree = ET.fromstring(snapshot(root, "gtest.xml")[0]);cases = tree.findall(".//testcase")
    require(len(cases) == 32 and not tree.findall(".//failure") and not tree.findall(".//skipped"), "hot_xml_incomplete_native_cases")
    seen = []
    for c in cases:
        v = c.get("value_param", "");require(v.startswith("(") and v.endswith(")"), "hot_xml_invalid_native_condition")
        seen.append(parse_json_bytes(("["+v[1:-1]+"]").encode()))
    expected = list(conditions())
    require(sorted(map(str, seen)) == sorted(str(list(c[1:])) for c in expected), "hot_xml_native_condition_set")
    require({p.name for p in (root/"artifacts").iterdir()} == {c[0] for c in expected}, "hot_xml_artifact_condition_set")
    data = {name: read_case(root/"artifacts"/name, *spec) for name, *spec in expected}
    return data, {"kind": "native_hot_xml_report", "schema_version": 1, "native_validation": validation,
                  "cases": {k: v["summary"] for k, v in data.items()},
                  "case_soma_pairs": sum(v["summary"]["somas"] for v in data.values()),
                  "scientific_verdict": None, "training_certificate": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True);parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plots", action="store_true");args = parser.parse_args()
    data, report = audit_run(args.input);runtime = plotting_runtime() if args.plots else None
    args.output.mkdir(parents=True, exist_ok=False)
    if args.plots:
        for name, value in data.items():
            report["cases"][name]["figures"] = render(value, args.output/name, source_label="Original warm soma",
                loaded_label="Loaded replay soma", context="Native hot XML load, Reset, replay; not selectivity")
    report["plotting_runtime"] = runtime
    (args.output/"validation.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")


if __name__ == "__main__":main()
