"""Extract changed Branch methods without changing their bodies.
Framework/IO are stubbed; this does not replace a full integration test.
"""
from pathlib import Path
import re,sys,hashlib
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/"Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp"
raw=source.read_text(encoding="utf-8")
clean=re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
             lambda m: ''.join('\n' if c=='\n' else ' ' for c in m[0]),raw)
def extract(signature):
 start=clean.index(signature);pos=clean.index("{",start);depth=1;end=pos+1
 while depth:
  depth+=(clean[end]=="{")-(clean[end]=="}");end+=1
 return raw[start:end]
prefix=r"""
#include <gtest/gtest.h>
#include "NNeuronPostTrainTune.h"
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <memory>
#include <cstdio>
#include <cmath>
#include <limits>
namespace PostTrainTune=NMSDK::PostTrainTune;
template<class T> struct P {
 T v{}; P()=default; P(T x):v(x){}; const T& GetData()const{return v;}
 operator T()const{return v;} P& operator=(T x){v=x;return *this;}
 void SetDataDirect(T x){v=x;}
};
template<class T> struct MDMatrix {
 std::vector<T> data;int rows=0,cols=0;
 void Resize(int r,int c,T value=T{}){rows=r;cols=c;data.assign(r*c,value);}
 T& operator()(int r,int c){return data.at(r*cols+c);}
 void SetDataDirect(const MDMatrix& x){*this=x;}
};
template<class T> using UEPtr=std::shared_ptr<T>;
struct NPatternResponseAnalyzer {bool Enable=false;int TrialIndex=-1;void Reset(){}};
struct UContainer {
 template<class T> UEPtr<T> GetComponentL(const std::string&,bool){return {};}
};
struct FakeGenerator{void Reset(){}};
using NPulseGeneratorTransit=FakeGenerator;
struct FakeNeuron{void Reset(){}};
struct FakeDataset {
 bool LoopSamples=false,AdvanceSampleAfterBurst=false;
 P<int> Iteration{0},StateGeneration{0};
 template<class T>void SetMatrixData(const T&){}
 template<class T>void SetMatrixClasses(const T&){}
 void Reset(){}
};
struct FakeEnv {std::string GetCurrentDataDir(){return "";}};
struct FakeLogger {template<class...T>void LogMessage(T...){}
 template<class...T>void LogMessageEx(T...){}};
namespace RDK {FakeLogger* GetLogger(){return nullptr;}}
constexpr int RDK_EX_INFO=1,RDK_EX_DEBUG=2,RDK_EX_ERROR=3;
class NNeuronTimeLearnerBranch {
public:
 static constexpr int kPhaseDone=2,kPhasePostTune=4;
 P<bool> IsNeedToTrain{true},PostTrainTuneComplete{false},EnablePostTrainMidThreshold{true};
 P<bool> AutoCalibrateFixedLTZThreshold{false},UseFixedLTZThreshold{true},EnableDebug{false};
 P<int> TrainingPhase{kPhasePostTune},PostTrainTipResistanceMode{4},NumInputDendrite{4},PostTrainTipSearchIters{1};
 P<int> PostTuneResult{PostTrainTune::kResultNone};
 P<double> FixedLTZThreshold{1},CalibratedFixedLTZThreshold{1},PostTrainSilentThreshold{1},LTZThreshold{1},TipResistanceCanonFloor{1};
 P<std::vector<double>> TipSynapseResistance{std::vector<double>{30,31,32,33}};
 bool PostTuneInferenceMidPending=false,PostTuneFreeRunActive=false,PostTuneSearchReverted=false;
 bool PostTuneHaveSavedMatrix=false,CanChangeDendLength=false,PostTuneInferenceMidDone=false;
 bool PostTuneRunInvalid=false;
 int PostTuneRunTerminal=PostTrainTune::kResultNone;
 double PostTuneLiveSomaMax=0,PostTuneFreeRunStartTime=-1,PostTuneBestGap=.4;
 int PostTuneLastDatasetIter=-1,PostTunePatternIndex=1,PostTuneSearchMult=2,PostTuneSearchTip=3,PostTuneSearchPass=0;
 std::vector<double> PostTuneMetrics{.5,.2},PostTuneTipSnapshot{10,11,12,13},PostTuneTrialTips{30,31,32,33},PostTuneBestTips{20,21,22,23},PostTuneTargetIsi;
 std::vector<PostTrainTune::SampleMetricState> PostTuneSampleState;
 std::vector<std::vector<double>> PostTunePatterns{{.01},{.02}};
 MDMatrix<double> PostTuneSavedMatrix,PostTuneSavedClasses,InputPattern;
 FakeDataset* Dataset=nullptr;FakeNeuron* Neuron=nullptr;FakeEnv* Environment=nullptr;
 bool setup_result=true,setup_called=false;std::vector<double> setup_tips;
 double probe_metric=.2;
 void FinalizePostTuneMid();void HandlePostTuneFinishIteration();
 double ReadPostTuneProbeMetric()const{return probe_metric;}
 bool SetupPostTuneFreeRunProbes(){setup_called=true;setup_tips=TipSynapseResistance.GetData();PostTuneFreeRunActive=setup_result;return setup_result;}
 void ApplyPostTrainTipMode(bool snapshot){TipSynapseResistance=snapshot?PostTuneTipSnapshot:PostTuneTrialTips;}
 void ApplyPulseGeneratorMute(){}
 void SetLTZThreshold(double){}
 void SetIsNeedToTrain(bool b){IsNeedToTrain=b;}
 void SyncInputPatternToDataset(MDMatrix<double>*){}
 FakeGenerator* GetDatasetGenerator(){return nullptr;}
 UEPtr<UContainer> GetOwner(){return {};}
 void RelinkDendriteSynapsesToDataset(int){}
 double ClampResistance(double x){return x;}
 void PushPostTunePattern(int){}
};
"""
tests=r"""
TEST(BranchUpdate, SelectedBestStartsFreshProbe) {
 NNeuronTimeLearnerBranch b;b.HandlePostTuneFinishIteration();
 EXPECT_TRUE(b.setup_called);EXPECT_EQ(b.setup_tips,std::vector<double>({20,21,22,23}));
 EXPECT_EQ(b.PostTuneMetrics,std::vector<double>({0,0}));
 EXPECT_FALSE(b.PostTrainTuneComplete.GetData());EXPECT_TRUE(b.IsNeedToTrain.GetData());
}
TEST(BranchUpdate, FailedBestFallsBackAndLeavesSilent) {
 NNeuronTimeLearnerBranch b;b.PostTuneMetrics={.5,.6};b.FinalizePostTuneMid();
 EXPECT_EQ(b.TipSynapseResistance.GetData(),std::vector<double>({10,11,12,13}));
 EXPECT_TRUE(b.PostTuneSearchReverted);EXPECT_DOUBLE_EQ(b.FixedLTZThreshold.GetData(),1);
}
TEST(BranchUpdate, ValidSearchTrainStaysSilentAndSuppressesSecondMid) {
 NNeuronTimeLearnerBranch b;b.FinalizePostTuneMid();
 EXPECT_DOUBLE_EQ(b.FixedLTZThreshold.GetData(),1);EXPECT_TRUE(b.PostTuneInferenceMidDone);
 EXPECT_FALSE(b.IsNeedToTrain.GetData());
}
TEST(BranchUpdate, InvalidInferenceKeepsSilentThreshold) {
 NNeuronTimeLearnerBranch b;b.IsNeedToTrain=false;b.TrainingPhase=2;
 b.PostTuneInferenceMidPending=true;b.PostTuneMetrics={.5,.6};b.FinalizePostTuneMid();
 EXPECT_DOUBLE_EQ(b.FixedLTZThreshold.GetData(),1);
 // Records completion semantics; this is not a successful calibration.
 EXPECT_TRUE(b.PostTrainTuneComplete.GetData());EXPECT_TRUE(b.PostTuneInferenceMidDone);
}
TEST(BranchUpdate, ValidInferenceCommitsMeasuredThreshold) {
 NNeuronTimeLearnerBranch b;b.IsNeedToTrain=false;b.TrainingPhase=2;
 b.PostTuneInferenceMidPending=true;b.FinalizePostTuneMid();
 EXPECT_NEAR(b.FixedLTZThreshold.GetData(),.35,1e-12);
}
TEST(BranchRemaining, NaNInferenceMustNotCommitRecognitionThreshold) {
 NNeuronTimeLearnerBranch b;b.IsNeedToTrain=false;b.TrainingPhase=2;
 b.PostTuneInferenceMidPending=true;b.PostTuneMetrics={.5,std::numeric_limits<double>::quiet_NaN()};
 b.FinalizePostTuneMid();EXPECT_GE(b.FixedLTZThreshold.GetData(),.9);
}
TEST(BranchRemaining, SetupFailureMustNotMarkCalibrationComplete) {
 NNeuronTimeLearnerBranch b;b.setup_result=false;b.HandlePostTuneFinishIteration();
 EXPECT_TRUE(b.setup_called);EXPECT_FALSE(b.PostTrainTuneComplete.GetData());
}
TEST(BranchRemaining, FallbackMustNotPublishRejectedCandidateMetrics) {
 NNeuronTimeLearnerBranch b;b.PostTuneMetrics={.5,.6};b.FinalizePostTuneMid();
 EXPECT_TRUE(b.PostTuneSearchReverted);
 // Real finalizer writes these metrics beside restored snapshot weights.
 EXPECT_TRUE(b.PostTuneMetrics.empty())<<"need a fresh snapshot probe or invalidation";
}
"""
bodies="\n".join(extract(s) for s in [
 "void NNeuronTimeLearnerBranch::FinalizePostTuneMid(void)",
 "void NNeuronTimeLearnerBranch::HandlePostTuneFinishIteration(void)"])
Path(sys.argv[1]).write_text("// source SHA256 "+hashlib.sha256(source.read_bytes()).hexdigest()+"\n"+prefix+bodies+tests,encoding="utf-8")
