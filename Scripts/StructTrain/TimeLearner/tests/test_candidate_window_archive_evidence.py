"""Controlled DATA-only fixtures. No native execution or Train PASS is asserted.

Worker execution only. The complete-primary controls reuse retained artificial
waveforms from the established portable fixture, never C++ asserted verdicts.
"""
from copy import deepcopy
import csv
import io
import struct
import unittest

from ..candidate_window_contract import (GRID_TAGS, MAX, POLICY_ID, calculate_window,
    configuration_view, validate_protocol, validate_proposal_data, recipe_content,
    instance_content, expected_measurement_id, validate_specification)
from ..candidate_window_binding_evidence import audit_candidate_binding2, reference_seed, replay_proposal
from ..candidate_window_archive_evidence import _geometry, _complete, _ledger, _accepted, audit_candidate_window_archive
from ..composite_measurement_evidence import audit_composite_measurement_archive
from ..composite_raw_evidence import audit_native_packets, audit_raw_trials
from ..model_identity import canonical_model_sha256 as digest
from ..native_evidence import EvidenceError
from .test_composite_configuration import configuration, protocol
from .test_matched_omission_portable import fixture as portable_fixture
from .test_declared_window_basin_evidence import fixture as basin_fixture, geometry_fixture


def policy(n=2):
    row=dict(delay_frames_per_segment=3,base_left_guard_frames=1,base_right_guard_frames=2,
        length_guard_frames=1,synapse_count_guard_frames=2,resistance_change_guard_frames=3,
        capacitance_change_guard_frames=4,hard_first_frame=0,hard_last_frame=200,maximum_window_frames=100)
    return dict(schema_version=1,policy_id=POLICY_ID,seed_rule='immutable_reference_full_before',
        coordinate_mode='relative_native_frame_interval',proposals_per_logical_request=1,
        maximum_feature_terms=128,inputs=[deepcopy(row) for _ in range(n)])


def declarations(n=2,branch=False):
    config=configuration(n=n,branch=branch);p=protocol(config)
    config['schema_version']=7;config['composite_measurement']['schema_version']=2
    config['composite_measurement']['candidate_window_policy']=policy(n)
    p['schema_version']=5;p['composite_measurement']['schema_version']=2
    p['composite_measurement']['reference_input_windows']=p['composite_measurement'].pop('input_windows')
    p['composite_measurement']['candidate_window_policy']=policy(n)
    return config,p


def arithmetic():
    grid=dict(frequency_hz=2000,source_origin='1'*64,source_pattern_binding='2'*64,
              source_profile_binding='3'*64,**GRID_TAGS)
    values=[dict(length=2,synapses=2,resistance=3.),dict(length=3,synapses=1,resistance=5.)]
    seed=dict(input_index=0,first_frame=20,last_frame=21,frame_count=201,grid=grid,
              initial_parameters=values,initial_capacitance=None)
    facts=dict(grid=deepcopy(grid),declared_maximum_samples=201,parameters=deepcopy(values),capacitance=None)
    return policy(),seed,facts


