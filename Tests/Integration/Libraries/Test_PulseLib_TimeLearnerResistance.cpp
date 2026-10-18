#include <gtest/gtest.h>

#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerAmpReference.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerResistanceBounds.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerStructuralAmp.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../Support/ConsoleLikeInit.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <string>
#include <vector>

using namespace RDK;

TEST(TimeLearnerAmpReferenceTest, CapturesOnlyTheFinalizedSingleSynapsePeak)
{
    using NMSDK::TimeLearnerAmpReference::ShouldCaptureFinalizedSingleSynapsePeakReference;

    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, false, true, 0.005, 0.0))
        << "a rising-edge sample is not the completed peak";
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, true, false, 0.0, 0.0))
        << "an empty measurement window has no reference peak";
    EXPECT_TRUE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, true, true, 0.02, 0.0));
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 2, true, true, 0.02, 0.0))
        << "additional structural contacts must not raise the reference";
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, true, true, 0.02, 0.01))
        << "later higher peaks must not move an established reference";
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, false, 1, true, true, 0.02, 0.0));
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        false, true, 1, true, true, 0.02, 0.0));
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, true, true, 0.0, 0.0));
    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, true, true, std::numeric_limits<double>::quiet_NaN(), 0.0));
}

TEST(TimeLearnerAmpReferenceTest, KeepsReferenceBeforeStructuralLengthening)
{
    using NMSDK::TimeLearnerAmpReference::ShouldCaptureFinalizedSingleSynapsePeakReference;

    double reference = 0.0;
    const double measured_single_synapse_peak = 0.015781466599319449;

    ASSERT_TRUE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, true, 1, true, true, measured_single_synapse_peak, reference));
    reference = measured_single_synapse_peak;
    EXPECT_DOUBLE_EQ(reference, measured_single_synapse_peak);

    EXPECT_FALSE(ShouldCaptureFinalizedSingleSynapsePeakReference(
        true, false, 1, true, true, 0.004, reference))
        << "after the dendrite grows, a later attenuated peak must not replace its unit-cable reference";
}

TEST(StructuralAmpQuantizationTest, AcceptsOnlyTheRepeatedLowerSideOfAnAdjacentBracket)
{
    NMSDK::StructuralAmpQuantizationTracker tracker;
    tracker.Reset(1, 10);
    const double target = 0.01;

    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));

    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), 7);
    EXPECT_FALSE(tracker.IsAccepted(0, 8, 6, target))
        << "the upper, over-target candidate must never be accepted";
    EXPECT_TRUE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_TRUE(tracker.IsAccepted(0, 7, 6, target));
}

TEST(StructuralAmpQuantizationTest, StepsDownFromUpperCountToAcceptedLowerCount)
{
    EXPECT_EQ(NMSDK::StructuralAmpQuantizedStepTowardLowerCount(99, 98), -1)
        << "a confirmed bracket must move from its upper count to the safe lower count";
    EXPECT_EQ(NMSDK::StructuralAmpQuantizedStepTowardLowerCount(98, 98), 0)
        << "the accepted lower count is held once selected";
    EXPECT_EQ(NMSDK::StructuralAmpQuantizedStepTowardLowerCount(97, 98), 0)
        << "do not remove further contacts when already below the selected count";
    EXPECT_EQ(NMSDK::StructuralAmpQuantizedStepTowardLowerCount(99, -1), 0)
        << "no structural step is requested without an accepted candidate";
}

TEST(StructuralAmpQuantizationTest, RejectsNonAdjacentCountsAndUnusableMeasurements)
{
    NMSDK::StructuralAmpQuantizationTracker tracker;
    tracker.Reset(1, 10);
    const double target = 0.01;

    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 9, 6, target, 0.011, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, false, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, false, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 9, 6, target, 0.011, true, true, 1e-5));
    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), -1);
}

TEST(StructuralAmpQuantizationTest, ChoosesTheHighestSafeAdjacentPair)
{
    NMSDK::StructuralAmpQuantizationTracker tracker;
    tracker.Reset(1, 10);
    const double target = 0.01;

    for (int repeat = 0; repeat < 2; ++repeat)
    {
        EXPECT_FALSE(tracker.Observe(0, 3, 6, target, 0.008, true, true, 1e-5));
        EXPECT_FALSE(tracker.Observe(0, 4, 6, target, 0.012, true, true, 1e-5));
    }
    for (int repeat = 0; repeat < 2; ++repeat)
    {
        EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
        EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    }

    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), 7);
}

TEST(StructuralAmpQuantizationTest, ExactMeasurementsClearTheQuantizedBracket)
{
    NMSDK::StructuralAmpQuantizationTracker tracker;
    tracker.Reset(1, 10);
    const double target = 0.01;

    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), 7);

    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, target, true, true, 1e-5));
    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), -1)
        << "an exact sample must use the existing exact EOL path";

    tracker.Reset(1, 10);
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), 7);
    EXPECT_FALSE(tracker.IsAccepted(0, 7, 7, target));
    EXPECT_FALSE(tracker.IsAccepted(0, 7, 6, target + 0.001));

    tracker.Reset(1, 10);
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), 7);
    EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.009, true, true, 1e-5));
    EXPECT_EQ(tracker.AcceptedCount(0, 6, target), -1)
        << "a count whose measurements crossed the target is not stable evidence";
}

TEST(StructuralAmpQuantizationTest, InvalidatesEvidenceWhenOtherStructureChanges)
{
    NMSDK::StructuralAmpQuantizationTracker tracker;
    tracker.Reset(3, 10);
    const double target = 0.01;

    for (int repeat = 0; repeat < 2; ++repeat)
    {
        EXPECT_FALSE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
        EXPECT_FALSE(tracker.Observe(0, 8, 6, target, 0.011, true, true, 1e-5));
        EXPECT_FALSE(tracker.Observe(1, 4, 6, target, 0.009, true, true, 1e-5));
        EXPECT_FALSE(tracker.Observe(1, 5, 6, target, 0.011, true, true, 1e-5));
    }
    EXPECT_TRUE(tracker.Observe(0, 7, 6, target, 0.009, true, true, 1e-5));
    EXPECT_TRUE(tracker.Observe(1, 4, 6, target, 0.009, true, true, 1e-5));
    ASSERT_TRUE(tracker.IsAccepted(0, 7, 6, target));
    ASSERT_TRUE(tracker.IsAccepted(1, 4, 6, target));

    tracker.InvalidateOtherInputs(0);
    EXPECT_TRUE(tracker.IsAccepted(0, 7, 6, target))
        << "the changing input's own adjacent-count evidence remains usable";
    EXPECT_FALSE(tracker.IsAccepted(1, 4, 6, target))
        << "other inputs must be re-measured after the shared response changes";

    tracker.InvalidateAll();
    EXPECT_FALSE(tracker.IsAccepted(0, 7, 6, target));
}

