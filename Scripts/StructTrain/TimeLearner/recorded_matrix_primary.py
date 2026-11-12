"""Compact, lossless scientific DATA subset of an audited recorded matrix.

Actual recognition models embed their complete stopped source and primary
training archive. Preserve those models, summaries and every new observation;
omit duplicate jobs/source copies and reproducible figures. This subset is not
the original runtime directory and must never pass as its full artifact closure.
"""
from pathlib import Path
import argparse
import html
import json
import tempfile

from .collector_provenance import frozen_digest
from .native_evidence import load, require
from .recorded_diagnostic_matrix import audit_closed_execution, audit_matrix
from .portable_primary import create_native_bundle, restore_native_bundle


HEADER = ('terminal.json', 'source-before.json', 'source-after.json', 'tool-before.json', 'tool-after.json')
CONTROLLER = ('request.json', 'supervisor-result.json', 'outer-closure.json',
              'original-outcome.json', 'reservation-final.json')
CASE_FILES = ('run-manifest.json', 'process/contained/owned-unit.json',
              'input/source/train_stopped_summary.json', 'native/model.json',
              'native/execution.json', 'native/evaluation.json') + tuple(f'native/trial-{i}.json' for i in range(8))


def _paths(request):
    return {'runtime/runtime.json', 'matrix/parameters.xml', 'matrix/observations.csv'} | {
        'native/'+n for n in HEADER} | {'controller/'+n for n in CONTROLLER} | {
        'native/'+r['name']+'/'+n for r in request['cases'] for n in CASE_FILES}


