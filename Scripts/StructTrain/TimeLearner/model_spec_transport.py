"""Exact positive N1 job replay, then measured calibration and fresh import.

Two-input engineering LT profile. This transport control preserves the pinned
production job and original tolerances. It is not stock scientific evaluation.
"""
import contextlib
from copy import deepcopy
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

from .native_evidence import load, require
from .native_calibration_worker import _signed, _write, audit_run_manifest as audit_calibration
from .native_pipeline_worker import audit_run_manifest, validate_job
from .learned_evidence import audit_learned_state, load_case
from .model_identity import canonical_model_sha256 as sha

BASELINE = 'bcbd30f1d87e352825e6c8400c5b929eff184ae5'
BASELINE_PATH = 'Reports/StructTrain/TimeLearner/s07-native-n1-refined-normal-a1/'
CRITERION = {'id': 'post_anchor_target_whole_window_foil_v1', 'anchor': 'onset',
             'begin_offset': 0., 'end_offset': None, 'reject_target_outside_window': True}


def inventory(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file()}


def prepare(repository, output):
    """Restore the exact Git primaries and preregister all four cold jobs."""
    def blob(name):
        return subprocess.check_output(['git', '-C', str(repository), 'show', BASELINE+':'+BASELINE_PATH+name])
    sums = json.loads(blob('SHA256SUMS.json'))
    raw, manifest_raw = blob('primary.tar.xz'), blob('manifest.json')
    require(hashlib.sha256(raw).hexdigest() == sums['primary.tar.xz'] and
            hashlib.sha256(manifest_raw).hexdigest() == sums['manifest.json'], 'transport_baseline_digest_mismatch')
    manifest = json.loads(manifest_raw)
    archive = tarfile.open(fileobj=io.BytesIO(raw), mode='r:xz')
    expected = {r['path']: r for r in manifest['records']}
    members = archive.getmembers()
    require(len(expected) == len(members) and {m.name for m in members} == set(expected),
            'transport_baseline_member_set_mismatch')
    payload = {}
    for member in members:
        name = PurePosixPath(member.name)
        require(member.isfile() and not name.is_absolute() and '..' not in name.parts,
                'transport_baseline_unsafe_member')
        data = archive.extractfile(member).read()
        require(len(data) == expected[member.name]['bytes'] and
                hashlib.sha256(data).hexdigest() == expected[member.name]['sha256'],
                'transport_baseline_member_digest_mismatch')
        payload[member.name] = data
    require(shutil.disk_usage(output.parent).free >= 2*1024**3, 'transport_primary_storage_capacity')
    output.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        p = output/'baseline'/name;p.parent.mkdir(parents=True, exist_ok=True);p.write_bytes(data)
    baseline = output/'baseline/corpus'
    index = load(baseline/'index.json')
    require(index['kind'] == 'native_n1_proposal_controls' and len(index['records']) == 2,
            'transport_baseline_scope')
    (output/'jobs').mkdir();rows = []
    for record in index['records']:
        folder = baseline/record['name']
        audit_run_manifest(folder/'run-manifest.json')
        case = load_case(folder/'native/train_learned_state.json')
        require(audit_learned_state(*case)['exact'], 'transport_baseline_not_exact')
        original = load(folder/'input/job.json')
        validate_job('train', original)
        model = original['configuration']['model']
        require(model['schema_version'] == 1 and model['initial_isi'] == [.01, .03] and
                model['normalization'] == 'N1' and model['frequency_hz'] == 2000,
                'transport_baseline_model_scope')
        top = 'Branch' if model['branch'] else 'Classic'
        for version in (1, 2):
            job = deepcopy(original)
            if version == 2:
                job['configuration']['model'].update(schema_version=2, initial_threshold=1.)
                job.pop('sha256');job = _signed(job)
            validate_job('train', job)
            name = top+'-v'+str(version)
            _write(output/'jobs'/(name+'-train.json'), job)
            rows.append({'name': name, 'topology': top, 'model_spec_version': version,
                         'original_job_sha256': original['sha256'], 'job_sha256': job['sha256'],
                         'baseline_name': record['name'], 'baseline_solo_sha256': case[0]['sha256']})
    require(len({r['name'] for r in rows}) == 4, 'transport_duplicate_condition')
    plan = {'kind': 'native_model_spec_transport_plan', 'schema_version': 1,
            'baseline_commit': BASELINE, 'baseline_archive_sha256': sums['primary.tar.xz'],
            'conditions': rows, 'engineering_lt_profile': True,
            'patterns': [[.01, .03], [.01, .24]], 'criterion': CRITERION,
            'duration': .4, 'maximum_samples': 805, 'calibration_protocol': 'historical_same_matrix',
            'threshold_grid_rule': 'measured_nonspiking_peak_brackets_plus_inherited_v1',
            'scientific_verdict': None}
    _write(output/'plan.json', plan)
    return plan


