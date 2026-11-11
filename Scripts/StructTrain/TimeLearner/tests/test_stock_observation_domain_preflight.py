"""Real stock graph admission for the full recorded-domain measurement policy."""
from . import test_stock_candidate_recovery_preflight as shared


class StockObservationDomainPreflightTest(shared.StockCandidateRecoveryPreflightTest):
    prepare_action = 'prepare-full-window'
    expected_plan_version = 3
