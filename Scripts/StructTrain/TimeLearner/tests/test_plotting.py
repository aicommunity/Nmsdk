import unittest

from Scripts.StructTrain.TimeLearner.plotting import time_views
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
