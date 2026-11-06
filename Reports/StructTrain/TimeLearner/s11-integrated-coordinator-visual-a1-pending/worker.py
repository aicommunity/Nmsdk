from pathlib import Path
import os,sys,json,subprocess,hashlib,tarfile,io,time,traceback,unittest,html
venv='/media/user/Data/TimeLearnerRefactor/plot-venv-a1'
if sys.prefix!=venv:os.execv(venv+'/bin/python',[venv+'/bin/python',str(Path(__file__))])
base=Path('/media/user/Data/TimeLearnerRefactor');source=base/'source-native-runtime-interface-a1';repo=base/'source-theory-retirement-a1';out=base/'readbacks/s11-integrated-coordinator-visual-a1';out.mkdir(exist_ok=False);cache=base/'ReportsCache/integrated-coordinator-visual-a1';cache.mkdir(parents=True,exist_ok=False);primary=base/'ReportsCache/integrated-coordinator-normal-a3/source';assert primary.is_dir();reports=cache/'reports';reports.mkdir()
sys.dont_write_bytecode=True;sys.path.insert(0,str(source));os.nice(19)
os.environ.update(MPLCONFIGDIR=str(cache/'matplotlib'),MPLBACKEND='Agg',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.native_evidence import load
from Scripts.StructTrain.TimeLearner.live_pipeline_reports import render_pipeline_run,read_pipeline_report
from Scripts.StructTrain.TimeLearner.calibration_transaction_reports import render_calibration_run
from Scripts.StructTrain.TimeLearner.recognition_metrics import load_evaluation,score_threshold_candidate
r=Reservations(base/'report-reservations.sqlite3');token=None;passed=False;rows=[];members={};rendered=[];frozen_pairs=0;train_pairs=0;calibration_pairs=0;images=0
commit='26a602e84adef89056021a671055d8272330d810';prefix='Reports/StructTrain/TimeLearner/s10-integrated-coordinator-normal-a3/'
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(n):return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+prefix+n])
write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'native_models_executed':0,'cache':str(cache),'source_code':'8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a'});(out/'producer.py').write_bytes(Path(__file__).read_bytes())
try:
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()=='8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a'
 lease=r.reserve(out.name,[{'path':str(out),'access':'write'},{'path':str(cache),'access':'write'},{'path':str(source),'access':'read'},{'path':str(primary),'access':'read'}],ttl_seconds=18000);token=lease['token'];write('reservation.json',lease)
 bundle=json.loads(blob('bundle.json'));archive=blob('primary.tar.xz');assert len(archive)==bundle['archive_bytes'] and hashlib.sha256(archive).hexdigest()==bundle['archive_sha256'];seen=set()
 for name,record in bundle['members'].items():
  p=primary/name;assert p.resolve().is_relative_to(primary.resolve()) and p.is_file() and not p.is_symlink();assert {'bytes':p.stat().st_size,'sha256':sha(p)}==record;seen.add(name)
 assert seen==set(bundle['members']) and len(seen)==2233
 write('primary-delivery.json',{'git_commit':commit,'all_members_verified':len(seen),'archive_sha256':bundle['archive_sha256'],'raw_source_cache_only':str(primary),'native_models_executed':0})
 for folder in sorted((primary/'actual-controls').iterdir()):
  case=load(folder/'result.json');positive=case['positive_source_declaration'];phases=['train','calibrate','evaluate'] if positive else ['train']
  for phase in phases:
   run=folder/'runs/pipeline/phases'/phase/'run-manifest.json';assert run.is_file();target=reports/(folder.name+'--'+phase);print('RENDER',target.name,flush=True)
   result=(render_calibration_run if phase=='calibrate' else render_pipeline_run)(run,target)
   row={'case':folder.name,'phase':phase,'source':str(run.relative_to(primary)),'folder':target.name,'result':result,'positive_source':positive};rows.append(row);rendered.append((run,target,phase));write('progress.json',rows);r.heartbeat(token,ttl_seconds=18000)
 assert len(rows)==16
 class ReportChecks(unittest.TestCase):
  def test_all_primary_files_and_source_binding_unchanged(self):
   for name,record in bundle['members'].items():self.assertEqual({'bytes':(primary/name).stat().st_size,'sha256':sha(primary/name)},record,name)
   for run,target,phase in rendered:
    m=load(target/'manifest.json')
    if phase=='calibrate':
     self.assertEqual(load(target/'primary/transaction.json.gz'),load(run.parent/'native/transaction.json'));self.assertTrue(load(target/'run-binding.json')['source_primary_checked'])
    else:self.assertEqual(m['source_manifest_sha256'],sha(run));self.assertFalse(m['visual_acceptance_complete'])
  def test_every_recorded_training_trace_is_lossless(self):
   global train_pairs
   for run,target,phase in rendered:
    if phase!='train':continue
    manifest,job,execution,audit,case,live,packets=read_pipeline_report(run);m=load(target/'manifest.json');self.assertEqual(m['source_completed_boundary'],execution['completed_boundary']);self.assertEqual(m['training_packet_order'],[p.name for p in packets])
    if not packets:continue
    entries=load(target/'training/manifest.json')['reports'];self.assertEqual(len(entries),len(packets))
    for row,packet in zip(entries,packets):
     folder=target/'training'/row['folder'];self.assertEqual(load(folder/'primary/probe.json'),load(packet));self.assertEqual((folder/'primary/trace.csv').read_bytes(),packet.with_suffix('.csv').read_bytes());train_pairs+=len(load(folder/'manifest.json')['figures'])
  def test_every_frozen_pattern_and_calibration_matrix_has_all_somas(self):
   global frozen_pairs,calibration_pairs
   for run,target,phase in rendered:
    if phase=='evaluate':
     expected=load_evaluation(run.parent/'native/evaluation.json')[1];actual=load_evaluation(target/'evaluation/primary/evaluation.json')[1];self.assertEqual(actual,expected);m=load(target/'evaluation/manifest.json');self.assertEqual({(f['trial_id'],f['descriptor']['index']) for f in m['figures']},{(o['trial_id'],i) for o in expected for i in range(len(o['samples'][0]['soma']))});frozen_pairs+=len(m['figures'])
    elif phase=='calibrate':
     outer=load(target/'manifest.json');transaction=load(run.parent/'native/transaction.json');self.assertEqual(outer['completed_matrices'],len(transaction['candidates'])+(1 if transaction['status'] in ['calibrated','confirmation_failed'] else 0))
     for matrix in outer['matrices']:
      d=target/matrix['name'];spec,observations=load_evaluation(d/'primary/evaluation.json');model=load(d/'primary/model.json');self.assertEqual(score_threshold_candidate(spec,observations,model),load(d/'analysis.json'));m=load(d/'manifest.json');self.assertEqual({(f['trial_id'],f['descriptor']['index']) for f in m['figures']},{(o['trial_id'],i) for o in observations for i in range(len(o['samples'][0]['soma']))});calibration_pairs+=len(m['figures'])
   self.assertEqual(frozen_pairs,24)
  def test_readable_native_scale_real_input_overlays_and_all_output_checksums(self):
   global images
   from PIL import Image
   for run,target,phase in rendered:
    sums=load(target/'SHA256SUMS.json');self.assertEqual(set(sums),{p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file() and p!=target/'SHA256SUMS.json'})
    for name,h in sums.items():self.assertEqual(sha(target/name),h)
    for metadata in target.rglob('manifest.json'):
     for figure in load(metadata).get('figures',[]):
      self.assertTrue(any(v['time_view']!='overview' for v in figure['views']))
      for view in figure['views']:
       self.assertFalse(view['downsampling'])
       if view['time_view']!='overview':self.assertGreaterEqual(view['minimum_native_tick_pixels_on_zoom'],8)
       png,svg,pdf=[metadata.parent/n for n in view['files']]
       with Image.open(png) as im:self.assertEqual(im.size,(1920,960))
       self.assertIn('Actual shared input',svg.read_text());self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'));images+=1
 with (out/'checks.log').open('w') as f:result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReportChecks))
 write('checks.json',{'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'expected':4});assert result.testsRun==4 and result.wasSuccessful() and not result.skipped
 links=''.join('<li><a href="'+html.escape(row['folder'])+'/index.html">'+html.escape(row['case']+' / '+row['phase'])+'</a></li>' for row in rows)
 (reports/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Integrated SDK2e coordinator actual soma/input traces</title><style>body{font:18px sans-serif;margin:2em}img{max-width:100%}</style><h1>Actual coordinator Train/calibration/frozen responses</h1><p>All declared patterns and soma channels, actual input pulses, full samples and readable zooms. Same-matrix engineering controls; independent evaluation and scientific stock4-input/8-pattern result are not established. ModelSpec1/2 are serialization controls, not independent repetitions. Negative Train has no Test. SI units and manual visual QA remain unverified.</p><ul>'+links+'</ul>',encoding='utf-8')
 write('coverage.json',{'cases':8,'phase_reports':len(rows),'train_trial_soma_pairs':train_pairs,'frozen_trial_soma_pairs':frozen_pairs,'calibration_trial_soma_pairs':calibration_pairs,'native_input_overlay_views_checked':images,'plot_size_px':[1920,960],'downsampling':False,'minimum_tick_pixels_on_zoom':8,'source_files_unchanged':2233,'selected_images_published':False,'manual_visual_QA':False,'scientific_verdict':None});passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 if token:r.release(token,note='Read-only source render/check procedure ended; no model/experiment process launched. Cache result status recorded separately.');write('reservation-final.json',r.inspect())
 write('terminal.json',{'report_and_checks_passed':passed,'native_models_executed':0,'source_commit':'8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a','primary_evidence_commit':commit,'cache':str(cache),'manual_visual_review_complete':False,'scientific_verdict':None});print('CLOSED',passed,flush=True)
