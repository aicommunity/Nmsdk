import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch

from Scripts.StructTrain.TimeLearner.plotting import time_views, series_timeline, detail_limits
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError


class PlotScaleTest(unittest.TestCase):
    def test_missing_backend_does_not_leave_partial_report(self):
        from Scripts.StructTrain.TimeLearner.reports import render_evaluation
        from Scripts.StructTrain.TimeLearner.probe_reports import render_probe, render_probe_set
        from Scripts.StructTrain.TimeLearner.native_test_reports import render_native_test_run
        from Scripts.StructTrain.TimeLearner.calibration_transaction_reports import render_calibration_transaction, render_calibration_run
        from Scripts.StructTrain.TimeLearner.posttune_transaction_reports import render_posttune_transaction, render_posttune_run
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);output = root/"report"
            calls = ((render_evaluation, (root/"evaluation.json", root/"model.json", output)),
                     (render_probe, (root/"probe.json", root/"trace.csv", output)),
                     (render_probe_set, (root/"spec.json", output)),
                     (render_native_test_run, (root/"spec.json", root/"artifacts", output)),
                     (render_calibration_transaction, (root/"transaction.json", output)),
                     (render_calibration_run, (root/"run-manifest.json", output)),
                     (render_posttune_transaction, (root/"transaction.json", root/"solo.json", output)),
                     (render_posttune_run, (root/"run-manifest.json", output)))
            for function, arguments in calls:
                with self.subTest(renderer=function.__name__), patch.dict("sys.modules", {"matplotlib": None}):
                    with self.assertRaisesRegex(EvidenceError, "plotting_runtime_unavailable"):
                        function(*arguments)
                    self.assertFalse(output.exists())
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

    def test_detail_preserves_negative_values_and_bracketing_samples(self):
        samples = [{"time": i*.001, "soma": [-.02+i*.00001]} for i in range(8)]
        limits = detail_limits(samples, 0, .002, .004, (-1., 1.))
        self.assertIsNotNone(limits)
        self.assertLess(limits[0], samples[1]["soma"][0])
        self.assertGreater(limits[1], samples[5]["soma"][0])
        self.assertIsNone(detail_limits(samples, 0, 1., 2., (-1., 1.)))
