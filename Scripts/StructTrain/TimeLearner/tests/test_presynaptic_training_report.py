"""Exercise the production comparator on a declared real Stock/PSI pair."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..presynaptic_training_report import compare


class PresynapticTrainingReportTest(unittest.TestCase):
    def test_actual_pair_keeps_all_rejections_and_readable_response_zooms(self):
        from PIL import Image

        controls = Path(os.environ["TIMELEARNER_PSI_PAIR_REPORT_CONTROLS"])
        declaration = load(controls/"declaration.json")
        output = Path(os.environ["TMPDIR"])/"presynaptic-cold-training-gallery"
        result = compare(declaration["stock"], declaration["psi"], output)
        self.assertEqual(result["effective_full_window_frames"], [0, 3600])
        self.assertTrue(result["derived_guards_profile_specific"])
        self.assertFalse(result["new_model_execution"])
        self.assertIsNone(result["scientific_verdict"])
        for role, row in result["rows"].items():
            expected = declaration["expected"][role]
            facts, report = row["facts"], row["report"]
            self.assertEqual(len(facts["all_scalar_candidates"]), expected["scalar_candidates"])
            self.assertEqual(facts["outcome"], expected["outcome"])
            self.assertIsNone(facts["certificate"])
            self.assertTrue(facts["all_rejected_groups_selected"])
            self.assertEqual(facts["composite_counters"]["archive"]["groups"], expected["groups"])
            self.assertFalse(report["downsampling"])
            self.assertFalse(report["visual_acceptance_complete"])
            self.assertTrue(report["native_response_zoom_policy"]["diagnostic_axis_only"])
            self.assertFalse(report["native_response_zoom_policy"]["peak_assignment_changed"])
            response = [f for f in report["figures"] if f["view"] == "response-maximum-native"]
            self.assertTrue((output/role/"index.html").is_file())
            self.assertEqual(len(response), len(report["groups"]))
            for figure in response:
                source = figure["response_zoom_source"]
                self.assertTrue(source["diagnostic_axis_only"])
                self.assertLessEqual(figure["x_bounds_seconds"][0], source["relative_time"])
                self.assertGreaterEqual(figure["x_bounds_seconds"][1], source["relative_time"])
                self.assertGreater(source["relative_time"], 0.)
                self.assertGreaterEqual(figure["minimum_native_tick_pixels"], 8.)
                with Image.open(output/role/figure["files"][0]) as image:
                    self.assertEqual(image.size, (2880, 2880))
