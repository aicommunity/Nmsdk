"""Owned production experiment entry; numerical results may be negative."""
import os
from pathlib import Path
import unittest

from ..native_burst_resistance_study import run, render
from ..native_evidence import load


class NativeBurstResistanceStudyTest(unittest.TestCase):
    def test_declared_grid_on_actual_stopped_model(self):
        native = Path(os.environ['TIMELEARNER_BURST_STUDY_SOURCE']).resolve(strict=True)
        controls = Path(os.environ['TIMELEARNER_BURST_STUDY_CONTROLS'])
        result = run(native/'train_stopped_state.json', controls)
        self.assertTrue(result['declared_grid_completed'])
        self.assertFalse(result['training_executed'])
        self.assertIsNone(result['classification_verdict'])
        directory = Path(load(controls/'declaration.json')['output'])
        plots = render(directory, directory.with_name(directory.name+'-plots'))
        self.assertTrue(plots['all_soma_channels_plotted'])
        self.assertTrue(plots['views'])
