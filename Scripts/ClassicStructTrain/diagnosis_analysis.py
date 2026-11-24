"""Audit controlled results, preserving per-input and per-iteration attribution."""
from collections import Counter, defaultdict
from itertools import zip_longest
from pathlib import Path
import json
import sys
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import ROOT, WORK, PREVIOUS, FACTORS, PILOT, records, load, save, sha, relative


def rows_of(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def iteration_identity(row):
    return {key: row.get(key) for key in (
        "iteration", "model_time", "dendrites", "synapses", "dend_status", "synapse_status",
        "dissynchronization", "amp_difference", "soma_maxima", "is_need_to_train",
    )}


def first_iteration(left, right):
    for i, (a, b) in enumerate(zip_longest(
            rows_of(left / "iterations.jsonl"), rows_of(right / "iterations.jsonl")), 1):
        if a is None or b is None:
            return {"record": i, "fields": ["end_of_log"]}
        state_a, state_b = iteration_identity(a), iteration_identity(b)
        fields = [key for key in state_a if state_a[key] != state_b[key]]
        if fields:
            return {"record": i, "fields": fields,
                    "base": {key: state_a[key] for key in fields}, "changed": {key: state_b[key] for key in fields}}
    return None


def actual_profile(path):
    if not path.exists():
        return []
    rows = Counter()
    for element in ET.parse(path).getroot().iter():
        if element.attrib.get("Class") not in {"NPulseSynapse", "NPulseSynapseStdp"}:
            continue
        parameters = element.find("Parameters")
        if parameters is not None:
            rows[tuple(parameters.findtext(name) for name in ("Resistance", "SecretionTC", "DissociationTC"))] += 1
    return [dict(resistance_ohm=r, secretion_s=s, dissociation_s=d, components=n)
            for (r, s, d), n in sorted(rows.items(), key=lambda x: repr(x[0]))]


def trace_differences(left, right):
    first = {}
    fields = ("drives", "generators", "synapses", "soma", "zone_V", "zone_output", "wrapper_output", "registered")
    left_rows = ((row["input_id"], row["tick"], row) for row in rows_of(left) if "registered" in row)
    right_rows = ((row["input_id"], row["tick"], row) for row in rows_of(right) if "registered" in row)
    b = next(right_rows, None)
    for i, t, a in left_rows:
        while b is not None and b[:2] < (i, t):
            b = next(right_rows, None)
        if b is None:
            break
        if b[:2] != (i, t):
            continue
        for field in fields:
            key = (i, field)
            if key not in first and a.get(field) != b[2].get(field):
                first[key] = {"input_id": i, "quantity": field, "tick": t,
                              "baseline_time_s": a["time_from_input_s"], "changed_time_s": b[2]["time_from_input_s"]}
    return list(first.values())


def first_training_tick(left, right):
    candidates = (left / "waveforms.jsonl", right / "waveforms.jsonl")
    if not all(p.exists() and p.stat().st_size for p in candidates):
        return {}
    observations = [ (row for row in rows_of(path) if row.get("phase") == "training")
                    for path in candidates ]
    changes = {}
    for a, b in zip(*observations):
        if a["tick"] != b["tick"]:
            break
        for key in ("generators", "synapses", "soma", "zone_V", "zone_output", "before", "after"):
            if key not in changes and a.get(key) != b.get(key):
                changes[key] = a["tick"]
    return changes


def audit():
    processes = []
    inference = {}
    training = {}
    trace_comparisons = []
    sequences = defaultdict(list)
    for process in sorted((WORK / "runs").glob("*/*/process.json")):
        metadata = load(process)
        folder = process.parent
        group = folder.parent.name
        run_id = folder.name
        processes.append({"phase": group, "run": run_id, "path": relative(process),
                          **{k: metadata[k] for k in ("status", "binary_sha256", "manifest_sha256")},
                          "seconds": metadata.get("elapsed_wall_seconds")})
        if metadata["status"] != "completed":
            continue
        source = folder / "results.jsonl"
        if not source.exists() or source.stat().st_size == 0:
            continue
        run = records(source)
        row = run[0]
        if "answers" in row:
            inference[group, run_id] = row, folder
        if row.get("record_type") == "training":
            training[group, run_id] = row, folder
        if group == "sequences":
            for entry in run:
                sequences[run_id].append({key: entry.get(key) for key in (
                    "record_type", "stage_index", "dendrites", "synapses", "status", "stop_reason", "iterations",
                    "ticks", "model_time", "elapsed_model_time", "TP", "FP", "FN", "TN", "answers",
                )})
    compare = []
    case_file = WORK / "locked-inference-cases.json"
    items = load(case_file) if case_file.exists() else []
    for item in items:
        label = item["label"]
        group = "pilot" if label in PILOT else "expansion"
        for factor in FACTORS:
            for repeat in range(1, 4):
                keys = [f"{label}-{condition}-r{repeat}" for condition in ("baseline", factor, "reversal")]
                if any((group, key) not in inference for key in keys):
                    continue
                (a, ap), (b, bp), (c, cp) = [inference[group, key] for key in keys]
                assert a["input_ids"] == b["input_ids"] == c["input_ids"]
                assert all(row["structure_unchanged"] and row["training_disabled"] for row in (a, b, c))
                before = a["answers"]
                history = item.get("historical")
                changed = []
                for index, (identifier, av, bv) in enumerate(zip(a["input_ids"], before, b["answers"], strict=True)):
                    if av != bv:
                        changed.append({
                            "id": identifier, "before": av, "after": bv, "historical": history[index] if history else None,
                            "margin_before_uV": a["decode_windows"][index]["margin_V"] * 1e6,
                            "margin_after_uV": b["decode_windows"][index]["margin_V"] * 1e6,
                            "first_zone_before": a["decode_windows"][index]["first_zone_tick"],
                            "first_zone_after": b["decode_windows"][index]["first_zone_tick"],
                        })
                compare.append({
                    "label": label, "factor": factor, "repeat": repeat, "changed": changed,
                    "same_original": before == item["expected"], "reversal": before == c["answers"],
                    "same_order": a["component_order"] == b["component_order"],
                    "metrics_before": {k: a[k] for k in ("TP", "FP", "FN", "TN")},
                    "metrics_after": {k: b[k] for k in ("TP", "FP", "FN", "TN")},
                    "history_diff_before": sum(x != y for x, y in zip(before, history, strict=True)) if history else None,
                    "history_diff_after": sum(x != y for x, y in zip(b["answers"], history, strict=True)) if history else None,
                    "same_peaks": a["zone_potential_peaks"] == b["zone_potential_peaks"],
                    "logs": [relative(path / "results.jsonl") for path in (ap, bp, cp)],
                })
    for group, run_id in inference:
        if not group.startswith("tick-"):
            continue
        factor = group.removeprefix("tick-")
        if not run_id.endswith("-" + factor + "-r1"):
            continue
        label = run_id.removesuffix("-" + factor + "-r1")
        a, ap = inference[group, label + "-baseline-r1"]
        b, bp = inference[group, run_id]
        trace_comparisons.append({"label": label, "factor": factor, "logs": [relative(ap), relative(bp)],
                                  "first_events": trace_differences(ap / "waveforms.jsonl", bp / "waveforms.jsonl")})
    observed = []
    for (group, run_id), (row, folder) in training.items():
        observation = inference.get(("snapshot-inference", run_id + "-baseline-r1"))
        observed.append({
            "phase": group, "run": run_id, "status": row["status"], "stop_reason": row.get("stop_reason", row["status"]),
            "d": row["dendrites"], "s": row["synapses"], "iterations": row["iterations"], "ticks": row["ticks"],
            "native_need_to_train": row.get("native_need_to_train"), "elapsed_model_s": row["elapsed_model_time"],
            "elapsed_wall_s": row["elapsed_wall_seconds"], "profile": actual_profile(folder / "trained/Model_00.xml"),
            "own_recognized": observation[0]["answers"][0] if observation else None, "directory": relative(folder),
        })
    observer = []
    for (group, run_id), (a, ap) in training.items():
        if group != "training-pilot" or "-plain-r" not in run_id:
            continue
        target = run_id.replace("-plain-r", "-trace-r")
        pair = training.get((group, target))
        if pair:
            b, bp = pair
            observer.append({"run": run_id, "same_end": all(a[k] == b[k] for k in ("status", "iterations", "ticks", "synapses", "dendrites")),
                             "first_difference": first_iteration(ap, bp), "logs": [relative(ap), relative(bp)]})
    training_comparisons = []
    combinations = (
        ("training-factors", "modern-default-", "archive-default-", "Архивный цикл при современном профиле"),
        ("training-factors", "modern-secretion2-", "archive-secretion2-", "Архивный цикл при секреции 2 мс"),
        ("training-factors", "modern-default-", "modern-secretion2-", "Секреция в современном цикле"),
        ("training-factors", "archive-default-", "archive-secretion2-", "Секреция в архивном цикле"),
        ("training-factors", "modern-default-", "modern-dissociation2-", "Фактическая диссоциация"),
        ("training-factors", "modern-default-", "modern-resistance100-", "Фактическое сопротивление"),
        ("training-factors", "modern-default-", "stop-tolerance-", "Допуск амплитуды"),
        ("training-factors", "modern-default-", "stop-keep-", "Продолжение после удаления"),
        ("training-factors", "stop-strict-", "stop-crossing-", "Пересечение цели"),
        ("training-factors", "modern-default-", "stop-reversal-", "Возврат исходного критерия NT"),
        ("training-order", "native-", "disabled-", "Явное обновление порядка при обучении"),
        ("training-order", "native-", "reversal-", "Возврат обновления порядка при обучении"),
    )
    for phase, before, after, title in combinations:
        for (group, name), (a, ap) in training.items():
            if group != phase or not name.startswith(before):
                continue
            suffix = name.removeprefix(before)
            other = training.get((phase, after + suffix))
            if other:
                b, bp = other
                training_comparisons.append({
                    "factor": title, "job": suffix, "iterations": [a["iterations"], b["iterations"]],
                    "status": [a["status"], b["status"]], "first_difference": first_iteration(ap, bp),
                    "first_training_ticks": first_training_tick(ap, bp),
                    "logs": [relative(ap), relative(bp)],
                })
    context = []
    for scheme in ("0_1", "0_1_4_full"):
        for repeat in range(1, 4):
            keys = [f"{scheme}-{name}-r{repeat}" for name in ("live", "snapshot", "pause")]
            if any(key not in sequences for key in keys):
                continue
            by_type = [{row["stage_index"] or 0: row for row in sequences[key] if row["record_type"] == "training"} for key in keys]
            aligned = sorted(set.intersection(*(set(row) for row in by_type)))
            for stage in aligned:
                a, b, c = (row[stage] for row in by_type)
                snapshot = inference.get(("snapshot-inference", f"{keys[1]}-s{stage}-baseline-r1"))
                live = next((row for row in sequences[keys[0]] if row["record_type"] == "evaluation_in_protocol"
                             and row["stage_index"] == stage), None)
                context.append({
                    "scheme": scheme, "repeat": repeat, "stage": stage,
                    "iterations": [row["iterations"] for row in (a, b, c)],
                    "time_s": [row["model_time"] for row in (a, b, c)],
                    "d": [row["dendrites"] for row in (a, b, c)], "s": [row["synapses"] for row in (a, b, c)],
                    "events": [row["status"] for row in (a, b, c)],
                    "live_Q": live["FP"] + live["FN"] if live else None,
                    "snapshot_Q": snapshot[0]["FP"] + snapshot[0]["FN"] if snapshot else None,
                })
    save(WORK / "diagnosis-analysis.json", {
        "processes": processes, "inference_comparisons": compare, "training": observed,
        "observer_pairs": observer, "tick_comparisons": trace_comparisons, "sequence_context": context,
        "training_comparisons": training_comparisons,
    })
    print(f"{len(processes)} processes, {len(compare)} paired controls, {len(observed)} training records")


if __name__ == "__main__":
    audit()
