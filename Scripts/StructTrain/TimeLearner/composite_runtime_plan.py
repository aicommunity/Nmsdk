"""Closed current-runtime search declaration, separate from initial cold state."""
from .capacitance_policy import audit_capacitance_search_policy
from .composite_configuration import validate_composite_measurement
from .composite_source_evidence import keys
from .native_evidence import count, number, require
from .response_domain_evidence import _same, _text

PLAN_FIELDS = set(('schema_version run_id initial_model_revision initial_model_epoch search '
    'maximum_reference_probes maximum_invalid_reference_probes maximum_model_seconds maximum_wall_seconds '
    'record_capacitance_history composite_measurement').split())
SEARCH_FIELDS = set(('normalization maximum_probes maximum_edits maximum_candidates_per_input maximum_sweeps '
    'maximum_invalid_observations resistance_subdivision_depth n0_candidate_repeats bounds tolerances '
    'capacitance_search invalid_measurement_recovery').split())
BOUND_FIELDS = {'minimum_length','maximum_length','minimum_synapses','maximum_synapses','minimum_resistance','maximum_resistance'}
TOLERANCE_FIELDS = {'amplitude_absolute','amplitude_relative','sync'}


def audit_runtime_plan(plan, configuration, protocol, *, capacitance_state=None):
    keys(plan,PLAN_FIELDS,'unknown_composite_runtime_plan_fields')
    require(count(plan['schema_version'])==1,'unknown_composite_runtime_plan_schema')
    _text(plan['run_id']);_text(plan['initial_model_revision']);count(plan['initial_model_epoch'])
    count(plan['maximum_reference_probes']);count(plan['maximum_invalid_reference_probes'])
    require(number(plan['maximum_model_seconds'])>0 and number(plan['maximum_wall_seconds'])>0
            and type(plan['record_capacitance_history']) is bool,'composite_runtime_clock_or_history_policy')
    n=len(protocol['inputs']);search=plan['search'];keys(search,SEARCH_FIELDS,'unknown_composite_runtime_search_fields')
    require(search['normalization'] in ('N0','N1') and search['normalization']==configuration['model']['normalization']
            and search['invalid_measurement_recovery']=='retry_same_candidate',
            'composite_runtime_normalization_or_recovery')
    for key in ('maximum_probes','maximum_edits','maximum_candidates_per_input','maximum_sweeps'):
        require(count(search[key])>0,'composite_runtime_positive_search_budget')
    count(search['maximum_invalid_observations']);require(count(search['resistance_subdivision_depth'])<=20,'composite_runtime_subdivision_depth')
    repeats=count(search['n0_candidate_repeats'])
    require(1<=repeats<=128 and (search['normalization']=='N0' or repeats==1),'composite_runtime_candidate_repeats')
    tolerances=search['tolerances'];keys(tolerances,TOLERANCE_FIELDS,'composite_runtime_tolerance_fields')
    require(all(number(value)>=0 for value in tolerances.values()),'composite_runtime_negative_tolerance')
    bounds=search['bounds'];require(type(bounds) is list and len(bounds)==n,'composite_runtime_bound_dimension')
    for bound in bounds:
        keys(bound,BOUND_FIELDS,'composite_runtime_bound_fields')
        require(1<=count(bound['minimum_length'])<=count(bound['maximum_length'])
                <=count(configuration['model']['maximum_cable_length'])
                and 1<=count(bound['minimum_synapses'])<=count(bound['maximum_synapses'])<=128
                and 0<number(bound['minimum_resistance'])<=number(bound['maximum_resistance']),
                'composite_runtime_invalid_bound')
    declaration=plan['composite_measurement']
    validate_composite_measurement(declaration,inputs=n,frequency=configuration['model']['frequency_hz'],
                                   maximum_samples=count(configuration['maximum_samples']))
    for field in ('schema_version','method_id','context_policy','geometry_policy'):
        _same(declaration[field],protocol['composite_measurement'][field])
    policy=search['capacitance_search']
    if policy is not None:
        require(plan['record_capacitance_history'] is True and capacitance_state is not None,
                'composite_runtime_C_search_without_actual_C0')
        audit_capacitance_search_policy(policy,maximum_relative_change=capacitance_state['maximum_relative_change'],configuration=search)
    return {'run_id':plan['run_id'],'normalization':search['normalization'],'n0_candidate_repeats':repeats,
            'runtime_plan_validated':True,'native_execution_verified':False,'scientific_verdict':None}


def validate_completed_parameters(parameters, plan):
    bounds=plan['search']['bounds']
    require(type(parameters) is list and len(parameters)==len(bounds),'composite_trained_parameter_dimension')
    for value,bound in zip(parameters,bounds):
        keys(value,{'length','synapses','resistance'},'composite_trained_parameter_fields')
        length,synapses,resistance=count(value['length']),count(value['synapses']),number(value['resistance'])
        require(count(bound['minimum_length'])<=length<=count(bound['maximum_length'])
                and count(bound['minimum_synapses'])<=synapses<=count(bound['maximum_synapses'])
                and number(bound['minimum_resistance'])<=resistance<=number(bound['maximum_resistance']),
                'composite_trained_parameter_outside_runtime_bounds')
        require(plan['search']['normalization']!='N1' or synapses==1,'composite_N1_has_multiple_synapses')
