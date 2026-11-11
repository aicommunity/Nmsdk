"""Bound collector inputs and source inventories, without execution attestation.

This reader does not inspect the kernel, release leases, build or run tests. A
matching STARTED record proves only that the supplied supervisor log names the
same contained launch. Callers still need fresh kernel/lease closure, compiled
inventory, producer auditors and an independent publication reader.
"""
from dataclasses import dataclass
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import uuid

from .native_evidence import EvidenceError, require
from .runtime import digest_json, runtime_content_identity, source_closure


DIALECT = "literal-TEST-and-attempt-invalid-budget-v1"
_COMMIT = re.compile(r"[0-9a-f]{40}")
_CASE = re.compile(r"([A-Za-z_]\w*)[/.]([A-Za-z_]\w*)")
_ROLES = {"request": "request.json", "binding": "owned-unit.json",
          "supervisor_launch": "supervisor.log", "worker_progress": "worker-stdout.log"}
_INPUT_ROLE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]*")
_SHA256 = re.compile(r"[0-9a-f]{64}")


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
        raw = stream.read(before.st_size + 1)
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


def _stage_frozen_files(owned_root, staging, files, prefix):
    require(type(files) is tuple and files and all(type(row) is tuple and len(row) == 2
            and type(row[0]) is str and _INPUT_ROLE.fullmatch(row[0]) is not None
            and row[0] not in (".", "..") and type(row[1]) is bytes for row in files)
            and len({row[0].casefold() for row in files}) == len(files), "collector_staged_files_invalid")
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
            for name, raw in files:
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=stage_fd)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(raw)
                path = staging/name
                require(_canonical(path).read_bytes() == raw, "collector_staged_bytes_changed")
                result[prefix + name] = path
        finally:
            os.close(stage_fd)
        require(owned_root.stat().st_ino == root_identity[1] and
                owned_root.stat().st_dev == root_identity[0], "collector_owned_root_changed")
    finally:
        os.close(root_fd)
    return result


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
        return _stage_frozen_files(owned_root, staging,
            (*self._files, ("descriptor.json", self._descriptor_json)), "collector-provenance/")


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
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"}, stderr=subprocess.PIPE)


def _relative(path):
    require(type(path) is str and path and "\\" not in path and ":" not in path and
            not PurePosixPath(path).is_absolute() and
            all(part not in ("", ".", "..") for part in path.split("/")), "collector_git_path_invalid")
    return path


def _git_blob(repository, commit, path, maximum_bytes=16*1024**2, *, expected_bytes=None):
    if expected_bytes is not None:
        require(type(expected_bytes) is int and 0 <= expected_bytes <= 2**53-1,
                "collector_input_count_invalid")
    _relative(path)
    entry = _git(repository, "ls-tree", "-z", commit, "--", path).split(b"\0")
    require(len(entry) == 2 and entry[1] == b"", "collector_git_blob_missing")
    header, recorded_path = entry[0].split(b"\t", 1)
    mode, kind, oid = header.decode().split()
    require(mode in ("100644", "100755") and kind == "blob" and recorded_path.decode() == path,
            "collector_git_regular_blob_required")
    require(_git(repository, "cat-file", "-t", oid).strip() == b"blob", "collector_git_regular_blob_required")
    size = int(_git(repository, "cat-file", "-s", oid).decode().strip())
    require(size <= maximum_bytes, "collector_git_blob_size_budget")
    require(expected_bytes is None or size == expected_bytes, "collector_git_blob_declared_size_changed")
    raw = _git(repository, "cat-file", "blob", oid)
    require(len(raw) == size, "collector_git_blob_size_changed")
    return raw, {"commit": commit, "path": path, "git_blob": oid, "bytes": len(raw), "sha256": _sha(raw)}


def _input_count(value, *, positive=False):
    require(type(value) is int and 0 <= value <= 2**53-1 and (not positive or value > 0),
            "collector_input_count_invalid")
    return value


def _input_path(value):
    _relative(value)
    require(not any(ord(char) < 32 or ord(char) == 127 for char in value), "collector_input_path_invalid")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise EvidenceError("collector_input_path_invalid") from error
    return value


