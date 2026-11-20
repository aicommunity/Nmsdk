#include <gtest/gtest.h>
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../../../Rdk/Core/Serialize/UXMLStdSerialize.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelArchive.h"
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include "TimeLearner/ModelInspection.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <limits>

namespace {
using namespace RDK;
using namespace NMSDK;

template<class T> void IntegralXmlRoundtrip(T expected)
{
 USerStorageXML saved;ASSERT_TRUE(saved.Create("IntegralProperty"));
 saved<<expected;
 std::string xml;ASSERT_TRUE(saved.Save(xml));
 USerStorageXML loaded;ASSERT_TRUE(loaded.Load(xml,"IntegralProperty"));
 T observed{};loaded>>observed;
 EXPECT_EQ(observed,expected)<<xml;
}

template<class T> void IntegralXmlBoundaries()
{
 IntegralXmlRoundtrip<T>(T(0));IntegralXmlRoundtrip<T>(T(1));
 IntegralXmlRoundtrip<T>(std::numeric_limits<T>::lowest());
 IntegralXmlRoundtrip<T>(std::numeric_limits<T>::max());
}

TEST(RdkIntegralXml, FullWidthValuesSurviveSaveLoad)
{
 IntegralXmlBoundaries<bool>();IntegralXmlBoundaries<char>();
 IntegralXmlBoundaries<unsigned char>();IntegralXmlBoundaries<short>();
 IntegralXmlBoundaries<unsigned short>();IntegralXmlBoundaries<int>();
 IntegralXmlBoundaries<unsigned int>();IntegralXmlBoundaries<long>();
 IntegralXmlBoundaries<unsigned long>();IntegralXmlBoundaries<long long>();
 IntegralXmlBoundaries<unsigned long long>();
 // Also exercise interior values that can be lost by a32-bit intermediate.
 IntegralXmlRoundtrip<long long>(4294967297LL);
 IntegralXmlRoundtrip<long long>(-4294967297LL);
 IntegralXmlRoundtrip<unsigned long long>(9223372036854775808ULL);
}

TEST(RdkIntegralXml, LegacyDecimalPrefixesRemainReadable)
{
 USerStorageXML xml;ASSERT_TRUE(xml.Create("IntegralProperty"));
 int value=0;unsigned int mask=0;bool enabled=false;
 xml.SetNodeText("  +17suffix");xml>>value;EXPECT_EQ(value,17);
 xml.SetNodeText(" -23.5");xml>>value;EXPECT_EQ(value,-23);
 xml.SetNodeText("-1");xml>>mask;EXPECT_EQ(mask,std::numeric_limits<unsigned int>::max());
 xml.SetNodeText(" +1 tail");xml>>enabled;EXPECT_TRUE(enabled);
 xml.SetNodeText("0x10");xml>>value;EXPECT_EQ(value,0); // Decimal, as before.
}

TEST(RdkIntegralXml, NativeNeuronCopyAndClassImagePreserveUnsignedMasks)
{
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 auto source=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
 auto copy=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
 ASSERT_TRUE(source);ASSERT_TRUE(copy);
 source->SetEnvironment(core.environment);source->SetGlobalTimeStep(2000);source->Init();
 source->StructureBuildMode=0;source->UseElementDefaults=false;
 const auto fullMask=std::numeric_limits<unsigned int>::max();
 source->DebugSysEventsMask=fullMask;
 auto soma=source->GetComponentL<UContainer>("Soma1",true);ASSERT_TRUE(soma);
 soma->DebugSysEventsMask=0x80000001u;
 copy->SetEnvironment(core.environment);source->Copy(copy);copy->Init();
 EXPECT_EQ(copy->DebugSysEventsMask.GetData(),fullMask);
 auto copiedSoma=copy->GetComponentL<UContainer>("Soma1",true);ASSERT_TRUE(copiedSoma);
 EXPECT_EQ(copiedSoma->DebugSysEventsMask.GetData(),0x80000001u);
 EXPECT_EQ(DescribeClassImage(copy),DescribeClassImage(source));
 const std::string name="TimeLearnerUnit_FullUnsignedMask";
 const auto image=RegisterClassImage(core.storage,name,source);
 auto restored=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(name));ASSERT_TRUE(restored);
 restored->SetEnvironment(core.environment);restored->Init();
 EXPECT_EQ(restored->DebugSysEventsMask.GetData(),fullMask);
 auto restoredSoma=restored->GetComponentL<UContainer>("Soma1",true);ASSERT_TRUE(restoredSoma);
 EXPECT_EQ(restoredSoma->DebugSysEventsMask.GetData(),0x80000001u);
 EXPECT_EQ(DescribeClassImage(restored),image.descriptor);
 core.storage->ReturnObject(restored);core.storage->ReturnObject(copy);core.storage->ReturnObject(source);
}

