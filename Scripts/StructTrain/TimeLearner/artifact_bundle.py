"""Lossless primary artifacts in Git; reproducible full figures in worker cache."""
import gzip
import hashlib
import json
import re
import shutil
import tarfile
from pathlib import Path

from .native_evidence import load, require
from .native_test_reports import inventory_native_test_run


def _sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""): digest.update(chunk)
    return digest.hexdigest()


def _name(value):
    require(type(value) is str and value and "\\" not in value and ":" not in value
            and not value.startswith("/") and all(p not in ("", ".", "..") for p in value.split("/")),
            "unsafe_primary_bundle_path")
    return value


def _write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n", encoding="utf-8")


def pack_native_tests(contract, artifacts, output, selected_report, maximum_bytes=8*1024**3):
    root = artifacts.resolve(strict=True); report = selected_report.resolve(strict=True)
    require(not output.resolve().is_relative_to(root) and not output.resolve().is_relative_to(report),
            "bundle_output_must_be_outside_sources")
    inventory = inventory_native_test_run(contract, root)
    require((root/"native-exit-status.txt").read_text().strip() == "0", "native_execution_not_completed")
    for required in ("runtime-before.json", "runtime-after.json", "source-closure.txt"):
        require((root/required).is_file(), "primary_bundle_requires_runtime_and_source_closure")
    sources = {"native/"+p.name: p for p in (root/"native").iterdir()}
    # Native fixture output files and terminal provenance only. Generated
    # figures/ is intentionally excluded; the complete raw records remain.
    sources.update({p.name: p for p in root.iterdir() if p.is_file()
                    and p.suffix.lower() not in (".png", ".svg", ".pdf", ".html")})
    sources["contract.json"] = contract
    require(all(p.is_file() and not p.is_symlink() for p in sources.values()), "primary_bundle_requires_regular_files")
    entries = [{"path": _name(name), "bytes": p.stat().st_size, "sha256": _sha(p),
                "role": "primary_trace" if p.suffix == ".csv" else "native_record" if name.startswith("native/") else "provenance"}
               for name, p in sorted(sources.items())]
    require(type(maximum_bytes) is int and maximum_bytes > 0
            and sum(e["bytes"] for e in entries) <= maximum_bytes, "primary_bundle_exceeds_extraction_budget")
    # Bind selected figures to packets/CSV from THIS producer, including /probe
    # wrappers. Equal trial IDs alone do not establish this association.
    rendered = load(report/"report/manifest.json")
    require(len(rendered["groups"]) == len(inventory["groups"]), "selected_report_group_coverage_mismatch")
    primary = {}
    for actual, expected in zip(rendered["groups"], inventory["groups"]):
        require(actual["identity"] == expected["identity"] and actual["trials"] == expected["trials"],
                "selected_report_primary_inventory_mismatch")
        folder = "report/"+Path(_name(actual["report"])).parent.as_posix()
        for index, trial in enumerate(expected["trials"]):
            primary[folder+f"/probe-{index:04d}"] = trial
    qa = load(report/"pdf-qa/manifest.json")
    require(qa.get("kind") == "timelearner_full_native_visual_pdf_qa" and type(qa.get("schema_version")) is int and qa["schema_version"] == 1
            and type(qa.get("records")) is list and bool(qa["records"]), "unknown_selected_figure_source")
    selected = []; names = set(); runtime = None
    for item in qa["records"]:
        name = _name(item["preview"])
        require("/" not in name and name.endswith(".png") and name not in names, "invalid_selected_figure_name")
        png = report/"pdf-qa"/name; pdf = report/_name(item["source_relative"])
        require(not png.is_symlink() and not pdf.is_symlink() and _sha(png) == item["preview_sha256"]
                and _sha(pdf) == item["source_sha256"], "selected_figure_source_checksum_mismatch")
        probe = pdf.parent.parent
        packet = load(probe/"primary/probe.json")
        key = probe.relative_to(report).as_posix()
        require(key in primary, "selected_figure_not_bound_to_primary_bundle")
        original = load(root/"native"/primary[key]["source_packet"])
        if primary[key]["json_pointer"]: original = original["probe"]
        require(packet == original and _sha(probe/"primary/trace.csv") == primary[key]["trace_sha256"],
                "selected_figure_not_bound_to_primary_bundle")
        actual_runtime = load(probe/"manifest.json")["runtime"]
        if runtime is None: runtime = actual_runtime
        require(runtime == actual_runtime, "inconsistent_selected_figure_runtime")
        selected.append({"path": "selected/"+name, "sha256": _sha(png), "bytes": png.stat().st_size,
                         "source_pdf_sha256": item["source_sha256"], "source_view": item["source_relative"],
                         "source_packet": primary[key]["source_packet"], "json_pointer": primary[key]["json_pointer"],
                         "source_trace": primary[key]["source_trace"]})
        names.add(name)
    provenance = load(report/"input-verification.json")
    renderer = provenance["renderer_root"]
    require(type(renderer) is str and re.fullmatch("[0-9a-f]{40}", renderer), "invalid_bundle_renderer_root")
    output.mkdir(parents=True, exist_ok=False)
    archive = output/"primary.tar.gz"
    with archive.open("xb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for entry in entries:
                info = tarfile.TarInfo(entry["path"]); info.size = entry["bytes"]; info.mode = 0o644
                with sources[entry["path"]].open("rb") as stream: tar.addfile(info, stream)
    (output/"selected").mkdir()
    for entry in selected: shutil.copyfile(report/"pdf-qa"/Path(entry["path"]).name, output/entry["path"])
    manifest = {"kind": "timelearner_primary_artifact_bundle", "schema_version": 1,
                "archive": {"file": archive.name, "sha256": _sha(archive), "bytes": archive.stat().st_size},
                "files": entries, "selected_figures": selected,
                "inventory": {k: v for k, v in inventory.items() if k != "groups"},
                "render_recipe": {"renderer_root": renderer, "runtime": runtime,
                    "command": "python3 -m Scripts.StructTrain.TimeLearner report EXTRACTED/contract.json --format native-test-run --artifacts EXTRACTED --output NEW_CACHE"},
                "scientific_verdict": None, "global_visual_acceptance": False}
    _write(output/"manifest.json", manifest)
    # A source changed during snapshot must not become a certified archive.
    require(all(_sha(sources[e["path"]]) == e["sha256"] for e in entries), "primary_source_changed_during_bundle")
    _write(output/"SHA256SUMS.json", {p.relative_to(output).as_posix(): _sha(p) for p in sorted(output.rglob("*")) if p.is_file()})
    verify_bundle(output, maximum_bytes)
    return {"kind": manifest["kind"], "primary_files": len(entries), "archive_bytes": archive.stat().st_size,
            "uncompressed_bytes": sum(e["bytes"] for e in entries), "selected_figures": len(selected), "scientific_verdict": None}


def _read_archive(bundle, manifest, output=None, maximum_bytes=8*1024**3):
    entries = manifest["files"]
    require(type(entries) is list and bool(entries), "empty_primary_bundle")
    expected = {}
    for entry in entries:
        require(type(entry) is dict and set(entry) == {"path", "bytes", "sha256", "role"}, "unknown_primary_bundle_entry")
        name = _name(entry["path"])
        require(name not in expected and type(entry["bytes"]) is int and entry["bytes"] >= 0
                and type(entry["sha256"]) is str and re.fullmatch("[0-9a-f]{64}", entry["sha256"]) is not None
                and entry["role"] in ("primary_trace", "native_record", "provenance"), "invalid_primary_bundle_entry")
        expected[name] = entry
    require(sum(e["bytes"] for e in entries) <= maximum_bytes, "primary_bundle_exceeds_extraction_budget")
    seen = set()
    with gzip.open(bundle/"primary.tar.gz", "rb") as zipped:
        with tarfile.open(fileobj=zipped, mode="r:") as tar:
            for member in tar:
                name = _name(member.name)
                require(member.isfile() and name in expected and name not in seen
                        and member.size == expected[name]["bytes"], "unexpected_primary_archive_member")
                digest = hashlib.sha256(); size = 0
                target = None
                if output is not None:
                    path = output/name; path.parent.mkdir(parents=True, exist_ok=True); target = path.open("xb")
                try:
                    with tar.extractfile(member) as stream:
                        for chunk in iter(lambda: stream.read(1024*1024), b""):
                            digest.update(chunk); size += len(chunk)
                            if target is not None: target.write(chunk)
                finally:
                    if target is not None: target.close()
                require(size == expected[name]["bytes"] and digest.hexdigest() == expected[name]["sha256"], "primary_archive_payload_mismatch")
                seen.add(name)
        for tail in iter(lambda: zipped.read(1024*1024), b""):
            require(not any(tail), "nonzero_trailing_primary_archive_data")
    require(seen == set(expected), "missing_primary_archive_member")


def verify_bundle(bundle, maximum_bytes=8*1024**3):
    root = bundle.resolve(strict=True); manifest = load(root/"manifest.json")
    require(set(manifest) == {"kind", "schema_version", "archive", "files", "selected_figures", "inventory", "render_recipe",
                             "scientific_verdict", "global_visual_acceptance"}
            and manifest.get("kind") == "timelearner_primary_artifact_bundle" and type(manifest.get("schema_version")) is int
            and manifest["schema_version"] == 1 and manifest["scientific_verdict"] is None
            and manifest["global_visual_acceptance"] is False, "unknown_primary_artifact_bundle")
    archive = manifest["archive"]
    require(type(archive) is dict and set(archive) == {"file", "bytes", "sha256"}
            and archive["file"] == "primary.tar.gz" and type(archive["bytes"]) is int and archive["bytes"] > 0
            and type(archive["sha256"]) is str and re.fullmatch("[0-9a-f]{64}", archive["sha256"]) is not None
            and not (root/archive["file"]).is_symlink()
            and (root/archive["file"]).stat().st_size == archive["bytes"] and _sha(root/archive["file"]) == archive["sha256"],
            "primary_archive_checksum_mismatch")
    _read_archive(root, manifest, maximum_bytes=maximum_bytes)
    seen = set()
    require(type(manifest["selected_figures"]) is list and bool(manifest["selected_figures"]), "missing_selected_bundle_figures")
    for figure in manifest["selected_figures"]:
        name = _name(figure["path"])
        require(name.startswith("selected/") and name.endswith(".png") and name not in seen, "invalid_bundle_selected_figure")
        path = root/name
        require(path.resolve(strict=True).is_relative_to(root) and not path.is_symlink()
                and path.stat().st_size == figure["bytes"] and _sha(path) == figure["sha256"], "selected_figure_checksum_mismatch")
        seen.add(name)
    checksums = load(root/"SHA256SUMS.json")
    require(set(checksums) == seen | {"manifest.json", "primary.tar.gz"}, "unexpected_primary_bundle_checksum_set")
    actual_files = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p != root/"SHA256SUMS.json"}
    require(actual_files == set(checksums), "unaccounted_primary_bundle_file")
    for name, expected in checksums.items():
        path = root/_name(name)
        require(not path.is_symlink() and type(expected) is str and _sha(path) == expected, "primary_bundle_file_checksum_mismatch")
    return manifest


def extract_bundle(bundle, output, maximum_bytes=8*1024**3):
    root = bundle.resolve(strict=True)
    require(not output.resolve().is_relative_to(root), "extraction_must_be_outside_bundle")
    manifest = verify_bundle(root, maximum_bytes)
    output.mkdir(parents=True, exist_ok=False)
    _read_archive(root, manifest, output, maximum_bytes)
    return {"kind": "timelearner_primary_bundle_extraction", "files": len(manifest["files"]),
            "archive_sha256": manifest["archive"]["sha256"], "scientific_verdict": None}
