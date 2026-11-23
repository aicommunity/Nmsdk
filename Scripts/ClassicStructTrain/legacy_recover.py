"""Recover frozen physical states from documented d/s and archived cell profiles."""
from pathlib import Path
import copy,hashlib,json,re,sys,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,CONFIG,OUT,save,param,find_subject,write_config

IGNORED={'Coord','DebugSysEventsMask','MemoryMonitor','MaxCalculationDuration','CalculationDurationThreshold','EnableDebug',
 'InputPattern','TrainingPattern','TrainingDendIndexes','TrainingSynapsisNum','DendriteLength','NumSynapse','InitialSomaPotential',
 'AdditionalInputPattern','PrevInputPattern','DendriteNeuronAmplitude','NeuronAmplitude','SomaNeuronAmplitude','Output','DataFromFile','Delay'}
def canonical(value):
    parts=(value or '').split()
    try:return [float(v) for v in parts]
    except ValueError:return ' '.join(parts)
def physical(root):
    result={}
    def walk(node,path):
        ps=node.find('Parameters')
        params={p.tag:canonical(p.text) for p in ps if p.tag not in IGNORED and int(p.get('IoType','17'))&1} if ps is not None else {}
        result[path]={'class':node.get('Class'),'parameters':params}
        for c in node.findall('Components/*'):walk(c,path+'.'+c.tag)
    subject=root.find('Model/Components/Subject');full=subject is None
    walk(root.find('Model') if full else subject,'Model' if full else 'Subject')
    links=set()
    for group in root.iter('Links'):
        for e in group:
            item=e.find('Item')
            if item is None:continue
            for c in e.findall('Connector'):
                if full or ((item.text or '').startswith('Subject.') and (c.text or '').startswith('Subject.')):
                    links.add((item.text,item.get('Name'),item.get('Index','-1'),c.text,c.get('Name'),c.get('Index','-1')))
    return {'nodes':result,'links':sorted(links)}
def fingerprint(root):return hashlib.sha256(json.dumps(physical(root),sort_keys=True).encode()).hexdigest()

def recover_subject(donor,d,s,kind,pattern):
    subject=copy.deepcopy(donor);subject.tag='Subject'
    neuron=subject.find('Components/Neuron');old=copy.deepcopy(neuron.find('Components'))
    comps=neuron.find('Components');comps.clear()
    for c in old:
        if not (re.fullmatch(r'Dendrite\d+_\d+',c.tag) or re.fullmatch(r'Soma\d+',c.tag)):comps.append(copy.deepcopy(c))
    # Known physical settings are copied by role. No threshold/resistance fitting.
    for i in range(1,6):
        soma=copy.deepcopy(old.find(f'Soma{i}'));comps.append(soma)
        base=old.find(f'Dendrite{i}_1')
        terminals=[c for c in old if re.fullmatch(rf'Dendrite{i}_\d+',c.tag)]
        terminal=max(terminals,key=lambda n:int(n.tag.rsplit('_',1)[1]))
        first=terminal.find('Components/ExcSynapse1')
        extra=terminal.find('Components/ExcSynapse2')
        if extra is None:
            extra=next((c.find('Components/ExcSynapse2') for c in old if c.find('Components/ExcSynapse2') is not None),None)
        for j in range(1,d[i-1]+1):
            cell=copy.deepcopy(base);cell.tag=f'Dendrite{i}_{j}'
            n=s[i-1] if j==d[i-1] else 1
            param(cell,'NumExcitatorySynapses',n)
            children=cell.find('Components')
            for c in list(children):
                if c.tag.startswith('ExcSynapse'):children.remove(c)
            for k in range(1,n+1):
                syn=copy.deepcopy(first if k==1 or extra is None else extra);syn.tag=f'ExcSynapse{k}';children.append(syn)
                if k>1:param(syn,'Resistance',subject.findtext('Parameters/SynapseResistanceStep'),'double')
            comps.append(cell)
    param(neuron,'NumDendriteMembranePartsVec',' '.join(map(str,d)),'std::vector<int>')
    param(neuron,'NumSomaMembraneParts',5)
    for name,values in [('TrainingDendIndexes',d),('TrainingSynapsisNum',s),('TrainingPattern',pattern)]:
        p=param(neuron,name,'\n'.join(map(str,values)),'MDMatrix<double>');p.set('Rows','5');p.set('Cols','1')
    if kind=='learner':
        param(subject,'DendriteLength',' '.join(map(str,d)),'std::vector<int>');param(subject,'NumSynapse',' '.join(map(str,s)),'std::vector<int>')
    p=param(subject,'InputPattern','\n'.join(map(str,pattern)),'MDMatrix<double>');p.set('Rows','5');p.set('Cols','1')
    # Recreate the archived one-way dendritic chains and native channel inputs.
    links=ET.Element('Links',{'Type':'ULinksList','Size':'0'})
    edges=set()
    def edge(a,ao,b,bi):edges.add((a,ao,b,bi))
    for i in range(1,6):
        soma=f'Subject.Neuron.Soma{i}'
        for channel in ['ExcChannel','InhChannel']:
            edge(soma+'.'+channel,'Output','Subject.Neuron.LTZone','Inputs')
        edge('Subject.Neuron.LTZone','Output',soma,'InputFeedbackSignal')
        terminal=f'Subject.Neuron.Dendrite{i}_{d[i-1]}'
        edge('Subject.Neuron.PosGenerator','Output',terminal+'.InhChannel','ChannelInputs')
        edge('Subject.Neuron.NegGenerator','Output',terminal+'.ExcChannel','ChannelInputs')
        for k in range(1,s[i-1]+1):edge(f'Subject.Source{i}','Output',terminal+f'.ExcSynapse{k}','Input')
        for j in range(1,d[i-1]+1):
            cell=f'Subject.Neuron.Dendrite{i}_{j}';previous=soma if j==1 else f'Subject.Neuron.Dendrite{i}_{j-1}'
            for channel in ['ExcChannel','InhChannel']:edge(cell+'.'+channel,'Output',previous+'.'+channel,'ChannelInputs')
    for cell in comps:
        if not (cell.tag.startswith('Dendrite') or cell.tag.startswith('Soma')):continue
        for syn in cell.findall('Components/*'):
            if re.fullmatch(r'(Exc|Inh)Synapse\d+',syn.tag):
                channel='ExcChannel' if syn.tag.startswith('Exc') else 'InhChannel'
                edge('Subject.Neuron.'+cell.tag+'.'+syn.tag,'Output','Subject.Neuron.'+cell.tag+'.'+channel,'SynapticInputs')
    for a,ao,b,bi in sorted(edges):
        e=ET.SubElement(links,'elem',{'Type':'ULink'})
        ET.SubElement(e,'Item',{'Type':'ULinkSide','Index':'-1','Name':ao}).text=a
        ET.SubElement(e,'Connector',{'Type':'ULinkSide','Index':'-1','Name':bi}).text=b
    links.set('Size',str(len(links)))
    return subject,links

