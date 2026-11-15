"""Exact-candidate selection and comparison using actual native stock primary."""
from copy import deepcopy
from pathlib import Path
import os
import tempfile
import unittest

from ..native_evidence import EvidenceError, load
from ..stock_wave_replay import select_packet, compare_traces
from ..stopped_evidence import load_case


class StockWaveReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get('TIMELEARNER_STOCK_WAVE_SOURCE')
        if not value:
            raise unittest.SkipTest('requires actual eight-case stock native study')
        cls.cases = [load_case(Path(value)/'runs'/name/'native/train_stopped_state.json')
                     for name in ('Classic-threshold-low-retry32', 'Branch-threshold-low-retry32')]

    def test_first_invalid_packet_matches_actual_full_archived_graph_in_both_topologies(self):
        for package, _, packets, _ in self.cases:
            packet = select_packet(package)
            self.assertEqual(packet['prepared']['base_model_revision'], package['model_revision'])
            self.assertEqual(packet, packets[packet['requested_specification']['trial_id']])
            self.assertFalse(packet['observation']['valid'])

    def test_later_matching_packet_cannot_hide_a_different_first_invalid_candidate(self):
        for case in self.cases:
            package = deepcopy(case[0]);first = select_packet(package)
            first['prepared']['base_model_revision'] = 'different-earlier-candidate'
            with self.assertRaisesRegex(EvidenceError, 'requires_intermediate_model_archive'):
                select_packet(package)

    def test_graph_revision_mismatch_is_rejected_before_any_native_run(self):
        for case in self.cases:
            package = deepcopy(case[0]);package['neuron']['graph']['identity']['sha256'] = 'different-graph'
            with self.assertRaisesRegex(EvidenceError, 'source_graph_revision_mismatch'):
                select_packet(package)

    def test_absent_invalid_observation_is_not_invented(self):
        package = deepcopy(self.cases[0][0]);package['observed_packets'] = []
        with self.assertRaisesRegex(EvidenceError, 'no_invalid_probe'):
            select_packet(package)

    def test_actual_self_comparison_is_exact_without_accepting_the_invalid_peak(self):
        for package, _, _, traces in self.cases:
            packet = select_packet(package);trace = traces[packet['requested_specification']['trial_id']]
            result = compare_traces(packet, trace, packet, trace)
            self.assertTrue(result['exact_waveform_reproduced'])
            self.assertEqual(result['original_reasons'], result['replay_reasons'])
            self.assertIsNone(result['scientific_verdict'])

    def test_damaged_primary_token_cannot_be_silently_dropped(self):
        package, _, _, traces = self.cases[0];packet = select_packet(package)
        original = traces[packet['requested_specification']['trial_id']]
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw)/'damaged.csv';lines = original.read_text().splitlines()
            fields = lines[1].split(',');fields[-1] = 'broken';lines[1] = ','.join(fields)
            path.write_text('\n'.join(lines)+'\n')
            with self.assertRaisesRegex(EvidenceError, 'invalid_partial_trace_token'):
                compare_traces(packet, original, packet, path)
