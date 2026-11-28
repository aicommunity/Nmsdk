#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NDatasetMatrix.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
constexpr unsigned Frequency = 2000;

void Require(bool condition, const char* reason)
{
    if (!condition) throw std::runtime_error(reason);
}

struct Scope {
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UNet> model;
    unsigned frequency;
    explicit Scope(unsigned frequency = Frequency): frequency(frequency)
    {
        const auto& engine = NmsdkTests::InitEngineForPulseLibTests();
        storage = engine.storage;
        environment = engine.environment;
        environment->DestroyModel();
        environment->SetUseIndTimeStepFlag(false);
        Require(environment->CreateModel("NModel"), "delay_fixture_model");
        model = dynamic_pointer_cast<UNet>(environment->GetModel());
        Require(bool(model), "delay_fixture_root");
        model->SetGlobalTimeStep(frequency);
    }
    ~Scope()
    {
        if (model) model->BreakLinks();
        environment->DestroyModel();
    }
    template<class Owner> UEPtr<Owner> Take()
    {
        constexpr bool branch = std::is_same_v<Owner, NNeuronTimeLearnerBranch>;
        auto owner = dynamic_pointer_cast<Owner>(storage->TakeObject(
            branch ? "NNeuronTimeLearnerBranch" : "NNeuronTimeLearner"));
        Require(bool(owner), "delay_fixture_owner");
        owner->Name = "Learner";
        owner->ControllerVersion = 1;
        owner->CalculateMode = 1;
        owner->StructureBuildMode = 1;
        owner->EnablePostTrainTuning = false;
        owner->AutoCalibrateFixedLTZThreshold = false;
        owner->IsNeedToTrain = false;
        owner->SetGlobalTimeStep(frequency);
        UEPtr<UContainer> component = owner;
        Require(model->AddComponent(component) != ForbiddenId, "delay_fixture_attach");
        return owner;
    }
};

template<class Owner> UEPtr<Owner> Legacy(Scope& scope, bool automatic, double initialDelay = 3.)
{
    constexpr bool branch = std::is_same_v<Owner, NNeuronTimeLearnerBranch>;
    auto owner = scope.Take<Owner>();
    StorageProfileSpec profile;
    profile.name = branch ? "DelayLegacyBranch" : "DelayLegacyClassic";
    profile.frequencyHz = Frequency;
    profile.neuronBaseClass = "NSPNeuronGen";
    const auto registered = RegisterStorageProfile(scope.storage, scope.environment, profile);
    owner->NeuronClassName = registered.neuronClass;
    owner->NumInputDendrite = 2;
    owner->NormalizationMode = 0;
    owner->DendriteLength = std::vector<int>{2, branch ? 1 : 3};
    owner->NumSynapse = std::vector<int>{1, 1};
    MDMatrix<double> pattern;
    pattern.Resize(2, 1);
    pattern(0, 0) = .01;
    pattern(1, 0) = .03;
    owner->InputPattern = pattern;
    owner->AutoScaleIterationGap = automatic;
    owner->Delay = initialDelay;
    owner->IsNeedToTrain = true;
    scope.environment->ModelInit();
    scope.model->Reset();
    owner->IsNeedToTrain = false;
    return owner;
}

template<class Owner> UEPtr<NDatasetMatrix> Dataset(UEPtr<Owner> owner)
{
    auto dataset = owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix", true);
    Require(bool(dataset), "delay_fixture_dataset");
    return dataset;
}

template<class Owner> void LegacyCandidate()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false);
    auto dataset = Dataset(owner);
    ASSERT_DOUBLE_EQ(dataset->Delay.GetData(), 3.);
    const auto time = scope.environment->GetTime().GetDoubleTime();
    EXPECT_NO_THROW(owner->Delay.SetData(5.));
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), 5.);
    // No second assignment, Build, Reset or tick may repair a stale setter.
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(), time);
}

