#include <gtest/gtest.h>

#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../Support/ConsoleLikeInit.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <string>

using namespace RDK;

class TimeLearnerResistanceTest : public ::testing::Test
{
protected:
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UContainer> model;

    void SetUp() override
    {
        const auto& core = NmsdkTests::InitEngineForPulseLibTests();
        storage = core.storage;
        environment = core.environment;
        ASSERT_TRUE(storage);
        ASSERT_TRUE(environment);
        ASSERT_TRUE(storage->CheckClass("NNeuronTimeLearner"));
        ASSERT_TRUE(storage->CheckClass("NNeuronTimeLearnerBranch"));
        ASSERT_TRUE(environment->CreateModel("NModel"));
        model = environment->GetModel();
        ASSERT_TRUE(model);
    }

    UEPtr<NMSDK::NNeuronTimeLearner> CreateLearner(const std::string& name)
    {
        UEPtr<UComponent> base = storage->TakeObject("NNeuronTimeLearner");
        EXPECT_TRUE(base);
        if (!base)
            return UEPtr<NMSDK::NNeuronTimeLearner>();

        UEPtr<UContainer> container = dynamic_pointer_cast<UContainer>(base);
        EXPECT_TRUE(container);
        if (!container)
            return UEPtr<NMSDK::NNeuronTimeLearner>();

        container->Name = name;
        container->Default();
        UEPtr<NMSDK::NNeuronTimeLearner> learner =
            dynamic_pointer_cast<NMSDK::NNeuronTimeLearner>(container);
        EXPECT_TRUE(learner);
        if (!learner)
            return learner;

        EXPECT_TRUE(model->Default());
        learner->StructureBuildMode = 1;
        learner->NumInputDendrite = 3;
        learner->MaxDendriteLength = 10;
        learner->IsNeedToTrain = true;
        learner->CalculateMode = 1;
        learner->ExperimentMode = false;

        MDMatrix<double> pattern;
        pattern.Assign(3, 1, 0.0);
        pattern(0, 0) = 0.01;
        pattern(1, 0) = 0.02;
        pattern(2, 0) = 0.03;
        learner->InputPattern = pattern;
        EXPECT_NE(model->AddComponent(container), ForbiddenId);
        return learner;
    }

    UEPtr<NMSDK::NNeuronTimeLearnerBranch> CreateBranchLearner(const std::string& name)
    {
        UEPtr<UComponent> base = storage->TakeObject("NNeuronTimeLearnerBranch");
        EXPECT_TRUE(base);
        if (!base)
            return UEPtr<NMSDK::NNeuronTimeLearnerBranch>();

        UEPtr<UContainer> container = dynamic_pointer_cast<UContainer>(base);
        EXPECT_TRUE(container);
        if (!container)
            return UEPtr<NMSDK::NNeuronTimeLearnerBranch>();

        container->Name = name;
        container->Default();
        auto learner = dynamic_pointer_cast<NMSDK::NNeuronTimeLearnerBranch>(container);
        EXPECT_TRUE(learner);
        if (!learner)
            return learner;

        EXPECT_TRUE(model->Default());
        learner->StructureBuildMode = 1;
        learner->NumInputDendrite = 3;
        learner->MaxDendriteLength = 10;
        learner->IsNeedToTrain = true;
        learner->CalculateMode = 1;
        learner->ExperimentMode = false;

        MDMatrix<double> pattern;
        pattern.Assign(3, 1, 0.0);
        pattern(0, 0) = 0.01;
        pattern(1, 0) = 0.02;
        pattern(2, 0) = 0.03;
        learner->InputPattern = pattern;
        EXPECT_NE(model->AddComponent(container), ForbiddenId);
        return learner;
    }

    template <class TLearner>
    bool BuildAndReset(const UEPtr<TLearner>& learner)
    {
        if (!learner || !model)
            return false;
        const int configuredMode = learner->NormalizationMode.GetData();
        if (!learner->Build())
            return false;
        EXPECT_EQ(learner->NormalizationMode.GetData(), configuredMode)
            << "learner Build changed NormalizationMode";
        if (!model->Build())
            return false;
        EXPECT_EQ(learner->NormalizationMode.GetData(), configuredMode)
            << "model Build changed NormalizationMode";
        // The fixture adds the learner after creating the model. Initialize
        // the completed component tree before requesting its cold reset.
        model->Init();
        learner->ResetToUntrainedState = true;
        if (!model->Reset())
            return false;
        EXPECT_EQ(learner->NormalizationMode.GetData(), configuredMode)
            << "model Reset changed NormalizationMode";
        EXPECT_FALSE(learner->ResetToUntrainedState.GetData())
            << "model Reset did not consume ResetToUntrainedState";
        return true;
    }
};

