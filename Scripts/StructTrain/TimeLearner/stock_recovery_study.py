"""Matched native cold Train controls for unassigned-burst recovery.

Eight conditions are frozen before any native operation. A valid stopped model
is a result, not a classifier or a completed training certificate. The historical
threshold study supplies declarations and expected cold graphs only.
"""
from copy import deepcopy
import json
from pathlib import Path
import shutil

from .candidate_recovery import RECOVERY_MODE, project_recovery_configuration
from .condition import ConditionSpec
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .n1_protocol_robustness import _signed, _write
from .process_runner import verify_runtime
from .stock_phasea_preflight import TARGET, audit_stock_profile
from .stock_threshold_study import THRESHOLDS, _condition as _threshold_condition, audit_final_stock


INVALID_ALLOWANCE = 32
POLICIES = ('retry_same_candidate', RECOVERY_MODE)


def _condition(job, expected, code, runtime):
    return _threshold_condition(job, expected, code, runtime,
                                algorithm_id='stock-phasea-cold-recovery-pair-v1')


def recovery_job(template, name, policy):
    require(policy in POLICIES, 'stock_recovery_unknown_policy')
    job = deepcopy(template)
    configuration = job['configuration']
    require(configuration['schema_version'] == 1 and
            configuration['search']['maximum_invalid_observations'] == 0,
            'stock_recovery_requires_original_base1_template')
    configuration['run_id'] = name
    configuration['search']['maximum_invalid_observations'] = INVALID_ALLOWANCE
    if policy == RECOVERY_MODE:
        configuration.update(schema_version=5, base_schema_version=1,
                             invalid_measurement_recovery=RECOVERY_MODE)
    job = _signed(job)
    validate_job('train', job)
    return job


def _normalized(job):
    configuration, _ = project_recovery_configuration(job['configuration'])
    configuration.pop('run_id')
    normalized = {k: deepcopy(v) for k, v in job.items() if k not in ('configuration', 'sha256')}
    normalized['configuration'] = configuration
    return normalized


def prepare(source, runtime_path, code_identity, output):
    source, output = Path(source).resolve(strict=True), Path(output)
    require(not output.exists(), 'stock_recovery_output_exists')
    runtime = load(Path(runtime_path));verify_runtime(runtime)
    original = load(source/'design.json')
    require(original['kind'] == 'stock_phasea_threshold_pair_design' and
            original['sha256'] == _signed(original)['sha256'] and
            len(original['rows']) == 4 and
            {(r['topology'], r['initial_threshold']) for r in original['rows']} ==
            {(t, v) for t in ('Classic', 'Branch') for v in THRESHOLDS},
            'stock_recovery_original_inventory')
    output.mkdir(parents=True)
    for name in ('jobs', 'expected', 'conditions', 'source'):
        (output/name).mkdir()
    _write(output/'runtime.json', runtime);_write(output/'code-identity.json', code_identity)
    _write(output/'source/design.json', original)
    rows = []
    for row in original['rows']:
        template = load(source/'jobs'/(row['name']+'.json'))
        expected = load(source/'expected'/(row['name']+'.json'))
        require(template['sha256'] == row['job_sha256'] == _signed(template)['sha256'] and
                expected['sha256'] == row['expected_initial_revision'],
                'stock_recovery_original_declaration_changed')
        model = template['configuration']['model']
        require(model['initial_isi'] == TARGET and model['normalization'] == 'N1' and
                model['neuron_class'] == 'NSPNeuronGen' and template['profile_archives'] == [] and
                template['configuration']['search']['tolerances'] ==
                {'amplitude_absolute': 1e-5, 'amplitude_relative': 0, 'sync': .02},
                'stock_recovery_original_scope_changed')
        audit_stock_profile(expected, branch=row['topology'] == 'Branch')
        _write(output/'source'/(row['name']+'.json'), template)
        for policy in POLICIES:
            name = row['name']+('-retry32' if policy == POLICIES[0] else '-advance32')
            job = recovery_job(template, name, policy)
            evidence = _condition(job, expected, code_identity, runtime)
            fingerprint = ConditionSpec.loads(json.dumps(evidence['condition'])).fingerprint
            _write(output/'jobs'/(name+'.json'), job)
            _write(output/'expected'/(name+'.json'), expected)
            _write(output/'conditions'/(name+'.json'), evidence)
            rows.append({**row, 'name': name, 'source_name': row['name'], 'policy': policy,
                         'job_sha256': job['sha256'], 'condition_fingerprint': fingerprint})
    design = _signed({'kind': 'stock_recovery_design', 'schema_version': 1, 'rows': rows,
                      'invalid_allowance': INVALID_ALLOWANCE, 'classification_assessed': False,
                      'scientific_verdict': None, 'all_jobs_frozen_before_native_operations': True})
    _write(output/'design.json', design)
    audit_design(output)
    return design


