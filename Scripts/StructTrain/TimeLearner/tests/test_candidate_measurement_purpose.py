"""Descriptor checks only; these labels grant no native observation authority."""
import unittest

from ..candidate_measurement_purpose import measurement_purpose_inventory
from ..native_evidence import EvidenceError


class CandidateMeasurementPurposeTest(unittest.TestCase):
    def test_historical_absence_is_unknown_not_exploration(self):
        self.assertIsNone(measurement_purpose_inventory([{}, {}]))

    def test_empty_history_invents_no_phase_counts(self):
        self.assertIsNone(measurement_purpose_inventory([]))

    def test_all_three_known_purposes_remain_distinct(self):
        result = measurement_purpose_inventory([
            {'measurement_purpose': 'exploration'},
            {'measurement_purpose': 'proposal_recheck'},
            {'measurement_purpose': 'selected_state_restore'}])
        self.assertEqual(result['records_by_purpose'], dict(exploration=1,
            proposal_recheck=1, selected_state_restore=1))
        self.assertFalse(result['controller_decisions_replayed'])

    def test_repeated_records_are_not_claimed_as_distinct_coordinates(self):
        result = measurement_purpose_inventory([{'measurement_purpose': 'exploration'}]*2)
        self.assertEqual(result['measurement_records'], 2)
        self.assertEqual(result['records_by_purpose']['exploration'], 2)
        self.assertFalse(result['distinct_exploration_candidates_recomputed'])

    def test_partial_tagging_does_not_silently_reclassify_legacy_records(self):
        with self.assertRaisesRegex(EvidenceError, 'mixed_candidate_measurement_purpose_schema'):
            measurement_purpose_inventory([{'measurement_purpose': 'exploration'}, {}])

    def test_unknown_names_and_nonstrings_are_rejected(self):
        for value in ('unknown', '', True, 0, None):
            with self.subTest(value=value), self.assertRaisesRegex(EvidenceError,
                    'unknown_candidate_measurement_purpose'):
                measurement_purpose_inventory([{'measurement_purpose': value}])

    def test_final_pass_cannot_be_disguised_as_search_candidate_evidence(self):
        with self.assertRaisesRegex(EvidenceError, 'unknown_candidate_measurement_purpose'):
            measurement_purpose_inventory([{'measurement_purpose': 'final_verification'}])

    def test_malformed_record_containers_are_rejected(self):
        for value in ({}, None, [None], [0]):
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                measurement_purpose_inventory(value)
