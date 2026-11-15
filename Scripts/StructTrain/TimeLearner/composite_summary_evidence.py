"""Summary6 is an additional consistency record, never primary Train evidence."""
from .composite_certificate_evidence import accepted_measurement_records
from .composite_configuration import METHOD
from .composite_measurement_contract import integral_number_view
from .composite_source_evidence import keys
from .domain_evidence import audit_resistance_domain
from .native_evidence import count, number, require
from .response_domain_evidence import _finite_json, _same

FIELDS = set(('kind schema_version state outcome reason model_state_kind actual_model_revision model_epoch '
    'actual_parameters tolerances runtime_plan measurement_method source_origin owner_family_binding '
    'reference_complete capture_revision capture_epoch reference_group_ids final_group_ids '
    'reference_semantic_proof_ids final_semantic_proof_ids composite_counters certificate '
    'certificate_matches_actual_model contains_evaluation_verdict search_history_retained candidates '
    'rejections resistance_domains accepted_parameters applied_edits search_probes references').split())
REFERENCE_FIELDS = set(('input_id run_id trial_id effective_model_revision raw_potential '
    'measurement_group_id semantic_proof_id').split())
CANDIDATE_FIELDS = set(('input_index model_epoch parameters full_parameters model_revision trial_id anchor_trial_id '
    'timing_low timing_high amplitude_residual within_timing within_amplitude parameter_change_cost '
    'measurement_group_id semantic_proof_id anchor_group_id anchor_semantic_proof_id').split())


def _measurement(records, identity, proof):
    require(identity in records, 'composite_summary_unknown_group')
    record = records[identity]
    require(record['consumed'] is True and record['measurement'] is not None
            and record['measurement']['semantic_proof_id'] == proof,
            'composite_summary_unconsumed_group_or_proof')
    return record


