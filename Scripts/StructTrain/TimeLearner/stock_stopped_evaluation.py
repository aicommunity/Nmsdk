"""Frozen eight-pattern diagnostics of actual unfinished stock cold models.

No training, threshold selection, template replacement or convergence claim.
The original source study and native diagnostic reader remain authoritative.
"""
from copy import deepcopy
from pathlib import Path
import shutil

from .n1_protocol_robustness import _inventory, _signed, _write
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .phasea_matrix import from_git, trial_design
from .process_runner import verify_runtime
from .stock_threshold_study import audit as audit_source, audit_final_stock
from .stopped_evidence import load_case


def job_for(row, package, matrix):
    """Use the complete stopped package, not an overlay on an initial template."""
    require(package['kind'] == 'timelearner_stopped_state' and
            package['state_kind'] == 'diagnostic' and package['certificate'] is None and
            package['model_revision'] == row['model_revision'] and
            package['configuration']['model']['branch'] is (row['topology'] == 'Branch'),
            'stock_diagnostic_source_not_actual_stopped_model')
    model = package['configuration']['model']
    require(model['frequency_hz'] == 2000 and model['initial_threshold'] == row['initial_threshold'],
            'stock_diagnostic_source_factor_changed')
    run_id = row['name']+'/stopped-phasea-diagnostic'
    trials = trial_design(matrix, model['initial_isi'], run_id, duration=2., rotations=1)
    job = _signed({'kind': 'timelearner_native_diagnostic_evaluation_job', 'schema_version': 1,
        'owner_class': 'NNeuronTimeLearner'+('Branch' if model['branch'] else ''),
        'implementation_id': package['implementation_id'], 'source_stopped': deepcopy(package),
        'conversion_spec': {'schema_version': 1, 'mode': 'identity', 'resistance_bounds': []},
        'maximum_model_ticks': sum(round(t['duration']*2000)+4 for t in trials),
        'run_id': run_id, 'coverage_policy': 'per_trial_windows',
        'criterion': {'id': 'post_anchor_target_whole_window_foil_v1', 'anchor': 'onset',
                      'begin_offset': 0., 'end_offset': None, 'reject_target_outside_window': True},
        'trials': trials})
    return job


def prepare(source, bin_repository, output):
    source, output = Path(source).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not source.is_relative_to(output) and
            not output.is_relative_to(source), 'stock_diagnostic_output_must_be_separate_and_new')
    analyzed = audit_source(source)
    require(len(analyzed['rows']) == 4 and all(not r['completed_boundary'] for r in analyzed['rows']),
            'stock_diagnostic_requires_four_unfinished_sources')
    output.mkdir(parents=True)
    shutil.copytree(source, output/'source')
    require(_inventory(source) == _inventory(output/'source'), 'stock_diagnostic_copy_changed')
    matrix = from_git(bin_repository)
    _write(output/'matrix.json', matrix)
    runtime = load(source/'runtime.json')
    _write(output/'runtime.json', runtime)
    rows = []
    for row in analyzed['rows']:
        native = output/'source/runs'/row['name']/'native'
        execution = load(native/'execution.json')
        require(execution['completed_boundary'] is False, 'stock_diagnostic_source_completed')
        package = load(native/execution['package_path'])
        job = job_for(row, package, matrix)
        validate_job('diagnostic-evaluate', job, load_case(native/execution['package_path']))
        _write(output/'jobs'/(row['name']+'.json'), job)
        rows.append({'name': row['name'], 'topology': row['topology'],
                     'initial_threshold': row['initial_threshold'], 'source_package': execution['package_path'],
                     'source_model_revision': row['model_revision'], 'job_sha256': job['sha256']})
    design = _signed({'kind': 'stock_stopped_phasea_diagnostic', 'schema_version': 1,
        'rows': rows, 'trials_per_model': 8, 'diagnostic_only': True, 'training_completed': False,
        'calibration_performed': False, 'historical_presentation_reproduced': False,
        'scientific_verdict': None})
    _write(output/'design.json', design)
    return design


