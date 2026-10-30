"""Actual native-suite coverage with destructive copies, never fabricated PASS."""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from ..native_evidence import EvidenceError, load
from ..native_test_reports import inventory_native_test_run, render_native_test_run


class NativeTestReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_NATIVE_TEST_REPORT_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual complete repeated-boundary native suite")
        cls.source = Path(directory)
        cls.contract = Path(__file__).parents[1]/"specs/repeat-boundary-native-v1.json"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tl-native-coverage-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = self.root/"spec.json"
        shutil.copyfile(self.contract, self.spec)

    def copied_run(self):
        target = self.root/"run"
        shutil.copytree(self.source/"native", target/"native")
        shutil.copyfile(self.source/"native.xml", target/"native.xml")
        return target

    def test_all_actual_phases_and_imported_processes_are_accounted_for(self):
        result = inventory_native_test_run(self.spec, self.source)
        self.assertEqual(result["tests"], 51)
        self.assertEqual(len(result["groups"]), 78)
        self.assertEqual(result["trials"], 338)
        self.assertEqual(sum(g["summary"] is not None for g in result["groups"]), 26)
        self.assertEqual(sum(e["json_pointer"] == "/probe" for g in result["groups"] for e in g["trials"]), 16)
        self.assertFalse(result["data_complete"])
        self.assertFalse(result["visual_acceptance_complete"])
        self.assertIsNone(result["scientific_verdict"])

    def test_whole_missing_phase_cannot_disappear_from_expected_coverage(self):
        spec = load(self.spec); spec["phases"].pop()
        self.spec.write_text(json.dumps(spec))
        with self.assertRaisesRegex(EvidenceError, "missing_or_extra_declared_phase"):
            inventory_native_test_run(self.spec, self.source)

    def test_deleted_trailing_probe_fails_the_recorded_phase_counter(self):
        root = self.copied_run(); phase = load(self.spec)["phases"][0]
        summary = load(root/"native"/phase["summary"])
        ordinal = summary["reference_probes"]+summary["search_probes"]
        (root/"native"/(phase["probe_prefix"]+str(ordinal)+".json")).unlink()
        with self.assertRaisesRegex(EvidenceError, "missing_or_extra_probe"):
            inventory_native_test_run(self.spec, root)

    def test_orphan_csv_and_dropped_fresh_process_are_not_silently_ignored(self):
        root = self.copied_run()
        (root/"native/orphan.csv").write_text("time,stimulus,soma0\n")
        with self.assertRaisesRegex(EvidenceError, "unaccounted_or_missing_primary_csv"):
            inventory_native_test_run(self.spec, root)
        spec = load(self.spec)
        spec["standalone"] = [r for r in spec["standalone"] if r["json_pointer"] != "/probe"]
        self.spec.write_text(json.dumps(spec))
        with self.assertRaisesRegex(EvidenceError, "unaccounted_or_missing_primary_packet"):
            inventory_native_test_run(self.spec, self.source)

    def test_reused_trial_id_in_another_execution_is_not_a_single_observation(self):
        result = inventory_native_test_run(self.spec, self.source)
        fresh = [g for g in result["groups"] if g["identity"].endswith("/probe")]
        self.assertEqual(len(fresh), 16)
        # The importer deliberately uses a stable ID. Original wrapper/hash and
        # execution group must distinguish these separate measured responses.
        self.assertLess(len({g["trials"][0]["trial_id"] for g in fresh}), len(fresh))
        self.assertEqual(len({g["identity"] for g in fresh}), 16)
        spec = load(self.spec);spec["standalone"].append(spec["standalone"][0])
        self.spec.write_text(json.dumps(spec))
        with self.assertRaises(EvidenceError):
            inventory_native_test_run(self.spec, self.source)

    def test_skipped_native_case_cannot_produce_complete_test_report(self):
        root = self.copied_run(); path = root/"native.xml"
        from xml.etree import ElementTree as ET
        xml = ET.parse(path)
        ET.SubElement(next(xml.getroot().iter("testcase")), "skipped")
        xml.write(path)
        with self.assertRaisesRegex(EvidenceError, "not_all_completed_successfully"):
            inventory_native_test_run(self.spec, root)

    def test_render_cannot_write_into_immutable_native_artifacts(self):
        root = self.copied_run()
        output = root/"native/recursive-output"
        with self.assertRaisesRegex(EvidenceError, "outside_immutable_artifacts"):
            render_native_test_run(self.spec, root, output)
        self.assertFalse(output.exists())
