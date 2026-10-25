#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembraneCommon.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NConstGenerator.h"
#include "../Support/ConsoleLikeInit.h"

#include <string>
#include <vector>

namespace {
using namespace RDK;

class SynapseCoefficientProbe : public NMSDK::NPulseSynapse
{
public:
    double SecretionSteps() const { return VSecretionTC; }
    double DissociationSteps() const { return VDissociationTC; }
};

class LifecycleTrace : public UNet
{
public:
    std::vector<std::string> hooks;
    int samples = 0;
    void InvalidateStructure() { Ready = false; }
protected:
    bool ABuild() override { hooks.push_back("build"); return true; }
    bool AReset() override { hooks.push_back("reset"); samples = 0; return true; }
    bool ABeforeCalculate() override { hooks.push_back("before"); return true; }
    bool ACalculate() override { hooks.push_back("calculate"); ++samples; return true; }
    bool AAfterCalculate() override { hooks.push_back("after"); return true; }
};

TEST(TimeLearnerNativeLifecycle, ConstantSourceResetPublishesRestValueBeforeFirstTick)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto source = dynamic_pointer_cast<NMSDK::NConstGenerator>(core.storage->TakeObject("NPNeuronPosCGenerator"));
    ASSERT_TRUE(source);
    source->SetEnvironment(core.environment);
    source->Init();
    source->Output.Assign(1, 1, 0.);
    source->Reset();
    EXPECT_DOUBLE_EQ(source->Output(0, 0), source->Amplitude.GetData());
    core.storage->ReturnObject(source);
}

TEST(TimeLearnerNativeLifecycle, SynapseResetClearsConductanceBeforeFirstTick)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto synapse = dynamic_pointer_cast<NMSDK::NPulseSynapse>(core.storage->TakeObject("NPSynapse"));
    ASSERT_TRUE(synapse);
    synapse->SetEnvironment(core.environment);
    synapse->Init();
    synapse->Output.Assign(1, 1, 1e-8);
    synapse->Reset();
    EXPECT_DOUBLE_EQ(synapse->Output(0, 0), 0.);
    core.storage->ReturnObject(synapse);
}

TEST(TimeLearnerNativeLifecycle, ResetRefreshesSynapseStepCoefficients)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    SynapseCoefficientProbe synapse;
    synapse.SetStorage(core.storage);
    synapse.SetEnvironment(core.environment);
    synapse.Default();
    synapse.Activity = true; // TakeObject activates instances; this fixture allocates directly.
    synapse.SecretionTC = .001;
    synapse.DissociationTC = .002;
    synapse.SetGlobalTimeStep(2000);
    synapse.Init();
    ASSERT_TRUE(synapse.IsInit());
    synapse.Reset();
    EXPECT_DOUBLE_EQ(synapse.SecretionSteps(), 2.0);
    EXPECT_DOUBLE_EQ(synapse.DissociationSteps(), 4.0);
    synapse.SetGlobalTimeStep(20000);
    synapse.Reset();
    EXPECT_DOUBLE_EQ(synapse.SecretionSteps(), 20.0);
    EXPECT_DOUBLE_EQ(synapse.DissociationSteps(), 40.0);
    // Returning to the previous frequency follows the same native reset path.
    synapse.SetGlobalTimeStep(2000);
    synapse.Reset();
    EXPECT_DOUBLE_EQ(synapse.SecretionSteps(), 2.0);
}

TEST(TimeLearnerNativeLifecycle, BuildResetAndCalculateHaveObservableNativeOrder)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    ASSERT_TRUE(core.storage);
    ASSERT_TRUE(core.environment);
    core.environment->CreateModel("NModel");
    core.environment->ModelInit();
    auto model = core.environment->GetModel();
    ASSERT_TRUE(model);

    UEPtr<LifecycleTrace> trace(new LifecycleTrace);
    trace->SetStorage(core.storage);
    trace->SetEnvironment(core.environment);
    trace->Default();
    trace->Activity = true;
    trace->Name = "LifecycleTrace";
    ASSERT_NE(model->AddComponent(trace), ForbiddenId);
    trace->SetGlobalTimeStep(model->GetTimeStep());
    trace->Init();
    ASSERT_TRUE(trace->IsInit());
    trace->hooks.clear();
    trace->Build();
    EXPECT_TRUE(trace->hooks.empty());
    trace->InvalidateStructure();
    trace->Build();
    EXPECT_EQ(trace->hooks, (std::vector<std::string>{"build", "reset"}));
    trace->hooks.clear();
    for(int tick = 0; tick < 3; ++tick)
    {
        model->Calculate();
        core.environment->IncreaseModelTimeByStep();
    }
    EXPECT_EQ(trace->samples, 3);
    EXPECT_EQ(trace->hooks, (std::vector<std::string>{
        "before", "calculate", "after", "before", "calculate", "after",
        "before", "calculate", "after"}));
    model->DelComponent("LifecycleTrace", false);
}

TEST(TimeLearnerNativeLifecycle, StorageImageSurvivesFreshTakeAndReuse)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    for(int pass = 0; pass < 2; ++pass)
    {
        auto component = core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9");
        auto neuron = dynamic_pointer_cast<NMSDK::NPulseNeuron>(component);
        ASSERT_TRUE(neuron);
        // Do not Default here: TakeObject already applies the class image.
        auto membrane = neuron->GetComponentL<NMSDK::NPulseMembraneCommon>("Soma1", true);
        ASSERT_TRUE(membrane);
        auto channel = membrane->GetComponentL<NMSDK::NPulseChannel>("ExcChannel", true);
        ASSERT_TRUE(channel);
        EXPECT_DOUBLE_EQ(channel->Capacity.GetData(), 1e-9);
        ASSERT_GT(membrane->GetNumChannels(), 0u);
        bool indexed = false;
        for(size_t i = 0; i < membrane->GetNumChannels(); ++i)
            indexed = indexed || membrane->GetChannel(i) == channel.Get();
        EXPECT_TRUE(indexed);
        core.storage->ReturnObject(neuron);
    }
}
// Free can call DisconnectAll -> Build -> Reset. Keep this otherwise unused
// pooled object unready until the test main performs native channel shutdown.
// ASan then verifies the Environment lifetime even when this test runs alone.
class ShutdownEnvironmentReader : public UNet
{
public:
    volatile double capturedTime = 0.;
    ShutdownEnvironmentReader* New(void) override { return new ShutdownEnvironmentReader; }
    void Invalidate() { Ready = false; }
protected:
    bool AReset() override
    {
        if(Environment) capturedTime = Environment->GetTime().GetDoubleTime();
        return true;
    }
};

TEST(TimeLearnerNativeLifecycle, PooledRebuildRequiresEnvironmentThroughChannelShutdown)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* { return new ShutdownEnvironmentReader; }, "ShutdownEnvironmentReader"),
        "ShutdownEnvironmentReader");
    auto probe = dynamic_pointer_cast<ShutdownEnvironmentReader>(
        core.storage->TakeObject("ShutdownEnvironmentReader"));
    ASSERT_TRUE(probe);
    probe->SetEnvironment(core.environment);
    probe->Init(); probe->Invalidate();
    core.storage->ReturnObject(probe);
    EXPECT_FALSE(probe->IsReady());
}
} // namespace
