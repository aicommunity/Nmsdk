"""Independent replay of declared-window basin diagnostics from bound primary.

Geometry is recomputed in Python. Native packet/context/CSV integrity reuses
the strict portable reader, never its v1 assignment as the new decision. File
consistency does not attest live execution, causal lineage or Train success.
"""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

from .matched_omission_evidence import (GROUP_FIELDS, POLICY_FIELDS, METHOD as MATCHED_METHOD,
    _dimension, _maximum_dimensions, _trace)
from .matched_omission_portable import (MAXIMUM, _relative_path, audit_portable_matched_evidence)
from .model_identity import canonical_model_sha256
from .native_evidence import EvidenceError, load, number, parse_json_bytes, require
from .response_domain_evidence import _finite_json, _keys, _same, _text

METHOD = 'declared-window-basin-necessity-v1'
KIND = 'native_declared_window_basin_diagnostic'
TOP = ('kind schema_version method group_id assigned_input channel window_begin_offset window_end_offset '
       'specification geometry_policy minimum_amplitude status status_enum reasons rejected_tampering '
       'actual_assigned_onset geometry_validity geometry measured_maximum diagnostic_only '
       'training_certificate_eligible scientific_verdict witness_binding')
SPEC = 'schema_version method_id group_id input_id assigned_input channel window_begin_offset window_end_offset'
POLICY = 'schema_version maximum_inputs maximum_samples maximum_total_samples repeatability_absolute'
BINDING = ('complete_group group_id source_pattern_sha256 source_specification_sha256 base_model_revision '
           'effective_model_revision protocol_revision group portable')
GEOMETRY = 'validity reasons candidates selected_candidate measured_maximum'
CANDIDATE = 'maximum left right status controls necessary_inputs reasons'
ANCHOR = 'first_sample last_sample record_edge'


def _strings(values):
    require(type(values) is list and all(type(v) is str and v for v in values), 'basin_invalid_reason_list')


def _extrema(values):
    """Run compression keeps plateau identity; no window slicing or smoothing."""
    runs, cursor = [], 0
    for value, items in itertools.groupby(values):
        size = sum(1 for _ in items); end = cursor+size-1
        left, right = cursor > 0, end+1 < len(values)
        high = (not left or value > values[cursor-1]) and (not right or value > values[end+1])
        low = (not left or value < values[cursor-1]) and (not right or value < values[end+1])
        if high or low: runs.append(dict(first=cursor, last=end, value=value, high=high, low=low, edge=not left or not right))
        cursor = end+1
    return runs


def _anchors(extrema, peak, size):
    left = dict(first_sample=0, last_sample=0, record_edge=True)
    right = dict(first_sample=size-1, last_sample=size-1, record_edge=True)
    for valley in (e for e in extrema if e['low']):
        item = dict(first_sample=valley['first'], last_sample=valley['last'], record_edge=valley['edge'])
        if valley['last'] < peak['first_sample']: left = item
        elif valley['first'] > peak['last_sample']: right = item; break
    return left, right


def _presence(extrema, left, right, size, minimum):
    interior, uncertain = [], False
    for e in (e for e in extrema if e['high'] and e['last'] >= left and e['first'] <= right):
        if e['first'] == 0 and e['last'] == size-1:
            uncertain |= e['value'] >= minimum
        elif e['edge'] or e['first'] <= left or e['last'] >= right:
            uncertain = True
        else:
            interior.append(e); uncertain |= e['value'] < minimum
    if uncertain or len(interior) > 1: return 'unknown'
    return 'preserved' if interior else 'absent_within_fixed_basin'


class _Outcome(Exception):
    def __init__(self, validity, reason): self.validity, self.reason = validity, reason


