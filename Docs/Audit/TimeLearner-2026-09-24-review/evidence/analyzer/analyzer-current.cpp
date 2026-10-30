// Audit source SHA256 0b88579685f808c2e71d6b4686da568a3c41a7e9a26acf7095b96d335f9ceb0d
// Production source SHA256 0b88579685f808c2e71d6b4686da568a3c41a7e9a26acf7095b96d335f9ceb0d

#include <iostream>
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
 int StimulusFeatureIndex=0;double trial_ltz_potential_max_=0; double trial_soma_amp_max_[4]={};double trial_soma_amp_sum_max_=0;
 static constexpr double kBurstIsiMax=0.005, kPerStimWindowFloor=0.003;
 Prop<bool> Enable{true};
 Prop<std::vector<MDMatrix<double>>> StimulusInputs{{MDMatrix<double>(0)}};
 Prop<std::vector<MDMatrix<double>>> NeuronOutputs{{MDMatrix<double>(0)}};
 double PostPatternWindow=.5;
 FakeEnv env; FakeEnv* Environment=&env;
 FakeDataset fake_ds; FakeDataset* dataset_source_=&fake_ds;
 bool trial_active_=false, trial_window_closed_=false, playback_stopped_=false;
 bool trial_pattern_complete_=false, trial_neu_edge_consumed_=false;
 int trial_neuron_fired_=0, trial_late_fired_=0, trial_target_class_=1, current_class=1;
 int trial_sample_id_=-1, trial_expected_stims_=0;
 double trial_t_last_stim_=0, trial_t_neuron_=-1, trial_t_late_neuron_=-1;
 double trial_observe_until_=-1, trial_t_first_stim_=0;
 double trial_sample_start_abs_=0, trial_expected_last_stim_abs_=-1;
 std::vector<double> trial_stim_times_, prev_stimulus_{0}, prev_neuron_{0}, trial_neuron_spike_times_;
 struct Result{int count,fired,late,label,stims;double deadline,closed_at;}; std::vector<Result> closed;
 static std::string ClassifyResponseMorphology(const std::vector<double>&, const std::vector<double>&);
 bool ACalculate();
 double EffectiveLateWindow(){return 1.5;}
 int ReadTargetClass(){return current_class;}
 void UpdateTrialMetrics(double){}
 void ResolveDatasetSourceIfNeeded(){}
 bool DetectRisingEdge(const std::vector<MDMatrix<double>>& x,std::vector<double>& p){
  bool edge=p[0]<=0 && x[0].v>0; p[0]=x[0].v; return edge;
 }
 bool IsPatternComplete() const;
 void MaybeClassifyFire(double now, double post_win);
 void RecordNeuronSpike(double t){trial_neuron_spike_times_.push_back(t);}
 void AttributeNeuronToActiveTrial(double now);
 void BeginTrial(double now);
 void AppendStim(double now);
 void CloseTrial(double now){closed.push_back({int(trial_neuron_spike_times_.size()),trial_neuron_fired_,trial_late_fired_,trial_target_class_,int(trial_stim_times_.size()),trial_observe_until_,now});ResetTrialState();}
 void ResetTrialState();
 void tick(double t,int stim,int spike){env.t.now=t;StimulusInputs.v[0].v=stim;NeuronOutputs.v[0].v=spike;ACalculate();}
};
void NPatternResponseAnalyzer::BeginTrial(double now)
{
 ResolveDatasetSourceIfNeeded();
 trial_active_ = true;
 trial_window_closed_ = false;
 trial_pattern_complete_ = false;
 trial_neu_edge_consumed_ = false;
 trial_observe_until_ = -1.0;

 if(dataset_source_)
 {
  trial_sample_id_ = dataset_source_->GetCurrentSampleId();
  trial_expected_stims_ = dataset_source_->CountScheduledSpikes(
      trial_sample_id_, int(StimulusFeatureIndex));
  trial_target_class_ = dataset_source_->GetSampleClass(trial_sample_id_);
  trial_sample_start_abs_ = dataset_source_->GetSampleStartTime();
  const double last_rel = dataset_source_->GetExpectedLastSpikeAbsRel(
      trial_sample_id_, int(StimulusFeatureIndex));
  trial_expected_last_stim_abs_ = trial_sample_start_abs_ + last_rel;
 }
 else
 {
  trial_sample_id_ = -1;
  trial_expected_stims_ = 0;
  trial_target_class_ = int(ReadTargetClass());
  trial_sample_start_abs_ = now;
  trial_expected_last_stim_abs_ = -1.0;
 }

 trial_neuron_fired_ = 0;
 trial_late_fired_ = 0;
 trial_t_first_stim_ = now;
 trial_t_last_stim_ = now;
 trial_t_neuron_ = -1.0;
 trial_t_late_neuron_ = -1.0;
 trial_ltz_potential_max_ = 0.0;
 trial_soma_amp_max_[0] = trial_soma_amp_max_[1] = 0.0;
 trial_soma_amp_max_[2] = trial_soma_amp_max_[3] = 0.0;
 trial_soma_amp_sum_max_ = 0.0;
 trial_stim_times_.clear();
 trial_neuron_spike_times_.clear();
 trial_stim_times_.push_back(now);
 if(IsPatternComplete())
 {
  trial_pattern_complete_ = true;
  trial_observe_until_ = trial_t_last_stim_ + EffectiveLateWindow();
 }
}
void NPatternResponseAnalyzer::ResetTrialState(void)
{
 trial_active_ = false;
 trial_window_closed_ = false;
 trial_stim_times_.clear();
 trial_neuron_spike_times_.clear();
 trial_neuron_fired_ = 0;
 trial_late_fired_ = 0;
 trial_sample_id_ = -1;
 trial_expected_stims_ = 0;
 trial_t_first_stim_ = 0.0;
 trial_t_last_stim_ = 0.0;
 trial_t_neuron_ = -1.0;
 trial_t_late_neuron_ = -1.0;
 trial_ltz_potential_max_ = 0.0;
 trial_soma_amp_max_[0] = trial_soma_amp_max_[1] = 0.0;
 trial_soma_amp_max_[2] = trial_soma_amp_max_[3] = 0.0;
 trial_soma_amp_sum_max_ = 0.0;
 trial_sample_start_abs_ = 0.0;
 trial_expected_last_stim_abs_ = -1.0;
 trial_observe_until_ = -1.0;
 trial_pattern_complete_ = false;
 trial_neu_edge_consumed_ = false;
}
bool NPatternResponseAnalyzer::ACalculate(void)
{
 if(!Enable.GetData())
  return true;

 ResolveDatasetSourceIfNeeded();
 const double now = Environment->GetTime().GetDoubleTime();
 const std::vector<MDMatrix<double> > &stim = StimulusInputs.GetData();
 const std::vector<MDMatrix<double> > &neuron = NeuronOutputs.GetData();
 const double post_win = double(PostPatternWindow);
 const double late_win = EffectiveLateWindow();

 const bool stim_edge = DetectRisingEdge(stim, prev_stimulus_);
 bool neu_edge = DetectRisingEdge(neuron, prev_neuron_);
 trial_neu_edge_consumed_ = false;

 // Watchdog: dataset advanced to a new sample while previous trial still open.
 if(trial_active_ && dataset_source_
    && trial_sample_id_ >= 0
    && dataset_source_->GetCurrentSampleId() != trial_sample_id_
    && !stim_edge)
 {
  CloseTrial(now);
 }

 if(!playback_stopped_ && stim_edge)
 {
  if(!trial_active_)
  {
   BeginTrial(now);
   if(neu_edge)
    AttributeNeuronToActiveTrial(now);
  }
  else if(!trial_pattern_complete_)
  {
   AppendStim(now);
   if(neu_edge)
    AttributeNeuronToActiveTrial(now);
  }
  else
  {
   // Pattern already complete: this stim starts the next sample.
   CloseTrial(now);
   BeginTrial(now);
   if(neu_edge)
    AttributeNeuronToActiveTrial(now);
  }
 }

 if(trial_active_)
 {
  UpdateTrialMetrics(now);

  if(neu_edge && !trial_neu_edge_consumed_)
   AttributeNeuronToActiveTrial(now);

  if(trial_pattern_complete_ && trial_observe_until_ < 0.0)
   trial_observe_until_ = trial_t_last_stim_ + late_win;

  if(trial_pattern_complete_
     && now + 1e-12 >= trial_t_last_stim_ + post_win)
   trial_window_closed_ = true;

  if(trial_observe_until_ >= 0.0
     && now + 1e-12 >= trial_observe_until_)
   CloseTrial(now);
 }

 return true;
}
std::string NPatternResponseAnalyzer::ClassifyResponseMorphology(
    const std::vector<double> &spike_rel_times,
    const std::vector<double> &stim_times)
{
 const size_t spike_count = spike_rel_times.size();
 if(spike_count == 0)
  return "single"; // silence — not a morphology fault by itself

 bool burst = false;
 if(spike_count >= 2)
 {
  for(size_t i = 1; i < spike_count; ++i)
  {
   if(spike_rel_times[i] - spike_rel_times[i - 1] <= kBurstIsiMax + 1e-12)
   {
    burst = true;
    break;
   }
  }
 }

 bool per_stim = false;
 const size_t stim_count = stim_times.size();
 if(stim_count >= 3 && spike_count >= stim_count)
  per_stim = true;
 else if(stim_count >= 1 && spike_count >= 1)
 {
  double min_isi = kPerStimWindowFloor;
  if(stim_count >= 2)
  {
   min_isi = stim_times[1] - stim_times[0];
   for(size_t i = 2; i < stim_count; ++i)
    min_isi = std::min(min_isi, stim_times[i] - stim_times[i - 1]);
  }
  const double win = std::max(2.0 * min_isi, kPerStimWindowFloor);
  // Injective matching: each spike covers at most one stim window.
  std::vector<bool> spike_used(spike_count, false);
  size_t matched = 0;
  for(size_t s = 0; s < stim_count; ++s)
  {
   const double t0 = stim_times[s] - stim_times[0];
   for(size_t k = 0; k < spike_count; ++k)
   {
    if(spike_used[k])
     continue;
    if(spike_rel_times[k] + 1e-12 >= t0
       && spike_rel_times[k] <= t0 + win + 1e-12)
    {
     spike_used[k] = true;
     ++matched;
     break;
    }
   }
  }
  const size_t need = static_cast<size_t>(std::ceil(0.75 * double(stim_count)));
  per_stim = matched >= need;
 }

 if(burst && per_stim)
  return "multi";
 if(burst)
  return "burst";
 if(per_stim)
  return "per_stim";
 if(spike_count == 1)
  return "single";
 return "multi";
}
bool NPatternResponseAnalyzer::IsPatternComplete() const
{
 if(trial_expected_stims_ > 0)
  return int(trial_stim_times_.size()) >= trial_expected_stims_;
 // Legacy without dataset: never treat the first stim as a complete pattern (A01).
 // Historical packA-class patterns without a bound dataset need >=4 observed stims.
 return trial_stim_times_.size() >= 4;
}
void NPatternResponseAnalyzer::MaybeClassifyFire(double now, double post_win)
{
 if(!trial_pattern_complete_)
  return;
 if(now + 1e-12 < trial_t_last_stim_)
  return;
 if(now <= trial_t_last_stim_ + post_win + 1e-12)
 {
  if(!trial_neuron_fired_)
  {
   trial_neuron_fired_ = 1;
   trial_t_neuron_ = now;
  }
 }
 else if(!trial_neuron_fired_ && !trial_late_fired_)
 {
  trial_late_fired_ = 1;
  trial_t_late_neuron_ = now;
 }
}
void NPatternResponseAnalyzer::AppendStim(double now)
{
 trial_stim_times_.push_back(now);
 trial_t_last_stim_ = now;
 if(IsPatternComplete())
 {
  trial_pattern_complete_ = true;
  if(trial_observe_until_ < 0.0)
   trial_observe_until_ = trial_t_last_stim_ + EffectiveLateWindow();
 }
}
void NPatternResponseAnalyzer::AttributeNeuronToActiveTrial(double now)
{
 if(!trial_active_ || trial_neu_edge_consumed_)
  return;
 RecordNeuronSpike(now);
 trial_neu_edge_consumed_ = true;
 MaybeClassifyFire(now, double(PostPatternWindow));
}
void run_stims(NPatternResponseAnalyzer& a){a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,0);a.tick(.06,1,0);}
int main(){
 {NPatternResponseAnalyzer a;a.tick(0,1,0);a.tick(.001,0,1);a.tick(.002,0,0);a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,0);a.tick(.06,1,0);a.tick(.061,0,0);a.tick(.561,0,0);a.tick(1.561,0,0);std::cout<<"A01 early fired="<<a.closed[0].fired<<'\n';}
 {NPatternResponseAnalyzer a;a.fake_ds.expected_stims=3;a.tick(0,1,0);a.tick(.001,0,0);a.tick(.01,1,0);a.tick(.011,0,0);a.tick(.03,1,0);a.tick(.031,0,1);a.tick(.032,0,0);a.tick(.54,0,0);a.tick(1.54,0,0);std::cout<<"A01 3stims fired="<<a.closed[0].fired<<'\n';}
 {NPatternResponseAnalyzer a;run_stims(a);a.tick(.061,0,1);a.tick(.062,0,0);a.tick(.561,0,0);a.tick(.7,0,1);a.tick(1.561,0,0);std::cout<<"A02 timely then late count="<<a.closed[0].count<<'\n';}
 {NPatternResponseAnalyzer a;run_stims(a);a.tick(.561,0,0);a.current_class=0;a.tick(.69,0,0);a.tick(.7,1,0);std::cout<<"A03 label="<<a.closed[0].label<<'\n';}
 std::cout<<"A04 morphology="<<NPatternResponseAnalyzer::ClassifyResponseMorphology({.375},{0,.125,.25,.375})<<'\n';
}
