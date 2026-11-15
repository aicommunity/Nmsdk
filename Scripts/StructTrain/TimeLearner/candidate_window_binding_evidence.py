"""Re-derive archive2 feature/bank DATA from complete semantic graph content.

No native import, scheduler execution or live lease is inferred from hashes.
Within-bank heterogeneous Rs is unsupported by the published C++ input model;
different homogeneous-bank Rs between logical inputs remains supported.
"""
import re
import struct

from .candidate_window_contract import (GRID_TAGS, bounded_count, capacitance,
    calculate_window, hash_id, parameters, validate_proposal_data, recipe_content, instance_content)
from .composite_source_evidence import keys, audit_identity
from .capacitance_evidence import _images
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import number, require
from .response_domain_evidence import _same, _text
from .training_capacitance_witness import audit_training_capacitance_witness

BINDING_FIELDS = {'kind','schema_version','source_origin','model_identity','storage_images_sha256',
                  'optional_C0_witness','physical_readback'}
BANK_FIELDS = {'input_ordinal','input_id','stimulus_id','receiver_path','bank_path',
               'attachment_segment','excitation_synapse_paths'}


def audit_candidate_binding2(candidate, witness_id, logical, source, origin, protocol):
    keys(candidate,BINDING_FIELDS,'candidate_window_binding2_fields')
    require(candidate['kind']=='composite_train_candidate_binding_v2' and bounded_count(candidate['schema_version'])==2
            and candidate['source_origin']==origin and witness_id==digest(candidate)
            and candidate['storage_images_sha256']==source['storage_images_sha256'],'candidate_window_candidate_source_or_digest')
    identity=candidate['model_identity'];nodes=audit_identity(identity)
    require(bounded_count(identity['schema_version'])==2 and identity['sha256']==logical['base_model_revision'],
            'candidate_window_candidate_identity_or_revision')
    model=identity['model'];_same(model['stimulus_ports'],[dict(id='burst',type='matrix_binary64')])
    n=len(protocol['inputs']);physical=candidate['physical_readback']
    keys(physical,{'parameters','input_banks','capacitance'},'candidate_window_physical_fields')
    values=parameters(physical['parameters'],inputs=n);banks=physical['input_banks']
    require(type(banks) is list and len(banks)==n,'candidate_window_actual_input_dimensions')
    declaration=source['model_spec'];branch=protocol['routing']=='branch_solo_burst'
    require(declaration['branch'] is branch and type(declaration['allow_muted_input_baseline']) is bool,
            'candidate_window_actual_routing_declaration')
    frequency=str(bounded_count(protocol['stimulus_profile']['frequency_hz'],positive=True))
    require(nodes['$']['class']==declaration['neuron_class'] and
            all(node['frequency_hz']==frequency for node in nodes.values()),'candidate_window_graph_node_or_frequency')
    links={}
    require(type(model['bindings']) is list,'candidate_window_graph_binding_inventory')
    for link in model['bindings']:
        keys(link,{'target','source','slot','kind'},'candidate_window_graph_link_fields')
        _text(link['target']);_text(link['source'])
        require(type(link['slot']) is str and re.fullmatch(r'0|[1-9][0-9]*',link['slot']) is not None,
                'candidate_window_graph_link_slot')
        links.setdefault(link['target'],[]).append(link)

    def parameter(path,name,kind):
        require(path in nodes,'candidate_window_missing_bank_member')
        item=nodes[path]['parameters'][name]
        require(item['binding'] is False and item['data']['type']==kind,'candidate_window_bound_control_knob_or_type')
        return item['data']

    def resistance(path):
        raw=parameter(path,'Resistance','binary64')['value']
        require(type(raw) is str and re.fullmatch('[0-9a-f]{16}',raw) is not None,
                'candidate_window_noncanonical_control_resistance')
        value=number(struct.unpack('>d',bytes.fromhex(raw))[0])
        require(value>0,'candidate_window_invalid_control_resistance');return value

    maximum=bounded_count(declaration['maximum_cable_length'],positive=True)
    for i,(value,bank) in enumerate(zip(values,banks)):
        keys(bank,BANK_FIELDS,'candidate_window_bank_fields')
        length=bounded_count(value['length']);synapses=bounded_count(value['synapses'])
        require(length<=maximum and synapses<=128 and (not branch or i==0 or values[i-1]['length']>=length),
                'candidate_window_actual_native_parameter_scope')
        path='$.Dendrite'+str(1 if branch else i+1)+'_'+str(length);receiver=path+'.ExcChannel'
        require(bounded_count(bank['input_ordinal'])==i and bank['input_id']==protocol['inputs'][i]['id']
                and bank['stimulus_id']==protocol['inputs'][i]['stimulus_id'] and bank['bank_path']==path
                and bank['receiver_path']==receiver and bounded_count(bank['attachment_segment'])==length
                and receiver in nodes,'candidate_window_actual_bank_membership')
        require(parameter(path,'NumExcitatorySynapses','signed_integer')['value']==str(synapses),
                'candidate_window_actual_synapse_count')
        members=bank['excitation_synapse_paths']
        require(type(members) is list and len(members)==synapses,'candidate_window_actual_bank_membership')
        connected=None;receivers=links.get(receiver+':SynapticInputs',[])
        for k,member in enumerate(members,1):
            expected=path+'.ExcSynapse'+str(k)
            require(member==expected and resistance(member)==value['resistance'],
                    'candidate_window_actual_bank_control_knob')
            incoming=links.get(member+':Input',[])
            require(len(incoming)<=1,'candidate_window_actual_stimulus_binding')
            active=bool(incoming)
            if active:_same(incoming[0],dict(target=member+':Input',source='burst',slot='0',kind='stimulus_port'))
            require((active or declaration['allow_muted_input_baseline']) and (connected is None or connected==active),
                    'candidate_window_actual_partial_or_unowned_bank')
            connected=active
            require(any(link['source']==member+':Output' and link['kind']=='property_pointer' for link in receivers),
                    'candidate_window_actual_receiver_membership')
    initial=source['optional_C0_witness'];witness=candidate['optional_C0_witness']
    budget=bounded_count(protocol['composite_measurement']['candidate_window_policy']['maximum_feature_terms'])
    initial_terms=0 if initial is None else len(initial['controller_parameters']['membrane_scales'])
    require(3*n+initial_terms<=budget,'candidate_window_feature_budget_exhausted')
    if physical['capacitance'] is not None:
        require(type(physical['capacitance']) is dict and type(physical['capacitance'].get('membrane_scales')) is dict
                and len(physical['capacitance']['membrane_scales'])<=budget-3*n-initial_terms,
                'candidate_window_feature_budget_exhausted')
    current=capacitance(physical['capacitance'])
    if initial is None:
        require(current is None and witness is None,'candidate_window_unbound_C0_witness')
    else:
        require(current is not None and witness is not None,'candidate_window_capacitance_family_changed')
        audit_training_capacitance_witness(witness)
        require(digest(_images(witness['storage_images']))==source['storage_images_sha256'],
                'candidate_window_C0_storage_changed')
        require(witness['model_revision']==identity['sha256'],'candidate_window_actual_C0_revision')
        _same(witness['model'],identity);_same(witness['controller_parameters'],current)
        require(current['origin']==source['optional_C0_origin'] and
                current['maximum_relative_change']==initial['controller_parameters']['maximum_relative_change'],
                'candidate_window_capacitance_family_changed')
    return dict(parameters=values,capacitance=current)


