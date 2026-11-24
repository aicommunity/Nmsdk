"""Apply isolated research changes; keep algorithm and lifecycle factors separate."""
from pathlib import Path
import argparse,re,subprocess,hashlib
import json
ROOT=Path(__file__).resolve().parents[2]
CORE=ROOT/'Libraries/Nmsdk-PulseLib/Core'
def span(text,signature):
 start=text.index(signature);op=text.index('{',start);depth=0;state='code';i=op
 while i<len(text):
  ch=text[i];nxt=text[i:i+2]
  if state=='line':
   if ch=='\n':state='code'
  elif state=='comment':
   if nxt=='*/':state='code';i+=1
  elif state in ['"',"'"]:
   if ch=='\\':i+=1
   elif ch==state:state='code'
  elif nxt=='//':state='line';i+=1
  elif nxt=='/*':state='comment';i+=1
  elif ch in ['"',"'"]:state=ch
  elif ch=='{':depth+=1
  elif ch=='}':
   depth-=1
   if depth==0:return start,i+1
  i+=1
 raise ValueError(signature)
HELPER='''
// Research lifecycle factor: initialize newly built descendants only.
// No reset, stimulus, parameter, or stopping-criterion change is made here.
bool InitNewTrainingComponents(UContainer* node)
{
 if(!node)
  return false;
 if(node->GetActivity() && !node->IsInit())
 {
  node->Init();
  if(!node->IsInit())
   return false;
 }
 for(int i = 0; i < node->GetNumComponents(); ++i)
 {
  auto child = node->GetComponentByIndex(i);
  if(child && !InitNewTrainingComponents(child.Get()))
   return false;
 }
 return true;
}
'''
def lifecycle():
 for cls,methods,pointer in [('NNeuronLearner',['ChangeDendriteLength','ChangeSynapseNumber'],'Neuron'),('NNeuronTrainer',['SomaSynapseNormalization','SomaSynchronizePattern'],'neuron')]:
  path=CORE/(cls+'.cpp');text=path.read_text(encoding='utf8');assert 'InitNewTrainingComponents' not in text
  before={name:text[slice(*span(text,'bool '+cls+'::'+name))] for name in (['Training','EndOfLearning'] if cls=='NNeuronLearner' else ['SomaSynapseNormalization','SomaSynchronizePattern'])}
  for name in methods:
   start,end=span(text,'bool '+cls+'::'+name);body=text[start:end];needle=pointer+'->Reset();'
   if cls=='NNeuronLearner':
    index=body.rindex(needle)+len(needle);body=body[:index]+'\n if(!InitNewTrainingComponents('+pointer+'.Get()))\n  return false;'+body[index:]
   else:body=body.replace(needle,needle+'\n                if(!InitNewTrainingComponents('+pointer+'.Get()))\n                 return false;')
   text=text[:start]+body+text[end:]
  text=text.replace('namespace {','namespace {\n'+HELPER,1)
  if cls=='NNeuronLearner':
   for name,original in before.items():assert text[slice(*span(text,'bool '+cls+'::'+name))]==original,'Stop logic was changed'
  path.write_text(text,encoding='utf8')
 print('Applied lifecycle-only initialization at native structural rebuild sites')
def profile():
 p=CORE/'NPulseSynapse.cpp';t=p.read_text(encoding='utf8');start,end=span(t,'bool NPulseSynapse::ADefault');body=t[start:end]
 for old,new in [('SecretionTC=0.001;','SecretionTC=0.002;'),('DissociationTC=0.01;','DissociationTC=0.002;'),('Resistance=1.0e9;','Resistance=100000000;')]:
  assert body.count(old)==1,old;body=body.replace(old,new)
 p.write_text(t[:start]+body+t[end:],encoding='utf8');print('Applied only the documented 15 April to 27 June 2022 synapse defaults')
