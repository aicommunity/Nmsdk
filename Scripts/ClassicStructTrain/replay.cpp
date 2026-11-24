// External replay controller. No PulseLib training code is changed or replaced.
#include "../../Rdk/Deploy/Include/rdk.h"
#include "../../Libraries/Nmsdk-PulseLib/Core/NNeuronLearner.h"
#include "../../Libraries/Nmsdk-PulseLib/Core/NNeuronTrainer.h"
#include "../../Libraries/Nmsdk-PulseLib/Core/NSpikeClassifier.h"
#include "../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../Tests/Integration/Support/ConsoleLikeInit.h"
#include <QCoreApplication>
#include <QLockFile>
#include <nlohmann/json.hpp>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

using namespace RDK;
using namespace NMSDK;
using json = nlohmann::json;
namespace fs = std::filesystem;

namespace {
// Forming a pointer to an inherited protected member inside a derived class is
// legal C++. Its type remains a Base::* and can observe an actual Base object.
// There is no downcast, replacement component, or modified Calculate method.
struct LearnerAccess : NNeuronLearner {
 static void bind(NNeuronLearner& n, UEPtr<NPulseNeuron> neuron, const std::vector<UEPtr<NPulseGeneratorTransit>>& sources) {
  n.*(&LearnerAccess::Neuron)=neuron; n.*(&LearnerAccess::Generators)=sources;
  n.DendriteNeuronAmplitude.Assign(6,1,0.0); n.SomaNeuronAmplitude.Assign(6,1,0.0); n.Output.Assign(1,1,0.0);
 }
 static void resetCount(NNeuronLearner& n) { n.*(&LearnerAccess::CountIteration)=0; }
 static int count(const NNeuronLearner& n) { return n.*(&LearnerAccess::CountIteration); }
 static bool first(const NNeuronLearner& n) { return n.*(&LearnerAccess::IsFirstBeat); }
 static const std::vector<int>& ds(const NNeuronLearner& n) { return n.*(&LearnerAccess::DendStatus); }
 static const std::vector<int>& ss(const NNeuronLearner& n) { return n.*(&LearnerAccess::SynapseStatus); }
 static const std::vector<double>& dy(const NNeuronLearner& n) { return n.*(&LearnerAccess::Dissynchronization); }
 static const std::vector<double>& amp(const NNeuronLearner& n) { return n.*(&LearnerAccess::AmpDifference); }
 static const std::vector<double>& maxima(const NNeuronLearner& n) { return n.*(&LearnerAccess::MaxIterSomaAmp); }
 static double start(const NNeuronLearner& n) { return n.*(&LearnerAccess::StartIterTime); }
 static void freeze(NNeuronLearner& n, bool freeze) { n.*(&LearnerAccess::CanChangeDendLength) = !freeze; }
};
struct TrainerAccess : NNeuronTrainer {
 static void bind(NNeuronTrainer& n, UEPtr<NPulseNeuron> neuron, const std::vector<UEPtr<NPulseGeneratorTransit>>& sources) {
  n.*(&TrainerAccess::neuron)=neuron; n.*(&TrainerAccess::generators)=sources;
  n.NeuronAmplitude.Assign(6,1,0.0); n.SomaNeuronAmplitude.Assign(6,1,0.0); n.Output.Assign(1,1,0.0);
 }
 static bool first(const NNeuronTrainer& n) { return n.*(&TrainerAccess::is_first_iter); }
 static bool sync(const NNeuronTrainer& n) { return n.*(&TrainerAccess::is_synchronizated); }
 static const std::vector<int>& dend(const NNeuronTrainer& n) { return n.*(&TrainerAccess::DendriteLength); }
 static const std::vector<int>& syn(const NNeuronTrainer& n) { return n.*(&TrainerAccess::SynapseNum); }
 static const std::vector<double>& dy(const NNeuronTrainer& n) { return n.*(&TrainerAccess::dissynchronization); }
 static const std::vector<double>& maxima(const NNeuronTrainer& n) { return n.*(&TrainerAccess::max_iter_dend_amp); }
 static const std::vector<double>& initial(const NNeuronTrainer& n) { return n.*(&TrainerAccess::InitialDendritePotential); }
 static const std::vector<int>& status(const NNeuronTrainer& n) { return n.*(&TrainerAccess::dend_status); }
 static void structure(NNeuronTrainer& n, const std::vector<int>& d, const std::vector<int>& s) {
  n.*(&TrainerAccess::DendriteLength)=d; n.*(&TrainerAccess::SynapseNum)=s;
 }
};

struct SavedNeuronAccess : NPulseNeuron {
 static void bind(NPulseNeuron& n) {
  auto& soma=n.*(&SavedNeuronAccess::Soma); soma.clear();
  for(int i=1;i<=5;++i) soma.push_back(n.GetComponentL<NPulseMembraneCommon>("Soma"+std::to_string(i),true));
 }
};
struct ClassifierAccess : NSpikeClassifier {
 static void bind(NSpikeClassifier& c) {
  auto& generators=c.*(&ClassifierAccess::generators);generators.clear();
  auto& trainers=c.*(&ClassifierAccess::trainers);trainers.clear();
  for(int i=1;i<=c.NumInputDendrite.GetData();++i)
   generators.push_back(c.GetComponentL<NPulseGeneratorTransit>("Source"+std::to_string(i),true));
  for(int i=1;i<=c.NumNeurons.GetData();++i)
   trainers.push_back(c.GetComponentL<NNeuronTrainer>("NeuronTrainer"+std::to_string(i),true));
 }
};

bool zero(const std::vector<int>& v) { return !v.empty() && std::all_of(v.begin(), v.end(), [](int x){return x == 0;}); }
double absmax(const std::vector<double>& v) {
 double result = 0;
 for(double x : v) { if(!std::isfinite(x)) return INFINITY; result = std::max(result, std::abs(x)); }
 return result;
}
MDMatrix<double> matrix(const std::vector<double>& v) {
 if(v.size() != 5 || !std::all_of(v.begin(), v.end(), [](double x){return std::isfinite(x);}))
  throw std::runtime_error("Expected five finite input delays");
 MDMatrix<double> m; m.Assign(5, 1, 0.0);
 for(int i=0; i<5; ++i) m(i,0)=v[i];
 return m;
}

struct Replay {
 json manifest;
 fs::path repo, out;
 UApplication* app{};
 UEPtr<UEnvironment> env;
 UEPtr<UContainer> model;
 UEPtr<NNeuronLearner> learner;
 UEPtr<NNeuronTrainer> trainer;
 std::ofstream results, history, waveforms;
 std::string kind, suite, key;
 int repeat{1};
 int maxIterations{1000};
 double wallTimeout{600};

