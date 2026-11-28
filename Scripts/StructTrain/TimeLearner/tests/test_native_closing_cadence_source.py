"""Use the retained eight-response native source, including its closing tail."""
from copy import deepcopy
import os
from pathlib import Path
import unittest

from ..frozen_fourth_pulse_history import declare_job
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_execution


class NativeClosingCadenceSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = Path(os.environ['TIMELEARNER_NATIVE_CLOSING_SOURCE'])
        cls.source = load(cls.native/'job.json')
        model = cls.source['source_model_data']
        cls.audit = audit_execution('physical-model-evaluate', cls.native,
                                    cls.source, (model,))

    def test_real_source_is_complete_and_admitted_without_changing_its_windows(self):
        original = self.source
        before = deepcopy(original)
        self.assertEqual([t['duration'] for t in original['trials']], [2.]*7+[2.4905])
        self.assertTrue(self.audit['frozen_model_verified'])
        self.assertEqual(len(self.audit['metrics']['trials']), 8)
        self.assertEqual(self.audit['metrics']['validity'], 'valid')
        self.assertEqual({k:self.audit['metrics']['pooled_counts'][k]
                          for k in ('TP','FP','FN','TN')}, dict(TP=1,FP=1,FN=0,TN=6))
        for policy in ('reset_per_trial', 'preserve_neuron_dynamics'):
            job, design = declare_job(original, 'actual-closing-source-reference',
                fourth_from_first_ticks=960, reset_policy=policy)
            self.assertEqual(job['source_model_data'], original['source_model_data'])
            self.assertEqual(design['probe_position'], 5)
            self.assertTrue(design['reference_case'])
        self.assertEqual(original, before)

    def test_one_tick_change_in_the_actual_closing_source_is_rejected(self):
        broken = deepcopy(self.source)
        broken['trials'][-1]['duration'] -= .0005
        broken['trials'][-1]['maximum_samples'] -= 1
        broken['maximum_model_ticks'] -= 1
        broken.pop('sha256'); broken['sha256'] = sha(broken)
        with self.assertRaises(EvidenceError):
            declare_job(broken, 'shortened-closing-source', fourth_from_first_ticks=960,
                        reset_policy='preserve_neuron_dynamics')
