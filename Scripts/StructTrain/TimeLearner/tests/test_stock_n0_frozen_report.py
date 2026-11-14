"""All eight actual stopped N0 responses, without another model execution."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load, require
from ..reports import render_diagnostic_evaluation


class StockN0FrozenReportTest(unittest.TestCase):
    def test_original_matrix_all_somas_and_readable_native_zoom(self):
        from PIL import Image

        source = Path(os.environ['TIMELEARNER_STOCK_N0_FROZEN_REPORT_RUN']).resolve(strict=True)
        run = load(source/'run-manifest.json')
        require(run['operation'] == 'diagnostic-evaluate' and
                (run['execution'], run['validity']) == ('completed', 'valid'),
                'n0_report_requires_completed_diagnostic')
        actual = run['analysis']['metrics']
        self.assertEqual(len(actual['trials']), 8)
        self.assertTrue(actual['diagnostic_only'])
        self.assertFalse(actual['training_completed'])
        self.assertEqual(actual['effective_threshold'], 100.)
        self.assertIsNone(actual['evaluation_verdict'])
        output = Path(os.environ['TMPDIR']).resolve(strict=True)/'stock-n0-frozen-gallery'
        result = render_diagnostic_evaluation(source/'native/evaluation.json',
            source/'native/model.json', source/'input/source/train_stopped_state.json', output)
        manifest = load(output/'manifest.json')
        self.assertEqual(load(output/'analysis.json'), actual)
        self.assertEqual(manifest['missing_observation_ids'], [])
        self.assertEqual(len(manifest['declared_trials']), 8)
        self.assertTrue(all(t['complete'] and t['sample_count'] > 0
                            for t in manifest['declared_trials']))
        self.assertEqual(result['trial_soma_pairs'], manifest['expected_trial_soma_pairs'])
        self.assertEqual(manifest['expected_trial_soma_pairs'], 32)
        self.assertEqual(len(manifest['figures']), 32)
        self.assertEqual({f['sample_id'] for f in manifest['figures']},
                         {t['sample_id'] for t in actual['trials']})
        self.assertFalse(manifest['visual_acceptance_complete'])
        for figure in manifest['figures']:
            self.assertTrue(any(v['time_view'] == 'overview' for v in figure['views']))
            self.assertTrue(any(v['time_view'] != 'overview' and
                v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in figure['views']))
            for view in figure['views']:
                self.assertFalse(view['downsampling'])
                with Image.open(output/view['files'][0]) as image:
                    self.assertEqual(image.size, (1920, 960))
                self.assertTrue((output/view['files'][1]).is_file())
                self.assertTrue((output/view['files'][2]).read_bytes().startswith(b'%PDF-'))
