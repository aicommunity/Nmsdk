#include <gtest/gtest.h>
#include "TimeLearner/ModelIdentity.h"
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
#include <chrono>

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
    UProperty<std::pair<std::string,std::string>, IdentityGraph, ptPubParameter> LinkName;
    UProperty<double, IdentityGraph, ptPubState | ptOutput> First, Second;
    UProperty<std::vector<double>, IdentityGraph, ptPubState | ptInput> Input;
    IdentityGraph() : Gain("Gain", this), Weights("Weights", this), Mapping("Mapping", this), LinkName("LinkName", this),
                      First("First", this), Second("Second", this), Input("Input", this)
    { Gain = 1e-9; Weights = std::vector<double>{1., 2.}; Mapping->Assign(2, 3, 0); LinkName = std::make_pair(std::string("Node"),std::string("Output")); }
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
    graph->LinkName = std::make_pair(std::string("Other"),std::string("Output")); EXPECT_NE(Digest(graph), initial);
    graph->LinkName = std::make_pair(std::string("Node"),std::string("Output")); EXPECT_EQ(Digest(graph), initial);
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

class ObserverGraph : public IdentityGraph {
public:
    UProperty<bool,ObserverGraph,ptPubParameter> Flag;
    UProperty<int,ObserverGraph,ptPubParameter> Int;
    UProperty<long,ObserverGraph,ptPubParameter> Long;
    UProperty<long long,ObserverGraph,ptPubParameter> LongLong;
    UProperty<unsigned int,ObserverGraph,ptPubParameter> UInt;
    UProperty<unsigned long,ObserverGraph,ptPubParameter> ULong;
    UProperty<unsigned long long,ObserverGraph,ptPubParameter> ULongLong;
    UProperty<std::string,ObserverGraph,ptPubParameter> Text;
    UProperty<std::vector<int>,ObserverGraph,ptPubParameter> Indices;
    UProperty<std::vector<std::string>,ObserverGraph,ptPubParameter> Labels;
    UProperty<MDMatrix<double>,ObserverGraph,ptPubParameter|ptInput> Matrix;
    UProperty<MDMatrix<double>,ObserverGraph,ptPubState|ptOutput> MatrixSource;
    ObserverGraph():Flag("Flag",this),Int("Int",this),Long("Long",this),LongLong("LongLong",this),
        UInt("UInt",this),ULong("ULong",this),ULongLong("ULongLong",this),Text("Text",this),
        Indices("Indices",this),Labels("Labels",this),Matrix("Matrix",this),MatrixSource("MatrixSource",this)
    {Flag=false;Int=0;Long=0;LongLong=0;UInt=0;ULong=0;ULongLong=0;Text="alpha";
     Indices=std::vector<int>{0,1};Labels=std::vector<std::string>{"a","b"};Matrix->Assign(2,3,0.);MatrixSource->Assign(2,3,1.);}
    ObserverGraph* New(void) override{return new ObserverGraph;}
};
UEPtr<ObserverGraph> ObservedGraph()
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string name="TimeLearnerObserverGraph";
    if(!core.storage->CheckClass(name))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]()->UComponent*{return new ObserverGraph;},name),name);
    auto graph=dynamic_pointer_cast<ObserverGraph>(core.storage->TakeObject(name));
    if(!graph)throw std::runtime_error("observer_fixture");
    graph->SetEnvironment(core.environment);graph->SetGlobalTimeStep(2000);graph->Init();return graph;
}
void CompareObserved(NmsdkTools::ModelRevisionObserver& observer,UEPtr<UContainer> model,
    const NmsdkTools::ModelBoundarySources& ports={})
{
    const auto actual=NmsdkTools::IdentifyModel(model,ports);
    if(actual["valid"].toBool())EXPECT_EQ(observer.Read(model,ports),actual["sha256"].toString());
    else EXPECT_THROW(observer.Read(model,ports),std::runtime_error);
}
TEST(ModelRevisionObserver, MatchesFullIdentityAcrossAllSupportedTypedParameterFamilies)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();auto graph=ObservedGraph();
    NmsdkTools::ModelRevisionObserver observer;CompareObserved(observer,graph);
    const auto edit=[&](auto change){const auto before=observer.FullReads();change();CompareObserved(observer,graph);EXPECT_EQ(observer.FullReads(),before+1);};
    edit([&]{graph->Flag=true;});edit([&]{graph->Int=-13;});edit([&]{graph->Long=17;});
    edit([&]{graph->LongLong=std::numeric_limits<long long>::min();});
    edit([&]{graph->UInt=std::numeric_limits<unsigned int>::max();});
    edit([&]{graph->ULong=std::numeric_limits<unsigned long>::max();});
    edit([&]{graph->ULongLong=std::numeric_limits<unsigned long long>::max();});
    edit([&]{graph->Gain=std::nextafter(graph->Gain.GetData(),std::numeric_limits<double>::infinity());});
    edit([&]{graph->Text="beta";});edit([&]{graph->LinkName=std::make_pair(std::string("x"),std::string("y"));});
    edit([&]{graph->Weights=std::vector<double>{2.,1.};});edit([&]{graph->Indices=std::vector<int>{1,0};});
    edit([&]{graph->Labels=std::vector<std::string>{"b","a"};});
    edit([&]{graph->Mapping(1,2)=7;});edit([&]{graph->Matrix(1,2)=std::nextafter(0.,1.);});
    edit([&]{graph->Matrix->Assign(3,2,0.);});edit([&]{graph->Mapping->Assign(3,2,7);});
    CompareObserved(observer,graph);EXPECT_GT(observer.CacheHits(),0u);core.storage->ReturnObject(graph);
}
TEST(ModelRevisionObserver, DoesNotHashDynamicsButDetectsMasksBindingsAliasesAndActivity)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();auto graph=ObservedGraph();
    NmsdkTools::ModelRevisionObserver observer;CompareObserved(observer,graph);const auto initial=observer.Read(graph);
    graph->Name="RenamedObserverRoot";graph->Coord=MVector<double,3>(3,4,5);graph->First=17.;
    CompareObserved(observer,graph);EXPECT_EQ(observer.Read(graph),initial);EXPECT_EQ(observer.FullReads(),1u);
    graph->Matrix.SetPointer(0,&graph->MatrixSource);CompareObserved(observer,graph);const auto bound=observer.Read(graph);
    graph->MatrixSource(0,0)=19.;CompareObserved(observer,graph);EXPECT_EQ(observer.Read(graph),bound);
    graph->Matrix.ResetPointer(0,&graph->MatrixSource);CompareObserved(observer,graph);
    graph->Input.SetPointer(0,&graph->First);graph->Input.SetPointer(1,&graph->Second);CompareObserved(observer,graph);
    graph->Input.ResetPointer(0,&graph->First);graph->Input.ResetPointer(0,&graph->Second);
    graph->Input.SetPointer(0,&graph->Second);graph->Input.SetPointer(1,&graph->First);CompareObserved(observer,graph);
    ASSERT_TRUE(graph->AddPropertyAlias("ExternalInput","","Input",ptPubInput));CompareObserved(observer,graph);
    graph->ClearPropertyAliases();CompareObserved(observer,graph);
    ASSERT_TRUE(graph->ChangeLookupPropertyType("Gain",ptPubState));CompareObserved(observer,graph);
    ASSERT_TRUE(graph->ChangeLookupPropertyType("Gain",ptPubParameter));CompareObserved(observer,graph);
    graph->Activity=false;CompareObserved(observer,graph);graph->Activity=true;CompareObserved(observer,graph);
    graph->Input.ResetPointer(0,&graph->Second);graph->Input.ResetPointer(0,&graph->First);
    core.storage->ReturnObject(graph);
}
TEST(ModelRevisionObserver, InvalidNumbersAndUnknownBindingsNeverReuseAValidHash)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();auto graph=ObservedGraph(),outside=ObservedGraph();
    NmsdkTools::ModelRevisionObserver observer;CompareObserved(observer,graph);
    graph->Gain=std::numeric_limits<double>::quiet_NaN();CompareObserved(observer,graph);
    graph->Gain=0.;CompareObserved(observer,graph);const auto full=observer.FullReads();
    graph->Gain=-0.;CompareObserved(observer,graph);EXPECT_EQ(observer.FullReads(),full);
    graph->Weights=std::vector<double>{std::numeric_limits<double>::infinity()};CompareObserved(observer,graph);
    graph->Weights=std::vector<double>{1.};CompareObserved(observer,graph);
    graph->Matrix(0,0)=std::numeric_limits<double>::infinity();CompareObserved(observer,graph);
    graph->Matrix(0,0)=0.;CompareObserved(observer,graph);
    graph->Input.SetPointer(0,&outside->First);CompareObserved(observer,graph);
    graph->Input.ResetPointer(0,&outside->First);CompareObserved(observer,graph);
    graph->UnInit();CompareObserved(observer,graph);EXPECT_FALSE(graph->IsInit());
    graph->Init();CompareObserved(observer,graph);graph->Reset();CompareObserved(observer,graph);
    graph->SetGlobalTimeStep(20000);graph->Init();CompareObserved(observer,graph);
    const auto before=observer.FullReads();observer.Read(graph,{},true);EXPECT_EQ(observer.FullReads(),before+1);
    observer.Clear();CompareObserved(observer,graph);
    core.storage->ReturnObject(outside);core.storage->ReturnObject(graph);
}
TEST(ModelRevisionObserver, RealNativeGraphCachesOrderGrowthAndReuseMatchTheFullInspector)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();StorageProfileSpec spec;spec.name="ObserverNativeProfile";
    spec.ltMembrane=spec.body;spec.ltMembrane->excChannel.capacity=.3e-9;
    const auto profile=RegisterStorageProfile(core.storage,core.environment,spec);
    auto neuron=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(profile.neuronClass));ASSERT_TRUE(neuron);
    neuron->SetEnvironment(core.environment);neuron->SetGlobalTimeStep(2000);
    neuron->NumSomaMembraneParts=2;neuron->StructureBuildMode=2;neuron->NumDendriteMembranePartsVec=std::vector<int>{1,3};neuron->Init();
    NmsdkTools::ModelRevisionObserver observer;CompareObserved(observer,neuron);
    auto channel=neuron->GetComponentL<NPulseChannel>("Dendrite2_3.ExcChannel",true);ASSERT_TRUE(channel);
    channel->Capacity=std::nextafter(channel->Capacity.GetData(),std::numeric_limits<double>::infinity());CompareObserved(observer,neuron);
    const auto membranes=neuron->Membranes;neuron->Membranes.pop_back();CompareObserved(observer,neuron);
    neuron->Membranes=membranes;CompareObserved(observer,neuron);
    const double timeConstant=channel->TimeConstant.GetData();channel->TimeConstant=std::numeric_limits<double>::quiet_NaN();CompareObserved(observer,neuron);
    channel->TimeConstant=timeConstant;CompareObserved(observer,neuron);
    neuron->SetComponentPosition("LTMembrane",0);CompareObserved(observer,neuron);
    neuron->NumDendriteMembranePartsVec=std::vector<int>{2,4};neuron->Build();neuron->Init();CompareObserved(observer,neuron);
    neuron->NumDendriteMembranePartsVec=std::vector<int>{1,1};neuron->Build();neuron->Init();CompareObserved(observer,neuron);
    core.storage->ReturnObject(neuron);
    neuron=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(profile.neuronClass));ASSERT_TRUE(neuron);
    neuron->SetEnvironment(core.environment);neuron->SetGlobalTimeStep(2000);neuron->Init();CompareObserved(observer,neuron);
    core.storage->ReturnObject(neuron);
}
TEST(ModelRevisionObserver, DeclaredPortsAndUnsupportedModelsAreCheckedWithoutStaleParameterReads)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();auto graph=ObservedGraph(),source=ObservedGraph();
    graph->Matrix.SetPointer(0,&source->MatrixSource);
    NmsdkTools::ModelBoundarySources ports{{&source->MatrixSource,"stimulus"}};
    NmsdkTools::ModelRevisionObserver observer;CompareObserved(observer,graph,ports);const auto initial=observer.Read(graph,ports);
    source->MatrixSource(0,0)=17.;CompareObserved(observer,graph,ports);EXPECT_EQ(observer.Read(graph,ports),initial);
    auto renamed=ports;renamed.begin()->second="other_port";CompareObserved(observer,graph,renamed);
    EXPECT_NE(observer.Read(graph,renamed),initial);CompareObserved(observer,graph,ports);
    graph->Matrix.ResetPointer(0,&source->MatrixSource);CompareObserved(observer,graph,ports);
    CompareObserved(observer,graph); // valid again only without the unused port
    graph->Matrix.SetPointer(0,&source->MatrixSource);CompareObserved(observer,graph,ports);
    source->Reset();CompareObserved(observer,graph,ports);
    graph->Matrix.ResetPointer(0,&source->MatrixSource);CompareObserved(observer,graph);
    core.storage->ReturnObject(source);core.storage->ReturnObject(graph);
    auto unsupported=new UnsupportedIdentityGraph;unsupported->SetEnvironment(core.environment);unsupported->Init();
    EXPECT_THROW(observer.Read(unsupported),std::runtime_error);delete unsupported;
}