TEST(TimeLearnerResistanceBoundsTest, ComputesNoCrossingRatioFromMembraneTimeScale)
{
    const auto br480 = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        1.0e-9, 1.0e7, 2000.0, 1);
    ASSERT_EQ(br480.status, NMSDK::TimeLearnerResistanceBounds::FloorStatus::Ok);
    EXPECT_NEAR(br480.dimensionlessTimeScale, 20.0, 1.0e-12);
    EXPECT_NEAR(br480.minimumResistance, 2.879e6, 2.0e3);

    const double q = br480.dimensionlessTimeScale;
    const double rho = br480.minimumResistance / 1.0e7;
    const double stepGain = std::pow(1.0 + 1.0 / rho, 2.0) / q;
    EXPECT_NEAR(stepGain, 1.0, 1.0e-12);
}

TEST(TimeLearnerResistanceBoundsTest, ScalesFloorForMultipleSynapsesAndFastSteps)
{
    const auto minMatrixQ = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        1.0e-11, 1.0e7, 20000.0, 1);
    ASSERT_EQ(minMatrixQ.status, NMSDK::TimeLearnerResistanceBounds::FloorStatus::Ok);
    EXPECT_NEAR(minMatrixQ.minimumResistance / 1.0e7, 2.41421356237, 1.0e-9);

    const auto twoSynapses = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        1.0e-9, 1.0e7, 2000.0, 2);
    ASSERT_EQ(twoSynapses.status, NMSDK::TimeLearnerResistanceBounds::FloorStatus::Ok);
    EXPECT_NEAR(twoSynapses.minimumResistance, 2.0 * 2.879e6, 4.0e3);
}

TEST(TimeLearnerResistanceBoundsTest, RejectsScalesWithoutFiniteNoCrossingFloor)
{
    const auto belowBoundary = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        1.0e-11, 1.0e7, 2000.0, 1);
    EXPECT_EQ(belowBoundary.status,
              NMSDK::TimeLearnerResistanceBounds::FloorStatus::NoFiniteLinearStabilityFloor);
    EXPECT_NEAR(belowBoundary.dimensionlessTimeScale, 0.2, 1.0e-12);

    const auto atBoundary = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        2.5e-11, 1.0e7, 2000.0, 1);
    EXPECT_EQ(atBoundary.status,
              NMSDK::TimeLearnerResistanceBounds::FloorStatus::NoFiniteLinearStabilityFloor);

    const auto stableButOvershooting = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        3.75e-11, 1.0e7, 2000.0, 1);
    EXPECT_EQ(stableButOvershooting.status,
              NMSDK::TimeLearnerResistanceBounds::FloorStatus::NoFiniteNoCrossingFloor);
    EXPECT_NEAR(stableButOvershooting.dimensionlessTimeScale, 0.75, 1.0e-12);

    const auto invalid = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
        0.0, 1.0e7, 2000.0, 1);
    EXPECT_EQ(invalid.status, NMSDK::TimeLearnerResistanceBounds::FloorStatus::InvalidInput);
}

TEST(TimeLearnerResistanceBoundsTest, SeparatesLinearStabilityFromMonotoneNoCrossing)
{
    const auto unstable = NMSDK::TimeLearnerResistanceBounds::AssessStepStability(
        1.0e-11, 1.0e7, 2000.0);
    EXPECT_EQ(unstable.status,
              NMSDK::TimeLearnerResistanceBounds::StepStabilityStatus::NoStrictLinearStabilityForAnyFiniteResistance);
    EXPECT_NEAR(unstable.dimensionlessTimeScale, 0.2, 1.0e-12);
    EXPECT_NEAR(unstable.minimumStepGainAtZeroConductance, 5.0, 1.0e-12);

    const auto marginal = NMSDK::TimeLearnerResistanceBounds::AssessStepStability(
        2.5e-11, 1.0e7, 2000.0);
    EXPECT_EQ(marginal.status,
              NMSDK::TimeLearnerResistanceBounds::StepStabilityStatus::NoStrictLinearStabilityForAnyFiniteResistance);
    EXPECT_NEAR(marginal.minimumStepGainAtZeroConductance, 2.0, 1.0e-12);

    const auto stablePossible = NMSDK::TimeLearnerResistanceBounds::AssessStepStability(
        3.75e-11, 1.0e7, 2000.0);
    EXPECT_EQ(stablePossible.status,
              NMSDK::TimeLearnerResistanceBounds::StepStabilityStatus::StrictLinearStabilityPossible);
    EXPECT_NEAR(stablePossible.minimumStepGainAtZeroConductance, 4.0 / 3.0, 1.0e-12);
}

TEST(TimeLearnerResistanceBoundsTest, KeepsDistinctPerInputResistanceIntervals)
{
    const auto result = NMSDK::TimeLearnerResistanceBounds::ComputePerInputBounds(
        {1.0e7, 1.0e8}, {2.879e6, 2.0e7}, 1.0);
    ASSERT_TRUE(result.valid);
    EXPECT_FALSE(result.commonIntervalExists)
        << "different membrane resistances need not share one absolute Rs interval";
    ASSERT_EQ(result.minimumResistance.size(), 2u);
    ASSERT_EQ(result.maximumResistance.size(), 2u);
    EXPECT_DOUBLE_EQ(result.minimumResistance[0], 1.0e7);
    EXPECT_DOUBLE_EQ(result.maximumResistance[0], 1.0e7);
    EXPECT_DOUBLE_EQ(result.minimumResistance[1], 1.0e8);
    EXPECT_DOUBLE_EQ(result.maximumResistance[1], 1.0e8);
    EXPECT_DOUBLE_EQ(result.maximumMinimumRatio, 1.0);
}

TEST(TimeLearnerResistanceBoundsTest, CombinesEachInputRatioWithItsOwnStabilityFloor)
{
    const auto result = NMSDK::TimeLearnerResistanceBounds::ComputePerInputBounds(
        {1.0e7, 1.0e8}, {2.879e6, 2.0e4}, 1000.0);
    ASSERT_TRUE(result.valid);
    ASSERT_TRUE(result.commonIntervalExists);
    ASSERT_EQ(result.minimumResistance.size(), 2u);
    EXPECT_NEAR(result.minimumResistance[0], 2.879e6, 1.0e-8);
    EXPECT_NEAR(result.minimumRatio[0], 0.2879, 1.0e-12);
    EXPECT_NEAR(result.minimumResistance[1], 1.0e5, 1.0e-8)
        << "the second input uses its own Rm and does not inherit the first input's absolute floor";
    EXPECT_NEAR(result.minimumRatio[1], 0.001, 1.0e-12);
}

TEST(TimeLearnerResistanceBoundsTest, RejectsOnlyWhenAnInputHasNoFeasibleLocalRange)
{
    const auto impossible = NMSDK::TimeLearnerResistanceBounds::ComputePerInputBounds(
        {1.0e7, 1.0e8}, {1.1e7, 1.0e5}, 1.0);
    EXPECT_FALSE(impossible.valid)
        << "a stability floor above that input's own upper ratio is infeasible";
}

