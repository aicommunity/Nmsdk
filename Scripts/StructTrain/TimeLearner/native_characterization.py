"""Cold whole-burst characterization; never a Train or recognition verdict.

This module prepares the strict public native job and audits its primary
artifacts. Process ownership/runtime evidence remain the supervisor's task.
"""
from copy import deepcopy
from pathlib import Path
import struct
import re

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
    version = job.get('schema_version') if type(job) is dict else None
    require(type(version) is int and version in (1, 2, 3, 4, 5), 'unknown_characterization_job')
    require(set(job) == JOB_FIELDS | ({'source_stopped', 'resistance_intervention'} if version >= 2 else set()) |
            ({'channel_diagnostics'} if version >= 3 else set()) | ({'presentation'} if version >= 4 else set()) | ({'profile_intervention'} if version == 5 else set()) and
            job['kind'] == 'timelearner_native_probe_job', 'unknown_characterization_job')
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
    if version == 5:
        validate_profile_intervention(job['profile_intervention'])
        require(job['presentation'] in ({'kind': 'single_pulse_characterization'}, {'kind': 'native_burst'}) and
                job['resistance_intervention'] == [] and
                job['stimulus_profile'] == job['source_stopped']['configuration']['stimulus_profile'],
                'profile_probe_presentation_invalid')
    if version == 4:
        require(is_single_pulse(job), 'single_pulse_presentation_invalid')
    if is_single_pulse(job):
        require(job['presentation'] == {'kind': 'single_pulse_characterization'} and
                job['resistance_intervention'] == [] and probe['peak_selection'] == 'isolated_window' and
                job['stimulus_profile'] == job['source_stopped']['configuration']['stimulus_profile'],
                'single_pulse_presentation_invalid')
    if version >= 3:
        require(type(job['channel_diagnostics']) is bool, 'characterization_diagnostics_boolean_required')
    if version >= 2:
        source = job['source_stopped'];_digest(source)
        require(source['kind'] == 'timelearner_stopped_state' and source['state_kind'] == 'diagnostic' and
                source['certificate'] is None and source['controller_version'] == 2 and
                source['implementation_id'] == job['implementation_id'] and
                source['configuration']['model'] == model and job['profile_archives'] == [],
                'characterization_stopped_source_mismatch')
        expected_import_parameters(job)
    return {'job_sha256': job['sha256'], 'native_configuration_validation_required': True, 'training_started': False}


def is_single_pulse(job):
    return job.get('presentation') == {'kind': 'single_pulse_characterization'}


def validate_profile_intervention(value):
    require(type(value) is dict and set(value) == {'kind', 'image_prefix', 'feedback_gain', 'baseline_reconstruction'} and
            value['kind'] == 'uniform_feedback_storage_profile' and type(value['image_prefix']) is str and
            re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,95}', value['image_prefix']) is not None and
            number(value['feedback_gain']) >= 0 and type(value['baseline_reconstruction']) is bool,
            'invalid_feedback_profile_intervention')


def prepare_feedback_profile_job(case, input_index, trial_id, *, image_prefix, feedback_gain,
                                 baseline_reconstruction=False, single_pulse=False, maximum_wall_seconds=900):
    require(type(single_pulse) is bool, 'profile_probe_presentation_invalid')
    builder = prepare_single_pulse_job if single_pulse else prepare_stopped_job
    job = builder(case, input_index, trial_id, maximum_wall_seconds=maximum_wall_seconds, channel_diagnostics=True)
    job.pop('sha256')
    job.update(schema_version=5, presentation={'kind': 'single_pulse_characterization' if single_pulse else 'native_burst'},
               profile_intervention={'kind': 'uniform_feedback_storage_profile', 'image_prefix': image_prefix,
                   'feedback_gain': feedback_gain, 'baseline_reconstruction': baseline_reconstruction})
    job = _signed(job);validate_job(job);return job


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


def expected_import_parameters(job):
    parameters = deepcopy(job['source_stopped']['trained_inputs'])
    require(len(parameters) == len(job['model']['inputs']), 'characterization_import_dimension_changed')
    changes = job['resistance_intervention']
    require(type(changes) is list and len(changes) <= len(parameters), 'characterization_intervention_invalid')
    seen = set()
    for change in changes:
        require(type(change) is dict and set(change) == {'input_index', 'resistance'}, 'characterization_intervention_fields')
        i, r = count(change['input_index']), number(change['resistance'])
        require(i < len(parameters) and i not in seen and r > 0, 'characterization_intervention_invalid')
        seen.add(i);parameters[i]['resistance'] = r
    if job['model']['branch']:
        banks = {}
        for p in parameters:
            require(p['length'] not in banks or banks[p['length']] == (p['synapses'], p['resistance']),
                    'characterization_shared_bank_intervention_inconsistent')
            banks[p['length']] = (p['synapses'], p['resistance'])
    return parameters


