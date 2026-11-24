"""Prepare the complete archived project with original activity and frozen training."""
import copy,json,re,shutil,sys,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,PLAN,CONFIG,OUT,param,save,find_subject,internal_links,write_config
CONTEXT_INPUTS=[1,22,45,51,60,64,84,90,110,129,132,134]
def main():
    data=json.loads(PLAN.read_text(encoding='utf8'));source=ROOT/'Bin/Configs/StructTrainClassic/Autocreate2022.03.11 11_12_05'
    folder=CONFIG/'FullContext';folder.mkdir(parents=True,exist_ok=True)
    for filename in ['Model_00.xml','Parameters_00.xml']:
        tree=ET.parse(source/filename)
        for node in tree.getroot().iter():
            cls=node.get('Class')
            if cls in ['NNeuronTrainer','NSpikeClassifier','NSPNeuronGen']:
                param(node,'StructureBuildMode',0)
            if cls in ['NNeuronTrainer','NSpikeClassifier']:
                param(node,'IsNeedToTrain',0,'bool');param(node,'EnableDebug',0,'bool')
                if cls=='NNeuronTrainer':param(node,'CalculateMode',6)
                if cls=='NSpikeClassifier':param(node,'DataFromFile',0,'bool')
                fixed=node.findtext('Parameters/FixedLTZThreshold')
                if fixed is not None:param(node,'LTZThreshold',fixed,'double')
                if cls=='NNeuronTrainer':
                    zone=node.find('Components/Neuron/Components/LTZone')
                    if zone is not None:param(zone,'Threshold',fixed,'double')
                    for source_node in node.findall('Components/*'):
                        if source_node.get('Class')=='NPulseGeneratorTransit':
                            param(source_node,'UseTransitSignal',1,'bool');param(source_node,'Frequency',0,'double')
        # The active native classifier propagates SpikesFrequency to its frozen
        # trainers during Init. Prepare that documented value explicitly so the
        # static graph comparison includes the actual initialized protocol.
        for m in data['models']:
            if m['project']!=source.name or not m['effective_active']:continue
            trainer=find_subject(tree.getroot(),m['component'])
            for source_node in trainer.findall('Components/*'):
                if source_node.get('Class')=='NPulseGeneratorTransit':
                    param(source_node,'Frequency',trainer.findtext('Parameters/SpikesFrequency'),'double')
        ET.indent(tree,space='\t');tree.write(folder/filename,encoding='utf8')
    project=(source/'project.ini').read_text(encoding='utf-8-sig')
    for name,val in {'ProjectAutoSaveFlag':0,'ProjectAutoSaveStateFlag':0,'DebugModeFlag':0,'MinInterstepsInterval':0,'InitAfterLoadFlag':0,'ResetAfterLoadFlag':0}.items():
        project=re.sub(rf'(<{name}>).*?(</{name}>)',lambda m:m[1]+str(val)+m[2],project)
    (folder/'project.ini').write_text(project,encoding='utf8');(folder/'Interface.xml').write_text('<Interfaces />\n',encoding='utf8')
    components=[m for m in data['models'] if m['project']==source.name]
    subjects=[{'subject_path':m['component'].removeprefix('Model.'),'dendrites':m['dendrites'],'synapses':m['synapses']} for m in components]
    classifiers=sorted({s['subject_path'].rsplit('.',1)[0] for s in subjects})
    jobs=[]
    for m in components:
        if not m['training_metadata_matches_graph']:continue
        path=m['component'].removeprefix('Model.')
        j={'id':m['id']+'-full-context','kind':'trainer','origin':'full_context','source_model':m['id'],'target_id':m['saved_training_id'],
           'target_class':(m['saved_training_id']-1)//50+1,'dendrites':m['dendrites'],'synapses':m['synapses'],
           'subject_path':path,'input_owner':path.rsplit('.',1)[0],'context_subjects':subjects,'context_classifiers':classifiers,
           'config':str((folder/'project.ini').relative_to(ROOT)).replace('\\','/'),'trace':True,'roundtrip':bool(m['effective_active']),
           'protocol_note':'Original component activity and all parent/lateral links retained. All 18 trainers frozen, sources switched to native classifier inference transit mode, retired file input disabled.'}
        if not m['effective_active']:j['input_ids']=[m['saved_training_id'],22,51,129]
        else:
            j['input_ids']=CONTEXT_INPUTS
            j['protocol_note']+=' Paired 12-input context diagnostic; independent of primary 150-input comparisons.'
        jobs.append(j)
    original=ET.parse(source/'Model_00.xml').getroot();m=next(m for m in components if m['id']=='M018')
    subject=copy.deepcopy(find_subject(original,m['component']))
    for child in subject.findall('Components/*'):
        if child.get('Class')=='NPulseGeneratorTransit':
            param(child,'UseTransitSignal',1,'bool')
            param(child,'Frequency',subject.findtext('Parameters/SpikesFrequency'),'double')
    driven=CONFIG/'Saved/M018/parent-driven'
    root=write_config(driven,original,subject,internal_links(original,m['component']),(source/'project.ini').read_text(encoding='utf-8-sig'),True)
    for filename in ['Model_00.xml','Parameters_00.xml']:
        tree=ET.parse(driven/filename)
        for i in range(1,6):
            node=tree.getroot().find(f'Model/Components/Drive{i}');node.remove(node.find('Parameters'))
            node.insert(0,copy.deepcopy(original.find(f'Model/Components/SpikeClassifier9/Components/Source{i}/Parameters')))
        ET.indent(tree,space='\t');tree.write(driven/filename,encoding='utf8')
    jobs.append({'id':'M018-parent-driven','kind':'trainer','origin':'parent_drive_control','source_model':'M018','target_id':132,'target_class':3,
                 'dendrites':m['dendrites'],'synapses':m['synapses'],'config':str((driven/'project.ini').relative_to(ROOT)).replace('\\','/'),
                 'trace':True,'roundtrip':True,'reset_drive_on_equal_pattern':False,
                 'protocol_note':'Isolated M018 with original parent-generator scalar parameters and native transit sources; no sibling/lateral competition.'})
    sampled=copy.deepcopy(jobs[-1]);sampled.update(id='M018-parent-driven-context12',input_ids=CONTEXT_INPUTS)
    jobs.append(sampled)
    autonomous=copy.deepcopy(sampled)
    autonomous.update(id='M018-autonomous-context12',origin='autonomous_context_control',
                      config='Bin/Configs/StructTrainClassic/LegacyInference/Saved/M018/preserved/project.ini',
                      protocol_note='Original autonomous M018; the same ordered 12 inputs as the parent-driven and full-context controls.')
    autonomous.pop('reset_drive_on_equal_pattern',None)
    jobs.append(autonomous)
    save(CONFIG/'context-jobs.json',jobs);print('Prepared full context and parent-drive control:',len(jobs),'jobs,',len(subjects),'frozen trainers')
if __name__=='__main__':main()