TEST(TimeLearnerResistanceBoundsTest, EffectiveSynapseCountMatchesChannelAggregation)
{
    EXPECT_EQ(NMSDK::TimeLearnerResistanceBounds::EffectiveConductanceCount(0, false), 0);
    EXPECT_EQ(NMSDK::TimeLearnerResistanceBounds::EffectiveConductanceCount(1, false), 1);
    EXPECT_EQ(NMSDK::TimeLearnerResistanceBounds::EffectiveConductanceCount(8, false), 8);
    EXPECT_EQ(NMSDK::TimeLearnerResistanceBounds::EffectiveConductanceCount(0, true), 0);
    EXPECT_EQ(NMSDK::TimeLearnerResistanceBounds::EffectiveConductanceCount(8, true), 1);
}

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

        model->Default();
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

        model->Default();
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
        learner->Build();
        if (!learner->IsReady())
            return false;
        EXPECT_EQ(learner->NormalizationMode.GetData(), configuredMode)
            << "learner Build changed NormalizationMode";
        model->Build();
        if (!model->IsReady())
            return false;
        EXPECT_EQ(learner->NormalizationMode.GetData(), configuredMode)
            << "model Build changed NormalizationMode";
        // The fixture adds the learner after creating the model. Initialize
        // the completed component tree before requesting its cold reset.
        model->Init();
        learner->ResetToUntrainedState = true;
        model->Reset();
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
    void SetCommittedPulseStatesForTest()
    {
        const size_t count = static_cast<size_t>(NumInputDendrite.GetData());
        PulseSynced.assign(count, true);
        DendBestEffortSynced.assign(count, true);
        NoImproveCount.assign(count, 7);
        InvalidPeakNoActionCount.assign(count, 2);
        DendLastAbsDt.assign(count, 0.0005);
        Dissynchronization.assign(count, 0.0005);
        DendStatus.assign(count, 1);
        SynapseStatus.assign(count, -1);
        AmpDifference.assign(count, 0.125);
    }

    void ReopenAfterStructuralChangeForTest(int edited_pulse = -1)
    {
        InvalidatePulseSyncAfterStructuralChange(edited_pulse);
    }

    bool AllPulsesSyncedForTest() const
    {
        return AllDendritesSynced();
    }

    bool PulseSyncedForTest(int pulse) const
    {
        return PulseSynced.at(static_cast<size_t>(pulse));
    }

    bool BestEffortSyncedForTest(int pulse) const
    {
        return DendBestEffortSynced.at(static_cast<size_t>(pulse));
    }

    int NoImproveCountForTest(int pulse) const
    {
        return NoImproveCount.at(static_cast<size_t>(pulse));
    }

    int InvalidPeakNoActionCountForTest(int pulse) const
    {
        return InvalidPeakNoActionCount.at(static_cast<size_t>(pulse));
    }

    int LengthStatusForTest(int pulse) const
    {
        return DendStatus.at(static_cast<size_t>(pulse));
    }

    int SynapseStatusForTest(int pulse) const
    {
        return SynapseStatus.at(static_cast<size_t>(pulse));
    }

    double AmpDifferenceForTest(int pulse) const
    {
        return AmpDifference.at(static_cast<size_t>(pulse));
    }

    double LastAbsDtForTest(int pulse) const
    {
        return DendLastAbsDt.at(static_cast<size_t>(pulse));
    }

    int SelectedPulseForTest() const
    {
        return SelectActiveDendrite();
    }

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
        IterationGap = 1.5;
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

    void ClearPeakAttemptForTest(int pulse)
    {
        if (pulse < int(MaxIterSomaAmp.size()))
            MaxIterSomaAmp[static_cast<size_t>(pulse)] = 0.0;
        if (int(PeakSeen.size()) != NumInputDendrite.GetData())
            PeakSeen.assign(static_cast<size_t>(NumInputDendrite.GetData()), false);
        else
            PeakSeen[static_cast<size_t>(pulse)] = false;
        if (pulse < int(SomaPeakValid.size()))
            SomaPeakValid[static_cast<size_t>(pulse)] = false;
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

TEST(BranchStructuralSyncInvalidationTest, ReopensCommittedPulsesAndReferenceAnchor)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 12, 6, 1}, 1, 100);
    learner.SetCommittedPulseStatesForTest();
    ASSERT_TRUE(learner.AllPulsesSyncedForTest());

    learner.ReopenAfterStructuralChangeForTest();

    EXPECT_FALSE(learner.AllPulsesSyncedForTest());
    for (int pulse = 0; pulse < 4; ++pulse)
    {
        EXPECT_FALSE(learner.PulseSyncedForTest(pulse)) << "pulse " << pulse;
        EXPECT_FALSE(learner.BestEffortSyncedForTest(pulse)) << "pulse " << pulse;
        EXPECT_EQ(learner.NoImproveCountForTest(pulse), 0) << "pulse " << pulse;
        EXPECT_EQ(learner.InvalidPeakNoActionCountForTest(pulse), 0) << "pulse " << pulse;
        EXPECT_EQ(learner.LengthStatusForTest(pulse), 0) << "pulse " << pulse;
        EXPECT_EQ(learner.SynapseStatusForTest(pulse), 0) << "pulse " << pulse;
        EXPECT_DOUBLE_EQ(learner.AmpDifferenceForTest(pulse), 0.0) << "pulse " << pulse;
        EXPECT_GT(learner.LastAbsDtForTest(pulse), 0.02) << "pulse " << pulse;
    }
    EXPECT_EQ(learner.SelectedPulseForTest(), 3)
        << "the reference pulse must be measured again before the earlier pulses are retuned";
}

