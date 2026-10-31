"""Strict primary-data audit for actual legacy inference free-run diagnostics.

These records are not V2 ProbeObservations, calibration proofs or certificates.
The producer terminates playback; this audit does not certify biological settling
or independent Test data. Fault-injection records have no physical CSV adapter.
"""
import csv
from pathlib import Path

from .native_evidence import count, equal, load, number, require
from .native_calibration_worker import _evidence_boundary


FIELDS = {"kind", "schema_version", "topology", "frequency_hz", "begin", "end", "ticks", "soma_channels",
          "stimulus_times", "pattern_isi", "sample_labels", "metric", "states", "all_samples_valid", "result",
          "threshold", "scientific_verdict"}


@_evidence_boundary
def read_free_run(packet_path, trace_path):
    packet = load(Path(packet_path));require(set(packet) == FIELDS and
        packet["kind"] == "legacy_posttune_physical_freerun" and type(packet["schema_version"]) is int and
        packet["schema_version"] == 1 and packet["scientific_verdict"] is None, "unknown_legacy_posttune_freerun")
    require(packet["topology"] in ("classic", "branch") and packet["metric"] == "simultaneous_soma_sum",
            "unsupported_legacy_posttune_trace")
    channels = count(packet["soma_channels"]);frequency = count(packet["frequency_hz"])
    require(channels == (1 if packet["topology"] == "branch" else 2) and frequency > 0,
            "legacy_posttune_channel_or_clock_mismatch")
    ticks = count(packet["ticks"]);begin,end = number(packet["begin"]),number(packet["end"])
    require(ticks > 0 and end > begin and equal(end-begin, ticks/frequency), "legacy_posttune_clock_changed")
    require(packet["sample_labels"] == ["target", "foil"] and type(packet["pattern_isi"]) is list and
            len(packet["pattern_isi"]) == 2 and all(type(p) is list and len(p) == 2 and
            all(number(v) >= 0 for v in p) for p in packet["pattern_isi"]), "legacy_posttune_design_changed")
    states = packet["states"]
    require(type(states) is list and len(states) == 2 and all(type(s) is dict and
            set(s) == {"peak", "observed", "finished", "finite_ok"} and s["observed"] is True and
            s["finished"] is True and s["finite_ok"] is True and number(s["peak"]) >= 0 for s in states) and
            packet["all_samples_valid"] is True, "legacy_posttune_incomplete_sample_states")
    require(type(packet["result"]) is int and packet["result"] in (1, 2, 6) and number(packet["threshold"]) >= 0,
            "legacy_posttune_invalid_terminal_status")
    header = ["time", "stimulus", *[f"soma{i}" for i in range(channels)],
              "dataset_iteration", "state_generation", "selected_metric"]
    samples,stimulus_times = [],[];previous=0.
    with Path(trace_path).open(encoding="utf-8", newline="") as stream:
        rows = csv.reader(stream);require(next(rows, None) == header, "legacy_posttune_csv_header")
        for index,row in enumerate(rows):
            require(len(row) == len(header) and all(v.strip() for v in row), "legacy_posttune_csv_shape")
            values = [number(float(v)) for v in row]
            time,stimulus = values[:2];soma = values[2:2+channels]
            require(equal(time, begin+index/frequency), "legacy_posttune_sample_clock_or_gap")
            require(all(v == round(v) for v in values[-3:-1]), "legacy_posttune_noninteger_dataset_state")
            require(equal(sum(soma), values[-1]), "legacy_posttune_selected_metric_changed")
            if stimulus > 0 and previous <= 0:stimulus_times.append(time)
            previous=stimulus
            samples.append({"time": time, "stimulus": stimulus, "soma": soma})
    require(len(samples) == ticks and len(stimulus_times) == 4 and type(packet["stimulus_times"]) is list and
            len(packet["stimulus_times"]) == 4 and all(equal(a, number(b)) for a,b in
            zip(stimulus_times,packet["stimulus_times"])), "legacy_posttune_incomplete_primary_trace")
    for pattern,index in zip(packet["pattern_isi"], (0,2)):
        require(abs(stimulus_times[index+1]-stimulus_times[index]-pattern[1]) <= 1.01/frequency,
                "legacy_posttune_presented_pattern_changed")
    audit = {"primary_data_consistent": True, "recorded_native_ticks": ticks, "soma_channels": channels,
             "declared_patterns": 2, "observed_input_pulses": 4, "result": packet["result"],
             "native_execution_verified": False, "calibration_validated": False,
             "physical_settling_verified": False, "scientific_verdict": None}
    return packet,samples,audit


def audit_free_run(packet_path, trace_path):
    return read_free_run(packet_path, trace_path)[2]
