"""Delta-auditor controls based on real imported stock graph identities.

Mutations exercise the auditor only; they are not native intervention results.
"""
from copy import deepcopy
import os
from pathlib import Path
import struct
import unittest

from ..feedback_intervention import audit_profile_delta
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError, load


class FeedbackProfileDeltaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ['TIMELEARNER_FEEDBACK_SOURCE_RUNS'])
        cls.sources = [load(p)['identity'] for p in sorted(root.glob('*-single/native/initial-state.json'))]
        if len(cls.sources) != 2:
            raise AssertionError('requires both actual stock imported single-pulse identities')

    def resign(self, value):
        value['sha256'] = canonical_model_sha256(value['model'])
        return value

    def changed_gain(self, source, value):
        result = deepcopy(source)
        for node in result['model']['nodes']:
            if 'FeedbackGain' in node['parameters']:
                node['parameters']['FeedbackGain']['data']['value'] = struct.pack('>d', value).hex()
        return self.resign(result)

    def test_actual_baseline_graphs_require_no_changes(self):
        for source in self.sources:
            result = audit_profile_delta(source, source, {})
            self.assertEqual(result['mode'], 'baseline_reconstruction')
            self.assertFalse(result['storage_image_closure_verified'])
            self.assertFalse(result['waveform_equivalence_verified'])
            self.assertIsNone(result['scientific_verdict'])

    def test_declared_uniform_gain_is_only_a_delta_audit(self):
        for source in self.sources:
            candidate = self.changed_gain(source, 0.)
            result = audit_profile_delta(source, candidate, {}, feedback_gain=0.)
            self.assertTrue(result['all_other_effective_graph_fields_equal'])
            self.assertTrue(all(n['candidate_gain'] == 0 for n in result['membranes']))
            self.assertIsNone(result['training_certificate'])

    def test_gain_change_cannot_pass_baseline_reconstruction(self):
        for source in self.sources:
            with self.assertRaisesRegex(EvidenceError, 'feedback_undeclared_graph_change'):
                audit_profile_delta(source, self.changed_gain(source, 0.), {})

    def test_all_membranes_must_receive_declared_gain(self):
        source = self.sources[0];candidate = self.changed_gain(source, 0.)
        node = next(n for n in candidate['model']['nodes'] if 'FeedbackGain' in n['parameters'])
        node['parameters']['FeedbackGain']['data']['value'] = struct.pack('>d', 2.).hex()
        with self.assertRaisesRegex(EvidenceError, 'feedback_effective_gain_mismatch'):
            audit_profile_delta(source, self.resign(candidate), {}, feedback_gain=0.)

    def test_hashed_threshold_and_channel_physics_changes_are_rejected(self):
        for source in self.sources:
            for parameter in ('Threshold', 'Capacity', 'DissociationTC', 'Resistance'):
                candidate = self.changed_gain(source, 0.)
                node = next(n for n in candidate['model']['nodes'] if parameter in n['parameters'])
                node['parameters'][parameter]['data']['value'] = struct.pack('>d', .123).hex()
                with self.assertRaisesRegex(EvidenceError, 'feedback_undeclared_graph_change'):
                    audit_profile_delta(source, self.resign(candidate), {}, feedback_gain=0.)

    def test_topology_order_and_frequency_changes_are_rejected(self):
        source = self.sources[0]
        for field in ('child_order', 'frequency_hz'):
            candidate = self.changed_gain(source, 0.);node = candidate['model']['nodes'][0]
            node[field] = list(reversed(node[field])) if field == 'child_order' else '20000'
            with self.assertRaisesRegex(EvidenceError, 'feedback_undeclared_graph_change'):
                audit_profile_delta(source, self.resign(candidate), {}, feedback_gain=0.)

    def test_missing_duplicate_and_stale_identity_are_rejected(self):
        source = self.sources[0]
        for mode in ('missing', 'duplicate', 'stale'):
            candidate = deepcopy(source)
            if mode == 'missing':candidate['model']['nodes'].pop()
            elif mode == 'duplicate':candidate['model']['nodes'].append(deepcopy(candidate['model']['nodes'][0]))
            else:candidate['sha256'] = '0'*64
            if mode != 'stale':self.resign(candidate)
            with self.assertRaises(EvidenceError):audit_profile_delta(source, candidate, {})

    def test_nonfinite_negative_and_boolean_gains_are_rejected(self):
        source = self.sources[0]
        for gain in (float('nan'), float('inf'), -1., True):
            with self.assertRaises(EvidenceError):audit_profile_delta(source, source, {}, feedback_gain=gain)

    def test_declared_class_rename_must_be_complete(self):
        source = self.sources[0];candidate = deepcopy(source)
        old = candidate['model']['nodes'][0]['class'];new = 'FeedbackControlImage'
        for node in candidate['model']['nodes']:
            if node['class'] == old:node['class'] = new
        candidate = self.resign(candidate)
        self.assertTrue(audit_profile_delta(source, candidate, {old:new})['all_other_effective_graph_fields_equal'])
        with self.assertRaises(EvidenceError):audit_profile_delta(source, candidate, {})
        with self.assertRaises(EvidenceError):audit_profile_delta(source, source, {'UnusedImage':new})

    def test_bound_gain_cannot_be_hidden_by_uniform_value(self):
        source = self.sources[0];candidate = self.changed_gain(source, 0.)
        node = next(n for n in candidate['model']['nodes'] if 'FeedbackGain' in n['parameters'])
        node['parameters']['FeedbackGain']['binding'] = True
        with self.assertRaisesRegex(EvidenceError, 'feedback_invalid_gain'):
            audit_profile_delta(source, self.resign(candidate), {}, feedback_gain=0.)
