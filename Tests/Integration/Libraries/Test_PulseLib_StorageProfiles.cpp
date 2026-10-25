#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../App/NeuroModelerConsole/ModelInspection.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <locale>
#include <sstream>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;

template<class T> UEPtr<T> Take(const std::string& name)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto value = dynamic_pointer_cast<T>(core.storage->TakeObject(name));
 if(value) value->SetEnvironment(core.environment);
 return value;
}

void Frequency(UEPtr<UContainer> node, unsigned int expected)
{
 EXPECT_EQ(node->GetTimeStep(), expected) << node->GetFullName();
 std::vector<NameT> children;
 node->GetComponentsList(children);
 for(const auto& name : children) Frequency(node->GetComponent(name, true), expected);
}

void ValidGraph(UEPtr<UContainer> model)
{
 const auto report = NmsdkTools::InspectModel(model);
 EXPECT_TRUE(report["valid"].toBool()) << QJsonDocument(report["diagnostics"].toArray()).toJson().constData();
}

TEST(TimeLearnerStorageProfiles, EmptyRoleOverridesPreserveLegacyClassSelection)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto membrane = Take<NPulseMembrane>("NPMembraneBio");
 ASSERT_TRUE(membrane);
 EXPECT_TRUE(membrane->ExcSynapseClassName->empty());
 EXPECT_TRUE(membrane->InhSynapseClassName->empty());
 membrane->Init();
 membrane->NumExcitatorySynapses = 3;
 membrane->NumInhibitorySynapses = 2;
 membrane->Build();
 EXPECT_EQ(membrane->GetEffectiveExcSynapseClassName(), membrane->SynapseClassName.GetData());
 EXPECT_EQ(membrane->GetEffectiveInhSynapseClassName(), membrane->SynapseClassName.GetData());
 EXPECT_EQ(membrane->GetNumExcitatorySynapses(), 3u);
 EXPECT_EQ(membrane->GetNumInhibitorySynapses(), 2u);
 for(const auto& name : {"ExcSynapse1", "ExcSynapse3", "InhSynapse2"})
 {
  auto synapse = membrane->GetComponentL<NPulseSynapse>(name, true);
  ASSERT_TRUE(synapse);
  EXPECT_EQ(synapse->GetCompClassName(), membrane->SynapseClassName.GetData());
  EXPECT_TRUE(synapse->IsInit());
 }
 ValidGraph(membrane);
 core.storage->ReturnObject(membrane);
}

TEST(TimeLearnerStorageProfiles, RoleReplacementInitializesNewChildrenAndPreservesOtherRole)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 StorageProfileSpec first; first.name = "TLProfileUnit_RolesA";
 auto a = RegisterStorageProfile(core.storage, core.environment, first);
 StorageProfileSpec second = first; second.name = "TLProfileUnit_RolesB";
 second.body.excSynapse.resistance = 43e6;
 second.body.excChannel.capacity = 1.45e-9;
 auto b = RegisterStorageProfile(core.storage, core.environment, second);
 auto membrane = Take<NPulseMembrane>(a.bodyMembraneClass);
 ASSERT_TRUE(membrane);
 membrane->Init();
 auto inherited = membrane->GetComponentL<NPulseSynapse>("InhSynapse1", true);
 ASSERT_TRUE(inherited);
 inherited->Resistance = 777e6;
 membrane->NumExcitatorySynapses = 3;
 membrane->NumInhibitorySynapses = 2;
 membrane->ExcSynapseClassName = second.name + "_Body_ExcSynapse";
 membrane->ExcChannelClassName = second.name + "_Body_ExcChannel";
 membrane->Build();
 for(const auto& name : {"ExcSynapse1", "ExcSynapse2", "ExcSynapse3"})
 {
  auto synapse = membrane->GetComponentL<NPulseSynapse>(name, true);
  ASSERT_TRUE(synapse);
  EXPECT_TRUE(synapse->IsInit());
  EXPECT_EQ(synapse->GetCompClassName(), second.name + "_Body_ExcSynapse");
  EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(), 43e6);
 }
 auto channel = membrane->GetComponentL<NPulseChannel>("ExcChannel", true);
 ASSERT_TRUE(channel);
 EXPECT_TRUE(channel->IsInit());
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(), 1.45e-9);
 EXPECT_DOUBLE_EQ(inherited->Resistance.GetData(), 777e6);
 auto addedInh = membrane->GetComponentL<NPulseSynapse>("InhSynapse2", true);
 ASSERT_TRUE(addedInh);
 EXPECT_TRUE(addedInh->IsInit());
 EXPECT_EQ(addedInh->GetCompClassName(), first.name + "_Body_InhSynapse");
 EXPECT_DOUBLE_EQ(addedInh->Resistance.GetData(), first.body.inhSynapse.resistance);
 ValidGraph(membrane);
 core.storage->ReturnObject(membrane);
}

