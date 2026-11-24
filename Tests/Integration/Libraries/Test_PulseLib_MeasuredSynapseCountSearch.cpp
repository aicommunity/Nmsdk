#include "Test_PulseLib_BoundedFixture.h"
#include "TimeLearner/MeasuredSynapseCountSearch.h"
#include <limits>
#include <stdexcept>

using namespace NMSDK::TimeLearner;
using namespace NmsdkBoundedTrainingTest;

TEST(MeasuredSynapseCountSearch, AdjacentLocalBracketsDoNotAssumeGlobalMonotonicity)
{
    const auto brackets=MeasuredAdjacentSynapseCountBrackets(
        {{1,-.003,true},{2,.001,true},{3,-.002,true},{6,.004,true}},1,8,1e-5);
    ASSERT_EQ(brackets.size(),2u);
    EXPECT_EQ(brackets[0].lower,1);EXPECT_EQ(brackets[0].upper,2);
    EXPECT_EQ(brackets[1].lower,2);EXPECT_EQ(brackets[1].upper,3);
    EXPECT_TRUE(MeasuredAdjacentSynapseCountBrackets({{1,-.003,true},{3,.001,true}},1,8,1e-5).empty());
}
TEST(MeasuredSynapseCountSearch, LocalBracketsRequireStableFiniteTimingReadyEvidence)
{
    EXPECT_TRUE(MeasuredAdjacentSynapseCountBrackets({{1,-.003,true},{2,.001,false}},1,8,1e-5).empty());
    EXPECT_TRUE(MeasuredAdjacentSynapseCountBrackets({{1,-.003,true},{2,.001,true},{2,.002,true}},1,8,1e-5).empty());
    EXPECT_TRUE(MeasuredAdjacentSynapseCountBrackets({{1,-.003,true},{2,0.,true}},1,8,1e-5).empty());
    EXPECT_TRUE(MeasuredAdjacentSynapseCountBrackets({{1,-.003,true},{2,std::numeric_limits<double>::infinity(),true}},1,8,1e-5).empty());
    EXPECT_THROW(MeasuredAdjacentSynapseCountBrackets({},0,8,1e-5),std::invalid_argument);
}

namespace {
void CoupledLengthSearch(ProbeRouting routing,bool damageFinal=false)
{
    const auto protocol=Protocol(2,routing);auto cfg=Configuration();
    cfg.maximumCandidatesPerInput=6;cfg.maximumN0LengthProposals=2;
    cfg.bounds={{2,8,1,2,1.,100.},{1,1,1,1,1.,100.}};
    BoundedTrainingSession session(References(protocol),cfg,{{4,1,10.},{1,1,10.}});
    std::vector<std::pair<int,int>> measured;
    DriveTraining(session,protocol,[&](const TrainingAction& action,auto& delay,auto& raw) {
        const auto& p=action.parameters[0];delay[0]=.13;
        // Two legal counts straddle the goal at L=4, but neither meets it.
        // The lower neighbour is worse; the other side must remain reachable.
        const double error=p.length==5 && p.synapses==2?0.:
            p.length==4?(p.synapses==1?-.00004:.00002):.00003;
        raw[0]+=error;
        if(action.finalVerification && damageFinal)raw[0]+=.001;
        if(!action.finalVerification && action.inputIndex==0) {
            measured.emplace_back(p.length,p.synapses);
            EXPECT_NE(session.Status(),TrainingStatus::Exact);
            EXPECT_FALSE(session.Certificate());
        }
    });
    ASSERT_GE(measured.size(),4u);
    EXPECT_EQ((std::vector<std::pair<int,int>>(measured.begin(),measured.begin()+4)),
              (std::vector<std::pair<int,int>>{{4,1},{4,2},{3,2},{5,2}}));
    if(damageFinal) {
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
        if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
    } else {
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);
        ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
        EXPECT_EQ(session.Certificate()->Residuals().size(),2u);
    }
}
}
TEST(BoundedTrainingN0LengthNeighborhood, ClassicMeasuresBothSidesAndVerifiesAllInputs)
{CoupledLengthSearch(ProbeRouting::ClassicBurst);}
TEST(BoundedTrainingN0LengthNeighborhood, BranchMeasuresBothSidesAndVerifiesAllInputs)
{CoupledLengthSearch(ProbeRouting::BranchSoloBurst);}
TEST(BoundedTrainingN0LengthNeighborhood, AChangedFinalResponseCannotReuseTheSearchCertificate)
{CoupledLengthSearch(ProbeRouting::BranchSoloBurst,true);}
TEST(BoundedTrainingN0LengthNeighborhood, InvalidModeOrBudgetIsRejectedBeforeMeasurement)
{
    const auto protocol=Protocol();auto cfg=Configuration();cfg.maximumN0LengthProposals=4;
    cfg.maximumCandidatesPerInput=3;
    EXPECT_THROW((BoundedTrainingSession(References(protocol),cfg,{{2,1,10.},{1,1,10.}})),std::invalid_argument);
    cfg.maximumCandidatesPerInput=8;cfg.normalization=Normalization::TipResistance;
    EXPECT_THROW((BoundedTrainingSession(References(protocol),cfg,{{2,1,10.},{1,1,10.}})),std::invalid_argument);
}

