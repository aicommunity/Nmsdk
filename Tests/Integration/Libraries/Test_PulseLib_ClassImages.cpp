#include <gtest/gtest.h>
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../App/NeuroModelerConsole/ModelInspection.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <limits>

namespace {
using namespace RDK;
using namespace NMSDK;

UEPtr<NPulseChannel> Channel(double capacity)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto channel = dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject("NPExcChannelBio"));
 if(channel)
 {
  channel->SetEnvironment(core.environment);
  channel->SetGlobalTimeStep(2000);
  channel->Capacity = capacity;
  channel->Init();
 }
 return channel;
}

TEST(TimeLearnerClassImages, OwnsSeparateImageAndAllowsEquivalentAliasRegistration)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto source = Channel(1.23e-9);
 ASSERT_TRUE(source);
 const std::string name = "TimeLearnerUnit_ImageChannel";
 const auto result = RegisterClassImage(core.storage, name, source);
 EXPECT_TRUE(result.created);
 const auto originalClass = source->GetClass();
 source->Capacity = 9e-9;
 core.storage->ReturnObject(source);
 auto instance = dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject(name));
 ASSERT_TRUE(instance);
 instance->SetEnvironment(core.environment);
 instance->Init();
 EXPECT_NE(instance->GetClass(), originalClass);
 EXPECT_DOUBLE_EQ(instance->Capacity.GetData(), 1.23e-9);
 EXPECT_EQ(DescribeClassImage(instance), result.descriptor);
 const auto repeat = RegisterClassImage(core.storage, name, instance);
 EXPECT_FALSE(repeat.created);
 EXPECT_EQ(repeat.descriptor, result.descriptor);
 core.storage->ReturnObject(instance);
}

TEST(TimeLearnerClassImages, CollisionCannotChangeAlreadyCreatedInstances)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto first = Channel(1e-9);
 auto other = Channel(2e-9);
 ASSERT_TRUE(first); ASSERT_TRUE(other);
 const std::string name = "TimeLearnerUnit_CollisionChannel";
 RegisterClassImage(core.storage, name, first);
 auto instance = dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject(name));
 ASSERT_TRUE(instance);
 try { RegisterClassImage(core.storage, name, other); FAIL() << "collision accepted"; }
 catch(const ClassImageError& error) { EXPECT_EQ(error.code, "image_name_collision"); }
 EXPECT_DOUBLE_EQ(instance->Capacity.GetData(), 1e-9);
 core.storage->ReturnObject(instance);
 core.storage->ReturnObject(other); core.storage->ReturnObject(first);
}

TEST(TimeLearnerClassImages, EnvironmentAssignmentRemovesPreviousTimeStepVisibility)
{
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 core.environment->SetUseIndTimeStepFlag(false);
 auto source=Channel(1.17e-9);ASSERT_TRUE(source);
 source->ChangeUseIndTimeStepMode(true); // Simulate an object returned by an individual-rate channel.
 ASSERT_NE(source->FindProperty("TimeStep")->GetType() & pgPublic,0u);
 source->SetEnvironment(core.environment);
 EXPECT_EQ(source->FindProperty("TimeStep")->GetType() & pgPublic,0u);
 EXPECT_EQ(source->GetTimeStep(),2000);
 const std::string name="TimeLearnerUnit_EnvironmentModeImage";
 const auto image=RegisterClassImage(core.storage,name,source);
 auto copy=dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject(name));ASSERT_TRUE(copy);
 copy->SetEnvironment(core.environment);copy->Init();
 EXPECT_EQ(DescribeClassImage(copy),image.descriptor);
 EXPECT_DOUBLE_EQ(copy->Capacity.GetData(),1.17e-9);
 core.storage->ReturnObject(copy);core.storage->ReturnObject(source);
}

TEST(TimeLearnerClassImages, EquivalentPhysicsRemainsIdempotentAcrossTimeStepVisibilityModes)
{
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 core.environment->SetUseIndTimeStepFlag(true);
 auto source=Channel(1.19e-9);ASSERT_TRUE(source);
 const std::string name="TimeLearnerUnit_ModeIndependentImage";
 const auto first=RegisterClassImage(core.storage,name,source);EXPECT_TRUE(first.created);
 for(bool individual:{false,true,false})
 {
  core.environment->SetUseIndTimeStepFlag(individual);source->SetEnvironment(core.environment);
  EXPECT_NO_THROW({const auto repeated=RegisterClassImage(core.storage,name,source);EXPECT_FALSE(repeated.created);});
 }
 // Numeric frequency still belongs to the image physics and cannot be ignored.
 source->SetGlobalTimeStep(20000);
 try {RegisterClassImage(core.storage,name,source);FAIL()<<"different rate accepted";}
 catch(const ClassImageError& error){EXPECT_EQ(error.code,"image_name_collision");}
 core.storage->ReturnObject(source);
}

