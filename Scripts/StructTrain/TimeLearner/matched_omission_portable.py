"""Independent reader of complete portable matched-omission witnesses.

The production codec and this reader share a data contract, not numerical code.
Primary CSV, intended/applied source hashes, packet bindings, sample budgets and
the operational assignment are checked afresh. No native execution, causal
origin, wall-time enforcement or TrainingCertificate is inferred from a file.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath

from .matched_omission_evidence import (METHOD, POLICY_FIELDS as COMPARISON_FIELDS,
    MAXIMUM_FIELDS as LEGACY_MAXIMUM_FIELDS, _dimension, _maximum_dimensions,
    _recompute, _trace)
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, load, number, require
from .response_domain_evidence import _finite_json, _keys, _same, _text

KIND = 'timelearner_matched_omission_evidence'
TOP = ('schema_version kind method complete_group diagnostic_only training_certificate_eligible '
       'scientific_verdict specification policy source time_budget traces assignment attestation')
SPEC = ('schema_version run_id group_id sample_id protocol_revision pattern_hash input_id '
        'base_model_revision effective_model_revision reset_binding model_instance_binding '
        'model_epoch assigned_input channel routing stimulus_ids physical_channel_paths '
        'stimulus_profile duration minimum_amplitude')
POLICY = COMPARISON_FIELDS+' schema_version maximum_samples maximum_total_samples maximum_native_probes'
SOURCE = 'planned_isi applied_isi planned_sha256 applied_sha256 canonical_encoding'
TIME = 'maximum_model_seconds maximum_wall_seconds elapsed_model_seconds elapsed_wall_seconds enforcement_verified'
TRACE = ('role omitted_input presented_ordinals planned_presented_isi applied_presented_isi '
         'presented_pattern_sha256 relative_path bytes sha256 native_evidence binding')
BINDING = ('group_id source_pattern_hash reset_binding model_instance_binding current_base_revision '
           'native_completed full_mask_restored physical_channel_paths')
ASSIGNMENT = 'validity reasons maxima selected_full_maximum measured_maximum'
MAXIMUM = 'first_sample last_sample amplitude raw_potential time plateau_end'
SUPPORT_MAXIMUM = LEGACY_MAXIMUM_FIELDS+' comparison_first_sample comparison_last_sample'
ATTESTATION = ('native_execution_verified physical_paths_independently_verified '
               'reset_instance_ownership_independently_verified')
CANONICAL_ENCODING = 'length-framed-utf8-binary64-v1'


def _isi(value):
    require(type(value) is list and bool(value), 'portable_missing_source_isi')
    result = []
    for item in value:
        item = number(item); require(item >= 0, 'portable_negative_source_isi')
        result.append(item)
    return result


def _presented(source, mask):
    """Exact addition order of production PlanStimulusSubset, not prefix subtraction."""
    if len(mask) == len(source): return list(source)
    result, next_source = [], 0
    for ordinal in mask:
        gap = 0.
        while next_source <= ordinal:
            gap = number(gap+source[next_source]); next_source += 1
        result.append(gap)
    return result


def _relative_path(value):
    require(type(value) is str and bool(value), 'portable_missing_trace_path')
    path = PurePosixPath(value)
    require(str(path) == value and not path.is_absolute() and ':' not in value and
            '\\' not in value and all(v not in ('', '.', '..') for v in value.split('/')),
            'portable_unsafe_trace_path')
    return value


def _canonical_csv(raw, channels):
    rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    header = ['time', 'stimulus']+['soma'+str(i) for i in range(channels)]
    require(rows and rows[0] == header and all(len(v) == len(header) for v in rows[1:]),
            'portable_trace_columns')
    values = [[number(float(v)) for v in row] for row in rows[1:]]
    canonical = ','.join(header)+'\n'
    canonical += ''.join(','.join(format(v, '.17g') for v in row)+'\n' for row in values)
    require(canonical.encode('utf-8') == raw, 'portable_noncanonical_primary_csv')


def audit_portable_matched_evidence(document, primary):
    try:
        _keys(document, TOP); _finite_json(document)
        require(document['kind'] == KIND and _dimension(document['schema_version']) == 1 and
                document['method'] == METHOD and document['complete_group'] is True and
                document['diagnostic_only'] is True and document['training_certificate_eligible'] is False and
                document['scientific_verdict'] is None, 'portable_unknown_schema_or_claim')
        spec, policy = document['specification'], document['policy']
        _keys(spec, SPEC); _keys(policy, POLICY)
        require(_dimension(spec['schema_version']) == _dimension(policy['schema_version']) == 1,
                'portable_unknown_specification_or_policy_schema')
        for key in ('run_id', 'group_id', 'sample_id', 'protocol_revision', 'pattern_hash', 'input_id',
                    'base_model_revision', 'effective_model_revision', 'reset_binding', 'model_instance_binding'):
            _text(spec[key])
        assigned, channel = _dimension(spec['assigned_input']), _dimension(spec['channel'])
        _dimension(spec['model_epoch'])
        require(number(spec['duration']) > 0 and number(spec['minimum_amplitude']) > 0,
                'portable_invalid_observation_limits')
        paths, ids = spec['physical_channel_paths'], spec['stimulus_ids']
        require(type(paths) is list and paths and all(type(v) is str and v for v in paths) and
                len(paths) == len(set(paths)), 'portable_invalid_physical_paths')
        source = document['source']; _keys(source, SOURCE)
        planned, applied = _isi(source['planned_isi']), _isi(source['applied_isi'])
        require(planned == applied and len(planned) >= 2, 'portable_applied_source_changed')
        n = len(planned)
        require(assigned < n and channel < len(paths) and type(ids) is list and
                ids == ['pulse'+str(i) for i in range(n)], 'portable_assigned_inventory')
        require(source['canonical_encoding'] == CANONICAL_ENCODING and
                source['planned_sha256'] == source['applied_sha256'] == spec['pattern_hash'] ==
                canonical_model_sha256(planned), 'portable_source_hash_changed')
        comparison = {key: policy[key] for key in COMPARISON_FIELDS.split()}
        for value in comparison.values(): require(number(value) >= 0, 'portable_negative_policy')
        radius = _dimension(policy['comparison_radius_ticks']); require(radius > 0, 'portable_invalid_radius')
        maximum_samples = _dimension(policy['maximum_samples'])
        maximum_total = _dimension(policy['maximum_total_samples'])
        maximum_probes = _dimension(policy['maximum_native_probes'])
        require(maximum_samples > 0 and maximum_total > 0 and maximum_probes >= n+2,
                'portable_invalid_sample_or_probe_budget')
        time = document['time_budget']; _keys(time, TIME)
        require(number(time['maximum_model_seconds']) > 0 and number(time['maximum_wall_seconds']) > 0 and
                time['elapsed_model_seconds'] is None and time['elapsed_wall_seconds'] is None and
                time['enforcement_verified'] is False, 'portable_unsupported_time_attestation')
        attestation = document['attestation']; _keys(attestation, ATTESTATION)
        require(all(v is False for v in attestation.values()), 'portable_unsupported_native_attestation')
        records = document['traces']
        require(type(records) is list and len(records) == n+2 and type(primary) is dict,
                'portable_incomplete_group')
        group = dict(group_id=spec['group_id'], assigned_input=assigned, assigned_channel=channel,
                     physical_channel_paths=paths, source_pattern_sha256=spec['pattern_hash'],
                     reset_binding=spec['reset_binding'], model_instance_binding=spec['model_instance_binding'],
                     policy=comparison)
        traces, names, total_samples = [], set(), 0
        for index, record in enumerate(records):
            _keys(record, TRACE)
            omitted = None if index in (0, n+1) else index-1
            role = 'full_before' if index == 0 else 'full_after' if index == n+1 else 'omit'
            require(record['role'] == role and (record['omitted_input'] is None if omitted is None else
                    _dimension(record['omitted_input']) == omitted), 'portable_control_order_changed')
            mask = [i for i in range(n) if i != omitted]
            require(type(record['presented_ordinals']) is list and
                    all(type(v) is int for v in record['presented_ordinals']) and
                    record['presented_ordinals'] == mask, 'portable_control_mask_changed')
            presented = _presented(planned, mask)
            require(_isi(record['planned_presented_isi']) == _isi(record['applied_presented_isi']) == presented and
                    record['presented_pattern_sha256'] == canonical_model_sha256(presented),
                    'portable_presented_source_changed')
            binding = record['binding']; _keys(binding, BINDING)
            expected_binding = dict(group_id=spec['group_id'], source_pattern_hash=spec['pattern_hash'],
                reset_binding=spec['reset_binding'], model_instance_binding=spec['model_instance_binding'],
                current_base_revision=spec['base_model_revision'], native_completed=True,
                full_mask_restored=True, physical_channel_paths=paths)
            _same(binding, expected_binding)
            name = _relative_path(record['relative_path'])
            require(name not in names and name in primary and type(primary[name]) is bytes,
                    'portable_missing_or_duplicate_primary')
            names.add(name); raw = primary[name]
            require(_dimension(record['bytes']) == len(raw) and
                    record['sha256'] == hashlib.sha256(raw).hexdigest(), 'portable_primary_hash_changed')
            _canonical_csv(raw, len(paths))
            packet = record['native_evidence']
            trace = _trace(packet, dict(path=name, presented_ordinals=mask, sha256=record['sha256']),
                           raw, group, index, expected_input_id=spec['input_id'])
            actual, requested, prepared = trace['spec'], packet['requested_specification'], trace['prepared']
            require(not traces or number(actual['begin']) > number(traces[-1]['spec']['end']),
                    'portable_native_trials_overlap_or_reorder')
            require(actual['run_id'] == spec['run_id'] and actual['sample_id'] == spec['sample_id'] and
                    actual['pattern_hash'] == record['presented_pattern_sha256'] and
                    actual['minimum_amplitude'] == spec['minimum_amplitude'] and
                    requested['end'] == spec['duration'],
                    'portable_native_specification_changed')
            _same(actual['stimulus_profile'], spec['stimulus_profile'])
            for key in ('protocol_revision', 'base_model_revision', 'effective_model_revision', 'model_epoch', 'routing'):
                _same(prepared[key], spec[key])
            require(_dimension(actual['maximum_samples']) <= maximum_samples and
                    len(trace['times']) <= maximum_samples, 'portable_per_probe_sample_budget_exhausted')
            total_samples += len(trace['times'])
            require(total_samples <= maximum_total, 'portable_total_sample_budget_exhausted')
            traces.append(trace)
        require(set(primary) == names, 'portable_unexpected_primary_files')
        observed_span = number(traces[-1]['spec']['end']-traces[0]['spec']['begin'])
        require(0 < observed_span <= time['maximum_model_seconds'], 'portable_observed_model_span_exceeds_budget')
        assignment = document['assignment']; _keys(assignment, ASSIGNMENT)
        require(type(assignment['maxima']) is list, 'portable_missing_maxima')
        legacy_maxima = []
        for peak in assignment['maxima']:
            _keys(peak, SUPPORT_MAXIMUM)
            legacy_maxima.append({key: peak[key] for key in LEGACY_MAXIMUM_FIELDS.split()})
        group.update(maxima=legacy_maxima, selected_full_maximum=assignment['selected_full_maximum'])
        _maximum_dimensions(group, len(traces[0]['times']), n)
        validity, reasons, maxima, selected = _recompute(group, traces)
        require(validity in ('valid', 'missing', 'ambiguous', 'clipped', 'non_repeatable'),
                'portable_not_a_complete_operational_outcome')
        _same(assignment['validity'], validity); _same(assignment['reasons'], reasons)
        _same(legacy_maxima, maxima); _same(assignment['selected_full_maximum'], selected)
        for recorded, measured in zip(assignment['maxima'], maxima):
            first = max(0, measured['first_sample']-radius)
            last = min(len(traces[0]['times'])-1, measured['last_sample']+radius)
            require(_dimension(recorded['comparison_first_sample']) == first and
                    _dimension(recorded['comparison_last_sample']) == last, 'portable_comparison_range_changed')
        measured = None if selected is None else {key: maxima[selected][key] for key in MAXIMUM.split()}
        _same(assignment['measured_maximum'], measured)
        return dict(reader_version=1, kind=KIND, method=METHOD, complete_group=True,
                    assignment_recomputed=True, assignment_validity=validity, maxima=maxima,
                    selected_full_maximum=selected, measured_maximum=measured,
                    primary_traces_checked=len(traces), total_samples_checked=total_samples,
                    total_budget_declarations_available=True, sample_probe_budgets_verified=True,
                    planned_applied_isi_hashes_recomputed=True, observed_model_span=observed_span,
                    time_budget_enforcement_independently_verified=False,
                    actual_event_schedule_derived_from_planned_isi=False,
                    native_execution_verified=False, physical_paths_independently_verified=False,
                    reset_instance_ownership_independently_verified=False, causal_origin_verified=False,
                    training_certificate_eligible=False, evaluation_verdict=None)
    except EvidenceError: raise
    except (KeyError, TypeError, ValueError, IndexError, AttributeError, UnicodeError, csv.Error, OverflowError) as error:
        raise EvidenceError('malformed_portable_matched_omission_evidence') from error


def audit_portable_matched_file(path):
    try:
        path = Path(path).resolve(); document = load(path); primary = {}
        require(type(document.get('traces')) is list, 'portable_missing_trace_inventory')
        for record in document['traces']:
            name = _relative_path(record['relative_path'])
            source = (path.parent/name).resolve()
            require(source.is_relative_to(path.parent) and name not in primary, 'portable_trace_escapes_or_duplicates')
            primary[name] = source.read_bytes()
        return audit_portable_matched_evidence(document, primary)
    except EvidenceError: raise
    except (OSError, KeyError, TypeError, AttributeError, ValueError) as error:
        raise EvidenceError('malformed_or_missing_portable_matched_primary') from error


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('evidence'); parser.add_argument('--output')
    args = parser.parse_args(); result = audit_portable_matched_file(args.evidence)
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.output:
        output = Path(args.output).resolve()
        require(not output.is_relative_to(Path(args.evidence).resolve().parent), 'portable_report_overlaps_primary')
        with output.open('x', encoding='utf-8') as stream: stream.write(text)
    else: print(text, end='')


if __name__ == '__main__': main()