def create_primary(directory, controller, runtime_manifest, output):
    """Export selected original bytes only after the full production audit."""
    directory, controller = Path(directory).resolve(strict=True), Path(controller).resolve(strict=True)
    runtime_manifest = Path(runtime_manifest).resolve(strict=True);output = Path(output).resolve()
    require(not output.exists() and all(not output.is_relative_to(p) and not p.is_relative_to(output)
            for p in (directory, controller, runtime_manifest.parent)), 'recorded_primary_output_overlaps_source')
    audit_matrix(directory, controller, runtime_manifest)
    request = load(controller/'request.json');matrix = request['matrix']
    sources = {'runtime/runtime.json': runtime_manifest,
               'matrix/parameters.xml': directory/'native-inputs'/matrix['parameters_name'],
               'matrix/observations.csv': directory/'native-inputs'/matrix['observations_name']}
    sources.update({'native/'+n: directory/n for n in HEADER})
    sources.update({'controller/'+n: controller/n for n in CONTROLLER})
    sources.update({'native/'+r['name']+'/'+n: directory/r['name']/n
                    for r in request['cases'] for n in CASE_FILES})
    require(set(sources) == _paths(request), 'recorded_primary_selection_changed')
    records = {n: {k: v for k, v in frozen_digest(p, 256*1024**2).items() if k != 'source_path'}
               for n, p in sources.items()}
    selection = dict(kind='timelearner_compact_recorded_matrix', schema_version=1,
        original_job_id=request['job_id'], files=records, complete_runtime_directory=False,
        diagnostic_only=True, native_execution_attested=False, scientific_verdict=None)
    with tempfile.TemporaryDirectory(prefix='matrix-selection-', dir=output.parent) as temporary:
        index = Path(temporary)/'selection.json'
        index.write_text(json.dumps(selection, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        sources['selection.json'] = index
        bundle = create_native_bundle(sources, output, dictionary_bytes=32*1024**2)
    require({n: r for n, r in bundle['members'].items() if n != 'selection.json'} == records,
            'recorded_primary_source_changed')
    return bundle


def audit_primary(bundle_path, restored):
    """Restore and rescore all primary observations through the sole scorer."""
    from .native_calibration_worker import _digest
    from .phasea_matrix import extract, trial_design
    from .recognition_metrics import load_diagnostic_evaluation, score_diagnostic_recognition_evaluation

    bundle_path = Path(bundle_path).resolve(strict=True);restored = Path(restored).resolve()
    require(not restored.is_relative_to(bundle_path.parent) and
            not bundle_path.parent.is_relative_to(restored), 'recorded_primary_restore_overlaps_bundle')
    declaration = load(bundle_path)
    require(type(declaration.get('archive_bytes')) is int and 0 < declaration['archive_bytes'] <= 128*1024**2
            and type(declaration.get('members')) is dict and 0 < len(declaration['members']) <= 64
            and type(declaration.get('expanded_bytes')) is int
            and 0 < declaration['expanded_bytes'] <= 768*1024**2, 'recorded_primary_size_budget')
    require(all(type(r) is dict and type(r.get('bytes')) is int and 0 <= r['bytes'] <= 256*1024**2
                for r in declaration['members'].values()) and
            sum(r['bytes'] for r in declaration['members'].values()) == declaration['expanded_bytes'],
            'recorded_primary_member_budget')
    restore_native_bundle(bundle_path, restored)
    restored = Path(restored);selection = load(restored/'selection.json')
    require(set(selection) == {'kind', 'schema_version', 'original_job_id', 'files',
        'complete_runtime_directory', 'diagnostic_only', 'native_execution_attested', 'scientific_verdict'}
        and selection['kind'] == 'timelearner_compact_recorded_matrix'
        and type(selection['schema_version']) is int and selection['schema_version'] == 1
        and selection['complete_runtime_directory'] is False and selection['diagnostic_only'] is True
        and selection['native_execution_attested'] is False and selection['scientific_verdict'] is None,
        'recorded_primary_selection_schema')
    request, runtime = audit_closed_execution(restored/'native', restored/'controller', restored/'runtime/runtime.json')
    require(selection['original_job_id'] == request['job_id'] and set(selection['files']) == _paths(request)
            and selection['files'] == {n: r for n, r in declaration['members'].items() if n != 'selection.json'},
            'recorded_primary_inventory_changed')
    matrix = extract((restored/'matrix/parameters.xml').read_bytes(),
                     (restored/'matrix/observations.csv').read_bytes(), request['matrix']['revision'])
    rows = []
    for case in request['cases']:
        prefix = 'native/'+case['name']+'/';root = restored/prefix
        manifest = load(root/'run-manifest.json');_digest(manifest)
        require(manifest['operation'] == 'diagnostic-evaluate' and manifest['execution'] == 'completed'
                and manifest['validity'] == 'valid' and manifest['runtime_fingerprint'] == runtime['runtime_fingerprint']
                and manifest['source_closure'] == runtime['source_closure'], 'recorded_primary_original_case_changed')
        original = {r['path']: {k: r[k] for k in ('bytes', 'sha256')} for r in manifest['artifacts']}
        for name in CASE_FILES:
            if name not in ('run-manifest.json', 'process/contained/owned-unit.json'):
                require(original.get(name) == selection['files'][prefix+name], 'recorded_primary_unbound_case_file')
        require(original['native/model.json'] == original['native/model-after.json'] and
                manifest['analysis']['frozen_model_verified'] is True, 'recorded_primary_model_was_not_frozen')
        model = load(root/'native/model.json');source = model['source_solo']
        summary = load(root/'input/source/train_stopped_summary.json')
        spec, observations = load_diagnostic_evaluation(root/'native/evaluation.json')
        wanted = trial_design(matrix, source['configuration']['model']['initial_isi'],
                              case['name']+'/stopped-phasea-diagnostic', duration=2., rotations=1)
        require(len(observations) == len(wanted) == 8 and all(o['complete'] for o in observations),
                'recorded_primary_incomplete_observations')
        by_id = {o['trial_id']: o for o in observations}
        require(set(by_id) == {t['trial_id'] for t in wanted} and all(
            all(by_id[t['trial_id']][k] == t[k] for k in
                ('run_id', 'sample_id', 'label', 'pattern_hash', 'pattern_isi', 'reset_policy')) for t in wanted),
            'recorded_primary_wrong_matrix')
        metrics = score_diagnostic_recognition_evaluation(spec, observations, model, (source, summary, {}, {}))
        require(metrics == manifest['analysis']['metrics'] and metrics['validity'] == 'valid'
                and metrics['evaluation_verdict'] is None, 'recorded_primary_rescore_changed')
        rows.append(dict(name=case['name'], trials=8, model_revision=model['model_revision'],
                         training_outcome=source['training_outcome'], counts=metrics['pooled_counts']))
    return dict(kind='timelearner_compact_recorded_matrix_readback', schema_version=1,
        original_job_id=request['job_id'], models=rows, trials=8*len(rows), diagnostic_only=True,
        complete_runtime_directory=False, native_execution_attested=False, scientific_verdict=None)


def report_primary(bundle_path, restored, output):
    """Restore, audit and render every recorded pattern from the compact bundle.

    The restored subset is never presented as the original runtime directory.
    Reports use the production diagnostic renderer and retain its lack of a
    scientific verdict and its explicit visual-review status.
    """
    from .plotting import plotting_runtime

    bundle_path = Path(bundle_path).resolve(strict=True)
    restored, output = Path(restored).resolve(), Path(output).resolve()
    protected = (bundle_path.parent, restored)
    require(not output.exists() and all(not output.is_relative_to(p) and
            not p.is_relative_to(output) for p in protected),
            'recorded_primary_report_overlaps_primary')
    plotting_runtime()  # Reject an unavailable renderer before decompression.
    from .reports import render_diagnostic_evaluation_case
    analysis = audit_primary(bundle_path, restored)
    output.mkdir(parents=True)
    reports = []
    for row in analysis['models']:
        root = restored/'native'/row['name']
        model = load(root/'native/model.json')
        summary = load(root/'input/source/train_stopped_summary.json')
        result = render_diagnostic_evaluation_case(root/'native/evaluation.json',
            root/'native/model.json', (model['source_solo'], summary, {}, {}), output/row['name'])
        reports.append(dict(name=row['name'], report=result))
    result = dict(analysis=analysis, reports=reports, visual_acceptance_complete=False,
                  native_execution_attested=False, scientific_verdict=None)
    (output/'manifest.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    links = ''.join('<li><a href="'+html.escape(r['name'])+'/index.html">'+html.escape(r['name'])+'</a></li>'
                    for r in reports)
    (output/'index.html').write_text('<!doctype html><meta charset="utf-8">'
        '<h1>Recorded diagnostic responses from compact primary data</h1>'
        '<p>Stopped models; inherited fixed thresholds. All declared patterns with actual input overlays. '
        'No convergence, calibration or independent scientific verdict is inferred.</p><ul>'+links+'</ul>',
        encoding='utf-8')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    create = commands.add_parser('create')
    for name in ('directory', 'controller', 'runtime_manifest'):create.add_argument(name, type=Path)
    audit = commands.add_parser('audit');audit.add_argument('bundle', type=Path)
    report = commands.add_parser('report');report.add_argument('bundle', type=Path)
    report.add_argument('--restored', required=True, type=Path)
    for command in (create, audit, report):command.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    if args.action == 'create':
        result = create_primary(args.directory, args.controller, args.runtime_manifest, args.output)
    elif args.action == 'audit':result = audit_primary(args.bundle, args.output)
    else:result = report_primary(args.bundle, args.restored, args.output)
    print(json.dumps(result, allow_nan=False));return 0


if __name__ == '__main__':
    raise SystemExit(main())
