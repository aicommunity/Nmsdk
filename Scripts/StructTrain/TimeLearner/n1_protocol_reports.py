"""All-condition N1 protocol report using the native temporal report renderer."""
import hashlib
import html
import json
from pathlib import Path

from .calibration_transaction_reports import render_calibration_run
from .n1_protocol_robustness import _inventory, audit_study
from .native_evidence import require
from .plotting import plotting_runtime


def render_study(source, output):
    plotting_runtime()
    source, output = Path(source).resolve(strict=True), Path(output)
    require(not output.exists() and not output.resolve().is_relative_to(source), 'n1_report_requires_separate_new_cache')
    analysis = audit_study(source)
    before = _inventory(source)
    output.mkdir(parents=True)
    rows = []
    for row in analysis['rows']:
        print('RENDER', row['name'], flush=True)
        result = render_calibration_run(source/'runs'/row['name']/'run-manifest.json', output/row['name'])
        rows.append({'name': row['name'], 'phase': row['phase'], 'topology': row['topology'],
                     'duration': row['duration'], 'reset_policy': row['reset_policy'],
                     'condition_fingerprint': row['condition_fingerprint'],
                     'report': row['name']+'/index.html', 'result': result})
    require(before == _inventory(source), 'n1_report_source_changed')
    pairs = sum(row['result']['trial_soma_pairs'] for row in rows)
    manifest = {'kind': 'n1_fixed_protocol_temporal_report', 'schema_version': 1,
                'analysis': analysis, 'rows': rows, 'operations': len(rows), 'trial_soma_pairs': pairs,
                'source_files_unchanged': len(before), 'all_native_samples': True,
                'input_pulses': 'actual-measured-timestamps', 'threshold_retuning': False,
                'independent_patterns': False, 'visual_acceptance_complete': False,
                'scientific_verdict': None}
    (output/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    links = []
    for row, report in zip(analysis['rows'], rows):
        counts = row['metrics']['pooled_counts']
        text = (f"{row['topology']}; {row['phase']}; {row['reset_policy']}; window {row['duration']} s; "
                f"TP {counts['TP']}, FP {counts['FP']}, FN {counts['FN']}, TN {counts['TN']}; "
                f"actual quiet interval {row['actual_quiet_interval_min']:.6g}–{row['actual_quiet_interval_max']:.6g} s")
        links.append('<li><a href="'+html.escape(report['report'], quote=True)+'">'+html.escape(text)+'</a></li>')
    (output/'index.html').write_text('<!doctype html><html lang="ru"><meta charset="utf-8">'
        '<title>N1: порядок, Reset и наблюдаемая пауза</title>'
        '<style>body{font:18px sans-serif;max-width:1100px;margin:2em auto;line-height:1.5}li{margin:1em 0}</style>'
        '<h1>Фиксированные N1-кандидаты: реакции моделей</h1>'
        '<p>Все условия, паттерны и сомы: полные нативные отсчёты мембранного потенциала '
        'с фактическими входными импульсами, overview и читаемые zoom, PNG/SVG/PDF. '
        'Восемь основных условий и две короткие smoke-пробы приведены отдельно.</p>'
        '<p>Пороги выбраны по прежней same-matrix калибровке и не подбираются здесь. '
        'Это не independent Test и не независимые обучения. Удлинение окна одновременно '
        'удлиняет наблюдаемую паузу; изолированный причинный эффект ITI не установлен. '
        'Полнота автоматических проверок не означает завершённую ручную визуальную приёмку.</p>'
        '<ul>'+''.join(links)+'</ul><p><a href="manifest.json">Полные метрики и provenance</a></p></html>\n', encoding='utf-8')
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'SHA256SUMS.json').write_text(json.dumps(sums, indent=2)+'\n', encoding='utf-8')
    return {'kind': manifest['kind'], 'operations': len(rows), 'trial_soma_pairs': pairs,
            'source_files_unchanged': len(before), 'visual_acceptance_complete': False, 'scientific_verdict': None}