def run(source, bin_repository, output):
    design = prepare(source, bin_repository, output)
    output = Path(output)
    runtime = load(output/'runtime.json');verify_runtime(runtime)
    before = _inventory(output/'source')
    for row in design['rows']:
        name = row['name'];print('DIAGNOSTIC', name, flush=True)
        result = run_job('diagnostic-evaluate', output/'jobs'/(name+'.json'),
            output/'source/runs'/name/'native'/row['source_package'],
            output/'runtime.json', output/'runs'/name, 1800.)
        require(result['execution'] == 'completed' and result['validity'] == 'valid',
                'stock_diagnostic_native_execution_incomplete')
    require(before == _inventory(output/'source'), 'stock_diagnostic_source_mutated')
    verify_runtime(runtime)
    result = audit(output);_write(output/'analysis.json', result)
    return result


def audit(directory):
    directory = Path(directory)
    design = load(directory/'design.json')
    require(design == _signed({k: v for k, v in design.items() if k != 'sha256'}) and
            set(design) == {'kind', 'schema_version', 'rows', 'trials_per_model', 'diagnostic_only',
                'training_completed', 'calibration_performed', 'historical_presentation_reproduced',
                'scientific_verdict', 'sha256'} and design['kind'] == 'stock_stopped_phasea_diagnostic' and
            type(design['schema_version']) is int and design['schema_version'] == 1 and
            design['trials_per_model'] == 8 and design['diagnostic_only'] is True and
            design['training_completed'] is design['calibration_performed'] is
            design['historical_presentation_reproduced'] is False and design['scientific_verdict'] is None,
            'stock_diagnostic_invalid_design')
    source = audit_source(directory/'source')
    rows = {r['name']: r for r in source['rows']}
    require(len(design['rows']) == len(rows) == 4 and
            {r['name'] for r in design['rows']} == set(rows), 'stock_diagnostic_missing_case')
    require(load(directory/'runtime.json') == load(directory/'source/runtime.json'),
            'stock_diagnostic_runtime_changed')
    matrix = load(directory/'matrix.json');results = []
    for row in design['rows']:
        name = row['name'];native_source = directory/'source/runs'/name/'native'
        original = rows[name];execution = load(native_source/'execution.json')
        package = load(native_source/execution['package_path'])
        job = job_for(original, package, matrix)
        validate_job('diagnostic-evaluate', job, load_case(native_source/execution['package_path']))
        expected = {'name': name, 'topology': original['topology'],
                    'initial_threshold': original['initial_threshold'],
                    'source_package': execution['package_path'], 'source_model_revision': original['model_revision'],
                    'job_sha256': job['sha256']}
        require(row == expected and load(directory/'jobs'/(name+'.json')) == job,
                'stock_diagnostic_job_or_source_changed')
        folder = directory/'runs'/name
        audit_run_manifest(folder/'run-manifest.json')
        manifest = load(folder/'run-manifest.json')
        require(manifest['execution'] == 'completed' and manifest['validity'] == 'valid' and
                load(folder/'process/runtime.json') == load(directory/'runtime.json'),
                'stock_diagnostic_incomplete_or_runtime_changed')
        model = load(folder/'native/model.json')
        require(model == load(folder/'native/model-after.json') and model['source_solo'] == package,
                'stock_diagnostic_frozen_source_changed')
        initial = load(native_source/'initial-state.json')['identity']
        audit_final_stock(initial, model['neuron']['graph']['identity'])
        metrics = manifest['analysis']['metrics']
        require(metrics['diagnostic_only'] is True and metrics['training_completed'] is False and
                metrics['training_certificate_present'] is False and metrics['evaluation_verdict'] is None,
                'stock_diagnostic_false_training_verdict')
        results.append({'name': name, 'source_model_revision': original['model_revision'], 'metrics': metrics})
    return {'kind': 'stock_stopped_phasea_diagnostic_analysis', 'schema_version': 1,
            'execution': 'completed', 'validity': 'valid', 'models': results, 'trials': 32,
            'diagnostic_only': True, 'training_completed': False, 'scientific_verdict': None}
