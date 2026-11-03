"""Check the real four-input stock NSPNeuronGen before scientific cold Train.

This builds through native preflight, never calculates or imports a trained
model. The earlier fixture supplies configuration syntax only, not physics.
"""
from copy import deepcopy
import re
from pathlib import Path

from .domain_evidence import _property
from .model_identity import canonical_model_sha256 as sha
from .n1_protocol_robustness import _inventory, _signed, _write, unpack_calibration
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest, run_job, validate_job
from .process_runner import verify_runtime


TARGET = [.01, .08, .16, .24]


def make_stock_job(solo, name):
    c = deepcopy(solo['configuration'])
    c.update(run_id=name, protocol_revision='stock-nspneurongen-phasea-target-v1', duration=1.8,
             maximum_samples=3605, maximum_model_seconds=3600, maximum_wall_seconds=7200,
             maximum_reference_probes=8, maximum_invalid_reference_probes=0,
             peak_selection='assigned_burst_wave', windows=[{'begin': 0, 'end': 1.8} for _ in TARGET])
    m = c['model']
    m.update(neuron_class='NSPNeuronGen', initial_isi=TARGET[:], maximum_cable_length=100,
             inputs=[{'attachment': 1, 'synapses': 1, 'resistance': 86e6} for _ in TARGET],
             allocated_cable_lengths=[1] if m['branch'] else [1]*4)
    require(m['frequency_hz'] == 2000 and m['normalization'] == 'N1' and m['inhibition'] == [],
            'stock_preflight_template_scope')
    c['search'].update(bounds=[{'minimum_length': 1, 'maximum_length': 100 if i < 3 else 1,
                               'minimum_synapses': 1, 'maximum_synapses': 1,
                               'minimum_resistance': 1e6 if i < 3 else 86e6, 'maximum_resistance': 86e6}
                              for i in range(4)], maximum_candidates_per_input=512,
                       maximum_edits=2048, maximum_probes=2048, maximum_sweeps=4)
    require(c['search']['tolerances'] == {'amplitude_absolute': 1e-5, 'amplitude_relative': 0, 'sync': .02},
            'stock_preflight_original_tolerances_required')
    # Empty archives is intentional: use the existing native registered image,
    # not the modified fixture archived in Solo. No parent/child repair writes.
    job = _signed({'kind': 'timelearner_native_training_job', 'schema_version': 1,
        'owner_class': 'NNeuronTimeLearner'+('Branch' if m['branch'] else ''),
        'implementation_id': 'native-stock-phasea-four-input-v1', 'configuration': c,
        'profile_archives': [], 'optional_modes': {'sync_capacitance_trim': 0,
            'post_train_tuning': False, 'auto_calibrate_threshold': False},
        'calculate_mode': 0, 'structure_build_mode': 1, 'maximum_model_ticks': 7200000})
    validate_job('preflight', job)
    return job


