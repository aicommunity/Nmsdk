"""Real32-trial stock diagnostics: all soma/input plots and unfinished role."""
import hashlib
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recognition_metrics import load_diagnostic_evaluation
from ..stock_stopped_evaluation import audit


class StockStoppedReportsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        values = [os.environ.get(k) for k in
                  ('TIMELEARNER_STOCK_STOPPED_EVALUATION', 'TIMELEARNER_STOCK_STOPPED_REPORTS')]
        if not all(values):
            raise unittest.SkipTest('requires actual32 native trials and completed production temporal cache')
        cls.source, cls.report = map(Path, values)

    def test_all_original_samples_and_eighty_trial_soma_pairs_are_preserved(self):
        analyzed = audit(self.source)
        manifest = load(self.report/'manifest.json')
        self.assertEqual(load(self.report/'analysis.json'), analyzed)
        self.assertEqual(manifest['trials'], 32)
        self.assertEqual(manifest['trial_soma_pairs'], 80)
        self.assertEqual(len(manifest['models']), 4)
        observed_pairs = set()
        for row in analyzed['models']:
            name = row['name'];folder = self.report/name/'evaluation'
            original = self.source/'runs'/name/'native/evaluation.json'
            _, before = load_diagnostic_evaluation(original)
            _, after = load_diagnostic_evaluation(folder/'primary/evaluation.json')
            self.assertEqual(after, before)
            expected = {(o['trial_id'], i) for o in before
                        for i in range(len(o['samples'][0]['soma']))}
            rendered = load(folder/'manifest.json')
            self.assertEqual({(f['trial_id'], f['descriptor']['index']) for f in rendered['figures']}, expected)
            # The pipeline embeds the actual return value of render_diagnostic_evaluation.
            # A correct nested manifest alone cannot prove the batch interface works.
            pipeline = load(self.report/name/'manifest.json')
            self.assertTrue(pipeline['evaluation_report']['diagnostic_only'])
            self.assertFalse(pipeline['evaluation_report']['training_completed'])
            self.assertEqual(pipeline['evaluation_report']['source_training_outcome'], 'invalid_observation')
            observed_pairs.update((name, *pair) for pair in expected)
        self.assertEqual(len(observed_pairs), 80)

    def test_all_figure_files_have_full_overviews_and_readable_native_zoom(self):
        from PIL import Image
        for row in load(self.report/'manifest.json')['models']:
            folder = self.report/row['name']/'evaluation'
            for figure in load(folder/'manifest.json')['figures']:
                self.assertTrue(any(v['time_view'] == 'overview' for v in figure['views']))
                self.assertTrue(any(v['time_view'] != 'overview' for v in figure['views']))
                for view in figure['views']:
                    self.assertFalse(view['downsampling'])
                    if view['time_view'] != 'overview':
                        self.assertGreaterEqual(view['minimum_native_tick_pixels_on_zoom'], 8)
                    png, svg, pdf = (folder/p for p in view['files'])
                    with Image.open(png) as image:
                        self.assertEqual(image.size, (1920, 960))
                    text = svg.read_text()
                    self.assertIn('Actual shared input', text)
                    self.assertIn('Stopped Train: invalid_observation', text)
                    self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))

    def test_complete_cache_hashes_no_lt_scope_and_no_training_or_manual_acceptance_claim(self):
        manifest = load(self.report/'manifest.json')
        self.assertEqual(manifest['physics_profile'], 'stock-four-input-NSPNeuronGen-without-LTMembrane')
        self.assertTrue(manifest['diagnostic_only'])
        for field in ('training_completed', 'calibration_performed', 'historical_presentation_reproduced',
                      'visual_acceptance_complete'):
            self.assertFalse(manifest[field])
        self.assertIsNone(manifest['scientific_verdict'])
        for name, digest in load(self.report/'SHA256SUMS.json').items():
            self.assertEqual(hashlib.sha256((self.report/name).read_bytes()).hexdigest(), digest)
        for row in manifest['models']:
            rendered = load(self.report/row['name']/'manifest.json')
            self.assertTrue(rendered['diagnostic_only'])
            self.assertFalse(rendered['training_completed'])
            self.assertFalse(rendered['visual_acceptance_complete'])
            self.assertIsNone(rendered['scientific_verdict'])
