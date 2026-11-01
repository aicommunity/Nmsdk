#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include <QJsonArray>
#include <cmath>
#include <cstdlib>
#include <limits>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;

template<class Property>
void CheckTimingProperty(Property& property,const bool strictlyPositive,
    const bool nonpositiveSeedAllowed,QJsonArray& observations)
{
    const double finite=.017123456789012345;
    for(const auto& candidate:std::vector<std::pair<const char*,double>>{
        {"nan",std::numeric_limits<double>::quiet_NaN()},
        {"positive_infinity",std::numeric_limits<double>::infinity()},
        {"negative_infinity",-std::numeric_limits<double>::infinity()}})
    {
        property.SetData(finite);
        bool rejected=false;
        try { property.SetData(candidate.second); }
        catch(const UIProperty::EPropertySetterFail&) { rejected=true; }
        EXPECT_TRUE(rejected)<<property.GetName()<<":"<<candidate.first;
        const bool preserved=property.GetData()==finite;
        EXPECT_TRUE(preserved)<<property.GetName()<<":"<<candidate.first;
        observations.append(QJsonObject{{"property",QString::fromStdString(property.GetName())},
            {"candidate",candidate.first},{"rejected",rejected},{"previous_value_preserved",preserved}});
    }
    // Existing finite domains remain distinct: Branch seed permits<=0 fallback;
    // ordinary time margins permit zero; Classic adaptive delay must be>0.
    property.SetData(finite);
    if(nonpositiveSeedAllowed)
    {
        EXPECT_NO_THROW(property.SetData(-1.));EXPECT_DOUBLE_EQ(property.GetData(),-1.);
        EXPECT_NO_THROW(property.SetData(0.));EXPECT_DOUBLE_EQ(property.GetData(),0.);
    }
    else
    {
        EXPECT_THROW(property.SetData(-1.),UIProperty::EPropertySetterFail);
        EXPECT_DOUBLE_EQ(property.GetData(),finite);
        if(strictlyPositive)
        {
            EXPECT_THROW(property.SetData(0.),UIProperty::EPropertySetterFail);
            EXPECT_DOUBLE_EQ(property.GetData(),finite);
        }
        else { EXPECT_NO_THROW(property.SetData(0.));EXPECT_DOUBLE_EQ(property.GetData(),0.); }
    }
    EXPECT_NO_THROW(property.SetData(finite));EXPECT_DOUBLE_EQ(property.GetData(),finite);
}

template<class Learner> void CheckStoredTimingContracts(const bool branch,const unsigned frequency)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    QJsonArray receipts;
    for(int pass=0;pass<2;++pass)
    {
        auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(
            branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        ASSERT_TRUE(learner);learner->SetEnvironment(core.environment);learner->SetGlobalTimeStep(frequency);
        QJsonArray checks;
        CheckTimingProperty(learner->SyncTolerance,false,false,checks);
        CheckTimingProperty(learner->PeakMeasureMargin,false,false,checks);
        CheckTimingProperty(learner->DelayAgreeMarginMin,false,false,checks);
        CheckTimingProperty(learner->IterationGap,false,false,checks);
        if constexpr(std::is_same_v<Learner,NNeuronTimeLearnerBranch>)
            CheckTimingProperty(learner->InitEstDelayPerSeg,false,true,checks);
        else CheckTimingProperty(learner->EstDelayPerSeg,true,false,checks);
        EXPECT_EQ(checks.size(),15);
        receipts.append(QJsonObject{{"take_sequence",pass},{"checks",checks}});
        core.storage->ReturnObject(learner);
    }
    if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        const auto folder=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(folder));
        NmsdkWorker::Write(folder,QString("timing-%1-f%2.json").arg(branch?"Branch":"Classic").arg(frequency),
            QJsonObject{{"kind","timelearner_native_timing_property_contract"},{"schema_version",1},
                {"topology",branch?"Branch":"Classic"},{"frequency_hz",int(frequency)},
                {"takes",receipts},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
    }
}

class NativeTimingProperties:public ::testing::TestWithParam<std::tuple<bool,unsigned>> {};
TEST_P(NativeTimingProperties, RejectNonfiniteWithoutChangingPreviousValue)
{
    const auto [branch,frequency]=GetParam();
    if(branch)CheckStoredTimingContracts<NNeuronTimeLearnerBranch>(true,frequency);
    else CheckStoredTimingContracts<NNeuronTimeLearner>(false,frequency);
}
INSTANTIATE_TEST_SUITE_P(TopologiesAndRates,NativeTimingProperties,
    ::testing::Combine(::testing::Bool(),::testing::Values(2000u,20000u)));
}