TEST(ModelRevisionObserver, ActualGraphReadCostIsRecordedWithoutChangingIdentityOrDynamics)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();StorageProfileSpec spec;spec.name="ObserverBenchmarkProfile";
    const auto profile=RegisterStorageProfile(core.storage,core.environment,spec);
    auto neuron=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(profile.neuronClass));ASSERT_TRUE(neuron);
    neuron->SetEnvironment(core.environment);neuron->SetGlobalTimeStep(2000);neuron->StructureBuildMode=2;
    neuron->NumSomaMembraneParts=6;neuron->NumDendriteMembranePartsVec=std::vector<int>{2,3,4,5,6,7};neuron->Init();
    NmsdkTools::ModelRevisionObserver observer;const auto hash=observer.Read(neuron);
    const auto started=std::chrono::steady_clock::now();constexpr unsigned reads=128;
    for(unsigned i=0;i<reads;++i)ASSERT_EQ(NmsdkTools::IdentifyModel(neuron)["sha256"].toString(),hash);
    const auto middle=std::chrono::steady_clock::now();
    for(unsigned i=0;i<reads;++i)ASSERT_EQ(observer.Read(neuron),hash);
    const auto finished=std::chrono::steady_clock::now();
    EXPECT_EQ(observer.FullReads(),1u);EXPECT_EQ(observer.CacheHits(),reads);
    Artifact("observer-read-cost.json",QJsonObject{{"kind","model_revision_observer_cost"},{"reads",int(reads)},
        {"model_sha256",hash},{"nodes",NmsdkTools::IdentifyModel(neuron)["model"].toObject()["nodes"].toArray().size()},
        {"full_seconds",std::chrono::duration<double>(middle-started).count()},
        {"observer_seconds",std::chrono::duration<double>(finished-middle).count()},
        {"frequency_hz",2000},{"measurement_only",true},{"dynamics_calculated",false}});
    core.storage->ReturnObject(neuron);
}
class ReplaceableObserverGraph : public ObserverGraph {
    std::unique_ptr<UIProperty> extra;
public:
    ReplaceableObserverGraph(){Replace(false);}
    ~ReplaceableObserverGraph() override{DelLookupProperty("Extra");extra.reset();}
    void Replace(bool integer)
    {
        if(extra){DelLookupProperty("Extra");extra.reset();}
        if(integer){auto value=new UProperty<int,ReplaceableObserverGraph,ptPubParameter>("Extra",this);*value=7;extra.reset(value);}
        else {auto value=new UProperty<double,ReplaceableObserverGraph,ptPubParameter>("Extra",this);*value=7.;extra.reset(value);}
    }
    ReplaceableObserverGraph* New(void) override{return new ReplaceableObserverGraph;}
};
TEST(ModelRevisionObserver, PropertyReplacementChecksMembershipAndTypeBeforeDereferencingOldReaders)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string name="TimeLearnerReplaceableObserverGraph";
    if(!core.storage->CheckClass(name))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]()->UComponent*{return new ReplaceableObserverGraph;},name),name);
    auto graph=dynamic_pointer_cast<ReplaceableObserverGraph>(core.storage->TakeObject(name));ASSERT_TRUE(graph);
    graph->SetEnvironment(core.environment);graph->SetGlobalTimeStep(2000);graph->Init();
    NmsdkTools::ModelRevisionObserver observer;const auto initial=observer.Read(graph);
    const auto lifetime=graph->ObserveLifecycle();
    graph->Replace(true);ASSERT_TRUE(lifetime.IsCurrent());CompareObserved(observer,graph);EXPECT_NE(observer.Read(graph),initial);
    graph->Replace(false);CompareObserved(observer,graph);EXPECT_EQ(observer.Read(graph),initial);
    core.storage->ReturnObject(graph);
}
TEST(ModelRevisionObserver, DestroyedDeclaredSourceIsRejectedBeforeReadingItsStaleProperty)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();auto graph=ObservedGraph();
    auto source=new ObserverGraph;source->SetEnvironment(core.environment);source->SetGlobalTimeStep(2000);source->Init();
    graph->Matrix.SetPointer(0,&source->MatrixSource);NmsdkTools::ModelBoundarySources ports{{&source->MatrixSource,"stimulus"}};
    NmsdkTools::ModelRevisionObserver observer;CompareObserved(observer,graph,ports);
    graph->Matrix.ResetPointer(0,&source->MatrixSource);delete source;
    EXPECT_THROW(observer.Read(graph,ports),std::runtime_error);
    CompareObserved(observer,graph);core.storage->ReturnObject(graph);
}
}
