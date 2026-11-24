"""Preserve an interrupted inference attempt before changing worker allocation."""
from pathlib import Path
import sys,shutil,subprocess,json,os,signal,time,ctypes
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save

def rebalance():
 raw=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -or $_.Name -eq 'ClassicSavedStateCheck-reference.exe' } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress"],encoding='utf8')
 procs=json.loads(raw)
 def terminate(pid):
  handle=ctypes.windll.kernel32.OpenProcess(0x00100001,False,pid)
  assert handle,'Cannot open process '+str(pid)
  try:
   assert ctypes.windll.kernel32.TerminateProcess(handle,1)
   assert ctypes.windll.kernel32.WaitForSingleObject(handle,20000)==0
  finally:ctypes.windll.kernel32.CloseHandle(handle)
 candidates=[]
 for proc in procs:
  args=proc['CommandLine'] or ''
  if proc['Name'].lower()!='python.exe':continue
  if 'training_repro.py inference' not in args or '--self-only' in args:continue
  if '--variant V1C' not in args or '--phase all' not in args:continue
  candidates.append(proc)
 assert len(candidates)==1,candidates
 parent=candidates[0];children=[p for p in procs if p['ParentProcessId']==parent['ProcessId']]
 assert all(p['Name']=='ClassicSavedStateCheck-reference.exe' for p in children)
 # Stop queue dispatch first, then preserve each child and its provenance.
 terminate(parent['ProcessId'])
 records=[]
 for child in children:
  args=child['CommandLine'];folder=Path(args.split('--output ',1)[1].split(' --suite',1)[0].strip('"')).resolve()
  assert folder.is_relative_to((WORK/'inference/V1C/all/reference').resolve())
  terminate(child['ProcessId'])
  record=load(folder/'process.json');record.update(status='interrupted_for_worker_reallocation',finished_utc=datetime.now(timezone.utc).isoformat(),reason='Queue changed from one worker to three; completed attempts retained unchanged')
  save(folder/'process.json',record)
  destination=WORK/'interrupted-inference'/(folder.name+'-'+datetime.now(timezone.utc).strftime('%H%M%S'))
  destination.parent.mkdir(parents=True,exist_ok=True);assert not destination.exists()
  shutil.move(str(folder),str(destination));records.append(str(destination.relative_to(ROOT)))
 save(WORK/'inference-reallocation.json',{'parent_pid':parent['ProcessId'],'preserved_attempts':records,'completed_attempts_modified':False})
 print('Preserved interrupted attempts:',records)
if __name__=='__main__':rebalance()
