"""Cold whole-burst characterization; never a Train or recognition verdict.

This module prepares the strict public native job and audits its primary
artifacts. Process ownership/runtime evidence remain the supervisor's task.
"""
from copy import deepcopy
from pathlib import Path

from .native_calibration_worker import _digest, _evidence_boundary, _signed
from .native_evidence import audit_probe, count, equal, load, number, require
from .native_model_spec import audit_initial_threshold, validate_model_spec
from .native_pipeline_worker import _artifact_records, validate_job as validate_training_job
from .model_identity import canonical_model_sha256 as sha
from .probe_diagnostics import read_partial_probe, audit_recorded_wave_diagnostics

JOB_FIELDS = {'kind', 'schema_version', 'owner_class', 'implementation_id', 'model', 'profile_archives',
              'stimulus_profile', 'probe', 'maximum_model_ticks', 'maximum_wall_seconds', 'sha256'}
PROBE_FIELDS = {'run_id', 'trial_id', 'sample_id', 'protocol_revision', 'input_index', 'duration',
                'maximum_sample_gap', 'minimum_amplitude', 'maximum_samples', 'record_spikes', 'peak_selection', 'window'}


@_evidence_boundary
def validate_job(job):
    require(type(job) is dict and set(job) == JOB_FIELDS and job['kind'] == 'timelearner_native_probe_job'
            and type(job['schema_version']) is int and job['schema_version'] == 1, 'unknown_characterization_job')
    _digest(job)
    validate_model_spec(job['model'])
    model, probe = job['model'], job['probe']
    require(type(model['branch']) is bool and job['owner_class'] == 'NNeuronTimeLearner'+('Branch' if model['branch'] else ''),
            'characterization_owner_mismatch')
    require(type(job['implementation_id']) is str and bool(job['implementation_id'].strip()), 'characterization_implementation_missing')
    require(type(model['inputs']) is list and len(model['inputs']) > 0, 'characterization_inputs_missing')
    require(type(job['profile_archives']) is list and len(job['profile_archives']) <= 32 and
            all(type(p) is dict for p in job['profile_archives']), 'characterization_profiles_invalid')
    require(type(probe) is dict and set(probe) == PROBE_FIELDS, 'characterization_probe_fields')
    require(all(type(probe[k]) is str and bool(probe[k].strip()) for k in ('run_id', 'trial_id', 'sample_id', 'protocol_revision')),
            'characterization_identity_missing')
    require(count(probe['input_index']) < len(model['inputs']), 'characterization_input_out_of_range')
    frequency = count(model['frequency_hz'])
    require(frequency > 0 and number(probe['duration']) > 0 and
            equal(probe['maximum_sample_gap'], 1/frequency) and number(probe['minimum_amplitude']) > 0 and
            1 <= count(probe['maximum_samples']) <= 100000000 and probe['record_spikes'] is False and
            probe['peak_selection'] in ('isolated_window', 'assigned_burst_wave'), 'characterization_protocol_invalid')
    window = probe['window']
    require(type(window) is dict and set(window) == {'begin', 'end'} and
            0 <= number(window['begin']) < number(window['end']) <= probe['duration'], 'characterization_window_invalid')
    require(1 <= count(job['maximum_model_ticks']) <= 1000000000 and number(job['maximum_wall_seconds']) > 0,
            'characterization_budget_invalid')
    profile = job['stimulus_profile']
    require(type(profile) is dict and set(profile) == {'generator_class', 'amplitude', 'pulse_length', 'frequency_hz',
            'frequency_deviation', 'use_transit_signal', 'use_pattern_output'} and
            profile['generator_class'] == model['generator_class'] and number(profile['frequency_hz']) == frequency and
            number(profile['pulse_length']) > 0 and number(profile['frequency_deviation']) == 0 and
            type(profile['use_transit_signal']) is bool and type(profile['use_pattern_output']) is bool,
            'characterization_stimulus_invalid')
    number(profile['amplitude'])
    return {'job_sha256': job['sha256'], 'native_configuration_validation_required': True, 'training_started': False}


