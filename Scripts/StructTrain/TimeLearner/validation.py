"""Declared Python validation suites; missing evidence and skips never pass.

This runs package checks, not numerical experiments. Native tests remain owned
by native-gate and its immutable runtime manifest.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path
import unittest

from .native_evidence import EvidenceError, load, require
from .collector_provenance import frozen_digest


def _digest(records):
    raw = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def package_fingerprint():
    root = Path(__file__).parent
    return _digest({p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(root.rglob("*.py")) if "__pycache__" not in p.parts})


def fixture_fingerprint(root, pattern):
    paths = sorted(root.glob(pattern))
    require(paths and all(p.is_file() and not p.is_symlink() for p in paths),
            "validation_fixture_files_missing_or_not_regular")
    require(all(p.resolve().is_relative_to(root) for p in paths), "validation_fixture_escapes_root")
    return len(paths), _digest({p.relative_to(root).as_posix():
                               frozen_digest(p, max(1, p.stat().st_size))['sha256']
                               for p in paths})


def _tests(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from _tests(test)
        else:
            yield test


def preflight(specification, fixtures):
    require(type(specification) is dict and set(specification) == {
        "kind", "schema_version", "suite_id", "package_fingerprint", "modules", "expected_test_ids", "fixtures"}
        and specification["kind"] == "timelearner_python_validation_suite"
        and type(specification["schema_version"]) is int and specification["schema_version"] == 1,
        "unknown_python_validation_suite")
    require(type(specification["suite_id"]) is str and bool(specification["suite_id"]), "validation_suite_id_missing")
    require(specification["package_fingerprint"] == package_fingerprint(), "validation_package_changed")
    declarations = specification["fixtures"]
    require(type(declarations) is dict and type(fixtures) is dict and set(fixtures) == set(declarations),
            "validation_fixture_bindings_mismatch")
    resolved, evidence = {}, {}
    for name, declaration in declarations.items():
        require(type(name) is str and name.startswith(("TIMELEARNER_", "TL_"))
                and type(declaration) is dict and set(declaration) == {"pattern", "files", "fingerprint"},
                "invalid_validation_fixture_declaration")
        pattern = declaration["pattern"]
        require(type(pattern) is str and pattern and not Path(pattern).is_absolute()
                and ".." not in Path(pattern).parts and "\\" not in pattern,
                "invalid_validation_fixture_pattern")
        root = Path(fixtures[name]).resolve(strict=True)
        require(root.is_dir(), "validation_fixture_not_directory")
        count, fingerprint = fixture_fingerprint(root, pattern)
        require(type(declaration["files"]) is int and declaration["files"] > 0
                and count == declaration["files"] and fingerprint == declaration["fingerprint"],
                "validation_fixture_changed")
        resolved[name] = str(root)
        evidence[name] = {"path": str(root), "files": count, "fingerprint": fingerprint}
    modules, expected = specification["modules"], specification["expected_test_ids"]
    require(type(modules) is list and modules and all(type(n) is str and
            n.startswith("Scripts.StructTrain.TimeLearner.tests.test_") for n in modules)
            and len(modules) == len(set(modules)), "invalid_validation_modules")
    require(type(expected) is list and expected and all(type(n) is str and n for n in expected)
            and len(expected) == len(set(expected)), "invalid_validation_expected_tests")
    with _environment(resolved):
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in modules)
    observed = [t.id() for t in _tests(suite)]
    require(len(observed) == len(set(observed)) and set(observed) == set(expected),
            "validation_test_inventory_changed")
    return suite, resolved, evidence


@contextmanager
def _environment(bindings):
    # Artifact tests must not silently inherit undeclared fixtures from a shell.
    names = {n for n in os.environ if n.startswith(("TIMELEARNER_", "TL_"))} | set(bindings)
    previous = {n: os.environ.get(n) for n in names}
    try:
        for n in names:
            os.environ.pop(n, None)
        os.environ.update(bindings)
        yield
    finally:
        for n in names:
            os.environ.pop(n, None)
        for n, value in previous.items():
            if value is not None:
                os.environ[n] = value


def run_suite(specification, fixtures, output):
    suite, bindings, evidence = preflight(specification, fixtures)
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    log = io.StringIO()
    with _environment(bindings):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    accepted = result.wasSuccessful() and not result.skipped and result.testsRun == len(specification["expected_test_ids"])
    record = {"kind": "timelearner_python_validation_result", "schema_version": 1,
              "suite_id": specification["suite_id"], "package_fingerprint": specification["package_fingerprint"],
              "execution": "completed", "assertion_status": "passed" if accepted else "failed",
              "expected_test_ids": specification["expected_test_ids"], "executed_tests": result.testsRun,
              "failures": [t.id() for t, _ in result.failures], "errors": [t.id() for t, _ in result.errors],
              "skipped": [{"test_id": t.id(), "reason": reason} for t, reason in result.skipped],
              "fixtures": evidence, "scientific_verdict": None}
    (output/"unittest.log").write_text(log.getvalue(), encoding="utf-8")
    (output/"suite.json").write_text(json.dumps(specification, indent=2)+"\n", encoding="utf-8")
    (output/"result.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", type=Path)
    parser.add_argument("--fixture", action="append", default=[], metavar="NAME=PATH")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        bindings = {}
        for item in args.fixture:
            name, separator, path = item.partition("=")
            require(separator and name not in bindings and path, "invalid_validation_fixture_binding")
            bindings[name] = path
        record = run_suite(load(args.suite), bindings, args.output)
    except (EvidenceError, OSError, ValueError) as error:
        print(json.dumps({"execution": "validation_error", "assertion_status": "not_assessed",
                          "reason": str(error), "scientific_verdict": None}))
        return 2
    print(json.dumps(record))
    return 0 if record["assertion_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