class BranchSegmentOrderHarness : public NMSDK::NNeuronTimeLearnerBranch
{
public:
    void SetOrderState(
        const std::vector<int>& lengths,
        int active,
        int max_length,
        bool active_peak_valid = true,
        bool exhausted_amp_collapse = false)
    {
        NumInputDendrite = static_cast<int>(lengths.size());
        MaxDendriteLength = max_length;
        DendriteLength = lengths;
        ActiveDendrite = active;
        ActivePulseIndex = active;
        SyncTolerance = 0.02;
        EstDelayPerSeg = 0.006666666666666667;
        DendStatus.assign(lengths.size(), 0);
        SomaPeakValid.assign(lengths.size(), false);
        SomaPeakValid.at(static_cast<size_t>(active)) = active_peak_valid;
        PeakRel.assign(lengths.size(), 0.0);
        PeakRel.at(static_cast<size_t>(active)) = 0.48;
        PulseSynced.assign(lengths.size(), false);
        PulseSynced.back() = true;
        StoredPeakRel.assign(lengths.size(), 0.0);
        StoredPeakRel.back() = 0.4945;
        ExpectedPulseRelTimes.assign(lengths.size(), 0.0);
        ExpectedPulseRelTimes.at(static_cast<size_t>(active)) = 0.08;
        DelayFromPulse.assign(lengths.size(), 0.0);
        DelayFromPulse.at(static_cast<size_t>(active)) = 0.41316;
        PrevPeakRel.assign(lengths.size(), 0.0);
        DendLastAbsDt.assign(lengths.size(), 0.0);
        DendBestEffortSynced.assign(lengths.size(), false);
        Dissynchronization.assign(lengths.size(), 0.0);
        PrevDissynchronization.assign(lengths.size(), 0.0);
        InitialSomaPotential.assign(lengths.size(), 0.0);
        MaxIterSomaAmp.assign(lengths.size(), 0.0);
        NumSynapse.assign(lengths.size(), 1);
        if (exhausted_amp_collapse)
        {
            auto initial_soma = InitialSomaPotential.GetData();
            auto num_synapses = NumSynapse.GetData();
            initial_soma.at(static_cast<size_t>(active)) = 0.01;
            MaxIterSomaAmp.at(static_cast<size_t>(active)) = 1.0e-11;
            num_synapses.at(static_cast<size_t>(active)) = 128;
            InitialSomaPotential = initial_soma;
            NumSynapse = num_synapses;
        }
        CanChangeDendLength = true;
        TrainingPhase = 0;
        TrainingFailureReason = 0;
    }

    void SetInvalidPeakNoActionState(double tip_r, bool model_ok)
    {
        SetOrderState({1, 10, 6, 1}, 1, 100, false);
        NormalizationMode = 1;
        ResistanceMin = 1.0e6;
        ResistanceMax = 1.0e8;
        TipSynapseResistance = {86.0e6, tip_r, 1.0e6, 86.0e6};
        InitialSomaPotential[1] = 0.015828572406203167;
        MaxIterSomaAmp[1] = 1.7046206635118466e-7;
        NumSynapse[1] = 1;
        IsNeedToTrain = true; // this callback clears the runtime sync vectors
        ActiveDendrite = 1;
        ActivePulseIndex = 1;
        DendStatus.assign(4, 0);
        EstDelayPerSeg = model_ok
            ? (0.4945 - 0.08) / 9.0
            : 0.006666666666666667;
        // Reassert the runtime reference after property setters: the test is
        // exercising an already committed Branch anchor, not anchor bootstrap.
        PulseSynced.assign(4, false);
        PulseSynced.back() = true;
        StoredPeakRel.assign(4, 0.0);
        StoredPeakRel.back() = 0.4945;
        HasPrevPeakSnapshot = true;
        InvalidPeakNoActionCount.assign(4, 0);
    }

    int InvalidPeakNoActionCountAt(int pulse) const
    {
        return InvalidPeakNoActionCount.at(static_cast<size_t>(pulse));
    }

    bool IsBestEffortSynced(int pulse) const
    {
        return DendBestEffortSynced.at(static_cast<size_t>(pulse));
    }

    double InvalidPeakModelTimingError(int pulse) const
    {
        const size_t index = static_cast<size_t>(pulse);
        return MeanStoredPeakRel(pulse) - ExpectedPulseRelTimes.at(index) - DelayLenOf(pulse);
    }

    double CurrentModelTimingError(int pulse) const
    {
        const size_t index = static_cast<size_t>(pulse);
        const double expected = ExpectedPulseRelTimes.at(index);
        const double measured_delay = DelayFromPulse.at(index);
        return MeanStoredPeakRel(pulse) - expected
            - DelayUseOf(pulse, expected, measured_delay);
    }