TEST(RdkIntegralXml, NamedIndexedAndPositionalUnsignedReadsPreserveFullWidth)
{
 USerStorageXML xml;ASSERT_TRUE(xml.Create("Root"));
 ASSERT_TRUE(xml.AddNode("Value"));xml.SetNodeText("4294967295");xml.SelectUp();
 ASSERT_TRUE(xml.AddNode("Value"));xml.SetNodeText("2147483648");xml.SelectUp();
 ASSERT_TRUE(xml.AddNode("Value"));xml.SetNodeText(" -1 suffix");xml.SelectUp();
 EXPECT_EQ(xml.ReadUnsigned("Value",0u),std::numeric_limits<unsigned int>::max());
 EXPECT_EQ(xml.ReadUnsigned("Value",1,0u),0x80000000u);
 EXPECT_EQ(xml.ReadUnsigned(2,0u),std::numeric_limits<unsigned int>::max());
 EXPECT_EQ(xml.ReadUnsigned("Missing",19u),19u);
 EXPECT_EQ(xml.GetNodeName(),"Root");
}

TEST(RdkXmlStorage, DirectMutationsAreVisibleAfterCachedReads)
{
 USerStorageXML xml;ASSERT_TRUE(xml.Create("Root"));
 xml.SetNodeText("first");EXPECT_EQ(xml.GetNodeText(),"first");
 xml.SetNodeText("second");EXPECT_EQ(xml.GetNodeText(),"second");
 EXPECT_EQ(xml.GetNodeName(),"Root");xml.RenameNode("Renamed");
 EXPECT_EQ(xml.GetNodeName(),"Renamed");EXPECT_EQ(xml.GetNodeText(),"second");
 xml.SetNodeAttribute("old","one");EXPECT_EQ(xml.GetNodeAttribute("old"),"one");
 EXPECT_EQ(xml.GetNodeAttribute("new"),"");
 xml.SetNodeAttribute("new","two");xml.SetNodeAttribute("old","updated");
 EXPECT_EQ(xml.GetNodeAttribute("new"),"two");
 EXPECT_EQ(xml.GetNodeAttribute("old"),"updated");
 xml.DelNodeAttribute("old");EXPECT_EQ(xml.GetNodeAttribute("old"),"");
 xml.SetNodeAttribute("old","recreated");
 std::string text;ASSERT_TRUE(xml.Save(text));
 USerStorageXML loaded;ASSERT_TRUE(loaded.Load(text,"Renamed"));
 EXPECT_EQ(loaded.GetNodeAttribute("new"),"two");
 EXPECT_EQ(loaded.GetNodeAttribute("old"),"recreated");
 xml.DelNodeContent();
 EXPECT_EQ(xml.GetNodeName(),"");EXPECT_EQ(xml.GetNodeText(),"");
 EXPECT_EQ(xml.GetNodeAttribute("new"),"");EXPECT_EQ(xml.GetNumNodes(),0);
}

