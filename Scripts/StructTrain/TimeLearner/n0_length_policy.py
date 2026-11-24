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


def declare_n0_length_job(original, run_id, maximum_proposals):
    """Change only attempt identity and this explicitly declared N0 factor.

    Zero in this operational request means the legacy policy and is omitted
    from the native configuration. All candidate/probe/time allowances and
    the complete physical specification are retained verbatim.
    """
    from copy import deepcopy
    from .model_identity import canonical_model_sha256 as sha
    from .native_pipeline_worker import validate_job

    validate_job('train', original)
    require(type(run_id) is str and bool(run_id.strip()), 'n0_length_job_run_id')
    require(type(maximum_proposals) is int and maximum_proposals >= 0,
            'n0_length_job_allowance')
    require(original['configuration']['model']['normalization'] == 'N0',
            'n0_length_job_requires_count_normalization')
    job = deepcopy(original)
    config = job['configuration']; config['run_id'] = run_id
    search = config['search']; search.pop(FIELD, None)
    if maximum_proposals:
        search[FIELD] = maximum_proposals
    audit_n0_length_policy(dict(search, normalization=config['model']['normalization']))
    job['sha256'] = sha({k:v for k,v in job.items() if k != 'sha256'})
    validate_job('train', job)
    return job
