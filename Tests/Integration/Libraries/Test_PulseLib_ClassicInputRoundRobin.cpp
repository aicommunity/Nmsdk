#include <gtest/gtest.h>
#include "Test_PulseLib_BoundedFixture.h"
#include "TimeLearner/TrainingCapacitance.h"
#include "TimeLearner/InputTraversalJson.h"
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

TEST(ClassicInputRoundRobin, InsufficientBudgetCannotStageAnUnmeasuredSelection)
{
    const auto protocol=Protocol(4);auto config=RoundRobin();config.maximumProbes=7;
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(4,{1,1,10.}));
    DriveTraining(session,protocol);
    EXPECT_TRUE(session.Evidence().empty());
    EXPECT_EQ(session.IssuedProbes(),0u);EXPECT_EQ(session.AppliedEdits(),0u);
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(session.Reason(),"cyclic_selection_has_no_admissible_proposal");
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
    std::set<std::size_t> improvedPaths;
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto&) {
        // Make L=2 a measured improvement on EVERY path, still outside the
        // timing tolerance. With a length-independent response L=1 legitimately
        // wins the change-cost tie; requiring final L=2 would test no invariant.
        for(std::size_t i=0;i<3;++i)
            if(action.parameters[i].length==2) {
                delay[i]+=.05*(3-i);
                if(action.inputIndex==i && !action.finalVerification)improvedPaths.insert(i);
            }
        std::size_t changed=0;
        for(std::size_t i=0;i<4;++i)if(action.parameters[i]!=previous[i])++changed;
        // Every independent path may change its own candidate. A re-entry or
        // best proposal cannot reinstate a saved complete graph of other paths.
        EXPECT_LE(changed,1u);EXPECT_EQ(action.parameters.back(),previous.back());
        previous=action.parameters;
    });
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
    EXPECT_EQ(improvedPaths,(std::set<std::size_t>{0,1,2}));
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
    std::map<std::size_t,std::size_t> measured,rechecks,restores;
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
        ASSERT_TRUE(action.capacitance);EXPECT_EQ(action.capacitance->origin,initial.origin);
        EXPECT_EQ(action.capacitance->membraneScales.at("Dendrite1_3"),.97);
        EXPECT_EQ(action.capacitance->membraneScales.at("Dendrite4_1"),1.1);
        if(!action.finalVerification && action.inputIndex<3) {
            if(action.purpose==TrainingMeasurementPurpose::Exploration)++measured[action.inputIndex];
            if(action.purpose==TrainingMeasurementPurpose::ProposalRecheck)++rechecks[action.inputIndex];
            if(action.purpose==TrainingMeasurementPurpose::SelectedStateRestore)++restores[action.inputIndex];
        }
    });
    for(std::size_t i=0;i<3;++i)
    {EXPECT_GT(measured[i],0u);EXPECT_LE(measured[i],config.maximumCandidatesPerInput);
     EXPECT_LE(rechecks[i],config.maximumCandidatesPerInput);EXPECT_LE(restores[i],1u);}
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

TEST(ClassicInputRoundRobin, NativeTraversalGuardRejectsUnknownOrUnusedChoices)
{
    auto config=RoundRobin();
    EXPECT_NO_THROW(ValidateNativeInputTraversalConfiguration(config));
    config.candidatesPerInputVisit=3;
    EXPECT_THROW(ValidateNativeInputTraversalConfiguration(config),std::invalid_argument);
    config.candidatesPerInputVisit=1;
    config.inputTraversal=InputTraversalPolicy::Sequential;
    EXPECT_NO_THROW(ValidateNativeInputTraversalConfiguration(config));
    config.maximumTraversalSeedElements=42;
    EXPECT_THROW(ValidateNativeInputTraversalConfiguration(config),std::invalid_argument);
}

TEST(ClassicInputRoundRobin, ThreeFreshLengthPointsPerVisitCanProposeBeforeAnotherBackgroundEdit)
{
    for(const std::size_t quantum:{1u,3u})
    {
        const auto protocol=Protocol(3);auto config=RoundRobin(3);
        config.maximumCandidatesPerInput=4;config.candidatesPerInputVisit=quantum;
        config.tolerances.sync=.006;config.bounds.assign(3,{1,64,1,1,10.,10.});
        BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}));
        std::vector<std::size_t> order;std::set<std::size_t> distant;
        DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto&) {
            for(std::size_t i=0;i<2;++i)delay[i]=.003+.005*action.parameters[i].length;
            if(!action.finalVerification && action.inputIndex<2) {
                order.push_back(action.inputIndex);
                if(action.parameters[action.inputIndex].length>=20)distant.insert(action.inputIndex);
            }
        });
        if(quantum==3)
        {
            ASSERT_GE(order.size(),6u);
            EXPECT_EQ((std::vector<std::size_t>(order.begin(),order.begin()+6)),
                (std::vector<std::size_t>{0,0,0,1,1,1}));
            EXPECT_EQ(distant,(std::set<std::size_t>{0,1}));
        }
        else EXPECT_TRUE(distant.empty());
        // These controlled observations compare proposals, not physical
        // convergence. All actual residuals and final gates remain active.
        EXPECT_LE(session.IssuedProbes(),config.maximumProbes);
        EXPECT_LE(session.AppliedEdits(),config.maximumEdits);
    }
}

