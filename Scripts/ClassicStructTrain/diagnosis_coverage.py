"""Account for the fixed cohort and distinguish conditional expansions."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import WORK, PREVIOUS, PILOT, MEASURED_FACTORS, load, save, sha, ROOT


def run():
    data = load(WORK / "diagnosis-analysis.json")
    status = Counter((p["phase"], p["status"]) for p in data["processes"])
    cases = load(WORK / "locked-inference-cases.json")
    physical_conditions = len(MEASURED_FACTORS) + 2
    prefix_schedule = WORK / "verified-prefix-schedule.json"
    scheduled = load(prefix_schedule) if prefix_schedule.exists() else []
    first_tick = sum("first-tick" in row["physical_factors"] for row in scheduled)
    expected = {
        "reference": len(cases), "pilot": len(PILOT) * physical_conditions + first_tick,
        "pilot-prefix": 2 * (len(PILOT) * physical_conditions + first_tick),
        "training-pilot": 54, "sequences": 21, "limits": 6, "parser": 3,
        "training-factors": 99, "profile-inference": 24, "training-order": 54,
        "pilot-window": 6, "warm-order": 9,
    }
    # Extra full repeats are recorded as additional evidence. They cannot
    # satisfy a missing condition from the scheduled first-pass cohort.
    initial_names = {f"{label}-{mode}-r1" for label in PILOT
                     for mode in ("baseline", *MEASURED_FACTORS, "reversal")}
    initial_names.update(f"{row['label']}-first-tick-r1" for row in scheduled
                         if "first-tick" in row["physical_factors"])
    for process in data["processes"]:
        if process["phase"] == "pilot" and process["run"] not in initial_names:
            status["pilot", process["status"]] -= 1
            status["pilot-extra", process["status"]] += 1
    expansion = WORK / "expansion-decision.json"
    training_expansion = WORK / "training-expansion-decision.json"
    if expansion.exists():
        decision = load(expansion)
        expected["expansion"] = len(decision["out_of_pilot_models"]) * (
            2 + len(decision["factors_with_repeatable_binary_effect"]))
    if training_expansion.exists():
        expected["training-ten"] = sum((10 - len(row["pilot_ids"])) for row in load(training_expansion)
                                       if row["expanded"])
    order_expansion = WORK / "training-order-expansion.json"
    if order_expansion.exists():
        expected["training-ten-order"] = sum(14 for row in load(order_expansion) if row["expanded"])
    for name in ("matched-training-order", "matched-warm-order"):
        if (WORK / "runs" / name).exists():
            expected[name] = 54 if name == "matched-training-order" else 9
    for prefix in ("warm-order-prefix-", "matched-warm-order-prefix-"):
        for phase in (WORK / "runs").glob(prefix + "*"):
            if phase.is_dir():
                schedule = WORK / f"{phase.name}-schedule.json"
                expected[phase.name] = len(load(schedule)["runs"]) if schedule.exists() else 3
    matched_expansion = WORK / "matched-training-order-expansion.json"
    if matched_expansion.exists():
        expected["matched-training-ten-order"] = sum(14 for row in load(matched_expansion) if row["expanded"])
    snapshot_resolution = WORK / "snapshot-resolution.json"
    snapshots = load(snapshot_resolution) if snapshot_resolution.exists() else {}
    if snapshots:
        expected["snapshot-inference"] = len(snapshots["representatives"])
        wanted = set(snapshots["representatives"])
        for process in data["processes"]:
            if process["phase"] == "snapshot-inference" and process["run"] not in wanted:
                status["snapshot-inference", process["status"]] -= 1
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
        "prefix_schedule_bound": len(scheduled) == len(PILOT),
        "training_order_expansion_decided": order_expansion.exists(),
        "snapshots_measured": status["snapshot-inference", "completed"],
        "snapshots_reused": len(snapshots.get("aliases", {})),
        "traces_measured": sum(n for (phase, result), n in status.items()
                                if phase.startswith("tick-") and result == "completed"),
    })
    print(f"Coverage checked for {len(rows)} phases, previous evidence unchanged: {passed}")


if __name__ == "__main__":
    run()
