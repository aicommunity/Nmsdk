"""Reaudit and visualize the complete declared cold N4 characterization.

Reading a restored archive establishes primary-data consistency, not current
process authority, training convergence or classification performance.
"""
from pathlib import Path

from .native_evidence import load, require
from .native_characterization import audit_execution
from .stock_cold_characterization import jobs
from .stock_phasea_preflight import audit_stock_profile


def audit_result(directory):
    directory = Path(directory).resolve(strict=True)
    expected = jobs('both')
    index = load(directory/'index.json')
    require(index.get('kind') == 'timelearner_stock_cold_characterization_result' and
        index.get('schema_version') == 1 and index.get('training_started') is False and
        index.get('training_windows_selected') is False and index.get('source_unchanged') is True and
        index.get('scientific_verdict') is None, 'stock_cold_primary_result_scope')
    rows = index.get('rows')
    require(type(rows) is list and len(rows) == len(expected) and
        all(type(row) is dict and type(row.get('name')) is str for row in rows) and
        len({row['name'] for row in rows}) == len(expected) and
        {row['name'] for row in rows} == set(expected), 'stock_cold_primary_expected_trials')
    require({p.name for p in (directory/'runs').iterdir()} == set(expected),
        'stock_cold_primary_run_namespace')
    observed, revisions = [], {}
    for name, job in expected.items():
        native = directory/'runs'/name/'native'
        require(load(native/'job.json') == job, 'stock_cold_primary_job_changed')
        audit = audit_execution(native)
        require(audit['execution'] == 'completed' and audit['observation_valid'] is True and
            audit['observation_complete'] is True and audit['model_unchanged'] is True and
            audit['training_started'] is False and audit['evaluation_verdict'] is None,
            'stock_cold_primary_observation_invalid')
        initial = load(native/'initial-state.json')
        physical = audit_stock_profile(initial['identity'], branch=job['model']['branch'])
        require(physical['initial_threshold'] == 100., 'stock_cold_primary_threshold_changed')
        packet = load(native/'probe_trial_1.json')
        observation = packet['observation']
        require(len(observation['peaks']) == 1, 'stock_cold_primary_assigned_peak_count')
        peak = observation['peaks'][0]
        require(peak['input_id'] == 'input'+str(job['probe']['input_index']) and
            peak['stimulus_id'] == 'pulse'+str(job['probe']['input_index']) and
            peak['validity'] == 'valid', 'stock_cold_primary_assigned_peak_identity')
        topology = 'Branch' if job['model']['branch'] else 'Classic'
        revision = packet['prepared']['base_model_revision']
        require(revisions.setdefault(topology, revision) == revision,
            'stock_cold_primary_initial_model_changed')
        observed.append(dict(name=name, topology=topology, peak=peak,
            physical=physical, primary_audit=audit))
    return dict(kind='timelearner_stock_cold_primary_audit', schema_version=1,
        rows=observed, initial_model_revisions=revisions, complete_probes=len(observed),
        training_started=False, current_execution_attested=False, scientific_verdict=None)


def render_result(directory, output):
    # Import plotting only for rendering; a data-only reader needs no matplotlib.
    from .probe_reports import _read_probe_data, render_probe
    from .plotting import padded_limits
    from .native_calibration_worker import _write
    directory, output = Path(directory), Path(output)
    audit = audit_result(directory)
    require(not output.exists(), 'stock_cold_report_output_exists')
    by_topology = {}
    for row in audit['rows']:
        native = directory/'runs'/row['name']/'native'
        data = _read_probe_data(native/'probe_trial_1.json', native/'probe_trial_1.csv')
        count = data[6]
        values = by_topology.setdefault(row['topology'], [[] for _ in range(count)])
        require(count == len(values), 'stock_cold_report_soma_dimension_changed')
        for sample in data[5]:
            for channel, value in enumerate(sample['soma']):
                values[channel].append(value)
    limits = {name: [padded_limits(values) for values in channels]
              for name, channels in by_topology.items()}
    output.mkdir(parents=True)
    reports = []
    for row in audit['rows']:
        native = directory/'runs'/row['name']/'native'
        result = render_probe(native/'probe_trial_1.json', native/'probe_trial_1.csv',
            output/row['name'], comparison_limits=limits[row['topology']])
        reports.append(dict(name=row['name'], **result))
    result = dict(kind='timelearner_stock_cold_visual_report', schema_version=1,
        primary_audit=audit, reports=reports, common_y_limits=limits,
        trial_soma_pairs=sum(row['soma_count'] for row in reports),
        routing_comparison='explicit assigned-input isolation; common axes within topology',
        visual_acceptance_complete=False, scientific_verdict=None)
    _write(output/'manifest.json', result)
    return result