 explicit Replay(const fs::path& file, fs::path output) : out(std::move(output)) {
  std::ifstream in(file); if(!in) throw std::runtime_error("Cannot read manifest"); in >> manifest;
  repo = fs::u8path(manifest.at("repository").get<std::string>());
  fs::create_directories(out);
  results.open(out / "results.jsonl", std::ios::app);
  history.open(out / "iterations.jsonl", std::ios::app);
  waveforms.open(out / "waveforms.jsonl", std::ios::app);
  if(!results || !history) throw std::runtime_error("Cannot open replay outputs");
  maxIterations=manifest["defaults"]["max_iterations"];
  wallTimeout=manifest["defaults"]["wall_timeout_seconds"];
  for(const auto name:{"NMSDK_DIAG_PROFILE","NMSDK_DIAG_NT_STOP"}) qunsetenv(name);
  if(manifest.contains("diagnostic_core")) {
   const auto& options=manifest.at("diagnostic_core");
   if(options.contains("profile")) qputenv("NMSDK_DIAG_PROFILE",QByteArray::fromStdString(options.at("profile").get<std::string>()));
   if(options.contains("nt_stop")) qputenv("NMSDK_DIAG_NT_STOP",QByteArray::fromStdString(options.at("nt_stop").get<std::string>()));
  }
  app=NmsdkTests::InitEngineForPulseLibTests().application;
  if(!app) throw std::runtime_error("No application from test engine initialization");
  app->SetApplicationFileName("ClassicStructTrainReplay-"+std::to_string(QCoreApplication::applicationPid())+".exe");
  if(auto log=RDK::GetLogger()) { log->SetDebugMode(false); log->SetDebugSysEventsMask(0); }
 }

 ~Replay() {
  // The test engine lives in a static AppCore. Shut it down while Qt's local
  // QCoreApplication is still alive, rather than during static destruction.
  if(app) { try { app->UnInit(); } catch(...) {} }
 }

 void writeResult(json record) {
  if(manifest.contains("variant")) record["variant"]=manifest.at("variant");
  record["suite"]=suite; record["case"]=key; record["repeat"]=repeat;
  results << record.dump() << '\n'; results.flush();
  std::cout << "[ClassicReplay] " << suite << '/' << key << " repeat=" << repeat
            << " status=" << record.value("status", "recorded") << std::endl;
 }

 void load(const std::string& requestedKind) {
  learner=nullptr; trainer=nullptr; model=nullptr; env=nullptr; kind=requestedKind;
  fs::path relative;
  for(const auto& t : manifest["templates"]) if(t["kind"] == kind) relative=fs::u8path(t["config"].get<std::string>());
  if(relative.empty()) throw std::runtime_error("Missing prepared configuration");
  if(!app->OpenProject((repo / relative).string())) throw std::runtime_error("OpenProject failed");
  Core_SelectChannel(0);
  env=RDK::GetEnvironment(); if(!env) throw std::runtime_error("Missing environment");
  env->SetMinInterstepsInterval(0); env->SetMaxCalcTime(0);
  model=env->GetModel(); if(!model) throw std::runtime_error("Missing model");
  learner=model->GetComponentL<NNeuronLearner>("Subject", true);
  trainer=model->GetComponentL<NNeuronTrainer>("Subject", true);
  if((kind=="learner" && !learner) || (kind=="trainer" && !trainer)) throw std::runtime_error("Subject has wrong class");
  if(int(model->GetTimeStep()) != 2000) throw std::runtime_error("Model calculation frequency is not 2000 Hz");
  env->SetCurrentDataDir((out / "native").string()); fs::create_directories(out / "native");
 }

