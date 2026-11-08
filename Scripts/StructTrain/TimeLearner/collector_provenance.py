"""Bound collector inputs and source inventories, without execution attestation.

This reader does not inspect the kernel, release leases, build or run tests. A
matching STARTED record proves only that the supplied supervisor log names the
same contained launch. Callers still need fresh kernel/lease closure, compiled
inventory, producer auditors and an independent publication reader.
"""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import uuid

from .native_evidence import require
from .runtime import digest_json, runtime_content_identity, source_closure


DIALECT = "literal-TEST-and-attempt-invalid-budget-v1"
_COMMIT = re.compile(r"[0-9a-f]{40}")
_CASE = re.compile(r"([A-Za-z_]\w*)[/.]([A-Za-z_]\w*)")
_ROLES = {"request": "request.json", "binding": "owned-unit.json",
          "supervisor_launch": "supervisor.log", "worker_progress": "worker-stdout.log"}


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "collector_duplicate_json_key")
        value[key] = item
    return value


def _json(raw):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_object,
                          parse_constant=lambda _: require(False, "collector_nonfinite_json"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        require(False, "collector_json_invalid")


def _signed(raw):
    value = _json(raw)
    require(type(value) is dict and value.get("sha256") ==
            digest_json({k: v for k, v in value.items() if k != "sha256"}),
            "collector_record_digest_changed")
    return value


def _canonical(path, *, exists=True):
    path = Path(path)
    require(path.is_absolute(), "collector_absolute_path_required")
    require(not any(p.is_symlink() for p in (path, *path.parents)), "collector_symlink_path")
    require(path.resolve(strict=exists) == path, "collector_noncanonical_path")
    return path


def _identity(value):
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def _frozen(path, maximum_bytes):
    require(type(maximum_bytes) is int and maximum_bytes > 0, "collector_invalid_size_budget")
    path = _canonical(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_size <= maximum_bytes,
            "collector_file_type_or_size")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        require(_identity(before) == _identity(opened), "collector_file_changed_during_read")
        raw = stream.read(maximum_bytes + 1)
        after_open = os.fstat(stream.fileno())
    after_path = path.lstat()
    require(len(raw) == before.st_size and len(raw) <= maximum_bytes and
            _identity(before) == _identity(after_open) == _identity(after_path),
            "collector_file_changed_during_read")
    return raw, {"source_path": str(path), "bytes": len(raw), "sha256": _sha(raw)}


def _binding(request, binding):
    require(set(request) == {"kind", "schema_version", "attempt_id", "unit", "boot_id", "uid",
            "controller", "executable", "arguments", "working_directory", "runtime_fingerprint",
            "memory_bytes", "tasks", "maximum_wall_seconds", "environment", "sha256"} and
            request["kind"] == "timelearner_contained_request" and
            type(request["schema_version"]) is int and request["schema_version"] == 1,
            "collector_request_schema")
    require(set(binding) == {"kind", "schema_version", "request_sha256", "unit", "invocation_id",
            "control_group", "initial_main_pid", "initial_start_ticks", "sha256"} and
            binding["kind"] == "timelearner_contained_binding" and
            type(binding["schema_version"]) is int and binding["schema_version"] == 1,
            "collector_binding_schema")
    require(type(request["attempt_id"]) is str and re.fullmatch(
            r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", request["attempt_id"]) is not None,
            "collector_request_attempt_invalid")
    require(request["unit"] == "timelearner-" + str(uuid.UUID(request["attempt_id"])) + ".service" and
            binding["unit"] == request["unit"] and binding["request_sha256"] == request["sha256"],
            "collector_request_binding_mismatch")
    require(type(binding["control_group"]) is str and type(binding["invocation_id"]) is str,
            "collector_binding_identity_invalid")
    group = PurePosixPath(binding["control_group"])
    require(group.is_absolute() and ".." not in group.parts and group.name == binding["unit"] and
            re.fullmatch(r"[0-9a-f]{32}", binding["invocation_id"]) is not None and
            type(binding["initial_main_pid"]) is int and binding["initial_main_pid"] > 0 and
            type(binding["initial_start_ticks"]) is str and
            re.fullmatch(r"[1-9][0-9]*", binding["initial_start_ticks"]) is not None,
            "collector_binding_identity_invalid")


def _bound_descriptor(raw, records):
    require(type(raw) is dict and set(raw) == set(_ROLES) and
            all(type(value) is bytes for value in raw.values()) and
            type(records) is dict and set(records) == set(_ROLES), "collector_captured_roles_invalid")
    for role, record in records.items():
        require(type(record) is dict and set(record) == {"source_path", "bytes", "sha256"} and
                type(record["source_path"]) is str and "\0" not in record["source_path"] and
                Path(record["source_path"]).is_absolute() and
                ".." not in Path(record["source_path"]).parts and
                type(record["bytes"]) is int and record["bytes"] == len(raw[role]) and
                record["sha256"] == _sha(raw[role]), "collector_captured_descriptor_changed")
    require(len({row["source_path"] for row in records.values()}) == 4, "collector_log_roles_alias")
    container = Path(records["request"]["source_path"]).parent
    require(Path(records["request"]["source_path"]).name == "request.json" and
            records["binding"]["source_path"] == str(container/"owned-unit.json") and
            records["worker_progress"]["source_path"] == str(container/"stdout.log"),
            "collector_worker_stdout_not_owned_container")
    request, binding = _signed(raw["request"]), _signed(raw["binding"])
    _binding(request, binding)
    try:
        supervisor = raw["supervisor_launch"].decode("utf-8")
    except UnicodeDecodeError:
        require(False, "collector_supervisor_log_invalid_utf8")
    starts = []
    for number, line in enumerate(supervisor.splitlines(), 1):
        if line.lstrip().startswith("STARTED"):
            require(line.startswith("STARTED "), "collector_supervisor_start_malformed")
            starts.append((number, _json(line[len("STARTED "):].encode("utf-8"))))
    require(len(starts) == 1, "collector_supervisor_start_missing_or_ambiguous")
    number, started = starts[0]
    require(started == binding, "collector_supervisor_binding_mismatch")
    return {"kind": "timelearner_collector_bound_inputs", "schema_version": 1,
            "inputs": records, "binding": binding, "request_sha256": request["sha256"],
            "supervisor_started_line": number, "roles": {
                "supervisor_launch": "launch_binding_and_supervisor_messages",
                "worker_progress": "worker_progress_not_supervisor_messages"},
            "kernel_closure_attested": False, "test_success_attested": False,
            "scientific_verdict": None}


@dataclass(frozen=True)
class CapturedCollectorInputs:
    """Frozen bytes, not a capability or a kernel/scientific certificate."""
    _descriptor_json: bytes
    _files: tuple

    @property
    def descriptor(self):
        return _json(self._descriptor_json)

    def materialize(self, owned_root, staging):
        """Write captured bytes once inside a fresh, explicit owned staging path."""
        # This is a public value object, not an unforgeable capture capability.
        # Validate names and descriptor again before any filesystem operation.
        require(type(self._files) is tuple and len(self._files) == 4 and
                all(type(row) is tuple and len(row) == 2 and type(row[0]) is str and
                    row[0] in _ROLES.values() and type(row[1]) is bytes for row in self._files) and
                len({row[0] for row in self._files}) == 4, "collector_captured_files_invalid")
        require(type(self._descriptor_json) is bytes, "collector_captured_descriptor_invalid")
        descriptor = _json(self._descriptor_json)
        require(type(descriptor) is dict, "collector_captured_descriptor_invalid")
        by_name = dict(self._files)
        raw = {role: by_name[name] for role, name in _ROLES.items()}
        require(descriptor == _bound_descriptor(raw, descriptor.get("inputs")),
                "collector_captured_descriptor_changed")
        owned_root = _canonical(owned_root)
        require(owned_root.is_dir(), "collector_owned_root_not_directory")
        staging = _canonical(staging, exists=False)
        require(staging.parent == owned_root and not staging.exists(), "collector_staging_scope_or_exists")
        require(os.mkdir in os.supports_dir_fd and os.open in os.supports_dir_fd,
                "collector_directory_fd_required")
        root_identity = _identity(owned_root.stat())
        root_fd = os.open(owned_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        result = {}
        try:
            require(_identity(os.fstat(root_fd)) == root_identity, "collector_owned_root_changed")
            os.mkdir(staging.name, mode=0o700, dir_fd=root_fd)
            stage_fd = os.open(staging.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
            try:
                for name, raw in (*self._files, ("descriptor.json", self._descriptor_json)):
                    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=stage_fd)
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(raw)
                    path = staging/name
                    require(_canonical(path).read_bytes() == raw, "collector_staged_bytes_changed")
                    result["collector-provenance/" + name] = path
            finally:
                os.close(stage_fd)
            require(owned_root.stat().st_ino == root_identity[1] and
                    owned_root.stat().st_dev == root_identity[0], "collector_owned_root_changed")
        finally:
            os.close(root_fd)
        return result


def capture_owned_supervisor(container, *, supervisor_log, worker_stdout, maximum_input_bytes=16*1024**2):
    """Validate an exact launch log; role paths are mandatory and never guessed."""
    container = _canonical(container)
    paths = {"request": container/"request.json", "binding": container/"owned-unit.json",
             "supervisor_launch": supervisor_log, "worker_progress": worker_stdout}
    raw, records = {}, {}
    for role, path in paths.items():
        raw[role], records[role] = _frozen(path, maximum_input_bytes)
    descriptor = _bound_descriptor(raw, records)
    return CapturedCollectorInputs((json.dumps(descriptor, indent=2, allow_nan=False)+"\n").encode(),
                                   tuple((_ROLES[role], content) for role, content in raw.items()))


def _git(repository, *arguments):
    return subprocess.check_output(["git", "-C", str(repository), *arguments],
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"})


def _relative(path):
    require(type(path) is str and path and "\\" not in path and ":" not in path and
            not PurePosixPath(path).is_absolute() and
            all(part not in ("", ".", "..") for part in path.split("/")), "collector_git_path_invalid")
    return path


def _git_blob(repository, commit, path, maximum_bytes=16*1024**2):
    _relative(path)
    entry = _git(repository, "ls-tree", "-z", commit, "--", path).split(b"\0")
    require(len(entry) == 2 and entry[1] == b"", "collector_git_blob_missing")
    header, recorded_path = entry[0].split(b"\t", 1)
    mode, kind, oid = header.decode().split()
    require(mode in ("100644", "100755") and kind == "blob" and recorded_path.decode() == path,
            "collector_git_regular_blob_required")
    size = int(_git(repository, "cat-file", "-s", oid).decode().strip())
    require(size <= maximum_bytes, "collector_git_blob_size_budget")
    raw = _git(repository, "cat-file", "blob", oid)
    require(len(raw) == size, "collector_git_blob_size_changed")
    return raw, {"commit": commit, "path": path, "git_blob": oid, "bytes": len(raw), "sha256": _sha(raw)}


def _literal_cases(raw):
    """The declared dialect only; this is not a general C++/gtest interpreter."""
    text = raw.decode("utf-8")
    kept, definitions = [], []
    continuation = False
    for line in text.splitlines():
        if continuation or line.lstrip().startswith("#"):
            if continuation:
                definitions[-1].append(line)
            else:
                definitions.append([line])
            continuation = line.rstrip().endswith("\\")
            kept.append("")
        else:
            kept.append(line)
    text = "\n".join(kept)
    text = re.sub(r"/\*.*?\*/", lambda m: "\n"*m.group().count("\n"), text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    require(not re.search(r"^\s*(?:TEST_F|TEST_P|TYPED_TEST|TYPED_TEST_P)\s*\(", text, re.M),
            "collector_test_dialect_unsupported")
    cases = [(m.start(), m.group(1)+"/"+m.group(2)) for m in
             re.finditer(r"^\s*TEST\(\s*(\w+)\s*,\s*(\w+)\s*\)", text, re.M)]
    macros = list(re.finditer(r"^\s*ATTEMPT_INVALID_BUDGET_TEST\(\s*(\w+)\s*,", text, re.M))
    if macros:
        definitions = ["\n".join(block) for block in definitions]
        definitions = [block for block in definitions if re.match(
            r"\s*#\s*define\s+ATTEMPT_INVALID_BUDGET_TEST\(", block)]
        require(len(definitions) == 1 and re.findall(
                r"\b(TEST|TEST_F|TEST_P|TYPED_TEST|TYPED_TEST_P)\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)",
                definitions[0]) == [("TEST", "TrainingInvalidBudget", "name")],
                "collector_invalid_budget_macro_changed")
        cases += [(m.start(), "TrainingInvalidBudget/"+m.group(1)) for m in macros]
    values = [case for _, case in sorted(cases)]
    require(values and len(values) == len(set(values)), "collector_test_cases_empty_or_duplicate")
    return values


def _clean_closure(root):
    value = source_closure(root)
    require(value and "root" in value and all(not row["status"] and
            (name == "root" or row["head"] == row["recorded_gitlink"]) for name, row in value.items()),
            "collector_actual_source_not_clean")
    return value


def capture_git_case_inventory(source_root, *, selections, inventory_documents=()):
    """Derive declared cases/hash from actual Git bytes, not copied nested hashes.

    Each selection is {path, suites, dialect}; suites is null (all recognized
    cases) or a nonempty explicit list. Compiled gtest inventory is still required.
    Optional documents are {path, source_path, claimed?}; claimed is checked only,
    never used to construct the authoritative output.
    """
    source_root = _canonical(source_root)
    closure = _clean_closure(source_root)
    commit = closure["root"]["head"]
    require(_COMMIT.fullmatch(commit) is not None and type(selections) is list and selections,
            "collector_inventory_specification_invalid")
    require(_git(source_root, "rev-parse", "HEAD").decode().strip() == commit,
            "collector_source_HEAD_changed")
    files, all_ids = {}, []
    for selection in selections:
        require(set(selection) == {"path", "suites", "dialect"} and selection["dialect"] == DIALECT,
                "collector_test_dialect_unsupported")
        path, suites = selection["path"], selection["suites"]
        _relative(path)
        require(path not in files and (suites is None or (type(suites) is list and suites and
                all(type(s) is str and re.fullmatch(r"[A-Za-z_]\w*", s) for s in suites) and
                len(suites) == len(set(suites)))), "collector_inventory_selection_invalid")
        raw, record = _git_blob(source_root, commit, path)
        working, _ = _frozen(source_root/path, 16*1024**2)
        require(working == raw, "collector_worktree_git_bytes_changed")
        recognized = _literal_cases(raw)
        ids = [case for case in recognized if suites is None or case.split("/")[0] in suites]
        require(ids and (suites is None or set(suites) == {c.split("/")[0] for c in ids}),
                "collector_selected_suite_missing")
        files[path] = {**record, "dialect": DIALECT, "suites": suites, "ids": ids,
                       "recognized_ids": recognized}
        all_ids += ids
    require(len(all_ids) == len(set(all_ids)), "collector_inventory_duplicate_case")
    documents = []
    for item in inventory_documents:
        require(type(item) is dict and set(item) <= {"path", "source_path", "claimed"} and
                {"path", "source_path"} <= set(item) and item["source_path"] in files,
                "collector_inventory_document_specification_invalid")
        raw, record = _git_blob(source_root, commit, item["path"])
        document = _json(raw)
        source_hash = files[item["source_path"]]["sha256"]
        require(document.get("source_sha256") == source_hash, "collector_inventory_source_hash_mismatch")
        if "claimed" in item:
            require(type(item["claimed"]) is dict and item["claimed"].get("source_sha256") == source_hash,
                    "collector_inventory_source_hash_mismatch")
            require(item["claimed"] == document, "collector_inventory_document_claim_changed")
        cases = document.get("cases")
        require(type(cases) is list and type(document.get("count")) is int and
                document["count"] == len(cases) and all(type(c) is str and _CASE.fullmatch(c) for c in cases),
                "collector_inventory_document_cases_invalid")
        normalized = ["/".join(_CASE.fullmatch(c).groups()) for c in cases]
        require(len(normalized) == len(set(normalized)) and
                set(normalized) <= set(files[item["source_path"]]["recognized_ids"]),
                "collector_inventory_document_cases_changed")
        documents.append({**record, "source_path": item["source_path"], "document": document})
    require(_clean_closure(source_root) == closure and
            _git(source_root, "rev-parse", "HEAD").decode().strip() == commit,
            "collector_source_changed_during_capture")
    return {"kind": "timelearner_git_case_inventory", "schema_version": 1,
            "source_closure": closure, "root_commit": commit, "files": files,
            "documents": documents, "ids": all_ids, "count": len(all_ids),
            "compiled_inventory_verified": False, "test_success_attested": False,
            "scientific_verdict": None}


def describe_collection(inputs, *, collector_tool_root, compilation_state, actual_sdk_source=None,
                        compiled_runtime=None, planned_source=None, declared_inventory=None):
    """Keep Python collector, observed SDK, compiled runtime and plan distinct."""
    require(isinstance(inputs, CapturedCollectorInputs), "collector_frozen_inputs_required")
    require(compilation_state in ("not_started", "not_observed", "built") and
            (compiled_runtime is not None) == (compilation_state == "built"),
            "collector_compilation_phase_runtime_mismatch")
    tool = _canonical(collector_tool_root)
    commit = _git(tool, "rev-parse", "HEAD").decode().strip()
    require(_COMMIT.fullmatch(commit) is not None and not
            _git(tool, "status", "--porcelain", "--untracked-files=no", "--ignore-submodules=all").strip(),
            "collector_tool_projection_not_clean")
    module = Path(__file__).resolve(strict=True)
    require(module.is_relative_to(tool), "collector_module_outside_tool_projection")
    relative = module.relative_to(tool).as_posix()
    raw, record = _git_blob(tool, commit, relative, 1024**2)
    require(_frozen(module, 1024**2)[0] == raw, "collector_tool_git_bytes_changed")
    actual = None if actual_sdk_source is None else _clean_closure(_canonical(actual_sdk_source))
    if declared_inventory is not None:
        require(type(declared_inventory) is dict and
                declared_inventory.get("kind") == "timelearner_git_case_inventory" and
                declared_inventory.get("schema_version") == 1 and
                _COMMIT.fullmatch(declared_inventory.get("root_commit", "")) is not None,
                "collector_declared_inventory_invalid")
    compiled = None
    if compiled_runtime is not None:
        require(actual is not None and compiled_runtime["source_closure"] == actual and
                digest_json(runtime_content_identity(compiled_runtime)) == compiled_runtime["runtime_fingerprint"],
                "collector_compiled_runtime_source_or_digest_changed")
        if declared_inventory is not None:
            require(declared_inventory["root_commit"] == actual["root"]["head"],
                    "collector_declared_compiled_source_mismatch")
        compiled = {"source_closure": compiled_runtime["source_closure"],
                    "runtime_fingerprint": compiled_runtime["runtime_fingerprint"],
                    "executable": compiled_runtime["executable"], "app_ini": compiled_runtime["app_ini"]}
    require(_git(tool, "rev-parse", "HEAD").decode().strip() == commit and not
            _git(tool, "status", "--porcelain", "--untracked-files=no", "--ignore-submodules=all").strip(),
            "collector_tool_changed_during_capture")
    return {"kind": "timelearner_collector_provenance", "schema_version": 1,
            "bound_inputs": inputs.descriptor,
            "collector_tool_source": {"root_commit": commit, "module": record,
                                      "scope": "materialized collector module Git bytes only",
                                      "SDK_gitlinks_verified": False},
            "planned_source": planned_source, "actual_sdk_source_closure": actual,
            "compilation_state": compilation_state,
            "actual_compiled_runtime": compiled, "declared_source_inventory": declared_inventory,
            "observed_test_inventory": None, "compiled_inventory_verified": False,
            "build_success_attested": False,
            "kernel_closure_attested": False, "test_success_attested": False,
            "scientific_verdict": None}
