"""Owned saved-state Phase A replay on the original immutable August Git closure."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from ..historical_phasea_native import (ROOT, BIN, PULSE, CASES, write, model_readback,
                                       prepare_case, add_native_temporal_observer)
from ..historical_selectivity import analyze_historical_csv
from ..native_evidence import load, require
from ..process_runner import execute, verify_runtime
from ..runtime import source_closure


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
