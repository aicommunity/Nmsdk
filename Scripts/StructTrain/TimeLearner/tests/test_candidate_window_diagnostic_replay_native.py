"""Independent geometry replay of the actual stopped stock Classic N4 Train."""
import json
import os
from pathlib import Path
import unittest

from ..candidate_window_diagnostic_replay import replay
from ..native_evidence import require


class CandidateWindowDiagnosticReplayNativeTest(unittest.TestCase):
    def test_recorded_and_full_windows_keep_failed_training_and_primary_unchanged(self):
        require('TIMELEARNER_COMPOSITE_TRAIN_NATIVE' in os.environ, 'actual_train_fixture_required')
        result = replay(Path(os.environ['TIMELEARNER_COMPOSITE_TRAIN_NATIVE']), [12, 14, 18])
        self.assertEqual(result['original_training_outcome'], 'invalid_observation')
        self.assertEqual([g['windows'][0]['geometry']['validity'] for g in result['groups']],
                         ['valid', 'missing', 'missing'])
        self.assertEqual(result['package_audit']['native_probes'], 108)
        self.assertTrue(result['posthoc_windows'])
        self.assertFalse(result['original_state_rewritten'])
        self.assertFalse(result['new_model_execution'])
        self.assertFalse(result['training_certificate_eligible'])
        self.assertIsNone(result['scientific_verdict'])
        # Do not prescribe an optimistic full-window answer. Record the actual
        # independent operational result, including ambiguity or missing peaks.
        for group in result['groups']:
            self.assertEqual([w['window'] for w in group['windows']], ['recorded', 'full_observation'])
            self.assertIn(group['windows'][1]['geometry']['validity'],
                          ('valid', 'missing', 'ambiguous', 'clipped', 'nonrepeatable'))
        output = Path(os.environ['TMPDIR'])/'candidate-window-diagnostic-replay.json'
        with output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')
