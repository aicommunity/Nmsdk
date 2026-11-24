"""Prepare immutable saved-state copies and supervise Release legacy inference."""
from __future__ import annotations
import argparse,copy,hashlib,json,math,os,re,subprocess,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
PLAN=ROOT/'Reports/StructTrainClassic/LegacyInferencePlan-20261123/work/plan-data.json'
CONFIG=ROOT/'Bin/Configs/StructTrainClassic/LegacyInference'
OUT=ROOT/'Reports/StructTrainClassic/LegacyChecks-20261123'
PYTHON=None
BINARY=ROOT/'Bin/Platform/Win/ClassicStructTrainReplay.exe'

def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def param(node,name,value,typ='int'):
    ps=node.find('Parameters')
    item=ps.find(name)
    if item is None:item=ET.SubElement(ps,name,{'Type':typ,'PType':'257','IoType':'17'})
    item.text=str(value)
    return item
def find_subject(root,path):
    node=root.find('Model')
    for name in path.split('.')[1:]:node=node.find('Components/'+name)
    return node
def write_config(folder,source_root,subject,links,project_text,activate=False):
    folder.mkdir(parents=True,exist_ok=True)
    root=ET.Element('Save',{'ModelName':'Model'})
    model=ET.SubElement(root,'Model',{'Class':'Model'})
    model.append(copy.deepcopy(source_root.find('Model/Parameters')))
    model.append(links)
    components=ET.SubElement(model,'Components'); subject=copy.deepcopy(subject);subject.tag='Subject'
    # Transit inputs originally received pulses from the parent classifier.
    # Supply equivalent native upstream generators in the isolated shell,
    # keeping every saved Subject source in its original transit mode.
    for i in range(1,6):
        source=subject.find(f'Components/Source{i}')
        if source is not None and source.findtext('Parameters/UseTransitSignal')=='1':
            drive=copy.deepcopy(source);drive.tag=f'Drive{i}'
            param(drive,'UseTransitSignal',0,'bool');param(drive,'Activity',int(activate),'bool');param(drive,'Frequency',1.5,'double')
            components.append(drive)
            elem=ET.SubElement(links,'elem',{'Type':'ULink'})
            ET.SubElement(elem,'Item',{'Type':'ULinkSide','Index':'-1','Name':'Output'}).text=f'Drive{i}'
            ET.SubElement(elem,'Connector',{'Type':'ULinkSide','Index':'-1','Name':'Input'}).text=f'Subject.Source{i}'
    links.set('Size',str(len(links)));components.append(subject)
    for node in subject.iter():
        if not node.get('Class'):continue
        if activate:param(node,'Activity',1,'bool')
        if node.get('Class') in ['NNeuronTrainer','NNeuronLearner','NSPNeuronGen','NPulseNeuron']:
            param(node,'StructureBuildMode',0)
        if node.get('Class') in ['NNeuronTrainer','NNeuronLearner']:
            param(node,'IsNeedToTrain',0,'bool')
            param(node,'EnableDebug',0,'bool')
            if node.get('Class')=='NNeuronLearner':param(node,'ExperimentMode',0,'bool')
            fixed=node.findtext('Parameters/FixedLTZThreshold')
            if fixed is not None:
                param(node,'LTZThreshold',fixed,'double')
                zone=node.find('Components/Neuron/Components/LTZone')
                if zone is not None:param(zone,'Threshold',fixed,'double')
            # Historical retired file I/O is external to this inference adapter.
            retired=node.find('Parameters/DataFromFile')
            if retired is not None:node.find('Parameters').remove(retired)
    ET.indent(root,space='\t');ET.ElementTree(root).write(folder/'Model_00.xml',encoding='utf8')
    properties=copy.deepcopy(root);properties.tag='SaveProperties'
    for node in properties.iter():
        for link in list(node.findall('Links')):node.remove(link)
    ET.ElementTree(properties).write(folder/'Parameters_00.xml',encoding='utf8')
    for name,val in {'ProjectAutoSaveFlag':0,'ProjectAutoSaveStateFlag':0,'DebugModeFlag':0,'MinInterstepsInterval':0,'InitAfterLoadFlag':0,'ResetAfterLoadFlag':0}.items():
        project_text=re.sub(rf'(<{name}>).*?(</{name}>)',lambda m:m[1]+str(val)+m[2],project_text)
    (folder/'project.ini').write_text(project_text,encoding='utf8')
    (folder/'Interface.xml').write_text('<Interfaces />\n',encoding='utf8')
    return root

