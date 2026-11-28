#include <gtest/gtest.h>
#include "NAxoneCommon.h"
#include "NAxoneSegment.h"
#include "NAxoneChain.h"
#include "NAxoneChainAndDelay.h"
#include "NAxoneTreeChain.h"
#include "NAxoneDelay.h"
#include "NAperiodicLink.h"
#include "TimeLearner/ModelArchive.h"
#include "TimeLearner/AxoneConductionObservation.h"
#include "NPulseGenerator.h"
#include "NPulseMembrane.h"
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <exception>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <utility>
#include <typeinfo>

namespace {
using namespace RDK;
using namespace NMSDK;

void Require(bool valid, const char* reason)
{
    if(!valid) throw std::runtime_error(reason);
}

double Scalar(const MDMatrix<double>& matrix)
{
    Require(matrix.GetSize() == 1, "axone_lifecycle_scalar_dimension");
    const double value = matrix(0, 0);
    Require(std::isfinite(value), "axone_lifecycle_nonfinite_signal");
    return value;
}

class AxoneLifecycle : public ::testing::Test {
protected:
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UNet> model;
    ULongTime originalTime = 0;

    void SetUp() override
    {
        const auto& core = NmsdkTests::InitEngineForPulseLibTests();
        storage = core.storage;
        environment = core.environment;
        ASSERT_TRUE(storage);
        ASSERT_TRUE(environment);
        originalTime = environment->GetTime().GetTime();
        environment->DestroyModel();
        environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));
        model = dynamic_pointer_cast<UNet>(environment->GetModel());
        ASSERT_TRUE(model);
        model->SetGlobalTimeStep(2000);
        environment->GetTime().SetTime(ULongTime(0));
    }

    template<class Action> void Cleanup(const char* phase, Action action)
    {
        try { action(); }
        catch(const UException& error) {
            ADD_FAILURE() << phase << ": " << typeid(error).name()
                << " type=" << error.GetType() << " number=" << error.GetNumber()
                << " file=" << error.GetExFileName() << ":" << error.GetExLineNumber()
                << " object=" << error.GetObjectName() << " message=" << error.what();
            CleanupLedger(phase);
        }
        catch(const std::exception& error) { ADD_FAILURE() << phase << ": " << error.what(); CleanupLedger(phase); }
        catch(...) { ADD_FAILURE() << phase << ": unknown native exception"; CleanupLedger(phase); }
    }

    void CleanupLedger(const char* phase)
    {
        // Logger failures can mask the original caught lifecycle exception.
        // The operation ledger survives independently and includes its reason.
        try {
            unsigned visited=0;
            std::function<void(UEPtr<UContainer>)> walk=[&](UEPtr<UContainer> node) {
                if(!node || visited++>=512) return;
                const auto failure=node->LastOperationFailure();
                if(failure.Sequence || failure.Overflowed)
                    std::cout << "CleanupLedger phase=" << phase << " component=" << node->GetFullName()
                        << " sequence=" << failure.Sequence << " operation=" << failure.Operation
                        << " reason=" << failure.Reason << std::endl;
                for(int index=0;index<node->GetNumComponents();++index)walk(node->GetComponentByIndex(index));
            };
            walk(model);
        } catch(...) { std::cout << "CleanupLedger unavailable phase=" << phase << std::endl; }
    }

    void TearDown() override
    {
        if(model) Cleanup("BreakLinks", [&] { model->BreakLinks(); });
        if(environment) {
            Cleanup("DestroyModel", [&] { environment->DestroyModel(); });
            Cleanup("RestoreClock", [&] { environment->GetTime().SetTime(originalTime); });
        }
    }

    template<class T> UEPtr<T> Take(const std::string& image, const std::string& name = "Axon")
    {
        auto component = dynamic_pointer_cast<T>(storage->TakeObject(image));
        Require(bool(component), "axone_lifecycle_factory");
        component->Name = name;
        component->SetEnvironment(environment);
        component->SetGlobalTimeStep(model->GetTimeStep());
        UEPtr<UContainer> base = component;
        Require(model->AddComponent(base) != ForbiddenId, "axone_lifecycle_attach");
        return component;
    }

    void Init()
    {
        const auto marker = model->OperationFailureSequence();
        model->Init();
        Require(model->IsReady() && model->IsInit() &&
                !model->HasOperationFailureSince(marker), "axone_lifecycle_init");
        model->Reset();
        Require(!model->HasOperationFailureSince(marker), "axone_lifecycle_reset");
    }

    void RequireInitialized(UEPtr<UContainer> node)
    {
        Require(node->IsInit() && node->IsReady(), "axone_lifecycle_uninitialized_subtree");
        for(int index = 0; index < node->GetNumComponents(); ++index)
            RequireInitialized(node->GetComponentByIndex(index));
    }

    template<class T> void Rebuild(const UEPtr<T>& node)
    {
        const auto marker = node->OperationFailureSequence();
        node->Build();
        Require(node->IsReady() && !node->HasOperationFailureSince(marker),
                "axone_lifecycle_rebuild");
    }

    template<class T> UEPtr<NLTZone> Zone(const UEPtr<T>& node, const std::string& path = "LTZone")
    {
        auto zone = node->template GetComponentL<NLTZone>(path, true);
        Require(bool(zone), "axone_lifecycle_zone");
        return zone;
    }
};

TEST_F(AxoneLifecycle, LayoutPreservesConfiguredThresholds)
{
    auto segment = Take<NAxoneSegment>("NAxoneSegment");
    Init();
    auto zone = Zone(segment);
    zone->Threshold = .071;
    zone->ThresholdOff = -.013;
    segment->ApplyDiagramLayout();
    EXPECT_DOUBLE_EQ(zone->Threshold.GetData(), .071);
    EXPECT_DOUBLE_EQ(zone->ThresholdOff.GetData(), -.013);
}

