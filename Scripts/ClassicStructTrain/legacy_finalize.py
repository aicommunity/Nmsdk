"""Publish verified native configurations and audit complete experiment evidence."""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,subprocess,sys,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,CONFIG,OUT,save
from legacy_recover import fingerprint
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args,directory=ROOT):return subprocess.check_output(['git',*args],cwd=directory,text=True,encoding='utf8').strip()
def prepare():
    a=load(OUT/'assessment.json');expected=load(CONFIG/'recovered-jobs.json')
    assert a['summary']['valid_saved_states']==9
    assert all(j['id'] in a['first_by_job'] for j in expected),'All recovered physical states must be measured or equivalently reused'
    unique={r['case']:r for r in a['first_by_job'].values()};jobs=[];verified=[]
    for case,r in unique.items():
        source=ROOT/r['directory']/'after';destination=CONFIG/'Verified'/case;destination.mkdir(parents=True,exist_ok=True)
        for filename in ['Model_00.xml','Parameters_00.xml','project.ini']:shutil.copy2(source/filename,destination/filename)
        (destination/'Interface.xml').write_text('<Interfaces />\n',encoding='utf8')
        job=copy.deepcopy(r['job']);job.update(id=case+'-all-init',audit_only=True,trace=False,roundtrip=False,
                       config=str((destination/'project.ini').relative_to(ROOT)).replace('\\','/'))
        job.pop('input_ids',None);jobs.append(job)
        verified.append({'case':case,'directory':str(destination.relative_to(ROOT)).replace('\\','/'),
                         'native_model_sha256':sha(destination/'Model_00.xml'),'physical_sha256':fingerprint(ET.parse(destination/'Model_00.xml').getroot()),
                         'aliases':[key for key,value in a['first_by_job'].items() if value['case']==case]})
    save(CONFIG/'initialization-jobs.json',jobs);save(CONFIG/'verified-manifest.json',verified)
    print('Verified native states and full initialization audits prepared:',len(jobs))

