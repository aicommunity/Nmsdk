"""Portable domain packets: literal independent fixtures, no native simulator.

Run only on the designated workers with the rest of the experiment tooling.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from ..native_evidence import EvidenceError
from ..response_domain_evidence import audit_response_domain_evidence, audit_response_domain_file


def fixture(schema=3):
    times = [i/10 for i in range(11)]
    raw = [2.,2.,3.,5.,3.,2.,3.,6.,3.,2.,2.]
    csv = ('time,stimulus,soma0,soma1\n' + ''.join(
        f'{t:.17g},{int(i in (1,5))},{v:.17g},{v:.17g}\n' for i,(t,v) in enumerate(zip(times,raw)))).encode()
    profile = dict(generator_class='NPulseGeneratorTransit', amplitude=1., pulse_length=.1, frequency_hz=10.,
                   frequency_deviation=0., use_transit_signal=False, use_pattern_output=False)
    windows = [dict(input_id='i0',stimulus_id='p0',channel=0,begin=.1,end=.5),
               dict(input_id='i1',stimulus_id='p1',channel=1,begin=.5,end=.9)]
    spec = dict(time_frame='absolute_model_time', schema_version=schema, run_id='run', trial_id='trial',
                sample_id='sample', pattern_hash='pattern', effective_model_revision='effective',begin=0.,end=1.,
                maximum_sample_gap=.1,minimum_amplitude=.5,maximum_samples=11,record_spikes=False,baseline=[2.,2.],
                windows=windows,expected_stimulus_ids=['p0','p1'],stimulus_profile=profile,
                wave_assignment='ordered_whole_burst' if schema==3 else 'window_only',peak_selection='isolated_window')
    requested=deepcopy(spec);requested.update(time_frame='relative_to_trial_start',baseline=[],effective_model_revision='')
    maxima=[dict(first_sample=3,last_sample=3,amplitude=3.,raw=5.,time=.3,plateau_end=.3),
            dict(first_sample=7,last_sample=7,amplitude=4.,raw=6.,time=.7,plateau_end=.7)]
    native_peaks=[]
    for sid,inp,m,onset in [('p0','i0',maxima[0],.1),('p1','i1',maxima[1],.5)]:
        native_peaks.append(dict(input_id=inp,stimulus_id=sid,validity='valid',amplitude=m['amplitude'],raw_potential=m['raw'],
            time=m['time'],plateau_end=m['plateau_end'],delay_from_stimulus=m['time']-onset,
            relative_to_trial_start=m['time'],candidate_count=1))
    waves=[dict(stimulus_id=sid,amplitude=m['amplitude'],raw_potential=m['raw'],time=m['time'],plateau_end=m['plateau_end'],
                relative_to_trial_start=m['time']) for sid,m in zip(('p0','p1'),maxima)]
    observation=dict(schema_version=schema,specification=spec,complete=True,valid=True,end_reason='window_closed',reasons=[],
        sample_count=11,stimuli=[dict(id='p0',time=.1,relative_to_trial_start=.1),dict(id='p1',time=.5,relative_to_trial_start=.5)],
        peaks=native_peaks,burst_assignments=[dict(channel=i,validity='valid',waves=deepcopy(waves)) for i in range(2)] if schema==3 else [],
        spikes=[],spike_count=None,first_stimulus_time=.1)
    native=dict(kind='timelearner_native_probe_evidence',evidence_schema_version=2,native_status='completed',
        current_base_revision='base',reasons=[],requires_fresh_verification=False,requested_specification=requested,
        prepared=dict(routing='classic_burst',input_id='i0',protocol_revision='protocol',base_model_revision='base',
                      effective_model_revision='effective',model_epoch=0,selected_input_index=None),observation=observation)
    domains=[dict(channel=ch,stimulus_id=sid,begin=begin,end=end) for ch in range(2)
             for sid,begin,end in [('p0',.1,.5),('p1',.5,.9)]]
    associations=[]
    for d in domains:
        selected=int(d['stimulus_id']=='p1');onset=.5 if selected else .1;t=.7 if selected else .3
        associations.append(dict(channel=d['channel'],stimulus_id=d['stimulus_id'],status='hypothesis',
            reason='exclusive_maximum_under_declared_domains_not_proven_origin',candidate_maxima=[selected],
            largest_measured_maximum=selected,selected_maximum=selected,actual_stimulus_time=onset,
            maximum_offset_low=t-onset,maximum_offset_high=t-onset,competing_stimulus_ids=[]))
    packet=dict(kind='timelearner_native_response_domain_evidence',schema_version=1,method='declared-response-domains-diagnostic-v1',
        diagnostic_only=True,training_certificate_eligible=False,scientific_verdict=None,native_evidence=native,
        domain_spec=dict(schema_version=1,model_revision='effective',protocol_revision='protocol',pattern_hash='pattern',
                         stimulus_ids=['p0','p1'],channel_ids=[0,1],domains=domains),
        capture=dict(run_id='run',trial_id='trial',sample_id='sample',complete=True,sample_count=11,begin=0.,end=1.,
            maximum_sample_gap=.1,minimum_amplitude=.5,channel_mapping=[dict(channel=i,physical_path='Soma'+str(i+1),
                csv_column='soma'+str(i),baseline=2.) for i in range(2)]),
        trace=dict(format='native-probe-csv-v1',path='trace.csv',bytes=len(csv),sha256=hashlib.sha256(csv).hexdigest(),
                   header=['time','stimulus','soma0','soma1'],time_frame='absolute_model_time'),
        analysis=dict(channels=[dict(channel=i,first_source_sample=0,feature_validity='valid',positive_maxima=deepcopy(maxima),
            global_maximum=deepcopy(maxima[1]),largest_interior_maximum_count=1,global_maximum_clipped=False,
            boundary_response_clipped=False) for i in range(2)],associations=associations,reasons=[]))
    return packet,csv


class ResponseDomainEvidenceTest(unittest.TestCase):
    def reject(self,p,raw):
        with self.assertRaises(EvidenceError): audit_response_domain_evidence(p,raw)

    def test_complete_schema2_and3_are_diagnostic_only(self):
        for schema in (2,3):
            p,raw=fixture(schema);result=audit_response_domain_evidence(p,raw)
            self.assertTrue(result['primary_trace_checked']);self.assertTrue(result['domain_graph_recomputed'])
            self.assertFalse(result['training_certificate_eligible']);self.assertFalse(result['causal_origin_verified'])
            self.assertFalse(result['physical_paths_independently_verified']);self.assertFalse(result['native_execution_verified'])

    def test_local_maximum_is_not_replaced_by_higher_full_maximum(self):
        p,raw=fixture();self.assertEqual(p['analysis']['associations'][0]['selected_maximum'],0)
        self.assertEqual(p['analysis']['channels'][0]['global_maximum']['time'],.7)
        audit_response_domain_evidence(p,raw)

    def test_reproduced_legacy_invalid_window_does_not_erase_complete_waveform(self):
        p,raw=fixture();e=p['native_evidence'];s=e['observation']['specification'];q=e['requested_specification']
        for spec in (s,q):spec['windows'][0].update(begin=0.,end=1.)
        e['observation'].update(valid=False,reasons=['peak_ambiguous:i0'])
        peak=e['observation']['peaks'][0]
        peak.update(validity='ambiguous',amplitude=None,raw_potential=None,time=None,plateau_end=None,
                    delay_from_stimulus=None,relative_to_trial_start=None,candidate_count=2)
        self.assertTrue(audit_response_domain_evidence(p,raw)['legacy_recorder_recomputed'])

    def test_foreign_or_changed_csv_is_not_accepted_by_recorded_clear_analysis(self):
        p,raw=fixture();self.reject(p,raw+b'\n')
        changed=raw.replace(b',5,5\n',b',9,5\n',1)
        p['trace'].update(bytes=len(changed),sha256=hashlib.sha256(changed).hexdigest());self.reject(p,changed)

    def test_changed_measured_maximum_plateau_or_association_is_rejected(self):
        for change in ('maximum','plateau','selection','signed_offset','candidate_bool'):
            p,raw=fixture()
            if change=='maximum':p['analysis']['channels'][0]['positive_maxima'][0]['raw']=9.
            elif change=='plateau':p['analysis']['channels'][0]['positive_maxima'][0]['last_sample']=4
            elif change=='selection':p['analysis']['associations'][0]['selected_maximum']=1
            elif change=='signed_offset':p['analysis']['associations'][0]['maximum_offset_low']=0.
            else:p['analysis']['associations'][0]['candidate_maxima']=[True]
            self.reject(p,raw)

    def test_channel_mapping_and_missing_competitor_are_rejected(self):
        p,raw=fixture();p['capture']['channel_mapping'].reverse();self.reject(p,raw)
        p,raw=fixture();p['domain_spec']['domains'].pop();self.reject(p,raw)

    def test_event_and_revision_changes_are_rejected(self):
        p,raw=fixture();p['native_evidence']['observation']['stimuli'][1].update(time=.6,relative_to_trial_start=.6);self.reject(p,raw)
        p,raw=fixture();p['domain_spec']['model_revision']='other';self.reject(p,raw)
        p,raw=fixture();p['native_evidence']['current_base_revision']='effective';self.reject(p,raw)

    def test_nonfinite_and_false_certificate_claim_are_rejected(self):
        p,raw=fixture();changed=raw.replace(b',5,5\n',b',nan,5\n',1)
        p['trace'].update(bytes=len(changed),sha256=hashlib.sha256(changed).hexdigest());self.reject(p,changed)
        p,raw=fixture();p['training_certificate_eligible']=True;self.reject(p,raw)
        p,raw=fixture();p['native_evidence']['requested_specification']['baseline']=[float('nan')];self.reject(p,raw)

    def test_unknown_integrity_reason_and_stale_native_peak_are_rejected(self):
        p,raw=fixture();p['native_evidence']['observation'].update(valid=False,reasons=['unknown_integrity_failure']);self.reject(p,raw)
        p,raw=fixture();p['native_evidence']['observation']['peaks'][0]['amplitude']=99.;self.reject(p,raw)

    def test_unknown_source_and_schema_fail_closed(self):
        p,raw=fixture();p['native_evidence']['observation']['specification']['stimulus_profile']['generator_class']='unknown';self.reject(p,raw)
        p,raw=fixture();p['schema_version']=99;self.reject(p,raw)

    def test_complete_graph_detects_shared_maximum(self):
        p,raw=fixture()
        for d in p['domain_spec']['domains'][:2]:d.update(begin=.1,end=.9)
        for index,a in enumerate(p['analysis']['associations'][:2]):
            a.update(status='ambiguous',reason='maximum_shared_by_competing_domains',candidate_maxima=[0,1],
                     largest_measured_maximum=1,selected_maximum=None,maximum_offset_low=.7-(.1 if index==0 else .5),
                     maximum_offset_high=.7-(.1 if index==0 else .5),competing_stimulus_ids=['p1' if index==0 else 'p0'])
        audit_response_domain_evidence(p,raw)
        p['analysis']['associations'][0].update(status='hypothesis',competing_stimulus_ids=[],selected_maximum=1)
        self.reject(p,raw)

    def test_file_entrypoint_binds_safe_relative_primary(self):
        p,raw=fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'trace.csv').write_bytes(raw);target=root/'packet.json'
            target.write_text(json.dumps(p,allow_nan=False),encoding='utf-8')
            self.assertTrue(audit_response_domain_file(target)['primary_trace_checked'])
            p['trace']['path']='../trace.csv';target.write_text(json.dumps(p),encoding='utf-8')
            with self.assertRaises(EvidenceError):audit_response_domain_file(target)