TEST_F(AxoneLifecycle, BuildAndResetPreserveConfiguredThresholds)
{
    auto segment = Take<NAxoneSegment>("NAxoneSegment");
    Init();
    auto zone = Zone(segment);
    zone->Threshold = .071;
    zone->ThresholdOff = -.013;
    Rebuild(segment); // Exercise the already-ready Build path too.
    model->Reset();
    EXPECT_EQ(Zone(segment), zone);
    EXPECT_DOUBLE_EQ(zone->Threshold.GetData(), .071);
    EXPECT_DOUBLE_EQ(zone->ThresholdOff.GetData(), -.013);
}

TEST_F(AxoneLifecycle, ExplicitDefaultRestoresAxonFactoryThresholds)
{
    auto segment = Take<NAxoneSegment>("NAxoneSegment");
    Init();
    Zone(segment)->Threshold = .071;
    Zone(segment)->ThresholdOff = -.013;
    const auto marker = segment->OperationFailureSequence();
    segment->Default();
    Rebuild(segment);
    EXPECT_FALSE(segment->HasOperationFailureSince(marker));
    EXPECT_DOUBLE_EQ(Zone(segment)->Threshold.GetData(), .03);
    EXPECT_DOUBLE_EQ(Zone(segment)->ThresholdOff.GetData(), 0.);
}

TEST_F(AxoneLifecycle, ChainGrowthPreservesExistingNodeParameters)
{
    auto chain = Take<NAxoneChain>("NAxoneChain");
    chain->NumSegments = 2;
    Init();
    auto first = chain->GetComponentL<NAxoneSegment>("Segment1", true);
    ASSERT_TRUE(first);
    Zone(first)->Threshold = .067;
    first->Inertial->Tau = .0025;
    chain->NumSegments = 3;
    Rebuild(chain);
    model->Reset();
    EXPECT_EQ(chain->GetComponentL<NAxoneSegment>("Segment1", true), first);
    EXPECT_DOUBLE_EQ(Zone(first)->Threshold.GetData(), .067);
    EXPECT_DOUBLE_EQ(first->Inertial->Tau.GetData(), .0025);
    ASSERT_TRUE(chain->GetComponent("Segment3", true));
    RequireInitialized(chain);
    EXPECT_DOUBLE_EQ(Zone(chain, "Segment3.LTZone")->Threshold.GetData(), .03);
}

TEST_F(AxoneLifecycle, ChainGrowthPreservesLoadedMembraneClassOverlay)
{
    auto chain = Take<NAxoneChain>("NAxoneChain");
    chain->NumSegments = 2;
    Init();
    auto membrane = dynamic_pointer_cast<NPulseMembrane>(storage->TakeObject("NPMembraneBio"));
    ASSERT_TRUE(membrane);
    membrane->SetEnvironment(environment);
    membrane->Init();
    const std::string image = "AxoneLifecycle_CustomMembrane";
    RegisterClassImage(storage, image, membrane);
    storage->ReturnObject(membrane);

    auto first = chain->GetComponentL<NAxoneSegment>("Segment1", true);
    ASSERT_TRUE(first);
    first->MembraneClassName = image;
    chain->NumSegments = 3;
    Rebuild(chain);
    EXPECT_EQ(first->MembraneClassName.GetData(), image);
    ASSERT_TRUE(first->GetComponent("Soma", true));
    EXPECT_EQ(first->GetComponent("Soma", true)->GetCompClassName(), image);
    EXPECT_EQ(chain->GetComponentL<NAxoneSegment>("Segment3", true)->MembraneClassName.GetData(),
              chain->MembraneClassName.GetData());
}

TEST_F(AxoneLifecycle, RebuildPreservesHeterogeneousInternodeDelays)
{
    auto chain = Take<NAxoneChainAndDelay>("NAxoneChainAndDelay");
    chain->NumNodes = 3;
    Init();
    auto first = chain->GetComponentL<NAxoneDelay>("Delay1", true);
    auto second = chain->GetComponentL<NAxoneDelay>("Delay2", true);
    ASSERT_TRUE(first);
    ASSERT_TRUE(second);
    first->DelayTime = .004;
    second->DelayTime = .007;
    chain->NumNodes = 4;
    Rebuild(chain);
    model->Reset();
    EXPECT_EQ(chain->GetComponentL<NAxoneDelay>("Delay1", true), first);
    EXPECT_EQ(chain->GetComponentL<NAxoneDelay>("Delay2", true), second);
    EXPECT_DOUBLE_EQ(first->DelayTime.GetData(), .004);
    EXPECT_DOUBLE_EQ(second->DelayTime.GetData(), .007);
    EXPECT_DOUBLE_EQ(chain->GetComponentL<NAxoneDelay>("Delay3", true)->DelayTime.GetData(),
                     chain->InternodeDelayTime.GetData());
}

TEST_F(AxoneLifecycle, ExplicitInternodeAssignmentUpdatesExistingDelays)
{
    auto chain = Take<NAxoneChainAndDelay>("NAxoneChainAndDelay");
    chain->NumNodes = 3;
    Init();
    chain->GetComponentL<NAxoneDelay>("Delay1", true)->DelayTime = .004;
    chain->InternodeDelayTime = .002;
    Rebuild(chain);
    EXPECT_DOUBLE_EQ(chain->GetComponentL<NAxoneDelay>("Delay1", true)->DelayTime.GetData(), .002);
    EXPECT_DOUBLE_EQ(chain->GetComponentL<NAxoneDelay>("Delay2", true)->DelayTime.GetData(), .002);
}

TEST_F(AxoneLifecycle, InvalidDelayIsRejectedWithoutChangingParameters)
{
    auto delay = Take<NAxoneDelay>("NAxoneDelay");
    Init();
    const double previous = delay->DelayTime.GetData();
    for(double invalid : {std::numeric_limits<double>::quiet_NaN(),
                          std::numeric_limits<double>::infinity(),
                          -std::numeric_limits<double>::infinity(),
                          std::numeric_limits<double>::max(), -1., 0.}) {
        EXPECT_ANY_THROW(delay->DelayTime.SetData(invalid));
        EXPECT_DOUBLE_EQ(delay->DelayTime.GetData(), previous);
    }
}

