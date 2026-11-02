"""Exercise the declared runner with real package suites and absent native data."""
from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..native_evidence import EvidenceError
from ..validation import (package_fingerprint, fixture_fingerprint, preflight,
                          run_suite, _tests)


def declaration(module="test_condition"):
    name = "Scripts.StructTrain.TimeLearner.tests."+module
    suite = unittest.defaultTestLoader.loadTestsFromName(name)
    return {"kind": "timelearner_python_validation_suite", "schema_version": 1,
            "suite_id": "runner-contract", "package_fingerprint": package_fingerprint(),
            "modules": [name], "expected_test_ids": [t.id() for t in _tests(suite)], "fixtures": {}}


class ValidationContractTest(unittest.TestCase):
    def test_actual_condition_checks_run_and_receipts_bind_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = declaration();out = Path(directory)/"result"
            result = run_suite(spec, {}, out)
            self.assertEqual(result["assertion_status"], "passed")
            self.assertEqual(result["executed_tests"], len(spec["expected_test_ids"]))
            self.assertTrue((out/"suite.json").is_file())
            self.assertTrue((out/"unittest.log").is_file())
            self.assertIsNone(result["scientific_verdict"])

    def test_real_native_suite_without_artifacts_is_not_a_positive_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = declaration("test_native_gate")
            # A shell binding must not silently supply undeclared fixture data.
            with patch.dict(os.environ, {"TIMELEARNER_NATIVE_GATE_DIR": "/undeclared"}):
                result = run_suite(spec, {}, Path(directory)/"result")
                self.assertEqual(os.environ["TIMELEARNER_NATIVE_GATE_DIR"], "/undeclared")
            self.assertEqual(result["assertion_status"], "failed")
            self.assertTrue(result["skipped"])
            self.assertEqual(result["executed_tests"], 0)

    def test_changed_package_and_test_inventory_rejected_before_output(self):
        spec = declaration()
        for change, reason in ((lambda s: s.update(package_fingerprint="0"*64), "validation_package_changed"),
                               (lambda s: s["expected_test_ids"].pop(), "validation_test_inventory_changed"),
                               (lambda s: s["expected_test_ids"].append(s["expected_test_ids"][0]), "invalid_validation_expected_tests")):
            changed = deepcopy(spec);change(changed)
            with self.subTest(reason=reason), self.assertRaisesRegex(EvidenceError, reason):
                preflight(changed, {})

    def test_fixture_inventory_hash_and_exact_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);file = root/"Project.ini";file.write_bytes(b"<Project/>")
            count, fingerprint = fixture_fingerprint(root, "**/Project.ini")
            spec = declaration();spec["fixtures"] = {"TIMELEARNER_CONFIG_CORPUS": {
                "pattern": "**/Project.ini", "files": count, "fingerprint": fingerprint}}
            with self.assertRaisesRegex(EvidenceError, "validation_fixture_bindings_mismatch"):
                preflight(spec, {})
            preflight(spec, {"TIMELEARNER_CONFIG_CORPUS": root})
            file.write_bytes(b"<Different/>")
            with self.assertRaisesRegex(EvidenceError, "validation_fixture_changed"):
                preflight(spec, {"TIMELEARNER_CONFIG_CORPUS": root})

    def test_unknown_schema_and_fixture_traversal_rejected(self):
        spec = declaration();spec["schema_version"] = True
        with self.assertRaisesRegex(EvidenceError, "unknown_python_validation_suite"):
            preflight(spec, {})
        spec = declaration();spec["fixtures"] = {"TL_CORPUS": {
            "pattern": "../*.json", "files": 1, "fingerprint": "0"*64}}
        with self.assertRaisesRegex(EvidenceError, "invalid_validation_fixture_pattern"):
            preflight(spec, {"TL_CORPUS": "."})

    def test_existing_result_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory)/"previous.txt";marker.write_text("preserve")
            with self.assertRaises(FileExistsError):
                run_suite(declaration(), {}, directory)
            self.assertEqual(marker.read_text(), "preserve")
