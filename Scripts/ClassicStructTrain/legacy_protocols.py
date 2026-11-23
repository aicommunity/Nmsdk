"""Define separate historical subsets and diagnostics, without reusing a 150-pass history."""
import copy,json,re,sys,shutil,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,CONFIG,OUT,save,param
from legacy_recover import fingerprint

def threshold_folder(base):
    source=(ROOT/base['config']).parent;folder=CONFIG/'ThresholdControl'/base['id'];folder.mkdir(parents=True,exist_ok=True)
    for filename in ['Model_00.xml','Parameters_00.xml']:
        tree=ET.parse(source/filename);subject=tree.getroot().find('Model/Components/Subject');training=subject.findtext('Parameters/TrainingLTZThreshold')
        param(subject,'FixedLTZThreshold',training,'double');param(subject,'LTZThreshold',training,'double')
        param(subject.find('Components/Neuron/Components/LTZone'),'Threshold',training,'double');ET.indent(tree,space='\t');tree.write(folder/filename,encoding='utf8')
    shutil.copy2(source/'project.ini',folder/'project.ini');(folder/'Interface.xml').write_text('<Interfaces />\n',encoding='utf8')
    return folder

def col(n):
    s=''
    while n:n,r=divmod(n-1,26);s=chr(65+r)+s
    return s
def colnum(s):
    n=0
    for c in s:n=n*26+ord(c)-64
    return n
