"""Execute discrepancy controls in fresh Release processes and preserve each attempt."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import argparse
import json
import shutil
import sys
import time
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import supervise
from training_repro import ROOT, WORK as PREVIOUS, OLD, BASE, RUNTIME, load, save, sha, git, pilot_jobs
from training_protocols import scheme_jobs, warm_job

WORK = ROOT / "Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124"
CONFIG = ROOT / "Bin/Configs/StructTrainClassic/DiscrepancyDiagnosis"
DELIVERY = PREVIOUS.parent / "outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/DiscrepancyDiagnosis"


def relative(path):
    return path.relative_to(ROOT).as_posix()


def records(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def result(folder):
    return records(folder / "results.jsonl")[0]


def old_variant(name):
    return load(PREVIOUS / "variants" / (name + ".json"))


def variant(name):
    metadata = WORK / "variants" / (name + ".json")
    return load(metadata) if metadata.exists() else old_variant(name)


def package(name):
    source = RUNTIME / "ClassicTrainingRepro.exe"
    dest = RUNTIME / f"ClassicDiagnosis-{name}.exe"
    if dest.exists():
        raise FileExistsError(dest)
    shutil.copy2(source, dest)
    shutil.copy2(RUNTIME / "ClassicStructTrainReplay.ini", dest.with_suffix(".ini"))
    paths = (
        "replay.cpp", "diagnosis_trace.inc", "legacy_replay.inc",
        "training_replay.inc", "training_file_protocol.inc",
    )
    snapshots = WORK / "source-snapshots" / name
    snapshots.mkdir(parents=True, exist_ok=False)
    for filename in paths:
        shutil.copy2(Path(__file__).parent / filename, snapshots / filename)
    metadata = {
        "id": name, "binary": relative(dest), "binary_sha256": sha(dest),
        "root_sha": git("rev-parse", "HEAD"), "bin_sha": git("rev-parse", "HEAD", repo=ROOT / "Bin"),
        "pulselib_sha": git("rev-parse", "HEAD", repo=ROOT / "Libraries/Nmsdk-PulseLib"),
        "rdk_sha": git("rev-parse", "HEAD", repo=ROOT / "Rdk"), "build": "Release",
        "sources": {relative(p): sha(p) for p in snapshots.iterdir()},
    }
    save(WORK / "variants" / (name + ".json"), metadata)
    return metadata


def launch(group, name, repeat, manifest, binary_meta, suite, timeout=660):
    folder = WORK / "runs" / group / f"{name}-r{repeat}"
    binary = ROOT / binary_meta["binary"]
    if binary.parent != RUNTIME or sha(binary) != binary_meta["binary_sha256"]:
        raise ValueError(f"Invalid Release binary: {binary}")
    old_process = folder / "process.json"
    job_path = CONFIG / "Jobs" / group / (folder.name + ".json")
    if old_process.exists():
        previous = load(old_process)
        while previous["status"] == "running":
            time.sleep(1)
            previous = load(old_process)
        if previous["status"] == "completed":
            if previous["binary_sha256"] != binary_meta["binary_sha256"] or load(job_path) != manifest:
                raise ValueError(f"Manifest changed under an existing run ID: {folder}")
            return folder
        raise RuntimeError(f"Preserve unsuccessful attempt and use another run ID: {folder}")
    # Preserve provenance separately from the manifest seen by the model.
    save(job_path, manifest)
    process = supervise(binary, job_path, folder, suite, repeat, 0, timeout)
    if process["status"] != "completed":
        print(f"{name} repeat {repeat}: {process['status']}", flush=True)
    return folder


def train(group, name, repeat, job, binary_name="main", wall=600, trace_ticks=0, core=None):
    binary = variant(binary_name)
    manifest = deepcopy(load(BASE))
    manifest.update(variant=binary, repro_job=job, training_trace_ticks=trace_ticks)
    if core:
        manifest["diagnostic_core"] = core
    manifest["defaults"]["wall_timeout_seconds"] = wall
    for template in manifest["templates"]:
        template["config"] = f"Bin/Configs/StructTrainClassic/TrainingReproducibility/Inputs/{template['kind']}/project.ini"
    return launch(group, name, repeat, manifest, binary, "repro", wall + 120)


def parallel(callback, jobs, workers):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(lambda args: callback(*args), jobs))


def previous_case(label, directory, expected=None):
    path = directory / "process.json"
    process = load(path)
    command = process["command"]
    manifest = load(Path(command[command.index("--manifest") + 1]))
    model = (ROOT / manifest["legacy_job"]["config"]).parent
    expected = result(directory)["answers"] if expected is None else expected
    return {
        "label": label, "directory": relative(directory), "manifest": manifest,
        "previous_binary_sha256": process["binary_sha256"], "expected": expected,
        "files": {relative(p): sha(p) for p in model.iterdir() if p.is_file()},
    }


def cases():
    science = load(OLD / "scientific-comparison-data.json")
    old_records = load(OLD / "assessment.json")["first_by_job"]
    new = load(PREVIOUS / "report-data.json")

    def old_case(label, job):
        row = old_records[job]
        return previous_case(label, ROOT / row["directory"], row["answers"])

    index = {x["label"]: x for x in new["recognition"]}
    items = []
    for row in science["recognition"]:
        item = old_case(row["label"], row["job"])
        item["historical"] = index[row["label"]]["historical_answers"]
        items.append(item)
    folder = (
        ROOT / "Docs/ClassicStructTrainExperiments/Эксперименты/Исследование"
        / "0 на 1+4 для 150 примеров"
    )
    for index, row in enumerate(science["epochs"], 1):
        item = old_case(f"transition-{index:02}", row["job"])
        path = folder / f"output_data{index}.txt"
        item["historical"] = [int(x) for x in path.read_text(encoding="utf-8-sig").splitlines()[1:]]
        items.append(item)
    for row in science["baselines"]:
        items.append(old_case("mean-51-61" if row["label"] == "Среднее" else "input-" + row["label"], row["job"]))
    nt111 = next(x for x in new["models"] if x["kind"] == "trainer" and x["target"] == 111)
    items.append(previous_case("new-NT111", ROOT / nt111["runs"][0]["inference_source"]))
    return items


FACTORS = {
    "order": {"preserve_native_order": True},
    "window": {"ticks_per_input_override": 1333},
    "first-tick": {"first_observed_tick": 1},
    "precision": {},
    "reset": {"independent_reset": True},
    "wrapper": {"observe_wrapper": True},
}
PILOT = {
    "NL22", "NT45", "NT60", "NT64(8)", "NT64(9)", "NT111", "new-NT111",
    "NL111", "mean-51-61", "transition-03", "transition-13",
}


def find_reference_binaries():
    return {sha(p): p for p in RUNTIME.glob("Classic*.exe") if p.is_file()}


def infer(group, item, condition, repeat, trace_ids=(), binary_name="main", binaries=None, core=None):
    for path, digest in item.get("files", {}).items():
        if sha(ROOT / path) != digest:
            raise ValueError(f"Locked inference configuration changed: {path}")
    manifest = deepcopy(item["manifest"])
    label = item["label"]
    job = manifest["legacy_job"]
    job["id"] = f"{label}-{condition}"
    if binaries is not None:
        digest = item["previous_binary_sha256"]
        reference = ROOT / load(PREVIOUS / "reference.json")["native_reference"]
        binary_file = binaries.get(digest, reference)
        binary = {"id": "reference", "binary": relative(binary_file), "binary_sha256": sha(binary_file),
                  "original_binary_sha256": digest, "exact_original_binary": digest in binaries}
    else:
        binary = variant(binary_name)
        job.update(diagnostic=True, diagnostic_trace_ids=list(trace_ids))
        if condition in FACTORS:
            job.update(FACTORS[condition])
        if condition == "precision":
            for sample in manifest["dataset"]:
                sample["pattern"] = [round(value, 4) for value in sample["pattern"]]
    if core:
        manifest["diagnostic_core"] = core
    manifest["variant"] = binary
    return launch(group, job["id"], repeat, manifest, binary, "legacy")


def baseline_and_pilot(items, workers):
    tasks = [(item, condition, repeat) for item in items if item["label"] in PILOT
             for repeat in range(1, 4)
             for condition in ("baseline", *FACTORS, "reversal")]

    def execute(item, condition, repeat):
        return infer("pilot", item, condition, repeat)

    parallel(execute, tasks, workers)
    for item in items:
        if item["label"] not in PILOT:
            continue
        baseline = result(WORK / "runs/pilot" / f"{item['label']}-baseline-r1")["answers"]
        for repeat in range(1, 4):
            for control in ("baseline", "reversal"):
                folder = WORK / "runs/pilot" / f"{item['label']}-{control}-r{repeat}"
                if result(folder)["answers"] != baseline:
                    raise ValueError(f"Instrumented baseline is not repeatable: {folder}")


def run_references(items, workers):
    binaries = find_reference_binaries()

    def check_prior(item):
        folder = infer("reference", item, "reference", 1, binaries=binaries)
        observed = result(folder)
        config = CONFIG / "Jobs/reference" / (folder.name + ".json")
        return {"label": item["label"], "matches": observed["answers"] == item["expected"],
                "binary": load(config)["variant"], "directory": relative(folder)}

    references = parallel(check_prior, [(item,) for item in items], workers)
    save(WORK / "reference-reproduction.json", references)


def training_pilot(workers):
    jobs = [(f"{j['id']}-{mode}", repeat, j, ticks)
            for j in pilot_jobs() for repeat in range(1, 4)
            for mode, ticks in (("plain", 0), ("trace", 4100))]
    parallel(lambda name, rep, job, ticks: train("training-pilot", name, rep, job, trace_ticks=ticks),
             jobs, workers)


def sequences(workers):
    jobs = []
    for job in scheme_jobs():
        if job["scheme"] not in {"0_1", "0_1_4_full"}:
            continue
        for mode in ("live", "snapshot", "pause"):
            for repeat in range(1, 4):
                jobs.append((f"{job['scheme']}-{mode}", repeat, dict(job, evaluation_context=mode)))
    warm = warm_job()
    warm["stages"] = warm["stages"][:1]
    for repeat in range(1, 4):
        jobs.append(("warm-22-37", repeat, warm))
    parallel(lambda *args: train("sequences", *args), jobs, workers)


def limits(which):
    if which == "nt80":
        job = {"id": "trainer-80", "kind": "trainer", "target_id": 80, "target_class": 2}
        for repeat in range(1, 4):
            train("limits", "NT80", repeat, job, "V1C")
    else:
        job = {"id": "trainer-22", "kind": "trainer", "target_id": 22, "target_class": 1}
        parallel(lambda repeat: train("limits", "NT22-strict", repeat, job, "FZ", 1800),
                 [(repeat,) for repeat in range(1, 4)], 3)


def parser_probes():
    data = load(BASE)["dataset"]
    sequence = [data[i-1] for i in (*range(41, 61), *range(101, 111))]
    for name, newline, truncated in (("newline", True, False), ("no-newline", False, False),
                                    ("partial-last", True, True)):
        job = {"id": name, "kind": "learner", "file_controller": True, "file_parser_only": True,
               "file_sequence": sequence, "trailing_newline": newline, "truncate_last": truncated}
        run = result(train("parser", name, 1, job))
        assert run["records_accepted"] == (29 if truncated else 30)
        assert not run["model_values_assigned"]


def factor_training(workers):
    samples = [j for j in pilot_jobs() if j["target_id"] in (22, 64, 111)]
    tasks = []
    for job in samples:
        for repeat in range(1, 4):
            for algorithm in ("modern", "archive"):
                for profile in ("default", "secretion2"):
                    tasks.append((f"{algorithm}-{profile}-{job['id']}", repeat, job, algorithm, profile, "default"))
            if job["target_id"] == 22:
                for profile in ("dissociation2", "resistance100"):
                    tasks.append((f"modern-{profile}-{job['id']}", repeat, job, "modern", profile, "default"))
                if job["kind"] == "trainer":
                    for criterion in ("tolerance", "keep", "strict", "crossing", "reversal"):
                        tasks.append((f"stop-{criterion}-{job['id']}", repeat, job, "modern", "default", criterion))

    def execute(name, repeat, job, algorithm, profile, criterion):
        timeout = 600
        trace = 4100 if repeat == 1 and job["target_id"] == 22 else 0
        stop = "default" if criterion == "reversal" else criterion
        return train("training-factors", name, repeat, job, algorithm, timeout, trace,
                     {"profile": profile, "nt_stop": stop})

    parallel(execute, tasks, workers)
    items = [item for item in cases() if item["label"] in {"NL22", "NT45"}]
    inference_tasks = [(item, repeat, profile) for item in items for repeat in range(1, 4)
                       for profile in ("default", "dissociation2", "resistance100", "reversal")]
    parallel(lambda item, rep, profile: infer("profile-inference", item, profile, rep, binary_name="modern",
             core={"profile": "default" if profile == "reversal" else profile}), inference_tasks, workers)


def training_order(workers):
    jobs = [job for job in pilot_jobs() if job["target_id"] in {22, 64, 111}]
    tasks = [(f"{mode}-{job['id']}", repeat, job, binary)
             for job in jobs for repeat in range(1, 4)
             for mode, binary in (("native", "VB"), ("disabled", "FO"), ("reversal", "VB"))]
    parallel(lambda *args: train("training-order", *args), tasks, workers)


def training_expansion(workers):
    chosen = []
    directory = WORK / "runs/training-factors"
    ten = [22, 37, 45, 60, 64, 84, 90, 111, 129, 134]
    choices = [
        ("archive-default", "archive", "default", "default", ("trainer", "learner")),
        ("modern-dissociation2", "modern", "dissociation2", "default", ("trainer", "learner")),
        ("modern-resistance100", "modern", "resistance100", "default", ("trainer", "learner")),
        ("stop-tolerance", "modern", "default", "tolerance", ("trainer",)),
        ("stop-keep", "modern", "default", "keep", ("trainer",)),
        ("stop-crossing", "modern", "default", "crossing", ("trainer",)),
    ]
    jobs = []
    for prefix, binary, profile, criterion, kinds in choices:
        for kind in kinds:
            name = f"{prefix}-{kind}-22"
            tested = [result(directory / f"{name}-r{rep}") for rep in range(1, 4)]
            base = result(directory / f"modern-default-{kind}-22-r1")
            own = [result(WORK / "runs/snapshot-inference" / f"{name}-r{rep}-baseline-r1")["answers"][0]
                   if (WORK / "runs/snapshot-inference" / f"{name}-r{rep}-baseline-r1" / "results.jsonl").exists() else None
                   for rep in range(1, 4)]
            def signature(row):
                return row["status"], row["iterations"], row["dendrites"], row["synapses"]
            changed = all(signature(test) == signature(tested[0]) for test in tested[1:])
            changed = changed and signature(tested[0]) != signature(base)
            passed = changed and own == [1, 1, 1]
            existing = {22, 64, 111} if prefix == "archive-default" else {22}
            chosen.append({"variant": prefix, "kind": kind, "stable_structural_or_completion_effect": changed,
                           "own_after_reload": own, "expanded": passed, "pilot_ids": sorted(existing)})
            if not passed:
                continue
            for target in (i for i in ten if i not in existing):
                for repeat in range(1, 4):
                    job = {"id": f"{kind}-{target}", "kind": kind, "target_id": target, "target_class": (target-1)//50+1}
                    jobs.append((f"{prefix}-{kind}-{target}", repeat, job, binary, profile, criterion))
    save(WORK / "training-expansion-decision.json", chosen)
    parallel(lambda name, rep, job, binary, profile, criterion:
             train("training-ten", name, rep, job, binary,
                   core={"profile": profile, "nt_stop": criterion}), jobs, workers)


def differences(left, right):
    return [identifier for identifier, a, b in zip(left["input_ids"], left["answers"], right["answers"], strict=True)
            if a != b]


def expansion(workers):
    items = cases()
    measured = set()
    for item in items:
        if item["label"] not in PILOT:
            continue
        for factor in FACTORS:
            changes = []
            for repeat in range(1, 4):
                left = result(WORK / "runs/pilot" / f"{item['label']}-baseline-r{repeat}")
                right = result(WORK / "runs/pilot" / f"{item['label']}-{factor}-r{repeat}")
                changes.append(differences(left, right))
            if changes[0] and all(row == changes[0] for row in changes[1:]):
                measured.add(factor)
    save(WORK / "expansion-decision.json", {"factors_with_repeatable_binary_effect": sorted(measured),
         "pilot": sorted(PILOT), "out_of_pilot_models": [item["label"] for item in items if item["label"] not in PILOT]})

    tasks = [(item, condition, repeat) for item in items if item["label"] not in PILOT
             for repeat in range(1, 4) for condition in ("baseline", *sorted(measured), "reversal")]
    parallel(lambda *args: infer("expansion", *args), tasks, workers)

    def trace(item, factor, changed):
        # First pass uses the entire original stream. Only detailed tracing is
        # restricted to changed windows and their immediately preceding window.
        sample_order = [sample["id"] for sample in item["manifest"]["dataset"]]
        ids = sorted(set(changed) | {sample_order[sample_order.index(i)-1] for i in changed if sample_order.index(i)})
        for condition in ("baseline", factor):
            infer("tick-" + factor, item, condition, 1, ids, binary_name="modern")

    tasks = []
    for item in items:
        group = "pilot" if item["label"] in PILOT else "expansion"
        left = result(WORK / "runs" / group / f"{item['label']}-baseline-r1")
        for factor in FACTORS if group == "pilot" else sorted(measured):
            right = result(WORK / "runs" / group / f"{item['label']}-{factor}-r1")
            changed = differences(left, right)
            if changed:
                tasks.append((item, factor, changed))
    parallel(trace, tasks, min(workers, 3))


def frozen_case(label, source, training, ids=None):
    from legacy_execute import write_config, internal_links
    from legacy_recover import physical

    original = ET.parse(source / "Model_00.xml").getroot()
    subject = original.find("Model/Components/Subject")
    target = CONFIG / "States" / label
    target.mkdir(parents=True, exist_ok=True)
    graph = write_config(target, original, subject, internal_links(original, "Model.Subject"),
                         (source / "project.ini").read_text(encoding="utf-8-sig"))
    before, after = physical(original), physical(graph)
    assert before["links"] == after["links"] and before["nodes"].keys() == after["nodes"].keys()
    changes = []
    for node, properties in before["nodes"].items():
        a, b = properties["parameters"], after["nodes"][node]["parameters"]
        assert properties["class"] == after["nodes"][node]["class"]
        for name in a.keys() | b.keys():
            if a.get(name) != b.get(name):
                assert (node, name) in {
                    ("Subject", "StructureBuildMode"), ("Subject", "IsNeedToTrain"), ("Subject", "LTZThreshold"),
                    ("Subject.Neuron", "StructureBuildMode"), ("Subject.Neuron.LTZone", "Threshold"),
                }, (node, name)
                changes.append([node, name, a.get(name), b.get(name)])
    save(target / "adapter-audit.json", {
        "source": relative(source / "Model_00.xml"), "source_sha256": sha(source / "Model_00.xml"),
        "adaptations": changes, "links": len(before["links"]), "nodes": len(before["nodes"]),
    })
    stage_job = training.get("stage", training["job"])
    manifest = deepcopy(load(BASE))
    job = {
        "id": label, "kind": training["kind"], "target_id": stage_job["target_id"],
        "target_class": stage_job["target_class"], "config": relative(target / "project.ini"),
        "dendrites": training["dendrites"], "synapses": training["synapses"],
    }
    if ids is not None:
        job["input_ids"] = ids
    manifest["legacy_job"] = job
    return {"label": label, "manifest": manifest}


def snapshots(workers):
    jobs = []
    for run in sorted((WORK / "runs/sequences").glob("*-snapshot-r*/results.jsonl")):
        if load(run.with_name("process.json"))["status"] != "completed":
            continue
        for row in records(run):
            if row["record_type"] != "training" or row["status"] != "completed":
                continue
            stage = row.get("stage_index", 0)
            if stage and not row["stage"].get("evaluate", False):
                continue
            identifier = run.parent.name + f"-s{stage}"
            source = run.parent / (f"stage-{stage}" if stage else "trained")
            jobs.append(frozen_case(identifier, source, row, row["job"]["evaluation_ids"]))
    # Test the trained input on exact saved states of the first detected factor
    # pairs and the plain/traced pilots. The mean uses its recorded vector.
    for group in ("training-pilot", "training-factors", "training-order", "training-ten"):
        for run in sorted((WORK / "runs" / group).glob("*/results.jsonl")):
            if load(run.with_name("process.json"))["status"] != "completed":
                continue
            row = records(run)[0]
            if row["status"] != "completed" or row["whole_initialization_audit"]["uninitialized"]:
                continue
            item = frozen_case(run.parent.name, run.parent / "trained", row, [row["job"]["target_id"] or 1])
            target = row["job"]["target_id"]
            if not target:
                item["manifest"]["dataset"][0] = {"id": 1, "class": 2, "pattern": row["job"]["pattern"]}
            jobs.append(item)
    parallel(lambda item: infer("snapshot-inference", item, "baseline", 1), [(job,) for job in jobs], workers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["package", "inference", "training", "sequences", "nt80", "strict",
                                          "parser", "factors", "expansion", "snapshots", "reference",
                                          "training-order", "training-expansion"])
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--variant", default="main")
    args = parser.parse_args()
    if args.action == "package":
        print(package(args.variant))
    elif args.action == "inference":
        items = cases()
        save(WORK / "locked-inference-cases.json", items)
        baseline_and_pilot(items, args.workers)
    elif args.action == "reference":
        run_references(cases(), args.workers)
    elif args.action == "training":
        training_pilot(args.workers)
    elif args.action == "sequences":
        sequences(args.workers)
    elif args.action == "parser":
        parser_probes()
    elif args.action == "factors":
        factor_training(args.workers)
    elif args.action == "training-order":
        training_order(args.workers)
    elif args.action == "training-expansion":
        training_expansion(args.workers)
    elif args.action == "expansion":
        expansion(args.workers)
    elif args.action == "snapshots":
        snapshots(args.workers)
    else:
        limits(args.action)


if __name__ == "__main__":
    main()
