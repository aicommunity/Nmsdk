#include <gtest/gtest.h>

#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronLearner.h"
#include "../Support/ConsoleLikeInit.h"

#include <algorithm>
#include <list>
#include <string>
#include <vector>

// Избегаем конфликта с макросом Windows GetMessage
#ifdef GetMessage
#undef GetMessage
#endif

using namespace RDK;

class PulseLibStorageIntegrationTest : public ::testing::Test
{
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
            storage = core.storage;
            environment = core.environment;
            modelInitialized = false;

            stage = "check-classes";
            ASSERT_TRUE(storage);
            ASSERT_TRUE(environment);
            ASSERT_TRUE(storage->CheckClass("NModel"));
            ASSERT_TRUE(storage->CheckClass("NPGenerator"));
            ASSERT_TRUE(storage->CheckClass("NSPNeuron"));
            ASSERT_TRUE(storage->CheckClass("NNeuronLearner"));

            // Создаём и инициализируем модель NModel через среду,
            // как это делает прикладной код (Environment+ModelInit)
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
            FAIL() << "Exception in SetUp (std::exception) at stage '" << stage << "': " << ex.what();
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

    void runModelSteps(int steps)
    {
        ASSERT_TRUE(model);

        if (!modelInitialized)
        {
            model->Default();
            model->Build();
            modelInitialized = true;
        }

        model->Reset();
        for (int i = 0; i < steps; ++i)
        {
            ASSERT_TRUE(model->Calculate());
        }
        model->Reset();
    }

    size_t getObjectCount(const std::string& className) const
    {
        return storage ? storage->CalcNumObjects(className) : 0;
    }

    bool modelHasComponentNamed(const std::string& name) const
    {
        if (!model)
            return false;

        std::vector<NameT> names;
        model->GetComponentsList(names);
        return std::find(names.begin(), names.end(), name) != names.end();
    }
};

// Тест 1: простой компонент из Nmsdk-PulseLib без вложенных компонент
// Несколько циклов: добавление → расчёт → останов → удаление
TEST_F(PulseLibStorageIntegrationTest, SimpleComponent_AddCalculateRemoveCycles)
{
    const std::string simpleClassName = "NPGenerator";
    const std::string instanceName    = "SimplePulseComponent";

    constexpr int cycles        = 5;
    constexpr int stepsPerCycle = 20;

    size_t baselineCount        = 0;
    bool baselineInitialized    = false;

    for (int i = 0; i < cycles; ++i)
    {
        auto comp = createAndAttachComponent(simpleClassName, instanceName);
        (void)comp;

        ASSERT_TRUE(modelHasComponentNamed(instanceName));

        runModelSteps(stepsPerCycle);

        model->DelComponent(instanceName, /*canfree=*/true);
        EXPECT_FALSE(modelHasComponentNamed(instanceName));

        const size_t count = getObjectCount(simpleClassName);
        if (!baselineInitialized)
        {
            baselineCount     = count;
            baselineInitialized = true;
        }
        else
        {
            EXPECT_EQ(count, baselineCount)
                << "Object count for class '" << simpleClassName
                << "' changed between cycles; possible leak in Storage.";
        }
    }
}

// Тест 2: сложный компонент-нейрон NSPNeuron (с вложенной структурой)
// Несколько циклов для одного и того же класса в хранилище
TEST_F(PulseLibStorageIntegrationTest, ComplexNeuron_AddCalculateRemoveCycles)
{
    const std::string neuronClassName = "NSPNeuron";
    const std::string instanceName    = "ComplexNeuron";

    constexpr int cycles        = 5;
    constexpr int stepsPerCycle = 20;

    size_t baselineCount        = 0;
    bool baselineInitialized    = false;

    for (int i = 0; i < cycles; ++i)
    {
        auto neuron = createAndAttachComponent(neuronClassName, instanceName);
        (void)neuron;

        ASSERT_TRUE(modelHasComponentNamed(instanceName));

        runModelSteps(stepsPerCycle);

        model->DelComponent(instanceName, /*canfree=*/true);
        EXPECT_FALSE(modelHasComponentNamed(instanceName));

        const size_t count = getObjectCount(neuronClassName);
        if (!baselineInitialized)
        {
            baselineCount     = count;
            baselineInitialized = true;
        }
        else
        {
            EXPECT_EQ(count, baselineCount)
                << "Object count for class '" << neuronClassName
                << "' changed between cycles; possible leak in Storage.";
        }
    }
}

