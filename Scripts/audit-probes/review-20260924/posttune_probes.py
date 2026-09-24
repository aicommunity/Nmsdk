"""Independent current-source PostTune counterexamples. No production edits.

Extract full FinalizePostTuneMid and UpdatePostTuneFreeRunPeak unchanged;
stub framework, clock, dataset and instantaneous signal only. The mode probe
additionally executes the unchanged soma-accumulator block from ACalculate.
No full application or physics integration is claimed.
"""
from pathlib import Path
import ast, re, hashlib, os, subprocess, json
ROOT=next(p for p in Path(__file__).resolve().parents if (p / ".gitmodules").exists())
OUT=ROOT/"build/audit-review-20260924/posttune"
OUT.mkdir(parents=True, exist_ok=True)
PULSE=ROOT/'Libraries/Nmsdk-PulseLib/Core'
tree=ast.parse((ROOT/'Scripts/audit-probes/generate_branch_update_probes.py').read_text(encoding='utf-8'))
prefix=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='prefix' for t in n.targets))
prefix=prefix.replace('#include <gtest/gtest.h>', '#include <iostream>')
prefix=prefix.replace('struct FakeEnv {std::string GetCurrentDataDir(){return "";}};', 'struct FakeTime {double now=0;double GetDoubleTime(){return now;}}; struct FakeEnv {FakeTime time;FakeTime& GetTime(){return time;} std::string GetCurrentDataDir(){return "";}};')
prefix=prefix.replace('void FinalizePostTuneMid();void HandlePostTuneFinishIteration();', 'void FinalizePostTuneMid();void UpdatePostTuneFreeRunPeak();double amp=.5; double ReadPostTuneLiveMetric()const{return amp;} double EffectiveDatasetDelaySec(){return .1;} double PatternSpanSec(){return .1;} double SettleMarginSec(){return .1;} void SomaBlock(double soma_amp);')
raw_by_type={name:(PULSE/(name+'.cpp')).read_text(encoding='utf-8') for name in ['NNeuronTimeLearnerBranch','NNeuronTimeLearner']}
def extract(raw,signature):
    clean=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]),raw)
    start=clean.index(signature); pos=clean.index('{',start);depth=1;end=pos+1
    while depth:
        depth+=(clean[end]=='{')-(clean[end]=='}');end+=1
    return raw[start:end]
parts=[prefix]
start=prefix.index('class NNeuronTimeLearnerBranch')
parts.append(prefix[start:].replace('NNeuronTimeLearnerBranch','NNeuronTimeLearner'))
for name,raw in raw_by_type.items():
    for method in ['FinalizePostTuneMid','UpdatePostTuneFreeRunPeak']:
        parts.append(extract(raw,f'void {name}::{method}(void)'))
