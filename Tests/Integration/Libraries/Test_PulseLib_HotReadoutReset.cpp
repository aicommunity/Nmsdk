#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseGenerator.h"
#include "../Support/ConsoleLikeInit.h"
#include "TimeLearner/ModelInspection.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <locale>
#include <sstream>
#include <tuple>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;

void SaveResetArtifact(const std::string& name,const std::string& data)
{
 const char* directory=std::getenv("TL_HOT_READOUT_DIR");if(!directory)return;
 auto path=std::filesystem::path(directory)/name;std::filesystem::create_directories(path.parent_path());
 std::ofstream file(path,std::ios::binary);file<<data;EXPECT_TRUE(file.good());
}

template<class Learner> void WarmReset(const bool branch,const int count,const unsigned frequency,
 const bool xmlRoundtrip=false,const bool includeState=false)
{
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 const std::string kind=branch?"Branch":"Classic";
 const std::string folder=kind+"-N"+std::to_string(count)+"-f"+std::to_string(frequency)+
  (xmlRoundtrip?(includeState?"-state1":"-state0"):"")+"/";
 core.environment->DestroyModel();ASSERT_TRUE(core.environment->CreateModel("NModel"));
 auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());ASSERT_TRUE(model);model->SetGlobalTimeStep(frequency);
 auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(learner);
 learner->Name="Learner";learner->ControllerVersion=1;learner->StructureBuildMode=1;
 learner->NormalizationMode=0;learner->NumInputDendrite=count;
 learner->DendriteLength=std::vector<int>(count,1);learner->NumSynapse=std::vector<int>(count,1);
 learner->InitialSomaPotential=std::vector<double>(count,.015);
 learner->TipSynapseResistance=std::vector<double>(count,86e6);
 learner->CalculateMode=1;learner->IsNeedToTrain=true;learner->EnablePostTrainTuning=false;
 learner->SyncCapacitanceTrim=0;learner->FixedLTZThreshold=1.;learner->LTZThreshold=1.;
 MDMatrix<double> pattern;pattern.Assign(count,1,.01);learner->InputPattern=pattern;
 ASSERT_NE(model->AddComponent(learner),ForbiddenId);core.environment->ModelInit();learner->IsNeedToTrain=false;
 auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
 learner->StructureBuildMode=0;neuron->StructureBuildMode=0;neuron->UseElementDefaults=false;
 auto channel=neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);ASSERT_TRUE(channel);
 auto synapse=neuron->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);ASSERT_TRUE(synapse);
 channel->Capacity=1.23e-9;synapse->Resistance=91e6;
 std::vector<double> tips(count,86e6);tips[0]=91e6;learner->TipSynapseResistance=tips;
 core.environment->Reset();
 ASSERT_EQ(learner->SomaNeuronAmplitude.GetRows(),count+1);ASSERT_EQ(learner->SomaNeuronAmplitude.GetCols(),1);
 std::vector<UEPtr<NPulseMembrane>> somas;
 for(int i=0;i<(branch?1:count);++i)
 {
  auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);somas.push_back(soma);
 }
 auto generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(generator);
 auto read=[&]() {
  QJsonArray physical,cached,dendriteReadout,history;double total=0.;
  for(size_t i=0;i<somas.size();++i)
  {
   const double value=somas[i]->SumPotential(0,0);physical.append(value);total+=value;
   cached.append(learner->SomaNeuronAmplitude(branch?0:int(i)+1,0));
  }
  QJsonObject result;result["physical_somas"]=physical;result["cached_somas"]=cached;
  for(int i=0;i<=count;++i)dendriteReadout.append(learner->DendriteNeuronAmplitude(i,0));
  for(int i=1;i<=count;++i)history.append(learner->SomaNeuronAmplitude(i,0));
  result["dendrite_readout"]=dendriteReadout;result["per_input_soma_readout"]=history;
  result["physical_total"]=total;result["cached_total"]=learner->SomaNeuronAmplitude(0,0);return result;
 };
 const auto initial=read();
 std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time_s,input";
 for(size_t i=0;i<somas.size();++i)trace<<",physical_soma"<<i+1<<",cached_soma"<<i+1;trace<<'\n';
 const unsigned warmTicks=xmlRoundtrip?frequency/10:frequency/20;
 double maximum=0.;std::vector<std::vector<double>> warmRows;
 for(unsigned tick=0;tick<warmTicks;++tick)
 {
  model->Calculate();core.environment->IncreaseModelTimeByStep();trace<<double(tick)/frequency<<','<<generator->Output(0,0);
  std::vector<double> row{generator->Output(0,0)};
  for(size_t i=0;i<somas.size();++i)
  {
   const double value=somas[i]->SumPotential(0,0);ASSERT_TRUE(std::isfinite(value));maximum=std::max(maximum,std::abs(value));
   const double cached=learner->SomaNeuronAmplitude(branch?0:int(i)+1,0);
   EXPECT_DOUBLE_EQ(cached,value);trace<<','<<value<<','<<cached;
   row.push_back(value);row.push_back(cached);
  }
  trace<<'\n';
  warmRows.push_back(row);
 }
 ASSERT_GT(maximum,1e-8);const auto warm=read();
 QJsonObject loadedBeforeReset;
 if(xmlRoundtrip)
 {
  const auto sourceGraph=NmsdkTools::InspectModel(model);ASSERT_TRUE(sourceGraph["valid"].toBool());
  SaveResetArtifact(folder+"source-model.json",QJsonDocument(sourceGraph).toJson().toStdString());
  USerStorageXML xml;ASSERT_TRUE(xml.Create("HotLearnerFixture"));
  ASSERT_TRUE(model->SaveComponent(&xml,true,ptPubParameter|pgSystem|(includeState?ptPubState:0)));
  std::string serialized;ASSERT_TRUE(xml.Save(serialized));SaveResetArtifact(folder+"hot-model.xml",serialized);
  const std::string modelName=model->GetName();
  somas.clear();generator=0;channel=0;synapse=0;neuron=0;learner=0;model=0;core.environment->DestroyModel();
  ASSERT_TRUE(core.environment->CreateModel("NModel"));model=dynamic_pointer_cast<UNet>(core.environment->GetModel());ASSERT_TRUE(model);
  model->SetGlobalTimeStep(frequency);ASSERT_TRUE(xml.SelectNode(modelName));
  TProjectLoadDiagnostics diagnostics;ASSERT_TRUE(model->LoadComponent(&xml,true,&diagnostics));
  std::ostringstream loadErrors;for(const auto& error:diagnostics.errors)loadErrors<<error<<'\n';
  SaveResetArtifact(folder+"load-errors.txt",loadErrors.str());ASSERT_TRUE(diagnostics.errors.empty())<<loadErrors.str();
  core.environment->ModelInit();
  learner=model->template GetComponentL<Learner>("Learner",true);ASSERT_TRUE(learner);
  neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
  channel=neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);ASSERT_TRUE(channel);
  synapse=neuron->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);ASSERT_TRUE(synapse);
  generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(generator);
  ASSERT_EQ(learner->SomaNeuronAmplitude.GetRows(),count+1);ASSERT_EQ(learner->SomaNeuronAmplitude.GetCols(),1);
  ASSERT_EQ(learner->DendriteNeuronAmplitude.GetRows(),count+1);ASSERT_EQ(learner->DendriteNeuronAmplitude.GetCols(),1);
  for(int i=0;i<(branch?1:count);++i)
  {
   auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);somas.push_back(soma);
  }
  loadedBeforeReset=read();
 }
 core.environment->Reset();const auto reset=read();
 QJsonObject observation;observation["kind"]=xmlRoundtrip?"native_hot_xml_reset":"native_hot_learner_reset";observation["schema_version"]=xmlRoundtrip?2:1;
 if(xmlRoundtrip)
 {
  observation["serialized_while_warm"]=true;observation["include_state"]=includeState;
  observation["warm_sample_count"]=int(warmTicks);observation["warm_duration_s"]=double(warmTicks)/frequency;
  observation["loaded_after_native_init_before_explicit_reset"]=loadedBeforeReset;
  const auto graph=NmsdkTools::InspectModel(model);ASSERT_TRUE(graph["valid"].toBool());
  SaveResetArtifact(folder+"loaded-model.json",QJsonDocument(graph).toJson().toStdString());
 }
 observation["topology"]=QString::fromStdString(kind);observation["inputs"]=count;observation["frequency_hz"]=int(frequency);
 observation["initial"]=initial;observation["warm"]=warm;observation["after_reset"]=reset;
 observation["effective_capacity"]=channel->Capacity.GetData();observation["effective_resistance"]=synapse->Resistance.GetData();
 SaveResetArtifact(folder+"observation.json",QJsonDocument(observation).toJson().toStdString());
 SaveResetArtifact(folder+"warm.csv",trace.str());
 for(size_t i=0;i<somas.size();++i)
 {
  const double rest=initial["physical_somas"].toArray()[int(i)].toDouble();
  EXPECT_DOUBLE_EQ(reset["physical_somas"].toArray()[int(i)].toDouble(),rest);
  EXPECT_DOUBLE_EQ(reset["cached_somas"].toArray()[int(i)].toDouble(),rest)<<"stale learner readout before first tick after native Reset";
 }
 EXPECT_DOUBLE_EQ(reset["cached_total"].toDouble(),reset["physical_total"].toDouble());
 EXPECT_EQ(reset["dendrite_readout"],initial["dendrite_readout"]);
 EXPECT_TRUE(learner->NativeModelEditFailure().empty());
 if(branch)for(int i=1;i<=count;++i)EXPECT_DOUBLE_EQ(learner->SomaNeuronAmplitude(i,0),0.0);
 if(xmlRoundtrip)
 {
  std::ostringstream replay;replay.imbue(std::locale::classic());replay<<std::setprecision(17)<<"time_s,warm_input,replay_input";
  for(size_t i=0;i<somas.size();++i)replay<<",warm_soma"<<i+1<<",replay_soma"<<i+1;replay<<'\n';
  for(unsigned tick=0;tick<warmTicks;++tick)
  {
   model->Calculate();core.environment->IncreaseModelTimeByStep();
   const double input=generator->Output(0,0);EXPECT_DOUBLE_EQ(input,warmRows[tick][0]);
   replay<<double(tick)/frequency<<','<<warmRows[tick][0]<<','<<input;
   for(size_t i=0;i<somas.size();++i)
   {
    const double value=somas[i]->SumPotential(0,0);ASSERT_TRUE(std::isfinite(value));
    EXPECT_NEAR(value,warmRows[tick][1+2*i],1e-12);
    EXPECT_DOUBLE_EQ(learner->SomaNeuronAmplitude(branch?0:int(i)+1,0),value);
    replay<<','<<warmRows[tick][1+2*i]<<','<<value;
   }
   replay<<'\n';
  }
  SaveResetArtifact(folder+"replay.csv",replay.str());
 }
 else
 {
  model->Calculate();core.environment->IncreaseModelTimeByStep();
  if(branch)for(int i=1;i<=count;++i)EXPECT_DOUBLE_EQ(learner->SomaNeuronAmplitude(i,0),0.0);
 }
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(),1.23e-9);EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(),91e6);
 EXPECT_EQ(learner->DendriteLength.GetData(),std::vector<int>(count,1));
 EXPECT_EQ(learner->TipSynapseResistance.GetData(),tips);
 core.environment->DestroyModel();
}

