import json,sys,subprocess,shlex,hashlib
from pathlib import Path
import paramiko
r=json.load(sys.stdin);host=r['host'];root=r['commit'];destination=r['destination'];pack=Path(r['pack']);patterns=r.get('patterns',['/*','!/Docs/','!/Reports/'])
from timelearner_ssh_connect import connect_ssh_chain
j,c=connect_ssh_chain(r)

def run(arguments):
 i,o,e=c.exec_command(shlex.join(arguments));i.close();out=o.read();err=e.read();status=o.channel.recv_exit_status()
 if status:raise RuntimeError(str(status)+':'+err.decode(errors='replace'))
 return out.decode()
try:
 run(['python3','-c','from pathlib import Path; import sys; p=Path(sys.argv[1]); p.mkdir(parents=True,exist_ok=True); assert not any(p.iterdir())',destination])
 run(['git','init','--quiet',destination])
 i,o,e=c.exec_command(shlex.join(['git','-C',destination,'index-pack','--stdin','--promisor']))
 with pack.open('rb') as f:
  while True:
   b=f.read(65536)
   if not b:break
   i.write(b)
 i.flush();i.channel.shutdown_write();indexed=o.read().decode();err=e.read();status=o.channel.recv_exit_status()
 if status:raise RuntimeError(err.decode(errors='replace'))
 run(['python3','-c','from pathlib import Path;import sys; (Path(sys.argv[1])/".git/shallow").write_text(sys.argv[2]+chr(10))',destination,root])
 run(['git','-C',destination,'config','core.repositoryformatversion','1'])
 run(['git','-C',destination,'config','extensions.partialClone','origin'])
 run(['git','-C',destination,'config','remote.origin.promisor','true'])
 run(['git','-C',destination,'sparse-checkout','init','--no-cone'])
 run(['git','-C',destination,'sparse-checkout','set','--no-cone',*patterns])
 run(['git','-C',destination,'-c','submodule.recurse=false','checkout','--detach',root])
 actual=run(['git','-C',destination,'rev-parse','HEAD']).strip();assert actual==root
 assert not run(['git','-C',destination,'status','--porcelain','--untracked-files=no']).strip()
 run(['python3','-c','from pathlib import Path;import sys; assert not (Path(sys.argv[1])/".git/objects/info/alternates").exists()',destination])
 physical_prefixes=json.loads(run(['python3','-c','from pathlib import Path;import json,sys; p=Path(sys.argv[1]); print(json.dumps({n:((p/n).exists() or (p/n).is_symlink()) for n in ("Docs","Reports")}))',destination]))
 actual_patterns=run(['git','-C',destination,'sparse-checkout','list']).splitlines()
 print(json.dumps({'kind':'standalone_shallow_code_git_delivery','host':host,'destination':destination,'commit':root,'pack_bytes':pack.stat().st_size,'pack_sha256':hashlib.sha256(pack.read_bytes()).hexdigest(),'omitted_paths':[n for n in ('Docs','Reports') if not physical_prefixes[n]],'actual_sparse_patterns':actual_patterns,'child_gitlinks_not_materialized':True,'checkout_clean':True,'alternates':False}))
finally:c.close();j.close()