def reference_seed(record, source, protocol):
    """Called only after independent closure/geometry/proof replay of this row."""
    identity=source['initial_model'];logical=record['logical_request'];measurement=record['measurement']
    require(record['purpose']=='reference' and record['consumed'] is True and record['training_requested_at_consume'] is True
            and logical['base_model_revision']==identity['sha256'] and logical['model_epoch']==source['initial_epoch']
            and record['candidate_binding']['model_identity']==identity and measurement is not None,
            'candidate_window_reference_not_original_family')
    initial_c0=None if source['optional_C0_witness'] is None else source['optional_C0_witness']['controller_parameters']
    _same(record['candidate_binding']['physical_readback']['capacitance'],initial_c0)
    peak=measurement['actual_peak']
    full=record['native_group']['traces'][0]['native_evidence']['observation']
    return dict(input_index=logical['input_index'],first_frame=peak['first_sample'],last_frame=peak['last_sample'],
        frame_count=full['sample_count'],
        grid=dict(frequency_hz=protocol['stimulus_profile']['frequency_hz'],source_origin=record['source_origin'],
            source_pattern_binding=protocol['pattern_hash'],source_profile_binding=digest(source['actual_source_profile']),
            **GRID_TAGS),
        initial_parameters=record['candidate_binding']['physical_readback']['parameters'],
        initial_capacitance=initial_c0)


def replay_proposal(record, protocol, source, references, candidate_facts, declared_maximum_samples):
    claim=record['window_proposal'];validate_proposal_data(claim)
    i=record['logical_request']['input_index'];ref=references[i];seed=reference_seed(ref,source,protocol)
    facts=dict(grid=seed['grid'],declared_maximum_samples=declared_maximum_samples,**candidate_facts)
    policy=protocol['composite_measurement']['candidate_window_policy']
    actual=dict(kind='composite_candidate_window_proposal_v1',schema_version=1,policy_id=policy['policy_id'],
        source_origin=record['source_origin'],owner_family_binding=record['owner_family_binding'],
        reference_proof_id=ref['measurement']['semantic_proof_id'],protocol_binding=digest(protocol),policy_binding=digest(policy),
        candidate_binding=digest(record['candidate_binding']),reference_group_id=ref['group_id'],attempt_id=record['attempt_id'],
        run_id=record['logical_request']['run_id'],trial_id=record['logical_request']['trial_id'],group_id=record['group_id'],
        input_id=record['logical_request']['input_id'],input_index=i,
        channel=i if protocol['routing']=='classic_burst' else 0,model_epoch=record['logical_request']['model_epoch'],
        purpose=record['purpose'],candidate_model_revision=record['logical_request']['base_model_revision'],
        reference=seed,candidate=facts,computation=calculate_window(policy,seed,facts))
    actual['window_recipe_id']=digest(recipe_content(actual));actual['measurement_instance_id']=digest(instance_content(actual))
    _same(claim,actual)
    _same(record['method_specification']['candidate_frame'],
          {key:actual['computation'][key] for key in ('first_frame','last_frame')})
    return actual
