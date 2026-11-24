"""Lossless deduplicated scientific evidence; restore refuses conflicting files."""
from pathlib import Path,PurePosixPath
import sys,json,gzip,hashlib,zipfile,argparse,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,SOURCE,OLD,DELIVERY,load,save,sha
from report_paths import PLANS,report_path

DEST=WORK/'Evidence'
def digest_stream(stream):
 h=hashlib.sha256()
 for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def code_snapshots():
 target=WORK/'code-versions';target.mkdir(exist_ok=True)
 (target/'all-submodules.txt').write_bytes(subprocess.check_output(['git','submodule','status','--recursive'],cwd=ROOT))
 (target/'root-working.patch').write_bytes(subprocess.check_output(['git','diff','--binary','--full-index','HEAD'],cwd=ROOT))
 save(target/'runtime-dlls.json',[{'file':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'size':p.stat().st_size} for p in (ROOT/'Bin/Platform/Win').glob('*.dll')])
 variants=[load(p) for p in (WORK/'variants').glob('*.json') if 'binary' in load(p)]
 sources={'PulseLib':(ROOT/'Libraries/Nmsdk-PulseLib','9f3c5131192521d23b77be062ebd9b97298f50d9','pulselib_sha'),
          'Rdk':(ROOT/'Rdk','f0d6078d0a7fb45d689d8e0e06c8426e6a56b5ac','rdk_sha')}
 records=[]
 for name,(repo,base,key) in sources.items():
  for commit in sorted({v[key] for v in variants}):
   patch=target/(name+'-'+commit+'.patch');patch.write_bytes(subprocess.check_output(['git','diff','--binary','--full-index',base,commit],cwd=repo))
   records.append({'module':name,'baseline':base,'commit':commit,'patch':str(patch.relative_to(ROOT)).replace('\\','/'),'sha256':sha(patch)})
 save(target/'manifest.json',records)

