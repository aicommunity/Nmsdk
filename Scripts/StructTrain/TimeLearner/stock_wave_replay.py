"""Replay the first invalid stock burst only from its exact archived model.

This diagnoses measurement repeatability. It never repairs a peak, restarts
training, changes a threshold, or treats a stopped state as a trained model.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json

from .native_evidence import audit_probe, equal, load, number, require
from .clock_alignment import relative_clocks_equal, specification_frequency
from .native_characterization import prepare_stopped_job, audit_execution
from .native_pipeline_worker import run_job, audit_run_manifest
from .n1_protocol_robustness import _signed, _write
from .probe_diagnostics import read_partial_probe
from .stock_recovery_study import audit_design
from .stopped_evidence import load_case


def select_packet(package):
    """Do not substitute the final model for an earlier, different candidate."""
    invalid = [p for p in package['observed_packets']
               if p['observation'] is not None and not p['observation']['valid']]
    require(bool(invalid), 'wave_replay_no_invalid_probe')
    packet = invalid[0]
    require(packet['prepared']['base_model_revision'] == package['model_revision'],
            'wave_replay_requires_intermediate_model_archive')
    require(package['neuron']['graph']['identity']['sha256'] == package['model_revision'],
            'wave_replay_source_graph_revision_mismatch')
    require(packet['observation']['complete'] is True and
            packet['observation']['specification']['peak_selection'] == 'assigned_burst_wave',
            'wave_replay_requires_complete_assigned_burst')
    return packet


def prepare(study, output, *, source_threshold=.0117):
    study, output = Path(study).resolve(strict=True), Path(output).resolve()
    require(not output.exists() and not output.is_relative_to(study) and
            not study.is_relative_to(output), 'wave_replay_output_overlap_or_exists')
    require(number(source_threshold) > 0, 'wave_replay_invalid_source_threshold')
    original = audit_design(study)
    selected = sorted((r for r in original['rows'] if r['initial_threshold'] == source_threshold and
                       r['policy'] == 'retry_same_candidate'), key=lambda r: r['name'])
    require(len(selected) == 2 and {r['topology'] for r in selected} == {'Classic', 'Branch'},
            'wave_replay_requires_both_selected_threshold_retry_controls')
    jobs, rows = [], []
    for row in selected:
        source = study/'runs'/row['name']/'native/train_stopped_state.json'
        case = load_case(source)
        packet = select_packet(case[0])
        input_id = packet['prepared']['input_id']
        matches = [i for i, v in enumerate(case[0]['protocol']['inputs']) if v['id'] == input_id]
        require(len(matches) == 1, 'wave_replay_input_identity_unknown')
        job = prepare_stopped_job(case, matches[0], row['name']+'/exact-invalid-wave-replay')
        require(job['resistance_intervention'] == [] and
                job['probe']['peak_selection'] == packet['requested_specification']['peak_selection'] and
                job['stimulus_profile'] == packet['requested_specification']['stimulus_profile'],
                'wave_replay_protocol_changed')
        trial = packet['requested_specification']['trial_id']
        old_path = case[3][trial].with_suffix('.json')
        rows.append({'name': row['name'], 'source_state': str(source),
                     'source_state_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'source_model_revision': case[0]['model_revision'],
                     'original_trial_id': trial, 'original_packet': str(old_path),
                     'original_packet_sha256': hashlib.sha256(old_path.read_bytes()).hexdigest(),
                     'original_trace': str(case[3][trial]),
                     'original_trace_sha256': hashlib.sha256(case[3][trial].read_bytes()).hexdigest(),
                     'job_sha256': job['sha256']})
        jobs.append(job)
    output.mkdir();(output/'jobs').mkdir()
    for row, job in zip(rows, jobs):
        _write(output/'jobs'/(row['name']+'.json'), job)
    design = _signed({'kind': 'stock_exact_invalid_wave_replay', 'schema_version': 1,
                      'source_study': str(study), 'rows': rows,
                      'all_jobs_frozen_before_native_operations': True,
                      'training_started': False, 'scientific_verdict': None})
    _write(output/'design.json', design)
    return design


def read_complete_burst(packet, trace):
    """Read primary burst data after valid or explicit whole-window diagnostic audit."""
    if packet['observation']['valid']:
        audit_probe(packet, Path(trace))
        with Path(trace).open(encoding='utf-8', newline='') as stream:
            rows = list(csv.reader(stream))[1:]
        samples = [{'time': number(float(row[0])), 'stimulus': number(float(row[1])),
                    'soma': [number(float(v)) for v in row[2:]]} for row in rows]
        return packet['observation']['specification'], samples
    partial = read_partial_probe(packet, Path(trace))
    require(partial[5]['recorded_window_complete'] and not partial[5]['nonfinite_cells'],
            'wave_replay_comparison_requires_complete_finite_windows')
    return partial[1], partial[3]


def compare_traces(original_packet, original_trace, replay_packet, replay_trace):
    """Report changes, including a mismatch; do not turn resemblance into PASS."""
    old_spec, a = read_complete_burst(original_packet, original_trace)
    new_spec, b = read_complete_burst(replay_packet, replay_trace)
    same_count = len(a) == len(b)
    same_clock = same_count and relative_clocks_equal([x['time'] for x in a],old_spec['begin'],
        [x['time'] for x in b],new_spec['begin'],specification_frequency(old_spec,new_spec))
    same_input = same_count and all(x['stimulus'] == y['stimulus'] for x, y in zip(a, b))
    same_signal = same_count and all(x['soma'] == y['soma'] for x, y in zip(a, b))
    return {'same_sample_count': same_count, 'relative_clock_equal_with_roundoff': same_clock,
            'stimulus_samples_exactly_equal': same_input, 'soma_samples_exactly_equal': same_signal,
            'original_reasons': original_packet['observation']['reasons'],
            'replay_reasons': replay_packet['observation']['reasons'],
            'exact_waveform_reproduced': same_clock and same_input and same_signal,
            'scientific_verdict': None}


def run(study, runtime, output, *, process_policy=None):
    output = Path(output)
    design = prepare(study, output);(output/'runs').mkdir()
    rows = []
    for row in design['rows']:
        for key in ('source_state', 'original_packet', 'original_trace'):
            require(hashlib.sha256(Path(row[key]).read_bytes()).hexdigest() == row[key+'_sha256'],
                    'wave_replay_original_primary_changed')
        folder = output/'runs'/row['name']
        result = run_job('probe', output/'jobs'/(row['name']+'.json'), row['source_state'],
                         runtime, folder, 900., process_policy=process_policy)
        require(result['execution'] == 'completed' and result['validity'] == 'valid',
                'wave_replay_execution_incomplete')
        audit_run_manifest(folder/'run-manifest.json');audit_execution(folder/'native')
        initial = load(folder/'native/initial-state.json')
        require(initial['identity']['sha256'] == row['source_model_revision'],
                'wave_replay_actual_import_changed')
        packet = load(folder/'native/probe_trial_1.json')
        comparison = compare_traces(load(Path(row['original_packet'])), row['original_trace'],
                                    packet, folder/'native/probe_trial_1.csv')
        rows.append({'name': row['name'], 'actual_model_revision': initial['identity']['sha256'],
                     **comparison})
        _write(output/'progress.json', rows)
    result = {'kind': 'stock_exact_invalid_wave_replay_analysis', 'schema_version': 1,
              'rows': rows, 'training_started': False, 'scientific_verdict': None,
              'causal_physics_explanation_attested': False}
    _write(output/'analysis.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.study, args.runtime, args.output), indent=2))


if __name__ == '__main__':
    main()