TEST(BranchStructuralSyncInvalidationTest, ScopedReopenKeepsAnchorWhenEarlierPulseEdited)
{
    BranchSegmentOrderHarness learner;
    learner.SetOrderState({1, 12, 6, 1}, 1, 100);
    learner.SetCommittedPulseStatesForTest();
    ASSERT_TRUE(learner.AllPulsesSyncedForTest());

    learner.ReopenAfterStructuralChangeForTest(1);

    EXPECT_FALSE(learner.PulseSyncedForTest(0));
    EXPECT_FALSE(learner.PulseSyncedForTest(1));
    EXPECT_TRUE(learner.PulseSyncedForTest(2))
        << "later committed pulses stay synced after an earlier structural edit";
    EXPECT_TRUE(learner.PulseSyncedForTest(3))
        << "anchor stays synced so SelectActive returns the edited pulse";
    EXPECT_EQ(learner.SelectedPulseForTest(), 1);
    // Scoped ±1 length edits must keep the no-improve streak; clearing it on
    // every invalidate freezes W10 @25 ms in an L=5↔6 oscillation.
    EXPECT_EQ(learner.NoImproveCountForTest(0), 7);
    EXPECT_EQ(learner.NoImproveCountForTest(1), 7);
    EXPECT_EQ(learner.InvalidPeakNoActionCountForTest(0), 2);
    EXPECT_EQ(learner.InvalidPeakNoActionCountForTest(1), 2);
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

TEST(BranchInvalidPeakNoRecoveryTest, DoesNotCountUnmeasuredBurstsTowardRefusal)
{
    BranchSegmentOrderHarness learner;
    learner.SetInvalidPeakNoActionState(1.0e6, false);
    learner.ClearPeakAttemptForTest(1);

    for (int burst = 0; burst < 5; ++burst)
    {
        ASSERT_TRUE(learner.DecideLength(1));
        EXPECT_EQ(learner.FailureReason(), 0);
        EXPECT_EQ(learner.Phase(), 0);
        EXPECT_EQ(learner.InvalidPeakNoActionCountAt(1), 0)
            << "empty PeakSeen/MaxAmp windows must not arm InvalidPeakNoRecovery";
    }
}

TEST(BranchInvalidPeakNoRecoveryTest, RefusesWhenTimingMatchesButAmplitudeCannotRecover)
{
    BranchSegmentOrderHarness learner;
    learner.SetInvalidPeakNoActionState(1.0e6, true);
    ASSERT_NEAR(learner.InvalidPeakModelTimingError(1), 0.0, 1e-12);

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
    EXPECT_FALSE(learner.IsBestEffortSynced(1));
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
    std::vector<double> expectedMinima;
    std::vector<double> expectedRatios;
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
        double stabilityFloor = 0.0;
        const double channelRs[] = {
            channel->Resistance.GetData(),
            channel->RestingResistance.GetData(),
            channel->FBResistance.GetData()
        };
        for (double candidateRs : channelRs)
        {
            const auto floor = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
                channel->Capacity.GetData(), candidateRs,
                static_cast<double>(channel->TimeStep.GetData()),
                std::max(1, channel->GetNumSynapses()));
            ASSERT_EQ(floor.status, NMSDK::TimeLearnerResistanceBounds::FloorStatus::Ok);
            stabilityFloor = std::max(stabilityFloor, floor.minimumResistance);
        }
        const double configuredRs = learner->SynapseResistanceBase.GetData();
        EXPECT_NEAR(tips[static_cast<size_t>(i)], configuredRs,
                    std::max(1e-6, configuredRs * 1e-9));
        const double localMinimum = std::max(rm / 1000.0, stabilityFloor);
        expectedMinima.push_back(localMinimum);
        expectedRatios.push_back(localMinimum / rm);
    }

    EXPECT_NEAR(learner->ResistanceMax.GetData(), minRm * 1000.0,
                std::max(1e-6, minRm * 1e-6));
    const double expectedMinRs = *std::max_element(expectedMinima.begin(), expectedMinima.end());
    const double expectedMinRatio = *std::max_element(expectedRatios.begin(), expectedRatios.end());
    EXPECT_NEAR(learner->ResistanceMin.GetData(), expectedMinRs,
                std::max(1e-6, expectedMinRs * 1e-9));
    EXPECT_NEAR(learner->ResistanceMinRatio.GetData(), expectedMinRatio, 1e-12);
    const auto actualMinima = learner->ResistanceMinByInput.GetData();
    const auto actualRatios = learner->ResistanceMinRatioByInput.GetData();
    ASSERT_EQ(actualMinima.size(), expectedMinima.size());
    ASSERT_EQ(actualRatios.size(), expectedRatios.size());
    for(size_t i = 0; i < expectedMinima.size(); ++i)
    {
        EXPECT_NEAR(actualMinima[i], expectedMinima[i], std::max(1e-6, expectedMinima[i] * 1e-9));
        EXPECT_NEAR(actualRatios[i], expectedRatios[i], 1e-12);
    }
    EXPECT_FALSE(learner->EnableRmaxLengthEscape.GetData());
}

TEST_F(TimeLearnerResistanceTest, ClassicParametricColdStartIgnoresStaleSerializedMinimum)
{
    auto learner = CreateLearner("TimeLearnerClassicStaleMinimum");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->NeuronClassName = "NSPNeuronGenAsymRmD001C1e9";
    learner->ResistanceMin.SetDataDirect(2.0e7);
    learner->SynapseResistanceBase = 1.0e7;
    learner->TipSynapseResistance = {1.0e7, 1.0e7, 1.0e7};
    learner->InitialSomaPotential = {0.01, 0.01, 0.01};

    ASSERT_TRUE(BuildAndReset(learner));

    const auto tips = learner->TipSynapseResistance.GetData();
    const auto minima = learner->ResistanceMinByInput.GetData();
    ASSERT_EQ(tips.size(), 3u);
    ASSERT_EQ(minima.size(), 2u);
    for (size_t i = 0; i < tips.size(); ++i)
    {
        const double expected = i < minima.size()
            ? std::max(1.0e7, minima[i]) : 1.0e7;
        EXPECT_DOUBLE_EQ(tips[i], expected)
            << "derived per-input bounds must not replace a configured Rs=10 MOhm cold start with the old 20 MOhm state";
        EXPECT_LT(tips[i], 2.0e7);
    }
    EXPECT_LT(learner->ResistanceMin.GetData(), 2.0e7);
}

TEST_F(TimeLearnerResistanceTest, BranchParametricColdStartIgnoresStaleSerializedMinimum)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchStaleMinimum");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->NeuronClassName = "NSPNeuronGenAsymRmD001C1e9";
    learner->ResistanceMin.SetDataDirect(2.0e7);
    learner->SynapseResistanceBase = 1.0e7;
    learner->TipSynapseResistance = {1.0e7, 1.0e7, 1.0e7};
    learner->InitialSomaPotential = {0.01, 0.01, 0.01};

    ASSERT_TRUE(BuildAndReset(learner));

    const auto tips = learner->TipSynapseResistance.GetData();
    const auto minima = learner->ResistanceMinByInput.GetData();
    ASSERT_EQ(tips.size(), 3u);
    ASSERT_EQ(minima.size(), 2u);
    for (size_t i = 0; i < tips.size(); ++i)
    {
        const double expected = i < minima.size()
            ? std::max(1.0e7, minima[i]) : 1.0e7;
        EXPECT_DOUBLE_EQ(tips[i], expected)
            << "derived per-input bounds must not replace a configured Rs=10 MOhm cold start with the old 20 MOhm state";
        EXPECT_LT(tips[i], 2.0e7);
    }
    EXPECT_LT(learner->ResistanceMin.GetData(), 2.0e7);
}

TEST_F(TimeLearnerResistanceTest, ClassicColdResetCanKeepExplicitPerInputTipResistance)
{
    auto learner = CreateLearner("TimeLearnerClassicLoadedTipReset");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->NeuronClassName = "NSPNeuronGenAsymRmD001C1e9";
    learner->SynapseResistanceBase = 8.6e7;
    learner->TipSynapseResistance = {8.6e7, 8.6e7, 8.6e7};
    learner->InitialSomaPotential = {0.01, 0.01, 0.01};
    learner->Build();
    ASSERT_TRUE(learner->IsReady());
    model->Build();
    ASSERT_TRUE(model->IsReady());
    model->Init();
    // Mimic the runtime per-input diagnostic overlay arriving after the cold
    // snapshot was captured, while keeping the final reference anchor fixed.
    learner->TipSynapseResistance = {5.0e7, 6.0e7, 8.6e7};
    learner->UseLoadedTipResistanceOnUntrainedReset = true;
    learner->ResetToUntrainedState = true;
    model->Reset();

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_EQ(tips.size(), 3u);
    EXPECT_DOUBLE_EQ(tips[0], 5.0e7);
    EXPECT_DOUBLE_EQ(tips[1], 6.0e7);
    EXPECT_DOUBLE_EQ(tips[2], 8.6e7)
        << "the configured reference anchor must remain independent of trainable tips";
}