def internal_links(source_root,path):
    prefix=path.removeprefix('Model.')
    links=ET.Element('Links',{'Type':'ULinksList','Size':'0'})
    for group in source_root.iter('Links'):
        for elem in group:
            item=elem.find('Item')
            if item is None or not (item.text or '').startswith(prefix+'.'):continue
            connectors=[c for c in elem.findall('Connector') if (c.text or '').startswith(prefix+'.')]
            if not connectors:continue
            output=ET.SubElement(links,'elem',elem.attrib)
            for side in [item,*connectors]:
                node=copy.deepcopy(side);node.text='Subject'+node.text[len(prefix):];output.append(node)
    links.set('Size',str(len(links)))
    return links

def prepare_saved():
    data=json.loads(PLAN.read_text(encoding='utf8'))
    jobs=[]
    for m in data['models']:
        if not m['training_metadata_matches_graph']:continue
        source=ROOT/'Bin/Configs/StructTrainClassic'/m['project']
        tree=ET.parse(source/'Model_00.xml').getroot()
        subject=find_subject(tree,m['component']);links=internal_links(tree,m['component'])
        for mode in (['preserved','activated'] if not m['effective_active'] else ['preserved']):
            folder=CONFIG/'Saved'/m['id']/mode
            write_config(folder,tree,subject,copy.deepcopy(links),(source/'project.ini').read_text(encoding='utf-8-sig'),mode=='activated')
            job={'id':m['id']+'-'+mode,'source_model':m['id'],'origin':'saved','kind':'trainer','target_id':m['saved_training_id'],
                 'target_class':(m['saved_training_id']-1)//50+1,'dendrites':m['dendrites'],'synapses':m['synapses'],
                 'config':str((folder/'project.ini').relative_to(ROOT)).replace('\\','/'),'source_project':m['project'],
                 'source_component':m['component'],'activation':mode,'trace':True,'roundtrip':True,
                 'external_drive':'native upstream periodic generators for saved transit sources; parent classifier competition excluded'}
            if mode=='preserved' and not m['effective_active']:
                job['input_ids']=[m['saved_training_id'],22,51,129];job['roundtrip']=False
            jobs.append(job)
    save(CONFIG/'saved-jobs.json',jobs); save(OUT/'saved-jobs.json',jobs)
    return data,jobs