def prepare_stopped_job(case, input_index, trial_id, *, resistance_intervention=None, maximum_wall_seconds=900,
                       channel_diagnostics=None):
    from .stopped_evidence import audit_stopped_state
    audit_stopped_state(*case)
    package = case[0];c = package['configuration']
    probe = {k: deepcopy(c[k]) for k in ('run_id', 'sample_id', 'protocol_revision', 'duration',
             'maximum_sample_gap', 'minimum_amplitude', 'maximum_samples', 'record_spikes', 'peak_selection')}
    require(count(input_index) < len(c['windows']), 'characterization_input_out_of_range')
    probe.update(input_index=input_index, trial_id=trial_id, window=deepcopy(c['windows'][input_index]))
    job = _signed({'kind': 'timelearner_native_probe_job', 'schema_version': 2,
        'owner_class': 'NNeuronTimeLearner'+('Branch' if c['model']['branch'] else ''),
        'implementation_id': package['implementation_id'], 'model': deepcopy(c['model']), 'profile_archives': [],
        'stimulus_profile': deepcopy(c['stimulus_profile']), 'probe': probe, 'source_stopped': deepcopy(package),
        'resistance_intervention': deepcopy(resistance_intervention or []),
        'maximum_model_ticks': (int(c['duration']*c['model']['frequency_hz'])+4)*(2 if resistance_intervention else 1), 'maximum_wall_seconds': maximum_wall_seconds})
    if channel_diagnostics is not None:
        require(type(channel_diagnostics) is bool, 'characterization_diagnostics_boolean_required')
        job.update(schema_version=3, channel_diagnostics=channel_diagnostics)
        job.pop('sha256')
        job = _signed(job)
    validate_job(job);return job


def prepare_single_pulse_job(case, input_index, trial_id, *, maximum_wall_seconds=900, channel_diagnostics=True):
    """Only transient presentation changes; full source model/target is imported."""
    job = prepare_stopped_job(case, input_index, trial_id, maximum_wall_seconds=maximum_wall_seconds,
                              channel_diagnostics=channel_diagnostics)
    job.update(schema_version=4, presentation={'kind': 'single_pulse_characterization'})
    job['probe']['peak_selection'] = 'isolated_window'
    job['probe']['window'] = {'begin': 0., 'end': job['probe']['duration']}
    job['probe']['protocol_revision'] += '/single-pulse-characterization-v1'
    job.pop('sha256')
    job = _signed(job);validate_job(job);return job