void EarlierVisitBestMustRemainARecheckProposal(Normalization normalization)
{
    const auto protocol=Protocol(3);auto config=RoundRobin(3);
    config.normalization=normalization;config.candidatesPerInputVisit=3;
    config.maximumCandidatesPerInput=6;config.bounds.assign(3,{1,6,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}));
    std::set<std::size_t> timingReady;
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
        for(std::size_t input=0;input<2;++input) {
            const int length=action.parameters[input].length;
            // A useful measured basin appears in the first visit; later legal
            // enumeration points are worse. No amplitude point is Exact.
            delay[input]=.03+(length==2?.1*(2-input):.005*(length-1));
            if(length==2)raw[input]+=.0001;
            if(length==2 && !action.finalVerification && action.inputIndex==input)
                timingReady.insert(input);
        }
    });
    ASSERT_EQ(timingReady,(std::set<std::size_t>{0,1}));
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
    EXPECT_LE(session.IssuedProbes(),config.maximumProbes);
    EXPECT_LE(session.AppliedEdits(),config.maximumEdits);
    // Old residuals cannot certify a changed graph. The earlier coordinates
    // must be retained as proposals and remeasured before final selection.
    for(std::size_t input=0;input<2;++input)EXPECT_EQ(session.Parameters()[input].length,2);
}

TEST(ClassicInputRoundRobin, EarlierVisitBestRemainsARecheckProposalN0)
{EarlierVisitBestMustRemainARecheckProposal(Normalization::SynapseCount);}
TEST(ClassicInputRoundRobin, EarlierVisitBestRemainsARecheckProposalN1)
{EarlierVisitBestMustRemainARecheckProposal(Normalization::TipResistance);}

TEST(ClassicInputRoundRobin, EarlierCoordinatesCompeteOnlyAfterFreshMeasurementInChangedBackground)
{
    const auto protocol=Protocol(3);auto config=RoundRobin(3);
    config.candidatesPerInputVisit=3;config.maximumCandidatesPerInput=6;
    config.bounds.assign(3,{1,6,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}));
    bool oldPointRemeasured=false,newPointRemeasured=false;
    DriveTraining(session,protocol,[&](const auto& action,auto& delay,auto& raw) {
        const int a=action.parameters[0].length,b=action.parameters[1].length;
        delay[0]=a==2 && b<=3?.23:a==4?.215:.03;
        delay[1]=b==6?.13:.03;
        raw[0]+=.0001;raw[1]+=.0001;
        if(action.inputIndex==0 && action.purpose==TrainingMeasurementPurpose::ProposalRecheck) {
            EXPECT_EQ(b,6);oldPointRemeasured|=a==2;newPointRemeasured|=a==4;
        }
    });
    EXPECT_TRUE(oldPointRemeasured);EXPECT_TRUE(newPointRemeasured);
    EXPECT_EQ(session.Parameters()[0].length,4);EXPECT_EQ(session.Parameters()[1].length,6);
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
}

TEST(ClassicInputRoundRobin, SelectionReservesFiniteGlobalBudgetsAtQuantumOneAndThree)
{
    for(const std::size_t quantum:{1u,3u})for(const std::size_t limit:{7u,17u,23u,31u,39u,45u,60u})
    {
        const auto protocol=Protocol(3);auto config=RoundRobin(3);
        config.candidatesPerInputVisit=quantum;config.maximumCandidatesPerInput=6;
        config.maximumProbes=limit;config.bounds.assign(3,{1,6,1,1,10.,10.});
        BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}));
        std::size_t observed=0;std::set<std::size_t> explored;
        DriveTraining(session,protocol,[&](const auto& action,auto&,auto& raw) {
            ++observed;for(auto& value:raw)value+=.0001;
            if(action.inputIndex<2 && action.purpose==TrainingMeasurementPurpose::Exploration)
                explored.insert(action.inputIndex);
        });
        EXPECT_EQ(session.IssuedProbes(),observed);EXPECT_LE(observed,limit);
        EXPECT_LE(session.AppliedEdits(),config.maximumEdits);
        if(limit>=31)EXPECT_EQ(explored,(std::set<std::size_t>{0,1}));
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
        if(session.Certificate())EXPECT_FALSE(session.Certificate()->Exact());
    }
}

