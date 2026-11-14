"""Same original production units and corpus before/after the N0 scope fix.

Expected failures on the old algorithm are evidence, not a passing classifier.
This gate does not execute Rdk components or admit a native SDK.
"""
import os
from pathlib import Path
import unittest

from ..controller_ab import run_controller_ab
from ..native_evidence import load, require


class N0GeometryControllerABTest(unittest.TestCase):
    def test_old_starvation_and_new_complete_scoped_corpus(self):
        binding = os.environ.get('TIMELEARNER_N0_GEOMETRY_AB_CONTROLS')
        require(binding is not None, 'n0_geometry_ab_controls_required')
        controls = Path(binding).resolve(strict=True)
        declaration = load(controls/'declaration.json')
        require(set(declaration) == {'root_repository', 'pulse_repository', 'compiler',
                                    'gtest_source', 'expected_baseline_failures'},
                'n0_geometry_ab_controls_schema')
        specification = load(controls/'specification.json')
        expected = specification['expected_test_ids']
        require(len(expected) == 6 and len(set(expected)) == 6 and
                declaration['expected_baseline_failures'] == expected[:5],
                'n0_geometry_ab_regression_inventory')
        result = run_controller_ab(controls/'specification.json',
            declaration['root_repository'], declaration['pulse_repository'],
            declaration['compiler'], declaration['gtest_source'],
            Path('tmp/n0-geometry-controller-ab').resolve())
        before, after = (result['cases'][name] for name in ('baseline', 'candidate'))
        self.assertEqual(before['compile']['execution'], 'completed')
        self.assertEqual(after['compile']['execution'], 'completed')
        self.assertEqual(before['execution'], 'process_error')
        self.assertEqual(before['validity'], 'valid')
        self.assertEqual(before['assertion_status'], 'failed')
        self.assertCountEqual(before['inventory']['failed_test_ids'],
                              declaration['expected_baseline_failures'])
        self.assertEqual(after['execution'], 'completed')
        self.assertEqual(after['validity'], 'valid')
        self.assertEqual(after['assertion_status'], 'passed')
        self.assertEqual(after['inventory']['failed_test_ids'], [])
        self.assertTrue(result['same_test_sources'])
        self.assertEqual(result['assertion_status'], 'failed')
        self.assertFalse(result['native_rdk_integration_verified'])
        self.assertFalse(result['operation_trace_equivalence_verified'])
        self.assertIsNone(result['scientific_verdict'])
