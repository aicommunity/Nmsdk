#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/LegacyController.h"

namespace {
using namespace NMSDK::TimeLearner::Legacy;

TEST(LegacyControllerPolicy, DelayFallbackRemainsPredictionRatherThanMeasurement)
{
    EXPECT_DOUBLE_EQ(ChooseDelay(.1,.11,true,.41,.3,.02,.001),.11);
    EXPECT_DOUBLE_EQ(ChooseDelay(.1,.11,false,.41,.3,.02,.001),.1);
    EXPECT_DOUBLE_EQ(ChooseDelay(.1,.11,true,.9,.3,.02,.001),.1);
}

TEST(LegacyControllerPolicy, OvershootAndUndershootAffectResistanceProposal)
{
    const ResistancePolicy policy{.5,1e-6,.5,1.5,2.};
    const auto initial=ProposeResistance(100.,2.,1.,.1,.5,std::nullopt,policy);
    const auto overshoot=ProposeResistance(100.,2.,1.,.1,.5,-.1,policy);
    const auto undershoot=ProposeResistance(100.,2.,1.,.1,.5,1.,policy);
    EXPECT_TRUE(initial.adjusted); EXPECT_DOUBLE_EQ(initial.proposedResistance,150.);
    EXPECT_DOUBLE_EQ(overshoot.effectiveGain,.25);
    EXPECT_DOUBLE_EQ(overshoot.proposedResistance,125.);
    EXPECT_DOUBLE_EQ(undershoot.effectiveGain,.75);
    EXPECT_DOUBLE_EQ(undershoot.proposedResistance,175.);
}

TEST(LegacyControllerPolicy, UnmeasurableAmplitudeProducesNoAdjustment)
{
    const ResistancePolicy policy{.5,1e-6,.5,1.5,2.};
    const auto decision=ProposeResistance(100.,1e-6,1.,.1,0.,std::nullopt,policy);
    EXPECT_FALSE(decision.adjusted);
    EXPECT_DOUBLE_EQ(decision.proposedResistance,100.);
    EXPECT_DOUBLE_EQ(decision.effectiveGain,.5);
}

TEST(LegacyControllerPolicy, ProposalLeavesPerInputPhysicalBoundsToAdapter)
{
    const ResistancePolicy policy{.5,1e-6,.5,1.5,2.};
    const auto decision=ProposeResistance(100.,4.,1.,.1,1.,std::nullopt,policy);
    EXPECT_TRUE(decision.adjusted);
    EXPECT_DOUBLE_EQ(decision.proposedResistance,400.);
    // The shared policy does not invent a common interval across inputs.
    // Real topology wrappers retain their existing ClampResistance calls.
}

TEST(LegacyControllerPolicy, PeakVectorsSupportMoreThanFourInputsAndMissingPeak)
{
    std::vector<double> peaks,delays;
    ComputePeakTimes(6,10.,{true,true,false,true,true,true},
        {10.,11.,12.,13.,14.,15.},{0.,.5,1.,1.5,2.,2.5},peaks,delays);
    ASSERT_EQ(peaks.size(),6u); ASSERT_EQ(delays.size(),6u);
    EXPECT_DOUBLE_EQ(peaks[5],5.); EXPECT_DOUBLE_EQ(delays[5],2.5);
    EXPECT_DOUBLE_EQ(peaks[2],0.); EXPECT_DOUBLE_EQ(delays[2],0.);
    // Zero for missing peaks is a legacy representation, not v2 validity.
}

TEST(LegacyControllerPolicy, CounterJumpAndLegacyResetFallbackRemainUnchanged)
{
    int previous=2; double level=0.;
    EXPECT_EQ(DetectPulses(5,1.,previous,level),3);
    EXPECT_EQ(previous,5);
    EXPECT_EQ(DetectPulses(5,1.,previous,level),0);
    EXPECT_EQ(DetectPulses(0,0.,previous,level),0);
    EXPECT_EQ(previous,5); // Historical reset handling is deliberately retained.
    EXPECT_EQ(DetectPulses(1,1.,previous,level),1);
}
}
