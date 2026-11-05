"""Publication exclusion and explicit Linux recovery after the whole Git chain exits.

The persistent guard inode is never unlinked. Git children inherit the locked
descriptor, so killing the Python frontend alone cannot authorize recovery.
Legacy/foreign lock directories are deliberately not recovered by this API.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
from pathlib import Path
import socket
import uuid

from .native_evidence import EvidenceError, load, require


_descriptor = ContextVar("timelearner_publication_guard", default=None)


def git_lock_arguments():
    descriptor = _descriptor.get()
    return {"pass_fds": (descriptor,)} if descriptor is not None else {}


def _start(pid):
    try:
        # The comm field can contain whitespace and parentheses.
        return Path("/proc", str(pid), "stat").read_text().rsplit(") ", 1)[1].split()[19]
    except FileNotFoundError:
        return None


@contextmanager
def _guard(common):
    require(os.name == "posix" and Path("/proc/sys/kernel/random/boot_id").is_file(),
            "publication_recovery_requires_linux_kernel_guard")
    import fcntl
    path = common/"timelearner-publication.guard"
    flags = os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise EvidenceError("publication_guard_busy_owner_or_git_child_live") from error
        stat = os.fstat(descriptor)
        token = _descriptor.set(descriptor)
        try:
            yield {"descriptor": descriptor, "device": stat.st_dev, "inode": stat.st_ino}
        finally:
            _descriptor.reset(token)
        # Do NOT explicitly LOCK_UN: an inherited descriptor may still belong
        # to a Git child after a failed/timed-out frontend operation.
    finally:
        os.close(descriptor)


@contextmanager
def hold(common):
    common = Path(common).resolve(strict=True)
    lock = common/"timelearner-publication.lock"
    if os.name != "posix" or not Path("/proc/sys/kernel/random/boot_id").is_file():
        # Preserve the conservative legacy behavior on non-server platforms.
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise EvidenceError("publication_lock_exists_inspect_owner_before_recovery") from error
        try:
            (lock/"owner.json").write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
            yield
        finally:
            (lock/"owner.json").unlink(missing_ok=True)
            lock.rmdir()
        return
    with _guard(common) as guard:
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise EvidenceError("publication_lock_exists_inspect_owner_before_recovery") from error
        try:
            owner = {"kind": "timelearner_kernel_publication_lock", "schema_version": 1,
                     "pid": os.getpid(), "start_ticks": _start(os.getpid()),
                     "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                     "host": socket.gethostname(), "token": uuid.uuid4().hex,
                     "guard_device": guard["device"], "guard_inode": guard["inode"]}
            require(owner["start_ticks"] is not None, "publication_owner_identity_missing")
            (lock/"owner.json").write_text(json.dumps(owner, indent=2)+"\n", encoding="utf-8")
            yield
        finally:
            (lock/"owner.json").unlink(missing_ok=True)
            lock.rmdir()


def recover(common):
    common = Path(common).resolve(strict=True)
    # Do not manufacture a new inode and use it to attest an older lock.
    require((common/"timelearner-publication.guard").is_file(), "publication_guard_missing")
    with _guard(common) as guard:
        lock = common/"timelearner-publication.lock"
        require(lock.is_dir() and not lock.is_symlink(), "publication_lock_missing_or_symlink")
        require({p.name for p in lock.iterdir()} == {"owner.json"} and
                not (lock/"owner.json").is_symlink(), "publication_lock_contents_unknown")
        owner = load(lock/"owner.json")
        require(type(owner) is dict and set(owner) == {
            "kind", "schema_version", "pid", "start_ticks", "boot_id", "host", "token",
            "guard_device", "guard_inode"} and owner["kind"] == "timelearner_kernel_publication_lock"
            and type(owner["schema_version"]) is int and owner["schema_version"] == 1,
            "publication_legacy_or_unknown_lock_requires_manual_inspection")
        require(type(owner["pid"]) is int and owner["pid"] > 0 and
                type(owner["start_ticks"]) is str and owner["start_ticks"].isdigit() and
                type(owner["token"]) is str and len(owner["token"]) == 32 and
                all(c in "0123456789abcdef" for c in owner["token"]), "publication_owner_record_invalid")
        require(owner["host"] == socket.gethostname() and
                owner["boot_id"] == Path("/proc/sys/kernel/random/boot_id").read_text().strip() and
                type(owner["guard_device"]) is int and owner["guard_device"] == guard["device"] and
                type(owner["guard_inode"]) is int and owner["guard_inode"] == guard["inode"],
                "publication_owner_host_boot_or_guard_changed")
        require(_start(owner["pid"]) != owner["start_ticks"], "publication_owner_still_live")
        # Atomic rename preserves the full old owner record, including crash
        # windows: recovery never deletes an unverified directory recursively.
        archive = common/("timelearner-publication-recovered-"+uuid.uuid4().hex)
        lock.rename(archive)
        return {"kind": "timelearner_publication_lock_recovery", "schema_version": 1,
                "recovery": "recovered", "previous_owner": owner,
                "preserved_owner_directory": str(archive), "kernel_guard_acquired": True,
                "previous_owner_identity_live": False, "git_push_executed": False,
                "publication": "not_attempted", "scientific_verdict": None}