snippet='if(PostTuneFreeRunActive && soma_amp > PostTuneLiveSomaMax)\n    PostTuneLiveSomaMax = soma_amp;'
assert snippet in raw_by_type['NNeuronTimeLearnerBranch']
parts.append('void NNeuronTimeLearnerBranch::SomaBlock(double soma_amp){'+snippet+'}')
parts.append(r'''
template<class T> void prepare(T& b,FakeDataset& d,FakeNeuron& n,FakeEnv& e) {
 b.IsNeedToTrain=false;b.TrainingPhase=2;b.PostTuneInferenceMidPending=true;
 b.PostTuneFreeRunActive=true;b.PostTuneMetrics={0,0};b.PostTuneFreeRunStartTime=0;
 b.Dataset=&d;b.Neuron=&n;b.Environment=&e;d.StateGeneration=2;
}
template<class T> void dump(const char* label,T& b) {
 std::cout<<label<<" result="<<b.PostTuneResult.GetData()<<" complete="<<b.PostTrainTuneComplete.GetData()<<" mid="<<b.FixedLTZThreshold.GetData()<<" metrics=";
 for(double m:b.PostTuneMetrics)std::cout<<m<<",";
 std::cout<<"\n";
}
template<class T> void timeout(const char* label) {
 T b;FakeDataset d;FakeNeuron n;FakeEnv e;prepare(b,d,n,e);
 e.time.now=100;b.amp=.5;b.UpdatePostTuneFreeRunPeak();dump(label,b);
}
template<class T> void nan_foil(const char* label) {
 T b;FakeDataset d;FakeNeuron n;FakeEnv e;prepare(b,d,n,e);
 b.amp=.5;b.UpdatePostTuneFreeRunPeak();d.Iteration=1;b.amp=0;b.UpdatePostTuneFreeRunPeak();
 b.amp=std::numeric_limits<double>::quiet_NaN();b.UpdatePostTuneFreeRunPeak();
 b.amp=0;d.StateGeneration=0;b.UpdatePostTuneFreeRunPeak();dump(label,b);
}
template<class T> void stale_result(const char* label) {
 T b;b.IsNeedToTrain=false;b.TrainingPhase=2;b.PostTuneInferenceMidPending=true;
 b.PostTuneResult=PostTrainTune::kResultSuccess;b.PostTuneMetrics={.5,.6};b.FinalizePostTuneMid();dump(label,b);
}
int main(){
 timeout<NNeuronTimeLearnerBranch>("branch_timeout_before_foil");
 timeout<NNeuronTimeLearner>("tl_timeout_before_foil");
 nan_foil<NNeuronTimeLearnerBranch>("branch_nan_in_foil_trace");
 nan_foil<NNeuronTimeLearner>("tl_nan_in_foil_trace");
 stale_result<NNeuronTimeLearnerBranch>("branch_stale_success");
 stale_result<NNeuronTimeLearner>("tl_stale_success");
 NNeuronTimeLearnerBranch b;FakeDataset d;FakeNeuron n;FakeEnv e;prepare(b,d,n,e);
 // ReadPostTuneLiveMetric() is stubbed to its explicit-LTZ output 0.2.
 // ACalculate soma side channel remains active before the real update.
 b.amp=.2;b.SomaBlock(.8);b.UpdatePostTuneFreeRunPeak();
 std::cout<<"branch_ltz_mode actual_accumulator="<<b.PostTuneLiveSomaMax<<" expected_ltz_peak=0.2\n";
}
''')
(OUT/'current_source_probes.cpp').write_text('\n'.join(parts),encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()}
ms=Path('C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207')
sdk=Path('C:/Program Files (x86)/Windows Kits/10'); version='10.0.26100.0'
env['PATH']=str(ms/'bin/Hostx64/x64')+';'+str(sdk/f'bin/{version}/x64')+';'+env['PATH']
env['INCLUDE']=';'.join(str(p) for p in [ms/'include']+[sdk/f'Include/{version}/{p}' for p in ['ucrt','shared','um','winrt']])
env['LIB']=';'.join(str(p) for p in [ms/'lib/x64']+[sdk/f'Lib/{version}/{p}/x64' for p in ['ucrt','um']])
cmd=[str(ms/'bin/Hostx64/x64/cl.exe'),'/nologo','/EHsc','/std:c++17','/I'+str(PULSE),str(OUT/'current_source_probes.cpp'),str(PULSE/'NNeuronPostTrainTune.cpp'),'/Fe:'+str(OUT/'current_source_probes.exe')]
build=subprocess.run(cmd,env=env,cwd=OUT,text=True,capture_output=True)
(OUT/'build.log').write_text(build.stdout+'\n'+build.stderr,encoding='utf-8')
if build.returncode:
    print(build.stdout,build.stderr);raise SystemExit(build.returncode)