def _input_root(value):
    require(isinstance(value, (str, Path)), "collector_absolute_path_required")
    text = str(value)
    require(text and not any(ord(char) < 32 or ord(char) == 127 for char in text), "collector_input_root_invalid")
    try:
        text.encode("utf-8")
    except UnicodeError as error:
        raise EvidenceError("collector_input_root_invalid") from error
    require(Path(value).is_absolute() and ".." not in Path(value).parts, "collector_absolute_path_required")
    return value


@dataclass(frozen=True)
class RequiredFileRole:
    role: str
    root: Path
    relative_path: str
    expected_bytes: int
    expected_sha256: str
    maximum_bytes: int
    staged_name: str


@dataclass(frozen=True)
class GitInputRole:
    role: str
    repository: Path
    repository_head: str
    commit: str
    path: str
    git_blob: str
    expected_bytes: int
    expected_sha256: str
    maximum_bytes: int


def _file_role(value):
    require(type(value) is RequiredFileRole and type(value.role) is str and
            _INPUT_ROLE.fullmatch(value.role) is not None, "collector_file_role_invalid")
    _input_root(value.root)
    _input_path(value.relative_path)
    require(type(value.expected_sha256) is str and _SHA256.fullmatch(value.expected_sha256) is not None,
            "collector_input_sha256_invalid")
    require(_input_count(value.expected_bytes) <= _input_count(value.maximum_bytes, positive=True),
            "collector_input_size_budget")
    require(type(value.staged_name) is str and _INPUT_ROLE.fullmatch(value.staged_name) is not None and
            value.staged_name.casefold() not in (".", "..", "descriptor.json"), "collector_input_staged_name_invalid")


def _git_role(value):
    require(type(value) is GitInputRole and type(value.role) is str and
            _INPUT_ROLE.fullmatch(value.role) is not None, "collector_git_role_invalid")
    _input_root(value.repository)
    for token in (value.repository_head, value.commit, value.git_blob):
        require(type(token) is str and _COMMIT.fullmatch(token) is not None, "collector_commit_invalid")
    _input_path(value.path)
    require(type(value.expected_sha256) is str and _SHA256.fullmatch(value.expected_sha256) is not None,
            "collector_input_sha256_invalid")
    require(_input_count(value.expected_bytes) <= _input_count(value.maximum_bytes, positive=True),
            "collector_input_size_budget")


def _requirements(values, validator, maximum_total_bytes):
    require(type(values) in (list, tuple) and bool(values), "collector_input_roles_required")
    _input_count(maximum_total_bytes, positive=True)
    # Validate the WHOLE manifest before reading any member.
    for value in values:
        validator(value)
    require(len({value.role for value in values}) == len(values), "collector_duplicate_input_role")
    require(sum(value.expected_bytes for value in values) <= maximum_total_bytes,
            "collector_input_total_size_budget")


def _file_descriptor(requirements, files):
    require(type(requirements) is tuple, "collector_captured_file_roles_invalid")
    _requirements(requirements, _file_role, 2**53-1)
    require(type(files) is tuple and len(files) == len(requirements) and
            all(type(row) is tuple and len(row) == 2 and type(row[1]) is bytes for row in files),
            "collector_captured_file_roles_invalid")
    names = [value.staged_name.casefold() for value in requirements]
    require(len(set(names)) == len(names), "collector_duplicate_staged_input")
    paths = [str(Path(value.root)/value.relative_path) for value in requirements]
    require(len(set(paths)) == len(paths), "collector_input_role_path_alias")
    rows = {}
    for value, (name, raw) in zip(requirements, files):
        require(name == value.staged_name and len(raw) == value.expected_bytes and
                _sha(raw) == value.expected_sha256, "collector_captured_file_role_changed")
        rows[value.role] = {"root": str(Path(value.root)), "relative_path": value.relative_path,
            "source_path": str(Path(value.root)/value.relative_path), "staged_name": name,
            "bytes": len(raw), "sha256": _sha(raw), "maximum_bytes": value.maximum_bytes}
    return {"kind": "timelearner_collector_required_files", "schema_version": 1, "roles": rows,
            "kernel_closure_attested": False, "test_success_attested": False, "scientific_verdict": None}


