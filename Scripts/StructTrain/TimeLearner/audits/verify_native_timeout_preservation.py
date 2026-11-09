"""Independent stdlib/Git hash reader for closed-native preservation schema2.

Does not import project code, execute tests/models, or analyze CSV numbers.
Kernel observations are supplied separately; cleanup never proves test success.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
from xml.etree import ElementTree as ET


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            assert k not in result, ('duplicate JSON key', k)
            result[k] = v
        return result
    def nonfinite(value):
        raise ValueError(value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def git(repo, *args, data=None):
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(['git','--no-replace-objects','-C',str(repo),*args], input=data, env=env)


def blobs(repo, names):
    names = list(dict.fromkeys(names))
    raw = git(repo,'cat-file','--batch',data=('\n'.join(names)+'\n').encode())
    offset, result = 0, {}
    for name in names:
        end = raw.index(b'\n',offset)
        header = raw[offset:end].decode().split()
        assert len(header)==3 and header[1]=='blob', (name,header)
        size = int(header[2]); assert 0 <= size <= 64*1024**2
        offset = end+1; result[name] = raw[offset:offset+size]; offset += size
        assert len(result[name])==size and raw[offset:offset+1]==b'\n'
        offset += 1
    assert offset==len(raw)
    return result


def safe(name):
    p = PurePosixPath(name)
    assert name==p.as_posix() and not p.is_absolute() and '\\' not in name and '\0' not in name
    assert not any(n in ('.','..','.git') for n in p.parts)


def verify(args):
    if not __debug__:
        raise RuntimeError('Independent metadata verification requires Python assertions enabled')
    repo = Path(args.repo)
    names = ['artifact-inventory.json','capture-proof.json','packed/bundle.json','packed/primary.tar.xz','verification.json']
    files = {n:git(repo,'show',args.commit+':'+args.prefix+'/'+n) for n in names}
    manifest = load(files['capture-proof.json'])
    assert manifest['schema_version']==2
    inventory = load(files['artifact-inventory.json'])
    assert set(inventory)==set(names)-{'artifact-inventory.json'}
    assert all(sha(files[n])==h for n,h in inventory.items())
    proof = manifest
    receipt = load(files['verification.json']); bundle = load(files['packed/bundle.json'])
    assert receipt['schema_version']==2 and receipt['collection_status']=='completed'
    assert receipt['scientific_verdict'] is None and receipt['collector_external_cgroup_attested'] is False
    assert receipt['artifact_hashes']=={n:h for n,h in inventory.items() if n!='verification.json'}
    assert proof['original_model_JSON_CSV_rewritten'] is False and proof['capture_owned_supervisor_used'] is False
    assert bundle['archive_bytes']==len(files['packed/primary.tar.xz'])
    assert bundle['archive_sha256']==sha(files['packed/primary.tar.xz'])
    assert bundle['compression']['dictionary_bytes']==32*1024**2
    assert bundle['expanded_bytes']<=256*1024**2
    members, kept, expanded = {}, {}, 0
    keep = {'observer/frozen-inputs.json','observer/readonly-inventory.json.gz','observer/capture-proof.json',
            'native-output/terminal.json','native-output/canonical-preparation.json','native-output/source-closure.json',
            'native-output/source-closure-after.json','native-output/CMakeCache-terminal.txt',
            'postclosure-build/CMakeCache.txt','controller/supervisor-result.json','controller/supervisor.log'}
    with tarfile.open(fileobj=io.BytesIO(files['packed/primary.tar.xz']),mode='r:xz') as stream:
        for entry in stream:
            safe(entry.name)
            assert entry.isfile() and entry.name not in members and entry.size<=64*1024**2
            expanded += entry.size; assert expanded<=bundle['expanded_bytes']
            raw = stream.extractfile(entry).read(); assert len(raw)==entry.size
            members[entry.name] = {'bytes':len(raw),'sha256':sha(raw)}
            if entry.name in keep or entry.name.endswith(('-actual-tests.json','/native.xml','-result.json','/result.json')):
                kept[entry.name] = raw
    assert expanded==bundle['expanded_bytes'] and members==bundle['members']
    manifest = load(kept['observer/frozen-inputs.json'])
    assert manifest['schema_version']==2 and manifest['supervisor_dialect']=='owned-native-json-lines-v1'
    control = git(repo,'show',args.control_commit+':'+args.plan_directory+'/manifest.json')
    assert control==kept['observer/frozen-inputs.json'] and sha(control)==receipt['manifest_sha256']
    observed_raw = gzip.decompress(kept['observer/readonly-inventory.json.gz'])
    assert sha(observed_raw)==manifest['readonly_inventory']['raw_sha256']
    assert len(observed_raw)==manifest['readonly_inventory']['raw_bytes']
    observed = load(observed_raw)
    assert observed['retained_symlinks_no_follow']==proof['links_no_follow']
    assert set(members)=={r['archive_path'] for r in manifest['regular_files']} | {
        'observer/frozen-inputs.json','observer/readonly-inventory.json.gz','observer/capture-proof.json'}
    for row in manifest['regular_files']:
        actual = members[row['archive_path']]
        assert actual=={'bytes':row['expected_bytes'],'sha256':row['expected_sha256']}
        descriptor = proof['regular_capture_descriptor']['roles'][row['role']]
        assert all(descriptor[k]==actual[k] for k in actual)
    assert kept['postclosure-build/CMakeCache.txt']==kept['native-output/CMakeCache-terminal.txt']
    read = lambda n:load(kept[n])
    terminal = read('native-output/terminal.json')
    assert terminal==observed['original_terminal'] and terminal['built'] is True
    assert terminal['scientific_verdict'] is None and terminal['whole_plan_complete'] is False
    prepared = read('native-output/canonical-preparation.json')
    selected = [i for r in prepared['current']['runplan'] for i in r['expected_ids']]
    cases, failures = [], []
    for name in manifest['children']:
        if name in manifest['incomplete_children']:
            declaration = manifest['incomplete_children'][name]
            assert declaration['execution']=='timeout' and declaration['junit_state']=='missing'
            assert 'native-output/'+name+'/native.xml' not in members
            gate = read('native-output/'+name+'-result.json')
            assert gate==read('native-output/'+name+'/result.json')
            assert gate['execution']=='timeout' and gate['validity']=='incomplete_test_observation'
            assert gate['assertion_status']=='not_assessed' and gate['inventory'] is None
            process = read('native-output/'+name+'/process/result.json')
            assert process['execution']=='timeout' and process['all_processes_closed'] is True
            continue
        xml = ET.fromstring(kept['native-output/'+name+'/native.xml'])
        ids, bad = [], []
        for case in xml.findall('.//testcase'):
            assert case.get('status')=='run' and case.get('result')=='completed' and case.find('skipped') is None
            identity = case.attrib['classname']+'/'+case.attrib['name']; ids.append(identity)
            if case.find('failure') is not None or case.find('error') is not None:bad.append(identity)
        record = read('native-output/'+name+'-actual-tests.json')
        assert record['observed_ids']==ids and record['failed_ids']==bad and not record['not_completed_ids']
        cases += ids; failures += bad
    original = manifest['original_outcome']
    assert len(selected)==len(set(selected))==original['planned']
    assert len(cases)==len(set(cases))==original['executed']
    assert failures==original['failed_ids'] and original['passed']==len(cases)-len(failures)
    assert [i for i in selected if i not in cases]==original['not_completed_ids']
    assert terminal['expected_cpp_cases']==original['planned']
    assert terminal['audited_completed_cpp_cases']==original['executed']
    assert terminal['actual_audited_assertion_passed_cpp_cases']==original['passed']
    assert proof['original_outcome']==receipt['original_outcome']==original
    closure = read('native-output/source-closure.json')
    assert closure==read('native-output/source-closure-after.json')
    roots = sorted((n for n in closure if n!='root'),key=len,reverse=True)
    groups = {}
    for name,row in observed['source_namespace_physical_tracked_postclosure'].items():
        role = next((r for r in roots if name.startswith(r+'/')),'root')
        relative = name if role=='root' else name[len(role)+1:]
        local = repo if role=='root' else Path(args.children_root)/role
        if role=='Libraries/Nmsdk-PulseLib':local = Path(args.pulse_repo)
        groups.setdefault((str(local),role),[]).append((relative,row))
    for (directory,role),rows in groups.items():
        commit = closure[role]['head']
        if role!='root':assert git(repo,'rev-parse',closure['root']['head']+':'+role).decode().strip()==commit
        values = blobs(directory,[commit+':'+n for n,_ in rows])
        tree = {}
        for entry in git(directory,'ls-tree','-r','-z',commit).split(b'\0'):
            if not entry:continue
            header,name = entry.split(b'\t',1); mode,kind,oid = header.decode().split()
            if kind=='blob':tree[name.decode()] = (mode,oid)
        for name,row in rows:
            raw = values[commit+':'+name]
            assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
            assert hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()==row['git_blob']
            assert tree[name]==(row['git_mode'],row['git_blob'])
    tool = proof['collector_tool_snapshot']
    assert tool['root_commit']==manifest['tool']['commit']
    values = blobs(repo,[tool['root_commit']+':'+n for n in tool['files']])
    for name,row in tool['files'].items():
        raw = values[tool['root_commit']+':'+name]
        assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
    snapshot = load(Path(args.observer).read_bytes())
    state = snapshot['original_state']; own = snapshot['current_collection_lease']
    assert snapshot['collector_receipt']==receipt and not state['supervisor_live']
    assert state['outer']['all_processes_closed'] and state['outer']['binding']==observed['outer']['binding']
    assert state['result']['record_errors']==[] and len(state['result']['children_closed'])==len(manifest['children'])
    for child in state['result']['children_closed']:
        name = Path(child['directory']).parents[1].name
        assert manifest['children'][name]=={'directory':child['directory'],'binding':child['binding']}
        assert child['closure']['all_processes_closed'] and child['closure']['binding']==child['binding']
    assert own['state']=='released' and own['owner_status']=='missing'
    assert all(own[k]==receipt['released_collection_lease'][k]==proof['own_reservation'][k]
               for k in ('token','job_id','owner','resources'))
    assert proof['original_released_lease']==observed['released_original_lease']
    assert proof['original_released_lease']['state']=='released'
    assert proof['original_released_lease']['token']==manifest['old_lease_token']
    assert git(repo,'rev-parse',args.commit+'^').decode().strip()==manifest['parent']
    assert set(git(repo,'diff-tree','--no-commit-id','--name-status','-r',manifest['parent'],args.commit).decode().splitlines())=={
        'A\t'+args.prefix+'/'+n for n in names}
    return dict(kind='independent_native_timeout_preservation_verification',schema_version=1,status='passed_metadata',
        commit=args.commit,original_outcome=original,original_files=len(manifest['regular_files']),
        archive_members=len(members),archive_bytes=len(files['packed/primary.tar.xz']),expanded_bytes=expanded,
        original_source_git_files=len(observed['source_namespace_physical_tracked_postclosure']),
        collector_source_git_files=len(tool['files']),collection_lease=own['token'],
        collector_external_cgroup_attested=False,local_numeric_or_test_execution=False,scientific_verdict=None,
        reader_sha256=sha(Path(__file__).read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo','commit','prefix','control-commit','plan-directory','children-root','pulse-repo','observer','output'):
        parser.add_argument('--'+name,required=True)
    args = parser.parse_args()
    result = verify(args)
    raw = (json.dumps(result,indent=2)+'\n').encode()
    output = Path(args.output)
    assert not output.exists() or output.read_bytes()==raw
    output.write_bytes(raw); print(raw.decode())


if __name__=='__main__':
    main()
