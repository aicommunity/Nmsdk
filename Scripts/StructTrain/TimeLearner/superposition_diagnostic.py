"""Compare a full burst with shifted single-pulse templates; never certify Train.

This tests a waveform hypothesis. A small residual does not establish linearity,
causal attribution of a burst maximum, or independent per-input measurements.
No model, threshold, pattern, observation policy or native result is modified.
"""
import csv
import hashlib
import math
from pathlib import Path
import sys

from .clock_alignment import specification_frequency
from .native_evidence import load, measured_wave_plateaus, number, require
from .native_pipeline_worker import audit_run_manifest
from .single_pulse_evidence import read_single_pulse
from .stock_wave_replay import read_complete_burst


def compare_samples(burst_spec, burst, single_spec, single, onset_times):
    """Diagnostic arithmetic on complete, independently audited native samples."""
    frequency = specification_frequency(burst_spec, single_spec)
    require(burst_spec['stimulus_profile'] == single_spec['stimulus_profile'], 'superposition_generator_physics_changed')
    require(burst_spec['baseline'] == single_spec['baseline'], 'superposition_baseline_changed')
    require(len(burst) == len(single) and len(burst) >= 3, 'superposition_sample_count_changed')
    n = len(burst_spec['baseline'])
    require(n > 0 and all(len(s['soma']) == n for s in burst+single), 'superposition_dimension_changed')
    require(len(onset_times) > 1, 'superposition_requires_burst')
    count = len(burst)
    # Bound accumulated binary64 arithmetic, not a physical timing tolerance.
    scale = max(1., *(abs(number(s['time'])) for s in burst+single),
                abs(number(burst_spec['begin'])), abs(number(single_spec['begin'])))
    allowance = 32*sys.float_info.epsilon*scale*(count+1)
    require(allowance < .25/frequency, 'superposition_clock_unresolvable')
    for spec, samples in ((burst_spec, burst), (single_spec, single)):
        for i, sample in enumerate(samples):
            require(abs(number(sample['time'])-(number(spec['begin'])+i/frequency)) <= allowance,
                    'superposition_not_complete_native_grid')
            number(sample['stimulus'])
            for value in sample['soma']:number(value)
    onsets = [number(t)-number(burst_spec['begin']) for t in onset_times]
    require(all(b > a for a,b in zip(onsets,onsets[1:])), 'superposition_onsets_not_ordered')
    shifts = []
    for onset in onsets:
        delta = onset-onsets[0];tick = round(delta*frequency)
        require(0 <= tick < count and abs(delta-tick/frequency) <= 2*allowance,
                'superposition_fractional_tick_shift')
        shifts.append(tick)
    template_input = [number(v['stimulus']) for v in single]
    require(all(number(v['stimulus']) == math.fsum(template_input[i-k] for k in shifts if i >= k)
                for i,v in enumerate(burst)), 'superposition_input_reconstruction_mismatch')
    observed = [[number(s['soma'][c]-burst_spec['baseline'][c]) for s in burst] for c in range(n)]
    template = [[number(s['soma'][c]-single_spec['baseline'][c]) for s in single] for c in range(n)]
    predicted = [[number(math.fsum(template[c][i-k] for k in shifts if i >= k))
                  for i in range(count)] for c in range(n)]
    residual = [[number(observed[c][i]-predicted[c][i]) for i in range(count)] for c in range(n)]
    rows = []
    minimum = number(burst_spec['minimum_amplitude'])
    for c in range(n):
        def peaks(values):
            return [{'relative_time':first/frequency,'amplitude':values[first],
                     'plateau_end_relative':last/frequency}
                    for first,last in measured_wave_plateaus(values, minimum)]
        oi = max(range(count), key=observed[c].__getitem__)
        pi = max(range(count), key=predicted[c].__getitem__)
        error = max(abs(v) for v in residual[c])
        scale = max(abs(v) for v in observed[c])
        rows.append({'channel':c,'observed_global_maximum':{'relative_time':oi/frequency,'amplitude':observed[c][oi]},
                     'predicted_global_maximum':{'relative_time':pi/frequency,'amplitude':predicted[c][pi]},
                     'observed_local_maxima':peaks(observed[c]),'predicted_local_maxima':peaks(predicted[c]),
                     'single_template_local_maxima':peaks(template[c]),
                     'max_abs_residual':error,'rms_residual':math.sqrt(math.fsum(v*v for v in residual[c])/count),
                     'max_abs_residual_div_observed_absolute_maximum':error/scale if scale else None})
    summary = {'kind':'timelearner_shifted_single_template_diagnostic','schema_version':1,
               'frequency_hz':frequency,'samples':count,'native_tick_shifts':shifts,
               'clock_roundoff_allowance_seconds':allowance,'input_reconstruction_exact':True,'channels':rows,
               'assumption':'sum of time-shifted isolated responses relative to native baseline',
               'negative_template_indices':'declared native baseline, no recorded prehistory',
               'linear_superposition_proven':False,'assigned_impulse_peaks_certified':False,
               'classification_evaluated':False,'scientific_verdict':None}
    return summary, observed, predicted, residual


def analyze_pair(burst_directory, single_directory, output_csv):
    burst_directory, single_directory = Path(burst_directory), Path(single_directory)
    files = {}
    for label, directory in [('burst',burst_directory),('single',single_directory)]:
        require(audit_run_manifest(directory.parent/'run-manifest.json')['run_evidence_consistent'],
                'superposition_run_manifest_inconsistent')
        for name in ['initial-state.json','probe_trial_1.json','probe_trial_1.csv']:
            p = directory/name
            files[label+'/'+name] = {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    require(load(burst_directory/'initial-state.json')['identity'] == load(single_directory/'initial-state.json')['identity'],
            'superposition_source_graph_changed')
    bp = load(burst_directory/'probe_trial_1.json');sp = load(single_directory/'probe_trial_1.json')
    require(all(bp['prepared'][k] == sp['prepared'][k] for k in
                ('routing','input_id','selected_input_index','base_model_revision','effective_model_revision')),
            'superposition_effective_routing_or_model_changed')
    bs, burst = read_complete_burst(bp, burst_directory/'probe_trial_1.csv')
    _, ss, _, single, _, quality = read_single_pulse(sp, single_directory/'probe_trial_1.csv')
    require(quality['recorded_window_complete'] and bp['observation']['complete'], 'superposition_incomplete_observation')
    require(bs['pattern_hash'] == ss['characterization']['source_training_pattern_hash'] and
            len(bs['expected_stimulus_ids']) == ss['characterization']['physical_input_count'],
            'superposition_training_pattern_changed')
    events = bp['observation']['stimuli']
    require(events[0]['time']-bs['begin'] == sp['observation']['stimuli'][0]['time']-ss['begin'],
            'superposition_first_onset_changed')
    summary, observed, predicted, residual = compare_samples(bs,burst,ss,single,[v['time'] for v in events])
    summary.update(primary_inputs=files,source_model_revision=bp['current_base_revision'],
                   original_training_measurement_valid=bp['observation']['valid'],
                   original_training_measurement_reasons=bp['observation']['reasons'])
    with Path(output_csv).open('x',encoding='utf-8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['relative_time','actual_stimulus']+[f'{kind}_{c}' for c in range(len(observed))
                                                          for kind in ('observed','predicted','residual')])
        for i, sample in enumerate(burst):
            writer.writerow([i/summary['frequency_hz'],sample['stimulus']]+
                            [values[c][i] for c in range(len(observed)) for values in (observed,predicted,residual)])
    summary['comparison_csv_sha256'] = hashlib.sha256(Path(output_csv).read_bytes()).hexdigest()
    return summary