TEST(BoundedTrainingN0LengthNeighborhood, LegacyOrderAndOneProposalKeepTheFiniteAllowance)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const std::size_t allowance:{0u,1u})
    {
        SCOPED_TRACE(int(routing));
        SCOPED_TRACE(allowance);
        const auto protocol=Protocol(2,routing);auto cfg=Configuration();
        cfg.maximumCandidatesPerInput=8;cfg.maximumN0LengthProposals=allowance;
        cfg.bounds={{2,8,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(protocol),cfg,{{4,1,10.},{1,1,10.}});
        std::vector<std::pair<int,int>> measured;
        DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
            const auto& p=action.parameters[0];delay[0]=.13;
            raw[0]+=p.length==4?(p.synapses==1?-.00004:.00002):.00003;
            if(!action.finalVerification && action.inputIndex==0)
                measured.emplace_back(p.length,p.synapses);
        });
        const std::vector<std::pair<int,int>> prefix=allowance?
            std::vector<std::pair<int,int>>{{4,1},{4,2},{3,2},{3,1}}:
            std::vector<std::pair<int,int>>{{4,1},{4,2},{5,1},{5,2}};
        ASSERT_GE(measured.size(),prefix.size());
        EXPECT_EQ((std::vector<std::pair<int,int>>(measured.begin(),measured.begin()+prefix.size())),prefix);
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
        EXPECT_LE(session.IssuedProbes(),cfg.maximumProbes);
        EXPECT_LE(session.AppliedEdits(),cfg.maximumEdits);
    }
}

TEST(BoundedTrainingN0LengthNeighborhood, StableRequiredRepeatsPrecedeEveryLengthProposal)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        SCOPED_TRACE(int(routing));
        const auto protocol=Protocol(2,routing);auto cfg=Configuration();
        cfg.maximumCandidatesPerInput=6;cfg.maximumN0LengthProposals=2;cfg.n0CandidateRepeats=2;
        cfg.bounds={{2,8,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(protocol),cfg,{{4,1,10.},{1,1,10.}});
        std::vector<std::pair<int,int>> measured;
        DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
            const auto& p=action.parameters[0];delay[0]=.13;
            raw[0]+=p.length==5 && p.synapses==2?0.:
                p.length==4?(p.synapses==1?-.00004:.00002):.00003;
            if(!action.finalVerification && action.inputIndex==0)
                measured.emplace_back(p.length,p.synapses);
        });
        const std::vector<std::pair<int,int>> expected{
            {4,1},{4,1},{4,2},{4,2},{3,2},{3,2},{5,2},{5,2}};
        EXPECT_EQ(measured,expected);
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);
        ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
        ASSERT_EQ(session.CandidateRepeats().size(),4u);
        for(const auto& group:session.CandidateRepeats()) {
            EXPECT_TRUE(group.complete);EXPECT_EQ(group.trialIds.size(),2u);
            EXPECT_EQ(group.anchorTrialIds.size(),2u);
        }
    }
}

