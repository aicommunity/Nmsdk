"""Summarize a closed factory-segment diagnostic without changing physical parameters."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import socket
import os


def require(value,reason):
    if not value:
        raise RuntimeError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def count(values):
    return sum(value>.5 and (index==0 or values[index-1]<=.5) for index,value in enumerate(values))


def events(values,frequency):
    result=[];high=False
    for tick,value in enumerate(values):
        if value>.5:
            if not high:result.append({"onset_tick":tick,"end_tick":tick+1,"peak":value,"right_censored":False})
            else:result[-1]["peak"]=max(result[-1]["peak"],value)
            high=True
        elif high:
            result[-1]["end_tick"]=tick;high=False
    if high:result[-1]["end_tick"]=len(values);result[-1]["right_censored"]=True
    for event in result:
        event["width_ticks"]=event["end_tick"]-event["onset_tick"]
        event["width_s"]=event["width_ticks"]/frequency
    return result


def frequencies(nodes):
    return [node["frequency_hz"] for node in nodes]+[value for node in nodes for value in frequencies(node["children"])]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    require(os.name=="nt" and socket.gethostname().upper()=="AQUA3060","server15_required")
    data=Path("E:/Nmsdk-AxoneTimeLearner-Data").resolve(strict=True)
    marker=read(data/"archive.root.json")
    require(marker.get("archive_id")=="7d37d9df-beda-4bdd-9cc2-7068e364f154" and marker.get("volume_serial")=="CC129017",
            "data_root_changed")
    root=args.gate_root.resolve(strict=True);output=args.output.resolve()
    require(root.is_relative_to(data/"NativeChecks") and output.is_relative_to(data/"Experiments") and not output.exists(),
            "invalid_diagnostic_analysis_paths")
    gate=read(root/"result.json");process=read(root/"native-gate/process/result.json")
    require(gate.get("native_checks_passed") is True and gate.get("expected_cases")==9 and
            process.get("all_processes_closed") is True and process.get("runtime_provenance")=="loaded_files_captured",
            "factory_gate_not_accepted")
    folder=root/"native-gate/native/AxoneSegmentDiagnostic"
    rows=[]
    for metadata in sorted(folder.glob("*.json")):
        record=read(metadata);frequency=record["frequency_hz"]
        with metadata.with_suffix(".csv").open(encoding="utf-8",newline="") as stream:
            reader=csv.DictReader(stream);values={name:[] for name in reader.fieldnames}
            for index,row in enumerate(reader):
                parsed={name:float(row[name]) for name in values}
                require(all(math.isfinite(x) for x in parsed.values()) and
                        parsed["tick"]==index and abs(parsed["time"]-index/frequency)<=1e-12,
                        "invalid_diagnostic_trace")
                for name,value in parsed.items():values[name].append(value)
        require(len(values["tick"])==frequency*8//100+1 and record["complete"] is True and
                record["parameters_before"]==record["parameters_after"],"incomplete_or_changed_diagnostic")
        segments=[]
        for index,p in enumerate(record["parameters_before"]):
            prefix="s"+str(index+1)+"_"
            segments.append({"index":index+1,"threshold":p["threshold"],
                "input_edges":count(values[prefix+"input"]),"output_edges":count(values[prefix+"segment_output"]),
                "input_events":events(values[prefix+"input"],frequency),
                "output_events":events(values[prefix+"segment_output"],frequency),
                "ranges":{key[len(prefix):]:[min(value),max(value)] for key,value in values.items() if key.startswith(prefix)}})
        rows.append({"id":record["id"],"frequency_hz":frequency,"carrier":record["carrier"],
                     "source_edges":count(values["source"]),"axon_edges":count(values["axon"]),
                     "source_events":events(values["source"],frequency),"axon_events":events(values["axon"],frequency),
                     "actual_source_emission_times":record["actual_source_emission_times"],
                     "child_frequencies_hz":sorted(set(frequencies(record["native_child_order"]))),
                     "segments":segments,"csv_sha256":sha(metadata.with_suffix(".csv")),
                     "metadata_sha256":sha(metadata)})
    require(len(rows)==9,"missing_factory_diagnostic_case")
    output.mkdir(parents=True,exist_ok=False)
    result={"kind":"axone_factory_diagnostic_analysis","schema_version":1,"gate_root":str(root),
            "gate_result_sha256":sha(root/"result.json"),"producer_sha256":sha(Path(__file__)),
            "rows":rows,"analysis_complete":True,"scientific_verdict":None,
            "claim_scope":"Ranges and event counts for the declared 80ms diagnostic; no physiological acceptance or full P1 verdict."}
    with (output/"result.json").open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write("\n")
    print(json.dumps([{"id":r["id"],"source_edges":r["source_edges"],"axon_edges":r["axon_edges"],
                       "frequencies":r["child_frequencies_hz"],"first_ltz_range":r["segments"][0]["ranges"]["ltz_potential"],
                       "threshold":r["segments"][0]["threshold"],
                       "first_output_widths_s":[e["width_s"] for e in r["segments"][0]["output_events"]],
                       "last_output_widths_s":[e["width_s"] for e in r["segments"][-1]["output_events"]]} for r in rows]))


if __name__=="__main__":
    main()
