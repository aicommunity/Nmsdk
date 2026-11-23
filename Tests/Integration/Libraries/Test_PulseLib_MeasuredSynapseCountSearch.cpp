#include "Test_PulseLib_BoundedFixture.h"
#include "TimeLearner/MeasuredSynapseCountSearch.h"
#include <limits>
#include <stdexcept>

using namespace NMSDK::TimeLearner;
using namespace NmsdkBoundedTrainingTest;

TEST(MeasuredSynapseCountSearch, TwoMeasuredPointsProposeBeyondTheNearestNeighbour)
{
    EXPECT_EQ(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,true}},1,128,1e-5),12);
    EXPECT_EQ(ProposeMeasuredSynapseCount({{4,-.01,true},{8,.01,true}},1,128,1e-5),6);
}
TEST(MeasuredSynapseCountSearch, AdjacentIntegersAreNotAnUnmeasuredExactSolution)
{
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{4,-.01,true},{5,.01,true}},1,128,1e-5));
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.01,true},{4,0.,true}},1,128,1e-5));
}
TEST(MeasuredSynapseCountSearch, KnownInconsistentNonmonotoneOrTimingInvalidMeasurementsUseFallback)
{
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,true},{2,-.019,true}},1,128,1e-5));
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,true},{3,-.021,true}},1,128,1e-5));
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,false}},1,128,1e-5));
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.02,true},{2,-.02,true}},1,128,1e-5));
}
TEST(MeasuredSynapseCountSearch, EffectiveBoundsLimitOnlyTheProposalNotItsVerdict)
{
    EXPECT_EQ(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,true}},1,6,1e-5),6);
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,true}},2,6,1e-5));
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.022,true},{2,-.020,true},{6,-.019,true}},1,6,1e-5));
    EXPECT_THROW(ProposeMeasuredSynapseCount({},0,6,1e-5),std::invalid_argument);
    EXPECT_THROW(ProposeMeasuredSynapseCount({},6,1,1e-5),std::invalid_argument);
}
TEST(MeasuredSynapseCountSearch, ExtremeFiniteErrorsCannotOverflowTheSecant)
{
    const double huge=std::numeric_limits<double>::max();
    EXPECT_EQ(ProposeMeasuredSynapseCount({{1,-huge,true},{2,-huge/2,true}},1,128,1e-5),3);
    EXPECT_EQ(ProposeMeasuredSynapseCount({{4,-huge,true},{8,huge,true}},1,128,1e-5),6);
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-huge,true},{1,huge,true},{2,1.,true}},1,128,1e-5));
    EXPECT_FALSE(ProposeMeasuredSynapseCount({{1,-.1,true},{2,std::numeric_limits<double>::quiet_NaN(),true}},1,128,1e-5));
}

