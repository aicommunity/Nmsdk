set -uo pipefail
out=/media/user/Data/TimeLearnerRefactor/readbacks/s07-n0-closure-a1
dst=/media/user/Data/TimeLearnerRefactor/closure-n0-develop-a1
git clone --no-checkout --single-branch --branch develop --reference-if-able /home/user/timelearner-refactor/source-order-baseline-a1 https://github.com/aicommunity/Nmsdk.git "$dst" > "$out/clone.log" 2>&1 &&
git -C "$dst" -c submodule.recurse=false checkout --detach fbda0476dd6d3a1e29f27545217e80f86e103b03 > "$out/checkout.log" 2>&1 &&
git -C "$dst" submodule update --init --recursive --jobs 2 > "$out/submodules.log" 2>&1 &&
DST="$dst" OUT="$out" python3 - <<'PY' > "$out/verification.log" 2>&1
import os,json,subprocess
from pathlib import Path
dst=Path(os.environ["DST"]);out=Path(os.environ["OUT"])
def git(*args,path=dst):
    return subprocess.check_output(["git","-C",str(path),*args],text=True).strip()
root=git("rev-parse","HEAD")
assert root=="fbda0476dd6d3a1e29f27545217e80f86e103b03"
assert not git("status","--porcelain","--untracked-files=no")
links=[]
for line in git("ls-tree","-r","HEAD").splitlines():
    before,path=line.split("\t")
    mode,kind,commit=before.split()
    if mode!="160000":continue
    actual=git("rev-parse","HEAD",path=dst/path)
    assert actual==commit,(path,actual,commit)
    assert not git("status","--porcelain","--untracked-files=no",path=dst/path),path
    links.append({"path":path,"recorded":commit,"actual":actual,"remote":git("remote","get-url","origin",path=dst/path),"tracked_clean":True})
assert len(links)==7,len(links)
assert next(x for x in links if x["path"]=="Libraries/Nmsdk-PulseLib")["actual"]=="b2b670a22f849e0d0d2b6789b8242308521b1c37"
assert next(x for x in links if x["path"]=="Bin")["actual"]=="cbb3bf453d82f58672541ed8a42f7b5da54a5508"
(out/"submodule-status.txt").write_text(git("submodule","status","--recursive")+"\n")
(out/"closure.json").write_text(json.dumps({"kind":"timelearner_git_closure_check","schema_version":1,"root":root,"fresh_recursive_checkout":True,"tracked_clean":True,"links":links,"scientific_verdict":None,"scope":"Git reconstruction only; native A2 and combined Python evidence apply through unchanged source content"},indent=2)+"\n")
print(json.dumps({"root":root,"submodules":len(links),"tracked_clean":True}))
PY
status=$?
printf '%s\n' "$status" > "$out/process-exit-status.txt"
exit "$status"
