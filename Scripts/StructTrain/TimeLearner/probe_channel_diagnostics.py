"""Read-only native channel samples; no inferred spikes or convergence claim."""
import csv
from pathlib import Path

from .native_evidence import count, equal, load, number, require
from .probe_diagnostics import read_partial_probe


def descriptors(identity, soma_count):
    nodes = {n['path']: n for n in identity['model']['nodes']}
    result = []
    def add(path, properties):
        require(path in nodes, 'channel_diagnostics_component_missing')
        result.extend({'path': path+'.'+prop, 'component_class': nodes[path]['class'],
                       'units': 'model_units_SI_unverified'} for prop in properties)
    add('$.LTZone', ('Potential', 'Output'))
    for i in range(soma_count):
        path = '$.Soma'+str(i+1)
        add(path, ('SumPotential', 'Feedback'))
        for role in ('ExcChannel', 'InhChannel'):
            add(path+'.'+role, ('Output', 'SumChannelInput'))
    return result


def audit(directory, job, execution, identity):
    directory = Path(directory)
    enabled = job['channel_diagnostics']
    require(type(enabled) is bool and execution['channel_diagnostics_enabled'] is enabled,
            'channel_diagnostics_enable_mismatch')
    intervention = bool(job['resistance_intervention'])
    baseline_terminal = execution['terminal_phase'] == 'source_baseline'
    prefixes = (['baseline_trial_'] if baseline_terminal else
                (['baseline_trial_', 'probe_trial_'] if intervention else ['probe_trial_']))
    expected = ['probe_diagnostics_'+str(i+1)+'.json' for i in range(len(prefixes))] if enabled else []
    require(execution['channel_diagnostic_files'] == expected, 'channel_diagnostics_inventory_mismatch')
    n = 1 if job['model']['branch'] else len(job['model']['inputs'])
    expected_descriptors = descriptors(identity, n)
    rows = []
    for filename, prefix in zip(expected, prefixes):
        diagnostic = load(directory/filename)
        packet = load(directory/(prefix+'1.json'))
        require(set(diagnostic) == {'kind', 'schema_version', 'sample_phase', 'trial_id',
                'base_model_revision', 'descriptors', 'samples', 'complete', 'scientific_verdict'} and
                diagnostic['kind'] == 'native_probe_channel_diagnostics' and
                type(diagnostic['schema_version']) is int and diagnostic['schema_version'] == 1 and
                diagnostic['sample_phase'] == 'native_after_children' and
                diagnostic['scientific_verdict'] is None and
                diagnostic['trial_id'] == packet['requested_specification']['trial_id'] and
                diagnostic['descriptors'] == expected_descriptors,
                'channel_diagnostics_context_or_descriptors_changed')
        if packet['prepared'] is not None:
            require(diagnostic['base_model_revision'] == packet['prepared']['base_model_revision'],
                    'channel_diagnostics_revision_changed')
        observation = packet['observation']
        trace = directory/(prefix+'1.csv')
        # The enclosing native-characterization audit checks the complete main
        # probe. Read invalid/partial data with its explicit diagnostic adapter.
        if observation is not None and observation['valid']:
            with trace.open(newline='', encoding='utf-8') as stream:
                values = list(csv.reader(stream))[1:]
            samples = [{'time': number(float(r[0])),
                        'soma': [number(float(v)) for v in r[2:]]} for r in values]
            spec = observation['specification']
        else:
            _, spec, _, samples, _, _ = read_partial_probe(packet, trace)
        measured = diagnostic['samples']
        require(type(measured) is list and len(measured) <= len(samples) and
                type(diagnostic['complete']) is bool and diagnostic['complete'] ==
                bool(packet['native_status'] == 'completed' and observation is not None and
                     observation['complete'] and len(measured) == len(samples)),
                'channel_diagnostics_coverage_mismatch')
        previous_spike = None;events = []
        for sample, primary in zip(measured, samples):
            require(type(sample) is dict and set(sample) == {'time', 'values', 'new_lt_spike_times'} and
                    equal(sample['time'], primary['time']) and type(sample['values']) is list and
                    len(sample['values']) == len(expected_descriptors), 'channel_diagnostics_sample_mismatch')
            values = [number(v) for v in sample['values']]
            require(all(values[2+6*i] == primary['soma'][i] for i in range(n)),
                    'channel_diagnostics_soma_primary_mismatch')
            require(type(sample['new_lt_spike_times']) is list, 'channel_diagnostics_invalid_spike_array')
            for event in sample['new_lt_spike_times']:
                event = number(event)
                require(spec['begin'] <= event <= sample['time'] and
                        (previous_spike is None or event > previous_spike),
                        'channel_diagnostics_invalid_spike_clock')
                previous_spike = event;events.append(event)
        rows.append({'file': filename, 'trial_id': diagnostic['trial_id'], 'samples': len(measured),
                     'complete': diagnostic['complete'], 'signals': len(expected_descriptors),
                     'recorded_lt_spike_times': events, 'soma_values_match_primary': True,
                     'channel_physics_reconstructed_independently': False})
    return {'enabled': enabled, 'probes': rows, 'scientific_verdict': None}
