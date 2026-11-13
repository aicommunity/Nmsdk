"""Audit native subset waveforms; this never assigns peaks or scores learning."""
import csv
import hashlib
import io
from pathlib import Path

from .model_identity import canonical_model_sha256
from .clock_alignment import relative_clocks_equal
from .native_evidence import (EvidenceError, count, equal, number, parse_json_bytes,
                              require, require_primary_trace_clock)


def audit_subset(packet, rows, *, allow_draft_without_restoration=False, expected_trial_id=None):
    try:
        return _audit_subset(packet, rows, allow_draft_without_restoration, expected_trial_id)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError('malformed_stimulus_subset_evidence:'+str(error)) from error


def _audit_subset(p, rows, legacy, expected_trial_id):
    require(type(p) is dict and p['kind']=='native_stimulus_subset_diagnostic' and
            type(p['schema_version']) is int and p['schema_version'] in (1,2) and
            p['scientific_training_result'] is False, 'unknown_stimulus_subset_wrapper')
    require(p['schema_version']==2 or legacy, 'draft_subset_missing_restoration_readback')
    expected={'kind','schema_version','source_pattern','evidence','model_before','model_after',
              'training_target_restored','scientific_training_result'}
    if p['schema_version']==2:expected|={'training_pattern_after','dataset_pattern_after','physical_input_count_after'}
    require(set(p)==expected,'unknown_stimulus_subset_wrapper_fields')
    result = audit_subset_observation(p['evidence'], rows, p['source_pattern'],
                                      expected_trial_id=expected_trial_id)
    for key in ['model_before','model_after']:
        graph=p[key];require(graph['valid'] is True and graph['sha256']==result['model_revision'] and
            canonical_model_sha256(graph['model'])==result['model_revision'], 'subset_effective_graph_changed')
    restored='unknown'
    if p['schema_version']==2:
        for key in ['training_pattern_after','dataset_pattern_after']:
            require(type(p[key]) is list and all(number(v)==v for v in p[key]),'invalid_subset_restoration_readback')
        require(type(p['physical_input_count_after']) is int and
                p['physical_input_count_after']==result['physical_input_count'] and
                p['training_pattern_after']==p['source_pattern'] and p['dataset_pattern_after']==p['source_pattern'] and
                p['training_target_restored'] is True, 'subset_training_pattern_not_restored')
        restored='validated_readback'
    return dict(result, restoration=restored)


def audit_subset_observation(e, rows, source_pattern, *, expected_trial_id=None):
    """Check waveform only; graph/restoration require their separate readbacks."""
    try:
        return _audit_subset_observation(e, rows, source_pattern, expected_trial_id)
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError('malformed_stimulus_subset_observation:'+str(error)) from error