 double time() const { return env->GetTime().GetDoubleTime(); }
 bool needs() const { return learner ? learner->IsNeedToTrain.GetData() : trainer->IsNeedToTrain.GetData(); }
 void step() { if(!env->Calculate()) throw std::runtime_error("Environment calculation failed"); }
 std::vector<int> dend() const { return learner ? learner->DendriteLength.GetData() : TrainerAccess::dend(*trainer); }
 std::vector<int> syn() const { return learner ? learner->NumSynapse.GetData() : TrainerAccess::syn(*trainer); }

 json structureReadback() const {
  json r={{"consistent",true},{"all_initialized",true},{"inputs",json::array()}};
  auto neuron=learner ? learner->GetComponentL<NPulseNeuron>("Neuron",true) : trainer->GetComponentL<NPulseNeuron>("Neuron",true);
  const auto d=dend(), s=syn();
  if(!neuron || d.size()!=5 || s.size()!=5) { r["consistent"]=false; return r; }
  for(int i=0;i<5;++i) {
   const auto name="Dendrite"+std::to_string(i+1)+"_"+std::to_string(d[i]);
   auto membrane=neuron->GetComponentL<NPulseMembrane>(name,true);
   int existing=0, links=0, initialized=0, active=0;
   if(membrane) for(int j=1;j<=s[i];++j) {
    const auto synName="ExcSynapse"+std::to_string(j);
    auto synapse=membrane->GetComponentL<NPulseSynapseCommon>(synName,true);
    if(synapse) { ++existing; if(synapse->IsInit()) ++initialized; if(synapse->GetActivity()) ++active; }
    if((learner ? static_cast<UNet*>(learner.Get()) : static_cast<UNet*>(trainer.Get()))->CheckLink(
        "Source"+std::to_string(i+1),"Output","Neuron."+name+"."+synName,"Input")) ++links;
   }
   const bool ok=membrane && existing==s[i] && links==s[i];
   r["inputs"].push_back({{"dendrite",i+1},{"expected_length",d[i]},{"expected_synapses",s[i]},
                          {"input_segment_exists",bool(membrane)},{"segment_initialized",membrane && membrane->IsInit()},
                          {"existing_synapses",existing},{"initialized_synapses",initialized},{"active_synapses",active},{"generator_links",links}});
   if(!ok) r["consistent"]=false;
   if(!membrane || !membrane->IsInit() || initialized!=s[i]) r["all_initialized"]=false;
  }
  return r;
 }

 json state() const {
  json r={{"model_time",time()},{"dendrites",dend()},{"synapses",syn()},{"is_need_to_train",needs()}};
  if(learner) {
   r["iterations_internal"]=LearnerAccess::count(*learner);
   r["dend_status"]=LearnerAccess::ds(*learner); r["synapse_status"]=LearnerAccess::ss(*learner);
   r["dissynchronization"]=LearnerAccess::dy(*learner); r["amp_difference"]=LearnerAccess::amp(*learner);
   r["soma_maxima"]=LearnerAccess::maxima(*learner);
   r["initial_soma_potential"]=learner->InitialSomaPotential.GetData();
   r["threshold"]=learner->LTZThreshold.GetData(); r["calculate_mode"]=learner->CalculateMode.GetData();
   r["signal_present"]=absmax(LearnerAccess::maxima(*learner)) > 1e-9;
   r["physical_bounds_pass"]=absmax(LearnerAccess::dy(*learner))<=.0050000001 && absmax(LearnerAccess::amp(*learner))<=.0002850001;
  } else {
   r["initial_dendrite_potential"]=TrainerAccess::initial(*trainer);
   r["dend_status"]=TrainerAccess::status(*trainer);
   r["dissynchronization"]=TrainerAccess::dy(*trainer); r["soma_maxima"]=TrainerAccess::maxima(*trainer);
   r["synchronized"]=TrainerAccess::sync(*trainer);
   r["threshold"]=trainer->LTZThreshold.GetData(); r["calculate_mode"]=trainer->CalculateMode.GetData();
   r["signal_present"]=absmax(TrainerAccess::maxima(*trainer)) > 1e-9;
  }
  return r;
 }

 void pattern(const std::vector<double>& p) {
  const auto m=matrix(p);
  if(learner) learner->InputPattern=m; else trainer->InputPattern=m;
 }

