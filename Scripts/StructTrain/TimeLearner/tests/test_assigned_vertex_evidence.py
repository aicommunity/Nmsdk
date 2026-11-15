"""Replay real native shared-vertex packets and mutate the actual primary data."""
import copy
import os
from pathlib import Path
import unittest

from ..assigned_vertex_evidence import audit_shared_vertex, read_shared_vertex
from ..native_evidence import EvidenceError


class AssignedVertexEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = os.environ.get('TIMELEARNER_ASSIGNED_VERTEX_CORPUS')
        if not corpus:
            raise unittest.SkipTest('requires actual native merged-burst guard evidence')
        cls.files = sorted(Path(corpus).glob('*_shared_vertex_certificate_guard.json'))
        if len(cls.files) != 1:
            raise AssertionError('expected the one declared Classic shared-vertex control')
        cls.result, cls.packet, cls.execution, cls.rows = read_shared_vertex(cls.files[0])

    def test_real_native_trace_proves_shared_samples_and_rejection(self):
        self.assertTrue(self.result['recorded_window_complete'])
        self.assertEqual(self.result['channel_count'], 2)
        self.assertEqual(self.result['shared_channel'], 0)
        self.assertEqual(len(self.result['actual_stimuli']), 2)
        self.assertEqual(self.result['spike_response'], 'unknown')
        self.assertIsNone(self.result['scientific_verdict'])

    def test_window_and_peak_order_do_not_change_measured_vertex(self):
        p = copy.deepcopy(self.packet)
        p['observation']['windows'].reverse();p['observation']['peaks'].reverse()
        result = audit_shared_vertex(p, self.execution, self.rows)
        self.assertEqual(result['shared_first_sample'], self.result['shared_first_sample'])
        self.assertEqual(result['shared_last_sample'], self.result['shared_last_sample'])

    def test_relabelled_channel_or_peak_is_rejected(self):
        for field in ('channel', 'raw', 'time'):
            p = copy.deepcopy(self.packet)
            if field == 'channel':p['observation']['windows'][1]['channel'] = 1
            else:p['observation']['peaks'][0][field] += .01
            with self.assertRaises(EvidenceError):audit_shared_vertex(p, self.execution, self.rows)

    def test_missing_duplicate_and_nonfinite_samples_are_rejected(self):
        for mutation in ('missing', 'duplicate', 'nonfinite'):
            rows = copy.deepcopy(self.rows)
            if mutation == 'missing':rows.pop(5)
            elif mutation == 'duplicate':rows[5] = rows[4]
            else:rows[5][2] = 'nan'
            with self.assertRaises(EvidenceError):audit_shared_vertex(self.packet, self.execution, rows)

    def test_changed_pattern_and_actual_events_are_rejected(self):
        p = copy.deepcopy(self.packet);p['native_pattern'][1] *= 2
        with self.assertRaises(EvidenceError):audit_shared_vertex(p, self.execution, self.rows)
        p = copy.deepcopy(self.packet);p['observation']['actual_stimuli'][1]['time'] += .01
        with self.assertRaises(EvidenceError):audit_shared_vertex(p, self.execution, self.rows)

    def test_incomplete_packet_or_missing_rejection_cannot_pass(self):
        for field, value in [('rejection', ''), ('schema_version', 2), ('scientific_training_result', True)]:
            p = copy.deepcopy(self.packet);p[field] = value
            with self.assertRaises(EvidenceError):audit_shared_vertex(p, self.execution, self.rows)
        p = copy.deepcopy(self.packet);p['observation']['complete'] = False
        with self.assertRaises(EvidenceError):audit_shared_vertex(p, self.execution, self.rows)

    def test_changed_effective_model_cannot_claim_same_probe(self):
        e = copy.deepcopy(self.execution);e['model_after']['model']['tampered'] = True
        with self.assertRaises(EvidenceError):audit_shared_vertex(self.packet, e, self.rows)
