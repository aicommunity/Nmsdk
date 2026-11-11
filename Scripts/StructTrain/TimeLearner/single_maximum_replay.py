"""Replay archived multi-peak single responses with an explicit peak-policy A/B.

Uses immutable Git primary data and the production native pipeline. No Train,
threshold tuning, physics intervention or classification verdict is performed.
"""
import argparse
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

from .native_characterization import audit_execution, validate_job
from .native_evidence import load, require
from .native_pipeline_worker import run_job, audit_run_manifest
from .n1_protocol_robustness import _signed, _write
from .single_pulse_evidence import read_single_pulse
from .stock_feedback_profile import compare_presentations


def _relative(value):
    require(type(value) is str and bool(value) and '\\' not in value and ':' not in value,
            'maximum_replay_invalid_relative_path')
    path=PurePosixPath(value)
    require(value!='.' and not path.is_absolute() and '..' not in path.parts and value==path.as_posix(),
            'maximum_replay_invalid_relative_path')
    return value


def validate_design(design):
    require(type(design) is dict and set(design)=={'kind','schema_version','source','cases'} and
            design['kind']=='timelearner_single_maximum_replay' and type(design['schema_version']) is int and
            design['schema_version']==1, 'maximum_replay_unknown_design')
    source=design['source']
    require(type(source) is dict and set(source)=={'repository','commit','bundle_path','archive_path'} and
            type(source['repository']) is str and Path(source['repository']).is_absolute() and
            type(source['commit']) is str and re.fullmatch('[0-9a-f]{40}',source['commit']),
            'maximum_replay_invalid_source')
    _relative(source['bundle_path']);_relative(source['archive_path'])
    require(type(design['cases']) is list and 1<=len(design['cases'])<=32,'maximum_replay_case_budget')
    ids=set();prefixes=set()
    for case in design['cases']:
        require(type(case) is dict and set(case)=={'id','member_prefix'} and type(case['id']) is str and
                re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]{0,100}',case['id']) and case['id'] not in ids,
                'maximum_replay_invalid_case')
        prefix=_relative(case['member_prefix'])
        require(prefix not in prefixes and not any(prefix.startswith(p+'/') or p.startswith(prefix+'/') for p in prefixes),
                'maximum_replay_overlapping_cases')
        ids.add(case['id']);prefixes.add(prefix)
    return design


def _git_blob(source,path):
    return subprocess.check_output(['git','-C',str(Path(source['repository']).resolve(strict=True)),
                                    'show',source['commit']+':'+path])


def _extract(design,output):
    source=design['source'];bundle=json.loads(_git_blob(source,source['bundle_path']))
    raw=_git_blob(source,source['archive_path'])
    require(len(raw)==bundle['archive_bytes'] and hashlib.sha256(raw).hexdigest()==bundle['archive_sha256'],
            'maximum_replay_archive_mismatch')
    seen=set();total=0;selected={case['id']:0 for case in design['cases']};bindings={}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:xz') as archive:
        for member in archive:
            name=_relative(member.name)
            require(member.isfile() and name not in seen and len(seen)<10000,
                    'maximum_replay_invalid_archive_member')
            total+=member.size
            require(0<=member.size<=64*1024**2 and total<=512*1024**2,'maximum_replay_archive_budget')
            data=archive.extractfile(member).read()
            require(bundle['members'].get(name)=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()},
                    'maximum_replay_member_mismatch')
            seen.add(name)
            for case in design['cases']:
                prefix=case['member_prefix']+'/'
                if name.startswith(prefix):
                    destination=output/case['id']/name[len(prefix):]
                    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
                    selected[case['id']]+=1
                    bindings[destination.relative_to(output).as_posix()]=bundle['members'][name]
    require(seen==set(bundle['members']) and all(selected.values()),'maximum_replay_archive_incomplete')
    return {'commit':source['commit'],'archive_path':source['archive_path'],
            'archive_sha256':bundle['archive_sha256'],'members_verified':len(seen),'selected_members':selected,
            'selected_file_bindings':bindings}


def _verify_source_cache(root,provenance):
    for name,record in provenance['selected_file_bindings'].items():
        path=root/_relative(name)
        require(not path.is_symlink() and path.is_file() and path.stat().st_size==record['bytes'] and
                hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],
                'maximum_replay_source_cache_changed')