TEST_F(TimeLearnerResistanceTest, BranchColdResetCanKeepExplicitPerInputTipResistance)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchLoadedTipReset");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->NeuronClassName = "NSPNeuronGenAsymRmD001C1e9";
    learner->SynapseResistanceBase = 8.6e7;
    learner->TipSynapseResistance = {8.6e7, 8.6e7, 8.6e7};
    learner->InitialSomaPotential = {0.01, 0.01, 0.01};
    learner->Build();
    ASSERT_TRUE(learner->IsReady());
    model->Build();
    ASSERT_TRUE(model->IsReady());
    model->Init();
    learner->TipSynapseResistance = {5.0e7, 6.0e7, 8.6e7};
    learner->UseLoadedTipResistanceOnUntrainedReset = true;
    learner->ResetToUntrainedState = true;
    model->Reset();

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_EQ(tips.size(), 3u);
    EXPECT_DOUBLE_EQ(tips[0], 5.0e7);
    EXPECT_DOUBLE_EQ(tips[1], 6.0e7);
    EXPECT_DOUBLE_EQ(tips[2], 8.6e7)
        << "the configured reference anchor must remain independent of trainable tips";
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
    EXPECT_TRUE(learner->ResistanceMinByInput.GetData().empty())
        << "input-specific parametric bounds must not survive in structural mode";
    learner->EnableRmaxLengthEscape = true;
    const double baseResistance = learner->SynapseResistanceBase.GetData();
    ASSERT_TRUE(BuildAndReset(learner));

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0);
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0);
    EXPECT_TRUE(learner->ResistanceMinByInput.GetData().empty());
    EXPECT_DOUBLE_EQ(learner->SynapseResistanceBase.GetData(), baseResistance);
    EXPECT_DOUBLE_EQ(tips[0], baseResistance);
    EXPECT_DOUBLE_EQ(tips[1], baseResistance);
}

TEST_F(TimeLearnerResistanceTest, ClassicStructuralRejectsTimeScaleUnstableForAnyRs)
{
    constexpr const char* kFastNeuron = "NSPNeuronGenAsymRmD001C1e11";
    ASSERT_TRUE(storage->CheckClass(kFastNeuron));
    auto learner = CreateLearner("TimeLearnerClassicNoStableStep");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    learner->NeuronClassName = kFastNeuron;

    learner->Build();
    EXPECT_TRUE(learner->IsReady())
        << "Build's bool result is not the failure contract; the component exposes its preflight state";
    EXPECT_EQ(learner->TrainingPhase.GetData(), 4);
    EXPECT_EQ(learner->TrainingFailureReason.GetData(), 2);
    EXPECT_TRUE(learner->SetIsNeedToTrain(true));
    EXPECT_EQ(learner->TrainingPhase.GetData(), 4)
        << "raising IsNeedToTrain must not clear an impossible integration step";
    learner->Reset();
    EXPECT_EQ(learner->TrainingPhase.GetData(), 4)
        << "Reset must preserve the integration preflight failure";
}

TEST_F(TimeLearnerResistanceTest, BranchStructuralRejectsTimeScaleUnstableForAnyRs)
{
    constexpr const char* kFastNeuron = "NSPNeuronGenAsymRmD001C1e11";
    ASSERT_TRUE(storage->CheckClass(kFastNeuron));
    auto learner = CreateBranchLearner("TimeLearnerBranchNoStableStep");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    learner->NeuronClassName = kFastNeuron;

    learner->Build();
    EXPECT_TRUE(learner->IsReady())
        << "Build's bool result is not the failure contract; the component exposes its preflight state";
    EXPECT_EQ(learner->TrainingPhase.GetData(), 5);
    EXPECT_EQ(learner->TrainingFailureReason.GetData(), 4);
    EXPECT_TRUE(learner->SetIsNeedToTrain(true));
    EXPECT_EQ(learner->TrainingPhase.GetData(), 5)
        << "raising IsNeedToTrain must not clear an impossible integration step";
    learner->Reset();
    EXPECT_EQ(learner->TrainingPhase.GetData(), 5)
        << "Reset must preserve the integration preflight failure";
}

TEST_F(TimeLearnerResistanceTest, ClassicChecksAllMembranesAndSkipsCalculationAfterPreflightFailure)
{
    auto learner = CreateLearner("TimeLearnerClassicSomaPreflight");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));
    learner->NormalizationMode = 1;
    learner->StructureBuildMode = 0;
    learner->Build();
    ASSERT_TRUE(learner->IsReady());
    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto soma = neuron->GetComponentL<NMSDK::NPulseMembrane>("Soma1", true);
    ASSERT_TRUE(soma);
    auto* channel = dynamic_cast<NMSDK::NPulseChannel*>(soma->GetPosChannel(0));
    ASSERT_NE(channel, nullptr);
    const double output_before = channel->Output(0, 0);
    channel->Capacity = 1.0e-11;

    EXPECT_FALSE(learner->SetMaxSynapseToMembraneResistanceRatio(
        learner->MaxSynapseToMembraneResistanceRatio.GetData()))
        << "the soma must be checked even though it is not a synaptic target tip";
    EXPECT_EQ(learner->TrainingFailureReason.GetData(), 2);
    EXPECT_EQ(learner->TrainingPhase.GetData(), 4);
    ASSERT_TRUE(learner->IsReady());
    learner->Calculate();
    EXPECT_DOUBLE_EQ(channel->Output(0, 0), output_before)
        << "the rejected learner must skip its unstable neuron child calculation";
}

TEST_F(TimeLearnerResistanceTest, BranchChecksAllMembranesAndSkipsCalculationAfterPreflightFailure)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchSomaPreflight");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));
    learner->NormalizationMode = 1;
    learner->StructureBuildMode = 0;
    learner->Build();
    ASSERT_TRUE(learner->IsReady());
    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto soma = neuron->GetComponentL<NMSDK::NPulseMembrane>("Soma1", true);
    ASSERT_TRUE(soma);
    auto* channel = dynamic_cast<NMSDK::NPulseChannel*>(soma->GetPosChannel(0));
    ASSERT_NE(channel, nullptr);
    const double output_before = channel->Output(0, 0);
    channel->Capacity = 1.0e-11;

    EXPECT_FALSE(learner->SetMaxSynapseToMembraneResistanceRatio(
        learner->MaxSynapseToMembraneResistanceRatio.GetData()))
        << "the soma must be checked even though it is not a synaptic target tip";
    EXPECT_EQ(learner->TrainingFailureReason.GetData(), 4);
    EXPECT_EQ(learner->TrainingPhase.GetData(), 5);
    ASSERT_TRUE(learner->IsReady());
    learner->Calculate();
    EXPECT_DOUBLE_EQ(channel->Output(0, 0), output_before)
        << "the rejected learner must skip its unstable neuron child calculation";
}

