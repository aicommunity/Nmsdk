#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseGenerator.h"
#include "TimeLearner/ModelInspection.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <locale>
#include <sstream>
#include <tuple>

namespace {
using namespace RDK;
using namespace NMSDK;

void ReadoutArtifact(const std::string& name,const std::string& contents)
{
 const char* directory=std::getenv("TL_LOADED_READOUT_DIR");if(!directory)return;
 const auto path=std::filesystem::path(directory)/name;
 std::filesystem::create_directories(path.parent_path());
 std::ofstream file(path,std::ios::binary);file<<contents;ASSERT_TRUE(file.good());
}

class LoadedLearnerReadout : public ::testing::TestWithParam<std::tuple<bool,int,unsigned,bool>> {};

template<class Learner> void LoadedReadout(const bool branch,const int count,const unsigned frequency,const bool savedState)
{
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 const std::string kind=branch?"Branch":"Classic";
 const std::string artifact=kind+"-N"+std::to_string(count)+"-f"+std::to_string(frequency)+"-state"+(savedState?"1/":"0/");
 const std::string className=branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner";
 core.environment->DestroyModel();ASSERT_TRUE(core.environment->CreateModel("NModel"));
 auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());ASSERT_TRUE(model);model->SetGlobalTimeStep(frequency);
 auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(className));ASSERT_TRUE(learner);
 learner->Name="Learner";learner->ControllerVersion=1;learner->StructureBuildMode=1;
 learner->NormalizationMode=0;learner->NumInputDendrite=count;
 learner->DendriteLength=std::vector<int>(count,1);learner->NumSynapse=std::vector<int>(count,1);
 learner->InitialSomaPotential=std::vector<double>(count,.015);
 learner->TipSynapseResistance=std::vector<double>(count,86e6);
 learner->CalculateMode=1;learner->IsNeedToTrain=true;learner->EnablePostTrainTuning=false;
 learner->SyncCapacitanceTrim=0;learner->FixedLTZThreshold=1.;learner->LTZThreshold=1.;
 MDMatrix<double> pattern;pattern.Assign(count,1,.01);learner->InputPattern=pattern;
 // Populate the native training dataset during construction, then freeze before
 // any Calculate. Need=false intentionally preserves an existing Test dataset.
 ASSERT_NE(model->AddComponent(learner),ForbiddenId);core.environment->ModelInit();learner->IsNeedToTrain=false;
 auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
 // A saved full graph owns these deliberately nonuniform child values.
 learner->StructureBuildMode=0;neuron->StructureBuildMode=0;neuron->UseElementDefaults=false;
 auto channel=neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);ASSERT_TRUE(channel);
 channel->Capacity=1.23e-9;
 auto synapse=neuron->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);ASSERT_TRUE(synapse);
 synapse->Resistance=91e6;
 std::vector<double> tips(count,86e6);tips[0]=91e6;learner->TipSynapseResistance=tips;
 model->Build();core.environment->Reset();
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(),1.23e-9);EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(),91e6);
 const auto before=NmsdkTools::InspectModel(neuron);
 ReadoutArtifact(artifact+"source-neuron.json",QJsonDocument(before).toJson().toStdString());
 const auto sourceGraph=NmsdkTools::InspectModel(model);
 ReadoutArtifact(artifact+"source-model.json",QJsonDocument(sourceGraph).toJson().toStdString());
 ASSERT_TRUE(sourceGraph["valid"].toBool())<<QJsonDocument(sourceGraph["diagnostics"].toArray()).toJson().constData();
 USerStorageXML xml;ASSERT_TRUE(xml.Create("LoadedReadoutFixture"));
 ASSERT_TRUE(model->SaveComponent(&xml,true,ptPubParameter|pgSystem|(savedState?ptPubState:0)));
 std::string serialized;ASSERT_TRUE(xml.Save(serialized));ReadoutArtifact(artifact+"model.xml",serialized);
 const std::string modelName=model->GetName();
 const auto capture=[&](auto owner,auto tree,std::vector<std::vector<double>>& rows) {
  auto generator=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
  ASSERT_TRUE(generator);
  for(unsigned tick=0;tick<frequency/10;++tick)
  {
   tree->Calculate();core.environment->IncreaseModelTimeByStep();
   std::vector<double> row{generator->Output(0,0)};
   for(int i=0;i<(branch?1:count);++i)
   {
    auto soma=owner->template GetComponentL<NPulseMembrane>("Neuron.Soma"+std::to_string(i+1),true);
    ASSERT_TRUE(soma);const double value=soma->SumPotential(0,0);ASSERT_TRUE(std::isfinite(value));
    row.push_back(value);
    ASSERT_DOUBLE_EQ(owner->SomaNeuronAmplitude(branch?0:i+1,0),value);
   }
   rows.push_back(row);
  }
 };
 ASSERT_EQ(learner->SomaNeuronAmplitude.GetRows(),count+1);
 std::vector<std::vector<double>> original;capture(learner,model,original);ASSERT_FALSE(::testing::Test::HasFatalFailure());
 // Exercise native XML construction, not an overlay onto a pre-built learner.
 neuron=0;channel=0;synapse=0;learner=0;model=0;core.environment->DestroyModel();
 ASSERT_TRUE(core.environment->CreateModel("NModel"));model=dynamic_pointer_cast<UNet>(core.environment->GetModel());ASSERT_TRUE(model);
 model->SetGlobalTimeStep(frequency);ASSERT_TRUE(xml.SelectNode(modelName));
 TProjectLoadDiagnostics diagnostics;ASSERT_TRUE(model->LoadComponent(&xml,true,&diagnostics));
 std::ostringstream errors;for(const auto& error:diagnostics.errors)errors<<error<<'\n';
 ReadoutArtifact(artifact+"load-errors.txt",errors.str());ASSERT_TRUE(diagnostics.errors.empty())<<errors.str();
 core.environment->ModelInit();core.environment->Reset();
 learner=model->template GetComponentL<Learner>("Learner",true);ASSERT_TRUE(learner);
 neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
 const auto after=NmsdkTools::InspectModel(neuron);
 ReadoutArtifact(artifact+"loaded-neuron.json",QJsonDocument(after).toJson().toStdString());
 const auto loadedGraph=NmsdkTools::InspectModel(model);
 ReadoutArtifact(artifact+"loaded-model.json",QJsonDocument(loadedGraph).toJson().toStdString());
 ASSERT_TRUE(loadedGraph["valid"].toBool())<<QJsonDocument(loadedGraph["diagnostics"].toArray()).toJson().constData();
 std::ostringstream dimensions;dimensions<<"{\"inputs\":"<<count<<",\"soma_rows\":"
  <<learner->SomaNeuronAmplitude.GetRows()<<",\"dendrite_rows\":"<<learner->DendriteNeuronAmplitude.GetRows()<<"}\n";
 ReadoutArtifact(artifact+"loaded-dimensions.json",dimensions.str());
 ASSERT_EQ(learner->SomaNeuronAmplitude.GetRows(),count+1);
 ASSERT_EQ(learner->SomaNeuronAmplitude.GetCols(),1);
 ASSERT_EQ(learner->DendriteNeuronAmplitude.GetRows(),count+1);
 ASSERT_EQ(learner->DendriteNeuronAmplitude.GetCols(),1);
 EXPECT_EQ(before["links"],after["links"]);EXPECT_EQ(before["nodes"].toArray().size(),after["nodes"].toArray().size());
 channel=neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);
 synapse=neuron->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);ASSERT_TRUE(channel);ASSERT_TRUE(synapse);
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(),1.23e-9);EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(),91e6);
 // A Ready component's Build is a native no-op, not a forced reconstruction.
 auto* identity=neuron.Get();const auto readyLifecycle=learner->ObserveLifecycle();
 learner->Build();EXPECT_TRUE(readyLifecycle.IsCurrent());core.environment->Reset();
 EXPECT_EQ(learner->template GetComponentL<NPulseNeuron>("Neuron",true).Get(),identity);
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(),1.23e-9);EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(),91e6);
 std::vector<std::vector<double>> restored;capture(learner,model,restored);ASSERT_FALSE(::testing::Test::HasFatalFailure());
 ASSERT_EQ(original.size(),restored.size());
 std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time_s,source_input,loaded_input";
 for(int i=0;i<(branch?1:count);++i)trace<<",source_soma"<<i+1<<",loaded_soma"<<i+1;trace<<'\n';
 double maximum=0;int pulses=0;
 for(size_t tick=0;tick<original.size();++tick)
 {
  ASSERT_EQ(original[tick].size(),restored[tick].size());
  trace<<double(tick)/frequency<<','<<original[tick][0]<<','<<restored[tick][0];
  EXPECT_DOUBLE_EQ(original[tick][0],restored[tick][0]);
  if(restored[tick][0]>0 && (tick==0 || restored[tick-1][0]==0))++pulses;
  for(size_t i=1;i<original[tick].size();++i)
  {EXPECT_NEAR(original[tick][i],restored[tick][i],1e-12);maximum=std::max(maximum,std::abs(restored[tick][i]));trace<<','<<original[tick][i]<<','<<restored[tick][i];}
  trace<<'\n';
 }
 EXPECT_EQ(pulses,count);EXPECT_GT(maximum,1e-8);
 ReadoutArtifact(artifact+"roundtrip.csv",trace.str());
 // A corrupted output state must be diagnosed before children, without a
 // per-tick resize. A no-op Build must retain the diagnostic under Rdk rules.
 learner->SomaNeuronAmplitude.Assign(1,2,0.0);ASSERT_TRUE(learner->IsReady());
 model->Calculate();
 EXPECT_EQ(learner->NativeModelEditFailure(),"legacy_readout_shape_requires_build");
 EXPECT_EQ(learner->SomaNeuronAmplitude.GetRows(),1);EXPECT_EQ(learner->SomaNeuronAmplitude.GetCols(),2);
 const auto failedLifecycle=learner->ObserveLifecycle();learner->Build();
 EXPECT_TRUE(failedLifecycle.IsCurrent());
 EXPECT_EQ(learner->NativeModelEditFailure(),"legacy_readout_shape_requires_build");
 EXPECT_EQ(learner->SomaNeuronAmplitude.GetRows(),1);EXPECT_EQ(learner->SomaNeuronAmplitude.GetCols(),2);
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(),1.23e-9);EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(),91e6);
 core.environment->DestroyModel();
}

TEST_P(LoadedLearnerReadout, NativeModeZeroXmlRestoresBuffersGraphAndResponse)
{
 const auto [branch,count,frequency,savedState]=GetParam();
 if(branch)LoadedReadout<NNeuronTimeLearnerBranch>(branch,count,frequency,savedState);
 else LoadedReadout<NNeuronTimeLearner>(branch,count,frequency,savedState);
}
INSTANTIATE_TEST_SUITE_P(NativeStorage,LoadedLearnerReadout,
 ::testing::Combine(::testing::Values(false,true),::testing::Values(1,2,4,6),::testing::Values(2000u,20000u),::testing::Values(false,true)));
}
