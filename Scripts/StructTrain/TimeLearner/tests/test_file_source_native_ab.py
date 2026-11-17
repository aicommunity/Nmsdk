"""Full-window comparison of four closed real native N4 cases, no model mocks."""
import json
import os
from pathlib import Path
import unittest

from ..closed_primary_bundle import verify_sources
from ..common_window_analysis import compare_diagnostic_runs
from ..native_data_checks import status
from ..native_evidence import load, require


class FileSourceNativeABTest(unittest.TestCase):
    def guard(self):
        names=('TIMELEARNER_AB_FIRST','TIMELEARNER_AB_FIRST_CONTROLLER',
               'TIMELEARNER_AB_REMAINING','TIMELEARNER_AB_REMAINING_CONTROLLER')
        roots={Path(os.environ[n]).resolve(strict=True) for n in names}
        collection=load(Path(os.environ['TIMELEARNER_AB_COLLECTION'])/'collection-manifest.json')
        require({Path(r['directory']).resolve(strict=True) for r in collection['roots']}==roots,
                'file_source_ab_collection_scope_changed')
        for name in ('TIMELEARNER_AB_FIRST_CONTROLLER','TIMELEARNER_AB_REMAINING_CONTROLLER'):
            observed=status(Path(os.environ[name]))
            require(observed['outer']['all_processes_closed'] and not observed['supervisor_live'],
                    'file_source_ab_owner_not_closed')
        require(load(Path(os.environ['TIMELEARNER_AB_FIRST'])/'terminal.json')['operation_passed'] is False,
                'file_source_ab_first_attempt_failure_lost')
        require(load(Path(os.environ['TIMELEARNER_AB_REMAINING'])/'terminal.json')['operation_passed'] is True,
                'file_source_ab_remaining_attempt_not_completed')
        return verify_sources(collection)

    def compare(self, topology):
        self.guard()
        first=Path(os.environ['TIMELEARNER_AB_FIRST'])
        remaining=Path(os.environ['TIMELEARNER_AB_REMAINING'])
        inline=(first if topology=='classic' else remaining)/(topology+'-inline/run-manifest.json')
        file=remaining/(topology+'-file/run-manifest.json')
        self.assertEqual(load(inline)['schema_version'],4)
        self.assertEqual(load(file)['schema_version'],5)
        self.assertEqual(load(inline)['runtime_fingerprint'],load(file)['runtime_fingerprint'])
        result=compare_diagnostic_runs({'inline':inline,'file':file},2.)
        self.assertEqual(result['full_window_counts']['inline'],result['full_window_counts']['file'])
        for metrics in result['full_window_counts'].values():
            self.assertEqual({k:metrics[k] for k in ('TP','FP','FN','TN')},dict(TP=1,FP=6,FN=0,TN=1))
        trials=result['comparisons'][0]['trials'];self.assertEqual(len(trials),8)
        for trial in trials:
            self.assertEqual(trial['compared_samples'],4001)
            # Cover the entire observation, not just a favorable prefix.
            self.assertEqual(trial['baseline']['observed_final_tick'],4000)
            self.assertEqual(trial['compared']['observed_final_tick'],4000)
            self.assertTrue(trial['prefix_numeric_samples_equal'],trial)
            self.assertTrue(trial['stimulus_ticks_equal'])
            self.assertTrue(trial['prefix_spike_ticks_equal'])
            self.assertEqual(trial['baseline']['tail_spike_ticks'],[])
            self.assertEqual(trial['compared']['tail_spike_ticks'],[])
        self.assertFalse(result['training_completed'])
        self.assertIsNone(result['scientific_verdict'])
        target=Path(os.environ['TMPDIR'])/(topology+'-file-source-comparison.json')
        with target.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
        self.guard()

    def test_classic_complete_native_response_and_model_equal(self):
        self.compare('classic')

    def test_branch_complete_native_response_and_model_equal(self):
        self.compare('branch')