@dataclass(frozen=True)
class CapturedFileRoles:
    """Captured metadata bytes; public construction cannot grant any authority."""
    _requirements: tuple
    _files: tuple

    @property
    def descriptor(self):
        return _file_descriptor(self._requirements, self._files)

    def materialize(self, owned_root, staging):
        descriptor = self.descriptor  # validate all names/bytes BEFORE mkdir/open
        encoded = (json.dumps(descriptor, indent=2, allow_nan=False)+"\n").encode()
        return _stage_frozen_files(owned_root, staging,
            (*self._files, ("descriptor.json", encoded)), "collector-file-inputs/")


def capture_required_file_roles(requirements, *, maximum_total_bytes=64*1024**2):
    """Capture all explicitly required inputs before the publisher creates output."""
    _requirements(requirements, _file_role, maximum_total_bytes)
    names = [value.staged_name.casefold() for value in requirements]
    require(len(set(names)) == len(names), "collector_duplicate_staged_input")
    files = []
    try:
        paths = []
        for value in requirements:
            root = _canonical(value.root)
            require(root.is_dir(), "collector_input_root_not_directory")
            paths.append(root/value.relative_path)
        require(len(set(paths)) == len(paths), "collector_input_role_path_alias")
        for value, path in zip(requirements, paths):
            path = _canonical(path)
            require(path.lstat().st_size == value.expected_bytes, "collector_required_input_size_changed")
            raw, record = _frozen(path, value.maximum_bytes)
            require(record["bytes"] == value.expected_bytes and record["sha256"] == value.expected_sha256,
                    "collector_required_input_changed")
            files.append((value.staged_name, raw))
    except OSError as error:
        raise EvidenceError("collector_required_input_unavailable") from error
    captured = CapturedFileRoles(tuple(requirements), tuple(files))
    captured.descriptor
    return captured


def verify_git_input_roles(requirements, *, maximum_total_bytes=128*1024**2):
    """Validate explicit Git ODB capabilities; do not retain/duplicate primary bytes."""
    _requirements(requirements, _git_role, maximum_total_bytes)
    rows = {}
    try:
        for value in requirements:
            repository = _canonical(value.repository)
            require(repository.is_dir(), "collector_input_root_not_directory")
            require(_git(repository, "rev-parse", "HEAD").decode().strip() == value.repository_head,
                    "collector_git_role_head_changed")
            require(_git(repository, "rev-parse", value.commit+":"+value.path).decode().strip() == value.git_blob,
                    "collector_git_role_object_changed")
            raw, record = _git_blob(repository, value.commit, value.path, value.maximum_bytes,
                                    expected_bytes=value.expected_bytes)
            require(record["git_blob"] == value.git_blob and record["bytes"] == value.expected_bytes and
                    record["sha256"] == value.expected_sha256, "collector_git_role_object_changed")
            require(_git(repository, "rev-parse", "HEAD").decode().strip() == value.repository_head,
                    "collector_git_role_head_changed")
            rows[value.role] = {"repository": str(repository), "repository_head": value.repository_head,
                **record, "maximum_bytes": value.maximum_bytes, "payload_retained": False}
    except (OSError, subprocess.CalledProcessError) as error:
        raise EvidenceError("collector_git_role_object_unavailable") from error
    return {"kind": "timelearner_collector_git_input_roles", "schema_version": 1, "roles": rows,
            "kernel_closure_attested": False, "test_success_attested": False, "scientific_verdict": None}


def _assignment_targets(statement):
    roots = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
    return [node for root in roots for node in ast.walk(root)
            if isinstance(node, (ast.Name, ast.Attribute)) and isinstance(node.ctx, ast.Store)]