def single_factor(name):
 if name=='order':
  p=CORE/'NPulseNeuron.cpp';t=p.read_text(encoding='utf8');a,b=span(t,'void NPulseNeuron::UpdateComputationOrder')
  t=t[:a]+'void NPulseNeuron::UpdateComputationOrder(void)\n{\n // Research control: the explicit order routine was introduced by 8f47c01 in April 2023.\n}\n'+t[b:]
 else:
  p=CORE/'NPulseSynapse.cpp';t=p.read_text(encoding='utf8');a,b=span(t,'bool NPulseSynapse::ADefault');body=t[a:b]
  old,new={'secretion':('SecretionTC=0.001;','SecretionTC=0.002;'),'dissociation':('DissociationTC=0.01;','DissociationTC=0.002;'),'resistance':('Resistance=1.0e9;','Resistance=100000000;')}[name]
  assert body.count(old)==1;body=body.replace(old,new);t=t[:a]+body+t[b:]
 p.write_text(t,encoding='utf8');print('Applied isolated factor',name)
def archival():
 records=[]
 for cls,methods in [('NNeuronLearner',['MeasureMaxPotentialAndTime','ChangeDendriteStatus','ChangeSynapseStatus','EndOfLearning']),('NNeuronTrainer',['SomaSynapseNormalization','SomaSynchronizePattern','CalculateProcess'])]:
  path=CORE/(cls+'.cpp');current=path.read_text(encoding='utf8')
  original=subprocess.check_output(['git','show','0b03edb:Core/'+cls+'.cpp'],cwd=CORE.parent).decode('cp1251')
  for name in methods:
   sig='bool '+cls+'::'+name;old=original[slice(*span(original,sig))];adapted=old
   if cls=='NNeuronTrainer':adapted=adapted.replace('neuron->Reset();','neuron->Reset();\n if(!InitNewTrainingComponents(neuron.Get())) return false;')
   start,end=span(current,sig);current=current[:start]+adapted+current[end:]
   records.append({'class':cls,'method':name,'source':'Git 0b03edb, 10 October 2023','original_sha256':hashlib.sha256(old.encode()).hexdigest(),'adaptation':'Lifecycle-only initialization after Reset' if cls=='NNeuronTrainer' else 'No decision changes'})
  if cls=='NNeuronLearner':
   source=ROOT/'Docs/ClassicStructTrainExperiments/Эксперименты/Исследование/код CalculateProcess.txt'
   old=source.read_text(encoding='utf-8-sig');adapted=old.replace('NNeuronLearner::CalculateProcess','NNeuronLearner::Training').replace('MeasureAmpAndTime()','MeasureMaxPotentialAndTime()')
   start,end=span(current,'bool NNeuronLearner::Training');current=current[:start]+adapted+current[end:]
   records.append({'class':cls,'method':'Training','source':str(source.relative_to(ROOT)),'original_sha256':hashlib.sha256(old.encode()).hexdigest(),'adaptation':'Function and measurement method renamed to current private interfaces; loop logic retained'})
  path.write_text(current,encoding='utf8')
 work=ROOT/'Reports/StructTrainClassic/_work/TrainingReproducibility-20261123/variants';work.mkdir(parents=True,exist_ok=True)
 (work/'V3-adaptation.json').write_text(json.dumps({'methods':records,'classification':'Partial archival algorithm on modern infrastructure; not a complete 2022 binary','limitations':['Complete 2022 learner and trainer sources are absent from the available Git history.','Archived 2022 loop and earliest available 2023 decision functions have different provenances.','The archived loop does not contain the modern dendrite-freezing guard; the synapse-only schedule requires a separately documented adapter.']},ensure_ascii=False,indent=2),encoding='utf8')
 print('Applied documented partial archival algorithm; modern physical engine and lifecycle correction retained')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('factor',choices=['lifecycle','profile','archival','secretion','dissociation','resistance','order']);a=p.parse_args()
 if a.factor in ['lifecycle','profile','archival']:{'lifecycle':lifecycle,'profile':profile,'archival':archival}[a.factor]()
 else:single_factor(a.factor)
