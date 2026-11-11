"""Actual stopped N4 Train package, audited CSVs and server-rendered figures."""
import hashlib
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_evidence import EvidenceError, load, require


class CompositeTrainingTemporalNativeTest(unittest.TestCase):
    def native(self):
        value = os.environ.get('TIMELEARNER_COMPOSITE_TRAIN_NATIVE')
        require(value is not None, 'actual_stopped_train_native_fixture_required')
        return Path(value).resolve(strict=True)

    def test_actual_failed_window_and_all_somas_controls_are_preserved(self):
        from PIL import Image
        native = self.native()
        output = Path(os.environ['TMPDIR'])/'classic-window-report'
        files = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in native.rglob('*') if p.is_file() and not p.is_symlink()}
        report = render(native, output, [12, 14, 18])
        self.assertEqual(report['package_audit']['training_outcome'], 'invalid_observation')
        self.assertEqual([g['ordinal'] for g in report['groups']], [12, 14, 18])
        self.assertEqual([g['selection']['geometry']['validity'] for g in report['groups']],
                         ['valid', 'missing', 'missing'])
        self.assertEqual(report['groups'][-1]['window_relative_seconds'], [.773, .813])
        self.assertEqual(len(report['figures']), 24)
        self.assertEqual({f['channel'] for f in report['figures']}, {0, 1, 2, 3})
        self.assertTrue(all(len(g['primary_references']) == 6 for g in report['groups']))
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertIsNone(report['scientific_verdict'])
        for figure in report['figures']:
            for filename in figure['files']:
                self.assertGreater((output/filename).stat().st_size, 100)
            with Image.open(output/figure['files'][0]) as picture:
                self.assertGreaterEqual(picture.width, 2800)
                self.assertGreaterEqual(picture.height, 2800)
        self.assertEqual(load(output/'manifest.json')['groups'], report['groups'])
        self.assertEqual(files, {p: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in files})

    def test_missing_group_refuses_output_after_actual_package_replay(self):
        output = Path(os.environ['TMPDIR'])/'missing-window-report'
        with self.assertRaisesRegex(EvidenceError, 'training_report_group_missing'):
            render(self.native(), output, [1000000])
        self.assertFalse(output.exists())