// Тест 3: многократное переиспользование одного и того же объекта NSPNeuron
// Циклы: добавление → расчёт → останов → удаление (без auto-free) → явный ReturnObject
TEST_F(PulseLibStorageIntegrationTest, ComplexNeuron_ReuseSameInstanceAcrossCycles)
{
    const std::string neuronClassName = "NSPNeuron";
    const std::string instanceName    = "ReusableNeuron";

    ASSERT_TRUE(storage);
    ASSERT_TRUE(model);

    UEPtr<UComponent> base = storage->TakeObject(neuronClassName);
    ASSERT_TRUE(base);

    UEPtr<UContainer> neuron = dynamic_pointer_cast<UContainer>(base);
    ASSERT_TRUE(neuron) << "Class '" << neuronClassName << "' is not a UContainer-derived component";

    neuron->Name = instanceName;
    neuron->Default();
    neuron->Build();

    constexpr int cycles        = 5;
    constexpr int stepsPerCycle = 20;

    size_t baselineCount        = 0;
    bool baselineInitialized    = false;

    for (int i = 0; i < cycles; ++i)
    {
        // Добавляем один и тот же объект в модель
        UId id = model->AddComponent(neuron);
        ASSERT_NE(id, ForbiddenId);
        ASSERT_TRUE(modelHasComponentNamed(instanceName));

        runModelSteps(stepsPerCycle);

        // Удаляем компонент из модели, но не возвращаем его в хранилище автоматически
        model->DelComponent(instanceName, /*canfree=*/false);
        EXPECT_FALSE(modelHasComponentNamed(instanceName));

        // После удаления из модели у объекта не должно быть владельца
        EXPECT_FALSE(neuron->GetOwner());

        // Явно возвращаем объект в хранилище
        storage->ReturnObject(neuron);

        const size_t count = getObjectCount(neuronClassName);
        if (!baselineInitialized)
        {
            baselineCount     = count;
            baselineInitialized = true;
        }
        else
        {
            EXPECT_EQ(count, baselineCount)
                << "Object count for class '" << neuronClassName
                << "' changed between reuse cycles; possible incorrect ReturnObject handling.";
        }
    }
}