def graph_binding(*,n=2,branch=False,shared=False):
    """Minimal semantic graph DATA, not an XML/native import attestation."""
    _,p=declarations(n,branch);nodes=[dict(path='$',**{'class':'DeclaredNeuronProfile'},frequency_hz='2000',parameters={})]
    links=[];values=[];banks=[];created=set()
    for i in range(n):
        length=(1 if shared else n-i) if branch else i+1
        value=dict(length=length,synapses=2,resistance=2. if shared else 2.+i);values.append(value)
        path='$.Dendrite'+str(1 if branch else i+1)+'_'+str(length);receiver=path+'.ExcChannel'
        members=[path+'.ExcSynapse'+str(k) for k in (1,2)]
        banks.append(dict(input_ordinal=i,input_id=p['inputs'][i]['id'],stimulus_id=p['inputs'][i]['stimulus_id'],
            receiver_path=receiver,bank_path=path,attachment_segment=length,excitation_synapse_paths=members))
        if path in created:continue
        created.add(path)
        nodes.extend([dict(path=path,**{'class':'Membrane'},frequency_hz='2000',parameters=dict(
            NumExcitatorySynapses=dict(binding=False,data=dict(type='signed_integer',value='2')))),
            dict(path=receiver,**{'class':'Receiver'},frequency_hz='2000',parameters={})])
        for k,member in enumerate(members):
            nodes.append(dict(path=member,**{'class':'Synapse'},frequency_hz='2000',parameters=dict(
                Resistance=dict(binding=False,data=dict(type='binary64',value=struct.pack('>d',value['resistance']).hex())))))
            links.extend([dict(target=member+':Input',source='burst',slot='0',kind='stimulus_port'),
                dict(target=receiver+':SynapticInputs',source=member+':Output',slot=str(k),kind='property_pointer')])
    model=dict(schema_version=2,nodes=nodes,bindings=links,stimulus_ports=[dict(id='burst',type='matrix_binary64')])
    identity=dict(kind='semantic_model_identity',schema_version=2,valid=True,diagnostics=[],
        canonical_encoding='length-framed-utf8-binary64-v1',model=model,sha256=digest(model))
    source=dict(storage_images_sha256='4'*64,optional_C0_witness=None,optional_C0_origin='',
        model_spec=dict(branch=branch,allow_muted_input_baseline=False,neuron_class='DeclaredNeuronProfile',
                        maximum_cable_length=8))
    binding=dict(kind='composite_train_candidate_binding_v2',schema_version=2,source_origin='1'*64,
        model_identity=identity,storage_images_sha256='4'*64,optional_C0_witness=None,
        physical_readback=dict(parameters=values,input_banks=banks,capacitance=None))
    logical=dict(base_model_revision=identity['sha256'])
    return binding,logical,source,p


def rebind_graph(binding,logical):
    binding['model_identity']['sha256']=digest(binding['model_identity']['model'])
    logical['base_model_revision']=binding['model_identity']['sha256']


def reference_records():
    _,p=declarations();binding,_,source,_=graph_binding();identity=binding['model_identity']
    source.update(initial_model=identity,initial_epoch=0,actual_source_profile=[p['stimulus_profile'][k] for k in
        ('generator_class','amplitude','pulse_length','frequency_hz','frequency_deviation','use_transit_signal','use_pattern_output')])
    records=[]
    for i in range(2):
        records.append(dict(purpose='reference',consumed=True,training_requested_at_consume=True,window_proposal=None,
            group_id='a/capture/0/'+str(i)+'/composite/'+str(i+1),attempt_id='a',source_origin='1'*64,owner_family_binding='5'*64,
            logical_request=dict(input_index=i,input_id=p['inputs'][i]['id'],base_model_revision=identity['sha256'],model_epoch=0),
            candidate_binding=deepcopy(binding),measurement=dict(semantic_proof_id=str(i+6)*64,
                actual_peak=dict(first_sample=20+i*40,last_sample=20+i*40)),
            method_specification=dict(channel=i),native_group=dict(traces=[dict(native_evidence=dict(observation=dict(sample_count=201)))])))
    return records,source,p


def proposal_fixture():
    refs,source,p=reference_records();r=deepcopy(refs[0]);r.update(purpose='search',consumed=False,group_id='a/search/0/composite/3',window_proposal=None)
    r['logical_request'].update(run_id='a',trial_id='a/search/0',sample_id='target',pattern_hash=p['pattern_hash'],protocol_revision=p['revision'],routing=p['routing'])
    seed=reference_seed(refs[0],source,p)
    facts=dict(grid=seed['grid'],declared_maximum_samples=201,parameters=r['candidate_binding']['physical_readback']['parameters'],capacitance=None)
    computation=calculate_window(p['composite_measurement']['candidate_window_policy'],seed,facts)
    claim=dict(kind='composite_candidate_window_proposal_v1',schema_version=1,policy_id=POLICY_ID,
        source_origin='1'*64,owner_family_binding='5'*64,reference_proof_id=refs[0]['measurement']['semantic_proof_id'],
        protocol_binding=digest(p),policy_binding=digest(p['composite_measurement']['candidate_window_policy']),
        candidate_binding=digest(r['candidate_binding']),reference_group_id=refs[0]['group_id'],attempt_id='a',run_id='a',
        trial_id='a/search/0',group_id=r['group_id'],input_id=p['inputs'][0]['id'],input_index=0,channel=0,model_epoch=0,purpose='search',
        candidate_model_revision=r['logical_request']['base_model_revision'],reference=seed,candidate=facts,computation=computation)
    claim['window_recipe_id']=digest(recipe_content(claim));claim['measurement_instance_id']=digest(instance_content(claim))
    r['window_proposal']=claim;r['method_specification']=dict(candidate_frame={k:computation[k] for k in ('first_frame','last_frame')})
    return r,refs,source,p


