#include <gtest/gtest.h>
#include "TimeLearner/AxoneLocalTimingRule.h"
#include <cmath>
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;

double Kernel(double interval, const AxoneLocalTimingParameters& p)
{
    const double lead=p.desiredLead+p.feedbackLatency;
    return p.learningRate*(interval-lead)/p.traceTimeConstant*
        std::exp(-std::abs(interval)/p.traceTimeConstant);
}

TEST(AxoneLocalTimingRule, CausalArrivalTeacherPairMatchesDeclaredKernel)
{
    const AxoneLocalTimingParameters p;
    for(double interval:{.0005,.001,.004,.02}) {
        AxoneLocalTimingRule rule(p);
        EXPECT_DOUBLE_EQ(rule.Observe(0.,true,false).delayIncrement,0.);
        EXPECT_NEAR(rule.Observe(interval,false,true).delayIncrement,Kernel(interval,p),1e-18);
    }
}

TEST(AxoneLocalTimingRule, AntiCausalTeacherArrivalPairMatchesDeclaredKernel)
{
    const AxoneLocalTimingParameters p;
    for(double interval:{.0005,.001,.004,.02}) {
        AxoneLocalTimingRule rule(p);
        EXPECT_DOUBLE_EQ(rule.Observe(0.,false,true).delayIncrement,0.);
        EXPECT_NEAR(rule.Observe(interval,true,false).delayIncrement,Kernel(-interval,p),1e-18);
    }
}

TEST(AxoneLocalTimingRule, CoincidentEventsIncludeTheirPairExactlyOnce)
{
    const AxoneLocalTimingParameters p;
    AxoneLocalTimingRule rule(p);
    const auto result=rule.Observe(0.,true,true);
    EXPECT_DOUBLE_EQ(result.beforeEvents.arrival,0.);
    EXPECT_DOUBLE_EQ(result.beforeEvents.feedback,0.);
    EXPECT_DOUBLE_EQ(result.afterEvents.arrival,1.);
    EXPECT_DOUBLE_EQ(result.afterEvents.feedback,1.);
    EXPECT_DOUBLE_EQ(result.delayIncrement,-p.learningRate*(p.desiredLead/p.traceTimeConstant));
}

TEST(AxoneLocalTimingRule, ExactDecayIsConsistentAcrossNativeTickRefinement)
{
    const AxoneLocalTimingParameters p;
    AxoneLocalTimingRule sparse(p),coarse(p),fine(p);
    sparse.Observe(0.,true,false);coarse.Observe(0.,true,false);fine.Observe(0.,true,false);
    for(int tick=1;tick<20;++tick) coarse.Observe(tick*.0005,false,false);
    for(int tick=1;tick<200;++tick) fine.Observe(tick*.00005,false,false);
    const auto reference=sparse.Observe(.01,false,true);
    const auto a=coarse.Observe(.01,false,true),b=fine.Observe(.01,false,true);
    EXPECT_NEAR(a.delayIncrement,reference.delayIncrement,1e-17);
    EXPECT_NEAR(b.delayIncrement,reference.delayIncrement,1e-17);
    EXPECT_NEAR(a.beforeEvents.arrivalAge,reference.beforeEvents.arrivalAge,1e-13);
    EXPECT_NEAR(b.beforeEvents.arrivalAge,reference.beforeEvents.arrivalAge,1e-13);
}

TEST(AxoneLocalTimingRule, DeclaredFeedbackLatencyCompensatesTheTeacherPath)
{
    AxoneLocalTimingParameters p;p.desiredLead=.002;p.feedbackLatency=.003;
    AxoneLocalTimingRule rule(p);
    rule.Observe(0.,true,false);
    EXPECT_NEAR(rule.Observe(.005,false,true).delayIncrement,0.,1e-18);
    AxoneLocalTimingRule uncompensated;
    uncompensated.Observe(0.,true,false);
    EXPECT_GT(uncompensated.Observe(.005,false,true).delayIncrement,0.);
}

