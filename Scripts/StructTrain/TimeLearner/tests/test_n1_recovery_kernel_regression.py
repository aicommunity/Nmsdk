"""Unchanged bounded-search regressions at both exact N1 production closures.

This checks the numerical controller; native rejected-token recovery is verified
separately by real storage/Environment fixtures, not by synthetic scalar probes.
"""
import os
from pathlib import Path
import unittest

from ..controller_ab import run_controller_ab
from ..native_evidence import load, require


class N1RecoveryKernelRegressionTest(unittest.TestCase):
    def test_same106_bounded_normalization_and_search_cases(self):
        controls = Path(os.environ['TIMELEARNER_N1_KERNEL_CONTROLS']).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'root_repository', 'pulse_repository', 'compiler', 'gtest_source'},
                'n1_kernel_controls_schema')
        specification = load(controls/'specification.json')
        self.assertEqual(specification['baseline_root'], '47d67e8fa0d8ea9e2cf61e49ad7e7019dd91c50f')
        self.assertEqual(specification['candidate_root'], '860ee87057196f0afb5b3a98cbd0bdacf378543a')
        self.assertEqual(len(specification['expected_test_ids']), 106)
        result = run_controller_ab(controls/'specification.json',
            declaration['root_repository'], declaration['pulse_repository'],
            declaration['compiler'], declaration['gtest_source'],
            Path(os.environ['TMPDIR']).resolve(strict=True)/'n1-recovery-kernel-regression')
        for name in ('baseline', 'candidate'):
            case = result['cases'][name]
            self.assertEqual(case['compile']['execution'], 'completed')
            self.assertEqual((case['execution'], case['validity'], case['assertion_status']),
                             ('completed', 'valid', 'passed'))
            self.assertEqual(case['inventory']['failed_test_ids'], [])
            self.assertEqual(case['inventory']['observed'], 106)
        self.assertTrue(result['same_test_sources'])
        self.assertEqual(result['assertion_status'], 'passed')
        self.assertFalse(result['native_rdk_integration_verified'])
        self.assertFalse(result['operation_trace_equivalence_verified'])
        self.assertIsNone(result['scientific_verdict'])