def recompute_declared_basin_geometry(spec, policy, times, before, repeat, omissions):
    """Geometry-only operational result; inputs have one explicitly shared grid."""
    output = dict(validity='invalid_specification', reasons=[], candidates=[], selected_candidate=None, measured_maximum=None)
    def check(ok, validity, reason):
        if not ok: raise _Outcome(validity, reason)
    try:
        n, assigned = _dimension(spec['input_count']), _dimension(spec['assigned_input'])
        begin, end, minimum = (number(spec[k]) for k in ('window_begin', 'window_end', 'minimum_amplitude'))
        tolerance = number(policy['repeatability_absolute'])
        check(_dimension(spec['schema_version']) == _dimension(policy['schema_version']) == 1 and n > 0 and assigned < n and
              end > begin and minimum > 0 and tolerance >= 0, 'invalid_specification', 'invalid_declared_basin_specification_or_policy')
        check(n >= 2, 'unsupported', 'single_input_uses_existing_single_impulse_path')
        cap, per, total = (_dimension(policy[k]) for k in ('maximum_inputs', 'maximum_samples', 'maximum_total_samples'))
        check(cap > 0 and per > 0 and total > 0, 'invalid_specification', 'missing_declared_basin_budget')
        check(n <= cap, 'budget_exhausted', 'basin_input_budget_exhausted')
        check(type(omissions) is list and len(omissions) == n, 'invalid_specification', 'basin_omission_inventory_changed')
        size = len(times); check(size >= 3, 'incomplete', 'insufficient_basin_samples')
        check(size <= per and size*(n+2) <= total, 'budget_exhausted', 'basin_sample_budget_exhausted')
        times = [number(t) for t in times]
        check(all(b > a for a, b in zip(times, times[1:])), 'invalid_specification', 'invalid_declared_basin_grid')
        check(begin >= times[0] and end <= times[-1], 'incomplete', 'declared_basin_window_not_covered')
        ordered = {}
        for omitted, trace in omissions:
            ordinal = _dimension(omitted)
            check(ordinal < n and ordinal not in ordered, 'invalid_specification', 'duplicate_or_unknown_basin_omission')
            ordered[ordinal] = trace
        def values(trace):
            baseline = number(trace['baseline']); raw = trace['raw']
            check(type(raw) is list and len(raw) == size, 'invalid_specification', 'basin_trace_dimensions_or_baseline_changed')
            return [number(number(v)-baseline) for v in raw]
        a, b = values(before), values(repeat)
        controls = [_extrema(values(ordered[i])) for i in range(n)]
        check(all(number(abs(x-y)) <= tolerance for x, y in zip(a, b)), 'nonrepeatable', 'basin_full_response_not_repeatable')
        full, repeated = _extrema(a), _extrema(b)
        def intersects(e): return times[e['last']] >= begin and times[e['first']] <= end
        def topology(features):
            return [(e['first'], e['last'], e['high'], e['low'], e['edge']) for e in features if intersects(e)]
        check(topology(full) == topology(repeated), 'nonrepeatable', 'basin_window_topology_not_repeated')
        def peaks(features, raw):
            return [dict(first_sample=e['first'], last_sample=e['last'], amplitude=e['value'], raw_potential=raw[e['first']],
                         time=times[e['first']], plateau_end=times[e['last']])
                    for e in features if e['high'] and e['value'] >= minimum and intersects(e)]
        maxima, again = peaks(full, before['raw']), peaks(repeated, repeat['raw'])
        check([(p['first_sample'], p['last_sample']) for p in maxima] == [(p['first_sample'], p['last_sample']) for p in again],
              'nonrepeatable', 'basin_observable_peak_inventory_not_repeated')
        for peak in maxima:
            first, last = peak['first_sample'], peak['last_sample']; left, right = _anchors(full, peak, size)
            check((left, right) == _anchors(repeated, peak, size), 'nonrepeatable', 'basin_peak_or_valley_range_not_repeated')
            candidate = dict(maximum=peak, left=left, right=right, status='unknown', controls=[], necessary_inputs=[], reasons=[])
            if first == 0 or last == size-1 or times[first-1] < begin or times[last+1] > end:
                candidate.update(status='clipped', reasons=['basin_full_peak_not_interior_to_declared_window'])
            else:
                states = [_presence(c, left['last_sample'], right['first_sample'], size, minimum) for c in controls]
                absent = [i for i, state in enumerate(states) if state == 'absent_within_fixed_basin']
                candidate.update(controls=states, necessary_inputs=absent)
                if 'unknown' in states: candidate.update(status='unknown', reasons=['basin_control_geometry_unknown'])
                elif len(absent) == 1: candidate['status'] = 'unique_necessary'
                elif not absent: candidate.update(status='no_necessary_input', reasons=['basin_has_no_unique_necessary_input'])
                else: candidate.update(status='shared_necessary', reasons=['basin_requires_multiple_inputs'])
            output['candidates'].append(candidate)
        candidates = output['candidates']
        eligible = [i for i, c in enumerate(candidates) if c['status'] == 'unique_necessary' and c['necessary_inputs'] == [assigned]]
        best = max(eligible, key=lambda i: candidates[i]['maximum']['amplitude']) if eligible else None
        ambiguous = {'shared_necessary', 'no_necessary_input', 'unknown'}
        def possible(c): return c['status'] == 'clipped' or len(c['controls']) <= assigned or c['controls'][assigned] != 'preserved'
        for c in candidates:
            if best is not None and c['maximum']['amplitude'] < candidates[best]['maximum']['amplitude']: continue
            check(c['status'] != 'clipped', 'clipped', 'highest_window_basin_peak_is_clipped')
            check(c['status'] not in ambiguous or (best is not None and not possible(c)), 'ambiguous',
                  'highest_window_basin_peak_has_ambiguous_necessity')
        check(best is not None, 'missing', 'no_unique_assigned_basin_peak_in_declared_window')
        height = candidates[best]['maximum']['amplitude']
        check(sum(candidates[i]['maximum']['amplitude'] == height for i in eligible) == 1,
              'ambiguous', 'highest_assigned_window_basin_peaks_tie')
        repeated_height = b[candidates[best]['maximum']['first_sample']]
        for i, c in enumerate(candidates):
            assigned_here = c['status'] == 'unique_necessary' and c['necessary_inputs'] == [assigned]
            risk = assigned_here or ((c['status'] in ambiguous or c['status'] == 'clipped') and possible(c))
            check(i == best or b[c['maximum']['first_sample']] < repeated_height or not risk,
                  'nonrepeatable', 'highest_assigned_basin_peak_not_repeated')
        output.update(validity='valid', selected_candidate=best, measured_maximum=candidates[best]['maximum'])
    except _Outcome as outcome: output.update(validity=outcome.validity, reasons=[outcome.reason])
    return output


