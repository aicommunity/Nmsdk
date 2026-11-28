"""Full actual primary audit of the separately declared two-sweep cold case.

The common complete-history/one-decode check is inherited unchanged. Only
the source role and independent declared-case factory differ. The expected
budget is never reconstructed from the finished run's outcome or edits.
"""
from . import test_closed_matched_count_training as single_sweep
from ..prepared_count_training import doubled_sweep_count_job


class ClosedDoubledCountTrainingTest(single_sweep.ClosedMatchedCountTrainingTest):
    EXPECTED_SWEEPS = 2
    PROOF_KIND = 'timelearner_closed_doubled_count_training_audit'
    PROOF_NAME = 'two-sweep-count-training-audit.json'
    SOURCE_RECORD_KEY = 'original_cold_count_normalization_job'

    def declared_job(self, original, run_id):
        return doubled_sweep_count_job(original, run_id)
