#include <gtest/gtest.h>
#include "Test_PulseLib_BoundedFixture.h"
#include "TimeLearner/TrainingCapacitance.h"
#include <algorithm>
#include <map>
#include <set>

namespace {
using namespace NMSDK::TimeLearner;
using namespace NmsdkBoundedTrainingTest;

BoundedTrainingConfig RoundRobin(std::size_t inputs=4)
{
    auto config=Configuration(inputs);
    config.inputTraversal=InputTraversalPolicy::ClassicCandidateRoundRobin;
    config.maximumCandidatesPerInput=2;
    config.bounds.assign(inputs,{1,2,1,1,10.,10.});
    return config;
}

TEST(ClassicInputRoundRobin, CompletedCandidatesVisitEveryAdjustableInputBeforeReturning)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    std::vector<std::size_t> measured,final;
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto&) {
        for(std::size_t i=0;i<3;++i)
            if(action.parameters[i].length==2)delay[i]+=.1*(3-i);
        if(action.inputIndex<3 && !action.finalVerification)measured.push_back(action.inputIndex);
        if(action.finalVerification)final.push_back(action.inputIndex);
    });
    EXPECT_EQ(measured,(std::vector<std::size_t>{0,1,2,0,1,2}));
    EXPECT_EQ(final,(std::vector<std::size_t>{0,1,2,3}));
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);
    ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    for(std::size_t i=0;i<3;++i)EXPECT_EQ(session.Parameters()[i].length,2);
    EXPECT_EQ(session.Parameters().back().length,1);
    EXPECT_LE(session.IssuedProbes(),config.maximumProbes);
}

TEST(ClassicInputRoundRobin, RepetitionsAndAnchorInputPairsCloseBeforeYield)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();config.n0CandidateRepeats=2;
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    std::vector<std::size_t> probes;
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto&) {
        for(std::size_t i=0;i<3;++i)
            if(action.parameters[i].length==2)delay[i]+=.1*(3-i);
        if(!action.finalVerification)probes.push_back(action.inputIndex);
    });
    ASSERT_GE(probes.size(),12u);
    EXPECT_EQ((std::vector<std::size_t>(probes.begin(),probes.begin()+12)),
        (std::vector<std::size_t>{3,0,3,0,3,1,3,1,3,2,3,2}));
    ASSERT_EQ(session.CandidateRepeats().size(),6u);
    for(const auto& group:session.CandidateRepeats())
    {EXPECT_TRUE(group.complete);EXPECT_EQ(group.trialIds.size(),2u);EXPECT_EQ(group.anchorTrialIds.size(),2u);}
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);
}

TEST(ClassicInputRoundRobin, GlobalOddProbeBudgetCannotBeReplenishedAtInputSwitch)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();config.maximumProbes=7;
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    DriveTraining(session,protocol);
    ASSERT_EQ(session.Evidence().size(),3u);
    for(std::size_t i=0;i<3;++i)EXPECT_EQ(session.Evidence()[i].inputIndex,i);
    EXPECT_EQ(session.IssuedProbes(),6u);EXPECT_EQ(session.AppliedEdits(),0u);
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(session.Reason(),"candidate_probe_pair_budget_exhausted");
    EXPECT_FALSE(session.Certificate());
}

TEST(ClassicInputRoundRobin, DamagedFinalInputCannotBorrowItsEarlierLocalSuccess)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
        for(std::size_t i=0;i<3;++i)
            if(action.parameters[i].length==2)delay[i]+=.1*(3-i);
        if(action.finalVerification)raw[0]+=.001;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(session.Reason(),"maximum_sweeps_exhausted");
    ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
    ASSERT_GE(session.Evidence().size(),6u);
    EXPECT_NE(session.Evidence()[0].modelRevision,session.ModelRevision());
}

TEST(ClassicInputRoundRobin, CountsAboveFourAndSingleFixedInputHaveTheirOwnDimensions)
{
    for(const std::size_t count:{1u,2u,6u})
    {
        const auto protocol=Protocol(count);auto config=RoundRobin(count);
        BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(count,{1,1,10.}));
        std::vector<std::size_t> measured;
        DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
            if(!action.finalVerification && action.inputIndex+1<count)measured.push_back(action.inputIndex);
        });
        if(count==1)
        {EXPECT_TRUE(measured.empty());EXPECT_EQ(session.Status(),TrainingStatus::Exact);}
        else
        {
            ASSERT_GE(measured.size(),count-1);
            for(std::size_t i=0;i+1<count;++i)EXPECT_EQ(measured[i],i);
            EXPECT_NE(session.Status(),TrainingStatus::Exact);
        }
    }
}