TEST(RdkXmlStorage, CreateLoadAndDestroyDiscardPreviousCursorValues)
{
 USerStorageXML xml;ASSERT_TRUE(xml.Create("Root"));
 xml.SetNodeText("old");xml.SetNodeAttribute("mode","old");
 EXPECT_EQ(xml.GetNodeName(),"Root");EXPECT_EQ(xml.GetNodeText(),"old");
 EXPECT_EQ(xml.GetNodeAttribute("mode"),"old");
 ASSERT_TRUE(xml.Create("Root"));
 EXPECT_EQ(xml.GetNodeText(),"");EXPECT_EQ(xml.GetNodeAttribute("mode"),"");
 ASSERT_TRUE(xml.Load("<Root mode=\"loaded\">new</Root>","Root"));
 EXPECT_EQ(xml.GetNodeName(),"Root");EXPECT_EQ(xml.GetNodeText(),"new");
 EXPECT_EQ(xml.GetNodeAttribute("mode"),"loaded");
 ASSERT_TRUE(xml.Load("<Root mode=\"again\">replacement</Root>","Root"));
 EXPECT_EQ(xml.GetNodeText(),"replacement");EXPECT_EQ(xml.GetNodeAttribute("mode"),"again");
 ASSERT_TRUE(xml.Destroy());
 EXPECT_EQ(xml.GetNodeName(),"");EXPECT_EQ(xml.GetNodeText(),"");
 EXPECT_EQ(xml.GetNodeAttribute("mode"),"");
 ASSERT_TRUE(xml.Create("Root"));
 EXPECT_EQ(xml.GetNodeName(),"Root");EXPECT_EQ(xml.GetNodeAttribute("mode"),"");
}

TEST(RdkXmlStorage, SameNamedNodesKeepIndependentCursorValues)
{
 USerStorageXML xml;ASSERT_TRUE(xml.Create("Node"));
 xml.SetNodeText("parent");xml.SetNodeAttribute("scope","parent");
 EXPECT_EQ(xml.GetNodeText(),"parent");EXPECT_EQ(xml.GetNodeAttribute("scope"),"parent");
 ASSERT_TRUE(xml.AddNode("Node"));
 EXPECT_EQ(xml.GetNodeText(),"");EXPECT_EQ(xml.GetNodeAttribute("scope"),"");
 xml.SetNodeText("first");xml.SetNodeAttribute("scope","first");
 EXPECT_EQ(xml.GetNodeText(),"first");EXPECT_EQ(xml.GetNodeAttribute("scope"),"first");
 xml.SelectUp();ASSERT_TRUE(xml.AddNode("Node"));
 xml.SetNodeText("second");xml.SetNodeAttribute("scope","second");
 EXPECT_EQ(xml.GetNodeText(),"second");EXPECT_EQ(xml.GetNodeAttribute("scope"),"second");
 xml.SelectRoot();ASSERT_TRUE(xml.SelectNode("Node",0));
 EXPECT_EQ(xml.GetNodeText(),"first");EXPECT_EQ(xml.GetNodeAttribute("scope"),"first");
 xml.SelectUp();ASSERT_TRUE(xml.SelectNode(1));
 EXPECT_EQ(xml.GetNodeText(),"second");EXPECT_EQ(xml.GetNodeAttribute("scope"),"second");
 xml.DelNode();
 EXPECT_EQ(xml.GetNodeText(),"parent");EXPECT_EQ(xml.GetNodeAttribute("scope"),"parent");
 EXPECT_EQ(xml.GetNumNodes("Node"),1);
}