TEST(TimeLearnerClassImages, NonfiniteParameterAndExternalBindingAreRejected)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto source = Channel(1e-9), outside = Channel(2e-9);
 ASSERT_TRUE(source); ASSERT_TRUE(outside);
 source->Capacity.SetDataDirect(std::numeric_limits<double>::quiet_NaN());
 try { RegisterClassImage(core.storage, "TimeLearnerUnit_Nonfinite", source); FAIL(); }
 catch(const ClassImageError& error) { EXPECT_EQ(error.code, "nonfinite_parameter"); }
 EXPECT_FALSE(core.storage->CheckClass("TimeLearnerUnit_Nonfinite"));
 source->Capacity = 1e-9;
 source->Capacity.SetPointer(0, &outside->Capacity);
 try { RegisterClassImage(core.storage, "TimeLearnerUnit_ExternalBinding", source); FAIL(); }
 catch(const ClassImageError& error) { EXPECT_EQ(error.code, "external_or_null_binding"); }
 EXPECT_FALSE(core.storage->CheckClass("TimeLearnerUnit_ExternalBinding"));
 source->Capacity.ResetPointer(0, &outside->Capacity);
 core.storage->ReturnObject(outside); core.storage->ReturnObject(source);
}

TEST(TimeLearnerClassImages, NativeCopyKeepsExplicitHeterogeneousGraph)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto source = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
 ASSERT_TRUE(source);
 source->SetEnvironment(core.environment);
 source->SetGlobalTimeStep(2000);
 source->Init();
 source->StructureBuildMode = 0;
 source->UseElementDefaults = false;
 auto channel = source->GetComponentL<NPulseChannel>("Soma1.ExcChannel", true);
 ASSERT_TRUE(channel);
 channel->Capacity = 1.37e-9;
 const auto registration = RegisterClassImage(core.storage, "TimeLearnerUnit_ExplicitNeuron", source);
 core.storage->ReturnObject(source);
 auto restored = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("TimeLearnerUnit_ExplicitNeuron"));
 ASSERT_TRUE(restored);
 restored->SetEnvironment(core.environment);
 restored->Init();
 EXPECT_EQ(DescribeClassImage(restored), registration.descriptor);
 const auto readback = NmsdkTools::InspectModel(restored);
 EXPECT_TRUE(readback["valid"].toBool()) << QJsonDocument(readback["diagnostics"].toArray()).toJson().constData();
 auto restoredChannel = restored->GetComponentL<NPulseChannel>("Soma1.ExcChannel", true);
 ASSERT_TRUE(restoredChannel);
 EXPECT_DOUBLE_EQ(restoredChannel->Capacity.GetData(), 1.37e-9);
 core.storage->ReturnObject(restored);
}

TEST(TimeLearnerClassImages, ContradictingParentDefaultsCannotSilentlyErasePhysics)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto source = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
 ASSERT_TRUE(source);
 source->SetEnvironment(core.environment);
 source->Init();
 ASSERT_TRUE(source->UseElementDefaults.GetData());
 auto channel = source->GetComponentL<NPulseChannel>("Soma1.ExcChannel", true);
 ASSERT_TRUE(channel);
 channel->Capacity = 1.37e-9;
 try { RegisterClassImage(core.storage, "TimeLearnerUnit_Contradiction", source); FAIL(); }
 catch(const ClassImageError& error) { EXPECT_EQ(error.code, "native_copy_mismatch"); }
 EXPECT_FALSE(core.storage->CheckClass("TimeLearnerUnit_Contradiction"));
 EXPECT_DOUBLE_EQ(channel->Capacity.GetData(), 1.37e-9);
 core.storage->ReturnObject(source);
}

TEST(TimeLearnerClassImages, DeleteUnusedImageAndReuseItsName)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto source = Channel(1.17e-9);
 ASSERT_TRUE(source);
 const std::string name = "TimeLearnerUnit_DeleteUnused";
 RegisterClassImage(core.storage, name, source);
 const auto id = core.storage->FindClassId(name);
 core.storage->DelClass(id);
 EXPECT_FALSE(core.storage->CheckClass(id));
 EXPECT_FALSE(core.storage->CheckClass(name));
 EXPECT_THROW(core.storage->DelClass(id), UStorage::EClassIdNotExist);
 source->Capacity = 1.29e-9;
 EXPECT_TRUE(RegisterClassImage(core.storage, name, source).created);
 auto instance = dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject(name));
 ASSERT_TRUE(instance);
 EXPECT_DOUBLE_EQ(instance->Capacity.GetData(), 1.29e-9);
 core.storage->ReturnObject(instance);
 core.storage->ReturnObject(source);
}

TEST(TimeLearnerClassImages, DeleteReturnedImageRefusesOutstandingLease)
{
 const auto& core = NmsdkTests::InitEngineForPulseLibTests();
 auto source = Channel(1.19e-9);
 ASSERT_TRUE(source);
 const std::string name = "TimeLearnerUnit_DeleteReturned";
 RegisterClassImage(core.storage, name, source);
 const auto id = core.storage->FindClassId(name);
 auto instance = dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject(name));
 ASSERT_TRUE(instance);
 EXPECT_THROW(core.storage->DelClass(id), UStorage::EObjectStorageNotEmpty);
 ASSERT_TRUE(core.storage->CheckClass(name));
 EXPECT_DOUBLE_EQ(instance->Capacity.GetData(), 1.19e-9);
 core.storage->ReturnObject(instance);
 instance = 0; // ReturnObject releases the lease; this is not an owning pointer.
 core.storage->DelClass(id);
 EXPECT_FALSE(core.storage->CheckClass(id));
 EXPECT_FALSE(core.storage->CheckClass(name));
 core.storage->ReturnObject(source);
}
}
