"""Derive repeatable manual-delay inputs from the sealed source-clock measurements on .15."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import socket


def require(value,reason):
    if not value:raise RuntimeError(reason)


def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,document):
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(document,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write("\n")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("data-root","source-pointer","archive-adapter","output"):
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--archive-id",required=True)
    parser.add_argument("--archive-adapter-sha256",required=True)
    args=parser.parse_args()
    require(os.name=="nt" and socket.gethostname().upper()=="AQUA3060","server15_required")
    adapter_path=args.archive_adapter.resolve(strict=True)
    require(sha(adapter_path)==args.archive_adapter_sha256,"archive_adapter_changed")
    specification=importlib.util.spec_from_file_location("axon_verified_archive_adapter",adapter_path)
    adapter=importlib.util.module_from_spec(specification);specification.loader.exec_module(adapter)
    adapter.verify(argparse.Namespace(data_root=args.data_root,archive_id=args.archive_id,
        verify_pointer=args.source_pointer,maximum_bytes=4*1024**3,maximum_files=20000))
    data,marker,_=adapter.root_identity(args.data_root,args.archive_id)
    pointer=read(args.source_pointer.resolve(strict=True))
    require(pointer["status"]["role"]=="native" and pointer["status"]["native_checks_passed"] is True,
            "accepted_source_clock_measurement_required")
    gate=(data/pointer["attempt_relative"]).resolve(strict=True)
    result=read(gate/"result.json");protocol=read(gate/"source-protocol.json")
    require(protocol["kind"]=="axone_historical_source_clock_contract" and result["expected_cases"]==15 and
            result["native_checks_passed"] is True,"unexpected_source_measurement")
    output=args.output.resolve()
    require(output.is_relative_to(data/"Experiments") and not output.exists(),"fresh_external_output_required")
    targets={target["span_ms"]:target for target in protocol["targets"]}
    documents=[]
    for case in protocol["cases"]:
        frequency=case["frequency_hz"];identity=case["id"]
        measurement=gate/"native-gate/native/AxoneHistoricalSourceClock"/(identity+".json")
        observed=read(measurement);target=targets[case["span_ms"]]
        require(observed["kind"]=="axone_historical_source_clock_observation" and observed["complete"] is True and
                observed["id"]==identity and observed["frequency_hz"]==frequency and
                observed["historical_recipe_canonical_lf_sha256"]==target["canonical_lf_sha256"] and
                observed["before_children_playback"] is True,"source_measurement_identity_mismatch")
        isi=[float(value) for value in target["historical_isi_decimal_s"]]
        events=observed["actual_source_events"];delays=observed["proposed_ideal_delays"]
        require(len(events)==len(delays)==len(isi)==4 and observed["initial_isi_s"]==isi,
                "incomplete_source_delay_vectors")
        ticks=[event["tick"] for event in events]
        require(all(type(tick) is int and tick>=0 for tick in ticks) and ticks==sorted(set(ticks)),
                "invalid_source_tick_vector")
        target_tick=ticks[-1]+frequency//1000
        for index,delay in enumerate(delays):
            desired=target_tick-ticks[index];parameter=delay["configured_delay_s"]
            require(delay["input_tick"]==ticks[index] and delay["target_tick"]==target_tick and
                    delay["desired_delay_ticks"]==desired and type(desired) is int and desired>0 and
                    math.isfinite(parameter) and parameter==math.nextafter(desired/frequency,math.inf) and
                    math.floor(parameter*frequency)==desired,"inconsistent_delay_proposal")
        documents.append((identity+".json",{
            "kind":"axone_manual_delay_condition","schema_version":1,
            "protocol_id":"P2-manual-synchronization-v1","id":identity,
            "status":"prepared_requires_native_composition","frequency_hz":frequency,
            "nominal_span_ms":case["span_ms"],"source":protocol["source"],"source_isi_s":isi,
            "calibrated_source_ticks":ticks,"ideal_delay_paths":delays,"selected_arrival_tick":target_tick,
            "window_s":1.1,"routing":"One ordinary generator sends every spike to every path.",
            "carrier":"NAxoneDelay","receiver_present":False,"training":False,
            "native_delay_execution_performed":False,"scientific_result":None,
            "provenance":{"archive_id":args.archive_id,"source_commit":result["source_commit"],
                "source_archive_manifest_relative":pointer["manifest_relative"],
                "source_archive_manifest_sha256":pointer["manifest"]["sha256"],
                "measurement_relative":measurement.relative_to(data).as_posix(),"measurement_sha256":sha(measurement),
                "source_protocol_sha256":sha(gate/"source-protocol.json"),
                "historical_recipe_canonical_lf_sha256":target["canonical_lf_sha256"]}}))
    require(len(documents)==15 and len({name for name,_ in documents})==15,"source_case_inventory_changed")
    output.mkdir(parents=True,exist_ok=False)
    records=[]
    for name,document in documents:
        destination=output/name;write(destination,document)
        records.append({"path":name,"sha256":sha(destination),"bytes":destination.stat().st_size})
    write(output/"result.json",{"kind":"axone_calibrated_delay_input_generation","schema_version":1,
        "analysis_complete":True,"model_execution_performed":False,"source_archive_pointer":str(args.source_pointer),
        "source_archive_pointer_sha256":sha(args.source_pointer),"producer_sha256":sha(Path(__file__)),
        "archive_adapter_sha256":args.archive_adapter_sha256,"files":records,
        "training":False,"scientific_verdict":None})
    print(json.dumps({"generated_source_conditions":len(records),"model_execution_performed":False}))


if __name__=="__main__":main()