// Тест 4: цепочка нейронов/связей по мотивам Configs/*
// PGenerator.Output -> NeuronA.Soma1.ExcSynapse1.Input
// NeuronA.LTZone.Output -> NeuronB.Soma1.ExcSynapse1.Input
// Важно: переиспользуем те же инстансы во всех циклах (как в тесте 3).
TEST_F(PulseLibStorageIntegrationTest, ComplexChain_ReuseSameInstancesAcrossCycles)
{
    const std::string generatorClassName = "NPGenerator";
    const std::string neuronClassName    = "NSPNeuron";

    const std::string generatorName = "PGenerator";
    const std::string neuronAName   = "ChainNeuronA";
    const std::string neuronBName   = "ChainNeuronB";

    const std::string neuronASynapsePath = neuronAName + ".Soma1.ExcSynapse1";
    const std::string neuronBSynapsePath = neuronBName + ".Soma1.ExcSynapse1";
    const std::string neuronALTZonePath  = neuronAName + ".LTZone";

    ASSERT_TRUE(storage);
    ASSERT_TRUE(model);
    ASSERT_TRUE(storage->CheckClass(generatorClassName));
    ASSERT_TRUE(storage->CheckClass(neuronClassName));

    UEPtr<UNet> net = dynamic_pointer_cast<UNet>(model);
    ASSERT_TRUE(net) << "Model is expected to be UNet-derived for CreateLink/BreakLink operations";

    UEPtr<UComponent> genBase = storage->TakeObject(generatorClassName);
    UEPtr<UComponent> aBase   = storage->TakeObject(neuronClassName);
    UEPtr<UComponent> bBase   = storage->TakeObject(neuronClassName);
    ASSERT_TRUE(genBase);
    ASSERT_TRUE(aBase);
    ASSERT_TRUE(bBase);

    UEPtr<UContainer> generator = dynamic_pointer_cast<UContainer>(genBase);
    UEPtr<UContainer> neuronA   = dynamic_pointer_cast<UContainer>(aBase);
    UEPtr<UContainer> neuronB   = dynamic_pointer_cast<UContainer>(bBase);
    ASSERT_TRUE(generator);
    ASSERT_TRUE(neuronA);
    ASSERT_TRUE(neuronB);

    generator->Name = generatorName;
    generator->Default();
    generator->Build();

    neuronA->Name = neuronAName;
    neuronA->Default();
    neuronA->Build();

    neuronB->Name = neuronBName;
    neuronB->Default();
    neuronB->Build();

    constexpr int cycles        = 5;
    constexpr int stepsPerCycle = 20;

    size_t baselineGenCount   = 0;
    size_t baselineNeuronCount = 0;
    bool baselineInitialized  = false;

    for (int i = 0; i < cycles; ++i)
    {
        ASSERT_NE(model->AddComponent(generator), ForbiddenId);
        ASSERT_NE(model->AddComponent(neuronA), ForbiddenId);
        ASSERT_NE(model->AddComponent(neuronB), ForbiddenId);

        ASSERT_TRUE(modelHasComponentNamed(generatorName));
        ASSERT_TRUE(modelHasComponentNamed(neuronAName));
        ASSERT_TRUE(modelHasComponentNamed(neuronBName));

        // Проверяем, что ожидаемые внутренние пути существуют (по образцу Configs/*)
        ASSERT_TRUE(net->GetComponentL(neuronASynapsePath, /*no_throw=*/true)) << neuronASynapsePath;
        ASSERT_TRUE(net->GetComponentL(neuronBSynapsePath, /*no_throw=*/true)) << neuronBSynapsePath;
        ASSERT_TRUE(net->GetComponentL(neuronALTZonePath, /*no_throw=*/true)) << neuronALTZonePath;

        ASSERT_TRUE(net->CreateLink(generatorName, "Output", neuronASynapsePath, "Input"));
        ASSERT_TRUE(net->CreateLink(neuronALTZonePath, "Output", neuronBSynapsePath, "Input"));

        runModelSteps(stepsPerCycle);

        // Чтобы при следующем цикле не накапливались дубли связей — разрываем исходящие связи.
        net->BreakAllOutgoingLinks(generatorName);
        net->BreakAllOutgoingLinks(neuronALTZonePath);

        model->DelComponent(neuronBName, /*canfree=*/false);
        model->DelComponent(neuronAName, /*canfree=*/false);
        model->DelComponent(generatorName, /*canfree=*/false);

        EXPECT_FALSE(modelHasComponentNamed(generatorName));
        EXPECT_FALSE(modelHasComponentNamed(neuronAName));
        EXPECT_FALSE(modelHasComponentNamed(neuronBName));

        EXPECT_FALSE(generator->GetOwner());
        EXPECT_FALSE(neuronA->GetOwner());
        EXPECT_FALSE(neuronB->GetOwner());

        storage->ReturnObject(neuronB);
        storage->ReturnObject(neuronA);
        storage->ReturnObject(generator);

        const size_t genCount   = getObjectCount(generatorClassName);
        const size_t neuronCount = getObjectCount(neuronClassName);

        if (!baselineInitialized)
        {
            baselineGenCount    = genCount;
            baselineNeuronCount = neuronCount;
            baselineInitialized = true;
        }
        else
        {
            EXPECT_EQ(genCount, baselineGenCount)
                << "Object count for class '" << generatorClassName
                << "' changed between reuse cycles; possible incorrect ReturnObject handling.";
            EXPECT_EQ(neuronCount, baselineNeuronCount)
                << "Object count for class '" << neuronClassName
                << "' changed between reuse cycles; possible incorrect ReturnObject handling.";
        }
    }
}

