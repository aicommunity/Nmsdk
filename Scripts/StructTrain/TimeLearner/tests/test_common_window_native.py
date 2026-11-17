"""Reaudit complete real frozen runs before common-prefix/tail analysis."""
import json
import os
from pathlib import Path
import unittest

from ..common_window_analysis import compare_diagnostic_runs
from ..native_evidence import load


class CommonWindowNativeTest(unittest.TestCase):
    def test_real_four_condition_study_keeps_complete_original_verdicts(self):
        manifest_list=load(Path(os.environ['TIMELEARNER_COMMON_WINDOW_MANIFESTS']))
        self.assertEqual(set(manifest_list),{'baseline2','reset4','continuous2','continuous4'})
        result=compare_diagnostic_runs(manifest_list,2.)
        self.assertEqual(len(result['comparisons']),3)
        self.assertIsNone(result['scientific_verdict'])
        self.assertFalse(result['training_completed'])
        for condition,path in manifest_list.items():
            metrics=load(Path(path))['analysis']['metrics']
            self.assertEqual(result['full_window_counts'][condition],metrics['pooled_counts'])
        for comparison in result['comparisons']:
            self.assertEqual(len(comparison['trials']),8)
            self.assertEqual({row['sample_id'] for row in comparison['trials']},
                             {'phasea-row-'+str(i) for i in range(8)})
            self.assertTrue(all(row['compared_samples']==4001 for row in comparison['trials']))
        output=Path(os.environ['TMPDIR'])/'common-window-comparison.json'
        with output.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
