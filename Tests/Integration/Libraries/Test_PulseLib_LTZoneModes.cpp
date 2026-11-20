#include <gtest/gtest.h>
#include "NPulseLTZone.h"
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include "../Support/ConsoleLikeInit.h"
#include <cmath>
#include <typeinfo>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;
constexpr double Drive=.02;
constexpr double Tau=.004;
constexpr std::size_t Samples=32;

std::vector<double> SubthresholdResponse(bool integrate,bool stabilizer,unsigned frequency)
{
    std::vector<double> response;
    const int result=NmsdkWorker::WithFreshOwner<NPulseLTZone>("NPulseLTZone",frequency,
        "IntegratedZoneFixture",[&](auto,auto environment,auto model,auto zone) {
        EXPECT_TRUE(typeid(*zone)==typeid(NPulseLTZone));
        if(typeid(*zone)!=typeid(NPulseLTZone))return 2;
        // Configure one isolated physical leaf before its final initialization.
        // No shared prototype, neuron element defaults or running probe is edited.
        zone->UseLTZIntegtation=integrate;
        zone->UseSpikeStabilizer=stabilizer;
        zone->TimeConstant=Tau; // Effective initial physics, after flag setters.
        zone->UseAveragePotential=false;
        zone->Threshold=100.;zone->ThresholdOff=0.;
        model->Init();model->Reset();
        EXPECT_EQ(zone->UseLTZIntegtation.GetData(),integrate);
        EXPECT_EQ(zone->UseSpikeStabilizer.GetData(),stabilizer);
        EXPECT_DOUBLE_EQ(zone->TimeConstant.GetData(),Tau);
        EXPECT_DOUBLE_EQ(double(zone->GetTimeStep()),double(frequency));
        if(zone->UseLTZIntegtation.GetData()!=integrate ||
           zone->UseSpikeStabilizer.GetData()!=stabilizer || zone->TimeConstant.GetData()!=Tau)
            return 2;
        std::vector<MDMatrix<double>> input(1);input[0].Assign(1,1,Drive);
        zone->Inputs=input;
        for(std::size_t tick=0;tick<Samples;++tick) {
            model->Calculate(); // Real leaf, exactly once in the native model tree.
            EXPECT_DOUBLE_EQ(zone->NeuralPotential.GetData(),Drive);
            EXPECT_EQ(zone->OutputPulseTimes.GetCols(),0);
            EXPECT_DOUBLE_EQ(zone->Output(0,0),0.);
            EXPECT_TRUE(std::isfinite(zone->Potential.GetData()));
            response.push_back(zone->Potential.GetData());
            environment->IncreaseModelTimeByStep();
        }
        return 0;
    });
    EXPECT_EQ(result,0);
    return response;
}

void CompareNonspikingFeedbackModes(unsigned frequency)
{
    const auto off=SubthresholdResponse(true,false,frequency);
    const auto on=SubthresholdResponse(true,true,frequency);
    ASSERT_EQ(off.size(),Samples);ASSERT_EQ(on.size(),Samples);
    // A spike stabilizer has no spike to act on in this experiment. Turning it
    // off must not disconnect afferent drive or change the subthreshold filter.
    EXPECT_GT(off.back(),1e-6);EXPECT_GT(on.back(),1e-6);
    EXPECT_LT(off.front(),Drive);EXPECT_LT(on.front(),Drive);
    for(std::size_t i=0;i<Samples;++i)
        EXPECT_NEAR(off[i],on[i],1e-12)<<"sample="<<i<<" frequency="<<frequency;
}

TEST(LTZoneDynamics, NonspikingFeedbackModesHaveTheSameDrivenResponseAt2000Hz)
{CompareNonspikingFeedbackModes(2000);}

TEST(LTZoneDynamics, NonspikingFeedbackModesHaveTheSameDrivenResponseAt20000Hz)
{CompareNonspikingFeedbackModes(20000);}

TEST(LTZoneDynamics, DisabledIntegrationIsAWorkingPositiveControlForBothFeedbackFlags)
{
    for(bool stabilizer:{false,true}) {
        const auto response=SubthresholdResponse(false,stabilizer,2000);
        ASSERT_EQ(response.size(),Samples);
        for(double value:response)EXPECT_DOUBLE_EQ(value,Drive);
    }
}

TEST(LTZoneDynamics, CopyAndStorageImagePreserveTheEffectiveCustomTimeConstant)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto source=dynamic_pointer_cast<NPulseLTZone>(core.storage->TakeObject("NPulseLTZone"));
    auto copied=dynamic_pointer_cast<NPulseLTZone>(core.storage->TakeObject("NPulseLTZone"));
    ASSERT_TRUE(source);ASSERT_TRUE(copied);
    ASSERT_TRUE(typeid(*source)==typeid(NPulseLTZone));
    ASSERT_TRUE(typeid(*copied)==typeid(NPulseLTZone));
    source->SetEnvironment(core.environment);source->SetGlobalTimeStep(2000);
    source->UseLTZIntegtation=true;source->UseSpikeStabilizer=false;
    source->TimeConstant=Tau;source->Threshold=100.;source->Init();
    ASSERT_DOUBLE_EQ(source->TimeConstant.GetData(),Tau);
    const auto original=DescribeClassImage(source);
    copied->SetEnvironment(core.environment);copied->SetGlobalTimeStep(2000);
    source->Copy(copied);copied->Init();
    EXPECT_DOUBLE_EQ(copied->TimeConstant.GetData(),Tau);
    EXPECT_FALSE(copied->UseSpikeStabilizer.GetData());
    EXPECT_TRUE(copied->UseLTZIntegtation.GetData());
    EXPECT_EQ(DescribeClassImage(copied),original);
    const auto image=RegisterClassImage(core.storage,"TimeLearnerUnit_IntegratedLtCustomTau",source);
    auto restored=dynamic_pointer_cast<NPulseLTZone>(
        core.storage->TakeObject("TimeLearnerUnit_IntegratedLtCustomTau"));
    ASSERT_TRUE(restored);
    restored->SetEnvironment(core.environment);restored->SetGlobalTimeStep(2000);restored->Init();
    EXPECT_DOUBLE_EQ(restored->TimeConstant.GetData(),Tau);
    EXPECT_FALSE(restored->UseSpikeStabilizer.GetData());
    EXPECT_TRUE(restored->UseLTZIntegtation.GetData());
    EXPECT_EQ(DescribeClassImage(restored),image.descriptor);
    core.storage->ReturnObject(restored);core.storage->ReturnObject(copied);core.storage->ReturnObject(source);
}
}
