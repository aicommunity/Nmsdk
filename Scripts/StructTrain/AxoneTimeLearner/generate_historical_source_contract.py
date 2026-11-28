"""Generate pinned historical targets and a native source-clock recipe, without calculation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner"
CPP="Tests/Integration/Libraries/Test_PulseLib_AxoneHistoricalSourceClock.cpp"
HEADER="Tests/Integration/Libraries/AxoneHistoricalTargets.inc"
DESTINATION=BASE/"protocols/P2-source-clock-v1.json"


def canonical(path):
    return path.read_bytes().replace(b"\r\n",b"\n")


def write_same(path,payload):
    if path.exists() and canonical(path)!=payload:
        raise FileExistsError("publish a new source contract instead of replacing different declared inputs")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(payload)


def main():
    records=[];targets=[];cases=[]
    lines=["// Generated source inputs; see generate_historical_source_contract.py.",
           "#pragma once","#include <array>","#include <string>","#include <vector>",
           "namespace NmsdkTests {",
           "struct AxoneHistoricalTarget { int spanMs; std::array<double,4> isi; std::string recipeSha256; };",
           "inline std::vector<AxoneHistoricalTarget> AxoneHistoricalTargets() { return {"]
    for span in (25,50,100,200,480):
        source=BASE/f"P2/historical-patterns/span{span}ms.json"
        payload=canonical(source);document=json.loads(payload)
        isi=document["target"]["historical_isi_decimal_s"]
        if len(isi)!=4:
            raise ValueError("expected_four_historical_source_intervals")
        digest=hashlib.sha256(payload).hexdigest()
        lines.append("    {"+str(span)+", {"+", ".join(isi)+"}, \""+digest+"\"},")
        relative=source.relative_to(ROOT).as_posix()
        targets.append({"span_ms":span,"input_recipe":relative,"canonical_lf_sha256":digest,
                        "historical_isi_decimal_s":isi})
        records.append({"repository":"Bin","workspace_path":relative,"canonical_lf_bytes":len(payload),
                        "canonical_lf_sha256":digest})
    lines+=["}; }","}",""]
    write_same(ROOT/HEADER,"\n".join(lines).encode("utf-8"))
    for relative in (CPP,HEADER):
        payload=canonical(ROOT/relative)
        records.append({"repository":"root","workspace_path":relative,"canonical_lf_bytes":len(payload),
                        "canonical_lf_sha256":hashlib.sha256(payload).hexdigest()})
    for frequency in (2000,20000,40000):
        for span in (25,50,100,200,480):
            identity=f"span{span}_f{frequency}"
            cases.append({"id":identity,"span_ms":span,"frequency_hz":frequency,
                "expected_test_id":"P2Source/AxoneHistoricalSourceClock.CapturesActualTargetEventsAndGridDelays/"+identity})
    document={"kind":"axone_historical_source_clock_contract","schema_version":1,
        "protocol_id":"P2-source-clock-v1","status":"source_prepared","test_target":"Test_PulseLib_StorageComponents",
        "source_records":records,"targets":targets,"cases":cases,
        "expected_test_ids":[c["expected_test_id"] for c in cases],
        "source":{"dataset_class":"NDatasetMatrix","generator_class":"NPulseGeneratorTransit",
                  "NumSamples":1,"NumFeatures":1,"MaxSpikesPerFeature":4,"Delay_s":2,
                  "AdvanceSampleAfterBurst":False,"LoopSamples":False,"StateGeneration":1,
                  "TimeGeneration_s":1,"pulse_width_s":.001,"amplitude":1,"frequency_deviation":0},
        "window_s":1.1,"artifact_subdirectory":"AxoneHistoricalSourceClock",
        "ideal_delay_proposal":{"target":"last_observed_source_tick+frequency/1000",
             "delay_ticks":"target_tick-input_tick",
             "parameter":"nextafter(delay_ticks/frequency,+infinity); require floor(parameter*frequency)==delay_ticks"},
        "native_execution_performed":False,"training":False,"scientific_result":None,
        "claim_scope":"Native source event calibration and ideal-grid proposals only. No receiver, physical delay execution, learning or classification result."}
    encoded=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    write_same(DESTINATION,encoded)
    print(json.dumps({"source_cases":len(cases),"generated_header":HEADER,"model_execution_performed":False}))


if __name__=="__main__":
    main()
