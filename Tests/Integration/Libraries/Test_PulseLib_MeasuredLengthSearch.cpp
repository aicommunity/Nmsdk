#include <gtest/gtest.h>
#include "TimeLearner/MeasuredLengthSearch.h"
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
TEST(MeasuredLengthSearch, ThreeMeasuredPointsCanProposeBeyondTheNearestMesh)
{
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09}},1,20,.005));
    EXPECT_EQ(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,-.08,-.08}},1,20,.005),12);
    EXPECT_EQ(ProposeMeasuredLength({{2,.1,.1},{3,.09,.09},{4,.08,.08}},1,20,.005),12);
}
TEST(MeasuredLengthSearch, BracketUsesOnlyAnUnmeasuredBoundedInteger)
{
    EXPECT_EQ(ProposeMeasuredLength({{2,-.1,-.1},{6,-.04,-.04},{14,.04,.04}},1,20,.005),10);
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.04,-.04},{4,.04,.04}},1,20,.005));
    EXPECT_EQ(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,-.08,-.08}},1,8,.005),8);
}
TEST(MeasuredLengthSearch, NonmonotoneFlatAndAmbiguousIntervalsKeepEnumeration)
{
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.08,-.08},{4,-.09,-.09}},1,20,.005));
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.1,-.1},{4,-.1,-.1}},1,20,.005));
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.05,-.05},{4,-.01,.01}},1,20,.005));
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.05,-.05},{4,-.001,.001}},1,20,.005));
}
TEST(MeasuredLengthSearch, RepeatedIntervalsCannotBeAveragedIntoASlope)
{
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,-.08,-.08},{4,-.02,-.02}},1,20,.005));
    EXPECT_EQ(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,-.08,-.08},{4,-.08,-.08}},1,20,.005),12);
}
TEST(MeasuredLengthSearch, InvalidNumbersAndDomainsNeverProposeAnEdit)
{
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,std::numeric_limits<double>::quiet_NaN(),0.}},1,20,.005));
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,.1,-.1}},1,20,.005));
    EXPECT_FALSE(ProposeMeasuredLength({{2,-.1,-.1},{3,-.09,-.09},{4,-.08,-.08}},3,20,.005));
    EXPECT_THROW(ProposeMeasuredLength({},0,20,.005),std::invalid_argument);
    EXPECT_THROW(ProposeMeasuredLength({},20,1,.005),std::invalid_argument);
    EXPECT_THROW(ProposeMeasuredLength({},1,20,std::numeric_limits<double>::infinity()),std::invalid_argument);
}
TEST(MeasuredLengthSearch, WideIntegerBoundsDoNotOverflowTheMidpoint)
{
    const int maximum=std::numeric_limits<int>::max();
    EXPECT_EQ(ProposeMeasuredLength({{1,-.1,-.1},{maximum-4,-.01,-.01},{maximum,.01,.01}},1,maximum,.005),maximum-2);
}
}
