#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeModelOwner.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelArchive.h"
#include "../Support/ConsoleLikeInit.h"
#include <type_traits>
#include <QFile>
#include <QDir>
#include <QJsonDocument>
#include <QJsonArray>
#include <cstdlib>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
struct Lease {
 UEPtr<UStorage> storage;UEPtr<UContainer> node;
 ~Lease(){if(node){if(auto net=dynamic_pointer_cast<UNet>(node))net->BreakLinks();storage->ReturnObject(node);}}
};
template<class Owner> void PreparedInstall()
{
 const bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 for(unsigned frequency:{2000u,20000u})
 {
  core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
  ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();
  auto source=dynamic_pointer_cast<Owner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
  ASSERT_TRUE(source);source->SetEnvironment(core.environment);source->Name="Source";source->ControllerVersion=1;
  source->CalculateMode=1;source->StructureBuildMode=1;source->EnablePostTrainTuning=false;source->AutoCalibrateFixedLTZThreshold=false;
  UEPtr<UContainer> child=source;ASSERT_NE(model->AddComponent(child),ForbiddenId);model->SetGlobalTimeStep(frequency);
  NativeModelSpec declaration;declaration.branch=branch;declaration.frequencyHz=frequency;
  declaration.neuronClass="NSPNeuronGen";declaration.normalization=Normalization::TipResistance;
  declaration.inputs={{2,1,86e6},{1,1,91e6}};declaration.initialIsi={.01,.08};
  declaration.editPolicy.normalization=Normalization::TipResistance;declaration.editPolicy.maximumCableLength=8;
  declaration.editPolicy.maximumResistanceRatio=200.;
  const auto built=source->ConstructNativeModel(declaration);ASSERT_EQ(built.status,NativeModelBuildStatus::Constructed)<<built.reason;
  source->Init();model->Init();model->Reset();
  auto neuron=source->template GetComponentL<NPulseNeuron>("Neuron",true);
  auto dataset=source->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(neuron);ASSERT_TRUE(dataset);
  auto generator=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
  const auto snapshot=NmsdkTools::ExportPhysicalGraphForEdit(neuron,{{&generator->Output,"burst"}});
  const auto datasetSnapshot=NmsdkTools::ExportDatasetSnapshot(dataset);
  FeedbackStorageProfileSpec recipe;recipe.frequencyHz=frequency;recipe.bodyFeedbackGain=0.;
  recipe.name=std::string("PreparedInstall_")+(branch?"Branch":"Classic")+std::to_string(frequency);
  const auto profile=RegisterFeedbackStorageProfile(core.storage,core.environment,recipe);
  auto actualDeclaration=declaration;actualDeclaration.neuronClass=profile.neuronClass;
  const std::map<std::string,std::string> names{{"NSPNeuronGen",profile.neuronClass},{"NPMembraneBio",profile.bodyMembraneClass}};
  auto cloneData=dynamic_pointer_cast<NDatasetMatrix>(NmsdkTools::ImportDatasetSnapshot(datasetSnapshot,core.storage,core.environment));
  ASSERT_TRUE(cloneData);UEPtr<UContainer> cloneDataNode=cloneData;Lease dataLease{core.storage,cloneDataNode};
  auto cloneGenerator=cloneData->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(cloneGenerator);
  auto clone=NmsdkTools::ImportFeedbackProfileGraphForEdit(snapshot,core.storage,core.environment,names,0.,{{&cloneGenerator->Output,"burst"}});
  Lease cloneLease{core.storage,clone};auto cloneNeuron=dynamic_pointer_cast<NPulseNeuron>(clone);ASSERT_TRUE(cloneNeuron);
  const auto expected=NmsdkTools::IdentifyModel(clone,{{&cloneGenerator->Output,"burst"}});
  const auto rejected=source->InstallNativePreparedModel(actualDeclaration,cloneNeuron,cloneData,built.effective);
  EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(rejected.modelMayHaveChanged);
  EXPECT_EQ(NmsdkTools::IdentifyModel(neuron,{{&generator->Output,"burst"}}),snapshot["identity"].toObject());
  auto fresh=dynamic_pointer_cast<Owner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
  ASSERT_TRUE(fresh);UEPtr<UContainer> freshNode=fresh;Lease freshLease{core.storage,freshNode};
  fresh->SetEnvironment(core.environment);fresh->SetGlobalTimeStep(frequency);fresh->ControllerVersion=2;fresh->CalculateMode=1;fresh->StructureBuildMode=1;
  fresh->EnablePostTrainTuning=false;fresh->AutoCalibrateFixedLTZThreshold=false;
  const auto installed=fresh->InstallNativePreparedModel(actualDeclaration,cloneNeuron,cloneData,built.effective);
  ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
  cloneLease.node=0;dataLease.node=0;
  EXPECT_EQ(NmsdkTools::IdentifyModel(fresh->GetComponent("Neuron",true),{{&cloneGenerator->Output,"burst"}}),expected);
  EXPECT_EQ(fresh->ReadNativeParameters(),built.effective);
  const auto& control=fresh->NativeTrainingController();EXPECT_EQ(control.State(),NativeTrainingState::Idle);
  EXPECT_TRUE(control.ObservedPackets().empty());EXPECT_FALSE(control.References());EXPECT_FALSE(control.Search());EXPECT_FALSE(control.Certificate());
  EXPECT_TRUE(fresh->NativeTrainingRequest().isEmpty());EXPECT_FALSE(fresh->IsNeedToTrain.GetData());
  const auto again=fresh->InstallNativePreparedModel(actualDeclaration,cloneNeuron,cloneData,built.effective);
  EXPECT_EQ(again.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(again.modelMayHaveChanged);
  EXPECT_EQ(fresh->ReadNativeParameters(),built.effective);
  EXPECT_EQ(NmsdkTools::IdentifyModel(fresh->GetComponent("Neuron",true),{{&cloneGenerator->Output,"burst"}}),expected);
  if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
  {
   QJsonObject renames;for(const auto& entry:names)renames[QString::fromStdString(entry.first)]=QString::fromStdString(entry.second);
   const auto after=NmsdkTools::IdentifyModel(fresh->GetComponent("Neuron",true),{{&cloneGenerator->Output,"burst"}});
   QJsonArray parameters;for(const auto& p:fresh->ReadNativeParameters())parameters.append(QJsonObject{{"length",p.length},{"synapses",p.synapses},{"resistance",p.resistance}});
   const auto record=QJsonObject{{"kind","native_prepared_model_fixture"},{"schema_version",1},
    {"source_identity",snapshot["identity"]},{"source_after",NmsdkTools::IdentifyModel(neuron,{{&generator->Output,"burst"}})},
    {"candidate_identity",after},{"preview_identity",expected},{"class_renames",renames},{"parameters",parameters},
    {"control_idle",control.State()==NativeTrainingState::Idle},{"observed_packet_count",int(control.ObservedPackets().size())},
    {"references_present",bool(control.References())},{"search_present",bool(control.Search())},{"certificate_present",bool(control.Certificate())},
    {"request",fresh->NativeTrainingRequest()},{"need_to_train",fresh->IsNeedToTrain.GetData()},
    {"source_refused",rejected.status==NativeModelBuildStatus::Rejected},{"repeat_refused",again.status==NativeModelBuildStatus::Rejected},
    {"candidate_waveform_evaluated",false}};
   QFile file(QString::fromLocal8Bit(output)+QString("/prepared-model-%1-%2.json").arg(branch?"Branch":"Classic").arg(frequency));
   ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto bytes=QJsonDocument(record).toJson();ASSERT_EQ(file.write(bytes),bytes.size());
  }
 }
 core.environment->DestroyModel();
}
TEST(PreparedNativeModel,ClassicFreshOwnerAndRepeatedRefusal){PreparedInstall<NNeuronTimeLearner>();}
TEST(PreparedNativeModel,BranchFreshOwnerAndRepeatedRefusal){PreparedInstall<NNeuronTimeLearnerBranch>();}
}