TEST(AxoneLocalTimingRule, ArrivalOnlyInputDoesNotInventFeedback)
{
    AxoneLocalTimingRule rule;
    for(int event=0;event<16;++event) {
        const auto value=rule.Observe(event*.002,true,false);
        EXPECT_DOUBLE_EQ(value.delayIncrement,0.);
        EXPECT_DOUBLE_EQ(value.afterEvents.feedback,0.);
        EXPECT_DOUBLE_EQ(value.afterEvents.feedbackAge,0.);
    }
}

TEST(AxoneLocalTimingRule, ZeroLearningRateKeepsObservableTracesWithoutAnEdit)
{
    AxoneLocalTimingParameters p;p.learningRate=0.;
    AxoneLocalTimingRule rule(p);
    EXPECT_DOUBLE_EQ(rule.Observe(0.,true,true).delayIncrement,0.);
    const auto value=rule.Observe(.003,true,true);
    EXPECT_DOUBLE_EQ(value.delayIncrement,0.);
    EXPECT_GT(value.beforeEvents.arrival,0.);
    EXPECT_GT(value.beforeEvents.feedback,0.);
}

TEST(AxoneLocalTimingRule, InvalidClockAndRepeatedTickLeaveTheTracesUnchanged)
{
    AxoneLocalTimingRule rule;
    rule.Observe(.01,true,false);
    EXPECT_THROW(rule.Observe(.01,false,true),std::invalid_argument);
    EXPECT_THROW(rule.Observe(.009,false,true),std::invalid_argument);
    EXPECT_THROW(rule.Observe(std::numeric_limits<double>::quiet_NaN(),false,true),std::invalid_argument);
    const auto state=rule.StateAt(.01);
    EXPECT_DOUBLE_EQ(state.arrival,1.);
    EXPECT_DOUBLE_EQ(state.feedback,0.);
    EXPECT_DOUBLE_EQ(rule.Observe(.011,false,true).beforeEvents.feedback,0.);
}

TEST(AxoneLocalTimingRule, VeryLongSilenceDecaysWithoutInfTimesZero)
{
    AxoneLocalTimingRule rule;
    rule.Observe(0.,true,true);
    const auto value=rule.Observe(std::numeric_limits<double>::max(),false,false);
    EXPECT_DOUBLE_EQ(value.delayIncrement,0.);
    EXPECT_DOUBLE_EQ(value.afterEvents.arrival,0.);
    EXPECT_DOUBLE_EQ(value.afterEvents.arrivalAge,0.);
    EXPECT_DOUBLE_EQ(value.afterEvents.feedback,0.);
    EXPECT_DOUBLE_EQ(value.afterEvents.feedbackAge,0.);
}

TEST(AxoneLocalTimingRule, MultipleArrivalsContributeWithoutSelectingAnOrdinal)
{
    const AxoneLocalTimingParameters p;
    AxoneLocalTimingRule rule(p);
    rule.Observe(0.,true,false);rule.Observe(.002,true,false);
    EXPECT_NEAR(rule.Observe(.005,false,true).delayIncrement,Kernel(.005,p)+Kernel(.003,p),1e-18);
}

TEST(AxoneLocalTimingRule, RejectsInvalidParametersAndDynamicsResetTime)
{
    const double nan=std::numeric_limits<double>::quiet_NaN();
    for(int field=0;field<4;++field) {
        AxoneLocalTimingParameters p;
        if(field==0)p.traceTimeConstant=nan;
        if(field==1)p.learningRate=nan;
        if(field==2)p.desiredLead=nan;
        if(field==3)p.feedbackLatency=nan;
        EXPECT_THROW((void)AxoneLocalTimingRule(p),std::invalid_argument);
    }
    AxoneLocalTimingParameters p;p.traceTimeConstant=0.;
    EXPECT_THROW((void)AxoneLocalTimingRule(p),std::invalid_argument);
    p={};p.learningRate=-1.;
    EXPECT_THROW((void)AxoneLocalTimingRule(p),std::invalid_argument);
    AxoneLocalTimingRule rule;
    rule.Observe(.001,true,false);
    EXPECT_THROW(rule.ResetDynamics(-1.),std::invalid_argument);
    EXPECT_DOUBLE_EQ(rule.StateAt(.001).arrival,1.);
    rule.ResetDynamics(.002);
    EXPECT_DOUBLE_EQ(rule.Observe(.002,false,true).delayIncrement,0.);
}
} // namespace
