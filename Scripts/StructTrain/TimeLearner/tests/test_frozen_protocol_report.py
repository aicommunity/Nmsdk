"""Full native temporal plots for all 24 completed window/reset study trials."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recorded_diagnostic_matrix import report_matrix
from .closed_protocol_fixture import verify_closed_protocol_fixture


class FrozenProtocolReportTest(unittest.TestCase):
    def test_all_three_complete_conditions_have_native_scale_temporal_views(self):
        from PIL import Image
        verify_closed_protocol_fixture()
        primary=Path(os.environ['TIMELEARNER_FROZEN_PROTOCOL_PRIMARY'])
        controller=Path(os.environ['TIMELEARNER_FROZEN_PROTOCOL_CONTROLLER'])
        runtime=Path(os.environ['TIMELEARNER_FROZEN_PROTOCOL_RUNTIME'])/'runtime.json'
        output=Path(os.environ['TMPDIR'])/'frozen-protocol-gallery'
        result=report_matrix(primary,controller,runtime,output)
        self.assertEqual(result['analysis']['trials'],24)
        self.assertFalse(result['analysis']['training_completed'])
        self.assertIsNone(result['scientific_verdict'])
        conditions={row['name']:row for row in result['analysis']['models']}
        self.assertEqual(set(conditions),{'long-reset','continuous','long-continuous'})
        total=0
        for name,row in conditions.items():
            self.assertEqual(row['trial_count'],8)
            self.assertEqual(row['metrics']['pooled_counts']['targets'],1)
            self.assertEqual(row['metrics']['pooled_counts']['foils'],7)
            self.assertEqual(row['metrics']['invalid_trial_ids'],[])
            gallery=output/name/'evaluation'
            manifest=load(gallery/'manifest.json')
            self.assertEqual(manifest['expected_trial_soma_pairs'],8)
            self.assertEqual(manifest['observed_trial_soma_pairs'],8)
            self.assertEqual(manifest['missing_observation_ids'],[])
            self.assertFalse(manifest['visual_acceptance_complete'])
            for figure in manifest['figures']:
                self.assertTrue(any(view['time_view'] != 'overview' and
                    view['minimum_native_tick_pixels_on_zoom'] >= 8 for view in figure['views']))
                for view in figure['views']:
                    self.assertFalse(view['downsampling'])
                    self.assertEqual(len(view['files']),3)
                    for file in view['files']:
                        self.assertTrue((gallery/file).is_file())
                    with Image.open(gallery/view['files'][0]) as image:
                        self.assertEqual(image.size,(1920,960))
            total+=len(manifest['figures'])
        self.assertEqual(total,24)
        verify_closed_protocol_fixture()
