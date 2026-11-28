"""Declare stabilized axonal burst and length conditions; generate source inputs only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE="Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner"
CPP="Tests/Integration/Libraries/Test_PulseLib_AxoneBurstDiagnostic.cpp"
HEADER="Tests/Integration/Libraries/AxoneHistoricalTargets.inc"
DESTINATION=ROOT/BASE/"protocols/P1-stabilized-bursts-and-lengths-v1.json"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite",action="store_true",help="Regenerate source inputs after reviewing the unpublished change.")
    args=parser.parse_args()
    patterns={"single":[.01],"m4_isi2ms":[.01,.002,.002,.002],
              "m4_isi5ms":[.01,.005,.005,.005],"m16_isi2ms":[.01]+[.002]*15}
    for span in (25,480):
        document=json.loads((ROOT/BASE/f"P2/historical-patterns/span{span}ms.json").read_bytes())
        # The committed generated header remains the native source; preserve
        # the exact historical first ISI, not its normalized illustration.
        patterns[f"span{span}"]=[float(value) for value in document["target"]["historical_isi_decimal_s"]]
    cases=[]
    for frequency in (20000,40000,100000):
        for carrier in ("NAxoneChain","NAxoneChainAndDelay"):
            declarations=[(length,"single") for length in (1,3,7,15,31)]
            declarations += [(3,name) for name in ("span25","span480","m4_isi2ms","m4_isi5ms","m16_isi2ms")]
            for length,pattern in declarations:
                identity=f"{carrier}_f{frequency}_n{length}_{pattern}"
                cases.append({"id":identity,"frequency_hz":frequency,"carrier":carrier,"segments":length,
                              "pattern":pattern,"source_isi_s":patterns[pattern],
                              "window_s":.75 if pattern=="span480" else .25,
                              "internode_delay_s":.002 if carrier=="NAxoneChainAndDelay" else None,
                              "expected_test_id":"P1Stable/AxoneBurstDiagnostic.CapturesDeclaredBurstAndLengthCondition/"+identity})
    sources=[]
    for source in (CPP,HEADER,*[BASE+f"/P2/historical-patterns/span{span}ms.json" for span in (25,480)]):
        payload=(ROOT/source).read_bytes().replace(b"\r\n",b"\n")
        sources.append({"workspace_path":source,"canonical_lf_bytes":len(payload),
                        "canonical_lf_sha256":hashlib.sha256(payload).hexdigest()})
    document={"kind":"axone_stabilized_burst_contract","schema_version":1,
              "protocol_id":"P1-stabilized-bursts-and-lengths-v1","status":"source_prepared",
              "test_target":"Test_PulseLib_StorageComponents","source_records":sources,
              "expected_test_ids":[case["expected_test_id"] for case in cases],"cases":cases,
              "source":{"dataset_class":"NDatasetMatrix","generator_class":"NPulseGeneratorTransit",
                        "samples":1,"features":1,"state_generation":1,"time_generation_s":1,
                        "delay_s":2,"loop":False,"advance_sample_after_burst":False,
                        "pulse_width_s":.001,"amplitude":1,"frequency_deviation":0},
              "axon_ltzone":{"base_image":"NPLTZone","cpp_class":"NPulseLTZone","threshold":.02,
                              "threshold_off":0,"pulse_amplitude":1,"UseLTZIntegtation":True,
                              "UseSpikeStabilizer":True,"TimeConstant_s":.00144},
              "profile_selection":"Exploratory candidate from the preceding 54-cell fixed grid; not independent confirmation or final carrier selection.",
              "global_clock_constraint":"frequency divides 1,000,000; UTimeControl increments integer microseconds",
              "event_threshold":.5,"temporal_assignment_lag_s":[0,.2],
              "artifact_subdirectory":"AxoneBurstDiagnostic","training":False,
              "native_execution_performed":False,"scientific_result":None,
              "maximum_wall_seconds":7200,"maximum_memory_bytes":2*1024**3,
              "capture_contract":["finite full window and exact global clock grid","effective source and unchanged axon identity",
                                  "all descendant rates match","actual source wavefront count matches pattern"],
              "measurement":["all segment and final events, widths, extra and missing spikes",
                             "all maximum ordered temporal associations and ambiguity",
                             "length-latency curve and dt dependence within the declared windows"],
              "limitations":["One execution, not three independent initializations or complete P1 acceptance.",
                             "Output conduction is measured, not required by the capture assertion.",
                             "No structural edit, saved replay, receiving neuron or learning."]}
    encoded=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    if DESTINATION.exists() and DESTINATION.read_bytes()!=encoded and not args.overwrite:
        raise FileExistsError("publish a new protocol version or explicitly regenerate unpublished inputs")
    DESTINATION.parent.mkdir(parents=True,exist_ok=True);DESTINATION.write_bytes(encoded)
    print(json.dumps({"source_cases":len(cases),"model_execution_performed":False}))


if __name__=="__main__":main()
