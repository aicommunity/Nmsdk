#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/ModelIdentity.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <limits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;

class IdentityGraph : public UNet
{
public:
    UProperty<double, IdentityGraph, ptPubParameter> Gain;
    UProperty<std::vector<double>, IdentityGraph, ptPubParameter> Weights;
    UProperty<MDMatrix<int>, IdentityGraph, ptPubParameter> Mapping;
    UProperty<double, IdentityGraph, ptPubState | ptOutput> First, Second;
    UProperty<std::vector<double>, IdentityGraph, ptPubState | ptInput> Input;
    IdentityGraph() : Gain("Gain", this), Weights("Weights", this), Mapping("Mapping", this),
                      First("First", this), Second("Second", this), Input("Input", this)
    { Gain = 1e-9; Weights = std::vector<double>{1., 2.}; Mapping->Assign(2, 3, 0); }
    IdentityGraph* New(void) override { return new IdentityGraph; }
};

UEPtr<IdentityGraph> Graph()
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    const std::string name = "TimeLearnerIdentityGraph";
    if(!core.storage->CheckClass(name))
        core.storage->AddClass(new UComponentFactoryMethod(core.storage,
            +[]() -> UComponent* { return new IdentityGraph; }, name), name);
    auto graph = dynamic_pointer_cast<IdentityGraph>(core.storage->TakeObject(name));
    if(graph) { graph->SetEnvironment(core.environment); graph->SetGlobalTimeStep(2000); graph->Init(); }
    return graph;
}

QString Digest(UEPtr<UContainer> model)
{
    const auto identity = NmsdkTools::IdentifyModel(model);
    EXPECT_TRUE(identity["valid"].toBool()) << QJsonDocument(identity).toJson().constData();
    EXPECT_EQ(identity["sha256"].toString().size(), 64);
    return identity["sha256"].toString();
}

void Artifact(const std::string& name, const QJsonObject& document)
{
    const char* directory = std::getenv("TIMELEARNER_IDENTITY_TEST_DIR");
    if(!directory) return;
    const auto path = std::filesystem::path(directory)/name;
    std::filesystem::create_directories(path.parent_path());
    std::ofstream file(path, std::ios::binary);
    file << QJsonDocument(document).toJson().toStdString();
    ASSERT_TRUE(file.good());
}

void MembraneIndexMatchesNativeOrder(UEPtr<NPulseNeuron> neuron)
{
    std::vector<NPulseMembraneCommon*> expected;
    for(int i = 0; i < neuron->GetNumComponents(); ++i)
        if(auto membrane = dynamic_pointer_cast<NPulseMembraneCommon>(neuron->GetComponentByIndex(i)))
            expected.push_back(membrane.Get());
    EXPECT_EQ(neuron->Membranes, expected);
}

TEST(TimeLearnerModelIdentity, IgnoresDynamicsAndRootNameButRetainsEveryPhysicalBit)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto graph = Graph(); ASSERT_TRUE(graph);
    const auto initial = Digest(graph);
    graph->First = 17.; graph->Second = -24.; graph->Name = "AnotherRootName";
    graph->Coord = MVector<double,3>(10,20,30);
    EXPECT_EQ(Digest(graph), initial);
    const double value = graph->Gain.GetData();
    graph->Gain = std::nextafter(value, std::numeric_limits<double>::infinity());
    EXPECT_NE(Digest(graph), initial);
    graph->Gain = value; EXPECT_EQ(Digest(graph), initial);
    graph->Weights = std::vector<double>{2.,1.}; EXPECT_NE(Digest(graph), initial);
    graph->Weights = std::vector<double>{1.,2.}; EXPECT_EQ(Digest(graph), initial);
    graph->Mapping(1,2) = 7; EXPECT_NE(Digest(graph), initial);
    graph->Mapping(1,2) = 0; EXPECT_EQ(Digest(graph), initial);
    graph->SetGlobalTimeStep(20000); graph->Init(); EXPECT_NE(Digest(graph), initial);
    graph->SetGlobalTimeStep(2000); graph->Init(); EXPECT_EQ(Digest(graph), initial);
    Artifact("canonical-fixture.json", NmsdkTools::IdentifyModel(graph));
    core.storage->ReturnObject(graph);
}

