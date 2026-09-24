"""Compile unchanged production method bodies against minimal scalar adapters.

This isolates the decision logic; it does not replace an Rdk integration test.
Source hashes are embedded so the extracted bodies remain attributable.
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "Libraries/Nmsdk-PulseLib/Core"


def method(file, signature):
    raw = (CORE / file).read_text(encoding="utf-8")
    # Blank comments and literals only to identify the balanced method boundary.
    clean = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
                   lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), raw)
    start = clean.index(signature)
    body = clean.index("{", start)
    depth = 1
    end = body + 1
    while depth:
        depth += (clean[end] == "{") - (clean[end] == "}")
        end += 1
    return (f"// {file} SHA256 {hashlib.sha256(raw.encode()).hexdigest()}\n"
            + raw[start:end] + "\n")


prefix = r'''
#include <gtest/gtest.h>
#include <vector>
#include <list>
#include <string>
#include <algorithm>
#include <cmath>
using std::size_t;
template<class T> struct MDMatrix {
 T v{}; MDMatrix() = default; MDMatrix(T x): v(x) {}
 void ToZero() { v=0; } int GetRows() const { return 1; }
 int GetCols() const { return 1; }
 void Assign(int,int,T x){v=x;}
 T& operator()(int,int){return v;} T operator()(int,int) const{return v;}
 MDMatrix& operator*(){return *this;}
};
template<class T> struct Prop {
 T v; const T& GetData() const {return v;}
};
struct FakeTime { double now=0; double GetDoubleTime() const {return now;} };
struct FakeEnv { FakeTime t; const FakeTime& GetTime() const{return t;} };
struct FakeDataset {
 int sample_id=0;
 int CountScheduledSpikes(int,int)const{return expected_stims;}
 int GetCurrentSampleId()const{return sample_id;}
 int GetSampleClass(int)const{return target_class;}
 double GetSampleStartTime()const{return 0;}
 double GetExpectedLastSpikeAbsRel(int,int)const{return 0;}
 int expected_stims=4;
 int target_class=1;
};
class NPatternResponseAnalyzer {
public:
 static constexpr double kBurstIsiMax=0.005, kPerStimWindowFloor=0.003;
 Prop<bool> Enable{true};
 Prop<std::vector<MDMatrix<double>>> StimulusInputs{{MDMatrix<double>(0)}};
 Prop<std::vector<MDMatrix<double>>> NeuronOutputs{{MDMatrix<double>(0)}};
 double PostPatternWindow=.5;
 FakeEnv env; FakeEnv* Environment=&env;
 FakeDataset fake_ds; FakeDataset* dataset_source_=&fake_ds;
 bool trial_active_=false, trial_window_closed_=false, playback_stopped_=false;
 bool trial_pattern_complete_=false, trial_neu_edge_consumed_=false;
 bool trial_censored_=false, trial_incomplete_=false, pending_neu_valid_=false;
 int trial_neuron_fired_=0, trial_late_fired_=0, trial_target_class_=1, current_class=1;
 int trial_sample_id_=-1, trial_expected_stims_=0;
 double trial_t_last_stim_=0, trial_t_neuron_=-1, trial_t_late_neuron_=-1;
 double trial_observe_until_=-1, trial_t_first_stim_=0;
 double trial_sample_start_abs_=0, trial_expected_last_stim_abs_=-1;
 double pending_neu_time_=-1;
 std::vector<double> trial_stim_times_, prev_stimulus_{0}, prev_neuron_{0}, spikes;
 struct Result{int count,fired,late,label;}; std::vector<Result> closed;
 static std::string ClassifyResponseMorphology(const std::vector<double>&, const std::vector<double>&);
 bool ACalculate();
 double EffectiveLateWindow(){return 1.5;}
 int ReadTargetClass(){return current_class;}
 void UpdateTrialMetrics(double){}
 void ResolveDatasetSourceIfNeeded(){}
 bool DetectRisingEdge(const std::vector<MDMatrix<double>>& x,std::vector<double>& p){
  bool edge=p[0]<=0 && x[0].v>0; p[0]=x[0].v; return edge;
 }
 bool IsPatternComplete()const{
  if(trial_expected_stims_>0) return int(trial_stim_times_.size())>=trial_expected_stims_;
  return trial_stim_times_.size()>=4;
 }
 void MaybeClassifyFire(double now,double post_win){
  if(!trial_pattern_complete_) return;
  if(now+1e-12<trial_t_last_stim_) return;
  if(now<=trial_t_last_stim_+post_win+1e-12){if(!trial_neuron_fired_){trial_neuron_fired_=1;trial_t_neuron_=now;}}
  else if(!trial_neuron_fired_&&!trial_late_fired_){trial_late_fired_=1;trial_t_late_neuron_=now;}
 }
 void RecordNeuronSpike(double t){spikes.push_back(t);}
 void AttributeNeuronToActiveTrial(double now){
  if(!trial_active_||trial_neu_edge_consumed_) return;
  RecordNeuronSpike(now); trial_neu_edge_consumed_=true;
  MaybeClassifyFire(now,PostPatternWindow);
 }
 void BeginTrial(double t){
  ResolveDatasetSourceIfNeeded();
  trial_active_=true;trial_window_closed_=false;trial_pattern_complete_=false;
  trial_neu_edge_consumed_=false;trial_observe_until_=-1;
  if(dataset_source_){
   trial_sample_id_=dataset_source_->GetCurrentSampleId();
   trial_expected_stims_=dataset_source_->CountScheduledSpikes(trial_sample_id_,0);
   trial_target_class_=dataset_source_->GetSampleClass(trial_sample_id_);
   trial_sample_start_abs_=dataset_source_->GetSampleStartTime();
   trial_expected_last_stim_abs_=trial_sample_start_abs_
     +dataset_source_->GetExpectedLastSpikeAbsRel(trial_sample_id_,0);
  }else{
   trial_sample_id_=-1;trial_expected_stims_=0;trial_target_class_=ReadTargetClass();
   trial_sample_start_abs_=t;trial_expected_last_stim_abs_=-1;
  }
  trial_neuron_fired_=trial_late_fired_=0;trial_t_first_stim_=t;trial_t_last_stim_=t;
  trial_t_neuron_=trial_t_late_neuron_=-1;spikes.clear();trial_stim_times_={t};
  if(IsPatternComplete()){trial_pattern_complete_=true;trial_observe_until_=t+EffectiveLateWindow();}
 }
 void AppendStim(double now){
  trial_stim_times_.push_back(now);trial_t_last_stim_=now;
  if(IsPatternComplete()){
   trial_pattern_complete_=true;
   if(trial_observe_until_<0) trial_observe_until_=trial_t_last_stim_+EffectiveLateWindow();
  }
 }
 void CloseTrial(double){
  closed.push_back({int(spikes.size()),trial_neuron_fired_,trial_late_fired_,trial_target_class_});
  trial_active_=false;
 }
 void tick(double t,int stim,int spike){env.t.now=t;StimulusInputs.v[0].v=stim;NeuronOutputs.v[0].v=spike;ACalculate();}
};
class NAxoneDelay {
public:
 int desired_buffer_length=2; double DelayTime=.001;
 std::list<MDMatrix<double>> buffer; MDMatrix<double> Input,Output;
 bool ACalculate();
};
class NAperiodicLink {
public:
 MDMatrix<double> Input,Output,filter_state;
 double Tau=.001,TimeStep=250,Bias=0;
 bool ACalculate();
};
'''
tests = r'''
TEST(AnalyzerAudit, FirstPulseResponseMustNotCountAsCompletePattern) {
 NPatternResponseAnalyzer a;
 a.tick(0,1,0);a.tick(.001,0,1);a.tick(.002,0,0);
 a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,0);a.tick(.06,1,0);a.tick(.061,0,0);
 a.tick(.561,0,0);a.tick(1.561,0,0);
 ASSERT_EQ(a.closed.size(),1u);EXPECT_EQ(a.closed[0].fired,0);
}
TEST(AnalyzerAudit, ThreePulseTargetMustBeSupported) {
 NPatternResponseAnalyzer a;a.fake_ds.expected_stims=3;
 a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,1);a.tick(.032,0,0);
 a.tick(1.54,0,0);a.tick(1.541,0,0);
 ASSERT_EQ(a.closed.size(),1u);EXPECT_EQ(a.closed[0].fired,1);
}
TEST(AnalyzerAudit, LateSpikeAfterTimelySpikeMustRemainCounted) {
 NPatternResponseAnalyzer a;
 a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,0);a.tick(.06,1,0);
 a.tick(.061,0,1);a.tick(.062,0,0);a.tick(.561,0,0);a.tick(.7,0,1);a.tick(1.561,0,0);
 ASSERT_EQ(a.closed.size(),1u);EXPECT_EQ(a.closed[0].count,2);
}
TEST(AnalyzerAudit, OneSpikeIsNotAResponseToEveryStimulus) {
 EXPECT_EQ(NPatternResponseAnalyzer::ClassifyResponseMorphology({.375},{0,.125,.25,.375}),"single");
}
TEST(AnalyzerAudit, NextClassMustNotRelabelPreviousTrial) {
 NPatternResponseAnalyzer a;
 a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,0);a.tick(.06,1,0);
 a.tick(.561,0,0);a.current_class=0;a.tick(.69,0,0);a.tick(.7,1,0);
 ASSERT_EQ(a.closed.size(),1u);EXPECT_EQ(a.closed[0].label,1);
}
TEST(AxonAudit, IntegerDelayMustNotAddAnExtraStep) {
 NAxoneDelay d;std::vector<double> out;
 for(int i=0;i<5;++i){d.Input.v=(i==0?1:0);d.ACalculate();out.push_back(d.Output.v);}
 EXPECT_EQ(out[2],1);EXPECT_EQ(out[3],0);
}
TEST(AxonAudit, PositiveTauShouldNotDivergeWithoutAStabilityGuard) {
 NAperiodicLink f;f.Input.v=1;
 for(int i=0;i<5;++i)f.ACalculate();
 EXPECT_GE(f.Output.v,0);EXPECT_LE(f.Output.v,1);
}
'''
bodies = [method("NPatternResponseAnalyzer.cpp", "std::string NPatternResponseAnalyzer::ClassifyResponseMorphology"),
          method("NPatternResponseAnalyzer.cpp", "bool NPatternResponseAnalyzer::ACalculate(void)"),
          method("NAxoneDelay.cpp", "bool NAxoneDelay::ACalculate(void)"),
          method("NAperiodicLink.cpp", "bool NAperiodicLink::ACalculate(void)")]
Path(sys.argv[1]).write_text(prefix + "\n".join(bodies) + tests, encoding="utf-8")
