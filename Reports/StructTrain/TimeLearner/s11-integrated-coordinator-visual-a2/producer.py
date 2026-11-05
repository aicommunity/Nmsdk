from pathlib import Path
import os,sys,json,hashlib,tarfile,io,struct,traceback,html
base=Path('/media/user/Data/TimeLearnerRefactor');out=base/'readbacks/s11-integrated-coordinator-selected-a1';out.mkdir(exist_ok=False);cache=base/'ReportsCache/integrated-coordinator-visual-a2';reports=cache/'reports';origin=base/'readbacks/s11-integrated-coordinator-visual-a2';source=base/'source-integrated-coordinator-report-reader-a2';sys.path.insert(0,str(base/'source-worker-dependency-normal-a2'));os.nice(15)
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.worker_dependency import inspect_worker_dependency
r=Reservations(base/'selected-report-metadata-reservations.sqlite3');token=None;passed=False;selection=[]
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(out/'producer.py').write_bytes(Path(__file__).read_bytes());write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'native_models_executed':0,'source_read_only':str(cache)})
try:
 states={}
 for suffix in ['a1','a2']:
  folder=base/('readbacks/s11-integrated-coordinator-visual-'+suffix);state=inspect_worker_dependency(Path(str(folder)+'-container'),Reservations(base/'report-reservations.sqlite3'),folder.name);assert state['state']=='ready' and state['reservation_state']=='released';states[suffix]=state
 write('render-prerequisites.json',states);assert json.loads((origin/'terminal.json').read_text())['report_and_checks_passed'];coverage=json.loads((origin/'coverage.json').read_text());assert coverage['native_input_overlay_views_checked']>0 and coverage['phase_reports']==16 and coverage['frozen_trial_soma_pairs']==24
 lease=r.reserve(out.name,[{'path':str(out),'access':'write'},{'path':str(cache),'access':'read'},{'path':str(origin),'access':'read'}],ttl_seconds=3600);token=lease['token'];write('reservation.json',lease);(out/'selected').mkdir();recipe=[]
 def pick(case,phase,folder,figure,view,details):
  png,svg,pdf=[folder/n for n in view['files']];assert all(p.resolve().is_relative_to(reports.resolve()) and not p.is_symlink() for p in [png,svg,pdf]);raw=png.read_bytes();assert raw.startswith(b'\x89PNG\r\n\x1a\n') and struct.unpack('>II',raw[16:24])==(1920,960)
  top=reports/(case+'--'+phase);sums=json.loads((top/'SHA256SUMS.json').read_text());assert sums[png.relative_to(top).as_posix()]==hashlib.sha256(raw).hexdigest();assert not view['downsampling'] and (view['time_view']=='overview' or view['minimum_native_tick_pixels_on_zoom']>=8)
  name='selected/'+f'{len(selection)+1:03d}.png';(out/name).write_bytes(raw);selection.append({'file':name,'case':case,'phase':phase,'source_png':str(png.relative_to(cache)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'source_svg_sha256':sha(svg),'source_pdf_sha256':sha(pdf),'figure_signal':{k:v for k,v in figure.items() if k!='views'},'view':view,'details':details})
 for row in json.loads((origin/'progress.json').read_text()):
  case,phase=row['case'],row['phase'];target=reports/row['folder'];fmt='calibration-run' if phase=='calibrate' else 'pipeline-run';recipe.append({'source_manifest_relative':row['source'],'format':fmt,'output_folder':row['folder'],'command':['python3','-m','Scripts.StructTrain.TimeLearner','report','{EXTRACTED}/'+row['source'],'--format',fmt,'--output','{CACHE}/'+row['folder']]})
  if phase=='evaluate':
   m=json.loads((target/'evaluation/manifest.json').read_text());assert not m['visual_acceptance_complete']
   picked_presentations={min(f['presentation_index'] for f in m['figures'] if f['label']==label) for label in ['target','foil']}
   for f in m['figures']:
    details={'kind':'all_frozen_trial_soma_overviews','trial_id':f['trial_id'],'label':f['label'],'presentation_index':f['presentation_index']};pick(case,phase,target/'evaluation',f,next(v for v in f['views'] if v['view']=='overview'),details)
    if case.endswith('-v1') and f['presentation_index'] in picked_presentations:
     for name in ['zoom-001','zoom-002']:pick(case,phase,target/'evaluation',f,next(v for v in f['views'] if v['view']==name),dict(details,kind='first_target_and_foil_readable_zoom'))
  elif phase=='train' and case in ['Classic-v1','Branch-v1']:
   train=target/'training';m=json.loads((train/'manifest.json').read_text());assert len(m['reports'])>1
   for tag,row2 in [('first',m['reports'][0]),('last',m['reports'][-1])]:
    folder=train/row2['folder'];probe=json.loads((folder/'manifest.json').read_text())
    for f in probe['figures']:pick(case,phase,folder,f,next(v for v in f['views'] if v['view']=='overview'),{'kind':'training_'+tag+'_packet','trial_id':probe['trial_id'],'source_packet_sha256':probe['source_packet_sha256'],'source_trace_sha256':probe['source_trace_sha256']})
 assert len(selection)==42 and sum(s['details']['kind']=='all_frozen_trial_soma_overviews' for s in selection)==24
 write('selection.json',{'kind':'timelearner_selected_original_temporal_figures','schema_version':1,'records':selection,'manual_reviewed':[],'global_visual_acceptance':False,'scientific_verdict':None});write('render-recipe.json',{'script_root':'2e0618110a9abb48b94f6edc6b63c51f829ec810','primary_evidence_commit':'26a602e84adef89056021a671055d8272330d810','archive_path':'Reports/StructTrain/TimeLearner/s10-integrated-coordinator-normal-a3/primary.tar.xz','bundle_path':'Reports/StructTrain/TimeLearner/s10-integrated-coordinator-normal-a3/bundle.json','commands':recipe,'cache_origin':str(cache),'rendering_does_not_execute_models':True,'full_bitwise_PDF_SVG_metadata_reproduction_attested':False})
 members={}
 with tarfile.open(out/'metadata.tar.xz','w:xz',preset=3) as a:
  inputs=[]
  for suffix in ['a1','a2']:
   for extra in ['', '-container']:
    folder=base/('readbacks/s11-integrated-coordinator-visual-'+suffix+extra);inputs.extend(('render-'+suffix+extra+'/'+p.relative_to(folder).as_posix(),p) for p in folder.rglob('*') if p.is_file())
  inputs.extend(('full-cache-metadata/'+p.relative_to(reports).as_posix(),p) for p in reports.rglob('*.json') if 'primary' not in p.relative_to(reports).parts)
  for name,p in sorted(inputs):
   assert not p.is_symlink() and name not in members;raw=p.read_bytes();members[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};info=tarfile.TarInfo(name);info.size=len(raw);a.addfile(info,io.BytesIO(raw))
 write('metadata-bundle.json',{'members':members,'archive_bytes':(out/'metadata.tar.xz').stat().st_size,'archive_sha256':sha(out/'metadata.tar.xz'),'regular_primary_inputs_retained_in_origin_evidence':True,'full_cache_images_included':False});write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts});write('coverage.json',coverage)
 cards=[]
 for s in selection:
  title=s['case']+' / '+s['phase']+' / '+s['details']['kind']+' / '+s['details']['trial_id']+' / '+s['view']['view'];cards.append('<section><h2>'+html.escape(title)+'</h2><p><a href="'+s['file']+'">Открыть оригинал 1920 на 960</a></p><img src="'+s['file']+'" style="width:100%;max-width:1920px"></section>')
 text='<!doctype html><meta charset="utf-8"><title>TimeLearner: Soma и входные импульсы</title><style>body{font:18px sans-serif;margin:2em;max-width:2000px}section{margin:3em 0}h2{font-size:20px;overflow-wrap:anywhere}</style><h1>Измеренные потенциалы сомы и реальные входные импульсы</h1><p>Четыре завершённых двухвходовых инженерных случая Classic/Branch, ModelSpec1/2:24 frozen trial-soma overview,12 читаемых zoom и6 training examples. Calibration historical_same_matrix; TP2/FP0/FN0/TN2 каждого случая не являются stock4-input/8-pattern или independent evaluation. ModelSpec1/2 являются контролем сериализации, а не независимыми повторами. Четыре stopped Train не имеют Test. SI units не подтверждены; показаны исходные model units. Все samples сохранены без downsampling. Полный кэш16 отчётов и все рассчитанные views остаётся на M40 Data; Git содержит примеры и сжатые primaries. Визуальная проверка выбранных originals ещё не завершена.</p>'+''.join(cards)
 (out/'index.html').write_text(text,encoding='utf-8');passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 if token:r.release(token,note='Read-only completed report selection/metadata packaging ended; no model run.');write('reservation-final.json',r.inspect())
 write('terminal.json',{'selection_passed':passed,'selected_originals':len(selection),'models_executed':0,'manual_review_complete':False,'scientific_verdict':None});print('CLOSED',passed,flush=True)