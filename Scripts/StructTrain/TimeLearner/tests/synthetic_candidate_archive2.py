"""Controlled whole-archive2 DATA fixture, deliberately NOT native execution.

Artificial semantic graphs/XML/clock declarations and retained artificial
waveforms exercise portable joins. No archive1 native export is upgraded,
no physical execution/lease/certificate is manufactured or claimed.
"""
import base64
from copy import deepcopy
import csv
import hashlib
import io
import struct

from ..capacitance_evidence import _images
from ..candidate_window_contract import (calculate_window, recipe_content, instance_content, expected_measurement_id)
from ..candidate_window_binding_evidence import reference_seed
from ..composite_measurement_contract import expected_artifact_document_id
from ..model_identity import canonical_model_sha256 as digest
from .test_candidate_window_archive_evidence import declarations, graph_binding
from .test_matched_omission_portable import fixture as portable_fixture


def identity(model):
    return dict(kind='semantic_model_identity',schema_version=2,valid=True,diagnostics=[],
        canonical_encoding='length-framed-utf8-binary64-v1',model=model,sha256=digest(model))


def snapshot(name,model):
    text='<synthetic-DATA-only class="'+name+'"/>'
    return dict(component_name=name,component_class=name,native_xml=text,
        native_xml_sha256=hashlib.sha256(text.encode()).hexdigest(),identity=identity(model))


def runtime2(configuration,protocol,revision):
    common=deepcopy(configuration['composite_measurement']);search=deepcopy(configuration['search'])
    search.update(normalization='N0',n0_candidate_repeats=1,capacitance_search=None,invalid_measurement_recovery='retry_same_candidate')
    return dict(schema_version=2,protocol_binding=digest(protocol),run_id='synthetic/session/1',initial_model_revision=revision,
        initial_model_epoch=0,search=search,maximum_reference_probes=configuration['maximum_reference_probes'],
        maximum_invalid_reference_probes=configuration['maximum_invalid_reference_probes'],
        maximum_model_seconds=configuration['maximum_model_seconds'],maximum_wall_seconds=configuration['maximum_wall_seconds'],
        record_capacitance_history=False,composite_measurement=common)