TEST(TimeLearnerModelIdentity, BindingSlotsAliasesAndDisconnectedPortsAreDistinct)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto graph = Graph(); ASSERT_TRUE(graph);
    const auto unbound = Digest(graph);
    graph->Input.SetPointer(0, &graph->First); graph->Input.SetPointer(1, &graph->Second);
    const auto bound = Digest(graph); EXPECT_NE(bound, unbound);
    graph->First = 8.; graph->Second = 11.; EXPECT_EQ(Digest(graph), bound);
    graph->Input.ResetPointer(0, &graph->First); graph->Input.ResetPointer(0, &graph->Second);
    graph->Input.SetPointer(0, &graph->Second); graph->Input.SetPointer(1, &graph->First);
    EXPECT_NE(Digest(graph), bound);
    const auto beforeAlias = Digest(graph);
    ASSERT_TRUE(graph->AddPropertyAlias("Stimulus", "", "Input", ptPubInput));
    EXPECT_NE(Digest(graph), beforeAlias);
    graph->ClearPropertyAliases();
    graph->Input.ResetPointer(0, &graph->Second); graph->Input.ResetPointer(0, &graph->First);
    core.storage->ReturnObject(graph);
}

TEST(TimeLearnerModelIdentity, NonfiniteAndOutsideBindingsCannotProduceFingerprint)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto graph = Graph(), outside = Graph(); ASSERT_TRUE(graph); ASSERT_TRUE(outside);
    graph->Gain = std::numeric_limits<double>::quiet_NaN();
    auto invalid = NmsdkTools::IdentifyModel(graph);
    EXPECT_FALSE(invalid["valid"].toBool()); EXPECT_FALSE(invalid.contains("sha256"));
    graph->Gain = 1e-9;
    graph->Input.SetPointer(0, &outside->First);
    invalid = NmsdkTools::IdentifyModel(graph);
    EXPECT_FALSE(invalid["valid"].toBool()); EXPECT_FALSE(invalid.contains("sha256"));
    graph->Input.ResetPointer(0, &outside->First);
    core.storage->ReturnObject(outside); core.storage->ReturnObject(graph);
}

TEST(TimeLearnerModelIdentity, DoesNotInitializeAnUnreadyModel)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto graph = Graph(); ASSERT_TRUE(graph);
    graph->UnInit(); ASSERT_FALSE(graph->IsInit());
    const auto report = NmsdkTools::IdentifyModel(graph);
    EXPECT_FALSE(report["valid"].toBool()); EXPECT_FALSE(report.contains("sha256"));
    EXPECT_FALSE(graph->IsInit());
    graph->Init(); EXPECT_FALSE(Digest(graph).isEmpty());
    core.storage->ReturnObject(graph);
}

TEST(TimeLearnerModelIdentity, VerifiesStoredDataBeforeComparingTheActualGraph)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto graph = Graph(); ASSERT_TRUE(graph);
    const auto expected = NmsdkTools::IdentifyModel(graph);
    auto check = NmsdkTools::VerifyModelIdentity(expected, graph);
    EXPECT_TRUE(check["valid"].toBool()); EXPECT_TRUE(check["match"].toBool());
    graph->Gain = 2e-9;
    check = NmsdkTools::VerifyModelIdentity(expected, graph);
    EXPECT_TRUE(check["valid"].toBool()); EXPECT_FALSE(check["match"].toBool());
    EXPECT_EQ(check["reason"].toString(), "model_mismatch");
    EXPECT_TRUE(check["first_difference"].toString().contains("Gain"));
    auto corrupt = expected; corrupt["sha256"] = QString(64, '0');
    check = NmsdkTools::VerifyModelIdentity(corrupt, graph);
    EXPECT_FALSE(check["valid"].toBool()); EXPECT_FALSE(check["match"].toBool());
    EXPECT_EQ(check["reason"].toString(), "expected_digest_mismatch");
    corrupt = expected; corrupt["schema_version"] = 999;
    EXPECT_FALSE(NmsdkTools::VerifyModelIdentity(corrupt, graph)["valid"].toBool());
    corrupt = expected; auto model = corrupt["model"].toObject(); model["nodes"] = QJsonArray{}; corrupt["model"] = model;
    EXPECT_FALSE(NmsdkTools::VerifyModelIdentity(corrupt, graph)["valid"].toBool());
    core.storage->ReturnObject(graph);
}

class UnsupportedIdentityGraph : public IdentityGraph
{
public:
    UProperty<std::list<double>, UnsupportedIdentityGraph, ptPubParameter> Unsupported;
    UProperty<std::string, UnsupportedIdentityGraph, ptPubParameter> ApiKey;
    UnsupportedIdentityGraph() : Unsupported("Unsupported",this), ApiKey("ApiKey",this)
    { ApiKey = "must-not-be-written"; }
    UnsupportedIdentityGraph* New(void) override { return new UnsupportedIdentityGraph; }
};

