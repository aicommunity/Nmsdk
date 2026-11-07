"""Matched storage-image FeedbackGain intervention on full stopped models.

No training, threshold tuning, certificate or classification verdict. Original
and unchanged-image waveforms must match before any zero-feedback run starts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from .native_characterization import prepare_feedback_profile_job, prepare_single_pulse_job, prepare_stopped_job
from .native_evidence import equal, load, measured_wave_plateaus, number, require
from .native_pipeline_worker import run_job, audit_run_manifest
from .n1_protocol_robustness import _signed, _write
from .single_pulse_evidence import read_single_pulse
from .stock_wave_replay import prepare, compare_traces, read_complete_burst
from .stopped_evidence import load_case


def _samples(folder, single):
    packet=load(folder/'probe_trial_1.json');trace=folder/'probe_trial_1.csv'
    if single:
        observation,spec,_,samples,_,quality=read_single_pulse(packet,trace)
        require(quality['recorded_window_complete'], 'feedback_single_window_incomplete')
    else:
        spec,samples=read_complete_burst(packet,trace)
    return spec,samples


def compare_presentations(first, second, single):
    a_spec,a=_samples(first,single);b_spec,b=_samples(second,single)
    same_count=bool(a) and len(a)==len(b)
    clock=same_count and all(equal(x['time']-a_spec['begin'],y['time']-b_spec['begin']) for x,y in zip(a,b))
    stimulus=same_count and all(x['stimulus']==y['stimulus'] for x,y in zip(a,b))
    soma=same_count and all(x['soma']==y['soma'] for x,y in zip(a,b))
    return {'same_sample_count':same_count,'relative_clock_equal_with_roundoff':clock,
            'stimulus_samples_exactly_equal':stimulus,'soma_samples_exactly_equal':soma,
            'exact_waveform_reproduced':clock and stimulus and soma}


def run(study,runtime,output,*,process_policy=None):
    output=Path(output);sources=prepare(study,output);rows=[]
    for row in sources['rows']:
        case=load_case(Path(row['source_state']))
        original=load(output/'jobs'/(row['name']+'.json'));index=original['probe']['input_index']
        gains=[]
        for node in case[0]['neuron']['graph']['identity']['model']['nodes']:
            if 'FeedbackGain' in node['parameters']:
                prop=node['parameters']['FeedbackGain']
                require(prop['binding'] is False and prop['data']['type']=='binary64','feedback_source_gain_bound_or_unsupported')
                gains.append(number(struct.unpack('>d',bytes.fromhex(prop['data']['value']))[0]))
        require(gains and len(set(gains))==1 and gains[0]>0,'feedback_study_requires_uniform_positive_source_gain')
        for presentation in ('burst','single'):
            single=presentation=='single'
            for factor in ('original','baseline','gain0'):
                name=row['name']+'-'+presentation+'-'+factor
                if factor=='original':
                    builder=prepare_single_pulse_job if single else prepare_stopped_job
                    job=builder(case,index,name,channel_diagnostics=True)
                else:
                    # All changed physics is constructed in native storage, not
                    # imposed on the live imported neuron on each tick.
                    job=prepare_feedback_profile_job(case,index,name,image_prefix='StockFeedback'+('Branch' if case[0]['configuration']['model']['branch'] else 'Classic')+factor.title(),
                        feedback_gain=gains[0] if factor=='baseline' else 0.,baseline_reconstruction=factor=='baseline',single_pulse=single)
                _write(output/'jobs'/(name+'.json'),job)
                rows.append({**row,'name':name,'source_name':row['name'],'presentation':presentation,'factor':factor,
                             'source_feedback_gain':gains[0],'job_file':name+'.json','job_sha256':job['sha256']})
    require(len(rows)==12,'feedback_study_requires_twelve_frozen_jobs')
    _write(output/'feedback-design.json',_signed({'kind':'stock_feedback_profile_diagnostic_design','schema_version':1,
        'rows':rows,'all_jobs_frozen_before_native_operations':True,'training_started':False,'classification_evaluated':False,'scientific_verdict':None}))
    (output/'runs').mkdir();executed=[];baseline_checks=[]

    def execute(row):
        for key in ('source_state','original_packet','original_trace'):
            require(hashlib.sha256(Path(row[key]).read_bytes()).hexdigest()==row[key+'_sha256'],'feedback_study_source_changed')
        folder=output/'runs'/row['name']
        result=run_job('probe',output/'jobs'/row['job_file'],row['source_state'],runtime,folder,900.,process_policy=process_policy)
        require(result['execution']=='completed' and result['validity']=='valid','feedback_study_native_execution_incomplete')
        require(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'],'feedback_study_manifest_inconsistent')
        executed.append(row['name']);_write(output/'progress.json',{'executed':executed,'classification_evaluated':False})
        return folder/'native'

    for row in rows:
        if row['factor']=='gain0':continue
        current=execute(row)
        if row['factor']=='original' and row['presentation']=='burst':
            comparison=compare_traces(load(Path(row['original_packet'])),Path(row['original_trace']),
                                      load(current/'probe_trial_1.json'),current/'probe_trial_1.csv')
            require(comparison['exact_waveform_reproduced'],'feedback_original_burst_does_not_reproduce_Train')
        if row['factor']=='baseline':
            original=next(r for r in rows if r['source_name']==row['source_name'] and r['presentation']==row['presentation'] and r['factor']=='original')
            comparison=compare_presentations(output/'runs'/original['name']/'native',current,row['presentation']=='single')
            baseline_checks.append({'name':row['name'],**comparison})
            _write(output/'baseline-checks.json',baseline_checks)
            require(comparison['exact_waveform_reproduced'],'feedback_baseline_reconstruction_changes_waveform')
    require(len(baseline_checks)==4 and len(executed)==8,'feedback_baseline_gate_incomplete')
    # A failed reconstruction never admits an apparently causal intervention.
    for row in rows:
        if row['factor']=='gain0':execute(row)
    measurements=[]
    for row in rows:
        native=output/'runs'/row['name']/'native';spec,samples=_samples(native,row['presentation']=='single')
        peaks=[]
        for i in range(len(samples[0]['soma'])):
            values=[number(s['soma'][i]-spec['baseline'][i]) for s in samples]
            peaks.append({'soma':i,'positive_local_maxima':[{'relative_time':samples[first]['time']-spec['begin'],
                'amplitude':values[first],'plateau_end_relative':samples[last]['time']-spec['begin']}
                for first,last in measured_wave_plateaus(values,number(spec['minimum_amplitude']))]})
        measurements.append({'name':row['name'],'factor':row['factor'],'presentation':row['presentation'],
            'source_name':row['source_name'],'peaks':peaks,'model_revision':load(native/'initial-state.json')['identity']['sha256'],
            'channel_diagnostics':load(native.parent/'run-manifest.json')['analysis']['channel_diagnostics']})
    comparisons=[]
    for row in rows:
        if row['factor']!='gain0':continue
        baseline=next(r for r in rows if r['source_name']==row['source_name'] and r['presentation']==row['presentation'] and r['factor']=='baseline')
        comparisons.append({'name':row['name'],**compare_presentations(output/'runs'/baseline['name']/'native',output/'runs'/row['name']/'native',row['presentation']=='single')})
    analysis={'kind':'stock_feedback_profile_characterization','schema_version':1,'baseline_checks':baseline_checks,
        'measurements':measurements,'intervention_comparisons':comparisons,'training_started':False,
        'classification_evaluated':False,'training_certificate_created':False,'scientific_verdict':None}
    _write(output/'analysis.json',analysis);return analysis


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('study',type=Path)
    parser.add_argument('--runtime',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(run(args.study,args.runtime,args.output),indent=2))


if __name__=='__main__':main()
