"""Strict runtime2 declaration DATA, separate from original cold7 configuration.

This does not reconstruct an executor, callbacks, live authority or a model.
Warm search/budgets/tolerances are checked as the active plan, never recaptured
from initial cold configuration or silently replaced with initial settings.
"""
from copy import deepcopy

from .candidate_window_contract import validate_protocol, validate_policy
from .capacitance_policy import audit_capacitance_search_policy
from .composite_configuration import COMPOSITE_FIELDS, validate_composite_measurement
from .composite_runtime_plan import PLAN_FIELDS, SEARCH_FIELDS, BOUND_FIELDS, TOLERANCE_FIELDS
from .composite_source_evidence import keys
from .model_identity import canonical_model_sha256 as digest
from .native_evidence import EvidenceError, count, number, require
from .response_domain_evidence import _same, _text, _finite_json

RUNTIME2_FIELDS=PLAN_FIELDS | {'protocol_binding'}


def _capacitance_contexts(policy):
    """Bounded count of the declared seed inventory, not measured C physics."""
    low,high=(number(policy[k]) for k in ('minimum_scale','maximum_scale'))
    limit=count(policy['maximum_contexts'])-1;values=set()
    def retain(value):
        if len(values)<limit and low<=value<=high:values.add(value)
    for value in (1.,low,high):retain(value)
    if low!=high:
        for level in range(1,count(policy['subdivision_depth'])+1):
            denominator=2**level
            for numerator in range(1,denominator,2):
                if len(values)>=limit:break
                retain(low+(high-low)*(numerator/denominator))
            if len(values)>=limit:break
    return 1+len(values)


def audit_candidate_window_runtime_plan(plan, configuration, protocol):
    """Validate active runtime2 against the immutable protocol, not cold search."""
    return _audit_candidate_window_runtime_plan(plan,configuration,protocol,version=2)


def audit_candidate_window_runtime_recovery_plan(plan, configuration, protocol):
    """Validate explicit runtime3 DATA; never restore a live rejection capability."""
    return _audit_candidate_window_runtime_plan(plan,configuration,protocol,version=3)


