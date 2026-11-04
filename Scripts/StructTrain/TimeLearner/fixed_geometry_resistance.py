"""Stock resistance interventions at a measured failure boundary.

The cold baseline must reproduce the complete archived semantic graph before
any intervention is measured. Shared Branch attachments are physical banks.
These are characterization probes, not retraining or recognition evaluation.
"""
from copy import deepcopy
from pathlib import Path
import re

from .model_identity import canonical_model_sha256 as sha
from .native_calibration_worker import _digest, _signed, _write
from .native_characterization import prepare_job, audit_execution as audit_probe_execution
from .native_evidence import count, load, number, require
from .native_pipeline_worker import run_job, audit_run_manifest
from .n1_protocol_robustness import _inventory
from .stock_failure_reports import select_failure_boundary


def baseline_model(package):
    """Describe the actual boundary without inventing unobserved cable/physics.

    This declaration is only a proposal. Cold construction may differ from a
    historical graph (e.g. old released banks); the full graph gate is mandatory.
    """
    require(package['kind'] == 'timelearner_stopped_state' and package['certificate'] is None,
            'fixed_geometry_requires_diagnostic_stopped_model')
    identity = package['neuron']['graph']['identity']
    require(identity['valid'] is True and identity['sha256'] == sha(identity['model']) == package['model_revision'],
            'fixed_geometry_invalid_source_graph')
    model = deepcopy(package['configuration']['model'])
    parameters = package['trained_inputs']
    require(len(parameters) == len(model['inputs']), 'fixed_geometry_source_dimension_changed')
    for target, actual in zip(model['inputs'], parameters):
        target.update(attachment=count(actual['length']), synapses=count(actual['synapses']), resistance=number(actual['resistance']))
    cables = {}
    for node in identity['model']['nodes']:
        match = re.fullmatch(r'\$\.Dendrite(\d+)_(\d+)', node['path'])
        if match:
            cable, position = map(int, match.groups())
            cables[cable] = max(cables.get(cable, 0), position)
    size = 1 if model['branch'] else len(parameters)
    require(set(cables) == set(range(1, size+1)), 'fixed_geometry_cable_inventory_changed')
    require(model['neuron_structure_mode'] == 2, 'fixed_geometry_requires_explicit_vector_allocation')
    model['allocated_cable_lengths'] = [cables[i] for i in range(1, size+1)]
    return model, identity


def physical_bank_owners(model, input_index):
    require(count(input_index) < len(model['inputs']), 'fixed_geometry_input_out_of_range')
    if not model['branch']:
        return [input_index]
    position = model['inputs'][input_index]['attachment']
    return [i for i, p in enumerate(model['inputs']) if p['attachment'] == position]


def prepare(directory, output):
    from .stock_threshold_study import audit
    directory, output = Path(directory).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(directory) and not directory.is_relative_to(output),
            'fixed_geometry_requires_separate_new_directory')
    before = _inventory(directory)
    study = audit(directory)
    output.mkdir(parents=True);(output/'jobs').mkdir();(output/'expected').mkdir()
    rows = []
    # High-threshold boundaries isolate the loss of ordered waves without
    # replacing the separate low-threshold spike-feedback investigation.
    for source in study['rows']:
        if source['initial_threshold'] != 100:
            continue
        name = source['name'];native = directory/'runs'/name/'native'
        boundary = select_failure_boundary(native)
        previous = next((p for p in boundary['probes'] if p['role'] == 'last-valid-same-input'), None)
        require(previous is not None and previous['candidate_parameters'] is not None,
                'fixed_geometry_previous_measured_parameters_missing')
        package = load(native/'train_stopped_state.json')
        model, identity = baseline_model(package);index = boundary['input_index']
        owners = physical_bank_owners(model, index)
        resistance = number(previous['candidate_parameters'][index]['resistance'])
        require(resistance > 0 and any(model['inputs'][i]['resistance'] != resistance for i in owners),
                'fixed_geometry_intervention_is_noop')
        template = load(directory/'jobs'/(name+'.json'));template.pop('sha256')
        template['configuration']['model'] = model
        template['configuration']['run_id'] = name+'/fixed-geometry'
        # preflight executes no search; retain the original declared domain
        # and verify all effective values through the ordinary native gate.
        template = _signed(template)
        _write(output/'jobs'/(name+'-preflight.json'), template)
        probe = prepare_job(template, index, name+'/fixed-geometry/baseline', maximum_wall_seconds=900)
        _write(output/'jobs'/(name+'-baseline.json'), probe)
        changed = deepcopy(probe);changed.pop('sha256')
        changed['probe']['trial_id'] = name+'/fixed-geometry/resistance'
        for i in owners:
            changed['model']['inputs'][i]['resistance'] = resistance
        changed = _signed(changed)
        _write(output/'jobs'/(name+'-resistance.json'), changed)
        _write(output/'expected'/(name+'.json'), {'identity': identity, 'parameters': package['trained_inputs'],
            'source_package_sha256': package['sha256'], 'source_boundary': boundary,
            'physical_bank_owners': owners, 'intervention_resistance': resistance})
        rows.append({'name': name, 'branch': model['branch'], 'input_index': index,
                     'physical_bank_owners': owners, 'source_package_sha256': package['sha256'],
                     'source_model_revision': identity['sha256'], 'intervention_resistance': resistance})
    require({r['branch'] for r in rows} == {False, True} and len(rows) == 2, 'fixed_geometry_source_coverage_missing')
    require(before == _inventory(directory), 'fixed_geometry_source_changed')
    plan = _signed({'kind': 'stock_fixed_geometry_resistance_plan', 'schema_version': 1, 'rows': rows,
                    'source_inventory_sha256': sha(before), 'source_study_sha256': sha(study),
                    'training_executed': False, 'scientific_verdict': None})
    _write(output/'plan.json', plan)
    return plan


