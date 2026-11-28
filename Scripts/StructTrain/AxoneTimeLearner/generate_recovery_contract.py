"""Declare node recovery measurements and matched controls; source generation only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
CPP="Tests/Integration/Libraries/Test_PulseLib_AxoneRecoveryDiagnostic.cpp"
DESTINATION=ROOT/"Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner/protocols/P1-node-recovery-v1.json"

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--overwrite",action="store_true")
    args=parser.parse_args();capacities=[1e-9,2.5e-10,2.5e-11];taus=[.00144,.00036];cases=[]
    for frequency in (20000,40000):
        for c,capacity in enumerate(capacities):
            for t,tau in enumerate(taus):
                for gap in (2,4,8,16,32,80):
                    identity=f"f{frequency}_c{c}_t{t}_gap{gap}"
                    cases.append({"id":identity,"frequency_hz":frequency,"capacity_f":capacity,
                                  "lt_time_constant_s":tau,"gap_ms":gap,
                                  "expected_test_id":"P1Recovery/AxoneRecoveryDiagnostic.CapturesMatchedPairAndOmissionControls/"+identity})
    payload=(ROOT/CPP).read_bytes().replace(b"\r\n",b"\n")
    document={"kind":"axone_recovery_diagnostic_contract","schema_version":1,"protocol_id":"P1-node-recovery-v1",
              "status":"source_prepared","test_target":"Test_PulseLib_StorageComponents",
              "source_records":[{"workspace_path":CPP,"canonical_lf_bytes":len(payload),"canonical_lf_sha256":hashlib.sha256(payload).hexdigest()}],
              "cases":cases,"expected_test_ids":[case["expected_test_id"] for case in cases],
              "carrier":"NAxoneSegment","membrane_base":"NPMembraneBio",
              "fixed_ltzone":{"base_image":"NPLTZone","threshold":.02,"threshold_off":0,"pulse_amplitude":1,
                              "UseLTZIntegtation":True,"UseSpikeStabilizer":True},
              "phase_order":["silent","first_only","second_only","pair"],"window_s":.25,
              "source":{"dataset_class":"NDatasetMatrix","generator_class":"NPulseGeneratorTransit",
                        "samples":1,"features":1,"max_spikes":2,"state_generation":1,"time_generation_s":1,
                        "delay_s":2,"loop":False,"advance_sample_after_burst":False,"pulse_width_s":.001,
                        "amplitude":1,"frequency_deviation":0,"first_nominal_s":.01},
              "phase_isi":{"silent":[0,0],"first_only":[.01,0],"second_only":["0.01+gap_s",0],"pair":[.01,"gap_s"]},
              "source_count_assertions":[0,1,1,2],"source_time_tolerance_ticks":2,
              "reset":"full root reset at time zero before each phase; no Default of physical components",
              "remaining_physics":"Retain the exact effective stock membrane, resistance, feedback, inertial and generator parameters; archive full typed axon identity and require no change across phases.",
              "recorded_columns":["tick","time","source","inertial","exc_channel","inh_channel","soma_sum",
                                  "lt_input","lt_pre","lt_potential","output","feedback","exc_tau","inh_tau"],
              "event_threshold":.5,"temporal_association_lag_s":[0,.2],
              "artifact_subdirectory":"AxoneRecoveryDiagnostic","maximum_wall_seconds":7200,
              "maximum_memory_bytes":2*1024**3,"maximum_expected_primary_bytes":1024**3,
              "capture_verdict":"Complete finite capture, source controls and unchanged physical identity; output counts and refractory interval are measured, not required to succeed.",
              "limitations":["Exploratory factor grid prompted by sealed dense-burst failure; not an independent confirmation.",
                             "One isolated node; a positive pair response does not establish chain or tree packet conduction.",
                             "No training, receiver, saved classifier or physiological morphology calibration.",
                             "Four matched controls per condition, not four independent random replications."],
              "native_execution_performed":False,"scientific_result":None}
    encoded=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    if DESTINATION.exists() and DESTINATION.read_bytes()!=encoded and not args.overwrite:
        raise FileExistsError("publish a new version or regenerate an unpublished declaration")
    DESTINATION.parent.mkdir(parents=True,exist_ok=True);DESTINATION.write_bytes(encoded)
    print(json.dumps({"source_cases":len(cases),"presentations":len(cases)*4,"model_execution_performed":False}))

if __name__=="__main__":main()
