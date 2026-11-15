"""Readable before/after plots of an audited native C-region intervention."""
import hashlib
import html
import json
from pathlib import Path

from .capacitance_region_evidence import audit_capacitance_region_record, audit_capacitance_region
from .native_evidence import load, parse_json_bytes, require
from .probe_reports import render_probe_set


def render_capacitance_region(source: Path, output: Path):
    source = Path(source).resolve(strict=True)
    output = Path(output)
    # Reject a broken or incomplete intervention before creating any report.
    raw = source.read_bytes()
    record = parse_json_bytes(raw)
    audit = audit_capacitance_region_record(record, source.parent)
    output.mkdir(parents=True, exist_ok=False)
    primary = output/'primary'
    primary.mkdir()
    (primary/'region.json').write_bytes(raw)
    for probe in record['probes']:
        for field in ('record_file', 'trace_file'):
            name = probe[field]
            (primary/name).write_bytes((source.parent/name).read_bytes())
    # The report uses this verified snapshot, never mutable external paths.
    snapshot = load(primary/'region.json')
    snapshot_audit = audit_capacitance_region(primary/'region.json')
    require(snapshot == record and snapshot_audit == audit, 'region_report_primary_changed_during_capture')
    trials = []
    context = []
    for index, probe in enumerate(snapshot['probes']):
        trial_id = probe['packet']['requested_specification']['trial_id']
        trials.append({'trial_id': trial_id, 'packet': 'primary/'+probe['record_file'],
                       'trace': 'primary/'+probe['trace_file']})
        context.append({'trial_id': trial_id, 'phase': probe['phase'], 'input_index': probe['input_index'],
                        'report': f'probes/probe-{index:04d}/index.html'})
    specification = output/'probe-spec.json'
    specification.write_text(json.dumps({'kind': 'timelearner_probe_report_spec', 'schema_version': 1,
                                         'trials': trials}, indent=2)+'\n', encoding='utf-8')
    rendered = render_probe_set(specification, output/'probes')
    require(rendered['trials'] == audit['primary_trials'], 'region_report_incomplete_trial_rendering')
    manifest = {'kind': 'timelearner_capacitance_region_visual_report', 'schema_version': 1,
                'status': 'diagnostic', 'branch': snapshot['branch'], 'normalization': snapshot['normalization'],
                'frequency_hz': snapshot['frequency_hz'], 'region': snapshot['region'], 'scale': snapshot['scale'],
                'primary_audit': snapshot_audit, 'rendered': rendered, 'trial_context': context,
                'comparison_scope': 'all inputs before and after one declared region intervention',
                'visual_acceptance_complete': False, 'scientific_verdict': None}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    links = ''.join('<li><a href="'+item['report']+'">'+html.escape(
        item['phase']+'; input'+str(item['input_index'])+'; '+item['trial_id'])+'</a></li>' for item in context)
    (output/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Native capacitance region intervention</title><h1>Native C-region: before / after</h1>'
        '<p>All recorded soma channels and actual input pulses, at original sample resolution. '
        'Common per-soma Y limits across this entire before/after set; labelled detail views are additional. '
        'Training-burst characterization, not pattern classification or a convergence certificate. '
        'SI units are unverified. Visual acceptance is pending.</p>'
        '<p><a href="probes/index.html">Common-scale probe set</a> · '
        '<a href="primary/region.json">Intervention and effective physical state</a></p><ul>'+links+'</ul></html>\n',
        encoding='utf-8')
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob('*') if p.is_file()}
    (output/'SHA256SUMS.json').write_text(json.dumps(sums, indent=2)+'\n', encoding='utf-8')
    return {'kind': manifest['kind'], 'status': 'diagnostic', 'trials': rendered['trials'],
            'trial_soma_pairs': rendered['trial_soma_pairs'], 'files': len(sums), 'scientific_verdict': None}