 json train(const std::vector<double>& p, bool cold, int fixedIterations=0, bool freezeDendrites=false) {
  if(cold) load(kind);
  if(learner) {
   learner->ExperimentMode=false;
   learner->CalculateMode=fixedIterations ? 1 : (cold ? (suite=="repro"?manifest.at("repro_job").value("cold_mode_override",0):0) : 1);
   learner->IsNeedToTrain=true;
   pattern(p);
   // Use the existing second-pattern status rule for synapse-only phases.
   learner->ExperimentNum.SetDataDirect(freezeDendrites ? 2 : 0);
   LearnerAccess::freeze(*learner, freezeDendrites);
  } else {
   if(!cold) throw std::runtime_error("Trainer is only trained from a fresh configuration");
   trainer->CalculateMode=6; trainer->IsNeedToTrain=true; pattern(p);
  }
  if(cold) { if(!model->Build()) throw std::runtime_error("Build failed"); if(!env->Reset()) throw std::runtime_error("Reset failed"); }
  int iterations=0, dendriteIterations=0, synapseIterations=0;
  const auto wallStart=std::chrono::steady_clock::now(); const double started=time();
  std::string status="completed";
  std::string stopReason="native_completion";
  int ticks=0;
  const int observedTicks=manifest.value("training_trace_ticks",0);
  while(true) {
   const int beforeCount=learner ? LearnerAccess::count(*learner) : 0;
   const bool beforeFirst=trainer && TrainerAccess::first(*trainer);
   const bool observe=ticks<observedTicks;
   json before;
   if(observe) before=state();
   step(); ++ticks;
   if(observe) {
    auto after=state();
    writeDiagnosticTick("training",ticks,before,after);
   }
   if(learner && key=="learner-111" && beforeCount>=5 && beforeCount<=10) {
    const auto& m=learner->SomaNeuronAmplitude.GetData();
    std::vector<double> soma;
    for(int i=0;i<m.GetRows();++i) soma.push_back(m(i,0));
    waveforms << json({{"suite",suite},{"case",key},{"repeat",repeat},{"iteration",beforeCount},
                       {"time",time()-1.0/2000},{"soma_potential",soma}}).dump() << '\n';
   }
   if(manifest.contains("repro_job") && manifest.at("repro_job").value("record_training_waveform",false)) {
    const auto& job=manifest.at("repro_job");const int iteration=learner?beforeCount:iterations;
    if(iteration>=job.value("trace_from_iteration",0) && iteration<=job.value("trace_to_iteration",1000)) {
     const auto& values=learner?learner->SomaNeuronAmplitude.GetData():trainer->SomaNeuronAmplitude.GetData();
     std::vector<double> soma;for(int i=0;i<values.GetRows();++i)soma.push_back(values(i,0));
     waveforms<<json({{"case",key},{"kind",kind},{"repeat",repeat},{"iteration",iteration},{"time",time()-1.0/2000},{"soma_potential",soma}}).dump()<<'\n';
    }
   }
   bool boundary=false;
   if(learner) {
    int count=LearnerAccess::count(*learner);
    boundary=count>beforeCount; iterations=std::max(iterations,count);
    if(boundary) {
     if(!zero(LearnerAccess::ds(*learner))) dendriteIterations=0;
     else if(dendriteIterations==0) dendriteIterations=iterations;
     if(!zero(LearnerAccess::ss(*learner))) synapseIterations=0;
     else if(synapseIterations==0) synapseIterations=iterations;
    }
   } else {
    boundary=beforeFirst && !TrainerAccess::first(*trainer);
    if(boundary) { ++iterations; if(!TrainerAccess::sync(*trainer)) dendriteIterations=iterations; }
   }
   if(boundary) {
    auto h=state(); h["suite"]=suite; h["case"]=key; h["repeat"]=repeat; h["iteration"]=iterations;
    auto readback=structureReadback();
    if(!readback["all_initialized"].get<bool>() && manifest.value("allow_initialization_grace_tick",false)) {
     h["before_initialization_grace_tick"]=readback;
     step();++ticks;readback=structureReadback();
     h["after_initialization_grace_tick"]=readback;
    }
    if(!readback["all_initialized"].get<bool>()) {
     h["structure_readback"]=readback;
     history << h.dump() << '\n'; history.flush();
     status="uninitialized_dynamic_structure";
     stopReason=status;
     break;
    }
    history << h.dump() << '\n';
   }
   if(fixedIterations>0 && iterations>=fixedIterations && (!learner || LearnerAccess::first(*learner))) {stopReason="scheduled_iterations";break;}
   if(!fixedIterations && !needs()) break;
   if(!fixedIterations && learner && iterations>0 && LearnerAccess::first(*learner)
       && zero(LearnerAccess::ds(*learner)) && zero(LearnerAccess::ss(*learner))) {stopReason="zero_status_at_boundary";break;}
   if(iterations>=maxIterations) {status="iteration_limit";stopReason=status;break;}
   if(time()-started>maxIterations/1.5+1) {status="model_time_limit";stopReason=status;break;}
   if(ticks%1024==0 && std::chrono::duration<double>(std::chrono::steady_clock::now()-wallStart).count()>wallTimeout) {
    status="wall_timeout";stopReason=status;break;
   }
  }
  auto r=state(); r["status"]=status; r["kind"]=kind; r["pattern"]=p; r["iterations"]=iterations;
  r["stop_reason"]=stopReason;
  r["dendrite_iterations"]=dendriteIterations; r["ticks"]=ticks; r["elapsed_model_time"]=time()-started;
  r["synapse_iterations"]=learner ? synapseIterations : iterations-dendriteIterations;
  r["model_time_from_iterations"]=iterations/1.5;
  r["elapsed_wall_seconds"]=std::chrono::duration<double>(std::chrono::steady_clock::now()-wallStart).count();
  r["structure_readback"]=structureReadback();
  if(status=="completed" && !r.value("signal_present",false)) r["status"]="completed_without_measured_signal";
  history.flush(); waveforms.flush(); return r;
 }