def graph_difference(a, b):
    """Retain exact semantic deltas; no parameter-name/number rounding filter."""
    if a == b:
        return []
    def differences(x, y, path):
        if type(x) is dict and type(y) is dict:
            for key in sorted(set(x) | set(y)):
                if key not in x or key not in y:
                    yield {'path': path+[key], 'before': x.get(key), 'after': y.get(key), 'missing_key': True}
                else:
                    yield from differences(x[key], y[key], path+[key])
        elif type(x) is list and type(y) is list and len(x) == len(y):
            for i, (left, right) in enumerate(zip(x, y)):
                yield from differences(left, right, path+[i])
        elif x != y:
            yield {'path': path, 'before': x, 'after': y, 'missing_key': False}
    return list(differences(a, b, []))


def run(prepared, runtime_manifest, output):
    prepared, output = Path(prepared).resolve(strict=True), Path(output).resolve()
    plan = load(prepared/'plan.json');_digest(plan)
    require(plan['kind'] == 'stock_fixed_geometry_resistance_plan' and plan['schema_version'] == 1 and
            plan['training_executed'] is False and plan['scientific_verdict'] is None, 'unknown_fixed_geometry_plan')
    require(not output.exists() and not output.is_relative_to(prepared) and not prepared.is_relative_to(output),
            'fixed_geometry_requires_separate_new_run')
    before = _inventory(prepared);output.mkdir(parents=True);rows = []
    for row in plan['rows']:
        name = row['name'];expected = load(prepared/'expected'/(name+'.json'))
        preflight = output/(name+'-preflight')
        run_job('preflight', prepared/'jobs'/(name+'-preflight.json'), None, runtime_manifest, preflight, 180)
        require(audit_run_manifest(preflight/'run-manifest.json')['run_evidence_consistent'], 'fixed_geometry_preflight_unverified')
        actual = load(preflight/'native/initial-state.json')
        graph_equal = actual['identity'] == expected['identity'] and actual['parameters'] == expected['parameters']
        record = {**row, 'source_graph_reproduced': graph_equal, 'probes_executed': False,
                  'baseline_difference': graph_difference(expected['identity'], actual['identity']),
                  'expected_parameters': expected['parameters'], 'actual_parameters': actual['parameters']}
        if graph_equal:
            probes = {}
            for variant in ('baseline', 'resistance'):
                folder = output/(name+'-'+variant)
                run_job('probe', prepared/'jobs'/(name+'-'+variant+'.json'), None, runtime_manifest, folder, 960)
                require(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'], 'fixed_geometry_probe_unverified')
                probes[variant] = {'audit': audit_probe_execution(folder/'native'),
                                   'initial': load(folder/'native/initial-state.json'),
                                   'packet': load(folder/'native/probe_trial_1.json')}
            require(probes['baseline']['initial']['identity'] == expected['identity'], 'fixed_geometry_probe_baseline_changed')
            record.update(probes_executed=True, probes=probes,
                          intervention_difference=graph_difference(probes['baseline']['initial']['identity'], probes['resistance']['initial']['identity']))
            # Keep every change for inspection before interpreting a causal
            # effect. A matching L/R summary alone never accepts an intervention.
            record['intervention_semantics_reviewed'] = False
        rows.append(record)
        _write(output/(name+'-result.json'), record)
    require(before == _inventory(prepared), 'fixed_geometry_prepared_inputs_changed')
    result = {'kind': 'stock_fixed_geometry_resistance_result', 'schema_version': 1,
              'plan_sha256': plan['sha256'], 'rows': rows, 'training_executed': False,
              'all_source_graphs_reproduced': all(r['source_graph_reproduced'] for r in rows),
              'intervention_semantics_reviewed': False, 'scientific_verdict': None}
    _write(output/'result.json', _signed(result))
    return result
