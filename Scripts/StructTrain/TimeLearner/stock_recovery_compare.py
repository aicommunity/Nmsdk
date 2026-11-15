"""Compare fully audited stock studies without merging their scientific claims.

Code/runtime may differ. Every declared training factor and cold effective
graph must match, apart from the attempt run_id. Matching is by condition labels,
never CSV/design row position. A self-comparison is not a new repetition.
"""
from copy import deepcopy
import hashlib
from pathlib import Path

from .native_evidence import load, require
from .search_coverage import analyze_stock_recovery
from .stock_recovery_study import audit_design


def _key(row):
    return row['topology'], row['initial_threshold'], row['policy']


def _declared_job(job):
    result = deepcopy(job)
    result.pop('sha256')
    result['configuration'].pop('run_id')
    return result


def match_designs(baseline, candidate):
    """Validate declarations only; this does not establish native execution."""
    baseline, candidate = Path(baseline), Path(candidate)
    before, after = audit_design(baseline), audit_design(candidate)
    left, right = ({_key(r): r for r in d['rows']} for d in (before, after))
    require(len(left) == len(right) == 8 and left.keys() == right.keys(),
            'stock_compare_condition_inventory_mismatch')
    pairs = []
    for key in sorted(left):
        a, b = left[key], right[key]
        job_a = load(baseline/'jobs'/(a['name']+'.json'))
        job_b = load(candidate/'jobs'/(b['name']+'.json'))
        require(_declared_job(job_a) == _declared_job(job_b),
                'stock_compare_training_factors_changed:'+str(key))
        expected_a = load(baseline/'expected'/(a['name']+'.json'))
        expected_b = load(candidate/'expected'/(b['name']+'.json'))
        require(expected_a == expected_b, 'stock_compare_cold_graph_changed:'+str(key))
        pairs.append({'topology': key[0], 'initial_threshold': key[1], 'policy': key[2],
                      'baseline_name': a['name'], 'candidate_name': b['name'],
                      'baseline_condition_fingerprint': a['condition_fingerprint'],
                      'candidate_condition_fingerprint': b['condition_fingerprint'],
                      'expected_initial_revision': expected_a['sha256']})
    return pairs


def _record(row):
    return {key: row[key] for key in (
        'name', 'model_revision', 'package_sha256', 'summary_sha256', 'outcome', 'reason',
        'measured_candidate_records', 'typed_unassigned_observations',
        'producer_invalid_observations', 'invalid_counter_unknown_for_legacy_summary',
        'search_probes', 'reference_probes', 'applied_edits')}


def compare_studies(baseline, candidate):
    baseline, candidate = Path(baseline).resolve(strict=True), Path(candidate).resolve(strict=True)
    pairs = match_designs(baseline, candidate)
    # These are the full production primary/CSV audits, not trusted summaries.
    before, after = (analyze_stock_recovery(p) for p in (baseline, candidate))
    left, right = ({r['name']: r for r in d['rows']} for d in (before, after))
    for pair in pairs:
        a, b = pair['baseline_name'], pair['candidate_name']
        pair['baseline'], pair['candidate'] = _record(left[a]), _record(right[b])
        pair['baseline']['recorded_geometry_groups'] = len(left[a]['recorded_geometry_groups'])
        pair['candidate']['recorded_geometry_groups'] = len(right[b]['recorded_geometry_groups'])
        def manifest_sha(directory, name):
            return hashlib.sha256((directory/'runs'/name/'run-manifest.json').read_bytes()).hexdigest()
        pair['baseline_run_manifest_sha256'] = manifest_sha(baseline, a)
        pair['candidate_run_manifest_sha256'] = manifest_sha(candidate, b)
        pair['same_attempt'] = pair['baseline_run_manifest_sha256'] == pair['candidate_run_manifest_sha256']
    return {'kind': 'stock_recovery_matched_code_comparison', 'schema_version': 1,
            'baseline_code': load(baseline/'code-identity.json'),
            'candidate_code': load(candidate/'code-identity.json'),
            'baseline_runtime_fingerprint': load(baseline/'runtime.json')['runtime_fingerprint'],
            'candidate_runtime_fingerprint': load(candidate/'runtime.json')['runtime_fingerprint'],
            'pairs': pairs, 'paired_conditions': 8, 'both_studies_primary_audited': True,
            'training_factors_and_cold_graph_matched': True,
            'same_attempt_pairs': sum(p['same_attempt'] for p in pairs),
            'independent_random_repeats_attested': False,
            'full_search_box_exhaustion_attested': False, 'physical_infeasibility_attested': False,
            'classification_assessed': False, 'scientific_verdict': None}
