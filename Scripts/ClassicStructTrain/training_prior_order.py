"""Direct order reversal on the exact NL22 configuration used by the prior report."""
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,BASE,load,save,sha
from run import supervise

science=load(ROOT/'Reports/StructTrainClassic/LegacyChecks-20261123/scientific-comparison-data.json')
identifier=next(r['job'] for r in science['recognition'] if r['label']=='NL22')
job=next(r for r in load(ROOT/'Bin/Configs/StructTrainClassic/LegacyInference/recovered-jobs.json') if r['id']==identifier)
model=(ROOT/job['config']).parent/'Model_00.xml';before=sha(model);results=[]
for label,preserve in [('manual',False),('native-order',True),('manual-reversal',False)]:
 name='prior-NL22-'+label;out=WORK/'prior-order-controls'/name
 if (out/'process.json').exists() and load(out/'process.json')['status']=='completed':continue
 m=copy.deepcopy(load(BASE));m['variant']=load(WORK/'variants/VB.json');m['legacy_job']=copy.deepcopy(job)
 m['legacy_job'].update(id=name,independent_reset=False,preserve_native_order=preserve,roundtrip=True)
 path=CONFIG/'PriorOrderControls'/(name+'.json');save(path,m);assert sha(model)==before
 results.append(supervise(ROOT/m['variant']['binary'],path,out,'legacy',1,0,660));assert sha(model)==before
save(WORK/'prior-order-completion.json',{'completed':all(r['status']=='completed' for r in results),'conditions':3,'original_job':identifier,'original_model':str(model.relative_to(ROOT)).replace('\\','/'),'source_model_sha256':before,'origin':'Reconstructed archival geometry, exactly the configuration used in ScientificComparisons; not asserted to contain all unknown 2022 physical parameters'})
