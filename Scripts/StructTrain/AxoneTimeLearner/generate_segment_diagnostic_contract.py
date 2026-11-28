"""Author the unchanged-factory diagnostic recipe without running a model."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "Tests/Integration/Libraries/Test_PulseLib_AxoneSegmentDiagnostic.cpp"
DESTINATION = ROOT/"Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner/protocols/P1-factory-diagnostic-v1.json"


def main():
    payload = (ROOT/SOURCE).read_bytes().replace(b"\r\n", b"\n")
    cases = []
    for frequency in (2000,20000,40000):
        for carrier in ("NAxoneSegment","NAxoneChain","NAxoneChainAndDelay"):
            name = f"{carrier}_f{frequency}"
            cases.append({"id": name, "carrier": carrier, "frequency_hz": frequency,
                          "segments": 1 if carrier == "NAxoneSegment" else 3,
                          "internode_delay_s": .002 if carrier == "NAxoneChainAndDelay" else None,
                          "expected_test_id": "P1Diagnostic/AxoneSegmentDiagnostic.CapturesUnchangedFactorySegmentDynamics/"+name})
    document = {"kind": "axone_factory_diagnostic_contract", "schema_version": 1,
                "protocol_id": "P1-factory-diagnostic-v1", "status": "source_prepared",
                "test_target": "Test_PulseLib_StorageComponents",
                "expected_test_ids": [case["expected_test_id"] for case in cases], "cases": cases,
                "source_records": [{"repository": "root", "workspace_path": SOURCE,
                                    "canonical_lf_bytes": len(payload),
                                    "canonical_lf_sha256": hashlib.sha256(payload).hexdigest()}],
                "window_s": .08, "source": {"image": "NPGenerator", "frequency_hz": 10,
                    "pulse_width_s": .001, "amplitude": 1, "delay_s": .01, "frequency_deviation": 0},
                "artifact_subdirectory": "AxoneSegmentDiagnostic",
                "parameter_intervention": False, "training": False, "native_execution_performed": False,
                "scientific_result": None,
                "assertion_scope": "Finite complete capture; one real source emission; unchanged parameters. Output conduction is not an assertion.",
                "limitations": ["No threshold tuning.", "80ms is a diagnostic window, not a validated universal settling tail.",
                                "Does not replace the P1 burst or repeatability matrix."]}
    encoded = (json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False)+"\n").encode("utf-8")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if DESTINATION.exists() and DESTINATION.read_bytes() != encoded:
        raise FileExistsError("publish a new diagnostic contract instead of replacing different declared inputs")
    DESTINATION.write_bytes(encoded)
    print(json.dumps({"source_cases": len(cases), "model_execution_performed": False}))


if __name__ == "__main__":
    main()
