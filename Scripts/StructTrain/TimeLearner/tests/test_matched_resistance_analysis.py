"""Actual time-matched controls and a real different-clock negative pair."""
import os
from pathlib import Path
import tempfile
import unittest

from ..matched_resistance_analysis import analyze, compare_probe_inputs, _trace
from ..native_calibration_worker import _write
from ..native_evidence import EvidenceError, load


class MatchedResistanceAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_MATCHED_RESISTANCE_CORPUS')
        if not value:
            raise unittest.SkipTest('requires actual source replay, matched control and Rs runs')
        cls.root = Path(value);cls.result = analyze(cls.root)

    def test_both_actual_controls_match_clock_samples_inputs_runtime_and_warm_source(self):
        self.assertTrue(self.result['all_conditions_matched'])
        self.assertEqual({r['branch'] for r in self.result['rows']}, {False, True})
        for row in self.result['rows']:
            self.assertEqual(row['source_model_revision'], row['control_model_revision'])
            self.assertNotEqual(row['control_model_revision'], row['changed_model_revision'])
            self.assertGreater(row['model_time_begin'], 0)
        self.assertFalse(self.result['training_executed']);self.assertFalse(self.result['spiking_response_measured'])
        self.assertIsNone(self.result['scientific_classification_verdict'])

    def test_selected_physical_bank_has_an_actual_soma_response_to_rs_change(self):
        for row in self.result['rows']:
            self.assertGreater(row['potential_differences'][0]['maximum_absolute_potential_difference'], 0)

    def test_actual_other_clock_pair_is_not_hidden_by_onset_alignment(self):
        rows = load(self.root/'index.json')['rows']
        replay = next(r for r in rows if not r['branch'] and r['variant'] == 'baseline')
        matched = next(r for r in rows if not r['branch'] and r['variant'] == 'matched-control')
        a, sa, xa = _trace(self.root/'runs'/replay['name']/'native')
        b, sb, xb = _trace(self.root/'runs'/matched['name']/'native')
        result = compare_probe_inputs(a, sa, xa, b, sb, xb)
        self.assertFalse(result['absolute_sample_times_equal']);self.assertFalse(result['windows_equal'])
        self.assertFalse(result['actual_stimulus_rows_and_events_equal'])

    def test_five_of_six_actual_rows_cannot_be_analyzed_as_a_complete_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp);index = load(self.root/'index.json');index['rows'] = index['rows'][:-1]
            _write(folder/'index.json', index)
            with self.assertRaisesRegex(EvidenceError, 'matched_control_coverage_missing'):analyze(folder)
