"""Describe audited native search history without promoting a stopped model.

Candidate measurements, rejected trials, domain assessments and the actual
terminal graph are separate evidence. Neither a legal domain nor a terminal
parameter vector proves that a complete candidate measurement exists.
"""
from copy import deepcopy
from pathlib import Path

from .collector_provenance import _frozen
from .native_evidence import count, number, parse_json_bytes, require
from .native_pipeline_worker import audit_run_manifest


def _parameters(values, size):
    require(type(values) is list and len(values) == size, 'search_report_parameter_dimensions')
    for value in values:
        require(type(value) is dict and set(value) == {'length', 'synapses', 'resistance'} and
                count(value['length']) >= 1 and count(value['synapses']) >= 1 and
                number(value['resistance']) > 0, 'search_report_parameters')
    return deepcopy(values)


def _project_summary(summary, model):
    require(summary.get('kind') == 'native_training_state_summary' and
            type(summary.get('schema_version')) is int and summary['schema_version'] == 8,
            'search_report_requires_native_summary8')
    size = len(model['inputs'])
    require(size > 0 and model['normalization'] in ('N0', 'N1') and
            type(model['branch']) is bool and type(summary['search_history_retained']) is bool and
            type(summary['reference_complete']) is bool,
            'search_report_model_or_history')
    require(all(type(summary[key]) is list for key in
                ('candidates', 'resistance_domains', 'rejections', 'final_group_ids')),
            'search_report_history_arrays')
    retained = summary['search_history_retained']
    actual = _parameters(summary['actual_parameters'], size)
    candidates = []
    for value in summary['candidates']:
        index = count(value['input_index'])
        require(index < size, 'search_report_input_index')
        parameters = _parameters(value['full_parameters'], size)
        require(parameters[index] == value['parameters'] and
                number(value['timing_low']) <= number(value['timing_high']) and
                type(value['within_timing']) is bool and type(value['within_amplitude']) is bool,
                'search_report_candidate')
        number(value['amplitude_residual'])
        # Retain cost, capacitance witnesses and all other audited fields too.
        # A formatter must not erase a factor that distinguished two candidates.
        candidates.append(deepcopy(value))
    ids = [value['trial_id'] for value in candidates]
    require(len(ids) == len(set(ids)) and (retained or not candidates),
            'search_report_duplicate_or_unretained_candidates')
    matches = [value['trial_id'] for value in candidates if
               value['model_revision'] == summary['actual_model_revision'] and
               value['full_parameters'] == actual]
    domains = []
    for value in summary['resistance_domains']:
        index = count(value['input_index'])
        require(index < size and 0 < number(value['minimum_resistance']) <=
                number(value['maximum_resistance']), 'search_report_resistance_domain')
        geometry = _parameters(value['geometry'], size)
        domains.append(dict(input_index=index, base_model_revision=value['base_model_revision'],
            geometry=geometry, minimum_resistance=value['minimum_resistance'],
            maximum_resistance=value['maximum_resistance'],
            locked_by_shared_bank=value['locked_by_shared_bank']))
    return dict(topology='Branch' if model['branch'] else 'Classic',
        normalization=model['normalization'], input_count=size, anchor_index=size-1,
        outcome=summary['outcome'], reason=summary['reason'],
        actual_model_revision=summary['actual_model_revision'], actual_parameters=actual,
        reference_complete=summary['reference_complete'],
        candidate_history_retained=retained,
        actual_model_candidate_trial_ids=matches if retained else None,
        actual_model_matched_in_candidate_history=bool(matches) if retained else None,
        final_verification_group_ids=deepcopy(summary['final_group_ids']),
        producer_reported_search_probes=count(summary['search_probes']),
        producer_reported_edits=count(summary['applied_edits']),
        recorded_candidate_measurements=candidates,
        recorded_rejections=deepcopy(summary['rejections']),
        assessed_resistance_domains=domains, tolerances=deepcopy(summary['tolerances']),
        domain_assessments_are_not_presentations=True,
        attempt_total_independently_recounted=False,
        training_or_final_verification_verdict=None, scientific_verdict=None)


def analyze_search_history(path):
    """Full production DATA audit, followed by a hash-bound summary projection.

    Only summary8 has this explicit projection contract. Historical formats keep
    their existing readers; no missing history is reconstructed from counters.
    """
    path = Path(path).resolve(strict=True)
    manifest_raw, manifest_record = _frozen(path, 16*1024**2)
    manifest = parse_json_bytes(manifest_raw)
    require(manifest.get('operation') == 'train' and manifest.get('validity') == 'valid',
            'search_report_requires_auditable_training_run')
    proof = audit_run_manifest(path)
    require(proof.get('run_evidence_consistent') is True, 'search_report_run_audit_incomplete')
    records = {value['path']: value for value in manifest['artifacts']}

    def bound(relative, maximum):
        raw, record = _frozen(path.parent/relative, maximum)
        require(relative in records and
                all(record[key] == records[relative][key] for key in ('bytes', 'sha256')),
                'search_report_source_changed')
        return parse_json_bytes(raw), record

    execution, _ = bound('native/execution.json', 16*1024**2)
    name = execution['package_path']
    require(name in ('train_stopped_state.json', 'train_learned_state.json'),
            'search_report_terminal_package')
    summary, summary_record = bound('native/'+name.replace('_state.json', '_summary.json'),
                                    64*1024**2)
    job, _ = bound('input/job.json', 16*1024**2)
    require(summary['actual_model_revision'] == execution['model_revision'] and
            summary['outcome'] == execution['training_outcome'], 'search_report_terminal_binding')
    result = _project_summary(summary, job['configuration']['model'])
    _, after = _frozen(path, 16*1024**2)
    require(after == manifest_record, 'search_report_manifest_changed')
    return dict(kind='timelearner_native_search_history_report', schema_version=1,
        source_manifest=manifest_record, source_summary=summary_record,
        source_run_execution=manifest['execution'], source_run_validity=manifest['validity'],
        runtime_fingerprint=manifest['runtime_fingerprint'], data_audit=proof,
        native_execution_attested=False, **result)
