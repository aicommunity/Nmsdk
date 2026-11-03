"""Preregistered stock four-input cold Train at two explicit output thresholds.

Both values run on the same immutable native runtime. A valid negative training
outcome is retained; this module never substitutes a template Test or infers
classification from convergence or process completion.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
import struct

from .condition import CONDITION_ROLES, ConditionSpec, artifact
from .model_identity import canonical_model_sha256 as sha
from .n1_protocol_robustness import _inventory, _signed, _write
from .native_evidence import load, require
from .native_model_spec import audit_initial_threshold
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .process_runner import verify_runtime
from .stock_phasea_preflight import TARGET, audit_stock_profile, _property


THRESHOLDS = (.0117, 100.)


def audit_final_stock(initial, final):
    """Growth may change morphology and individual Rs, never the declared physics."""
    require(final['valid'] is True and final['diagnostics'] == [] and
            final['sha256'] == sha(final['model']), 'stock_pair_final_identity_invalid')
    before = {n['path']: n for n in initial['model']['nodes']}
    nodes = {n['path']: n for n in final['model']['nodes']}
    require(len(nodes) == len(final['model']['nodes']) and nodes['$']['class'] == 'NSPNeuronGen' and
            not any(p == '$.LTMembrane' or p.startswith('$.LTMembrane.') for p in nodes),
            'stock_pair_final_profile_changed')
    require(all(n['frequency_hz'] == '2000' for n in nodes.values()), 'stock_pair_final_frequency_changed')
    membranes = {p for p in nodes if re.fullmatch(r'\$\.(?:Soma\d+|Dendrite\d+_\d+)', p)}
    require(bool(membranes) and {p for p in membranes if p.startswith('$.Soma')} ==
            {p for p in before if re.fullmatch(r'\$\.Soma\d+', p)}, 'stock_pair_final_somas_changed')
    channels = 0
    for path in membranes:
        require(nodes[path]['class'] == 'NPMembraneBio', 'stock_pair_final_membrane_class_changed')
        for role in ('Exc', 'Inh'):
            channel = nodes[path+'.'+role+'Channel'];baseline = before['$.Soma1.'+role+'Channel']
            require(channel['class'] == baseline['class'], 'stock_pair_final_channel_class_changed')
            for field in ('Capacity', 'Resistance', 'RestingResistance', 'FBResistance', 'Type'):
                require(_property(channel, field) == _property(baseline, field),
                        'stock_pair_final_channel_physics_changed:'+field)
            channels += 1
    for node in nodes.values():
        if node['class'] == 'NPSynapseBio':
            for field, value in {'SecretionTC': .001, 'DissociationTC': .005, 'TypicalPulseDuration': .001,
                                 'UsePresynapticInhibition': False, 'InhibitionCoeff': 0.}.items():
                require(_property(node, field) == value, 'stock_pair_final_synapse_physics_changed:'+field)
    require(nodes['$.LTZone'] == before['$.LTZone'], 'stock_pair_final_ltzone_changed')
    def zone_bindings(model):
        return sorted((b['source'], b['target'], b['kind']) for b in model['bindings']
                      if b['target'] == '$.LTZone:Inputs' or b['source'] == '$.LTZone:Output')
    require(zone_bindings(final['model']) == zone_bindings(initial['model']),
            'stock_pair_final_ltzone_connections_changed')
    return {'lt_membrane': False, 'membranes_checked': len(membranes), 'channels_checked': channels,
            'threshold_unchanged': True, 'feedback_connections_unchanged': True}


def _expected(initial, threshold):
    result = deepcopy(initial)
    zones = [n for n in result['model']['nodes'] if n['path'] == '$.LTZone']
    require(len(zones) == 1, 'stock_pair_source_zone_missing')
    zones[0]['parameters']['Threshold']['data']['value'] = struct.pack('>d', threshold).hex()
    result['sha256'] = sha(result['model'])
    return result


def _condition(job, expected, code, runtime):
    c = deepcopy(job['configuration']);c.pop('run_id')
    payloads = {
        'algorithm': {'id': 'stock-phasea-cold-initial-threshold-pair-v1', 'native_code': code,
                      'executable_sha256': runtime['executable']['sha256']},
        'model_spec': c['model'],
        'storage_profiles': {'class': 'NSPNeuronGen', 'expected_effective_model': expected['model']},
        'initial_state': {'model_revision': expected['sha256'], 'cold': True},
        'training_plan': c,
        'input_data': {'target_isi': TARGET},
        'presentation_protocol': {k: c[k] for k in ('duration', 'windows', 'peak_selection', 'stimulus_profile')},
        'calibration_spec': {'performed': False},
        'evaluation_spec': {'performed': False, 'classification_assessed': False},
        'execution_policy': {'maximum_model_ticks': job['maximum_model_ticks'],
                             'maximum_wall_seconds': c['maximum_wall_seconds']},
        'randomness_spec': {'declared_random_factors': [], 'cold_runs_per_condition': 1},
    }
    artifacts = {role: artifact(role, payloads[role]) for role in CONDITION_ROLES}
    condition = ConditionSpec(controller_version=2, amplitude_goal='captured_per_input',
                             **{role: a['sha256'] for role, a in artifacts.items()})
    condition.resolve({a['sha256']: a for a in artifacts.values()})
    return {'condition': condition.to_object(), 'artifacts': artifacts}


def prepare(source, runtime_path, code_identity, output):
    source, output = Path(source).resolve(strict=True), Path(output)
    require(not output.exists(), 'stock_pair_output_exists')
    runtime = load(Path(runtime_path));verify_runtime(runtime)
    require(runtime == load(source/'runtime.json'), 'stock_pair_not_same_preflight_runtime')
    require(type(code_identity) is dict and set(code_identity) == {'pulse_core', 'rdk_core', 'console_driver'} and
            all(type(v) is str and re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', v) for v in code_identity.values()),
            'stock_pair_code_identity_required')
    index = load(source/'index.json')
    require(index['kind'] == 'stock_phasea_native_preflight' and index['operations'] == 2 and
            {r['name'] for r in index['rows']} == {t+'-stock-nspneurongen-inputs4' for t in ('Classic', 'Branch')},
            'stock_pair_source_preflight_inventory')
    templates = []
    for top in ('Classic', 'Branch'):
        folder = source/'runs'/(top+'-stock-nspneurongen-inputs4')
        audit_run_manifest(folder/'run-manifest.json')
        job = load(folder/'input/job.json');initial = load(folder/'native/initial-state.json')['identity']
        audit_stock_profile(initial, branch=top == 'Branch')
        m = job['configuration']['model']
        require(m['schema_version'] == 2 and m['initial_threshold'] == 100 and m['initial_isi'] == TARGET and
                m['normalization'] == 'N1' and m['neuron_class'] == 'NSPNeuronGen' and job['profile_archives'] == [],
                'stock_pair_requires_explicit_high_threshold_stock_template')
        audit_initial_threshold(m, initial)
        templates.append((top, job, initial))
    output.mkdir(parents=True)
    for name in ('jobs', 'expected', 'conditions', 'source'):(output/name).mkdir()
    _write(output/'runtime.json', runtime);_write(output/'code-identity.json', code_identity)
    _write(output/'source/index.json', index)
    shutil.copytree(source/'runs', output/'source/runs')
    rows = []
    for top, template, initial in templates:
        for threshold in THRESHOLDS:
            name = top+('-threshold-low' if threshold == .0117 else '-threshold-training100')
            job = deepcopy(template);job['configuration']['run_id'] = name
            job['configuration']['model']['initial_threshold'] = threshold;job = _signed(job)
            validate_job('train', job)
            expected = _expected(initial, threshold)
            evidence = _condition(job, expected, code_identity, runtime)
            condition = ConditionSpec.loads(json.dumps(evidence['condition']))
            _write(output/'jobs'/f'{name}.json', job)
            _write(output/'expected'/f'{name}.json', expected)
            _write(output/'conditions'/f'{name}.json', evidence)
            rows.append({'name': name, 'topology': top, 'initial_threshold': threshold,
                         'job_sha256': job['sha256'], 'expected_initial_revision': expected['sha256'],
                         'condition_fingerprint': condition.fingerprint})
    design = _signed({'kind': 'stock_phasea_threshold_pair_design', 'schema_version': 1,
                      'rows': rows, 'all_jobs_frozen_before_native_operations': True,
                      'classification_assessed': False, 'scientific_verdict': None})
    _write(output/'design.json', design)
    return design


def run(source, runtime_path, code_identity, output):
    output = Path(output)
    design = prepare(source, runtime_path, code_identity, output)
    before = _inventory(output/'source')
    require(shutil.disk_usage(output).free >= 16*1024**3, 'stock_pair_primary_capacity')
    (output/'preflights').mkdir();(output/'runs').mkdir()
    # No Train starts before all four declared effective-model controls pass.
    for row in design['rows']:
        print('PREFLIGHT', row['name'], flush=True)
        folder = output/'preflights'/row['name']
        result = run_job('preflight', output/'jobs'/f"{row['name']}.json", None, output/'runtime.json', folder, 180.)
        require(result['execution'] == 'completed' and result['validity'] == 'valid', 'stock_pair_preflight_failed')
        actual = load(folder/'native/initial-state.json')['identity']
        require(actual == load(output/'expected'/f"{row['name']}.json"), 'stock_pair_effective_profile_drift')
        audit_stock_profile(actual, branch=row['topology'] == 'Branch')
    records = []
    for row in design['rows']:
        print('TRAIN', row['name'], flush=True)
        folder = output/'runs'/row['name']
        result = run_job('train', output/'jobs'/f"{row['name']}.json", None, output/'runtime.json', folder, 7200.)
        require(result['execution'] == 'completed' and result['validity'] == 'valid', 'stock_pair_training_execution_invalid')
        audit_run_manifest(folder/'run-manifest.json')
        require(load(folder/'native/initial-state.json') ==
                load(output/'preflights'/row['name']/'native/initial-state.json'), 'stock_pair_cold_state_changed')
        execution = load(folder/'native/execution.json')
        records.append({'name': row['name'], 'training_outcome': execution['training_outcome'],
                        'completed_boundary': execution['completed_boundary'], 'model_revision': execution['model_revision']})
        _write(output/'progress.json', records)
        print('END', row['name'], execution['training_outcome'], flush=True)
    require(before == _inventory(output/'source'), 'stock_pair_source_changed')
    _write(output/'index.json', _signed({'kind': 'stock_phasea_threshold_pair', 'schema_version': 1,
           'records': records, 'operations': 4, 'classification_assessed': False, 'scientific_verdict': None}))
    result = audit(output);_write(output/'analysis.json', result)
    return result


def audit(directory):
    directory = Path(directory).resolve(strict=True)
    design, index = load(directory/'design.json'), load(directory/'index.json')
    require(set(design) == {'kind', 'schema_version', 'rows', 'all_jobs_frozen_before_native_operations',
                            'classification_assessed', 'scientific_verdict', 'sha256'} and
            set(index) == {'kind', 'schema_version', 'records', 'operations', 'classification_assessed',
                           'scientific_verdict', 'sha256'}, 'stock_pair_unknown_fields')
    for value in (design, index):
        require(value['sha256'] == sha({k: v for k, v in value.items() if k != 'sha256'}), 'stock_pair_digest_mismatch')
    require(design['kind'] == 'stock_phasea_threshold_pair_design' and type(design['schema_version']) is int and design['schema_version'] == 1 and
            index['kind'] == 'stock_phasea_threshold_pair' and type(index['schema_version']) is int and index['schema_version'] == 1 and
            index['operations'] == len(index['records']) == len(design['rows']) == 4 and
            {(r['topology'], r['initial_threshold']) for r in design['rows']} ==
            {(t, v) for t in ('Classic', 'Branch') for v in THRESHOLDS}, 'stock_pair_incomplete_matrix')
    require(design['all_jobs_frozen_before_native_operations'] is True and
            design['classification_assessed'] is index['classification_assessed'] is False and
            design['scientific_verdict'] is index['scientific_verdict'] is None, 'stock_pair_unsupported_scientific_claim')
    claimed = {r['name']: r for r in index['records']}
    require(len(claimed) == 4 and set(claimed) == {r['name'] for r in design['rows']}, 'stock_pair_record_inventory')
    code, runtime = load(directory/'code-identity.json'), load(directory/'runtime.json')
    rows = []
    templates = {}
    for row in design['rows']:
        name = row['name'];job = load(directory/'jobs'/f'{name}.json')
        validate_job('train', job)
        require(job['sha256'] == row['job_sha256'] and job['configuration']['model']['schema_version'] == 2 and
                job['configuration']['model']['initial_threshold'] == row['initial_threshold'], 'stock_pair_factor_changed')
        neutral = deepcopy(job);neutral.pop('sha256');neutral['configuration'].pop('run_id')
        neutral['configuration']['model'].pop('initial_threshold')
        if row['topology'] in templates:require(templates[row['topology']] == neutral, 'stock_pair_other_factors_changed')
        templates[row['topology']] = neutral
        expected = load(directory/'expected'/f'{name}.json')
        source = directory/'source/runs'/(row['topology']+'-stock-nspneurongen-inputs4')
        audit_run_manifest(source/'run-manifest.json')
        template = load(source/'input/job.json')
        source_model = template['configuration']['model']
        require(source_model['schema_version'] == 2 and source_model['initial_threshold'] == 100 and
                source_model['initial_isi'] == TARGET and source_model['normalization'] == 'N1' and
                source_model['neuron_class'] == 'NSPNeuronGen' and template['profile_archives'] == [],
                'stock_pair_source_template_changed')
        template.pop('sha256');template['configuration'].pop('run_id')
        template['configuration']['model'].pop('initial_threshold')
        require(neutral == template, 'stock_pair_source_other_factors_changed')
        initial = load(source/'native/initial-state.json')['identity']
        require(expected == _expected(initial, row['initial_threshold']) and
                expected['sha256'] == row['expected_initial_revision'], 'stock_pair_expected_model_changed')
        evidence = load(directory/'conditions'/f'{name}.json')
        require(evidence == _condition(job, expected, code, runtime), 'stock_pair_condition_not_effective')
        condition = ConditionSpec.loads(json.dumps(evidence['condition']))
        require(condition.fingerprint == row['condition_fingerprint'], 'stock_pair_condition_changed')
        for phase in ('preflights', 'runs'):
            folder = directory/phase/name
            audit_run_manifest(folder/'run-manifest.json')
            actual = load(folder/'native/initial-state.json')['identity']
            require(actual == expected and load(folder/'process/runtime.json') == runtime, 'stock_pair_initial_or_runtime_changed')
            audit_stock_profile(actual, branch=row['topology'] == 'Branch')
        execution = load(directory/'runs'/name/'native/execution.json')
        package = load(directory/'runs'/name/'native'/execution['package_path'])
        final_physics = audit_final_stock(expected, package['neuron']['graph']['identity'])
        measured = {'name': name, 'training_outcome': execution['training_outcome'],
                    'completed_boundary': execution['completed_boundary'], 'model_revision': execution['model_revision']}
        require(measured == claimed[name], 'stock_pair_producer_result_changed')
        rows.append({**row, **measured, 'final_stock_physics': final_physics})
    return {'kind': 'stock_phasea_threshold_pair_analysis', 'schema_version': 1,
            'execution': 'completed', 'validity': 'valid', 'rows': rows,
            'training_runs': 4, 'preflight_runs': 4, 'classification_assessed': False, 'scientific_verdict': None}
