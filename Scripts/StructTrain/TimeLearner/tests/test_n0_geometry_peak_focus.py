"""Actual schema7 N0 peaks at readable native resolution, without new probes."""
import os
from pathlib import Path
import unittest

from ..native_evidence import load
from ..recorded_training_focus import render


class N0GeometryPeakFocusNativeTest(unittest.TestCase):
    def test_actual_best_assigned_peaks_are_inside_the_displayed_native_frames(self):
        from PIL import Image
        for role, group, peak_frame in (('before', 62, 978), ('after', 74, 996)):
            native = Path(os.environ['TIMELEARNER_N0_GEOMETRY_'+role.upper()]).resolve(strict=True)
            summary = load(native/'train_stopped_summary.json')
            self.assertEqual(summary['outcome'], 'budget_exhausted')
            self.assertIsNone(summary['certificate'])
            self.assertFalse(any(c['within_timing'] and c['within_amplitude']
                                 for c in summary['candidates']))
            best = min((c for c in summary['candidates'] if c['within_timing']),
                       key=lambda c: abs(c['amplitude_residual']))
            package = load(native/'train_stopped_state.json')
            self.assertEqual(package['schema_version'], 7)
            self.assertTrue(package['configuration']['model']['branch'])
            self.assertEqual(package['configuration']['model']['normalization'], 'N0')
            record = package['measurement_archive']['records'][group-1]
            self.assertEqual(record['group_id'], best['measurement_group_id'])
            geometry = record['selection']['geometry']
            self.assertEqual(geometry['validity'], 'valid')
            self.assertEqual(geometry['measured_maximum']['first_sample'], peak_frame)
            self.assertEqual(geometry['measured_maximum']['last_sample'], peak_frame)
            self.assertTrue(920 < peak_frame < 1040)
            del geometry, record, package
            # Use the already maintained production focus renderer. Its source
            # audit includes every package/CSV; this is only a display slice.
            output = Path(os.environ['TMPDIR'])/('N0-geometry-'+role+'-peak-focus')
            report = render(native, output, [group], channel=0, first_frame=920, last_frame=1040)
            self.assertEqual(len(report['rows']), 1)
            self.assertEqual(report['rows'][0]['samples'], 121)
            self.assertEqual(report['rows'][0]['original_selection'], 'valid')
            self.assertGreaterEqual(report['minimum_native_tick_pixels'], 8.)
            self.assertFalse(report['downsampling'])
            self.assertFalse(report['assignment_changed'])
            self.assertTrue(report['display_only'])
            self.assertIsNone(report['scientific_verdict'])
            with Image.open(output/report['files'][0]) as image:
                self.assertEqual(image.size, (2800, 800))