def pack():
 assert load(WORK/'completion-audit.json')['passed'],'Pack only a completed audited study'
 assert not DEST.exists(),'Do not overwrite an existing evidence bundle'
 code_snapshots();files=[]
 for prefix in ['runs','inference','engine-controls','geometry-engine-controls','prior-order-controls','interrupted-inference','interrupted-diagnostics','variants','code-versions','code-history','history','factors','gates','template','excel-charts']:
  folder=WORK/prefix
  if folder.exists():files.extend(p for p in folder.rglob('*') if p.is_file())
 files.extend(p for p in WORK.iterdir() if p.is_file() and p.suffix in ['.json','.log','.ndjson','.txt'])
 files.extend(p for p in CONFIG.rglob('*') if p.is_file() and not p.name.endswith('.lock'))
 files.extend(p for p in (SOURCE/'Эксперименты').rglob('*') if p.is_file() and p.suffix.lower() in ['.docx','.xlsx','.txt','.xml','.ini','.png','.jpg','.jpeg','.csv','.dat'])
 files.append(SOURCE/'ВКР_ЕременкоЕА.docx')
 files.extend(OLD/name for name in ['assessment.json','scientific-comparison-data.json','digitized-waves.json'])
 previous=load(OLD/'assessment.json')['first_by_job']
 for row in load(OLD/'scientific-comparison-data.json')['recognition']:
  folder=report_path(previous[row['job']]['directory'])
  files.extend(p for p in folder.rglob('*') if p.is_file())
 prior_source=ROOT/load(WORK/'prior-order-completion.json')['original_model']
 files.extend(p for p in prior_source.parent.rglob('*') if p.is_file())
 reports=[DELIVERY/(name+suffix) for name in ('ScientificComparisons','TrainingReproducibility')
          for suffix in ('.docx','.xlsx')]
 reports.append(PLANS/'TrainingReproducibilityPlan.docx')
 files.extend(p for p in reports if p.is_file())
 binaries={ROOT/load(WORK/'reference.json')['native_reference']}
 binaries.update(ROOT/load(p)['binary'] for p in (WORK/'variants').glob('*.json') if 'binary' in load(p))
 files.extend(binaries)
 files.extend(p.with_suffix('.ini') for p in binaries if p.with_suffix('.ini').exists())
 files.extend(p for p in (ROOT/'Scripts/ClassicStructTrain').iterdir() if p.is_file() and p.suffix in ['.py','.ps1','.mjs','.cpp','.inc'])
 files.append(ROOT/'Tests/Integration/Libraries/CMakeLists.txt')
 files=sorted(set(files));DEST.mkdir();records=[];blobs={};part=0;part_bytes=0;archive=None;original_bytes=0
 try:
  for p in files:
   relative=str(p.relative_to(ROOT)).replace('\\','/');size=p.stat().st_size;digest=sha(p);original_bytes+=size
   if digest not in blobs:
    if archive is None or part_bytes+size>256*1024*1024:
     if archive:archive.close()
     part+=1;part_bytes=0;archive=zipfile.ZipFile(DEST/f'blobs-{part:03}.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)
    archive.write(p,'sha256/'+digest);blobs[digest]={'part':part,'size':size};part_bytes+=size
   records.append({'path':relative,'sha256':digest,'size':size,'part':blobs[digest]['part']})
 finally:
  if archive:archive.close()
 with gzip.open(DEST/'index.json.gz','wt',encoding='utf8') as stream:json.dump({'format':'nmsdk-scientific-evidence-v1','files':records},stream,ensure_ascii=False,separators=(',',':'))
 summary={'files':len(records),'unique_blobs':len(blobs),'original_bytes':original_bytes,'unique_uncompressed_bytes':sum(r['size'] for r in blobs.values()),
  'parts':[{'file':p.name,'size':p.stat().st_size,'sha256':sha(p)} for p in sorted(DEST.glob('*.zip'))],
  'index_sha256':sha(DEST/'index.json.gz'),'restore':'Scripts/ClassicStructTrain/training_evidence_bundle.py restore --root <repository root>; conflicting existing files are never overwritten'}
 save(DEST/'bundle.json',summary);verify();print(json.dumps(summary,ensure_ascii=False,indent=2))

def index():
 with gzip.open(DEST/'index.json.gz','rt',encoding='utf8') as stream:return json.load(stream)['files']

def verify():
 summary=load(DEST/'bundle.json');assert sha(DEST/'index.json.gz')==summary['index_sha256']
 records=index();checked=set()
 for part in summary['parts']:
  path=DEST/part['file'];assert sha(path)==part['sha256']
  with zipfile.ZipFile(path) as z:
   for r in records:
    if r['part']!=int(path.stem.split('-')[-1]) or r['sha256'] in checked:continue
    with z.open('sha256/'+r['sha256']) as stream:assert digest_stream(stream)==r['sha256'],r
    checked.add(r['sha256'])
 assert len(checked)==summary['unique_blobs']
 save(DEST/'verification.json',{'passed':True,'files':len(records),'verified_unique_blobs':len(checked),'lossless':True})

def restore(root):
 verify();root=root.resolve()
 for part in load(DEST/'bundle.json')['parts']:
  with zipfile.ZipFile(DEST/part['file']) as z:
   number=int(Path(part['file']).stem.split('-')[-1])
   for r in index():
    if r['part']!=number:continue
    rel=PurePosixPath(r['path']);assert not rel.is_absolute() and '..' not in rel.parts
    target=report_path(Path(*rel.parts),root=root).resolve();assert target.is_relative_to(root)
    if target.exists():assert target.is_file() and sha(target)==r['sha256'],'Conflicting existing file: '+str(target);continue
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as output,z.open('sha256/'+r['sha256']) as source:
     for chunk in iter(lambda:source.read(1024*1024),b''):output.write(chunk)
    assert sha(target)==r['sha256']

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=['pack','verify','restore']);parser.add_argument('--root',type=Path);args=parser.parse_args()
 if args.action=='pack':pack()
 elif args.action=='verify':verify()
 else:assert args.root;restore(args.root)
