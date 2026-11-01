"""D5.2: extract NPulseDelay::ACalculate and run bypass / buffer / reset probes."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".gitmodules").exists())
OUT = ROOT / "build/audit-review-20260924/pulse_delay"
OUT.mkdir(parents=True, exist_ok=True)
EVIDENCE = ROOT / "Docs/Audit/TimeLearner-2026-09-24-review/evidence/tails"
CORE = ROOT / "Libraries/Nmsdk-PulseLib/Core"
raw = (CORE / "NPulseDelay.cpp").read_text(encoding="utf-8")


def extract(src: str, sig: str) -> str:
    clean = re.sub(
        r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
        lambda m: "".join("\n" if c == "\n" else " " for c in m[0]),
        src,
    )
    start = clean.index(sig)
    pos = clean.index("{", start)
    depth, end = 1, pos + 1
    while depth:
        depth += (clean[end] == "{") - (clean[end] == "}")
        end += 1
    return src[start:end]


body = extract(raw, "bool NPulseDelay::ACalculate(void)")
cpp = f"""// NPulseDelay.cpp SHA256 {hashlib.sha256(raw.encode()).hexdigest()}
#include <cmath>
#include <cstdlib>
#include <list>
#include <iostream>
#include <vector>
using std::fabs;
template<class T> struct MDMatrix {{
 T v{{}}; MDMatrix()=default; MDMatrix(T x):v(x){{}}
 void ToZero(){{v=0;}}
 MDMatrix& operator*(){{return *this;}}
 MDMatrix& operator=(const MDMatrix& o){{v=o.v;return *this;}}
}};
class NPulseDelay {{
public:
 int desired_buffer_length=2; double DelayTime=.001; double TimeStep=1000;
 std::list<MDMatrix<double>> buffer; MDMatrix<double> Input,Output;
 bool ACalculate();
 bool AReset(){{buffer.clear();Output.ToZero();return true;}}
}};
{body}
int main(){{
 int pass=0,fail=0;
 auto check=[&](const char* n,bool ok){{std::cout<<n<<"="<<ok<<"\\n";(ok?++pass:++fail);}};
 {{
  NPulseDelay d;d.DelayTime=0.0005;d.desired_buffer_length=2;d.Input.v=1;d.ACalculate();
  check("bypass_sub_ms", d.Output.v==1 && d.buffer.empty());
 }}
 {{
  NPulseDelay d;d.DelayTime=0.002;d.desired_buffer_length=1;d.Input.v=1;
  d.ACalculate(); // fill
  bool fill_ok=d.Output.v==0 && int(d.buffer.size())==1;
  d.Input.v=0;d.ACalculate();
  check("buffer_n1", fill_ok && d.Output.v==1 && int(d.buffer.size())==1);
 }}
 {{
  NPulseDelay d;d.DelayTime=0.002;d.desired_buffer_length=2;d.Input.v=1;
  d.ACalculate();d.Input.v=0;d.ACalculate();
  bool mid=d.Output.v==0 && int(d.buffer.size())==2;
  d.Input.v=0;d.ACalculate();
  check("buffer_n2", mid && d.Output.v==1 && int(d.buffer.size())==2);
 }}
 {{
  NPulseDelay d;d.desired_buffer_length=2;d.Input.v=1;d.ACalculate();d.ACalculate();
  d.AReset();
  check("reset_clears", d.buffer.empty() && d.Output.v==0);
 }}
 std::cout<<"pass="<<pass<<" fail="<<fail<<"\\n";
 return fail?1:0;
}}
"""
(OUT / "pulse_delay_probes.cpp").write_text(cpp, encoding="utf-8")
gxx = shutil.which("g++")
if not gxx:
    raise SystemExit("g++ required")
exe = OUT / "pulse_delay_probes"
build = subprocess.run(
    [gxx, "-std=c++17", "-O2", "-o", str(exe), str(OUT / "pulse_delay_probes.cpp")],
    text=True,
    capture_output=True,
)
(OUT / "build.log").write_text(build.stdout + "\n" + build.stderr, encoding="utf-8")
if build.returncode:
    print(build.stdout, build.stderr)
    raise SystemExit(build.returncode)
run = subprocess.run([str(exe)], text=True, capture_output=True)
(OUT / "results.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
EVIDENCE.mkdir(parents=True, exist_ok=True)
(EVIDENCE / "d5_pulse_delay.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
print(run.stdout)
raise SystemExit(run.returncode)
