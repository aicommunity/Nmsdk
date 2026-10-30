"""Declared native-test coverage, including imported-process and partial probes.

This adapter describes test artifacts, not a scientific experiment runner. It
never infers a complete expected set from whichever files happen to exist.
"""
import hashlib
import html
import json
import math
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from .native_evidence import count, load, require
from .probe_reports import _read_probe_data, render_probe_set


KIND = "timelearner_native_probe_evidence"
SUMMARY_MARKERS = {"_training_summary.json": "_service_", "_xml_summary.json": "_xmlprobe_",
                   "_learned_summary.json": "_state_trial_", "_stopped_summary.json": "_stopped_trial_",
                   "_warm_summary.json": "_warm_trial_"}


def _artifact(root, relative):
    require(type(relative) is str and relative and "\\" not in relative and ":" not in relative
            and not Path(relative).is_absolute() and ".." not in Path(relative).parts,
            "invalid_native_test_artifact_path")
    path = (root/relative).resolve(strict=True)
    require(path.is_relative_to(root), "native_test_artifact_escapes_root")
    return path


def _write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")


def inventory_native_test_run(specification, artifact_root):
    spec = load(specification)
    require(set(spec) == {"kind", "schema_version", "fixture_contract", "expected_test_ids", "phases", "standalone"}
            and spec["kind"] == "timelearner_native_test_report_spec"
            and type(spec["schema_version"]) is int and spec["schema_version"] == 1,
            "unknown_native_test_report_spec")
    require(type(spec["fixture_contract"]) is str and bool(spec["fixture_contract"]), "missing_native_test_contract")
    expected = spec["expected_test_ids"]
    require(type(expected) is list and bool(expected) and all(type(x) is str and x for x in expected)
            and len(expected) == len(set(expected)), "invalid_native_test_expected_tests")
    root = artifact_root.resolve(strict=True)
    native = _artifact(root, "native")
    require(native.is_dir(), "native_test_primary_directory_missing")
    require(all(p.is_file() and not p.is_symlink() for p in native.iterdir()),
            "native_test_primary_must_contain_only_regular_files")
    junit = ET.parse(_artifact(root, "native.xml")).getroot()
    cases = list(junit.iter("testcase"))
    actual = [c.get("classname", "")+"/"+c.get("name", "") for c in cases]
    require(len(actual) == len(set(actual)) and set(actual) == set(expected), "native_test_junit_expected_set_mismatch")
    require(all(c.get("status", "run") == "run" and c.get("result", "completed") == "completed"
                and not any(c.find(tag) is not None for tag in ("failure", "error", "skipped")) for c in cases),
            "native_test_junit_not_all_completed_successfully")
    require(type(spec["phases"]) is list and bool(spec["phases"])
            and type(spec["standalone"]) is list, "invalid_native_test_groups")
    groups, packet_sources, trace_sources, summaries, identities = [], set(), set(), set(), set()

    def entry(packet_name, trace_name, pointer=""):
        require(pointer in ("", "/probe"), "unsupported_native_probe_json_pointer")
        source, trace = _artifact(native, packet_name), _artifact(native, trace_name)
        require(source.parent == native and trace.parent == native, "native_test_sources_must_be_flat")
        value = load(source)
        packet = value if not pointer else value.get("probe")
        require(type(packet) is dict and packet.get("kind") == KIND, "native_test_source_is_not_probe")
        key = (packet_name, pointer)
        require(key not in packet_sources and trace_name not in trace_sources, "duplicate_native_test_source")
        # Validate all primary numeric/context data before creating an output.
        _, audit, _, _, _, _, channels, quality = _read_probe_data_from_value(packet, trace)
        trial = audit["trial_id"]
        packet_sources.add(key); trace_sources.add(trace_name)
        return {"source_packet": packet_name, "json_pointer": pointer, "source_trace": trace_name,
                "trial_id": trial, "channels": channels,
                "plottable_channels": quality["plottable_channels"], "data_complete": quality["complete"],
                "packet_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest()}

    for phase in spec["phases"]:
        require(type(phase) is dict and set(phase) == {"summary", "probe_prefix"}, "unknown_native_test_phase")
        summary_name, prefix = phase["summary"], phase["probe_prefix"]
        summary_path = _artifact(native, summary_name)
        require(summary_path.parent == native and summary_name not in summaries, "duplicate_native_test_phase")
        suffix = next((s for s in SUMMARY_MARKERS if summary_name.endswith(s)), None)
        require(suffix is not None and prefix == summary_name[:-len(suffix)]+SUMMARY_MARKERS[suffix],
                "native_test_phase_prefix_mismatch")
        summary = load(summary_path)
        require(summary.get("kind") == "native_training_state_summary", "native_test_phase_summary_kind")
        total = count(summary["reference_probes"])+count(summary.get("search_probes", 0))
        require(total > 0, "native_test_phase_has_no_recorded_probes")
        paths = sorted(p.name for p in native.glob(prefix+"*.json"))
        expected_paths = [prefix+str(i)+".json" for i in range(1, total+1)]
        require(set(paths) == set(expected_paths), "native_test_phase_missing_or_extra_probe")
        entries = [entry(p, p[:-5]+".csv") for p in expected_paths]
        require(len({e["trial_id"] for e in entries}) == total, "native_test_phase_duplicate_trial_id")
        groups.append({"identity": summary_name, "summary": summary_name, "trials": entries})
        summaries.add(summary_name); identities.add(summary_name)
    actual_summaries = {p.name for p in native.glob("*.json") if any(p.name.endswith(s) for s in SUMMARY_MARKERS)}
    require(actual_summaries == summaries, "native_test_missing_or_extra_declared_phase")
    for row in spec["standalone"]:
        require(type(row) is dict and set(row) == {"packet", "trace", "json_pointer"}, "unknown_native_test_standalone")
        identity = row["packet"]+row["json_pointer"]
        require(identity not in identities, "duplicate_native_test_group")
        groups.append({"identity": identity, "summary": None,
                       "trials": [entry(row["packet"], row["trace"], row["json_pointer"])]})
        identities.add(identity)
    discovered = set()
    for path in native.glob("*.json"):
        value = load(path)
        if value.get("kind") == KIND:
            discovered.add((path.name, ""))
        if type(value.get("probe")) is dict and value["probe"].get("kind") == KIND:
            discovered.add((path.name, "/probe"))
    require(discovered == packet_sources, "native_test_unaccounted_or_missing_primary_packet")
    require({p.name for p in native.glob("*.csv")} == trace_sources, "native_test_unaccounted_or_missing_primary_csv")
    return {"kind": "timelearner_native_test_inventory", "schema_version": 1,
            "fixture_contract": spec["fixture_contract"], "tests": len(cases), "groups": groups,
            "trials": sum(len(g["trials"]) for g in groups),
            "known_trial_soma_pairs": sum(e["channels"] for g in groups for e in g["trials"]),
            "plottable_trial_soma_pairs": sum(e["plottable_channels"] for g in groups for e in g["trials"]),
            "data_complete": all(e["data_complete"] for g in groups for e in g["trials"]),
            "visual_acceptance_complete": False, "scientific_verdict": None}


def _read_probe_data_from_value(packet, trace):
    """Use the production loader for extracted packets, without changing inputs."""
    import tempfile
    with tempfile.TemporaryDirectory(prefix="tl-native-packet-") as directory:
        path = Path(directory)/"packet.json"
        _write(path, packet)
        data = _read_probe_data(path, trace, allow_incomplete=True)
    _, _, _, _, _, samples, channels, quality = data
    finite = sum(any(math.isfinite(s["soma"][i]) for s in samples) for i in range(channels))
    return (*data[:-1], {"plottable_channels": finite,
                        "complete": quality["recorded_window_complete"] and data[1]["valid_observation"] is True})


def render_native_test_run(specification, artifact_root, output):
    inventory = inventory_native_test_run(specification, artifact_root)
    root = artifact_root.resolve(strict=True)
    output.mkdir(parents=True, exist_ok=False)
    primary = output/"primary"; primary.mkdir()
    # Preserve original wrappers as well as extracted /probe values. Import in
    # a fresh process may reuse a trial ID; it remains a separate execution group.
    shutil.copytree(root/"native", primary/"native")
    shutil.copyfile(root/"native.xml", primary/"native.xml")
    shutil.copyfile(specification, output/"native-test-spec.json")
    links = []; rendered_pairs = 0
    for i, group in enumerate(inventory["groups"]):
        prepared = output/f"group-{i:03d}-input"; prepared.mkdir()
        trials = []
        for j, entry in enumerate(group["trials"]):
            packet = load(primary/"native"/entry["source_packet"])
            if entry["json_pointer"]: packet = packet["probe"]
            name = f"probe-{j:04d}.json"
            _write(prepared/name, packet)
            shutil.copyfile(primary/"native"/entry["source_trace"], prepared/(name[:-5]+".csv"))
            trials.append({"trial_id": entry["trial_id"], "packet": name, "trace": name[:-5]+".csv"})
        _write(prepared/"spec.json", {"kind": "timelearner_probe_report_spec", "schema_version": 2,
                                     "observation_policy": "complete_or_partial", "trials": trials})
        folder = output/f"group-{i:03d}"
        result = render_probe_set(prepared/"spec.json", folder)
        require(result["trials"] == len(trials) and result["trial_soma_pairs"] == sum(e["plottable_channels"] for e in group["trials"]),
                "native_test_rendered_coverage_mismatch")
        rendered_pairs += result["trial_soma_pairs"]
        group["report"] = folder.name+"/index.html"
        links.append('<li><a href="'+group["report"]+'">'+html.escape(group["identity"])+"</a></li>")
    require(rendered_pairs == inventory["plottable_trial_soma_pairs"], "native_test_total_rendered_coverage_mismatch")
    inventory["rendered_trial_soma_pairs"] = rendered_pairs
    _write(output/"manifest.json", inventory)
    (output/"index.html").write_text('<!doctype html><meta charset="utf-8"><title>Native test run</title>'
        '<style>body{font:18px sans-serif;margin:2em}</style><h1>All declared native test observations</h1>'
        '<p>Includes partial and fresh-process probes. Every expected phase and primary CSV is accounted for. '
        'No scientific verdict or complete visual acceptance is inferred. Open individual full PNG/SVG/PDF views.</p><ul>'
        +''.join(links)+'</ul>\n', encoding="utf-8")
    _write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(output.rglob("*")) if p.is_file()})
    return {k: v for k, v in inventory.items() if k != "groups"}
