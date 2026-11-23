"""Full compiled production decision cohort, before/after deferred reservations.

Reuses the existing pinned-source/compiler/runtime/loaded-file/JUnit A/B path.
The controlled observations prove scheduling, not physical neuron convergence.
"""
from . import test_n1_geometry_cpp_ab as compiled


class N0ProposalReservationCppABTest(compiled.N1GeometryCppABTest):
    controls_environment = 'TIMELEARNER_N0_PROPOSAL_RESERVATION_CPP_CONTROLS'
    required_regression_ids = tuple(
        'BoundedTrainingMeasuredCount/' + name for name in (
            'ClassicRefinesBeforeReservingOrdinaryNeighbours',
            'BranchRefinesBeforeReservingOrdinaryNeighbours',
            'DeferredNeighboursNeverReplaceAFreshFinalCertificate'))
    result_kind = 'timelearner_n0_proposal_reservation_cpp_ab'