def accounting(attempts=('a','a'),bytes_=(60,60),caps=(200,200),current='b',cap=300):
    records=[];rows=[]
    for i,(attempt,size,limit) in enumerate(zip(attempts,bytes_,caps),1):
        records.append(dict(attempt_id=attempt,purpose='reference',group_id=attempt+'/capture/0/0/composite/'+str(i),
            budgets=dict(maximum_total_primary_bytes=limit,attempt_limits=dict(maximum_groups=10,maximum_native_probes=40,maximum_total_samples=1000))))
        rows.append(dict(native_probes=4,sampled_frames=20,primary_bytes=size))
    return dict(records=records,current_attempt_id=current,maximum_total_primary_bytes=cap,reference_group_ids=[]),rows


def geometry_data(*,offset=0.):
    spec,policy,times,full,repeat,controls=geometry_fixture()
    actual=[offset+t+.001*t*t for t in times]
    def trace(shape):
        return dict(times=actual,raws=[shape['raw']],baseline=[shape['baseline']],spec=dict(begin=offset),event_frames=[1,6],
            packet=dict(observation=dict(stimuli=[dict(time=actual[1]),dict(time=actual[6])])) )
    decoded=[trace(full),*[trace(shape) for _,shape in controls],trace(repeat)]
    record=dict(method_specification=dict(channel=0,assigned_input=0,coordinate_mode='candidate_frame',
        candidate_frame=dict(first_frame=0,last_frame=5)),geometry_policy=policy)
    p=dict(inputs=[{},{}],minimum_amplitude=.5)
    return record,p,decoded


def complete_primary_data():
    portable,primary=portable_fixture();basin,_=basin_fixture();s=portable['specification'];group=s['group_id']
    s['reset_binding']='native-neuron-dataset-reset-before-children-v1';raw={};packets={}
    for i,trace in enumerate(portable['traces']):
        packet=trace['native_evidence'];identity=group+'/native/'+str(i)
        packet['requested_specification']['trial_id']=identity;packet['observation']['specification']['trial_id']=identity
        trace['binding']['reset_binding']=s['reset_binding'];packets[identity]=packet
        raw[identity]=dict(trial=dict(primary_ref={k:trace[k] for k in ('relative_path','bytes','sha256')}))
    p=dict(inputs=[dict(id='input0'),dict(id='input1')],routing=s['routing'],revision=s['protocol_revision'],sample_id=s['sample_id'],
        pattern_hash=s['pattern_hash'],stimulus_ids=s['stimulus_ids'],origin_stimulus_id='pulse0',stimulus_profile=s['stimulus_profile'],
        minimum_amplitude=s['minimum_amplitude'],composite_measurement=dict(context_policy=portable['policy']))
    logical={k:s[k] for k in ('run_id','sample_id','input_id','base_model_revision','model_epoch')};logical['input_index']=s['assigned_input']
    r=dict(native_group=portable,logical_request=logical,group_id=group,group_state='completed',measurement=None,
        budgets=dict(maximum_group_model_seconds=10.,maximum_group_wall_seconds=60.),geometry_policy=basin['geometry_policy'],
        method_specification=dict(channel=0,assigned_input=0,coordinate_mode='reference_time',
            reference_time=dict(begin_offset=0.,end_offset=.5)),
        selection={k:basin[k] for k in ('status','status_enum','reasons','actual_assigned_onset','geometry')})
    return r,p,dict(applied_source_isi=[.1,.5]),raw,packets,primary