def audit():
    errors=[];a=load(OUT/'assessment.json');p=load(PLAN);prepared=load(ROOT/'Bin/Configs/StructTrainClassic/Prepared/manifest.json')
    for doc in p['documents']:
        if sha(ROOT/'Docs/ClassicStructTrainExperiments'/doc['path'])!=doc['sha256']:errors.append('Archive changed: '+doc['path'])
    for cfg in prepared['verbatim_configs']:
        if sha(ROOT/'Bin/Configs/StructTrainClassic'/cfg['path'])!=cfg['sha256']:errors.append('Verbatim config changed: '+cfg['path'])
    stages=['saved-b','recovered-b','protocols-a','context-a','initialization-a','scientific-extra'];processes=[]
    expected_counts={'saved-b':26,'recovered-b':2*(len(load(CONFIG/'recovered-jobs.json'))-len(load(OUT/'recovered-reused.json'))),
                     'protocols-a':len(load(CONFIG/'protocol-jobs.json')),'context-a':sum(1 if j.get('input_ids') else 2 for j in load(CONFIG/'context-jobs.json')),
                     'initialization-a':len(load(CONFIG/'initialization-jobs.json')),'scientific-extra':len(load(CONFIG/'scientific-jobs.json'))}
    for stage in stages:
        meta=load(OUT/(stage+'-run.json'))
        if not meta['complete']:errors.append('Incomplete stage: '+stage)
        if len(meta['jobs'])!=expected_counts[stage]:errors.append('Stage process count mismatch: '+stage)
        for item in meta['jobs']:
            processes.append(item)
            if item['status']!='completed' or item['exit_code']!=0:errors.append('Native process failed: '+item['job'])
            if Path(item['cwd']).resolve()!=(ROOT/'Bin/Platform/Win').resolve() or Path(item['command'][0]).resolve().parent!=(ROOT/'Bin/Platform/Win').resolve():errors.append('Wrong runtime/CWD: '+item['job'])
    expected_recovered=2*(len(load(CONFIG/'recovered-jobs.json'))-len(load(OUT/'recovered-reused.json')))
    if len(a['recovered'])!=expected_recovered:errors.append('Recovered run count mismatch')
    for key,stage in [('saved','saved-b'),('protocols','protocols-a'),('context','context-a'),('scientific_extra','scientific-extra')]:
        if len(a[key])!=expected_counts[stage]:errors.append('Assessment record count mismatch: '+stage)
    for field in ['graph_load_failures','graph_inference_failures','graph_roundtrip_failures','roundtrip_answer_failures','repeat_differences']:
        if a['summary'][field]:errors.append(field+': '+str(a['summary'][field]))
    for r in a['saved']+a['recovered']+a['protocols']+a.get('context',[])+a.get('scientific_extra',[]):
        if not r['training_disabled'] or not r['structure_unchanged']:errors.append('Training/structure invariant failed: '+r['case'])
        if len(r['answers'])!=len(r['input_ids']):errors.append('Answer cardinality mismatch: '+r['case'])
        if not(r['graph_loading']['passed'] and r['graph_inference']['passed']):errors.append('Physical graph comparison failed: '+r['case'])
        if r.get('whole_initialization_audit',{}).get('uninitialized'):errors.append('Full-context active objects are uninitialized: '+r['case'])
    init_records=[]
    for folder in (OUT/'initialization-a').iterdir():
        file=folder/'results.jsonl'
        if file.exists():init_records.extend(json.loads(line) for line in file.read_text().splitlines() if line.strip())
    expected_init=len(load(CONFIG/'initialization-jobs.json'))
    if len(init_records)!=expected_init:errors.append('Initialization audit count mismatch')
    uninitialized=sum(len(r['initialization_audit']['uninitialized']) for r in init_records)
    if uninitialized:errors.append('Uninitialized active objects: '+str(uninitialized))
    for c in a['reload_checks']:
        if not(c['same_answer'] and c['same_peak'] and c['graph']):errors.append('Saved-state roundtrip control failed: '+c['base'])
    for c in a['third_checks']:
        if not(c['same_answers'] and c['same_peaks']):errors.append('Third repeat failed: '+c['base'])
    if not a['assembly_check'] or not all(a['assembly_check'][k] for k in ['same_answers','same_peaks','same_graph']):errors.append('Independent reconstruction assembly control failed')
    if git('branch','--show-current')!='autoPreset' or git('branch','--show-current',directory=ROOT/'Bin')!='autoPreset':errors.append('Unexpected branch')
    if git('rev-parse','HEAD')!=prepared['root_sha']:errors.append('Unexpected root revision')
    production={relative:git('status','--short',directory=ROOT/relative) for relative in ['Rdk','Libraries/Nmsdk-PulseLib']}
    if any(production.values()):errors.append('Production sources modified')
    cache=(ROOT/'build/win-vs2022-ninja-release-localqt/CMakeCache.txt').read_text(encoding='utf8')
    if 'CMAKE_BUILD_TYPE:STRING=Release' not in cache or '/O2 /Ob2 /DNDEBUG' not in cache:errors.append('Release optimization missing')
    result={'passed':not errors,'errors':errors,'archive_files_checked':len(p['documents']),'verbatim_configs_checked':len(prepared['verbatim_configs']),
        'native_processes':len(processes),'initialization_states':len(init_records),'uninitialized_objects':uninitialized,
        'active_objects_checked':sum(r['initialization_audit']['active_components'] for r in init_records),
        'root_sha':git('rev-parse','HEAD'),'pulselib_sha':git('rev-parse','HEAD',directory=ROOT/'Libraries/Nmsdk-PulseLib'),
        'production_status':production,'binary_hashes':sorted({r['binary_sha256'] for r in processes})}
    save(OUT/'final-audit.json',result);print(json.dumps(result,ensure_ascii=False))
    if errors:raise SystemExit(1)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare-init','audit']);args=parser.parse_args();prepare() if args.action=='prepare-init' else audit()