def audit_design(directory):
    directory = Path(directory)
    design = load(directory/'design.json')
    require(design == _signed(design) and design['kind'] == 'stock_recovery_design' and
            type(design['schema_version']) is int and design['schema_version'] == 1 and
            design['invalid_allowance'] == INVALID_ALLOWANCE and
            design['all_jobs_frozen_before_native_operations'] is True and
            design['classification_assessed'] is False and design['scientific_verdict'] is None,
            'stock_recovery_design_changed')
    rows = design['rows']
    require(len(rows) == len({r['name'] for r in rows}) == 8 and
            {(r['topology'], r['initial_threshold'], r['policy']) for r in rows} ==
            {(t, v, p) for t in ('Classic', 'Branch') for v in THRESHOLDS for p in POLICIES},
            'stock_recovery_incomplete_matrix')
    original = load(directory/'source/design.json')
    require(original == _signed(original) and len(original['rows']) == 4,
            'stock_recovery_original_inventory')
    sources = {r['name']: r for r in original['rows']}
    require(len(sources) == 4, 'stock_recovery_original_inventory')
    runtime, code = load(directory/'runtime.json'), load(directory/'code-identity.json')
    for row in rows:
        name = row['name'];job = load(directory/'jobs'/(name+'.json'))
        source = load(directory/'source'/(row['source_name']+'.json'))
        require(row['source_name'] in sources and
                source['sha256'] == sources[row['source_name']]['job_sha256'] == _signed(source)['sha256'] and
                row['expected_initial_revision'] == sources[row['source_name']]['expected_initial_revision'],
                'stock_recovery_original_declaration_changed')
        require(job == recovery_job(source, name, row['policy']) and job['sha256'] == row['job_sha256'],
                'stock_recovery_other_factors_changed')
        expected = load(directory/'expected'/(name+'.json'))
        require(expected['sha256'] == row['expected_initial_revision'] and
                job['configuration']['model']['branch'] == (row['topology'] == 'Branch') and
                job['configuration']['model']['initial_threshold'] == row['initial_threshold'],
                'stock_recovery_factor_changed')
        evidence = _condition(job, expected, code, runtime)
        require(evidence == load(directory/'conditions'/(name+'.json')) and
                ConditionSpec.loads(json.dumps(evidence['condition'])).fingerprint == row['condition_fingerprint'],
                'stock_recovery_condition_changed')
        peer = next(r for r in rows if r['source_name'] == row['source_name'] and r['policy'] != row['policy'])
        require(_normalized(job) == _normalized(load(directory/'jobs'/(peer['name']+'.json'))),
                'stock_recovery_unmatched_pair')
    return design


def run(source, runtime_path, code_identity, output, *, process_policy=None):
    output = Path(output)
    design = prepare(source, runtime_path, code_identity, output)
    require(shutil.disk_usage(output).free >= 16*1024**3, 'stock_recovery_primary_capacity')
    (output/'preflights').mkdir();(output/'runs').mkdir()
    for row in design['rows']:
        name = row['name'];print('PREFLIGHT', name, flush=True)
        result = run_job('preflight', output/'jobs'/(name+'.json'), None,
                         output/'runtime.json', output/'preflights'/name, 180., process_policy=process_policy)
        require(result['execution'] == 'completed' and result['validity'] == 'valid',
                'stock_recovery_preflight_failed')
        require(load(output/'preflights'/name/'native/initial-state.json')['identity'] ==
                load(output/'expected'/(name+'.json')), 'stock_recovery_effective_profile_drift')
    records = []
    for row in design['rows']:
        name = row['name'];print('TRAIN', name, flush=True)
        result = run_job('train', output/'jobs'/(name+'.json'), None,
                         output/'runtime.json', output/'runs'/name, 7200., process_policy=process_policy)
        require(result['execution'] == 'completed' and result['validity'] == 'valid',
                'stock_recovery_training_execution_invalid')
        records.append(_audit_run(output, row))
        _write(output/'progress.json', records)
        print('END', name, records[-1]['training_outcome'], flush=True)
    _write(output/'index.json', _signed({'kind': 'stock_recovery_index', 'schema_version': 1,
                                       'records': records}))
    result = audit(output);_write(output/'analysis.json', result)
    return result


def _audit_run(directory, row):
    name = row['name'];expected = load(directory/'expected'/(name+'.json'))
    runtime = load(directory/'runtime.json')
    for phase in ('preflights', 'runs'):
        folder = directory/phase/name
        audit_run_manifest(folder/'run-manifest.json')
        require(load(folder/'native/initial-state.json')['identity'] == expected and
                load(folder/'process/runtime.json') == runtime, 'stock_recovery_initial_or_runtime_changed')
    native = directory/'runs'/name/'native';execution = load(native/'execution.json')
    package = load(native/execution['package_path'])
    physics = audit_final_stock(expected, package['neuron']['graph']['identity'])
    return {'name': name, 'training_outcome': execution['training_outcome'],
            'completed_boundary': execution['completed_boundary'], 'model_revision': execution['model_revision'],
            'final_stock_physics': physics}


def audit(directory):
    directory = Path(directory).resolve(strict=True);design = audit_design(directory)
    index = load(directory/'index.json')
    require(index == _signed(index) and index['kind'] == 'stock_recovery_index' and
            type(index['schema_version']) is int and index['schema_version'] == 1 and
            len(index['records']) == 8, 'stock_recovery_incomplete_results')
    actual = [_audit_run(directory, row) for row in design['rows']]
    require(index['records'] == actual, 'stock_recovery_producer_result_changed')
    return {'kind': 'stock_recovery_analysis', 'schema_version': 1, 'validity': 'valid',
            'training_runs': 8, 'preflight_runs': 8, 'rows': actual,
            'classification_assessed': False, 'scientific_verdict': None}
