"""Generate a framework-isolated probe using real current analyzer method bodies.

Run from any directory. C++17, standard library only. Compilation is separate.
The CloseTrial adapter captures state then invokes the actual ResetTrialState.
Dataset identity, scalar input edges, properties and metrics I/O are adapters.
"""
import ast
import hashlib
import re
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.gitmodules').exists())
OUT = ROOT / 'build/audit-review-20260924/analyzer'
OUT.mkdir(parents=True, exist_ok=True)
gen = (ROOT / 'Scripts/audit-probes/generate_probes.py').read_text(encoding='utf8')
tree = ast.parse(gen)
prefix = next(ast.literal_eval(n.value) for n in tree.body
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
              and t.id == 'prefix' for t in n.targets))
raw = (ROOT / 'Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.cpp').read_text(encoding='utf8')

def method(src, sig):
    clean = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                   lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), src)
    start = clean.index(sig)
    body = clean.index('{', start)
    depth, end = 1, body + 1
    while depth:
        depth += (clean[end] == '{') - (clean[end] == '}')
        end += 1
    return start, end, src[start:end]

prefix = prefix[:prefix.index('class NAxoneDelay')]
prefix = prefix.replace('#include <gtest/gtest.h>', '#include <iostream>')
prefix = prefix.replace('spikes', 'trial_neuron_spike_times_')
prefix = prefix.replace('struct Result{int count,fired,late,label;}',
                        'struct Result{int count,fired,late,label,stims;double deadline,closed_at;}')
prefix = prefix.replace(' static constexpr double kBurstIsiMax',
    ' int StimulusFeatureIndex=0;double trial_ltz_potential_max_=0;'
    'double trial_soma_amp_max_[4]={};double trial_soma_amp_sum_max_=0;\n'
    ' static constexpr double kBurstIsiMax')
bodies = []
for old, new in [
    ('bool IsPatternComplete()const', 'bool NPatternResponseAnalyzer::IsPatternComplete() const'),
    ('void MaybeClassifyFire(double now,double post_win)', 'void NPatternResponseAnalyzer::MaybeClassifyFire(double now, double post_win)'),
    ('void AttributeNeuronToActiveTrial(double now)', 'void NPatternResponseAnalyzer::AttributeNeuronToActiveTrial(double now)'),
    ('void BeginTrial(double t)', 'void NPatternResponseAnalyzer::BeginTrial(double now)'),
    ('void AppendStim(double now)', 'void NPatternResponseAnalyzer::AppendStim(double now)'),
]:
    start, end, _ = method(prefix, old)
    _, _, body = method(raw, new)
    decl = body[:body.index('{')].replace('NPatternResponseAnalyzer::', '').strip() + ';'
    prefix = prefix[:start] + decl + prefix[end:]
    bodies.append(body)
start, end, _ = method(prefix, 'void CloseTrial(double)')
prefix = prefix[:start] + '''void CloseTrial(double now){
 closed.push_back({int(trial_neuron_spike_times_.size()),trial_neuron_fired_,
 trial_late_fired_,trial_target_class_,int(trial_stim_times_.size()),trial_observe_until_,now});
 ResetTrialState();
}
void ResetTrialState();''' + prefix[end:]
for sig in ['void NPatternResponseAnalyzer::ResetTrialState(void)',
            'bool NPatternResponseAnalyzer::ACalculate(void)']:
    bodies.append(method(raw, sig)[2])

main = r'''
void stim4(NPatternResponseAnalyzer& a){
 a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);
 a.tick(.03,1,0);a.tick(.031,0,0);a.tick(.06,1,0);a.tick(.061,0,1);a.tick(.062,0,0);
}
int main(){
 {NPatternResponseAnalyzer a;stim4(a);a.fake_ds.sample_id=1;a.fake_ds.target_class=0;
  a.tick(.31,0,0);a.tick(.4,0,1);a.tick(.401,0,0);a.tick(.5,1,0);
  std::cout<<"advance_window deadline="<<a.closed[0].deadline<<" closed="<<a.closed[0].closed_at
  <<" count="<<a.closed[0].count<<" subsequent_spike_at_0.4_lost="
  <<(a.closed[0].count==1 && a.trial_neuron_spike_times_.empty())<<'\n';}
 {NPatternResponseAnalyzer a;a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);
  a.tick(.03,1,0);a.tick(.031,0,0);a.fake_ds.sample_id=1;a.fake_ds.target_class=0;a.tick(.1,1,1);
  std::cout<<"incomplete_sample_new_stim old_sample="<<a.trial_sample_id_
  <<" expected_current=1 observed="<<a.trial_stim_times_.size()<<" complete="
  <<a.trial_pattern_complete_<<" fired="<<a.trial_neuron_fired_<<" label="<<a.trial_target_class_<<'\n';}
 {NPatternResponseAnalyzer a;a.dataset_source_=nullptr;a.tick(0,1,0);a.tick(.001,0,1);
  a.tick(.002,0,0);a.tick(2,0,0);std::cout<<"unbound_single_stim active="<<a.trial_active_
  <<" complete="<<a.trial_pattern_complete_<<" closed_count="<<a.closed.size()<<'\n';}
}
'''
(OUT / 'analyzer-boundaries.cpp').write_text(
    '// Production source SHA256 ' + hashlib.sha256(raw.encode()).hexdigest() + '\n'
    + prefix + '\n'.join(bodies) + main, encoding='utf8')
print(OUT / 'analyzer-boundaries.cpp')
