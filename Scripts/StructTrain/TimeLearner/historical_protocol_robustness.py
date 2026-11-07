"""Frozen Phase A order/ITI controls on the exact historical native runtime.

No Train, retargeting, threshold selection, synthetic response or new certificate.
The original criterion and complete recorded inter-trial intervals stay separate.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from .historical_model import serialized_neuron
from .historical_phasea_temporal import read_stream, rising_edges
from .historical_selectivity import analyze_historical_csv
from .model_identity import canonical_model_sha256
from .native_evidence import load, require
from .process_runner import execute, verify_runtime
from .runtime import source_closure
from .historical_phasea_native import (ROOT, BIN, PULSE, prepare_case,
    add_native_temporal_observer, write, parameter_export, recognition_identity)


CASE = "EXP01_ltz_threshold_sweep/Test_thr00135"
THRESHOLD = .0135
MODEL_SECONDS = 40


def _one(node, path):
    values = node.findall(path)
    require(len(values) == 1, "historical_protocol_property_not_unique:"+path)
    return values[0]


def _dataset(tree):
    return _one(tree, "./Model/Components/NeuronTimeLearner/Components/DatasetMatrix/Parameters")


def _read_patterns(parameters):
    for name, expected in (("NumFeatures", "1"), ("NumSamples", "8"),
                           ("MaxSpikesPerFeature", "4"), ("LoopSamples", "0"),
                           ("AdvanceSampleAfterBurst", "1")):
        require((_one(parameters, "./"+name).text or "").strip() == expected,
                "unsupported_historical_protocol_layout:"+name)
    data = _one(parameters, "./MatrixData");classes = _one(parameters, "./MatrixClasses")
    require((data.get("Rows"), data.get("Cols")) == ("32", "1") and
            (classes.get("Rows"), classes.get("Cols")) == ("1", "8"),
            "unsupported_historical_flat_matrix")
    tokens = (data.text or "").split();labels = (classes.text or "").split()
    require(len(tokens) == 32 and len(labels) == 8 and all(v in ("0", "1") for v in labels)
            and labels.count("1") == 1, "invalid_historical_protocol_matrix")
    values = [float(v) for v in tokens]
    require(all(math.isfinite(v) and v > 0 for v in values), "invalid_historical_protocol_isi")
    return [tokens[i:i+4] for i in range(0, 32, 4)], labels


def prepare_protocol(work, order, iti):
    """Address actual flat matrix blocks and labels in both native input files."""
    require(type(order) is list and len(order) == 8 and all(type(v) is int for v in order)
            and set(order) == set(range(8)), "invalid_historical_protocol_permutation")
    require(type(iti) in (int, float) and math.isfinite(iti) and iti in (1.5, 3.),
            "unsupported_historical_protocol_iti")
    source = None;source_identity = serialized_neuron(work/"Model_00.xml");prepared = []
    for filename in ("Model_00.xml", "Parameters_00.xml"):
        path = work/filename;tree = ET.parse(path);root = tree.getroot()
        parameters = _dataset(root);patterns, labels = _read_patterns(parameters)
        declared = ([[float(v) for v in row] for row in patterns], labels)
        require(source is None or source == declared, "historical_protocol_model_parameter_data_disagree")
        source = declared
        learner = _one(root, "./Model/Components/NeuronTimeLearner/Parameters")
        require((_one(learner, "./IsNeedToTrain").text or "").strip() == "0",
                "historical_protocol_must_not_train")
        require((_one(learner, "./NumInputDendrite").text or "").strip() == "4" and
                (_one(learner, "./StructureBuildMode").text or "").strip() ==
                ("1" if filename == "Model_00.xml" else "0"),
                "historical_protocol_unsafe_native_load_modes")
        _one(learner, "./Delay");_one(parameters, "./Delay")
        prepared.append((path, tree, learner, parameters, patterns, labels))
    # Validate both native files before editing either one. A corrupt second
    # file must not leave the first with a partially changed declared protocol.
    for path, tree, learner, parameters, patterns, labels in prepared:
        _one(parameters, "./MatrixData").text = "\n".join(v for index in order for v in patterns[index])
        _one(parameters, "./MatrixClasses").text = "\n".join(labels[index] for index in order)
        # Learner owns the effective dataset delay; setting only its child can
        # be overwritten by native construction. Both declarations are explicit.
        _one(learner, "./Delay").text = str(iti)
        _one(parameters, "./Delay").text = str(iti)
        tree.write(path, encoding="utf-8")
    require(serialized_neuron(work/"Model_00.xml")["sha256"] == source_identity["sha256"],
            "historical_protocol_edit_changed_neuron")
    patterns, labels = source
    return {"order": order, "iti_declared": iti, "threshold": THRESHOLD,
            "reset_policy": "historical native Test; fresh process per matrix; no added per-trial reset",
            "model_seconds": MODEL_SECONDS,
            "samples": [{"sample_id": "phasea-"+str(i), "original_index": i,
                         "pattern_hash": canonical_model_sha256({"isi": [float(v) for v in patterns[i]]}),
                         "pattern": [float(v) for v in patterns[i]], "label": "target" if labels[i] == "1" else "foil"}
                        for i in order],
            "serialized_source_neuron_sha256": source_identity["sha256"],
            "training_started": False, "independent_evaluation": False}


def effective_protocol(path, declared):
    root = ET.parse(path).getroot();p = _dataset(root);patterns, labels = _read_patterns(p)
    require([[float(v) for v in row] for row in patterns] == [s["pattern"] for s in declared["samples"]]
            and labels == ["1" if s["label"] == "target" else "0" for s in declared["samples"]],
            "historical_protocol_effective_matrix_changed")
    delay = float(_one(p, "./Delay").text)
    require(math.isfinite(delay) and delay == declared["iti_declared"],
            "historical_protocol_effective_iti_changed")


def read_observations(folder, declared):
    """Use actual native pulses, labels and all edges, not CSV row position."""
    records = load(folder/"trace-files.json");streams = {};times = None
    expected = {"stimulus", "lt_spikes", "neuron_soma_sum", "learner_cached_somas"}
    expected.update("soma"+str(i)+"_"+kind for i in range(1, 5) for kind in ("exc", "inh"))
    require(len(records) == len(expected) and {r["role"] for r in records} == expected,
            "historical_protocol_trace_set")
    for record in records:
        path = (folder/record["path"]).resolve(strict=True)
        require(path.is_relative_to(folder.resolve()), "historical_protocol_trace_path_escape")
        clock, data = read_stream(path, 5 if record["role"] == "learner_cached_somas" else 1, record["sha256"])
        require(times is None or times == clock, "historical_protocol_clock_disagreement")
        times = clock;streams[record["role"]] = data
    # Preserve the historical reader's exact 40s/2000Hz clock contract.
    pulses = rising_edges(streams["stimulus"]);spikes = rising_edges(streams["lt_spikes"])
    require(len(pulses) == 32, "historical_protocol_stimulus_set_incomplete")
    native = analyze_historical_csv(folder/"work/SelectivityLog/results.csv", [str(i) for i in range(8)])
    by_id = {r["trial_id"]: r for r in native["rows"]};trials = []
    for position, sample in enumerate(declared["samples"]):
        row = by_id[str(position)];actual = [times[i] for i in pulses[position*4:(position+1)*4]]
        require(row["label"] == sample["label"] and row["isis"] == sample["pattern"][1:],
                "historical_protocol_presented_identity_mismatch")
        require(all(abs(actual[j+1]-actual[j]-sample["pattern"][j+1]) < 1e-9 for j in range(3)),
                "historical_protocol_actual_isi_mismatch")
        onset = actual[0];accept_end = actual[-1]+.5
        interval_end = times[pulses[(position+1)*4]] if position < 7 else MODEL_SECONDS
        require(onset < accept_end < interval_end and times[-1]+1/2000 >= interval_end,
                "historical_protocol_incomplete_or_overlapping_window")
        in_window = [times[i] for i in spikes if onset <= times[i] <= accept_end]
        full = [times[i] for i in spikes if onset <= times[i] < interval_end]
        require(bool(in_window) == row["reported_fired"], "historical_protocol_csv_spike_disagreement")
        trials.append({**sample, "trial_id": str(position), "position": position, "onset": onset,
                       "stimulus_times": actual, "accept_end": accept_end, "interval_end": interval_end,
                       "spike_times": in_window, "full_interval_spike_times": full,
                       "late_spike_times": [t for t in full if t > accept_end],
                       "native_match": row["native_match"], "complete": True})
    # A protocol must apply its factor; report the actual gap before accepting.
    gaps = [trials[i+1]["onset"]-trials[i]["stimulus_times"][-1] for i in range(7)]
    require(all(gap >= declared["iti_declared"]-1e-9 for gap in gaps),
            "historical_protocol_actual_gap_shorter_than_declared")
    somas = [[streams["soma"+str(i)+"_exc"][n][0]+streams["soma"+str(i)+"_inh"][n][0]
              for i in range(1, 5)] for n in range(len(times))]
    require(all(s == c[1:] for s, c in zip(somas, streams["learner_cached_somas"])),
            "historical_protocol_native_soma_alignment_changed")
    return {"kind": "historical_frozen_protocol_observations", "schema_version": 1,
            "trials": trials, "native_counts": native["reported_counts"],
            "native_correct": native["native_match_count"], "actual_inter_burst_gaps": gaps,
            "pre_stimulus_spikes": [times[i] for i in spikes if times[i] < trials[0]["onset"]],
            "samples": len(times), "all_recorded_windows_complete": True,
            "training_certificate": None, "independent_evaluation": False,
            "scientific_verdict": None}


def run_case(source, runtime, output, order, iti):
    source = Path(source).resolve(strict=True);output = Path(output).resolve()
    runtime_root = Path(runtime["executable"]["path"]).resolve(strict=True).parent
    require(not output.exists() and not output.is_relative_to(source) and not source.is_relative_to(output)
            and not output.is_relative_to(runtime_root) and not runtime_root.is_relative_to(output),
            "historical_protocol_output_exists_or_overlaps")
    closure = source_closure(source)
    require(closure["root"]["head"] == ROOT and closure["Bin"]["head"] == BIN and
            closure["Libraries/Nmsdk-PulseLib"]["head"] == PULSE and runtime["source_closure"] == closure,
            "historical_protocol_source_runtime_mismatch")
    verify_runtime(runtime)
    inputs, work, reference, records = prepare_case(source/"Bin", CASE, output)
    declared = prepare_protocol(work, order, iti)
    observer = add_native_temporal_observer(source/"Bin", work);parameter_export(work)
    write(output/"protocol.json", declared);write(output/"inputs.json", records);write(output/"observer.json", observer)
    shutil.copyfile(runtime["app_ini"]["path"], work/"NeuroModelerConsole.ini")
    ini_hash = hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest()
    require(ini_hash == runtime["app_ini"]["sha256"], "historical_protocol_runtime_ini_mismatch")
    prepared = output/"prepared";shutil.copytree(work, prepared)
    short = output/"preflight/work";shutil.copytree(prepared, short)
    result = execute(runtime, ["-c", str(short/"Project.ini"), "-s", "-t", ".0005", "-x", "-S"],
                     short, output/"preflight/process", 120)
    require(result["execution"] == "completed", "historical_protocol_preflight_execution_failed")
    identity = serialized_neuron(short/"Model_00.xml")
    source_identity = serialized_neuron(inputs/"Model_00.xml")
    require(identity["sha256"] == recognition_identity(source_identity, THRESHOLD),
            "historical_protocol_effective_neuron_changed")
    effective_protocol(short/"Model_00.xml", declared)
    cached = list((short/"TemporalTrace").glob("*NeuronTimeLearner.SomaNeuronAmplitude.txt"))
    stimulus = list((short/"TemporalTrace").glob("*NeuronTimeLearner.DatasetMatrix.Generator1.Output.txt"))
    require(len(cached) == len(stimulus) == 1, "historical_protocol_prestimulus_stream_missing")
    cached_rows = [line.split() for line in cached[0].read_text().splitlines()]
    require(bool(cached_rows) and all(len(row) == 7 for row in cached_rows),
            "historical_protocol_prestimulus_readout_dimension_invalid")
    require(all(float(line.split()[-1]) == 0 for line in stimulus[0].read_text().splitlines()),
            "historical_protocol_prestimulus_already_presented_input")
    write(output/"preflight/validation.json", {"effective_neuron_identity": identity["sha256"],
          "effective_pattern_and_iti_verified": True, "learner_readout_rows": 5,
          "no_stimulus_presented": True, "original_native_load_modes_preserved": True})
    result = execute(runtime, ["-c", str(work/"Project.ini"), "-s", "-t", str(MODEL_SECONDS), "-x", "-S"],
                     work, output/"process", 900)
    require(result["execution"] == "completed", "historical_protocol_execution_failed")
    require(serialized_neuron(work/"Model_00.xml")["sha256"] == identity["sha256"],
            "historical_protocol_frozen_neuron_changed")
    effective_protocol(work/"Model_00.xml", declared)
    require(hashlib.sha256((work/"NeuroModelerConsole.ini").read_bytes()).hexdigest() == ini_hash,
            "historical_protocol_runtime_ini_changed")
    traces = []
    for stream in observer["streams"]:
        paths = [p for p in (work/"TemporalTrace").glob("*.txt") if p.name.endswith(stream["source"]+".txt")]
        require(len(paths) == 1 and paths[0].stat().st_size > 0,
                "historical_protocol_trace_missing:"+stream["role"])
        p = paths[0];traces.append({**stream, "path": str(p.relative_to(output)),
                                  "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    write(output/"trace-files.json", traces)
    observation = read_observations(output, declared)
    baseline = order == list(range(8)) and iti == 1.5
    if baseline:
        require((work/"SelectivityLog/results.csv").read_bytes() == reference.read_bytes(),
                "historical_protocol_original_control_csv_changed")
    require(source_closure(source) == closure, "historical_protocol_source_changed")
    observation.update(frozen_neuron_sha256=identity["sha256"], original_control_csv_equal=True if baseline else None)
    write(output/"observations.json", observation)
    return observation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rotation", type=int, required=True, choices=range(8))
    parser.add_argument("--iti", type=float, required=True, choices=(1.5, 3.))
    args = parser.parse_args();order = [(i+args.rotation) % 8 for i in range(8)]
    result = run_case(args.source_root, load(args.runtime), args.output, order, args.iti)
    print(json.dumps({k: v for k, v in result.items() if k != "trials"}, allow_nan=False))


if __name__ == "__main__":
    main()
