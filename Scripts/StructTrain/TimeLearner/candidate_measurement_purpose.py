"""Validate optional controller labels; never replace primary measurement proof.

Historical summaries omit the label. Do not infer exploration from omission.
Counts below describe measurement records, including N0 repeats, not distinct
explored coordinates or convergence. A single summary cannot mix producers.
"""
from .native_evidence import require

FIELD = 'measurement_purpose'
PURPOSES = ('exploration', 'proposal_recheck', 'selected_state_restore')


def measurement_purpose_inventory(candidates):
    require(type(candidates) is list and all(type(c) is dict for c in candidates),
            'candidate_measurement_purpose_records_required')
    present = [FIELD in candidate for candidate in candidates]
    if not any(present):
        return None  # Legacy/unlabelled, not evidence of an exploration phase.
    require(all(present), 'mixed_candidate_measurement_purpose_schema')
    counts = dict.fromkeys(PURPOSES, 0)
    for candidate in candidates:
        value = candidate[FIELD]
        require(type(value) is str and value in PURPOSES,
                'unknown_candidate_measurement_purpose')
        counts[value] += 1
    return dict(measurement_records=len(candidates), records_by_purpose=counts,
                distinct_exploration_candidates_recomputed=False,
                controller_decisions_replayed=False)