    void SetDissynchronization(int pulse, double value)
    {
        Dissynchronization.at(static_cast<size_t>(pulse)) = value;
    }

    double DissynchronizationAt(int pulse) const
    {
        return Dissynchronization.at(static_cast<size_t>(pulse));
    }

    double TipResistance(int pulse) const
    {
        return TipSynapseResistance.GetData().at(static_cast<size_t>(pulse));
    }

    double MinimumResistance() const
    {
        return ResistanceMin.GetData();
    }

    bool IsPulsePeakValid(int pulse) const
    {
        return SomaPeakValid.at(static_cast<size_t>(pulse));
    }

    bool IsReferencePulseSynced() const
    {
        return PulseSynced.back();
    }

    bool DecideLength(int pulse)
    {
        return ChangeDendriteStatus(pulse);
    }

    int LengthStatus(int pulse) const
    {
        return DendStatus.at(static_cast<size_t>(pulse));
    }

    int FailureReason() const
    {
        return TrainingFailureReason.GetData();
    }

    int Phase() const
    {
        return TrainingPhase.GetData();
    }
};

class ClassicDelayRoundoffHarness : public NMSDK::NNeuronTimeLearner
{
public:
    void SetDelayState(double measured_delay)
    {
        NumInputDendrite = 4;
        MaxDendriteLength = 100;
        IterationGap = 1.5;
        SyncTolerance = 0.02;
        EstDelayPerSeg = 0.005;
        NormalizationMode = 0;
        DendriteLength = {17, 17, 9, 1};
        ActiveDendrite = 2;
        HasPrevPeakSnapshot = true;
        FirstImpulseTime = 12.2565;
        ExpectedPulseRelTimes = {0.0, 0.08, 0.24, 0.48};
        MDMatrix<double> input_pattern;
        input_pattern.Assign(4, 1, 0.0);
        for(int i = 0; i < 4; ++i)
            input_pattern(i, 0) = ExpectedPulseRelTimes[static_cast<size_t>(i)];
        InputPattern = input_pattern;
        PrevInputPattern = input_pattern;
        TimeOfMaxIterSomaAmp = {0.0, 0.0,
            FirstImpulseTime + ExpectedPulseRelTimes[2] + measured_delay, 0.0};
        SomaPeakValid = {false, false, true, false};
        PeakRel = {0.0, 0.0, 0.24, 0.0};
        DelayFromPulse = {0.0, 0.0, measured_delay, 0.0};
        PrevPeakValid = {false, false, false, true};
        PrevPeakRel = {0.0, 0.0, 0.0, 0.4945};
        DendStatus.assign(4, 0);
        DendLastAbsDt.assign(4, 0.0);
        DendBestEffortSynced.assign(4, false);
        Dissynchronization.assign(4, 0.0);
        PrevDissynchronization.assign(4, 0.0);
        NoImproveCount.assign(4, 0);
        InitialSomaPotential.assign(4, 0.0);
        MaxIterSomaAmp.assign(4, 0.0);
        NumSynapse.assign(4, 1);
        LastLengthDelta = 0;
        LastLengthDeltaDendrite = -1;
    }

    bool DecideLength(int pulse)
    {
        return ChangeDendriteStatus(pulse);
    }

    int LengthStatus(int pulse) const
    {
        return DendStatus.at(static_cast<size_t>(pulse));
    }
};

TEST(ClassicDelayRoundoffTest, ClampsOnlyAbsoluteTimeSubtractionNoise)
{
    ClassicDelayRoundoffHarness learner;
    learner.SetDelayState(-1.7763568394002505e-15);

    ASSERT_TRUE(learner.DecideLength(2));
    EXPECT_EQ(learner.LengthStatus(2), 1)
        << "a one-ULP negative delay at the pulse should use the cable-delay estimate";
}

TEST(ClassicDelayRoundoffTest, KeepsMeaningfulNegativeDelayInvalid)
{
    ClassicDelayRoundoffHarness learner;
    learner.SetDelayState(-1e-9);

    ASSERT_TRUE(learner.DecideLength(2));
    EXPECT_EQ(learner.LengthStatus(2), 0)
        << "a real early-peak measurement must not be rounded into the valid range";
}

TEST(BranchSegmentOrderTransitionTest, GrowsSyncedActivePulseWhenOrderIsBroken)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 61, 89, 1}, 1, 100);

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.LengthStatus(1), 1)
        << "a locally synchronized pulse must still grow past the next committed attach point";
    EXPECT_EQ(learner.FailureReason(), 0);
}