def _reference(reference, artifacts):
    _keys(reference, 'relative_path bytes sha256'); path = _relative_path(reference['relative_path'])
    require(path in artifacts and type(artifacts[path]) is bytes, 'basin_missing_bound_artifact')
    raw = artifacts[path]
    require(_dimension(reference['bytes']) == len(raw) and reference['sha256'] == hashlib.sha256(raw).hexdigest(), 'basin_artifact_digest_changed')
    value = parse_json_bytes(raw); require(type(value) is dict, 'basin_reference_not_object'); return path, value


def _geometry_dimensions(value, frames, inputs):
    _keys(value, GEOMETRY); _strings(value['reasons']); require(type(value['candidates']) is list, 'basin_missing_candidates')
    def maximum(peak):
        _keys(peak, MAXIMUM); first, last = (_dimension(peak[k]) for k in ('first_sample', 'last_sample'))
        require(first <= last < frames, 'basin_maximum_index_changed')
        for k in ('amplitude', 'raw_potential', 'time', 'plateau_end'): number(peak[k])
    for candidate in value['candidates']:
        _keys(candidate, CANDIDATE); maximum(candidate['maximum']); _strings(candidate['reasons'])
        for key in ('left', 'right'):
            anchor = candidate[key]; _keys(anchor, ANCHOR)
            require(_dimension(anchor['first_sample']) <= _dimension(anchor['last_sample']) < frames and
                    type(anchor['record_edge']) is bool, 'basin_anchor_changed')
        require(type(candidate['controls']) is list and type(candidate['necessary_inputs']) is list, 'basin_candidate_dimensions')
        for i in candidate['necessary_inputs']: require(_dimension(i) < inputs, 'basin_necessary_input_index_changed')
    if value['selected_candidate'] is not None:
        require(_dimension(value['selected_candidate']) < len(value['candidates']), 'basin_selected_candidate_index_changed')
    if value['measured_maximum'] is not None: maximum(value['measured_maximum'])


