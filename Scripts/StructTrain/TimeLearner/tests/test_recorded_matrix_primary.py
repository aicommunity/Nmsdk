"""Compact primary boundaries and opt-in replay of real closed model data."""
import json
import os
from pathlib import Path
import tempfile
import unittest

from ..recorded_matrix_primary import audit_primary, create_primary


class RecordedMatrixPrimaryBoundsTest(unittest.TestCase):
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
