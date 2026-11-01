"""Audit real warm learner Reset exports; retain negative lifecycle evidence."""
import argparse
import csv
import io
import itertools
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from .loaded_readout_reports import render, snapshot
from .native_evidence import EvidenceError, parse_json_bytes, require
from .plotting import plotting_runtime


def conditions():
    for branch, count, frequency in itertools.product((False, True), (2, 4), (2000, 20000)):
        yield ("Branch" if branch else "Classic")+f"-N{count}-f{frequency}", branch, count, frequency


def read_case(folder, branch, count, frequency):
    records = []
    def raw(name):
        data, record = snapshot(folder, name);records.append(record);return data
    o = parse_json_bytes(raw("observation.json"));topology = "Branch" if branch else "Classic"
    require(o.get("kind") == "native_hot_learner_reset" and type(o.get("schema_version")) is int
            and o["schema_version"] == 1, "hot_unknown_observation_schema")
    require(o.get("topology") == topology and type(o.get("inputs")) is int and o["inputs"] == count
            and type(o.get("frequency_hz")) is int and o["frequency_hz"] == frequency, "hot_condition_mismatch")
    somas = 1 if branch else count
    def number(value):
        require(type(value) in (int, float) and math.isfinite(value), "hot_invalid_number");return value
    for phase in ("initial", "warm", "after_reset"):
        state = o.get(phase);require(type(state) is dict, "hot_missing_state")
        for key in ("physical_somas", "cached_somas"):
            values = state.get(key)
            require(type(values) is list and len(values) == somas, "hot_wrong_soma_dimension")
            for value in values:number(value)
        for key in ("physical_total", "cached_total"):number(state.get(key))
        require(abs(sum(state["physical_somas"])-state["physical_total"]) <= 1e-12, "hot_inconsistent_physical_total")
        require(abs(sum(state["cached_somas"])-state["cached_total"]) <= 1e-12, "hot_inconsistent_cached_total")
    require(number(o.get("effective_capacity")) == 1.23e-9
            and number(o.get("effective_resistance")) == 91e6, "hot_individual_physics_changed")
    for a, b in zip(o["initial"]["physical_somas"], o["after_reset"]["physical_somas"]):
        require(abs(a-b) <= 1e-12, "hot_physical_rest_changed")
    header = ["time_s", "input"]
    for i in range(1, somas+1):header += [f"physical_soma{i}", f"cached_soma{i}"]
    reader = csv.reader(io.StringIO(raw("warm.csv").decode("utf-8"), newline=""))
    require(next(reader, None) == header, "hot_csv_schema")
    rows = []
    for index, fields in enumerate(reader):
        require(len(fields) == len(header), "hot_csv_width")
        try:values = [float(v) for v in fields]
        except ValueError as error:raise EvidenceError("hot_invalid_number") from error
        require(all(math.isfinite(v) for v in values), "hot_invalid_number")
        require(abs(values[0]-index/frequency) < 1e-12, "hot_sample_clock")
        require(values[1] >= 0, "hot_invalid_stimulus")
        # Renderer consumes two compared curves with one actual input timeline.
        rows.append(values[:2]+[values[1]]+values[2:])
    require(len(rows) == frequency//20, "hot_incomplete_grid")
    edges = [i for i, r in enumerate(rows) if r[2] > 0 and (i == 0 or rows[i-1][2] == 0)]
    require(len(edges) == count, "hot_pulse_count")
    times = [rows[i][0] for i in edges]
    require(all(abs(b-a-.01) < 1e-12 for a, b in zip(times, times[1:])), "hot_pulse_intervals")
    for i in range(somas):
        physical = [r[3+2*i] for r in rows];cached = [r[4+2*i] for r in rows]
        require(max(physical)-min(physical) > 1e-8, "hot_flat_soma_control")
        require(all(abs(a-b) <= 1e-12 for a, b in zip(physical, cached)), "hot_live_readout_mismatch")
        require(abs(physical[-1]-o["warm"]["physical_somas"][i]) <= 1e-12
                and abs(cached[-1]-o["warm"]["cached_somas"][i]) <= 1e-12, "hot_warm_snapshot_mismatch")
    residuals = [a-b for a, b in zip(o["after_reset"]["cached_somas"], o["after_reset"]["physical_somas"])]
    stale = any(abs(r) > 1e-12 for r in residuals)
    return {"rows": rows, "summary": {"topology": topology, "inputs": count, "frequency_hz": frequency,
            "somas": somas, "samples": len(rows), "stimulus_times": times, "reset_residuals": residuals,
            "observed_lifecycle": "stale_readout" if stale else "consistent_readout",
            "observation": o, "primary": records, "lt_spike_timestamps": None, "scientific_verdict": None}}


def audit_run(root):
    validation = parse_json_bytes(snapshot(root, "validation.json")[0])
    tree = ET.fromstring(snapshot(root, "gtest.xml")[0]);cases = tree.findall(".//testcase")
    require(len(cases) == 8 and not tree.findall(".//skipped"), "hot_incomplete_native_cases")
    expected = list(conditions());seen = []
    for c in cases:
        param = c.get("value_param", "")
        require(param.startswith("(") and param.endswith(")"), "hot_invalid_native_condition")
        seen.append(parse_json_bytes(("["+param[1:-1]+"]").encode()))
    require(sorted(map(str, seen)) == sorted(str(list(c[1:])) for c in expected), "hot_native_condition_set")
    require({p.name for p in (root/"artifacts").iterdir()} == {c[0] for c in expected}, "hot_artifact_condition_set")
    data = {name: read_case(root/"artifacts"/name, *spec) for name, *spec in expected}
    failures = sum(v["summary"]["observed_lifecycle"] == "stale_readout" for v in data.values())
    g = validation["gtest"];execution = validation["execution"]
    require(g["tests"] == "8" and g["errors"] == g["disabled"] == "0" and int(g["failures"]) == failures
            and len(tree.findall(".//testcase[failure]")) == failures, "hot_native_verdict_disagreement")
    require(execution["returncode"] == (1 if failures else 0)
            and execution["execution"] == ("process_error" if failures else "completed"), "hot_execution_disagreement")
    return data, {"kind": "native_hot_reset_report", "schema_version": 1, "native_validation": validation,
                  "cases": {k: v["summary"] for k, v in data.items()}, "stale_cases": failures,
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
            report["cases"][name]["figures"] = render(value, args.output/name, source_label="Physical soma",
                loaded_label="Learner readout", context="Warm response; Reset is checked in JSON",
                state_description="before Reset")
    report["plotting_runtime"] = runtime
    (args.output/"validation.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":main()
