"""Collect an existing closed65 gate through Source2caf metadata APIs; never run tests."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading

B=Path('/media/user/Data/TimeLearnerRefactor')
C=B/'source-collector-input-capabilities-m40-a1'
T=B/'source-channel-lt-overview-tool-m40-a2'
P=B/'plan-collector-input-capabilities65-m40-a2'
OLD=B/'plan-collector-input-capabilities65-m40-a1'
J=B/'readbacks/s10-collector-input-capabilities65-m40-a1'
PUB=B/'publication-collector-input-capabilities65-m40-a1'
REPO=B/'evidence-collector-input-capabilities65-m40-a1'
INPUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(C))
os.environ.update(GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0')
from Scripts.StructTrain.TimeLearner.collector_provenance import (
    RequiredFileRole,GitInputRole,capture_required_file_roles,verify_git_input_roles,
    capture_python_selection_inventory,capture_owned_supervisor,describe_collection,_frozen,_json,_canonical)
from Scripts.StructTrain.TimeLearner.contained_process import inspect
from Scripts.StructTrain.TimeLearner.owned_python_job import _source_snapshot
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.runtime import runtime_content_identity,digest_json
from Scripts.StructTrain.TimeLearner.portable_primary import create_native_bundle

assert len(sys.argv)==2 and re.fullmatch('[0-9a-f]{64}',sys.argv[1])
manifest_raw,manifest_record=_frozen(INPUT/'input-manifest.json',128*1024)
assert manifest_record['sha256']==sys.argv[1]
E=_json(manifest_raw)
assert E['kind']=='collector65_fixed_closed_metadata_inputs' and E['schema_version']==1
assert E['job_id']=='s10-collector-input-capabilities65-m40-a1'
SOURCE=E['collection_source_commit'];TOOL=E['original_tool_commit'];PLAN=E['plan_commit']
assert SOURCE=='2caf3ad467b7f8b82c7f1b42c4680cbe0061bdae'
assert TOOL=='cec33f2fcceb8c8f815e3494173bf48dcd39ed6c'
assert PLAN=='884dad3970ba4ec11b9f6ba8739e0b354eb29fcf'
assert E['expected_tests']==65 and E['external_scientific_fixtures']=={}
for root in (B,C,T,P,OLD,J,INPUT):assert _canonical(root).is_dir()
for root in (PUB,REPO):assert _canonical(root,exists=False)==root and not root.exists()

def git(root,*arguments,data=None):
    return subprocess.check_output(['git','-C',str(root),*arguments],input=data,
        env={**os.environ,'GIT_NO_LAZY_FETCH':'1','GIT_OPTIONAL_LOCKS':'0'})

def inventory(root):
    result={}
    for path in sorted(root.rglob('*')):
        if path.is_dir() and not path.is_symlink():continue
        raw,row=_frozen(path,16*1024**2)
        result[path.relative_to(root).as_posix()]={'bytes':len(raw),'sha256':row['sha256']}
    return result

def immutable_lease(row):
    return {k:row[k] for k in ('token','job_id','owner','resources','state','created','deadline','updated','release_note')}

registry=Reservations.open_existing(B/'resource-reservations.sqlite3')

def closure():
    current=inspect(J/'process/contained');binding=current['binding'];expected=E['binding']
    assert binding==expected and current['all_processes_closed'] and current['state']['MainPID']=='0'
    assert not current['state']['ControlGroup'] and not Path('/sys/fs/cgroup'+binding['control_group']).exists()
    request=_json(_frozen(J/'process/contained/request.json',1024**2)[0])
    worker=_json(_frozen(J/'worker/reservation.json',1024**2)[0])
    rows=[r for r in registry.inspect()['leases'] if r['job_id']==E['job_id']]
    assert len(rows)==1 and rows[0]['state']=='released' and rows[0]['token']==E['lease_token']
    released=rows[0]
    for key in ('token','job_id','owner','resources'):assert released[key]==worker[key]
    owner=released['owner']
    assert owner['pid']==binding['initial_main_pid'] and owner['start_ticks']==binding['initial_start_ticks']
    assert owner['boot_id']==request['boot_id']==E['boot_id'] and owner['uid']==request['uid']==1000
    runtime=_json(_frozen(J/'process/runtime.json',1024**2)[0])
    assert runtime_content_identity(runtime)==runtime['runtime_identity']
    assert digest_json(runtime['runtime_identity'])==runtime['runtime_fingerprint']==request['runtime_fingerprint']
    assert runtime['source_closure']['tool_root']==TOOL and owner['executable']==runtime['executable']['path']
    return {'kernel':current,'released_lease':released,'runtime_fingerprint':runtime['runtime_fingerprint']}

# Each capability and every required path is validated before publication writes.
source_before=_source_snapshot(C,SOURCE);tool_before=_source_snapshot(T,TOOL)
assert len(source_before['files'])==635 and len(tool_before['files'])==632
job_before=inventory(J)
assert set(E['required_job_paths'])<=set(job_before)
assert not any(Path(n).suffix.lower() in ('.csv','.png','.svg','.pdf','.gguf','.xz','.tar') for n in job_before)
assert sum(r['bytes'] for r in job_before.values())<16*1024**2
suite_raw,_=_frozen(P/'suite.json',128*1024);suite=_json(suite_raw)
assert hashlib.sha256(suite_raw).hexdigest()==E['suite_sha256']
assert suite['expected_test_ids']==E['expected_test_ids'] and suite['fixtures']=={}
literal=capture_python_selection_inventory(C,SOURCE,suite['modules'],E['expected_test_ids'])
git_requirements=[GitInputRole(**{**row,'repository':Path(row['repository'])}) for row in E['git_roles']]
git_capabilities=verify_git_input_roles(git_requirements,maximum_total_bytes=2*1024**2)
supervisor=capture_owned_supervisor(J/'process/contained',supervisor_log=J/'supervisor.log',worker_stdout=J/'process/contained/stdout.log')
fresh_before=closure();assert supervisor.descriptor['binding']==fresh_before['kernel']['binding']
requirements=[];archive_names={}

def add(role,root,name,row,archive):
    staged='f%04d'%len(requirements)
    requirements.append(RequiredFileRole(role,root,name,row['bytes'],row['sha256'],16*1024**2,staged))
    assert archive not in archive_names.values();archive_names[role]=archive

add('input-manifest',INPUT,'input-manifest.json',manifest_record,'preparation-history/input-manifest.json')
for number,(name,row) in enumerate(sorted(E['input_files'].items())):
    add('input-%04d'%number,INPUT,name,row,'preparation-history/'+name)
for number,(name,row) in enumerate(sorted(job_before.items())):
    add('job-%04d'%number,J,name,row,'original-job/'+name)
for number,row in enumerate(E['plan_files']):
    add('plan-%04d'%number,P,row['path'],row,'frozen-plan/'+row['archive_name'])
prep_raw,prep_record=_frozen(P/'prepared-metadata.json',128*1024)
prep=_json(prep_raw)
assert prep['status']=='prepared_not_dispatched' and prep['tests_dispatched'] is False
assert prep['binding']['source_commit']==SOURCE and prep['binding']['plan_commit']==PLAN
assert prep['source_scripts']==635 and prep['source_package_python_files']==444 and prep['source_package_fingerprint']==E['source_package_fingerprint']
assert prep['prep_lease_after']['state']=='released' and prep['prep_lease_after']['token']=='157c4d29-d44c-4a2f-b846-de533fab58aa'
assert len(prep['prior_failed_preparation_preserved']['files'])==10
add('plan-preparation-receipt',P,'prepared-metadata.json',prep_record,'frozen-plan/prepared-metadata.json')
for number,row in enumerate(E['prior_plan_files']):
    add('prior-plan-%04d'%number,OLD,row['path'],row,'failed-preparation-a1/'+row['archive_name'])
captured=capture_required_file_roles(requirements,maximum_total_bytes=24*1024**2)
assert E['producer_name'] in E['input_files'] and Path(__file__).name==E['producer_name']
assert not PUB.exists() and not REPO.exists()
assert shutil.disk_usage(B).free>=512*1024**2+96*1024**2
memory=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024
assert memory>=768*1024**2
lease=registry.reserve('publish-collector-input-capabilities65-m40-a1',
    [{'path':str(root),'access':'write'} for root in (PUB,REPO)]+
    [{'path':str(root),'access':'read'} for root in (C,T,P,OLD,J,INPUT)],ttl_seconds=120,
    demands={'slots':1,'memory_bytes':536870912,'disk_bytes':134217728} if registry.capacity is not None else None)
stop=threading.Event();heartbeat_errors=[]
def heartbeat():
    while not stop.wait(10):
        try:registry.heartbeat(lease['token'],ttl_seconds=120);registry.validate_paths(lease['token'])
        except BaseException as error:heartbeat_errors.append(str(error));return
thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
publication=None
try:
    registry.validate_paths(lease['token']);PUB.mkdir();stage=PUB/'observer';stage.mkdir()
    staged=captured.materialize(stage,stage/'captured-files')
    files={archive_names[role]:staged['collector-file-inputs/'+row['staged_name']]
           for role,row in captured.descriptor['roles'].items()}
    files.update(supervisor.materialize(stage,stage/'bound-supervisor'))
    def write(name,value):
        path=stage/name
        with path.open('x',encoding='utf-8') as stream:
            json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        files['observer/'+name]=path
    def original(name):return _json(files['original-job/'+name].read_bytes())
    request=original('request.json');result=original('worker/validation/result.json')
    assert hashlib.sha256(files['original-job/request.json'].read_bytes()).hexdigest()==E['request_sha256']
    assert request['tool_commit']==TOOL and request['operation']['source']=={'path':str(C),'commit':SOURCE}
    assert request['operation']['suite']=={'path':str(P/'suite.json'),'sha256':E['suite_sha256']} and request['operation']['fixtures']=={}
    assert result['assertion_status']=='passed' and result['execution']=='completed' and result['executed_tests']==65
    assert not any(result[key] for key in ('errors','failures','skipped')) and result['expected_test_ids']==E['expected_test_ids']
    log=files['original-job/worker/validation/unittest.log'].read_bytes()
    actual_ids=re.findall(r'^\S+ \(([^)]+)\) \.\.\. ok$',log.decode('utf-8'),re.M)
    assert len(actual_ids)==len(set(actual_ids))==65 and set(actual_ids)==set(literal['literal_test_ids'])
    controller=original('controller-result.json');terminal=original('worker/terminal.json')
    assert controller['execution']=='completed' and controller['returncode']==0 and controller['all_processes_closed']
    assert controller['runtime_provenance']=='loaded_files_captured' and terminal['operation_passed'] and not terminal['heartbeat_errors']
    assert source_before==original('worker/validation-source-before.json')==original('worker/validation-source-after.json')
    assert tool_before==original('worker/tool-source-before.json')==original('worker/tool-source-after.json')
    assert original('worker/fixtures-before.json')==original('worker/fixtures-after.json')=={}
    for snapshot,count,expected in ((source_before,444,E['source_package_fingerprint']),(tool_before,441,E['tool_package_fingerprint'])):
        package={p.removeprefix('Scripts/StructTrain/TimeLearner/'):r['sha256'] for p,r in snapshot['files'].items() if p.startswith('Scripts/StructTrain/TimeLearner/') and p.endswith('.py')}
        assert len(package)==count and digest_json(package)==expected
    write('typed-file-capabilities.json',captured.descriptor)
    write('typed-Git-capabilities.json',git_capabilities)
    write('literal-inventory.json',literal)
    write('collection-provenance.json',describe_collection(supervisor,collector_tool_root=C,
        compilation_state='not_started',actual_sdk_source=None,compiled_runtime=None,
        planned_source={'original_controller_tool':TOOL,'validation_source':SOURCE,'plan_commit':PLAN,'scope':'metadata65 only'}))
    write('actual-log-test-ids.json',{'ids':actual_ids,'count':65,'log_sha256':hashlib.sha256(log).hexdigest()})
    facts={'kind':'closed_collector_input_capabilities65_scoped_passed','schema_version':1,
        'collection_source_root':SOURCE,'original_controller_tool_root':TOOL,'validation_source_root':SOURCE,'plan_commit':PLAN,
        'tests':65,'passed':65,'failures':0,'errors':0,'skipped':0,'old_tests':39,'new_tests':26,
        'fresh_closure_and_released_lease':fresh_before,'original_controller':controller,'original_terminal':terminal,
        'source_before_after_equal':True,'external_scientific_fixtures':{},'source_SDK_verified':False,
        'original_job_manifest':job_before,'archive_roles':archive_names,'upfront_production_APIs_used':[
            'capture_required_file_roles','verify_git_input_roles','capture_python_selection_inventory','capture_owned_supervisor'],
        'publication_reservation':lease,'original_preparation_A1_preserved':True,'no_test_or_model_rerun':True,
        'collector_transition':{'this_producer':'transitional fixed reviewed consumer of maintained Source2caf APIs',
            'negative73_requires_maintained_data_driven_Root_entrypoint':True,'frozen65_tests_not_expanded':True},
        'native_CPP_or_scientific_acceptance':False,'scientific_verdict':None}
    write('verification.json',facts)
    expanded=sum(path.stat().st_size for path in files.values());assert expanded<24*1024**2
    assert not heartbeat_errors and shutil.disk_usage(B).free>=512*1024**2+3*expanded+96*1024**2
    bundle=create_native_bundle(files,stage/'packed',dictionary_bytes=32*1024**2)
    assert inventory(J)==job_before and _source_snapshot(C,SOURCE)==source_before and _source_snapshot(T,TOOL)==tool_before
    assert capture_required_file_roles(requirements,maximum_total_bytes=24*1024**2).descriptor==captured.descriptor
    assert verify_git_input_roles(git_requirements,maximum_total_bytes=2*1024**2)==git_capabilities
    assert capture_python_selection_inventory(C,SOURCE,suite['modules'],E['expected_test_ids'])==literal
    assert immutable_lease(closure()['released_lease'])==immutable_lease(fresh_before['released_lease']) and not heartbeat_errors
    subprocess.run(['git','init','--quiet',str(REPO)],check=True)
    for pack in sorted((T/'.git/objects/pack').glob('*.pack')):
        with pack.open('rb') as stream:subprocess.run(['git','-C',str(REPO),'index-pack','--stdin','--promisor'],stdin=stream,stdout=subprocess.PIPE,check=True)
    (REPO/'.git/shallow').write_bytes((TOOL+'\n').encode())
    index_env={**os.environ,'GIT_INDEX_FILE':str(REPO/'.git/collector.index')}
    def rg(*arguments,data=None):
        return subprocess.check_output(['git','-C',str(REPO),*arguments],input=data,env=index_env).decode().strip()
    rg('read-tree',TOOL+'^{tree}');prefix='Reports/StructTrain/TimeLearner/'+E['job_id']
    for name,path in (('primary.tar.xz',stage/'packed/primary.tar.xz'),('bundle.json',stage/'packed/bundle.json'),('verification.json',stage/'verification.json')):
        oid=rg('hash-object','-w','--stdin',data=path.read_bytes());rg('update-index','--add','--cacheinfo','100644,'+oid+','+prefix+'/'+name)
    commit=rg('-c','user.name=Codex','-c','user.email=codex@openai.com','commit-tree',rg('write-tree','--missing-ok'),'-p',TOOL,
              data=b'Preserve closed metadata65 and real production typed-collector integration\n')
    rg('update-ref','refs/heads/evidence',commit);pack=stage/'evidence.pack'
    with pack.open('xb') as stream:subprocess.run(['git','-C',str(REPO),'pack-objects','--stdout','--revs'],input=(commit+'\n^'+TOOL+'\n').encode(),stdout=stream,env=index_env,check=True)
    pack_raw,pack_record=_frozen(pack,16*1024**2)
    publication={'evidence_commit':commit,'parent':TOOL,'prefix':prefix,'archive_members':len(files),'expanded_bytes':expanded,
        'archive_bytes':bundle['archive_bytes'],'archive_sha256':bundle['archive_sha256'],'pack_path':str(pack),
        'pack':{'bytes':len(pack_raw),'sha256':pack_record['sha256']},'tests':65,'scientific_verdict':None}
finally:
    stop.set();thread.join(timeout=15)
    registry.release(lease['token'],note='Closed65 metadata publication completed or failed; no tests, models, SDK/source or original-job changes.')
if publication is not None:
    rows=[r for r in registry.inspect()['leases'] if r['token']==lease['token']]
    assert len(rows)==1 and rows[0]['state']=='released'
    publication['publication_released_lease']=rows[0]
    print(json.dumps(publication,sort_keys=True,allow_nan=False),flush=True)
