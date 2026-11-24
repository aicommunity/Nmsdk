"""Account for the fixed cohort and distinguish conditional expansions."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import WORK, PREVIOUS, PILOT, FACTORS, load, save, sha, ROOT


def run():
    data = load(WORK / "diagnosis-analysis.json")
    status = Counter((p["phase"], p["status"]) for p in data["processes"])
    cases = load(WORK / "locked-inference-cases.json")
    expected = {
        "reference": len(cases), "pilot": len(PILOT) * (len(FACTORS) + 2) * 3,
        "training-pilot": 54, "sequences": 21, "limits": 6, "parser": 3,
        "training-factors": 99, "profile-inference": 24, "training-order": 54,
    }
    expansion = WORK / "expansion-decision.json"
    training_expansion = WORK / "training-expansion-decision.json"
    if expansion.exists():
        decision = load(expansion)
        expected["expansion"] = len(decision["out_of_pilot_models"]) * (
            2 + len(decision["factors_with_repeatable_binary_effect"])) * 3
    if training_expansion.exists():
        expected["training-ten"] = sum((10 - len(row["pilot_ids"])) * 3 for row in load(training_expansion)
                                       if row["expanded"])
    rows = [{
        "phase": phase, "planned": count, "completed_processes": status[phase, "completed"],
        "running": status[phase, "running"], "failed_processes": sum(n for (group, key), n in status.items()
            if group == phase and key not in {"completed", "running"}),
        "pending_processes": max(0, count - sum(n for (group, key), n in status.items() if group == phase)),
    } for phase, count in expected.items()]
    lock = load(PREVIOUS / "prior-evidence-lock.json")
    passed = all(sha(ROOT / name) == digest for name, digest in lock.items())
    save(WORK / "diagnosis-coverage.json", {
        "phases": rows, "previous_evidence_unchanged": passed,
        "inference_expansion_decided": expansion.exists(), "training_expansion_decided": training_expansion.exists(),
        "snapshots_measured": status["snapshot-inference", "completed"],
        "traces_measured": sum(n for (phase, result), n in status.items()
                                if phase.startswith("tick-") and result == "completed"),
    })
    print(f"Coverage checked for {len(rows)} phases, previous evidence unchanged: {passed}")


if __name__ == "__main__":
    run()