TEST(BranchSegmentOrderTransitionTest, RefreshesTimingErrorBeforeOrderRepairReturn)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 61, 89, 1}, 1, 100);
    const double current_error = learner.CurrentModelTimingError(1);
    ASSERT_NEAR(current_error, 0.00134, 1e-10);
    learner.SetDissynchronization(1, 1.5);

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_NEAR(learner.DissynchronizationAt(1), current_error, 1e-12)
        << "the next delay-per-segment estimate must compare against the current error, not stale IterationGap";
    EXPECT_EQ(learner.LengthStatus(1), 1);
    EXPECT_EQ(learner.FailureReason(), 0);
}

TEST(BranchSegmentOrderTransitionTest, DoesNotChangeLengthWithoutActivePeak)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 61, 89, 1}, 1, 100, false);

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.LengthStatus(1), 0)
        << "segment-order recovery must preserve the no-length-change-without-peak contract";
    EXPECT_EQ(learner.FailureReason(), 0);
}

TEST(BranchSegmentOrderTransitionTest, RepairsOrderAfterConfirmedAmpCollapseWithoutPeak)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 61, 89, 1}, 1, 100, false, true);

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.LengthStatus(1), 1)
        << "confirmed amplitude collapse at exhausted synapse capacity permits only the structural order repair";
    EXPECT_EQ(learner.FailureReason(), 0);
}

TEST(BranchSegmentOrderTransitionTest, RefusesOrderRepairAtMaxLengthAfterAmpCollapse)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 100, 100, 1}, 1, 100, false, true);

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.LengthStatus(1), 0);
    EXPECT_EQ(learner.FailureReason(), 2);
    EXPECT_EQ(learner.Phase(), 5);
}

TEST(BranchSegmentOrderTransitionTest, RefusesWhenMaxLengthCannotRestoreOrder)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 100, 100, 1}, 1, 100);

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.LengthStatus(1), 0);
    EXPECT_EQ(learner.FailureReason(), 2);
    EXPECT_EQ(learner.Phase(), 5);
}

TEST(BranchInvalidPeakNoRecoveryTest, RefusesAfterRepeatedNoActionBurstsAtRmin)
{
    BranchSegmentOrderHarness learner;
    learner.SetInvalidPeakNoActionState(1.0e6, false);
    ASSERT_NEAR(learner.TipResistance(1), learner.MinimumResistance(), 1e-9);
    ASSERT_FALSE(learner.IsPulsePeakValid(1));
    ASSERT_TRUE(learner.IsReferencePulseSynced());
    ASSERT_GT(std::fabs(learner.InvalidPeakModelTimingError(1)), 0.02);

    for (int burst = 1; burst < 3; ++burst)
    {
        ASSERT_TRUE(learner.DecideLength(1));
        EXPECT_EQ(learner.FailureReason(), 0);
        EXPECT_EQ(learner.Phase(), 0);
        EXPECT_EQ(learner.LengthStatus(1), 0);
        EXPECT_EQ(learner.InvalidPeakNoActionCountAt(1), burst);
    }

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.FailureReason(), 3)
        << "parametric Branch must report refusal when the invalid peak, Rmin, and timing guard leave no legal transition";
    EXPECT_EQ(learner.Phase(), 5);
    EXPECT_EQ(learner.LengthStatus(1), 0)
        << "the refusal must preserve the no-length-change-without-peak contract";
}

TEST(BranchInvalidPeakNoRecoveryTest, DoesNotRefuseWhenCableTimingIsWithinTolerance)
{
    BranchSegmentOrderHarness learner;
    learner.SetInvalidPeakNoActionState(1.0e6, true);
    ASSERT_NEAR(learner.InvalidPeakModelTimingError(1), 0.0, 1e-12);

    for (int burst = 0; burst < 5; ++burst)
        ASSERT_TRUE(learner.DecideLength(1));

    EXPECT_EQ(learner.FailureReason(), 0);
    EXPECT_EQ(learner.Phase(), 0);
    EXPECT_EQ(learner.InvalidPeakNoActionCountAt(1), 0);
    EXPECT_TRUE(learner.IsBestEffortSynced(1));
}

TEST(BranchInvalidPeakNoRecoveryTest, RefusesAfterRepeatedNoActionAboveRmin)
{
    BranchSegmentOrderHarness learner;
    learner.SetInvalidPeakNoActionState(2.0e6, false);
    ASSERT_GT(learner.TipResistance(1), learner.MinimumResistance());

    for (int burst = 1; burst < 3; ++burst)
    {
        ASSERT_TRUE(learner.DecideLength(1));
        EXPECT_EQ(learner.FailureReason(), 0);
        EXPECT_EQ(learner.Phase(), 0);
        EXPECT_EQ(learner.InvalidPeakNoActionCountAt(1), burst);
    }

    ASSERT_TRUE(learner.DecideLength(1));
    EXPECT_EQ(learner.FailureReason(), 3);
    EXPECT_EQ(learner.Phase(), 5);
    EXPECT_EQ(learner.InvalidPeakNoActionCountAt(1), 3);
    EXPECT_EQ(learner.LengthStatus(1), 0);
}

