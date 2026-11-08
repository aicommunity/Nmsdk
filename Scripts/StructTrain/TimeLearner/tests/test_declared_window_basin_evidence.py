"""Controlled independent-replay fixtures. Execute numerical tests on workers."""
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
import unittest

from ..declared_window_basin_evidence import (KIND,METHOD,audit_declared_window_basin_evidence,
    audit_declared_window_basin_file,recompute_declared_basin_geometry)
from ..matched_omission_evidence import POLICY_FIELDS
from ..model_identity import canonical_model_sha256
from ..native_evidence import EvidenceError
from .test_matched_omission_portable import fixture as portable_fixture


def encoded(value): return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def reference(name,raw): return dict(relative_path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def fixture(*,branch=False,shared=False,partial=False,input_id=None):
    portable,primary=portable_fixture(branch=branch,shared=shared,input_id=input_id)
    source=portable['specification'];assigned=source['assigned_input'];channel=source['channel']
    assignment=portable['assignment']
    group=dict(schema_version=1,kind='native_matched_omission_fixture',method=portable['method'],group_id=source['group_id'],native_probes=4,
        packets=[v['native_evidence'] for v in portable['traces']],
        traces=[dict(path=v['relative_path'],presented_ordinals=v['presented_ordinals'],sha256=v['sha256']) for v in portable['traces']],
        source_pattern_sha256=source['pattern_hash'],reset_binding=source['reset_binding'],model_instance_binding=source['model_instance_binding'],
        physical_channel_paths=source['physical_channel_paths'],assigned_input=assigned,assigned_channel=channel,
        policy={k:portable['policy'][k] for k in POLICY_FIELDS.split()},assignment_reasons=assignment['reasons'],
        maxima=[{k:v for k,v in p.items() if not k.startswith('comparison_')} for p in assignment['maxima']],
        selected_full_maximum=assignment['selected_full_maximum'],assignment_validity=assignment['validity'],
        reason='omission_group_closed',training_certificate_eligible=False,scientific_verdict=None)
    peak=dict(first_sample=8 if branch else 3,last_sample=8 if branch else 3,amplitude=2. if branch else 3.,
              raw_potential=4. if branch else 5.,time=.8 if branch else .3,plateau_end=.8 if branch else .3)
    left=dict(first_sample=5 if branch else 0,last_sample=7 if branch else 1,record_edge=not branch)
    right=dict(first_sample=9 if branch else 5,last_sample=12 if branch else 7,record_edge=branch)
    geometry=dict(validity='valid',reasons=[],selected_candidate=0,measured_maximum=deepcopy(peak),
        candidates=[dict(maximum=deepcopy(peak),left=left,right=right,status='unique_necessary',
            controls=['preserved','absent_within_fixed_basin'] if branch else ['absent_within_fixed_basin','preserved'],
            necessary_inputs=[assigned],reasons=[])])
    spec=dict(schema_version=1,method_id=METHOD,group_id=source['group_id'],input_id=source['input_id'],assigned_input=assigned,channel=channel,
              window_begin_offset=.6 if branch else 0.,window_end_offset=1. if branch else .5)
    record=dict(kind=KIND,schema_version=1,method=METHOD,group_id=source['group_id'],assigned_input=assigned,channel=channel,
        window_begin_offset=spec['window_begin_offset'],window_end_offset=spec['window_end_offset'],specification=spec,
        geometry_policy=dict(schema_version=1,maximum_inputs=2,maximum_samples=13,maximum_total_samples=52,repeatability_absolute=0.),
        minimum_amplitude=.5,status='completed',status_enum=1,reasons=[],rejected_tampering=13,
        actual_assigned_onset=.6 if branch else .1,geometry_validity='valid',geometry=geometry,measured_maximum=peak,
        diagnostic_only=True,training_certificate_eligible=False,scientific_verdict=None,
        witness_binding=dict(complete_group=True,group_id=source['group_id'],source_pattern_sha256=source['pattern_hash'],
            source_specification_sha256=canonical_model_sha256(source),base_model_revision=source['base_model_revision'],
            effective_model_revision=source['effective_model_revision'],protocol_revision=source['protocol_revision']))
    artifacts=dict(primary)
    if partial:
        group.update(native_probes=1,packets=group['packets'][:1],traces=group['traces'][:1],reason='omission_group_external_stop',
                     assignment_validity='not_available',assignment_reasons=[],maxima=[],selected_full_maximum=None)
        artifacts={group['traces'][0]['path']:primary[group['traces'][0]['path']]}
        record.update(status='rejected',status_enum=0,reasons=['missing_omission_controls'],geometry=None,
                      geometry_validity=None,measured_maximum=None,actual_assigned_onset=None,rejected_tampering=0)
        record['witness_binding'].update(complete_group=False,portable=None,source_specification_sha256=None)
    else:
        raw=encoded(portable);artifacts['matched-witness.json']=raw;record['witness_binding']['portable']=reference('matched-witness.json',raw)
    raw=encoded(group);artifacts['group.json']=raw;record['witness_binding']['group']=reference('group.json',raw)
    return record,artifacts


def geometry_fixture():
    spec=dict(schema_version=1,input_count=2,assigned_input=0,window_begin=0.,window_end=10.,minimum_amplitude=.5)
    policy=dict(schema_version=1,maximum_inputs=2,maximum_samples=11,maximum_total_samples=44,repeatability_absolute=0.)
    full=[2.,2.,3.,5.,3.,2.,3.,6.,3.,2.,2.]
    omitted0=[2.,2.,2.,2.,2.,2.,3.,6.,3.,2.,2.];omitted1=[2.,2.,3.,5.,3.,2.,2.,2.,2.,2.,2.]
    shape=lambda raw:dict(baseline=2.,raw=raw)
    return spec,policy,list(map(float,range(11))),shape(full),shape(list(full)),[(0,shape(omitted0)),(1,shape(omitted1))]


class DeclaredWindowBasinEvidenceTest(unittest.TestCase):
    def rejected(self,record,artifacts):
        with self.assertRaises(EvidenceError):audit_declared_window_basin_evidence(record,artifacts)

    def test_complete_actual_parameters_and_primary_are_recomputed(self):
        record,artifacts=fixture();result=audit_declared_window_basin_evidence(record,artifacts)
        self.assertTrue(result['geometry_recomputed']);self.assertEqual(result['primary_traces_checked'],4)
        self.assertEqual(result['measured_maximum']['raw_potential'],5.);self.assertFalse(result['training_certificate_eligible'])
        self.assertFalse(result['native_execution_verified']);self.assertFalse(result['causal_lineage_verified'])

    def test_branch_assigned_one_uses_actual_source_onset_and_channel_zero(self):
        record,artifacts=fixture(branch=True);result=audit_declared_window_basin_evidence(record,artifacts)
        self.assertEqual(result['measured_maximum']['first_sample'],8);self.assertEqual(result['geometry_validity'],'valid')

    def test_historical_v1_shared_outcome_does_not_veto_new_local_criterion(self):
        record,artifacts=fixture(shared=True);result=audit_declared_window_basin_evidence(record,artifacts)
        self.assertEqual(result['geometry_validity'],'valid');self.assertEqual(result['measured_maximum']['first_sample'],3)

    def test_partial_rejection_is_checked_without_claiming_full_replay(self):
        record,artifacts=fixture(partial=True);result=audit_declared_window_basin_evidence(record,artifacts)
        self.assertFalse(result['complete_group']);self.assertFalse(result['geometry_recomputed'])
        self.assertTrue(result['partial_rejection_checked']);self.assertEqual(result['primary_traces_checked'],1)

    def test_qt_json_spelling_is_not_used_as_the_semantic_source_hash(self):
        record,artifacts=fixture(input_id='путь-правый')
        for name,key in [('group.json','group'),('matched-witness.json','portable')]:
            value=json.loads(artifacts[name]);text=json.dumps(value,ensure_ascii=True,separators=(',',':'))
            text=re.sub(r'(?<![\w.])0\.1(?=[,}\]])','1e-1',text)
            raw=text.replace('"frequency_hz":10.0','"frequency_hz":10').encode()
            artifacts[name]=raw;record['witness_binding'][key]=reference(name,raw)
        self.assertEqual(audit_declared_window_basin_evidence(record,artifacts)['geometry_validity'],'valid')

    def test_policy_is_recorded_and_cannot_be_inferred_or_tampered(self):
        for key,value in [('maximum_inputs',1),('maximum_samples',12),('maximum_total_samples',51),('repeatability_absolute',-1.)]:
            record,artifacts=fixture();record['geometry_policy'][key]=value;self.rejected(record,artifacts)
        record,artifacts=fixture();del record['geometry_policy'];self.rejected(record,artifacts)

    def test_schema_and_dimension_bool_or_integral_float_are_rejected(self):
        paths=[('schema_version',),('status_enum',),('assigned_input',),('channel',),('specification','schema_version'),
               ('specification','assigned_input'),('geometry_policy','maximum_samples'),
               ('geometry','selected_candidate'),('geometry','candidates',0,'maximum','first_sample')]
        for path in paths:
            for boolean in (True,False):
                record,artifacts=fixture();node=record
                for key in path[:-1]:node=node[key]
                node[path[-1]]=True if boolean else float(node[path[-1]])
                self.rejected(record,artifacts)

    def test_unknown_fields_method_status_or_claims_fail_closed(self):
        for key,value in [('schema_version',2),('method','matched-omission-assigned-maximum-v1'),('status','success'),
                          ('status_enum',0),('training_certificate_eligible',True),('scientific_verdict','PASS'),('unknown',0)]:
            record,artifacts=fixture();record[key]=value;self.rejected(record,artifacts)

    def test_nested_specification_must_match_flat_fields_and_source(self):
        for key,value in [('input_id','other'),('assigned_input',1),('channel',1),('group_id','other'),('window_end_offset',.6)]:
            record,artifacts=fixture();record['specification'][key]=value;self.rejected(record,artifacts)
        record,artifacts=fixture();record['minimum_amplitude']=.6;self.rejected(record,artifacts)

    def test_selected_sample_raw_time_amplitude_and_causality_are_checked(self):
        for key,value in [('first_sample',4),('raw_potential',6.),('amplitude',4.),('time',.4),('plateau_end',.4)]:
            record,artifacts=fixture();record['geometry']['measured_maximum'][key]=value;record['measured_maximum'][key]=value
            self.rejected(record,artifacts)
        record,artifacts=fixture();record['actual_assigned_onset']=.4;self.rejected(record,artifacts)

    def test_candidate_presence_valleys_and_indices_are_replayed(self):
        for action in ('controls','necessary','anchor','record_edge','selected','reasons'):
            record,artifacts=fixture();candidate=record['geometry']['candidates'][0]
            if action=='controls':candidate['controls']=['preserved','preserved']
            elif action=='necessary':candidate['necessary_inputs']=[1]
            elif action=='anchor':candidate['right']['first_sample']=6
            elif action=='record_edge':candidate['left']['record_edge']=False
            elif action=='selected':record['geometry']['selected_candidate']=1
            else:candidate['reasons']=['forged']
            self.rejected(record,artifacts)

    def test_bound_group_portable_and_primary_bytes_are_required(self):
        for name in ('group.json','matched-witness.json','native-0.csv'):
            record,artifacts=fixture();artifacts[name]+=b' ';self.rejected(record,artifacts)
            record,artifacts=fixture();del artifacts[name];self.rejected(record,artifacts)
        record,artifacts=fixture();artifacts['extra.csv']=b'';self.rejected(record,artifacts)

    def test_source_spec_digest_and_model_bindings_cannot_be_substituted(self):
        for key in ('source_specification_sha256','source_pattern_sha256','base_model_revision','effective_model_revision','protocol_revision'):
            record,artifacts=fixture();record['witness_binding'][key]='tampered';self.rejected(record,artifacts)

    def test_rehashed_portable_source_readback_change_is_still_rejected(self):
        record,artifacts=fixture();portable=json.loads(artifacts['matched-witness.json']);portable['source']['applied_isi'][0]+=.01
        raw=encoded(portable);artifacts['matched-witness.json']=raw;record['witness_binding']['portable']=reference('matched-witness.json',raw)
        self.rejected(record,artifacts)

    def test_partial_cannot_claim_complete_geometry_or_a_portable_proof(self):
        for field,value in [('complete_group',True),('source_specification_sha256','forged')]:
            record,artifacts=fixture(partial=True);record['witness_binding'][field]=value;self.rejected(record,artifacts)
        record,artifacts=fixture(partial=True);record['geometry']={'validity':'valid'};self.rejected(record,artifacts)

    def test_unsafe_references_and_duplicate_raw_json_are_rejected(self):
        record,artifacts=fixture();record['witness_binding']['group']['relative_path']='../group.json';self.rejected(record,artifacts)
        record,artifacts=fixture();raw=b'{"schema_version":1,"schema_version":1}'
        artifacts['group.json']=raw;record['witness_binding']['group']=reference('group.json',raw);self.rejected(record,artifacts)

    def test_file_api_snapshots_exact_referenced_primary(self):
        record,artifacts=fixture()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name,raw in artifacts.items():(root/name).write_bytes(raw)
            target=root/'declared-window-basin-diagnostic.json';target.write_bytes(encoded(record))
            self.assertTrue(audit_declared_window_basin_file(target)['geometry_recomputed'])

    def test_pre_event_geometry_is_replayed_but_never_promoted(self):
        # Deliberately synthetic packet/CSV evidence, not a physical native run:
        # source1 is made necessary for a vertex before its actual event.
        record,artifacts=fixture(branch=True);portable=json.loads(artifacts['matched-witness.json'])
        signals=([2.,2.,3.,5.,3.,2.,2.,2.,2.,2.,2.,2.,2.],
                 [2.,2.,2.,2.,2.,2.,2.,2.,4.,2.,2.,2.,2.])
        for index,signal in zip((1,2),signals):
            item=portable['traces'][index];name=item['relative_path'];rows=list(csv.reader(io.StringIO(artifacts[name].decode())))
            values=[[float(v) for v in row] for row in rows[1:]]
            for row,value in zip(values,signal):row[2]=value
            raw=(','.join(rows[0])+'\n'+''.join(','.join(format(v,'.17g') for v in row)+'\n' for row in values)).encode()
            artifacts[name]=raw;item.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        assignment=portable['assignment'];assignment.update(validity='ambiguous',
            reasons=['assigned_omission_changes_pre_stimulus_maximum'],selected_full_maximum=None,measured_maximum=None)
        assignment['maxima'][0].update(supported_inputs=[1],influence_by_input=['not_supported','supported'])
        assignment['maxima'][1].update(supported_inputs=[0],influence_by_input=['supported','not_supported'])
        group=json.loads(artifacts['group.json']);group.update(packets=[v['native_evidence'] for v in portable['traces']],
            traces=[dict(path=v['relative_path'],presented_ordinals=v['presented_ordinals'],sha256=v['sha256']) for v in portable['traces']],
            assignment_validity=assignment['validity'],assignment_reasons=assignment['reasons'],selected_full_maximum=None,
            maxima=[{k:v for k,v in peak.items() if not k.startswith('comparison_')} for peak in assignment['maxima']])
        for name,value,key in [('group.json',group,'group'),('matched-witness.json',portable,'portable')]:
            raw=encoded(value);artifacts[name]=raw;record['witness_binding'][key]=reference(name,raw)
        record['specification'].update(window_begin_offset=0.,window_end_offset=.5)
        record.update(window_begin_offset=0.,window_end_offset=.5,status='causality_rejected',status_enum=2,
            reasons=['basin_native_selected_peak_precedes_actual_assigned_event'],geometry=None,geometry_validity=None,
            measured_maximum=None,actual_assigned_onset=None)
        result=audit_declared_window_basin_evidence(record,artifacts)
        self.assertEqual(result['status'],'causality_rejected');self.assertTrue(result['geometry_recomputed']);self.assertIsNone(result['measured_maximum'])

    def test_independent_geometry_separated_tail_and_actual_potential(self):
        args=list(geometry_fixture());args[3]['raw'][7]=6.3;args[4]['raw'][7]=6.3
        args[5][1][1]['raw'][5:10]=[2.5,2.4,2.3,2.2,2.1]
        first=recompute_declared_basin_geometry(*args);self.assertEqual(first['validity'],'valid');self.assertEqual(first['measured_maximum']['first_sample'],3)
        args[0]['assigned_input']=1;late=recompute_declared_basin_geometry(*args)
        self.assertEqual(late['validity'],'valid');self.assertEqual(late['measured_maximum']['raw_potential'],6.3)

    def test_independent_geometry_true_merged_and_cooperative_peaks_are_ambiguous(self):
        for cooperative in (False,True):
            args=list(geometry_fixture());signal=args[5][1][1]['raw']
            args[3]['raw']=list(signal);args[4]['raw']=list(signal)
            args[5]=[(0,dict(baseline=2.,raw=[2.]*11 if cooperative else list(signal))),
                     (1,dict(baseline=2.,raw=[2.]*11 if cooperative else list(signal)))]
            self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'ambiguous')

    def test_independent_geometry_plateau_and_original_shoulder_are_distinguished(self):
        args=list(geometry_fixture());args[0]['window_end']=5.;args[5][0][1]['raw'][4:7]=[4.,4.,4.]
        self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'valid')
        args[5][0][1]['raw'][7]=3.
        self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'ambiguous')

    def test_independent_geometry_unknown_floor_and_repeat_topology(self):
        args=list(geometry_fixture());args[0]['window_end']=5.;args[5][0][1]['raw'][3]=2.25
        self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'ambiguous')
        args=list(geometry_fixture());args[1]['repeatability_absolute']=.2
        args[3]['raw'][5:7]=[3.,3.1];args[4]['raw'][5:7]=[3.1,3.]
        self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'nonrepeatable')

    def test_independent_geometry_ties_clipping_and_budget_fail_honestly(self):
        args=list(geometry_fixture());args[0]['window_begin']=3.;self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'clipped')
        args=list(geometry_fixture());args[1]['maximum_total_samples']=43
        self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'budget_exhausted')
        args=list(geometry_fixture());args[0]['window_end']=5.
        for shape in (args[3],args[4],args[5][1][1]):shape['raw'][2:5]=[5.,2.,5.]
        self.assertEqual(recompute_declared_basin_geometry(*args)['validity'],'ambiguous')


if __name__=='__main__':unittest.main()
