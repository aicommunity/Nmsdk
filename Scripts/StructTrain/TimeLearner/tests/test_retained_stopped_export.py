"""Audit an archived stopped export even when its producing job was interrupted.

The original execution failure remains a failure. Only the retained model DATA
and its embedded measurement history can pass this separate recovery audit.
"""
import json
import os
from pathlib import Path
import unittest

from ..collector_provenance import frozen_digest
from ..native_evidence import load, require
from ..stopped_evidence import audit_stopped_state, load_case


class RetainedStoppedExportTest(unittest.TestCase):
    def test_original_bytes_replay_without_recovering_execution_or_training_authority(self):
        root = Path(os.environ['TIMELEARNER_RETAINED_STOPPED_EXPORT'])
        expected = load(Path(os.environ['TIMELEARNER_RETAINED_STOPPED_EXPECTATIONS'])/'expected.json')
        require(set(expected) == {'kind', 'schema_version', 'state_file', 'bytes', 'sha256',
                                 'original_job', 'original_failure'}, 'retained_export_expectation_fields')
        require(expected['kind'] == 'timelearner_retained_stopped_export_expectations' and
                type(expected['schema_version']) is int and expected['schema_version'] == 1 and
                expected['state_file'] == 'train_stopped_state.json' and
                type(expected['original_job']) is str and bool(expected['original_job']) and
                type(expected['original_failure']) is str and bool(expected['original_failure']),
                'retained_export_expectation_scope')
        path = root/expected['state_file']
        before = frozen_digest(path, expected['bytes'])
        self.assertEqual({k: before[k] for k in ('bytes', 'sha256')},
                         {k: expected[k] for k in ('bytes', 'sha256')})
        package, summary, packets, traces = load_case(path)
        self.assertEqual(package['kind'], 'timelearner_stopped_state')
        self.assertIsNone(package['certificate'])
        result = audit_stopped_state(package, summary, packets, traces)
        self.assertTrue(result['package_digest_verified'])
        for key in ('native_import_verified', 'native_execution_verified', 'live_authority_restored'):
            self.assertIs(result[key], False)
        self.assertIsNone(result['evaluation_verdict'])
        self.assertEqual(frozen_digest(path, expected['bytes']), before)
        report = dict(kind='timelearner_retained_stopped_export_audit', schema_version=1,
            original_job=expected['original_job'], original_failure=expected['original_failure'],
            original_outcome_unchanged=True, source_file=before, data_audit=result,
            model_revision=package['model_revision'], parameters=package['trained_inputs'],
            training_outcome=package['training_outcome'], training_reason=package['reason'],
            certificate=None, classification_assessed=False, native_import_verified=False,
            native_execution_verified=False, scientific_verdict=None)
        output = Path(os.environ['TMPDIR'])/'retained-stopped-export-audit.json'
        output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
