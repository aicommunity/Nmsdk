"""Reassign the pending inference queue without interrupting its native attempt."""
from pathlib import Path
import sys,subprocess,json,ctypes,time
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,load,save,inference

def main():
 raw=subprocess.check_output(['powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -or $_.Name -eq 'ClassicSavedStateCheck-reference.exe' } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress"],encoding='utf8')
 processes=json.loads(raw)
 parents=[p for p in processes if p['Name']=='python.exe' and 'training_repro.py inference --variant VP1 --phase all' in (p['CommandLine'] or '') and '--self-only' not in p['CommandLine']]
 assert len(parents)==1,parents
 parent=parents[0];children=[p for p in processes if p['ParentProcessId']==parent['ProcessId']]
 assert len(children)==1 and children[0]['Name']=='ClassicSavedStateCheck-reference.exe',children
 child=children[0];folder=Path(child['CommandLine'].split('--output ',1)[1].split(' --suite',1)[0].strip('"')).resolve()
 assert folder.is_relative_to((WORK/'inference/VP1/all/reference').resolve())
 kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 kernel.OpenProcess.restype=ctypes.c_void_p;kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32]
 kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
 kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32];kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
 native=kernel.OpenProcess(0x00100000|0x1000,False,child['ProcessId']);dispatch=kernel.OpenProcess(1|0x00100000,False,parent['ProcessId']);assert native and dispatch
 save(folder/'supervisor-transfer.json',{'old_controller_pid':parent['ProcessId'],'native_pid':child['ProcessId'],'native_interrupted':False,'reason':'Resume remaining independent saved-state inference with three workers','utc':datetime.now(timezone.utc).isoformat()})
 try:
  assert kernel.TerminateProcess(dispatch,0);assert kernel.WaitForSingleObject(dispatch,20000)==0
  while kernel.WaitForSingleObject(native,1000)==258:time.sleep(.5)
  code=ctypes.c_uint32();assert kernel.GetExitCodeProcess(native,ctypes.byref(code))
  meta=load(folder/'process.json');finished=datetime.now(timezone.utc)
  meta.update(exit_code=code.value,status='completed' if code.value==0 else 'process_error',finished_utc=finished.isoformat(),elapsed_wall_seconds=(finished-datetime.fromisoformat(meta['started_utc'])).total_seconds(),supervisor_transferred=True)
  save(folder/'process.json',meta);assert code.value==0,meta
 finally:kernel.CloseHandle(native);kernel.CloseHandle(dispatch)
 inference('VP1','all',workers=3)

if __name__=='__main__':main()