template<class Owner> void LegacyFloor()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false);
    auto dataset = Dataset(owner);
    ASSERT_DOUBLE_EQ(dataset->Delay.GetData(), 3.);
    EXPECT_NO_THROW(owner->Delay.SetData(.2));
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), .2);
    // Preserve the existing complete-observation floor, rather than allowing .2s.
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), 1.55);
}

template<class Owner> void AutomaticGap()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, true);
    auto dataset = Dataset(owner);
    ASSERT_DOUBLE_EQ(dataset->Delay.GetData(), 1.55);
    EXPECT_NO_THROW(owner->Delay.SetData(5.));
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), 1.55);
}

template<class Owner> void RejectNonFinite()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false);
    auto dataset = Dataset(owner);
    const double before = owner->Delay.GetData();
    const double effective = dataset->Delay.GetData();
    for (const double value : {std::numeric_limits<double>::quiet_NaN(),
                              std::numeric_limits<double>::infinity(),
                              -std::numeric_limits<double>::infinity()}) {
        EXPECT_THROW(owner->Delay.SetData(value), UIProperty::EPropertySetterFail);
        EXPECT_DOUBLE_EQ(owner->Delay.GetData(), before);
        EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), effective);
    }
}

template<class Owner> void ColdConfiguredDelay()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false, 5.);
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(Dataset(owner)->Delay.GetData(), 5.);
}

template<class Owner> void NonPositiveLegacyFallback()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false);
    for (const double value : {0., -1.}) {
        EXPECT_NO_THROW(owner->Delay.SetData(value));
        EXPECT_DOUBLE_EQ(owner->Delay.GetData(), value);
        EXPECT_DOUBLE_EQ(Dataset(owner)->Delay.GetData(), 1.55);
    }
}

template<class Owner> void ConnectedDatasetOwnership()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false);
    auto dataset = Dataset(owner);
    owner->IterationGap = 5.;
    // UProperty's generic AttachTo returns false. Scalar connections are
    // installed through the same SetPointer contract used by Rdk connectors.
    ASSERT_TRUE(dataset->Delay.SetPointer(0, &owner->IterationGap));
    ASSERT_TRUE(dataset->Delay.IsConnected());
    EXPECT_NO_THROW(owner->Delay.SetData(5.));
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(owner->IterationGap.GetData(), 5.);
    EXPECT_THROW(owner->Delay.SetData(6.), UIProperty::EPropertySetterFail);
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), 5.);
    EXPECT_DOUBLE_EQ(owner->IterationGap.GetData(), 5.);
    EXPECT_TRUE(dataset->Delay.IsConnected());
    owner->IterationGap = 6.;
    ASSERT_DOUBLE_EQ(dataset->Delay.GetData(), 6.);
    EXPECT_NO_THROW(owner->Delay.SetData(6.));
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), 6.);
    EXPECT_THROW(owner->Delay.SetData(7.), UIProperty::EPropertySetterFail);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), 6.);
    EXPECT_DOUBLE_EQ(owner->IterationGap.GetData(), 6.);
    EXPECT_TRUE(dataset->Delay.IsConnected());
    dataset->Delay.DetachFrom();
}

template<class Owner> void QueuedProbeOwnership()
{
    Scope scope;
    auto owner = Legacy<Owner>(scope, false);
    auto dataset = Dataset(owner);
    const auto time = scope.environment->GetTime().GetDoubleTime();
    const double before = owner->Delay.GetData();
    const double effective = dataset->Delay.GetData();
    NativeProbeRequest request;
    request.specification.runId = "delay-probe-ownership";
    request.specification.trialId = "queued-before-first-tick";
    owner->QueueNativeProbe(std::move(request));
    ASSERT_TRUE(owner->NativeProbeOwnsControl());
    ASSERT_EQ(owner->NativeProbeState(), NativeProbeStatus::Queued);
    EXPECT_THROW(owner->Delay.SetData(before + 2.), UIProperty::EPropertySetterFail);
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), before);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), effective);
    EXPECT_NO_THROW(owner->Delay.SetData(before));
    EXPECT_EQ(owner->NativeProbeState(), NativeProbeStatus::Queued);
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(), time);
    owner->CancelNativeProbe("delay-fixture-finished-before-stimulus");
}

