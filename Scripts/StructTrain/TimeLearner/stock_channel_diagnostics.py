"""Matched observer-off/on native probes of the exact two archived candidates."""
from copy import deepcopy
from pathlib import Path
import argparse
import json

from .native_evidence import load, require
from .native_characterization import validate_job
from .native_pipeline_worker import run_job, audit_run_manifest
from .n1_protocol_robustness import _signed, _write
from .stock_wave_replay import prepare, compare_traces


def run(study, runtime, output, *, process_policy=None):
    output = Path(output)
    sources = prepare(study, output)
    rows = []
    for row in sources['rows']:
        off = load(output/'jobs'/(row['name']+'.json'))
        on = deepcopy(off);on.update(schema_version=3, channel_diagnostics=True);on = _signed(on)
        validate_job(on)
        path = output/'jobs'/(row['name']+'-channels.json');_write(path, on)
        rows.append({**row, 'off_job': row['name']+'.json', 'on_job': path.name,
                     'off_sha256': off['sha256'], 'on_sha256': on['sha256']})
    _write(output/'channels-design.json', _signed({
        'kind': 'stock_native_channel_diagnostic_pair', 'schema_version': 1, 'rows': rows,
        'all_jobs_frozen_before_native_operations': True, 'scientific_verdict': None}))
    (output/'runs').mkdir();results = []
    for row in rows:
        for mode in ('off', 'on'):
            folder = output/'runs'/(row['name']+'-'+mode)
            result = run_job('probe', output/'jobs'/row[mode+'_job'], row['source_state'],
                             runtime, folder, 900., process_policy=process_policy)
            require(result['execution'] == 'completed' and result['validity'] == 'valid',
                    'channel_diagnostic_native_probe_incomplete')
            audit_run_manifest(folder/'run-manifest.json')
        off = output/'runs'/(row['name']+'-off')/'native'
        on = output/'runs'/(row['name']+'-on')/'native'
        require(load(off/'initial-state.json')['identity']['sha256'] ==
                load(on/'initial-state.json')['identity']['sha256'] == row['source_model_revision'],
                'channel_diagnostic_actual_candidate_changed')
        comparison = compare_traces(load(off/'probe_trial_1.json'), off/'probe_trial_1.csv',
                                    load(on/'probe_trial_1.json'), on/'probe_trial_1.csv')
        original = compare_traces(load(Path(row['original_packet'])), row['original_trace'],
                                  load(off/'probe_trial_1.json'), off/'probe_trial_1.csv')
        exact = (off/'probe_trial_1.csv').read_bytes() == (on/'probe_trial_1.csv').read_bytes()
        results.append({'name': row['name'], 'observer_off_on': comparison,
                        'observer_off_matches_original': original,
                        'off_on_primary_csv_bytes_equal': exact,
                        'diagnostics': load(on.parent/'run-manifest.json')['analysis']['channel_diagnostics']})
        _write(output/'progress.json', results)
    result = {'kind': 'stock_native_channel_diagnostic_analysis', 'schema_version': 1,
              'rows': results, 'training_started': False, 'scientific_verdict': None}
    _write(output/'analysis.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.study, args.runtime, args.output), indent=2))


if __name__ == '__main__':
    main()
