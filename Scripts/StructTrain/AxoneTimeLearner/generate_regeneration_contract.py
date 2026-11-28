"""Declare a fixed 54-cell axonal spike-formation comparison; source generation only."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCE="Tests/Integration/Libraries/Test_PulseLib_AxoneRegenerationDiagnostic.cpp"
DESTINATION=ROOT/"Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner/protocols/P1-regeneration-comparison-v1.json"


def main():
    payload=(ROOT/SOURCE).read_bytes().replace(b"\r\n",b"\n")
    cases=[]
    for frequency in (2000,20000,40000):
        for carrier in ("NAxoneSegment","NAxoneChain","NAxoneChainAndDelay"):
            for profile in ("factory","stabilized"):
                for milli_threshold in (10,20,30):
                    identity=f"{carrier}_f{frequency}_{profile}_thr{milli_threshold}"
                    cases.append({"id":identity,"frequency_hz":frequency,"carrier":carrier,
                                  "segments":1 if carrier=="NAxoneSegment" else 3,
                                  "internode_delay_s":.002 if carrier=="NAxoneChainAndDelay" else None,
                                  "ltzone_profile":profile,"threshold_model_units":milli_threshold/1000,
                                  "expected_test_id":"P1Regeneration/AxoneRegenerationDiagnostic.CapturesDeclaredSpikeFormationComparison/"+identity})
    document={"kind":"axone_regeneration_comparison_contract","schema_version":1,
              "protocol_id":"P1-regeneration-comparison-v1","status":"source_prepared",
              "test_target":"Test_PulseLib_StorageComponents","expected_test_ids":[c["expected_test_id"] for c in cases],
              "source_records":[{"repository":"root","workspace_path":SOURCE,"canonical_lf_bytes":len(payload),
                                 "canonical_lf_sha256":hashlib.sha256(payload).hexdigest()}],
              "cases":cases,"window_s":.08,"source":{"image":"NPGenerator","frequency_hz":10,
                "pulse_width_s":.001,"amplitude":1,"delay_s":.01,"frequency_deviation":0},
              "ltzone_models":{"factory":{"cpp_class":"NPulseLTZoneThreshold","base_image":"NPulseLTZoneThreshold"},
                               "stabilized":{"cpp_class":"NPulseLTZone","base_image":"NPLTZone",
                                   "UseLTZIntegtation":True,"UseSpikeStabilizer":True,"TimeConstant_s":.00144}},
              "common_ltzone":{"ThresholdOff":0,"PulseAmplitude":1},
              "unchanged_factory_control":"factory profile at threshold 0.03",
              "threshold_grid_model_units":[.01,.02,.03],
              "artifact_subdirectory":"AxoneRegenerationDiagnostic",
              "native_execution_performed":False,"training":False,"scientific_result":None,
              "claim_scope":"Engineering capture of a declared model-parameter comparison. Nonzero conduction is measured, not required.",
              "limitations":["Exploratory fixed grid, not automatic threshold calibration.",
                             "RC spike stabilizer is an existing phenomenological model, not a validated biophysical action potential.",
                             "No full P1 burst, replay, dt convergence or learning acceptance."]}
    encoded=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    DESTINATION.parent.mkdir(parents=True,exist_ok=True)
    if DESTINATION.exists() and DESTINATION.read_bytes()!=encoded:
        raise FileExistsError("publish a new protocol version")
    DESTINATION.write_bytes(encoded)
    print(json.dumps({"source_cases":len(cases),"model_execution_performed":False}))


if __name__=="__main__":
    main()
