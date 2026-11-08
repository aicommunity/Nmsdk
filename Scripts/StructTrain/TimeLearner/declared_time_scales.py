"""Conditional zero-G diagnostics from explicit configuration bytes.

Q=C*R*f is not an integrator stability test or an effective storage readback.
Class attributes may name registered images; this reader never resolves them.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import re
import subprocess

from .collector_provenance import _frozen
from .config_document import ConfigDocument, ConfigDocumentError, decode_text
from .native_evidence import EvidenceError, number, require

RESISTANCES = ("Resistance", "RestingResistance", "FBResistance")
THRESHOLDS = (0.5, 1.0, 2.0)
MAXIMUM_FILE_BYTES = 64 * 1024 * 1024
_DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def _identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def _threshold_policy():
    return {"id": "binary64-exact-declared-q-v1", "relative_tolerance": 0.0,
            "thresholds": list(THRESHOLDS)}


def _walk(node, path=()):
    current = (*path, node.name)
    yield node, current
    for child in node.children:
        yield from _walk(child, current)


def _text(document, node):
    require(not node.children and not node.self_closing, "time_scale_scalar_leaf_required")
    return decode_text(document.raw[node.content_start:node.content_end]).strip()


def _one(document, parent, name):
    matches = [node for node in parent.children if node.name == name]
    require(len(matches) == 1, "time_scale_field_missing_or_duplicate:" + name)
    return _text(document, matches[0])


def _finite(text, field):
    require(_DECIMAL.fullmatch(text) is not None, "time_scale_invalid_numeric_token:" + field)
    value = float(text)
    require(math.isfinite(value), "time_scale_not_finite:" + field)
    return value


def _positive(text, field):
    value = _finite(text, field)
    require(value > 0, "time_scale_not_positive:" + field)
    return value


def _clock(project_raw, parameter_filename, override):
    result = {"frequency_hz": None, "basis": None, "project_channel_path": None,
              "effective_frequency_attested": False, "issues": []}
    if override is not None:
        frequency = number(override)
        require(frequency > 0, "time_scale_override_not_positive")
        result.update(frequency_hz=frequency, basis="explicit_hypothetical_override")
    if project_raw is None:
        result["issues"].append("project_document_missing")
        return result
    try:
        document = ConfigDocument(project_raw)
        require(document.root.name == "Project", "time_scale_project_root_required")
        channels = document.select(("Project", "Channels"))
        matching = [node for node in channels.children
                    if _one(document, node, "ParametersFileName") == parameter_filename]
        require(len(matching) == 1, "time_scale_project_channel_missing_or_ambiguous")
        channel = matching[0]
        result["project_channel_path"] = ["Project", "Channels", channel.name]
        individual = _one(document, channel, "UseIndTimeStepFlag")
        require(individual in ("0", "1"), "time_scale_invalid_individual_clock_flag")
        require(individual == "0", "time_scale_individual_clock_requires_effective_resolution")
        global_frequency = _finite(_one(document, channel, "GlobalTimeStep"), "GlobalTimeStep")
        require(global_frequency >= 0, "time_scale_negative_GlobalTimeStep")
        if global_frequency == 0:
            frequency = _positive(_one(document, channel, "DefaultTimeStep"), "DefaultTimeStep")
            basis = "declared_project_DefaultTimeStep"
        else:
            frequency = global_frequency
            basis = "declared_project_GlobalTimeStep"
        result["declared_frequency_hz"] = frequency
        if override is None:
            result.update(frequency_hz=frequency, basis=basis)
    except (ConfigDocumentError, EvidenceError, ValueError) as error:
        result["issues"].append(str(error))
    return result


def audit_declared_pair(project_raw, parameters_raw, *, parameter_filename="Parameters_00.xml",
                        explicit_frequency_hz=None):
    """Parse and hash exactly these bytes; never infer storage/effective physics."""
    require(type(parameters_raw) is bytes and (project_raw is None or type(project_raw) is bytes),
            "time_scale_raw_bytes_required")
    require(type(parameter_filename) is str and bool(parameter_filename) and
            Path(parameter_filename).name == parameter_filename and "\\" not in parameter_filename,
            "time_scale_parameter_basename_required")
    clock = _clock(project_raw, parameter_filename, explicit_frequency_hz)
    result = {"kind": "timelearner_declared_time_scale_diagnostic", "schema_version": 1,
              "audit_method": {"id": "declared-zero-G-RC-binary64-v1", "source_execution_attested": False},
              "diagnostic_status": "not_assessed", "threshold_policy": _threshold_policy(),
              "inputs": {"project": None if project_raw is None else _identity(project_raw),
                         "parameters": _identity(parameters_raw)},
              "clock": clock, "parameter_blocks": [], "issues": [],
              "applicability": {"physics": "unknown", "Class_attribute": "registered_image_or_class_name",
                                "effective_model_attested": False, "storage_resolution_attested": False,
                                "runtime_conductance_observed": False,
                                "assumed_units": {"Capacity": "farad", "resistance_fields": "ohm", "frequency": "Hz"}},
              "integrator_stability_verdict": None, "scientific_verdict": None,
              "summary": {"parameter_blocks": 0, "declared_modes": 0, "conditionally_assessed_modes": 0,
                          "unassessed_modes": 0, "blocks_with_issues": 0,
                          "conditional_q_counts": {str(t): 0 for t in THRESHOLDS}}}
    try:
        document = ConfigDocument(parameters_raw)
    except ConfigDocumentError as error:
        result["issues"].append(str(error))
        return result
    parents = {id(child): parent for parent, _ in _walk(document.root) for child in parent.children}
    for parameters, path in _walk(document.root):
        if parameters.name != "Parameters":
            continue
        names = {node.name for node in parameters.children}
        if not names.intersection({"Capacity", *RESISTANCES}):
            continue
        parent = parents.get(id(parameters))
        block = {"document_path": list(path), "parameter_block_ordinal": len(result["parameter_blocks"]),
                 "component_name": parent.name if parent else None,
                 "registered_image_or_class_name": parent.attributes.get("Class") if parent else None,
                 "capacity": None, "modes": [], "issues": []}
        result["parameter_blocks"].append(block)
        try:
            block["capacity"] = _positive(_one(document, parameters, "Capacity"), "Capacity")
        except (EvidenceError, ConfigDocumentError) as error:
            block["issues"].append(str(error))
        if "TimeStep" in names:
            block["issues"].append("component_TimeStep_requires_effective_resolution")
        for field in RESISTANCES:
            if field not in names:
                continue
            mode = {"field": field, "resistance": None, "q": None, "inverse_q": None,
                    "conditional_q_band": None, "threshold_membership": None, "issues": []}
            block["modes"].append(mode)
            try:
                resistance = _positive(_one(document, parameters, field), field)
                mode["resistance"] = resistance
                require(block["capacity"] is not None, "time_scale_capacity_unresolved")
                require(clock["frequency_hz"] is not None, "time_scale_frequency_unresolved")
                require("TimeStep" not in names, "time_scale_component_clock_unresolved")
                try:
                    q = block["capacity"] * resistance * clock["frequency_hz"]
                except OverflowError:
                    require(False, "time_scale_product_not_finite_positive")
                require(math.isfinite(q) and q > 0, "time_scale_product_not_finite_positive")
                try:
                    inverse = 1.0 / q
                except (OverflowError, ZeroDivisionError):
                    require(False, "time_scale_inverse_not_finite_positive")
                require(math.isfinite(inverse) and inverse > 0, "time_scale_inverse_not_finite_positive")
                mode.update(q=q, inverse_q=inverse,
                            conditional_q_band=("q_le_0_5" if q <= .5 else "q_le_1" if q <= 1 else "q_gt_1"),
                            threshold_membership={str(t): q <= t for t in THRESHOLDS})
            except (EvidenceError, ConfigDocumentError, OverflowError, ZeroDivisionError) as error:
                mode["issues"].append(str(error))
        if not block["modes"]:
            block["issues"].append("resistance_fields_not_declared")
    modes = [mode for block in result["parameter_blocks"] for mode in block["modes"]]
    assessed = [mode for mode in modes if mode["q"] is not None]
    unresolved_blocks = [b for b in result["parameter_blocks"] if b["issues"]]
    result["summary"] = {"parameter_blocks": len(result["parameter_blocks"]), "declared_modes": len(modes),
                         "conditionally_assessed_modes": len(assessed), "unassessed_modes": len(modes)-len(assessed),
                         "blocks_with_issues": len(unresolved_blocks),
                         "conditional_q_counts": {str(t): sum(m["q"] <= t for m in assessed)
                                                  for t in THRESHOLDS}}
    if not result["parameter_blocks"]:
        result["issues"].append("no_declared_RC_parameter_blocks")
    if assessed:
        result["diagnostic_status"] = ("partially_assessed_conditionally" if unresolved_blocks or
            len(assessed) != len(modes) or clock["issues"] else "assessed_conditionally")
    return result


def audit_case(parameter_path, *, project_path=None, explicit_frequency_hz=None):
    """Stable reads share the collector's canonical, regular-file size policy."""
    parameter_path = Path(parameter_path).absolute()
    project_path = Path(project_path).absolute() if project_path is not None else parameter_path.parent/"Project.ini"
    raw, parameter_record = _frozen(parameter_path, MAXIMUM_FILE_BYTES)
    project_raw, project_record = None, None
    if project_path.exists() or project_path.is_symlink():
        project_raw, project_record = _frozen(project_path, MAXIMUM_FILE_BYTES)
    result = audit_declared_pair(project_raw, raw, parameter_filename=parameter_path.name,
                                 explicit_frequency_hz=explicit_frequency_hz)
    result["inputs"]["parameters"] = parameter_record
    result["inputs"]["project"] = project_record
    return result