def audit_stock_profile(identity, *, branch):
    """Inspect actual descendants, including the absence of an LT membrane."""
    require(identity['valid'] is True and identity['diagnostics'] == [] and
            identity['sha256'] == sha(identity['model']), 'stock_profile_identity_invalid')
    nodes = identity['model']['nodes']
    paths = {n['path']: n for n in nodes}
    require(len(paths) == len(nodes) and paths['$']['class'] == 'NSPNeuronGen', 'stock_profile_not_native_image')
    require(not any(p == '$.LTMembrane' or p.startswith('$.LTMembrane.') for p in paths),
            'stock_profile_unexpected_lt_membrane')
    require(all(n['frequency_hz'] == '2000' for n in nodes), 'stock_profile_frequency_mismatch')
    membrane_paths = {p for p in paths if re.fullmatch(r'\$\.(?:Soma\d+|Dendrite\d+_\d+)', p)}
    expected = {'$.Soma1', '$.Dendrite1_1'} if branch else {
        f'$.{kind}{i}'+('_1' if kind == 'Dendrite' else '') for kind in ('Soma', 'Dendrite') for i in range(1, 5)}
    require(membrane_paths == expected and all(paths[p]['class'] == 'NPMembraneBio' for p in membrane_paths),
            'stock_profile_cold_structure_mismatch')
    channels = synapses = 0
    for path in sorted(membrane_paths):
        for role, sign in [('Exc', -1.), ('Inh', 1.)]:
            node = paths[path+'.'+role+'Channel']
            require(node['class'] == 'NP'+role+'ChannelBio', 'stock_profile_channel_class_mismatch')
            for key, value in {'Capacity': 1e-9, 'Resistance': 1e7, 'RestingResistance': 1e7,
                               'FBResistance': 1e7, 'Type': sign}.items():
                require(_property(node, key) == value, 'stock_profile_channel_physics_mismatch:'+key)
            channels += 1
        bank = [n for p, n in paths.items() if p.startswith(path+'.') and n['class'] == 'NPSynapseBio']
        require(bool(bank), 'stock_profile_synapse_missing')
        for node in bank:
            for key, value in {'Resistance': 86e6, 'SecretionTC': .001, 'DissociationTC': .005,
                               'TypicalPulseDuration': .001, 'UsePresynapticInhibition': False,
                               'InhibitionCoeff': 0.}.items():
                require(_property(node, key) == value, 'stock_profile_synapse_physics_mismatch:'+key)
            synapses += 1
    require('$.LTZone' in paths and paths['$.LTZone']['class'] == 'NPulseLTZoneThreshold',
            'stock_profile_ltzone_mismatch')
    return {'profile': 'NSPNeuronGen', 'lt_membrane': False, 'input_count': 4,
            'body_membranes': len(membrane_paths), 'channels_checked': channels,
            'synapses_checked': synapses, 'frequency_hz': 2000,
            'initial_threshold': _property(paths['$.LTZone'], 'Threshold'),
            'model_revision': identity['sha256'], 'training_started': False,
            'historical_dynamics_equivalence_proven': False, 'scientific_verdict': None}


def run_stock_preflight(bundle, runtime_path, output):
    output = Path(output)
    require(not output.exists(), 'stock_preflight_output_exists')
    runtime = load(Path(runtime_path));verify_runtime(runtime)
    unpack_calibration(bundle, output/'source')
    before = _inventory(output/'source')
    _write(output/'runtime.json', runtime)
    (output/'jobs').mkdir();(output/'runs').mkdir()
    jobs = []
    for top in ('Classic', 'Branch'):
        source = load(output/'source/corpus/runs'/f'{top}-grid/native/transaction.json')['source_recognition']['source_solo']
        name = top+'-stock-nspneurongen-inputs4'
        job = make_stock_job(source, name)
        _write(output/'jobs'/f'{name}.json', job)
        jobs.append((name, job))
    # Both complete declarations precede the first native creation.
    _write(output/'design.json', {'kind': 'stock_phasea_native_preflight_design', 'schema_version': 1,
           'source_archive_sha256': load(output/'source/source-bundle.json')['archive_sha256'],
           'jobs': {name: job['sha256'] for name, job in jobs}, 'uses_fixture_physics': False,
           'training_run': False, 'scientific_verdict': None})
    rows = []
    for name, job in jobs:
        print('PREFLIGHT', name, flush=True)
        result = run_job('preflight', output/'jobs'/f'{name}.json', None,
                         output/'runtime.json', output/'runs'/name, 180.)
        require(result['execution'] == 'completed' and result['validity'] == 'valid', 'stock_preflight_native_failed')
        run_audit = audit_run_manifest(output/'runs'/name/'run-manifest.json')
        initial = load(output/'runs'/name/'native/initial-state.json')
        profile = audit_stock_profile(initial['identity'], branch=job['configuration']['model']['branch'])
        rows.append({'name': name, 'run_audit': run_audit, 'profile': profile})
        _write(output/'progress.json', rows)
    require(before == _inventory(output/'source'), 'stock_preflight_source_changed')
    index = {'kind': 'stock_phasea_native_preflight', 'schema_version': 1, 'rows': rows,
             'operations': 2, 'training_started': False, 'source_files_unchanged': len(before), 'scientific_verdict': None}
    _write(output/'index.json', index)
    return index
