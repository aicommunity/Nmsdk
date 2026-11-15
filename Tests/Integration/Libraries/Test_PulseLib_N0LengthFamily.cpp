#include "Test_PulseLib_BoundedFixture.h"

using namespace NMSDK::TimeLearner;
using namespace NmsdkBoundedTrainingTest;

namespace {
void BranchN0LengthFamily(std::size_t n,ProbeRouting routing=ProbeRouting::BranchSoloBurst,bool fixedBank=false)
{
    const auto p=Protocol(n,routing);auto cfg=Configuration(n);
    cfg.maximumCandidatesPerInput=8;cfg.bounds.assign(n,{2,64,1,1,1.,100.});
    cfg.bounds.back()={1,1,1,1,1.,100.};
    std::vector<InputParameters> initial(n,{2,1,10.});initial.back().length=1;
    if(fixedBank)for(std::size_t i=0;i+2<n;++i)initial[i].length=40;
    BoundedTrainingSession session(References(p),cfg,initial);
    const auto input=n-2;
    DriveTraining(session,p,[&](const TrainingAction& a,auto& delay,auto&) {
        // Controlled measured observations: test scheduling, not physical feasibility.
        for(std::size_t i=0;i+1<n;++i)delay[i]=.03+.1*(n-1-i);
        delay[input]=.03+.00625*a.parameters[input].length;
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_TRUE(session.Certificate()->Exact());EXPECT_EQ(session.Certificate()->Residuals().size(),n);
    EXPECT_EQ(session.Parameters()[input].length,16);
    std::vector<int> measured;
    for(const auto& e:session.Evidence())if(e.inputIndex==input)measured.push_back(e.parameters.length);
    ASSERT_GE(measured.size(),routing==ProbeRouting::BranchSoloBurst && !fixedBank?5u:4u);
    if(fixedBank || routing==ProbeRouting::ClassicBurst)EXPECT_EQ(measured[3],16);
    EXPECT_EQ((std::vector<int>(measured.begin(),measured.begin()+3)),(std::vector<int>{2,3,4}));
    EXPECT_TRUE(std::any_of(measured.begin(),measured.end(),[](int l){return l>9;}));
    EXPECT_LE(measured.size(),cfg.maximumCandidatesPerInput);
}
}
TEST(BoundedTrainingN0LengthFamily, BranchN4MeasuresDistantCandidateWithinOriginalBudget)
{BranchN0LengthFamily(4);}
TEST(BoundedTrainingN0LengthFamily, BranchN5MeasuresDistantCandidateWithinOriginalBudget)
{BranchN0LengthFamily(5);}
TEST(BoundedTrainingN0LengthFamily, NonmonotoneMeasurementsPreserveFiniteFallback)
{
    const auto p=Protocol(4,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(4);
    cfg.maximumCandidatesPerInput=8;cfg.bounds.assign(4,{2,16,1,1,1.,100.});cfg.bounds.back()={1,1,1,1,1.,100.};
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{2,1,10.},{2,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto&) {
        for(std::size_t i=0;i<3;++i)delay[i]=.03+.1*(3-i);
        const int l=a.parameters[2].length;
        delay[2]=l==2?.05:l==3?.07:l==4?.06:l==5?.08:l==6?.13:.09;
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_TRUE(session.Certificate()->Exact());EXPECT_EQ(session.Parameters()[2].length,6);
}
TEST(BoundedTrainingN0LengthFamily, ExtrapolatedProposalCannotCertifyAnUnmeasuredOrInexactPeak)
{
    const auto p=Protocol(4,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(4);
    cfg.maximumCandidatesPerInput=8;cfg.bounds.assign(4,{2,32,1,1,1.,100.});cfg.bounds.back()={1,1,1,1,1.,100.};
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{2,1,10.},{2,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto&) {
        for(std::size_t i=0;i<3;++i)delay[i]=.03+.1*(3-i);
        delay[2]=.03+.001*a.parameters[2].length;
    });
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
    if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
    for(const auto& e:session.Evidence())if(e.inputIndex==2)
    {EXPECT_LE(e.parameters.length,32);EXPECT_FALSE(e.withinTiming);}
}

TEST(BoundedTrainingN0LengthFamily, UnchangedUpstreamBankKeepsExistingDirectProposal)
{BranchN0LengthFamily(4,ProbeRouting::BranchSoloBurst,true);}
TEST(BoundedTrainingN0LengthFamily, ClassicKeepsExistingDirectProposal)
{BranchN0LengthFamily(4,ProbeRouting::ClassicBurst);}