def run_job(data,job,repeat,stage):
    directory=OUT/stage/(job['id']+f'-r{repeat}')
    if (directory/'process.json').exists():
        old=json.loads((directory/'process.json').read_text(encoding='utf8'))
        if old.get('status')=='completed':return old
        raise ValueError('Existing failed probe must be preserved: '+str(directory))
    directory.mkdir(parents=True,exist_ok=True)
    manifest={'repository':str(ROOT),'defaults':{'max_iterations':1000,'wall_timeout_seconds':600},'dataset':data['dataset'],'legacy_job':job}
    if 'precision_decimals' in job or 'pattern_overrides' in job:
        manifest['dataset']=copy.deepcopy(data['dataset'])
        for sample in manifest['dataset']:
            if 'precision_decimals' in job:sample['pattern']=[float(f"{v:.{job['precision_decimals']}f}") for v in sample['pattern']]
            override=job.get('pattern_overrides',{}).get(str(sample['id']))
            if override is not None:sample['pattern']=override
    manifest_path=directory/'manifest.json';save(manifest_path,manifest)
    binary=BINARY
    command=[str(binary),'--manifest',str(manifest_path),'--output',str(directory),'--suite','legacy','--repeat',str(repeat)]
    meta={'job':job['id'],'repeat':repeat,'cwd':str(binary.parent),'command':command,'binary_sha256':digest(binary),
          'manifest_sha256':digest(manifest_path),'config_sha256':digest(ROOT/job['config']),'started_utc':datetime.now(timezone.utc).isoformat(),'status':'running'}
    env=os.environ.copy();env.pop('QT_PLUGIN_PATH',None);env.pop('QML2_IMPORT_PATH',None);env['QT_QPA_PLATFORM']='offscreen'
    start=last=time.monotonic();size=-1
    print('Starting',job['id'],repeat,flush=True)
    with (directory/'stdout.log').open('wb') as stdout,(directory/'stderr.log').open('wb') as stderr:
        proc=subprocess.Popen(command,cwd=binary.parent,stdout=stdout,stderr=stderr,env=env);meta['pid']=proc.pid;save(directory/'process.json',meta)
        while proc.poll() is None:
            path=directory/'iterations.jsonl';new=path.stat().st_size if path.exists() else 0
            if new!=size:last=time.monotonic();size=new
            if time.monotonic()-last>660:proc.kill();meta['status']='idle_timeout';break
            time.sleep(.5)
        code=proc.wait()
    if meta['status']=='running':meta['status']='completed' if code==0 else 'process_error'
    meta.update(exit_code=code,elapsed_wall_seconds=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat());save(directory/'process.json',meta)
    print('Finished',job['id'],repeat,meta['status'],round(meta['elapsed_wall_seconds'],1),flush=True)
    return meta

def main():
    global BINARY
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare-saved','saved','probe','recovered','protocols','initialization','context','scientific']);p.add_argument('--jobs',type=int,default=4);p.add_argument('--only');p.add_argument('--stage',default='saved');p.add_argument('--repeats',type=int,default=2);p.add_argument('--probe',action='store_true');p.add_argument('--binary',type=Path);a=p.parse_args()
    if a.action=='prepare-saved':
        data,jobs=prepare_saved();print('Prepared',len(jobs),'saved-state protocols');return
    if a.action in ['context','initialization']:BINARY=ROOT/'Bin/Platform/Win/ClassicSavedStateCheck.exe'
    if a.binary:
        BINARY=a.binary.resolve()
        if BINARY.parent!=(ROOT/'Bin/Platform/Win').resolve():raise ValueError('Binary must be in Bin/Platform/Win')
    data=json.loads(PLAN.read_text(encoding='utf8'))
    job_files={'recovered':'recovered-jobs.json','protocols':'protocol-jobs.json','initialization':'initialization-jobs.json','context':'context-jobs.json','scientific':'scientific-jobs.json'}
    jobs=json.loads((CONFIG/job_files.get(a.action,'saved-jobs.json')).read_text(encoding='utf8'))
    if a.action=='recovered' and (OUT/'recovered-reused.json').exists():
        reused=json.loads((OUT/'recovered-reused.json').read_text(encoding='utf8'));excluded={r['recovered_job'] for r in reused}
        jobs=[j for j in jobs if j['id'] not in excluded]
    if a.only:jobs=[j for j in jobs if j['id']==a.only]
    if a.action=='probe' or a.probe:
        jobs=copy.deepcopy(jobs[:1]);jobs[0]['input_ids']=[jobs[0]['target_id'],22,51,129];jobs[0]['roundtrip']=True
    tasks=[(job,r) for job in jobs for r in range(1,(1 if job.get('input_ids') and a.action!='probe' else a.repeats)+1)]
    with ThreadPoolExecutor(max_workers=a.jobs) as executor:
        outcomes=list(executor.map(lambda x:run_job(data,*x,a.stage),tasks))
    save(OUT/(a.stage+'-run.json'),{'jobs':outcomes,'complete':all(j['status']=='completed' for j in outcomes)})
    if not all(j['status']=='completed' for j in outcomes):raise SystemExit(1)
if __name__=='__main__':main()