 json recognize(const std::vector<json>& dataset, int targetClass) {
  if(learner) learner->IsNeedToTrain=false; else trainer->IsNeedToTrain=false;
  const auto originalDend=dend(), originalSyn=syn();
  std::vector<int> answers; int tp=0, fp=0, tn=0, fn=0;
  for(const auto& sample : dataset) {
   pattern(sample["pattern"].get<std::vector<double>>());
   bool fired=false;
   auto neuron=learner ? learner->GetComponentL<NPulseNeuron>("Neuron",true) : trainer->GetComponentL<NPulseNeuron>("Neuron",true);
   if(!neuron) throw std::runtime_error("Recognition neuron is absent");
   auto ltz=neuron->GetComponentL<NLTZone>("LTZone",true);
   if(!ltz) throw std::runtime_error("Recognition LTZone is absent");
   for(int tick=0; tick<1334; ++tick) { step(); if(ltz->Output(0,0)>.001) fired=true; }
   answers.push_back(fired ? 1 : 0);
   const bool own=sample.at("class").get<int>()==targetClass;
   if(own) { if(fired) ++tp; else ++fn; } else { if(fired) ++fp; else ++tn; }
  }
  if(dend()!=originalDend || syn()!=originalSyn) throw std::runtime_error("Structure changed during recognition");
  const double n=double(answers.size());
  return {{"status","completed"},{"kind",kind},{"answers",answers},{"TP",tp},{"FP",fp},{"FN",fn},{"TN",tn},
          {"precision",tp+fp ? json(double(tp)/(tp+fp)) : json(nullptr)},
          {"recall",tp+fn ? json(double(tp)/(tp+fn)) : json(nullptr)},
          {"accuracy",n ? json((tp+tn)/n) : json(nullptr)},
          {"balanced_accuracy",tp+fn && tn+fp ? json(.5*(double(tp)/(tp+fn)+double(tn)/(tn+fp))) : json(nullptr)},
          {"empirical_risk",n ? json((fp+fn)/n) : json(nullptr)}, {"error_count",fp+fn},
          {"dendrites",originalDend},{"synapses",originalSyn},{"structure_unchanged",true},
          {"structure_readback",structureReadback()}};
 }

 void freezeStructure(const std::vector<int>& d, const std::vector<int>& s) {
  if(d.size()!=5 || s.size()!=5) throw std::runtime_error("Invalid archived frozen structure");
  if(learner) learner->IsNeedToTrain=false; else trainer->IsNeedToTrain=false;
  // A frozen model is constructed before initialization, as a loaded model is.
  // This is distinct from the native algorithm's dynamic training path above.
  env->ModelUnInit();
  auto neuron=learner ? learner->GetComponentL<NPulseNeuron>("Neuron",true) : trainer->GetComponentL<NPulseNeuron>("Neuron",true);
  if(!neuron) throw std::runtime_error("No neuron for frozen recognition variant");
  neuron->StructureBuildMode=2; neuron->NumDendriteMembranePartsVec=d; neuron->NumSomaMembraneParts=5;
  if(!neuron->Build()) throw std::runtime_error("Cannot build archived frozen structure");
  auto subject=learner ? static_cast<UNet*>(learner.Get()) : static_cast<UNet*>(trainer.Get());
  for(int i=0;i<5;++i) {
   const std::string segment="Dendrite"+std::to_string(i+1)+"_"+std::to_string(d[i]);
   auto membrane=neuron->GetComponentL<NPulseMembrane>(segment,true);
   auto source=subject->GetComponentL<NPulseGeneratorTransit>("Source"+std::to_string(i+1),true);
   if(!membrane || !source) throw std::runtime_error("Frozen input segment or generator missing");
   membrane->NumExcitatorySynapses=s[i];
   if(!membrane->Build()) throw std::runtime_error("Frozen synapse build failed");
   source->DisconnectAll("Output");
   for(int j=1;j<=s[i];++j) {
    const auto synName="ExcSynapse"+std::to_string(j);
    auto synapse=membrane->GetComponentL<NPulseSynapseCommon>(synName,true);
    if(!synapse) throw std::runtime_error("Frozen synapse missing");
    // Storage templates can be inactive. A reconstructed static input uses all
    // of its explicitly requested synapses; native training is left untouched.
    synapse->SetActivity(true);
    if(j>1) synapse->Resistance=learner ? learner->SynapseResistanceStep.GetData() : trainer->SynapseResistanceStep.GetData();
    if(!subject->CreateLink("Source"+std::to_string(i+1),"Output","Neuron."+segment+"."+synName,"Input"))
     throw std::runtime_error("Cannot connect frozen input");
   }
  }
  if(learner) { learner->DendriteLength.SetDataDirect(d); learner->NumSynapse.SetDataDirect(s); }
  else TrainerAccess::structure(*trainer,d,s);
  if(learner) learner->StructureBuildMode.SetDataDirect(0);
  else trainer->StructureBuildMode.SetDataDirect(0);
  // NPulseNeuron::Build initializes newly created membrane segments early.
  // Clear those flags after all frozen synapses exist, then initialize the
  // complete static subtree. Native dynamic training never uses this path.
  neuron->Init();
  neuron->UnInit();
  neuron->Init();
  env->ModelInit();
  if(!env->Reset()) throw std::runtime_error("Frozen model Reset failed");
  const auto readback=structureReadback();
  if(!readback.at("consistent").get<bool>() || !readback.at("all_initialized").get<bool>())
   throw std::runtime_error("Frozen physical structure does not match archive or is uninitialized: "+readback.dump());
 }