template<class Owner> void NativeOwnership()
{
    constexpr bool branch = std::is_same_v<Owner, NNeuronTimeLearnerBranch>;
    Scope scope;
    auto owner = scope.Take<Owner>();
    StorageProfileSpec profile;
    profile.name = branch ? "DelayNativeBranch" : "DelayNativeClassic";
    profile.frequencyHz = Frequency;
    profile.neuronBaseClass = "NSPNeuronGen";
    const auto registered = RegisterStorageProfile(scope.storage, scope.environment, profile);
    NativeModelSpec specification;
    specification.branch = branch;
    specification.frequencyHz = Frequency;
    specification.neuronClass = registered.neuronClass;
    specification.normalization = Normalization::SynapseCount;
    specification.editPolicy.normalization = specification.normalization;
    specification.editPolicy.maximumCableLength = 8;
    specification.initialIsi = {.01, .03};
    specification.inputs = {{2, 1, 86e6}, {branch ? 1 : 3, 1, 123e6}};
    const auto built = owner->ConstructNativeModel(specification);
    ASSERT_EQ(built.status, NativeModelBuildStatus::Constructed) << built.reason;
    scope.model->Init();
    scope.model->Reset();
    auto dataset = Dataset(owner);
    const auto parameters = owner->ReadNativeParameters();
    const double before = owner->Delay.GetData();
    const double effective = dataset->Delay.GetData();
    const auto time = scope.environment->GetTime().GetDoubleTime();
    EXPECT_THROW(owner->Delay.SetData(before + 2.), UIProperty::EPropertySetterFail);
    EXPECT_DOUBLE_EQ(owner->Delay.GetData(), before);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), effective);
    EXPECT_NO_THROW(owner->Delay.SetData(before));
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), effective);
    EXPECT_EQ(owner->ReadNativeParameters(), parameters);
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(), time);
}

void WriteActiveEvidence(const std::string& name, const QJsonObject& value)
{
    if (const char* directory = std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
        const auto folder = QString::fromLocal8Bit(directory);
        Require(QDir().mkpath(folder), "active_delay_output_directory");
        QFile file(QDir(folder).filePath(QString::fromStdString(name)+".json"));
        Require(file.open(QIODevice::WriteOnly | QIODevice::NewOnly), "active_delay_output_exists");
        const auto bytes = QJsonDocument(value).toJson();
        Require(file.write(bytes) == bytes.size() && file.flush(), "active_delay_output_write");
    }
}

enum class ProbeDelayMode { GuardDuringCapture, ConnectedSufficient, ConnectedTooShort };

