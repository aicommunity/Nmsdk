"""Run a prepared native-check cohort from one canonical declaration.

The outer owned launcher supplies containment, disk-growth monitoring and final
lease release after this worker and every recorded native leaf have closed.
This module builds/tests an idle SDK snapshot; it never updates its sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from xml.etree import ElementTree as ET


def _require(value, reason):
    if not value:
        raise ValueError(reason)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def _sha(path):
    checksum = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def _json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            _require(key not in result, "duplicate_job_key:"+key)
            result[key] = value
        return result
    path = Path(path)
    _require(not path.is_symlink() and path.resolve(strict=True) == path.absolute(), "job_file_alias")
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        _require(before.st_size <= 16*1024**2, "job_file_size")
        raw = stream.read()
        after = os.fstat(stream.fileno())
    identity = lambda row: (row.st_dev, row.st_ino, row.st_size, row.st_mtime_ns, row.st_ctime_ns)
    _require(identity(before) == identity(after) == identity(path.stat()), "job_file_changed")
    value = json.loads(raw, object_pairs_hook=unique,
                       parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite_job_json")))
    return value, raw


def _relative(value):
    _require(type(value) is str and value and "\\" not in value and ":" not in value and
             not PurePosixPath(value).is_absolute() and
             all(part not in ("", ".", "..") for part in value.split("/")), "relative_output_path")
    return value


def _declared_cache_profile(required):
    """Parse complete postconditions; a cache name has exactly one declaration."""
    _require(type(required) is list and required, "build_profile")
    result = {}
    for line in required:
        _require(type(line) is str and not any(c in line for c in "\r\n\0"),
                 "complete_cache_entry_required")
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*):([A-Z_]+)=(.*)", line)
        _require(match is not None, "complete_cache_entry_required")
        name, kind, value = match.groups()
        _require(kind in {"BOOL", "FILEPATH", "PATH", "STRING", "INTERNAL", "STATIC", "UNINITIALIZED"},
                 "unsupported_cache_type:"+name)
        _require(name not in result, "duplicate_declared_cache_key:"+name)
        result[name] = (kind, value, line)
    return result


def configure_arguments(job, paths, protected):
    """Apply the declared build profile without turning arbitrary checks into -D."""
    declared = _declared_cache_profile(job["build"]["required_cache_tokens"])
    fixed = {
        "CMAKE_BUILD_TYPE": ("STRING", job["build"]["type"]),
        "NMSDK_DEPLOY_ROOT": ("PATH", str(paths["runtime"])),
        "NMSDK_RESOURCE_ROOT": ("PATH", str(paths["resources"])),
        # Keep the historical untyped parallel setting/cache representation.
        "NMSDK_BUILD_PARALLEL_JOBS": ("UNINITIALIZED", str(job["build"]["parallel"])),
        "FETCHCONTENT_SOURCE_DIR_GOOGLETEST": ("PATH", str(paths["framework"])),
        "FETCHCONTENT_FULLY_DISCONNECTED": ("BOOL", "ON"),
        "FETCHCONTENT_UPDATES_DISCONNECTED": ("BOOL", "ON"),
    }
    for name, wanted in {**fixed, "CMAKE_HOME_DIRECTORY": ("INTERNAL", str(paths["source"]))}.items():
        if name in declared:
            _require(declared[name][:2] == wanted, "canonical_configure_conflict:"+name)
    arguments = ["cmake", "-S", str(paths["source"]), "-B", str(paths["build"])]
    arguments += ["-D"+name+(":"+kind if kind != "UNINITIALIZED" else "")+"="+value
                  for name, (kind, value) in fixed.items()]
    active = job["build"]["type"].upper()
    flags = {"CMAKE_C_FLAGS", "CMAKE_CXX_FLAGS", "CMAKE_EXE_LINKER_FLAGS",
             "CMAKE_SHARED_LINKER_FLAGS", "CMAKE_MODULE_LINKER_FLAGS", "CMAKE_STATIC_LINKER_FLAGS",
             "CMAKE_C_FLAGS_"+active, "CMAKE_CXX_FLAGS_"+active}
    booleans = {"RDK_USE_LLM", "RDK_LLM_BUILD_EMBEDDED"}
    for name, (kind, value, _) in declared.items():
        if name in flags:
            _require(kind == "STRING", "configure_flag_type:"+name)
            arguments.append("-D"+name+":STRING="+value)
        elif name in booleans:
            _require(kind == "BOOL" and value in ("ON", "OFF"), "configure_bool:"+name)
            arguments.append("-D"+name+":BOOL="+value)
        elif name == "RDK_LLM_LLAMA_CPP_DIR":
            _require(kind == "PATH", "configure_llama_type")
            path = Path(value)
            try:
                valid = (path.is_absolute() and path.is_relative_to(Path(job["workspace"])) and
                         path.resolve(strict=True) == path and path.is_dir() and
                         not any(p.is_symlink() for p in (path, *path.parents)))
            except OSError:
                valid = False
            _require(valid, "configure_llama_path")
            _require(path in protected, "configure_llama_not_protected")
            arguments.append("-DRDK_LLM_LLAMA_CPP_DIR:PATH="+str(path))
        elif re.fullmatch(r"CMAKE_(C|CXX)_FLAGS_(RELEASE|RELWITHDEBINFO)", name):
            _require(False, "inactive_configuration_flags:"+name)
        # Unknown, syntactically valid entries remain read-only postconditions.
    if declared.get("RDK_LLM_BUILD_EMBEDDED", (None, None))[1] == "ON":
        _require("RDK_LLM_LLAMA_CPP_DIR" in declared, "configure_embedded_llama_source_required")
    return arguments


def validate_cache_profile(cache, required):
    """Require complete, unique CMake cache entries, including empty values."""
    _require(type(cache) is str and type(required) is list and required, "build_profile")
    entries = {}
    for line in cache.splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line:
            continue
        declaration = line.split("=", 1)[0]
        if ":" in declaration:
            entries.setdefault(declaration.rsplit(":", 1)[0], []).append(line)
    for name, (_, _, expected) in _declared_cache_profile(required).items():
        _require(name and entries.get(name) == [expected], "changed_cached_build_profile:"+name)


def validate_job(job, preparation, arguments):
    """Validate data/wiring through the production serializer, without execution."""
    from .native_preparation import serialize_preparation
    # Use the same production canonical contract as the separate preparer.
    # A content hash alone cannot establish consistency between copied fields.
    serialize_preparation(preparation)
    _require(type(job) is dict and set(job) == {
        "kind", "schema_version", "workspace", "preparation", "paths", "build",
        "limits", "asan_options", "protected_runtimes", "artifacts"}, "job_schema")
    _require(job["kind"] == "timelearner_native_acceptance_job" and
             type(job["schema_version"]) is int and job["schema_version"] == 1, "job_version")
    _require(preparation.get("kind") == "timelearner_native_preparation" and
             type(preparation.get("schema_version")) is int and preparation["schema_version"] == 2 and
             preparation.get("sha256") == _digest({k:v for k,v in preparation.items() if k != "sha256"}),
             "canonical_preparation_identity")
    execution = preparation["execution"]
    _require(execution["mode"] == "repo_module" and
             execution["module"] == "Scripts.StructTrain.TimeLearner.native_acceptance_worker" and
             execution["arguments"] == arguments, "actual_worker_invocation_mismatch")
    _require(preparation["compiled_inventory_verified"] is False and
             preparation["kernel_closure_attested"] is False and
             preparation["test_success_attested"] is False and preparation["scientific_verdict"] is None,
             "preparation_attestation_outside_scope")
    paths = job["paths"]
    _require(type(paths) is dict and set(paths) == {
        "source", "build", "runtime", "output", "resources", "framework"}, "job_paths")
    _require(type(job["build"]) is dict and set(job["build"]) == {
        "type", "parallel", "wall_seconds", "required_cache_tokens"}, "build_profile")
    _require(job["build"]["type"] in ("Release", "RelWithDebInfo") and
             type(job["build"]["parallel"]) is int and job["build"]["parallel"] in (1, 2) and
             type(job["build"]["wall_seconds"]) is int and job["build"]["wall_seconds"] > 0 and
             type(job["build"]["required_cache_tokens"]) is list and
             bool(job["build"]["required_cache_tokens"]) and
             all(type(v) is str and v for v in job["build"]["required_cache_tokens"]), "build_profile")
    _declared_cache_profile(job["build"]["required_cache_tokens"])
    _require(type(job["limits"]) is dict and set(job["limits"]) == {
        "whole_wall_seconds", "leaf_memory_bytes", "leaf_tasks", "physical_free_floor_bytes",
        "reservation_memory_bytes", "reservation_disk_bytes"} and
        all(type(v) is int and v > 0 for v in job["limits"].values()), "job_limits")
    _require(job["asan_options"] in (None, "detect_leaks=0"), "asan_profile")
    _require(type(job["protected_runtimes"]) is list and
             len(job["protected_runtimes"]) == len(set(job["protected_runtimes"])), "protected_runtime_list")
    _require(type(job["artifacts"]) is list, "artifact_rules")
    for rule in job["artifacts"]:
        _require(type(rule) is dict and set(rule) == {"glob", "minimum", "maximum"} and
                 type(rule["minimum"]) is int and rule["minimum"] > 0 and
                 (rule["maximum"] is None or type(rule["maximum"]) is int and
                  rule["maximum"] >= rule["minimum"]), "artifact_rule")
        _relative(rule["glob"])
    current = preparation["current"]
    flattened = [case for leaf in current["runplan"] for case in leaf["expected_ids"]]
    _require(flattened and len(flattened) == len(set(flattened)) == current["counts"]["selected_cases"] and
             len(current["runplan"]) == current["counts"]["leaf_gates"], "canonical_cohort_counts")
    _require(set(current["inventory"]["files"]) <= set(preparation["source_inventory"]["files"]),
             "canonical_source_selection")
    for leaf in current["runplan"]:
        name = leaf["name"]
        _require(type(name) is str and name not in (".", "..") and name and
                 all(c.isalnum() or c in "_.-" for c in name) and
                 type(leaf["wall_seconds"]) is int and leaf["wall_seconds"] > 0,
                 "canonical_leaf")
    _require(len({v["name"] for v in current["runplan"]}) == len(current["runplan"]), "duplicate_leaf_name")
    return flattened


def observed_junit(path):
    """Read actual completed case IDs, including failures; never fill from a plan."""
    root = ET.parse(path).getroot()
    observed, failed, not_completed = [], [], []
    for case in root.findall(".//testcase"):
        identity = case.attrib["classname"]+"/"+case.attrib["name"]
        if case.get("status") != "run" or case.get("result") != "completed" or case.find("skipped") is not None:
            not_completed.append(identity)
            continue
        observed.append(identity)
        if case.find("failure") is not None or case.find("error") is not None:
            failed.append(identity)
    _require(len(observed) == len(set(observed)), "duplicate_JUnit_case")
    return observed, failed, not_completed


def validate_job_paths(job, *, loaded_source_root=None):
    """Side-effect-free path/configure preflight, shared with the owned controller.

    Worker supplies its actual __file__ root for the original namespace check.
    A metadata-only controller omits it and makes no loaded-SDK attestation.
    """
    base = Path(job["workspace"])
    def canonical(path, exists=False):
        _require(path.is_absolute() and path.is_relative_to(base) and
                 path.resolve(strict=exists) == path and
                 not any(p.is_symlink() for p in (path, *path.parents)), "workspace_path_alias:"+str(path))
        return path
    _require(base.is_absolute() and base.resolve(strict=True) == base and
             not any(p.is_symlink() for p in (base, *base.parents)), "workspace_alias")
    paths = {name:canonical(Path(value)) for name,value in job["paths"].items()}
    all_paths = list(paths.values())
    _require(len(set(all_paths)) == len(all_paths) and all(
        not a.is_relative_to(b) and not b.is_relative_to(a)
        for i,a in enumerate(all_paths) for b in all_paths[i+1:]), "overlapping_job_paths")
    if loaded_source_root is not None:
        _require(loaded_source_root == paths["source"], "worker_loaded_from_other_SDK")
    _require(not paths["output"].exists() and not paths["runtime"].exists(), "nonempty_new_output")
    protected = [canonical(Path(value), True) for value in job["protected_runtimes"]]
    _require(all(p.is_dir() for p in protected), "protected_runtime_not_directory")
    _require(all(not p.is_relative_to(paths[k]) and not paths[k].is_relative_to(p)
                 for p in protected for k in ("build", "runtime", "output")), "protected_write_path_overlap")
    _require(all(paths[k].is_dir() for k in ("source", "resources", "framework")), "missing_read_only_directory")
    return base, paths, protected, configure_arguments(job, paths, protected)


class Worker:
    def __init__(self, job, preparation, arguments):
        self.expected = validate_job(job, preparation, arguments)
        self.job, self.preparation = job, preparation
        self.base, self.paths, self.protected, self.configure = validate_job_paths(
            job, loaded_source_root=Path(__file__).resolve().parents[3])
        self.source = self.paths["source"]
        self.out, self.runtime = self.paths["output"], self.paths["runtime"]
        from . import runtime, native_gate, resource_reservations, contained_process, native_preparation, collector_provenance
        self.api = runtime, native_gate, resource_reservations, contained_process
        self.imports = {m.__name__:str(Path(m.__file__).resolve()) for m in
                        (*self.api, native_preparation, collector_provenance)}
        _require(all(Path(p).is_relative_to(self.source) for p in self.imports.values()), "mixed_SDK_imports")
        self.registry = resource_reservations.Reservations.open_existing(self.base/"resource-reservations.sqlite3")
        self.token = None
        self.stop = threading.Event()
        self.heartbeat_errors = []
        self.started = time.monotonic()
        self.observed, self.passed, self.failed, self.gates = [], [], [], 0
        self.out.mkdir()

    def canonical(self, path, exists=False):
        _require(path.is_absolute() and path.is_relative_to(self.base) and
                 path.resolve(strict=exists) == path and
                 not any(p.is_symlink() for p in (path, *path.parents)), "workspace_path_alias:"+str(path))
        return path

    def write(self, name, value):
        path = self.out/_relative(name)
        path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")

    def git(self, directory, *args):
        return subprocess.check_output(["git", "-C", str(directory), *args])

    def inventory(self, folder):
        rows = {}
        for path in sorted(folder.rglob("*")):
            if ".git" in path.relative_to(folder).parts:
                continue
            if path.is_symlink():
                rows[path.relative_to(folder).as_posix()] = {"kind":"symlink", "text":os.readlink(path)}
            elif path.is_file():
                rows[path.relative_to(folder).as_posix()] = {"bytes":path.stat().st_size, "sha256":_sha(path)}
        return rows

    def verify_materialized_resources(self):
        directory = self.paths["resources"]
        checked = {}
        for entry in self.git(directory, "ls-files", "--stage", "-z").split(b"\0"):
            if not entry:
                continue
            header, relative = entry.split(b"\t", 1)
            mode, oid, stage = header.decode().split()
            _require(stage == "0", "resource_merge_conflict")
            path = directory/os.fsdecode(relative)
            if mode == "160000" or not (path.exists() or path.is_symlink()):
                continue
            raw = os.readlink(path).encode() if mode == "120000" else path.read_bytes()
            _require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == oid,
                     "resource_Git_bytes_changed:"+str(path))
            checked[os.fsdecode(relative)] = {"git_blob":oid, "sha256":hashlib.sha256(raw).hexdigest()}
        _require(checked and any(p.startswith("ClDesc/") for p in checked), "missing_materialized_resources")
        return checked

    def source_files(self):
        rows, omitted = {}, {}
        for name in self.api[0].source_closure(self.source):
            relative = "" if name == "root" else name
            directory = self.source/relative
            missing = []
            for entry in self.git(directory, "ls-files", "--stage", "-z").split(b"\0"):
                if not entry:
                    continue
                header, path = entry.split(b"\t", 1)
                mode, oid, stage = header.decode().split()
                _require(stage == "0", "source_merge_conflict")
                if mode == "160000":
                    continue
                item = directory/os.fsdecode(path)
                if not item.exists() and not item.is_symlink():
                    _require(name == "Bin" or os.fsdecode(path).split("/")[0] in ("Docs", "Reports"),
                             "unexpected_source_omission:"+str(item))
                    missing.append(os.fsdecode(path))
                    continue
                raw = os.readlink(item).encode() if mode == "120000" else item.read_bytes()
                _require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest() == oid,
                         "source_Git_bytes_changed:"+str(item))
                rows[item.relative_to(self.source).as_posix()] = {
                    "bytes":len(raw), "sha256":hashlib.sha256(raw).hexdigest(), "git_blob":oid, "git_mode":mode}
            omitted[name] = missing
        return rows, omitted

    def guard(self):
        _require(not self.heartbeat_errors, "reservation_heartbeat_failed")
        _require(shutil.disk_usage(self.base).free >= self.job["limits"]["physical_free_floor_bytes"], "physical_disk_floor")
        _require(time.monotonic()-self.started < self.job["limits"]["whole_wall_seconds"], "whole_wall_budget")
        _require(not (self.out/"stop-request.json").exists(), "outer_stop_requested")
        if self.token:
            self.registry.validate_paths(self.token)

    def command(self, arguments, name, timeout):
        self.guard()
        arguments = list(map(str, arguments))
        with (self.out/name).open("xb") as log:
            process = subprocess.Popen(arguments, stdout=log, stderr=subprocess.STDOUT)
            self.write("owned-"+name+".json", {"pid":process.pid, "arguments":arguments,
                "maximum_wall_seconds":timeout, "start_ticks":Path("/proc",str(process.pid),"stat").read_text().rsplit(") ",1)[1].split()[19]})
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.write("stop-request.json", {"reason":"owned_build_command_timeout", "pid":process.pid})
                raise
        _require(code == 0, "command_failed:"+name+":"+str(code))
        self.guard()

    def gate(self, leaf):
        self.guard()
        name, ids = leaf["name"], leaf["expected_ids"]
        _require(name and all(c.isalnum() or c in "_.-" for c in name) and name not in (".", ".."), "leaf_name")
        manifest = self.out/(name+"-runtime.json")
        self.write(manifest.name, self.api[0].snapshot(self.source, self.runtime/"Test_PulseLib_StorageComponents",
            self.runtime/"NeuroModelerConsole.ini", self.paths["build"]/"CMakeCache.txt"))
        remaining = max(1, int(self.job["limits"]["whole_wall_seconds"]-(time.monotonic()-self.started)))
        spec = {"kind":"timelearner_native_test_gate", "schema_version":3,
            "runtime_manifest":str(manifest), "source_root":str(self.source), "expected_test_ids":ids,
            "maximum_wall_seconds":min(leaf["wall_seconds"], remaining), "asan_options":self.job["asan_options"] or "",
            "cooperative_runtime_capture":True, "process_limits":{
                "memory_bytes":self.job["limits"]["leaf_memory_bytes"], "tasks":self.job["limits"]["leaf_tasks"]}}
        self.write(name+"-spec.json", spec)
        result = self.api[1].run_native_gate(self.out/(name+"-spec.json"), self.out/name)
        self.write(name+"-result.json", result)
        self.gates += 1
        inventory = result.get("inventory")
        # A killed/timed-out gtest often never writes its final XML. Preserve
        # the typed process outcome; missing or corrupt XML is not a new
        # FileNotFoundError hiding the original failure, nor a passing case.
        actual, failed, incomplete = [], [], []
        observation_error = None
        try:
            actual, failed, incomplete = observed_junit(self.out/name/"native.xml")
        except (OSError, ET.ParseError, ValueError, KeyError) as error:
            observation_error = {"type":type(error).__name__, "reason":str(error)}
        self.observed += actual
        self.failed += failed
        self.passed += [case for case in actual if case not in failed]
        self.write(name+"-actual-tests.json", {"observed_ids":actual, "failed_ids":failed,
            "not_completed_ids":incomplete, "source":"native.xml",
            "observation_error":observation_error,
            "unobserved_expected_ids":[case for case in ids if case not in actual],
            "gate_execution":result.get("execution"), "gate_validity":result.get("validity"),
            "gate_reason":result.get("reason"), "scientific_verdict":None})
        _require(result["validity"] == "valid" and result["assertion_status"] == "passed" and inventory and
                 inventory["observed"] == len(ids) and not inventory["failed_test_ids"],
                 "native_gate_rejected:"+name+":"+str(result.get("execution"))+":"+
                 str(result.get("validity"))+":"+str(result.get("reason")))
        _require(observation_error is None, "native_JUnit_unreadable:"+name)
        request = json.loads((self.out/name/"process/contained/request.json").read_bytes())
        _require(request["environment"]["TIMELEARNER_COMPOSITE_OUTPUT"] == str(self.out/name/"native-composite"),
                 "native_output_route_changed")
        _require(set(actual) == set(ids) and not incomplete and not failed, "actual_JUnit_selection_mismatch")
        self.write("progress.json", {"passed_cases":len(self.passed), "closed_leaf_gates":self.gates,
            "current_gate":name, "expected_cases":len(self.expected)})

    def final_captures(self, runtime_before, frozen, before_source, closure):
        """Attempt every independent observation even if an earlier one fails."""
        errors, protected_after = [], {}
        def capture(label, operation):
            try:
                operation()
            except BaseException as error:
                errors.append({"capture":label, "reason":str(error)})
        def current_runtime():
            actual = self.inventory(self.runtime)
            self.write("current-runtime-after.json", actual)
            _require(actual == runtime_before, "current_runtime_changed")
        if runtime_before is not None:
            capture("current_runtime", current_runtime)
        for path, expected in frozen.items():
            def protected(path=path, expected=expected):
                actual = self.inventory(Path(path))
                protected_after[path] = actual
                _require(actual == expected, "protected_runtime_or_resources_changed:"+path)
            capture("protected:"+path, protected)
        capture("protected_inventory_write", lambda:self.write("protected-files-after.json", protected_after))
        if before_source is not None:
            def source_bytes():
                actual, _ = self.source_files()
                self.write("source-hashes-after.json", actual)
                _require(actual == before_source, "source_changed_during_run")
            capture("source_bytes", source_bytes)
        if closure is not None:
            def source_identity():
                actual = self.api[0].source_closure(self.source)
                self.write("source-closure-after.json", actual)
                _require(actual == closure, "source_closure_changed_during_run")
            def resource_identity():
                head = self.git(self.paths["resources"], "rev-parse", "HEAD").decode().strip()
                self.write("resource-closure-after.json", {"head":head})
                _require(head == closure["Bin"]["recorded_gitlink"], "resource_commit_changed_during_run")
            capture("source_closure", source_identity)
            capture("resource_closure", resource_identity)
        if "build" in self.paths:
            def build_metadata():
                build = self.paths["build"]
                cache = build/"CMakeCache.txt"
                if cache.is_file() and not cache.is_symlink():
                    (self.out/"CMakeCache-terminal.txt").write_bytes(cache.read_bytes())
                commands = {}
                for relative in ("Rdk/CMakeFiles/rdk.static.qt.dir",
                                 "Libraries/Nmsdk-PulseLib/CMakeFiles/Nmsdk-PulseLib.core.dir",
                                 "Tests/Integration/Libraries/CMakeFiles/Test_PulseLib_StorageComponents.dir"):
                    for name in ("flags.make", "link.txt"):
                        path = build/relative/name
                        if path.is_file() and not path.is_symlink():
                            raw = path.read_bytes()
                            commands[relative+"/"+name] = {"bytes":len(raw),
                                "sha256":hashlib.sha256(raw).hexdigest(),"text":raw.decode("utf-8")}
                self.write("generated-build-commands.json", commands)
            capture("build_metadata", build_metadata)
        capture("capture_errors_write", lambda:self.write("final-capture-errors.json", errors))
        return errors

    def run(self):
        passed, built, frozen = False, False, {}
        before_source = None
        closure = None
        runtime_before = None
        thread = None
        try:
            self.write("source-imports.json", self.imports)
            self.write("job.json", self.job)
            self.write("canonical-preparation.json", self.preparation)
            resources = [{"path":str(self.paths[k]), "access":"write"} for k in ("build", "runtime", "output")]
            resources += [{"path":str(p), "access":"read"} for p in [self.source,self.paths["resources"],self.paths["framework"],*self.protected]]
            demands = {} if self.registry.capacity is None else {"demands":{
                "slots":1, "memory_bytes":self.job["limits"]["reservation_memory_bytes"],
                "disk_bytes":self.job["limits"]["reservation_disk_bytes"]}}
            lease = self.registry.reserve(self.out.name, resources, ttl_seconds=120, **demands)
            self.token = lease["token"]
            self.write("reservation.json", lease)
            def heartbeat():
                while not self.stop.wait(10):
                    try:
                        self.registry.heartbeat(self.token, ttl_seconds=120)
                        self.registry.validate_paths(self.token)
                    except BaseException as error:
                        self.heartbeat_errors.append(str(error))
                        self.write("stop-request.json", {"reason":"heartbeat_failed"})
                        return
            thread = threading.Thread(target=heartbeat, daemon=True)
            thread.start()
            closure = self.api[0].source_closure(self.source)
            _require(closure == self.preparation["source_inventory"]["source_closure"], "fresh_source_closure_mismatch")
            _require(all(not r["status"] and (k=="root" or r["head"]==r["recorded_gitlink"]) for k,r in closure.items()), "source_not_clean")
            for row in self.preparation["prior_bindings"]:
                state = self.api[3].inspect(Path(row["binding_path"]).parent)
                _require(state["all_processes_closed"] and state["binding"] == row["binding"], "prior_kernel_group_not_closed")
            before_source, omitted = self.source_files()
            self.write("source-hashes-before-build.json", before_source)
            self.write("source-materialization.json", omitted)
            for name,row in self.preparation["source_inventory"]["files"].items():
                _require(_sha(self.source/name) == row["sha256"], "prepared_test_source_changed")
            worker = self.preparation["execution"]["source"]
            _require(closure["root"]["head"] == worker["commit"] and
                     worker["path"] == "Scripts/StructTrain/TimeLearner/native_acceptance_worker.py" and
                     _sha(Path(__file__)) == worker["sha256"] and
                     self.git(self.source, "rev-parse", "HEAD:"+worker["path"]).decode().strip() == worker["git_blob"],
                     "physical_worker_source_changed")
            self.write("source-closure.json", closure)
            resource_head = self.git(self.paths["resources"], "rev-parse", "HEAD").decode().strip()
            _require(resource_head == closure["Bin"]["recorded_gitlink"], "resource_commit_mismatch")
            _require(not self.git(self.paths["resources"], "status", "--porcelain", "--untracked-files=no").strip(),
                     "resource_worktree_changed")
            self.write("resource-Git-bytes.json", self.verify_materialized_resources())
            frozen = {str(p):self.inventory(p) for p in self.protected+[
                self.paths["resources"], self.paths["framework"]]}
            self.write("protected-files-before.json", frozen)
            temporary = self.out/"compiler-tmp"
            temporary.mkdir()
            os.environ["TMPDIR"] = str(temporary)
            self.write("configure-arguments.json", self.configure)
            self.command(self.configure, "configure.log", 180)
            cache = (self.paths["build"]/"CMakeCache.txt").read_text()
            validate_cache_profile(cache, self.job["build"]["required_cache_tokens"])
            ini = (self.runtime/"NeuroModelerConsole.ini").read_text()
            _require("LibrariesPath="+str(self.paths["resources"])+"/" in ini.splitlines() and
                     "ClDescPath="+str(self.paths["resources"])+"/ClDesc/" in ini.splitlines(),
                     "configured_resource_path_mismatch")
            # Compile the production job/transport entry points as well as the
            # component tests. Inline artifact tests do not compile the Console.
            self.command(["cmake","--build",self.paths["build"],"--target","Test_PulseLib_StorageComponents","NeuroModelerConsole",
                "--parallel",str(self.job["build"]["parallel"])], "build.log", self.job["build"]["wall_seconds"])
            built = True
            os.environ["QT_QPA_PLATFORM"] = "offscreen"
            for key in ("LD_LIBRARY_PATH", "QT_PLUGIN_PATH"):
                os.environ.pop(key, None)
            if self.job["asan_options"] is not None:
                os.environ["ASAN_OPTIONS"] = self.job["asan_options"]
            else:
                os.environ.pop("ASAN_OPTIONS", None)
            runtime_before = self.inventory(self.runtime)
            self.write("current-runtime-before.json", runtime_before)
            self.command([self.runtime/"Test_PulseLib_StorageComponents","--gtest_list_tests"], "compiled-test-inventory.log", 120)
            compiled, suite = [], None
            for line in (self.out/"compiled-test-inventory.log").read_text().splitlines():
                if line and not line.startswith(" ") and line.rstrip().endswith("."):
                    suite = line.strip()[:-1]
                elif suite and line.startswith("  ") and line.strip() and not line.strip().startswith("#"):
                    compiled.append(suite+"/"+line.strip().split(" #",1)[0])
            _require(len(compiled)==len(set(compiled)) and set(self.expected)<=set(compiled), "compiled_selected_cohort_missing")
            self.write("compiled-inventory-crosscheck.json", {"compiled":compiled, "expected":self.expected,
                "expected_total":len(self.expected), "accepted":True, "scope":"selected subset, not every binary case"})
            for leaf in self.preparation["current"]["runplan"]:
                self.gate(leaf)
            _require(len(self.observed) == len(set(self.observed)) == len(self.expected) and
                     set(self.observed) == set(self.expected) and set(self.passed) == set(self.expected) and
                     not self.failed, "incomplete_cohort")
            files = {}
            for rule in self.job["artifacts"]:
                matches = [p for p in self.out.glob(rule["glob"]) if p.is_file() and not p.is_symlink()]
                _require(len(matches)>=rule["minimum"] and (rule["maximum"] is None or len(matches)<=rule["maximum"]), "missing_required_primary:"+rule["glob"])
                files.update({p.relative_to(self.out).as_posix():{"bytes":p.stat().st_size,"sha256":_sha(p)} for p in matches})
            self.write("required-primary-files.json", files)
            passed = True
        except BaseException as error:
            self.write("exception.json", {"reason":str(error), "traceback":traceback.format_exc()})
        finally:
            self.stop.set()
            if thread:
                thread.join(timeout=20)
                if thread.is_alive():
                    self.heartbeat_errors.append("heartbeat_shutdown_not_completed")
            capture_errors = self.final_captures(runtime_before, frozen, before_source, closure)
            passed = passed and not capture_errors
            passed = passed and not self.heartbeat_errors
            assertions_passed = (len(self.observed) == len(set(self.observed)) == len(self.expected) and
                                 set(self.passed) == set(self.expected) and not self.failed)
            self.write("terminal.json", {"job_validation_passed":passed,
                "cohort_assertions_passed":assertions_passed, "built":built,
                "expected_cpp_cases":len(self.expected), "audited_completed_cpp_cases":len(self.observed),
                "actual_audited_assertion_passed_cpp_cases":len(self.passed), "actual_audited_failed_cpp_ids":self.failed,
                "completed_leaf_gates":self.gates, "heartbeat_errors":self.heartbeat_errors,
                "final_capture_errors":capture_errors,
                "scientific_verdict":None, "whole_plan_complete":False,
                "lease_release_policy":"external owner only after exact outer and all recorded leaf kernel groups are closed"})
        return 0 if passed else 1


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    args = parser.parse_args(arguments)
    sys.dont_write_bytecode = True
    job, _ = _json(args.job.absolute())
    preparation, _ = _json(Path(job["preparation"]).absolute())
    return Worker(job, preparation, arguments).run()


if __name__ == "__main__":
    raise SystemExit(main())
