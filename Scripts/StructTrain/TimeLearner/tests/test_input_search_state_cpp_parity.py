"""Compile the complete decision cohort on both sides of a mechanical change.

The fixture must declare no expected baseline failures. This verifies the
production units and full test inventory, not exact action-trace equality or
native neuronal convergence. No production function bodies are copied.
"""
import os
from pathlib import Path

from . import test_n1_geometry_cpp_ab as compiled


class InputSearchStateCppParityTest(compiled.N1GeometryCppABTest):
    controls_environment = 'TIMELEARNER_INPUT_SEARCH_STATE_CPP_CONTROLS'
    required_regression_ids = (
        'BoundedTrainingMeasuredBoundary/'
        'CompletedSelectionSurvivesAdvanceToFreshFinalVerification',
        'BoundedTrainingMeasuredBoundary/'
        'IncompleteN0RepeatsDoNotPublishARestoreSelection',
        'BoundedTrainingMeasuredCount/'
        'DeferredNeighboursNeverReplaceAFreshFinalCertificate',
    )
    result_kind = 'timelearner_input_search_state_cpp_parity'

    def test_before_exposes_starvation_and_after_passes_complete_decision_cohort(self):
        binding = os.environ.get(self.controls_environment)
        compiled.require(binding is not None, 'decision_cpp_controls_required')
        spec = compiled.load(Path(binding)/'declaration.json')
        compiled.require(spec['expected_before_failures'] == [],
            'input_search_state_baseline_must_pass')
        super().test_before_exposes_starvation_and_after_passes_complete_decision_cohort()