// The trace is produced by the real Environment/scheduler and native probe.
// No test copy of SetDelay, recorder, or model calculation is used.
template<class Owner> void ActiveProbeOwnership(unsigned frequency, unsigned inputs, ProbeDelayMode mode)
{
    constexpr bool branch = std::is_same_v<Owner, NNeuronTimeLearnerBranch>;
    Scope scope(frequency);
    auto owner = scope.Take<Owner>();
    const std::string name = std::string(branch ? "Branch" : "Classic")+"_active_delay_"+
        std::to_string(frequency)+"_M"+std::to_string(inputs)+"_"+std::to_string(int(mode));
    StorageProfileSpec profile;
    profile.name = name;
    profile.frequencyHz = frequency;
    profile.neuronBaseClass = "NSPNeuronGen";
    const auto registered = RegisterStorageProfile(scope.storage, scope.environment, profile);
    NativeModelSpec specification;
    specification.branch = branch;
    specification.frequencyHz = frequency;
    specification.neuronClass = registered.neuronClass;
    specification.normalization = Normalization::SynapseCount;
    specification.editPolicy.normalization = specification.normalization;
    specification.editPolicy.maximumCableLength = 8;
    for (unsigned i = 0; i < inputs; ++i) {
        specification.initialIsi.push_back(i ? .03 : .01);
        specification.inputs.push_back({int(inputs-i), 1, 86e6});
    }
    const auto built = owner->ConstructNativeModel(specification);
    ASSERT_EQ(built.status, NativeModelBuildStatus::Constructed) << built.reason;
    scope.model->Init();
    scope.model->Reset();
    auto dataset = Dataset(owner);
    auto neuron = owner->template GetComponentL<NPulseNeuron>("Neuron", true);
    auto generator = dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1", true);
    ASSERT_TRUE(neuron);
    ASSERT_TRUE(generator);
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output, "burst"}};
    const auto revision = [&] {
        const auto identity = NmsdkTools::IdentifyModel(neuron, ports);
        Require(identity["valid"].toBool(), "active_delay_model_identity");
        return identity["sha256"].toString().toStdString();
    };
    const auto originalRevision = revision();
    const auto parameters = owner->ReadNativeParameters();
    const double configured = owner->Delay.GetData();
    constexpr double duration = .2;
    if (mode != ProbeDelayMode::GuardDuringCapture) {
        owner->IterationGap = mode == ProbeDelayMode::ConnectedSufficient ? 5. : .05;
        ASSERT_TRUE(dataset->Delay.SetPointer(0, &owner->IterationGap));
        ASSERT_TRUE(dataset->Delay.IsConnected());
    }
    const double effective = dataset->Delay.GetData();
    const auto sources = dataset->Delay.GetDataSources();
    std::vector<std::vector<NativeProbeSample>> traces;
    QJsonArray packets;
    const unsigned attempts = mode == ProbeDelayMode::GuardDuringCapture ? 2 : 1;
    for (unsigned attempt = 0; attempt < attempts; ++attempt) {
        traces.emplace_back();
        bool changedAttempted = false;
        NativeProbeRequest request;
        request.routing = branch ? ProbeRouting::BranchSoloBurst : ProbeRouting::ClassicBurst;
        request.activeInput = 0;
        request.inputId = "input0";
        request.protocolRevision = "active-delay-ownership-v1";
        request.baseModelRevision = originalRevision;
        request.expectedInputIsi = specification.initialIsi;
        request.readModelRevision = revision;
        auto& s = request.specification;
        s.runId = name;
        s.trialId = name+"/trial-"+std::to_string(attempt);
        s.sampleId = "control";
        QJsonArray pattern;
        for (const auto gap : specification.initialIsi) pattern.append(gap);
        s.patternHash = NmsdkTools::CanonicalModelDataSha256(pattern).toStdString();
        s.end = duration;
        s.maximumSampleGap = 1./frequency;
        s.maximumSamples = std::size_t((duration+.01)*frequency);
        for (unsigned i = 0; i < inputs; ++i) s.expectedStimulusIds.push_back("pulse"+std::to_string(i));
        s.windows = {{"input0", 0, .01, .15, "pulse0"}};
        request.onSample = [&](const NativeProbeSample& sample) {
            traces.back().push_back(sample);
            if (attempt != 1 || changedAttempted || traces.back().size() < frequency/50) return;
            ASSERT_EQ(owner->NativeProbeState(), NativeProbeStatus::Running);
            ASSERT_TRUE(owner->NativeProbeOwnsControl());
            const auto clock = scope.environment->GetTime().GetDoubleTime();
            const auto currentRevision = revision();
            const double during = dataset->Delay.GetData();
            EXPECT_THROW(owner->Delay.SetData(configured+2.), UIProperty::EPropertySetterFail);
            EXPECT_NO_THROW(owner->Delay.SetData(configured));
            EXPECT_DOUBLE_EQ(owner->Delay.GetData(), configured);
            EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), during);
            EXPECT_EQ(owner->ReadNativeParameters(), parameters);
            EXPECT_EQ(revision(), currentRevision);
            EXPECT_EQ(owner->NativeProbeState(), NativeProbeStatus::Running);
            EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(), clock);
            changedAttempted = true;
        };
        owner->QueueNativeProbe(std::move(request));
        for (unsigned ticks = 0; owner->NativeProbeState() == NativeProbeStatus::Queued ||
                                owner->NativeProbeState() == NativeProbeStatus::Running; ++ticks) {
            ASSERT_LT(ticks, unsigned((duration+.02)*frequency));
            scope.model->Calculate();
            scope.environment->IncreaseModelTimeByStep();
        }
        const auto result = owner->TakeNativeProbeResult();
        ASSERT_TRUE(result);
        packets.append(EncodeNativeProbeEvidence(*result));
        if (mode == ProbeDelayMode::ConnectedTooShort) {
            EXPECT_EQ(result->status, NativeProbeStatus::Rejected);
            EXPECT_TRUE(!result->observation || !result->observation->complete);
            EXPECT_TRUE(traces.back().empty());
        } else {
            ASSERT_EQ(result->status, NativeProbeStatus::Completed);
            ASSERT_TRUE(result->observation);
            EXPECT_TRUE(result->observation->complete);
            EXPECT_GE(traces.back().size(), unsigned(duration*frequency));
            if (attempt == 1) EXPECT_TRUE(changedAttempted);
        }
        EXPECT_DOUBLE_EQ(owner->Delay.GetData(), configured);
        EXPECT_DOUBLE_EQ(dataset->Delay.GetData(), effective);
        EXPECT_EQ(dataset->Delay.GetDataSources(), sources);
        EXPECT_EQ(owner->ReadNativeParameters(), parameters);
        EXPECT_EQ(revision(), originalRevision);
    }
    if (mode == ProbeDelayMode::GuardDuringCapture) {
        ASSERT_EQ(traces[0].size(), traces[1].size());
        unsigned stimuli = 0;
        for (std::size_t i = 0; i < traces[0].size(); ++i) {
            const auto& a = traces[0][i];
            const auto& b = traces[1][i];
            EXPECT_NEAR(a.time-traces[0][0].time, b.time-traces[1][0].time, 1e-12);
            EXPECT_DOUBLE_EQ(a.stimulus, b.stimulus);
            ASSERT_EQ(a.potentials.size(), b.potentials.size());
            for (std::size_t channel = 0; channel < a.potentials.size(); ++channel)
                EXPECT_NEAR(a.potentials[channel], b.potentials[channel], 1e-12);
            ASSERT_EQ(a.newStimuli.size(), b.newStimuli.size());
            stimuli += unsigned(a.newStimuli.size());
            for (std::size_t event = 0; event < a.newStimuli.size(); ++event) {
                EXPECT_EQ(a.newStimuli[event].id, b.newStimuli[event].id);
                EXPECT_NEAR(a.newStimuli[event].time-traces[0][0].time,
                            b.newStimuli[event].time-traces[1][0].time, 1e-12);
            }
        }
        EXPECT_EQ(stimuli, inputs);
    } else {
        EXPECT_DOUBLE_EQ(owner->IterationGap.GetData(), effective);
        EXPECT_TRUE(dataset->Delay.IsConnected());
        dataset->Delay.DetachFrom();
    }
    QJsonArray rawTraces;
    for (const auto& trace : traces) {
        QJsonArray frames;
        for (const auto& sample : trace) {
            QJsonArray potentials, events;
            for (double value : sample.potentials) potentials.append(value);
            for (const auto& event : sample.newStimuli)
                events.append(QJsonObject{{"id", QString::fromStdString(event.id)}, {"time", event.time}});
            frames.append(QJsonObject{{"time", sample.time}, {"stimulus", sample.stimulus},
                {"soma", potentials}, {"actual_stimuli", events}});
        }
        rawTraces.append(frames);
    }
    WriteActiveEvidence(name, {{"kind", "active_native_delay_ownership"}, {"schema_version", 1},
        {"frequency_hz", int(frequency)}, {"input_count", int(inputs)}, {"mode", int(mode)},
        {"configured_delay", configured}, {"effective_original_delay", effective}, {"packets", packets}, {"traces", rawTraces},
        {"waveforms_compared", mode == ProbeDelayMode::GuardDuringCapture},
        {"training_or_convergence_claimed", false}, {"scientific_verdict", QJsonValue(QJsonValue::Null)}});
}
}

