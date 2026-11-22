"""Audit a closed actual order study without assuming its scientific outcome."""
import os
from pathlib import Path
import unittest

from ..frozen_physical_order_audit import audit_closed_order


class ClosedPhysicalOrderReanalysisTest(unittest.TestCase):
    def test_all_closed_native_observations_and_relative_responses(self):
        result=audit_closed_order(Path(os.environ['TIMELEARNER_CLOSED_ORDER_CONTROLS']),
            Path(os.environ['TMPDIR'])/'closed-order-stimulus-relative-reanalysis.json')
        self.assertEqual(result['source_control_trials'],8)
        self.assertEqual(result['new_study_trials'],56)
        self.assertEqual(len(result['rows']),56)
        self.assertTrue(result['all_input_bytes_unchanged'])
        self.assertTrue(result['all_eight_target_positions_observed'])
        self.assertFalse(result['native_rerun_performed'])
        self.assertFalse(result['training_completed'])
        self.assertIn(result['original_controller_execution'], ('completed','process_error'))
        if result['original_controller_execution']=='process_error':
            self.assertFalse(result['original_pipeline_success_claimed'])
        self.assertEqual(result['schema_version'],2)
        self.assertIsNone(result['scientific_verdict'])
        # Changed responses/classifications, if measured, remain data. They
        # are not turned into validation failures or hidden by desired counts.
