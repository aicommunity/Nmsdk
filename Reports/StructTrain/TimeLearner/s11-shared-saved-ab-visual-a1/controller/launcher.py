import json,os,time,sys
from pathlib import Path
p=Path(sys.argv[1]);request=json.loads((p/'request.json').read_text())
ready={'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().rsplit(') ',1)[1].split()[19]}
temporary=p/'ready.pending';temporary.write_text(json.dumps(ready));temporary.rename(p/'ready.json')
while not (p/'start.ack').exists():time.sleep(.01)
env=dict(os.environ)
for key in ('LD_LIBRARY_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM'):env.pop(key,None)
env.update(request['environment'])
os.execve(request['executable'],[request['executable'],*request['arguments']],env)
