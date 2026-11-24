"""Transfer a live native protocol process without interrupting its experiment."""
from pathlib import Path
import sys,subprocess,json,ctypes,time,argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,CONFIG,load,save
from training_protocols import execute
from run import supervise

def run(cohort,workers):
 raw=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -or $_.Name -eq 'ClassicTrainingRepro-VP1.exe' } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress"],encoding='utf8')
 processes=json.loads(raw);parents=[p for p in processes if p['Name']=='python.exe' and 'training_protocols.py '+cohort+' --variant VP1' in (p['CommandLine'] or '')]
 assert len(parents)==1,parents
 parent=parents[0];children=[p for p in processes if p['ParentProcessId']==parent['ProcessId']]
 assert len(children)==1 and children[0]['Name']=='ClassicTrainingRepro-VP1.exe',children
 child=children[0];args=child['CommandLine'];folder=Path(args.split('--output ',1)[1].split(' --suite',1)[0].strip('"')).resolve()
 assert folder.is_relative_to((WORK/'runs/VP1'/cohort).resolve())
 kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 kernel.OpenProcess.restype=ctypes.c_void_p;kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32]
 kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
 kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
 kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
 native=kernel.OpenProcess(0x00100000|0x1000,False,child['ProcessId']);dispatch=kernel.OpenProcess(1|0x00100000,False,parent['ProcessId'])
 assert native and dispatch
 save(folder/'supervisor-transfer.json',{'old_controller_pid':parent['ProcessId'],'native_pid':child['ProcessId'],'native_interrupted':False,'reason':'Increase parallelism for remaining independent protocol attempts','utc':datetime.now(timezone.utc).isoformat()})
 try:
  assert kernel.TerminateProcess(dispatch,0);assert kernel.WaitForSingleObject(dispatch,20000)==0
  pending_pool=ThreadPoolExecutor(max_workers=workers);pending=[]
  if cohort=='warm':
   binary=ROOT/load(WORK/'variants/VP1.json')['binary']
   for repeat in range(1,4):
    output=WORK/'runs/VP1/warm'/('warm-91-r'+str(repeat))
    if output.resolve()==folder:continue
    metadata=output/'process.json'
    if metadata.exists() and load(metadata)['status']=='completed':continue
    assert not output.exists() or not any(output.iterdir()),'Unfinished warm attempt must be preserved'
    manifest=CONFIG/'Jobs/VP1'/('warm-warm-91-r'+str(repeat)+'.json');assert manifest.exists()
    pending.append(pending_pool.submit(supervise,binary,manifest,output,'repro',repeat,0,660))
  while kernel.WaitForSingleObject(native,1000)==258:time.sleep(.5)
  code=ctypes.c_uint32();assert kernel.GetExitCodeProcess(native,ctypes.byref(code))
  meta=load(folder/'process.json');finished=datetime.now(timezone.utc)
  meta.update(exit_code=code.value,status='completed' if code.value==0 else 'process_error',finished_utc=finished.isoformat(),elapsed_wall_seconds=(finished-datetime.fromisoformat(meta['started_utc'])).total_seconds(),supervisor_transferred=True)
  save(folder/'process.json',meta);assert code.value==0,meta
  print('Native attempt completed without interruption:',folder.name,flush=True)
  for future in pending:assert future.result()['status']=='completed'
  pending_pool.shutdown()
 finally:kernel.CloseHandle(native);kernel.CloseHandle(dispatch)
 execute('VP1',cohort,workers)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('cohort',choices=['warm','schemes']);parser.add_argument('--workers',type=int,default=3);a=parser.parse_args();run(a.cohort,a.workers)