def run(design,runtime,output):
    validate_design(design);output=Path(output).resolve();repository=Path(design['source']['repository']).resolve(strict=True)
    require(not output.exists() and not output.is_relative_to(repository) and not repository.is_relative_to(output),
            'maximum_replay_output_overlap_or_exists')
    executable=Path(load(Path(runtime))['executable']['path']).resolve(strict=True)
    require(not output.is_relative_to(executable.parent),'maximum_replay_output_inside_runtime')
    output.mkdir(parents=True);_write(output/'design.json',design)
    (output/'jobs').mkdir();(output/'baseline').mkdir()
    provenance=_extract(design,output/'source');_write(output/'source-provenance.json',provenance)
    rows=[];prepared=[]
    for case in design['cases']:
        original=output/'source'/case['id'];original_native=original/'native'
        audit_execution(original_native)
        job=load(original_native/'job.json');validate_job(job)
        require(job['schema_version']==4 and job['presentation']=={'kind':'single_pulse_characterization'} and
                job['probe']['peak_selection']=='isolated_window','maximum_replay_requires_archived_single_job')
        source_files=list((original/'input/source').glob('*_stopped_state.json'))
        require(len(source_files)==1,'maximum_replay_stopped_source_missing')
        original_packet=load(original_native/'probe_trial_1.json')
        require(original_packet['observation']['complete'] and
                original_packet['observation']['peaks'][0]['candidate_count']>1,
                'maximum_replay_requires_actual_multi_peak_source')
        jobs={}
        for policy in ('isolated_window','single_impulse_maximum'):
            candidate=deepcopy(job);candidate['probe']['trial_id']+='/replay-'+policy
            candidate['probe']['peak_selection']=policy
            if policy=='single_impulse_maximum':candidate['probe']['protocol_revision']+='/single-impulse-maximum-v1'
            candidate.pop('sha256');candidate=_signed(candidate);validate_job(candidate)
            job_path=output/'jobs'/(case['id']+'-'+policy+'.json');_write(job_path,candidate)
            jobs[policy]={'path':str(job_path),'sha256':candidate['sha256']}
        prepared.append({'id':case['id'],'original_native':str(original_native),
                         'source_state':str(source_files[0]),'jobs':jobs})
    _write(output/'frozen-jobs.json',{'cases':prepared,'all_jobs_frozen_before_native_operations':True})
    for case in prepared:
        folders={};original_native=Path(case['original_native'])
        for policy in ('isolated_window','single_impulse_maximum'):
            _verify_source_cache(output/'source',provenance)
            job_path=Path(case['jobs'][policy]['path'])
            require(load(job_path)['sha256']==case['jobs'][policy]['sha256'],'maximum_replay_job_changed')
            folder=output/'runs'/case['id']/policy
            result=run_job('probe',job_path,Path(case['source_state']),runtime,folder,900.)
            require(result['execution']=='completed' and result['validity']=='valid','maximum_replay_incomplete_execution')
            require(audit_run_manifest(folder/'run-manifest.json')['run_evidence_consistent'],
                    'maximum_replay_inconsistent_manifest')
            folders[policy]=folder/'native'
            if policy=='isolated_window':
                baseline=compare_presentations(original_native,folders[policy],True)
                _write(output/'baseline'/ (case['id']+'.json'),baseline)
                require(baseline['exact_waveform_reproduced'],'maximum_replay_original_waveform_changed')
        _verify_source_cache(output/'source',provenance)
        comparison=compare_presentations(folders['isolated_window'],folders['single_impulse_maximum'],True)
        require(comparison['exact_waveform_reproduced'],'maximum_replay_policy_changes_physics')
        before=load(folders['isolated_window']/'probe_trial_1.json')
        after=load(folders['single_impulse_maximum']/'probe_trial_1.json')
        require(before['prepared']['base_model_revision']==after['prepared']['base_model_revision'] and
                before['prepared']['effective_model_revision']==after['prepared']['effective_model_revision'],
                'maximum_replay_model_context_changed')
        observation,spec,_,_,_,quality=read_single_pulse(after,folders['single_impulse_maximum']/'probe_trial_1.csv')
        rows.append({'id':case['id'],'comparison':comparison,'original_baseline':baseline,
                     'old_peak':before['observation']['peaks'][0],'new_peak':observation['peaks'][0],
                     'quality':quality,'physical_input_count':spec['characterization']['physical_input_count'],
                     'selected_input_index':spec['characterization']['selected_input_index']})
        _write(output/'progress.json',{'completed_cases':[r['id'] for r in rows]})
    analysis={'kind':'single_maximum_replay_result','schema_version':1,'rows':rows,'source_provenance':provenance,
              'training_started':False,'training_certificate_created':False,'classification_evaluated':False,
              'whole_burst_assignment_verified':False,'scientific_verdict':None}
    _write(output/'analysis.json',analysis);return analysis


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('design',type=Path)
    parser.add_argument('--runtime',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(run(load(args.design),args.runtime,args.output),indent=2))


if __name__=='__main__':main()
