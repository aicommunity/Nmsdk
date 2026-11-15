"""Compact primary boundaries and opt-in replay of real closed model data."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ..recorded_matrix_primary import audit_primary, create_primary, report_primary


class RecordedMatrixPrimaryReportBoundsTest(unittest.TestCase):
    def test_report_cannot_replace_bundle_or_restore_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);(root/'input').mkdir()
            bundle = root/'input/bundle.json';bundle.write_bytes(b'{}')
            for output in (root/'input/report', root/'restored/report', root):
                with self.subTest(output=output), self.assertRaisesRegex(ValueError, 'report_overlaps_primary'):
                    report_primary(bundle, root/'restored', output)
            self.assertFalse((root/'restored').exists())

    def test_backend_failure_precedes_archive_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);(root/'input').mkdir()
            bundle = root/'input/bundle.json';bundle.write_bytes(b'{}')
            with patch('Scripts.StructTrain.TimeLearner.plotting.plotting_runtime',
                       side_effect=ValueError('test_backend_unavailable')), \
                 patch('Scripts.StructTrain.TimeLearner.recorded_matrix_primary.audit_primary') as audit:
                with self.assertRaisesRegex(ValueError, 'test_backend_unavailable'):
                    report_primary(bundle, root/'restored', root/'report')
                audit.assert_not_called()
            self.assertFalse((root/'restored').exists())
            self.assertFalse((root/'report').exists())


class RecordedMatrixPrimaryReportActualTest(unittest.TestCase):
    """Opt-in full production rendering from the published compact bundle only."""
    def test_published_bundle_renders_all_forty_trial_soma_pairs(self):
        root = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_BUNDLE'])
        temporary = Path(os.environ['TMPDIR'])
        result = report_primary(root/'bundle.json', temporary/'compact-report-restored',
                                temporary/'compact-report-gallery')
        self.assertEqual(result['analysis']['trials'], 16)
        self.assertEqual({r['name']: r['report']['trial_soma_pairs'] for r in result['reports']},
                         {'classic': 32, 'branch': 8})
        self.assertFalse(result['native_execution_attested'])
        self.assertFalse(result['visual_acceptance_complete'])
        self.assertIsNone(result['scientific_verdict'])
        for row in result['reports']:
            report = row['report']
            self.assertTrue(report['diagnostic_only'])
            self.assertFalse(report['training_completed'])
            self.assertIsNone(report['evaluation_verdict'])
        (temporary/'compact-report-readback.json').write_text(
            json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


class RecordedMatrixPrimaryBoundsTest(unittest.TestCase):
    def test_explicit_member_budget_remains_typed_and_bounded(self):
        for value in (True, 0, -1, 512*1024**2+1, float('inf')):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'member_limit'):
                audit_primary(Path('/not-read/bundle.json'), Path('/not-created/restored'),
                              maximum_member_bytes=value)

    def test_export_normalizes_parent_segments_before_overlap_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('source', 'controller', 'runtime', 'detour'):(root/name).mkdir()
            runtime = root/'runtime/runtime.json';runtime.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'output_overlaps_source'):
                create_primary(root/'source', root/'controller', runtime,
                               root/'detour/../source/new-bundle')
            self.assertFalse((root/'source/new-bundle').exists())

    def test_restore_never_writes_into_input_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);path = root/'bundle.json';path.write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError, 'restore_overlaps_bundle'):
                audit_primary(path, root/'restored')
            self.assertFalse((root/'restored').exists())

    def test_excessive_archive_is_refused_before_decompression(self):
        self.refused(dict(archive_bytes=128*1024**2+1, members={'x': dict(bytes=1)}, expanded_bytes=1), 'size_budget')

    def test_excessive_expansion_is_refused_before_decompression(self):
        self.refused(dict(archive_bytes=1, members={'x': dict(bytes=1)}, expanded_bytes=768*1024**2+1), 'size_budget')

    def test_member_total_must_match_declared_expansion(self):
        self.refused(dict(archive_bytes=1, members={'x': dict(bytes=1)}, expanded_bytes=2), 'member_budget')

    def test_large_individual_model_is_refused_before_decompression(self):
        size = 256*1024**2+1
        self.refused(dict(archive_bytes=1, members={'x': dict(bytes=size)}, expanded_bytes=size), 'member_budget')

    def refused(self, value, reason):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary);(root/'input').mkdir();path = root/'input/bundle.json'
            path.write_text(json.dumps(value), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, reason):audit_primary(path, root/'restored')
            self.assertFalse((root/'restored').exists())


class RecordedMatrixPrimaryActualTest(unittest.TestCase):
    def test_actual_models_and_all_sixteen_observations_rescore_from_compact_bundle(self):
        directory = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_PRIMARY'])
        controller = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_CONTROLLER'])
        runtime = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_RUNTIME'])/'runtime.json'
        temporary = Path(os.environ['TMPDIR']);output = temporary/'recorded-matrix-compact-primary'
        bundle = create_primary(directory, controller, runtime, output)
        result = audit_primary(output/'bundle.json', temporary/'recorded-matrix-compact-restored')
        self.assertEqual(result['trials'], 16)
        self.assertEqual({r['name'] for r in result['models']}, {'classic', 'branch'})
        self.assertTrue(result['diagnostic_only'])
        self.assertFalse(result['complete_runtime_directory'])
        self.assertFalse(result['native_execution_attested'])
        self.assertIsNone(result['scientific_verdict'])
        self.assertLessEqual(bundle['archive_bytes'], 128*1024**2)
        self.assertLess(bundle['expanded_bytes'], 768*1024**2)
        (temporary/'recorded-matrix-compact-readback.json').write_text(
            json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')


class RecordedMatrixPrimaryPortableTest(unittest.TestCase):
    """Replay using only the published bundle, without the M40 work directory."""
    def test_published_models_and_sixteen_trials_need_no_original_runtime_directory(self):
        root = Path(os.environ['TIMELEARNER_RECORDED_MATRIX_BUNDLE'])
        bundle = json.loads((root/'bundle.json').read_bytes())
        self.assertEqual(bundle['archive_bytes'], 28053768)
        self.assertEqual(bundle['archive_sha256'],
                         'd8ea0c4911f0114737d955a81261abba23a1f4e49858a08c8e4e2991a6755468')
        self.assertEqual(len(bundle['members']), 42)
        temporary = Path(os.environ['TMPDIR'])
        result = audit_primary(root/'bundle.json', temporary/'recorded-matrix-portable-restored')
        self.assertEqual(result['original_job_id'], 's11-recorded-n4-diagnostic16-m40-a2')
        self.assertEqual(result['trials'], 16)
        self.assertTrue(result['diagnostic_only'])
        self.assertFalse(result['complete_runtime_directory'])
        self.assertFalse(result['native_execution_attested'])
        self.assertIsNone(result['scientific_verdict'])
        rows = {r['name']: r for r in result['models']}
        self.assertEqual(set(rows), {'classic', 'branch'})
        self.assertEqual(rows['classic']['training_outcome'], 'invalid_observation')
        self.assertEqual(rows['branch']['training_outcome'], 'budget_exhausted')
        for row in rows.values():
            self.assertEqual({k: row['counts'][k] for k in ('TP', 'FP', 'FN', 'TN')},
                             dict(TP=0, FP=0, FN=1, TN=7))
        (temporary/'recorded-matrix-portable-readback.json').write_text(
            json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