def audit_feedback_profile_import(job, record, candidate):
    from .feedback_intervention import audit_profile_delta
    from .archive_transfer_reports import graph
    fields = {'kind', 'schema_version', 'source_stopped_sha256', 'source_identity', 'candidate_identity',
              'dataset_identity', 'class_renames', 'image_prefix', 'feedback_gain', 'baseline_reconstruction',
              'image_definitions', 'image_definitions_fingerprint', 'physical_dynamics_reset',
              'controller_history_copied', 'certificate_copied', 'training_started', 'sha256'}
    factor, source = job['profile_intervention'], job['source_stopped']
    require(set(record) == fields and record['kind'] == 'native_feedback_profile_import' and
            type(record['schema_version']) is int and record['schema_version'] == 1 and
            record['source_stopped_sha256'] == source['sha256'] and
            record['source_identity'] == source['neuron']['graph']['identity'] and
            record['candidate_identity'] == candidate and record['dataset_identity'] == source['dataset']['identity'] and
            all(record[k] == factor[k] for k in ('image_prefix', 'feedback_gain', 'baseline_reconstruction')) and
            record['physical_dynamics_reset'] is True and
            all(record[k] is False for k in ('controller_history_copied', 'certificate_copied', 'training_started')),
            'profile_probe_import_scope_changed')
    audit_profile_delta(record['source_identity'], candidate, record['class_renames'],
                        feedback_gain=None if factor['baseline_reconstruction'] else factor['feedback_gain'])
    definitions = record['image_definitions']
    require(type(definitions) is list and 0 < len(definitions) <= 4096, 'profile_probe_invalid_images')
    semantic, edges = {}, {}
    def classes(model):
        names = set()
        for node in model['nodes']:
            names.add(node['class'])
            for name, prop in node['parameters'].items():
                if name.endswith('ClassName'):
                    data = prop['data']
                    if data['type'] == 'utf8' and data['value']:names.add(data['value'])
        return names
    for definition in definitions:
        require(type(definition) is dict and set(definition) == {'name', 'kind', 'base_class', 'snapshot', 'dependencies'} and
                type(definition['name']) is str and definition['name'] and definition['name'] not in semantic and
                definition['kind'] in ('native_required', 'derived_image') and type(definition['base_class']) is str and
                (bool(definition['base_class']) == (definition['kind'] == 'derived_image')) and
                type(definition['dependencies']) is list and all(type(v) is str and v for v in definition['dependencies']),
                'profile_probe_invalid_image_definition')
        model = graph(definition['snapshot'])
        name, base = definition['name'], definition['base_class']
        expected = classes(model) - {name}
        if base:expected.add(base)
        require(len(set(definition['dependencies'])) == len(definition['dependencies']) and
                set(definition['dependencies']) == expected, 'profile_probe_image_dependencies_changed')
        edges[name] = expected
        semantic[name] = {'kind': definition['kind'], 'base_class': base, 'model': model}
    require(all(deps <= semantic.keys() for deps in edges.values()) and
            classes(candidate['model']) <= semantic.keys() and sha(semantic) == record['image_definitions_fingerprint'],
            'profile_probe_image_closure_or_fingerprint_changed')
    done, visiting = set(), set()
    def visit(name, depth):
        require(depth <= 128 and name not in visiting, 'profile_probe_image_cycle_or_depth')
        if name in done:return
        visiting.add(name)
        for child in edges[name]:visit(child, depth+1)
        visiting.remove(name);done.add(name)
    for name in edges:visit(name, 0)
    return {'image_metadata_checked': True, 'native_xml_readback_proof_required': True,
            'waveform_equivalence_verified': False, 'scientific_verdict': None}


def expected_import_model(job):
    """Exact physical graph projection for an Rs-only intervention, including aliases."""
    parameters = expected_import_parameters(job)
    model = deepcopy(job['source_stopped']['neuron']['graph']['identity']['model'])
    nodes = {n['path']: n for n in model['nodes']}
    for i, (before, after) in enumerate(zip(job['source_stopped']['trained_inputs'], parameters)):
        if before['resistance'] == after['resistance']:
            continue
        cable = 1 if job['model']['branch'] else i+1
        for k in range(1, count(after['synapses'])+1):
            path = '$.Dendrite'+str(cable)+'_'+str(after['length'])+'.ExcSynapse'+str(k)
            data = nodes[path]['parameters']['Resistance']['data']
            require(data['type'] == 'binary64', 'characterization_resistance_type_unsupported')
            data['value'] = struct.pack('>d', number(after['resistance'])).hex()
    return model


