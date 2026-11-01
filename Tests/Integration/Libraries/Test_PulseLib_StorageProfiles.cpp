#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "TimeLearner/ModelInspection.h"
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

void Artifact(const std::string& name, const std::string& content)
{
 const char* directory = std::getenv("TIMELEARNER_PROFILE_TEST_DIR");
 if(!directory) return;
 const auto path = std::filesystem::path(directory) / name;
 std::filesystem::create_directories(path.parent_path());
 std::ofstream file(path, std::ios::binary); file << content;
 ASSERT_TRUE(file.good()) << path.string();
}

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
 Artifact(specification.name + ".json", QJsonDocument(NmsdkTools::InspectModel(restored)).toJson().toStdString());
 std::string serialized; ASSERT_TRUE(xml.Save(serialized));
 Artifact(specification.name + ".xml", serialized);
 core.storage->ReturnObject(restored); core.storage->ReturnObject(neuron);
}

class ProfileWaveform : public ::testing::TestWithParam<unsigned int> {};

TEST_P(ProfileWaveform, DeclaredBaselineMatchesLegacyPhysicalResponse)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 const unsigned int frequency = GetParam();
 StorageProfileSpec specification;
 specification.name = "TLProfileUnit_Wave_" + std::to_string(frequency);
 specification.frequencyHz = frequency;
 const auto profile = RegisterStorageProfile(core.storage, core.environment, specification);
 auto source = Take<NPulseNeuron>(specification.neuronBaseClass);
 auto target = Take<NPulseNeuron>(profile.neuronClass);
 ASSERT_TRUE(source); ASSERT_TRUE(target);
 core.environment->CreateModel("NModel");
 auto model = core.environment->GetModel(); ASSERT_TRUE(model);
 source->Name = "Legacy"; target->Name = "Profile";
 for(auto neuron : {source, target})
 {
  neuron->NumSomaMembraneParts = 2;
  neuron->StructureBuildMode = 2;
  neuron->NumDendriteMembranePartsVec = std::vector<int>{1, 2};
  neuron->Build();
  ASSERT_NE(model->AddComponent(neuron), ForbiddenId);
 }
 model->SetGlobalTimeStep(frequency);
 core.environment->ModelInit(); model->Reset();
 auto a = source->GetComponentL<NPulseSynapse>("Dendrite2_2.ExcSynapse1", true);
 auto b = target->GetComponentL<NPulseSynapse>("Dendrite2_2.ExcSynapse1", true);
 auto outputA = source->GetComponentL<NPulseChannel>("Soma2.ExcChannel", true);
 auto outputB = target->GetComponentL<NPulseChannel>("Soma2.ExcChannel", true);
 ASSERT_TRUE(a); ASSERT_TRUE(b); ASSERT_TRUE(outputA); ASSERT_TRUE(outputB);
 ASSERT_FALSE(a->Input.IsConnected()); ASSERT_FALSE(b->Input.IsConnected());
 double maxError = 0.; std::vector<double> response;
 std::ostringstream trace; trace.imbue(std::locale::classic());
 trace << std::setprecision(17) << "tick,tick_start_s,stimulus,legacy_soma2_exc,profile_soma2_exc\n";
 for(unsigned int tick = 0; tick < frequency / 10; ++tick)
 {
  const double time = double(tick) / frequency;
  const double stimulus = time >= .005 && time < .006 ? 1. : 0.;
  a->Input.Assign(1, 1, stimulus); b->Input.Assign(1, 1, stimulus);
  model->Calculate(); core.environment->IncreaseModelTimeByStep();
  const double x = outputA->Output(0,0), y = outputB->Output(0,0);
  ASSERT_TRUE(std::isfinite(x)); ASSERT_TRUE(std::isfinite(y));
  maxError = std::max(maxError, std::abs(x-y)); response.push_back(x);
  trace << tick << ',' << time << ',' << stimulus << ',' << x << ',' << y << '\n';
 }
 const auto range = std::minmax_element(response.begin(), response.end());
 EXPECT_GT(*range.second - *range.first, 1e-8);
 EXPECT_LE(maxError, 1e-12);
 Frequency(source, frequency); Frequency(target, frequency);
 ValidGraph(source); ValidGraph(target);
 Artifact(specification.name + ".csv", trace.str());
 model->DelComponent("Profile", false); model->DelComponent("Legacy", false);
 core.storage->ReturnObject(target); core.storage->ReturnObject(source);
}

INSTANTIATE_TEST_SUITE_P(SingleRateBaseline, ProfileWaveform, ::testing::Values(2000u, 20000u));

TEST(TimeLearnerStorageProfiles, ScalarStructureModeOneSurvivesGrowthAndXml)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 StorageProfileSpec specification; specification.name = "TLProfileUnit_ScalarMode";
 const auto profile = RegisterStorageProfile(core.storage, core.environment, specification);
 auto source = Take<NPulseNeuron>(profile.neuronClass); ASSERT_TRUE(source);
 source->StructureBuildMode = 1;
 source->NumSomaMembraneParts = 2;
 source->NumDendriteMembraneParts = 3;
 source->Build(); source->Init();
 ASSERT_TRUE(source->GetComponent("Dendrite2_3", true));
 USerStorageXML xml; ASSERT_TRUE(xml.Create("ScalarGrowth"));
 ASSERT_TRUE(source->SaveComponent(&xml, true, ptPubParameter | ptPubState | pgSystem));
 ASSERT_TRUE(xml.SelectNode(source->GetName()));
 auto restored = Take<NPulseNeuron>(profile.neuronClass); ASSERT_TRUE(restored);
 ASSERT_TRUE(restored->LoadComponent(&xml, true)); restored->Init();
 EXPECT_EQ(restored->StructureBuildMode.GetData(), 1);
 EXPECT_EQ(restored->NumSomaMembraneParts.GetData(), 2);
 EXPECT_EQ(restored->NumDendriteMembraneParts.GetData(), 3);
 EXPECT_TRUE(restored->GetComponent("Dendrite2_3", true));
 restored->NumSomaMembraneParts = 3;
 restored->Build(); restored->Init();
 EXPECT_TRUE(restored->GetComponent("Dendrite3_3", true));
 EXPECT_EQ(restored->NumDendriteMembraneParts.GetData(), 3);
 ValidGraph(restored);
 Artifact(specification.name + ".json", QJsonDocument(NmsdkTools::InspectModel(restored)).toJson().toStdString());
 core.storage->ReturnObject(restored); core.storage->ReturnObject(source);
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
