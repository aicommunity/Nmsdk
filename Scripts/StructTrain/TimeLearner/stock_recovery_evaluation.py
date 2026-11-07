"""Frozen eight-pattern responses of every actual recovery-study model.

Completed models use native solo export; unfinished models use the explicitly
diagnostic native import path. Neither path repairs physics or selects a new
threshold. All observations retain their training provenance.
"""
from copy import deepcopy
import hashlib
import html
from pathlib import Path

from .learned_evidence import load_case as load_completed
from .native_evidence import load, require
from .native_pipeline_worker import _snapshot_source, audit_run_manifest, run_job, validate_job
from .n1_protocol_robustness import _signed, _write
from .phasea_matrix import from_git, trial_design
from .process_runner import verify_runtime
from .stock_recovery_study import audit as audit_training
from .stock_stopped_evaluation import job_for as diagnostic_job
from .stock_threshold_study import audit_final_stock
from .stopped_evidence import load_case as load_stopped


def _export_job(package):
    return _signed({'kind': 'timelearner_native_recognition_export_job', 'schema_version': 1,
                    'implementation_id': package['implementation_id'], 'source_solo': deepcopy(package),
                    'conversion_spec': {'schema_version': 1, 'mode': 'identity', 'resistance_bounds': []}})


def _evaluation_job(row, package, matrix, recognition=None):
    if not row['completed_boundary']:
        require(recognition is None, 'recovery_diagnostic_cannot_replace_source')
        return diagnostic_job(row, package, matrix)
    require(package['kind'] == 'timelearner_completed_state' and recognition is not None,
            'recovery_completed_export_required')
    model = package['configuration']['model'];run_id = row['name']+'/frozen-phasea'
    trials = trial_design(matrix, model['initial_isi'], run_id, duration=2., rotations=1)
    return _signed({'kind': 'timelearner_native_evaluation_job', 'schema_version': 1,
        'owner_class': 'NNeuronTimeLearner'+('Branch' if model['branch'] else ''),
        'implementation_id': package['implementation_id'], 'source_recognition': deepcopy(recognition),
        'maximum_model_ticks': sum(round(t['duration']*2000)+4 for t in trials),
        'run_id': run_id, 'coverage_policy': 'per_trial_windows',
        'criterion': {'id': 'post_anchor_target_whole_window_foil_v1', 'anchor': 'onset',
                      'begin_offset': 0., 'end_offset': None, 'reject_target_outside_window': True},
        'trials': trials})


def _source(directory, row):
    path = directory/'sources'/row['name']/row['source_package']
    require(hashlib.sha256(path.read_bytes()).hexdigest() == row['source_package_sha256'],
            'recovery_evaluation_source_package_changed')
    return path, (load_completed if row['completed_boundary'] else load_stopped)(path)