def main():
    evidence=json.loads((ROOT/'Reports/StructTrainClassic/archive-evidence.json').read_text(encoding='utf8'))
    data=json.loads(PLAN.read_text(encoding='utf8'));recovered=json.loads((CONFIG/'recovered-jobs.json').read_text(encoding='utf8'))
    lookup={(j['kind'],tuple(j['dendrites']),tuple(j['synapses'])):j for j in recovered}
    jobs={};refs=[];gaps=[]
    for name,sheet in evidence['research_sheets'].items():
        if name=='Исследование примеров':continue
        value=lambda cell:sheet.get(cell,{}).get('value')
        header=next((a for a,v in sheet.items() if v['value']=='Число сегментов дендритов'),None)
        if not header:continue
        hcol=colnum(re.match('[A-Z]+',header)[0]);hrow=int(re.search(r'\d+',header)[0])
        structures={}
        for row in range(hrow+1,hrow+31):
            label=value(f'{col(hcol-1)}{row}');vs=[value(f'{col(hcol+i)}{row}') for i in range(10)]
            if isinstance(label,(int,float)) and all(isinstance(x,(int,float)) and x>=1 and int(x)==x for x in vs):structures[int(label)]=list(map(int,vs))
        ids=[]
        for row in range(2,152):
            ident=value('A'+str(row))
            if isinstance(ident,(int,float)) and 1<=ident<=150:ids.append(int(ident))
            else:break
        for c in range(2,23):
            label=value(col(c)+'1')
            if not isinstance(label,(int,float)) or int(label) not in structures:continue
            answers=[value(f'{col(c)}{i+2}') for i in range(len(ids))]
            if not ids or any(a not in (0,1) for a in answers):continue
            ds=structures[int(label)];key=('learner',tuple(ds[:5]),tuple(ds[5:]));base=lookup.get(key)
            if not base:gaps.append({'sheet':name,'state':label,'dendrites':ds[:5],'synapses':ds[5:],'reason':'state not present in restoration registry'});continue
            full=ids==list(range(1,151));ident=base['id'] if full else base['id']+f'-subset{len(ids)}'
            if not full and ident not in jobs:
                job=copy.deepcopy(base);job.update(id=ident,input_ids=ids,target_id=51,target_class=2,roundtrip=False,trace=True,protocol_source=name)
                jobs[ident]=job
            refs.append({'sheet':name,'state':int(label),'source_range':f'{col(c)}2:{col(c)}{len(ids)+1}','job':ident,'base_job':base['id'],
                         'input_ids':ids,'answers':answers,'dendrites':ds[:5],'synapses':ds[5:]})
    # Independent Reset checks are distinct protocols and use a short control set.
    saved=json.loads((CONFIG/'saved-jobs.json').read_text(encoding='utf8'))
    controls=[next(j for j in saved if j['id']=='M001-activated'),next(j for j in saved if j['id']=='M018-preserved')]
    for index in [0,2]:
        base=data['baselines'][index]
        controls.append(lookup[('learner',tuple(base['dendrites']),tuple(base['synapses']))])
    for base in controls:
        j=copy.deepcopy(base);j.update(id=base['id']+'-independent',input_ids=[22,45,51,61,129,132],independent_reset=True,roundtrip=False,trace=True)
        jobs[j['id']]=j
        j=copy.deepcopy(base);j.update(id=base['id']+'-continuous-control6',input_ids=[22,45,51,61,129,132],independent_reset=False,roundtrip=False,trace=True)
        jobs[j['id']]=j
    for base in saved:
        if 'input_ids' in base:continue
        model=next(m for m in data['models'] if m['id']==base['source_model'])
        literal=[float(v) for v in model['neuron_parameters']['TrainingPattern'].split()]
        for mode in ['dataset','literal']:
            j=copy.deepcopy(base);j.update(id=base['id']+'-own-'+mode,input_ids=[base['target_id']],roundtrip=False,trace=True,
                                         own_pattern_source=mode,comparison_original=base['id'])
            if mode=='literal':j['pattern_overrides']={str(base['target_id']):literal}
            jobs[j['id']]=j
        state=OUT/'saved-b'/(base['id']+'-r1')/'after'
        destination=CONFIG/'Verified'/base['id'];destination.mkdir(parents=True,exist_ok=True)
        for filename in ['Model_00.xml','Parameters_00.xml','project.ini']:
            shutil.copy2(state/filename,destination/filename)
        (destination/'Interface.xml').write_text('<Interfaces />\n',encoding='utf8')
        j=copy.deepcopy(base);j.update(id=base['id']+'-reloadfirst',config=str((destination/'project.ini').relative_to(ROOT)).replace('\\','/'),
                                      input_ids=[1],roundtrip=True,trace=False,comparison_original=base['id'])
        jobs[j['id']]=j
    for base in [controls[0],controls[2]]:
        j=copy.deepcopy(base);j.update(id=base['id']+'-third',roundtrip=False,trace=False,comparison_original=base['id']);jobs[j['id']]=j
    equivalent=next(j for j in recovered if j['id']=='G30fd64096ec7')
    for base,origin in [(controls[0],'saved'),(equivalent,'reconstructed')]:
        j=copy.deepcopy(base);j.update(id=base['id']+'-assembly-control',input_ids=[45,22,51,129],roundtrip=True,trace=True,
                                      equivalence_control='NT45_saved_vs_reconstructed',control_origin=origin);jobs[j['id']]=j
    for kind in ['learner','trainer']:
        base=next(j for j in recovered if j['kind']==kind and j['target_id']==111)
        j=copy.deepcopy(base);j.update(id=base['id']+'-five111',input_ids=[111]*5,roundtrip=False,trace=True,frozen_state_reference_id=111);jobs[j['id']]=j
        folder=threshold_folder(base)
        j=copy.deepcopy(base);j.update(id=base['id']+'-five111-training-threshold',input_ids=[111]*5,roundtrip=False,trace=True,
             config=str((folder/'project.ini').relative_to(ROOT)).replace('\\','/'),threshold_control=True,
             protocol_note='Fixed physical graph, learning disabled; archived TrainingLTZThreshold isolates LTZone feedback. Not a classification comparison.')
        j['base_physical_sha256']=base['physical_sha256'];j['physical_sha256']=fingerprint(ET.parse(folder/'Model_00.xml').getroot())
        jobs[j['id']]=j
    for base in [controls[0],next(j for j in recovered if j['kind']=='learner' and j['target_id']==22)]:
        j=copy.deepcopy(base);j.update(id=base['id']+'-rounded4',precision_decimals=4,roundtrip=False,trace=True)
        j.pop('input_ids',None);jobs[j['id']]=j
    # Final fixed models provide separate input-transition traces, not a claim
    # to reproduce the historical evolution of weights while learning.
    for target in [22,37,129]:
        cold=next(r for r in evidence['cold'] if r['kind']=='learner' and r['id']==target)
        for after in [37,129]:
            if target not in [22,after]:continue
            reference=cold if target==22 else next(r for r in evidence['warm'] if r['repeat']==1 and r['from_index']==1 and r['to_index']==(2 if target==37 else 9))
            base=lookup[('learner',tuple(reference['dendrites']),tuple(reference['synapses']))]
            j=copy.deepcopy(base);j.update(id=base['id']+f'-transition22to{after}',input_ids=[22]+[after]*5,roundtrip=False,trace=True,target_id=after,frozen_state_reference_id=target)
            j['target_class']=(target-1)//50+1;j['frozen_state_source']=reference['source']
            jobs[j['id']]=j
            if target==22:
                folder=threshold_folder(base);j=copy.deepcopy(j)
                j.update(id=base['id']+f'-transition22to{after}-training-threshold',threshold_control=True,
                         config=str((folder/'project.ini').relative_to(ROOT)).replace('\\','/'),base_physical_sha256=base['physical_sha256'],
                         physical_sha256=fingerprint(ET.parse(folder/'Model_00.xml').getroot()))
                jobs[j['id']]=j
    save(CONFIG/'protocol-jobs.json',list(jobs.values()));save(OUT/'protocol-references.json',refs);save(OUT/'protocol-source-gaps.json',gaps)
    print('Protocol jobs',len(jobs),'historical columns',len(refs),'unmapped structures',len(gaps))
if __name__=='__main__':main()