class HotReadoutReset : public ::testing::TestWithParam<std::tuple<bool,int,unsigned>> {};
TEST_P(HotReadoutReset, NativeResetPublishesModelRestBeforeFirstTick)
{
 const auto [branch,count,frequency]=GetParam();
 if(branch)WarmReset<NNeuronTimeLearnerBranch>(branch,count,frequency);
 else WarmReset<NNeuronTimeLearner>(branch,count,frequency);
}
INSTANTIATE_TEST_SUITE_P(NativeStorage,HotReadoutReset,
 ::testing::Combine(::testing::Values(false,true),::testing::Values(2,4),::testing::Values(2000u,20000u)));

class HotXmlReadoutReset : public ::testing::TestWithParam<std::tuple<bool,int,unsigned,bool>> {};
TEST_P(HotXmlReadoutReset, NativeLoadOfWarmGraphResetsDynamicsAndReplaysResponse)
{
 const auto [branch,count,frequency,state]=GetParam();
 if(branch)WarmReset<NNeuronTimeLearnerBranch>(branch,count,frequency,true,state);
 else WarmReset<NNeuronTimeLearner>(branch,count,frequency,true,state);
}
INSTANTIATE_TEST_SUITE_P(NativeStorage,HotXmlReadoutReset,
 ::testing::Combine(::testing::Values(false,true),::testing::Values(1,2,4,6),::testing::Values(2000u,20000u),::testing::Values(false,true)));
}
