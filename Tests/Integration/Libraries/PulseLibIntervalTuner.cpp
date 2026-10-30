#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTrainer.h"
#include "../Support/ConsoleLikeInit.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <cstdio>

using namespace RDK;

namespace {

struct TunerContext
{
    UEPtr<UStorage>     storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UContainer>   model;
    bool                modelInitialized{};
};

bool InitContext(TunerContext& ctx)
{
    std::cout << "[IntervalTuner] InitContext: start" << std::endl;

    std::string stage = "start";
    try
    {
        stage = "init-engine";
        const auto& core = NmsdkTests::InitEngineForPulseLibTests();
        ctx.storage      = core.storage;
        ctx.environment  = core.environment;
        ctx.modelInitialized = false;

        stage = "check-classes";
        if (!ctx.storage || !ctx.environment)
        {
            std::cerr << "[IntervalTuner] Storage or Environment is null at stage '" << stage << "'\n";
            return false;
        }

        if (!ctx.storage->CheckClass("NModel") ||
            !ctx.storage->CheckClass("NNeuronLearner") ||
            !ctx.storage->CheckClass("NNeuronTrainer"))
        {
            std::cerr << "[IntervalTuner] Required classes not available in Storage\n";
            return false;
        }

        stage = "create-model";
        if (!ctx.environment->CreateModel("NModel"))
        {
            std::cerr << "[IntervalTuner] Failed to create NModel at stage '" << stage << "'\n";
            return false;
        }

        ctx.environment->ModelInit();
        ctx.model = ctx.environment->GetModel();
        if (!ctx.model)
        {
            std::cerr << "[IntervalTuner] Model is null after ModelInit\n";
            return false;
        }

        std::cout << "[IntervalTuner] InitContext: success" << std::endl;
        return true;
    }
    catch (const RDK::UException& ex)
    {
        std::cerr << "[IntervalTuner] RDK::UException at stage '" << stage
                  << "': " << ex.what() << "\n";
    }
    catch (const std::exception& ex)
    {
        std::cerr << "[IntervalTuner] std::exception at stage '" << stage
                  << "': " << ex.what() << "\n";
    }
    catch (...)
    {
        std::cerr << "[IntervalTuner] Unknown exception at stage '" << stage << "'\n";
    }

    std::cout << "[IntervalTuner] InitContext: failed at stage '" << stage << "'" << std::endl;
    return false;
}

UEPtr<UContainer> CreateAndAttachComponent(TunerContext&      ctx,
                                           const std::string& className,
                                           const std::string& instanceName)
{
    if (!ctx.storage || !ctx.model)
        return UEPtr<UContainer>();

    UEPtr<UComponent> base = ctx.storage->TakeObject(className);
    if (!base)
    {
        std::cerr << "[IntervalTuner] Failed to TakeObject(" << className << ")\n";
        return UEPtr<UContainer>();
    }

    UEPtr<UContainer> comp = dynamic_pointer_cast<UContainer>(base);
    if (!comp)
    {
        std::cerr << "[IntervalTuner] Class '" << className
                  << "' is not a UContainer-derived component\n";
        return UEPtr<UContainer>();
    }

    comp->Name = instanceName;
    comp->Default();
    comp->Build();

    UId id = ctx.model->AddComponent(comp);
    if (id == ForbiddenId)
    {
        std::cerr << "[IntervalTuner] Failed to AddComponent(" << instanceName << ")\n";
        return UEPtr<UContainer>();
    }

    return comp;
}

void EnsureModelInitialized(TunerContext& ctx)
{
    if (!ctx.model)
        return;

    if (!ctx.modelInitialized)
    {
        ctx.model->Default();
        ctx.model->Build();
        ctx.modelInitialized = true;
    }
}

struct LearnerMetrics
{
    double firstAvgLength{};
    double lastAvgLength{};
    int    lengthOscillations{};
};

LearnerMetrics MeasureLearner(TunerContext& ctx,
                              double        timeScale,
                              double        synapseScale,
                              double        ltzScale)
{
    LearnerMetrics metrics;

    const std::string className    = "NNeuronLearner";
    const std::string instanceName = "Tuner_NeuronLearner";

    UEPtr<UContainer> cont = CreateAndAttachComponent(ctx, className, instanceName);
    if (!cont)
        return metrics;

    UEPtr<NMSDK::NNeuronLearner> learner = dynamic_pointer_cast<NMSDK::NNeuronLearner>(cont);
    if (!learner)
    {
        std::cerr << "[IntervalTuner] Failed to cast to NNeuronLearner\n";
        ctx.model->DelComponent(instanceName, /*canfree=*/true);
        return metrics;
    }

    constexpr int numInputDendrite = 4;

    learner->StructureBuildMode = 1;
    learner->NumInputDendrite   = numInputDendrite;
    learner->MaxDendriteLength  = 100;
    learner->IsNeedToTrain      = true;
    learner->CalculateMode      = 0;
    learner->ExperimentMode     = false;
    learner->EnableDebug        = true;

    // Масштабируем синаптические и пороговые параметры относительно базовых значений.
    const double baseSynStepLearner = learner->SynapseResistanceStep.GetData();
    if (baseSynStepLearner > 0.0)
        learner->SynapseResistanceStep = baseSynStepLearner * synapseScale;

    const double baseTrainLtz = learner->TrainingLTZThreshold.GetData();
    if (baseTrainLtz > 0.0)
    {
        const double newTrainLtz = baseTrainLtz * ltzScale;
        learner->TrainingLTZThreshold = newTrainLtz;
        // Для простых сценариев выставляем тот же порог и как рабочий.
        learner->LTZThreshold = newTrainLtz;
    }

    MDMatrix<double> pattern;
    pattern.Assign(numInputDendrite, 1, 0.0);
    const double baseTimes[numInputDendrite] = {0.01, 0.02, 0.03, 0.04};
    for (int i = 0; i < numInputDendrite; ++i)
        pattern(i, 0) = baseTimes[i] * timeScale;

    learner->InputPattern = pattern;

    learner->Build();

    EnsureModelInitialized(ctx);

    ctx.model->Reset();

    constexpr int steps = 50;

    std::vector<std::vector<int>> lengthHistory;
    lengthHistory.reserve(steps);

    for (int step = 0; step < steps; ++step)
    {
        if (!ctx.model->Calculate())
        {
            std::cerr << "[IntervalTuner] model->Calculate() failed for NNeuronLearner\n";
            break;
        }

        const std::vector<int>& lengths = learner->DendriteLength;
        if (static_cast<int>(lengths.size()) != numInputDendrite)
            break;

        lengthHistory.push_back(lengths);
    }

    ctx.model->Reset();
    ctx.model->DelComponent(instanceName, /*canfree=*/true);

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

struct TrainerMetrics
{
    double firstNumParts{};
    double lastNumParts{};
    int    partsOscillations{};
};

TrainerMetrics MeasureTrainer(TunerContext& ctx,
                              double        timeScale,
                              double        synapseScale,
                              double        ltzScale)
{
    TrainerMetrics metrics;

    const std::string className    = "NNeuronTrainer";
    const std::string instanceName = "Tuner_NeuronTrainer";

    UEPtr<UContainer> cont = CreateAndAttachComponent(ctx, className, instanceName);
    if (!cont)
        return metrics;

    UEPtr<NMSDK::NNeuronTrainer> trainer = dynamic_pointer_cast<NMSDK::NNeuronTrainer>(cont);
    if (!trainer)
    {
        std::cerr << "[IntervalTuner] Failed to cast to NNeuronTrainer\n";
        ctx.model->DelComponent(instanceName, /*canfree=*/true);
        return metrics;
    }

    constexpr int numInputDendrite = 5;

    trainer->StructureBuildMode = 1;
    trainer->NumInputDendrite   = numInputDendrite;
    trainer->MaxDendriteLength  = 100;
    trainer->IsNeedToTrain      = true;
    trainer->CalculateMode      = 6;
    trainer->EnableDebug        = true;

    const double baseSynStepTrainer = trainer->SynapseResistanceStep.GetData();
    if (baseSynStepTrainer > 0.0)
        trainer->SynapseResistanceStep = baseSynStepTrainer * synapseScale;

    const double baseLtz = trainer->LTZThreshold.GetData();
    if (baseLtz > 0.0)
    {
        const double newLtz = baseLtz * ltzScale;
        trainer->LTZThreshold       = newLtz;
        trainer->FixedLTZThreshold  = newLtz;
    }

    MDMatrix<double> pattern;
    pattern.Assign(numInputDendrite, 1, 0.0);
    const double baseTimes[numInputDendrite] = {0.01, 0.02, 0.03, 0.04, 0.05};
    for (int i = 0; i < numInputDendrite; ++i)
        pattern(i, 0) = baseTimes[i] * timeScale;

    trainer->InputPattern = pattern;

    trainer->Build();

    EnsureModelInitialized(ctx);

    UEPtr<UNet> net = dynamic_pointer_cast<UNet>(ctx.model);
    if (!net)
    {
        std::cerr << "[IntervalTuner] Model is not UNet-derived\n";
        ctx.model->DelComponent(instanceName, /*canfree=*/true);
        return metrics;
    }

    ctx.model->Reset();

    constexpr int steps = 50;

    std::vector<int> partsHistory;
    partsHistory.reserve(steps);

    for (int step = 0; step < steps; ++step)
    {
        if (!ctx.model->Calculate())
        {
            std::cerr << "[IntervalTuner] model->Calculate() failed for NNeuronTrainer\n";
            break;
        }

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

    ctx.model->Reset();
    ctx.model->DelComponent(instanceName, /*canfree=*/true);

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

std::string ScaleValueInRow(const std::string& row, double scale)
{
    std::string result = row;

    size_t first = row.find_first_not_of(" \t");
    if (first == std::string::npos)
        return result;

    size_t last = first;
    while (last < row.size() &&
           !std::isspace(static_cast<unsigned char>(row[last])))
    {
        ++last;
    }

    std::string valueStr = row.substr(first, last - first);
    try
    {
        double value   = std::stod(valueStr);
        double scaled  = value * scale;

        std::ostringstream oss;
        oss.setf(std::ios::fixed);
        oss.precision(12);
        oss << scaled;

        result = row.substr(0, first) + oss.str() + row.substr(last);
    }
    catch (...)
    {
        // Если парсинг не удался, оставляем строку как есть.
    }

    return result;
}

bool ApplyScaleToConfig(double scale)
{
    namespace fs = std::filesystem;

    fs::path baseDir = fs::current_path();
    // Ожидаем структуру .../Bin/Platform/Win => поднимаемся до .../Bin, затем в Configs/...
    fs::path cfgPath = baseDir.parent_path().parent_path()
        / "Configs" / "Bakhshiev" / "TestTrain" / "Parameters_00.xml";

    std::ifstream in(cfgPath);
    if (!in.is_open())
    {
        std::cerr << "[IntervalTuner] Failed to open config file: " << cfgPath << "\n";
        return false;
    }

    std::ostringstream out;

    bool insideLearner  = false;
    bool insideTrainer  = false;

    std::string line;
    while (std::getline(in, line))
    {
        if (line.find("<NeuronLearner Class=\"NNeuronLearner\">") != std::string::npos)
        {
            insideLearner = true;
        }
        else if (line.find("</NeuronLearner>") != std::string::npos)
        {
            insideLearner = false;
        }

        if (line.find("<NeuronTrainer Class=\"NNeuronTrainer\">") != std::string::npos)
        {
            insideTrainer = true;
        }
        else if (line.find("</NeuronTrainer>") != std::string::npos)
        {
            insideTrainer = false;
        }

        if (insideLearner &&
            line.find("<InputPattern Type=\"MDMatrix") != std::string::npos)
        {
            out << line << "\n";

            // В TestTrain у NeuronLearner Rows="4".
            const int rows = 4;
            for (int i = 0; i < rows; ++i)
            {
                if (!std::getline(in, line))
                    break;

                out << ScaleValueInRow(line, scale) << "\n";
            }

            continue;
        }

        if (insideTrainer &&
            line.find("<InputPattern Type=\"MDMatrix") != std::string::npos)
        {
            out << line << "\n";

            // В TestTrain у NeuronTrainer Rows="5".
            const int rows = 5;
            for (int i = 0; i < rows; ++i)
            {
                if (!std::getline(in, line))
                    break;

                out << ScaleValueInRow(line, scale) << "\n";
            }

            continue;
        }

        out << line << "\n";
    }

    in.close();

    std::ofstream outFile(cfgPath, std::ios::trunc);
    if (!outFile.is_open())
    {
        std::cerr << "[IntervalTuner] Failed to open config for writing: " << cfgPath << "\n";
        return false;
    }

    outFile << out.str();
    outFile.close();

    std::cout << "[IntervalTuner] Updated Parameters_00.xml with scale = " << scale << "\n";
    return true;
}

} // namespace

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;

    // Для тюнера подавляем вывод на stderr (туда пишет glog),
    // чтобы не засорять консоль сообщениями "COULD NOT CREATE A LOGGINGFILE".
#if defined(_WIN32)
    FILE* dummy = nullptr;
    freopen_s(&dummy, "NUL", "w", stderr);
#endif

    std::cout << "[IntervalTuner] Started PulseLibIntervalTuner" << std::endl;

    TunerContext ctx;
    if (!InitContext(ctx))
    {
        std::cout << "[IntervalTuner] InitContext failed, exiting" << std::endl;
        return 1;
    }

    const double timeScales[]    = {0.5, 0.75, 1.0, 1.25, 1.5, 2.0};
    const double synapseScales[] = {0.5, 1.0, 1.5};
    const double ltzScales[]     = {0.5, 1.0, 1.5};

    double bestTimeScale   = 1.0;
    double bestSynScale    = 1.0;
    double bestLtzScale    = 1.0;
    double bestScore       = -1e100;

    for (double tscale : timeScales)
    {
        for (double sscale : synapseScales)
        {
            for (double lscale : ltzScales)
            {
                LearnerMetrics learnerMetrics = MeasureLearner(ctx, tscale, sscale, lscale);
                TrainerMetrics trainerMetrics = MeasureTrainer(ctx, tscale, sscale, lscale);

                double learnerScore =
                    (learnerMetrics.lastAvgLength - learnerMetrics.firstAvgLength) -
                    0.1 * static_cast<double>(learnerMetrics.lengthOscillations);

                double trainerScore =
                    (trainerMetrics.lastNumParts - trainerMetrics.firstNumParts) -
                    0.1 * static_cast<double>(trainerMetrics.partsOscillations);

                double totalScore = learnerScore + trainerScore;

                std::cout << "[IntervalTuner] tscale=" << tscale
                          << " synScale=" << sscale
                          << " ltzScale=" << lscale
                          << " learner(first=" << learnerMetrics.firstAvgLength
                          << ", last=" << learnerMetrics.lastAvgLength
                          << ", osc=" << learnerMetrics.lengthOscillations << ")"
                          << " trainer(first=" << trainerMetrics.firstNumParts
                          << ", last=" << trainerMetrics.lastNumParts
                          << ", osc=" << trainerMetrics.partsOscillations << ")"
                          << " totalScore=" << totalScore << "\n";

                if (totalScore > bestScore)
                {
                    bestScore     = totalScore;
                    bestTimeScale = tscale;
                    bestSynScale  = sscale;
                    bestLtzScale  = lscale;
                }
            }
        }
    }

    std::cout << "[IntervalTuner] Best combination: tscale=" << bestTimeScale
              << " synScale=" << bestSynScale
              << " ltzScale=" << bestLtzScale
              << " (score = " << bestScore << ")\n";

    // В конфиг автоматически записываем только масштаб времени (InputPattern),
    // а найденные множители для синапсов и порогов остаются в логе для анализа.
    if (!ApplyScaleToConfig(bestTimeScale))
        return 2;

    return 0;
}

