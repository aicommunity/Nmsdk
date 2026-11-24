"""Versioned search order, never a physical model or convergence certificate."""
from copy import deepcopy

from .native_evidence import count, number, require

FIELD = 'input_traversal'
KIND = 'timelearner_input_traversal'
POLICY = 'classic_candidate_round_robin'
MAX_EXACT = 2**53-1
FIELDS = {'kind', 'schema_version', 'policy', 'candidates_per_visit', 'maximum_seed_elements'}


def optional_fields(search):
    require(type(search) is dict, 'invalid_input_traversal_search')
    return {FIELD} if FIELD in search else set()


def audit_input_traversal(search, *, branch, normalization=None, capacitance_search=None):
    """Validate the declaration/bounded seed inventory, not native execution.

    Cold declarations store C policy outside search; runtime/summary records
    store it inside. Callers pass the actual cold policy explicitly when used.
    Omission preserves legacy data and does not fabricate a new field.
    """
    require(type(search) is dict, 'invalid_input_traversal_search')
    if FIELD not in search:
        return None
    value = search[FIELD]
    require(type(value) is dict and set(value) == FIELDS and
            value['kind'] == KIND and count(value['schema_version']) == 1 and
            value['policy'] == POLICY, 'unknown_input_traversal_declaration')
    require(branch is False, 'round_robin_input_traversal_requires_classic')
    quantum = count(value['candidates_per_visit']);limit = count(value['maximum_seed_elements'])
    candidates = count(search['maximum_candidates_per_input'])
    require(1 <= quantum <= min(candidates,MAX_EXACT) and 1 <= limit <= MAX_EXACT,
            'invalid_round_robin_budget')
    normalization = search.get('normalization') if normalization is None else normalization
    require(normalization in ('N0', 'N1', 'synapse_count', 'tip_resistance'),
            'unknown_input_traversal_normalization')
    bounds = search['bounds']
    require(type(bounds) is list and bool(bounds), 'input_traversal_bound_dimensions')
    policy = search.get('capacitance_search') if capacitance_search is None else capacitance_search
    contexts = 1 if policy is None else count(policy['maximum_contexts'])
    require(contexts > 0, 'round_robin_seed_contexts_are_zero')
    total = 0
    for bound in bounds[:-1]:
        lower,upper = count(bound['minimum_length']),count(bound['maximum_length'])
        first,last = count(bound['minimum_synapses']),count(bound['maximum_synapses'])
        require(1 <= lower <= upper <= 2**31-1 and 1 <= first <= last <= 128 and
                0 < number(bound['minimum_resistance']) <= number(bound['maximum_resistance']),
                'round_robin_seed_bounds_are_invalid')
        lengths = min(candidates, upper-lower+1)
        normalizers = last-first+1 if normalization in ('N0', 'synapse_count') else max(3,candidates)
        total += contexts*(lengths+normalizers)
        require(total <= limit, 'round_robin_seed_inventory_exceeds_declared_budget')
    return dict(kind=KIND, schema_version=1, policy=POLICY,
        candidates_per_visit=quantum, maximum_seed_elements=limit)


def bind_input_traversal(declared, observed, *, branch, normalization=None, capacitance_search=None):
    expected = audit_input_traversal(declared, branch=branch, normalization=normalization,
        capacitance_search=capacitance_search)
    actual = audit_input_traversal(observed, branch=branch, capacitance_search=capacitance_search)
    require(expected == actual, 'configuration_summary_input_traversal_mismatch')
    return expected


def declare_input_traversal_job(original, run_id, *, policy, candidates_per_visit=1,
                                maximum_seed_elements=131072):
    """Bind only run identity and the complete traversal factor, then re-sign."""
    from .model_identity import canonical_model_sha256 as digest
    from .native_pipeline_worker import validate_job
    from .composite_configuration import project_training_configuration
    validate_job('train', original)
    require(type(run_id) is str and bool(run_id.strip()), 'input_traversal_run_id')
    require(type(candidates_per_visit) is int and type(maximum_seed_elements) is int,
            'input_traversal_operational_counts_must_be_integers')
    require(policy in ('sequential', POLICY), 'unknown_input_traversal_policy')
    job = deepcopy(original);config = job['configuration'];config['run_id'] = run_id
    config['search'].pop(FIELD, None)
    if policy == POLICY:
        config['search'][FIELD] = dict(kind=KIND, schema_version=1, policy=POLICY,
            candidates_per_visit=candidates_per_visit, maximum_seed_elements=maximum_seed_elements)
    else:
        require(candidates_per_visit == 1 and maximum_seed_elements == 131072,
                'unused_sequential_traversal_parameter')
    view = project_training_configuration(config)
    audit_input_traversal(view['search'], branch=view['model']['branch'],
        normalization=view['model']['normalization'], capacitance_search=view.get('capacitance_search'))
    job['sha256'] = digest({k:v for k,v in job.items() if k != 'sha256'})
    validate_job('train', job)
    return job