def _audit_summary(document, package, archive_audit, *, schema_version, recovery=False):
    keys(document, FIELDS | ({'recovery_ledger','contains_controller_checkpoint'} if recovery else set()),
         'unknown_composite_summary_fields'); _finite_json(document)
    if recovery:
        require(document['contains_controller_checkpoint'] is False,'recovery_summary_is_not_checkpoint')
        _same(document['recovery_ledger'],package['recovery_ledger'])
    summary = integral_number_view(document); archive = package['measurement_archive']
    require(summary['kind'] == 'native_training_state_summary' and count(summary['schema_version']) == schema_version
            and summary['state'] == 'finished' and summary['measurement_method'] == METHOD
            and summary['contains_evaluation_verdict'] is False,
            'composite_summary_schema_state_or_evaluation_claim')
    for field, value in [('outcome', package['training_outcome']), ('reason', package['reason']),
            ('model_state_kind', package['state_kind']), ('actual_model_revision', package['model_revision']),
            ('model_epoch', package['model_epoch']), ('actual_parameters', package['trained_inputs']),
            ('runtime_plan', package['runtime_plan']), ('tolerances', package['runtime_plan']['search']['tolerances']),
            ('source_origin', archive['source_origin']), ('owner_family_binding', archive['owner_family_binding']),
            ('reference_complete', package['reference_complete']), ('capture_revision', package['capture_revision']),
            ('capture_epoch', package['capture_epoch']), ('certificate', package['certificate']),
            ('reference_group_ids', archive['reference_group_ids']), ('final_group_ids', archive['final_group_ids']),
            ('composite_counters', archive['counters'])]:
        _same(summary[field], value)
    require(type(summary['certificate_matches_actual_model']) is bool
            and summary['certificate_matches_actual_model'] is (package['certificate'] is not None)
            and type(summary['search_history_retained']) is bool, 'composite_summary_certificate_or_history_flag')
    references, finals = accepted_measurement_records(archive)
    for field, records in [('reference_semantic_proof_ids', references), ('final_semantic_proof_ids', finals)]:
        _same(summary[field], [record['measurement']['semantic_proof_id'] for record in records])
    require(type(summary['references']) is list and len(summary['references']) == len(references),
            'composite_summary_reference_dimension')
    for entry, record in zip(summary['references'], references):
        keys(entry, REFERENCE_FIELDS, 'composite_summary_reference_fields')
        logical = record['logical_request']
        _same(entry, dict(input_id=logical['input_id'], run_id=logical['run_id'], trial_id=logical['trial_id'],
            effective_model_revision=record['native_group']['specification']['effective_model_revision'],
            raw_potential=record['measurement']['raw_potential'], measurement_group_id=record['group_id'],
            semantic_proof_id=record['measurement']['semantic_proof_id']))
    for field in ('candidates', 'rejections', 'resistance_domains'):
        require(type(summary[field]) is list, 'composite_summary_history_array')
    if not summary['search_history_retained']:
        require(all(not summary[field] for field in ('candidates', 'rejections', 'resistance_domains'))
                and all(summary[field] is None for field in ('accepted_parameters', 'applied_edits', 'search_probes')),
                'composite_imported_summary_invented_search_history')
        return dict(summary_consistent=True, search_history_retained=False, native_execution_verified=False,
                    evaluation_verdict=None)
    count(summary['applied_edits']); count(summary['search_probes'])
    accepted = summary['accepted_parameters']
    require(type(accepted) is list and len(accepted) == len(package['protocol']['inputs']),
            'composite_summary_accepted_parameter_dimension')
    for value in accepted:
        keys(value, {'length', 'synapses', 'resistance'}, 'composite_summary_accepted_parameter_fields')
        require(count(value['length']) >= 1 and 1 <= count(value['synapses']) <= 128 and number(value['resistance']) > 0,
                'composite_summary_accepted_parameter_value')
    records = {record['group_id']: record for record in archive['records']}
    target = {record['logical_request']['input_id']: record['measurement']['raw_potential'] for record in references}
    tolerances = summary['tolerances']; cap_candidates = 0
    for candidate in summary['candidates']:
        allowed = CANDIDATE_FIELDS | ({'capacitance'} if 'capacitance' in candidate else set())
        keys(candidate, allowed, 'composite_summary_candidate_fields')
        current = _measurement(records, candidate['measurement_group_id'], candidate['semantic_proof_id'])
        anchor = _measurement(records, candidate['anchor_group_id'], candidate['anchor_semantic_proof_id'])
        logical = current['logical_request']; index = count(candidate['input_index'])
        require(index == count(logical['input_index']) and index < len(package['protocol']['inputs'])
                and current['purpose'] == anchor['purpose'] == 'search'
                and candidate['trial_id'] == logical['trial_id']
                and candidate['anchor_trial_id'] == anchor['logical_request']['trial_id']
                and candidate['model_revision'] == logical['base_model_revision'] == anchor['logical_request']['base_model_revision']
                and count(candidate['model_epoch']) == count(logical['model_epoch']) == count(anchor['logical_request']['model_epoch']),
                'composite_summary_candidate_group_binding')
        parameters = candidate['full_parameters']
        require(type(parameters) is list and len(parameters) == len(package['protocol']['inputs']),
                'composite_summary_candidate_parameter_dimension')
        _same(candidate['parameters'], parameters[index])
        from .training_capacitance_witness import validate_graph_input_parameters
        validate_graph_input_parameters(package['configuration']['model'], current['candidate_binding']['model_identity'], parameters)
        measured, fixed = current['measurement'], anchor['measurement']
        low = number(measured['arrival'] - fixed['plateau_end']); high = number(measured['plateau_end'] - fixed['arrival'])
        residual = number(measured['raw_potential'] - target[logical['input_id']])
        amplitude_tolerance = number(tolerances['amplitude_absolute'] + tolerances['amplitude_relative'] * abs(target[logical['input_id']]))
        _same(candidate['timing_low'], low); _same(candidate['timing_high'], high)
        _same(candidate['amplitude_residual'], residual)
        require(type(candidate['within_timing']) is bool and type(candidate['within_amplitude']) is bool
                and candidate['within_timing'] is (max(abs(low), abs(high)) <= tolerances['sync'])
                and candidate['within_amplitude'] is (abs(residual) <= amplitude_tolerance)
                and number(candidate['parameter_change_cost']) >= 0, 'composite_summary_candidate_residual')
        if 'capacitance' in candidate:
            witness = current['candidate_binding']['optional_C0_witness']
            require(witness is not None, 'composite_summary_candidate_invented_C0')
            _same(candidate['capacitance'], witness['controller_parameters']); cap_candidates += 1
    for rejection in summary['rejections']:
        keys(rejection, {'trial_id', 'reason'}, 'composite_summary_rejection_fields')
        require(type(rejection['trial_id']) is str and type(rejection['reason']) is str and rejection['reason'],
                'composite_summary_rejection_identity')
    domains = [audit_resistance_domain(record) for record in summary['resistance_domains']]
    return dict(summary_consistent=True, search_history_retained=True, candidates_recomputed=len(summary['candidates']),
                capacitance_candidates=cap_candidates, resistance_domains=domains, native_execution_verified=False,
                search_decisions_replayed=False, parameter_change_cost_recomputed=False,
                rejection_reasons_recomputed=False, evaluation_verdict=None)


def audit_composite_summary(document, package, archive_audit):
    return _audit_summary(document, package, archive_audit, schema_version=6)