def raw_primary_data():
    r,p,source,_,packets,primary=complete_primary_data();raw=[]
    p['maximum_sample_gap']=next(iter(packets.values()))['observation']['specification']['maximum_sample_gap']
    r['logical_request'].update(routing=p['routing'],pattern_hash=p['pattern_hash'],protocol_revision=p['revision'])
    for trace in r['native_group']['traces']:
        packet=trace['native_evidence'];spec=packet['observation']['specification'];path=trace['relative_path']
        times=[float(row[0]) for row in list(csv.reader(io.StringIO(primary[path].decode())))[1:]]
        raw.append(dict(native_trial_id=spec['trial_id'],prepared_context=packet['prepared'],actual_specification=spec,
            primary_ref={k:trace[k] for k in ('relative_path','bytes','sha256')},
            actual_stimuli=[dict(id=e['id'],time=e['time'],frame_index=times.index(e['time'])) for e in packet['observation']['stimuli']]))
    r['raw_trials']=raw
    return r,p,dict(duration=1.2,maximum_samples=13),primary,audit_native_packets(list(packets.values()))


class CandidateWindowDataTest(unittest.TestCase):
    def test_cold7_common_view_preserves_original_and_does_not_enable_legacy_parser(self):
        for base in range(1,5):
            config,p=declarations();config['base_schema_version']=base
            # Base-specific fields come from the real declaration helper.
            old=configuration(base);config.update({k:v for k,v in old.items() if k not in ('schema_version','composite_measurement')})
            original=deepcopy(config);self.assertEqual(configuration_view(config)['schema_version'],6)
            validate_protocol(p,config);self.assertEqual(config,original)

    def test_changed_protocol_mapping_origin_windows_and_policy_are_not_normalized_away(self):
        config,p=declarations()
        for change in ('mapping','pattern','origin','window','policy','unknown'):
            bad=deepcopy(p)
            if change=='mapping':bad['inputs'][0]['stimulus_id']='pulse1'
            elif change=='pattern':bad['pattern_hash']='f'*64
            elif change=='origin':bad['origin_stimulus_id']='pulse99'
            elif change=='window':bad['composite_measurement']['reference_input_windows'][0]['end_offset']=.09
            elif change=='policy':bad['composite_measurement']['candidate_window_policy']['inputs'][0]['base_left_guard_frames']=2
            else:bad['composite_measurement']['future']=True
            with self.subTest(change=change),self.assertRaises(EvidenceError):validate_protocol(bad,config)
        p['origin_stimulus_id']='pulse1';validate_protocol(p,config)

    def test_unchanged_candidate_window_uses_reference_plateau_not_any_waveform(self):
        p,seed,facts=arithmetic();actual=calculate_window(p,seed,facts)
        self.assertEqual((actual['first_frame'],actual['last_frame'],actual['shift_frames'],actual['uncertainty_frames']),(19,23,0,0))

    def test_structural_growth_shifts_window_and_counts_all_input_feature_changes(self):
        p,seed,facts=arithmetic();facts['parameters'][0]['length']=4;facts['parameters'][1]['synapses']=3;facts['parameters'][1]['resistance']=7.
        actual=calculate_window(p,seed,facts)
        self.assertEqual((actual['shift_frames'],actual['uncertainty_frames'],actual['first_frame'],actual['last_frame']),(6,9,16,38))
        self.assertEqual((actual['length_change'],actual['synapse_count_change'],actual['resistance_changes']),(2,2,1))

    def test_contraction_has_signed_shift_and_never_wraps_unsigned_frames(self):
        p,seed,facts=arithmetic();facts['parameters'][0]['length']=1
        actual=calculate_window(p,seed,facts);self.assertEqual((actual['shift_frames'],actual['first_frame'],actual['last_frame']),(-3,15,21))

    def test_unknown_grid_phase_reset_and_policy_are_rejected(self):
        p,seed,facts=arithmetic()
        for key in GRID_TAGS:
            bad=deepcopy(facts);bad['grid'][key]='both-sides-same-unsupported'
            other=deepcopy(seed);other['grid'][key]=bad['grid'][key]
            with self.subTest(key=key),self.assertRaises(EvidenceError):calculate_window(p,other,bad)
        p['policy_id']='other'
        with self.assertRaises(EvidenceError):calculate_window(p,seed,facts)

    def test_boolean_fraction_nonfinite_overflow_and_hard_envelope_fail_closed(self):
        for value in (True,.5,'1',float('nan'),float('inf'),MAX+1):
            p,seed,facts=arithmetic();p['inputs'][0]['base_left_guard_frames']=value
            with self.subTest(value=value),self.assertRaises(EvidenceError):calculate_window(p,seed,facts)
        p,seed,facts=arithmetic();p['inputs'][0]['delay_frames_per_segment']=MAX;facts['parameters'][0]['length']=4
        with self.assertRaises(EvidenceError):calculate_window(p,seed,facts)
        p,seed,facts=arithmetic();p['inputs'][0]['hard_first_frame']=20
        with self.assertRaises(EvidenceError):calculate_window(p,seed,facts)

    def test_unit_C0_extension_does_not_manufacture_capacitance_change(self):
        p,seed,facts=arithmetic();seed['initial_capacitance']=dict(origin='7'*64,maximum_relative_change=.1,membrane_scales={'Dendrite1_1':1.})
        facts['capacitance']=deepcopy(seed['initial_capacitance']);facts['capacitance']['membrane_scales']['Dendrite1_2']=1.
        actual=calculate_window(p,seed,facts);self.assertEqual(actual['capacitance_changes'],0);self.assertEqual(actual['feature_terms'],9)
        facts['capacitance']['membrane_scales']['Dendrite1_2']=1.05
        self.assertEqual(calculate_window(p,seed,facts)['capacitance_changes'],1)

    def test_C0_off_requires_no_C_property_but_invented_changed_family_is_rejected(self):
        p,seed,facts=arithmetic();self.assertEqual(calculate_window(p,seed,facts)['capacitance_changes'],0)
        facts['capacitance']=dict(origin='7'*64,maximum_relative_change=.1,membrane_scales={'Dendrite1_1':1.})
        with self.assertRaises(EvidenceError):calculate_window(p,seed,facts)

    def test_real_content_graph_checks_different_Rs_across_inputs(self):
        b,l,s,p=graph_binding();actual=audit_candidate_binding2(b,digest(b),l,s,'1'*64,p)
        self.assertEqual([v['resistance'] for v in actual['parameters']],[2.,3.]);self.assertIsNone(actual['capacitance'])

    def test_N4_N6_distinct_Branch_attachment_and_ordinal_graph_data(self):
        for n in (4,6):
            b,l,s,p=graph_binding(n=n,branch=True)
            self.assertEqual([v['length'] for v in audit_candidate_binding2(b,digest(b),l,s,'1'*64,p)['parameters']],list(range(n,0,-1)))
            bad=deepcopy(b);bad['physical_readback']['input_banks'][0]['input_ordinal']=1
            with self.assertRaises(EvidenceError):audit_candidate_binding2(bad,digest(bad),l,s,'1'*64,p)

    def test_shared_Branch_bank_is_legal_DATA_without_claiming_distinct_routing(self):
        b,l,s,p=graph_binding(n=4,branch=True,shared=True)
        audit_candidate_binding2(b,digest(b),l,s,'1'*64,p)
        self.assertEqual(len({v['bank_path'] for v in b['physical_readback']['input_banks']}),1)

    def test_heterogeneous_within_bank_Rs_is_unsupported_not_flattened(self):
        b,l,s,p=graph_binding();original=deepcopy(b);path=b['physical_readback']['input_banks'][0]['excitation_synapse_paths'][1]
        next(v for v in b['model_identity']['model']['nodes'] if v['path']==path)['parameters']['Resistance']['data']['value']=struct.pack('>d',9.).hex()
        rebind_graph(b,l)
        with self.assertRaises(EvidenceError):audit_candidate_binding2(b,digest(b),l,s,'1'*64,p)
        self.assertEqual(b['physical_readback'],original['physical_readback'])

    def test_rehashed_missing_receiver_link_wrong_source_or_bound_Rs_rejects(self):
        for change in ('receiver','source','bound','frequency','attachment'):
            b,l,s,p=graph_binding()
            if change=='receiver':b['model_identity']['model']['bindings'].pop(1)
            elif change=='source':b['model_identity']['model']['bindings'][0]['source']='foreign'
            elif change=='bound':b['model_identity']['model']['nodes'][3]['parameters']['Resistance']['binding']=True
            elif change=='frequency':b['model_identity']['model']['nodes'][1]['frequency_hz']='20000'
            else:b['physical_readback']['input_banks'][0]['attachment_segment']=2
            rebind_graph(b,l)
            with self.subTest(change=change),self.assertRaises(EvidenceError):audit_candidate_binding2(b,digest(b),l,s,'1'*64,p)

    def test_proposal_is_recomputed_from_original_references_and_current_graph_facts(self):
        r,refs,s,p=proposal_fixture();facts=r['candidate_binding']['physical_readback']
        actual=replay_proposal(r,p,s,refs,{k:facts[k] for k in ('parameters','capacitance')},201)
        self.assertEqual(actual,r['window_proposal'])

    def test_self_consistent_rehashed_wrong_seed_is_not_reference_authority(self):
        r,refs,s,p=proposal_fixture();claim=r['window_proposal']
        claim['reference']['first_frame']+=1;claim['reference']['last_frame']+=1
        claim['computation']=calculate_window(p['composite_measurement']['candidate_window_policy'],claim['reference'],claim['candidate'])
        claim['window_recipe_id']=digest(recipe_content(claim));claim['measurement_instance_id']=digest(instance_content(claim));validate_proposal_data(claim)
        with self.assertRaises(EvidenceError):replay_proposal(r,p,s,refs,{k:r['candidate_binding']['physical_readback'][k] for k in ('parameters','capacitance')},201)

    def test_wrong_live_instance_context_cannot_be_fixed_by_recipe_rehash(self):
        r,refs,s,p=proposal_fixture();r['window_proposal']['attempt_id']='different'
        r['window_proposal']['measurement_instance_id']=digest(instance_content(r['window_proposal']))
        with self.assertRaises(EvidenceError):replay_proposal(r,p,s,refs,{k:r['candidate_binding']['physical_readback'][k] for k in ('parameters','capacitance')},201)

    def test_reference_seed_cannot_be_recaptured_from_trained_graph_or_other_epoch(self):
        refs,s,p=reference_records()
        for field,value in [('base_model_revision','f'*64),('model_epoch',1)]:
            bad=deepcopy(refs[0]);bad['logical_request'][field]=value
            with self.assertRaises(EvidenceError):reference_seed(bad,s,p)

    def test_retained_prefix_cap_is_checked_against_historical_not_only_current_limit(self):
        a,rows=accounting(caps=(100,100))
        with self.assertRaises(EvidenceError):_ledger(a,rows)
        a,rows=accounting();_ledger(a,rows)

    def test_new_attempt_cap_also_covers_retained_prior_history(self):
        a,rows=accounting(attempts=('a','b'),caps=(200,100))
        with self.assertRaises(EvidenceError):_ledger(a,rows)

    def test_reopened_attempt_and_nonincreasing_group_ordinal_reject(self):
        a,rows=accounting(attempts=('a','b','a'),bytes_=(1,1,1),caps=(200,200,200))
        with self.assertRaises(EvidenceError):_ledger(a,rows)
        a,rows=accounting();a['records'][1]['group_id']=a['records'][0]['group_id']
        with self.assertRaises(EvidenceError):_ledger(a,rows)

    def test_cumulative_group_probe_and_sample_caps_are_not_per_record_only(self):
        for field,value in [('maximum_groups',1),('maximum_native_probes',7),('maximum_total_samples',39)]:
            a,rows=accounting()
            for r in a['records']:r['budgets']['attempt_limits'][field]=value
            with self.subTest(field=field),self.assertRaises(EvidenceError):_ledger(a,rows)

    def test_candidate_cannot_precede_complete_retained_references(self):
        a,rows=accounting();a['reference_group_ids']=['missing'];a['records'][0]['purpose']='search'
        with self.assertRaises(EvidenceError):_ledger(a,rows)

    def test_partial_reference_capture_cannot_publish_consumed_prefix(self):
        refs,s,p=reference_records();a=dict(records=refs[:1],source_binding=s,reference_group_ids=[refs[0]['group_id']],final_group_ids=[])
        rows=[dict(group_id=refs[0]['group_id'],purpose='reference',input_index=0,consumed=True,measured=True,native_closure_recomputed=True)]
        with self.assertRaises(EvidenceError):_accepted(a,rows,p)
        a['reference_group_ids']=[];a['records'][0]['consumed']=False
        self.assertEqual(_accepted(a,rows,p),[])

    def test_unknown_archive_schema_boolean_and_extra_fields_fail_closed(self):
        for version in (True,0,3,'2'):
            with self.subTest(version=version),self.assertRaises(EvidenceError):audit_composite_measurement_archive(dict(schema_version=version),{})
        with self.assertRaises(EvidenceError):audit_candidate_window_archive(dict(schema_version=2,unknown=True),{})

    def test_protocol4_and_cold6_are_not_promoted_by_archive2_dispatch(self):
        with self.assertRaises(EvidenceError):validate_protocol(protocol(configuration()),configuration())

    def test_specification2_does_not_accept_ambiguous_coordinate_modes(self):
        _,p=declarations();logical=dict(input_index=0,input_id='input0')
        spec=dict(schema_version=2,method_id=p['composite_measurement']['method_id'],group_id='g',input_id='input0',assigned_input=0,channel=0,
            coordinate_mode='candidate_frame',reference_time=None,candidate_frame=dict(first_frame=10,last_frame=12))
        validate_specification(spec,p,logical,'g','search')
        spec['reference_time']=dict(begin_offset=0.,end_offset=.1)
        with self.assertRaises(EvidenceError):validate_specification(spec,p,logical,'g','search')

    def test_proof2_keeps_caps_actual_primary_and_declared_policy_but_not_live_addresses_or_paths(self):
        r,_,_,p=proposal_fixture();r['budgets']=dict(attempt_limits=dict(maximum_groups=2,maximum_native_probes=8,maximum_total_samples=804,
            maximum_model_seconds=1.,maximum_wall_seconds=20.),maximum_group_model_seconds=.5,maximum_group_wall_seconds=10.,maximum_total_primary_bytes=99999)
        r['native_group']=dict(specification=dict(actual='DATA'),traces=[dict(native_evidence=dict(DATA='packet'),sha256='2'*64,relative_path='old.csv')])
        r['measurement']['actual_peak']=dict(first_sample=20,last_sample=20,amplitude=2.,raw_potential=2.,time=.01,plateau_end=.01)
        original=expected_measurement_id(r,p)
        changed=deepcopy(r);changed['live_attempt_binding']='another-process';changed['native_group']['traces'][0]['relative_path']='renamed.csv'
        self.assertEqual(expected_measurement_id(changed,p),original)
        for change in ('cap','primary','proposal'):
            bad=deepcopy(r)
            if change=='cap':bad['budgets']['maximum_total_primary_bytes']-=1
            elif change=='primary':bad['native_group']['traces'][0]['sha256']='3'*64
            else:bad['window_proposal']['computation']['last_frame']+=1
            self.assertNotEqual(expected_measurement_id(bad,p),original)

    def test_frame_projection_uses_actual_irregular_timestamps(self):
        r,p,decoded=geometry_data(offset=100.)
        result=_geometry(r,p,decoded)
        self.assertEqual(result['status'],'completed');self.assertEqual(result['geometry']['validity'],'valid')
        self.assertEqual(result['geometry']['measured_maximum']['time'],decoded[0]['times'][3])
        self.assertNotEqual(result['geometry']['measured_maximum']['time'],100.+3/2000.)

    def test_missing_declared_frame_rejects_without_interpolation_or_clamping(self):
        r,p,decoded=geometry_data();r['method_specification']['candidate_frame']['last_frame']=11
        self.assertEqual(_geometry(r,p,decoded),dict(status='rejected',status_enum=0,reasons=['window_frames_not_captured'],
            actual_assigned_onset=None,geometry=None))

    def test_reference_window_must_fit_actual_group_duration_without_timestep_tolerance(self):
        for end in (5.,5.+1e-12):
            r,p,decoded=geometry_data();r['native_group']=dict(specification=dict(duration=5.))
            r['method_specification'].update(coordinate_mode='reference_time',reference_time=dict(begin_offset=0.,end_offset=end))
            result=_geometry(r,p,decoded)
            self.assertEqual(result['status'],'completed' if end==5. else 'rejected')
            if end!=5.:self.assertEqual(result['reasons'],['basin_native_method_or_window_binding_changed'])

    def test_local_window_does_not_veto_unrelated_higher_late_vertex(self):
        r,p,decoded=geometry_data();result=_geometry(r,p,decoded)
        self.assertEqual(result['geometry']['measured_maximum']['first_sample'],3)
        self.assertEqual(result['geometry']['measured_maximum']['raw_potential'],5.)

    def test_actual_assigned_event_causality_not_predictor_time_is_enforced(self):
        r,p,decoded=geometry_data();decoded[0]['event_frames'][0]=4
        decoded[0]['packet']['observation']['stimuli'][0]['time']=decoded[0]['times'][4]
        self.assertEqual(_geometry(r,p,decoded)['status'],'causality_rejected')

    def test_full_repeat_topology_change_and_shared_vertex_do_not_mint_valid_peak(self):
        r,p,decoded=geometry_data();decoded[-1]['raws'][0][3]=4.
        self.assertNotEqual(_geometry(r,p,decoded)['geometry']['validity'],'valid')
        r,p,decoded=geometry_data();decoded[2]['raws'][0]=[2.]*11
        self.assertNotEqual(_geometry(r,p,decoded)['geometry']['validity'],'valid')

    def test_complete_portable_context_and_new_geometry_replay_from_actual_primary(self):
        result=_complete(*complete_primary_data())
        self.assertTrue(result['native_closure_recomputed']);self.assertTrue(result['geometry_recomputed'])
        self.assertEqual(result['geometry_validity'],'valid');self.assertFalse(result['measured'])

    def test_changed_primary_cannot_be_hidden_by_cpp_selection_metadata(self):
        r,p,s,raw,packets,primary=complete_primary_data()
        name=next(iter(primary));primary[name]=primary[name].replace(b'5',b'4',1)
        with self.assertRaises(EvidenceError):_complete(r,p,s,raw,packets,primary)

    def test_changed_complete_source_reset_policy_and_selection_fail_closed(self):
        for change in ('source','reset','budget','selection'):
            r,p,s,raw,packets,primary=complete_primary_data()
            if change=='source':s['applied_source_isi'][0]=.2
            elif change=='reset':r['native_group']['specification']['reset_binding']='another-reset'
            elif change=='budget':r['budgets']['maximum_group_model_seconds']=20.
            else:r['selection']['geometry']['measured_maximum']['raw_potential']=9.
            with self.subTest(change=change),self.assertRaises(EvidenceError):_complete(r,p,s,raw,packets,primary)

    def test_schema1_raw_default_keeps_exact_sample_declaration(self):
        r,p,c,primary,packets=raw_primary_data();audit_raw_trials(r,p,c,primary,packets)
        c['maximum_samples']=14
        with self.assertRaises(EvidenceError):audit_raw_trials(r,p,c,primary,packets)
        audit_raw_trials(r,p,c,primary,packets,maximum_samples_limit=14)
        with self.assertRaises(EvidenceError):audit_raw_trials(r,p,c,primary,packets,maximum_samples_limit=12)

    def test_partial_actual_event_interval_is_explicit_not_a_legacy_tolerance_change(self):
        r,p,c,primary,_=raw_primary_data();r['raw_trials']=r['raw_trials'][:1]
        event=r['raw_trials'][0]['actual_stimuli'][0];event['time']-=.01
        with self.assertRaises(EvidenceError):audit_raw_trials(r,p,c,primary,{})
        audit_raw_trials(r,p,c,primary,{},actual_event_frame_interval=True)
        event['time']-=.2
        with self.assertRaises(EvidenceError):audit_raw_trials(r,p,c,primary,{},actual_event_frame_interval=True)


if __name__=='__main__':unittest.main()