TEST_F(TimeLearnerResistanceTest, ResistanceRatioMustBeAtLeastOne)
{
    auto classic = CreateLearner("TimeLearnerRatioBoundary");
    ASSERT_TRUE(classic);
    classic->NormalizationMode = 0; // isolate parameter-domain validation from live stability feasibility
    EXPECT_FALSE(classic->SetMaxSynapseToMembraneResistanceRatio(0.999));
    EXPECT_TRUE(classic->SetMaxSynapseToMembraneResistanceRatio(1.0));
    classic->MaxSynapseToMembraneResistanceRatio = 1.0;
    EXPECT_DOUBLE_EQ(classic->MaxSynapseToMembraneResistanceRatio.GetData(), 1.0);
}

TEST_F(TimeLearnerResistanceTest, AllowsPerInputRatioOneWithoutFalseGlobalIntervalFailure)
{
    auto classic = CreateLearner("TimeLearnerRatioStabilityConflict");
    ASSERT_TRUE(classic);
    classic->NormalizationMode = 1;
    ASSERT_TRUE(BuildAndReset(classic));
    auto neuron = classic->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto secondMembrane = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite2_1", true);
    ASSERT_TRUE(secondMembrane);
    ASSERT_GT(secondMembrane->GetNumPosChannels(), 0);
    auto* secondChannel = dynamic_cast<NMSDK::NPulseChannel*>(secondMembrane->GetPosChannel(0));
    ASSERT_NE(secondChannel, nullptr);
    secondChannel->RestingResistance = 2.0e7;
    ASSERT_TRUE(classic->SetMaxSynapseToMembraneResistanceRatio(1.0));
    EXPECT_DOUBLE_EQ(classic->MaxSynapseToMembraneResistanceRatio.GetData(), 1.0);
    EXPECT_GT(classic->ResistanceMin.GetData(), classic->ResistanceMax.GetData())
        << "the diagnostic common interval may be empty when tips have different Rm";
    const auto minima = classic->ResistanceMinByInput.GetData();
    const auto maxima = classic->ResistanceMaxByInput.GetData();
    const auto tips = classic->TipSynapseResistance.GetData();
    ASSERT_EQ(minima.size(), 2u);
    ASSERT_EQ(maxima.size(), minima.size());
    ASSERT_GE(tips.size(), minima.size());
    for(size_t i = 0; i < minima.size(); ++i)
    {
        EXPECT_DOUBLE_EQ(minima[i], maxima[i]);
        EXPECT_NEAR(tips[i], minima[i], std::max(1e-6, minima[i] * 1e-9));
    }
    EXPECT_NEAR(minima[0], 1.0e7, 1.0e-6);
    EXPECT_NEAR(minima[1], 2.0e7, 1.0e-6);
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
    double minRm = std::numeric_limits<double>::max();
    double stabilityMinRatio = 0.0;
    auto membrane = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_1", true);
    ASSERT_TRUE(membrane);
    ASSERT_GT(membrane->GetNumPosChannels(), 0);
    auto* channel = dynamic_cast<NMSDK::NPulseChannel*>(membrane->GetPosChannel(0));
    ASSERT_NE(channel, nullptr);
    const double rm = channel->RestingResistance.GetData() > 0.0
        ? channel->RestingResistance.GetData()
        : channel->Resistance.GetData();
    ASSERT_GT(rm, 0.0);
    minRm = rm;
    const double channelRs[] = {
        channel->Resistance.GetData(),
        channel->RestingResistance.GetData(),
        channel->FBResistance.GetData()
    };
    for (double candidateRs : channelRs)
    {
        const auto floor = NMSDK::TimeLearnerResistanceBounds::ComputeNoCrossingResistanceFloor(
            channel->Capacity.GetData(), candidateRs,
            static_cast<double>(channel->TimeStep.GetData()),
            std::max(1, channel->GetNumSynapses()));
        ASSERT_EQ(floor.status, NMSDK::TimeLearnerResistanceBounds::FloorStatus::Ok);
        stabilityMinRatio = std::max(stabilityMinRatio, floor.minimumResistance / rm);
    }

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);
    const double configuredRs = learner->SynapseResistanceBase.GetData();
    EXPECT_NEAR(tips[0], configuredRs, std::max(1e-6, configuredRs * 1e-9));
    EXPECT_NEAR(tips[1], configuredRs, std::max(1e-6, configuredRs * 1e-9));
    EXPECT_NEAR(learner->ResistanceMax.GetData(), minRm * 1000.0,
                std::max(1e-6, minRm * 1e-6));
    const double expectedMinRatio = std::max(1.0 / 1000.0, stabilityMinRatio);
    const double expectedMinRs = rm * expectedMinRatio;
    EXPECT_NEAR(learner->ResistanceMin.GetData(), expectedMinRs,
                std::max(1e-6, expectedMinRs * 1e-9));
    EXPECT_NEAR(learner->ResistanceMinRatio.GetData(), expectedMinRatio, 1e-12);
    const auto actualMinima = learner->ResistanceMinByInput.GetData();
    const auto actualRatios = learner->ResistanceMinRatioByInput.GetData();
    ASSERT_EQ(actualMinima.size(), 2u);
    ASSERT_EQ(actualRatios.size(), 2u);
    for(size_t i = 0; i < actualMinima.size(); ++i)
    {
        EXPECT_NEAR(actualMinima[i], expectedMinRs, std::max(1e-6, expectedMinRs * 1e-9));
        EXPECT_NEAR(actualRatios[i], expectedMinRatio, 1e-12);
    }
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
    EXPECT_TRUE(learner->ResistanceMinByInput.GetData().empty())
        << "input-specific parametric bounds must not survive in structural mode";
    learner->EnableRmaxLengthEscape = true;
    const double baseResistance = learner->SynapseResistanceBase.GetData();
    ASSERT_TRUE(BuildAndReset(learner));

    const auto tips = learner->TipSynapseResistance.GetData();
    ASSERT_GE(tips.size(), 2u);
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0);
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0);
    EXPECT_TRUE(learner->ResistanceMinByInput.GetData().empty());
    EXPECT_DOUBLE_EQ(learner->SynapseResistanceBase.GetData(), baseResistance);
    EXPECT_DOUBLE_EQ(tips[0], baseResistance);
    EXPECT_DOUBLE_EQ(tips[1], baseResistance);
}

