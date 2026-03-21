#include <gtest/gtest.h>

#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTrainer.h"
#include "../Support/ConsoleLikeInit.h"

#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

using namespace RDK;

namespace {

struct LearnerGrowthMetrics;
struct TrainerGrowthMetrics;

class PulseLibNeuronGrowthTest : public ::testing::Test
{
public:
    LearnerGrowthMetrics MeasureLearnerGrowthForScale(double timeScale);
    TrainerGrowthMetrics MeasureTrainerGrowthForScale(double timeScale);

protected:
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UContainer> model;
    bool modelInitialized{};

    void SetUp() override
    {
        std::string stage = "start";
        try
        {
            stage = "init-engine";
            const auto& core = NmsdkTests::InitEngineForPulseLibTests();
            storage      = core.storage;
            environment  = core.environment;
            modelInitialized = false;

            stage = "check-classes";
            ASSERT_TRUE(storage);
            ASSERT_TRUE(environment);
            ASSERT_TRUE(storage->CheckClass("NModel"));
            ASSERT_TRUE(storage->CheckClass("NNeuronLearner"));
            ASSERT_TRUE(storage->CheckClass("NNeuronTrainer"));

            stage = "create-model";
            ASSERT_TRUE(environment->CreateModel("NModel"));
            environment->ModelInit();
            model = environment->GetModel();
            ASSERT_TRUE(model);
        }
        catch (const RDK::UException& ex)
        {
            FAIL() << "Exception in SetUp (RDK::UException) at stage '" << stage
                   << "': " << ex.what();
        }
        catch (const std::exception& ex)
        {
            FAIL() << "Exception in SetUp (std::exception) at stage '" << stage
                   << "': " << ex.what();
        }
        catch (...)
        {
            FAIL() << "Unknown exception in SetUp at stage '" << stage << "'";
        }
    }

    UEPtr<UContainer> createAndAttachComponent(const std::string& className,
                                               const std::string& instanceName)
    {
        EXPECT_TRUE(storage);
        EXPECT_TRUE(model);
        if (!storage || !model)
            return UEPtr<UContainer>();

        UEPtr<UComponent> base = storage->TakeObject(className);
        EXPECT_TRUE(base);
        if (!base)
            return UEPtr<UContainer>();

        UEPtr<UContainer> comp = dynamic_pointer_cast<UContainer>(base);
        EXPECT_TRUE(comp) << "Class '" << className << "' is not a UContainer-derived component";
        if (!comp)
            return UEPtr<UContainer>();

        comp->Name = instanceName;
        comp->Default();
        comp->Build();

        UId id = model->AddComponent(comp);
        EXPECT_NE(id, ForbiddenId);
        if (id == ForbiddenId)
            return UEPtr<UContainer>();

        return comp;
    }

