#include "Test_PulseLib_BoundedFixture.h"
#include <iterator>

using namespace NMSDK::TimeLearner;
using namespace NmsdkBoundedTrainingTest;

namespace {
void N0LocalGeometryAfterBetterGlobalCandidate(ProbeRouting routing,std::size_t n=2,std::size_t repeats=1)
{
    const auto p=Protocol(n,routing);auto cfg=Configuration(n);
    cfg.maximumCandidatesPerInput=n==2?4:5;cfg.n0CandidateRepeats=repeats;
    cfg.bounds.assign(n,{1,20,1,2,1.,100.});cfg.bounds.back()={1,1,1,1,1.,100.};
    std::vector<InputParameters> initial(n,{1,1,10.});
    BoundedTrainingSession session(References(p),cfg,initial);
    const auto input=n-2;
    DriveTraining(session,p,[&](const TrainingAction& action,auto& delay,auto& raw) {
        // Controlled observations exercise the production controller, not
        // physical feasibility. A good-but-inexact Ns2/L1 must not suppress
        // normalization at L2, whose initial Ns1 is globally much worse.
        for(std::size_t i=0;i+1<n;++i)delay[i]=.03+.1*(n-1-i);
        const auto& candidate=action.parameters[input];
        if(candidate.length==1)raw[input]+=candidate.synapses==2?.0002:.002;
        else if(candidate.length==2)raw[input]+=candidate.synapses==2?0.:.003;
        else {raw[input]+=.004;delay[input]=.03;}
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_TRUE(session.Certificate()->Exact());EXPECT_EQ(session.Certificate()->Residuals().size(),n);
    EXPECT_EQ(session.Parameters()[input],(InputParameters{2,2,10.}));
    const auto& history=session.Evidence();
    const auto first=std::find_if(history.begin(),history.end(),[&](const auto& e) {
        return e.inputIndex==input && e.parameters.length==1 && e.parameters.synapses==2;
    });
    const auto later=std::find_if(history.begin(),history.end(),[&](const auto& e) {
        return e.inputIndex==input && e.parameters.length==2 && e.parameters.synapses==1;
    });
    const auto exact=std::find_if(history.begin(),history.end(),[&](const auto& e) {
        return e.inputIndex==input && e.parameters.length==2 && e.parameters.synapses==2 && e.withinAmplitude;
    });
    ASSERT_NE(first,history.end());ASSERT_NE(later,history.end());ASSERT_NE(exact,history.end());
    EXPECT_LT(first,later);EXPECT_LT(later,exact);
    EXPECT_LT(std::fabs(first->amplitudeResidual),std::fabs(later->amplitudeResidual));
    if(n==4)EXPECT_EQ(exact->fullParameters,(std::vector<InputParameters>{{3,1,10.},{3,1,10.},{2,2,10.},{1,1,10.}}));
    if(repeats>1)
        for(const auto& group:session.CandidateRepeats())
        {EXPECT_TRUE(group.complete);EXPECT_EQ(group.trialIds.size(),repeats);EXPECT_EQ(group.anchorTrialIds.size(),repeats);}
}
}
TEST(BoundedTrainingN0Geometry, ClassicLaterGeometryNormalizesDespiteWorseStartingAmplitude)
{N0LocalGeometryAfterBetterGlobalCandidate(ProbeRouting::ClassicBurst);}
TEST(BoundedTrainingN0Geometry, BranchLaterGeometryNormalizesDespiteWorseStartingAmplitude)
{N0LocalGeometryAfterBetterGlobalCandidate(ProbeRouting::BranchSoloBurst);}
TEST(BoundedTrainingN0Geometry, BranchN4SeparatesTheUpstreamBankBeforeCountMeasurement)
{N0LocalGeometryAfterBetterGlobalCandidate(ProbeRouting::BranchSoloBurst,4);}
TEST(BoundedTrainingN0Geometry, LocalHistoryWaitsForCompleteRepeatedCandidates)
{N0LocalGeometryAfterBetterGlobalCandidate(ProbeRouting::ClassicBurst,2,2);}
TEST(BoundedTrainingN0Geometry, ImprovingCountsCannotConsumeTheWholeBudgetBeforeAnotherLength)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=30;
        cfg.bounds={{1,2,1,128,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
        DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto& raw) {
            delay[0]=.13;raw[0]+=.005/a.parameters[0].synapses;
        });
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        const auto& points=session.Evidence();
        const auto other=std::find_if(points.begin(),points.end(),[](const auto& e){return e.parameters.length==2;});
        ASSERT_NE(other,points.end());EXPECT_LT(std::distance(points.begin(),other),15);
        EXPECT_LE(points.size(),cfg.maximumCandidatesPerInput);
        if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
    }
}
TEST(BoundedTrainingN0Geometry, WorseNeighborDoesNotRemoveANonmonotoneFallbackSolution)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=6;
        cfg.bounds={{1,2,1,3,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
        DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto& raw) {
            const auto& point=a.parameters[0];delay[0]=.13;
            if(point.length==1)raw[0]+=point.synapses==3?0.:.001*(point.synapses+1);
            else raw[0]+=.004+.001*point.synapses;
        });
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
        EXPECT_TRUE(session.Certificate()->Exact());EXPECT_EQ(session.Parameters()[0],(InputParameters{1,3,10.}));
    }
}