 std::vector<double> sample(int id) const { return manifest["dataset"].at(id-1)["pattern"].get<std::vector<double>>(); }

 void advancePeriods(int periods) { for(int tick=0;tick<periods*1334;++tick) step(); }

 bool saveSnapshot(const fs::path& directory) {
  // SaveFileSafe uses a CWD-relative save.tmp. Serialize only serialization;
  // independent simulations still run concurrently from Bin/Platform/Win.
  QLockFile snapshotLock(QString::fromStdString((repo/"Bin/Platform/Win/.classic-struct-snapshot.lock").string()));
  snapshotLock.setStaleLockTime(0);
  if(!snapshotLock.tryLock(180000)) throw std::runtime_error("Snapshot serialization lock timed out");
  fs::create_directories(directory);
  app->SetProjectPath(directory.string()+"/"); app->SetProjectFileName("project.ini");
  const bool saved=app->SaveProject();
  return saved && fs::is_regular_file(directory/"Model_00.xml") && fs::file_size(directory/"Model_00.xml")>0
               && fs::is_regular_file(directory/"Parameters_00.xml") && fs::file_size(directory/"Parameters_00.xml")>0;
 }

 void modes() {
  kind="learner";
  const auto p=manifest["mode_patterns"].get<std::vector<std::vector<double>>>();
  for(const auto& test : manifest["mode_cases"]) {
   json precondition=nullptr; key=test["case"]; const int row=test["source_row"]; const auto& v=test["values"];
   if(row>=35) {
    auto trained=train(p[0],true);
    if(trained["status"]=="completed" && needs() && learner->CalculateMode.GetData()==0
       && zero(LearnerAccess::ds(*learner)) && zero(LearnerAccess::ss(*learner))) step();
    if(trained["status"]=="completed" && needs()) trained["status"]="native_completion_failed";
    precondition=state();
    if(trained["status"]!="completed") { trained["phase"]="precondition"; trained["source_row"]=row; writeResult(trained); continue; }
    learner->CalculateMode=v["H"].get<int>(); learner->IsNeedToTrain=v["I"]=="об";
    auto before=state(); json changes=json::array();
    for(size_t i=1;i<p.size();++i) { pattern(p[i]); advancePeriods(2); changes.push_back(state()); }
    writeResult({{"training_precondition",precondition},{"status","recorded"},{"source_row",row},{"before",before},{"pattern_changes",changes}});
    continue;
   }
   const bool fresh=row>=28;
   const bool same=v["L"]=="обучен";
   if(!fresh) {
    auto trained=train(p[0],true);
    if(trained["status"]=="completed" && needs() && learner->CalculateMode.GetData()==0
       && zero(LearnerAccess::ds(*learner)) && zero(LearnerAccess::ss(*learner))) step();
    if(trained["status"]=="completed" && needs()) trained["status"]="native_completion_failed";
    precondition=state();
    if(trained["status"]!="completed") { trained["phase"]="precondition"; trained["source_row"]=row; writeResult(trained); continue; }
    learner->CalculateMode=v["H"].get<int>();
    learner->IsNeedToTrain=v["I"]=="об";
   } else { load(kind); if(!model->Build() || !env->Reset()) throw std::runtime_error("Fresh model initialization failed"); }
   if(!same) pattern(p[1]);
   auto before=state();
   learner->CalculateMode=v["J"].get<int>();
   const bool targetTrain=v["K"]=="об";
   learner->IsNeedToTrain=targetTrain;
   const auto immediate=state(); const auto d=dend(), s=syn();
   advancePeriods(2);
   auto after=state();
   const bool thresholdOk=std::abs(immediate["threshold"].get<double>()-(targetTrain ? 100.0 : .0115))<1e-12;
   const bool recognitionStable=targetTrain || (dend()==d && syn()==s);
   writeResult({{"training_precondition",precondition},{"status","recorded"},{"source_row",row},{"before",before},{"immediate",immediate},{"after_two_periods",after},
         {"threshold_matches_requested_mode",thresholdOk},{"recognition_structure_unchanged",recognitionStable},
         {"archived_transition_note",v["M"]},{"target_pattern_already_learned",same}});
  }
 }

