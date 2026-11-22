"""Check the production preparer against an actual completed DATA replay.

No native model is run here. Legacy job equality covers the mechanical move
from the former case-specific operator; the new native transfer still has its
own all-eight waveform/event gate.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..prepared_physical_replay import prepare
from ..runtime import file_record


class ActualPhysicalReplayPreparationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((Path(os.environ['TIMELEARNER_ACTUAL_DATA_REPLAY_PREPARATION'])/'fixture.json').read_bytes())
        cls.base=Path('C:/Projects/TimeLearnerWorker').resolve(strict=True)
        if os.name!='nt' or cls.fixture['kind']!='timelearner_actual_data_replay_preparation_fixture':
            raise ValueError('actual_windows_DATA_fixture_required')

    def setUp(self):
        self.controls=tempfile.TemporaryDirectory(prefix='data-replay-preparation-test-',dir=self.base/'controls')
        self.jobs=tempfile.TemporaryDirectory(prefix='data-replay-preparation-test-',dir=self.base/'jobs')
        self.control=Path(self.controls.name).resolve(strict=True)
        self.job=Path(self.jobs.name).resolve(strict=True)
        self.assertTrue(self.control.is_relative_to(self.base/'controls'))
        self.assertTrue(self.job.is_relative_to(self.base/'jobs'))

    def tearDown(self):
        # Only these freshly created, scope-checked test directories are caches.
        self.assertEqual(self.control.parent,self.base/'controls')
        self.assertEqual(self.job.parent,self.base/'jobs')
        self.controls.cleanup();self.jobs.cleanup()

    def declaration(self):
        destination=self.control/'destination';destination.mkdir()
        return dict(kind='timelearner_physical_replay_preparation',schema_version=1,
            source_controls=self.fixture['source_controls'],export_controls=self.fixture['export_controls'],
            source_audit=self.fixture['source_audit'],destination=str(destination),
            inputs=str(self.job/'inputs'),output=str(self.job/'output'),run_id='actual-DATA-preparer-test',
            python_source=str(Path(__file__).resolve().parents[4]),python_root=self.fixture['python_root'])

    def test_matches_the_actual_legacy_DATA_job_after_identity_normalization(self):
        declaration=self.declaration()
        before=file_record(Path(self.fixture['legacy_job']))
        result=prepare(declaration)
        job=json.loads((Path(declaration['inputs'])/'job.json').read_bytes())
        legacy=json.loads(Path(self.fixture['legacy_job']).read_bytes())
        comparable=deepcopy(job);comparable['run_id']=legacy['run_id']
        for current,original in zip(comparable['trials'],legacy['trials']):
            current['run_id']=original['run_id'];current['trial_id']=original['trial_id']
        comparable['sha256']=sha({k:v for k,v in comparable.items() if k!='sha256'})
        self.assertEqual(comparable,legacy)
        self.assertEqual(file_record(Path(self.fixture['legacy_job'])),before)
        self.assertTrue(result['source_model_not_changed'])
        self.assertFalse(result['native_execution_started'])
        spec=json.loads((Path(declaration['destination'])/'specification.json').read_bytes())
        self.assertEqual(spec['resolved_job_sha256'],job['sha256'])
        self.assertEqual(spec['source_model_revision'],legacy['source_model_data']['model_revision'])
        self.assertEqual(len(spec['source_inventory']),9)

    def test_rejects_incomplete_source_audit_before_creating_trial_inputs(self):
        declaration=self.declaration()
        audit=json.loads(Path(self.fixture['source_audit']).read_bytes())
        audit['native_evidence']['frozen_model_verified']=False
        bad=self.control/'incomplete-audit.json';bad.write_text(json.dumps(audit),encoding='utf-8')
        declaration['source_audit']=str(bad)
        with self.assertRaisesRegex(ValueError,'physical_replay_preparation_requires_complete_source_audit'):
            prepare(declaration)
        self.assertFalse(Path(declaration['inputs']).exists())

    def test_rejects_a_different_export_SDK(self):
        declaration=self.declaration()
        spec=json.loads((Path(self.fixture['export_controls'])/'specification.json').read_bytes())
        spec['sdk_source']=declaration['python_source']
        other=self.control/'other-sdk';other.mkdir()
        (other/'specification.json').write_text(json.dumps(spec),encoding='utf-8')
        declaration['export_controls']=str(other)
        with self.assertRaisesRegex(ValueError,'physical_replay_preparation_sdk_mismatch'):
            prepare(declaration)
        self.assertFalse(Path(declaration['inputs']).exists())

    def test_rejects_changed_source_envelope_even_with_a_recomputed_envelope_digest(self):
        declaration=self.declaration()
        previous=json.loads((Path(self.fixture['source_controls'])/'specification.json').read_bytes())
        envelope=json.loads((Path(previous['inputs'])/'native-job-source.json').read_bytes())
        envelope['job']['run_id']+='/changed-after-native-execution'
        envelope['sha256']=sha({k:v for k,v in envelope.items() if k!='sha256'})
        changed=self.job/'changed-source-inputs';changed.mkdir()
        (changed/'native-job-source.json').write_text(json.dumps(envelope),encoding='utf-8')
        previous['inputs']=str(changed)
        other=self.control/'changed-controls';other.mkdir()
        (other/'specification.json').write_text(json.dumps(previous),encoding='utf-8')
        declaration['source_controls']=str(other)
        with self.assertRaisesRegex(ValueError,'physical_replay_preparation_source_request_bytes_changed'):
            prepare(declaration)
        self.assertFalse(Path(declaration['inputs']).exists())
