#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseLTZone.h"
#include "../Support/ConsoleLikeInit.h"

#include <limits>
#include <string>
#include <vector>

namespace {
class IsiAnalyzerProbe : public NMSDK::NPatternResponseAnalyzer
{
public:
    using NPatternResponseAnalyzer::BeginTrial;
    using NPatternResponseAnalyzer::AppendStim;
    using NPatternResponseAnalyzer::CloseTrial;
    using NPatternResponseAnalyzer::IsIsiTemplateMatch;
    using NPatternResponseAnalyzer::ReadLtzPotential;
    void Label(int label) { trial_target_class_ = label; }
};

class IsiTemplateValidation : public ::testing::Test
{
protected:
    RDK::UEPtr<RDK::UContainer> model;
    RDK::UEPtr<NMSDK::NPulseNeuron> neuron;
    RDK::UEPtr<IsiAnalyzerProbe> analyzer;

    void MakeFixture(const std::string& learnerClass)
    {
        analyzer = nullptr;
        neuron = nullptr;
        model = nullptr;
        const auto& core = NmsdkTests::InitEngineForPulseLibTests();
        core.environment->DestroyModel();
        ASSERT_TRUE(core.environment->CreateModel("NModel"));
        core.environment->ModelInit();
        model = core.environment->GetModel();
        ASSERT_TRUE(model);
        // Real storage objects and real owner lookup. No copied comparator or
        // learner Build is needed to inspect the declared template property.
        auto learner = RDK::dynamic_pointer_cast<RDK::UContainer>(core.storage->TakeObject(learnerClass));
        ASSERT_TRUE(learner);
        learner->Name = "TemplateLearner";
        ASSERT_NE(model->AddComponent(learner), RDK::ForbiddenId);
        neuron = learner->GetComponentL<NMSDK::NPulseNeuron>("Neuron", true);
        if(!neuron)
        {
            neuron = RDK::dynamic_pointer_cast<NMSDK::NPulseNeuron>(core.storage->TakeObject("NSPNeuronGen"));
            ASSERT_TRUE(neuron);
            neuron->Name = "Neuron";
            ASSERT_NE(learner->AddComponent(neuron), RDK::ForbiddenId);
        }
        analyzer = RDK::UEPtr<IsiAnalyzerProbe>(new IsiAnalyzerProbe);
        analyzer->SetStorage(core.storage);
        analyzer->SetEnvironment(core.environment);
        analyzer->Default();
        analyzer->Name = "TemplateAnalyzer";
        analyzer->LearnerComponentName = "TemplateLearner";
        analyzer->MatchMode = 1;
        analyzer->Enable = false; // Inspect outputs without creating a CSV in cwd.
        ASSERT_NE(model->AddComponent(analyzer), RDK::ForbiddenId);
    }

    void TearDown() override
    {
        analyzer = nullptr;
        neuron = nullptr;
        model = nullptr;
        NmsdkTests::InitEngineForPulseLibTests().environment->DestroyModel();
    }

    void Reference(std::vector<double> values)
    {
        RDK::MDMatrix<double> pattern;
        pattern.Resize(static_cast<int>(values.size()), 1);
        for(size_t i = 0; i < values.size(); ++i)
            pattern(static_cast<int>(i), 0) = values[i];
        neuron->TrainingPattern.SetDataDirect(pattern);
    }

    void Present(int label, double second = 10.08)
    {
        analyzer->BeginTrial(10.0);
        analyzer->Label(label);
        analyzer->AppendStim(second);
        analyzer->AppendStim(10.24);
        analyzer->AppendStim(10.48);
    }