def source_data():
    config,p=declarations(branch=True);binding,_,_,_=graph_binding(branch=True)
    config['model'].update(frequency_hz=10,inputs=[dict(attachment=v['length'],synapses=v['synapses'],resistance=v['resistance'])
        for v in binding['physical_readback']['parameters']],allocated_cable_lengths=[2],initial_isi=[.1,.5])
    config.update(duration=1.2,maximum_sample_gap=.1,minimum_amplitude=.5,maximum_samples=13,
        maximum_model_seconds=100.,maximum_wall_seconds=1000.,windows=[dict(begin=0.,end=.5),dict(begin=.6,end=1.)])
    portable,_=portable_fixture(branch=True);config['stimulus_profile']=deepcopy(portable['specification']['stimulus_profile'])
    common=config['composite_measurement'];common.update(context_policy=deepcopy(portable['policy']),
        geometry_policy=dict(schema_version=1,maximum_inputs=2,maximum_samples=13,maximum_total_samples=52,repeatability_absolute=0.),
        maximum_group_model_seconds=10.,maximum_group_wall_seconds=60.,maximum_total_primary_bytes=10000000,
        attempt_limits=dict(maximum_groups=16,maximum_native_probes=64,maximum_total_samples=1000))
    for row in common['candidate_window_policy']['inputs']:
        row.update(delay_frames_per_segment=1,base_left_guard_frames=1,base_right_guard_frames=1,
            length_guard_frames=0,synapse_count_guard_frames=0,resistance_change_guard_frames=0,capacitance_change_guard_frames=0,
            hard_first_frame=0,hard_last_frame=12,maximum_window_frames=13)
    p.update(pattern_hash=digest([.1,.5]),maximum_sample_gap=.1,minimum_amplitude=.5,stimulus_profile=deepcopy(config['stimulus_profile']))
    p['composite_measurement']={k:deepcopy(common[k]) for k in ('schema_version','method_id','context_policy','geometry_policy','candidate_window_policy')}
    p['composite_measurement']['reference_input_windows']=[dict(begin_offset=w['begin'],end_offset=w['end']) for w in config['windows']]
    model=binding['model_identity']['model']
    for node in model['nodes']:node['frequency_hz']='10'
    binding['model_identity']=identity(model)
    def prop(kind,value,**extra):return dict(binding=False,data=dict(type=kind,value=value,**extra))
    binary=lambda value:struct.pack('>d',value).hex()
    dataset=dict(schema_version=2,nodes=[dict(path='$',**{'class':config['model']['dataset_class']},frequency_hz='10',parameters=dict(
        MatrixData=prop('binary64_matrix',[[binary(v)] for v in [.1,.5]],rows='2',columns='1'),
        NumSamples=prop('signed_integer','1'),NumFeatures=prop('signed_integer','1'),MaxSpikesPerFeature=prop('signed_integer','2'))),
        dict(path='$.Generator1',**{'class':'NPulseGeneratorTransit'},frequency_hz='10',parameters={})],bindings=[],stimulus_ports=[])
    generator=dataset['nodes'][1]['parameters'];profile=config['stimulus_profile']
    for name,key in [('Amplitude','amplitude'),('PulseLength','pulse_length'),('FrequencyDeviation','frequency_deviation')]:generator[name]=prop('binary64',binary(profile[key]))
    for name,key in [('UseTransitSignal','use_transit_signal'),('UsePatternOutput','use_pattern_output')]:generator[name]=prop('boolean',profile[key])
    classes={node['class'] for node in model['nodes']}|{node['class'] for node in dataset['nodes']}
    images=[dict(name=name,kind='native_required',base_class='',dependencies=[],snapshot=snapshot(name,
        dict(schema_version=2,nodes=[dict(path='$',**{'class':name},frequency_hz='10',parameters={})],bindings=[],stimulus_ports=[]))) for name in sorted(classes)]
    dataset_snapshot=snapshot(config['model']['dataset_class'],dataset)
    dataset_snapshot['required_class_names']=sorted({n['class'] for n in dataset['nodes']},key=lambda name:name.encode('utf-16-be'))
    source=dict(kind='composite_train_initial_source_v1',schema_version=2,initial_model=binding['model_identity'],
        initial_native_snapshot=snapshot(config['model']['neuron_class'],model),initial_dataset=dataset_snapshot,initial_epoch=0,
        model_spec=deepcopy(config['model']),storage_images=images,storage_images_sha256=digest(_images(images)),
        applied_source_isi=[.1,.5],pattern_hash=p['pattern_hash'],actual_source_profile=[profile[k] for k in
        ('generator_class','amplitude','pulse_length','frequency_hz','frequency_deviation','use_transit_signal','use_pattern_output')],
        optional_C0_origin='',optional_C0_witness=None)
    binding.update(source_origin=digest(source),storage_images_sha256=source['storage_images_sha256'])
    return config,p,source,binding