def _python_cases(raw, selected_class):
    """Closed literal dialect, never an import or a replacement test loader."""
    try:
        tree = ast.parse(raw)
    except (SyntaxError, UnicodeError, ValueError) as error:
        raise EvidenceError("collector_python_source_invalid") from error
    module_aliases = set()
    case_aliases = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            module_aliases.update(item.asname or item.name for item in node.names if item.name == "unittest")
        if isinstance(node, ast.ImportFrom) and node.module == "unittest":
            case_aliases.update(item.asname or item.name for item in node.names if item.name == "TestCase")
        require(not (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "load_tests"),
                "collector_python_dynamic_inventory_unsupported")
    def standard_case(base):
        return (isinstance(base, ast.Name) and base.id in case_aliases or
                isinstance(base, ast.Attribute) and base.attr == "TestCase" and
                isinstance(base.value, ast.Name) and base.value.id in module_aliases)
    def skip_decorator(node):
        call = node.func if isinstance(node, ast.Call) else node
        return isinstance(call, ast.Attribute) and isinstance(call.value, ast.Name) and \
            call.value.id in module_aliases and call.attr in ("skip", "skipIf", "skipUnless")
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    outside = [node.name for node in classes if selected_class is not None and node.name != selected_class]
    if selected_class is not None:
        classes = [node for node in classes if node.name == selected_class]
        require(len(classes) == 1, "collector_python_selected_class_missing")
    selected = []
    for node in classes:
        if not node.bases or all(isinstance(base, ast.Name) and base.id == "object" for base in node.bases):
            require(selected_class is None, "collector_python_selected_class_not_testcase")
            outside.append(node.name)
            continue
        require(len(node.bases) == 1 and standard_case(node.bases[0]) and not node.keywords and
                all(skip_decorator(item) for item in node.decorator_list),
                "collector_python_dynamic_or_inherited_class_unsupported")
        methods = [item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and item.name.startswith("test")]
        require(all(isinstance(item, ast.FunctionDef) and
                    all(skip_decorator(decorator) for decorator in item.decorator_list) for item in methods),
                "collector_python_dynamic_test_method_unsupported")
        require(len({item.name for item in methods}) == len(methods), "collector_python_duplicate_literal_test")
        # Test functions installed by assignments/conditionals/inherited bases
        # are outside this dialect, even if an expected count happens to match.
        for statement in node.body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # local variables/closures are not class test members
            for item in ast.walk(statement):
                require(not (isinstance(item, ast.Name) and isinstance(item.ctx, ast.Store) and
                             item.id.startswith("test")), "collector_python_dynamic_inventory_unsupported")
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test"):
                    require(False, "collector_python_dynamic_inventory_unsupported")
                if isinstance(item, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                    targets = _assignment_targets(item)
                    require(not any(isinstance(target, ast.Name) and target.id.startswith("test") or
                                    isinstance(target, ast.Attribute) and target.attr.startswith("test") for target in targets),
                            "collector_python_dynamic_inventory_unsupported")
        selected.append((node.name, [item.name for item in methods]))
    selected_names = {name for name, _ in selected}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for item in ast.walk(node):
            require(not isinstance(item, ast.ClassDef), "collector_python_conditional_class_unsupported")
            require(not (isinstance(item, ast.Name) and item.id in selected_names),
                    "collector_python_dynamic_inventory_unsupported")
            require(not (isinstance(item, ast.Name) and isinstance(item.ctx, ast.Store) and
                         item.id in module_aliases | case_aliases), "collector_python_dynamic_inventory_unsupported")
            if isinstance(item, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                targets = _assignment_targets(item)
                require(not any(isinstance(target, ast.Name) and target.id in module_aliases | case_aliases
                                for target in targets), "collector_python_dynamic_inventory_unsupported")
                require(not any(isinstance(target, ast.Name) and target.id in selected_names or
                                isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and
                                target.value.id in selected_names for target in targets),
                        "collector_python_dynamic_inventory_unsupported")
                if isinstance(item, ast.Assign):
                    require(not any(isinstance(value, ast.Name) and value.id in selected_names
                                    for value in ast.walk(item.value)),
                            "collector_python_dynamic_inventory_unsupported")
            if isinstance(item, ast.Call):
                require(not any(isinstance(argument, ast.Name) and argument.id in selected_names for argument in item.args),
                        "collector_python_dynamic_inventory_unsupported")
    require(selected and all(methods for _, methods in selected), "collector_python_literal_tests_missing")
    return selected, outside


def capture_python_selection_inventory(source_root, commit, selectors, expected_test_ids, *, maximum_source_bytes=8*1024**2):
    """Match explicit module/class selections to frozen Git+physical literal tests.

    The production unittest loader and actual log/result IDs remain required.
    Dynamic/method/inherited selection is rejected rather than guessed.
    """
    require(type(commit) is str and _COMMIT.fullmatch(commit) is not None, "collector_commit_invalid")
    _input_root(source_root)
    _input_count(maximum_source_bytes, positive=True)
    require(type(selectors) in (list, tuple) and selectors and
            all(type(value) is str and re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+", value) and
                value.startswith("Scripts.StructTrain.TimeLearner.tests.test_") for value in selectors) and
            len(set(selectors)) == len(selectors),
            "collector_python_selectors_invalid")
    require(type(expected_test_ids) in (list, tuple) and expected_test_ids and
            all(type(value) is str and value for value in expected_test_ids) and
            len(set(expected_test_ids)) == len(expected_test_ids), "collector_python_expected_ids_invalid")
    try:
        source_root = _canonical(source_root)
        require(source_root.is_dir(), "collector_input_root_not_directory")
        require(_git(source_root, "rev-parse", "HEAD").decode().strip() == commit, "collector_python_source_head_changed")
        paths = {}
        for entry in _git(source_root, "ls-tree", "-r", "-z", commit, "--", "Scripts/StructTrain/TimeLearner/tests").split(b"\0"):
            if entry:
                header, path = entry.split(b"\t", 1)
                mode, kind, oid = header.decode().split()
                if mode in ("100644", "100755") and kind == "blob" and path.endswith(b".py"):
                    paths[path.decode()] = oid
        contents = {}
        records = {}
        selections = []
        ids = []
        retained = 0
        for selector in selectors:
            parts = selector.split(".")
            matches = [(index, "/".join(parts[:index])+".py") for index in range(1, len(parts)+1)
                       if "/".join(parts[:index])+".py" in paths]
            require(len(matches) == 1, "collector_python_selector_source_missing_or_ambiguous")
            length, path = matches[0]
            require(len(parts)-length in (0, 1), "collector_python_method_selector_unsupported")
            chosen = None if length == len(parts) else parts[-1]
            if path not in contents:
                require(retained < maximum_source_bytes, "collector_python_source_size_budget")
                raw, record = _git_blob(source_root, commit, path, maximum_source_bytes-retained)
                working, _ = _frozen(source_root/path, maximum_source_bytes-retained)
                require(raw == working, "collector_python_physical_source_changed")
                retained += len(raw)
                contents[path] = raw
                records[path] = record
            classes, outside = _python_cases(contents[path], chosen)
            selected_ids = [".".join(parts[:length])+"."+name+"."+method
                            for name, methods in classes for method in methods]
            ids.extend(selected_ids)
            selections.append({"selector": selector, "path": path, "class": chosen,
                               "literal_test_ids": selected_ids, "outside_declared_scope": outside})
        require(len(ids) == len(set(ids)) and set(ids) == set(expected_test_ids), "collector_python_literal_inventory_changed")
        require(_git(source_root, "rev-parse", "HEAD").decode().strip() == commit, "collector_python_source_head_changed")
    except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
        raise EvidenceError("collector_python_source_unavailable") from error
    return {"kind": "timelearner_collector_python_literal_inventory", "schema_version": 1,
            "dialect": "literal-python-unittest-module-class-v1", "source_root": str(source_root),
            "source_commit": commit, "sources": records, "selections": selections, "literal_test_ids": sorted(ids),
            "runtime_inventory_verified": False, "tests_executed": False, "SDK_source_verified": False,
            "kernel_closure_attested": False, "test_success_attested": False, "scientific_verdict": None}


def _literal_cases(raw, suites=None):
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
    outside = []
    for match in re.finditer(
            r"^\s*(TEST_F|TEST_P|TYPED_TEST|TYPED_TEST_P)\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)", text, re.M):
        family, suite, name = match.groups()
        require(suites is not None and suite not in suites, "collector_test_dialect_unsupported")
        outside.append({"macro": family, "suite": suite, "id": suite+"/"+name,
                        "source_line": text[:match.start(1)].count("\n")+1,
                        "scope": "outside_declared_scope", "coverage_attested": False})
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
    return values, outside


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
        recognized, outside = _literal_cases(raw, suites)
        ids = [case for case in recognized if suites is None or case.split("/")[0] in suites]
        require(ids and (suites is None or set(suites) == {c.split("/")[0] for c in ids}),
                "collector_selected_suite_missing")
        files[path] = {**record, "dialect": DIALECT, "suites": suites, "ids": ids,
                       "recognized_ids": recognized, "outside_declared_scope": outside}
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