TEST_F(TimeLearnerResistanceTest, BranchStructuralSynapseMultiplicityIsDrivenByGenerator)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchStructuralSynapseWiring");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));
    learner->DendriteLength = {1, 1, 1};
    learner->NumSynapse = {1, 3, 1};
    learner->Build();
    ASSERT_TRUE(learner->IsReady());

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto tip = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_1", true);
    ASSERT_TRUE(tip);
    auto exc_channel = tip->GetComponentL<NMSDK::NPulseChannelCommon>("ExcChannel", true);
    ASSERT_TRUE(exc_channel);
    ASSERT_EQ(int(tip->NumExcitatorySynapses), 3)
        << "structural NumSynapse must survive Build/Reset at its attach segment; NumSynapse=["
        << learner->NumSynapse[0] << ',' << learner->NumSynapse[1] << ','
        << learner->NumSynapse[2] << "] DendriteLength=["
        << learner->DendriteLength[0] << ',' << learner->DendriteLength[1] << ','
        << learner->DendriteLength[2] << ']';

    for (int index = 1; index <= 3; ++index)
    {
        auto synapse = tip->GetComponentL<NMSDK::NPulseSynapseCommon>(
            std::string("ExcSynapse") + std::to_string(index), true);
        ASSERT_TRUE(synapse) << "missing structural synapse " << index;
        EXPECT_TRUE(synapse->Input.IsConnected())
            << "every structural synapse contributing to this pulse must receive Generator1";
        ASSERT_NE(synapse->Input.GetItem(), nullptr);
        EXPECT_EQ(synapse->Input.GetItem()->GetName(), "Generator1");
        auto* channel_input = exc_channel->SynapticInputs.GetItem(index - 1);
        ASSERT_NE(channel_input, nullptr);
        EXPECT_EQ(channel_input->GetName(), synapse->GetName());
    }
    EXPECT_EQ(exc_channel->SynapticInputs.GetNumPointers(), 3)
        << "every created structural synapse must remain linked to its membrane ExcChannel";
}

TEST_F(TimeLearnerResistanceTest, BranchDynamicallyAddedStructuralSynapsesAreActiveAndInitialized)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchDynamicSynapseLifecycle");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto tip = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_1", true);
    ASSERT_TRUE(tip);
    ASSERT_TRUE(tip->GetActivity());
    ASSERT_TRUE(tip->IsInit());
    ASSERT_EQ(tip->NumExcitatorySynapses.GetData(), 1);

    // Mirror ChangeSynapseNumber's live structural update: rebuild the
    // membrane, then apply neuron-wide parameters without rebuilding the
    // complete neuron tree.
    tip->NumExcitatorySynapses = 3;
    tip->Build();
    ASSERT_TRUE(tip->IsReady());
    ASSERT_TRUE(tip->IsInit());
    neuron->ApplyElementDefaults();

    for (int index = 1; index <= 3; ++index)
    {
        auto synapse = tip->GetComponentL<NMSDK::NPulseSynapseCommon>(
            std::string("ExcSynapse") + std::to_string(index), true);
        ASSERT_TRUE(synapse) << "missing dynamic structural synapse " << index;
        EXPECT_TRUE(synapse->GetActivity())
            << "dynamic structural synapse " << index << " is inactive after membrane Build";
        EXPECT_TRUE(synapse->IsInit())
            << "dynamic structural synapse " << index << " is not initialized after membrane Build";
    }
}

TEST_F(TimeLearnerResistanceTest, BranchDynamicallyAddedInhibitorySynapseIsActiveAndInitialized)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchDynamicNextSegSynapseLifecycle");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    // The cold reset intentionally returns the cable to length one. Build an
    // initialized second segment so this exercises adding NextSeg inhibition
    // to an already-running membrane.
    neuron->NumDendriteMembranePartsVec = {2};
    neuron->Build();
    ASSERT_TRUE(neuron->IsReady());
    neuron->Reset();
    auto segment = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_2", true);
    ASSERT_TRUE(segment);
    if (!segment->GetActivity())
        segment->SetActivity(true);
    if (!segment->IsInit())
        segment->Init();
    ASSERT_TRUE(segment->GetActivity());
    ASSERT_TRUE(segment->IsInit());

    // Remove the default child, then recreate it as EnsureNextSegInhSynapseOnSegment does.
    segment->NumInhibitorySynapses = 0;
    segment->Build();
    ASSERT_TRUE(segment->IsReady());
    EXPECT_FALSE(segment->GetComponentL<NMSDK::NPulseSynapseCommon>("InhSynapse1", true));
    segment->NumInhibitorySynapses = 1;
    segment->Build();
    ASSERT_TRUE(segment->IsReady());
    ASSERT_TRUE(segment->IsInit());
    neuron->ApplyElementDefaults();

    auto synapse = segment->GetComponentL<NMSDK::NPulseSynapseCommon>("InhSynapse1", true);
    ASSERT_TRUE(synapse);
    EXPECT_TRUE(synapse->GetActivity());
    EXPECT_TRUE(synapse->IsInit());
}

TEST_F(TimeLearnerResistanceTest, ClassicStructuralSynapseOutputsSurviveGeneratorRelink)
{
    auto learner = CreateLearner("TimeLearnerClassicStructuralSynapseWiring");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));
    learner->DendriteLength = {1, 1, 1};
    learner->NumSynapse = {3, 1, 1};
    learner->Build();
    ASSERT_TRUE(learner->IsReady());

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto tip = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_1", true);
    ASSERT_TRUE(tip);
    auto exc_channel = tip->GetComponentL<NMSDK::NPulseChannelCommon>("ExcChannel", true);
    ASSERT_TRUE(exc_channel);
    ASSERT_EQ(int(tip->NumExcitatorySynapses), 3);

    for (int index = 1; index <= 3; ++index)
    {
        auto synapse = tip->GetComponentL<NMSDK::NPulseSynapseCommon>(
            std::string("ExcSynapse") + std::to_string(index), true);
        ASSERT_TRUE(synapse) << "missing structural synapse " << index;
        EXPECT_TRUE(synapse->Input.IsConnected());
        ASSERT_NE(synapse->Input.GetItem(), nullptr);
        EXPECT_EQ(synapse->Input.GetItem()->GetName(), "Generator1");
        auto* channel_input = exc_channel->SynapticInputs.GetItem(index - 1);
        ASSERT_NE(channel_input, nullptr);
        EXPECT_EQ(channel_input->GetName(), synapse->GetName());
    }
    EXPECT_EQ(exc_channel->SynapticInputs.GetNumPointers(), 3)
        << "the structural synapses must remain connected to their membrane ExcChannel";
}

