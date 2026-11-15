"""All actual controls for the five rejected Branch N4 recovery groups."""
import hashlib
import os
from pathlib import Path
import unittest

from ..composite_training_temporal import render
from ..native_evidence import load, require


class CandidateRecoveryTrainingTemporalNativeTest(unittest.TestCase):
    def test_actual_Branch_recovery_rejections_have_soma_and_own_input_figures(self):
        from PIL import Image
        native = Path(os.environ['TIMELEARNER_RECOVERY_N4_STOPPED_NATIVE']).resolve(strict=True)
        package = load(native/'train_stopped_state.json');summary = load(native/'train_stopped_summary.json')
        require(package['schema_version'] == 7 and summary['schema_version'] == 8 and
            package['configuration']['model']['branch'] is True and
            len(package['configuration']['model']['inputs']) == 4 and
            summary['outcome'] == 'invalid_observation', 'recovery_temporal_actual_N4_scope')
        records = package['measurement_archive']['records']
        rejected_ids = {d['event']['group_id'] for d in summary['recovery_ledger']['deliveries']}
        rejected = [i for i,r in enumerate(records, 1) if r['group_id'] in rejected_ids]
        self.assertEqual(len(rejected), 5)
        assigned = records[rejected[0]-1]['method_specification']['assigned_input']
        preceding = [i for i,r in enumerate(records, 1) if i < rejected[0] and
            r['method_specification']['assigned_input'] == assigned and
            r['selection']['geometry']['validity'] == 'valid']
        require(preceding, 'recovery_temporal_preceding_control_required')
        groups = [max(preceding), *rejected]
        files = {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in native.rglob('*')
            if p.is_file() and not p.is_symlink()}
        output = Path(os.environ['TMPDIR'])/'Branch-N4-recovery-temporal'
        report = render(native, output, groups, native_window_zooms=True)
        self.assertEqual(report['package_audit']['training_outcome'], 'invalid_observation')
        self.assertEqual([g['ordinal'] for g in report['groups']], groups)
        self.assertEqual([g['selection']['geometry']['validity'] for g in report['groups']],
            ['valid']+['missing']*5)
        self.assertEqual(len(report['figures']), 24)
        self.assertEqual(report['schema_version'], 2)
        self.assertFalse(report['native_window_zoom_policy']['peak_assignment_changed'])
        self.assertEqual({f['channel'] for f in report['figures']}, {0})
        self.assertTrue(all(len(g['primary_references']) == 6 for g in report['groups']))
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['training_certificate_eligible'])
        self.assertFalse(report['visual_acceptance_complete'])
        self.assertIsNone(report['scientific_verdict'])
        for figure in report['figures']:
            if figure['view'].endswith('-native'):
                self.assertGreaterEqual(figure['minimum_native_tick_pixels'], 8.)
            for filename in figure['files']:
                self.assertGreater((output/filename).stat().st_size, 100)
            with Image.open(output/figure['files'][0]) as image:
                self.assertGreaterEqual(image.width, 2800)
                self.assertGreaterEqual(image.height, 2800)
        self.assertEqual(files, {p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
