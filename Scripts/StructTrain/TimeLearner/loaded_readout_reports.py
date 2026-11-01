"""Audit/plot actual native mode0 XML roundtrips; no classification verdict.

Rdk textual parameters are compared conservatively within each worker. This
readback projection is not ModelArchive or a controller/dynamics checkpoint.
"""
import argparse
import bisect
import csv
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, parse_json_bytes, require
from .plotting import padded_limits, plotting_runtime, time_views


def conditions():
    for branch, count, frequency, state in itertools.product((False, True), (1, 2, 4, 6),
                                                            (2000, 20000), (False, True)):
        name = ("Branch" if branch else "Classic")+f"-N{count}-f{frequency}-state{int(state)}"
        yield name, branch, count, frequency, state


def snapshot(folder, name):
    path = (folder/name).resolve(strict=True)
    require(path.is_relative_to(folder.resolve()), "readout_artifact_path_escape")
    before = path.stat(); raw = path.read_bytes(); after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
            "readout_artifact_changed")
    return raw, {"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def graph_projection(graph, frequency):
    require(graph.get("kind") == "effective_model_readback" and type(graph.get("schema_version")) is int and
            graph["schema_version"] == 1,
            "readout_unknown_graph_schema")
    require(graph.get("valid") is True and graph.get("diagnostics") == [] and
            graph.get("lifecycle_mutated_by_inspector") is False, "readout_invalid_graph")
    nodes = []
    require(isinstance(graph.get("nodes"), list) and graph["nodes"], "readout_missing_graph_nodes")
    for node in graph["nodes"]:
        require(node["frequency_hz"] == frequency, "readout_graph_frequency")
        nodes.append({"path": node["path"], "class": node["class"], "active": node["active"],
                      "frequency_hz": node["frequency_hz"], "child_order": node["child_order"],
                      "physics": node["physics"],
                      "parameters": {k: v for k, v in node["properties"].items() if v["mask"] & 1},
                      "caches": {k: v for k, v in node.items() if k.startswith("cached_")}})
    require(len({n["path"] for n in nodes}) == len(nodes), "readout_duplicate_graph_node")
    result = {"schema": "native_readout_graph_projection_v1", "nodes": nodes, "links": graph["links"]}
    # Also rejects nonfinite JSON numbers anywhere in the selected physical graph.
    return result, canonical_model_sha256(result)


def read_case(folder, branch, count, frequency, state):
    records = []
    def raw(name):
        value, record = snapshot(folder, name);records.append(record);return value
    source, loaded = [parse_json_bytes(raw(name)) for name in ("source-model.json", "loaded-model.json")]
    before, identity = graph_projection(source, frequency)
    after, loaded_identity = graph_projection(loaded, frequency)
    require(before == after and identity == loaded_identity, "readout_graph_changed_on_load")
    learner = [n for n in before["nodes"] if n["path"].endswith(".Learner")]
    require(len(learner) == 1 and learner[0]["class"] ==
            ("NNeuronTimeLearnerBranch" if branch else "NNeuronTimeLearner"), "readout_wrong_learner")
    parameters = learner[0]["parameters"]
    require(parameters["NumInputDendrite"]["rdk_value"].strip() == str(count) and
            parameters["ControllerVersion"]["rdk_value"].strip() == "1" and
            parameters["StructureBuildMode"]["rdk_value"].strip() == "0" and
            parameters["IsNeedToTrain"]["rdk_value"].strip() in {"0", "false"},
            "readout_wrong_frozen_configuration")
    dimensions = parse_json_bytes(raw("loaded-dimensions.json"))
    require(dimensions == {"inputs": count, "soma_rows": count+1, "dendrite_rows": count+1},
            "readout_wrong_loaded_dimensions")
    require(raw("load-errors.txt").strip() == b"", "readout_native_load_error")
    xml = ET.fromstring(raw("model.xml"))
    has_state = xml.find("./Model/Components/Learner/State") is not None
    require(has_state == state, "readout_wrong_state_protocol")
    somas = 1 if branch else count
    header = ["time_s", "source_input", "loaded_input"]
    for i in range(1, somas+1):header += [f"source_soma{i}", f"loaded_soma{i}"]
    reader = csv.reader(io.StringIO(raw("roundtrip.csv").decode("utf-8"), newline=""))
    require(next(reader, None) == header, "readout_csv_schema")
    rows = []
    for index, fields in enumerate(reader):
        require(len(fields) == len(header), "readout_csv_width")
        try:values = [float(v) for v in fields]
        except ValueError as error:raise EvidenceError("readout_invalid_number") from error
        require(all(math.isfinite(v) for v in values), "readout_nonfinite_sample")
        require(abs(values[0]-index/frequency) < 1e-12, "readout_sample_clock")
        require(values[1] == values[2] and values[1] >= 0, "readout_stimulus_disagreement")
        rows.append(values)
    require(len(rows) == frequency//10, "readout_incomplete_grid")
    edges = [i for i, row in enumerate(rows) if row[2] > 0 and (i == 0 or rows[i-1][2] == 0)]
    require(len(edges) == count, "readout_pulse_count")
    times = [rows[i][0] for i in edges]
    require(all(abs(b-a-.01) < 1e-12 for a, b in zip(times, times[1:])), "readout_pulse_intervals")
    maxima, spans = [], []
    for i in range(somas):
        maxima.append(max(abs(row[3+2*i]-row[4+2*i]) for row in rows))
        values = [row[4+2*i] for row in rows];spans.append(max(values)-min(values))
    require(all(v <= 1e-12 for v in maxima), "readout_roundtrip_waveform_changed")
    require(all(v > 1e-8 for v in spans), "readout_flat_soma_control")
    return {"rows": rows, "summary": {"topology": "Branch" if branch else "Classic", "inputs": count,
        "frequency_hz": frequency, "saved_state": state, "somas": somas, "samples": len(rows),
        "sample_grid_complete": True, "stimulus_times": times, "maximum_waveform_difference": maxima,
        "soma_spans": spans, "graph_projection_sha256": identity, "loaded_graph_projection_sha256": loaded_identity,
        "nodes": len(before["nodes"]), "links": len(before["links"]), "primary": records,
        "lt_spike_timestamps": None, "training_certificate": None, "scientific_verdict": None}}


def audit_run(root):
    def passed(name, expected):
        value = parse_json_bytes(snapshot(root, name)[0])
        require(value["execution"]["execution"] == "completed" and value["execution"]["returncode"] == 0,
                "readout_native_process_failed")
        data = value["gtest"]
        require(int(data["tests"]) == expected and data["failures"] == data["errors"] == data["disabled"] == "0",
                "readout_native_tests_failed")
        return value
    validation = passed("validation.json", 32)
    regression = passed("regression-validation.json", 21)
    require(regression["skipped"] == 0, "readout_skipped_regression")
    tree = ET.fromstring(snapshot(root, "gtest.xml")[0]);cases = tree.findall(".//testcase")
    require(len(cases) == 32 and not tree.findall(".//failure") and not tree.findall(".//skipped"),
            "readout_gtest_detail_incomplete")
    expected = list(conditions());seen = []
    for case in cases:
        value = case.get("value_param", "")
        require(value.startswith("(") and value.endswith(")"), "readout_invalid_test_condition")
        seen.append(parse_json_bytes(("["+value[1:-1]+"]").encode()))
    require(sorted(map(str, seen)) == sorted(str(list(c[1:])) for c in expected), "readout_test_condition_set")
    folders = {p.name for p in (root/"artifacts").iterdir()}
    require(folders == {c[0] for c in expected}, "readout_artifact_condition_set")
    data = {name: read_case(root/"artifacts"/name, *spec) for name, *spec in expected}
    return data, {"schema": "loaded_learner_roundtrip_report_v1", "native_validation": validation,
                  "native_regression": regression, "cases": {name: value["summary"] for name, value in data.items()},
                  "case_soma_pairs": sum(v["summary"]["somas"] for v in data.values()),
                  "training_certificate": None, "scientific_verdict": None}


def render(data, output):
    import matplotlib.pyplot as plt
    output.mkdir(parents=True, exist_ok=False);figures = []
    s = data["summary"];rows = data["rows"];clock = [r[0] for r in rows]
    for soma in range(s["somas"]):
        source = [r[3+2*soma] for r in rows];loaded = [r[4+2*soma] for r in rows]
        shared = padded_limits(source+loaded)
        for view, left, right in time_views(clock[0], clock[-1], s["frequency_hz"]):
            a = max(0, bisect.bisect_left(clock, left)-1);z = min(len(clock), bisect.bisect_right(clock, right)+1)
            local = padded_limits(source[a:z]+loaded[a:z]);scales = [("shared", shared)]
            if 0 < local[1]-local[0] < .25*(shared[1]-shared[0]):scales.append(("detail", local))
            for scale, limits in scales:
                fig, ax = plt.subplots(figsize=(12, 6), dpi=160)
                fig.subplots_adjust(left=.12, right=.86, bottom=.15, top=.72)
                ax.plot(clock, source, color="navy", lw=1.8, label="Source soma")
                ax.plot(clock, loaded, color="teal", ls="--", lw=1., label="Loaded soma")
                pulse = ax.twinx();pulse.step(clock, [r[2] for r in rows], where="post", color="darkorange",
                                             alpha=.7, label="Actual native input")
                ax.set_xlim(left, right);ax.set_ylim(*limits);ax.grid(alpha=.25)
                ax.set_xlabel("Native time [s]");ax.set_ylabel("Soma SumPotential [model units; SI unverified]")
                pulse.set_ylabel("Input [native units]", color="darkorange")
                fig.suptitle(f'{s["topology"]} N={s["inputs"]} {s["frequency_hz"]} Hz State={int(s["saved_state"])} | soma {soma+1}\n'
                             f'{view}, {scale} amplitude | XML roundtrip characterization; not selectivity\n'
                             'LT events were not recorded', y=.98)
                h, labels = ax.get_legend_handles_labels();h2, labels2 = pulse.get_legend_handles_labels()
                fig.legend(h+h2, labels+labels2, loc="upper center", bbox_to_anchor=(.5, .83), frameon=False, ncol=3)
                path = output/f"soma-{soma+1}-{view}-{scale}.png";fig.savefig(path);plt.close(fig)
                figures.append({"path": path.name, "soma": soma+1, "view": view, "scale": scale,
                                "begin": left, "end": right, "y_limits": limits,
                                "png_width": 1920, "png_height": 960, "downsampling": False,
                                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return figures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plots", action="store_true")
    args = parser.parse_args();data, report = audit_run(args.input)
    runtime = plotting_runtime() if args.plots else None
    args.output.mkdir(parents=True, exist_ok=False)
    if args.plots:
        for name, value in data.items():report["cases"][name]["figures"] = render(value, args.output/name)
    report["plotting_runtime"] = runtime
    (args.output/"validation.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()