run=subprocess.run([str(OUT/'current_source_probes.exe')],cwd=OUT,text=True,capture_output=True)
(OUT/'results.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
(OUT/'source_sha256.json').write_text(json.dumps({str(PULSE/(name+'.cpp')):hashlib.sha256((PULSE/(name+'.cpp')).read_bytes()).hexdigest() for name in raw_by_type},indent=2),encoding='utf-8')
print(run.stdout,run.stderr)

# Retrospective reproduction at the exact PulseLib gitlink in audit root23e4.
# Compatibility stub has PostTuneResult, but historical bodies never write it.
revision='17854a4fabd53841d8840d382a2186ba1cadbd80'
def git_file(path):
    return subprocess.check_output(['git','-c','safe.directory='+str(PULSE.parent).replace('\\','/'),'-C',str(PULSE.parent),'show',revision+':'+path]).decode('utf-8')
historic={name:git_file('Core/'+name+'.cpp') for name in raw_by_type}
historic_include=OUT/'historical_include'
historic_include.mkdir(exist_ok=True)
(historic_include/'NNeuronPostTrainTune.h').write_text(git_file('Core/NNeuronPostTrainTune.h'),encoding='utf-8')
old_helper=OUT/'historical_posttrain_helper.cpp'
old_helper.write_text(git_file('Core/NNeuronPostTrainTune.cpp'),encoding='utf-8')
old_prefix=prefix.replace('void FinalizePostTuneMid();','void FinalizePostTuneMid();void HandlePostTuneFinishIteration();')
old_prefix=old_prefix.replace('PostTrainTune::kResultNone','0')
old_parts=[old_prefix,old_prefix[old_prefix.index('class NNeuronTimeLearnerBranch'):].replace('NNeuronTimeLearnerBranch','NNeuronTimeLearner')]
for name,raw in historic.items():
    for method in ['FinalizePostTuneMid','HandlePostTuneFinishIteration']:
        old_parts.append(extract(raw,f'void {name}::{method}(void)'))
old_parts.append(r'''
template<class T>void legacy_infer(const char* label,std::vector<double> metrics) {
 T b;b.IsNeedToTrain=false;b.TrainingPhase=2;b.PostTuneInferenceMidPending=true;b.PostTuneMetrics=metrics;b.FinalizePostTuneMid();
 std::cout<<label<<" mid="<<b.FixedLTZThreshold.GetData()<<" complete="<<b.PostTrainTuneComplete.GetData()<<"\n";
}
template<class T>void legacy_best(const char* label) {
 T b;b.HandlePostTuneFinishIteration();
 std::cout<<label<<" setup_called="<<b.setup_called<<" mid="<<b.FixedLTZThreshold.GetData()<<" complete="<<b.PostTrainTuneComplete.GetData()<<" tips0="<<b.TipSynapseResistance.GetData()[0]<<" metrics=";
 for(double m:b.PostTuneMetrics)std::cout<<m<<",";std::cout<<"\n";
}
int main(){
 legacy_infer<NNeuronTimeLearner>("historical_tl_higher_foil",{.5,.2,.6});
 legacy_infer<NNeuronTimeLearnerBranch>("historical_branch_higher_foil",{.5,.2,.6});
 legacy_infer<NNeuronTimeLearnerBranch>("historical_branch_nan",{.5,std::numeric_limits<double>::quiet_NaN()});
 legacy_best<NNeuronTimeLearner>("historical_tl_best");
 legacy_best<NNeuronTimeLearnerBranch>("historical_branch_best");
 NNeuronTimeLearnerBranch b;b.PostTuneMetrics={.5,.6};b.FinalizePostTuneMid();
 std::cout<<"historical_branch_reverted_snapshot tips0="<<b.TipSynapseResistance.GetData()[0]<<" metrics=";for(double m:b.PostTuneMetrics)std::cout<<m<<",";std::cout<<"\n";
}
''')
old_cpp=OUT/'historical_source_probes.cpp';old_cpp.write_text('\n'.join(old_parts),encoding='utf-8')
old_exe=OUT/'historical_source_probes.exe'
cmd=[str(ms/'bin/Hostx64/x64/cl.exe'),'/nologo','/EHsc','/std:c++17','/I'+str(historic_include),'/I'+str(PULSE),str(old_cpp),str(old_helper),'/Fe:'+str(old_exe)]
build=subprocess.run(cmd,env=env,cwd=OUT,text=True,capture_output=True)
(OUT/'historical_build.log').write_text(build.stdout+'\n'+build.stderr,encoding='utf-8')
if build.returncode:
    print(build.stdout,build.stderr);raise SystemExit(build.returncode)
run=subprocess.run([str(old_exe)],cwd=OUT,text=True,capture_output=True)
(OUT/'historical_results.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
print(run.stdout,run.stderr)
