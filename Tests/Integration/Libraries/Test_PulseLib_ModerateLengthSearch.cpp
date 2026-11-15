#include <gtest/gtest.h>
#include "TimeLearner/MeasuredLengthSearch.h"
#include <algorithm>
#include <limits>
#include <stdexcept>
#include <vector>

namespace {
using namespace NMSDK::TimeLearner;
TEST(ModerateLengthSearch, ModerateUnissuedGeometryPrecedesAnExpensiveGlobalEndpoint)
{
    std::vector<int> issued{28};
    for(const int expected:{56,42,35}) {
        const auto proposal=ProposeModerateUnvisitedLength(issued,28,28,255);
        ASSERT_TRUE(proposal);EXPECT_EQ(*proposal,expected);
        EXPECT_LE(*proposal,56);EXPECT_NE(*proposal,255);issued.push_back(*proposal);
    }
}
TEST(ModerateLengthSearch, FixedResistanceRecoveryStillLeavesTheNearestFourLengthMesh)
{
    // The real native counterexample rejects L3 with nearest mesh L2..5.
    EXPECT_EQ(ProposeModerateUnvisitedLength({2,3},3,2,64),6);
}
TEST(ModerateLengthSearch, FullDeclaredDomainRemainsReachableAfterTheModerateBand)
{
    EXPECT_EQ(ProposeModerateUnvisitedLength({2,3,4,5,6},3,2,64),64);
    std::vector<int> issued{3};
    while(const auto proposal=ProposeModerateUnvisitedLength(issued,3,2,12)) {
        ASSERT_LT(issued.size(),11u);
        EXPECT_GE(*proposal,2);EXPECT_LE(*proposal,12);
        EXPECT_EQ(std::find(issued.begin(),issued.end(),*proposal),issued.end());
        issued.push_back(*proposal);
    }
    std::sort(issued.begin(),issued.end());
    EXPECT_EQ(issued,(std::vector<int>{2,3,4,5,6,7,8,9,10,11,12}));
}
TEST(ModerateLengthSearch, DuplicateOutsideAndExhaustedInventoryCannotCreateACandidate)
{
    EXPECT_EQ(ProposeModerateUnvisitedLength({1,28,28,900},28,28,255),56);
    EXPECT_FALSE(ProposeModerateUnvisitedLength({2,3,4,5,6},3,2,6));
    EXPECT_FALSE(ProposeModerateUnvisitedLength({3},3,3,3));
}
TEST(ModerateLengthSearch, ACenterOutsideTheIndependentBankDomainStartsAtItsLegalBoundary)
{
    EXPECT_EQ(ProposeModerateUnvisitedLength({},1,28,255),28);
    EXPECT_EQ(ProposeModerateUnvisitedLength({},256,2,64),64);
    EXPECT_EQ(ProposeModerateUnvisitedLength({},28,28,255),28);
}
TEST(ModerateLengthSearch, VeryWideBoundsDoNotAllocateTheDomainOrOverflowTheGrowthBand)
{
    const int maximum=std::numeric_limits<int>::max();
    EXPECT_EQ(ProposeModerateUnvisitedLength({maximum},maximum,1,maximum),1073741824);
    EXPECT_EQ(ProposeModerateUnvisitedLength({maximum-1},maximum-1,1,maximum),1073741823);
    EXPECT_EQ(ProposeModerateUnvisitedLength({1},1,1,maximum),2);
}
TEST(ModerateLengthSearch, InvalidCenterAndBoundsCannotAuthorizeAnEdit)
{
    EXPECT_THROW(ProposeModerateUnvisitedLength({},0,1,64),std::invalid_argument);
    EXPECT_THROW(ProposeModerateUnvisitedLength({},3,0,64),std::invalid_argument);
    EXPECT_THROW(ProposeModerateUnvisitedLength({},3,64,1),std::invalid_argument);
}
}