def _group(ordinal,input_index,purpose,config,p,source,binding,refs,primary):
    attempt='synthetic/session/1';phase='/capture/0' if purpose=='reference' else '/final/1' if purpose=='final' else ''
    run=attempt+phase;trial=run+('/'+str(input_index) if purpose=='reference' else '/verify/0/'+str(input_index) if purpose=='final' else '/search/0')
    group=trial+'/composite/'+str(ordinal);offset=float((ordinal-1)*8);revision=binding['model_identity']['sha256']
    portable,oldprimary=portable_fixture(branch=True);s=portable['specification']
    s.update(run_id=run,group_id=group,input_id=p['inputs'][input_index]['id'],assigned_input=input_index,
        base_model_revision=revision,effective_model_revision=revision,reset_binding='native-neuron-dataset-reset-before-children-v1',
        model_instance_binding='synthetic-DATA-instance-'+str(ordinal),protocol_revision=p['revision'],sample_id=p['sample_id'])
    raw=[];packets=[];full_times=None
    for i,trace in enumerate(portable['traces']):
        packet=trace['native_evidence'];actual=packet['observation']['specification'];requested=packet['requested_specification'];native_id=group+'/native/'+str(i)
        for spec in (requested,actual):spec.update(run_id=run,trial_id=native_id,sample_id=p['sample_id'])
        actual.update(begin=actual['begin']+offset,end=actual['begin']+offset+1.2,effective_model_revision=revision)
        packet.update(current_base_revision=revision)
        packet['prepared'].update(input_id=s['input_id'],selected_input_index=input_index,protocol_revision=p['revision'],
                                  base_model_revision=revision,effective_model_revision=revision)
        observation=packet['observation']
        for event in observation['stimuli']:
            event['time']+=offset;event['relative_to_trial_start']=event['time']-actual['begin']
        observation['first_stimulus_time']=observation['stimuli'][0]['time']
        rows=list(csv.reader(io.StringIO(oldprimary[trace['relative_path']].decode())))
        values=[[float(v) for v in row] for row in rows[1:]]
        for row in values:row[0]+=offset
        times=[v[0] for v in values]
        if i==0:full_times=times
        content=(','.join(rows[0])+'\n'+''.join(','.join(format(v,'.17g') for v in row)+'\n' for row in values)).encode()
        name='composite-measurements/group-'+format(ordinal,'06d')+'/'+('full-before.csv' if i==0 else 'full-after.csv' if i==3 else 'omit-'+str(i-1)+'.csv')
        primary[name]=content;trace.update(relative_path=name,bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
        trace['binding'].update(group_id=group,reset_binding=s['reset_binding'],model_instance_binding=s['model_instance_binding'],current_base_revision=revision)
        packets.append(packet)
        raw.append(dict(native_trial_id=native_id,prepared_context=packet['prepared'],actual_specification=actual,
            primary_ref={k:trace[k] for k in ('relative_path','bytes','sha256')},
            actual_stimuli=[dict(id=e['id'],time=e['time'],frame_index=times.index(e['time'])) for e in observation['stimuli']]))
    assignment=portable['assignment'];assignment.update(validity='valid',reasons=[],selected_full_maximum=input_index)
    for i,peak in enumerate(assignment['maxima']):
        frame=3 if i==0 else 8;peak.update(time=full_times[frame],plateau_end=full_times[frame],precedes_assigned_stimulus=i<input_index)
    assignment['measured_maximum']={k:assignment['maxima'][input_index][k] for k in ('first_sample','last_sample','amplitude','raw_potential','time','plateau_end')}
    logical=dict(run_id=run,trial_id=trial,input_id=s['input_id'],input_index=input_index,sample_id=p['sample_id'],pattern_hash=p['pattern_hash'],
        protocol_revision=p['revision'],base_model_revision=revision,routing=p['routing'],model_epoch=0)
    spec=dict(schema_version=2,method_id=p['composite_measurement']['method_id'],group_id=group,input_id=s['input_id'],assigned_input=input_index,channel=0,
        coordinate_mode='reference_time' if purpose=='reference' else 'candidate_frame',
        reference_time=deepcopy(p['composite_measurement']['reference_input_windows'][input_index]) if purpose=='reference' else None,candidate_frame=None)
    common=config['composite_measurement']
    r=dict(kind='timelearner_composite_measurement',schema_version=2,logical_request=logical,purpose=purpose,group_id=group,attempt_id=attempt,
        source_origin=digest(source),owner_family_binding='f'*64,live_attempt_binding='synthetic-DATA-not-live',method_specification=spec,
        geometry_policy=deepcopy(common['geometry_policy']),candidate_binding=deepcopy(binding),candidate_witness_id=digest(binding),
        group_state='completed',complete_group=True,native_group=portable,raw_trials=raw,native_packets=packets,selection=None,measurement=None,
        consumed=True,training_requested_at_consume=True,rejection_reason='',window_proposal=None,
        budgets=dict(attempt_limits={**common['attempt_limits'],'maximum_model_seconds':100.,'maximum_wall_seconds':1000.},
            maximum_group_model_seconds=10.,maximum_group_wall_seconds=60.,maximum_total_primary_bytes=common['maximum_total_primary_bytes']),
        counters=dict(native_probes=4,sampled_frames=52,retained_frames=52,primary_bytes=sum(t['primary_ref']['bytes'] for t in raw)),
        clock_observation=dict(start_model_time=offset,end_model_time=offset+7.2,start_wall_time=ordinal*10.,end_wall_time=ordinal*10.+1.,wall_enforcement='live_checked_before_mint'),
        capacitance_witnesses={},native_trial_witness_ids={})
    if purpose!='reference':
        seed=reference_seed(refs[input_index],source,p)
        facts=dict(grid=seed['grid'],declared_maximum_samples=13,parameters=binding['physical_readback']['parameters'],capacitance=None)
        c=calculate_window(common['candidate_window_policy'],seed,facts)
        claim=dict(kind='composite_candidate_window_proposal_v1',schema_version=1,policy_id=common['candidate_window_policy']['policy_id'],
            source_origin=r['source_origin'],owner_family_binding=r['owner_family_binding'],reference_proof_id=refs[input_index]['measurement']['semantic_proof_id'],
            protocol_binding=digest(p),policy_binding=digest(common['candidate_window_policy']),candidate_binding=digest(binding),
            reference_group_id=refs[input_index]['group_id'],attempt_id=attempt,run_id=run,trial_id=trial,group_id=group,input_id=s['input_id'],input_index=input_index,
            channel=0,model_epoch=0,purpose=purpose,candidate_model_revision=revision,reference=seed,candidate=facts,computation=c)
        claim['window_recipe_id']=digest(recipe_content(claim));claim['measurement_instance_id']=digest(instance_content(claim));r['window_proposal']=claim
        spec['candidate_frame']={k:c[k] for k in ('first_frame','last_frame')}
    frame=3 if input_index==0 else 8;peak=deepcopy(assignment['measured_maximum'])
    left=dict(first_sample=0,last_sample=1,record_edge=True) if input_index==0 else dict(first_sample=5,last_sample=7,record_edge=False)
    right=dict(first_sample=5,last_sample=7,record_edge=False) if input_index==0 else dict(first_sample=9,last_sample=12,record_edge=True)
    geometry=dict(validity='valid',reasons=[],selected_candidate=0,measured_maximum=peak,candidates=[dict(maximum=deepcopy(peak),left=left,right=right,
        status='unique_necessary',controls=['absent_within_fixed_basin','preserved'] if input_index==0 else ['preserved','absent_within_fixed_basin'],necessary_inputs=[input_index],reasons=[])])
    onset=raw[0]['actual_stimuli'][input_index]['time'];origin=raw[0]['actual_stimuli'][0]['time']
    r['selection']=dict(status='completed',status_enum=1,reasons=[],actual_assigned_onset=onset,geometry=geometry)
    r['measurement']=dict(actual_peak=peak,raw_potential=peak['raw_potential'],arrival=peak['time']-origin,plateau_end=peak['plateau_end']-origin,
        actual_origin_time=origin,semantic_proof_id='')
    r['measurement']['semantic_proof_id']=expected_measurement_id(r,p)
    return r


def fixture():
    config,p,source,binding=source_data();primary={};refs=[]
    for i in range(2):refs.append(_group(i+1,i,'reference',config,p,source,binding,refs,primary))
    records=[*refs,_group(3,0,'search',config,p,source,binding,refs,primary),
        _group(4,0,'final',config,p,source,binding,refs,primary),_group(5,1,'final',config,p,source,binding,refs,primary)]
    runtime=runtime2(config,p,binding['model_identity']['sha256']);blobs={}
    for raw in primary.values():blobs[hashlib.sha256(raw).hexdigest()]=dict(bytes=len(raw),base64=base64.b64encode(raw).decode())
    archive=dict(kind='timelearner_composite_measurement_archive',schema_version=2,method_id=p['composite_measurement']['method_id'],protocol=p,
        source_origin=digest(source),owner_family_binding='f'*64,source_binding=source,maximum_total_primary_bytes=10000000,current_attempt_id=runtime['run_id'],
        records=records,reference_group_ids=[r['group_id'] for r in refs],final_group_ids=[r['group_id'] for r in records[-2:]],primary_blobs=blobs,
        counters=dict(attempt=dict(logical_groups=5,native_probes=20,sampled_frames=260),
            archive=dict(groups=5,native_probes=20,sampled_frames=260,primary_bytes=sum(len(raw) for raw in primary.values()))))
    archive['artifact_document_sha256']=expected_artifact_document_id(archive)
    return archive,config,runtime,primary