    void ensureModelInitialized()
    {
        ASSERT_TRUE(model);

        if (!modelInitialized)
        {
            model->Default();
            model->Build();
            modelInitialized = true;
        }
    }
};

struct LearnerGrowthMetrics
{
    double firstAvgLength{};
    double lastAvgLength{};
    int    lengthOscillations{};
    int    steps{};
};

LearnerGrowthMetrics PulseLibNeuronGrowthTest::MeasureLearnerGrowthForScale(double timeScale)
{
    LearnerGrowthMetrics metrics;

    if (!storage || !model)
        return metrics;

    const std::string className    = "NNeuronLearner";
    const std::string instanceName = "NeuronLearnerGrowth";

    UEPtr<UContainer> cont = createAndAttachComponent(className, instanceName);
    if (!cont)
        return metrics;

    UEPtr<NMSDK::NNeuronLearner> learner = dynamic_pointer_cast<NMSDK::NNeuronLearner>(cont);
    if (!learner)
        return metrics;

    constexpr int numInputDendrite = 4;

    learner->StructureBuildMode = 1;
    learner->NumInputDendrite   = numInputDendrite;
    learner->MaxDendriteLength  = 100;
    learner->IsNeedToTrain      = true;
    learner->CalculateMode      = 0;
    learner->ExperimentMode     = false;
    learner->EnableDebug        = true;

    // Базовый паттерн задержек (0.01, 0.02, 0.03, 0.04) масштабируем по timeScale.
    MDMatrix<double> pattern;
    pattern.Assign(numInputDendrite, 1, 0.0);
    const double baseTimes[numInputDendrite] = {0.01, 0.02, 0.03, 0.04};
    for (int i = 0; i < numInputDendrite; ++i)
        pattern(i, 0) = baseTimes[i] * timeScale;

    learner->InputPattern = pattern;

    // Пересобираем структуру с учётом обновлённых параметров.
    learner->Build();

    ensureModelInitialized();

    model->Reset();

    constexpr int steps = 50;

    std::vector<std::vector<int>> lengthHistory;
    lengthHistory.reserve(steps);

    for (int step = 0; step < steps; ++step)
    {
        if (!model->Calculate())
            break;

        const std::vector<int>& lengths = learner->DendriteLength;
        if (static_cast<int>(lengths.size()) != numInputDendrite)
            break;

        lengthHistory.push_back(lengths);
    }

    model->Reset();
    model->DelComponent(instanceName, /*canfree=*/true);

    metrics.steps = static_cast<int>(lengthHistory.size());

    if (!lengthHistory.empty())
    {
        const std::vector<int>& first = lengthHistory.front();
        const std::vector<int>& last  = lengthHistory.back();

        auto avg = [](const std::vector<int>& v) -> double {
            if (v.empty())
                return 0.0;
            long long sum = 0;
            for (int x : v)
                sum += x;
            return static_cast<double>(sum) / static_cast<double>(v.size());
        };

        metrics.firstAvgLength = avg(first);
        metrics.lastAvgLength  = avg(last);

        // Подсчитываем число смен направления роста/убывания средней длины.
        int prevDeltaSign = 0;
        for (size_t i = 1; i < lengthHistory.size(); ++i)
        {
            double prevAvg = avg(lengthHistory[i - 1]);
            double curAvg  = avg(lengthHistory[i]);
            double delta   = curAvg - prevAvg;

            int sign = (delta > 1e-9) ? 1 : (delta < -1e-9 ? -1 : 0);
            if (sign != 0 && prevDeltaSign != 0 && sign != prevDeltaSign)
                ++metrics.lengthOscillations;

            if (sign != 0)
                prevDeltaSign = sign;
        }
    }

    return metrics;
}

TEST_F(PulseLibNeuronGrowthTest, NNeuronLearner_GrowthStatisticsForIntervalScales)
{
    const double scales[] = {0.5, 1.0, 1.5, 2.0};

    for (double s : scales)
    {
        LearnerGrowthMetrics m = MeasureLearnerGrowthForScale(s);

        std::cout << "[NNeuronLearner] scale=" << s
                  << " firstAvgLength=" << m.firstAvgLength
                  << " lastAvgLength=" << m.lastAvgLength
                  << " lengthOscillations=" << m.lengthOscillations
                  << " steps=" << m.steps << std::endl;

        // Инварианты: длины дендритов всегда положительны и не превышают MaxDendriteLength.
        EXPECT_GE(m.firstAvgLength, 1.0);
        EXPECT_GE(m.lastAvgLength, 1.0);
        EXPECT_LE(m.firstAvgLength, 100.0);
        EXPECT_LE(m.lastAvgLength, 100.0);
    }
}

struct TrainerGrowthMetrics
{
    double firstNumParts{};
    double lastNumParts{};
    int    partsOscillations{};
    int    steps{};
};

TrainerGrowthMetrics PulseLibNeuronGrowthTest::MeasureTrainerGrowthForScale(double timeScale)
{
    TrainerGrowthMetrics metrics;

    if (!storage || !model)
        return metrics;

    const std::string className    = "NNeuronTrainer";
    const std::string instanceName = "NeuronTrainerGrowth";

    UEPtr<UContainer> cont = createAndAttachComponent(className, instanceName);
    if (!cont)
        return metrics;

    UEPtr<NMSDK::NNeuronTrainer> trainer = dynamic_pointer_cast<NMSDK::NNeuronTrainer>(cont);
    if (!trainer)
        return metrics;

    constexpr int numInputDendrite = 5;

    trainer->StructureBuildMode = 1;
    trainer->NumInputDendrite   = numInputDendrite;
    trainer->MaxDendriteLength  = 100;
    trainer->IsNeedToTrain      = true;
    trainer->CalculateMode      = 6;
    trainer->EnableDebug        = true;

    MDMatrix<double> pattern;
    pattern.Assign(numInputDendrite, 1, 0.0);
    const double baseTimes[numInputDendrite] = {0.01, 0.02, 0.03, 0.04, 0.05};
    for (int i = 0; i < numInputDendrite; ++i)
        pattern(i, 0) = baseTimes[i] * timeScale;

    trainer->InputPattern = pattern;

    trainer->Build();

    ensureModelInitialized();

    UEPtr<UNet> net = dynamic_pointer_cast<UNet>(model);
    if (!net)
        return metrics;

    model->Reset();

    constexpr int steps = 50;

    std::vector<int> partsHistory;
    partsHistory.reserve(steps);

    for (int step = 0; step < steps; ++step)
    {
        if (!model->Calculate())
            break;

        UEPtr<NMSDK::NPulseNeuron> neuron =
            net->GetComponentL<NMSDK::NPulseNeuron>(instanceName + ".Neuron", /*no_throw=*/true);

        if (!neuron)
            break;

        int numParts = 0;
        if (neuron->StructureBuildMode != 2)
            numParts = neuron->NumDendriteMembraneParts;
        else
            numParts = static_cast<int>(neuron->NumDendriteMembranePartsVec.size());

        partsHistory.push_back(numParts);
    }

    model->Reset();
    model->DelComponent(instanceName, /*canfree=*/true);

    metrics.steps = static_cast<int>(partsHistory.size());

    if (!partsHistory.empty())
    {
        metrics.firstNumParts = static_cast<double>(partsHistory.front());
        metrics.lastNumParts  = static_cast<double>(partsHistory.back());

        int prevDeltaSign = 0;
        for (size_t i = 1; i < partsHistory.size(); ++i)
        {
            int delta = partsHistory[i] - partsHistory[i - 1];
            int sign  = (delta > 0) ? 1 : (delta < 0 ? -1 : 0);

            if (sign != 0 && prevDeltaSign != 0 && sign != prevDeltaSign)
                ++metrics.partsOscillations;

            if (sign != 0)
                prevDeltaSign = sign;
        }
    }

    return metrics;
}

TEST_F(PulseLibNeuronGrowthTest, NNeuronTrainer_GrowthStatisticsForIntervalScales)
{
    const double scales[] = {0.5, 1.0, 1.5, 2.0};

    for (double s : scales)
    {
        TrainerGrowthMetrics m = MeasureTrainerGrowthForScale(s);

        std::cout << "[NNeuronTrainer] scale=" << s
                  << " firstNumParts=" << m.firstNumParts
                  << " lastNumParts=" << m.lastNumParts
                  << " partsOscillations=" << m.partsOscillations
                  << " steps=" << m.steps << std::endl;

        EXPECT_GE(m.firstNumParts, 1.0);
        EXPECT_GE(m.lastNumParts, 1.0);
    }
}

} // namespace

