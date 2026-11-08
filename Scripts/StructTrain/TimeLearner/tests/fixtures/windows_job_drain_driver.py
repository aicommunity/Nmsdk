"""Real Windows process lifetime controls, with no SDK model calculations."""
import argparse
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=('parent','child'))
    parser.add_argument('--directory',type=Path,required=True);parser.add_argument('--sleep',type=float,required=True)
    parser.add_argument('--code',type=int,default=0);args=parser.parse_args();args.directory.mkdir(parents=True,exist_ok=True)
    if args.mode=='child':
        kernel=C.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=W.HANDLE
        times=[W.FILETIME() for _ in range(4)]
        kernel.GetProcessTimes.argtypes=(W.HANDLE,)+(C.POINTER(W.FILETIME),)*4
        if not kernel.GetProcessTimes(kernel.GetCurrentProcess(),*[C.byref(value) for value in times]):raise C.WinError(C.get_last_error())
        created=str((times[0].dwHighDateTime<<32)|times[0].dwLowDateTime)
        pending=args.directory/'child-ready.pending.json'
        pending.write_text(json.dumps(dict(pid=os.getpid(),creation_filetime=created,executable=str(Path(sys.executable).resolve())))+'\n',encoding='utf-8')
        pending.rename(args.directory/'child-ready.json');time.sleep(args.sleep);return 0
    subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'child','--directory',str(args.directory),'--sleep',str(args.sleep)])
    deadline=time.monotonic()+5
    while not (args.directory/'child-ready.json').is_file():
        if time.monotonic()>=deadline:raise RuntimeError('child_ready_timeout')
        time.sleep(.01)
    (args.directory/'main-return.json').write_text(json.dumps(dict(code=args.code))+'\n',encoding='utf-8')
    return args.code


if __name__=='__main__':raise SystemExit(main())
