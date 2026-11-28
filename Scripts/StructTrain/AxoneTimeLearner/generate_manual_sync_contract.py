"""Declare physical ideal-delay composition checks from committed calibrated inputs; source generation only."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE="Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner"
CPP="Tests/Integration/Libraries/Test_PulseLib_AxoneManualSynchronization.cpp"
DESTINATION=ROOT/BASE/"protocols/P2-manual-synchronization-v1.json"


def main():
    cases=[];sources=[]
    def source(relative):
        payload=(ROOT/relative).read_bytes().replace(b"\r\n",b"\n")
        sources.append({"workspace_path":relative,"canonical_lf_bytes":len(payload),
                        "canonical_lf_sha256":hashlib.sha256(payload).hexdigest()})
    source(CPP)
    for frequency in (2000,20000,40000):
        for span in (25,50,100,200,480):
            identity=f"span{span}_f{frequency}"
            relative=BASE+f"/P2/manual-delay-calibrated-v1/{identity}.json";source(relative)
            cases.append({"id":identity,"frequency_hz":frequency,"nominal_span_ms":span,"input_config":relative,
                          "expected_test_id":"P2Manual/AxoneManualSynchronization.PhysicallyShiftsEverySpikeAndAlignsSelectedEvents/"+identity})
    document={"kind":"axone_manual_synchronization_contract","schema_version":1,
        "protocol_id":"P2-manual-synchronization-v1","status":"source_prepared",
        "test_target":"Test_PulseLib_StorageComponents","source_records":sources,"cases":cases,
        "expected_test_ids":[case["expected_test_id"] for case in cases],"artifact_subdirectory":"AxoneManualSynchronization",
        "window_s":1.1,"maximum_wall_seconds":900,"maximum_memory_bytes":2*1024**3,
        "source":"NDatasetMatrix with one ordinary NPulseGeneratorTransit; every pulse reaches all four paths",
        "carrier":"Four separate NAxoneDelay components using the declared calibrated parameters",
        "assertions":["actual source ticks equal the calibrated input","all four events survive each path",
                      "all onset and end ticks shift by the declared integer delay","selected events share the declared target tick",
                      "effective source, clocks, delay parameters and pattern remain as declared"],
        "receiver_present":False,"training":False,"native_execution_performed":False,"scientific_result":None,
        "claim_scope":"Physical ideal-delay composition before P2 receiving-neuron experiments; no classification or learning result."}
    payload=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    if DESTINATION.exists() and DESTINATION.read_bytes()!=payload:raise FileExistsError("publish a new protocol version")
    DESTINATION.write_bytes(payload);print(json.dumps({"source_cases":len(cases),"model_execution_performed":False}))


if __name__=="__main__":main()
