"""Generate reproducible source declarations; never execute the physical model."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
CPP="Tests/Integration/Libraries/Test_PulseLib_AxoneTimeLearner.cpp"
BASE="Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner"
DESTINATION=ROOT/BASE/"protocols/P2-terminal-controller-v2.json"

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overwrite",action="store_true",help="Regenerate an unpublished declaration.")
    args=parser.parse_args()
    tests=re.findall(r"TEST_F\(AxoneTimeLearner,\s*(\w+)\)",(ROOT/CPP).read_text(encoding="utf-8"))
    if len(tests)!=8 or len(set(tests))!=8:raise ValueError("terminal_controller_inventory_changed")
    sources=[]
    for source in (CPP,"Libraries/Nmsdk-PulseLib/Core/NNeuronAxoneTimeLearner.h",
                   "Libraries/Nmsdk-PulseLib/Core/NNeuronAxoneTimeLearner.cpp"):
        payload=(ROOT/source).read_bytes().replace(b"\r\n",b"\n")
        sources.append({"workspace_path":source,"canonical_lf_bytes":len(payload),
                        "canonical_lf_sha256":hashlib.sha256(payload).hexdigest()})
    document={"kind":"axone_terminal_controller_contract","schema_version":1,
              "protocol_id":"P2-terminal-controller-v2","status":"source_prepared",
              "supersedes_source_declaration":"P2-terminal-controller-v1; superseded by source review before native execution",
              "test_target":"Test_PulseLib_StorageComponents","source_records":sources,
              "expected_test_ids":["AxoneTimeLearner."+name for name in tests],
              "frequency_hz":2000,"window_s":.3,"source_isi_s":[.01,.08],"expected_source_ticks":[20,180],
              "source":{"dataset_class":"NDatasetMatrix","generator_class":"NPulseGeneratorTransit",
                        "amplitude":1,"pulse_width_s":.001,"frequency_deviation":0,"state_generation":1,
                        "time_generation_s":1,"delay_s":2,"loop":False,"advance_sample_after_burst":False},
              "tree":{"fixed_stem":{"carrier":"NAxoneChain","segments":1},
                      "private_leaves":2,"leaf_carrier":"NAxoneChainAndDelay","leaf_segments":3,
                      "initial_internode_delay_s":.002,"editable_internode":1,
                      "ltzone":{"base_image":"NPLTZone","threshold":.02,"threshold_off":0,
                                "UseSpikeStabilizer":True,"UseLTZIntegtation":True,"TimeConstant_s":.00144,"pulse_amplitude":1}},
              "receiver":{"base_image":"NSPNeuronGen","soma_parts":2,"dendrite_lengths":[1,1],
                          "synapses_per_terminal":1,"threshold":.0117,"exc_capacity":1e-9,"inh_capacity":1e-9,
                          "exc_resistance":1e7,"inh_resistance":1e8,"synapse_resistance":86e6},
              "controller":{"class":"NNeuronAxoneTimeLearner","version":1,"objective":"terminal_onset_diagnostic",
                            "maximum_presentations":2048,"maximum_internode_delay_s":.6,"alignment_tolerance_ticks":2,
                            "reference_path":"last","edit":"bounded managed terminal Delay1, unchanged reference",
                            "normalization":"not_implemented","is_trained":False},
              "artifact_subdirectory":"AxoneTimeLearner","maximum_wall_seconds":1800,
              "maximum_memory_bytes":2*1024**3,"native_execution_performed":False,"scientific_result":None,
              "claim_scope":"Ownership, scheduler, guarded parameter edit, all-event terminal alignment, fresh verification and invalidation after edits. Not full neuronal learning, local plasticity, classification or a final carrier choice."}
    payload=(json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
    if DESTINATION.exists() and DESTINATION.read_bytes()!=payload and not args.overwrite:
        raise FileExistsError("publish a new version or explicitly regenerate unpublished inputs")
    DESTINATION.parent.mkdir(parents=True,exist_ok=True);DESTINATION.write_bytes(payload)
    print(json.dumps({"source_cases":len(tests),"model_execution_performed":False}))

if __name__=="__main__":main()