def requests(name, *, frozen=False):
    patterns = [([.01, .03], 'target'), ([.01, .24], 'foil')]
    order = patterns+list(reversed(patterns)) if frozen else patterns
    return [{'run_id': name, 'trial_id': name+'/'+str(i), 'sample_id': label,
             'label': label, 'pattern_hash': sha(pattern), 'pattern_isi': pattern,
             'duration': .4, 'maximum_samples': 805, 'reset_policy': 'reset_per_trial',
             'record_threshold_potential': True} for i, (pattern, label) in enumerate(order)]


def run(prepared, runtime, output):
    from .__main__ import main as cli
    from .recognition_metrics import load_evaluation
    from .calibrated_evidence import audit_calibrated_state
    require(output != prepared and not output.exists(), 'transport_output_must_be_new')
    plan = load(prepared/'plan.json')
    require(plan['kind'] == 'native_model_spec_transport_plan' and plan['baseline_commit'] == BASELINE
            and len(plan['conditions']) == 4, 'transport_unknown_plan')
    before = inventory(prepared)
    output.mkdir(parents=True);(output/'jobs').mkdir();(output/'runs').mkdir()
    _write(output/'plan.json', plan)
    rows = []

    def invoke(mode, name, job, source=None):
        path = output/'jobs'/(name+'.json');_write(path, job)
        folder = output/'runs'/name
        args = (['calibrate', 'run'] if mode == 'calibrate' else [mode])+[str(path)]
        if source is not None:args += ['--source-solo', str(source)]
        args += ['--runtime-manifest', str(runtime), '--wall-seconds', '1800', '--output', str(folder)]
        print('BEGIN', name, flush=True)
        with (output/(name+'.log')).open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            code = cli(args)
        _write(output/(name+'-cli.json'), {'exit_code': code, 'mode': mode})
        require(code == 0, 'transport_operation_failed:'+name)
        audit = (audit_calibration if mode == 'calibrate' else audit_run_manifest)(folder/'run-manifest.json')
        require(load(folder/'run-manifest.json')['execution'] == 'completed', 'transport_incomplete_operation:'+name)
        print('END', name, flush=True)
        return folder, audit

    for condition in plan['conditions']:
        name = condition['name'];job = load(prepared/'jobs'/(name+'-train.json'))
        require(job['sha256'] == condition['job_sha256'], 'transport_declared_job_changed')
        train, train_audit = invoke('train', name+'-train', job)
        source = train/'native/train_learned_state.json';case = load_case(source)
        require(audit_learned_state(*case)['exact'], 'transport_replay_not_exact:'+name)
        initial = load(train/'native/initial-state.json')
        previous = load(prepared/'baseline/corpus'/condition['baseline_name']/'native/initial-state.json')
        require(initial['identity'] == previous['identity'] and initial['parameters'] == previous['parameters'],
                'transport_original_effective_model_changed:'+name)
        implementation = case[0]['implementation_id']
        exported, export_audit = invoke('export', name+'-export', _signed({
            'kind': 'timelearner_native_recognition_export_job', 'schema_version': 1,
            'implementation_id': implementation, 'source_solo': case[0],
            'conversion_spec': {'schema_version': 1, 'mode': 'identity', 'resistance_bounds': []}}), source)
        model = load(exported/'native/model.json')

        def evaluate(package, suffix, frozen=False):
            run_id = name+'/'+suffix
            return invoke('evaluate', name+'-'+suffix, _signed({
                'kind': 'timelearner_native_evaluation_job', 'schema_version': 1,
                'owner_class': job['owner_class'], 'implementation_id': implementation,
                'source_recognition': package, 'maximum_model_ticks': 200000, 'run_id': run_id,
                'coverage_policy': 'per_trial_windows', 'criterion': CRITERION,
                'trials': requests(run_id, frozen=frozen)}), source)

        measured, measure_audit = evaluate(model, 'proposal')
        _, observations = load_evaluation(measured/'native/evaluation.json')
        require(len(observations) == 2 and all(o['complete'] and o['valid'] and o['spike_count'] == 0
                                             for o in observations), 'transport_peak_proposal_requires_nonspiking_full_windows')
        peaks = [max(s['lt_potential'] for s in o['samples'] if s['time'] >= o['stimulus_onset']) for o in observations]
        require(all(math.isfinite(p) and p > 0 for p in peaks), 'transport_invalid_measured_peak')
        unique = sorted(set(peaks));inherited = model['neuron']['metadata']['calibration']['threshold']
        thresholds = sorted(set([.9*unique[0], 1.1*unique[-1], inherited]+
                                [a+.5*(b-a) for a, b in zip(unique, unique[1:])]))
        _write(output/'jobs'/(name+'-proposal.json'), {'peaks': peaks, 'thresholds': thresholds,
                'source_run_manifest_sha256': load(measured/'run-manifest.json')['sha256'],
                'rule': plan['threshold_grid_rule'], 'selection_verdict': None})
        grid, grid_audit = invoke('calibrate', name+'-calibrate', _signed({
            'kind': 'timelearner_native_calibration_job', 'schema_version': 1,
            'owner_class': job['owner_class'], 'implementation_id': implementation, 'frequency_hz': 2000,
            'maximum_model_ticks': 200000, 'source_recognition': model,
            'thresholds': thresholds, 'maximum_candidates': len(thresholds),
            'specification': {'protocol': 'historical_same_matrix', 'data_partition_id': 'engineering-two-pattern-primary-pair-v1',
                'attempt_id': name+'/grid', 'clock_id': 'native-2000Hz',
                'criterion': {k: v for k, v in CRITERION.items() if k != 'id'}},
            'trials': requests(name+'/declared-calibration')}), source)
        transaction = load(grid/'native/transaction.json');final = load(grid/'native/model.json')
        row = {**condition, 'training_audit': train_audit, 'export_audit': export_audit,
               'proposal_audit': measure_audit, 'calibration_audit': grid_audit,
               'calibration_status': transaction['status'], 'source_solo_sha256': case[0]['sha256'],
               'fresh_frozen_evaluation': None, 'scientific_verdict': None}
        if transaction['status'] == 'calibrated':
            audit_calibrated_state(final, case)
            require(final['threshold'] != 1., 'transport_selected_threshold_did_not_change')
            frozen, frozen_audit = evaluate(final, 'frozen', True)
            require(load(frozen/'native/model.json') == final == load(frozen/'native/model-after.json'),
                    'transport_calibrated_frozen_package_changed')
            row['fresh_frozen_evaluation'] = {'audit': frozen_audit, 'model_sha256': final['sha256'],
                                             'threshold': final['threshold']}
        rows.append(row);_write(output/'progress.json', rows)
    require(before == inventory(prepared), 'transport_prepared_sources_changed')
    result = {'kind': 'native_model_spec_transport_result', 'schema_version': 1,
              'conditions': rows, 'prepared_primary_unchanged': True,
              'all_calibrated_transfers_completed': all(r['fresh_frozen_evaluation'] is not None for r in rows),
              'engineering_lt_profile': True, 'statistical_independence_verified': False, 'scientific_verdict': None}
    _write(output/'index.json', result)
    return result
