"""Finite opt-in geometry proposals; no extra budget or convergence authority."""
from .native_evidence import count, require

FIELD = 'maximum_n0_length_proposals'


def audit_n0_length_policy(search):
    """Omission alone denotes the historical order; explicit zero is noncanonical."""
    if FIELD not in search:
        return 0
    value = count(search[FIELD])
    require(search['normalization'] in ('N0', 'synapse_count') and
            0 < value <= count(search['maximum_candidates_per_input']),
            'invalid_n0_length_proposal_budget')
    return value


def bind_n0_length_policy(declared, observed):
    expected = audit_n0_length_policy(declared)
    actual = audit_n0_length_policy(observed)
    require(expected == actual, 'configuration_summary_n0_length_policy_mismatch')
    return expected
