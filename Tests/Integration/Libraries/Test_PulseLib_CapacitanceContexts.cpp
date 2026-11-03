#include <gtest/gtest.h>
#include "TimeLearner/BoundedTraining.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <functional>


namespace {
using namespace NMSDK::TimeLearner;
VerificationProtocol Protocol(std::size_t n=2,ProbeRouting routing=ProbeRouting::ClassicBurst)
{
    VerificationProtocol p;p.schemaVersion=3;p.routing=routing;p.revision="bounded_burst_v1";
    p.sampleId="target";p.patternHash="actual_burst_hash";p.originStimulusId="p0";
    p.maximumSampleGap=.005;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    for(std::size_t i=0;i<n;++i){p.inputs.push_back({"i"+std::to_string(i),"p"+std::to_string(i)});p.stimulusIds.push_back("p"+std::to_string(i));}
    return p;
}
PreparedVerificationProbe Prepare(const VerificationProtocol& p,std::size_t index,const std::string& revision,std::size_t epoch)
{
    PreparedVerificationProbe result{p.routing,p.inputs.at(index).id,p.revision,revision,
        revision+"/route/"+std::to_string(index),epoch,{}};
    if(p.routing==ProbeRouting::BranchSoloBurst)result.selectedInputIndex=index;
    return result;
}
ProbeObservation Observe(const VerificationProtocol& p,const PreparedVerificationProbe& prepared,
    std::size_t index,const std::string& run,const std::string& trial,
    const std::vector<double>& delay,const std::vector<double>& raw)
{
    const bool branch=p.routing==ProbeRouting::BranchSoloBurst;const auto n=p.inputs.size();
    const double onset=.05+.1*index,arrival=onset+delay.at(index);
    ProbeSpec s;s.schemaVersion=3;s.runId=run;s.trialId=trial;s.sampleId=p.sampleId;
    s.patternHash=p.patternHash;s.modelRevision=prepared.effectiveModelRevision;
    s.begin=0.;s.end=1.;s.maximumSampleGap=p.maximumSampleGap;s.maximumSamples=201;
    s.baseline.assign(branch?1:n,-.065);s.expectedStimulusIds=p.stimulusIds;
    s.stimulusProfile=p.stimulusProfile;s.waveAssignment=p.waveAssignment;
    s.windows={{p.inputs[index].id,branch?0u:index,arrival-.015,arrival+.015,p.stimulusIds[index]}};
    ProbeRecorder recorder(s);
    for(int tick=0;tick<=200;++tick)
    {
        const double time=.005*tick;std::vector<double> values(branch?1:n,-.065);
        for(std::size_t channel=0;channel<values.size();++channel)
        {
            const auto input=branch?index:channel;
            for(std::size_t pulse=0;pulse<n;++pulse)
            {
                const int center=int(std::llround((.05+.1*pulse+delay.at(input))/.005));
                values[channel]+=(raw.at(input)+.065)*std::max(0.,1.-std::abs(tick-center)/2.);
            }
        }
        recorder.Observe(time,values,prepared.effectiveModelRevision);
    }
    for(std::size_t pulse=0;pulse<n;++pulse)recorder.RecordStimulus(p.stimulusIds[pulse],.05+.1*pulse);
    return recorder.Close(1.,prepared.effectiveModelRevision,"window_closed");
}
std::vector<double> Raw(std::size_t n){std::vector<double> result;for(std::size_t i=0;i<n;++i)result.push_back(-.055+.001*i);return result;}
CapturedReferences References(const VerificationProtocol& p)
{
    std::vector<ReferenceEvidence> evidence;
    for(std::size_t i=0;i<p.inputs.size();++i)
    {
        const auto prepared=Prepare(p,i,"initial",0);
        evidence.push_back({prepared,Observe(p,prepared,i,"capture","reference"+std::to_string(i),
            std::vector<double>(p.inputs.size(),.03),Raw(p.inputs.size()))});
    }
    return CapturedReferences::Capture(p,evidence);
}
BoundedTrainingConfig Configuration(std::size_t n=2,Normalization normalization=Normalization::SynapseCount)
{
    BoundedTrainingConfig cfg;cfg.runId="training";cfg.initialModelRevision="initial";
    cfg.maximumProbes=1000;cfg.maximumEdits=1000;cfg.maximumCandidatesPerInput=128;cfg.maximumSweeps=1;
    cfg.normalization=normalization;cfg.tolerances.sync=.005;cfg.resistanceSubdivisionDepth=2;
    cfg.bounds.assign(n,{1,3,1,128,1.,100.});return cfg;
}
using Response=std::function<void(const TrainingAction&,std::vector<double>&,std::vector<double>&)>;
using DomainProvider=std::function<ResistanceDomainAssessment(const TrainingAction&)>;
void DriveTraining(BoundedTrainingSession& session,const VerificationProtocol& protocol,const Response& response={},const DomainProvider& domain={})
{
    std::size_t iterations=0;
    while(auto action=session.NextAction())
    {
        ASSERT_LT(++iterations,4000u);
        const auto stable=session.NextAction();ASSERT_TRUE(stable);EXPECT_EQ(stable->serial,action->serial);
        if(action->kind==TrainingActionKind::Edit)
        {
            session.Applied(action->serial,action->parameters,"model"+std::to_string(action->serial),action->capacitance);continue;
        }
        if(action->kind==TrainingActionKind::ResistanceDomain)
        {
            ASSERT_TRUE(bool(domain));session.AssessedDomain(action->serial,domain(*action),action->baseModelRevision);continue;
        }
        const auto prepared=Prepare(protocol,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);EXPECT_FALSE(session.NextAction());
        std::vector<double> delay(protocol.inputs.size(),.03),raw=Raw(protocol.inputs.size());
        if(response)response(*action,delay,raw);
        auto observation=Observe(protocol,prepared,action->inputIndex,action->runId,action->trialId,delay,raw);
        ASSERT_TRUE(observation.valid) << (observation.reasons.empty()?"":observation.reasons.front());
        session.Consume(observation,action->baseModelRevision);
    }
}


TrainingCapacitance ContextC0()
{return {std::string(64,'a'),.3,{{"Dendrite1_1",1.},{"Dendrite1_2",1.},{"Dendrite2_1",1.},{"Dendrite1_99",.8}}};}
BoundedTrainingConfig ContextConfig(Normalization normalization=Normalization::SynapseCount)
{
    auto cfg=Configuration(2,normalization);cfg.maximumCandidatesPerInput=6;
    cfg.bounds={{2,2,1,normalization==Normalization::SynapseCount?128:1,10.,10.},{1,1,1,1,10.,10.}};
    cfg.capacitanceSearch=CapacitanceSearchPolicy{.8,1.2,0,4,8};return cfg;
}
double SelectedScale(const std::optional<TrainingCapacitance>& value)
{return value->membraneScales.at("Dendrite1_2");}

TEST(CapacitanceContexts, MissingOrIncompatibleOwnedC0IsRejected)
{
    const auto protocol=Protocol();auto cfg=ContextConfig();
    EXPECT_THROW(BoundedTrainingSession(References(protocol),cfg,{{2,1,10.},{1,1,10.}}),std::invalid_argument);
    auto state=ContextC0();state.maximumRelativeChange=.1;state.membraneScales.erase("Dendrite1_99");
    EXPECT_THROW(BoundedTrainingSession(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,state),std::invalid_argument);
}
TEST(CapacitanceContexts, ContextAndRegionBudgetsArePreflightConstraints)
{
    const auto protocol=Protocol();const std::vector<InputParameters> initial{{2,1,10.},{1,1,10.}};
    for(const auto policy:{CapacitanceSearchPolicy{.8,1.2,0,1,8},CapacitanceSearchPolicy{.8,1.2,0,7,8},
            CapacitanceSearchPolicy{.8,1.2,0,4,1},CapacitanceSearchPolicy{0.,1.2,0,4,8},
            CapacitanceSearchPolicy{.8,1.2,21,4,8}})
    {auto cfg=ContextConfig();cfg.capacitanceSearch=policy;EXPECT_THROW(ValidateBoundedTrainingInputs(protocol,cfg,initial),std::invalid_argument);}
}
TEST(CapacitanceContexts, N0VisitsDifferentScalesBeforeExhaustingTheSynapseMesh)
{
    const auto protocol=Protocol();const auto cfg=ContextConfig();
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    DriveTraining(session,protocol);
    ASSERT_GE(session.Evidence().size(),4u);bool lower=false,upper=false;
    for(std::size_t i=0;i<4;++i){const auto scale=SelectedScale(session.Evidence()[i].capacitance);lower|=scale==.8;upper|=scale==1.2;}
    EXPECT_TRUE(lower);EXPECT_TRUE(upper);ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
}
TEST(CapacitanceContexts, CompleteJointStateRetainsDormantAndAnchorParameters)
{
    const auto protocol=Protocol();auto cfg=ContextConfig();
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    DriveTraining(session,protocol,[&](const auto& action,auto&,auto&) {
        ASSERT_TRUE(action.capacitance);EXPECT_EQ(action.capacitance->origin,ContextC0().origin);
        EXPECT_EQ(action.capacitance->membraneScales.at("Dendrite1_99"),.8);
        EXPECT_EQ(action.capacitance->membraneScales.at("Dendrite2_1"),1.);
        EXPECT_EQ(action.parameters[1],(InputParameters{1,1,10.}));
    });
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
}
TEST(CapacitanceContexts, N1RequestsDomainsForEachChangedCapacitance)
{
    const auto protocol=Protocol();auto cfg=ContextConfig(Normalization::TipResistance);
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},true,ContextC0());
    bool lower=false,upper=false;
    DriveTraining(session,protocol,{},[&](const auto& action) {
        const auto scale=SelectedScale(action.capacitance);lower|=scale==.8;upper|=scale==1.2;
        ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;d.baseModelRevision=action.baseModelRevision;
        d.previewModelRevision="scope/"+std::to_string(scale);d.geometry=action.parameters;d.inputIndex=action.inputIndex;
        d.minimumResistance=5.;d.maximumResistance=20.;d.sourceAmplitude=1.;d.capacitance=action.capacitance;return d;
    });
    EXPECT_TRUE(lower);EXPECT_TRUE(upper);EXPECT_NE(session.Status(),TrainingStatus::Exact);
}
TEST(CapacitanceContexts, N1CannotUseADomainForAnotherCapacitanceState)
{
    const auto protocol=Protocol();auto cfg=ContextConfig(Normalization::TipResistance);
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},true,ContextC0());
    DriveTraining(session,protocol,{},[&](const auto& action) {
        ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;d.baseModelRevision=action.baseModelRevision;
        d.previewModelRevision="scope";d.geometry=action.parameters;d.inputIndex=action.inputIndex;
        d.minimumResistance=5.;d.maximumResistance=20.;d.sourceAmplitude=1.;return d; // Deliberately loses C0 state.
    });
    EXPECT_EQ(session.Status(),TrainingStatus::InvalidModel);EXPECT_FALSE(session.Certificate());
}
TEST(CapacitanceContexts, RequiredN0RepeatsFinishBeforeTheNextCContext)
{
    const auto protocol=Protocol();auto cfg=ContextConfig();cfg.n0CandidateRepeats=2;
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    DriveTraining(session,protocol);ASSERT_GE(session.CandidateRepeats().size(),4u);
    for(const auto& group:session.CandidateRepeats())
    {EXPECT_TRUE(group.complete);EXPECT_EQ(group.trialIds.size(),2u);EXPECT_EQ(group.anchorTrialIds.size(),2u);ASSERT_TRUE(group.capacitance);}
}
TEST(CapacitanceContexts, ATrimCandidateNeedsFreshAllInputVerificationForExact)
{
    const auto protocol=Protocol();auto cfg=ContextConfig();
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    DriveTraining(session,protocol,[&](const auto& action,auto& delays,auto&) {
        delays[0]=.13+(SelectedScale(action.capacitance)-1.2)*.1;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    EXPECT_EQ(SelectedScale(session.Capacitance()),1.2);
    EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
}
TEST(CapacitanceContexts, BranchCEditCannotHideDamageToTheFixedReferenceInput)
{
    const auto protocol=Protocol(2,ProbeRouting::BranchSoloBurst);auto cfg=ContextConfig();
    BoundedTrainingSession session(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    DriveTraining(session,protocol,[&](const auto& action,auto& delays,auto& raw) {
        const auto scale=SelectedScale(action.capacitance);delays[0]=.13+(scale-1.2)*.1;
        if(scale!=1.)raw[1]+=.002;
    });
    EXPECT_NE(session.Status(),TrainingStatus::Exact);
    ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
    EXPECT_EQ(session.Capacitance()->membraneScales.at("Dendrite1_1"),1.);
}
TEST(CapacitanceContexts, ProbeBudgetAndExternalStopCannotManufactureExact)
{
    const auto protocol=Protocol();auto cfg=ContextConfig();cfg.maximumProbes=1;
    BoundedTrainingSession limited(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    DriveTraining(limited,protocol);EXPECT_EQ(limited.Status(),TrainingStatus::BudgetExhausted);EXPECT_FALSE(limited.Certificate());
    cfg=ContextConfig();BoundedTrainingSession stopped(References(protocol),cfg,{{2,1,10.},{1,1,10.}},false,ContextC0());
    stopped.ExternalStop();EXPECT_EQ(stopped.Status(),TrainingStatus::ExternalStop);EXPECT_FALSE(stopped.NextAction());EXPECT_FALSE(stopped.Certificate());
}
}
