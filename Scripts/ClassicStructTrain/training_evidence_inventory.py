"""Inventory study evidence without traversing external package junctions."""
from pathlib import Path
from collections import defaultdict
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import WORK,CONFIG,save

groups=defaultdict(lambda:{'files':0,'bytes':0})
for start in [WORK,CONFIG]:
 for p in start.rglob('*'):
  if p.is_file():
   key=start.name+'/'+p.relative_to(start).parts[0];groups[key]['files']+=1;groups[key]['bytes']+=p.stat().st_size
save(WORK/'evidence-inventory.json',dict(groups))
print(json.dumps(dict(groups),ensure_ascii=False,indent=2))
