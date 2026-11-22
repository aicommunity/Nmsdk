"""Render all actual fresh-model observations; negative science stays visible."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recorded_diagnostic_matrix import report_matrix


class FreshRecordedMatrixReportTest(unittest.TestCase):
    def test_baseline_and_actual_candidate_keep_all_eighty_trial_soma_pairs(self):
        from PIL import Image
        runtime=Path(os.environ['TIMELEARNER_FRESH_MATRIX_RUNTIME'])/'runtime.json'
        total=0
        for phase,counts in [('baseline',dict(TP=0,FP=0,FN=1,TN=7)),
                             ('candidate',dict(TP=1,FP=6,FN=0,TN=1))]:
            prefix='TIMELEARNER_FRESH_MATRIX_'+phase.upper()
            source=Path(os.environ[prefix+'_PRIMARY']);controller=Path(os.environ[prefix+'_CONTROLLER'])
            output=Path(os.environ['TMPDIR'])/('fresh-n4-'+phase+'-gallery')
            result=report_matrix(source,controller,runtime,output)
            self.assertEqual(result['analysis']['trials'],16)
            self.assertFalse(result['analysis']['training_completed'])
            self.assertIsNone(result['scientific_verdict'])
            for row in result['analysis']['models']:
                self.assertEqual(row['training_outcome'],'external_stop')
                self.assertEqual({k:row['metrics']['pooled_counts'][k] for k in counts},counts)
            for role,expected in [('classic',32),('branch',8)]:
                folder=output/role/'evaluation';manifest=load(folder/'manifest.json')
                self.assertEqual(manifest['expected_trial_soma_pairs'],expected)
                self.assertEqual(manifest['observed_trial_soma_pairs'],expected)
                self.assertEqual(manifest['missing_observation_ids'],[])
                self.assertEqual(len(manifest['figures']),expected)
                self.assertFalse(manifest['visual_acceptance_complete'])
                for figure in manifest['figures']:
                    views=figure['views']
                    self.assertTrue(any(v['time_view']=='overview' for v in views))
                    self.assertTrue(any(v['time_view']!='overview' and
                        v['minimum_native_tick_pixels_on_zoom']>=8 for v in views))
                    for view in views:
                        self.assertFalse(view['downsampling'])
                        self.assertGreater(view['end'],view['begin'])
                        self.assertEqual(len(view['files']),3)
                        with Image.open(folder/view['files'][0]) as image:self.assertEqual(image.size,(1920,960))
                total+=len(manifest['figures'])
        self.assertEqual(total,80)
