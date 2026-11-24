"""Trace factory overrides separately from constructor-default changes."""
from pathlib import Path
import sys,subprocess,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save,sha

repo=ROOT/'Libraries/Nmsdk-PulseLib';dest=WORK/'code-history';dest.mkdir(exist_ok=True);records=[]
for ref in ['b8aad55ae895e55a938039ae4f90c85aad1a0046','5f3f06d','0be546f','98d1edc14b30a10f9aee79be4aecbdb622fb4570','871097806f1d468ebdada88fc85c8d68f1c0952d']:
 commit=subprocess.check_output(['git','rev-parse',ref],cwd=repo,text=True).strip()
 source=subprocess.check_output(['git','show',commit+':Core/NPulseLibrary.cpp'],cwd=repo)
 path=dest/(commit+'-NPulseLibrary.cpp.txt');path.write_bytes(source)
 matches=[line.decode('ascii',errors='replace').strip() for line in source.splitlines() if b'syn->Resistance=' in line or b'syn->DissociationTC=0.005' in line or b'UploadClass("NPSynapseBio' in line]
 records.append({'commit':commit,'author_date':subprocess.check_output(['git','show','-s','--format=%aI',commit],cwd=repo,text=True).strip(),'source':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),'factory_lines':matches})
save(WORK/'factory-override-history.json',{'records':records,'finding':'The Bio factory resistance 86 MOhm and dissociation 5 ms exist in 2021 and both 2022 constructor-default anchor revisions. Constructor changes do not establish a universal physical synapse profile.'})
history=load(WORK/'history.json')
for commit,factor in [('b8aad55ae895e55a938039ae4f90c85aad1a0046','Фабричный профиль Bio до исторических опытов'),('98d1edc14b30a10f9aee79be4aecbdb622fb4570','Расширение фабричного профиля Bio2')]:
 if not any(r['sha'].startswith(commit[:7]) for r in history['commits']):
  raw=subprocess.check_output(['git','show','-s','--format=%aI%n%s',commit],cwd=repo,text=True).splitlines()
  history['commits'].append({'sha':commit,'author_date':raw[0],'subject':raw[1],'factor':factor,'status':'Сопоставлены исходники фабрики и фактические XML; источник не равен значениям конструктора'})
history['commits'].sort(key=lambda r:r['author_date']);save(WORK/'history.json',history)
print('Preserved five factory revisions and extended the dated history register')