def prepare_job(training_job, input_index, trial_id, *, maximum_wall_seconds=None):
    """Copy declared physics/protocol; discard every search/finalization factor.

    Callers may edit the explicit ModelSpec before signing for an intervention.
    The actual baseline graph must be compared separately with the source state.
    """
    validate_training_job('preflight', training_job)
    c = training_job['configuration']
    require(count(input_index) < len(c['model']['inputs']), 'characterization_input_out_of_range')
    probe = {k: deepcopy(c[k]) for k in ('run_id', 'sample_id', 'protocol_revision', 'duration',
             'maximum_sample_gap', 'minimum_amplitude', 'maximum_samples', 'record_spikes', 'peak_selection')}
    probe.update(input_index=input_index, trial_id=trial_id, window=deepcopy(c['windows'][input_index]))
    job = _signed({'kind': 'timelearner_native_probe_job', 'schema_version': 1,
                   **{k: deepcopy(training_job[k]) for k in ('owner_class', 'implementation_id', 'profile_archives', 'maximum_model_ticks')},
                   'model': deepcopy(c['model']), 'stimulus_profile': deepcopy(c['stimulus_profile']), 'probe': probe,
                   'maximum_wall_seconds': c['maximum_wall_seconds'] if maximum_wall_seconds is None else maximum_wall_seconds})
    validate_job(job)
    return job


