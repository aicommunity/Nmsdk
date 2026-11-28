import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch

from Scripts.StructTrain.TimeLearner.plotting import time_views, series_timeline, detail_limits
from Scripts.StructTrain.TimeLearner.native_evidence import EvidenceError


class PlotScaleTest(unittest.TestCase):
    def test_positive_overviews_share_an_explicit_comparison_range(self):
        import copy
        from Scripts.StructTrain.TimeLearner.plotting import render_positive_lobe_views
        def observation(peak):
            return dict(sample_id="control", label="foil", trial_id="trial",
                reset_policy="reset_per_trial", valid=True, complete=True,
                begin=0., end=.002, closed_at=.002, frequency_hz=1000.,
                spike_times=[], model_before="a"*64,
                samples=[dict(time=i*.001, soma=[v], stimulus=float(i==1))
                         for i,v in enumerate([-1.,peak,0.])])
        observations=[observation(.1),observation(.2)]
        originals=copy.deepcopy(observations)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); overviews=[]
            for i,o in enumerate(observations):
                folder=root/str(i);folder.mkdir()
                views=render_positive_lobe_views(o,0,"soma",folder,
                    shared_minimum=-1.,shared_maximum=.2)
                overview=next(v for v in views if v['view']=='positive-lobe-detail-overview')
                self.assertEqual(overview['positive_range_scope'],'shared')
                self.assertLess(overview['y_limits'][0],0.)
                self.assertGreater(overview['y_limits'][1],.2)
                self.assertTrue((folder/overview['files'][0]).is_file())
                overviews.append(overview)
            self.assertEqual(overviews[0]['y_limits'],overviews[1]['y_limits'])
            folder=root/'local';folder.mkdir()
            views=render_positive_lobe_views(observations[0],0,"soma",folder)
            self.assertTrue(all(v['positive_range_scope']=='per_observation' for v in views))
            svg=(folder/views[0]['files'][1]).read_text()
            self.assertIn('per_observation Y',svg)
        self.assertEqual(observations,originals)

    def test_invalid_shared_positive_maximum_is_rejected_before_rendering(self):
        from Scripts.StructTrain.TimeLearner.plotting import render_positive_lobe_views
        observation=dict(samples=[dict(soma=[-.1]),dict(soma=[.2])])
        with tempfile.TemporaryDirectory() as directory:
            for maximum in (True,.1,float('nan'),float('inf')):
                with self.subTest(maximum=maximum):
                    folder=Path(directory)/'never-created'
                    with self.assertRaisesRegex(EvidenceError,'invalid_positive_lobe_shared_maximum'):
                        render_positive_lobe_views(observation,0,'soma',folder,shared_maximum=maximum)
                    self.assertFalse(folder.exists())

    def test_actual_long_trial_title_fits_fixed_page_and_preserves_identifiers(self):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from Scripts.StructTrain.TimeLearner.plotting import figure_title
        text = ('Stopped Train: invalid_observation | phasea-row-0 | target | '
                'Classic-threshold-low/stopped-phasea-diagnostic/rotation-0/0\n'
                '$.Soma1.SumPotential | reset_per_trial\n'
                'overview (shared Y) | valid=True, complete=True | model aeeb20de9f62')
        fig = plt.figure(figsize=(12, 6), dpi=160)
        try:
            title = figure_title(fig, text)
            self.assertEqual(''.join(title.get_text().split()), ''.join(text.split()))
            bounds = title.get_window_extent(fig.canvas.get_renderer())
            self.assertGreaterEqual(bounds.x0, .03*1920)
            self.assertLessEqual(bounds.x1, .97*1920)
            self.assertGreaterEqual(bounds.y0, .85*960)
            self.assertGreaterEqual(title.get_fontsize(), 9)
            self.assertEqual(fig.canvas.get_width_height(), (1920, 960))
        finally:
            plt.close(fig)

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
