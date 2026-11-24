"""Separate inference order from geometry for the FO model matching archival d/s."""
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,load,save,sha
from run import supervise

original=load(CONFIG/'InferenceJobs/FO/factor/reference/learner-22-r1.json')
model=(ROOT/original['legacy_job']['config']).parent/'Model_00.xml';source_hash=sha(model)
records=[]
for label,backend,preserve in [('manual','VB',False),('native-order','VB',True),('order-disabled','FO',True),('manual-reversal','VB',False)]:
 name='NL22-FO-'+label;out=WORK/'geometry-engine-controls'/name
 if (out/'process.json').exists() and load(out/'process.json')['status']=='completed':continue
 m=copy.deepcopy(original);m['variant']=load(WORK/'variants'/(backend+'.json'));m['legacy_job'].update(id=name,independent_reset=False,preserve_native_order=preserve,roundtrip=True)
 path=CONFIG/'GeometryEngineControls'/(name+'.json');save(path,m)
 assert sha(model)==source_hash
 records.append(supervise(ROOT/m['variant']['binary'],path,out,'legacy',1,0,660))
 assert sha(model)==source_hash
save(WORK/'geometry-engine-completion.json',{'completed':all(r['status']=='completed' for r in records),'source_model_sha256':source_hash,'conditions':4,'source_training':'FO/factor/learner-22-r1','geometry':'Matches archived NL22 d and s; complete physical equality to historical model is not asserted'})
