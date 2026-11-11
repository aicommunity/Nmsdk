"""Reference annotations must not hide a small recorded signal behind its threshold."""
import unittest

from ..channel_diagnostic_reports import lt_threshold_display
from ..native_evidence import EvidenceError


class ChannelLTThresholdDisplayTest(unittest.TestCase):
    def test_remote_thresholds_keep_exact_value_and_direction_without_an_axis_line(self):
        limits = [-.001, .004]
        for threshold, direction in ((100., 'above'), (-100., 'below')):
            with self.subTest(direction=direction):
                display = lt_threshold_display(threshold, limits)
                self.assertEqual(display['position'], direction)
                self.assertFalse(display['line_drawn'])
                self.assertEqual(float(display['value_text']), threshold)
                self.assertIn(direction+' displayed Y', display['annotation'])
                self.assertEqual(display['axis_range_policy'], 'recorded_values_only')
        self.assertEqual(limits, [-.001, .004])

    def test_visible_threshold_and_axis_boundaries_keep_the_actual_reference_line(self):
        for threshold in (-.001, .002, .004):
            with self.subTest(threshold=threshold):
                display = lt_threshold_display(threshold, (-.001, .004))
                self.assertEqual(display['position'], 'inside')
                self.assertTrue(display['line_drawn'])
                self.assertEqual(float(display['value_text']), threshold)
                self.assertNotIn('outside', display['annotation'])

    def test_nonfinite_threshold_or_invalid_axis_cannot_be_reported_as_a_valid_reference(self):
        for threshold, limits in ((float('nan'), (0., 1.)), (float('inf'), (0., 1.)),
                                  (100., []), (100., (1., 0.)), (100., (0., 0.)),
                                  (100., (0., float('inf')))):
            with self.subTest(threshold=threshold, limits=limits), self.assertRaises(EvidenceError):
                lt_threshold_display(threshold, limits)