@_evidence_boundary
def audit_execution(directory):
    directory = Path(directory)
    job, execution = load(directory/'job.json'), load(directory/'execution.json')
    validate_job(job);_digest(execution)
    require(set(execution) == {'kind', 'schema_version', 'execution', 'job_sha256', 'model_revision', 'frequency_hz',
            'model_ticks', 'model_time_begin', 'model_time_end', 'training_started', 'search_executed', 'certificate_available',
            'model_unchanged', 'controller_idle', 'probe_status', 'observation_valid', 'observation_complete', 'artifacts',
            'evaluation_verdict', 'sha256'} and execution['kind'] == 'timelearner_native_probe_execution' and
            type(execution['schema_version']) is int and execution['schema_version'] == 1 and
            execution['job_sha256'] == job['sha256'], 'characterization_execution_scope_changed')
    expected_files = {'job.json', 'owner-configuration.json', 'initial-state.json',
                      'final-state.json', 'probe_trial_1.json', 'probe_trial_1.csv'}
    if (directory/'cancel.request').exists():
        require((directory/'cancel.request').stat().st_size <= 65536, 'characterization_cancel_request_too_large')
        expected_files.add('cancel.request')
    require(_artifact_records(directory, execution) == expected_files, 'characterization_artifact_closure_changed')
    require(all(execution[k] is False for k in ('training_started', 'search_executed', 'certificate_available')) and
            execution['evaluation_verdict'] is None, 'characterization_claims_training')
    require(execution['execution'] in ('completed', 'cancelled', 'timeout', 'model_tick_budget_exhausted', 'probe_rejected',
            'model_changed', 'unexpected_training_activity'), 'characterization_execution_unknown')
    initial, final = load(directory/'initial-state.json'), load(directory/'final-state.json')
    _digest(initial);_digest(final)
    for state, kind in ((initial, 'native_probe_initial_state'), (final, 'native_probe_final_state')):
        require(state['kind'] == kind and type(state['schema_version']) is int and state['schema_version'] == 1,
                'characterization_state_schema')
        identity = state['identity']
        require(identity['kind'] == 'semantic_model_identity' and identity['schema_version'] == 2 and
                identity['valid'] is True and identity['diagnostics'] == [] and identity['sha256'] == sha(identity['model']),
                'characterization_invalid_model')
    audit_initial_threshold(job['model'], initial['identity'])
    require(initial['training_started'] is False and initial['search_executed'] is False and initial['dynamics_checkpoint'] is False,
            'characterization_initial_training_claim')
    require(initial['identity'] == final['identity'] and initial['parameters'] == final['parameters'] and
            execution['model_revision'] == initial['identity']['sha256'] and
            all(value is True for value in (final['model_unchanged'], final['controller_idle'], execution['model_unchanged'], execution['controller_idle'])),
            'characterization_model_or_controller_changed')
    parameters = initial['parameters']
    require(len(parameters) == len(job['model']['inputs']) and all(set(p) == {'length', 'synapses', 'resistance'} and
            count(p['length']) == q['attachment'] and count(p['synapses']) == q['synapses'] and number(p['resistance']) > 0 and
            (q['resistance'] is None or p['resistance'] == q['resistance']) for p, q in zip(parameters, job['model']['inputs'])),
            'characterization_effective_parameters_changed')
    ticks, frequency = count(execution['model_ticks']), count(execution['frequency_hz'])
    require(0 < ticks <= job['maximum_model_ticks'] and frequency == job['model']['frequency_hz'] and
            equal(execution['model_time_begin'], 0) and equal(execution['model_time_end'], ticks/frequency),
            'characterization_clock_changed')
    packet, trace = load(directory/'probe_trial_1.json'), directory/'probe_trial_1.csv'
    requested, p = packet['requested_specification'], job['probe']
    require(all(requested[k] == p[k] for k in ('run_id', 'trial_id', 'sample_id', 'maximum_sample_gap', 'minimum_amplitude',
            'maximum_samples', 'record_spikes', 'peak_selection')) and equal(requested['begin'], 0) and
            equal(requested['end'], p['duration']) and requested['pattern_hash'] == sha(job['model']['initial_isi']) and
            requested['stimulus_profile'] == job['stimulus_profile'], 'characterization_request_changed')
    window = requested['windows']
    i = p['input_index']
    require(len(window) == 1 and window[0] == {'input_id': 'input'+str(i), 'stimulus_id': 'pulse'+str(i),
            'channel': 0 if job['model']['branch'] else i, **p['window']}, 'characterization_selected_window_changed')
    observation = packet['observation']
    require(execution['probe_status'] == packet['native_status'] and
            type(execution['observation_valid']) is type(execution['observation_complete']) is bool and
            execution['observation_valid'] == bool(observation and observation['valid']) and
            execution['observation_complete'] == bool(observation and observation['complete']), 'characterization_observation_flags_changed')
    if execution['execution'] in ('cancelled', 'timeout', 'model_tick_budget_exhausted'):
        # End-to-end binding to the native recorder's actual termination reason.
        # A cancelled process or a file alone cannot manufacture a closed trial.
        require(observation is not None and packet['native_status'] == 'rejected' and
                execution['execution'] in packet['reasons'] and observation['end_reason'] == execution['execution'] and
                observation['valid'] is False, 'characterization_interruption_not_observed')
        if execution['execution'] == 'cancelled':
            require('cancel.request' in expected_files, 'characterization_cancellation_request_missing')
        if execution['execution'] == 'model_tick_budget_exhausted':
            require(ticks == job['maximum_model_ticks'], 'characterization_tick_budget_not_reached')
    audit = audit_probe(packet, trace)
    if not audit['valid_observation']:
        observation, spec, _, samples, _, quality = read_partial_probe(packet, trace)
        audit_recorded_wave_diagnostics(observation, spec, samples, quality)
    if packet['prepared'] is not None:
        prepared = packet['prepared']
        require(prepared['base_model_revision'] == execution['model_revision'] and prepared['protocol_revision'] == p['protocol_revision'] and
                prepared['input_id'] == 'input'+str(i) and prepared['selected_input_index'] == (i if job['model']['branch'] else None),
                'characterization_prepared_context_changed')
    require((execution['execution'] == 'completed') == (packet['native_status'] == 'completed'), 'characterization_completion_changed')
    return {'primary_evidence_checked': True, 'runtime_provenance_checked': False, 'model_unchanged': True,
            'execution': execution['execution'], 'observation_valid': execution['observation_valid'],
            'observation_complete': execution['observation_complete'], 'training_started': False, 'evaluation_verdict': None}