TEST_F(AxoneLifecycle, DelayFrequencyChangeFlushesOldGridAndRecomputesDefault)
{
    auto source = Take<NPulseGenerator>("NPGenerator", "Source");
    auto delay = Take<NAxoneDelay>("NAxoneDelay");
    source->Frequency = 10.; source->Amplitude = 1.;
    source->PulseLength = .001; source->Delay = .01; source->FrequencyDeviation = 0.;
    Require(model->CreateLink("Source", "Output", "Axon", "Input"), "delay_clock_source_link");
    Init();
    const auto marker = model->OperationFailureSequence();
    bool emitted = false;
    for(unsigned tick = 0; tick < 100 && !emitted; ++tick) {
        model->Calculate();
        Require(!model->HasOperationFailureSince(marker), "delay_clock_old_grid_calculate");
        emitted = Scalar(source->Output.GetData()) > .5;
        EXPECT_DOUBLE_EQ(Scalar(delay->Output.GetData()), 0.);
        environment->IncreaseModelTimeByStep();
    }
    ASSERT_TRUE(emitted);
    model->SetGlobalTimeStep(20000);
    source->Frequency = 0.;
    // Do not Reset: a queued old-grid pulse must be discarded by the component.
    for(unsigned tick = 0; tick < 25; ++tick) {
        model->Calculate();
        Require(!model->HasOperationFailureSince(marker), "delay_clock_transition_calculate");
        EXPECT_DOUBLE_EQ(Scalar(delay->Output.GetData()), 0.);
        environment->IncreaseModelTimeByStep();
    }
    source->Frequency = 10.;
    environment->GetTime().SetTime(ULongTime(0));
    model->Reset();
    int inputTick = -1, outputTick = -1;
    for(int tick = 0; tick <= 800; ++tick) {
        model->Calculate();
        Require(!model->HasOperationFailureSince(marker), "delay_clock_new_grid_calculate");
        if(inputTick < 0 && Scalar(source->Output.GetData()) > .5) inputTick = tick;
        if(outputTick < 0 && Scalar(delay->Output.GetData()) > .5) outputTick = tick;
        environment->IncreaseModelTimeByStep();
    }
    ASSERT_GE(inputTick, 0); ASSERT_GE(outputTick, 0);
    EXPECT_EQ(outputTick-inputTick, 20);
    EXPECT_DOUBLE_EQ(delay->DelayTime.GetData(), .001);
}

TEST_F(AxoneLifecycle, InvalidInternodeDelayIsRejectedBeforeChildChanges)
{
    auto chain = Take<NAxoneChainAndDelay>("NAxoneChainAndDelay");
    chain->NumNodes = 2;
    Init();
    const double previous = chain->InternodeDelayTime.GetData();
    const double child = chain->GetComponentL<NAxoneDelay>("Delay1", true)->DelayTime.GetData();
    EXPECT_ANY_THROW(chain->InternodeDelayTime.SetData(std::numeric_limits<double>::quiet_NaN()));
    EXPECT_ANY_THROW(chain->InternodeDelayTime.SetData(std::numeric_limits<double>::infinity()));
    EXPECT_ANY_THROW(chain->InternodeDelayTime.SetData(std::numeric_limits<double>::max()));
    EXPECT_DOUBLE_EQ(chain->InternodeDelayTime.GetData(), previous);
    EXPECT_DOUBLE_EQ(chain->GetComponentL<NAxoneDelay>("Delay1", true)->DelayTime.GetData(), child);
}

TEST_F(AxoneLifecycle, InertialLinkRejectsNonfiniteParameters)
{
    auto link = Take<NAperiodicLink>("NAperiodicLink");
    Init();
    const double tau = link->Tau.GetData(), bias = link->Bias.GetData();
    EXPECT_ANY_THROW(link->Tau.SetData(std::numeric_limits<double>::quiet_NaN()));
    EXPECT_ANY_THROW(link->Tau.SetData(std::numeric_limits<double>::infinity()));
    EXPECT_ANY_THROW(link->Bias.SetData(std::numeric_limits<double>::quiet_NaN()));
    EXPECT_ANY_THROW(link->Bias.SetData(std::numeric_limits<double>::infinity()));
    EXPECT_DOUBLE_EQ(link->Tau.GetData(), tau);
    EXPECT_DOUBLE_EQ(link->Bias.GetData(), bias);
}

TEST_F(AxoneLifecycle, MissingChildClassRecordsBuildFailureAndCanRecover)
{
    auto segment = Take<NAxoneSegment>("NAxoneSegment");
    Init();
    segment->MembraneClassName = "AxoneLifecycle_MissingMembraneImage";
    const auto rejected = segment->OperationFailureSequence();
    segment->Build(); // Its bool is not an error channel in Rdk.
    EXPECT_FALSE(segment->IsReady());
    EXPECT_TRUE(segment->HasOperationFailureSince(rejected));
    segment->MembraneClassName = "NPMembraneBio";
    Rebuild(segment);
    EXPECT_EQ(segment->GetComponent("Soma", true)->GetCompClassName(), "NPMembraneBio");
}

TEST_F(AxoneLifecycle, ElongationReportsNativeBuildFailure)
{
    auto chain = Take<NAxoneChain>("NAxoneChain");
    Init();
    const int previous = chain->NumSegments.GetData();
    chain->MembraneClassName = "AxoneLifecycle_MissingElongationImage";
    const auto marker = chain->OperationFailureSequence();
    EXPECT_EQ(chain->Elongate(), nullptr);
    EXPECT_EQ(chain->NumSegments.GetData(), previous);
    EXPECT_TRUE(chain->HasOperationFailureSince(marker));
    chain->MembraneClassName = "NPMembraneBio";
    Rebuild(chain);
}