@_evidence_boundary
def audit_execution(directory):
    directory = Path(directory)
    job, execution = load(directory/'job.json'), load(directory/'execution.json')
    validate_job(job);_digest(execution)
    schema = execution['schema_version']
    require(type(schema) is int and schema in (1, 2, 3, 4, 5), 'characterization_execution_schema')
    require(set(execution) == {'kind', 'schema_version', 'execution', 'job_sha256', 'model_revision', 'frequency_hz',
            'model_ticks', 'model_time_begin', 'model_time_end', 'training_started', 'search_executed', 'certificate_available',
            'model_unchanged', 'controller_idle', 'probe_status', 'observation_valid', 'observation_complete', 'artifacts',
            'evaluation_verdict', 'sha256'} | ({'probe_wall_seconds'} if schema >= 2 else set()) |
            ({'terminal_phase', 'resistance_intervention_applied'} if schema >= 3 else set()) |
            ({'channel_diagnostics_enabled', 'channel_diagnostic_files'} if schema >= 4 else set()) |
            ({'profile_intervention_applied'} if schema == 5 else set()) and execution['kind'] == 'timelearner_native_probe_execution' and
            execution['job_sha256'] == job['sha256'], 'characterization_execution_scope_changed')
    imported = job['schema_version'] >= 2
    require((schema >= 4) == (job['schema_version'] >= 3) and (schema == 5) == (job['schema_version'] == 5), 'characterization_diagnostics_schema_mismatch')
    baseline_terminal = schema >= 3 and execution['terminal_phase'] == 'source_baseline'
    if schema >= 3:
        require(imported and execution['terminal_phase'] in ('source_baseline', 'main_probe') and
                type(execution['resistance_intervention_applied']) is bool and
                execution['resistance_intervention_applied'] == (bool(job['resistance_intervention']) and not baseline_terminal) and
                (not baseline_terminal or (job['resistance_intervention'] and execution['execution'] != 'completed')),
                'characterization_phase_or_intervention_changed')
    applied = imported and bool(job['resistance_intervention']) and not baseline_terminal
    terminal_prefix = 'baseline_trial_' if baseline_terminal else 'probe_trial_'
    expected_files = {'job.json', 'owner-configuration.json', 'initial-state.json',
                      'final-state.json', terminal_prefix+'1.json', terminal_prefix+'1.csv'}
    if imported:
        expected_files.update({'source-import.json', 'probe-configuration.json', 'controller-before.json', 'controller-after.json'})
        if job['resistance_intervention']:
            expected_files.update({'baseline_trial_1.json', 'baseline_trial_1.csv'})
    if schema >= 4:
        require(type(execution['channel_diagnostic_files']) is list and
                all(type(v) is str and v in ('probe_diagnostics_1.json', 'probe_diagnostics_2.json')
                    for v in execution['channel_diagnostic_files']), 'channel_diagnostics_invalid_artifact_names')
        expected_files.update(execution['channel_diagnostic_files'])
    if (directory/'cancel.request').exists():
        require((directory/'cancel.request').stat().st_size <= 65536, 'characterization_cancel_request_too_large')
        expected_files.add('cancel.request')
    require(_artifact_records(directory, execution) == expected_files, 'characterization_artifact_closure_changed')
    require(all(execution[k] is False for k in ('training_started', 'search_executed', 'certificate_available')) and
            execution['evaluation_verdict'] is None, 'characterization_claims_training')
    require(execution['execution'] in ('completed', 'cancelled', 'timeout', 'model_tick_budget_exhausted', 'probe_rejected',
            'model_changed', 'unexpected_training_activity'), 'characterization_execution_unknown')
    if schema >= 2:
        require(number(execution['probe_wall_seconds']) > 0 and
                (execution['execution'] != 'timeout' or execution['probe_wall_seconds'] >= job['maximum_wall_seconds']),
                'characterization_wall_budget_not_reached')
    initial, final = load(directory/'initial-state.json'), load(directory/'final-state.json')
    _digest(initial);_digest(final)
    for state, kind in ((initial, 'native_probe_initial_state'), (final, 'native_probe_final_state')):
        require(state['kind'] == kind and type(state['schema_version']) is int and state['schema_version'] == 1,
                'characterization_state_schema')
        identity = state['identity']
        require(identity['kind'] == 'semantic_model_identity' and identity['schema_version'] == 2 and
                identity['valid'] is True and identity['diagnostics'] == [] and identity['sha256'] == sha(identity['model']),
                'characterization_invalid_model')
    if not imported:
        audit_initial_threshold(job['model'], initial['identity'])
    if imported:
        source_import = load(directory/'source-import.json');_digest(source_import)
        source = job['source_stopped']
        profiled = job['schema_version'] == 5
        if profiled:
            audit_feedback_profile_import(job, source_import, initial['identity'])
            require(execution['profile_intervention_applied'] is True, 'profile_probe_intervention_missing')
        else:
            require(source_import['kind'] == 'native_probe_source_import' and source_import['schema_version'] == 1 and
                    source_import['source_stopped_sha256'] == source['sha256'] and
                    source_import['identity'] == source['neuron']['graph']['identity'] and
                    source_import['parameters'] == source['trained_inputs'] and
                    source_import['physical_dynamics_reset'] is True and source_import['controller_dynamics_reset'] is True and
                    source_import['controller_history_preserved'] is True and
                    source_import['training_started'] is False, 'characterization_source_import_changed')
        control = load(directory/'controller-before.json');_digest(control)
        summary = control['summary']
        expected_history = [] if profiled else source['observed_packets']
        require(control == load(directory/'controller-after.json') and control['kind'] == 'native_probe_controller_snapshot' and
                control['schema_version'] == 1 and summary['state'] == 'idle' and summary['certificate'] is None and
                summary['reference_probes'] == 0 and control['observed_packet_count'] == len(expected_history) and
                control['observed_packets_sha256'] == sha(expected_history), 'characterization_imported_controller_changed')
        require(initial['parameters'] == (expected_import_parameters(job) if applied else source['trained_inputs']),
                'characterization_import_parameters_changed')
        if not profiled:
            require(initial['identity']['model'] == (expected_import_model(job) if applied else source['neuron']['graph']['identity']['model']),
                    'characterization_import_or_intervention_graph_changed')
        if applied:
            baseline = load(directory/'baseline_trial_1.json')
            require(baseline['native_status'] == 'completed' and baseline['observation'] is not None and
                    baseline['observation']['complete'] is True and
                    baseline['requested_specification']['trial_id'] == job['probe']['trial_id']+'/source-baseline' and
                    baseline['prepared']['base_model_revision'] == source['model_revision'], 'characterization_edit_boundary_not_measured')
            baseline_trace = directory/'baseline_trial_1.csv'
            base_audit = audit_probe(baseline, baseline_trace)
            if not base_audit['valid_observation']:
                observation, spec, _, samples, _, quality = read_partial_probe(baseline, baseline_trace)
                audit_recorded_wave_diagnostics(observation, spec, samples, quality)
    require(initial['training_started'] is False and initial['search_executed'] is False and initial['dynamics_checkpoint'] is False,
            'characterization_initial_training_claim')
    require(initial['identity'] == final['identity'] and initial['parameters'] == final['parameters'] and
            execution['model_revision'] == initial['identity']['sha256'] and
            all(value is True for value in (final['model_unchanged'], final['controller_idle'], execution['model_unchanged'], execution['controller_idle'])),
            'characterization_model_or_controller_changed')
    parameters = initial['parameters']
    source_parameters = (expected_import_parameters(job) if applied else job['source_stopped']['trained_inputs']) if imported else None
    inputs = [{'attachment': p['length'], **p} for p in source_parameters] if imported else job['model']['inputs']
    require(len(parameters) == len(inputs) and all(set(p) == {'length', 'synapses', 'resistance'} and
            count(p['length']) == q['attachment'] and count(p['synapses']) == q['synapses'] and number(p['resistance']) > 0 and
            (q['resistance'] is None or p['resistance'] == q['resistance']) for p, q in zip(parameters, inputs)),
            'characterization_effective_parameters_changed')
    ticks, frequency = count(execution['model_ticks']), count(execution['frequency_hz'])
    require(0 < ticks <= job['maximum_model_ticks'] and frequency == job['model']['frequency_hz'] and
            equal(execution['model_time_begin'], 0) and equal(execution['model_time_end'], ticks/frequency),
            'characterization_clock_changed')
    packet, trace = load(directory/(terminal_prefix+'1.json')), directory/(terminal_prefix+'1.csv')
    requested, p = packet['requested_specification'], job['probe']
    require(requested['trial_id'] == p['trial_id']+('/source-baseline' if baseline_terminal else '') and
            all(requested[k] == p[k] for k in ('run_id', 'sample_id', 'maximum_sample_gap', 'minimum_amplitude',
            'maximum_samples', 'record_spikes', 'peak_selection')) and equal(requested['begin'], 0) and
            equal(requested['end'], p['duration']) and requested['pattern_hash'] == sha(job['model']['initial_isi'][:1] if is_single_pulse(job) else job['model']['initial_isi']) and
            requested['stimulus_profile'] == job['stimulus_profile'], 'characterization_request_changed')
    window = requested['windows']
    i = p['input_index']
    require(len(window) == 1 and window[0] == {'input_id': 'input'+str(i), 'stimulus_id': 'pulse'+str(0 if is_single_pulse(job) else i),
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
    single_audit = {}
    if is_single_pulse(job):
        from .single_pulse_evidence import read_single_pulse
        observation, spec, _, samples, _, quality = read_single_pulse(packet, trace)
        require(requested['characterization'] == {'purpose': 'single_pulse_characterization',
                'source_training_pattern_hash': sha(job['model']['initial_isi']),
                'physical_input_count': len(job['model']['inputs']), 'selected_input_index': i},
                'single_pulse_source_or_selector_changed')
        single_audit['single_pulse_diagnostic'] = quality
    else:
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
    diagnostic_audit = {}
    if schema >= 4:
        from .probe_channel_diagnostics import audit as audit_channels
        diagnostic_audit['channel_diagnostics'] = audit_channels(directory, job, execution, initial['identity'])
    return {'primary_evidence_checked': True, 'runtime_provenance_checked': False, 'model_unchanged': True,
            **({'terminal_phase': execution['terminal_phase']} if schema >= 3 else {}), **diagnostic_audit, **single_audit,
            'execution': execution['execution'], 'observation_valid': execution['observation_valid'],
            'observation_complete': execution['observation_complete'], 'training_started': False, 'evaluation_verdict': None}