 void diagnostics() {
  kind="learner"; key="observer-noninterference";
  auto observed=train(sample(22),true);
  const auto d=dend(), s=syn(); const int ticks=observed["ticks"];
  load(kind); learner->ExperimentMode=false; learner->CalculateMode=0; learner->IsNeedToTrain=true;
  learner->ExperimentNum.SetDataDirect(0); pattern(sample(22));
  if(!model->Build() || !env->Reset()) throw std::runtime_error("Observer control initialization failed");
  for(int tick=0;tick<ticks;++tick) step();
  auto control=state();
  writeResult({{"status","recorded"},{"observed",observed},{"control",control},
        {"same_structure",dend()==d && syn()==s},{"same_need_to_train",control["is_need_to_train"]==observed["is_need_to_train"]}});
  key="mode-change-iteration-clock";
  learner->CalculateMode=1; learner->IsNeedToTrain=true; pattern(sample(37));
  const double transitionTime=time(); step();
  writeResult({{"status","recorded"},{"transition_model_time",transitionTime},{"new_iteration_start",LearnerAccess::start(*learner)},
        {"start_matches_transition",std::abs(transitionTime-LearnerAccess::start(*learner))<1e-9}});
  key="recreate-subject";
  auto recreated=train(sample(22),true);
  writeResult({{"status","recorded"},{"training",recreated},{"same_structure_after_recreation",recreated["dendrites"]==observed["dendrites"] && recreated["synapses"]==observed["synapses"]}});
  key="save-reload-trained-model";
  if(recreated["status"]!="completed") {
   writeResult({{"status","not_run_precondition"},{"reason","Native training did not produce a trained model"},
                {"training_status",recreated["status"]}});
   key="save-reload-partial-model";
  }
  const auto before=state();
  const fs::path saved=out/"roundtrip"; fs::create_directories(saved);
  app->SetProjectPath(saved.string()+"/"); app->SetProjectFileName("project.ini");
  if(!app->SaveProject()) throw std::runtime_error("SaveProject failed for roundtrip copy");
  learner=nullptr; trainer=nullptr; model=nullptr; env=nullptr;
  if(!app->OpenProject((saved/"project.ini").string())) throw std::runtime_error("Roundtrip OpenProject failed");
  Core_SelectChannel(0); env=RDK::GetEnvironment(); model=env->GetModel();
  learner=model->GetComponentL<NNeuronLearner>("Subject",true);
  if(!learner) throw std::runtime_error("Reloaded Subject missing");
  auto after=state();
  writeResult({{"status","recorded"},{"before",before},{"after",after},
        {"same_structure",before["dendrites"]==after["dendrites"] && before["synapses"]==after["synapses"]},
        {"structure_readback",structureReadback()}});
 }

