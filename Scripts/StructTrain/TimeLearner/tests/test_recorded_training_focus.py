import os
from pathlib import Path
import unittest

from ..recorded_training_focus import render


class RecordedTrainingFocusNativeTest(unittest.TestCase):
    def test_actual_L14_L15_native_grid_focus(self):
        from PIL import Image
        native = Path(os.environ['TIMELEARNER_L22_TRAIN_NATIVE'])
        output = Path(os.environ['TMPDIR'])/'L14-L15-native-frame-focus'
        report = render(native, output, [44, 48], channel=0, first_frame=290, last_frame=351)
        self.assertEqual([r['samples'] for r in report['rows']], [62, 62])
        self.assertEqual([r['original_selection'] for r in report['rows']], ['valid', 'ambiguous'])
        self.assertGreaterEqual(report['minimum_native_tick_pixels'], 8.)
        self.assertFalse(report['downsampling'])
        self.assertFalse(report['assignment_changed'])
        self.assertIsNone(report['scientific_verdict'])
        with Image.open(output/report['files'][0]) as image:
            self.assertGreaterEqual(image.width, 2800)
            self.assertGreaterEqual(image.height, 1600)