def audit_declared_window_basin_evidence(record, artifacts):
    try:
        _keys(record, TOP); _finite_json(record)
        require(_dimension(record['schema_version']) == 1 and record['kind'] == KIND and record['method'] == METHOD and
                record['diagnostic_only'] is True and record['training_certificate_eligible'] is False and
                record['scientific_verdict'] is None, 'basin_unknown_schema_method_or_claim')
        spec, policy, binding = record['specification'], record['geometry_policy'], record['witness_binding']
        _keys(spec, SPEC); _keys(policy, POLICY); _keys(binding, BINDING)
        require(_dimension(spec['schema_version']) == _dimension(policy['schema_version']) == 1 and spec['method_id'] == METHOD,
                'basin_unknown_specification_or_policy')
        for k in ('group_id', 'input_id'): _text(spec[k])
        assigned, channel = _dimension(spec['assigned_input']), _dimension(spec['channel'])
        for k in ('maximum_inputs', 'maximum_samples', 'maximum_total_samples'): _dimension(policy[k])
        require(number(policy['repeatability_absolute']) >= 0 and number(record['minimum_amplitude']) > 0,
                'basin_invalid_geometry_policy')
        begin, end = number(spec['window_begin_offset']), number(spec['window_end_offset'])
        require(0 <= begin < end, 'basin_invalid_declared_window')
        for key in ('group_id', 'assigned_input', 'channel', 'window_begin_offset', 'window_end_offset'):
            _same(record[key], spec[key])
        _dimension(record['assigned_input']); _dimension(record['channel']); _dimension(record['rejected_tampering'])
        require(record['status'] in ('rejected', 'completed', 'causality_rejected') and
                _dimension(record['status_enum']) == {'rejected':0,'completed':1,'causality_rejected':2}[record['status']], 'basin_invalid_status')
        _strings(record['reasons']); require(type(binding['complete_group']) is bool, 'basin_invalid_completeness')
        _same(binding['group_id'], spec['group_id'])
        for k in ('source_pattern_sha256', 'base_model_revision', 'effective_model_revision', 'protocol_revision'): _text(binding[k])
        group_path, group = _reference(binding['group'], artifacts); _keys(group, GROUP_FIELDS)
        require(group_path == 'group.json' and _dimension(group['schema_version']) == 1 and
                group['kind'] == 'native_matched_omission_fixture' and group['method'] == MATCHED_METHOD and group['training_certificate_eligible'] is False and
                group['scientific_verdict'] is None, 'basin_invalid_referenced_group')
        _keys(group['policy'],POLICY_FIELDS)
        for value in group['policy'].values():require(number(value) >= 0,'basin_invalid_referenced_policy')
        for a, b in (('group_id','group_id'), ('source_pattern_sha256','source_pattern_sha256')): _same(group[a], binding[b])
        _same(group['assigned_input'], assigned); _same(group['assigned_channel'], channel)
        require(type(group['packets']) is list and type(group['traces']) is list and
                len(group['packets']) == len(group['traces']) == _dimension(group['native_probes']) > 0, 'basin_group_inventory_changed')
        traces, primary, expected_artifacts = [], {}, {group_path}
        for index, (packet, trace_record) in enumerate(zip(group['packets'], group['traces'])):
            _keys(trace_record, 'path presented_ordinals sha256'); name = _relative_path(trace_record['path'])
            require(name not in primary and name in artifacts, 'basin_missing_or_reused_primary')
            primary[name] = artifacts[name]; expected_artifacts.add(name)
            traces.append(_trace(packet, trace_record, primary[name], group, index, expected_input_id=spec['input_id']))
        first = traces[0]; n = first['n']; require(assigned < n and end <= number(first['packet']['requested_specification']['end']), 'basin_window_or_input_outside_source')
        _maximum_dimensions(group,len(first['times']),n)
        _same(record['minimum_amplitude'], first['spec']['minimum_amplitude'])
        for key in ('base_model_revision','effective_model_revision','protocol_revision'): _same(first['prepared'][key],binding[key])
        if not binding['complete_group']:
            require(binding['portable'] is None and binding['source_specification_sha256'] is None and len(traces) < n+2 and
                    group['reason'] != 'omission_group_closed' and group['assignment_validity'] == 'not_available' and
                    group['maxima'] == group['assignment_reasons'] == [] and group['selected_full_maximum'] is None and
                    record['status'] == 'rejected' and record['reasons'] and record['geometry'] is None and
                    record['geometry_validity'] is None and record['measured_maximum'] is None and record['actual_assigned_onset'] is None,
                    'basin_partial_group_claims_measurement')
            require(set(artifacts) == expected_artifacts, 'basin_unexpected_artifacts')
            return dict(reader_version=1, method=METHOD, complete_group=False, geometry_recomputed=False,
                        partial_rejection_checked=True, primary_traces_checked=len(traces), status='rejected',
                        rejection_reason_recomputed=False,declared_specification=spec,geometry_policy=policy,
                        training_certificate_eligible=False, native_execution_verified=False, causal_lineage_verified=False)
        portable_path, portable = _reference(binding['portable'], artifacts); expected_artifacts.add(portable_path)
        require(portable_path == 'matched-witness.json' and set(artifacts) == expected_artifacts, 'basin_unexpected_artifacts')
        audit_portable_matched_evidence(portable, primary)  # integrity; its assignment is not the new decision
        source = portable['specification']
        require(binding['source_specification_sha256'] == canonical_model_sha256(source), 'basin_source_specification_digest_changed')
        for key in ('group_id','input_id','assigned_input','channel'): _same(source[key],spec[key])
        for key in ('base_model_revision','effective_model_revision','protocol_revision'): _same(source[key],binding[key])
        _same(source['pattern_hash'],binding['source_pattern_sha256']); _same(source['minimum_amplitude'],record['minimum_amplitude'])
        for key in ('reset_binding','model_instance_binding','physical_channel_paths'): _same(group[key],source[key])
        require(group['reason'] == 'omission_group_closed' and len(traces) == n+2, 'basin_complete_group_not_closed')
        for index, item in enumerate(portable['traces']):
            _same(group['packets'][index],item['native_evidence'])
            _same(group['traces'][index],dict(path=item['relative_path'],presented_ordinals=item['presented_ordinals'],sha256=item['sha256']))
        for key in POLICY_FIELDS.split(): _same(group['policy'][key],portable['policy'][key])
        assignment = portable['assignment']
        _same(group['assignment_validity'],assignment['validity']); _same(group['assignment_reasons'],assignment['reasons'])
        _same(group['selected_full_maximum'],assignment['selected_full_maximum'])
        _same(group['maxima'],[{k:v for k,v in peak.items() if not k.startswith('comparison_')} for peak in assignment['maxima']])
        # Native common-context pointwise repeat is separate from the geometry
        # policy and is not inferred from a recognized v1 outcome/reason list.
        native_policy = portable['policy']; repeat = traces[-1]
        for av,bv,ab,bb in zip(first['raws'],repeat['raws'],first['baseline'],repeat['baseline']):
            for x,y in zip(av,bv):
                a,b = number(x-ab),number(y-bb)
                require(number(abs(a-b)) <= number(native_policy['repeatability_absolute']+
                    native_policy['repeatability_relative']*max(abs(a),abs(b))), 'basin_native_full_response_not_repeatable')
        geometry_spec = dict(schema_version=1,input_count=n,assigned_input=assigned,
            window_begin=number(first['spec']['begin']+begin),window_end=number(first['spec']['begin']+end),
            minimum_amplitude=record['minimum_amplitude'])
        shape = lambda t:dict(baseline=t['baseline'][channel],raw=t['raws'][channel])
        geometry = recompute_declared_basin_geometry(geometry_spec,policy,first['times'],shape(first),shape(repeat),
            [(i,shape(t)) for i,t in enumerate(traces[1:-1])])
        onset = first['packet']['observation']['stimuli'][assigned]['time']
        causal = geometry['validity'] == 'valid' and (geometry['measured_maximum']['first_sample'] < first['event_frames'][assigned] or
                                                     geometry['measured_maximum']['time'] < onset)
        if causal:
            require(record['status'] == 'causality_rejected' and record['geometry'] is None and
                    record['geometry_validity'] is None and record['measured_maximum'] is None and record['actual_assigned_onset'] is None,
                    'basin_pre_event_measurement_promoted')
            _same(record['reasons'],['basin_native_selected_peak_precedes_actual_assigned_event'])
        else:
            require(record['status'] == 'completed' and record['reasons'] == [], 'basin_completed_status_changed')
            _geometry_dimensions(record['geometry'],len(first['times']),n)
            _same(record['geometry'],geometry); _same(record['geometry_validity'],geometry['validity'])
            _same(record['measured_maximum'],geometry['measured_maximum']); _same(record['actual_assigned_onset'],onset)
        return dict(reader_version=1,method=METHOD,complete_group=True,geometry_recomputed=True,status=record['status'],
                    geometry_validity=geometry['validity'],measured_maximum=None if causal else geometry['measured_maximum'],
                    primary_traces_checked=len(traces),source_policy_binding_checked=True,native_execution_verified=False,
                    declared_specification=spec,geometry_policy=policy,minimum_amplitude=record['minimum_amplitude'],
                    source_specification_sha256=binding['source_specification_sha256'],
                    causal_lineage_verified=False,training_certificate_eligible=False)
    except EvidenceError: raise
    except (KeyError,TypeError,ValueError,IndexError,AttributeError,UnicodeError,OverflowError,OSError,csv.Error) as error:
        raise EvidenceError('malformed_declared_window_basin_evidence') from error


