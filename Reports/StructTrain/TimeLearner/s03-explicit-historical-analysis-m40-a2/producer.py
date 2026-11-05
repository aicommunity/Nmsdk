from pathlib import Path
base=Path('/media/user/Data/TimeLearnerRefactor')
primary=Path('/media/user/Data/TimeLearnerRefactor/ReportsCache/managed-coordinator-normal-a4/source/actual-controls')
modules=['Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest', 'Scripts.StructTrain.TimeLearner.tests.test_model_spec_transport.ModelSpecTransportPreparationTest']
ids=['Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_completed_classic_branch_and_wire_versions_require_explicit_adapter', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_stopped_training_keeps_its_original_outcome_without_certificate', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_public_cli_exposes_adapter_and_retains_unverified_native_execution', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_adapter_cannot_be_applied_to_another_format', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_unknown_and_noninteger_archived_auditor_versions_are_rejected', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_exact_primary_count_and_model_identity_are_not_projected', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_missing_capacitance_or_unknown_analysis_fields_are_rejected', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_stopped_and_completed_statuses_cannot_be_promoted', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_old_v2_adapter_does_not_accept_v3_record', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_runtime_identity_changes_are_rejected_before_analysis_projection', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_modified_primary_model_is_rejected', 'Scripts.StructTrain.TimeLearner.tests.test_historical_pipeline_analysis.HistoricalPipelineAnalysisTest.test_unknown_adapter_is_rejected', 'Scripts.StructTrain.TimeLearner.tests.test_model_spec_transport.ModelSpecTransportPreparationTest.test_only_model_wire_version_and_explicit_threshold_change', 'Scripts.StructTrain.TimeLearner.tests.test_model_spec_transport.ModelSpecTransportPreparationTest.test_actual_pinned_source_is_exact_with_original_tolerances', 'Scripts.StructTrain.TimeLearner.tests.test_model_spec_transport.ModelSpecTransportPreparationTest.test_frozen_target_in_both_positions_uses_complete_predeclared_windows', 'Scripts.StructTrain.TimeLearner.tests.test_model_spec_transport.ModelSpecTransportPreparationTest.test_historical_adapter_preserves_original_claims_and_default_stays_strict']

