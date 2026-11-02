"""Production readers on actual native output, with destructive negative copies."""
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from ..native_evidence import EvidenceError
from ..wall_schedule_reports import inventory_wall_schedule, render_reset_diagnostics


class WallScheduleReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_WALL_SCHEDULE_REPORT_DIR")
        if not directory:
            raise unittest.SkipTest("requires actual 66-case native wall-policy output")
        cls.source = Path(directory)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tl-wall-reports-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)/"run"
        shutil.copytree(self.source, self.root)

    def mutate(self, pattern, change):
        path = next((self.root/"native").glob(pattern))
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def test_complete_declared_set_preserves_invalid_and_raw_diagnostics(self):
        result = inventory_wall_schedule(self.root)
        self.assertEqual(result["native_inventory"]["trials"], 46)
        self.assertEqual(result["native_inventory"]["plottable_trial_soma_pairs"], 21)
        self.assertEqual(len(result["reset_diagnostics"]), 4)
        self.assertFalse(result["native_inventory"]["data_complete"])
        self.assertFalse(result["visual_acceptance_complete"])
        self.assertIsNone(result["scientific_verdict"])

    def test_missing_positive_probe_is_not_a_complete_test_report(self):
        next((self.root/"native").glob("*probe_4_evidence.json")).unlink()
        with self.assertRaises((EvidenceError, FileNotFoundError)):
            inventory_wall_schedule(self.root)

    def test_failed_junit_is_not_accepted_as_a_successful_gate(self):
        path = self.root/"native.xml"
        tree = ET.parse(path)
        ET.SubElement(next(tree.getroot().iter("testcase")), "failure", {"message": "negative control"})
        tree.write(path)
        with self.assertRaisesRegex(EvidenceError, "not_all_completed_successfully"):
            inventory_wall_schedule(self.root)

    def test_reset_cannot_claim_a_closed_probe(self):
        self.mutate("*reset_diagnostic.json", lambda row: row.update(closed_probe_available=True))
        with self.assertRaisesRegex(EvidenceError, "wall_reset_control_mismatch"):
            inventory_wall_schedule(self.root)

    def test_nonfinite_reset_sample_is_rejected(self):
        self.mutate("*reset_diagnostic.json", lambda row: row["raw_pre_reset_samples"][0]["soma"].__setitem__(0, float("nan")))
        with self.assertRaises(EvidenceError):
            inventory_wall_schedule(self.root)

    def test_reset_sample_clock_is_checked(self):
        self.mutate("*reset_diagnostic.json", lambda row: row["raw_pre_reset_samples"][1].update(time=0))
        with self.assertRaisesRegex(EvidenceError, "wall_reset_sample_clock_mismatch"):
            inventory_wall_schedule(self.root)

    def test_training_certificate_cannot_be_inferred_from_sink_change(self):
        self.mutate("*sink_policy_summary.json", lambda row: row.update(certificate=True))
        with self.assertRaisesRegex(EvidenceError, "wall_sink_control_mismatch"):
            inventory_wall_schedule(self.root)

    def test_extra_reset_diagnostic_is_not_silently_ignored(self):
        source = next((self.root/"native").glob("*reset_diagnostic.json"))
        shutil.copyfile(source, self.root/"native/extra_reset_diagnostic.json")
        with self.assertRaisesRegex(EvidenceError, "wall_missing_or_extra_reset_diagnostic"):
            inventory_wall_schedule(self.root)

    def test_renderer_cannot_write_into_primary_artifacts(self):
        with self.assertRaisesRegex(EvidenceError, "wall_output_inside_immutable_artifacts"):
            render_reset_diagnostics(self.root, self.root/"native/rendered")
