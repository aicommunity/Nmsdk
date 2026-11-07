"""Audit actual native profile-intervention records and rehashed corruptions."""
from copy import deepcopy
import os
from pathlib import Path
import unittest
from ..native_characterization import audit_execution, audit_feedback_profile_import
from ..native_evidence import EvidenceError, load
from ..n1_protocol_robustness import _signed


@unittest.skipUnless(os.environ.get('TIMELEARNER_FEEDBACK_PROFILE_CORPUS'), 'requires actual twelve-probe profile study')
class FeedbackProfileExecutionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(os.environ['TIMELEARNER_FEEDBACK_PROFILE_CORPUS'])
        cls.rows=load(cls.root/'feedback-design.json')['rows']
        if len(cls.rows)!=12:raise AssertionError('requires both topologies, both presentations and three factors')

    def test_actual_complete_probes_and_exact_baseline_gate(self):
        for row in self.rows:
            result=audit_execution(self.root/'runs'/row['name']/'native')
            self.assertEqual(result['execution'],'completed');self.assertTrue(result['observation_complete'])
            self.assertFalse(result['training_started']);self.assertIsNone(result['evaluation_verdict'])
        checks=load(self.root/'analysis.json')['baseline_checks']
        self.assertEqual(len(checks),4)
        self.assertTrue(all(row['exact_waveform_reproduced'] for row in checks))

    def test_rehashed_source_profile_image_and_history_corruption_is_rejected(self):
        for row in self.rows:
            if row['factor']=='original':continue
            native=self.root/'runs'/row['name']/'native'
            job=load(native/'job.json');record=load(native/'source-import.json');candidate=load(native/'initial-state.json')['identity']
            audit_feedback_profile_import(job,record,candidate)
            for factor in ('source','gain','dataset','history','images'):
                bad=deepcopy(record)
                if factor=='source':bad['source_stopped_sha256']='0'*64
                elif factor=='gain':bad['feedback_gain']=1.+bad['feedback_gain']
                elif factor=='dataset':bad['dataset_identity']={}
                elif factor=='history':bad['controller_history_copied']=True
                else:bad['image_definitions_fingerprint']='0'*64
                with self.subTest(name=row['name'],factor=factor),self.assertRaises(EvidenceError):
                    audit_feedback_profile_import(job,_signed(bad),candidate)