TEST(BranchInvalidPeakNoRecoveryTest, DoesNotRefuseAtRmaxWhileW3EscapeIsEnabled)
{
    BranchSegmentOrderHarness learner;
    learner.SetInvalidPeakNoActionState(1.0e8, false);
    learner.EnableRmaxLengthEscape = true;

    for (int burst = 0; burst < 5; ++burst)
    {
        ASSERT_TRUE(learner.DecideLength(1));
        EXPECT_EQ(learner.FailureReason(), 0);
        EXPECT_EQ(learner.Phase(), 0);
        EXPECT_EQ(learner.InvalidPeakNoActionCountAt(1), 0);
    }
}

TEST_F(TimeLearnerResistanceTest, ParametricColdStartPreservesTipResistanceAndDerivedBounds)
{
    auto learner = CreateLearner("TimeLearnerParametricResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    ASSERT_TRUE(BuildAndReset(learner));
    ASSERT_EQ(learner->NumInputDendrite.GetData(), 3);

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);

    double minRm = std::numeric_limits<double>::max();
    double maxRm = 0.0;
    for (int i = 0; i < 2; ++i)
    {
        const std::string membraneName = "Dendrite" + std::to_string(i + 1) + "_1";
        auto membrane = neuron->GetComponentL<NMSDK::NPulseMembrane>(membraneName, true);
        ASSERT_TRUE(membrane) << membraneName;
        ASSERT_GT(membrane->GetNumPosChannels(), 0);
        auto* channel = dynamic_cast<NMSDK::NPulseChannel*>(membrane->GetPosChannel(0));
        ASSERT_NE(channel, nullptr);
        const double rm = channel->RestingResistance.GetData() > 0.0
            ? channel->RestingResistance.GetData()
            : channel->Resistance.GetData();
        ASSERT_GT(rm, 0.0);
        minRm = std::min(minRm, rm);
        maxRm = std::max(maxRm, rm);
        const double configuredRs = learner->SynapseResistanceBase.GetData();
        EXPECT_NEAR(tips[static_cast<size_t>(i)], configuredRs,
                    std::max(1e-6, configuredRs * 1e-9));
    }

    EXPECT_NEAR(learner->ResistanceMax.GetData(), minRm * 1000.0,
                std::max(1e-6, minRm * 1e-6));
    EXPECT_NEAR(learner->ResistanceMin.GetData(), maxRm / 1000.0,
                std::max(1e-6, maxRm * 1e-9));
    EXPECT_FALSE(learner->EnableRmaxLengthEscape.GetData());
}

TEST_F(TimeLearnerResistanceTest, FrozenAttenuationGammaSurvivesColdReset)
{
    auto learner = CreateLearner("TimeLearnerFrozenAttenuationGamma");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->AutoEstimateAttenuationGamma = false;
    learner->AttenuationGamma = 0.05;

    ASSERT_TRUE(BuildAndReset(learner));
    EXPECT_FALSE(learner->AutoEstimateAttenuationGamma.GetData());
    EXPECT_DOUBLE_EQ(learner->AttenuationGamma.GetData(), 0.05)
        << "cold reset must preserve a fixed gamma used for controlled training comparisons";
}

class SyncResistanceFreezeHarness : public NMSDK::NNeuronTimeLearner
{
public:
    void SetSyncEvidence(double absDt)
    {
        NumInputDendrite = 3;
        HasPrevPeakSnapshot = true;
        SomaPeakValid.assign(3, true);
        PrevPeakValid.assign(3, true);
        DendLastAbsDt.assign(3, absDt);
        DendBestEffortSynced.assign(3, false);
        ResistanceStatus.assign(3, 0);
        TipSynapseResistance.assign(3, 8.6e7);
        ResistanceMin = 1.0e3;
        InitialSomaPotential.assign(3, 0.01);
        MaxIterSomaAmp.assign(3, 0.02);
    }

    bool ObserveSyncAndMaybeFreeze()
    {
        return ShouldFreezeTipResistanceAfterFirstSync();
    }

    bool TryChangeResistance(int dendrite)
    {
        return ChangeSynapseResistanceStatus(dendrite);
    }

