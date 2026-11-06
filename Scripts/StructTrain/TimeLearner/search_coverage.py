"""Describe recorded search coverage without claiming exhaustive feasibility.

Only candidate evidence and typed recovery events carry full parameter vectors.
Other invalid observations must stay unknown here, rather than being assigned
an invented geometry from the final model or a neighbouring trial.
"""
from collections import Counter
import hashlib
from pathlib import Path

from .candidate_recovery import project_recovery_summary, RECOVERY_MODE
from .learned_evidence import load_case as load_completed
from .native_evidence import load, require
from .stock_recovery_study import audit as audit_study
from .stopped_evidence import load_case as load_stopped


def summarize_recorded_search(summary):
    """Projection of already audited producer records, never a primary audit."""
    _, policy = project_recovery_summary(summary)
    groups = {};valid = summary['candidates'];events = summary.get('candidate_recovery_events', [])
    candidate_trials = {e['trial_id'] for e in valid}
    event_trials = {e['trial_id'] for e in events}
    require(len(candidate_trials) == len(valid) and len(event_trials) == len(events) and
            not candidate_trials.intersection(event_trials), 'coverage_duplicate_or_relabelled_trial')
    for field, records in (('measured_candidates', valid), ('typed_unassigned_observations', events)):
        for event in records:
            # Anchor rejection belongs to its candidate's full physical graph;
            # retain measured-input versus controlled-input as separate axes.
            input_index = event.get('candidate_input_index', event['input_index'])
            parameters = event['full_parameters']
            require(type(input_index) is int and 0 <= input_index < len(parameters), 'coverage_input_out_of_range')
            key = (input_index, tuple(p['length'] for p in parameters), tuple(p['synapses'] for p in parameters))
            group = groups.setdefault(key, {'measured_candidates': 0, 'typed_unassigned_observations': 0,
                                           'resistances': set(), 'observed_input_indices': set(),
                                           'trial_ids': []})
            group[field] += 1;group['resistances'].add(parameters[input_index]['resistance'])
            group['observed_input_indices'].add(event['input_index']);group['trial_ids'].append(event['trial_id'])
    rows = []
    for (index, lengths, counts), group in sorted(groups.items()):
        resistances = sorted(group.pop('resistances'))
        rows.append({'candidate_input_index': index, 'full_lengths': list(lengths), 'full_synapses': list(counts),
                     **group, 'observed_input_indices': sorted(group['observed_input_indices']),
                     'trial_ids': sorted(group['trial_ids']), 'distinct_resistances': len(resistances),
                     'resistance_values': resistances})
    rejections = summary['rejections']
    unassigned = Counter(e['validity'] for e in events)
    return {'policy': policy, 'outcome': summary['outcome'], 'reason': summary['reason'],
            'recorded_geometry_groups': rows, 'measured_candidate_records': len(valid),
            'typed_unassigned_observations': len(events), 'typed_assignment_failures': dict(sorted(unassigned.items())),
            'recorded_rejection_entries': len(rejections),
            'rejection_entries_without_full_parameter_witness': sum(r['trial_id'] not in event_trials for r in rejections),
            'producer_invalid_observations': summary['invalid_observations'] if policy == RECOVERY_MODE else None,
            'invalid_counter_unknown_for_legacy_summary': policy != RECOVERY_MODE,
            'all_invalid_observations_independently_recounted': False,
            'search_probes': summary['search_probes'], 'reference_probes': summary['reference_probes'],
            'applied_edits': summary['applied_edits'], 'full_search_box_exhaustion_attested': False,
            'physical_infeasibility_attested': False, 'primary_validation_performed_by_this_projection': False,
            'scientific_verdict': None}


def analyze_stock_recovery(directory):
    """Audit original complete study/CSV first, then describe recorded coverage."""
    directory = Path(directory).resolve(strict=True)
    audited = audit_study(directory);rows = []
    design = load(directory/'design.json')
    declarations = {r['name']: r for r in design['rows']}
    for row in audited['rows']:
        native = directory/'runs'/row['name']/'native';execution = load(native/'execution.json')
        path = native/execution['package_path']
        package, summary, _, _ = (load_completed if row['completed_boundary'] else load_stopped)(path)
        summary_path = path.with_name(path.name.replace('_learned_state.json', '_learned_summary.json')
                                      if row['completed_boundary'] else path.name.replace('_stopped_state.json', '_stopped_summary.json'))
        rows.append({'name': row['name'], 'topology': declarations[row['name']]['topology'],
                     'initial_threshold': declarations[row['name']]['initial_threshold'],
                     'package_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'summary_sha256': hashlib.sha256(summary_path.read_bytes()).hexdigest(),
                     'model_revision': package['model_revision'], **summarize_recorded_search(summary)})
    return {'kind': 'stock_recovery_search_coverage', 'schema_version': 1, 'rows': rows,
            'source_study_audited': True, 'primary_validation_scope': 'existing full native study audit',
            'classification_assessed': False, 'scientific_verdict': None}
