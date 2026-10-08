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

TEST_F(TimeLearnerResistanceTest, ParametricColdStartUsesTargetRmAndDerivedCeiling)
{
    auto learner = CreateLearner("TimeLearnerParametricResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->InitialSynapseToMembraneResistanceRatio = 2.0;
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
        const double expectedRs = std::max(learner->ResistanceMin.GetData(), rm * 2.0);
        EXPECT_NEAR(tips[static_cast<size_t>(i)], expectedRs,
                    std::max(1e-6, expectedRs * 1e-9));
    }

    EXPECT_NEAR(learner->ResistanceMax.GetData(), minRm * 1000.0,
                std::max(1e-6, minRm * 1e-6));
    EXPECT_NEAR(learner->ResistanceMin.GetData(), maxRm / 1000.0,
                std::max(1e-6, maxRm * 1e-9));
    EXPECT_FALSE(learner->EnableRmaxLengthEscape.GetData());
}

TEST_F(TimeLearnerResistanceTest, StructuralColdStartDoesNotApplyParametricRatios)
{
    auto learner = CreateLearner("TimeLearnerStructuralResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only cap";
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only floor";
    learner->InitialSynapseToMembraneResistanceRatio = 17.0;
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

TEST_F(TimeLearnerResistanceTest, BranchParametricColdStartUsesTargetRmAndDerivedCeiling)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchParametricResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 1;
    learner->InitialSynapseToMembraneResistanceRatio = 2.0;
    ASSERT_TRUE(BuildAndReset(learner));

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
    const double expectedRs = std::max(learner->ResistanceMin.GetData(), rm * 2.0);
    EXPECT_NEAR(tips[0], expectedRs, std::max(1e-6, expectedRs * 1e-9));
    EXPECT_NEAR(tips[1], expectedRs, std::max(1e-6, expectedRs * 1e-9));
    EXPECT_NEAR(learner->ResistanceMax.GetData(), rm * 1000.0,
                std::max(1e-6, rm * 1e-6));
    EXPECT_NEAR(learner->ResistanceMin.GetData(), rm / 1000.0,
                std::max(1e-6, rm * 1e-9));
}

TEST_F(TimeLearnerResistanceTest, BranchStructuralColdStartDoesNotApplyParametricRatios)
{
    auto learner = CreateBranchLearner("TimeLearnerBranchStructuralResistance");
    ASSERT_TRUE(learner);
    learner->NormalizationMode = 0;
    EXPECT_DOUBLE_EQ(learner->ResistanceMax.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only cap";
    EXPECT_DOUBLE_EQ(learner->ResistanceMin.GetData(), 0.0)
        << "switching to structural mode must clear the parametric-only floor";
    learner->InitialSynapseToMembraneResistanceRatio = 17.0;
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
