"""Audit actual native two-context regressions; synthetic decisions are insufficient."""
import os
from pathlib import Path
import unittest

from ..native_evidence import audit_training_summary
from ..stopped_evidence import audit_stopped_state, load_case


class CapacitanceMinimalContextEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = os.environ.get('TIMELEARNER_CAPACITANCE_MINIMAL_CONTEXT_DIR')
        if not directory:
            raise unittest.SkipTest('requires real native two-context C-search traces')
        cls.cases = [load_case(p) for p in sorted(Path(directory).glob('*_csearch_minimal_stopped_state.json'))]
        inventory = {(p['configuration']['model']['branch'], p['configuration']['model']['normalization'])
                     for p, _, _, _ in cls.cases}
        if len(cls.cases) != 4 or inventory != {
            (branch, normalization) for branch in (False, True)
            for normalization in ('N0', 'N1')
        }:
            raise RuntimeError('requires Classic/Branch N0/N1 actual minimal-context cases')

    def test_complete_primary_data_and_owned_capacitance_state_are_valid(self):
        for case in self.cases:
            with self.subTest(model=case[0]['model_revision']):
                result = audit_stopped_state(*case)
                self.assertTrue(result['capacitance_history']['consistent'])
                self.assertTrue(result['capacitance_state']['consistent'])
                self.assertIsNone(result['evaluation_verdict'])

    def test_two_slots_really_measure_a_nonunit_capacitance(self):
        for package, summary, packets, traces in self.cases:
            with self.subTest(model=package['model_revision']):
                self.assertEqual(package['configuration']['capacitance_search']['maximum_contexts'], 2)
                self.assertEqual(summary['configuration']['capacitance_search']['maximum_contexts'], 2)
                changed = [c for c in summary['candidates']
                           if any(scale != 1. for scale in c['capacitance']['membrane_scales'].values())]
                self.assertTrue(changed, 'two slots must include a measured physical C edit')
                if summary['configuration']['normalization'] == 'tip_resistance':
                    self.assertTrue(any(scale != 1. for domain in summary['resistance_domains']
                                        for scale in domain['requested_capacitance']['membrane_scales'].values()))
                self.assertTrue(packets)
                self.assertEqual(len(packets), len(traces))
                self.assertTrue(all(p['observation']['complete'] and p['observation']['valid']
                                    for p in packets.values()))

    def test_zero_sync_negative_control_never_claims_exact_or_classification(self):
        for package, summary, packets, _ in self.cases:
            with self.subTest(model=package['model_revision']):
                result = audit_training_summary(summary, packets,
                    package['protocol']['origin_stimulus_id'], require_certificate=False)
                self.assertNotEqual(package['training_outcome'], 'exact')
                self.assertIsNone(package['certificate'])
                self.assertIsNone(result['exact'])
                self.assertIsNone(result['evaluation_verdict'])