 void run(const std::string& selectedSuite, int selectedRepeat, int onlyId) {
  suite=selectedSuite; repeat=selectedRepeat;
  if(suite=="legacy") { legacy(); return; }
  if(suite=="repro") { repro(); return; }
  const auto ids=manifest["selected_ids"].get<std::vector<int>>();
  if(suite=="smoke" || suite=="cold" || suite=="structures") {
   std::vector<int> selected=ids;
   if(suite=="smoke") selected={22};
   if(suite=="structures") { selected.resize(150); std::iota(selected.begin(), selected.end(), 1); }
   for(const auto& k : {std::string("learner"),std::string("trainer")}) for(int id : selected) {
    if(onlyId && id!=onlyId) continue;
    kind=k; key=k+"-"+std::to_string(id); auto r=train(sample(id),true); r["id"]=id;
    if(suite=="smoke") {
     const fs::path snapshot=out/("effective-model-"+kind);
     r["snapshot_saved"]=saveSnapshot(snapshot); r["snapshot_directory"]=snapshot.string();
    }
    writeResult(r);
   }
  } else if(suite=="warm") {
   kind="learner"; int index=0;
   for(const auto& input : manifest["warm_sequence"]) {
    key="transition-"+std::to_string(index); auto r=train(input["pattern"].get<std::vector<double>>(),index==0);
    r["id"]=input["id"]; r["transition_index"]=index++; writeResult(r);
    if(r["status"]!="completed") {
     for(int skipped=index;skipped<int(manifest["warm_sequence"].size());++skipped) {
      key="transition-"+std::to_string(skipped);
      writeResult({{"status","not_run_precondition"},{"kind","learner"},{"transition_index",skipped},
                   {"id",manifest["warm_sequence"][skipped]["id"]},{"training_status",r["status"]},
                   {"reason","The preceding native training did not complete; the required previous learned state is unavailable"}});
     }
     break;
    }
   }
  } else if(suite=="recognition") {
   const auto data=manifest["dataset"].get<std::vector<json>>();
   for(const auto& k : {std::string("learner"),std::string("trainer")}) for(int id : ids) {
    if(onlyId && id!=onlyId) continue;
    kind=k; key=k+"-"+std::to_string(id); auto trained=train(sample(id),true);
    if(trained["status"]!="completed") { trained["id"]=id; trained["phase"]="training"; writeResult(trained); continue; }
    auto r=recognize(data,(id-1)/50+1); r["id"]=id; r["training"]=trained; writeResult(r);
   }
   for(const auto& variant : manifest["recognition_models"]) {
    // Frozen recognition is a supplementary deterministic archive control;
    // the three protocol repeats apply to newly trained models above.
    if(repeat!=1) break;
    const int id=variant["id"]; if(onlyId && id!=onlyId) continue;
    kind=variant["kind"].get<std::string>(); key=kind+"-"+std::to_string(id)+"-frozen-"+std::to_string(variant["variant_index"].get<int>());
    try {
     load(kind);
     if(learner) learner->IsNeedToTrain=false; else trainer->IsNeedToTrain=false;
     pattern(sample(id));
     freezeStructure(variant["dendrites"].get<std::vector<int>>(),variant["synapses"].get<std::vector<int>>());
     auto r=recognize(data,(id-1)/50+1); r["id"]=id; r["frozen_archive_structure"]=true; r["reference"]=variant; writeResult(r);
    } catch(const std::exception& error) {
     writeResult({{"status","frozen_reconstruction_error"},{"reason",error.what()},
                  {"id",id},{"kind",kind},{"frozen_archive_structure",true},{"reference",variant}});
    }
   }
  } else if(suite=="two_examples") {
   const auto fullData=manifest["dataset"].get<std::vector<json>>();
   for(const std::string scheme : {"baseline51","baseline61","midpoint","2_2","3_4","0_1","0_1_4_subset","0_1_4_full"}) {
    kind="learner"; key=scheme+"-initial";
    auto initial=sample(scheme=="baseline61" ? 61 : 51);
    if(scheme=="midpoint") { auto other=sample(61); for(int i=0;i<5;++i) initial[i]=(initial[i]+other[i])*.5; }
    auto trained=train(initial,true);
    if(trained["status"]!="completed") {
     const int last=scheme.rfind("baseline",0)==0 || scheme=="midpoint" ? 0 : scheme=="3_4" ? 7 : scheme=="0_1" ? 18 : 13;
     for(int skipped=0;skipped<=last;++skipped) {
      key=scheme+"-epoch-"+std::to_string(skipped);
      writeResult({{"status","not_run_precondition"},{"scheme",scheme},{"epoch",skipped},{"training_status",trained["status"]},
                   {"reason","Initial native training did not produce the learned state required by this epoch"},{"training",trained}});
     }
     continue;
    }
    std::vector<json> data=fullData;
    if(scheme=="3_4" || scheme=="0_1" || scheme=="2_2") {
     data.clear(); for(const auto& x:fullData) { int id=x["id"]; if((id>=41&&id<=60)||(id>=101&&id<=110)) data.push_back(x); }
    } else if(scheme=="0_1_4_subset") { data.clear(); for(int id=51;id<=60;++id) data.push_back(fullData[id-1]); }
    const int epochs=scheme.rfind("baseline",0)==0 || scheme=="midpoint" ? 0 : scheme=="3_4" ? 7 : scheme=="0_1" ? 18 : 13;
    for(int epoch=0;epoch<=epochs;++epoch) {
     if(epoch>0) {
      key=scheme+"-train-"+std::to_string(epoch);
      if(scheme=="2_2" || scheme=="3_4") {
       if(epoch>1) trained=train(sample(51),false,scheme=="2_2" ? 2 : 3);
       trained=train(sample(61),false,scheme=="2_2" ? 2 : 4);
      } else {
       trained=train(sample(61),false,1);
       if(scheme!="0_1") trained=train(sample(61),false,4,true);
      }
     }
     key=scheme+"-epoch-"+std::to_string(epoch);
     auto r=recognize(data,2); r["scheme"]=scheme; r["epoch"]=epoch; r["training"]=trained; writeResult(r);
    }
   }
   key="0_1_2_4_ambiguous";
   writeResult({{"status","source_gap"},{"reason","The archive preserves preliminary results but no unambiguous implementation of the erroneous 0/(1(2)+4) schedule. It is not replaced by the corrected 1+4 algorithm."}});
  } else if(suite=="modes") {
   modes();
  } else if(suite=="diagnostics") {
   diagnostics();
  } else {
   throw std::runtime_error("Unsupported suite: "+suite);
  }
 }

#include "diagnosis_trace.inc"
#include "legacy_replay.inc"
#include "training_file_protocol.inc"
#include "training_replay.inc"
};
}

int main(int argc, char** argv) {
#ifndef NDEBUG
 std::cerr << "Classic experiments require a Release build; Debug execution is disabled.\n";
 return 2;
#endif
 QCoreApplication qt(argc,argv);
 fs::path manifest, output;
 std::string suite="smoke"; int repeat=1, onlyId=0;
 for(int i=1;i<argc;++i) {
  std::string a=argv[i];
  if(i+1>=argc) { std::cerr << "Expected value after " << a << '\n'; return 2; }
  std::string v=argv[++i];
  if(a=="--manifest") manifest=fs::u8path(v); else if(a=="--output") output=fs::u8path(v);
  else if(a=="--suite") suite=v; else if(a=="--repeat") repeat=std::stoi(v);
  else if(a=="--only-id") onlyId=std::stoi(v); else { std::cerr << "Unknown option " << a << '\n'; return 2; }
 }
 if(manifest.empty() || output.empty()) { std::cerr << "Required: --manifest path --output path [--suite name --repeat N --only-id ID]\n"; return 2; }
 try { Replay replay(manifest,output); replay.run(suite,repeat,onlyId); return 0; }
 catch(const RDK::UException& e) { std::cerr << "RDK exception: " << e.what() << std::endl; }
 catch(const std::exception& e) { std::cerr << "Replay failed: " << e.what() << std::endl; }
 catch(...) { std::cerr << "Replay failed: unknown exception" << std::endl; }
 return 1;
}
