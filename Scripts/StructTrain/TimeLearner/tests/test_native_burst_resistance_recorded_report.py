"""Render the already completed L22 grid; never rerun native experiments."""
import os
from pathlib import Path
import unittest

from ..native_burst_resistance_study import render
from ..native_evidence import load
from ..native_pipeline_worker import audit_run_manifest
from ..plotting import plotting_runtime


class NativeBurstResistanceRecordedReportTest(unittest.TestCase):
    def test_actual_completed_grid_report(self):
        plotting_runtime()
        from PIL import Image
        directory = Path(os.environ['TIMELEARNER_L22_COMPLETED_GRID']).resolve(strict=True)
        result = load(directory/'result.json')
        self.assertTrue(result['declared_grid_completed'])
        self.assertEqual(result['source_revision'],
            '3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c')
        self.assertEqual(result['source_geometry'], [22, 1, 1, 1])
        self.assertEqual(result['physical_bank_owners'], [0])
        self.assertEqual([r['resistance'] for r in result['rows']],
                         [86000000, 86000000, 64500000, 43000000, 21500000])
        self.assertTrue(all(r['observation_complete'] and r['sample_count'] == 3601
                            for r in result['rows']))
        self.assertTrue(all(all(c['conditions'].values()) for c in result['comparisons']))
        self.assertFalse(result['training_executed'])
        self.assertFalse(result['assigned_peak_measured'])
        self.assertIsNone(result['classification_verdict'])
        # render audits matched + all changes; replay must be audited as well.
        self.assertTrue(audit_run_manifest(directory/'runs/replay/run-manifest.json')
                        ['run_evidence_consistent'])
        output = Path(os.environ['TMPDIR'])/'L22-Rs-study-plots'
        report = render(directory, output)
        self.assertTrue(report['all_soma_channels_plotted'])
        self.assertIsNone(report['classification_verdict'])
        self.assertEqual({v['channel'] for v in report['views']}, {0, 1, 2, 3})
        self.assertEqual(len(report['views']), 24)
        for view in report['views']:
            self.assertTrue(view['raw_samples_not_resampled'])
            if 'frames-' in view['path']:
                self.assertLessEqual(view['samples'], 901)
            with Image.open(output/view['path']) as image:
                self.assertGreaterEqual(image.width, 3200)
                self.assertGreaterEqual(image.height, 1400)
