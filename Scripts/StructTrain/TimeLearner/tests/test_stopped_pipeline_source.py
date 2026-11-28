"""Admission of the real closed Branch/Rs Train, without repeating Train.

The fixture is the full preserved production run, not a synthetic training
package. Negative cases change private metadata; primary source files remain
unchanged. This suite grants no later import or classification verdict.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..model_identity import canonical_model_sha256 as sha
from ..native_evidence import EvidenceError, load
from ..runtime import file_record
from ..stopped_pipeline_source import closed_pipeline_source


class ActualStoppedPipelineSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ['TIMELEARNER_STOPPED_PIPELINE_PRIMARY']).resolve(strict=True)
        cls.manifest = load(cls.root/'run-manifest.json')
        cls.audit = cls.manifest['analysis']['training_audit']
        cls.execution = load(cls.root/'native/execution.json')
        cls.job = load(cls.root/'native/job.json')

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.native = self.directory/'native'
        self.native.mkdir()

    def write(self, path, value):
        value = deepcopy(value)
        value['sha256'] = sha({k:v for k,v in value.items() if k != 'sha256'})
        path.write_text(json.dumps(value, allow_nan=False)+'\n', encoding='utf-8')

    def metadata(self, manifest=None, execution=None):
        path = self.directory/'run-manifest.json'
        self.write(path, self.manifest if manifest is None else manifest)
        self.write(self.native/'execution.json', self.execution if execution is None else execution)
        return path

    def test_actual_Branch_Rs_primary_is_fully_reaudited_before_admission(self):
        self.assertIs(self.job['configuration']['model']['branch'], True)
        self.assertEqual(self.job['configuration']['model']['normalization'], 'N1')
        path = self.root/'run-manifest.json'
        before = file_record(path)
        result = closed_pipeline_source(path, self.root/'native', self.audit)
        self.assertTrue(result['full_primary_reaudited'])
        self.assertTrue(result['pipeline_evidence']['run_evidence_consistent'])
        self.assertFalse(result['pipeline_evidence']['native_execution_verified'])
        self.assertFalse(result['training_completed'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertEqual(result['source_package'], file_record(self.root/'native/train_stopped_state.json'))
        self.assertEqual(file_record(path), before)

    def test_a_manifest_cannot_admit_a_different_native_directory(self):
        with self.assertRaisesRegex(EvidenceError, 'actual_run_path'):
            closed_pipeline_source(self.root/'run-manifest.json', self.native, self.audit)

    def test_unknown_boolean_or_uncontained_manifest_is_rejected(self):
        for version in (True, 2, 3, 5, 99):
            m = deepcopy(self.manifest); m['schema_version'] = version
            with self.subTest(version=version):
                self.write(self.directory/'run-manifest.json', m)
                with self.assertRaisesRegex(EvidenceError, 'closed_contained_cold_train_required'):
                    closed_pipeline_source(self.directory/'run-manifest.json', self.native, self.audit)

    def test_a_completed_boundary_cannot_be_relabelled_as_stopped(self):
        m = deepcopy(self.manifest); m['analysis']['completed_boundary'] = True
        path = self.metadata(manifest=m)
        with self.assertRaisesRegex(EvidenceError, 'complete_original_audit_required'):
            closed_pipeline_source(path, self.native, self.audit)

    def test_a_different_saved_audit_is_not_evidence_for_this_run(self):
        a = deepcopy(self.audit); a['model_revision'] = '0'*64
        path = self.metadata()
        with self.assertRaisesRegex(EvidenceError, 'complete_original_audit_required'):
            closed_pipeline_source(path, self.native, a)

    def test_resigned_wrong_terminal_graph_job_or_outcome_is_rejected(self):
        for key, value in (('model_revision','0'*64), ('job_sha256','0'*64),
                           ('training_outcome','exact'), ('completed_boundary',True),
                           ('package_path','train_learned_state.json')):
            e = deepcopy(self.execution); e[key] = value
            path = self.metadata(execution=e)
            with self.subTest(field=key), self.assertRaisesRegex(EvidenceError, 'terminal_binding'):
                closed_pipeline_source(path, self.native, self.audit)

    def test_empty_or_boolean_package_size_is_rejected(self):
        for size in (0, True):
            e = deepcopy(self.execution)
            next(r for r in e['artifacts'] if r['path']=='train_stopped_state.json')['bytes'] = size
            path = self.metadata(execution=e)
            with self.subTest(size=size), self.assertRaisesRegex(EvidenceError, 'package_artifact'):
                closed_pipeline_source(path, self.native, self.audit)

    def test_missing_history_cannot_be_replaced_by_small_model_or_template(self):
        path = self.metadata()
        (self.native/'train_stopped_state.json').write_text('{}\n', encoding='utf-8')
        with self.assertRaisesRegex(EvidenceError, 'package_bytes_changed'):
            closed_pipeline_source(path, self.native, self.audit)


if __name__ == '__main__':
    unittest.main()
