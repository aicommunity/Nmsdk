"""Materialize the source-only event-assignment contract. Never run native code."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
DESTINATION = ROOT / "Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner/protocols/P1-event-assignment.json"
SOURCES = (
    ("root", "Tests/Integration/Libraries/Test_PulseLib_AxoneConductionObservation.cpp"),
    ("Nmsdk-PulseLib", "Libraries/Nmsdk-PulseLib/Core/TimeLearner/AxoneConductionObservation.h"),
    ("Nmsdk-PulseLib", "Libraries/Nmsdk-PulseLib/Core/TimeLearner/AxoneConductionObservation.cpp"),
)

def main() -> None:
    records, tests = [], []
    for repository, relative in SOURCES:
        payload = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
        if len(payload) > 1024 * 1024:
            raise ValueError("source_exceeds_1MiB")
        records.append({"repository": repository, "workspace_path": relative,
                        "canonical_lf_bytes": len(payload),
                        "canonical_lf_sha256": hashlib.sha256(payload).hexdigest()})
        if repository == "root":
            tests = ["AxoneConductionObservation." + name for name in re.findall(
                r"TEST\(AxoneConductionObservation,\s*(\w+)\)", payload.decode("utf-8"))]
    if not tests or len(tests) != len(set(tests)):
        raise ValueError("invalid_test_inventory")
    document = {
        "kind": "axone_event_assignment_contract", "schema_version": 1,
        "protocol_id": "P1-event-assignment-v1", "status": "source_prepared",
        "test_target": "Test_PulseLib_StorageComponents", "expected_test_ids": tests,
        "source_records": records, "native_execution_performed": False,
        "model_execution": False, "scientific_result": None,
        "claim_scope": "Engineering event extraction and temporal association only; no causal-conduction or learning certificate.",
    }
    encoded = (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if DESTINATION.exists() and DESTINATION.read_bytes() != encoded:
        raise FileExistsError("publish a new contract version instead of replacing different declared inputs")
    DESTINATION.write_bytes(encoded)
    print(json.dumps({"files": 1, "source_test_cases": len(tests), "native_execution_performed": False}))

if __name__ == "__main__":
    main()
