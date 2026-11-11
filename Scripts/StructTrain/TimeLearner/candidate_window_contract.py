"""Archive2 candidate-window DATA contracts, never native/live authority.

The arithmetic proposes a declared interval. Only separately replayed primary
can supply a measured maximum; no predictor value becomes an observation.
"""
from copy import deepcopy
import re

from .composite_configuration import (METHOD, COMPOSITE_FIELDS,
    project_composite_configuration, validate_composite_protocol)
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import count, number, require
from .response_domain_evidence import _same, _text

MAX = 2**53-1
POLICY_ID = 'reference-anchored-candidate-window-v1'
POLICY_FIELDS = set(('schema_version policy_id seed_rule coordinate_mode '
    'proposals_per_logical_request maximum_feature_terms inputs').split())
INPUT_FIELDS = set(('delay_frames_per_segment base_left_guard_frames base_right_guard_frames '
    'length_guard_frames synapse_count_guard_frames resistance_change_guard_frames '
    'capacitance_change_guard_frames hard_first_frame hard_last_frame maximum_window_frames').split())
GRID_TAGS = dict(frame_origin_policy='native-full-before-frame-zero-v1',
    source_phase_policy='same-declared-source-native-events-measured-v1',
    reset_binding='native-neuron-dataset-reset-before-children-v1')
GRID_FIELDS = set(GRID_TAGS) | {'frequency_hz','source_origin','source_pattern_binding','source_profile_binding'}
SEED_FIELDS = {'input_index','first_frame','last_frame','frame_count','grid','initial_parameters','initial_capacitance'}
FACT_FIELDS = {'grid','declared_maximum_samples','parameters','capacitance'}
COMPUTATION_FIELDS = set(('status first_frame last_frame shift_frames uncertainty_frames length_change '
    'synapse_count_change resistance_changes capacitance_changes feature_terms').split())
PROPOSAL_FIELDS = set(('kind schema_version policy_id source_origin owner_family_binding reference_proof_id '
    'protocol_binding policy_binding candidate_binding reference_group_id attempt_id run_id trial_id group_id '
    'input_id input_index channel model_epoch purpose candidate_model_revision window_recipe_id '
    'measurement_instance_id reference candidate computation').split())
SPEC2_FIELDS = set(('schema_version method_id group_id input_id assigned_input channel coordinate_mode '
    'reference_time candidate_frame').split())


def bounded_count(value, *, positive=False):
    value = count(value)
    require(value <= MAX and (not positive or value > 0), 'candidate_window_inexact_or_nonpositive_count')
    return value


def hash_id(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None,
            'candidate_window_hash_id_format')
    return value


def parameters(values, *, inputs=None):
    require(type(values) is list and bool(values) and (inputs is None or len(values)==inputs),
            'candidate_window_parameter_dimensions')
    for item in values:
        keys(item,{'length','synapses','resistance'},'candidate_window_parameter_fields')
        require(0 < bounded_count(item['length']) <= 2**31-1 and
                0 < bounded_count(item['synapses']) <= 2**31-1 and number(item['resistance']) > 0,
                'candidate_window_invalid_parameter_feature')
    return values


def capacitance(value):
    if value is None: return None
    keys(value,{'origin','maximum_relative_change','membrane_scales'},'candidate_window_capacitance_fields')
    hash_id(value['origin']); change=number(value['maximum_relative_change'])
    scales=value['membrane_scales']
    require(change>=0 and type(scales) is dict and bool(scales),'candidate_window_invalid_capacitance_feature')
    for path,scale in scales.items():
        require(type(path) is str and re.fullmatch(r'Dendrite[1-9][0-9]*_[1-9][0-9]*',path) is not None
                and number(scale)>0 and 1-change <= scale <= 1+change,'candidate_window_invalid_capacitance_scale')
    return value


def equivalent_capacitance(a,b):
    capacitance(a);capacitance(b)
    if a is None or b is None:return a is b
    if a['origin']!=b['origin'] or a['maximum_relative_change']!=b['maximum_relative_change']:return False
    return all(a['membrane_scales'].get(path,1.)==b['membrane_scales'].get(path,1.)
               for path in a['membrane_scales'].keys() | b['membrane_scales'].keys())


def grid(value):
    keys(value,GRID_FIELDS,'candidate_window_grid_fields')
    bounded_count(value['frequency_hz'],positive=True)
    for key,tag in GRID_TAGS.items():require(value[key]==tag,'candidate_window_unknown_grid_or_phase_policy')
    for key in ('source_origin','source_pattern_binding','source_profile_binding'):_text(value[key])
    return value