def _audit_candidate_window_runtime_plan(plan, configuration, protocol, *, version):
    try:
        # Only ORIGINAL configuration is a cold7 document. This call never
        # feeds runtime2 through configuration_view (the frozen7352 P1).
        validate_protocol(protocol,configuration)
        keys(plan,RUNTIME2_FIELDS,'candidate_window_runtime2_fields');_finite_json(plan)
        require(count(plan['schema_version'])==version and plan['protocol_binding']==digest(protocol),
                'candidate_window_runtime2_schema_or_protocol_binding')
        _text(plan['run_id']);_text(plan['initial_model_revision']);count(plan['initial_model_epoch'])
        n=len(protocol['inputs'])
        require(count(plan['maximum_reference_probes'])>=n,'candidate_window_runtime2_reference_budget')
        count(plan['maximum_invalid_reference_probes'])
        require(number(plan['maximum_model_seconds'])>0 and number(plan['maximum_wall_seconds'])>0
                and type(plan['record_capacitance_history']) is bool,'candidate_window_runtime2_clock_or_history')
        search=plan['search'];keys(search,SEARCH_FIELDS,'candidate_window_runtime2_search_fields')
        recovery='retry_same_candidate' if version==2 else 'advance_rejected_candidate_window'
        require(search['normalization'] in ('N0','N1') and search['invalid_measurement_recovery']==recovery,
                'candidate_window_runtime2_normalization_or_recovery')
        for key in ('maximum_probes','maximum_edits','maximum_candidates_per_input','maximum_sweeps'):
            require(count(search[key])>0,'candidate_window_runtime2_positive_search_budget')
        invalid=count(search['maximum_invalid_observations'])
        require(version==2 or invalid>0,'candidate_window_recovery_requires_invalid_budget')
        require(count(search['resistance_subdivision_depth'])<=20,'candidate_window_runtime2_subdivision_depth')
        repeats=count(search['n0_candidate_repeats'])
        require(1<=repeats<=128 and (search['normalization']=='N0' or repeats==1),'candidate_window_runtime2_candidate_repeats')
        keys(search['tolerances'],TOLERANCE_FIELDS,'candidate_window_runtime2_tolerance_fields')
        require(all(number(value)>=0 for value in search['tolerances'].values()),'candidate_window_runtime2_negative_tolerance')
        bounds=search['bounds'];require(type(bounds) is list and len(bounds)==n,'candidate_window_runtime2_bound_dimension')
        for bound in bounds:
            keys(bound,BOUND_FIELDS,'candidate_window_runtime2_bound_fields')
            require(1<=count(bound['minimum_length'])<=count(bound['maximum_length'])<=2**31-1
                and 1<=count(bound['minimum_synapses'])<=count(bound['maximum_synapses'])<=128
                and 0<number(bound['minimum_resistance'])<=number(bound['maximum_resistance']),
                'candidate_window_runtime2_invalid_bound')
        common=plan['composite_measurement']
        keys(common,COMPOSITE_FIELDS|{'candidate_window_policy'},'candidate_window_runtime2_common_fields')
        require(count(common['schema_version'])==2,'candidate_window_runtime2_common_schema')
        contract=protocol['composite_measurement']
        for key in ('schema_version','method_id','context_policy','geometry_policy','candidate_window_policy'):_same(common[key],contract[key])
        maximum=count(contract['context_policy']['maximum_samples'])
        validate_policy(common['candidate_window_policy'],n,maximum)
        # Private policy1 view reuses shared numeric/context validation only;
        # it is not a cold configuration or schema1 observation/certificate.
        view=deepcopy(common);view.pop('candidate_window_policy');view['schema_version']=1
        validate_composite_measurement(view,inputs=n,frequency=protocol['stimulus_profile']['frequency_hz'],maximum_samples=maximum)
        limits=common['attempt_limits']
        require(count(limits['maximum_native_probes'])>=n+2 and
                count(limits['maximum_total_samples'])>=count(contract['context_policy']['maximum_total_samples']),
                'candidate_window_runtime2_attempt_budget_relations')
        for axis in ('model','wall'):
            require(number(common['maximum_group_'+axis+'_seconds'])<=number(plan['maximum_'+axis+'_seconds']),
                    'candidate_window_runtime2_group_budget_relations')
        policy=search['capacitance_search']
        if policy is not None:
            # The declaration codec does not manufacture/require an owned C0
            # witness or change the caller's record_capacitance_history flag.
            audit_capacitance_search_policy(policy,configuration=search)
            reserve=count(policy['maximum_cursor_elements'])//_capacitance_contexts(policy)
            for i,bound in enumerate(bounds[:-1]):
                lengths=min(count(search['maximum_candidates_per_input']),count(bound['maximum_length'])-count(bound['minimum_length'])+1)
                counts=count(bound['maximum_synapses'])-count(bound['minimum_synapses'])+1 if search['normalization']=='N0' else 0
                require(lengths<=reserve and counts<=reserve-lengths,'candidate_window_runtime2_C_cursor_budget')
                region=count(bound['maximum_length'])-(count(bounds[i+1]['minimum_length']) if protocol['routing']=='branch_solo_burst' else 0)
                require(region<=0 or region<=count(policy['maximum_membranes']),'candidate_window_runtime2_C_region_budget')
        return dict(runtime_plan_schema_version=version,run_id=plan['run_id'],protocol_binding=plan['protocol_binding'],
            normalization=search['normalization'],n0_candidate_repeats=repeats,runtime_plan_validated=True,
            current_search_derived_from_cold_configuration=False,live_authority_restored=False,
            native_execution_verified=False,training_certificate_verified=False,scientific_verdict=None)
    except EvidenceError:raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,OverflowError) as error:
        raise EvidenceError('malformed_candidate_window_runtime2') from error
