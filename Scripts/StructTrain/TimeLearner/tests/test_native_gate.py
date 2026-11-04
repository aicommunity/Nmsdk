"""Audit actual native JUnit and destructive temporary copies, without running a substitute model."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

from ..native_evidence import EvidenceError
from ..native_gate import FIELDS, _environment, audit_junit, supported_specification


class NativeGateJUnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get("TIMELEARNER_NATIVE_GATE_DIR")
        if not root:
            raise unittest.SkipTest("requires an actual completed native-gate run")
        cls.root = Path(root)
        cls.expected = json.loads((cls.root/"specification.json").read_text())["expected_test_ids"]
        cls.original = (cls.root/"native.xml").read_bytes()

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="tl-native-junit-")
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name)/"native.xml"
        self.path.write_bytes(self.original)

    def mutate(self, change):
        tree = ET.parse(self.path)
        change(tree.getroot())
        tree.write(self.path, encoding="utf-8", xml_declaration=True)

    def test_actual_inventory_and_reversed_declaration_have_identical_results(self):
        result = audit_junit(self.path, self.expected)
        self.assertEqual(result, audit_junit(self.path, list(reversed(self.expected))))
        self.assertEqual(result["observed"], len(self.expected))

    def test_actual_contract_and_explicit_capture_versions(self):
        original = json.loads((self.root/"specification.json").read_text())
        self.assertTrue(supported_specification(original))
        legacy = {key: original[key] for key in FIELDS}
        legacy['schema_version'] = 1
        self.assertTrue(supported_specification(legacy))
        cooperative = dict(legacy, schema_version=2, cooperative_runtime_capture=True)
        self.assertTrue(supported_specification(cooperative))
        for change in ({"schema_version": True}, {"schema_version": 3},
                       {"cooperative_runtime_capture": 1}, {"cooperative_runtime_capture": "true"},
                       {"cooperative_runtime_capture": False}, {"unknown_capture_option": True}):
            self.assertFalse(supported_specification(dict(cooperative, **change)))
        self.assertFalse(supported_specification(dict(legacy, cooperative_runtime_capture=True)))

    def test_missing_or_duplicate_identity_is_rejected(self):
        for duplicate in (False, True):
            self.path.write_bytes(self.original)
            def change(root):
                cases = list(root.iter("testcase"))
                if duplicate:
                    cases[1].set("classname", cases[0].get("classname"))
                    cases[1].set("name", cases[0].get("name"))
                else:
                    cases[0].set("name", "NotTheDeclaredCase")
            self.mutate(change)
            with self.assertRaisesRegex(EvidenceError, "expected_set_mismatch"):
                audit_junit(self.path, self.expected)

    def test_skipped_or_unfinished_case_is_rejected(self):
        for attribute, value in (("status", "notrun"), ("result", "suppressed"), (None, None)):
            self.path.write_bytes(self.original)
            def change(root):
                case = next(root.iter("testcase"))
                if attribute:
                    case.set(attribute, value)
                else:
                    ET.SubElement(case, "skipped")
            self.mutate(change)
            with self.assertRaisesRegex(EvidenceError, "skipped_or_unfinished"):
                audit_junit(self.path, self.expected)

    def test_corrupt_totals_are_rejected(self):
        for field in ("tests", "failures", "errors", "disabled"):
            self.path.write_bytes(self.original)
            self.mutate(lambda root: root.set(field, str(int(root.get(field, "0"))+1)))
            with self.assertRaisesRegex(EvidenceError, "totals_mismatch"):
                audit_junit(self.path, self.expected)

    def test_complete_assertion_failure_is_observed_as_failed(self):
        def change(root):
            for parent in root.iter():
                for child in list(parent):
                    if child.tag in ("failure", "error"):
                        parent.remove(child)
            ET.SubElement(next(root.iter("testcase")), "failure", message="destructive reader control")
            root.set("failures", "1")
            root.set("errors", "0")
        self.mutate(change)
        result = audit_junit(self.path, self.expected)
        self.assertEqual(result["assertion_status"], "failed")
        self.assertEqual(len(result["failed_test_ids"]), 1)

    def test_truncated_xml_is_rejected(self):
        self.path.write_bytes(self.original[:len(self.original)//2])
        with self.assertRaises(ET.ParseError):
            audit_junit(self.path, self.expected)


class NativeGateEnvironmentTest(unittest.TestCase):
    def test_present_and_absent_environment_are_restored_after_exception(self):
        present, absent = "TIMELEARNER_GATE_TEST_PRESENT", "TIMELEARNER_GATE_TEST_ABSENT"
        old = {key: os.environ.get(key) for key in (present, absent)}
        try:
            os.environ[present] = "original"
            os.environ.pop(absent, None)
            with self.assertRaisesRegex(RuntimeError, "deliberate"):
                with _environment({present: None, absent: "temporary"}):
                    self.assertNotIn(present, os.environ)
                    self.assertEqual(os.environ[absent], "temporary")
                    raise RuntimeError("deliberate")
            self.assertEqual(os.environ[present], "original")
            self.assertNotIn(absent, os.environ)
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