class ProfileGrowth : public ::testing::TestWithParam<std::tuple<unsigned int, bool>> {};

TEST_P(ProfileGrowth, NativeGrowthAndXmlPreserveLearnedValuesAndSeparateLtPhysics)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 const auto frequency = std::get<0>(GetParam());
 const bool lt = std::get<1>(GetParam());
 StorageProfileSpec specification;
 specification.name = "TLProfileUnit_Growth_" + std::to_string(frequency) + (lt ? "_LT" : "_Solo");
 specification.frequencyHz = frequency;
 specification.body.excChannel.capacity = .8e-9;
 specification.body.inhChannel.capacity = 1.2e-9;
 specification.body.excSynapse.usePresynapticInhibition = true;
 specification.body.excSynapse.inhibitionCoefficient = 2.5;
 if(lt)
 {
  specification.ltMembrane = specification.body;
  specification.ltMembrane->excChannel.capacity = .3e-9;
  specification.ltMembrane->inhChannel.capacity = .4e-9;
 }
 const auto profile = RegisterStorageProfile(core.storage, core.environment, specification);
 const auto repeat = RegisterStorageProfile(core.storage, core.environment, specification);
 EXPECT_EQ(profile.classNames, repeat.classNames);
 auto neuron = Take<NPulseNeuron>(profile.neuronClass);
 ASSERT_TRUE(neuron);
 EXPECT_FALSE(neuron->UseElementDefaults.GetData());
 EXPECT_DOUBLE_EQ(neuron->MembraneCapacity.GetData(), 0.);
 neuron->SetGlobalTimeStep(frequency);
 neuron->NumSomaMembraneParts = 2;
 neuron->StructureBuildMode = 2;
 neuron->NumDendriteMembranePartsVec = std::vector<int>{1, 2};
 neuron->Build(); neuron->Init();
 auto tip = neuron->GetComponentL<NPulseMembrane>("Dendrite2_2", true);
 ASSERT_TRUE(tip);
 tip->NumExcitatorySynapses = 3; tip->NumInhibitorySynapses = 2;
 tip->Build();
 auto oldSynapse = tip->GetComponentL<NPulseSynapse>("ExcSynapse1", true);
 auto oldExc = tip->GetComponentL<NPulseChannel>("ExcChannel", true);
 auto oldInh = tip->GetComponentL<NPulseChannel>("InhChannel", true);
 ASSERT_TRUE(oldSynapse); ASSERT_TRUE(oldExc); ASSERT_TRUE(oldInh);
 oldSynapse->Resistance = 333e6;
 oldExc->Capacity = 1.41e-9; oldInh->Capacity = 1.59e-9;
 for(const auto& lengths : {std::vector<int>{2,3}, std::vector<int>{2,4}, std::vector<int>{2,3}})
 {
  neuron->NumDendriteMembranePartsVec = lengths;
  neuron->Build();
  EXPECT_DOUBLE_EQ(oldSynapse->Resistance.GetData(), 333e6);
  EXPECT_DOUBLE_EQ(oldExc->Capacity.GetData(), 1.41e-9);
  EXPECT_DOUBLE_EQ(oldInh->Capacity.GetData(), 1.59e-9);
  EXPECT_EQ(tip->GetNumExcitatorySynapses(), 3u);
  EXPECT_EQ(tip->GetNumInhibitorySynapses(), 2u);
  auto added = neuron->GetComponentL<NPulseMembrane>("Dendrite2_3", true);
  ASSERT_TRUE(added);
  auto addedExc = added->GetComponentL<NPulseChannel>("ExcChannel", true);
  auto addedSynapse = added->GetComponentL<NPulseSynapse>("ExcSynapse1", true);
  ASSERT_TRUE(addedExc); ASSERT_TRUE(addedSynapse);
  EXPECT_TRUE(added->IsInit()); EXPECT_TRUE(addedExc->IsInit()); EXPECT_TRUE(addedSynapse->IsInit());
  EXPECT_EQ(addedExc->GetCompClassName(), specification.name + "_Body_ExcChannel");
  EXPECT_DOUBLE_EQ(addedExc->Capacity.GetData(), .8e-9);
  EXPECT_DOUBLE_EQ(addedSynapse->Resistance.GetData(), specification.body.excSynapse.resistance);
  EXPECT_TRUE(addedSynapse->UsePresynapticInhibition.GetData());
  EXPECT_DOUBLE_EQ(addedSynapse->InhibitionCoeff.GetData(), 2.5);
  auto addedInh = tip->GetComponentL<NPulseSynapse>("InhSynapse2", true);
  ASSERT_TRUE(addedInh);
  EXPECT_DOUBLE_EQ(addedInh->Resistance.GetData(), specification.body.inhSynapse.resistance);
  Frequency(neuron, frequency);
  ValidGraph(neuron);
 }
 if(lt)
 {
  auto channel = neuron->GetComponentL<NPulseChannel>("LTMembrane.ExcChannel", true);
  ASSERT_TRUE(channel);
  EXPECT_DOUBLE_EQ(channel->Capacity.GetData(), .3e-9);
 }
 USerStorageXML xml; ASSERT_TRUE(xml.Create("ProfileGrowth"));
 ASSERT_TRUE(neuron->SaveComponent(&xml, true, ptPubParameter | ptPubState | pgSystem));
 ASSERT_TRUE(xml.SelectNode(neuron->GetName()));
 auto restored = Take<NPulseNeuron>(profile.neuronClass);
 ASSERT_TRUE(restored);
 ASSERT_TRUE(restored->LoadComponent(&xml, true)); restored->Init();
 auto restoredTip = restored->GetComponentL<NPulseMembrane>("Dendrite2_2", true);
 ASSERT_TRUE(restoredTip);
 EXPECT_EQ(restoredTip->ExcSynapseClassName.GetData(), specification.name + "_Body_ExcSynapse");
 EXPECT_EQ(restoredTip->InhSynapseClassName.GetData(), specification.name + "_Body_InhSynapse");
 auto restoredSynapse = restoredTip->GetComponentL<NPulseSynapse>("ExcSynapse1", true);
 auto restoredChannel = restoredTip->GetComponentL<NPulseChannel>("ExcChannel", true);
 ASSERT_TRUE(restoredSynapse); ASSERT_TRUE(restoredChannel);
 EXPECT_DOUBLE_EQ(restoredSynapse->Resistance.GetData(), 333e6);
 EXPECT_DOUBLE_EQ(restoredChannel->Capacity.GetData(), 1.41e-9);
 EXPECT_EQ(restoredTip->GetNumExcitatorySynapses(), 3u);
 Frequency(restored, frequency); ValidGraph(restored);
 core.storage->ReturnObject(restored); core.storage->ReturnObject(neuron);
}