def audit_declared_window_basin_file(path):
    try: path = Path(path).resolve(); record = load(path); artifacts = {}
    except EvidenceError: raise
    except (OSError,TypeError,ValueError) as error: raise EvidenceError('missing_or_malformed_declared_basin_record') from error
    def capture(name):
        name = _relative_path(name); source = (path.parent/name).resolve()
        require(source.is_relative_to(path.parent), 'basin_artifact_escapes_directory')
        require(name not in artifacts, 'basin_duplicate_artifact_reference'); artifacts[name] = source.read_bytes()
        # The immutable snapshot contains both JSON envelopes and CSV traces.
        # Parse by the declared role; never treat every referenced file as JSON.
        return artifacts[name]
    try:
        group = parse_json_bytes(capture(record['witness_binding']['group']['relative_path']))
        portable = record['witness_binding']['portable']
        if portable is not None: capture(portable['relative_path'])
        for item in group['traces']: capture(item['path'])
        return audit_declared_window_basin_evidence(record,artifacts)
    except EvidenceError: raise
    except (KeyError,TypeError,ValueError,AttributeError,OSError) as error:
        raise EvidenceError('missing_or_malformed_declared_basin_artifacts') from error


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('diagnostic');parser.add_argument('--output')
    args=parser.parse_args();result=audit_declared_window_basin_file(args.diagnostic)
    text=json.dumps(result,indent=2,allow_nan=False)+'\n'
    if args.output:
        output=Path(args.output).resolve();require(not output.is_relative_to(Path(args.diagnostic).resolve().parent),'basin_report_overlaps_primary')
        with output.open('x',encoding='utf-8') as stream:stream.write(text)
    else:print(text,end='')


if __name__=='__main__':main()
