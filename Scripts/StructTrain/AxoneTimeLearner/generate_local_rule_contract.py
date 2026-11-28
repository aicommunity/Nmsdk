"""Publish source-only inputs for the local axonal timing-rule regressions."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
DESTINATION=ROOT/"Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner/protocols/P5-local-rule-unit-v1.json"
SOURCES=[
    ("root","Tests/Integration/Libraries/Test_PulseLib_AxoneLocalTimingRule.cpp"),
    ("Nmsdk-PulseLib","Libraries/Nmsdk-PulseLib/Core/TimeLearner/AxoneLocalTimingRule.h"),
    ("Nmsdk-PulseLib","Libraries/Nmsdk-PulseLib/Core/TimeLearner/AxoneLocalTimingRule.cpp"),
]


def main():
    records=[];tests=[]
    for repository,relative in SOURCES:
        payload=(ROOT/relative).read_bytes().replace(b"\r\n",b"\n")
        records.append({"repository":repository,"workspace_path":relative,
                        "canonical_lf_bytes":len(payload),
                        "canonical_lf_sha256":hashlib.sha256(payload).hexdigest()})
        if repository=="root":
            tests=["AxoneLocalTimingRule."+name for name in re.findall(
                r"TEST\(AxoneLocalTimingRule,\s*(\w+)\)",payload.decode("utf-8"))]
    if len(tests)!=11 or len(set(tests))!=11:
        raise ValueError("local_rule_test_inventory_changed")
    document={"kind":"axone_local_timing_rule_contract","schema_version":1,
              "protocol_id":"P5-local-rule-unit-v1","status":"source_prepared",
              "test_target":"Test_PulseLib_StorageComponents","expected_test_ids":tests,"source_records":records,
              "parameters":{"trace_time_constant_s":.01,"learning_rate_s":.0001,
                            "desired_lead_s":.001,"feedback_latency_s":0},
              "equations":{"pair_kernel":"eta*(Delta-lambda_eff)/tau*exp(-abs(Delta)/tau)",
                           "lambda_eff":"desired_lead+feedback_latency",
                           "coincident_pair":"-eta*lambda_eff/tau","trace_decay":"exact exponential"},
              "input_scope":"One arrival edge and one feedback edge per native tick, supplied in one batch.",
              "native_execution_performed":False,"model_execution":False,"scientific_result":None,
              "claim_scope":"Pure local trace/proposal implementation. No physical delay edit, training result, carrier selection or physiological validation."}
    encoded=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    DESTINATION.parent.mkdir(parents=True,exist_ok=True)
    if DESTINATION.exists() and DESTINATION.read_bytes()!=encoded:
        raise FileExistsError("publish a new contract version")
    DESTINATION.write_bytes(encoded)
    print(json.dumps({"source_cases":len(tests),"model_execution_performed":False}))


if __name__=="__main__":
    main()
