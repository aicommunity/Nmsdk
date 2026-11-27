"""A missing compact field cannot erase or replace original Train identity."""
import copy
import unittest

from ..audited_training_identity import compact_job_identity, LEGACY_BRANCH_KIND
from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError


def signed(value):
    return {**value, 'sha256': sha(value)}


class AuditedTrainingIdentity(unittest.TestCase):
    def documents(self):
        job = signed(dict(kind='timelearner_native_training_job', owner_class='NNeuronTimeLearnerBranch',
            configuration=dict(run_id='declared-Train', model=dict(branch=True))))
        execution = signed(dict(kind='timelearner_native_training_execution',
            job_sha256=job['sha256'], attempt_id='declared-Train',
            package_path='train_stopped_state.json', training_outcome='invalid_observation',
            completed_boundary=False, model_revision='model-before-Test'))
        compact = dict(kind=LEGACY_BRANCH_KIND, schema_version=1,
            source_package=dict(path='/frozen/native/train_stopped_state.json',size=1,sha256='0'*64),
            source_summary=dict(path='/frozen/native/train_stopped_summary.json',size=1,sha256='1'*64),
            training_outcome='invalid_observation', completed_boundary=False,
            terminal={}, historical={}, candidate_count=25, classification_performed=False,
            scientific_verdict=None)
        proof = dict(completed_boundary=False, training_outcome='invalid_observation',
            training_audit=dict(package_digest_verified=True, model_revision='model-before-Test',
                                training_outcome='invalid_observation'))
        return compact, job, execution, proof

    def resolve(self, docs):
        return compact_job_identity(*docs, docs[1]['sha256'])

    def test_recorded_legacy_schema_derives_identity_without_rewriting_or_completion(self):
        docs = self.documents(); before = copy.deepcopy(docs)
        result = self.resolve(docs)
        self.assertEqual(result['job_sha256'], docs[1]['sha256'])
        self.assertEqual(result['adapter'], 'legacy_branch_count24_v1_original_native_job_execution')
        self.assertFalse(result['training_completion_inferred'])
        self.assertFalse(result['native_import_verified'])
        self.assertEqual(docs, before)

    def test_existing_compact_identity_remains_required(self):
        docs = self.documents(); docs[0]['job_sha256'] = docs[1]['sha256']
        self.assertEqual(self.resolve(docs)['adapter'], 'compact_declared_job_sha256')
        docs[0]['job_sha256'] = '0'*64
        with self.assertRaisesRegex(EvidenceError, 'compact_job_changed'):self.resolve(docs)

    def test_unknown_missing_field_schemas_are_not_guessed(self):
        for patch in (dict(kind='future-reader'), dict(schema_version=2), dict(schema_version=True), dict(extra=1)):
            docs = self.documents(); docs[0].update(patch)
            with self.subTest(patch=patch), self.assertRaisesRegex(EvidenceError, 'unknown_missing_job_identity_schema'):
                self.resolve(docs)

    def test_unsigned_job_changes_and_other_execution_are_rejected(self):
        docs = self.documents(); docs[1]['configuration']['run_id'] = 'other-Train'
        with self.assertRaisesRegex(EvidenceError, 'digest_mismatch'):self.resolve(docs)
        docs = self.documents(); body={k:v for k,v in docs[2].items()if k!='sha256'}
        body['job_sha256']='0'*64;docs[2]=signed(body)
        with self.assertRaisesRegex(EvidenceError, 'original_job_changed'):self.resolve(docs)

    def test_legacy_adapter_cannot_promote_completion_or_classification(self):
        for patch in (dict(completed_boundary=True), dict(classification_performed=True), dict(scientific_verdict='PASS')):
            docs = self.documents();docs[0].update(patch)
            with self.subTest(patch=patch), self.assertRaisesRegex(EvidenceError, 'legacy_branch_scope_changed'):
                self.resolve(docs)

    def test_legacy_adapter_requires_matching_original_primary_audit(self):
        for key,value in [('package_digest_verified',False),('model_revision','other-model'),('training_outcome','exact')]:
            docs=self.documents();docs[3]['training_audit'][key]=value
            with self.subTest(key=key), self.assertRaisesRegex(EvidenceError, 'legacy_branch_primary_audit_changed'):
                self.resolve(docs)

    def test_legacy_package_and_summary_cannot_describe_different_sources(self):
        docs=self.documents();docs[0]['source_summary']['path']='/other/native/train_stopped_summary.json'
        with self.assertRaisesRegex(EvidenceError, 'legacy_branch_scope_changed'):self.resolve(docs)
        for key,value in [('size',True),('sha256','broken'),('path','../train_stopped_state.json')]:
            docs=self.documents();docs[0]['source_package'][key]=value
            with self.subTest(key=key), self.assertRaisesRegex(EvidenceError, 'source_record_changed'):
                self.resolve(docs)


if __name__ == '__main__':
    unittest.main()