TEST(TimeLearnerDelayOwnership, ClassicLegacyCandidateAppliedImmediately) { LegacyCandidate<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchLegacyCandidateAppliedImmediately) { LegacyCandidate<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicLegacyCandidateRetainsObservationFloor) { LegacyFloor<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchLegacyCandidateRetainsObservationFloor) { LegacyFloor<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicAutomaticGapIgnoresConfiguredFloor) { AutomaticGap<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchAutomaticGapIgnoresConfiguredFloor) { AutomaticGap<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicRejectsNonFiniteDelay) { RejectNonFinite<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchRejectsNonFiniteDelay) { RejectNonFinite<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicNativeOwnedMutationRejected) { NativeOwnership<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchNativeOwnedMutationRejected) { NativeOwnership<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicColdConfiguredDelay) { ColdConfiguredDelay<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchColdConfiguredDelay) { ColdConfiguredDelay<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicNonPositiveLegacyFallback) { NonPositiveLegacyFallback<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchNonPositiveLegacyFallback) { NonPositiveLegacyFallback<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicConnectedDatasetOwnership) { ConnectedDatasetOwnership<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchConnectedDatasetOwnership) { ConnectedDatasetOwnership<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicQueuedProbeOwnership) { QueuedProbeOwnership<NNeuronTimeLearner>(); }
TEST(TimeLearnerDelayOwnership, BranchQueuedProbeOwnership) { QueuedProbeOwnership<NNeuronTimeLearnerBranch>(); }
TEST(TimeLearnerDelayOwnership, ClassicActiveProbe2000M2PreservesActualTrace) { ActiveProbeOwnership<NNeuronTimeLearner>(2000, 2, ProbeDelayMode::GuardDuringCapture); }
TEST(TimeLearnerDelayOwnership, BranchActiveProbe2000M2PreservesActualTrace) { ActiveProbeOwnership<NNeuronTimeLearnerBranch>(2000, 2, ProbeDelayMode::GuardDuringCapture); }
TEST(TimeLearnerDelayOwnership, ClassicActiveProbe20000M4PreservesActualTrace) { ActiveProbeOwnership<NNeuronTimeLearner>(20000, 4, ProbeDelayMode::GuardDuringCapture); }
TEST(TimeLearnerDelayOwnership, BranchActiveProbe20000M4PreservesActualTrace) { ActiveProbeOwnership<NNeuronTimeLearnerBranch>(20000, 4, ProbeDelayMode::GuardDuringCapture); }
TEST(TimeLearnerDelayOwnership, ClassicConnectedProbeSufficientDelay) { ActiveProbeOwnership<NNeuronTimeLearner>(2000, 2, ProbeDelayMode::ConnectedSufficient); }
TEST(TimeLearnerDelayOwnership, BranchConnectedProbeSufficientDelay) { ActiveProbeOwnership<NNeuronTimeLearnerBranch>(2000, 2, ProbeDelayMode::ConnectedSufficient); }
TEST(TimeLearnerDelayOwnership, ClassicConnectedProbeTooShortCannotComplete) { ActiveProbeOwnership<NNeuronTimeLearner>(2000, 2, ProbeDelayMode::ConnectedTooShort); }
TEST(TimeLearnerDelayOwnership, BranchConnectedProbeTooShortCannotComplete) { ActiveProbeOwnership<NNeuronTimeLearnerBranch>(2000, 2, ProbeDelayMode::ConnectedTooShort); }