INSTANTIATE_TEST_SUITE_P(SingleRateBodyAndLt, ProfileGrowth,
 ::testing::Values(std::make_tuple(2000u, false), std::make_tuple(20000u, false),
                   std::make_tuple(2000u, true), std::make_tuple(20000u, true)));

TEST(TimeLearnerStorageProfiles, InvalidRecipesAndCollisionsDoNotChangeExistingPhysics)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 StorageProfileSpec invalid; invalid.name = "TLProfileUnit_Invalid";
 invalid.body.excChannel.baseClass = "NPInhChannelBio";
 const auto count = core.storage->GetNumClasses();
 EXPECT_THROW(RegisterStorageProfile(core.storage, core.environment, invalid), ClassImageError);
 EXPECT_EQ(core.storage->GetNumClasses(), count);
 EXPECT_FALSE(core.storage->CheckClass(invalid.name + "_Body_ExcChannel"));
 invalid.body.excChannel.baseClass = "NPExcChannelBio";
 invalid.body.excChannel.capacity = std::numeric_limits<double>::quiet_NaN();
 EXPECT_THROW(RegisterStorageProfile(core.storage, core.environment, invalid), ClassImageError);
 EXPECT_EQ(core.storage->GetNumClasses(), count);
 StorageProfileSpec specification; specification.name = "TLProfileUnit_Collision";
 const auto profile = RegisterStorageProfile(core.storage, core.environment, specification);
 auto live = Take<NPulseNeuron>(profile.neuronClass); ASSERT_TRUE(live); live->Init();
 specification.body.excChannel.capacity *= 2.;
 EXPECT_THROW(RegisterStorageProfile(core.storage, core.environment, specification), ClassImageError);
 auto channel = live->GetComponentL<NPulseChannel>("Soma1.ExcChannel", true);
 ASSERT_TRUE(channel); EXPECT_DOUBLE_EQ(channel->Capacity.GetData(), 1e-9);
 auto legacy = Take<NPulseNeuron>("NSPNeuronGenAsymRmD001C1e9"); ASSERT_TRUE(legacy); legacy->Init();
 auto legacyChannel = legacy->GetComponentL<NPulseChannel>("Soma1.ExcChannel", true);
 ASSERT_TRUE(legacyChannel); EXPECT_DOUBLE_EQ(legacyChannel->Capacity.GetData(), 1e-9);
 core.storage->ReturnObject(legacy); core.storage->ReturnObject(live);
}
}
