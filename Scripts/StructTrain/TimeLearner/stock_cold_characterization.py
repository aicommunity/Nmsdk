"""Preregistered cold stock N4 burst probes; no Train or recognition claim.

Each assigned input is observed on a freshly constructed native image. The
wide diagnostic window does not define the subsequent training windows.
"""
from copy import deepcopy
from pathlib import Path

from .collector_provenance import frozen_digest
from .contained_process import inspect
from .native_calibration_worker import _signed, _write
from .native_characterization import audit_execution, validate_job
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest, run_job
from .native_process_policy import policy_for_reservation
from .process_runner import verify_runtime
from .resource_reservations import Reservations
from .stock_phasea_preflight import TARGET, audit_stock_profile


def jobs(topology='both'):
    require(topology in ('both', 'Classic', 'Branch'), 'stock_cold_probe_topology')
    result = {}
    for branch in (False, True):
        name = 'Branch' if branch else 'Classic'
        if topology not in ('both', name):
            continue
        model = dict(schema_version=2, branch=branch, frequency_hz=2000,
            neuron_class='NSPNeuronGen', dataset_class='NDatasetMatrix',
            generator_class='NPulseGeneratorTransit', neuron_structure_mode=2,
            normalization='N1', inputs=[dict(attachment=1, synapses=1, resistance=86e6)
                for _ in TARGET], initial_isi=TARGET[:],
            allocated_cable_lengths=[1] if branch else [1]*4,
            maximum_cable_length=100, preserve_allocated_cable=False,
            maximum_resistance_ratio=1000., configured_minimum_resistance=0.,
            inhibition=[], scale_inhibition_with_input=True,
            allow_muted_input_baseline=False, initial_threshold=100.)
        for i in range(4):
            key = name+'-cold-stock-input'+str(i)
            job = _signed(dict(kind='timelearner_native_probe_job', schema_version=1,
                owner_class='NNeuronTimeLearner'+('Branch' if branch else ''),
                implementation_id='stock-cold-four-input-burst-characterization-v1',
                model=deepcopy(model), profile_archives=[],
                stimulus_profile=dict(generator_class='NPulseGeneratorTransit',
                    amplitude=1., pulse_length=.001, frequency_hz=2000,
                    frequency_deviation=0., use_transit_signal=False,
                    use_pattern_output=False),
                probe=dict(run_id=key, trial_id=key+'/burst', sample_id='phasea-target',
                    protocol_revision='cold-stock-assigned-burst-diagnostic-v1',
                    input_index=i, duration=1.8, maximum_sample_gap=.0005,
                    minimum_amplitude=1e-6, maximum_samples=3605,
                    record_spikes=False, peak_selection='assigned_burst_wave',
                    window=dict(begin=0., end=1.8)),
                maximum_model_ticks=4000, maximum_wall_seconds=180.))
            validate_job(job)
            result[key] = job
    return result


def prepare(output, topology='both'):
    output = Path(output)
    require(not output.exists(), 'stock_cold_probe_preparation_exists')
    declared = jobs(topology)
    output.mkdir(parents=True)
    for name, job in declared.items():
        _write(output/(name+'.json'), job)
    index = dict(kind='timelearner_stock_cold_characterization', schema_version=1,
        topology=topology, jobs={name: job['sha256'] for name, job in declared.items()},
        training_started=False, training_windows_selected=False, scientific_verdict=None)
    _write(output/'index.json', index)
    return index


def run(source, runtime_path, controller, output):
    source = Path(source).resolve(strict=True)
    runtime_path = Path(runtime_path).resolve(strict=True)
    output = Path(output).resolve()
    require(not output.exists(), 'stock_cold_probe_result_exists')
    design = load(source/'index.json')
    expected = jobs(design.get('topology'))
    require(design == dict(kind='timelearner_stock_cold_characterization', schema_version=1,
        topology=design['topology'], jobs={n:j['sha256'] for n,j in expected.items()},
        training_started=False, training_windows_selected=False, scientific_verdict=None),
        'stock_cold_probe_design_changed')
    for name, job in expected.items():
        require(load(source/(name+'.json')) == job, 'stock_cold_probe_job_changed')
    require({p.name for p in source.iterdir()} == {'index.json', *(n+'.json' for n in expected)}
        and all(p.is_file() and not p.is_symlink() for p in source.iterdir()),
        'stock_cold_probe_source_inventory_changed')
    before = {p.name: frozen_digest(p, 1024**2) for p in source.iterdir() if p.is_file()}
    runtime = load(runtime_path);verify_runtime(runtime)
    output.mkdir(parents=True)
    _write(output/'design.json', design)
    registry = Reservations(output/'leases.sqlite3', managed_units=True,
        capacity=dict(slots=1, memory_bytes=8*1024**3, disk_bytes=2*1024**3, tasks=512))
    lease = registry.reserve('stock-cold-burst-'+design['topology'],
        [dict(path=str(output/'runs'), access='write')],
        demands=dict(slots=1, memory_bytes=6*1024**3, disk_bytes=1024**3, tasks=256),
        controller_directory=str(controller), ttl_seconds=1800)
    policy = policy_for_reservation(registry, lease['token'], memory_bytes=4*1024**3, tasks=64)
    rows = []
    for name, job in expected.items():
        folder = output/'runs'/name
        result = run_job('probe', source/(name+'.json'), None, runtime_path, folder, 180.,
            process_policy=policy)
        require(result['execution'] == 'completed' and result['validity'] == 'valid',
            'stock_cold_probe_execution_invalid')
        audit = audit_execution(folder/'native')
        initial = load(folder/'native/initial-state.json')
        physical = audit_stock_profile(initial['identity'], branch=job['model']['branch'])
        require(physical['initial_threshold'] == 100., 'stock_cold_probe_threshold_changed')
        require(inspect(folder/'process/contained')['all_processes_closed'], 'stock_cold_probe_group_live')
        run_audit = audit_run_manifest(folder/'run-manifest.json')
        rows.append(dict(name=name, physical=physical, probe=audit, run=run_audit))
        _write(output/('progress-'+str(len(rows))+'.json'), rows)
    require(before == {p.name: frozen_digest(p, 1024**2) for p in source.iterdir() if p.is_file()},
        'stock_cold_probe_sources_changed')
    registry.release(lease['token'], note='All declared cold diagnostic probe units closed; no Train/science claim.')
    result = dict(kind='timelearner_stock_cold_characterization_result', schema_version=1,
        rows=rows, training_started=False, training_windows_selected=False,
        source_unchanged=True, scientific_verdict=None)
    _write(output/'index.json', result)
    return result
