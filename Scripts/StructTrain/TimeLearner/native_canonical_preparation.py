"""Canonical DATA only, under the existing owned Python job.

The SDK, build and native controller are never written. An isolated child runs
this maintained Tool file as __main__, then imports only SDK Scripts. No generated
program, source update, build, native test, model or new ownership loop is used.
"""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASES = {Path('/home/user/timelearner-refactor'),Path('/media/user/Data/TimeLearnerRefactor')}
MODULES = ('native_acceptance_worker','native_preparation','collector_provenance','runtime',
           'native_gate','contained_process','resource_reservations','validation')


def _api():
    # Delayed: file-mode child installs SDK sys.path before any Scripts import.
    from Scripts.StructTrain.TimeLearner import collector_provenance, native_evidence, runtime
    return collector_provenance, native_evidence.require, runtime


def _hash(raw):return hashlib.sha256(raw).hexdigest()


def _keys(value, fields, reason):
    _, require, _ = _api()
    require(type(value) is dict and set(value)==set(fields.split()),reason)


def _path(value, *, exists=True):
    provenance, require, _ = _api()
    require(type(value) is str and Path(value).is_absolute(),'canonical_absolute_path_required')
    return provenance._canonical(Path(value),exists=exists)


def _binding(value):
    provenance, require, _ = _api()
    _keys(value,'path sha256','canonical_file_binding')
    require(type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['sha256']),
            'canonical_file_digest')
    path=_path(value['path']);raw,record=provenance._frozen(path,32*1024**2)
    require(_hash(raw)==value['sha256'],'canonical_input_changed:'+str(path))
    return provenance._json(raw),raw,record


