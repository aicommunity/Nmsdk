"""All recorded frozen-order responses through the common diagnostic renderer."""
from collections import Counter
from pathlib import Path
import html

from .native_calibration_worker import _write
from .native_evidence import load, require
from .native_pipeline_worker import audit_run_manifest
from .reports import render_diagnostic_evaluation
from .runtime import file_record


def render_frozen_order(source: Path, output: Path):
    source = source.resolve(strict=True)
    output = output.resolve()
    require(not output.exists() and not output.is_relative_to(source) and
            not source.is_relative_to(output), 'frozen_order_report_output_overlaps_source')
    result = load(source/'result.json')
    require(result['kind'] == 'frozen_stopped_order_native_result' and
            result['schema_version'] == 1 and not result['training_completed'] and
            not result['independent_evaluation'] and result['scientific_verdict'] is None,
            'frozen_order_report_requires_completed_diagnostic')
    phases = result['actual_results']
    require([p['name'] for p in phases] == ['baseline', 'study'],
            'frozen_order_report_phase_set_changed')
    rotations = [r for phase in phases for r in phase['rotations']]
    size = len(rotations)
    require(size > 1 and result['expected_trials'] == size*size and
            sorted(r['rotation'] for r in rotations) == list(range(size)) and
            sorted(r['target_position'] for r in rotations) == list(range(size)),
            'frozen_order_report_rotation_design_incomplete')
    before = {'result.json': file_record(source/'result.json')}
    for phase in phases:
        folder = source/'runs'/phase['name']
        manifest_path = folder/'run-manifest.json'
        require(audit_run_manifest(manifest_path)['run_evidence_consistent'],
                'frozen_order_report_run_audit_failed')
        manifest = load(manifest_path)
        require(manifest['execution'] == 'completed' and manifest['validity'] == 'valid' and
                manifest['analysis']['metrics'] == phase['metrics'] and
                phase['metrics']['model_revision'] == result['model_revision'] and
                phase['metrics']['effective_threshold'] == result['threshold'],
                'frozen_order_report_metrics_or_model_changed')
        rows = [row for rotation in phase['rotations'] for row in rotation['trials']]
        require(len(rows) == len(phase['metrics']['trials']) and
                {r['trial_id']: r for r in rows} ==
                {r['trial_id']: r for r in phase['metrics']['trials']} and
                len({r['trial_id'] for r in rows}) == len(rows),
                'frozen_order_report_rotation_trials_changed')
        for rotation in phase['rotations']:
            counts = Counter(r['classification'] for r in rotation['trials'])
            require(len(rotation['trials']) == size and
                    {k: counts[k] for k in ('TP', 'FP', 'FN', 'TN')} == rotation['counts'] and
                    counts['TP']+counts['FN'] == 1 and counts['FP']+counts['TN'] == size-1,
                    'frozen_order_report_rotation_counts_changed')
        for name in ('run-manifest.json', 'native/model.json',
                     'input/source/train_stopped_state.json'):
            before[phase['name']+'/'+name] = file_record(folder/name)
    output.mkdir()
    rendered = []
    for phase in phases:
        name = phase['name']; folder = source/'runs'/name
        render_diagnostic_evaluation(folder/'native/evaluation.json', folder/'native/model.json',
            folder/'input/source/train_stopped_state.json', output/name)
        report = load(output/name/'manifest.json')
        decisions = load(output/name/'lt-decision-views.json')
        require(load(output/name/'analysis.json') == phase['metrics'] and
                not report['missing_observation_ids'] and
                decisions['all_declared_trials_rendered'] and decisions['all_observations_complete'],
                'frozen_order_report_missing_or_changed_observations')
        require({f['trial_id'] for f in report['figures']} ==
                {t['trial_id'] for t in phase['metrics']['trials']},
                'frozen_order_report_missing_soma_trial')
        rendered.append(dict(name=name, trials=len(phase['metrics']['trials']),
            soma_pairs=len(report['figures']), lt_trials=len(decisions['trials'])))
    for name, record in before.items():
        path = source/name if name == 'result.json' else source/'runs'/name
        require(file_record(path) == record, 'frozen_order_report_source_changed')
    summary = dict(kind='frozen_stopped_order_temporal_report', schema_version=1,
        model_revision=result['model_revision'], threshold=result['threshold'],
        expected_trials=result['expected_trials'], phases=rendered,
        rotations=rotations, source_records=before,
        all_patterns_at_all_positions_rendered=True, new_native_calculation=False,
        threshold_selected=False, training_completed=False, independent_evaluation=False,
        visual_acceptance_complete=False, scientific_verdict=None)
    _write(output/'manifest.json', summary)
    rows = ''.join('<tr><td>'+str(r['rotation'])+'</td><td>'+str(r['target_position'])+
        '</td>'+''.join('<td>'+str(r['counts'][k])+'</td>' for k in ('TP','FP','FN','TN'))+
        '</tr>' for r in sorted(rotations, key=lambda r: r['rotation']))
    links = ''.join('<li><a href="'+html.escape(p['name'])+'/index.html">'+
        html.escape(p['name'])+': '+str(p['trials'])+' recorded trials</a></li>' for p in rendered)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8">'
        '<h1>Frozen-model order study: every recorded pattern</h1>'
        '<p>Fixed model and threshold. Reset per trial; no retraining, retuning or '
        'independent data partition. Common native Soma/LT plots include actual input '
        'and spike times, full recovery ranges and readable native zooms. '
        'Visual acceptance remains separate.</p><ul>'+links+'</ul>'
        '<table><tr><th>Rotation</th><th>Target position (0-based)</th>'
        '<th>TP</th><th>FP</th><th>FN</th><th>TN</th></tr>'+rows+'</table>', encoding='utf-8')
    return summary
