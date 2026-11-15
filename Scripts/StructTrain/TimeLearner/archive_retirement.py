"""Typed duplicate-AR maintenance over the unchanged production apply_plan.

Only a previously reviewed plan and its hashed read-only snapshot are accepted.
Retained symlinks are inventoried with lstat/readlink, never dereferenced.
"""
import json
import os
from pathlib import Path
import stat
import subprocess
import time

from .collector_provenance import _canonical, _frozen, _json
from .contained_process import inspect
from .native_evidence import require
from .runtime import file_record
from . import static_archive_cleanup
from .static_archive_cleanup import apply_plan, _record


def _identity(value):
    return [value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns,
            value.st_ctime_ns, value.st_nlink]


def _link(path):
    _canonical(path.parent)
    before = path.lstat()
    require(stat.S_ISLNK(before.st_mode), "archive_retained_link_type_changed")
    record = {"mode": before.st_mode, "identity": _identity(before),
              "link_text": os.readlink(path), "link_not_followed": True}
    require(_identity(path.lstat()) == record["identity"], "archive_retained_link_changed")
    return record


def snapshot(root, names):
    regular, links = {}, {}
    for name in names:
        directory = _canonical(root/name)
        regular[name], links[name] = {}, {}
        for path in sorted(directory.rglob("*")):
            before = path.lstat()
            if stat.S_ISDIR(before.st_mode):
                continue
            relative = path.relative_to(directory).as_posix()
            if stat.S_ISLNK(before.st_mode):
                links[name][relative] = _link(path)
                continue
            _canonical(path)
            require(stat.S_ISREG(before.st_mode), "archive_unclassified_retained_entry")
            value = file_record(path)
            require(_identity(path.stat()) == _identity(before), "archive_retained_file_changed")
            regular[name][relative] = {"bytes": value["size"], "sha256": value["sha256"],
                "identity": _identity(before), "allocated_bytes": before.st_blocks*512}
    return {"regular": regular, "links": links}


def _owners(rows, boot):
    observed = []
    for row in rows:
        owner = row["historical"]
        require(_json(_frozen(Path(row["path"]), 1024*1024)[0]) == owner,
                "archive_historical_owner_record_changed")
        current = None
        try:
            current = Path("/proc", str(owner["pid"]), "stat").read_text().rsplit(") ", 1)[1].split()[19]
        except (FileNotFoundError, ProcessLookupError):
            pass
        alive = current == str(owner["start_ticks"]) and owner.get("boot_id", boot) == boot
        require(not alive, "archive_historical_owner_still_alive")
        observed.append({"path": row["path"], "pid": owner["pid"],
                         "original_start_ticks": owner["start_ticks"],
                         "current_start_ticks": current, "same_identity_alive": alive})
    return observed


def _processes(roots, own_ancestry, approved):
    result = {"same_uid_scanned": 0, "other_uid_not_fully_scanned": 0,
              "path_matches": [], "unreadable_contexts": []}
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            if proc.stat().st_uid != os.getuid():
                result["other_uid_not_fully_scanned"] += 1
                continue
            ticks = (proc/"stat").read_text().rsplit(") ", 1)[1].split()[19]
            if own_ancestry.get(proc.name) == ticks:
                continue
            result["same_uid_scanned"] += 1
            values, denied = [], []
            for channel in ("cmdline", "maps"):
                try:
                    values.append((channel, (proc/channel).read_bytes().replace(b"\0", b" ").decode(errors="replace")))
                except PermissionError:
                    denied.append(channel)
            for channel in ("cwd", "exe"):
                try:
                    values.append((channel, os.readlink(proc/channel)))
                except PermissionError:
                    denied.append(channel)
            try:
                for path in (proc/"fd").iterdir():
                    try:
                        values.append(("fd:"+path.name, os.readlink(path)))
                    except FileNotFoundError:
                        pass
            except PermissionError:
                denied.append("fd")
            hits = [{"channel": key, "root": str(root)} for key, value in values
                    for root in roots if str(root) in value]
            if hits:
                result["path_matches"].append({"pid": int(proc.name), "start_ticks": ticks, "hits": hits})
            if denied:
                row = {"pid": int(proc.name), "start_ticks": ticks, "comm": (proc/"comm").read_text().strip(),
                       "cmdline": [v for k, v in values if k == "cmdline"],
                       "cgroup": (proc/"cgroup").read_text().strip(), "unreadable_channels": denied}
                row["matches_explicit_review"] = any(all(row[key] == old[key] for key in row)
                                                    for old in approved)
                result["unreadable_contexts"].append(row)
        except (FileNotFoundError, ProcessLookupError):
            pass
    return result