struct Capture {
    std::vector<double> inputs, outputs;
    std::string csv;
    bool complete = false;
};

bool WriteArtifact(const std::string& stem, const std::string& suffix, const QByteArray& bytes)
{
    const char* output = std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
    if(!output) return false; // Engineering assertions alone are not scientific admission.
    const QString directory = QDir(QString::fromLocal8Bit(output)).filePath("AxoneP1");
    Require(QDir().mkpath(directory), "axone_lifecycle_output_directory");
    QFile file(QDir(directory).filePath(QString::fromStdString(stem + suffix)));
    Require(file.open(QIODevice::WriteOnly | QIODevice::NewOnly), "axone_lifecycle_output_exists");
    Require(file.write(bytes) == bytes.size() && file.flush(), "axone_lifecycle_output_write");
    return true;
}

Capture Play(UEPtr<UNet> model, UEPtr<UEnvironment> environment,
             UEPtr<NPulseGenerator> source, UEPtr<NAxoneCommon> axon,
             unsigned frequency, const std::string& stem)
{
    std::ostringstream csv;
    csv.imbue(std::locale::classic());
    csv << std::setprecision(17) << "time,source,axon\n";
    Capture result;
    bool inputHigh = false, outputHigh = false;
    const auto marker = model->OperationFailureSequence();
    std::exception_ptr failure;
    try {
        const unsigned end = frequency * 11 / 20; // 0.5 s source, 0.05 s tail.
        for(unsigned tick = 0; tick <= end; ++tick) {
            if(tick == frequency / 2) source->Frequency = 0.;
            model->Calculate();
            Require(!model->HasOperationFailureSince(marker), "axone_lifecycle_calculate");
            const double time = environment->GetTime().GetDoubleTime();
            Require(std::abs(time - double(tick) / frequency) <= 1e-12,
                    "axone_lifecycle_clock_grid");
            const double input = Scalar(source->Output.GetData());
            const double output = Scalar(axon->Output.GetData());
            if(input > .5 && !inputHigh) result.inputs.push_back(time);
            if(output > .5 && !outputHigh) result.outputs.push_back(time);
            inputHigh = input > .5;
            outputHigh = output > .5;
            csv << time << ',' << input << ',' << output << '\n';
            environment->IncreaseModelTimeByStep();
        }
        result.complete = true;
    } catch(...) {
        failure = std::current_exception();
    }
    result.csv = csv.str();
    QJsonArray inputs, outputs;
    for(double value : result.inputs) inputs.append(value);
    for(double value : result.outputs) outputs.append(value);
    const QJsonObject record{
        {"kind", "axone_native_lifecycle_observation"}, {"schema_version", 1},
        {"frequency_hz", int(frequency)}, {"source_window_s", .5}, {"tail_s", .05},
        {"complete", result.complete}, {"input_events", inputs}, {"output_events", outputs},
        {"axon_class", QString::fromStdString(axon->GetCompClassName())},
        {"scheduler", "root_UNet"}, {"source", "NPulseGenerator"}, {"training", false}
    };
    WriteArtifact(stem, ".csv", QByteArray::fromStdString(result.csv));
    WriteArtifact(stem, ".json", QJsonDocument(record).toJson(QJsonDocument::Indented));
    if(failure) std::rethrow_exception(failure);
    return result;
}

struct PropagationCase {
    std::string id, image;
    unsigned frequency;
    int count;
    double delay;
};

std::vector<PropagationCase> Cases()
{
    std::vector<PropagationCase> result;
    for(unsigned frequency : {2000u, 20000u, 40000u}) {
        for(int milliseconds : {1, 2, 5, 10, 20})
            result.push_back({"delay_t" + std::to_string(milliseconds) + "ms_f" + std::to_string(frequency),
                              "NAxoneDelay", frequency, 0, milliseconds / 1000.});
        for(int count : {1, 2, 3, 5, 7})
            result.push_back({"chain_n" + std::to_string(count) + "_f" + std::to_string(frequency),
                              "NAxoneChain", frequency, count, 0.});
        for(int count : {1, 2, 3, 4, 5})
            result.push_back({"cad_n" + std::to_string(count) + "_f" + std::to_string(frequency),
                              "NAxoneChainAndDelay", frequency, count, .002});
    }
    return result;
}

class AxonePropagation : public AxoneLifecycle,
                         public ::testing::WithParamInterface<PropagationCase> {};

TEST_P(AxonePropagation, PreservesAllSparseSpikesThroughNativeScheduler)
{
    const auto& request = GetParam();
    model->SetGlobalTimeStep(request.frequency);
    auto source = Take<NPulseGenerator>("NPGenerator", "Source");
    auto axon = Take<NAxoneCommon>(request.image);
    source->Frequency = 10.;
    source->PulseLength = .001;
    source->Amplitude = 1.;
    source->Delay = .01;
    source->FrequencyDeviation = 0.;
    if(auto chain = dynamic_pointer_cast<NAxoneChain>(axon))
        chain->NumSegments = request.count;
    if(auto chain = dynamic_pointer_cast<NAxoneChainAndDelay>(axon)) {
        chain->NumNodes = request.count;
        chain->InternodeDelayTime = request.delay;
    }
    if(auto delay = dynamic_pointer_cast<NAxoneDelay>(axon))
        delay->DelayTime = request.delay;
    Require(model->CreateLink("Source", "Output", "Axon", "Input"), "axone_lifecycle_source_link");
    Init();
    ASSERT_EQ(source->GetTimeStep(), request.frequency);
    ASSERT_EQ(axon->GetTimeStep(), request.frequency);
    if(request.count > 0) {
        for(int index = 1; index <= request.count; ++index) {
            auto segment = axon->GetComponentL<NAxoneSegment>("Segment" + std::to_string(index), true);
            ASSERT_TRUE(segment);
            ASSERT_EQ(segment->GetTimeStep(), request.frequency);
        }
        EXPECT_FALSE(axon->GetComponent("Segment" + std::to_string(request.count + 1), true));
    }
    RequireInitialized(axon);
    const auto captured = Play(model, environment, source, axon, request.frequency, request.id);
    ASSERT_TRUE(captured.complete);
    ASSERT_EQ(captured.inputs.size(), 5u);
    ASSERT_EQ(captured.outputs.size(), captured.inputs.size());
    for(std::size_t index = 0; index < captured.inputs.size(); ++index) {
        EXPECT_GE(captured.outputs[index], captured.inputs[index]);
        if(request.image == "NAxoneDelay") {
            const double exact = std::floor(request.delay * request.frequency) / request.frequency;
            EXPECT_NEAR(captured.outputs[index] - captured.inputs[index], exact, 1e-12);
        }
    }
}

