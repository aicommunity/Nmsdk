"""Retain preliminary batched cases; independent cases supply controlled starts."""
from pathlib import Path
import sys,subprocess,json,os,signal,time
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save
def main():
 raw=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name='ClassicTrainingRepro-VB.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],encoding='utf8')
 records=json.loads(raw);records=[records] if isinstance(records,dict) else records
 records=[r for r in records if '--suite modes ' in r['CommandLine'] and '\\runs\\VB\\modes\\modes-r' in r['CommandLine']]
 assert 1<=len(records)<=3,records
 folders=[]
 for r in records:
  folder=Path(r['CommandLine'].split('--output ',1)[1].split(' --suite',1)[0].strip('"')).resolve()
  assert folder.is_relative_to((WORK/'runs/VB/modes').resolve());folders.append(folder);os.kill(r['ProcessId'],signal.SIGTERM)
 for folder in folders:
  start=time.monotonic()
  while load(folder/'process.json')['status']=='running':
   assert time.monotonic()-start<30;time.sleep(.2)
  record=load(folder/'process.json');record.update(status='interrupted_batched_mode_precondition',reason='Repeat the 32 independent historical cases in fresh processes; precondition limits were observed in the preliminary multi-case process',finished_utc=datetime.now(timezone.utc).isoformat())
  save(folder/'process.json',record)
 save(WORK/'modes-isolation-decision.json',{'retained_batched_attempts':[str(p.relative_to(ROOT)) for p in folders],'independent_probe':'VB/modes-isolated/mode-16-r1','probe_result':'recorded; native precondition finalized; threshold check true','interpretation':'Fresh processes enforce independent initial conditions. Exact cause of precondition differences in multi-case processes is not established.'})
 print('Retained preliminary batches; independent mode cases are authoritative')
if __name__=='__main__':main()
