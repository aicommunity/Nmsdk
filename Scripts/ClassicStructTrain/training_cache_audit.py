"""Independently verify every reused inference including ordered saved components."""
from pathlib import Path
import sys,json
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parent))
from report_paths import report_path
from training_repro import ROOT,WORK,CONFIG,load,save,component_order,sha
from training_report_data import inference_result
from legacy_recover import physical
def manifest(folder):
 meta=folder/'process.json'
 if meta.exists():
  m=load(meta);return load(m['command'][m['command'].index('--manifest')+1]),m['binary_sha256']
 relative=folder.relative_to(WORK/'inference');variant,phase,backend,name=relative.parts
 path=CONFIG/'InferenceJobs'/variant/phase/backend/(name+'.json')
 engine=backend.removesuffix('-own')
 binary_hash=load(WORK/'reference.json')['native_sha256'] if engine=='reference' else load(WORK/'variants'/(engine+'.json'))['binary_sha256']
 return load(path),binary_hash
def main():
 mismatches=[];pending=[];count=0
 for p in (WORK/'inference').glob('*/*/*/*/reuse.json'):
  target=p.parent;data=load(p);source=report_path(data['source']);seen={target}
  while (source/'reuse.json').exists() and not (source/'process.json').exists():
   assert source not in seen;seen.add(source);source=report_path(load(source/'reuse.json')['source'])
  if not (source/'process.json').exists() or load(source/'process.json')['status']!='completed':pending.append(str(p.relative_to(ROOT)));continue
  a,ah=manifest(target);b,bh=manifest(source);ar=ET.parse((ROOT/a['legacy_job']['config']).parent/'Model_00.xml').getroot();br=ET.parse((ROOT/b['legacy_job']['config']).parent/'Model_00.xml').getroot()
  pattern=lambda root:[float(v) for v in root.findtext('Model/Components/Subject/Parameters/InputPattern').split()]
  checks={'physical':physical(ar)==physical(br),'component_order':component_order(ar)==component_order(br),'initial_serialized_pattern':pattern(ar)==pattern(br),'dataset':a['dataset']==b['dataset'],'target_class':a['legacy_job']['target_class']==b['legacy_job']['target_class']}
  if ah:checks['binary']=ah==bh
  count+=1
  if not all(checks.values()):mismatches.append({'alias':str(p.relative_to(ROOT)),'source':str(source.relative_to(ROOT)),'checks':checks})
 save(WORK/'inference-reuse-audit.json',{'passed':not mismatches and not pending,'checked':count,'mismatches':mismatches,'pending':pending,'comparison':'Graph, all physical parameters, saved component order, stimulus sequence, target class and binary SHA256; alias binary from immutable packaged variant when no native target process exists'})
 print(json.dumps({'checked':count,'mismatches':len(mismatches),'pending':len(pending)}))
if __name__=='__main__':main()