    void ExpectInvalid()
    {
        EXPECT_FALSE(analyzer->IsIsiTemplateMatch());
        analyzer->CloseTrial(20.0);
        // CloseTrial resets temporary probe state. Inspect the retained result,
        // rather than a flag that now belongs to the next, empty observation.
        EXPECT_EQ(analyzer->LastMatch.GetData(), 0);
        EXPECT_EQ(analyzer->LastErrorClass.GetData(), "invalid_measurement");
    }
};

TEST_F(IsiTemplateValidation, ResolvesActualLearnerAndKeepsFiniteTolerance)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        Reference({.01, .08, .16, .24});
        Present(1);
        EXPECT_TRUE(analyzer->IsIsiTemplateMatch());
        Reference({.08, .16, .24}); // Historical gap-only representation.
        EXPECT_TRUE(analyzer->IsIsiTemplateMatch());
        Reference({.01, .081, .16, .24});
        EXPECT_FALSE(analyzer->IsIsiTemplateMatch());
        analyzer->CloseTrial(20.0);
        EXPECT_NE(analyzer->LastErrorClass.GetData(), "invalid_measurement");
    }
}

TEST_F(IsiTemplateValidation, NonfiniteReferenceInvalidatesTargetAndFoil)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        for(double bad : {std::numeric_limits<double>::quiet_NaN(),
                          std::numeric_limits<double>::infinity(),
                          -std::numeric_limits<double>::infinity()})
            for(int label : {0, 1})
            {
                Reference({.01, bad, .16, .24});
                Present(label);
                ExpectInvalid();
            }
    }
}

TEST_F(IsiTemplateValidation, NonfiniteStimulusCannotBecomeTemplateMatch)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        Reference({.01, .08, .16, .24});
        for(int label : {0, 1})
        {
            Present(label, std::numeric_limits<double>::quiet_NaN());
            ExpectInvalid();
        }
    }
}

TEST_F(IsiTemplateValidation, MissingTemplateCannotBecomeSuccessfulFoil)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        Reference({.01, .08, .16, .24});
        analyzer->LearnerComponentName = "AbsentLearner";
        for(int label : {0, 1})
        {
            Present(label);
            ExpectInvalid();
        }
    }
}

TEST_F(IsiTemplateValidation, LazyLtzLookupUsesActualNeuronForBothTopologies)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        auto ltz = neuron->GetComponentL<NMSDK::NPulseLTZoneCommon>("LTZone", true);
        if(!ltz)
        {
            RDK::UEPtr<NMSDK::NPulseLTZoneThreshold> source(new NMSDK::NPulseLTZoneThreshold);
            const auto& core = NmsdkTests::InitEngineForPulseLibTests();
            source->SetStorage(core.storage);
            source->SetEnvironment(core.environment);
            source->Default();
            source->Name = "LTZone";
            ASSERT_NE(neuron->AddComponent(source), RDK::ForbiddenId);
            ltz = source;
        }
        ltz->Potential.SetDataDirect(.123);
        // No analyzer Build or test-only BindLtz: exercise production lazy lookup.
        EXPECT_DOUBLE_EQ(analyzer->ReadLtzPotential(), .123);
    }
}

TEST_F(IsiTemplateValidation, EmptyShapeAndNonfiniteUnusedColumnInvalidateBothLabels)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        for(int label : {0, 1})
        {
            Reference({});
            Present(label);
            ExpectInvalid();
            RDK::MDMatrix<double> emptyColumns;
            emptyColumns.Resize(4, 0);
            neuron->TrainingPattern.SetDataDirect(emptyColumns);
            Present(label);
            ExpectInvalid();
            RDK::MDMatrix<double> extraColumn;
            extraColumn.Resize(4, 2, .1);
            const double reference[] = {.01, .08, .16, .24};
            for(int i = 0; i < 4; ++i) extraColumn(i, 0) = reference[i];
            extraColumn(0, 1) = std::numeric_limits<double>::quiet_NaN();
            neuron->TrainingPattern.SetDataDirect(extraColumn);
            Present(label);
            ExpectInvalid();
        }
    }
}

TEST_F(IsiTemplateValidation, NonIncreasingStimulusInvalidatesBothLabels)
{
    for(const std::string learnerClass : {"NNeuronTimeLearner", "NNeuronTimeLearnerBranch"})
    {
        SCOPED_TRACE(learnerClass);
        ASSERT_NO_FATAL_FAILURE(MakeFixture(learnerClass));
        Reference({.01, .08, .16, .24});
        for(double second : {10.0, 9.99})
            for(int label : {0, 1})
            {
                Present(label, second);
                ExpectInvalid();
            }
    }
}

}