def validate_policy(policy, inputs, maximum_samples):
    keys(policy,POLICY_FIELDS,'candidate_window_policy_fields')
    require(bounded_count(policy['schema_version'])==1 and policy['policy_id']==POLICY_ID
            and policy['seed_rule']=='immutable_reference_full_before'
            and policy['coordinate_mode']=='relative_native_frame_interval'
            and bounded_count(policy['proposals_per_logical_request'])==1,'candidate_window_unknown_policy_or_strategy')
    maximum=bounded_count(maximum_samples); budget=bounded_count(policy['maximum_feature_terms'],positive=True)
    require(type(policy['inputs']) is list and len(policy['inputs'])==inputs and 2<=inputs<=budget//3
            and maximum>=3,'candidate_window_declaration_dimensions_or_feature_budget')
    for item in policy['inputs']:
        keys(item,INPUT_FIELDS,'candidate_window_input_policy_fields')
        for key in INPUT_FIELDS:bounded_count(item[key])
        require(item['hard_first_frame']<item['hard_last_frame']<maximum and item['maximum_window_frames']>=2,
                'candidate_window_invalid_declared_envelope')
    return policy


def configuration_view(configuration):
    """Private common-field view; retain the exact cold7/8 record for execution."""
    require(type(configuration) is dict and bounded_count(configuration.get('schema_version')) in (7,8),
            'candidate_window_requires_cold7_declaration')
    recovery=configuration['schema_version']==8
    if recovery:
        require(configuration.get('invalid_measurement_recovery')=='advance_rejected_candidate_window',
                'unsupported_candidate_window_recovery_envelope')
        require(bounded_count(configuration['search']['maximum_invalid_observations'])>0,
                'candidate_window_recovery_requires_invalid_budget')
    common=configuration.get('composite_measurement')
    keys(common,COMPOSITE_FIELDS|{'candidate_window_policy'},'candidate_window_native_policy2_fields')
    require(bounded_count(common['schema_version'])==2,'candidate_window_native_policy2_required')
    n=len(configuration['model']['inputs'])
    validate_policy(common['candidate_window_policy'],n,common['context_policy']['maximum_samples'])
    view=deepcopy(configuration);view['schema_version']=6
    if recovery:view.pop('invalid_measurement_recovery')
    view['composite_measurement'].pop('candidate_window_policy');view['composite_measurement']['schema_version']=1
    project_composite_configuration(view)
    return view


def validate_protocol(protocol, configuration):
    common=configuration_view(configuration)
    require(type(protocol) is dict and bounded_count(protocol.get('schema_version'))==5,
            'candidate_window_requires_protocol5')
    contract=protocol['composite_measurement']
    keys(contract,{'schema_version','method_id','context_policy','geometry_policy','reference_input_windows',
                   'candidate_window_policy'},'candidate_window_contract2_fields')
    require(bounded_count(contract['schema_version'])==2 and contract['method_id']==METHOD,
            'candidate_window_contract2_required')
    validate_policy(contract['candidate_window_policy'],len(protocol['inputs']),contract['context_policy']['maximum_samples'])
    _same(contract['candidate_window_policy'],configuration['composite_measurement']['candidate_window_policy'])
    # Exactly the same numeric/context declarations; this temporary descriptor
    # is not a schema4 observation, proof, public parser result or certificate.
    view=deepcopy(protocol);view['schema_version']=4
    view['composite_measurement'].pop('candidate_window_policy')
    view['composite_measurement']['input_windows']=view['composite_measurement'].pop('reference_input_windows')
    view['composite_measurement']['schema_version']=1
    validate_composite_protocol(view,common)
    return common


def _add(a,b):
    a=bounded_count(a);b=bounded_count(b)
    require(0<=a<=MAX and 0<=b<=MAX-a,'candidate_window_count_addition_overflow');return a+b


