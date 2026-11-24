"""Record dated module closures and missing historical algorithm sources."""
from pathlib import Path
import sys,subprocess,hashlib,zipfile,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,OLD,DELIVERY,load,save,git,sha

def object_exists(repo,obj):
 return subprocess.run(['git','cat-file','-e',obj],cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def closure(root_sha):
 tree=git('ls-tree','-r',root_sha);modules=[]
 for line in tree.splitlines():
  head,path=line.split('\t',1);mode,typ,obj=head.split()
  if mode!='160000':continue
  repo=ROOT/path;available=repo.exists() and object_exists(repo,obj)
  row={'path':path,'sha':obj,'available':available}
  if available and 'PulseLib' in path:
   files=git('ls-tree','-r','--name-only',obj,repo=repo).splitlines()
   row['training_named_files']=[x for x in files if any(k in x.lower() for k in ['learner','trainer'])]
   row['required_classes_present']={n:any(Path(x).name==n+'.cpp' for x in files) for n in ['NNeuronLearner','NNeuronTrainer']}
  modules.append(row)
 return {'root_sha':root_sha,'author_date':git('show','-s','--format=%aI',root_sha),'modules':modules}

def main():
 candidates=['bc635671441fe8842299aee86ce0c3bd37acaea9']
 for date in ['2022-03-31T23:59:59+03:00','2022-06-27T23:59:59+03:00','2023-10-10T23:59:59+03:00']:
  candidate=git('rev-list','-1','--before='+date,'--all')
  if candidate and candidate not in candidates:candidates.append(candidate)
 closures=[closure(c) for c in candidates]
 science=load(OLD/'scientific-comparison-data.json');history=load(WORK/'history.json');experiments=[]
 for c in science['cases']:
  evidence=[r for r in history['documents'] if any(Path(r['path']).name in str(s) for s in c['sources'])]
  experiments.append({'id':c['id'],'experiment':c['title'],'sources':c['sources'],'date_evidence':evidence,
   'date_interpretation':'Office save dates and configuration histories bound document versions, not exact run dates; XLSX creation in 2015 is a template date',
   'candidate_closures':[v['root_sha'] for v in closures],
   'known_parameters':c['protocol'],'missing_parameters':'Exact executable, complete 2022 learner/trainer source, and complete per-run physical settings are not uniquely identified',
   'historical_algorithm_classification':'Partial port with adaptations, not an identified full 2022 executable'})
 pulse=ROOT/'Libraries/Nmsdk-PulseLib'
 first=git('log','--all','--reverse','--format=%H %aI','--','Core/NNeuronLearner.cpp',repo=pulse).splitlines()[0]
 results={'closures':closures,'experiments':experiments,'first_available_learner_commit':first,
  'repository_is_shallow':git('rev-parse','--is-shallow-repository',repo=pulse),
  'full_2022_experiment_build':{'status':'not_run_missing_required_sources','reason':'Dated coherent module closures do not contain both required learner/trainer class implementations. Compiling that closure would not reconstruct the documented experiment. The partial V3 port is explicitly separate.'},
  'limitation':'A candidate nearest in time is not proof of the code used by an archived experiment. Availability checks do not imply a successful historical build.'}
 save(WORK/'history-feasibility.json',results)
 print('Recorded',len(closures),'coherent module closures and',len(experiments),'experiment source records')
if __name__=='__main__':main()
