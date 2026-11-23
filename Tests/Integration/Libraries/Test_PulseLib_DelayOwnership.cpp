#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NDatasetMatrix.h"
#include "TimeLearner/StorageProfiles.h"
#include "../Support/ConsoleLikeInit.h"
#include <cmath>
#include <limits>
#include <stdexcept>
#include <type_traits>

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
    Scope()
    {
        const auto& engine = NmsdkTests::InitEngineForPulseLibTests();
        storage = engine.storage;
        environment = engine.environment;
        environment->DestroyModel();
        environment->SetUseIndTimeStepFlag(false);
        Require(environment->CreateModel("NModel"), "delay_fixture_model");
        model = dynamic_pointer_cast<UNet>(environment->GetModel());
        Require(bool(model), "delay_fixture_root");
        model->SetGlobalTimeStep(Frequency);
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
        owner->SetGlobalTimeStep(Frequency);
        UEPtr<UContainer> component = owner;
        Require(model->AddComponent(component) != ForbiddenId, "delay_fixture_attach");
        return owner;
    }
};

template<class Owner> UEPtr<Owner> Legacy(Scope& scope, bool automatic)
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
    owner->Delay = 3.;
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