def prepare(source, bin_repository, output):
    source, output = Path(source).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(source) and
            not source.is_relative_to(output), 'recovery_evaluation_output_overlap')
    # A partial Train matrix cannot silently become the evaluation population.
    training = audit_training(source)
    design = load(source/'design.json')
    output.mkdir(parents=True)
    for name in ('sources', 'expected', 'jobs'):
        (output/name).mkdir()
    _write(output/'training-design.json', design);_write(output/'training-analysis.json', training)
    matrix = from_git(bin_repository);_write(output/'matrix.json', matrix)
    _write(output/'runtime.json', load(source/'runtime.json'))
    actual = {r['name']: r for r in training['rows']};rows = []
    for declared in design['rows']:
        row = {**declared, **actual[declared['name']]};native = source/'runs'/row['name']/'native'
        execution = load(native/'execution.json');path = native/execution['package_path']
        snapshot = _snapshot_source(path, output/'sources'/row['name'], diagnostic=not row['completed_boundary'])
        row.update(source_package=snapshot.name,
                   source_package_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        package = load(snapshot)
        require(package['model_revision'] == row['model_revision'] and
                package['configuration']['model']['initial_threshold'] == row['initial_threshold'],
                'recovery_evaluation_source_identity_changed')
        _write(output/'expected'/(row['name']+'.json'), load(source/'expected'/(row['name']+'.json')))
        if row['completed_boundary']:
            job = _export_job(package);mode = 'export'
        else:
            job = _evaluation_job(row, package, matrix);mode = 'diagnostic-evaluate'
        validate_job(mode, job, _source(output, row)[1])
        _write(output/'jobs'/(row['name']+'.json'), job)
        rows.append(row)
    result = _signed({'kind': 'stock_recovery_frozen_evaluation_design', 'schema_version': 1,
                      'rows': rows, 'trials_per_model': 8, 'duration': 2., 'rotations': 1,
                      'reset_policy': 'reset_per_trial', 'threshold_selection': 'inherited_fixed',
                      'calibration_performed': False, 'independent_patterns': False,
                      'historical_presentation_reproduced': False, 'scientific_verdict': None})
    _write(output/'design.json', result)
    return result


def run(source, bin_repository, output):
    output = Path(output);design = prepare(source, bin_repository, output)
    verify_runtime(load(output/'runtime.json'))
    (output/'runs').mkdir();(output/'exports').mkdir()
    matrix = load(output/'matrix.json')
    for row in design['rows']:
        name = row['name'];path, case = _source(output, row)
        if row['completed_boundary']:
            print('EXPORT', name, flush=True)
            result = run_job('export', output/'jobs'/(name+'.json'), path,
                             output/'runtime.json', output/'exports'/name, 1800.)
            require(result['execution'] == 'completed' and result['validity'] == 'valid',
                    'recovery_native_export_failed')
            recognition = load(output/'exports'/name/'native/model.json')
            job = _evaluation_job(row, case[0], matrix, recognition)
            validate_job('evaluate', job, case)
            job_path = output/'jobs'/(name+'-evaluate.json');_write(job_path, job);mode = 'evaluate'
        else:
            job_path = output/'jobs'/(name+'.json');mode = 'diagnostic-evaluate'
        print(mode.upper(), name, flush=True)
        result = run_job(mode, job_path, path, output/'runtime.json', output/'runs'/name, 1800.)
        require(result['execution'] == 'completed' and result['validity'] == 'valid',
                'recovery_frozen_evaluation_incomplete')
    result = audit(output);_write(output/'analysis.json', result)
    return result


def audit(directory):
    directory = Path(directory).resolve(strict=True)
    design = load(directory/'design.json');training = load(directory/'training-analysis.json')
    original = load(directory/'training-design.json');matrix = load(directory/'matrix.json')
    require(design == _signed(design) and design['kind'] == 'stock_recovery_frozen_evaluation_design' and
            type(design['schema_version']) is int and design['schema_version'] == 1 and
            design['trials_per_model'] == 8 and design['duration'] == 2. and design['rotations'] == 1 and
            design['reset_policy'] == 'reset_per_trial' and design['threshold_selection'] == 'inherited_fixed' and
            design['calibration_performed'] is design['independent_patterns'] is
            design['historical_presentation_reproduced'] is False and design['scientific_verdict'] is None,
            'recovery_evaluation_design_changed')
    require(original == _signed(original) and len(design['rows']) == 8 and
            len({r['name'] for r in design['rows']}) == 8 and
            {r['name'] for r in design['rows']} == {r['name'] for r in original['rows']} ==
            {r['name'] for r in training['rows']}, 'recovery_evaluation_population_changed')
    actual = {r['name']: r for r in training['rows']};declared = {r['name']: r for r in original['rows']}
    models = []
    for row in design['rows']:
        name = row['name']
        expected_row = {**declared[name], **actual[name]}
        require({k: v for k, v in row.items() if k not in ('source_package', 'source_package_sha256')} == expected_row,
                'recovery_evaluation_training_role_changed')
        _, case = _source(directory, row)
        folder = directory/'runs'/name;manifest = load(folder/'run-manifest.json')
        audit_run_manifest(folder/'run-manifest.json')
        recognition = None
        if row['completed_boundary']:
            export = directory/'exports'/name
            audit_run_manifest(export/'run-manifest.json')
            require(load(export/'input/job.json') == _export_job(case[0]), 'recovery_export_source_changed')
            recognition = load(export/'native/model.json')
        expected_job = _evaluation_job(row, case[0], matrix, recognition)
        require(load(folder/'input/job.json') == expected_job and
                manifest['execution'] == 'completed' and manifest['validity'] == 'valid' and
                load(folder/'process/runtime.json') == load(directory/'runtime.json'),
                'recovery_evaluation_job_or_runtime_changed')
        model = load(folder/'native/model.json')
        require(model == load(folder/'native/model-after.json') and model['source_solo'] == case[0],
                'recovery_evaluation_frozen_model_changed')
        audit_final_stock(load(directory/'expected'/(name+'.json')), model['neuron']['graph']['identity'])
        metrics = manifest['analysis']['metrics']
        if not row['completed_boundary']:
            require(metrics['diagnostic_only'] is True and metrics['training_completed'] is False and
                    metrics['training_certificate_present'] is False and metrics['evaluation_verdict'] is None,
                    'recovery_diagnostic_false_certificate')
        models.append({'name': name, 'source_completed': row['completed_boundary'],
                       'source_model_revision': row['model_revision'], 'metrics': metrics})
    return {'kind': 'stock_recovery_frozen_evaluation_analysis', 'schema_version': 1,
            'validity': 'valid', 'models': models, 'trials': 64,
            'completed_training_models': sum(r['source_completed'] for r in models),
            'calibration_performed': False, 'independent_patterns': False, 'scientific_verdict': None}


def report(directory, output):
    from .live_pipeline_reports import render_pipeline_run
    directory, output = Path(directory).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(directory) and
            not directory.is_relative_to(output), 'recovery_report_requires_separate_cache')
    result = audit(directory);output.mkdir(parents=True);_write(output/'analysis.json', result)
    reports = [];pairs = 0
    for row in result['models']:
        rendered = render_pipeline_run(directory/'runs'/row['name']/'run-manifest.json', output/row['name'])
        require(rendered.get('diagnostic_only', False) is (not row['source_completed']) and
                rendered['source_operation'] == ('evaluate' if row['source_completed'] else 'diagnostic-evaluate'),
                'recovery_report_training_role_changed')
        pairs += rendered['recognition_trial_soma_pairs']
        reports.append({'name': row['name'], 'path': row['name']+'/index.html',
                        'source_completed': row['source_completed'],
                        'trial_soma_pairs': rendered['recognition_trial_soma_pairs']})
    require(pairs == 160, 'recovery_report_missing_pattern_or_soma')
    _write(output/'manifest.json', {'kind': 'stock_recovery_temporal_cache', 'schema_version': 1,
                                  'reports': reports, 'trials': 64, 'trial_soma_pairs': pairs,
                                  'visual_acceptance_complete': False, 'scientific_verdict': None})
    links = ''.join('<li><a href="'+html.escape(r['path'], quote=True)+'">'+html.escape(r['name'])+'</a></li>'
                    for r in reports)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Stock recovery responses</title>'
        '<h1>Frozen responses; unfinished Train remains diagnostic</h1><ul>'+links+'</ul>', encoding='utf-8')
    return {'trials': 64, 'trial_soma_pairs': pairs, 'scientific_verdict': None}
