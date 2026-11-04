"""Check declared downstream factors before Train, without inventing its model.

This is not effective-model validation. Every native phase must still validate
its actual predecessor state, graph and observations using its production worker.
"""
from .calibration import validate_trial_design
from .calibrated_evidence import REQUEST_FIELDS
from .model_identity import canonical_model_sha256 as digest
from .native_calibration_worker import SPEC_FIELDS, _evidence_boundary
from .native_evidence import count, equal, number, require
from .recognition_metrics import CRITERION_FIELDS, validate_response_criterion


@_evidence_boundary
def validate_downstream_declaration(operation, job, model):
    """Validate factors known from declarations; never create a source package."""
    n = len(model['inputs'])
    if operation == 'export':
        conversion = job['conversion_spec']
        require(type(conversion) is dict and type(conversion.get('schema_version')) is int
                and conversion['schema_version'] in (1, 2) and set(conversion) ==
                {'schema_version', 'mode', 'resistance_bounds'} |
                ({'post_tune'} if conversion['schema_version'] == 2 else set()),
                'unknown_conversion_spec')
        mode, bounds = conversion['mode'], conversion['resistance_bounds']
        require(mode in ('identity', 'historical_branch_n1_v1') and type(bounds) is list,
                'unknown_conversion_mode')
        if mode == 'identity':
            require(bounds == [], 'identity_has_unused_bounds')
        else:
            require(model['branch'] is True and model['normalization'] == 'N1' and len(bounds) == n,
                    'unsupported_historical_conversion')
            require(all(type(b) is dict and set(b) == {'minimum', 'maximum'} and
                        0 < number(b['minimum']) <= number(b['maximum']) for b in bounds),
                    'invalid_conversion_bounds')
        return
    require(1 <= count(job['maximum_model_ticks']) <= 1000000000,
            'pipeline_owner_or_tick_budget_invalid')
    if operation == 'evaluate':
        require(job['coverage_policy'] == 'per_trial_windows',
                'pipeline_continuous_stream_not_yet_verified')
        criterion = job['criterion']
    else:
        require(job['frequency_hz'] == model['frequency_hz'] and
                type(job['frequency_hz']) is int, 'worker_clock_or_tick_budget_mismatch')
        declaration = job['specification']
        require(type(declaration) is dict and set(declaration) == SPEC_FIELDS and
                all(type(declaration[k]) is str and declaration[k].strip()
                    for k in SPEC_FIELDS-{'criterion'}) and declaration['protocol'] in
                ('historical_same_matrix', 'frozen_independent_calibration'),
                'unknown_worker_calibration_specification')
        require(type(declaration['criterion']) is dict and
                set(declaration['criterion']) == CRITERION_FIELDS-{'id'}, 'unknown_response_criterion')
        criterion = {'id': 'post_anchor_target_whole_window_foil_v1', **declaration['criterion']}
        # PostTune fixed-threshold controls intentionally have no grid. Their
        # mode-specific semantics still belong to the native PostTune worker.
        fixed = operation == 'posttune' and job['schema_version'] >= 2 and \
            job['post_tune'].get('finalization') == 'keep_fixed_threshold'
        thresholds = job['thresholds']
        require(type(thresholds) is list and len(thresholds) <= 256, 'worker_grid_budget_limit')
        values = [number(t) for t in thresholds]
        require(len(set(values)) == len(values), 'invalid_calibration_threshold_grid')
        budget = count(job['maximum_candidates'])
        require((not values and budget == 0) if fixed else (bool(values) and 1 <= budget <= 256),
                'invalid_calibration_budget')
    validate_response_criterion(criterion)
    trials = job['trials']
    require(type(trials) is list and 2 <= len(trials) <= 10000 and
            all(type(t) is dict and set(t) == REQUEST_FIELDS for t in trials),
            'invalid_evaluation_trial_design')
    design = [{**{k: t[k] for k in ('trial_id', 'sample_id', 'label', 'pattern_isi',
                                  'reset_policy', 'duration')}, 'presentation_index': i}
              for i, t in enumerate(trials)]
    validate_trial_design(design)
    samples = {}
    target = digest(model['initial_isi'])
    for trial in trials:
        require(type(trial['run_id']) is str and bool(trial['run_id'].strip()) and
                (operation != 'evaluate' or trial['run_id'] == job['run_id']) and
                len(trial['pattern_isi']) == n and trial['pattern_hash'] == digest(trial['pattern_isi'])
                and ((trial['label'] == 'target') == (trial['pattern_hash'] == target)),
                'worker_trial_identity_or_shape_mismatch')
        require(type(trial['record_threshold_potential']) is bool and
                2 <= count(trial['maximum_samples']) <= 10000000,
                'invalid_calibration_proof_request_budget')
        ticks = number(number(trial['duration'])*number(model['frequency_hz']))
        require(equal(ticks, round(ticks)) and ticks+1 <= trial['maximum_samples'],
                'worker_trial_window_or_sample_budget')
        signature = trial['label'], trial['pattern_hash']
        require(samples.setdefault(trial['sample_id'], signature) == signature, 'worker_sample_collision')
