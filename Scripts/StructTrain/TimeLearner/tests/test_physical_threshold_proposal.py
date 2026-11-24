"""Threshold proposals preserve ties, bad input and negative scientific outcomes."""
from copy import deepcopy
import math
import unittest

from ..native_evidence import EvidenceError
from ..physical_threshold_proposal import midgap_from_rows


def rows(target=10., foils=(1., 2., 3., 4., 5., 6., 12.)):
    return [dict(trial_id=str(i), sample_id='pattern-'+str(i),
                 label='target' if i == 0 else 'foil', lt_maximum=value)
            for i, value in enumerate((target, *foils))]


class PhysicalThresholdProposalTest(unittest.TestCase):
    def test_rule_keeps_the_foil_above_target_as_a_proxy_false_positive(self):
        result = midgap_from_rows(rows())
        self.assertEqual(result['status'], 'candidate')
        self.assertEqual(result['threshold'], 8.)
        self.assertEqual(result['full_matrix_peak_margin'], -2.)
        self.assertEqual(result['nonspiking_proxy'], dict(TP=1, FN=0, FP=1, TN=6))

    def test_row_order_does_not_select_target(self):
        source = rows(); expected = midgap_from_rows(source)
        for offset in range(8):
            self.assertEqual(midgap_from_rows(source[offset:]+source[:offset]), expected)

    def test_equal_foil_is_not_separated_by_an_invented_epsilon(self):
        result = midgap_from_rows(rows(foils=(1., 2., 3., 4., 5., 6., 10.)))
        self.assertEqual(result['threshold'], 8.)
        self.assertEqual(result['nonspiking_proxy']['FP'], 1)
        self.assertEqual(result['full_matrix_peak_margin'], 0.)

    def test_no_lower_foil_is_a_valid_negative_result_without_silent_candidate(self):
        result = midgap_from_rows(rows(foils=(10., 11., 12., 13., 14., 15., 16.)))
        self.assertEqual(result['status'], 'nonseparable')
        self.assertIsNone(result['threshold'])
        self.assertIsNone(result['nonspiking_proxy'])

    def test_adjacent_floats_are_unresolved_instead_of_relaxing_the_gap(self):
        result = midgap_from_rows(rows(target=math.nextafter(1., math.inf), foils=(1.,)*7))
        self.assertEqual(result['status'], 'unresolved')
        self.assertIsNone(result['threshold'])

    def test_invalid_numeric_maxima_are_rejected(self):
        for value in (math.nan, math.inf, -math.inf, True, '10'):
            source = rows(); source[3]['lt_maximum'] = value
            with self.subTest(value=value), self.assertRaises(EvidenceError):
                midgap_from_rows(source)

    def test_duplicate_or_missing_identity_is_rejected(self):
        for key in ('trial_id', 'sample_id'):
            source = rows(); source[2][key] = source[1][key]
            with self.subTest(key=key), self.assertRaises(EvidenceError):
                midgap_from_rows(source)
        source = rows(); source[0]['sample_id'] = ''
        with self.assertRaises(EvidenceError): midgap_from_rows(source)

    def test_missing_trial_and_wrong_label_are_rejected(self):
        for source in (rows()[:-1], [dict(r, label='foil') for r in rows()],
                       [dict(r, label='unknown') if i == 2 else r for i, r in enumerate(rows())]):
            with self.assertRaises(EvidenceError): midgap_from_rows(source)

    def test_input_is_not_rewritten(self):
        source = rows(); before = deepcopy(source)
        midgap_from_rows(source)
        self.assertEqual(source, before)