TEST(RdkXmlStorage, LoadingFieldsPreservesSourceCursorAndCopiesActualValues)
{
 USerStorageXML source;ASSERT_TRUE(source.Create("Document"));
 ASSERT_TRUE(source.AddNode("Item"));source.SetNodeText("child");
 source.SetNodeAttribute("owner","source");
 EXPECT_EQ(source.GetNodeName(),"Item");EXPECT_EQ(source.GetNodeText(),"child");
 EXPECT_EQ(source.GetNodeAttribute("owner"),"source");
 USerStorageXML target;ASSERT_TRUE(target.Create("Document"));
 target.SetNodeText("target");target.SetNodeAttribute("owner","target");
 EXPECT_EQ(target.GetNodeText(),"target");EXPECT_EQ(target.GetNodeAttribute("owner"),"target");
 ASSERT_TRUE(target.LoadFieldsToNode(source,false));
 EXPECT_EQ(source.GetNodeName(),"Item");EXPECT_EQ(source.GetNodeText(),"child");
 EXPECT_EQ(source.GetNodeAttribute("owner"),"source");
 source.SetNodeText("source changed");
 ASSERT_TRUE(target.SelectNode("Item"));
 EXPECT_EQ(target.GetNodeText(),"child");EXPECT_EQ(target.GetNodeAttribute("owner"),"source");
 target.SelectRoot();target.DelNodeInternalContent();
 EXPECT_EQ(target.GetNodeName(),"Document");EXPECT_EQ(target.GetNodeText(),"target");
 EXPECT_EQ(target.GetNodeAttribute("owner"),"target");EXPECT_EQ(target.GetNumNodes(),0);
 ASSERT_TRUE(target.LoadToNode(source,false));
 ASSERT_TRUE(target.SelectNode("Document"));ASSERT_TRUE(target.SelectNode("Item"));
 EXPECT_EQ(target.GetNodeText(),"source changed");
 target.SelectRoot();
 ASSERT_TRUE(target.LoadToNode("<Imported flag=\"yes\">text</Imported>","Imported",true));
 ASSERT_TRUE(target.SelectNode("Imported"));
 EXPECT_EQ(target.GetNodeText(),"text");EXPECT_EQ(target.GetNodeAttribute("flag"),"yes");
 target.SelectRoot();EXPECT_EQ(target.GetNumNodes(),1);
 EXPECT_EQ(source.GetNodeName(),"Item");EXPECT_EQ(source.GetNodeText(),"source changed");
}

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


