"""Admission controls from actual archived stopped candidates; no fake Train."""
from copy import deepcopy
import os
import unittest
from .test_single_pulse_job import SinglePulseJobTest
from ..native_characterization import prepare_feedback_profile_job, validate_job
from ..native_evidence import EvidenceError
from ..n1_protocol_robustness import _signed


@unittest.skipUnless(os.environ.get('TIMELEARNER_STOCK_WAVE_SOURCE'), 'requires archived native stopped models')
class FeedbackProfileJobTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SinglePulseJobTest.setUpClass.__func__(cls)
    def test_profile_builder_preserves_source_physics_and_target_for_both_presentations(self):
        for case,index,_ in self.rows:
            for single in (False, True):
                for baseline,gain in ((True,2.),(False,0.)):
                    job=prepare_feedback_profile_job(case,index,'profile-admission',image_prefix='ProfileAdmission',
                        feedback_gain=gain,baseline_reconstruction=baseline,single_pulse=single)
                    validate_job(job)
                    self.assertEqual(job['schema_version'],5)
                    self.assertEqual(job['source_stopped'],case[0])
                    self.assertEqual(job['model'],case[0]['configuration']['model'])
                    self.assertEqual(job['stimulus_profile'],case[0]['configuration']['stimulus_profile'])
                    self.assertEqual(job['resistance_intervention'],[])
                    self.assertEqual(job['presentation']['kind'],'single_pulse_characterization' if single else 'native_burst')

    def test_profile_malformed_factors_and_mixed_edits_are_rejected(self):
        for case,index,_ in self.rows:
            job=prepare_feedback_profile_job(case,index,'profile-negative',image_prefix='ProfileAdmission',feedback_gain=0.)
            for key,value in [('image_prefix','A\n'),('image_prefix','../A'),('feedback_gain',-1.),
                              ('feedback_gain',True),('baseline_reconstruction',1),('kind','hot_patch')]:
                bad=deepcopy(job);bad['profile_intervention'][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(EvidenceError):validate_job(_signed(bad))
            bad=deepcopy(job);bad['resistance_intervention']=[{'input_index':index,'resistance':3e8}]
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))
            bad=deepcopy(job);bad['stimulus_profile']['amplitude']*=2
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))
            bad=deepcopy(job);bad['profile_intervention']['unknown']=True
            with self.assertRaises(EvidenceError):validate_job(_signed(bad))