def _git(root,*arguments):
    return subprocess.check_output(['git','-C',str(root),*arguments],
        env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0'))


def validate_plan(plan):
    _, require, _ = _api()
    _keys(plan,'kind schema_version workspace source cohort native_job prior_bindings external_output native_tool require_fresh_build',
          'canonical_plan_schema')
    require(plan['kind']=='timelearner_native_canonical_preparation' and
            type(plan['schema_version']) is int and plan['schema_version']==1 and
            plan['require_fresh_build'] is True,'canonical_plan_version_or_build_policy')
    base=_path(plan['workspace']);require(base in BASES,'canonical_workspace')
    _keys(plan['source'],'path commit namespace','canonical_source_schema')
    _keys(plan['native_tool'],'path commit','canonical_native_tool_schema')
    source=_path(plan['source']['path']);tool=_path(plan['native_tool']['path'])
    for row in (plan['source'],plan['native_tool']):
        require(type(row['commit']) is str and re.fullmatch('[0-9a-f]{40}',row['commit']),
                'canonical_full_commit_required')
    namespace,_,_=_binding(plan['source']['namespace']);cohort,_,_=_binding(plan['cohort'])
    job,jobraw,_=_binding(plan['native_job'])
    _keys(cohort,'selections selected_ids runplan partitions','canonical_cohort_schema')
    require(type(namespace) is dict and namespace,'canonical_source_namespace_missing')
    for relative,row in namespace.items():
        require(type(relative) is str and relative and not PurePosixPath(relative).is_absolute() and
                all(p not in ('','..','.') for p in relative.split('/')) and '\\' not in relative,
                'canonical_source_namespace_path')
        _keys(row,'git_mode git_blob bytes sha256','canonical_source_namespace_row')
        require(row['git_mode'] in ('100644','100755') and type(row['bytes']) is int and
                row['bytes']>=0 and type(row['git_blob']) is str and
                re.fullmatch('[0-9a-f]{40}',row['git_blob']) and type(row['sha256']) is str and
                re.fullmatch('[0-9a-f]{64}',row['sha256']),'canonical_source_namespace_row')
    require(type(plan['prior_bindings']) is list,'canonical_prior_bindings_schema')
    prior=[]
    for binding in plan['prior_bindings']:
        value,raw,_=_binding(binding);prior.append((binding['path'],value,raw))
    output=_path(plan['external_output'],exists=False)
    require(not output.exists() and output.is_relative_to(base/'readbacks'),'canonical_new_external_output')
    from Scripts.StructTrain.TimeLearner.native_acceptance_worker import validate_job_paths
    workspace,paths,protected,configure=validate_job_paths(job)
    require(workspace==base and paths['source']==source and not paths['build'].exists(),
            'canonical_source_or_fresh_build')
    controller=base/'readbacks'/(paths['output'].name+'-controller')
    require(job['preparation']==str(controller/'inputs/preparation.json') and not controller.exists(),
            'canonical_internal_copy_layout')
    reads=[source,tool,*[Path(v['path']).parent for v in (plan['cohort'],plan['native_job'],plan['source']['namespace'])],
           *[Path(v['path']).parent for v in plan['prior_bindings']],paths['resources'],paths['framework'],*protected]
    require(all(p.is_relative_to(base) for p in reads) and all(not(output==p or output.is_relative_to(p) or p.is_relative_to(output)) for p in reads),
            'canonical_input_output_overlap')
    return {'base':base,'source':source,'tool':tool,'namespace':namespace,'cohort':cohort,
            'job':job,'jobraw':jobraw,'paths':paths,'protected':protected,'configure':configure,
            'controller':controller,'output':output,'reads':reads,'prior':prior}


def resources(plan, job_directory, plan_path):
    state=validate_plan(plan)
    plan_parent=_path(str(Path(plan_path).parent))
    _,require,_=_api();require(plan_parent.is_relative_to(state['base']),'canonical_plan_outside_workspace')
    # All these scopes are read-only and already explicitly declared. A prior
    # binding's directory needs no second lease row when a protected original
    # output already covers it. Never introduce a new common ancestor or fold
    # write scopes into this reduction; the registry's 64-row cap stays intact.
    reads=set([ROOT,plan_parent,*state['reads']])
    reads=sorted((p for p in reads if not any(p!=q and p.is_relative_to(q) for q in reads)),key=str)
    rows=[{'path':str(p),'access':'read'} for p in reads]+[
        {'path':str(state['output']),'access':'write'},{'path':str(job_directory),'access':'write'}]
    return list({(r['path'],r['access']):r for r in rows}.values())


def capture_inputs(plan, plan_path, plan_digest):
    """Re-freeze original control bytes, including a separately stored plan."""
    provenance,require,_=_api();raw,_=provenance._frozen(Path(plan_path),1024**2)
    require(_hash(raw)==plan_digest and provenance._json(raw)==plan,'canonical_plan_changed')
    records={str(plan_path):_hash(raw)}
    for binding in [plan['source']['namespace'],plan['cohort'],plan['native_job'],*plan['prior_bindings']]:
        _,raw,_=_binding(binding);records[binding['path']]=_hash(raw)
    return records


def verify_namespace(source, expected):
    """Data-first independent check; never instantiate/fake a native Worker."""
    provenance,require,runtime=_api();source=Path(source)
    closure=runtime.source_closure(source);roots={k:source/(k if k!='root' else '') for k in closure}
    physical=set()
    for folder,dirs,files in os.walk(source,followlinks=False):
        dirs[:]=[x for x in dirs if x!='.git']
        for name in files:
            if name!='.git':physical.add((Path(folder)/name).relative_to(source).as_posix())
        for name in list(dirs):
            path=Path(folder)/name
            if path.is_symlink():physical.add(path.relative_to(source).as_posix());dirs.remove(name)
    require(physical==set(expected),'canonical_source_projection_changed')
    git_entries={}
    for key,directory in roots.items():
        mapping={}
        for entry in _git(directory,'ls-tree','-r','-z',closure[key]['head']).split(b'\0'):
            if entry:
                header,name=entry.split(b'\t',1);mode,kind,oid=header.decode().split()
                if kind=='blob':mapping[name.decode('utf-8')]=(mode,oid)
        git_entries[key]=mapping
    actual={}
    for relative,row in expected.items():
        key=next((k for k in sorted(roots,key=len,reverse=True) if k!='root' and relative.startswith(k+'/')),'root')
        name=relative if key=='root' else relative[len(key)+1:]
        gitraw,gitrecord=provenance._git_blob(roots[key],closure[key]['head'],name,max(row['bytes'],1)+1024)
        path=source/relative
        raw,_=provenance._frozen(path,max(row['bytes'],1)+1024)
        mode,oid=git_entries[key][name]
        require(oid==gitrecord['git_blob'],'canonical_source_Git_entry_changed')
        observed={'git_mode':mode,'git_blob':gitrecord['git_blob'],'bytes':len(raw),'sha256':_hash(raw)}
        require(raw==gitraw and observed==row,'canonical_source_Git_bytes_changed:'+relative)
        actual[relative]=observed
    return closure,actual


def validate_sdk_module_inventory(loaded, source, namespace):
    """Common child/parent contract for every consumed source module."""
    provenance,require,_=_api();source=Path(source)
    require(type(loaded) is dict and loaded,'canonical_SDK_module_inventory_required')
    required={'Scripts.StructTrain.TimeLearner.'+name for name in MODULES}
    require(required<=set(loaded),'canonical_required_SDK_module_missing')
    for name,row in loaded.items():
        require(type(name) is str and name.startswith('Scripts.'),'canonical_child_module_name_path_changed')
        _keys(row,'path sha256 git_blob','canonical_child_module_record')
        require(type(row['path']) is str,'canonical_child_module_origin')
        path=provenance._canonical(Path(row['path']))
        require(path.is_relative_to(source),'canonical_child_Tool_SDK_namespace_mix')
        relative=path.relative_to(source).as_posix()
        expected=(relative[:-len('/__init__.py')] if relative.endswith('/__init__.py')
                  else relative[:-3] if relative.endswith('.py') else '')
        require(expected and name==expected.replace('/','.'),'canonical_child_module_name_path_changed')
        require(relative in namespace and row['sha256']==namespace[relative]['sha256'] and
                row['git_blob']==namespace[relative]['git_blob'],'canonical_child_module_changed')
    return loaded


def capture_sdk_modules(source, namespace):
    """Bind the actual import closure to declared Git bytes, never a fixed count."""
    _,require,_=_api();source=Path(source);loaded={}
    for name,module in tuple(sys.modules.items()):
        if not name.startswith('Scripts.') or not getattr(module,'__file__',None):continue
        path=Path(module.__file__).resolve(strict=True)
        require(path.is_relative_to(source),'canonical_child_Tool_SDK_namespace_mix')
        relative=path.relative_to(source).as_posix();data=path.read_bytes()
        require(relative in namespace and _hash(data)==namespace[relative]['sha256'],
                'canonical_child_module_changed')
        loaded[name]={'path':str(path),'sha256':_hash(data),'git_blob':namespace[relative]['git_blob']}
    return validate_sdk_module_inventory(loaded,source,namespace)


def _child(plan_path, source, commit, plan_digest):
    if __package__ not in (None,'') or any(n=='Scripts' or n.startswith('Scripts.') for n in sys.modules):
        raise ValueError('canonical_child_not_clean_file_bootstrap')
    source=Path(source)
    if source.resolve(strict=True)!=source or _git(source,'rev-parse','HEAD').decode('utf-8').strip()!=commit:
        raise ValueError('canonical_child_wrong_source')
    sys.path.insert(0,str(source));modules={n:importlib.import_module('Scripts.StructTrain.TimeLearner.'+n) for n in MODULES}
    provenance,require,runtime=_api();raw,_=provenance._frozen(Path(plan_path),1024**2)
    require(_hash(raw)==plan_digest,'canonical_plan_changed');plan=provenance._json(raw);state=validate_plan(plan)
    require(state['source']==source and plan['source']['commit']==commit,'canonical_child_source_binding')
    closure,namespace=verify_namespace(source,state['namespace'])
    require(closure['root']['head']==commit,'canonical_child_source_head')
    loaded=capture_sdk_modules(source,namespace)
    claims=[{'binding_path':p,'binding':value} for p,value,_ in state['prior']]
    originals={p:raw for p,_,raw in state['prior']}
    args=['--job',str(state['controller']/'inputs/job.json')]
    spec=modules['native_preparation'].prepare_native_module_checks(source,**state['cohort'],
        module='Scripts.StructTrain.TimeLearner.native_acceptance_worker',arguments=args,
        prior_bindings=claims,prior_originals=originals,historical={'role':'fresh native canonical only; not compile/test/model execution'})
    canonical=modules['native_preparation'].serialize_preparation(spec)
    ids=modules['native_acceptance_worker'].validate_job(state['job'],spec,args)
    require(runtime.source_closure(source)==closure,'canonical_source_changed_during_child')
    # Include imports performed lazily by the real preparation/validation APIs.
    # Required roots and every consumed file still need exact declared Git bytes.
    final_loaded=capture_sdk_modules(source,namespace)
    require(all(final_loaded.get(name)==row for name,row in loaded.items()),
            'canonical_SDK_module_changed_during_preparation')
    return {'kind':'timelearner_native_canonical_child_result','schema_version':1,
        'canonical_utf8':canonical.decode('utf-8'),'native_job_utf8':state['jobraw'].decode('utf-8'),
        'source_closure':closure,'namespace':namespace,'SDK_modules':final_loaded,'selected_ids':ids,
        'configure_arguments':state['configure'],'actor':{'path':str(Path(__file__).resolve()),
        'sha256':_hash(Path(__file__).read_bytes()),'Scripts_namespace_owner':str(source)},
        'compiled_or_tests_or_models':False,'scientific_verdict':None}


def produce(plan, plan_path, plan_digest, output, registry, token, guard, emit):
    """Called only by existing owned_python_job with its one live lease."""
    from .resource_reservations import Reservations
    from .contained_process import inspect
    from .native_preparation import serialize_preparation
    from .native_acceptance_worker import validate_job
    _,require,runtime=_api();state=validate_plan(plan);registry.validate_paths(token)
    rows=[r for r in Reservations.read_snapshot(registry.path)['leases'] if r['token']==token]
    require(len(rows)==1 and rows[0]['state']=='held' and rows[0]['owner']['pid']==os.getpid(),
            'canonical_not_owned_worker')
    required=resources(plan,Path(output).parent,plan_path)
    require(all(any(v['canonical_path']==r['path'] and v['access']==r['access'] for v in rows[0]['resources']) for r in required),
            'canonical_lease_resources_changed')
    inputs_before=capture_inputs(plan,plan_path,plan_digest);emit('canonical-inputs-before.json',inputs_before)
    for path,binding,_ in state['prior']:
        observed=inspect(Path(path).parent)
        require(observed['all_processes_closed'] and observed['binding']==binding,'canonical_prior_not_closed')
    from .owned_python_job import _source_snapshot
    native_tool=_source_snapshot(state['tool'],plan['native_tool']['commit'])
    emit('canonical-native-tool.json',native_tool)
    before=runtime.source_closure(state['source']);emit('canonical-source-before.json',before);guard()
    arguments=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'_child',str(plan_path),
        str(state['source']),plan['source']['commit'],plan_digest]
    environment=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
    for name in ('PYTHONPATH','PYTHONHOME'):environment.pop(name,None)
    try:child=subprocess.run(arguments,cwd=state['source'],env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    except subprocess.TimeoutExpired as error:
        (Path(output)/'canonical-child.stdout').write_bytes(error.stdout or b'')
        (Path(output)/'canonical-child.stderr').write_bytes(error.stderr or b'');raise
    (Path(output)/'canonical-child.stdout').write_bytes(child.stdout);(Path(output)/'canonical-child.stderr').write_bytes(child.stderr)
    require(child.returncode==0 and len(child.stdout)<=16*1024**2,'canonical_child_failed_or_oversize')
    provenance,_,_=_api();result=provenance._json(child.stdout)
    _keys(result,'kind schema_version canonical_utf8 native_job_utf8 source_closure namespace SDK_modules selected_ids configure_arguments actor compiled_or_tests_or_models scientific_verdict','canonical_child_result_schema')
    require(result['kind']=='timelearner_native_canonical_child_result' and type(result['schema_version']) is int and result['schema_version']==1 and
        result['compiled_or_tests_or_models'] is False and result['scientific_verdict'] is None,'canonical_child_result')
    require(result['actor']['path']==str(Path(__file__).resolve()) and result['actor']['sha256']==_hash(Path(__file__).read_bytes()),'canonical_child_actor_changed')
    canonical=result['canonical_utf8'].encode('utf-8');jobraw=result['native_job_utf8'].encode('utf-8');spec=provenance._json(canonical)
    require(serialize_preparation(spec)==canonical and jobraw==state['jobraw'],'canonical_child_raw_documents_changed')
    args=['--job',str(state['controller']/'inputs/job.json')];ids=validate_job(state['job'],spec,args)
    after,namespace=verify_namespace(state['source'],state['namespace'])
    require(after==before==result['source_closure'] and namespace==result['namespace'] and ids==result['selected_ids'],'canonical_child_source_changed')
    validate_sdk_module_inventory(result['SDK_modules'],state['source'],namespace)
    require(result['configure_arguments']==state['configure'],'canonical_child_configure_changed')
    inputs_after=capture_inputs(plan,plan_path,plan_digest);emit('canonical-inputs-after.json',inputs_after)
    require(inputs_after==inputs_before,'canonical_inputs_changed_during_preparation')
    guard();registry.validate_paths(token)
    state['output'].mkdir(exist_ok=False)
    (state['output']/'canonical-preparation.json').write_bytes(canonical)
    (state['output']/'native48-job.json').write_bytes(jobraw)
    (state['output']/'same-SDK-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    native={'kind':'timelearner_owned_native_job','schema_version':1,'job_id':state['paths']['output'].name,
        'worker_host':socket.gethostname(),'execution_root':str(state['base']),
        'tool_commit':plan['native_tool']['commit'],'job':{'path':str(state['output']/'native48-job.json'),'sha256':_hash(jobraw)},
        'preparation':{'path':str(state['output']/'canonical-preparation.json'),'sha256':_hash(canonical)}}
    (state['output']/'owned-native-request.json').write_text(json.dumps(native,indent=2)+'\n',encoding='utf-8')
    emit('canonical-result.json',{'external_output':str(state['output']),'selected':len(ids),
        'SDK_imported_modules':len(result['SDK_modules']),'source_files':len(namespace),
        'canonical_sha256':_hash(canonical),'job_sha256':_hash(jobraw),'native_dispatch':False,'scientific_verdict':None})


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('_child',))
    parser.add_argument('plan');parser.add_argument('source');parser.add_argument('commit');parser.add_argument('digest')
    args=parser.parse_args(argv);result=_child(args.plan,args.source,args.commit,args.digest)
    print(json.dumps(result,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
