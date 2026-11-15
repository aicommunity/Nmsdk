"""Compare recorded and full observation windows without changing Train state.

The complete package and external CSVs are audited first. A wider diagnostic
window is post-hoc analysis, never a new training measurement or certificate.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

from .composite_package_evidence import audit_composite_package
from .composite_primary import filesystem_primary_resolver
from .declared_window_basin_evidence import recompute_declared_basin_geometry
from .native_evidence import count, load, number, require


def replay(native, group_numbers):
    native = Path(native).resolve(strict=True)
    package_path = native/'train_stopped_state.json'
    summary_path = native/'train_stopped_summary.json'
    raw_package, raw_summary = package_path.read_bytes(), summary_path.read_bytes()
    package, summary = load(package_path), load(summary_path)
    version = count(package['schema_version'])
    require(version in (6, 7), 'window_replay_requires_candidate_window_package')
    resolver = filesystem_primary_resolver(native)
    audit = audit_composite_package(package, summary, external_resolver=resolver)
    records = package['measurement_archive']['records']
    require(type(group_numbers) is list and group_numbers and
            all(type(i) is int and 0 < i <= len(records) for i in group_numbers) and
            len(set(group_numbers)) == len(group_numbers), 'window_replay_group_inventory')
    groups = []
    for ordinal in group_numbers:
        record = records[ordinal-1]
        method = record['method_specification']; channel = count(method['channel'])
        n = count(record['raw_trials'][0]['actual_specification']['stimulus_subset']['physical_input_count'])
        full, omissions, references, shared_offsets = [], {}, [], None
        for trial in record['raw_trials']:
            ref = trial['primary_ref']; raw = resolver(ref['relative_path'])
            require(len(raw) == ref['bytes'] and hashlib.sha256(raw).hexdigest() == ref['sha256'],
                    'window_replay_primary_changed_after_audit')
            spec = trial['actual_specification']
            rows = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
            values = [[number(float(v)) for v in row] for row in rows[1:]]
            offsets = [v[0]-number(spec['begin']) for v in values]
            if shared_offsets is None:
                shared_offsets = offsets
            require(len(offsets) == len(shared_offsets) and
                    all(abs(a-b) <= 1e-10 for a, b in zip(offsets, shared_offsets)),
                    'window_replay_control_grid_changed')
            missing = set(range(n))-set(spec['stimulus_subset']['source_ordinals'])
            trace = dict(raw=[v[channel+2] for v in values], baseline=spec['baseline'][channel])
            if not missing:
                full.append((values, trace))
            else:
                require(len(missing) == 1 and next(iter(missing)) not in omissions,
                        'window_replay_omission_inventory_changed')
                omissions[next(iter(missing))] = trace
            references.append(ref)
        require(len(full) == 2 and set(omissions) == set(range(n)),
                'window_replay_requires_two_full_and_every_omission')
        times = [v[0] for v in full[0][0]]
        frame = method['candidate_frame']
        first, last = count(frame['first_frame']), count(frame['last_frame'])
        require(0 <= first < last < len(times),
                'window_replay_candidate_frame_invalid')
        windows = [('recorded', times[first], times[last]),
                   ('full_observation', times[0], times[-1])]
        results = []
        for name, begin, end in windows:
            specification = dict(schema_version=1, input_count=n,
                assigned_input=method['assigned_input'], window_begin=begin, window_end=end,
                minimum_amplitude=record['native_group']['specification']['minimum_amplitude'])
            geometry = recompute_declared_basin_geometry(specification, record['geometry_policy'],
                times, full[0][1], full[1][1], sorted(omissions.items()))
            results.append(dict(window=name, begin=begin, end=end, geometry=geometry))
        require(results[0]['geometry']['validity'] == record['selection']['geometry']['validity'],
                'window_replay_recorded_decision_mismatch')
        groups.append(dict(ordinal=ordinal, group_id=record['group_id'],
            original_selection=record['selection'], windows=results, primary_references=references))
    require(raw_package == package_path.read_bytes() and raw_summary == summary_path.read_bytes(),
            'window_replay_package_changed')
    return dict(kind='timelearner_candidate_window_diagnostic_replay', schema_version=1,
        package_sha256=hashlib.sha256(raw_package).hexdigest(),
        summary_sha256=hashlib.sha256(raw_summary).hexdigest(), package_audit=audit,
        groups=groups, posthoc_windows=True, original_state_rewritten=False,
        original_training_outcome=audit['training_outcome'], new_model_execution=False,
        training_certificate_eligible=False, scientific_verdict=None)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--groups', type=int, nargs='+', required=True)
    args = parser.parse_args(argv)
    require(not args.output.exists(), 'window_replay_output_exists')
    result = replay(args.native, args.groups)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False); stream.write('\n')


if __name__ == '__main__':
    main()
