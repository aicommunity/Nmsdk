"""Temporal soma/input reports bound to an audited, complete C-search history."""
import hashlib
import html
import json
from pathlib import Path

from .learned_evidence import audit_learned_state, load_case as learned_case
from .stopped_evidence import audit_stopped_state, load_case as stopped_case
from .native_evidence import EvidenceError, require
from .probe_reports import render_probe_set


def render_capacitance_search(source: Path, output: Path):
    try:
        return _render_capacitance_search(source, output)
    except EvidenceError:
        raise
    except (KeyError, TypeError, IndexError) as error:
        raise EvidenceError('malformed_capacitance_search_report_primary') from error


def _render_capacitance_search(source: Path, output: Path):
    source = Path(source).resolve(strict=True)
    output = Path(output)
    completed = source.name.endswith('_learned_state.json')
    require(completed or source.name.endswith('_stopped_state.json'), 'unexpected_search_report_filename')
    loader, auditor = (learned_case, audit_learned_state) if completed else (stopped_case, audit_stopped_state)
    original = loader(source)
    audit = auditor(*original)
    package, summary, packets, traces = original
    require(package['schema_version'] == 4, 'search_report_requires_explicit_search_policy')
    require(packets and set(packets) == set(traces), 'search_report_requires_complete_primary_inventory')
    require(all(packet['observation']['complete'] and packet['observation']['valid']
                for packet in packets.values()), 'search_report_incomplete_or_invalid_probe')
    suffix = '_learned_state.json' if completed else '_stopped_state.json'
    stem = source.name.removesuffix(suffix)
    summary_path = source.with_name(stem + ('_learned_summary.json' if completed else '_stopped_summary.json'))
    # Filenames come from the native loader, never from user-controlled manifest paths.
    names = {source.name, summary_path.name}
    for trace in traces.values():
        require(trace.parent.resolve() == source.parent, 'search_report_external_primary_path')
        names.update((trace.name, trace.with_suffix('.json').name))
    captured = {name: (source.parent/name).read_bytes() for name in sorted(names)}
    output.mkdir(parents=True, exist_ok=False)
    primary = output/'primary'
    primary.mkdir()
    for name, data in captured.items():
        (primary/name).write_bytes(data)
    snapshot = loader(primary/source.name)
    require(snapshot[:3] == original[:3] and auditor(*snapshot) == audit,
            'search_report_primary_changed_during_capture')
    package, summary, packets, traces = snapshot
    history = package['capacitance_history']
    references = {p['requested_specification']['trial_id'] for p in package['reference_packets']}
    finals = {p['requested_specification']['trial_id'] for p in package['final_packets']}
    candidates = {c['trial_id'] for c in summary['candidates']}
    anchors = {c['anchor_trial_id'] for c in summary['candidates'] if c.get('anchor_trial_id')}
    trials, contexts = [], []
    for index, (trial_id, packet) in enumerate(packets.items()):
        phase = ('reference' if trial_id in references else 'final verification' if trial_id in finals
                 else 'candidate' if trial_id in candidates else 'candidate anchor' if trial_id in anchors
                 else 'search probe')
        witness_id = history['trial_witness_ids'][trial_id]
        witness = history['witnesses'][witness_id]
        trial = {'trial_id': trial_id, 'packet': 'primary/'+traces[trial_id].with_suffix('.json').name,
                 'trace': 'primary/'+traces[trial_id].name}
        trials.append(trial)
        contexts.append({'trial_id': trial_id, 'phase': phase,
                         'inputs': [peak['input_id'] for peak in packet['observation']['peaks']],
                         'model_revision': packet['current_base_revision'], 'witness_id': witness_id,
                         'membrane_scales': witness['controller_parameters']['membrane_scales'],
                         'report': f'probes/probe-{index:04d}/index.html'})
    spec = output/'probe-spec.json'
    spec.write_text(json.dumps({'kind': 'timelearner_probe_report_spec', 'schema_version': 1,
                               'trials': trials}, indent=2)+'\n', encoding='utf-8')
    rendered = render_probe_set(spec, output/'probes')
    require(rendered['trials'] == len(packets), 'search_report_incomplete_trial_rendering')
    manifest = {'kind': 'timelearner_capacitance_search_visual_report', 'schema_version': 1,
                'status': 'diagnostic', 'training_outcome': package['training_outcome'],
                'capacitance_search': package['configuration']['capacitance_search'],
                'primary_audit': audit, 'rendered': rendered, 'trial_context': contexts,
                'primary_sha256': {n: hashlib.sha256(v).hexdigest() for n, v in captured.items()},
                'visual_acceptance_complete': False, 'scientific_verdict': None}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    links = ''.join('<li><a href="'+c['report']+'">'+html.escape(
        c['phase']+'; '+', '.join(c['inputs'])+'; '+c['trial_id'])+'</a><pre>'+
        html.escape(json.dumps(c['membrane_scales'], sort_keys=True))+'</pre></li>' for c in contexts)
    (output/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<title>Native capacitance search</title><h1>Native C-search: all observed trials</h1>'
        '<p>All soma channels and actual stimulus timestamps at original sample resolution. '
        'Shared per-soma Y scales cover the full set; additional detail views are labelled. '
        'Each trial is bound to its physical C witness and model revision in manifest.json. '
        'These training-burst probes are not an all-pattern classification test. '
        'SI units are unverified. Visual acceptance is pending.</p>'
        '<p><a href="probes/index.html">Common-scale probe set</a></p><ul>'+links+'</ul></html>\n',
        encoding='utf-8')
    sums = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob('*') if p.is_file()}
    (output/'SHA256SUMS.json').write_text(json.dumps(sums, indent=2)+'\n', encoding='utf-8')
    return {'kind': manifest['kind'], 'status': 'diagnostic', 'trials': rendered['trials'],
            'trial_soma_pairs': rendered['trial_soma_pairs'], 'files': len(sums), 'scientific_verdict': None}
