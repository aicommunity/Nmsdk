"""Production preparation on actual closed Train metadata and recorded DATA.

No Native model is calculated. Fixtures must be original worker artifacts;
these checks do not certify the later cap24 projection/import/evaluation.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError,load
from ..model_identity import canonical_model_sha256 as sha
from ..prepared_physical_evaluation import evaluation_limits
from ..windows_closed_training_recognition import (validate_request,validate_source_metadata,
                                                   evaluation_job,evaluation_condition)


class ActualClosedTrainingRecognition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=load(Path(os.environ['TIMELEARNER_CLOSED_TRAIN_METADATA']))
        cls.model=load(Path(os.environ['TIMELEARNER_PHYSICAL_SOURCE_MODEL']))
        cls.runtime=load(Path(cls.fixture['runtime_record']['path']))
        m=cls.fixture
        cls.base=dict(kind='timelearner_windows_closed_training_recognition',schema_version=1,
            job_id='closed-training-actual-fixture',python_root='a'*40,
            source_case=m['case_spec_record'],source_job=m['job_record'],source_full_audit=m['full_primary_audit_record'],
            runtime_manifest=m['runtime_record'],stimulus_source=m['stimulus_source'],
            predecessors=[dict(request=m['training_control_request'],owner=m['training_owner']),
                          dict(request=m['predecessor_request'],owner=m['predecessor_owner'])],
            expected_job_sha256=m['job']['sha256'],maximum_wait_seconds=60000,maximum_whole_seconds=108000,
            preparation_wall_seconds=3600,native_evaluation_wall_seconds=5400)
        cls.stimulus=dict(job=dict(trials=m['stimuli'],criterion=m['criterion']))

    def request(self):return deepcopy(self.base)

    def job(self, q=None, stimulus=None):
        return evaluation_job(q or self.request(),self.fixture['job'],self.model,
                              stimulus or self.stimulus,'baseline')

    def test_actual_closed_metadata_preserves_measured_terminal_and_budget_outcome(self):
        q=self.request();self.assertEqual(validate_request(q),self.base)
        m=self.fixture;r=validate_source_metadata(q,m['case_spec'],m['job'],m['full_primary_audit'],m['execution'])
        self.assertEqual(r['model_revision'],m['execution']['model_revision'])
        self.assertEqual(r['training_outcome'],'budget_exhausted');self.assertIs(r['completed_boundary'],False)
        self.assertEqual(r['package']['path'],'train_stopped_state.json')

    def test_foreign_or_modified_training_job_cannot_use_the_old_audit(self):
        m=self.fixture;job=deepcopy(m['job']);job['configuration']['search']['maximum_candidates_per_input']+=1
        job['sha256']=sha({k:v for k,v in job.items()if k!='sha256'})
        with self.assertRaises(EvidenceError):
            validate_source_metadata(self.request(),m['case_spec'],job,m['full_primary_audit'],m['execution'])

    def test_changed_terminal_graph_or_outcome_is_rejected(self):
        m=self.fixture
        for key,value in [('model_revision','0'*64),('training_outcome','exact')]:
            execution=deepcopy(m['execution']);execution[key]=value
            execution['sha256']=sha({k:v for k,v in execution.items()if k!='sha256'})
            with self.subTest(key=key),self.assertRaises(EvidenceError):
                validate_source_metadata(self.request(),m['case_spec'],m['job'],m['full_primary_audit'],execution)

    def test_outer_completed_flag_cannot_relabel_a_stopped_package(self):
        m=self.fixture;execution=deepcopy(m['execution']);proof=deepcopy(m['full_primary_audit'])
        execution['completed_boundary']=proof['completed_boundary']=True
        execution['sha256']=sha({k:v for k,v in execution.items()if k!='sha256'})
        with self.assertRaises(EvidenceError):
            validate_source_metadata(self.request(),m['case_spec'],m['job'],proof,execution)

    def test_hidden_factors_and_boolean_budgets_or_owners_are_rejected(self):
        for key in ('threshold','new_Train','normalization','reference_amplitudes'):
            q=self.request();q[key]=1
            with self.subTest(key=key),self.assertRaises(EvidenceError):validate_request(q)
        for key in ('maximum_wait_seconds','maximum_whole_seconds','preparation_wall_seconds','native_evaluation_wall_seconds'):
            q=self.request();q[key]=True
            with self.subTest(key=key),self.assertRaises(EvidenceError):validate_request(q)
        q=self.request();q['predecessors'][0]['owner']['pid']=True
        with self.assertRaises(EvidenceError):validate_request(q)

    def test_partial_windows_and_changed_training_target_are_rejected(self):
        for key,value in [('duration',1.5),('maximum_samples',1000),('reset_policy','preserve_neuron_dynamics')]:
            stimulus=deepcopy(self.stimulus);stimulus['job']['trials'][1][key]=value
            with self.subTest(key=key),self.assertRaises(EvidenceError):self.job(stimulus=stimulus)
        stimulus=deepcopy(self.stimulus);target=next(r for r in stimulus['job']['trials']if r['label']=='target')
        target['pattern_isi']=[.01,.16,.16,.16];target['pattern_hash']=sha(target['pattern_isi'])
        with self.assertRaises(EvidenceError):self.job(stimulus=stimulus)

    def test_actual_DATA_job_keeps_all_eight_declared_trials_and_frozen_physics(self):
        before=sha(self.model);stimulus=deepcopy(self.stimulus);job=self.job()
        self.assertEqual(len(job['trials']),8);self.assertEqual(job['source_model_data'],self.model)
        self.assertEqual(job['maximum_model_ticks'],32032)
        self.assertEqual(self.stimulus,stimulus);self.assertEqual(sha(self.model),before)
        self.assertTrue(all(r['run_id']==job['run_id']and r['trial_id'].startswith(job['run_id']+'/')for r in job['trials']))

    def test_target_can_be_fourth_without_retargeting_the_model(self):
        stimulus=deepcopy(self.stimulus);rows=stimulus['job']['trials'];target=next(r for r in rows if r['label']=='target')
        rows.remove(target);rows.insert(3,target);job=self.job(stimulus=stimulus)
        self.assertEqual([r['label']for r in job['trials']].index('target'),3)
        self.assertEqual(job['source_model_data'],self.model)

    def plan(self, version=1):
        q=self.request();return dict(kind='timelearner_prepared_physical_evaluation_plan',schema_version=version,
            job_id='actual-job',source_data={'sha256':sha(self.model)},runtime_manifest=q['runtime_manifest'],
            sdk_source=self.fixture['case_spec']['sdk_source'],worker_origin={'root_commit':'a'*40},job=self.job())

    def test_legacy_limits_are_unchanged_and_cannot_hide_a_new_budget(self):
        plan=self.plan();self.assertEqual(evaluation_limits(plan),dict(memory_bytes=8*1024**3,maximum_wall_seconds=3600))
        plan['execution_limits']=dict(memory_bytes=8*1024**3,maximum_wall_seconds=5400)
        with self.assertRaises(EvidenceError):evaluation_limits(plan)

    def test_explicit_limits_reach_preparation_without_boolean_or_unknown_values(self):
        plan=self.plan(2)
        with self.assertRaises(EvidenceError):evaluation_limits(plan)
        plan['execution_limits']=dict(memory_bytes=8*1024**3,maximum_wall_seconds=5400)
        self.assertEqual(evaluation_limits(plan),plan['execution_limits'])
        for key,value in [('maximum_wall_seconds',True),('memory_bytes',True),('memory_bytes',64*1024**3)]:
            changed=deepcopy(plan);changed['execution_limits'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(EvidenceError):evaluation_limits(changed)

    def test_condition_ignores_attempt_identity_and_tracks_actual_native_budget(self):
        q=self.request();job=self.job(q);first=evaluation_condition(q,job,self.runtime)
        changed=deepcopy(q);changed['job_id']='another-attempt'
        second=evaluation_condition(changed,self.job(changed),self.runtime)
        self.assertEqual(first,second)
        changed=deepcopy(q);changed['native_evaluation_wall_seconds']=7200
        third=evaluation_condition(changed,job,self.runtime)
        self.assertNotEqual(first['fingerprint'],third['fingerprint'])
        policy=third['artifacts']['execution_policy']['payload']
        self.assertEqual(policy['native_wall_seconds'],7200)


if __name__=='__main__':unittest.main()