def _multiply(a,b):
    a=bounded_count(a);b=bounded_count(b)
    require(0<=a<=MAX and 0<=b<=MAX and (a==0 or b<=MAX//a),'candidate_window_count_product_overflow');return a*b


def _signed_add(a,b):
    require(number(a).is_integer() and number(b).is_integer(),'candidate_window_inexact_signed_frame')
    a=int(a);b=int(b)
    require(-MAX<=a<=MAX and -MAX<=b<=MAX and -MAX<=a+b<=MAX,'candidate_window_signed_frame_overflow');return a+b


def calculate_window(policy, seed, candidate):
    """Independent bounded integer arithmetic from declared features, DATA only."""
    keys(seed,SEED_FIELDS,'candidate_window_seed_fields');keys(candidate,FACT_FIELDS,'candidate_window_facts_fields')
    before=seed['initial_parameters'];after=candidate['parameters']
    require(type(before) is list and type(after) is list and len(before)==len(after),
            'candidate_window_parameter_dimensions')
    n=len(before)
    maximum=bounded_count(candidate['declared_maximum_samples']);validate_policy(policy,n,maximum)
    terms=_multiply(n,3)
    for value in (seed['initial_capacitance'],candidate['capacitance']):
        if value is not None:
            require(type(value) is dict and type(value.get('membrane_scales')) is dict,
                    'candidate_window_invalid_capacitance_feature')
            terms=_add(terms,len(value['membrane_scales']))
            require(terms<=policy['maximum_feature_terms'],'candidate_window_feature_budget_exhausted')
    parameters(before);parameters(after,inputs=n)
    index=bounded_count(seed['input_index']);require(index<n,'candidate_window_seed_input_index')
    grid(seed['grid']);grid(candidate['grid']);_same(seed['grid'],candidate['grid'])
    first,last,size=(bounded_count(seed[k]) for k in ('first_frame','last_frame','frame_count'))
    require(size>=3 and 0<first<=last<size-1,'candidate_window_invalid_reference_frame_seed')
    a,b=capacitance(seed['initial_capacitance']),capacitance(candidate['capacitance'])
    require((a is None)==(b is None),'candidate_window_capacitance_family_changed')
    if a is not None:require(a['origin']==b['origin'] and a['maximum_relative_change']==b['maximum_relative_change'],
                            'candidate_window_capacitance_family_changed')
    lengths=synapses=resistances=0
    for old,new in zip(before,after):
        lengths=_add(lengths,abs(old['length']-new['length']))
        synapses=_add(synapses,abs(old['synapses']-new['synapses']))
        resistances=_add(resistances,int(old['resistance']!=new['resistance']))
    changed_c=0 if equivalent_capacitance(a,b) else 1;p=policy['inputs'][index]
    shift=_multiply(abs(after[index]['length']-before[index]['length']),p['delay_frames_per_segment'])
    if after[index]['length']<before[index]['length']:shift=-shift
    uncertainty=_add(_add(_multiply(lengths,p['length_guard_frames']),_multiply(synapses,p['synapse_count_guard_frames'])),
        _add(_multiply(resistances,p['resistance_change_guard_frames']),_multiply(changed_c,p['capacitance_change_guard_frames'])))
    low=_signed_add(_signed_add(first,shift),-_add(p['base_left_guard_frames'],uncertainty))
    high=_signed_add(_signed_add(last,shift),_add(p['base_right_guard_frames'],uncertainty))
    require(0<=low<high and low>=p['hard_first_frame'] and high<=p['hard_last_frame'],
            'candidate_window_outside_declared_envelope')
    require(_add(high-low,1)<=p['maximum_window_frames'],'candidate_window_width_exceeds_policy')
    return dict(status='computed',first_frame=low,last_frame=high,shift_frames=shift,uncertainty_frames=uncertainty,
        length_change=lengths,synapse_count_change=synapses,resistance_changes=resistances,
        capacitance_changes=changed_c,feature_terms=terms)


def recipe_content(record):
    names=('policy_binding reference_proof_id source_origin owner_family_binding protocol_binding input_id '
           'input_index channel candidate_model_revision model_epoch candidate_binding reference candidate computation').split()
    return dict(kind='candidate_window_recipe_v1',**{k:record[k] for k in names})


def instance_content(record):
    return dict(kind='candidate_window_instance_v1',**{k:record[k] for k in
        ('window_recipe_id','attempt_id','run_id','trial_id','group_id','purpose')})


def validate_proposal_data(record):
    keys(record,PROPOSAL_FIELDS,'candidate_window_proposal_fields')
    require(record['kind']=='composite_candidate_window_proposal_v1' and bounded_count(record['schema_version'])==1
            and record['policy_id']==POLICY_ID and record['purpose'] in ('search','final'),'candidate_window_proposal_schema_or_purpose')
    for key in ('source_origin','owner_family_binding','reference_proof_id','protocol_binding','policy_binding',
                'candidate_binding','candidate_model_revision','window_recipe_id','measurement_instance_id'):hash_id(record[key])
    for key in ('reference_group_id','attempt_id','run_id','trial_id','group_id','input_id'):_text(record[key])
    for key in ('input_index','channel','model_epoch'):bounded_count(record[key])
    seed,current=record['reference'],record['candidate'];keys(seed,SEED_FIELDS,'candidate_window_seed_fields');keys(current,FACT_FIELDS,'candidate_window_facts_fields')
    n=len(parameters(seed['initial_parameters']));parameters(current['parameters'],inputs=n)
    grid(seed['grid']);grid(current['grid']);_same(seed['grid'],current['grid'])
    require(seed['grid']['source_origin']==record['source_origin'] and n>=2 and
            bounded_count(seed['input_index'])==bounded_count(record['input_index'])<n,'candidate_window_proposal_dimensions')
    require(3<=bounded_count(seed['frame_count']) and 0<bounded_count(seed['first_frame'])<=bounded_count(seed['last_frame'])<seed['frame_count']-1,
            'candidate_window_invalid_reference_frame_seed')
    capacitance(seed['initial_capacitance']);capacitance(current['capacitance'])
    computation=record['computation'];keys(computation,COMPUTATION_FIELDS,'candidate_window_computation_fields')
    require(computation['status']=='computed','candidate_window_proposal_not_computed')
    for key in COMPUTATION_FIELDS-{'status','shift_frames'}:bounded_count(computation[key])
    shift=number(computation['shift_frames']);require(shift.is_integer() and abs(shift)<=MAX,'candidate_window_inexact_signed_frame')
    require(computation['first_frame']<computation['last_frame']<bounded_count(current['declared_maximum_samples']),
            'candidate_window_proposal_dimensions')
    require(record['window_recipe_id']==digest(recipe_content(record)) and record['measurement_instance_id']==digest(instance_content(record)),
            'candidate_window_proposal_self_binding')
    return record


def validate_specification(spec, protocol, logical, group_id, purpose):
    keys(spec,SPEC2_FIELDS,'candidate_window_specification_fields')
    i=bounded_count(logical['input_index'])
    require(bounded_count(spec['schema_version'])==2 and spec['method_id']==METHOD and spec['group_id']==group_id
            and spec['input_id']==logical['input_id'] and bounded_count(spec['assigned_input'])==i
            and bounded_count(spec['channel'])==(i if protocol['routing']=='classic_burst' else 0),
            'candidate_window_specification_binding')
    if purpose=='reference':
        require(spec['coordinate_mode']=='reference_time' and spec['candidate_frame'] is None,'candidate_window_reference_specification')
        _same(spec['reference_time'],protocol['composite_measurement']['reference_input_windows'][i])
    else:
        require(spec['coordinate_mode']=='candidate_frame' and spec['reference_time'] is None,'candidate_window_candidate_specification')
        frame=spec['candidate_frame'];keys(frame,{'first_frame','last_frame'},'candidate_window_frame_fields')
        require(bounded_count(frame['first_frame'])<bounded_count(frame['last_frame']),'candidate_window_invalid_frame_window')
    return spec


def expected_measurement_id(record,protocol):
    """Proof2 CONTENT hash, after independent replay; no restored live lease."""
    budget=record['budgets'];limits=budget['attempt_limits']
    return digest(dict(kind='live-composite-training-measurement-v2',method_binding=protocol,
        source_origin=record['source_origin'],owner_family_binding=record['owner_family_binding'],
        candidate_witness=digest(record['candidate_binding']),attempt_id=record['attempt_id'],
        logical_request=record['logical_request'],group_id=record['group_id'],purpose=record['purpose'],
        method_specification=record['method_specification'],window_proposal=record['window_proposal'],
        native_specification=record['native_group']['specification'],
        attempt_limits=[limits[k] for k in ('maximum_groups','maximum_native_probes','maximum_total_samples','maximum_model_seconds','maximum_wall_seconds')],
        group_limits=[budget['maximum_group_model_seconds'],budget['maximum_group_wall_seconds']],
        maximum_total_primary_bytes=budget['maximum_total_primary_bytes'],
        primary=[dict(native=t['native_evidence'],csv_sha256=t['sha256']) for t in record['native_group']['traces']],
        maximum=record['measurement']['actual_peak']))