TEST(BoundedTrainingN0LengthNeighborhood, UnstableRepeatsCannotSupplyALengthSeed)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        SCOPED_TRACE(int(routing));
        const auto protocol=Protocol(2,routing);auto cfg=Configuration();
        cfg.maximumCandidatesPerInput=6;cfg.maximumN0LengthProposals=2;cfg.n0CandidateRepeats=2;
        cfg.bounds={{2,8,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(protocol),cfg,{{4,1,10.},{1,1,10.}});
        std::vector<std::pair<int,int>> measured;unsigned upperRepeats=0;
        DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
            const auto& p=action.parameters[0];delay[0]=.13;
            raw[0]+=p.length==4?(p.synapses==1?-.00004:.00002):.00003;
            if(!action.finalVerification && action.inputIndex==0) {
                measured.emplace_back(p.length,p.synapses);
                if(p.length==4 && p.synapses==2 && ++upperRepeats==2)raw[0]+=.0002;
            }
        });
        const std::vector<std::pair<int,int>> prefix{{4,1},{4,1},{4,2},{4,2},{5,1},{5,1}};
        ASSERT_GE(measured.size(),prefix.size());
        EXPECT_TRUE(std::equal(prefix.begin(),prefix.end(),measured.begin()));
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
    }
}

TEST(BoundedTrainingN0LengthNeighborhood, CapacitanceContextsShareOneInputAllowance)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        SCOPED_TRACE(int(routing));
        const auto protocol=Protocol(2,routing);auto cfg=Configuration();
        cfg.maximumCandidatesPerInput=24;cfg.maximumN0LengthProposals=1;
        cfg.bounds={{2,8,1,2,1.,100.},{1,1,1,1,1.,100.}};
        cfg.capacitanceSearch=CapacitanceSearchPolicy{.8,1.2,0,3,16};
        TrainingCapacitance initial{std::string(64,'a'),.3,{{"Dendrite2_1",1.}}};
        for(int segment=1;segment<=8;++segment)
            initial.membraneScales["Dendrite1_"+std::to_string(segment)]=1.;
        BoundedTrainingSession session(References(protocol),cfg,{{4,1,10.},{1,1,10.}},false,initial);
        std::map<double,std::vector<std::pair<int,int>>> contexts;
        DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
            const auto& p=action.parameters[0];delay[0]=.13;
            raw[0]+=p.length==4?(p.synapses==1?-.00004:.00002):.00003;
            if(!action.finalVerification && action.inputIndex==0) {
                ASSERT_TRUE(action.capacitance);
                const auto scale=action.capacitance->membraneScales.at("Dendrite1_2");
                contexts[scale].emplace_back(p.length,p.synapses);
            }
        });
        ASSERT_EQ(contexts.size(),3u);unsigned priorityContexts=0;
        for(const auto& [scale,points]:contexts) {
            SCOPED_TRACE(scale);ASSERT_GE(points.size(),3u);
            EXPECT_EQ(points[0],(std::pair<int,int>{4,1}));
            EXPECT_EQ(points[1],(std::pair<int,int>{4,2}));
            if(points[2]==std::pair<int,int>{3,2})++priorityContexts;
            else EXPECT_EQ(points[2],(std::pair<int,int>{5,1}));
        }
        EXPECT_EQ(priorityContexts,1u);
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
    }
}

TEST(BoundedTrainingN0LengthNeighborhood, ANewSweepDoesNotRenewSpentLengthProposals)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        SCOPED_TRACE(int(routing));
        const auto protocol=Protocol(2,routing);auto cfg=Configuration();
        cfg.maximumCandidatesPerInput=6;cfg.maximumN0LengthProposals=2;cfg.maximumSweeps=2;
        cfg.bounds={{2,8,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(protocol),cfg,{{4,1,10.},{1,1,10.}});
        bool firstVerificationStarted=false;std::vector<std::pair<int,int>> secondSweep;
        DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
            const auto& p=action.parameters[0];delay[0]=.13;
            if(action.finalVerification)firstVerificationStarted=true;
            if(!firstVerificationStarted)
                raw[0]+=p.length==5 && p.synapses==2?0.:
                    p.length==4?(p.synapses==1?-.00004:.00002):.00003;
            else {
                raw[0]+=p.synapses==1?-.00004:.00002;
                if(!action.finalVerification && action.inputIndex==0)
                    secondSweep.emplace_back(p.length,p.synapses);
            }
        });
        const std::vector<std::pair<int,int>> prefix{{5,2},{5,1},{6,2}};
        ASSERT_GE(secondSweep.size(),prefix.size());
        EXPECT_TRUE(std::equal(prefix.begin(),prefix.end(),secondSweep.begin()));
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
        EXPECT_EQ(session.Reason(),"maximum_sweeps_exhausted");
    }
}

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