def audit_config_tree(config_root, *, discovery, explicit_frequency_hz=None):
    """Audit explicit matrix layout or tracked files, retaining every case issue."""
    root = Path(config_root).absolute()
    require(root.is_dir() and root.resolve(strict=True) == root and
            not any(p.is_symlink() for p in (root, *root.parents)), "time_scale_config_root_not_canonical")
    require(discovery in ("matrix", "tracked-tree"), "time_scale_discovery_required")
    if explicit_frequency_hz is not None:
        require(number(explicit_frequency_hz) > 0, "time_scale_override_not_positive")
    provenance = {"discovery": discovery, "config_root": str(root), "Git_revision_is_not_worktree_hash": True}
    if discovery == "matrix":
        paths = sorted(root.glob("W*/inputs/*/Train/Parameters_00.xml"))
    else:
        repository = Path(subprocess.check_output(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                                                 text=True).strip()).resolve(strict=True)
        prefix = root.relative_to(repository).as_posix()
        arguments = ["git", "-C", str(repository), "ls-files", "-z"]
        if prefix != ".":
            arguments += ["--", ":(literal)" + prefix]
        raw = subprocess.check_output(arguments)
        paths = sorted(repository/path.decode("utf-8") for path in raw.split(b"\0")
                       if path and (path.endswith(b"/Train/Parameters_00.xml") or
                                    path == b"Train/Parameters_00.xml"))
        provenance.update(repository=str(repository), config_repository_head=subprocess.check_output(
            ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True).strip())
    cases = []
    for path in paths:
        require(path.is_relative_to(root), "time_scale_parameter_path_outside_config_root")
        try:
            record = audit_case(path, explicit_frequency_hz=explicit_frequency_hz)
        except (EvidenceError, ConfigDocumentError, OSError, ValueError) as error:
            record = {"diagnostic_status": "not_assessed", "issues": [str(error)], "inputs": None,
                      "integrator_stability_verdict": None, "scientific_verdict": None}
        cases.append({"parameter_path": path.relative_to(root).as_posix(), "diagnostic": record})
    return {"kind": "timelearner_declared_time_scale_tree", "schema_version": 1,
            "audit_method": {"id": "declared-zero-G-RC-binary64-v1", "source_execution_attested": False},
            "provenance": provenance, "threshold_policy": _threshold_policy(), "cases": cases,
            "diagnostic_coverage": ("empty" if not cases else "complete" if all(
                c["diagnostic"]["diagnostic_status"] == "assessed_conditionally" for c in cases) else "incomplete"),
            "summary": {"discovered_cases": len(paths), "not_assessed_cases": sum(
                c["diagnostic"]["diagnostic_status"] == "not_assessed" for c in cases),
                "partially_assessed_cases": sum(c["diagnostic"]["diagnostic_status"] ==
                    "partially_assessed_conditionally" for c in cases)},
            "issues": [] if paths else ["no_parameter_files_discovered"],
            "integrator_stability_verdict": None, "effective_model_attested": False,
            "scientific_verdict": None}
