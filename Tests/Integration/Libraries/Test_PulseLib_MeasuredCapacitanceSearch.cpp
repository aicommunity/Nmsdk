#include <gtest/gtest.h>
#include "TimeLearner/MeasuredCapacitanceSearch.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
const std::string scope="complete-fixed-graph-and-protocol/input0/C0/selected-paths";
MeasuredCapacitancePoint Point(double scale,double low,double high)
{return {scale,low,high,scope};}

TEST(MeasuredCapacitanceSearch, SeedMeshIsFinitePositiveAbsoluteAndBounded)
{
    const auto values=CapacitanceSeedScales(.7,1.3,1.1,3,8);
    ASSERT_EQ(values.size(),8u);EXPECT_EQ(values.front(),1.1);
    EXPECT_NE(std::find(values.begin(),values.end(),1.),values.end());
    EXPECT_NE(std::find(values.begin(),values.end(),.7),values.end());
    EXPECT_NE(std::find(values.begin(),values.end(),1.3),values.end());
    auto unique=values;std::sort(unique.begin(),unique.end());
    EXPECT_EQ(std::adjacent_find(unique.begin(),unique.end()),unique.end());
    for(double scale:values){EXPECT_TRUE(std::isfinite(scale));EXPECT_GE(scale,.7);EXPECT_LE(scale,1.3);}
}
TEST(MeasuredCapacitanceSearch, FixedDomainAndSmallBudgetDoNotManufactureCandidates)
{
    EXPECT_EQ(CapacitanceSeedScales(1.,1.,1.,20,128),(std::vector<double>{1.}));
    EXPECT_EQ(CapacitanceSeedScales(.8,1.2,1.1,20,1),(std::vector<double>{1.1}));
    const auto values=CapacitanceSeedScales(2.,4.,3.,1,8);
    EXPECT_EQ(values,(std::vector<double>{3.,2.,4.}));
}
TEST(MeasuredCapacitanceSearch, SeedValidationRejectsUnsafeDeclarations)
{
    EXPECT_THROW(CapacitanceSeedScales(0.,1.,1.,2,8),std::invalid_argument);
    EXPECT_THROW(CapacitanceSeedScales(2.,1.,1.,2,8),std::invalid_argument);
    EXPECT_THROW(CapacitanceSeedScales(.8,1.2,1.3,2,8),std::invalid_argument);
    EXPECT_THROW(CapacitanceSeedScales(.8,1.2,1.,21,8),std::invalid_argument);
    EXPECT_THROW(CapacitanceSeedScales(.8,1.2,1.,2,0),std::invalid_argument);
}
TEST(MeasuredCapacitanceSearch, ThreeMeasuredScalesBracketWithoutAssumingDirection)
{
    const auto a=ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,.01,.01),Point(1.3,-.02,-.02)},scope,.7,1.3,.0005,.8);
    const auto b=ProposeMeasuredCapacitanceRefinement({Point(1.3,.02,.02),Point(.7,-.03,-.03),Point(.9,-.01,-.01)},scope,.7,1.3,.0005,.8);
    ASSERT_TRUE(a);ASSERT_TRUE(b);EXPECT_DOUBLE_EQ(*a,1.1);EXPECT_DOUBLE_EQ(*b,1.1);
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.9,.01,.01),Point(1.3,-.02,-.02)},scope,.7,1.3,.0005,.8));
}
TEST(MeasuredCapacitanceSearch, MixedEffectivePhysicsNeverCreatesARefinement)
{
    auto points=std::vector{Point(.7,.03,.03),Point(.9,.01,.01),Point(1.3,-.02,-.02)};
    points[1].comparisonScope="same-L-Ns-Rs-but-different-idle-bank-or-protocol";
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement(points,scope,.7,1.3,.0005,.8));
}
TEST(MeasuredCapacitanceSearch, InconsistentRepeatsCannotBeAveragedIntoSuccess)
{
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,.01,.01),Point(.9,-.01,-.01),Point(1.3,-.02,-.02)},scope,.7,1.3,.0005,.8));
    const auto repeated=ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,.01,.01),Point(.9,.0101,.0101),Point(1.3,-.02,-.02)},scope,.7,1.3,.0005,.8);
    ASSERT_TRUE(repeated);EXPECT_DOUBLE_EQ(*repeated,1.1);
}
TEST(MeasuredCapacitanceSearch, NonmonotoneAndFlatResponsesKeepFiniteMeshFallback)
{
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,-.01,-.01),Point(1.3,.02,.02)},scope,.7,1.3,.0005,.8));
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,.01,.01),Point(.9,.01,.01),Point(1.3,.01,.01)},scope,.7,1.3,.0005,.8));
}
TEST(MeasuredCapacitanceSearch, BroadPeakIntervalsDoNotBecomeAnInventedZero)
{
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,-.03,-.03),Point(.9,-.01,-.01),Point(1.3,-.002,.002)},scope,.7,1.3,.0005,.8));
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,-.03,-.03),Point(.9,-.0001,.0001),Point(1.3,.02,.02)},scope,.7,1.3,.0005,.8));
}
TEST(MeasuredCapacitanceSearch, OneSidedTrendProposesBoundedDampedScaleOnly)
{
    const auto value=ProposeMeasuredCapacitanceRefinement({Point(.8,-.03,-.03),Point(.9,-.02,-.02),Point(1.,-.01,-.01)},scope,.7,1.3,.0005,.8);
    ASSERT_TRUE(value);EXPECT_NEAR(*value,1.08,1e-14);
    const auto clipped=ProposeMeasuredCapacitanceRefinement({Point(.8,-.03,-.03),Point(.9,-.02,-.02),Point(1.,-.01,-.01)},scope,.7,1.05,.0005,5.);
    ASSERT_TRUE(clipped);EXPECT_DOUBLE_EQ(*clipped,1.05);
}
TEST(MeasuredCapacitanceSearch, ChangedBoundsCannotReuseAnOldThreePointTrend)
{
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,.01,.01),Point(1.3,-.02,-.02)},scope,.8,1.3,.0005,.8));
}
TEST(MeasuredCapacitanceSearch, NonfiniteAndReversedIntervalsNeverPropose)
{
    const auto nan=std::numeric_limits<double>::quiet_NaN();
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,nan,.01),Point(1.3,-.02,-.02)},scope,.7,1.3,.0005,.8));
    EXPECT_FALSE(ProposeMeasuredCapacitanceRefinement({Point(.7,.03,.03),Point(.9,.02,.01),Point(1.3,-.02,-.02)},scope,.7,1.3,.0005,.8));
    EXPECT_THROW(ProposeMeasuredCapacitanceRefinement({},"",.7,1.3,.0005,.8),std::invalid_argument);
    EXPECT_THROW(ProposeMeasuredCapacitanceRefinement({},scope,.7,1.3,.0005,0.),std::invalid_argument);
    EXPECT_THROW(ProposeMeasuredCapacitanceRefinement({},scope,.7,1.3,nan,.8),std::invalid_argument);
}
TEST(MeasuredCapacitanceSearch, WideFiniteScaleAndResidualRangesDoNotOverflowMidpoint)
{
    const auto value=ProposeMeasuredCapacitanceRefinement({Point(1e-300,-1e308,-1e308),Point(1e100,-1e307,-1e307),Point(1e308,1e307,1e307)},scope,1e-300,1e308,0.,.8);
    ASSERT_TRUE(value);EXPECT_TRUE(std::isfinite(*value));EXPECT_GT(*value,1e100);EXPECT_LT(*value,1e308);
    for(double scale:CapacitanceSeedScales(1e-300,1e308,1.,3,16))EXPECT_TRUE(std::isfinite(scale));
}
}
