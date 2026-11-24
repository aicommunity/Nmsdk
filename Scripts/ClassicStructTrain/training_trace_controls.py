"""Capture the remaining historical learning waveforms and isolate EOF parsing."""
from pathlib import Path
import sys,shutil,subprocess,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,BASE,load,save,sha,run_jobs,inference
from training_post_controls import build,file_jobs

def prepare():
 # The previous controller has the same source hashes in VB and FZ. Preserve
 # its complete includes before adding new observations.
 baseline=load(WORK/'variants/VB.json');old=load(WORK/'variants/FZ.json')
 if baseline['controller_sha256']==old['controller_sha256'] and baseline['training_adapter_sha256']==old['training_adapter_sha256']:
  copies={}
  for source,h in old.get('source_snapshots',{}).items():
   source=ROOT/source;assert sha(source)==h;dest=WORK/'variants/controller-sources/VB'/source.name
   dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);copies[str(dest.relative_to(ROOT))]=h
  save(WORK/'variants/VB-source-snapshot-audit.json',{'matched_controller_sha256':baseline['controller_sha256'],'matched_adapter_sha256':baseline['training_adapter_sha256'],'verified_full_snapshot_from':'FZ','files':copies})
 path=ROOT/'Scripts/ClassicStructTrain/replay.cpp';text=path.read_text(encoding='utf8')
 if 'record_training_waveform' not in text:
  marker='   bool boundary=false;'
  block='''   if(manifest.contains("repro_job") && manifest.at("repro_job").value("record_training_waveform",false)) {
    const auto& job=manifest.at("repro_job");const int iteration=learner?beforeCount:iterations;
    if(iteration>=job.value("trace_from_iteration",0) && iteration<=job.value("trace_to_iteration",1000)) {
     const auto& values=learner?learner->SomaNeuronAmplitude.GetData():trainer->SomaNeuronAmplitude.GetData();
     std::vector<double> soma;for(int i=0;i<values.GetRows();++i)soma.push_back(values(i,0));
     waveforms<<json({{"case",key},{"kind",kind},{"repeat",repeat},{"iteration",iteration},{"time",time()-1.0/2000},{"soma_potential",soma}}).dump()<<'\\n';
    }
   }
'''
  assert text.count(marker)==1;text=text.replace(marker,block+marker)
  path.write_text(text,encoding='utf8')
 path=ROOT/'Scripts/ClassicStructTrain/training_file_protocol.inc';text=path.read_text(encoding='utf8')
 if 'file_parser_only' not in text:
  marker=' bool first=true,newPattern=true,written=false;size_t index=0;'
  block=''' if(job.value("file_parser_only",false)) {
  size_t accepted=0;
  while(true) {
   const bool eof=fin.eof();size_t extracted=0;double value;
   if(!eof)for(int i=0;i<5;++i){if(!(fin>>value))break;++extracted;}
   events<<json({{"eof_before",eof},{"extracted_values",extracted},{"accepted",extracted==5}}).dump()<<'\\n';events.flush();
   if(extracted!=5){writeResult({{"status",extracted==0?"completed":"incomplete_input_record"},{"record_type","file_parser_probe"},{"job",job},{"records_accepted",accepted},{"failed_read_values",extracted},{"eof_before",eof},{"model_values_assigned",false}});return;}
   ++accepted;
  }
 }
'''
  assert text.count(marker)==1;text=text.replace(marker,block+marker);path.write_text(text,encoding='utf8')

def main():
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT/'Libraries/Nmsdk-PulseLib').strip()
 if not (WORK/'variants/VT.json').exists():prepare();build('VT')
 parser=[]
 for job in file_jobs()[1:]:
  parser.append({**job,'id':job['id']+'-parser','file_parser_only':True})
 run_jobs('VT',parser,'parser-only',2)
 data=load(BASE)['dataset'];jobs=[{'id':'trainer-111-trace','kind':'trainer','target_id':111,'target_class':3,'record_training_waveform':True,'trace_from_iteration':5,'trace_to_iteration':9}]
 for target in [129,37]:
  jobs.append({'id':'learner-22-to'+str(target)+'-trace','kind':'learner','target_id':22,'target_class':1,'record_training_waveform':True,
   'stages':[{'pattern':data[target-1]['pattern'],'target_id':target,'target_class':(target-1)//50+1,'iterations':5}],
   'interpretation':'Diagnostic reconstruction of the plotted switch: last complete cold period for 22 and five subsequent learning periods. The exact historical display clock is unavailable.'})
 run_jobs('VT',jobs,'traces',2)
 inference('VT','traces',self_only=True,workers=1)
 save(WORK/'trace-controls-completion.json',{'completed':True,'parser_probes':9,'training_waveform_attempts':9,'fixed_warm_continuation_iterations':5})
if __name__=='__main__':main()
