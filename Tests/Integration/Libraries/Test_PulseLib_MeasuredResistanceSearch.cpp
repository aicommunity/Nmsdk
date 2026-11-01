#include <gtest/gtest.h>
#include "TimeLearner/MeasuredResistanceSearch.h"
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