void NativeFastProfile(unsigned variant,unsigned frequency)
{
 using namespace NMSDK::TimeLearner;
 const auto& core=NmsdkTests::InitEngineForPulseLibTests();
 const double capacities[]={1e-9,5e-10,2.5e-10,2.5e-10};
 const double dissociations[]={.005,.005,.005,.002};
 const double cap=capacities[variant],tc=dissociations[variant];
 auto stock=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGen"));ASSERT_TRUE(stock);
 stock->SetEnvironment(core.environment);stock->SetGlobalTimeStep(frequency);stock->Init();
 auto membrane=stock->GetComponentL<NPulseMembrane>("Soma1",true);ASSERT_TRUE(membrane);
 StorageProfileSpec spec;spec.name="TLNativeFast"+std::to_string(variant)+"F"+std::to_string(frequency);
 spec.frequencyHz=frequency;spec.neuronBaseClass="NSPNeuronGen";
 spec.ltZoneBaseClass=stock->LTZoneClassName.GetData();
 spec.positiveGeneratorBaseClass=stock->ExcGeneratorClassName.GetData();
 spec.negativeGeneratorBaseClass=stock->InhGeneratorClassName.GetData();
 spec.initialThreshold=stock->LTZone->Threshold.GetData();
 spec.body.baseClass=membrane->GetCompClassName();
 spec.body.useAveragePotential=membrane->UseAveragePotential.GetData();
 spec.body.feedbackGain=membrane->FeedbackGain.GetData();
 for(const auto& role:{std::string("Exc"),std::string("Inh")})
 {
  auto ch=membrane->GetComponentL<NPulseChannel>(role+"Channel",true);ASSERT_TRUE(ch);
  auto sy=membrane->GetComponentL<NPulseSynapse>(role+"Synapse1",true);ASSERT_TRUE(sy);
  auto& channel=role=="Exc"?spec.body.excChannel:spec.body.inhChannel;
  channel={ch->GetCompClassName(),cap,ch->Resistance.GetData(),ch->RestingResistance.GetData()};
  auto& synapse=role=="Exc"?spec.body.excSynapse:spec.body.inhSynapse;
  synapse.baseClass=sy->GetCompClassName();synapse.resistance=sy->Resistance.GetData();
  synapse.secretionTC=sy->SecretionTC.GetData();synapse.dissociationTC=tc;
  synapse.pulseDuration=sy->TypicalPulseDuration.GetData();synapse.pulseAmplitude=sy->PulseAmplitude.GetData();
  synapse.usePulseSignal=sy->UsePulseSignal.GetData();synapse.usePresynapticInhibition=sy->UsePresynapticInhibition.GetData();
  synapse.inhibitionCoefficient=sy->InhibitionCoeff.GetData();
 }
 core.storage->ReturnObject(stock);
 const auto profile=RegisterStorageProfile(core.storage,core.environment,spec);
 for(int reuse=0;reuse<2;++reuse)
 {
  auto neuron=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(profile.neuronClass));ASSERT_TRUE(neuron);
  neuron->SetEnvironment(core.environment);neuron->SetGlobalTimeStep(frequency);neuron->Init();
  EXPECT_FALSE(neuron->UseElementDefaults.GetData());EXPECT_DOUBLE_EQ(neuron->MembraneCapacity.GetData(),0.);
  const auto check=[&]() {
   std::vector<NameT> parts;neuron->GetComponentsList(parts);unsigned membranes=0;
   for(const auto& path:parts)
   {
    EXPECT_NE(path,"LTMembrane");
    auto part=dynamic_pointer_cast<NPulseMembrane>(neuron->GetComponent(path,true));if(!part)continue;
    ++membranes;
    for(const auto& role:{std::string("Exc"),std::string("Inh")})
    {
     auto ch=part->GetComponentL<NPulseChannel>(role+"Channel",true);ASSERT_TRUE(ch);
     auto sy=part->GetComponentL<NPulseSynapse>(role+"Synapse1",true);ASSERT_TRUE(sy);
     EXPECT_DOUBLE_EQ(ch->Capacity.GetData(),cap);EXPECT_EQ(ch->GetTimeStep(),frequency);
     EXPECT_DOUBLE_EQ(sy->DissociationTC.GetData(),tc);EXPECT_EQ(sy->GetTimeStep(),frequency);
    }
   }
   EXPECT_GE(membranes,1u);
  };
  check(); // Fresh/reused image before a growth Build can mask its physics.
  neuron->StructureBuildMode=2;neuron->NumSomaMembraneParts=1;
  neuron->NumDendriteMembranePartsVec=std::vector<int>{2};neuron->Build();neuron->Init();
  ASSERT_TRUE(neuron->GetComponent("Dendrite1_2",true));check();
  neuron->Reset();check();const auto identity=NmsdkTools::InspectModel(neuron);
  ASSERT_TRUE(identity["valid"].toBool())<<QJsonDocument(identity["diagnostics"].toArray()).toJson().constData();
  if(reuse==0)
  {
   QJsonObject metadata{{"implementation_id","timelearner-native-fast-profile-v1"},{"state_kind","model_spec"},
    {"training",QJsonObject{{"status","not_trained"}}},
    {"calibration",QJsonObject{{"status","fixed"},{"protocol","profile-default-not-calibrated"},
      {"threshold",spec.initialThreshold},{"ltzone_path","$.LTZone"}}},
    {"conversion",QJsonObject{{"mode","none"}}}};
   const auto archive=NmsdkTools::ExportModelArchive(neuron,metadata,{},profile.classNames);
   const char* directory=std::getenv("TIMELEARNER_PROFILE_TEST_DIR");
   if(!directory)directory=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");
   if(directory)
   {
    std::filesystem::create_directories(directory);
    const auto path=std::filesystem::path(directory)/(spec.name+".json");
    std::ofstream out(path,std::ios::binary);out<<QJsonDocument(archive).toJson().constData();ASSERT_TRUE(out.good());
   }
  }
  core.storage->ReturnObject(neuron);
 }
}
TEST(NativeFastStorageProfiles, Stock2000) {NativeFastProfile(0,2000);}
TEST(NativeFastStorageProfiles, Stock20000) {NativeFastProfile(0,20000);}
TEST(NativeFastStorageProfiles, HalfC2000) {NativeFastProfile(1,2000);}
TEST(NativeFastStorageProfiles, HalfC20000) {NativeFastProfile(1,20000);}
TEST(NativeFastStorageProfiles, QuarterC2000) {NativeFastProfile(2,2000);}
TEST(NativeFastStorageProfiles, QuarterC20000) {NativeFastProfile(2,20000);}
TEST(NativeFastStorageProfiles, QuarterCFast2000) {NativeFastProfile(3,2000);}
TEST(NativeFastStorageProfiles, QuarterCFast20000) {NativeFastProfile(3,20000);}

}
