"""Distinguish exact executable retention from complete intermediate source capture."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save,sha

pool={sha(p):str(p.relative_to(ROOT)).replace('\\','/') for p in (WORK/'variants/controller-sources').rglob('*') if p.is_file()}
rows=[]
for p in sorted((WORK/'variants').glob('*.json')):
 v=load(p)
 if 'binary' not in v:continue
 patch=WORK/'variants'/(v['id']+'-controller.patch')
 rows.append({'variant':v['id'],'binary_retained_and_sha256_verified':(ROOT/v['binary']).exists() and sha(ROOT/v['binary'])==v['binary_sha256'],
  'controller_source_identical_snapshot':pool.get(v['controller_sha256']),'training_adapter_identical_snapshot':pool.get(v['training_adapter_sha256']),
  'tracked_files_patch_retained':patch.exists() and sha(patch)==v['controller_patch_sha256'],'sdk_commit':v['pulselib_sha'],'rdk_commit':v['rdk_sha'],
  'boundary':'An absent separate inc snapshot is a source-rebuild limitation; it does not erase the exact retained executable or its native observations.'})
save(WORK/'source-availability.json',rows)
assert all(r['binary_retained_and_sha256_verified'] and r['tracked_files_patch_retained'] for r in rows)
print('Verified binaries and tracked-source patches:',len(rows),'variants')
