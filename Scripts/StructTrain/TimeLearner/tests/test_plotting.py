import unittest

from Scripts.StructTrain.TimeLearner.plotting import time_views, series_timeline
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError


class PlotScaleTest(unittest.TestCase):
    def test_each_zoom_resolves_one_tick_at_high_absolute_clock(self):
        for frequency in (2000, 20000):
            views = time_views(192., 192.12, frequency)
            self.assertEqual(views[0], ("overview", 192., 192.12))
            self.assertGreater(len(views), 1)
            self.assertEqual(views[1][1], 192.)
            self.assertEqual(views[-1][2], 192.12)
            for _, begin, end in views[1:]:
                self.assertLessEqual((end-begin)*frequency, 100.000001)
                self.assertGreater(end, begin)
            for left, right in zip(views[1:], views[2:]):
                self.assertAlmostEqual(left[2], right[1])

    def test_invalid_window_is_not_repaired(self):
        for args in ((0, 0, 2000), (1, 0, 2000), (0, 1, 0), (0, 1, float("nan"))):
            with self.assertRaises(EvidenceError):
                time_views(*args)

    def test_series_retains_real_gaps_and_reset_boundaries(self):
        def trial(i, start, end, reset, stimuli):
            return {"trial_id": f"t{i}", "sample_id": f"s{i}", "label": "target",
                    "begin": start, "end": end, "closed_at": end,
                    "reset_policy": reset, "frequency_hz": 2000.,
                    "stimulus_times": stimuli}
        rows = series_timeline([trial(0, 0., .1, "reset_per_trial", [.01]),
                                trial(1, .25, .35, "preserve_neuron_dynamics", [.26])])
        self.assertEqual(rows[1]["unobserved_gap"], [.1, .25])
        self.assertEqual(rows[1]["onset_to_onset_seconds"], .25)
        self.assertIsNone(rows[0]["exact_reset_timestamp"])
