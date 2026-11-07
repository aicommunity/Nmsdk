"""Separate single-pulse controls of exact archived candidates; no new Train."""
from copy import deepcopy
from pathlib import Path
import argparse
import csv
import hashlib
import json

from .native_characterization import prepare_single_pulse_job, validate_job
from .native_evidence import equal, load, measured_wave_plateaus, number, require
from .native_pipeline_worker import run_job, audit_run_manifest
from .n1_protocol_robustness import _signed, _write
from .single_pulse_evidence import read_single_pulse
from .stock_wave_replay import prepare, compare_traces, read_complete_burst
from .stopped_evidence import load_case


def compare_first_prefix(burst_packet, burst_trace, single_packet, single_trace):
    """Compare only before the second ACTUAL burst onset, in native relative time."""
    observed = burst_packet['observation'];begin = number(observed['specification']['begin'])
    require(observed['complete'] and len(observed['stimuli']) > 1, 'single_pulse_prefix_requires_complete_multi_impulse_burst')
    cutoff = number(observed['stimuli'][1]['time'])-begin
    _, burst = read_complete_burst(burst_packet,burst_trace)
    a = [{'time':s['time']-begin,'stimulus':s['stimulus'],'soma':s['soma']}
         for s in burst if s['time']-begin < cutoff]
    _,spec,_,samples,_,quality = read_single_pulse(single_packet,single_trace)
    require(quality['recorded_window_complete'], 'single_pulse_prefix_incomplete_characterization')
    b = [{'time':s['time']-spec['begin'],'stimulus':s['stimulus'],'soma':s['soma']}
         for s in samples if s['time']-spec['begin'] < cutoff]
    same_count = len(a) == len(b) and bool(a)
    same_clock = same_count and all(equal(x['time'],y['time']) for x,y in zip(a,b))
    same_input = same_count and all(x['stimulus'] == y['stimulus'] for x,y in zip(a,b))
    same_soma = same_count and all(x['soma'] == y['soma'] for x,y in zip(a,b))
    return {'cutoff_second_actual_onset_relative':cutoff,'samples':len(a),'same_sample_count':same_count,
            'relative_clock_equal_with_roundoff':same_clock,'stimulus_samples_exactly_equal':same_input,
            'soma_samples_exactly_equal':same_soma,'exact_first_prefix_reproduced':same_clock and same_input and same_soma,
            'scientific_verdict':None}


def run(study,runtime,output,*,process_policy=None,source_threshold=.0117):
    output = Path(output);sources = prepare(study,output,source_threshold=source_threshold);rows = []
    for row in sources['rows']:
        baseline = load(output/'jobs'/(row['name']+'.json'))
        baseline.update(schema_version=3,channel_diagnostics=True);baseline = _signed(baseline)
        validate_job(baseline)
        single = prepare_single_pulse_job(load_case(Path(row['source_state'])),baseline['probe']['input_index'],
                                         row['name']+'/single-pulse-characterization')
        burst_file = row['name']+'-burst.json';single_file = row['name']+'-single.json'
        _write(output/'jobs'/burst_file,baseline);_write(output/'jobs'/single_file,single)
        rows.append({**row,'burst_job':burst_file,'single_job':single_file,
                     'burst_job_sha256':baseline['sha256'],'single_job_sha256':single['sha256']})
    _write(output/'single-pulse-design.json',_signed({'kind':'stock_single_pulse_diagnostic_design','schema_version':1,
        'rows':rows,'all_jobs_frozen_before_native_operations':True,'training_started':False,'scientific_verdict':None}))
    (output/'runs').mkdir();results = []
    for row in rows:
        for mode in ('burst','single'):
            for key in ('source_state','original_packet','original_trace'):
                require(hashlib.sha256(Path(row[key]).read_bytes()).hexdigest() == row[key+'_sha256'],
                        'single_pulse_original_source_changed')
            folder = output/'runs'/(row['name']+'-'+mode)
            result = run_job('probe',output/'jobs'/row[mode+'_job'],row['source_state'],runtime,folder,900.,process_policy=process_policy)
            require(result['execution'] == 'completed' and result['validity'] == 'valid','single_pulse_native_execution_incomplete')
            audit_run_manifest(folder/'run-manifest.json')
        burst = output/'runs'/(row['name']+'-burst')/'native'
        single = output/'runs'/(row['name']+'-single')/'native'
        require(load(burst/'initial-state.json')['identity'] == load(single/'initial-state.json')['identity'] and
                load(single/'initial-state.json')['identity']['sha256'] == row['source_model_revision'],
                'single_pulse_actual_source_graph_changed')
        burst_packet = load(burst/'probe_trial_1.json');single_packet = load(single/'probe_trial_1.json')
        replay = compare_traces(load(Path(row['original_packet'])),row['original_trace'],burst_packet,burst/'probe_trial_1.csv')
        prefix = compare_first_prefix(burst_packet,burst/'probe_trial_1.csv',single_packet,single/'probe_trial_1.csv')
        require(replay['exact_waveform_reproduced'] and prefix['exact_first_prefix_reproduced'],
                'single_pulse_control_waveform_changed')
        _,spec,_,samples,n,quality = read_single_pulse(single_packet,single/'probe_trial_1.csv')
        peaks = []
        for i in range(n):
            values = [number(s['soma'][i]-spec['baseline'][i]) for s in samples]
            peaks.append({'soma':i,'positive_local_maxima':[
                {'relative_time':samples[first]['time']-spec['begin'],'raw_potential':samples[first]['soma'][i],
                 'amplitude':values[first],'plateau_end_relative':samples[last]['time']-spec['begin']}
                for first,last in measured_wave_plateaus(values,number(spec['minimum_amplitude']))]})
        results.append({'name':row['name'],'burst_matches_original_Train':replay,'first_prefix':prefix,
            'single_pulse_waveform_quality':quality,'single_pulse_peaks':peaks,
            'single_pulse_channels':load(single.parent/'run-manifest.json')['analysis']['channel_diagnostics'],
            'classification_evaluated':False,'scientific_verdict':None})
        _write(output/'progress.json',results)
    analysis = {'kind':'stock_single_pulse_characterization','schema_version':1,'rows':results,
                'training_started':False,'classification_evaluated':False,'scientific_verdict':None}
    _write(output/'analysis.json',analysis);return analysis


def main():
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('study',type=Path)
    p.add_argument('--runtime',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--source-threshold',type=float,default=.0117,help='Select archived source conditions; never change the model threshold')
    a = p.parse_args();print(json.dumps(run(a.study,a.runtime,a.output,source_threshold=a.source_threshold),indent=2))


if __name__ == '__main__':main()
