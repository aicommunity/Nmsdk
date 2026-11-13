#include <gtest/gtest.h>
#include "TimeLearner/MeasuredResistanceSearch.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
TEST(MeasuredResistanceSearch, ThreeMeasuredMonotonePointsProposeAnUnmeasuredInteriorResistance)
{
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{4.,1.,true},{16.,-1.,true}},1.,16.,1e-5));
    const auto decreasing=ProposeMeasuredResistanceRefinement({{16.,-1.,true},{1.,3.,true},{4.,1.,true}},1.,16.,1e-5);
    ASSERT_TRUE(decreasing);EXPECT_NEAR(*decreasing,8.,1e-12);
    const auto increasing=ProposeMeasuredResistanceRefinement({{1.,-3.,true},{4.,-1.,true},{16.,1.,true}},1.,16.,1e-5);
    ASSERT_TRUE(increasing);EXPECT_NEAR(*increasing,8.,1e-12);
}
TEST(MeasuredResistanceSearch, NonmonotoneTimingInvalidAndInconsistentRepeatDataKeepMeshFallback)
{
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,1.,true},{4.,-1.,true},{16.,1.,true}},1.,16.,1e-5));
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,3.,true},{4.,1.,false},{16.,-1.,true}},1.,16.,1e-5));
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,3.,true},{4.,1.,true},{4.,.5,true},{16.,-1.,true}},1.,16.,1e-5));
}
TEST(MeasuredResistanceSearch, MeasuredLogTrendProposesItsRootAndNonlinearResponseIsMeasuredAgain)
{
    const auto exact=ProposeMeasuredResistanceRefinement(
        {{1.,std::log(1./6.),true},{4.,std::log(4./6.),true},{16.,std::log(16./6.),true}},1.,16.,1e-8);
    ASSERT_TRUE(exact);EXPECT_NEAR(*exact,6.,1e-12);
    // A different, curved response must not inherit that interpolation as a
    // solution. Feed every new measurement back through the production search.
    std::vector<MeasuredResistancePoint> points;
    for(double r:{1.,4.,16.})points.push_back({r,1./r-1./6.,true});
    double best=1.;
    for(unsigned step=0;step<12 && best>1e-8;++step)
    {
        const auto next=ProposeMeasuredResistanceRefinement(points,1.,16.,1e-8);
        ASSERT_TRUE(next);EXPECT_GT(*next,1.);EXPECT_LT(*next,16.);
        const double measured=1. / (*next)-1./6.;best=std::min(best,std::fabs(measured));
        points.push_back({*next,measured,true});
    }
    EXPECT_LE(best,1e-8);
}
TEST(MeasuredResistanceSearch, FiniteExtremeResidualsCannotOverflowTheSafeguardedFraction)
{
    const double maximum=std::numeric_limits<double>::max();
    const auto next=ProposeMeasuredResistanceRefinement(
        {{1e-200,maximum,true},{1.,maximum,true},{1e200,-maximum,true}},1e-200,1e200,1e-5);
    ASSERT_TRUE(next);EXPECT_TRUE(std::isfinite(*next));EXPECT_GT(*next,1.);EXPECT_LT(*next,1e200);
}
TEST(MeasuredResistanceSearch, AMeasuredPointWithinToleranceNeedsNoInventedRefinement)
{
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,3.,true},{4.,1e-6,true},{16.,-1.,true}},1.,16.,1e-5));
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,3.,true},{4.,2.,true},{16.,1.,true}},1.,16.,1e-5));
}
TEST(MeasuredResistanceSearch, EffectiveBoundsExcludeOldPointsAndInvalidNumbersCannotProposeAnEdit)
{
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,3.,true},{4.,1.,true},{16.,-1.,true}},4.,16.,1e-5));
    EXPECT_FALSE(ProposeMeasuredResistanceRefinement({{1.,3.,true},{4.,std::numeric_limits<double>::quiet_NaN(),true},{16.,-1.,true}},1.,16.,1e-5));
    EXPECT_THROW(ProposeMeasuredResistanceRefinement({},0.,16.,1e-5),std::invalid_argument);
    EXPECT_THROW(ProposeMeasuredResistanceRefinement({},16.,1.,1e-5),std::invalid_argument);
}
TEST(MeasuredResistanceSearch, WideFiniteDomainsDoNotOverflowTheGeometricMidpoint)
{
    const auto result=ProposeMeasuredResistanceRefinement({{1e-300,3.,true},{1e100,1.,true},{1e300,-1.,true}},1e-300,1e300,1e-5);
    ASSERT_TRUE(result);EXPECT_TRUE(std::isfinite(*result));EXPECT_GT(*result,1e100);EXPECT_LT(*result,1e300);
}
}