    void TryFeedforwardLengthGrow(int dendrite, int deltaLength)
    {
        FeedforwardResistanceOnLengthGrow(dendrite, deltaLength);
    }

    void SetPendingResistanceStatus(int dendrite, int status)
    {
        ResistanceStatus.at(static_cast<size_t>(dendrite)) = status;
    }

    int PendingResistanceStatus(int dendrite) const
    {
        return ResistanceStatus.at(static_cast<size_t>(dendrite));
    }

    void InvalidateOnePeak()
    {
        SomaPeakValid[0] = false;
    }
};

TEST(TimeLearnerResistanceFreezeTest, LatchesOnlyAfterGlobalSyncAndSurvivesLaterDesync)
{
    SyncResistanceFreezeHarness learner;
    learner.Default();
    EXPECT_FALSE(learner.FreezeTipResistanceAfterFirstSync.GetData());
    EXPECT_FALSE(learner.TipResistanceFrozenAfterSync.GetData());
    learner.FreezeTipResistanceAfterFirstSync = true;
    learner.SetSyncEvidence(0.03);

    EXPECT_FALSE(learner.ObserveSyncAndMaybeFreeze());
    EXPECT_FALSE(learner.TipResistanceFrozenAfterSync.GetData());

    learner.SetSyncEvidence(0.01);
    EXPECT_TRUE(learner.ObserveSyncAndMaybeFreeze());
    EXPECT_TRUE(learner.TipResistanceFrozenAfterSync.GetData());

    const double frozenR = learner.TipSynapseResistance[0];
    learner.SetPendingResistanceStatus(0, 1);
    EXPECT_TRUE(learner.TryChangeResistance(0));
    EXPECT_DOUBLE_EQ(learner.TipSynapseResistance[0], frozenR);
    EXPECT_EQ(learner.PendingResistanceStatus(0), 0);

    learner.TryFeedforwardLengthGrow(0, 2);
    EXPECT_DOUBLE_EQ(learner.TipSynapseResistance[0], frozenR);

    learner.InvalidateOnePeak();
    EXPECT_TRUE(learner.ObserveSyncAndMaybeFreeze());
}

TEST_F(TimeLearnerResistanceTest, StructuralColdStartPreservesBaseResistance)
{
    auto learner = CreateLearner("TimeLearnerStructuralResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only cap";
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only floor";
    learner->EnableRmaxLengthEscape = true;
    const double baseResistance = learner->SynapseResistanceBase.GetData();
    ASSERT_TRUE(BuildAndReset(learner));

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0);
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0);
    EXPECT_DOUBLE_EQ(learner->SynapseResistanceBase.GetData(), baseResistance);
    EXPECT_DOUBLE_EQ(tips[0], baseResistance);
    EXPECT_DOUBLE_EQ(tips[1], baseResistance);
}

TEST_F(TimeLearnerResistanceTest, ResistanceRatioMustBeAtLeastOne)
{
    auto classic = CreateLearner("TimeLearnerRatioBoundary");
    ASSERT_TRUE(classic);
    EXPECT_FALSE(classic->SetMaxSynapseToMembraneResistanceRatio(0.999));
    EXPECT_TRUE(classic->SetMaxSynapseToMembraneResistanceRatio(1.0));
    classic->MaxSynapseToMembraneResistanceRatio = 1.0;
    EXPECT_DOUBLE_EQ(classic->MaxSynapseToMembraneResistanceRatio.GetData(), 1.0);
}

TEST_F(TimeLearnerResistanceTest, BranchResistanceRatioMustBeAtLeastOne)
{
    auto branch = CreateBranchLearner("TimeLearnerBranchRatioBoundary");
    ASSERT_TRUE(branch);
    EXPECT_FALSE(branch->SetMaxSynapseToMembraneResistanceRatio(0.999));
    EXPECT_TRUE(branch->SetMaxSynapseToMembraneResistanceRatio(1.0));
    branch->MaxSynapseToMembraneResistanceRatio = 1.0;
    EXPECT_DOUBLE_EQ(branch->MaxSynapseToMembraneResistanceRatio.GetData(), 1.0);
}

