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
from ..historical_phasea_native import (ROOT, BIN, PULSE, CASES, prepare_case,
    add_native_temporal_observer, write, transfer_model, parameter_export, recognition_identity)


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
        # Validate the native loaded graph AND runtime buffer dimensions before
        # the expensive matrix. Never reuse this post-save Model (now mode0)
        # as the next input; the full run starts from the untouched prepared pair.
        short = folder/"preflight/work";short.parent.mkdir()
        shutil.copytree(prepared, short)
        gate = execute(runtime, ["-c", str(short/"Project.ini"), "-s", "-t", "0.0005", "-x", "-S"],
                       short, folder/"preflight/process", 120)
        require(gate["execution"] == "completed", "historical_import_prestimulus_process_failed:"+name)
        require(serialized_neuron(short/"Model_00.xml")["sha256"] == recognition_identity(solo, threshold),
                "historical_import_prestimulus_neuron_changed:"+name)
        cached = list((short/"TemporalTrace").glob("*NeuronTimeLearner.SomaNeuronAmplitude.txt"))
        stimulus = list((short/"TemporalTrace").glob("*NeuronTimeLearner.DatasetMatrix.Generator1.Output.txt"))
        require(len(cached) == len(stimulus) == 1, "historical_import_prestimulus_stream_missing")
        cached_rows = [line.split() for line in cached[0].read_text().splitlines()]
        require(bool(cached_rows) and all(len(row) == 7 for row in cached_rows),
                "historical_import_learner_readout_dimension_invalid")
        require(all(float(line.split()[-1]) == 0 for line in stimulus[0].read_text().splitlines()),
                "historical_import_prestimulus_already_received_input")
        write(folder/"preflight/validation.json", {"execution": gate["execution"],
            "neuron_identity_verified": True, "learner_cached_soma_rows": 5,
            "no_input_pulse": True, "original_load_modes": {"Model": 1, "Parameters": 0},
            "scientific_verdict": None})
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
