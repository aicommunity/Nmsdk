#include <gtest/gtest.h>
#include "TimeLearner/MeasuredLengthSearch.h"
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
TEST(BranchLengthProposalFamily, OrdinaryAndSeparatedBanksRemainDistinctMeasuredFamilies)
{
    const std::vector<InputParameters> base(4,{1,1,10.});
    auto ordinary=base,later=base,separated=base,laterSeparated=base;
    for(std::size_t i=0;i<3;++i){ordinary[i].length=2;later[i].length=7;}
    separated=ordinary;laterSeparated=later;
    for(std::size_t i=0;i<2;++i){separated[i].length=3;laterSeparated[i].length=8;}
    EXPECT_TRUE(SameBranchLengthProposalFamily(base,2,ordinary,later));
    EXPECT_TRUE(SameBranchLengthProposalFamily(base,2,separated,laterSeparated));
    EXPECT_FALSE(SameBranchLengthProposalFamily(base,2,ordinary,laterSeparated));
    auto warmBase=base;warmBase[0].length=9;warmBase[1].length=8;
    ordinary[0].length=later[0].length=9;ordinary[1].length=later[1].length=8;
    ordinary[2].resistance=later[2].resistance=5.;
    EXPECT_TRUE(SameBranchLengthProposalFamily(warmBase,2,ordinary,later));
    later[2].resistance=6.;EXPECT_FALSE(SameBranchLengthProposalFamily(warmBase,2,ordinary,later));
}
TEST(BranchLengthProposalFamily, ChangedOwnersDownstreamStateInvalidDimensionsAndNonfiniteValuesAreExcluded)
{
    const std::vector<InputParameters> base(4,{1,1,10.});auto a=base,b=base;
    for(std::size_t i=0;i<3;++i){a[i].length=2;b[i].length=3;}
    for(int fault=0;fault<7;++fault)
    {
        auto old=a,next=b;
        if(fault==0)next[0].resistance=11.;
        if(fault==1)old[0].resistance=next[0].resistance=11.;
        if(fault==2)next[1].synapses=2;
        if(fault==3)old[3].length=next[3].length=2;
        if(fault==4)next[0].length=5;
        if(fault==5)next[2].resistance=std::numeric_limits<double>::quiet_NaN();
        if(fault==6)next.pop_back();
        EXPECT_FALSE(SameBranchLengthProposalFamily(base,2,old,next))<<fault;
    }
    EXPECT_FALSE(SameBranchLengthProposalFamily(base,3,a,b));
    EXPECT_FALSE(SameBranchLengthProposalFamily({},0,{},{}));
}
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