def retire(plan, review, registry, token, output, launch_ancestry, emit, extra_guard):
    """Run one fresh reviewed plan; never resume a partial journal automatically."""
    require(review["kind"] == "Elder_extra13_duplicate_AR_focused_readonly_review" and
            review["read_only"] is True and review["deletions_performed"] is False and
            review["approved_candidate_plan"] == plan, "archive_review_contract_mismatch")
    require(_frozen(Path(static_archive_cleanup.__file__), 1024*1024)[1]['sha256'] ==
            review['source_module_sha256'], 'archive_production_apply_plan_source_changed')
    root = _canonical(Path(plan["root"]))
    expected = {"regular": review["whole_regular_manifests"], "links": review["retained_symlinks_no_follow"]}
    names = sorted(expected["regular"])
    plan_names = {value["path"].split('/')[0] for row in plan['rows'] for value in (row['target'], row['keeper'])}
    require(set(names) == plan_names and all(type(name) is str and name.startswith('runtime-') and
            Path(name).name == name for name in names), 'archive_review_runtime_scope')
    roots = [root/name for name in names]
    old_kernel = review["fresh_known_kernel_observations"]
    owners = review["legacy_identity_observations"]
    approved = review["proc_visibility"]["unreadable"]
    boot = review["proc_visibility"]["boot_id"]
    require(Path("/proc/sys/kernel/random/boot_id").read_text().strip() == boot, "archive_worker_boot_changed")
    own = dict(launch_ancestry)
    pid = os.getpid()
    while pid > 1:
        fields = Path("/proc", str(pid), "stat").read_text().rsplit(") ", 1)[1].split()
        own[str(pid)] = fields[19]; pid = int(fields[1])
    before = snapshot(root, names)
    require(before == expected, "archive_whole_preimage_changed")
    emit("runtime-before.json", before)
    for row in plan["rows"]:
        for value in (row["target"], row["keeper"]):
            require(_record(root, value["path"]) == value, "archive_AR_preimage_changed")
    full_kernel = {}
    for directory, old in old_kernel.items():
        require(_json(_frozen(Path(directory)/'owned-unit.json', 1024*1024)[0]) == old['binding'],
                'archive_original_binding_missing_or_changed')
        current = inspect(Path(directory))
        require(current["binding"] == old["binding"] and current["all_processes_closed"] and
                current["state"]["MainPID"] == "0" and not current["state"]["ControlGroup"],
                "archive_historical_kernel_group_live")
        full_kernel[directory] = current
    emit("protected-kernel-before.json", full_kernel)
    units = {row["binding"]["unit"]: row["binding"] for row in old_kernel.values()}
    observations = []

    def guard():
        extra_guard()
        require(Path("/proc/sys/kernel/random/boot_id").read_text().strip() == boot, "archive_worker_boot_changed")
        rows = subprocess.run(["systemctl", "--user", "show",
            "--property=Id,LoadState,MainPID,ControlGroup,InvocationID", *units], capture_output=True,
            text=True, timeout=30).stdout
        kernel = [dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
                  for block in rows.strip().split("\n\n") if block.strip()]
        require(len(kernel) == len(units) and {r.get("Id") for r in kernel} == set(units), "archive_kernel_batch_incomplete")
        for value in kernel:
            binding = units[value["Id"]]
            require(value["MainPID"] == "0" and not value["ControlGroup"] and
                value["LoadState"] in ("loaded", "not-found") and
                (value["LoadState"] == "not-found" or value["InvocationID"] == binding["invocation_id"]) and
                not Path("/sys/fs/cgroup"+binding["control_group"]).exists(), "archive_kernel_group_drift")
        held = [row for row in registry.inspect()["leases"] if row["state"] == "held"]
        require(len(held) == 1 and held[0]["token"] == token, "archive_other_held_lease")
        process = _processes(roots, own, approved)
        for name, links in expected["links"].items():
            for relative, value in links.items():
                require(_link(root/name/relative) == value, "archive_retained_link_drift")
        value = {"index": len(observations), "time": time.time(), "kernel": kernel,
                 "owners": _owners(owners, boot), "process_visibility": process,
                 "retained_links_checked": sum(map(len, expected["links"].values())),
                 "universal_process_absence_claim": False}
        with (output/"fresh-guards.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, allow_nan=False)+"\n");stream.flush();os.fsync(stream.fileno())
        observations.append(value)
        require(not process["path_matches"] and all(r["matches_explicit_review"]
                for r in process["unreadable_contexts"]), "archive_unapproved_process_context")

    class CheckedRegistry:
        def validate_paths(self, value):
            registry.validate_paths(value); guard()
        def inspect(self):
            return registry.inspect()

    guard()
    receipt = apply_plan(plan, CheckedRegistry(), token, output/"unlink-journal.jsonl")
    emit("receipt.json", receipt)
    guard()
    after = snapshot(root, names)
    targets = {row["target"]["path"] for row in plan["rows"]}
    remaining = {name: {p: r for p, r in rows.items() if name+"/"+p not in targets}
                 for name, rows in before["regular"].items()}
    require(after == {"regular": remaining, "links": before["links"]} and
            all(not (root/path).exists() for path in targets), "archive_non_target_postimage_changed")
    for row in plan["rows"]:
        require(_record(root, row["keeper"]["path"]) == row["keeper"], "archive_keeper_postimage_changed")
    emit("runtime-after.json", after)
    emit("retirement-ledger.json", {"kind": "duplicate_AR_retirement_ledger", "schema_version": 1,
        "plan": plan, "before": before, "after": after, "guards": len(observations),
        "whole_runtime_historical_unchanged_claim": False, "scientific_verdict": None})
    return receipt
