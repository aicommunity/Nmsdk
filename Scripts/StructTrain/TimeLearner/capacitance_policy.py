"""Closed absolute-C0 search policy; validates declarations, not native execution."""
from .native_evidence import EvidenceError, count, number, require


def _audit(policy, *, maximum_relative_change=None, configuration=None):
    require(type(policy) is dict and set(policy) == {'enumeration', 'minimum_scale', 'maximum_scale',
            'subdivision_depth', 'maximum_contexts', 'maximum_membranes', 'maximum_cursor_elements'} and
            policy['enumeration'] == 'round_robin_absolute_C0_v1', 'unknown_capacitance_search_policy')
    low, high = number(policy['minimum_scale']), number(policy['maximum_scale'])
    require(0 < low <= 1. <= high and count(policy['subdivision_depth']) <= 20 and
            2 <= count(policy['maximum_contexts']) <= 4096 and count(policy['maximum_membranes']) > 0 and
            count(policy['maximum_cursor_elements']) > 0, 'invalid_capacitance_search_policy')
    if maximum_relative_change is not None:
        limit = number(maximum_relative_change)
        require(limit >= 0 and low >= 1.-limit and high <= 1.+limit,
                'capacitance_search_outside_owned_policy')
    if configuration is not None:
        require(count(configuration['maximum_candidates_per_input']) >= count(policy['maximum_contexts']),
                'capacitance_contexts_exceed_candidate_budget')
    return {'schema_version': 1, 'policy_validated': True, 'enumeration_coverage_verified': False,
            'native_lifecycle_verified': False, 'scientific_verdict': None}


def audit_capacitance_search_policy(policy, *, maximum_relative_change=None, configuration=None):
    try:
        return _audit(policy, maximum_relative_change=maximum_relative_change, configuration=configuration)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise EvidenceError('malformed_capacitance_search_policy:'+str(error)) from error