INSTANTIATE_TEST_SUITE_P(P1Baseline, AxonePropagation, ::testing::ValuesIn(Cases()),
    [](const ::testing::TestParamInfo<PropagationCase>& value) { return value.param.id; });


std::string TreeTopology(const std::string& carrier = "NAxoneChain",
                         int leftLength = 3, bool addBranch = false)
{
    const auto section = [&](const char* id, const char* parent, int tap, int length) {
        QJsonObject value{{"id", id}, {"parent", parent}, {"attach_segment", tap},
                          {"carrier", QString::fromStdString(carrier)}, {"segments", length}};
        if(carrier == "NAxoneChainAndDelay") value.insert("internode_delay_s", .002);
        return value;
    };
    // Intentionally not in calculation order.
    QJsonArray sections{section("Left", "Root", 1, leftLength),
                        section("Right", "Root", 2, 2), section("Root", "", 0, 2)};
    QJsonObject ports{{"main", "Left"}, {"left", "Left"}, {"right", "Right"}, {"trunk", "Root"}};
    if(addBranch) {
        sections.append(section("Later", "Root", 1, 1));
        ports.insert("later", "Later");
    }
    return QJsonDocument(QJsonObject{{"schema_version", 1}, {"sections", sections},
                                    {"ports", ports}, {"output_port", "main"}})
        .toJson(QJsonDocument::Compact).toStdString();
}

TEST(AxoneTreeTopology, SortsParentsBeforeChildrenAndKeepsStablePortNames)
{
    const auto graph = NAxoneTreeChain::ParseTopology(TreeTopology());
    ASSERT_EQ(graph.sections.size(), 3u);
    EXPECT_EQ(graph.sections[0].id, "Root");
    EXPECT_EQ(graph.sections[1].id, "Left");
    EXPECT_EQ(graph.sections[2].id, "Right");
    EXPECT_EQ(graph.ports.at("left"), "Left");
    EXPECT_EQ(graph.ports.at("right"), "Right");
}

TEST(AxoneTreeTopology, RejectsInvalidGraphsBeforeNativeMutation)
{
    const auto edit = [](const std::function<void(QJsonObject&)>& change) {
        auto object = QJsonDocument::fromJson(QByteArray::fromStdString(TreeTopology())).object();
        change(object);
        return QJsonDocument(object).toJson(QJsonDocument::Compact).toStdString();
    };
    const std::vector<std::string> invalid{
        "{}", "[]", "{",
        R"({"schema_version":1,"schema_version":1})",
        R"({"schema_version":1,"schema_\u0076ersion":1})",
        edit([](QJsonObject& object) { object.insert("schema_version", 2); }),
        edit([](QJsonObject& object) { object.insert("output_port", "missing"); }),
        edit([](QJsonObject& object) { object.insert("unexpected", true); }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            auto row = rows[0].toObject(); row["parent"] = "Missing"; rows[0] = row;
            object["sections"] = rows;
        }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            auto row = rows[0].toObject(); row["attach_segment"] = 3; rows[0] = row;
            object["sections"] = rows;
        }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            auto row = rows[0].toObject(); row["segments"] = 1.5; rows[0] = row;
            object["sections"] = rows;
        }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            auto left = rows[0].toObject(); left["parent"] = "Right"; rows[0] = left;
            auto right = rows[1].toObject(); right["parent"] = "Left"; rows[1] = right;
            object["sections"] = rows;
        }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            rows.append(rows[0]); object["sections"] = rows;
        }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            auto row = rows[0].toObject(); row["id"] = "Unsafe.Path"; rows[0] = row;
            object["sections"] = rows;
        }),
        edit([](QJsonObject& object) {
            auto rows = object["sections"].toArray();
            auto row = rows[0].toObject(); row["parent"] = ""; row["attach_segment"] = 0;
            rows[0] = row; object["sections"] = rows;
        })
    };
    for(std::size_t index = 0; index < invalid.size(); ++index) {
        SCOPED_TRACE(index);
        EXPECT_THROW(NAxoneTreeChain::ParseTopology(invalid[index]), std::invalid_argument);
    }
}

TEST(AxoneTreeTopology, AllowsGrowthButRejectsLiveShorteningAndCarrierReplacement)
{
    const auto original = NAxoneTreeChain::ParseTopology(TreeTopology());
    EXPECT_NO_THROW(NAxoneTreeChain::ValidateExtension(
        original, NAxoneTreeChain::ParseTopology(TreeTopology("NAxoneChain", 4, true))));
    EXPECT_THROW(NAxoneTreeChain::ValidateExtension(
        original, NAxoneTreeChain::ParseTopology(TreeTopology("NAxoneChain", 2))),
        std::invalid_argument);
    EXPECT_THROW(NAxoneTreeChain::ValidateExtension(
        original, NAxoneTreeChain::ParseTopology(TreeTopology("NAxoneChainAndDelay"))),
        std::invalid_argument);
}