TEST_F(TimeLearnerResistanceTest, ClassicDynamicallyAddedStructuralSynapsesAreActiveAndInitialized)
{
    auto learner = CreateLearner("TimeLearnerClassicDynamicSynapseLifecycle");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    ASSERT_TRUE(BuildAndReset(learner));

    auto neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
    ASSERT_TRUE(neuron);
    auto tip = neuron->GetComponentL<NMSDK::NPulseMembrane>("Dendrite1_1", true);
    ASSERT_TRUE(tip);
    ASSERT_TRUE(tip->GetActivity());
    ASSERT_TRUE(tip->IsInit());
    ASSERT_EQ(tip->NumExcitatorySynapses.GetData(), 1);

    // Mirror NNeuronTimeLearner::ChangeSynapseNumber after the initial build.
    tip->NumExcitatorySynapses = 3;
    tip->Build();
    ASSERT_TRUE(tip->IsReady());
    ASSERT_TRUE(tip->IsInit());
    neuron->ApplyElementDefaults();

    for (int index = 1; index <= 3; ++index)
    {
        auto synapse = tip->GetComponentL<NMSDK::NPulseSynapseCommon>(
            std::string("ExcSynapse") + std::to_string(index), true);
        ASSERT_TRUE(synapse) << "missing dynamic structural synapse " << index;
        EXPECT_TRUE(synapse->GetActivity())
            << "dynamic structural synapse " << index << " is inactive after membrane Build";
        EXPECT_TRUE(synapse->IsInit())
            << "dynamic structural synapse " << index << " is not initialized after membrane Build";
    }
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
        ActivePulseIndex = 0;
        InputPattern.Assign(2, 1, 0.0);
        PrevInputPattern.Assign(2, 1, 0.0);
    }

    void SetAmpError(double dt)
    {
        MaxIterSomaAmp[0] = InitialSomaPotential[0] - dt;
    }

    void SetNearTargetResistance(double resistance)
    {
        TipSynapseResistance[0] = resistance;
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

    int NoImproveCount() const
    {
        return NoImproveResistanceCount[0];
    }

    bool IsAmpNormalized() const
    {
        return AllSynapsesNormalized();
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

TEST(BranchAmpNormOscillationTest, RepeatedCrossingsReachExistingNearTargetEol)
{
    BranchPathologicalAmpHarness learner;
    learner.Default();
    learner.SetAmpState(0.015781 - 1.1e-5);
    learner.SetNearTargetResistance(717430.0);

    for (const double dt : {1.1e-5, -3.4e-5, 1.1e-5})
    {
        learner.SetAmpError(dt);
        ASSERT_TRUE(learner.Tune());
    }

    EXPECT_EQ(learner.NoImproveCount(), 3)
        << "a smaller residual on the opposite side of the target is an oscillation, not progress";
    EXPECT_EQ(learner.PendingResistanceStatus(), 0);
    EXPECT_TRUE(learner.IsAmpNormalized())
        << "the existing near-target EOL should accept the repeated bounded oscillation";
}

class ClassicStructuralDeadTipHarness : public NMSDK::NNeuronTimeLearner
{
public:
    void SetDeadTipState(int synapseCount)
    {
        NumInputDendrite = 2;
        NormalizationMode = 0;
        AcceptQuantizedAmpUnderTarget = false;
        DendriteLength = {59, 1};
        NumSynapse = {synapseCount, 1};
        InitialSomaPotential = {0.015828572406203167, 0.015828572406203167};
        MaxIterSomaAmp = {7.932737848825866e-7, 0.0};
        SomaPeakValid = {false, true};
        DendLastAbsDt = {0.000269921, 1.500999};
        DendBestEffortSynced = {true, false};
        DendStatus.assign(2, 0);
        SynapseStatus.assign(2, 0);
        AmpDifference.assign(2, 0.0);
        InputPattern.Assign(2, 1, 0.0);
        PrevInputPattern.Assign(2, 1, 0.0);
    }

    bool Decide() { return ChangeSynapseStatus(0); }
    int PendingCountChange() const { return SynapseStatus[0]; }
    bool IsAmpNormalized() const { return AllSynapsesNormalized(); }

    void SetUnmeasuredPeakState()
    {
        MaxIterSomaAmp = {0.0, 0.0};
        PeakSeen.assign(2, false);
    }
};

class BranchStructuralDeadTipHarness : public NMSDK::NNeuronTimeLearnerBranch
{
public:
    void SetDeadTipState(int synapseCount)
    {
        NumInputDendrite = 2;
        NormalizationMode = 0;
        AcceptQuantizedAmpUnderTarget = false;
        DendriteLength = {59, 1};
        NumSynapse = {synapseCount, 1};
        InitialSomaPotential = {0.015828572406203167, 0.015828572406203167};
        MaxIterSomaAmp = {7.932737848825866e-7, 0.0};
        SomaPeakValid = {false, true};
        DendLastAbsDt = {0.000269921, 1.500999};
        DendBestEffortSynced = {true, false};
        DendStatus.assign(2, 0);
        SynapseStatus.assign(2, 0);
        AmpDifference.assign(2, 0.0);
        InputPattern.Assign(2, 1, 0.0);
        PrevInputPattern.Assign(2, 1, 0.0);
    }

    bool Decide() { return ChangeSynapseStatus(0); }
    int PendingCountChange() const { return SynapseStatus[0]; }
    bool IsAmpNormalized() const { return AllSynapsesNormalized(); }

    void SetUnmeasuredPeakState()
    {
        MaxIterSomaAmp = {0.0, 0.0};
        PeakSeen.assign(2, false);
    }
};

TEST(StructuralDeadTipRecoveryTest, ClassicContinuesAddingBelowTheStructuralCap)
{
    ClassicStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(8);

    ASSERT_TRUE(learner.Decide());
    EXPECT_EQ(learner.PendingCountChange(), 1)
        << "a best-effort timing estimate must not suppress the only structural amplitude control";
}

TEST(StructuralDeadTipRecoveryTest, ClassicStopsAddingAtTheStructuralCap)
{
    ClassicStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(128);

    ASSERT_TRUE(learner.Decide());
    EXPECT_EQ(learner.PendingCountChange(), 0);
}

TEST(StructuralDeadTipRecoveryTest, ClassicDoesNotAcceptUnmeasurableAmplitudeBelowCap)
{
    ClassicStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(8);

    EXPECT_FALSE(learner.IsAmpNormalized());
}

TEST(StructuralDeadTipRecoveryTest, ClassicAcceptsUnmeasurableAmplitudeAtCap)
{
    ClassicStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(128);

    EXPECT_TRUE(learner.IsAmpNormalized());
}

TEST(StructuralDeadTipRecoveryTest, BranchContinuesAddingBelowTheStructuralCap)
{
    BranchStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(8);

    ASSERT_TRUE(learner.Decide());
    EXPECT_EQ(learner.PendingCountChange(), 1)
        << "a best-effort timing estimate must not suppress the only structural amplitude control";
}

TEST(StructuralDeadTipRecoveryTest, BranchDoesNotAddWhenPeakWasNeverMeasured)
{
    BranchStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(8);
    learner.SetUnmeasuredPeakState();

    ASSERT_TRUE(learner.Decide());
    EXPECT_EQ(learner.PendingCountChange(), 0)
        << "PeakLocked/unmeasured bursts must not grow N from Initial-vs-zero amp";
}

TEST(StructuralDeadTipRecoveryTest, ClassicDoesNotAddWhenPeakWasNeverMeasured)
{
    ClassicStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(8);
    learner.SetUnmeasuredPeakState();

    ASSERT_TRUE(learner.Decide());
    EXPECT_EQ(learner.PendingCountChange(), 0)
        << "PeakLocked/unmeasured bursts must not grow N from Initial-vs-zero amp";
}

TEST(StructuralDeadTipRecoveryTest, BranchStopsAddingAtTheStructuralCap)
{
    BranchStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(128);

    ASSERT_TRUE(learner.Decide());
    EXPECT_EQ(learner.PendingCountChange(), 0);
}

TEST(StructuralDeadTipRecoveryTest, BranchDoesNotAcceptUnmeasurableAmplitudeBelowCap)
{
    BranchStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(8);

    EXPECT_FALSE(learner.IsAmpNormalized());
}

TEST(StructuralDeadTipRecoveryTest, BranchAcceptsUnmeasurableAmplitudeAtCap)
{
    BranchStructuralDeadTipHarness learner;
    learner.Default();
    learner.SetDeadTipState(128);

    EXPECT_TRUE(learner.IsAmpNormalized());
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