TEST(ClassicInputRoundRobin, AnotherSweepStartsFreshWithoutResettingAttemptBudgets)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();config.maximumSweeps=2;
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    unsigned finalCount=0;std::size_t previousProbes=0,previousEdits=0;
    std::vector<std::size_t> secondSweep;
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
        for(std::size_t i=0;i<3;++i)
            if(action.parameters[i].length==2)delay[i]+=.1*(3-i);
        EXPECT_GE(session.IssuedProbes(),previousProbes);previousProbes=session.IssuedProbes();
        EXPECT_GE(session.AppliedEdits(),previousEdits);previousEdits=session.AppliedEdits();
        if(action.finalVerification) {++finalCount;raw[0]+=.001;}
        else if(finalCount && action.inputIndex<3)secondSweep.push_back(action.inputIndex);
    });
    EXPECT_EQ(secondSweep,(std::vector<std::size_t>{0,1,2}));
    EXPECT_EQ(finalCount,8u);EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(session.Reason(),"maximum_sweeps_exhausted");
    ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
}

TEST(ClassicInputRoundRobin, NativeN1RequestsFreshDomainsAfterOtherInputsEdit)
{
    const auto protocol=Protocol(3);auto config=RoundRobin(3);
    config.normalization=Normalization::TipResistance;config.maximumCandidatesPerInput=4;
    config.resistanceSubdivisionDepth=1;config.bounds.assign(3,{1,2,1,1,1.,100.});
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}),true);
    std::vector<std::size_t> measured;std::map<std::size_t,std::set<std::string>> revisions;
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
        if(!action.finalVerification && action.inputIndex<2)measured.push_back(action.inputIndex);
    },[&](const auto& action) {
        EXPECT_EQ(action.baseModelRevision,session.ModelRevision());
        revisions[action.inputIndex].insert(action.baseModelRevision);
        ResistanceDomainAssessment domain;domain.status=ResistanceDomainStatus::Available;
        domain.baseModelRevision=action.baseModelRevision;domain.geometry=action.parameters;
        domain.inputIndex=action.inputIndex;domain.sourceAmplitude=1.;
        domain.previewModelRevision="preview/"+action.baseModelRevision+"/"+std::to_string(action.inputIndex);
        domain.minimumResistance=1.;domain.maximumResistance=100.;return domain;
    });
    ASSERT_GE(measured.size(),4u);
    EXPECT_EQ((std::vector<std::size_t>(measured.begin(),measured.begin()+4)),
        (std::vector<std::size_t>{0,1,0,1}));
    EXPECT_GE(revisions[0].size(),2u);EXPECT_GE(revisions[1].size(),2u);
    EXPECT_LE(session.IssuedProbes(),config.maximumProbes);
    EXPECT_LE(session.AppliedEdits(),config.maximumEdits);
    EXPECT_FALSE(session.Status()==TrainingStatus::Exact);
}

TEST(ClassicInputRoundRobin, ChangedBackgroundNeverRestoresOtherInputParameters)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    std::vector<InputParameters> previous(4,{1,1,10.});
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
        std::size_t changed=0;
        for(std::size_t i=0;i<4;++i)if(action.parameters[i]!=previous[i])++changed;
        // Every independent path may change its own candidate. A re-entry or
        // best proposal cannot reinstate a saved complete graph of other paths.
        EXPECT_LE(changed,1u);EXPECT_EQ(action.parameters.back(),previous.back());
        previous=action.parameters;
    });
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
    for(std::size_t i=0;i<3;++i)EXPECT_EQ(session.Parameters()[i].length,2);
}

TEST(ClassicInputRoundRobin, CapacitanceContextsRemainFiniteAcrossInputSwitches)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();config.maximumCandidatesPerInput=4;
    config.capacitanceSearch=CapacitanceSearchPolicy{.8,1.2,0,2,16};
    TrainingCapacitance initial{std::string(64,'a'),.3,
        {{"Dendrite1_1",.95},{"Dendrite1_3",.97},{"Dendrite2_1",1.05},
         {"Dendrite3_1",.9},{"Dendrite4_1",1.1}}};
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}),false,initial);
    std::map<std::size_t,std::size_t> measured;
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
        ASSERT_TRUE(action.capacitance);EXPECT_EQ(action.capacitance->origin,initial.origin);
        EXPECT_EQ(action.capacitance->membraneScales.at("Dendrite1_3"),.97);
        EXPECT_EQ(action.capacitance->membraneScales.at("Dendrite4_1"),1.1);
        if(!action.finalVerification && action.inputIndex<3)++measured[action.inputIndex];
    });
    for(std::size_t i=0;i<3;++i)
    {EXPECT_GT(measured[i],0u);EXPECT_LE(measured[i],config.maximumCandidatesPerInput+1);}
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
    EXPECT_LE(session.AppliedEdits(),config.maximumEdits);
}

