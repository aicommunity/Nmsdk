"""Admission boundaries using the real, preserved cold N0/N1 declarations.

The tiny closed-audit records here are input fixtures, not completed model
evidence. These tests do not produce a training certificate or classification.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..prepare_stopped_baseline import closed_count_source
from ..prepared_count_training import doubled_sweep_count_job
from ..runtime import file_record


class StoppedBaselineSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(os.environ['TIMELEARNER_TWO_SWEEP_SOURCE']).resolve(strict=True)
        cls.count=load(root/'count-job.json');cls.resistance=load(root/'resistance-job.json')

    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.native=self.root/'native';self.native.mkdir()

    def write(self,path,value):
        path.write_text(json.dumps(value,allow_nan=False)+'\n',encoding='utf-8')

    def case(self,sweeps):
        original=self.resistance if sweeps==1 else self.count
        job=deepcopy(self.count) if sweeps==1 else doubled_sweep_count_job(self.count,'source-admission-two-sweeps')
        original_path=self.root/'original.json';self.write(original_path,original)
        self.write(self.native/'job.json',job)
        execution=dict(job_sha256=job['sha256'],completed_boundary=False,training_outcome='budget_exhausted')
        self.write(self.native/'execution.json',execution)
        audit=dict(package_digest_verified=True,training_outcome='budget_exhausted',model_revision='a'*64)
        role='original_resistance_normalization_job' if sweeps==1 else 'original_cold_count_normalization_job'
        proof=dict(kind='timelearner_closed_matched_count_training_audit' if sweeps==1 else
            'timelearner_closed_doubled_count_training_audit',schema_version=1,native=str(self.native),
            source_package_full_decodes=1,original_outcome_unchanged=True,
            original_physics_target_tolerances_and_budgets_preserved=True,
            consumed_job_sha256=job['sha256'],consumed_job_file=file_record(self.native/'job.json'),
            execution_file=file_record(self.native/'execution.json'),
            full_primary_audit=dict(completed_boundary=False,training_outcome='budget_exhausted',training_audit=audit))
        proof[role]=file_record(original_path)
        return proof,audit

    def test_one_sweep_retains_original_kind_and_role(self):
        p,a=self.case(1);r=closed_count_source(p,self.native,a)
        self.assertEqual(r['maximum_sweeps'],1)
        self.assertEqual(r['proof_kind'],p['kind'])
        self.assertEqual(r['original_case_role'],'original_resistance_normalization_job')

    def test_two_sweeps_retains_separate_kind_and_cold_count_origin(self):
        p,a=self.case(2);before=deepcopy(p);r=closed_count_source(p,self.native,a)
        self.assertEqual(r['maximum_sweeps'],2);self.assertEqual(r['proof_kind'],p['kind'])
        self.assertEqual(r['original_case_role'],'original_cold_count_normalization_job')
        self.assertEqual(p,before)

    def test_renaming_one_sweep_proof_does_not_extend_its_budget(self):
        p,a=self.case(1);p['kind']='timelearner_closed_doubled_count_training_audit'
        with self.assertRaisesRegex(EvidenceError,'original_case_role_mismatch'):
            closed_count_source(p,self.native,a)

    def test_forged_role_and_kind_still_fail_actual_sweep_count(self):
        p,a=self.case(1);p['kind']='timelearner_closed_doubled_count_training_audit'
        p['original_cold_count_normalization_job']=p.pop('original_resistance_normalization_job')
        with self.assertRaisesRegex(EvidenceError,'proof_job_or_outcome_mismatch'):
            closed_count_source(p,self.native,a)

    def test_unknown_kind_and_boolean_schema_are_rejected(self):
        p,a=self.case(2)
        for key,value in [('kind','timelearner_closed_anything'),('schema_version',True)]:
            bad=deepcopy(p);bad[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(EvidenceError,'unknown_count_audit_protocol'):
                closed_count_source(bad,self.native,a)

    def test_a_completed_boundary_cannot_be_relabelled_as_stopped(self):
        p,a=self.case(2);p['full_primary_audit']['completed_boundary']=True
        with self.assertRaisesRegex(EvidenceError,'requires_complete_original_primary_audit'):
            closed_count_source(p,self.native,a)

    def test_partial_decode_or_changed_audit_is_not_complete_evidence(self):
        p,a=self.case(2)
        for value in (0,True,2):
            bad=deepcopy(p);bad['source_package_full_decodes']=value
            with self.subTest(value=value),self.assertRaisesRegex(EvidenceError,'requires_complete_original_primary_audit'):
                closed_count_source(bad,self.native,a)
        wrong=deepcopy(a);wrong['model_revision']='b'*64
        with self.assertRaisesRegex(EvidenceError,'requires_complete_original_primary_audit'):
            closed_count_source(p,self.native,wrong)

    def test_job_or_original_bytes_changed_after_audit_are_rejected(self):
        p,a=self.case(2);job=self.native/'job.json';job.write_bytes(job.read_bytes()+b' ')
        with self.assertRaisesRegex(EvidenceError,'audited_input_changed:consumed_job_file'):
            closed_count_source(p,self.native,a)
        p['consumed_job_file']=file_record(job)
        original=Path(p['original_cold_count_normalization_job']['path']);original.write_bytes(original.read_bytes()+b' ')
        with self.assertRaisesRegex(EvidenceError,'original_case_changed'):
            closed_count_source(p,self.native,a)

    def test_resigned_different_probe_budget_is_not_the_declared_case(self):
        p,a=self.case(2);job=load(self.native/'job.json')
        job['configuration']['search']['maximum_probes']+=1
        job['sha256']=sha({k:v for k,v in job.items()if k!='sha256'});self.write(self.native/'job.json',job)
        execution=load(self.native/'execution.json');execution['job_sha256']=job['sha256'];self.write(self.native/'execution.json',execution)
        p.update(consumed_job_sha256=job['sha256'],consumed_job_file=file_record(self.native/'job.json'),
                 execution_file=file_record(self.native/'execution.json'))
        with self.assertRaisesRegex(EvidenceError,'declared_cold_case_changed'):
            closed_count_source(p,self.native,a)


if __name__=='__main__':unittest.main()
