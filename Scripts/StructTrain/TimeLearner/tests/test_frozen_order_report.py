"""Render the actual closed baseline8/study56 cohort without another model run."""
import os
from pathlib import Path
import unittest

from ..frozen_order_reports import render_frozen_order
from ..native_evidence import load


class FrozenOrderReportTest(unittest.TestCase):
    def test_every_pattern_and_position_uses_common_native_soma_and_lt_views(self):
        from PIL import Image
        source = Path(os.environ['TIMELEARNER_FROZEN_ORDER_COMPLETED'])
        output = Path(os.environ['TMPDIR'])/'frozen-order-all-patterns-gallery'
        summary = render_frozen_order(source, output)
        self.assertEqual(summary['expected_trials'], 64)
        self.assertEqual([(p['name'], p['trials'], p['lt_trials']) for p in summary['phases']],
                         [('baseline', 8, 8), ('study', 56, 56)])
        self.assertFalse(summary['new_native_calculation'])
        self.assertFalse(summary['visual_acceptance_complete'])
        self.assertIsNone(summary['scientific_verdict'])
        for phase in summary['phases']:
            folder = output/phase['name']
            manifest = load(folder/'manifest.json')
            decisions = load(folder/'lt-decision-views.json')
            figures = [(f, folder) for f in manifest['figures']]
            figures += [(f, folder/f['folder']) for f in decisions['trials']]
            for figure, base in figures:
                views = figure['views']
                self.assertTrue(any(v['time_view'] == 'overview' for v in views))
                self.assertTrue(any(v['time_view'] != 'overview' and
                    v['minimum_native_tick_pixels_on_zoom'] >= 8 for v in views))
                self.assertTrue(all(not v['downsampling'] for v in views))
                for view in views:
                    with Image.open(base/view['files'][0]) as image:
                        self.assertEqual(image.size, (1920, 960))