TEST(ClassicInputRoundRobin, BranchUnknownPolicyAndUnboundedSeedInventoryAreRejected)
{
    auto config=RoundRobin();const auto initial=std::vector<InputParameters>(4,{1,1,10.});
    EXPECT_THROW((BoundedTrainingSession(References(Protocol(4,ProbeRouting::BranchSoloBurst)),config,initial)),std::invalid_argument);
    config.inputTraversal=static_cast<InputTraversalPolicy>(42);
    EXPECT_THROW((BoundedTrainingSession(References(Protocol(4)),config,initial)),std::invalid_argument);
    config=RoundRobin();config.maximumTraversalSeedElements=0;
    EXPECT_THROW((BoundedTrainingSession(References(Protocol(4)),config,initial)),std::invalid_argument);
    config.maximumTraversalSeedElements=8;
    EXPECT_THROW((BoundedTrainingSession(References(Protocol(4)),config,initial)),std::invalid_argument);
}

TEST(ClassicInputRoundRobin, ExternalStopCannotPromoteEarlierInputMeasurements)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    for(unsigned probe=0;probe<2;++probe)
    {
        const auto action=session.NextAction();ASSERT_TRUE(action);ASSERT_EQ(action->kind,TrainingActionKind::Probe);
        const auto prepared=Prepare(protocol,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);
        session.Consume(Observe(protocol,prepared,action->inputIndex,action->runId,action->trialId,
            std::vector<double>(4,.03),Raw(4)),action->baseModelRevision);
    }
    ASSERT_EQ(session.Evidence().size(),1u);session.ExternalStop();
    EXPECT_EQ(session.Status(),TrainingStatus::ExternalStop);EXPECT_FALSE(session.NextAction());EXPECT_FALSE(session.Certificate());
}

TEST(ClassicInputRoundRobin, UnboundNativeCodecCannotSilentlyLoseTheOptInPolicy)
{
    auto config=RoundRobin();
    EXPECT_THROW(ValidateNativeInputTraversalConfiguration(config),std::invalid_argument);
    config.inputTraversal=InputTraversalPolicy::Sequential;
    EXPECT_NO_THROW(ValidateNativeInputTraversalConfiguration(config));
    config.maximumTraversalSeedElements=42;
    EXPECT_THROW(ValidateNativeInputTraversalConfiguration(config),std::invalid_argument);
}

TEST(ClassicInputCapacitanceOwner, RestoreKeepsOtherCurrentCorrectionsIncludingPrefixNeighbour)
{
    TrainingCapacitance old{std::string(64,'a'),.3,
        {{"Dendrite1_1",.8},{"Dendrite1_9",.9},{"Dendrite2_1",1.},{"Dendrite10_1",1.}}};
    auto current=old;current.membraneScales["Dendrite1_1"]=1.1;
    current.membraneScales["Dendrite1_10"]=1.2;
    current.membraneScales["Dendrite2_1"]=.85;current.membraneScales["Dendrite10_1"]=.95;
    const auto restored=RestoreClassicDendriteCapacitance(old,current,1);ASSERT_TRUE(restored);
    EXPECT_EQ(restored->membraneScales.at("Dendrite1_1"),.8);
    EXPECT_EQ(restored->membraneScales.at("Dendrite1_9"),.9);
    EXPECT_EQ(restored->membraneScales.at("Dendrite1_10"),1.);
    EXPECT_EQ(restored->membraneScales.at("Dendrite2_1"),.85);
    EXPECT_EQ(restored->membraneScales.at("Dendrite10_1"),.95);
    EXPECT_EQ(RestoreClassicDendriteCapacitance(old,*restored,1),restored);
    EXPECT_EQ(current.membraneScales.at("Dendrite1_1"),1.1);
}

TEST(ClassicInputCapacitanceOwner, OriginPolicyAndHistoricalPathLossAreNotRepaired)
{
    TrainingCapacitance old{std::string(64,'a'),.3,{{"Dendrite1_1",.8},{"Dendrite2_1",1.}}};
    auto changed=old;changed.origin=std::string(64,'b');
    EXPECT_THROW(RestoreClassicDendriteCapacitance(old,changed,1),std::invalid_argument);
    changed=old;changed.maximumRelativeChange=.4;
    EXPECT_THROW(RestoreClassicDendriteCapacitance(old,changed,1),std::invalid_argument);
    changed=old;changed.membraneScales.erase("Dendrite2_1");
    EXPECT_THROW(RestoreClassicDendriteCapacitance(old,changed,1),std::invalid_argument);
    EXPECT_THROW(RestoreClassicDendriteCapacitance(old,old,0),std::invalid_argument);
    EXPECT_FALSE(RestoreClassicDendriteCapacitance({}, {},1));
    EXPECT_THROW(RestoreClassicDendriteCapacitance({},old,1),std::invalid_argument);
}
}
