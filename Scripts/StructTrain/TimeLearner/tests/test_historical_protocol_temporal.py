"""Actual archived native signals; execute on an analysis worker."""
import bisect
import os
from pathlib import Path
import unittest

from ..historical_protocol_robustness import analyze_case
from ..historical_protocol_temporal import trial_views


class HistoricalProtocolTemporal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = Path(os.environ["TL_HISTORICAL_PROTOCOL_CASE"]).resolve(strict=True)
        cls.observation = analyze_case(cls.folder, include_signals=True)

    def test_all_eight_complete_intervals_exclude_the_next_input(self):
        signals = self.observation["signals"]
        for trial in self.observation["trials"]:
            view = trial_views(signals, trial)
            self.assertLess(signals["times"][view["end"]-1], trial["interval_end"])
            if view["end"] < len(signals["times"]):
                self.assertGreaterEqual(signals["times"][view["end"]], trial["interval_end"])
                self.assertGreater(signals["stimulus"][view["end"]], 0)
            self.assertLess(view["first"], view["response_end"])
            self.assertLessEqual(view["response_end"], view["end"])
            self.assertGreater(signals["times"][view["response_end"]-1], trial["stimulus_times"][-1])

    def test_global_test_maxima_use_every_native_sample_in_the_complete_interval(self):
        signals = self.observation["signals"]
        for trial in self.observation["trials"]:
            view = trial_views(signals, trial)
            begin = bisect.bisect_left(signals["times"], trial["onset"])
            for channel, peak in zip(view["channels"], view["peaks"]):
                values = channel[begin:view["end"]]
                expected = max(values)
                self.assertEqual(peak["value"], expected)
                self.assertEqual(peak["time"], signals["times"][begin+values.index(expected)])
                self.assertEqual(peak["equal_maximum_samples"], values.count(expected))

    def test_optional_signals_preserve_the_original_observation_schema(self):
        plain = analyze_case(self.folder)
        self.assertEqual(plain, {k: v for k, v in self.observation.items() if k != "signals"})
        self.assertEqual(len(self.observation["signals"]["times"]), 80000)
        self.assertTrue(all(len(v) == 4 for v in self.observation["signals"]["somas"]))


if __name__ == "__main__":
    unittest.main()