TEST(ClassicInputRoundRobin, RetainedProposalRechecksRepeatEveryAnchorInputPair)
{
    const auto protocol=Protocol(3);auto config=RoundRobin(3);
    config.n0CandidateRepeats=2;config.candidatesPerInputVisit=1;
    config.maximumCandidatesPerInput=4;config.bounds.assign(3,{1,4,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}));
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto& raw) {
        if(action.inputIndex<2)raw[action.inputIndex]+=.0001;
    });
    std::size_t rechecked=0;
    for(const auto& e:session.Evidence())if(e.purpose==TrainingMeasurementPurpose::ProposalRecheck)++rechecked;
    EXPECT_GT(rechecked,0u);
    for(const auto& group:session.CandidateRepeats()) {
        EXPECT_TRUE(group.complete);EXPECT_EQ(group.trialIds.size(),2u);EXPECT_EQ(group.anchorTrialIds.size(),2u);
    }
    EXPECT_LE(session.IssuedProbes(),config.maximumProbes);EXPECT_NE(session.Status(),TrainingStatus::Exact);
}

TEST(ClassicInputRoundRobin, HistoricalN1CoordinatesCannotBorrowAnOldResistanceDomain)
{
    const auto protocol=Protocol(3);auto config=RoundRobin(3);
    config.normalization=Normalization::TipResistance;config.maximumCandidatesPerInput=4;
    config.bounds.assign(3,{1,3,1,1,1.,100.});
    BoundedTrainingSession session(References(protocol),config,std::vector<InputParameters>(3,{1,1,10.}),true);
    std::size_t freshDomains=0,rechecked=0;
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
        if(action.purpose==TrainingMeasurementPurpose::ProposalRecheck)++rechecked;
    },[&](const auto& action) {
        ResistanceDomainAssessment domain;domain.status=ResistanceDomainStatus::Available;
        domain.baseModelRevision=action.baseModelRevision;domain.geometry=action.parameters;
        domain.capacitance=action.capacitance;domain.inputIndex=action.inputIndex;domain.sourceAmplitude=1.;
        domain.previewModelRevision="selection-preview/"+std::to_string(action.serial);
        const bool selection=action.purpose!=TrainingMeasurementPurpose::Exploration;
        if(selection)++freshDomains;
        domain.minimumResistance=selection?25.:1.;domain.maximumResistance=selection?75.:100.;return domain;
    });
    EXPECT_GT(freshDomains,0u);EXPECT_EQ(rechecked,0u);
    EXPECT_EQ(session.Status(),TrainingStatus::SearchUnresolved);EXPECT_FALSE(session.Certificate());
    EXPECT_TRUE(std::any_of(session.Rejected().begin(),session.Rejected().end(),[](const auto& r) {
        return r.reason=="proposal_selection:historical_resistance_outside_fresh_domain";
    }));
}

TEST(InputTraversalCodec, OmissionResetsTheOldPolicyWithoutInventingFields)
{
    auto configuration=RoundRobin();configuration.maximumTraversalSeedElements=4096;
    QJsonObject search{{"other",5}};TakeInputTraversalDeclaration(search,configuration);
    EXPECT_EQ(configuration.inputTraversal,InputTraversalPolicy::Sequential);
    EXPECT_EQ(configuration.candidatesPerInputVisit,1u);EXPECT_EQ(configuration.maximumTraversalSeedElements,131072u);
    AppendInputTraversalDeclaration(search,configuration);EXPECT_EQ(search,QJsonObject({{"other",5}}));
}

TEST(InputTraversalCodec, RoundTripRetainsTheWholeDeclaredQuantumAndSeedLimit)
{
    auto before=RoundRobin();before.maximumCandidatesPerInput=8;before.candidatesPerInputVisit=3;
    before.maximumTraversalSeedElements=4096;QJsonObject search;AppendInputTraversalDeclaration(search,before);
    const auto declaration=search;auto after=Configuration(4);
    TakeInputTraversalDeclaration(search,after);EXPECT_TRUE(search.isEmpty());
    EXPECT_EQ(after.inputTraversal,before.inputTraversal);EXPECT_EQ(after.candidatesPerInputVisit,3u);
    EXPECT_EQ(after.maximumTraversalSeedElements,4096u);AppendInputTraversalDeclaration(search,after);
    EXPECT_EQ(search,declaration);
}

TEST(InputTraversalCodec, UnknownSchemaBooleanCountsAndExtraFieldsDoNotPartlyMutateInput)
{
    auto original=RoundRobin();QJsonObject encoded;AppendInputTraversalDeclaration(encoded,original);
    for(int defect=0;defect<6;++defect)
    {
        auto search=encoded;auto value=search["input_traversal"].toObject();
        if(defect==0)value["schema_version"]=2;
        else if(defect==1)value["maximum_seed_elements"]=true;
        else if(defect==2)value["candidates_per_visit"]=.5;
        else if(defect==3)value["policy"]="sequential";
        else if(defect==4)value["unknown"]=1;
        else value.remove("candidates_per_visit");
        search["input_traversal"]=value;const auto before=search;auto target=Configuration(4);
        EXPECT_THROW(TakeInputTraversalDeclaration(search,target),std::invalid_argument);
        EXPECT_EQ(search,before);EXPECT_EQ(target.inputTraversal,InputTraversalPolicy::Sequential);
    }
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