TEST(TimeLearnerModelIdentity, UnsupportedParametersFailClosedAndCredentialsAreExcluded)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    const std::string name = "TimeLearnerUnsupportedIdentityGraph";
    core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* { return new UnsupportedIdentityGraph; }, name), name);
    auto graph = dynamic_pointer_cast<UnsupportedIdentityGraph>(core.storage->TakeObject(name));
    ASSERT_TRUE(graph); graph->SetEnvironment(core.environment); graph->Init();
    const auto report = NmsdkTools::IdentifyModel(graph);
    EXPECT_FALSE(report["valid"].toBool()); EXPECT_FALSE(report.contains("sha256"));
    const auto serialized = QJsonDocument(report).toJson();
    EXPECT_TRUE(serialized.contains("unsupported_parameter_type"));
    EXPECT_TRUE(serialized.contains("excluded_credential_property"));
    EXPECT_FALSE(serialized.contains("must-not-be-written"));
    core.storage->ReturnObject(graph);
}

TEST(TimeLearnerModelIdentity, NativeAsymmetricXmlRoundtripRetainsFullSemanticModel)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    StorageProfileSpec spec; spec.name = "TimeLearnerIdentityProfile";
    spec.ltMembrane = spec.body; spec.ltMembrane->excChannel.capacity = .3e-9;
    const auto profile = RegisterStorageProfile(core.storage, core.environment, spec);
    auto source = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(profile.neuronClass));
    ASSERT_TRUE(source); source->SetEnvironment(core.environment);
    source->NumSomaMembraneParts = 2; source->StructureBuildMode = 2;
    source->NumDendriteMembranePartsVec = std::vector<int>{1,3}; source->Init();
    auto tip = source->GetComponentL<NPulseMembrane>("Dendrite2_3", true); ASSERT_TRUE(tip);
    tip->NumExcitatorySynapses = 3; tip->Build();
    auto synapse = tip->GetComponentL<NPulseSynapse>("ExcSynapse2", true);
    auto channel = tip->GetComponentL<NPulseChannel>("ExcChannel", true);
    ASSERT_TRUE(synapse); ASSERT_TRUE(channel);
    synapse->Resistance = 333e6; channel->Capacity = 1.41e-9;
    MembraneIndexMatchesNativeOrder(source);
    const auto original = Digest(source);
    USerStorageXML xml; ASSERT_TRUE(xml.Create("ModelIdentityFixture"));
    ASSERT_TRUE(source->SaveComponent(&xml, true, ptPubParameter | ptPubState | pgSystem));
    ASSERT_TRUE(xml.SelectNode(source->GetName()));
    auto restored = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(profile.neuronClass));
    ASSERT_TRUE(restored); restored->SetEnvironment(core.environment);
    ASSERT_TRUE(restored->LoadComponent(&xml,true)); restored->Init();
    MembraneIndexMatchesNativeOrder(restored);
    Artifact("asymmetric-restored.json", NmsdkTools::IdentifyModel(restored));
    EXPECT_EQ(Digest(restored), original);
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(NmsdkTools::IdentifyModel(source), restored)["match"].toBool());
    const auto completeIndex = restored->Membranes;
    restored->Membranes.pop_back();
    auto invalid = NmsdkTools::IdentifyModel(restored);
    EXPECT_FALSE(invalid["valid"].toBool()); EXPECT_FALSE(invalid.contains("sha256"));
    restored->Membranes = completeIndex;
    auto restoredSynapse = restored->GetComponentL<NPulseSynapse>("Dendrite2_3.ExcSynapse2", true);
    ASSERT_TRUE(restoredSynapse); restoredSynapse->Resistance = 334e6;
    EXPECT_NE(Digest(restored), original); restoredSynapse->Resistance = 333e6;
    EXPECT_EQ(Digest(restored), original);
    const auto ltPosition = restored->GetComponent("LTMembrane",true)->GetName();
    restored->SetComponentPosition(ltPosition,0);
    EXPECT_NE(Digest(restored), original);
    Artifact("asymmetric-source.json", NmsdkTools::IdentifyModel(source));
    Artifact("asymmetric-reordered.json", NmsdkTools::IdentifyModel(restored));
    core.storage->ReturnObject(restored); core.storage->ReturnObject(source);
}
}
