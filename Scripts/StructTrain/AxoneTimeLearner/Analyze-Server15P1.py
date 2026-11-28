"""Summarize closed sparse P1 captures on .15; never infer learning or carrier acceptance."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def sha(path):
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def write_new(path, value):
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write("\n")


def events(values):
    result=[]
    high=False
    for tick,value in enumerate(values):
        if value>.5:
            if not high:
                result.append({"onset_tick":tick,"end_tick":tick+1,"peak":value,
                               "left_censored":tick==0,"right_censored":False})
            else:
                result[-1]["peak"]=max(result[-1]["peak"],value)
            high=True
        elif high:
            result[-1]["end_tick"]=tick
            high=False
    if high:
        result[-1]["end_tick"]=len(values)
        result[-1]["right_censored"]=True
    for event in result:
        event["threshold_width_ticks"]=event["end_tick"]-event["onset_tick"]
    return result


def trace(path,frequency,columns):
    with path.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream)
        require(reader.fieldnames==columns,"unexpected_trace_columns")
        data={name:[] for name in columns}
        for index,row in enumerate(reader):
            require(None not in row and all(value is not None for value in row.values()),"invalid_csv_row")
            values={name:float(row[name]) for name in columns}
            require(all(math.isfinite(value) for value in values.values()),"nonfinite_trace")
            require(abs(values["time"]-index/frequency)<=1e-12,"invalid_time_grid")
            for name,value in values.items():
                data[name].append(value)
    require(len(data["time"])==frequency*11//20+1,"incomplete_declared_window")
    return data


def association(inputs,outputs,frequency):
    # All admissible edges in the predeclared 0..50ms sparse window.
    # Degree-one isolated pairs are sufficient for unique full one-to-one
    # association; no greedy owner or count-only conduction claim is made.
    edges=[(i,j) for i,a in enumerate(inputs) for j,b in enumerate(outputs)
           if 0<=b["onset_tick"]-a["onset_tick"]<=frequency//20]
    a=[[j for i2,j in edges if i2==i] for i in range(len(inputs))]
    b=[[i for i,j2 in edges if j2==j] for j in range(len(outputs))]
    isolated=[(i,values[0]) for i,values in enumerate(a) if len(values)==1 and len(b[values[0]])==1]
    pairs=[{"input":i,"output":j,"lag_ticks":outputs[j]["onset_tick"]-inputs[i]["onset_tick"],
            "lag_s":(outputs[j]["onset_tick"]-inputs[i]["onset_tick"])/frequency} for i,j in isolated]
    return {"lag_bounds_s":[0,.05],"admissible_edges":[list(edge) for edge in edges],
            "isolated_pairs":pairs,"unassociated_input_indices":[i for i,x in enumerate(a) if not x],
            "unassociated_output_indices":[j for j,x in enumerate(b) if not x],
            "nonisolated_association":any(len(x)>1 for x in a+b),
            "unique_full_temporal_association":bool(inputs) and len(inputs)==len(outputs)==len(isolated),
            "causal_conduction_proven":False}


def analyze_case(case,folder):
    identity=case["id"];frequency=case["model_frequency_hz"]
    metadata_path=folder/(identity+".json");csv_path=folder/(identity+".csv")
    metadata=read(metadata_path)
    require(metadata.get("complete") is True and metadata.get("frequency_hz")==frequency and
            metadata.get("training") is False,"capture_metadata_not_complete")
    result={"id":identity,"carrier":case["carrier"],"frequency_hz":frequency,
            "csv_sha256":sha(csv_path),"metadata_sha256":sha(metadata_path),"capture_valid":True}
    if identity.startswith("tree_equivalence_"):
        columns=["time","source","tree_root","explicit_root","tree_left","explicit_left","tree_right","explicit_right"]
        data=trace(csv_path,frequency,columns)
        measures={}
        for port in ("root","left","right"):
            tree,explicit=data["tree_"+port],data["explicit_"+port]
            measures[port]={"maximum_absolute_difference":max(abs(x-y) for x,y in zip(tree,explicit)),
                            "tree_events":events(tree),"explicit_events":events(explicit)}
        result.update(source_events=events(data["source"]),ports=measures,
            all_ports_equal=all(value["maximum_absolute_difference"]==0 for value in measures.values()),
            nontrivial_left_conduction=len(measures["left"]["tree_events"])==5 and len(events(data["source"]))==5)
        return result
    require(metadata.get("kind")=="axone_native_lifecycle_observation","unexpected_capture_kind")
    data=trace(csv_path,frequency,["time","source","axon"])
    inputs,outputs=events(data["source"]),events(data["axon"])
    for declared,actual in ((metadata["input_events"],inputs),(metadata["output_events"],outputs)):
        require(len(declared)==len(actual) and all(abs(t-event["onset_tick"]/frequency)<=1e-12
                for t,event in zip(declared,actual)),"capture_events_disagree_with_waveform")
    result.update(input_events=inputs,output_events=outputs,association=association(inputs,outputs,frequency),
                  source_edge_count=len(inputs),output_count=len(outputs),
                  source_peak=max(data["source"]),axon_peak=max(data["axon"]))
    if case["carrier"]=="NAxoneDelay":
        expected=math.floor(case["delay_s"]*frequency)
        result["requested_delay_s"]=case["delay_s"]
        result["expected_delay_ticks"]=expected
        result["all_isolated_pairs_have_expected_delay"]=all(
            pair["lag_ticks"]==expected for pair in result["association"]["isolated_pairs"])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("gate-root","output","archive-adapter"):
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--archive-adapter-sha256",required=True)
    parser.add_argument("--archive-id",required=True)
    args=parser.parse_args()
    adapter=args.archive_adapter.resolve(strict=True)
    require(sha(adapter)==args.archive_adapter_sha256.lower(),"archive_adapter_changed")
    spec=importlib.util.spec_from_file_location("axon_archive_adapter",adapter)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    data,marker,marker_record=module.root_identity(Path("E:/Nmsdk-AxoneTimeLearner-Data"),args.archive_id)
    gate_root=module.private(args.gate_root)
    require(gate_root.is_relative_to(data/"NativeChecks"),"analysis_gate_outside_declared_data")
    closed=read(gate_root/"native-gate/process/result.json")
    verdict=read(gate_root/"result.json")
    require(closed.get("all_processes_closed") is True and verdict.get("complete") is True and
            verdict.get("gate",{}).get("validity")=="valid","native_gate_not_validly_closed")
    recipe_path=gate_root/"source-protocol.json";recipe=read(recipe_path)
    require(recipe.get("kind")=="axone_native_contract_inputs" and len(recipe["cases"])==51,
            "wrong_sparse_p1_protocol")
    destination=args.output.resolve()
    require(destination.is_relative_to(data/"Experiments") and not destination.exists() and
            not destination.is_relative_to(gate_root),"fresh_analysis_output_required")
    destination.mkdir(parents=True,exist_ok=False)
    specification=read(gate_root/"gate-specification.json")
    expected=specification["expected_test_ids"]
    require(len(expected)==verdict["expected_cases"], "gate_inventory_changed")
    selected=[case for case in recipe["cases"] if case["gtest_filter"] in expected]
    require(bool(selected), "no_declared_waveform_cases_selected")
    rows=[]
    for case in selected:
        try:
            rows.append(analyze_case(case,gate_root/"native-gate/native/AxoneP1"))
        except (ValueError,RuntimeError,OSError,KeyError,TypeError) as error:
            rows.append({"id":case["id"],"carrier":case["carrier"],"frequency_hz":case["model_frequency_hz"],
                         "capture_valid":False,"reason":str(error)})
    summary={"kind":"axone_p1_sparse_baseline_analysis","schema_version":1,
             "input_gate":str(gate_root),"input_gate_result_sha256":sha(gate_root/"result.json"),
             "protocol_sha256":sha(recipe_path),"archive_id":args.archive_id,"marker":marker_record,
             "producer":{"path":str(Path(__file__).resolve()),"sha256":sha(Path(__file__))},
             "analysis_complete":all(row["capture_valid"] for row in rows),
             "native_assertion_status":verdict["gate"].get("assertion_status"),
             "native_expected_cases":len(expected), "analyzed_waveform_cases":len(selected),
             "unmapped_native_test_ids":[name for name in expected if name not in {c["gtest_filter"] for c in selected}],
             "cases":rows,"training":False,"carrier_selected":False,"full_P1_accepted":False,
             "scientific_verdict":None,
             "limitations":["One engineering execution; three declared repeatability runs are not replaced.",
                            "Sparse 10Hz sequence is not the burst/refractory matrix.",
                            "Temporal association and equal graphs do not prove causal conduction."]}
    write_new(destination/"result.json",summary)
    compact=[{"id":r["id"],"valid":r["capture_valid"],
              "input_count":len(r.get("input_events",r.get("source_events",[]))),
              "output_count":r.get("output_count"),
              "axon_peak":r.get("axon_peak"),"ports_equal":r.get("all_ports_equal"),
              "reason":r.get("reason")} for r in rows]
    write_new(destination/"compact.json",compact)
    print(json.dumps({"analysis_complete":summary["analysis_complete"],"cases":len(rows),
        "invalid":[row["id"] for row in rows if not row["capture_valid"]],
        "groups":[{"frequency_hz":f,"carrier":c,"output_counts":[r.get("output_count") for r in rows
                   if r["capture_valid"] and r["frequency_hz"]==f and r["carrier"]==c and "output_count" in r]}
                  for f in (2000,20000,40000) for c in ("NAxoneDelay","NAxoneChain","NAxoneChainAndDelay")]},
                  ensure_ascii=False))
    return 0 if summary["analysis_complete"] else 1


if __name__=="__main__":
    raise SystemExit(main())
