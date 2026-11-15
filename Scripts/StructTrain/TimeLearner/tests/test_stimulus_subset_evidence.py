"""Audit server-produced subset traces and reject damaged versions of those data."""
import copy
import os
from pathlib import Path
import unittest

from ..native_evidence import EvidenceError
from ..stimulus_subset_evidence import audit_subset, read_subset


class StimulusSubsetEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = os.environ.get('TIMELEARNER_STIMULUS_SUBSET_CORPUS')
        if not corpus:
            raise unittest.SkipTest('requires real native subset JSON and CSV primary data')
        cls.legacy = os.environ.get('TIMELEARNER_ALLOW_DRAFT_SUBSET') == '1'
        cls.files = sorted(Path(corpus).glob('*_subset.json'))
        if not cls.files:
            raise AssertionError('declared native subset corpus is empty')
        cls.records = [read_subset(p, allow_draft_without_restoration=cls.legacy)
                       for p in cls.files]

    def audit(self, packet, rows):
        return audit_subset(packet, rows, allow_draft_without_restoration=self.legacy)

    def test_real_native_waveforms_preserve_diagnostic_scope(self):
        self.assertEqual({r[0]['routing'] for r in self.records},
                         {'classic_burst', 'branch_solo_burst'})
        for result, packet, rows in self.records:
            with self.subTest(run=result['run_id']):
                self.assertTrue(result['recorded_window_complete'])
                self.assertEqual(result['peak_assignment'], 'not_performed')
                self.assertEqual(result['spike_response'], 'unknown')
                self.assertIsNone(result['scientific_verdict'])
                self.assertEqual(len(rows)-1, result['sample_count'])
                self.assertEqual(result['restoration'], 'validated_readback'
                                 if packet['schema_version'] == 2 else 'unknown')

    def test_missing_duplicate_nonfinite_and_short_rows_are_rejected(self):
        for _, packet, original in self.records:
            for mutation in ('missing', 'duplicate', 'nan', 'inf', 'short'):
                rows = copy.deepcopy(original)
                if mutation == 'missing': rows.pop(5)
                elif mutation == 'duplicate': rows[5] = rows[4]
                elif mutation == 'short': rows[5].pop()
                else: rows[5][2] = mutation
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    self.audit(packet, rows)

    def test_source_ordinals_and_pattern_hash_cannot_be_relabelled(self):
        for _, original, rows in self.records:
            for key in ('source_ordinals', 'source_training_pattern_hash', 'physical_input_count'):
                packet = copy.deepcopy(original)
                metadata = packet['evidence']['observation']['specification']['stimulus_subset']
                metadata[key] = {'source_ordinals': [999], 'source_training_pattern_hash': '0'*64,
                                 'physical_input_count': 0}[key]
                with self.subTest(field=key), self.assertRaises(EvidenceError):
                    self.audit(packet, rows)

    def test_event_id_time_and_actual_source_signal_are_verified(self):
        for _, original, source in self.records:
            for mutation in ('id', 'time', 'signal'):
                packet, rows = copy.deepcopy(original), copy.deepcopy(source)
                events = packet['evidence']['observation']['stimuli']
                if mutation == 'id': events[0]['id'] = 'pulse999'
                elif mutation == 'time': events[0]['time'] += .01
                else:
                    index = next(i for i, row in enumerate(rows[1:], 1)
                                 if float(row[0]) == events[0]['time'])
                    rows[index][1] = '0'
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    self.audit(packet, rows)

    def test_model_changes_and_false_complete_flags_are_rejected(self):
        for _, original, rows in self.records:
            for mutation in ('model', 'complete', 'spikes', 'peaks'):
                packet = copy.deepcopy(original)
                if mutation == 'model': packet['model_after']['sha256'] = '0'*64
                elif mutation == 'complete': packet['evidence']['observation']['complete'] = False
                elif mutation == 'spikes': packet['evidence']['observation']['spike_count'] = 0
                else: packet['evidence']['observation']['peaks'] = [{}]
                with self.subTest(mutation=mutation), self.assertRaises(EvidenceError):
                    self.audit(packet, rows)

    def test_draft_restoration_is_never_silently_promoted(self):
        for _, original, rows in self.records:
            packet = copy.deepcopy(original)
            packet['schema_version'] = 1
            for key in ('training_pattern_after', 'dataset_pattern_after', 'physical_input_count_after'):
                packet.pop(key, None)
            with self.assertRaisesRegex(EvidenceError, 'draft_subset_missing_restoration_readback'):
                audit_subset(packet, rows)
            self.assertEqual(audit_subset(packet, rows, allow_draft_without_restoration=True)
                             ['restoration'], 'unknown')

    def test_actual_restoration_readbacks_are_required(self):
        records = [record for record in self.records if record[1]['schema_version'] == 2]
        if not records:
            self.skipTest('draft producer has no actual restoration readback; not accepted')
        for _, original, rows in records:
            for key in ('training_pattern_after', 'dataset_pattern_after', 'physical_input_count_after'):
                packet = copy.deepcopy(original)
                packet[key] = 0 if key.endswith('count_after') else []
                with self.subTest(field=key), self.assertRaises(EvidenceError):
                    self.audit(packet, rows)


if __name__ == '__main__':
    unittest.main()