from pathlib import Path
import os,sys,json,hashlib,subprocess,traceback,tarfile,time,threading,shutil
source=base/'source-historical-analysis-python-a2';out=base/'readbacks/s03-explicit-historical-analysis-a2';out.mkdir(exist_ok=False);sys.dont_write_bytecode=True;sys.path.insert(0,str(source));os.nice(15)
from Scripts.StructTrain.TimeLearner.resource_reservations import Reservations
from Scripts.StructTrain.TimeLearner.validation import package_fingerprint,fixture_fingerprint
r=Reservations(base/'historical-analysis-reservations.sqlite3');stop=threading.Event();thread=None;token=None;errors=[];passed=False
root='d2d68a83bfb5d30e2a380b4eedf6f1cc162154d5'
def write(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def inventory():
 result={}
 for name in ['Classic-v1','Classic-v2','Branch-v1','Branch-v2','Classic-N0','Classic-N1','Branch-N0','Branch-N1']:
  folder=primary/name/'runs/pipeline/phases/train';assert (folder/'run-manifest.json').is_file()
  for f in sorted(folder.rglob('*')):
   if f.is_symlink():result[f.relative_to(primary).as_posix()]={'symlink':os.readlink(f)}
   elif f.is_file():result[f.relative_to(primary).as_posix()]={'bytes':f.stat().st_size,'sha256':sha(f)}
 return result
(out/'producer.py').write_bytes(Path(__file__).read_bytes());write('owner.json',{'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19],'root':root,'new_native_model_runs':0})
try:
 previous=(base/'readbacks/launch-explicit-historical-analysis-a1-container.log').read_text();assert 'FileExistsError' in previous;write('previous-failed-launch.json',{'reason':'outer wrapper precreated contained output directory, but production start owns creation','launch_log':previous,'worker_started':False,'tests_executed':0,'reservation_created':False})
 assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==root
 assert shutil.disk_usage(base).free>=2*1024**3
 write('fixture-origins.json',{'old_auditor2_primary_commit':'bcbd30f1d87e352825e6c8400c5b929eff184ae5','auditor3_primary_evidence':'2776bd89fb53a4c32324a445d771e75d010a30d0','actual_primary_path':str(primary),'original_models_not_installed':True})
 held=Reservations(base/'resource-reservations.sqlite3').inspect()['leases']
 for lease in held:
  if lease['state']!='held':continue
  for v in lease['resources']:
   q=Path(v['canonical_path'])
   for f in [out,source,primary]:assert not f.is_relative_to(q) and not q.is_relative_to(f),str(q)
 lease=r.reserve(out.name,[{'path':str(out),'access':'write'},{'path':str(source),'access':'read'},{'path':str(primary),'access':'read'}],ttl_seconds=120);token=lease['token'];write('reservation.json',lease)
 def heartbeat():
  while not stop.wait(20):
   try:r.heartbeat(token,ttl_seconds=120);r.validate_paths(token)
   except BaseException as e:errors.append(str(e));return
 thread=threading.Thread(target=heartbeat,daemon=True);thread.start()
 before=inventory();write('train-primary-inventory-before.json',before)
 declarations={};bindings={'TIMELEARNER_HISTORICAL_PIPELINE_PRIMARY':primary,'TIMELEARNER_MODEL_SPEC_TRANSPORT_REPOSITORY':source}
 for key,pattern in [('TIMELEARNER_HISTORICAL_PIPELINE_PRIMARY','*/runs/pipeline/phases/train/run-manifest.json'),('TIMELEARNER_MODEL_SPEC_TRANSPORT_REPOSITORY','.git/objects/pack/*.pack')]:
  count,digest=fixture_fingerprint(bindings[key],pattern);declarations[key]={'pattern':pattern,'files':count,'fingerprint':digest}
 spec={'kind':'timelearner_python_validation_suite','schema_version':1,'suite_id':'explicit-historical-analysis16','package_fingerprint':package_fingerprint(),'modules':modules,'expected_test_ids':ids,'fixtures':declarations};write('suite.json',spec)
 temp=out/'temporary';temp.mkdir();env=dict(os.environ,TMPDIR=str(temp),PYTHONDONTWRITEBYTECODE='1');args=[sys.executable,'-m','Scripts.StructTrain.TimeLearner.validation',str(out/'suite.json'),'--output',str(out/'structured-result')]
 for k,v in bindings.items():args+=['--fixture',k+'='+str(v)]
 with (out/'validation-cli.log').open('wb') as log:process=subprocess.run(args,cwd=source,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=6900)
 result=json.loads((out/'structured-result/result.json').read_text());write('validation-returncode.json',{'returncode':process.returncode})
 after=inventory();write('train-primary-inventory-after.json',after);assert before==after
 assert process.returncode==0 and result['executed_tests']==16 and result['assertion_status']=='passed' and not any(result[k] for k in ['failures','errors','skipped'])
 assert not list(temp.iterdir());temp.rmdir();assert not errors;passed=True
except BaseException as e:write('exception.json',{'reason':str(e),'traceback':traceback.format_exc()})
finally:
 stop.set()
 if thread:thread.join(timeout=30)
 write('source-hashes.json',{p.relative_to(source).as_posix():sha(p) for p in (source/'Scripts/StructTrain/TimeLearner').rglob('*.py') if '__pycache__' not in p.parts})
 write('terminal.json',{'tests_passed':passed,'expected_tests':16,'new_native_models_executed':0,'cpp_runtime_executed':False,'source_package':root,'full_pipeline_runtime_acceptance_complete':False,'scientific_verdict':None})
 members={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in out.rglob('*') if p.is_file() and not p.is_symlink()}
 with tarfile.open(out/'primary.tar.xz','w:xz',preset=3) as a:
  for n,record in members.items():
   info=tarfile.TarInfo(n);info.size=record['bytes']
   with (out/n).open('rb') as f:a.addfile(info,f)
 write('bundle.json',{'members':members,'archive_bytes':(out/'primary.tar.xz').stat().st_size,'archive_sha256':sha(out/'primary.tar.xz'),'scientific_verdict':None});print('CLOSED',passed,flush=True)
