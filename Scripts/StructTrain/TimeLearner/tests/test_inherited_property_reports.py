"""Actual declared inherited-property suite; corruption uses temporary copies."""
import csv
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..native_test_reports import inventory_native_test_run


class InheritedPropertyReports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path(os.environ["TIMELEARNER_INHERITED_REPORT_DIR"])
        cls.contract = Path(__file__).parents[1]/"specs/inherited-properties-native-v1.json"

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tl-inherited-reports-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.spec = self.root/"spec.json"
        self.design = json.loads(self.contract.read_text())
        self.save()

    def save(self):
        self.spec.write_text(json.dumps(self.design))

    def copied(self):
        target = self.root/"run"
        shutil.copytree(self.source/"native", target/"native")
        shutil.copyfile(self.source/"native.xml", target/"native.xml")
        return target

    def test_full_declared_standalone_suite_includes_expected_rejections(self):
        result = inventory_native_test_run(self.spec, self.source)
        self.assertEqual(result["tests"],16)
        self.assertEqual(result["trials"],56)
        self.assertEqual(len(result["groups"]),56)
        self.assertEqual(result["known_trial_soma_pairs"],72)
        self.assertEqual(result["plottable_trial_soma_pairs"],72)
        entries = [e for group in result["groups"] for e in group["trials"]]
        self.assertEqual(sum(e["channels"] == 0 for e in entries),8)
        self.assertFalse(result["data_complete"])
        self.assertIsNone(result["scientific_verdict"])

    def test_all_groups_empty_cannot_be_a_complete_report(self):
        self.design["standalone"] = [];self.save()
        with self.assertRaisesRegex(EvidenceError,"invalid_native_test_groups"):
            inventory_native_test_run(self.spec,self.source)

    def test_missing_declared_probe_cannot_be_inferred_from_surviving_files(self):
        self.design["standalone"].pop();self.save()
        with self.assertRaisesRegex(EvidenceError,"unaccounted_or_missing_primary_packet"):
            inventory_native_test_run(self.spec,self.source)

    def test_missing_csv_is_rejected(self):
        target = self.copied()
        (target/"native"/self.design["standalone"][0]["trace"]).unlink()
        with self.assertRaises((EvidenceError,FileNotFoundError)):
            inventory_native_test_run(self.spec,target)

    def test_duplicate_test_identity_is_rejected(self):
        self.design["expected_test_ids"].append(self.design["expected_test_ids"][0]);self.save()
        with self.assertRaisesRegex(EvidenceError,"invalid_native_test_expected_tests"):
            inventory_native_test_run(self.spec,self.source)

    def test_nonfinite_complete_trace_is_not_downgraded_into_valid_diagnostic(self):
        target = self.copied();trace = target/"native"/self.design["standalone"][0]["trace"]
        with trace.open(newline="") as stream:rows = list(csv.reader(stream))
        self.assertGreater(len(rows),2);rows[1][2] = "nan"
        with trace.open("w",newline="") as stream:csv.writer(stream).writerows(rows)
        with self.assertRaises(EvidenceError):inventory_native_test_run(self.spec,target)

    def test_extra_csv_is_not_silently_ignored(self):
        target = self.copied();native = target/"native"
        shutil.copyfile(native/self.design["standalone"][0]["trace"],native/"undeclared.csv")
        with self.assertRaisesRegex(EvidenceError,"unaccounted_or_missing_primary_csv"):
            inventory_native_test_run(self.spec,target)
