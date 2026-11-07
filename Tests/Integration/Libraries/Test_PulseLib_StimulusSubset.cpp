#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StimulusSubset.h"
#include <limits>
#include <stdexcept>
using namespace NMSDK::TimeLearner;

TEST(StimulusSubset, FullSelectionPreservesOriginalIntervals)
{
    const std::vector<double> source{.01,.08,.16,.24};
    const auto result=PlanStimulusSubset(source,{0,1,2,3});
    EXPECT_EQ(result.presentedIsi,source);EXPECT_EQ(result.sourceOffsets.size(),4u);
}
TEST(StimulusSubset, RemovingInteriorEventKeepsSourceOrdinals)
{
    const auto result=PlanStimulusSubset({.125,.125,.25,.5},{0,2,3});
    EXPECT_EQ(result.presentedIsi,(std::vector<double>{.125,.375,.5}));
    EXPECT_EQ(result.sourceOffsets,(std::vector<double>{.125,.5,1.}));
}
TEST(StimulusSubset, LaterSingleImpulseKeepsItsOriginalRequestedTime)
{
    const auto result=PlanStimulusSubset({.125,.125,.25,.5},{3});
    EXPECT_EQ(result.presentedIsi,(std::vector<double>{1.}));
    EXPECT_EQ(result.sourceOffsets,(std::vector<double>{1.}));
}
TEST(StimulusSubset, ZeroIntervalsArePreservedWithoutInventingEvents)
{
    const auto result=PlanStimulusSubset({0.,0.,.25},{0,1,2});
    EXPECT_EQ(result.presentedIsi,(std::vector<double>{0.,0.,.25}));
    // Native duplicate-time emission validity is a separate measured contract.
    EXPECT_EQ(result.sourceOffsets,(std::vector<double>{0.,0.,.25}));
}
TEST(StimulusSubset, RejectsEmptyAndInvalidOrdinals)
{
    EXPECT_THROW(PlanStimulusSubset({},{}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.},{}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.},{1}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.,2.},{1,0}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.,2.},{0,0}),std::invalid_argument);
}
TEST(StimulusSubset, RejectsInvalidUnselectedSourceIntervals)
{
    for(double value:{-1.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
        EXPECT_THROW(PlanStimulusSubset({.1,value},{0}),std::invalid_argument);
}
TEST(StimulusSubset, RejectsOverflowEvenAfterLastSelectedEvent)
{
    const auto huge=std::numeric_limits<double>::max();
    EXPECT_THROW(PlanStimulusSubset({.1,huge,huge},{0}),std::invalid_argument);
}