TEST_F(AxoneLifecycle, TreeGrowthPreservesPhysicalSectionsAndNamedPorts)
{
    auto tree = Take<NAxoneTreeChain>("NAxoneTreeChain");
    tree->Topology = TreeTopology();
    Init();
    RequireInitialized(tree);
    const auto left = tree->GetPortComponent("left");
    const auto rootSection = tree->GetPortComponent("trunk");
    auto zone = Zone(left, "Segment1.LTZone");
    zone->Threshold = .063;
    EXPECT_EQ(tree->ResolvePortPath("left"), "Left.Output");
    EXPECT_TRUE(tree->CheckPropertyAlias("left"));

    tree->Topology = TreeTopology("NAxoneChain", 4, true);
    Rebuild(tree);
    model->Reset();
    RequireInitialized(tree);
    EXPECT_EQ(tree->GetPortComponent("left"), left);
    EXPECT_EQ(tree->GetPortComponent("trunk"), rootSection);
    EXPECT_EQ(tree->ResolvePortPath("left"), "Left.Output");
    EXPECT_DOUBLE_EQ(Zone(left, "Segment1.LTZone")->Threshold.GetData(), .063);
    EXPECT_TRUE(tree->GetPortComponent("later"));
    const auto previous = tree->Topology.GetData();
    EXPECT_ANY_THROW(tree->Topology.SetData(TreeTopology("NAxoneChain", 2)));
    EXPECT_EQ(tree->Topology.GetData(), previous);
    EXPECT_TRUE(tree->IsReady());
}

TEST_F(AxoneLifecycle, TreeCopyRefreshesPortsAndPreservesLearnedChildParameters)
{
    auto tree = Take<NAxoneTreeChain>("NAxoneTreeChain");
    tree->Topology = TreeTopology("NAxoneChainAndDelay");
    Init();
    Zone(tree->GetPortComponent("left"), "Segment1.LTZone")->Threshold = .057;
    auto delay = tree->GetComponentL<NAxoneDelay>("Left.Delay1", true);
    ASSERT_TRUE(delay);
    delay->DelayTime = .007;
    auto copy = dynamic_pointer_cast<NAxoneTreeChain>(tree->Alloc(storage));
    ASSERT_TRUE(copy);
    copy->Name = "TreeCopy";
    UEPtr<UContainer> base = copy;
    ASSERT_NE(model->AddComponent(base), ForbiddenId);
    copy->Init();
    copy->Reset();
    RequireInitialized(copy);
    EXPECT_NE(copy->GetPortComponent("left"), tree->GetPortComponent("left"));
    EXPECT_EQ(copy->ResolvePortPath("left"), "Left.Output");
    EXPECT_DOUBLE_EQ(Zone(copy->GetPortComponent("left"), "Segment1.LTZone")->Threshold.GetData(), .057);
    EXPECT_DOUBLE_EQ(copy->GetComponentL<NAxoneDelay>("Left.Delay1", true)->DelayTime.GetData(), .007);
}

TEST_F(AxoneLifecycle, TreeFreeDetachesCompleteGraphWithoutRebuilding)
{
    auto tree=Take<NAxoneTreeChain>("NAxoneTreeChain");
    tree->Topology=TreeTopology();
    Init();
    const auto marker=tree->OperationFailureSequence();
    ASSERT_NO_THROW(tree->Free());
    EXPECT_FALSE(tree->GetOwner());
    EXPECT_EQ(tree->GetNumComponents(),0);
    EXPECT_FALSE(model->GetComponent("Axon",true));
    EXPECT_FALSE(tree->HasOperationFailureSince(marker));
    EXPECT_TRUE(tree->GetPropertyAliases().empty());
}

TEST_F(AxoneLifecycle, TreeCanBeReacquiredAfterWholeModelDestruction)
{
    auto tree=Take<NAxoneTreeChain>("NAxoneTreeChain");
    tree->Topology=TreeTopology("NAxoneChainAndDelay");
    Init();
    ASSERT_NO_THROW(environment->DestroyModel());
    ASSERT_FALSE(environment->GetModel());
    ASSERT_TRUE(environment->CreateModel("NModel"));
    model=dynamic_pointer_cast<UNet>(environment->GetModel());
    ASSERT_TRUE(model);
    model->SetGlobalTimeStep(20000);
    auto next=Take<NAxoneTreeChain>("NAxoneTreeChain","Reacquired");
    next->Topology=TreeTopology("NAxoneChain",4,true);
    Init();
    RequireInitialized(next);
    EXPECT_EQ(next->ResolvePortPath("left"),"Left.Output");
    EXPECT_EQ(next->ResolvePortPath("later"),"Later.Output");
    EXPECT_EQ(next->GetComponentL<NAxoneChain>("Left",true)->NumSegments.GetData(),4);
}

