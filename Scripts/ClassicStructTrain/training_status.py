"""Compact read-only progress snapshot of actual experiment records."""
from pathlib import Path
import sys,json,collections
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,load

groups=collections.defaultdict(collections.Counter)
for p in (WORK/'runs').glob('*/*/*/process.json'):
 try:m=load(p)
 except (OSError,ValueError):continue
 variant,phase=p.relative_to(WORK/'runs').parts[:2]
 groups[variant+'/'+phase][m['status']]+=1
for k,v in sorted(groups.items()):print(k,dict(v))
for variant in ['V1C','VP1']:
 for backend in ['reference','reference-own']:
  counter=collections.Counter()
  for p in (WORK/'inference'/variant/'all'/backend).glob('*/process.json'):counter[load(p)['status']]+=1
  counter['aliases']=len(list((WORK/'inference'/variant/'all'/backend).glob('*/reuse.json')))
  print('inference',variant,backend,dict(counter))
for name in ['V1C-full-console.log','full-inference-resumed-console.log','cold-inference-additional-console.log','protocol-inference-transferred-console.log','modes-independent-console.log','schemes-transferred-console.log','warm-file-exact-console.log','stopping-engine-controls-console.log','order-live-console.log','order-live-trainer-console.log']:
 p=WORK/name
 if p.exists():print(name, ' | '.join(p.read_text(encoding='utf-8',errors='replace').splitlines()[-2:])[:280])
for p in sorted(WORK.glob('*completion*.json')):
 print(p.name,json.dumps(load(p),ensure_ascii=False)[:500])
