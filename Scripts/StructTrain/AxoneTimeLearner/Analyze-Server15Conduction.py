"""Verify and summarize sealed burst or manual-delay matrices on .15 using shared evidence tools."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import socket
import struct
import sys
import traceback


def require(value,reason):
    if not value:raise RuntimeError(reason)


def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,document):
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(document,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write("\n")


def module(path,expected,name):
    path=path.resolve(strict=True);require(sha(path)==expected,"analysis_dependency_changed")
    specification=importlib.util.spec_from_file_location(name,path)
    loaded=importlib.util.module_from_spec(specification);specification.loader.exec_module(loaded)
    return loaded


def scalar(node,name,kind):
    parameter=node["parameters"][name]
    require(parameter["binding"] is False and parameter["data"]["type"]==kind,"unexpected_parameter_type:"+name)
    value=parameter["data"]["value"]
    if kind=="binary64":
        require(isinstance(value,str) and re.fullmatch(r"[0-9a-f]{16}",value),"invalid_binary64_parameter")
        value=struct.unpack(">d",bytes.fromhex(value))[0]
        require(math.isfinite(value),"nonfinite_parameter")
    elif kind=="boolean":require(type(value) is bool,"invalid_boolean_parameter")
    elif kind in ("signed_integer","unsigned_integer"):
        require(isinstance(value,str) and re.fullmatch(r"-?[0-9]+",value),"invalid_integer_parameter");value=int(value)
    return value


def trace(path,frequency,window,columns):
    data={name:[] for name in columns}
    with path.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream);require(reader.fieldnames==columns,"trace_columns_changed")
        for tick,row in enumerate(reader):
            require(None not in row and all(value is not None for value in row.values()),"incomplete_trace_row")
            values={name:float(row[name]) for name in columns}
            require(all(math.isfinite(value) for value in values.values()) and values["tick"]==tick and
                    abs(values["time"]-tick/frequency)<=1e-12,"invalid_trace_grid_or_values")
            for name,value in values.items():data[name].append(value)
    require(len(data["time"])==round(window*frequency)+1,"incomplete_trace_window")
    return data


def comparable(events):
    return [{key:event[key] for key in ("onset_tick","end_tick","peak","right_censored")} for event in events]


def checked_events(values,declared,frequency,helper):
    actual=helper.events(values,frequency)
    require(comparable(actual)==declared,"native_events_do_not_match_csv")
    return actual


def assignment(value,inputs,outputs,frequency):
    require(value["minimum_lag_ticks"]==0 and value["maximum_lag_ticks"]==frequency//5 and
            0<=value["maximum_matched"]<=min(len(inputs),len(outputs)) and
            len(value["possible_inputs"])==len(outputs) and len(value["possible_outputs"])==len(inputs) and
            len(value["input_can_be_unmatched"])==len(inputs) and len(value["output_can_be_unmatched"])==len(outputs),
            "invalid_native_association_shape")
    for pair in value["certain_pairs"]:
        i,j=pair["input"],pair["output"]
        require(type(i) is int and type(j) is int and 0<=i<len(inputs) and 0<=j<len(outputs) and
                0<=pair["lag_ticks"]<=frequency//5 and pair["lag_ticks"]==outputs[j]["onset_tick"]-inputs[i]["onset_tick"] and
                value["possible_outputs"][i]==[j] and value["possible_inputs"][j]==[i] and
                value["input_can_be_unmatched"][i] is False and value["output_can_be_unmatched"][j] is False,
                "invalid_certain_native_association")
    complete=(value["maximum_matched"]==len(inputs)==len(outputs) and
              len(value["certain_pairs"])==len(inputs) and value["ambiguous"] is False)
    require(value["complete_one_to_one"]==complete,"inconsistent_native_association_status")
    # Preserve the shared native module's full maximum-matching result. This
    # check does not implement a second optimizer or infer causal ownership.
    return {**value,"certain_lags_s":[pair["lag_ticks"]/frequency for pair in value["certain_pairs"]]}


def burst(case,metadata,payload,helper,canonical_model_sha256):
    frequency=case["frequency_hz"];length=case["segments"];window=case["window_s"]
    require(metadata["kind"]=="axone_burst_diagnostic" and metadata["complete"] is True and
            metadata["error"]=="" and metadata["frequency_hz"]==frequency and metadata["carrier"]==case["carrier"] and
            metadata["segments"]==length and metadata["pattern"]==case["pattern"] and
            metadata["source_isi_s"]==case["source_isi_s"] and metadata["window_s"]==window and
            metadata["before_children_playback"] is True,"burst_case_identity_mismatch")
    identity=metadata["axon_identity_before"]
    require(identity==metadata["axon_identity_after"] and identity["valid"] is True and
            identity["diagnostics"]==[] and identity["sha256"]==canonical_model_sha256(identity["model"]),
            "axon_identity_not_verified_or_changed")
    nodes={node["path"]:node for node in identity["model"]["nodes"]}
    require(len(nodes)==len(identity["model"]["nodes"]) and
            all(int(node["frequency_hz"])==frequency for node in nodes.values()),"axon_child_clock_mismatch")
    root=nodes["$"];parameter="NumSegments" if case["carrier"]=="NAxoneChain" else "NumNodes"
    require(scalar(root,parameter,"signed_integer")==length,"axon_length_mismatch")
    if case["carrier"]=="NAxoneChainAndDelay":
        require(scalar(root,"InternodeDelayTime","binary64")==.002,"axon_internode_default_mismatch")
        for i in range(1,length):require(scalar(nodes[f"$.Delay{i}"],"DelayTime","binary64")==.002,
                                       "axon_effective_internode_mismatch")
    lt_profiles=[]
    for i in range(1,length+1):
        zone=nodes[f"$.Segment{i}.LTZone"]
        profile={name:scalar(zone,name,kind) for name,kind in (("Threshold","binary64"),("ThresholdOff","binary64"),
                 ("PulseAmplitude","binary64"),("TimeConstant","binary64"),
                 ("UseLTZIntegtation","boolean"),("UseSpikeStabilizer","boolean"))}
        require(profile=={"Threshold":.02,"ThresholdOff":0.,"PulseAmplitude":1.,"TimeConstant":.00144,
                          "UseLTZIntegtation":True,"UseSpikeStabilizer":True},"effective_ltzone_profile_mismatch")
        lt_profiles.append({"segment":i,"class":zone["class"],**profile})
    columns=["tick","time","source","axon"]+[f"segment{i}" for i in range(1,length+1)]
    data=trace(payload,frequency,window,columns)
    inputs=checked_events(data["source"],metadata["source_events"],frequency,helper)
    outputs=checked_events(data["axon"],metadata["axon_events"],frequency,helper)
    require(len(inputs)==len(case["source_isi_s"])==metadata["expected_source_events"] and
            len(metadata["segment_events"])==length,"burst_source_or_segment_inventory_mismatch")
    segments=[]
    for i,native in enumerate(metadata["segment_events"],1):
        require(native["segment"]==i,"segment_event_order_changed")
        events=checked_events(data[f"segment{i}"],native["events"],frequency,helper)
        segments.append({"segment":i,"events":events,"association":assignment(native["assignment"],inputs,events,frequency)})
    require(data["axon"]==data[f"segment{length}"],"carrier_output_differs_from_last_segment")
    return {"id":case["id"],"capture_valid":True,"carrier":case["carrier"],"frequency_hz":frequency,"segments":length,
        "pattern":case["pattern"],"axon_model_sha256":identity["sha256"],"ltzone_profiles":lt_profiles,
        "source_events":inputs,"output_events":outputs,"segment_events":segments,
        "association":assignment(metadata["assignment"],inputs,outputs,frequency),
        "input_count":len(inputs),"output_count":len(outputs),"output_widths_s":[event["width_s"] for event in outputs]}


def manual(case,metadata,payload,helper,source):
    frequency=case["frequency_hz"];config_path=(source/case["input_config"]).resolve(strict=True)
    require(config_path.is_relative_to(source),"input_config_outside_sdk");config=read(config_path)
    require(metadata["kind"]=="axone_manual_synchronization_observation" and metadata["complete"] is True and
            metadata["frequency_hz"]==frequency and metadata["window_s"]==1.1 and
            metadata["source_config"]==config and metadata["config_sha256"]==sha(config_path),"manual_case_identity_mismatch")
    data=trace(payload,frequency,1.1,["tick","time","source","path1","path2","path3","path4"])
    inputs=checked_events(data["source"],metadata["source_events"],frequency,helper)
    require(len(inputs)==4 and [event["onset_tick"] for event in inputs]==config["calibrated_source_ticks"] and
            len(metadata["paths"])==4 and metadata["selected_target_tick"]==config["selected_arrival_tick"],
            "manual_source_or_target_mismatch")
    paths=[]
    for i,native in enumerate(metadata["paths"]):
        expected=config["ideal_delay_paths"][i];delay=expected["desired_delay_ticks"]
        require(native["path"]==i+1 and native["delay_ticks"]==delay and native["frequency_hz"]==frequency and
                native["effective_delay_s"]==expected["configured_delay_s"] and
                math.floor(native["effective_delay_s"]*frequency)==delay,"manual_effective_delay_mismatch")
        values=data[f"path{i+1}"];events=checked_events(values,native["events"],frequency,helper)
        require(len(events)==4 and events[i]["onset_tick"]==config["selected_arrival_tick"],"manual_event_alignment_failed")
        require(all(value==(data["source"][tick-delay] if tick>=delay else 0.) for tick,value in enumerate(values)),
                "manual_full_fifo_waveform_shift_failed")
        for a,b in zip(inputs,events):require(b["onset_tick"]==a["onset_tick"]+delay and
            b["end_tick"]==a["end_tick"]+delay and not b["right_censored"],"manual_event_shift_failed")
        paths.append({"path":i+1,"delay_ticks":delay,"delay_s":delay/frequency,"events":events,
                      "full_waveform_shift_verified":True})
    return {"id":case["id"],"capture_valid":True,"frequency_hz":frequency,"nominal_span_ms":case["nominal_span_ms"],
            "source_events":inputs,"paths":paths,"selected_arrival_tick":config["selected_arrival_tick"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("data-root","gate-pointer","archive-adapter","event-helper","output"):
        parser.add_argument("--"+name,type=Path,required=True)
    for name in ("archive-id","archive-adapter-sha256","event-helper-sha256"):
        parser.add_argument("--"+name,required=True)
    args=parser.parse_args();sys.dont_write_bytecode=True
    require(os.name=="nt" and socket.gethostname().upper()=="AQUA3060","server15_required")
    adapter=module(args.archive_adapter,args.archive_adapter_sha256,"axon_matrix_archive")
    data,marker,_=adapter.root_identity(args.data_root,args.archive_id);output=args.output.resolve()
    require(output.is_relative_to(data/"Experiments") and not output.exists(),"fresh_analysis_output_required")
    output.mkdir(parents=True,exist_ok=False)
    result={"kind":"axone_conduction_matrix_analysis","schema_version":1,"analysis_complete":False,
            "producer_sha256":sha(Path(__file__)),"archive_id":args.archive_id,"scientific_verdict":None,
            "training":False,"receiver_present":False,"carrier_selected":False,"full_P1_accepted":False}
    try:
        adapter.verify(argparse.Namespace(data_root=data,archive_id=args.archive_id,verify_pointer=args.gate_pointer,
                                         maximum_bytes=4*1024**3,maximum_files=20000))
        pointer=read(args.gate_pointer);status=pointer["status"]
        require(status["role"]=="native" and status["validity"]=="valid" and
                status["process_closure"]=="bound_windows_job_closed" and
                status["process_evidence"]["runtime_provenance"]=="loaded_files_captured" and
                status["process_evidence"]["cooperative_capture"]=="completed","complete_observed_gate_required")
        gate=(data/pointer["attempt_relative"]).resolve(strict=True)
        verdict=read(gate/"result.json");protocol=read(gate/"source-protocol.json");runtime=read(gate/"runtime.json")
        modes={"axone_stabilized_burst_contract":("burst",60,"AxoneBurstDiagnostic"),
               "axone_manual_synchronization_contract":("manual",15,"AxoneManualSynchronization")}
        mode,count,folder=modes[protocol["kind"]]
        require(verdict["expected_cases"]==len(protocol["cases"])==count,"matrix_inventory_mismatch")
        source=Path(runtime["windows_source_root"]).resolve(strict=True);sys.path.insert(0,str(source))
        from Scripts.StructTrain.TimeLearner.runtime import source_closure
        from Scripts.StructTrain.TimeLearner.model_identity import canonical_model_sha256
        closure=source_closure(source);require(closure==runtime["source_closure"],"source_closure_changed")
        helper=module(args.event_helper,args.event_helper_sha256,"axon_matrix_events")
        folder=gate/"native-gate/native"/folder
        expected_ids={case["id"] for case in protocol["cases"]}
        require({p.stem for p in folder.glob("*.json")}.issubset(expected_ids) and
                {p.stem for p in folder.glob("*.csv")}.issubset(expected_ids),"unexpected_matrix_artifact")
        failed_tests=set(verdict["gate"]["inventory"]["failed_test_ids"])
        rows=[]
        for case in protocol["cases"]:
            metadata_path=folder/(case["id"]+".json");csv_path=metadata_path.with_suffix(".csv")
            try:
                metadata=read(metadata_path);require(metadata["id"]==case["id"],"case_id_mismatch")
                row=burst(case,metadata,csv_path,helper,canonical_model_sha256) if mode=="burst" else manual(case,metadata,csv_path,helper,source)
                row.update(metadata_sha256=sha(metadata_path),csv_sha256=sha(csv_path))
                row["native_assertions_passed"]=case["expected_test_id"] not in failed_tests
                if not row["native_assertions_passed"]:row.update(capture_valid=False,reason="native_case_assertion_failure")
            except (ValueError,RuntimeError,OSError,KeyError,TypeError) as error:
                row={"id":case["id"],"capture_valid":False,"reason":str(error)}
            rows.append(row)
        require(source_closure(source)==closure,"analysis_changed_source_files")
        result.update(mode=mode,source_commit=verdict["source_commit"],gate_result_sha256=sha(gate/"result.json"),
            source_archive_manifest_sha256=pointer["manifest"]["sha256"],event_helper_sha256=args.event_helper_sha256,
            archive_adapter_sha256=args.archive_adapter_sha256,rows=rows,
            analysis_complete=all(row["capture_valid"] for row in rows),
            native_assertion_status=verdict["gate"]["assertion_status"],failed_native_test_ids=sorted(failed_tests),
            common_identity_source_sha256=sha(source/"Scripts/StructTrain/TimeLearner/model_identity.py"),
            claim_scope="Declared engineering observations and shared native temporal associations; no causal ownership, learning, classification or final carrier selection.")
    except BaseException as error:result.update(error=str(error),traceback=traceback.format_exc())
    write(output/"result.json",result)
    print(json.dumps({"analysis_complete":result["analysis_complete"],"mode":result.get("mode"),
        "cases":len(result.get("rows",[])),"invalid":[row["id"] for row in result.get("rows",[]) if not row["capture_valid"]],
        "error":result.get("error")}))
    return 0 if result["analysis_complete"] else 1


if __name__=="__main__":raise SystemExit(main())
