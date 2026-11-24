"""Audit controlled results, preserving per-input and per-iteration attribution."""
from collections import Counter, defaultdict
from copy import copy
from functools import lru_cache
from itertools import zip_longest
from pathlib import Path
import json
import sys
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import ROOT, WORK, PREVIOUS, FACTORS, PILOT, records, load, save, sha, relative
from legacy_recover import physical
from training_repro import component_order


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
        if not element.tag.startswith(("ExcSynapse", "InhSynapse")):
            continue
        parameters = element.find("Parameters")
        if parameters is not None:
            values = tuple(parameters.findtext(name) for name in ("Resistance", "SecretionTC", "DissociationTC"))
            if all(value is not None for value in values):
                rows[values] += 1
    return [dict(resistance_ohm=r, secretion_s=s, dissociation_s=d, components=n)
            for (r, s, d), n in sorted(rows.items(), key=lambda x: repr(x[0]))]


@lru_cache(maxsize=64)
def canonical_graph(path):
    return physical(ET.parse(path).getroot())


def observed_confusion(row, size):
    count = Counter(((i - 1) // 50 + 1 == row["target_class"], answer)
                    for i, answer in zip(row["input_ids"][:size], row["answers"][:size], strict=True))
    return dict(TP=count[True, 1], FP=count[False, 1], FN=count[True, 0], TN=count[False, 0])


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
                before, after = a.get(field), b[2].get(field)
                location = None
                if isinstance(before, list) and isinstance(after, list):
                    for index, (old, new) in enumerate(zip_longest(before, after), 1):
                        if old != new:
                            location = (old or new)[:2] if field == "synapses" else index
                            before, after = old, new
                            break
                first[key] = {"input_id": i, "quantity": field, "tick": t,
                              "component_index": location, "before": before, "after": after,
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
    matched_inputs = {}
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
        if group.startswith(("matched-training-", "matched-warm-")):
            command = metadata["command"]
            manifest = load(Path(command[command.index("--manifest") + 1]))
            assert manifest.pop("diagnostic_core") == {
                "disable_neuron_reorder": "disabled" in run_id.split("-")
            }, run_id
            pair_key = (group, run_id.removeprefix("matched-").removeprefix("warm-").split("-", 1)[1])
            common = (metadata["binary_sha256"], manifest)
            assert matched_inputs.setdefault(pair_key, common) == common, (group, run_id)
        source = folder / "results.jsonl"
        if not source.exists() or source.stat().st_size == 0:
            continue
        run = records(source)
        row = run[0]
        if "answers" in row:
            inference[group, run_id] = row, folder
        if row.get("record_type") == "training":
            training[group, run_id] = row, folder
        if group in {"sequences", "warm-order"} or group.startswith(("warm-order-prefix-", "matched-warm-")):
            key = f"{group}/{run_id}" if group not in {"sequences", "warm-order"} else run_id
            for entry in run:
                sequences[key].append({field: entry.get(field) for field in (
                    "record_type", "stage_index", "dendrites", "synapses", "status", "stop_reason", "iterations",
                    "ticks", "model_time", "elapsed_model_time", "TP", "FP", "FN", "TN", "answers", "input_ids",
                )})
    resolution = WORK / "snapshot-resolution.json"
    aliases = load(resolution)["aliases"] if resolution.exists() else {}

    def snapshot(key):
        return (inference.get(("snapshot-inference", key)) or
                inference.get(("snapshot-inference", aliases.get(key))))

    compare = []
    case_file = WORK / "locked-inference-cases.json"
    items = load(case_file) if case_file.exists() else []
    prefix_fields = ("input_ids", "answers", "zone_potential_peaks", "first_spikes", "decode_windows")
    for (phase, name), (prefix, _) in inference.items():
        if phase not in {"pilot-prefix", "pilot-window"}:
            continue
        first_name = name.rsplit("-r", 1)[0] + "-r1"
        full, _ = inference["pilot", first_name]
        length = len(prefix["input_ids"])
        assert all(prefix[key] == full[key][:length] for key in prefix_fields), ("Prefix changed", name)
    reference_audit = []
    for item in items:
        cached = inference.get(("reference", item["label"] + "-reference-r1"))
        if cached is None:
            continue
        measured, folder = cached
        process = load(folder / "process.json")
        reference_audit.append({
            "label": item["label"], "matches": measured["answers"] == item["expected"],
            "actual_binary": process["binary_sha256"], "original_binary": item["previous_binary_sha256"],
            "exact_original_binary": process["binary_sha256"] == item["previous_binary_sha256"],
            "log": relative(folder / "results.jsonl"),
        })
    for item in items:
        label = item["label"]
        group = "pilot" if label in PILOT else "expansion"
        for factor in FACTORS:
            for repeat in range(1, 4):
                keys = [f"{label}-{condition}-r{repeat}" for condition in ("baseline", factor, "reversal")]
                groups = (group, "pilot-prefix") if group == "pilot" else (group,)
                if label == "NT45" and factor == "window":
                    groups += ("pilot-window",)
                chosen = next((name for name in groups if all((name, key) in inference for key in keys)), None)
                effect_type = "separate_process"
                if chosen is not None:
                    (a, ap), (b, bp), (c, cp) = [inference[chosen, key] for key in keys]
                elif factor in {"wrapper", "first-tick"}:
                    chosen = next((name for name in groups if all((name, key) in inference for key in (keys[0], keys[2]))), None)
                    if chosen is None:
                        continue
                    (a, ap), (c, cp) = inference[chosen, keys[0]], inference[chosen, keys[2]]
                    if factor == "first-tick" and any(row["first_zone_tick"] == 0 for row in a["decode_windows"]):
                        continue
                    b, bp = copy(a), ap
                    if factor == "wrapper":
                        b["answers"] = a["wrapper_answers"]
                    effect_type = "simultaneous_outputs" if factor == "wrapper" else "no_event_on_excluded_tick"
                else:
                    continue
                assert a["input_ids"] == b["input_ids"] == c["input_ids"]
                assert all(row["structure_unchanged"] and row["training_disabled"] for row in (a, b, c))
                first_graph, changed_graph, restored_graph = [
                    canonical_graph(path / "loaded/Model_00.xml") for path in (ap, bp, cp)
                ]
                assert first_graph == changed_graph == restored_graph, ("Loaded graph changed", label, factor, repeat)
                before = a["answers"]
                history = item["historical"][:len(before)] if item.get("historical") else None
                changed = []
                for index, (identifier, av, bv) in enumerate(zip(a["input_ids"], before, b["answers"], strict=True)):
                    if av != bv:
                        changed.append({
                            "id": identifier, "before": av, "after": bv, "historical": history[index] if history else None,
                            "margin_before_uV": a["decode_windows"][index]["margin_V"] * 1e6,
                            "margin_after_uV": b["decode_windows"][index]["margin_V"] * 1e6,
                            "first_zone_before": a["decode_windows"][index]["first_zone_tick"],
                            "first_zone_after": b["decode_windows"][index]["first_zone_tick"],
                            "start_before_s": a["decode_windows"][index]["start_model_s"],
                            "start_after_s": b["decode_windows"][index]["start_model_s"],
                        })
                compare.append({
                    "label": label, "factor": factor, "repeat": repeat, "changed": changed,
                    "same_original": before == item["expected"][:len(before)], "reversal": before == c["answers"],
                    "physical_reversal": all(a[key] == c[key] for key in (
                        "input_ids", "answers", "first_spikes", "zone_potential_peaks", "decode_windows",
                        "component_order")),
                    "same_order": a["component_order"] == b["component_order"],
                    "observation_mode": effect_type, "tested_inputs": len(before),
                    "metrics_before": observed_confusion(a, len(before)),
                    "metrics_after": observed_confusion(b, len(before)),
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
        base = inference.get((group, label + "-baseline-r1"))
        if base is None:
            continue
        a, ap = base
        b, bp = inference[group, run_id]
        full = "pilot" if label in PILOT else "expansion"
        original_a = inference.get((full, label + "-baseline-r1"))
        original_b = inference.get((full, label + "-" + factor + "-r1"))
        if original_a is None or original_b is None:
            continue
        if not all(prefix[key] == original[0][key][:len(prefix["input_ids"])]
                   for prefix, original in ((a, original_a), (b, original_b)) for key in prefix_fields):
            raise AssertionError(("Prefix failed full sequence validation", label, factor))
        trace_comparisons.append({"label": label, "factor": factor, "logs": [relative(ap), relative(bp)],
                                  "validated_prefix": len(a["input_ids"]),
                                  "first_events": trace_differences(ap / "waveforms.jsonl", bp / "waveforms.jsonl")})
    observed = []
    for (group, run_id), (row, folder) in training.items():
        observation = snapshot(run_id + "-baseline-r1")
        observed.append({
            "phase": group, "run": run_id, "status": row["status"], "stop_reason": row.get("stop_reason", row["status"]),
            "d": row["dendrites"], "s": row["synapses"], "iterations": row["iterations"], "ticks": row["ticks"],
            "native_need_to_train": row.get("native_need_to_train"), "elapsed_model_s": row["elapsed_model_time"],
            "elapsed_wall_s": row["elapsed_wall_seconds"], "profile": actual_profile(folder / "trained/Model_00.xml"),
            "own_recognized": observation[0]["answers"][0] if observation else None,
            "own_zone_mV": observation[0]["zone_potential_peaks"][0] * 1000 if observation else None,
            "own_log": relative(observation[1] / "results.jsonl") if observation else None,
            "directory": relative(folder),
        })
    profile_controls = []
    roundtrip_controls = [
        {"phase": group, "run": run_id, "same_first_answer": row["roundtrip_same_first_answer"],
         "same_first_peak": row["roundtrip_same_first_peak"], "log": relative(folder / "results.jsonl")}
        for (group, run_id), (row, folder) in inference.items()
        if "roundtrip_same_first_answer" in row and not group.startswith("tick-")
    ]
    for (group, name), (row, folder) in inference.items():
        if group != "profile-inference":
            continue
        label, profile, repeat = name.rsplit("-", 2)
        baseline = inference.get((group, f"{label}-default-{repeat}"))
        changed_ids = [] if baseline is None else [i for i, a, b in zip(
            row["input_ids"], baseline[0]["answers"], row["answers"], strict=True) if a != b]
        changes = Counter()
        if baseline is not None:
            current = canonical_graph(folder / "after/Model_00.xml")
            unchanged = canonical_graph(baseline[1] / "after/Model_00.xml")
            assert current["links"] == unchanged["links"] and current["nodes"].keys() == unchanged["nodes"].keys()
            for node, old in unchanged["nodes"].items():
                new = current["nodes"][node]
                assert old["class"] == new["class"]
                for param in old["parameters"].keys() | new["parameters"].keys():
                    if old["parameters"].get(param) != new["parameters"].get(param):
                        changes[param] += 1
        profile_controls.append({
            "label": label, "profile": profile, "repeat": int(repeat[1:]), "changed_ids": changed_ids,
            "metrics": {k: row[k] for k in ("TP", "FP", "FN", "TN")},
            "physical_match": baseline is not None and all(row[key] == baseline[0][key] for key in (
                "input_ids", "answers", "zone_potential_peaks", "first_spikes", "decode_windows")),
            "actual_profile": actual_profile(folder / "after/Model_00.xml"), "parameter_changes": dict(changes),
            "directory": relative(folder),
        })
    observer = []
    for (group, run_id), (a, ap) in training.items():
        if group != "training-pilot" or "-plain-r" not in run_id:
            continue
        target = run_id.replace("-plain-r", "-trace-r")
        pair = training.get((group, target))
        if pair:
            b, bp = pair
            left = ET.parse(ap / "trained/Model_00.xml").getroot()
            right = ET.parse(bp / "trained/Model_00.xml").getroot()
            observer.append({"run": run_id,
                             "same_end": all(a[k] == b[k] for k in ("status", "iterations", "ticks", "synapses", "dendrites"))
                             and physical(left) == physical(right) and component_order(left) == component_order(right),
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
        ("training-ten-order", "native-", "disabled-", "Явное обновление порядка на контрольной десятке"),
        ("matched-training-order", "matched-native-", "matched-disabled-", "Изоляция обновления порядка на одном бинарнике"),
        ("matched-training-order", "matched-native-", "matched-reversal-", "Возврат обновления порядка на одном бинарнике"),
        ("matched-training-ten-order", "matched-native-", "matched-disabled-", "Обновление порядка на десятке на одном бинарнике"),
        ("matched-warm-order", "warm-native-", "warm-disabled-", "Первое различие учебного цикла в последовательности № 22 → № 37"),
        ("matched-warm-order", "warm-native-", "warm-reversal-", "Возврат исходной траектории № 22 → № 37"),
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
    structural = defaultdict(list)
    source = load(WORK / "source-audit.json").get("structure", {})
    for row in source.get("rows", []):
        structural[row["algorithm"], row["input_id"]].append(row)
    order_structure = []
    for (phase, identifier), (native, native_path) in training.items():
        if phase not in {"training-order", "training-ten-order", "matched-training-order",
                         "matched-training-ten-order"} or not identifier.endswith("-r1"):
            continue
        mode = identifier.removeprefix("matched-")
        if not mode.startswith("native-"):
            continue
        _, kind, target, _ = mode.split("-")
        tag = "NL" if kind == "learner" else "NT"
        flavor = "matched-" if phase.startswith("matched-") else ""
        comparison = training.get((phase, flavor + "disabled-" + mode.removeprefix("native-")))
        entries = structural.get((tag, int(target)), [])
        if comparison is None or not entries:
            continue
        disabled, disabled_path = comparison
        order_structure.append({
            "kind": tag, "target": int(target), "historical_d": sorted({tuple(r["dendrites"]) for r in entries}),
            "matched": bool(flavor),
            "cells": sorted({r["length_range"] for r in entries}),
            "source": source["path"], "sha256": source["sha256"],
            "native_d": native["dendrites"], "disabled_d": disabled["dendrites"],
            "native_matches": any(native["dendrites"] == r["dendrites"] for r in entries),
            "disabled_matches": any(disabled["dendrites"] == r["dendrites"] for r in entries),
            "logs": [relative(folder / "results.jsonl") for folder in (native_path, disabled_path)],
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
                evaluated = snapshot(f"{keys[1]}-s{stage}-baseline-r1")
                live = next((row for row in sequences[keys[0]] if row["record_type"] == "evaluation_in_protocol"
                             and row["stage_index"] == stage), None)
                changes = []
                if live and evaluated:
                    ids = evaluated[0]["input_ids"]
                    if live["input_ids"] is not None:
                        assert live["input_ids"] == ids
                    changes = [[i, a, b] for i, a, b in zip(ids, live["answers"], evaluated[0]["answers"], strict=True)
                               if a != b]
                context.append({
                    "scheme": scheme, "repeat": repeat, "stage": stage,
                    "iterations": [row["iterations"] for row in (a, b, c)],
                    "time_s": [row["model_time"] for row in (a, b, c)],
                    "d": [row["dendrites"] for row in (a, b, c)], "s": [row["synapses"] for row in (a, b, c)],
                    "events": [row["status"] for row in (a, b, c)],
                    "live_Q": live["FP"] + live["FN"] if live else None,
                    "snapshot_Q": evaluated[0]["FP"] + evaluated[0]["FN"] if evaluated else None,
                    "live_answers": live["answers"] if live else None,
                    "snapshot_answers": evaluated[0]["answers"] if evaluated else None,
                    "snapshot_log": relative(evaluated[1] / "results.jsonl") if evaluated else None,
                    "changes": changes if live and evaluated else None,
                })
    warm = []
    previous_data = load(PREVIOUS / "report-data.json")
    for repeat in range(1, 4):
        name = f"warm-22-37-r{repeat}"
        stage = next((row for row in sequences.get(name, []) if row["stage_index"] == 1), None)
        if stage is None:
            continue
        original = next(row for row in previous_data["warm_comparisons"]
                        if row["repeat"] == repeat and row["transition"] == 1)
        assert original["from_id"] == 22 and original["to_id"] == 37
        historical = original["old"]
        warm.append({
            "repeat": repeat, "from_id": 22, "to_id": 37,
            "historical_d": historical["dendrites"], "historical_s": historical["synapses"],
            "historical_iterations": historical["iterations"],
            "observed_d": stage["dendrites"], "observed_s": stage["synapses"],
            "observed_iterations": stage["iterations"], "stop_reason": stage["stop_reason"],
            "log": relative(WORK / "runs/sequences" / name / "results.jsonl"),
        })
    warm_order = []
    for phase in ("warm-order", "matched-warm-order"):
        for mode in ("native", "disabled", "reversal"):
            for repeat in range(1, 4):
                run_id = f"warm-{mode}-r{repeat}"
                key = run_id if phase == "warm-order" else f"{phase}/{run_id}"
                entries = sequences.get(key, [])
                if not entries:
                    continue
                stages = [row for row in entries if row["record_type"] == "training"]
                warm_order.append({
                    "mode": mode, "repeat": repeat, "stages": stages, "matched": phase == "matched-warm-order",
                    "log": relative(WORK / "runs" / phase / run_id / "results.jsonl"),
                })
    historical_warm = {r["transition"]: r for r in previous_data["warm_comparisons"] if r["repeat"] == 1}
    warm_extensions = []
    for key, entries in sequences.items():
        if not key.startswith(("warm-order-prefix-", "matched-warm-order-prefix-")):
            continue
        for row in entries:
            stage = row["stage_index"]
            if row["record_type"] != "training" or not stage:
                continue
            prior = historical_warm[stage]
            old = prior["old"]
            warm_extensions.append({
                "series": key, "transition": stage, "from_id": prior["from_id"], "to_id": prior["to_id"],
                "d": row["dendrites"], "s": row["synapses"], "iterations": row["iterations"],
                "historical_d": old["dendrites"], "historical_s": old["synapses"],
                "historical_iterations": old["iterations"], "status": row["status"],
                "matches": (row["dendrites"], row["synapses"], row["iterations"]) ==
                           (old["dendrites"], old["synapses"], old["iterations"]),
                "log": relative(WORK / "runs" / key / "results.jsonl"),
            })
    save(WORK / "diagnosis-analysis.json", {
        "processes": processes, "inference_comparisons": compare, "training": observed,
        "observer_pairs": observer, "tick_comparisons": trace_comparisons, "sequence_context": context,
        "training_comparisons": training_comparisons, "profile_inference": profile_controls,
        "order_structure": order_structure,
        "warm_prefix_22_37": warm,
        "warm_order": warm_order,
        "warm_extensions": warm_extensions,
        "roundtrip_controls": roundtrip_controls,
        "reference_audit": reference_audit,
    })
    print(f"{len(processes)} processes, {len(compare)} paired controls, {len(observed)} training records")


if __name__ == "__main__":
    audit()