namespace {
void ReachesMeasuredCountWithinBudget(ProbeRouting routing,bool damageFinal=false)
{
    const auto protocol=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=4;
    cfg.bounds={{2,2,1,16,1.,100.},{1,1,1,1,1.,100.}};
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}});
    std::vector<int> measured;
    DriveTraining(session,protocol,[&](const TrainingAction& a,auto& delay,auto& raw) {
        delay[0]=.13;raw[0]+=.0001*(a.parameters[0].synapses-8);
        if(a.finalVerification && damageFinal)raw[0]+=.001;
        if(!a.finalVerification && a.inputIndex==0)
        {
            measured.push_back(a.parameters[0].synapses);
            EXPECT_NE(session.Status(),TrainingStatus::Exact);
            EXPECT_FALSE(session.Certificate());
        }
    });
    EXPECT_EQ(measured,(std::vector<int>{1,2,8}));
    EXPECT_EQ(session.Parameters()[0].synapses,8);
    if(damageFinal)
    {
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
    }
    else
    {
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
        EXPECT_TRUE(session.Certificate()->Exact());EXPECT_EQ(session.Certificate()->Residuals().size(),2);
    }
}
}
TEST(BoundedTrainingMeasuredCount, ClassicNeedsFreshMeasurementsAndFinalCertificate)
{ReachesMeasuredCountWithinBudget(ProbeRouting::ClassicBurst);}
TEST(BoundedTrainingMeasuredCount, BranchNeedsFreshMeasurementsAndFinalCertificate)
{ReachesMeasuredCountWithinBudget(ProbeRouting::BranchSoloBurst);}
TEST(BoundedTrainingMeasuredCount, AGoodSearchPointDoesNotCertifyAChangedFinalResponse)
{ReachesMeasuredCountWithinBudget(ProbeRouting::BranchSoloBurst,true);}
TEST(BoundedTrainingMeasuredCount, AMeasuredWorseOvershootStillRefinesItsBracket)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto protocol=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=8;
        cfg.bounds={{2,2,1,16,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}});
        std::vector<int> measured;
        DriveTraining(session,protocol,[&](const TrainingAction& a,auto& delay,auto& raw) {
            const auto n=a.parameters[0].synapses;delay[0]=.13;
            raw[0]+=n<=2?.001*(n-10):.00225*(n-6);
            if(!a.finalVerification && a.inputIndex==0)measured.push_back(n);
        });
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);
        EXPECT_EQ(measured,(std::vector<int>{1,2,10,6}));
    }
}
TEST(BoundedTrainingMeasuredCount, KnownUnstableRepeatsDoNotCreateAFittedJump)
{
    const auto protocol=Protocol();auto cfg=Configuration();cfg.maximumCandidatesPerInput=4;cfg.n0CandidateRepeats=2;
    cfg.bounds={{2,2,1,16,1.,100.},{1,1,1,1,1.,100.}};
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}});
    std::vector<int> measured;unsigned countTwoMeasurements=0;
    DriveTraining(session,protocol,[&](const TrainingAction& a,auto& delay,auto& raw) {
        const int n=a.parameters[0].synapses;delay[0]=.13;raw[0]+=.0001*(n-8);
        if(!a.finalVerification && a.inputIndex==0)
        {
            measured.push_back(n);
            if(n==2 && ++countTwoMeasurements%2==0)raw[0]+=.0002;
        }
    });
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(std::find(measured.begin(),measured.end(),8),measured.end());
    if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
}

namespace {
void RefinesBeforeReservingOrdinaryNeighbours(ProbeRouting routing,bool damageFinal=false)
{
    const auto protocol=Protocol(2,routing);auto cfg=Configuration();
    cfg.maximumCandidatesPerInput=8;cfg.maximumProbes=160;
    cfg.bounds={{2,2,1,16,1.,100.},{1,1,1,1,1.,100.}};
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}});
    std::vector<int> measured;
    DriveTraining(session,protocol,[&](const TrainingAction& a,auto& delay,auto& raw) {
        const int n=a.parameters[0].synapses;delay[0]=.13;
        // Controlled complete observations exercise the production controller,
        // not a physical-neuron result. The monotone response needs several
        // measured refinements; its first secant does not solve the amplitude.
        const double residual=n<=2?-.00265+.00025*n:
            n<=11?-.00215+(n-2)*(.00215-.0002684)/9.:
            n==12?-.0001118:.0001*(n-13);
        raw[0]+=residual;
        if(a.finalVerification && damageFinal)raw[0]+=.001;
        if(!a.finalVerification && a.inputIndex==0)
        {
            measured.push_back(n);
            EXPECT_NE(session.Status(),TrainingStatus::Exact);
            EXPECT_FALSE(session.Certificate());
        }
    });
    // The old eager neighbour reservations consume the same finite local
    // allowance before Ns=13, then fall back to 3,4,... until this budget ends.
    EXPECT_EQ(measured,(std::vector<int>{1,2,11,12,13}));
    EXPECT_EQ(session.Parameters()[0].synapses,13);
    EXPECT_LE(session.IssuedProbes(),cfg.maximumProbes);
    EXPECT_LE(session.AppliedEdits(),cfg.maximumEdits);
    if(damageFinal)
    {
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
    }
    else
    {
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);
        ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
        EXPECT_EQ(session.Certificate()->Residuals().size(),2);
    }
}
}
TEST(BoundedTrainingMeasuredCount, ClassicRefinesBeforeReservingOrdinaryNeighbours)
{RefinesBeforeReservingOrdinaryNeighbours(ProbeRouting::ClassicBurst);}
TEST(BoundedTrainingMeasuredCount, BranchRefinesBeforeReservingOrdinaryNeighbours)
{RefinesBeforeReservingOrdinaryNeighbours(ProbeRouting::BranchSoloBurst);}
TEST(BoundedTrainingMeasuredCount, DeferredNeighboursNeverReplaceAFreshFinalCertificate)
{RefinesBeforeReservingOrdinaryNeighbours(ProbeRouting::BranchSoloBurst,true);}