TEST_F(AxoneLifecycle, TreeNativeSnapshotPreservesPortsParametersAndActualWaveforms)
{
    auto source=Take<NPulseGenerator>("NPGenerator","Source");
    source->Frequency=10.;source->PulseLength=.001;source->Amplitude=1.;source->Delay=.01;
    source->FrequencyDeviation=0.;source->AvgInterval=1.;
    auto tree=Take<NAxoneTreeChain>("NAxoneTreeChain");tree->Topology=TreeTopology("NAxoneChainAndDelay");
    ASSERT_TRUE(model->CreateLink("Source","Output","Axon","Input"));Init();
    Zone(tree->GetPortComponent("left"),"Segment1.LTZone")->Threshold=.027;
    tree->GetComponentL<NAxoneDelay>("Left.Delay1",true)->DelayTime=.007;
    const NmsdkTools::ModelBoundarySources ports{{&source->Output,"source"}};
    const auto identity=NmsdkTools::IdentifyModel(tree,ports);
    ASSERT_TRUE(identity["valid"].toBool());
    const auto snapshot=NmsdkTools::ExportAxoneTreeSnapshot(tree,ports);
    const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
    Require(output!=nullptr,"axone_snapshot_owned_output_required");
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneTreeSnapshot");
    Require(QDir().mkpath(folder),"axone_snapshot_output_directory");
    QFile file(QDir(folder).filePath("heterogeneous-tree.json"));
    Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"axone_snapshot_file_exists");
    const auto bytes=QJsonDocument(snapshot).toJson();
    Require(file.write(bytes)==bytes.size() && file.flush(),"axone_snapshot_file_write");file.close();
    Require(file.open(QIODevice::ReadOnly),"axone_snapshot_file_read");
    const auto restoredDocument=QJsonDocument::fromJson(file.readAll()).object();
    ASSERT_EQ(restoredDocument,snapshot);
    auto copy=dynamic_pointer_cast<NAxoneTreeChain>(NmsdkTools::ImportAxoneTreeSnapshot(restoredDocument,storage,environment,ports));
    ASSERT_TRUE(copy);ASSERT_FALSE(copy->GetOwner());copy->Name="RestoredTree";
    UEPtr<UContainer> base=copy;ASSERT_NE(model->AddComponent(base),ForbiddenId);
    model->Reset();RequireInitialized(copy);
    EXPECT_EQ(copy->ResolvePortPath("left"),"Left.Output");EXPECT_TRUE(copy->CheckPropertyAlias("right"));
    EXPECT_DOUBLE_EQ(Zone(copy->GetPortComponent("left"),"Segment1.LTZone")->Threshold.GetData(),.027);
    EXPECT_DOUBLE_EQ(copy->GetComponentL<NAxoneDelay>("Left.Delay1",true)->DelayTime.GetData(),.007);
    EXPECT_EQ(NmsdkTools::IdentifyModel(tree,ports),identity);
    EXPECT_EQ(NmsdkTools::IdentifyModel(copy,ports),identity);
    const auto marker=model->OperationFailureSequence();
    std::vector<double> input,originalOutput,restoredOutput;
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"tick,time,source,original,restored\n";
    for(unsigned tick=0;tick<=model->GetTimeStep()*8/100;++tick){
        model->Calculate();Require(!model->HasOperationFailureSince(marker),"axone_snapshot_calculate");
        input.push_back(Scalar(source->Output.GetData()));originalOutput.push_back(Scalar(tree->Output.GetData()));
        restoredOutput.push_back(Scalar(copy->Output.GetData()));
        EXPECT_DOUBLE_EQ(originalOutput.back(),restoredOutput.back());
        for(const auto* port:{"left","right","trunk"})
            EXPECT_DOUBLE_EQ(Scalar(tree->GetPortComponent(port)->Output.GetData()),Scalar(copy->GetPortComponent(port)->Output.GetData()));
        csv<<tick<<','<<environment->GetTime().GetDoubleTime()<<','<<input.back()<<','<<originalOutput.back()<<','<<restoredOutput.back()<<'\n';
        environment->IncreaseModelTimeByStep();
    }
    QFile trace(QDir(folder).filePath("heterogeneous-tree.csv"));
    Require(trace.open(QIODevice::WriteOnly|QIODevice::NewOnly),"axone_snapshot_trace_exists");
    const auto text=QByteArray::fromStdString(csv.str());Require(trace.write(text)==text.size() && trace.flush(),"axone_snapshot_trace_write");
    EXPECT_EQ(NMSDK::TimeLearner::ExtractAxonePulseEvents(input,.5).size(),1u);
    EXPECT_EQ(NMSDK::TimeLearner::ExtractAxonePulseEvents(originalOutput,.5).size(),1u);
    EXPECT_EQ(NMSDK::TimeLearner::ExtractAxonePulseEvents(restoredOutput,.5).size(),1u);
}

TEST_F(AxoneLifecycle, TreeSnapshotRejectsWrongEnvelopeAndUnknownFields)
{
    auto tree=Take<NAxoneTreeChain>("NAxoneTreeChain");tree->Topology=TreeTopology();Init();
    const auto snapshot=NmsdkTools::ExportAxoneTreeSnapshot(tree);
    auto invalid=snapshot;invalid["kind"]="timelearner_model_archive";
    EXPECT_THROW(NmsdkTools::ImportAxoneTreeSnapshot(invalid,storage,environment),NmsdkTools::ModelArchiveError);
    invalid=snapshot;invalid["unrecognized_field"]=true;
    EXPECT_THROW(NmsdkTools::ImportAxoneTreeSnapshot(invalid,storage,environment),NmsdkTools::ModelArchiveError);
}

TEST_F(AxoneLifecycle, TreeSnapshotRejectsGraphMismatchAfterEnvelopeDigestIsRecomputed)
{
    auto tree=Take<NAxoneTreeChain>("NAxoneTreeChain");tree->Topology=TreeTopology();Init();
    auto snapshot=NmsdkTools::ExportAxoneTreeSnapshot(tree);
    auto graph=snapshot["graph"].toObject();graph["component_class"]="NAxoneChain";snapshot["graph"]=graph;
    snapshot.remove("sha256");snapshot["sha256"]=NmsdkTools::CanonicalModelDataSha256(snapshot);
    const auto before=storage->CalcNumObjects("NAxoneTreeChain");
    EXPECT_THROW(NmsdkTools::ImportAxoneTreeSnapshot(snapshot,storage,environment),NmsdkTools::ModelArchiveError);
    EXPECT_EQ(storage->CalcNumObjects("NAxoneTreeChain"),before);
}

TEST_F(AxoneLifecycle, TreeSnapshotKeepsAxonalAndNeuronSnapshotTypesSeparate)
{
    auto chain=Take<NAxoneChain>("NAxoneChain","Linear");
    auto tree=Take<NAxoneTreeChain>("NAxoneTreeChain");tree->Topology=TreeTopology();Init();
    EXPECT_THROW(NmsdkTools::ExportAxoneTreeSnapshot(chain),NmsdkTools::ModelArchiveError);
    EXPECT_THROW(NmsdkTools::ExportPhysicalGraphForEdit(tree),NmsdkTools::ModelArchiveError);
}

struct TreeCase { std::string id, carrier; unsigned frequency; };

class AxoneTreeEquivalence : public AxoneLifecycle,
                             public ::testing::WithParamInterface<TreeCase> {};

