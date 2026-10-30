"""Production report readback, including all soma series and local detail views."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load


class SeriesReportEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get("TIMELEARNER_SERIES_REPORT_DIR")
        if not directory:
            raise unittest.SkipTest("requires newly rendered actual-clock report")
        cls.root = Path(directory)
        cls.manifest = load(cls.root/"manifest.json")

    def test_every_recorded_soma_has_actual_order_and_intervals(self):
        manifest = self.manifest
        expected_channels = {f["descriptor"]["index"] for f in manifest["figures"]}
        self.assertEqual({s["descriptor"]["index"] for s in manifest["series"]}, expected_channels)
        spec = load(self.root/"primary/evaluation.json")
        wanted = sorted(spec["trials"], key=lambda t: t["presentation_index"])
        observations = [load(self.root/"primary"/t["observation"]) for t in wanted]
        for series in manifest["series"]:
            self.assertEqual([t["trial_id"] for t in series["timeline"]], [t["trial_id"] for t in wanted])
            for index, row in enumerate(series["timeline"]):
                self.assertEqual(row["begin"], observations[index]["begin"])
                self.assertIsNone(row["exact_reset_timestamp"])
                if index:
                    self.assertAlmostEqual(row["onset_to_onset_seconds"],
                        observations[index]["stimulus_times"][0]-observations[index-1]["stimulus_times"][0])
            for view in series["views"]:
                self.assertFalse(view["clock_compression"])
                self.assertEqual(view["begin"], observations[view["first_presentation"]]["begin"])
                for relative in view["files"]:
                    self.assertTrue((self.root/relative).is_file())

    def test_detail_is_additional_and_explicit_not_hidden_rescaling(self):
        details = 0
        for figure in self.manifest["figures"]:
            by_name = {view["view"]: view for view in figure["views"]}
            for view in figure["views"]:
                if view["y_scale"] != "local_detail":
                    continue
                details += 1
                shared = by_name[view["time_view"]]
                self.assertEqual(shared["y_scale"], "shared")
                self.assertEqual(view["begin"], shared["begin"])
                self.assertEqual(view["end"], shared["end"])
                self.assertEqual(view["shared_y_limits"], shared["y_limits"])
                self.assertLess(view["y_limits"][1]-view["y_limits"][0],
                                shared["y_limits"][1]-shared["y_limits"][0])
        self.assertGreater(details, 0)
