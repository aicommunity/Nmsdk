"""Bind readable figures to complete archived physical-model evaluations.

Preparation rereads production native evidence and the exact primary members.
It starts no model, changes no threshold and does not attest original process
ownership. That authority remains with the explicitly referenced source archive.
The existing scientific renderer consumes the resulting sources.json unchanged.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shutil

from .external_archive import validate_reference
from .native_evidence import load, require
from .native_pipeline_worker import audit_execution
from .publications.plot_algorithm_trials import physical_trial_title
from .runtime import file_record


def _write(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def _identifier(value):
    return type(value) is str and re.fullmatch('[a-z0-9][a-z0-9_-]{0,99}', value) is not None


def validate_plan(plan):
    require(type(plan) is dict and set(plan) == {'kind', 'schema_version', 'cases'} and
            plan['kind'] == 'timelearner_closed_physical_gallery_plan' and
            type(plan['schema_version']) is int and plan['schema_version'] == 1,
            'closed_gallery_plan_schema')
    cases = plan['cases']
    require(type(cases) is list and 0 < len(cases) <= 256, 'closed_gallery_case_count')
    names = set()
    for case in cases:
        require(type(case) is dict and set(case) == {'id', 'scale_group', 'title_mode',
                'native_directory', 'bundle', 'primary', 'primary_member_prefix', 'source_catalog'},
                'closed_gallery_case_schema')
        require(_identifier(case['id']) and case['id'] not in names,
                'closed_gallery_duplicate_or_invalid_case_id')
        names.add(case['id'])
        require(_identifier(case['scale_group']) and case['title_mode'] in ('pattern', 'fourth_time'),
                'closed_gallery_presentation_schema')
        require(type(case['native_directory']) is str and Path(case['native_directory']).is_absolute(),
                'closed_gallery_native_directory_required')
        binding = case['bundle']
        require(type(binding) is dict and set(binding) == {'path', 'size', 'sha256'} and
                type(binding['path']) is str and Path(binding['path']).is_absolute() and
                type(binding['size']) is int and binding['size'] > 0 and
                type(binding['sha256']) is str and re.fullmatch('[0-9a-f]{64}', binding['sha256']),
                'closed_gallery_bundle_binding')
        validate_reference(case['primary'])
        prefix = case['primary_member_prefix']
        require(type(prefix) is str and bool(prefix) and '\\' not in prefix and
                not PurePosixPath(prefix).is_absolute() and
                all(part not in ('', '.', '..') for part in prefix.split('/')),
                'closed_gallery_primary_prefix')
        catalog = case['source_catalog']
        require(type(catalog) is dict and set(catalog) == {'relative_path', 'bytes', 'sha256'} and
                type(catalog['relative_path']) is str and catalog['relative_path'].startswith('experiments/') and
                '\\' not in catalog['relative_path'] and
                all(p not in ('', '.', '..') for p in catalog['relative_path'].split('/')) and
                type(catalog['bytes']) is int and catalog['bytes'] > 0 and
                type(catalog['sha256']) is str and re.fullmatch('[0-9a-f]{64}', catalog['sha256']),
                'closed_gallery_source_catalog_binding')
    return cases


def prepare(plan_path, output):
    """Prepare existing complete trials; retain negative classifications too."""
    plan_path = Path(plan_path).resolve(strict=True)
    plan_record = file_record(plan_path)
    cases = validate_plan(load(plan_path))
    output = Path(output).absolute()
    require(output.parent.resolve(strict=True) == output.parent and
            not output.exists() and not output.is_symlink(), 'closed_gallery_fresh_output_required')
    output.mkdir()
    (output/'primary').mkdir()
    (output/'audits').mkdir()
    records, summaries, frozen = [], [], [(plan_path, plan_record)]
    seen_trials = set()
    for case in cases:
        native = Path(case['native_directory'])
        require(native.resolve(strict=True) == native and native.is_dir(), 'closed_gallery_native_alias')
        bundle_path = Path(case['bundle']['path'])
        require(file_record(bundle_path) == case['bundle'], 'closed_gallery_bundle_changed')
        bundle = load(bundle_path)
        require(bundle.get('archive_sha256') == case['primary']['sha256'] and
                bundle.get('archive_bytes') == case['primary']['bytes'] and
                type(bundle.get('members')) is dict, 'closed_gallery_archive_binding_changed')
        frozen.append((bundle_path, case['bundle']))

        def bound(name):
            path = native/name
            require(path.is_file() and not path.is_symlink(), 'closed_gallery_primary_missing:'+name)
            record = file_record(path)
            member = bundle['members'].get(case['primary_member_prefix']+'/'+name)
            require(member == dict(bytes=record['size'], sha256=record['sha256']),
                    'closed_gallery_primary_member_changed:'+name)
            frozen.append((path, record))
            return path, record

        job_path, _ = bound('job.json')
        bound('execution.json')
        bound('evaluation.json')
        job = load(job_path)
        model = job['source_model_data']
        audit = audit_execution('physical-model-evaluate', native, job, (model,))
        metrics = audit['metrics']
        require(audit['frozen_model_verified'] and metrics['validity'] == 'valid' and
                len(metrics['trials']) == len(job['trials']), 'closed_gallery_incomplete_or_invalid_run')
        _write(output/'audits'/(case['id']+'.json'), audit)
        for row in metrics['trials']:
            index = row['presentation_index']
            source, record = bound('trial-'+str(index)+'.json')
            observation = load(source)
            require(observation['complete'] and not observation['censored'] and
                    observation['trial_id'] == row['trial_id'] and
                    observation['sample_id'] == row['sample_id'] and
                    observation['trial_id'] not in seen_trials, 'closed_gallery_trial_identity_or_completeness')
            seen_trials.add(observation['trial_id'])
            require(len(records) < 256, 'closed_gallery_trial_count_exceeds_renderer_limit')
            title = physical_trial_title(observation)
            if case['title_mode'] == 'fourth_time':
                require(len(observation['relative_stimulus_times']) == 4,
                        'closed_gallery_fourth_title_requires_M4')
                title = ('Четвёртый импульс '+
                         format(observation['relative_stimulus_times'][3]*1000, '.8g')+' мс · '+title)
            name = case['id']+'-'+str(index)+'.json'
            target = output/'primary'/name
            shutil.copyfile(source, target)
            copied = file_record(target)
            require((copied['size'], copied['sha256']) == (record['size'], record['sha256']),
                    'closed_gallery_observation_copy_changed')
            records.append(dict(id=case['id']+'-'+str(index), case_id=case['scale_group'], title=title,
                response=row['classification'], trial_id=row['trial_id'], sample_id=row['sample_id'],
                model_revision=model['model_revision'], primary=case['primary'],
                primary_member=case['primary_member_prefix']+'/'+source.name,
                observation=dict(path='primary/'+name, bytes=record['size'], sha256=record['sha256'])))
        summaries.append(dict(id=case['id'], source_catalog=case['source_catalog'],
            model_revision=model['model_revision'], observations=len(metrics['trials']),
            counts=metrics['pooled_counts'], frozen_model_verified=True))
    require(all(file_record(path) == record for path, record in frozen), 'closed_gallery_source_changed')
    _write(output/'sources.json', dict(kind='timelearner_scientific_trial_figure_sources',
                                      schema_version=1, trials=records))
    result = dict(kind='timelearner_closed_physical_gallery_preparation', schema_version=1,
        plan=plan_record, cases=summaries, observations=len(records),
        all_observations_bound_to_primary_members=True, classifications_from_production_full_window_audit=True,
        source_native_process_ownership_reattested=False, native_experiment_started=False,
        threshold_changed=False, figures_rendered=False, visual_review_complete=False, scientific_verdict=None)
    _write(output/'preparation.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = prepare(args.plan, args.output)
    print(json.dumps(dict(cases=len(result['cases']), observations=result['observations'],
                          figures_rendered=False, scientific_verdict=None)))


if __name__ == '__main__':
    main()