def _audit_subset_observation(e, rows, source_pattern, expected_trial_id):
    o=e['observation'];s=o['specification'];q=e['requested_specification'];prepared=e['prepared']
    require(e['kind']=='timelearner_native_probe_evidence' and type(e['evidence_schema_version']) is int and
            e['evidence_schema_version']==2 and e['native_status']=='completed' and
            e['requires_fresh_verification'] is False and e['reasons']==[], 'subset_execution_not_complete')
    require(type(s['schema_version']) is int and s['schema_version']==o['schema_version']==q['schema_version']==6 and
            o['complete'] is True and o['valid'] is True and o['end_reason']=='window_closed' and
            o['reasons']==[] and o['peaks']==[] and o['burst_assignments']==[] and
            o['spikes']==[] and o['spike_count'] is None and s['record_spikes'] is False,
            'subset_observation_not_diagnostic_complete')
    frequency=number(s['stimulus_profile']['frequency_hz'])
    require(s['time_frame']=='absolute_model_time' and q['time_frame']=='relative_to_trial_start' and
            number(q['begin'])==0. and relative_clocks_equal([number(s['end'])],number(s['begin']),
                [number(q['end'])],0.,frequency),
            'subset_requested_window_mismatch')
    for key in ['maximum_sample_gap','minimum_amplitude','maximum_samples','record_spikes']:
        require(s[key]==q[key],'subset_requested_policy_changed:'+key)
    for key in ['run_id','trial_id','sample_id','pattern_hash']:
        require(type(s[key]) is str and bool(s[key]) and s[key]==q[key], 'subset_identity_mismatch:'+key)
    require(s['trial_id']==(s['run_id']+'/probe0' if expected_trial_id is None else expected_trial_id),
            'subset_trial_identity_mismatch')
    require('characterization' not in s and 'characterization' not in q and s['windows']==q['windows']==[] and
            s['wave_assignment']==q['wave_assignment']=='window_only' and
            s['peak_selection']==q['peak_selection']=='isolated_window', 'subset_has_peak_assignment')
    c=s['stimulus_subset'];require(c==q['stimulus_subset'] and set(c)=={
        'purpose','source_training_pattern_hash','physical_input_count','source_ordinals'} and
        c['purpose']=='stimulus_subset_characterization', 'unknown_subset_presentation_metadata')
    n=count(c['physical_input_count']);indices=c['source_ordinals'];source=source_pattern
    require(n>0 and type(source) is list and len(source)==n and type(indices) is list and
            0<len(indices)<=n and all(type(i) is int and 0<=i<n for i in indices) and
            all(b>a for a,b in zip(indices,indices[1:])), 'invalid_subset_source_ordinals')
    source=[number(v) for v in source];require(all(v>=0 for v in source), 'invalid_subset_source_pattern')
    require(canonical_model_sha256(source)==c['source_training_pattern_hash'], 'subset_original_pattern_hash_mismatch')
    presented=[];start=0
    for index in indices:
        gap=0.
        for value in source[start:index+1]:gap=number(gap+value)
        presented.append(gap);start=index+1
    if len(indices)==n:presented=source[:]
    require(canonical_model_sha256(presented)==s['pattern_hash'], 'subset_presented_pattern_hash_mismatch')
    ids=['pulse'+str(i) for i in indices]
    require(s['expected_stimulus_ids']==q['expected_stimulus_ids']==ids and
            [v['id'] for v in o['stimuli']]==ids, 'subset_actual_stimulus_identity_mismatch')
    revision=e['current_base_revision']
    require(type(revision) is str and len(revision)==64 and prepared['base_model_revision']==revision and
            prepared['effective_model_revision']==s['effective_model_revision'], 'subset_revision_mismatch')
    routing=prepared['routing'];require(routing in ('classic_burst','branch_solo_burst'), 'unknown_subset_routing')
    channels=n if routing=='classic_burst' else 1
    require(len(s['baseline'])==channels and all(number(v)==v for v in s['baseline']), 'subset_baseline_shape_mismatch')
    if routing=='classic_burst':require(prepared['selected_input_index'] is None, 'unexpected_subset_selector')
    else:require(type(prepared['selected_input_index']) is int and 0<=prepared['selected_input_index']<n,
                 'invalid_subset_solo_selector')
    require(bool(rows) and rows[0]==['native_tick_start_s','stimulus']+['raw_soma_'+str(i) for i in range(channels)] and
            all(len(row)==channels+2 for row in rows[1:]), 'unknown_subset_trace_schema')
    values=[[number(float(v)) for v in row] for row in rows[1:]];times=[r[0] for r in values]
    require_primary_trace_clock(s,o['sample_count'],times)
    profile=s['stimulus_profile']
    require(frequency>0 and equal(number(s['maximum_sample_gap']),1/frequency) and
            number(profile['amplitude'])>0 and number(profile['pulse_length'])>=1/frequency and
            number(profile['frequency_deviation'])==0 and profile['use_transit_signal'] is False and
            profile['use_pattern_output'] is False, 'unsupported_subset_source_profile')
    require(type(profile['generator_class']) is str and bool(profile['generator_class']) and
            all(row[1] in (0.,profile['amplitude']) for row in values), 'subset_source_amplitude_mismatch')
    events=o['stimuli'];event_times=[number(v['time']) for v in events]
    require(all(b>a for a,b in zip(event_times,event_times[1:])), 'subset_actual_stimulus_order')
    for event,time in zip(events,event_times):
        found=[i for i,t in enumerate(times) if equal(t,time)]
        require(len(found)==1 and values[found[0]][1]>0 and
                equal(number(event['relative_to_trial_start']),time-number(s['begin'])),
                'subset_stimulus_not_in_actual_trace')
    require(equal(number(o['first_stimulus_time']),event_times[0]), 'subset_first_stimulus_mismatch')
    return {'kind':'native_stimulus_subset_trace_audit','schema_version':1,'run_id':s['run_id'],
            'model_revision':revision,'routing':routing,'physical_input_count':n,'channel_count':channels,
            'source_ordinals':indices,'source_pattern_hash':c['source_training_pattern_hash'],
            'presented_pattern_hash':s['pattern_hash'],'actual_stimuli':events,'frequency_hz':frequency,
            'sample_count':len(times),'recorded_window_complete':True,'restoration':'not_checked',
            'source_timing':'observed; paired full control required to establish retained timing invariance',
            'spike_response':'unknown','peak_assignment':'not_performed','scientific_verdict':None}


def read_console_subset_observation(packet, trace, source_pattern, *, expected_trial_id):
    """Lossless Console CSV header adapter; no graph/restoration attestation."""
    with Path(trace).open(newline='', encoding='utf-8') as stream:rows=list(csv.reader(stream))
    channels=len(source_pattern) if packet['prepared']['routing']=='classic_burst' else 1
    require(rows and rows[0]==['time','stimulus']+['soma'+str(i) for i in range(channels)],
            'unknown_console_subset_trace')
    rows[0]=['native_tick_start_s','stimulus']+['raw_soma_'+str(i) for i in range(channels)]
    quality=audit_subset_observation(packet,rows,source_pattern,expected_trial_id=expected_trial_id)
    samples=[dict(time=number(float(r[0])),stimulus=number(float(r[1])),
                  soma=[number(float(v)) for v in r[2:]]) for r in rows[1:]]
    observation=packet['observation']
    return observation,observation['specification'],samples,quality


def read_subset(path, *, allow_draft_without_restoration=False):
    path=Path(path);require(path.name.endswith('_subset.json'), 'unknown_subset_filename')
    stem=path.name[:-len('_subset.json')];trace=path.with_name(stem+'.csv')
    raw=path.read_bytes();data=trace.read_bytes();packet=parse_json_bytes(raw)
    rows=list(csv.reader(io.StringIO(data.decode('utf-8'))))
    result=audit_subset(packet,rows,allow_draft_without_restoration=allow_draft_without_restoration)
    require(result['run_id']==stem,'subset_filename_identity_mismatch')
    result['source_files']={path.name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},
                            trace.name:{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}}
    return result,packet,rows