// Тест 5: NNeuronLearner с параметрической структурой (NumInputDendrite)
// Цикл: создать -> настроить NumInputDendrite=4 -> расчёт -> удалить -> повторить в той же модели.
TEST_F(PulseLibStorageIntegrationTest, NNeuronLearner_CreateDeleteWithNumInputDendrite)
{
    const std::string className    = "NNeuronLearner";
    const std::string instanceName = "NeuronLearnerInstance";

    constexpr int numInputDendrite = 4;
    constexpr int cycles           = 2;
    constexpr int stepsPerCycle    = 20;

    ASSERT_TRUE(storage);
    ASSERT_TRUE(model);
    ASSERT_TRUE(storage->CheckClass(className));

    for (int i = 0; i < cycles; ++i)
    {
        std::string stage = "before-create";
        try
        {
            const size_t beforeCount = getObjectCount(className);

            stage = "create-component";
            UEPtr<UContainer> cont = createAndAttachComponent(className, instanceName);
            ASSERT_TRUE(cont) << "Failed to create NNeuronLearner component from Storage";

            stage = "cast-to-nneuronlearner";
            UEPtr<NMSDK::NNeuronLearner> learner = dynamic_pointer_cast<NMSDK::NNeuronLearner>(cont);
            ASSERT_TRUE(learner) << "Class '" << className << "' is not NNeuronLearner or hierarchy changed";

            stage = "configure-and-build";
            // Настраиваем параметр, влияющий на внутреннюю структуру обучателя
            learner->NumInputDendrite = numInputDendrite;
            // Обновляем внутреннюю структуру с учётом новых параметров
            learner->Build();

            // Проверяем, что внутренние структуры согласованы с NumInputDendrite
            EXPECT_EQ(learner->NumInputDendrite.GetData(), numInputDendrite);
            EXPECT_EQ(learner->DendriteLength.size(), static_cast<size_t>(numInputDendrite));
            EXPECT_EQ(learner->NumSynapse.size(), static_cast<size_t>(numInputDendrite));
            EXPECT_EQ(learner->InitialSomaPotential.size(), static_cast<size_t>(numInputDendrite));

            stage = "before-run-steps";
            ASSERT_TRUE(modelHasComponentNamed(instanceName));

            // Расчёт модели с настроенным NNeuronLearner
            stage = "run-steps";
            runModelSteps(stepsPerCycle);

            stage = "delete-component";
            // Удаляем компонент и освобождаем его в Storage
            model->DelComponent(instanceName, /*canfree=*/true);
            EXPECT_FALSE(modelHasComponentNamed(instanceName));

            stage = "check-storage-count";
            // Инвариант:
            // - если до цикла в Storage не было ни одного свободного объекта этого класса, после
            //   первого полного create->delete появится ровно 1 (пул пополняется);
            // - если свободные объекты уже были, их число после цикла должно вернуться к исходному.
            const size_t afterCount = getObjectCount(className);
            const size_t expectedCount = (beforeCount == 0 ? 1 : beforeCount);
            EXPECT_EQ(afterCount, expectedCount)
                << "Object count for class '" << className
                << "' changed after cycle; possible leak or incorrect cleanup in Storage.";
        }
        catch (const RDK::UException& ex)
        {
            std::cerr << "[NNeuronLearnerTest] Caught RDK::UException at stage='" << stage
                      << "', number=" << ex.GetNumber()
                      << ", type=" << ex.GetType()
                      << ", file=" << ex.GetExFileName()
                      << ", line=" << ex.GetExLineNumber()
                      << ", what=" << ex.what()
                      << std::endl;

            FAIL() << "Exception in NNeuronLearner_CreateDeleteWithNumInputDendrite at stage '"
                   << stage << "': number=" << ex.GetNumber()
                   << ", type=" << ex.GetType()
                   << ", file=" << ex.GetExFileName()
                   << ", line=" << ex.GetExLineNumber()
                   << ", what=" << ex.what();
        }
        catch (const std::exception& ex)
        {
            std::cerr << "[NNeuronLearnerTest] Caught std::exception at stage='" << stage
                      << "': what=" << ex.what() << std::endl;

            FAIL() << "std::exception in NNeuronLearner_CreateDeleteWithNumInputDendrite at stage '"
                   << stage << "': " << ex.what();
        }
        catch (...)
        {
            std::cerr << "[NNeuronLearnerTest] Caught unknown exception at stage='" << stage
                      << "'" << std::endl;

            FAIL() << "Unknown exception in NNeuronLearner_CreateDeleteWithNumInputDendrite at stage '"
                   << stage << "'";
        }
    }
}

