"""Explicit reanalysis of real archived native Train data, without model runs."""
from copy import deepcopy
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from ..__main__ import main
from ..native_calibration_worker import _signed
from ..native_evidence import EvidenceError, load
from ..native_pipeline_worker import audit_run_manifest


ADAPTER = 'training-v3-no-capacitance-history'


class HistoricalPipelineAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_HISTORICAL_PIPELINE_PRIMARY')
        if not value:
            raise unittest.SkipTest('requires actual immutable coordinator corpus with auditor3 Train receipts')
        cls.source = Path(value)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='tl-historical-analysis-')
        self.addCleanup(temporary.cleanup)
        self.temporary = Path(temporary.name)

    def manifest(self, name='Classic-v1', *, copied=False):
        original = self.source/name/'runs/pipeline/phases/train'
        if copied:
            destination = self.temporary/name
            shutil.copytree(original, destination, symlinks=True)
            return destination/'run-manifest.json'
        return original/'run-manifest.json'

    def write(self, path, record):
        record = deepcopy(record)
        record.pop('sha256')
        path.write_text(json.dumps(_signed(record)), encoding='utf-8')

    def test_completed_classic_branch_and_wire_versions_require_explicit_adapter(self):
        for name in ('Classic-v1', 'Classic-v2', 'Branch-v1', 'Branch-v2'):
            with self.subTest(case=name):
                path = self.manifest(name)
                before = path.read_bytes()
                with self.assertRaisesRegex(EvidenceError, 'pipeline_run_analysis_changed'):
                    audit_run_manifest(path)
                result = audit_run_manifest(path, historical_analysis=ADAPTER)
                self.assertEqual(result['historical_analysis_adapter'], ADAPTER)
                self.assertTrue(result['run_evidence_consistent'])
                self.assertFalse(result['native_execution_verified'])
                self.assertIsNone(result['evaluation_verdict'])
                self.assertEqual(path.read_bytes(), before)

    def test_stopped_training_keeps_its_original_outcome_without_certificate(self):
        for name in ('Classic-N0', 'Classic-N1', 'Branch-N0', 'Branch-N1'):
            with self.subTest(case=name):
                path = self.manifest(name)
                saved = load(path)
                self.assertFalse(saved['analysis']['completed_boundary'])
                self.assertFalse(saved['analysis']['training_audit']['certificate_present'])
                result = audit_run_manifest(path, historical_analysis=ADAPTER)
                self.assertIsNone(result['evaluation_verdict'])
                self.assertEqual(load(path), saved)

    def test_public_cli_exposes_adapter_and_retains_unverified_native_execution(self):
        path = self.manifest()
        text = io.StringIO()
        with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
            code = main(['analyze', str(path), '--format', 'pipeline-run',
                         '--historical-analysis', ADAPTER])
        self.assertEqual(code, 0, text.getvalue())
        record = json.loads(text.getvalue())
        self.assertIn(ADAPTER, text.getvalue())
        self.assertIsNone(record['evaluation_verdict'])

    def test_adapter_cannot_be_applied_to_another_format(self):
        text = io.StringIO()
        with contextlib.redirect_stdout(text), contextlib.redirect_stderr(text):
            code = main(['analyze', str(self.manifest()), '--format', 'learned-solo',
                         '--historical-analysis', ADAPTER])
        self.assertEqual(code, 2, text.getvalue())
        self.assertIn('historical_analysis_is_only_for_pipeline_run', text.getvalue())

    def test_unknown_and_noninteger_archived_auditor_versions_are_rejected(self):
        path = self.manifest(copied=True)
        saved = load(path)
        for value in (2, 4, 5, 99, 3.0, True, '3'):
            with self.subTest(version=value):
                changed = deepcopy(saved)
                changed['analysis']['training_audit']['auditor_version'] = value
                self.write(path, changed)
                with self.assertRaises(EvidenceError):
                    audit_run_manifest(path, historical_analysis=ADAPTER)

    def test_exact_primary_count_and_model_identity_are_not_projected(self):
        path = self.manifest(copied=True)
        saved = load(path)
        for key, value in (('exact', False), ('primary_trials', 0), ('model_revision', 'changed')):
            with self.subTest(field=key):
                changed = deepcopy(saved)
                changed['analysis']['training_audit'][key] = value
                self.write(path, changed)
                with self.assertRaises(EvidenceError):
                    audit_run_manifest(path, historical_analysis=ADAPTER)

    def test_missing_capacitance_or_unknown_analysis_fields_are_rejected(self):
        path = self.manifest(copied=True)
        saved = load(path)
        changed = deepcopy(saved)
        changed['analysis']['training_audit'].pop('capacitance_state')
        self.write(path, changed)
        with self.assertRaises(EvidenceError):
            audit_run_manifest(path, historical_analysis=ADAPTER)
        for key in ('capacitance_history', 'unknown_field'):
            changed = deepcopy(saved)
            changed['analysis']['training_audit'][key] = None
            self.write(path, changed)
            with self.subTest(field=key), self.assertRaises(EvidenceError):
                audit_run_manifest(path, historical_analysis=ADAPTER)

    def test_stopped_and_completed_statuses_cannot_be_promoted(self):
        path = self.manifest('Classic-N0', copied=True)
        saved = load(path)
        for key, value in (('completed_boundary', True), ('training_outcome', 'exact')):
            changed = deepcopy(saved)
            changed['analysis'][key] = value
            self.write(path, changed)
            with self.subTest(field=key), self.assertRaises(EvidenceError):
                audit_run_manifest(path, historical_analysis=ADAPTER)

    def test_old_v2_adapter_does_not_accept_v3_record(self):
        with self.assertRaises(EvidenceError):
            audit_run_manifest(self.manifest(), historical_analysis='learned-v2-no-capacitance')

    def test_runtime_identity_changes_are_rejected_before_analysis_projection(self):
        path = self.manifest(copied=True)
        saved = load(path)
        saved['runtime_fingerprint'] = '0'*64
        self.write(path, saved)
        with self.assertRaises(EvidenceError):
            audit_run_manifest(path, historical_analysis=ADAPTER)

    def test_modified_primary_model_is_rejected(self):
        path = self.manifest(copied=True)
        model = path.parent/'native/train_learned_state.json'
        model.write_bytes(model.read_bytes()+b'\n')
        with self.assertRaises(EvidenceError):
            audit_run_manifest(path, historical_analysis=ADAPTER)

    def test_unknown_adapter_is_rejected(self):
        with self.assertRaisesRegex(EvidenceError, 'unknown_pipeline_historical_adapter'):
            audit_run_manifest(self.manifest(), historical_analysis='any-version')