TEST_P(AxoneTreeEquivalence, MatchesExplicitTreeAtEveryNativeTick)
{
    const auto& request = GetParam();
    model->SetGlobalTimeStep(request.frequency);
    auto source = Take<NPulseGenerator>("NPGenerator", "Source");
    source->Frequency = 10.;
    source->PulseLength = .001;
    source->Amplitude = 1.;
    source->Delay = .01;
    source->FrequencyDeviation = 0.;
    auto tree = Take<NAxoneTreeChain>("NAxoneTreeChain", "Tree");
    tree->Topology = TreeTopology(request.carrier);
    auto trunk = Take<NAxoneCommon>(request.carrier, "ExplicitRoot");
    auto left = Take<NAxoneCommon>(request.carrier, "ExplicitLeft");
    auto right = Take<NAxoneCommon>(request.carrier, "ExplicitRight");
    for(const auto& entry : std::vector<std::pair<UEPtr<NAxoneCommon>, int>>{
            {trunk, 2}, {left, 3}, {right, 2}}) {
        if(auto chain = dynamic_pointer_cast<NAxoneChain>(entry.first)) chain->NumSegments = entry.second;
        if(auto chain = dynamic_pointer_cast<NAxoneChainAndDelay>(entry.first)) {
            chain->NumNodes = entry.second;
            chain->InternodeDelayTime = .002;
        }
        Rebuild(entry.first); // Materialize deep taps before wiring them.
    }
    Require(model->CreateLink("Source", "Output", "Tree", "Input"), "tree_source_link");
    Require(model->CreateLink("Source", "Output", "ExplicitRoot", "Input"), "explicit_source_link");
    Require(model->CreateLink("ExplicitRoot.Segment1", "Output", "ExplicitLeft", "Input"), "explicit_left_link");
    Require(model->CreateLink("ExplicitRoot.Segment2", "Output", "ExplicitRight", "Input"), "explicit_right_link");
    Init();
    RequireInitialized(tree);
    RequireInitialized(trunk);
    RequireInitialized(left);
    RequireInitialized(right);
    ASSERT_EQ(tree->GetNumComponents(), 3);
    EXPECT_EQ(tree->GetComponentByIndex(0)->GetName(), "Root");

    std::ostringstream csv;
    csv.imbue(std::locale::classic());
    csv << std::setprecision(17)
        << "time,source,tree_root,explicit_root,tree_left,explicit_left,tree_right,explicit_right\n";
    unsigned actualInputs = 0, actualLeft = 0;
    bool previousInput = false, previousLeft = false;
    bool complete = false;
    std::exception_ptr failure;
    const auto marker = model->OperationFailureSequence();
    try {
        for(unsigned tick = 0; tick <= request.frequency * 11 / 20; ++tick) {
            if(tick == request.frequency / 2) source->Frequency = 0.;
            model->Calculate();
            Require(!model->HasOperationFailureSince(marker), "tree_equivalence_calculate");
            const double time = environment->GetTime().GetDoubleTime();
            const double input = Scalar(source->Output.GetData());
            const double rootValue = Scalar(tree->GetPortComponent("trunk")->Output.GetData());
            const double leftValue = Scalar(tree->GetPortComponent("left")->Output.GetData());
            const double rightValue = Scalar(tree->GetPortComponent("right")->Output.GetData());
            const double expectedRoot = Scalar(trunk->Output.GetData());
            const double expectedLeft = Scalar(left->Output.GetData());
            const double expectedRight = Scalar(right->Output.GetData());
            if(input > .5 && !previousInput) ++actualInputs;
            if(leftValue > .5 && !previousLeft) ++actualLeft;
            previousInput = input > .5;
            previousLeft = leftValue > .5;
            csv << time << ',' << input << ',' << rootValue << ',' << expectedRoot << ','
                << leftValue << ',' << expectedLeft << ',' << rightValue << ',' << expectedRight << '\n';
            EXPECT_DOUBLE_EQ(rootValue, expectedRoot) << tick;
            EXPECT_DOUBLE_EQ(leftValue, expectedLeft) << tick;
            EXPECT_DOUBLE_EQ(rightValue, expectedRight) << tick;
            EXPECT_DOUBLE_EQ(Scalar(tree->Output.GetData()), leftValue) << tick;
            environment->IncreaseModelTimeByStep();
        }
        complete = true;
    } catch(...) { failure = std::current_exception(); }
    const std::string stem = "tree_equivalence_" + request.id;
    WriteArtifact(stem, ".csv", QByteArray::fromStdString(csv.str()));
    WriteArtifact(stem, ".json", QJsonDocument(QJsonObject{
        {"kind", "axone_tree_equivalence_observation"}, {"schema_version", 1},
        {"frequency_hz", int(request.frequency)}, {"complete", complete},
        {"carrier", QString::fromStdString(request.carrier)}, {"input_count", int(actualInputs)},
        {"left_count", int(actualLeft)}, {"scheduler", "root_UNet"}, {"training", false},
        {"topology", QString::fromStdString(tree->Topology.GetData())}
    }).toJson(QJsonDocument::Indented));
    if(failure) std::rethrow_exception(failure);
    EXPECT_TRUE(complete);
    EXPECT_EQ(actualInputs, 5u);
    EXPECT_EQ(actualLeft, actualInputs); // Trace equality must not pass on two silent graphs.
}

std::vector<TreeCase> TreeCases()
{
    std::vector<TreeCase> result;
    for(unsigned frequency : {2000u, 20000u, 40000u})
        for(const std::string carrier : {"NAxoneChain", "NAxoneChainAndDelay"})
            result.push_back({carrier + "_f" + std::to_string(frequency), carrier, frequency});
    return result;
}

INSTANTIATE_TEST_SUITE_P(P1Tree, AxoneTreeEquivalence, ::testing::ValuesIn(TreeCases()),
    [](const ::testing::TestParamInfo<TreeCase>& value) { return value.param.id; });

} // namespace
