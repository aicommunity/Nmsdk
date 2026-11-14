"""Preregistered order/reset/observed-quiet-tail probes of two saved N1 models.

Thresholds come from the earlier measured grid. Every new native operation has
one declared threshold; its transaction status is not a successful calibration
or an independent-pattern test claim. No Train or physical-profile edit occurs.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import tarfile

from .calibration_transaction_evidence import audit_native_calibration_transaction
from .condition import CONDITION_ROLES, ConditionSpec, artifact
from .learned_evidence import audit_learned_state, load_case
from .model_identity import canonical_model_sha256 as sha
from .native_calibration_worker import audit_run_manifest, run_job, validate_job
from .native_evidence import after, load, require
from .process_runner import verify_runtime
from .recognition_metrics import score_threshold_candidate


THRESHOLDS = {'Classic': .005104094175900908, 'Branch': .01023534737566667}
POLICIES = ('reset_per_trial', 'preserve_neuron_dynamics')
DURATIONS = (.4, 1.6)


def _write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def _signed(value):
    body = {k: v for k, v in value.items() if k != 'sha256'}
    return {**body, 'sha256': sha(body)}


def _inventory(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def unpack_calibration(bundle, output):
    """Verify the original declared archive, including every primary byte."""
    bundle = Path(bundle).resolve(strict=True)
    sums = load(bundle/'SHA256SUMS.json')
    from .external_archive import locate
    require(set(sums) == {'README.md', 'manifest.json', 'primary.tar.xz'}, 'n1_source_bundle_checksum_schema')
    for name, digest in sums.items():
        require(hashlib.sha256(locate(bundle/name).read_bytes()).hexdigest() == digest, 'n1_source_bundle_checksum')
    manifest = load(bundle/'manifest.json')
    require(manifest['kind'] == 'positive_n1_measured_calibration_primary' and
            type(manifest['schema_version']) is int and manifest['schema_version'] == 1 and manifest['operations'] == 2 and
            manifest['complete_pattern_trials'] == 160, 'n1_source_calibration_scope')
    expected = {r['path']: r for r in manifest['records']}
    require(len(expected) == len(manifest['records']) and
            all(type(r['bytes']) is int and r['bytes'] >= 0 for r in expected.values()) and
            sum(r['bytes'] for r in expected.values()) <= 512*1024**2, 'n1_source_bundle_budget')
    files = {}
    with tarfile.open(locate(bundle/'primary.tar.xz'), 'r:xz') as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            require(member.isfile() and not name.is_absolute() and '..' not in name.parts and
                    name.as_posix() == member.name and '\\' not in member.name and ':' not in member.name and
                    member.name in expected and member.name not in files, 'n1_source_bundle_member')
            row = expected[member.name]
            require(member.size == row['bytes'], 'n1_source_bundle_member_size')
            raw = archive.extractfile(member).read()
            require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'n1_source_bundle_member_digest')
            files[member.name] = raw
    require(set(files) == set(expected), 'n1_source_bundle_incomplete')
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in files.items():
        target = output/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    _write(output/'source-bundle.json', {'manifest': manifest, 'archive_sha256': sums['primary.tar.xz']})
    return manifest


def _trials(patterns, identifier, policy, duration, rotations):
    result = []
    for rotation in range(rotations):
        for position, old in enumerate(patterns[rotation:]+patterns[:rotation]):
            q = deepcopy(old)
            q.update(run_id=identifier+'/search', trial_id=f'{identifier}/rotation-{rotation}/{position}',
                     reset_policy=policy, duration=duration, maximum_samples=math.ceil(duration*2000)+5)
            result.append(q)
    return result


def _condition(source, selected, trials, runtime):
    model = source['source_solo']['configuration']['model']
    protocol = [{k: q[k] for k in ('sample_id', 'label', 'pattern_hash', 'pattern_isi', 'reset_policy', 'duration')}
                for q in trials]
    payloads = {
        'algorithm': {'operation': 'fixed-preregistered-native-threshold-probe-v1',
                      'implementation_id': source['implementation_id'],
                      'native_pulse': runtime['source_closure']['Libraries/Nmsdk-PulseLib']['head'],
                      'native_rdk': runtime['source_closure']['Rdk']['head']},
        'model_spec': {'semantic_model': source['model_revision'], 'branch': model['branch'],
                       'frequency_hz': 2000, 'normalization': 'N1'},
        'storage_profiles': {k: v for k, v in source['neuron'].items() if k not in {'graph', 'metadata', 'sha256'}},
        'initial_state': {'selected_model': selected['model_revision'], 'initialization': 'native-import-reset'},
        'training_plan': {'operation': 'reuse_exact_solo_no_retraining', 'amplitude_goal': 'captured_per_input'},
        'input_data': {'patterns': [{k: q[k] for k in ('sample_id', 'label', 'pattern_hash', 'pattern_isi')}
                                  for q in trials[:8]]},
        'presentation_protocol': {'ordered_trials': protocol, 'frequency_hz': 2000,
                                  'spacing': 'fully-observed-trial-window-plus-native-boundary-step'},
        'calibration_spec': {'threshold': selected['threshold'], 'adaptation': False,
                             'selection_data': 'previous-historical-same-matrix-grid'},
        'evaluation_spec': {'window': 'actual-onset-to-complete-trial-end', 'independent_patterns': False,
                            'quiet_tail_and_observation_window_change_together': True},
        'execution_policy': {'maximum_model_ticks': 500000, 'maximum_wall_seconds': 1800},
        'randomness_spec': {'deterministic_saved_models': True, 'independent_trainings': 0},
    }
    artifacts = {role: artifact(role, payloads[role]) for role in CONDITION_ROLES}
    condition = ConditionSpec(controller_version=source['source_solo']['controller_version'], amplitude_goal='captured_per_input',
                              **{role: value['sha256'] for role, value in artifacts.items()})
    condition.resolve({value['sha256']: value for value in artifacts.values()})
    return condition.to_object(), artifacts


def prepare_study(bundle, runtime_path, output, source_evidence):
    require(re.fullmatch('[0-9a-f]{40}', source_evidence) is not None, 'n1_source_full_commit_required')
    output = Path(output)
    require(not output.exists(), 'n1_study_output_already_exists')
    runtime = load(Path(runtime_path))
    verify_runtime(runtime)
    # Source evidence is verified before any Console is launched.
    manifest = unpack_calibration(bundle, output/'source')
    require(runtime['source_closure']['root']['head'] == manifest['runtime_root'] and
            runtime['source_closure']['Libraries/Nmsdk-PulseLib']['head'] == manifest['runtime_pulse'],
            'n1_study_requires_original_scientific_runtime')
    _write(output/'runtime.json', runtime)
    (output/'jobs').mkdir()
    rows = []
    for top, threshold in THRESHOLDS.items():
        folder = output/'source/corpus/runs'/f'{top}-grid'
        audit_run_manifest(folder/'run-manifest.json')
        prior = load(folder/'native/transaction.json')
        run_manifest = load(folder/'run-manifest.json')
        source_path = folder/run_manifest['source_package_path']
        case = load_case(source_path)
        require(audit_learned_state(*case)['exact'] is True, 'n1_study_source_not_exact')
        audit_native_calibration_transaction(prior, case)
        matches = [r for r in prior['candidates'] if r['candidate']['threshold'] == threshold]
        require(len(matches) == 1, 'n1_study_missing_preregistered_candidate')
        selected = matches[0]['candidate']
        require(prior['status'] == 'nonseparable' and prior['source_restored'], 'n1_study_prior_transaction_scope')
        require({k: matches[0]['assessment']['pooled_counts'][k] for k in ('TP', 'FP', 'FN', 'TN')} ==
                {'TP': 1, 'FP': 3, 'FN': 0, 'TN': 4}, 'n1_study_prior_five_of_eight_not_verified')
        source = prior['source_recognition']
        model = case[0]['configuration']['model']
        require(model['branch'] is (top == 'Branch') and model['frequency_hz'] == 2000 and
                case[0]['protocol']['pattern_hash'] == sha([.01, .03]), 'n1_study_model_scope')
        patterns = prior['trials']
        require(len(patterns) == 8 and len({q['pattern_hash'] for q in patterns}) == 8 and
                sum(q['label'] == 'target' for q in patterns) == 1, 'n1_study_source_patterns')
        configurations = [('smoke', 'preserve_neuron_dynamics', .4, 1)] + [
            ('study', policy, duration, 8) for policy in POLICIES for duration in DURATIONS]
        for phase, policy, duration, rotations in configurations:
            name = f'{top}-{phase}-{policy}-{round(duration*1000)}ms'
            trials = _trials(patterns, name, policy, duration, rotations)
            job = _signed({'kind': 'timelearner_native_calibration_job', 'schema_version': 1,
                'owner_class': 'NNeuronTimeLearner'+('Branch' if model['branch'] else ''),
                'implementation_id': source['implementation_id'], 'frequency_hz': 2000,
                'maximum_model_ticks': 500000, 'source_recognition': source,
                'thresholds': [threshold], 'maximum_candidates': 1, 'trials': trials,
                'specification': {'protocol': 'historical_same_matrix',
                    'data_partition_id': 'n1-preregistered-candidate-protocol-robustness-v1',
                    'attempt_id': name, 'clock_id': 'native-2000Hz', 'criterion': prior['criterion']}})
            validate_job(job, case)
            condition, artifacts = _condition(source, selected, trials, runtime)
            _write(output/'jobs'/f'{name}.json', job)
            _write(output/'jobs'/f'{name}-condition.json', {'condition': condition, 'artifacts': artifacts})
            rows.append({'name': name, 'phase': phase, 'topology': top, 'reset_policy': policy,
                         'duration': duration, 'source_path': source_path.relative_to(output).as_posix(),
                         'source_solo_sha256': case[0]['sha256'], 'selected_candidate_sha256': selected['sha256'],
                         'condition_fingerprint': ConditionSpec.loads(json.dumps(condition)).fingerprint,
                         'expected_trials': len(trials)})
    # Finish the entire design before the first new native observation.
    rows.sort(key=lambda row: (row['phase'] != 'smoke', row['name']))
    design = {'kind': 'n1_fixed_candidate_protocol_robustness_design', 'schema_version': 1,
              'source_evidence': source_evidence, 'source_archive_sha256': load(output/'source/source-bundle.json')['archive_sha256'],
              'rows': rows, 'threshold_selection_frozen': True, 'independent_patterns': False,
              'scientific_verdict': None}
    _write(output/'design.json', _signed(design))
    return design


def run_study(bundle, runtime_path, output, source_evidence):
    output = Path(output)
    design = prepare_study(bundle, runtime_path, output, source_evidence)
    before = _inventory(output/'source')
    (output/'runs').mkdir()
    rows = []
    for row in design['rows']:
        print('BEGIN', row['name'], flush=True)
        result = run_job(output/'jobs'/f"{row['name']}.json", output/row['source_path'],
                         output/'runtime.json', output/'runs'/row['name'], 1800.)
        require(result['execution'] == 'completed' and result['validity'] == 'valid', 'n1_study_native_operation_failed')
        transaction = load(output/'runs'/row['name']/'native/transaction.json')
        require(len(transaction['candidates']) == 1 and
                transaction['candidates'][0]['candidate']['sha256'] == row['selected_candidate_sha256'],
                'n1_study_selected_physics_or_threshold_changed')
        measured = transaction['candidates'][0]
        metrics = _matrix_metrics(measured['matrix'], measured['candidate'], transaction['criterion'],
                                  continuous=row['reset_policy'] == 'preserve_neuron_dynamics')
        require(metrics['validity'] == 'valid' and metrics['pooled_counts'] == measured['assessment']['pooled_counts'],
                'n1_study_native_and_reader_counts_disagree')
        rows.append({'name': row['name'], 'phase': row['phase'], 'status': transaction['status'],
                     'counts': transaction['candidates'][0]['assessment']['pooled_counts']})
        _write(output/'progress.json', rows)
        print('END', row['name'], rows[-1]['counts'], flush=True)
    require(before == _inventory(output/'source'), 'n1_study_source_changed')
    _write(output/'index.json', _signed({'kind': 'n1_fixed_candidate_protocol_robustness', 'schema_version': 1,
        'records': rows, 'operations': len(rows), 'expected_search_trials': 528,
        'source_files_unchanged': len(before), 'threshold_retuning': False, 'independent_patterns': False,
        'scientific_verdict': None}))
    _write(output/'analysis.json', audit_study(output))
    return {'execution': 'completed', 'operations': len(rows), 'scientific_verdict': None}


def _matrix_metrics(matrix, candidate, criterion, *, continuous):
    requests = matrix['requests']
    trials = [{**{k: q[k] for k in ('trial_id', 'sample_id', 'label', 'pattern_hash', 'reset_policy', 'duration')},
               'presentation_index': i, 'observation': 'inline/'+q['trial_id']} for i, q in enumerate(requests)]
    return score_threshold_candidate({'kind': 'timelearner_recognition_evaluation_spec', 'schema_version': 1,
        'run_id': requests[0]['run_id'], 'model_revision': candidate['model_revision'],
        'coverage_policy': 'continuous_native_stream' if continuous else 'per_trial_windows',
        'criterion': {'id': 'post_anchor_target_whole_window_foil_v1', **criterion}, 'trials': trials},
        matrix['observations'], candidate)


def audit_study(directory):
    """Recompute every matrix, frozen candidate, order and actual interval."""
    directory = Path(directory).resolve(strict=True)
    design, index = load(directory/'design.json'), load(directory/'index.json')
    require(set(design) == {'kind', 'schema_version', 'source_evidence', 'source_archive_sha256', 'rows',
                           'threshold_selection_frozen', 'independent_patterns', 'scientific_verdict', 'sha256'} and
            design['kind'] == 'n1_fixed_candidate_protocol_robustness_design' and
            type(design['schema_version']) is int and design['schema_version'] == 1 and
            design['threshold_selection_frozen'] is True and design['independent_patterns'] is False and
            design['scientific_verdict'] is None, 'n1_study_unknown_design')
    require(set(index) == {'kind', 'schema_version', 'records', 'operations', 'expected_search_trials',
                          'source_files_unchanged', 'threshold_retuning', 'independent_patterns', 'scientific_verdict', 'sha256'} and
            index['kind'] == 'n1_fixed_candidate_protocol_robustness' and
            type(index['schema_version']) is int and index['schema_version'] == 1 and
            index['threshold_retuning'] is False and index['independent_patterns'] is False and
            index['scientific_verdict'] is None, 'n1_study_unknown_index')
    for value in [design, index]:
        require(value['sha256'] == sha({k: v for k, v in value.items() if k != 'sha256'}), 'n1_study_digest')
    expected = {(top, policy, duration) for top in THRESHOLDS for policy in POLICIES for duration in DURATIONS}
    study = [row for row in design['rows'] if row['phase'] == 'study']
    require(len(study) == 8 and {(r['topology'], r['reset_policy'], r['duration']) for r in study} == expected and
            len(design['rows']) == len(index['records']) == len({r['name'] for r in design['rows']}) == 10 and
            {r['name'] for r in design['rows']} == {r['name'] for r in index['records']}, 'n1_study_incomplete_conditions')
    require({(r['topology'], r['reset_policy'], r['duration'], r['expected_trials'])
             for r in design['rows'] if r['phase'] == 'smoke'} ==
            {(top, 'preserve_neuron_dynamics', .4, 8) for top in THRESHOLDS}, 'n1_study_smoke_scope')
    claimed = {row['name']: row for row in index['records']}
    source_receipt = load(directory/'source/source-bundle.json')
    source_records = source_receipt['manifest']['records']
    require(design['source_archive_sha256'] == source_receipt['archive_sha256'], 'n1_study_source_archive_changed')
    actual_source = _inventory(directory/'source')
    require(len(actual_source) == index['source_files_unchanged'] == len(source_records)+1 and
            set(actual_source) == {r['path'] for r in source_records} | {'source-bundle.json'} and
            all(actual_source[r['path']] == r['sha256'] for r in source_records), 'n1_study_source_snapshot_changed')
    rows = []
    search_trials = confirmation_trials = 0
    for row in design['rows']:
        source = load_case(directory/row['source_path'])
        require(source[0]['sha256'] == row['source_solo_sha256'], 'n1_study_source_solo_changed')
        job = load(directory/'jobs'/f"{row['name']}.json")
        validate_job(job, source)
        prior_folder = directory/'source/corpus/runs'/f"{row['topology']}-grid"
        audit_run_manifest(prior_folder/'run-manifest.json')
        prior = load(prior_folder/'native/transaction.json')
        audit_native_calibration_transaction(prior, source)
        selected = [r['candidate'] for r in prior['candidates']
                    if r['candidate']['threshold'] == THRESHOLDS[row['topology']]]
        require(len(selected) == 1 and selected[0]['sha256'] == row['selected_candidate_sha256'] and
                job['source_recognition'] == prior['source_recognition'], 'n1_study_not_original_selected_model')
        require(job['trials'] == _trials(prior['trials'], row['name'], row['reset_policy'], row['duration'],
                                        8 if row['phase'] == 'study' else 1), 'n1_study_rotation_design_changed')
        require(job['thresholds'] == [THRESHOLDS[row['topology']]] and job['maximum_candidates'] == 1,
                'n1_study_threshold_retuned')
        evidence = load(directory/'jobs'/f"{row['name']}-condition.json")
        condition = ConditionSpec.loads(json.dumps(evidence['condition']))
        condition.resolve({a['sha256']: a for a in evidence['artifacts'].values()})
        require(condition.fingerprint == row['condition_fingerprint'], 'n1_study_condition_changed')
        run = directory/'runs'/row['name']
        audit_run_manifest(run/'run-manifest.json')
        transaction = load(run/'native/transaction.json')
        audit_native_calibration_transaction(transaction, source)
        require(len(transaction['candidates']) == 1, 'n1_study_candidate_inventory')
        record = transaction['candidates'][0]
        candidate, matrix = record['candidate'], record['matrix']
        require(candidate['sha256'] == row['selected_candidate_sha256'], 'n1_study_frozen_candidate_changed')
        runtime = load(directory/'runtime.json')
        require(runtime == load(run/'process/runtime.json'), 'n1_study_runtime_changed')
        expected_condition, expected_artifacts = _condition(transaction['source_recognition'], candidate, job['trials'], runtime)
        require(evidence == {'condition': expected_condition, 'artifacts': expected_artifacts}, 'n1_study_condition_not_effective')
        require(len(matrix['requests']) == row['expected_trials'] and
                all(q['reset_policy'] == row['reset_policy'] and q['duration'] == row['duration'] for q in matrix['requests']),
                'n1_study_presentation_protocol_changed')
        require([(q['sample_id'], q['label'], q['pattern_hash']) for q in matrix['requests']] ==
                [(q['sample_id'], q['label'], q['pattern_hash']) for q in job['trials']], 'n1_study_trial_order_changed')
        metrics = _matrix_metrics(matrix, candidate, transaction['criterion'],
                                  continuous=row['reset_policy'] == 'preserve_neuron_dynamics')
        require(metrics['validity'] == 'valid', 'n1_study_invalid_observations')
        require(claimed[row['name']]['counts'] == metrics['pooled_counts'] and
                claimed[row['name']]['status'] == transaction['status'] and
                claimed[row['name']]['phase'] == row['phase'], 'n1_study_producer_metrics_disagree')
        if row['phase'] == 'study':
            positions = {i % 8 for i, q in enumerate(matrix['requests']) if q['label'] == 'target'}
            require(positions == set(range(8)), 'n1_study_target_positions_missing')
        observations = matrix['observations']
        intervals = [b['stimulus_times'][0]-a['stimulus_times'][-1]
                     for a, b in zip(observations, observations[1:])]
        require(all(math.isfinite(t) and t > 0 for t in intervals), 'n1_study_invalid_actual_intervals')
        late_foil_spikes = sum(sum(after(t, o['begin']+.4) for t in o['spike_times'])
                              for o in observations if o['label'] == 'foil')
        rows.append({'name': row['name'], 'phase': row['phase'], 'topology': row['topology'],
                     'duration': row['duration'], 'reset_policy': row['reset_policy'],
                     'condition_fingerprint': condition.fingerprint, 'metrics': metrics,
                     'actual_quiet_interval_min': min(intervals), 'actual_quiet_interval_max': max(intervals),
                     'foil_spikes_after_initial_400ms': late_foil_spikes, 'transaction_status': transaction['status']})
        search_trials += len(observations)
        confirmation_trials += len(transaction['confirmation']['observations'])
    require(search_trials == index['expected_search_trials'] == 528, 'n1_study_search_trial_inventory')
    return {'kind': 'n1_fixed_candidate_protocol_robustness_analysis', 'schema_version': 1,
            'execution': 'completed', 'validity': 'valid', 'rows': rows, 'search_trials': search_trials,
            'confirmation_trials': confirmation_trials, 'threshold_retuning': False,
            'independent_patterns': False, 'independent_trainings': 0, 'scientific_verdict': None}