def main():
    data=json.loads(PLAN.read_text(encoding='utf8'));rows=copy.deepcopy(data['restoration_rows'])
    # Add only an unambiguous donor for the same algorithm, input ID and d.
    resolutions=[]
    for row in rows:
        if row['complete']:continue
        matches=[r for r in rows if r['complete'] and r['kind']==row['kind'] and str(r.get('target'))==str(row.get('target')) and r['dendrites']==row['dendrites']]
        for m in data['models']:
            if m['training_metadata_matches_graph'] and row['kind']=='trainer' and m['saved_training_id']==row.get('target') and m['dendrites']==row['dendrites']:
                matches.append({'id':m['id'],'synapses':m['synapses']})
        choices={tuple(m['synapses']) for m in matches}
        if len(choices)==1:
            row['synapses']=list(next(iter(choices)));row['complete']=True;row['completion_donors']=[m['id'] for m in matches]
            resolutions.append({'row':row['id'],'donors':row['completion_donors'],'synapses':row['synapses']})
    donors={}
    for kind,ident in [('trainer','M001'),('learner','M019')]:
        m=next(m for m in data['models'] if m['id']==ident);source=ROOT/'Bin/Configs/StructTrainClassic'/m['project']
        root=ET.parse(source/'Model_00.xml').getroot();donors[kind]=(root,find_subject(root,m['component']),(source/'project.ini').read_text(encoding='utf-8-sig'),m)
    jobs=[];mapping=[];by_hash={};by_structure={}
    for row in rows:
        if not row['complete']:mapping.append({'row':row['id'],'status':'missing_synapses','source':row['source']});continue
        structure_key=(row['kind'],tuple(row['dendrites']),tuple(row['synapses']))
        if structure_key in by_structure:
            mapping.append({'row':row['id'],'job':by_structure[structure_key]['id'],'source':row['source'],'target':row.get('target'),'epoch':row.get('epoch'),
                            'group':row['group'],'snapshot':row.get('snapshot'),'status':'constructed','completion_donors':row.get('completion_donors',[])})
            continue
        kind=row['kind'];tree,donor,project,origin=donors[kind]
        target=row.get('target');target_id=int(target) if str(target).isdigit() and 1<=int(target)<=150 else 51
        pattern=data['dataset'][target_id-1]['pattern']
        subject,links=recover_subject(donor,row['dendrites'],row['synapses'],kind,pattern)
        # Candidate identity already includes every constructed physical setting.
        folder=CONFIG/'Recovered'/('G'+row['structure_group'])
        root=write_config(folder,tree,subject,links,project,True)
        signature=fingerprint(root)
        if signature not in by_hash:
            job={'id':'G'+row['structure_group'],'kind':kind,'origin':'reconstructed','target_id':target_id,'target_class':(target_id-1)//50+1,
                 'dendrites':row['dendrites'],'synapses':row['synapses'],'config':str((folder/'project.ini').relative_to(ROOT)).replace('\\','/'),
                 'profile_donor':origin['id'],'physical_sha256':signature,'trace':True,'roundtrip':True,'activation':'all_active',
                 'training_metadata_provenance':'reconstructed d/s; TrainingPattern is a control stimulus, not evidence of a unique learned example'}
            jobs.append(job);by_hash[signature]=job
        by_structure[structure_key]=by_hash[signature]
        mapping.append({'row':row['id'],'job':by_hash[signature]['id'],'source':row['source'],'target':row.get('target'),'epoch':row.get('epoch'),
                        'group':row['group'],'snapshot':row.get('snapshot'),'status':'constructed','completion_donors':row.get('completion_donors',[])})
    save(CONFIG/'recovered-jobs.json',jobs);save(OUT/'recovered-mapping.json',mapping);save(OUT/'partial-resolutions.json',resolutions)
    save(OUT/'recovery-summary.json',{'unique_physical_states':len(jobs),'source_rows':len(rows),'completed_partial_rows':len(resolutions),
                                    'unresolved_rows':sum(m['status']!='constructed' for m in mapping),'profiles':{'trainer':'M001','learner':'M019'}})
    print('Recovered',len(jobs),'unique physical states;',len(resolutions),'partial rows completed;',sum(m['status']!='constructed' for m in mapping),'unresolved')
if __name__=='__main__':main()
