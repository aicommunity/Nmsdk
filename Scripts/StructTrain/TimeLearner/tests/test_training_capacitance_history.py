"""Actual service history and waveform controls for complete C-state transport."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from ..native_evidence import EvidenceError, audit_training_summary, load
from ..capacitance_evidence import audit_capacitance_state
from ..training_capacitance_history import (audit_training_capacitance_case,
    audit_training_capacitance_history, load_training_capacitance_case)


class TrainingCapacitanceHistoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.environ.get('TIMELEARNER_TRAINING_CAPACITANCE_HISTORY_DIR')
        if not root:
            raise unittest.SkipTest('requires actual schema3 native service histories')
        cls.root = Path(root)
        cls.cases = [(p, *load_training_capacitance_case(p))
                     for p in sorted(cls.root.glob('*_tracked_summary.json'))]
        inventory = set()
        for _, summary, _, _ in cls.cases:
            h = summary['capacitance_history']; initial = h['witnesses'][h['capture_witness_id']]
            inventory.add((initial['native_state']['baseline']['model_spec']['branch'],
                summary['configuration']['normalization'], summary['configuration']['n0_candidate_repeats']))
        expected = {(b, n, r) for b in (False, True)
                    for n, r in [('synapse_count', 1), ('tip_resistance', 1), ('synapse_count', 2)]}
        if len(cls.cases) != 6 or inventory != expected:
            raise RuntimeError('requires Classic/Branch N0/N1 and repeated N0 actual native histories')

    def test_actual_physics_measurements_and_all_primary_traces(self):
        for path, _, _, _ in self.cases:
            with self.subTest(path=path.name):
                result = audit_training_capacitance_case(path)
                self.assertTrue(result['physical_history']['physical_contexts_verified'])
                self.assertTrue(result['measurement_consistent'])
                self.assertTrue(result['primary_traces_verified'])
                self.assertGreater(result['primary_trials'], 0)
                self.assertIsNone(result['scientific_verdict'])

    def test_production_cli_on_every_actual_case(self):
        for path, _, _, _ in self.cases:
            with self.subTest(path=path.name):
                p = subprocess.run([sys.executable, '-m', 'Scripts.StructTrain.TimeLearner', 'analyze',
                    str(path), '--format', 'capacitance-history'], capture_output=True, text=True, timeout=300)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertEqual(json.loads(p.stdout)['analysis'], audit_training_capacitance_case(path))

    def test_default_certificate_requirement_is_preserved(self):
        for _, summary, packets, _ in self.cases:
            if summary['certificate'] is None:
                with self.assertRaisesRegex(EvidenceError, 'unsupported_summary_state_kind|missing_or_unknown_certificate'):
                    audit_training_summary(summary, packets, 'pulse0')
                result = audit_training_summary(summary, packets, 'pulse0', require_certificate=False)
                self.assertFalse(result['certificate_consistent']);self.assertIsNone(result['exact'])
            else:
                self.assertTrue(audit_training_summary(summary, packets, 'pulse0')['certificate_consistent'])

    def test_reset_retains_references_and_does_not_invent_search_history(self):
        for path, before, packets, _ in self.cases:
            after = load(path.with_name(path.name.removesuffix('_tracked_summary.json')+'_tracked_reset_summary.json'))
            self.assertFalse(after['search_history_retained'])
            self.assertEqual(after['references'], before['references'])
            self.assertEqual(after['capacitance_history']['trial_witness_ids'], before['capacitance_history']['trial_witness_ids'])
            self.assertEqual(after['capacitance_history']['resistance_domain_witness_ids'], [])
            self.assertTrue(audit_training_capacitance_history(after, packets)['actual_state_verified'])

    def test_missing_referenced_witness_is_rejected(self):
        for _, original, packets, _ in self.cases:
            summary = copy.deepcopy(original);h = summary['capacitance_history']
            del h['witnesses'][h['capture_witness_id']]
            with self.assertRaisesRegex(EvidenceError, '^missing_training_capacitance_history_witness$'):
                audit_training_capacitance_history(summary, packets)

    def test_old_schema_cannot_hide_new_C_history(self):
        for _, original, packets, _ in self.cases:
            for schema in (1, 2):
                summary = copy.deepcopy(original);summary['schema_version'] = schema
                with self.assertRaisesRegex(EvidenceError, '^unversioned_training_summary_capacitance$'):
                    audit_training_summary(summary, packets, 'pulse0')

    def test_candidate_C_context_cannot_be_fabricated(self):
        for _, original, packets, _ in self.cases:
            self.assertTrue(original['candidates'])
            summary = copy.deepcopy(original)
            summary['candidates'][0]['capacitance']['membrane_scales']['Dendrite1_2'] = 1.15
            with self.assertRaisesRegex(EvidenceError, '^training_history_capacitance_context_mismatch$'):
                audit_training_capacitance_history(summary, packets)

    def test_candidate_Rs_must_match_real_synapses(self):
        for _, original, packets, _ in self.cases:
            summary = copy.deepcopy(original);summary['candidates'][0]['full_parameters'][0]['resistance'] *= 1.01
            with self.assertRaisesRegex(EvidenceError, '^training_capacitance_resistance_mismatch$'):
                audit_training_capacitance_history(summary, packets)

    def test_repeated_group_witness_inventory_is_complete(self):
        cases = [c for c in self.cases if c[1]['configuration']['n0_candidate_repeats'] == 2]
        self.assertEqual(len(cases), 2)
        for _, original, packets, _ in cases:
            summary = copy.deepcopy(original);self.assertTrue(summary['candidate_repeat_groups'])
            summary['candidate_repeat_groups'][0]['anchor_capacitance_witness_ids'].pop()
            with self.assertRaisesRegex(EvidenceError, '^training_repeat_capacitance_dimensions_mismatch$'):
                audit_training_capacitance_history(summary, packets)

    def test_primary_trial_inventory_cannot_be_omitted(self):
        path, original, _, _ = self.cases[0]
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory)/path.name;missing.write_text(json.dumps(original), encoding='utf-8')
            with self.assertRaisesRegex(EvidenceError, '^incomplete_tracked_primary_trial_inventory$'):
                load_training_capacitance_case(missing)

    def test_unbound_C0_is_not_fabricated_by_service(self):
        paths = sorted(self.root.glob('*_unbound_capacitance_service_unbound_history.json'))
        self.assertEqual(len(paths), 2)
        for path in paths:
            record = load(path)
            self.assertEqual(record['reason'], 'native_training_capacitance_history_requires_bound_C0')
            self.assertEqual(record['before'], record['after'])
            self.assertEqual(record['owner'], {})
            self.assertFalse(record['history_present'])

    def test_changed_dormant_context_after_window_is_rejected(self):
        paths = sorted(self.root.glob('*_capacitance_history_sink_fault_history_sink_fault.json'))
        self.assertEqual(len(paths), 2)
        for path in paths:
            record = load(path);summary = record['summary'];history = summary['capacitance_history']
            self.assertEqual(record['before_revision'], record['after_revision'])
            self.assertEqual(record['previous_owner']['dormant_membrane_scales']['Dendrite1_2'], 1.1)
            self.assertEqual(record['actual_owner']['dormant_membrane_scales']['Dendrite1_2'], 1.15)
            previous = history['witnesses'][history['current_witness_id']]
            self.assertGreater(audit_capacitance_state(record['actual_owner'],
                record['actual_owner']['baseline']['model_spec'], previous['model'], previous['storage_images'])['effective_channels'], 0)
            self.assertFalse(history['current_verified']);self.assertIsNone(summary['actual_capacitance_witness_id'])
            self.assertIsNone(summary['certificate']);self.assertEqual(summary['references'], [])
            self.assertEqual(summary['outcome'], 'invalid_observation')
            self.assertEqual(summary['reason'], 'native_training_capacitance_readback_mismatch')
            with self.assertRaisesRegex(EvidenceError, '^unverified_training_summary_actual_capacitance$'):
                audit_training_summary(summary, {}, 'pulse0', require_certificate=False)