TEST_F(TimeLearnerResistanceTest, BranchParametricColdStartPreservesTipResistanceAndDerivedBounds)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchParametricResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    ASSERT_TRUE(BuildAndReset(learner));

    // Branch resets every input to the first segment. The final input is the
    // reference anchor and must also be clamped back to a valid segment.
    const auto lengths = learner->DendriteLength.GetData();
    ASSERT_EQ(lengths.size(), static_cast<size_t>(learner->NumInputDendrite.GetData()));
    EXPECT_TRUE(std::all_of(lengths.begin(), lengths.end(), [](int value) { return value == 1; }));
    EXPECT_TRUE(learner->IsNeedToTrain.GetData());

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto membrane = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_1", true);
    ASSERT_TRUE(membrane);
    ASSERT_GT(membrane->GetNumPosChannels(), 0);
    auto* channel = dynamic_cast<NMSDK::NPulseChannel*>(membrane->GetPosChannel(0));
    ASSERT_NE(channel, nullptr);
    const double rm = channel->RestingResistance.GetData() > 0.0
        ? channel->RestingResistance.GetData()
        : channel->Resistance.GetData();
    ASSERT_GT(rm, 0.0);

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);
    const double configuredRs = learner->SynapseResistanceBase.GetData();
    EXPECT_NEAR(tips[0], configuredRs, std::max(1e-6, configuredRs * 1e-9));
    EXPECT_NEAR(tips[1], configuredRs, std::max(1e-6, configuredRs * 1e-9));
    EXPECT_NEAR(learner->ResistanceMax.GetData(), rm * 1000.0,
                std::max(1e-6, rm * 1e-6));
    EXPECT_NEAR(learner->ResistanceMin.GetData(), rm / 1000.0,
                std::max(1e-6, rm * 1e-9));
}

TEST_F(TimeLearnerResistanceTest, BranchStructuralColdStartPreservesBaseResistance)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchStructuralResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only cap";
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only floor";
    learner->EnableRmaxLengthEscape = true;
    const double baseResistance = learner->SynapseResistanceBase.GetData();
    ASSERT_TRUE(BuildAndReset(learner));

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0);
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0);
    EXPECT_DOUBLE_EQ(learner->SynapseResistanceBase.GetData(), baseResistance);
    EXPECT_DOUBLE_EQ(tips[0], baseResistance);
    EXPECT_DOUBLE_EQ(tips[1], baseResistance);
}

TEST_F(TimeLearnerResistanceTest, ClassicToleranceAndPeakMarginBoundaries)
{
    auto learner = CreateLearner("TimeLearnerClassicToleranceBoundaries");
    ASSERT_TRUE(learner);

    EXPECT_FALSE(learner->SetSyncTolerance(-std::numeric_limits<double>::epsilon()));
    EXPECT_TRUE(learner->SetSyncTolerance(0.0));
    EXPECT_TRUE(learner->SetSyncTolerance(std::numeric_limits<double>::min()));

    EXPECT_FALSE(learner->SetPeakMeasureMargin(-std::numeric_limits<double>::epsilon()));
    EXPECT_TRUE(learner->SetPeakMeasureMargin(0.0));
    EXPECT_TRUE(learner->SetPeakMeasureMargin(std::numeric_limits<double>::min()));
}

TEST_F(TimeLearnerResistanceTest, BranchToleranceAndPeakMarginBoundaries)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchToleranceBoundaries");
    ASSERT_TRUE(learner);

    EXPECT_FALSE(learner->SetSyncTolerance(-std::numeric_limits<double>::epsilon()));
    EXPECT_TRUE(learner->SetSyncTolerance(0.0));
    EXPECT_TRUE(learner->SetSyncTolerance(std::numeric_limits<double>::min()));

    EXPECT_FALSE(learner->SetPeakMeasureMargin(-std::numeric_limits<double>::epsilon()));
    EXPECT_TRUE(learner->SetPeakMeasureMargin(0.0));
    EXPECT_TRUE(learner->SetPeakMeasureMargin(std::numeric_limits<double>::min()));
}


class BranchPathologicalAmpHarness : public NMSDK::NNeuronTimeLearnerBranch
{
public:
    void SetAmpState(double amp)
    {
        NumInputDendrite = 2;
        NormalizationMode = 1;
        EnableRmaxLengthEscape = false;
        AutoEstimateAttenuationGamma = false;
        AttenuationGamma = 0.05;
        ResistanceAdjustGain = 0.4;
        SynapseResistanceBase = 8.6e7;
        ResistanceMin = 1.0e4;
        ResistanceMax = 1.0e10;
        MaxDendriteLength = 100;
        DendriteLength = {9, 1};
        TipSynapseResistance = {2.5e5, 8.6e7};
        InitialSomaPotential = {0.015781, 0.015781};
        MaxIterSomaAmp = {amp, 0.0};
        NumSynapse = {1, 1};
        DendStatus.assign(2, 0);
        SynapseStatus.assign(2, 0);
        ResistanceStatus.assign(2, 0);
        ResistanceDifference.assign(2, 0.0);
        PrevAmpError.assign(2, 0.0);
        PrevResistanceRatio.assign(2, 1.0);
        NoImproveResistanceCount.assign(2, 0);
        AmpDtSkipCount.assign(2, 0);
        RmaxDwellCount.assign(2, 0);
        RmaxOvershootLengthGrow.assign(2, false);
        RmaxOvershootLengthCooldown.assign(2, 0);
        EffectiveResistanceGain.assign(2, 0.4);
        DendLastAbsDt.assign(2, 0.0);
        DendBestEffortSynced.assign(2, false);
        InputPattern.Assign(2, 1, 0.0);
        PrevInputPattern.Assign(2, 1, 0.0);
    }

