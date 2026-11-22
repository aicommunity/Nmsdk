"""Pre-execution protocol/identity checks against the actual frozen DATA case."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_physical_foil_study import condition, declare_job, declare_trials
from ..native_evidence import EvidenceError, load


class FrozenPhysicalFoilDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=Path(os.environ['TIMELEARNER_FOIL_SOURCE'])
        cls.original=load(source/'input/job.json')
        cls.runtime=load(source/'process/runtime.json')
        cls.threshold=load(source/'run-manifest.json')['analysis']['metrics']['effective_threshold']

    def declaration(self):
        return dict(threshold=self.threshold,native_memory_bytes=2*1024**3,maximum_native_wall_seconds=7200)

    def test_real_source_produces_26_unseen_foils_and_middle_target(self):
        job,design=declare_job(self.original,'foil-design-check/a1')
        self.assertEqual(len(job['trials']),27)
        self.assertEqual(design['new_foil_trials'],26)
        self.assertEqual(design['target_position'],13)
        self.assertEqual(job['trials'][0]['pattern_isi'],[.01,.04,.08,.12])
        self.assertEqual(job['trials'][-1]['pattern_isi'],[.01,.12,.24,.36])
        self.assertEqual(job['trials'][13]['label'],'target')
        self.assertEqual(job['trials'][0]['label'],'foil')
        prior={t['pattern_hash'] for t in self.original['trials']}
        self.assertFalse({t['pattern_hash'] for t in job['trials'] if t['label']=='foil'} & prior)
        self.assertEqual(job['source_model_data'],self.original['source_model_data'])
        self.assertEqual(job['criterion'],self.original['criterion'])
        self.assertTrue(all(t['duration']==2 and t['maximum_samples']==4005 and
                            t['reset_policy']=='reset_per_trial' for t in job['trials']))

    def test_attempt_and_executable_path_do_not_change_condition(self):
        first,design=declare_job(self.original,'foil-design-check/a1')
        second,other_design=declare_job(self.original,'unrelated-attempt-name/a2')
        runtime=deepcopy(self.runtime)
        runtime['executable']['path']='/different/deployment/unchanged-executable'
        a=condition(first,design,self.runtime,self.declaration())
        b=condition(second,other_design,runtime,self.declaration())
        self.assertEqual(a['condition_fingerprint'],b['condition_fingerprint'])

    def test_a_changed_threshold_changes_condition(self):
        job,design=declare_job(self.original,'foil-design-check/a1')
        d=self.declaration();a=condition(job,design,self.runtime,d)
        d['threshold']+=.001;b=condition(job,design,self.runtime,d)
        self.assertNotEqual(a['condition_fingerprint'],b['condition_fingerprint'])

    def test_corrupt_labels_and_non_native_grid_are_rejected(self):
        broken=deepcopy(self.original);broken['trials'][0]['label']='foil'
        with self.assertRaises(EvidenceError):declare_trials(broken,'bad-labels')
        broken=deepcopy(self.original)
        broken['source_model_data']['configuration']['model']['frequency_hz']=2001
        with self.assertRaises(EvidenceError):declare_trials(broken,'bad-grid')