    bool Tune()
    {
        return ChangeSynapseResistanceStatus(0);
    }

    double TipResistance() const
    {
        return TipSynapseResistance[0];
    }

    int PendingResistanceStatus() const
    {
        return ResistanceStatus[0];
    }

    int PathologicalSkipCount() const
    {
        return AmpDtSkipCount[0];
    }
};

TEST(BranchPathologicalAmpNormTest, BoundsRepeatedExtremeAmplitudeSteps)
{
    BranchPathologicalAmpHarness learner;
    learner.Default();
    learner.SetAmpState(1.0e19);
    const double initialR = learner.TipResistance();

    ASSERT_TRUE(learner.Tune());
    EXPECT_DOUBLE_EQ(learner.TipResistance(), initialR);
    EXPECT_EQ(learner.PendingResistanceStatus(), 0);
    EXPECT_EQ(learner.PathologicalSkipCount(), 1);

    ASSERT_TRUE(learner.Tune());
    EXPECT_DOUBLE_EQ(learner.TipResistance(), initialR);
    EXPECT_EQ(learner.PendingResistanceStatus(), 0);
    EXPECT_EQ(learner.PathologicalSkipCount(), 2);

    ASSERT_TRUE(learner.Tune());
    EXPECT_NEAR(learner.TipResistance(), initialR * 1.15, 1e-6);
    EXPECT_LT(learner.TipResistance(), 1.0e10);
    EXPECT_EQ(learner.PendingResistanceStatus(), 1);
    EXPECT_EQ(learner.PathologicalSkipCount(), 0);
}

TEST(BranchPathologicalAmpNormTest, OrdinaryUnderTargetStillUsesAmplitudeFeedback)
{
    BranchPathologicalAmpHarness learner;
    learner.Default();
    learner.SetAmpState(0.00045);
    const double initialR = learner.TipResistance();

    ASSERT_TRUE(learner.Tune());
    EXPECT_LT(learner.TipResistance(), initialR);
    EXPECT_GT(learner.TipResistance(), 1.0e4);
    EXPECT_EQ(learner.PathologicalSkipCount(), 0);
}

class BranchPerInputGammaHarness : public NMSDK::NNeuronTimeLearnerBranch
{
public:
    void SetGammaState(bool perInput)
    {
        NumInputDendrite = 3;
        NormalizationMode = 1;
        AutoEstimateAttenuationGamma = false;
        UsePerInputAttenuationGamma = perInput;
        AttenuationGamma = 0.05;
        AttenuationGammaByInput = {0.1, 0.2, 0.3};
        SynapseResistanceBase = 8.6e7;
        TipSynapseResistance = {1.0e6, 2.0e6, 3.0e6};
        ResistanceStatus.assign(3, 0);
        ResistanceDifference.assign(3, 0.0);
        InitialSomaPotential.assign(3, 0.01);
        MaxIterSomaAmp.assign(3, 0.0);
    }

    void Grow(int input, int deltaLength)
    {
        FeedforwardResistanceOnLengthGrow(input, deltaLength);
    }
};

TEST(BranchAttenuationGammaTest, PerInputModeUsesOnlyTheGrowingInputsGamma)
{
    BranchPerInputGammaHarness learner;
    learner.Default();
    learner.SetGammaState(true);

    learner.Grow(1, 2);

    const auto tips = learner.TipSynapseResistance.GetData();
    ASSERT_EQ(tips.size(), 3u);
    EXPECT_DOUBLE_EQ(tips[0], 1.0e6);
    EXPECT_NEAR(tips[1], 2.0e6 * std::exp(-0.2 * 2.0), 1e-8);
    EXPECT_DOUBLE_EQ(tips[2], 3.0e6);
}

TEST(BranchAttenuationGammaTest, SharedModeRetainsLegacyScalarGamma)
{
    BranchPerInputGammaHarness learner;
    learner.Default();
    learner.SetGammaState(false);

    learner.Grow(1, 2);

    const auto tips = learner.TipSynapseResistance.GetData();
    ASSERT_EQ(tips.size(), 3u);
    EXPECT_NEAR(tips[1], 2.0e6 * std::exp(-0.05 * 2.0), 1e-8);
}
