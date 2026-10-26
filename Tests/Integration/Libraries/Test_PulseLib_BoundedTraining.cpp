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
        revision+"/route/"+std::to_string(index),epoch};
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
void DriveTraining(BoundedTrainingSession& session,const VerificationProtocol& protocol,const Response& response={})
{
    std::size_t iterations=0;
    while(auto action=session.NextAction())
    {
        ASSERT_LT(++iterations,4000u);
        const auto stable=session.NextAction();ASSERT_TRUE(stable);EXPECT_EQ(stable->serial,action->serial);
        if(action->kind==TrainingActionKind::Edit)
        {
            session.Applied(action->serial,action->parameters,"model"+std::to_string(action->serial));continue;
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

TEST(BoundedTraining, MeasuredNonmonotoneLengthsAndFixedAnchorRequireFreshAllInputGate)
{
    for(auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();
        BoundedTrainingSession session(References(p),cfg,std::vector<InputParameters>(2,{1,1,10.}));
        DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto&) {
            // Deliberately nonmonotone: length 2 is worse than length 1;
            // length 3 synchronizes. Prediction/bisection cannot certify this.
            delay[0]=a.parameters[0].length==3?.13:a.parameters[0].length==2?.01:.03;
        });
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
        EXPECT_TRUE(session.Certificate()->Exact());EXPECT_EQ(session.Parameters()[0].length,3);
        EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
        ASSERT_GE(session.Evidence().size(),3u);EXPECT_LT(session.Evidence()[0].timingResidualHigh,0.);
        EXPECT_TRUE(session.Certificate()->Matches(session.ModelRevision(),References(p),cfg.tolerances,
            ModelStateKind::LearnedSolo,session.ModelEpoch()));
        EXPECT_EQ(session.Certificate()->Residuals().size(),2u);
    }
}

TEST(BoundedTraining, IndependentResistanceBoundsAndNoCommonIntersection)
{
    const auto p=Protocol(3,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(3,Normalization::TipResistance);
    cfg.bounds={{3,3,1,1,1.,2.},{2,2,1,1,10.,20.},{1,1,1,1,100.,200.}};
    cfg.tolerances.sync=1.;
    BoundedTrainingSession session(References(p),cfg,{{3,1,1.5},{2,1,15.},{1,1,150.}});
    DriveTraining(session,p,[](const TrainingAction& a,auto&,auto& raw) {
        raw[0]+=(a.parameters[0].resistance==2.?0.:.001);
        raw[1]+=(a.parameters[1].resistance==20.?0.:.001);
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);EXPECT_EQ(session.Parameters()[0].resistance,2.);
    EXPECT_EQ(session.Parameters()[1].resistance,20.);EXPECT_EQ(session.Parameters()[2].resistance,150.);
    ASSERT_FALSE(session.Evidence().empty());EXPECT_EQ(session.Evidence().front().inputIndex,1u);
}

TEST(BoundedTraining, Ns128IsJudgedByActualResidualAndQuantizationNeverBecomesExact)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.bounds[0]={1,1,127,128,1.,100.};cfg.tolerances.sync=1.;
    for(bool exactAtCap:{false,true})
    {
        BoundedTrainingSession session(References(p),cfg,{{1,127,10.},{1,1,10.}});
        DriveTraining(session,p,[&](const TrainingAction& a,auto&,auto& raw) {
            raw[0]+=exactAtCap && a.parameters[0].synapses==128?0.:.0001;
        });
        EXPECT_EQ(session.Status(),exactAtCap?TrainingStatus::Exact:TrainingStatus::SearchUnresolved);
        ASSERT_TRUE(session.Certificate());EXPECT_EQ(session.Certificate()->Exact(),exactAtCap);
        if(exactAtCap)EXPECT_EQ(session.Parameters()[0].synapses,128);
    }
}

TEST(BoundedTraining, LaterSharedPhysicsDamageCannotInheritLocalSuccess)
{
    const auto p=Protocol(3,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(3);
    cfg.tolerances.sync=1.;cfg.maximumCandidatesPerInput=2;
    BoundedTrainingSession session(References(p),cfg,std::vector<InputParameters>(3,{1,1,10.}));
    DriveTraining(session,p,[](const TrainingAction& a,auto&,auto& raw) {
        // Each local probe succeeds; the independent final sweep exposes damage
        // to an earlier committed input. No local flag can bypass that sweep.
        if(a.finalVerification)raw[1]+=.001;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::SearchUnresolved);ASSERT_TRUE(session.Certificate());
    EXPECT_FALSE(session.Certificate()->Exact());EXPECT_FALSE(session.Certificate()->Residuals()[1].withinAmplitude);
}

TEST(BoundedTraining, SearchBudgetAndExternalStopNeverCreateCertificate)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.maximumProbes=1;
    BoundedTrainingSession budget(References(p),cfg,{{1,1,10.},{1,1,10.}});DriveTraining(budget,p);
    EXPECT_EQ(budget.Status(),TrainingStatus::BudgetExhausted);EXPECT_FALSE(budget.Certificate());
    cfg.maximumProbes=100;
    BoundedTrainingSession stopped(References(p),cfg,{{1,1,10.},{1,1,10.}});
    ASSERT_TRUE(stopped.NextAction());stopped.ExternalStop();
    EXPECT_EQ(stopped.Status(),TrainingStatus::ExternalStop);EXPECT_FALSE(stopped.NextAction());EXPECT_FALSE(stopped.Certificate());
    BoundedTrainingSession deadline(References(p),cfg,{{1,1,10.},{1,1,10.}});
    ASSERT_TRUE(deadline.NextAction());deadline.ExhaustBudget();
    EXPECT_EQ(deadline.Status(),TrainingStatus::BudgetExhausted);EXPECT_FALSE(deadline.NextAction());EXPECT_FALSE(deadline.Certificate());
}

TEST(BoundedTraining, CoincidentBranchInputsCannotHideChangesToTheFixedAnchor)
{
    const auto p=Protocol(2,ProbeRouting::BranchSoloBurst);auto cfg=Configuration();cfg.tolerances.sync=1.;
    cfg.bounds.assign(2,{1,3,1,2,1.,100.});
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const TrainingAction& action,auto&,auto& raw) {
        if(action.parameters[0].length==action.parameters[1].length)
        {
            EXPECT_EQ(action.parameters[0].synapses,action.parameters[1].synapses);
            EXPECT_EQ(action.parameters[0].resistance,action.parameters[1].resistance);
        }
        raw[0]+=action.parameters[0].synapses==2?0.:.0001;
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);EXPECT_GT(session.Parameters()[0].length,1);
    EXPECT_EQ(session.Parameters()[0].synapses,2);EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
    cfg.bounds[0].maximumLength=1;
    BoundedTrainingSession tied(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(tied,p,[](const auto&,auto&,auto& raw){raw[0]+=.0001;});
    EXPECT_EQ(tied.Status(),TrainingStatus::SearchUnresolved);EXPECT_EQ(tied.AppliedEdits(),0u);
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,2,10.},{1,1,10.}})),std::invalid_argument);
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,1,11.},{1,1,10.}})),std::invalid_argument);
}

TEST(BoundedTraining, AppliedReadbackAndProbeRevisionAreMandatory)
{
    const auto p=Protocol();auto cfg=Configuration();BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,p); // Constant delays cannot synchronize these two inputs.
    EXPECT_EQ(session.Status(),TrainingStatus::SearchUnresolved);
    BoundedTrainingSession bad(References(p),cfg,{{1,1,10.},{1,1,10.}});
    auto action=bad.NextAction();ASSERT_TRUE(action);const auto prepared=Prepare(p,action->inputIndex,"initial",0);
    bad.Arm(action->serial,prepared);
    bad.Consume(Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.03,.03},Raw(2)),"external_edit");
    EXPECT_EQ(bad.Status(),TrainingStatus::InvalidModel);EXPECT_FALSE(bad.Certificate());
    BoundedTrainingSession readback(References(p),cfg,{{1,1,10.},{1,1,10.}});
    for(unsigned step=0;step<2;++step)
    {
        const auto a=readback.NextAction();ASSERT_TRUE(a);ASSERT_EQ(a->kind,TrainingActionKind::Probe);
        const auto context=Prepare(p,a->inputIndex,a->baseModelRevision,a->modelEpoch);readback.Arm(a->serial,context);
        readback.Consume(Observe(p,context,a->inputIndex,a->runId,a->trialId,{.03,.03},Raw(2)),a->baseModelRevision);
    }
    const auto edit=readback.NextAction();ASSERT_TRUE(edit);ASSERT_EQ(edit->kind,TrainingActionKind::Edit);
    auto wrong=edit->parameters;wrong[1].resistance=11.;
    readback.Applied(edit->serial,wrong,"changed_graph");EXPECT_EQ(readback.Status(),TrainingStatus::InvalidModel);
    EXPECT_FALSE(readback.Certificate());EXPECT_EQ(readback.AppliedEdits(),0u);
}

TEST(BoundedTraining, SingleInputStillRequiresRealFinalProbe)
{
    const auto p=Protocol(1);auto cfg=Configuration(1);
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.}});EXPECT_FALSE(session.Certificate());
    EXPECT_EQ(session.Status(),TrainingStatus::Verifying);DriveTraining(session,p);
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);EXPECT_EQ(session.IssuedProbes(),1u);
}

TEST(BoundedTraining, MissingAmbiguousOrIncompletePeaksCannotDriveEdits)
{
    const auto p=Protocol();auto cfg=Configuration();
    for(int fault=0;fault<4;++fault)
    {
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
        const auto action=session.NextAction();ASSERT_TRUE(action);
        const auto prepared=Prepare(p,action->inputIndex,"initial",0);session.Arm(action->serial,prepared);
        auto observation=Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.03,.03},Raw(2));
        if(fault==0){observation.valid=false;observation.peaks[0].validity=PeakValidity::Missing;}
        if(fault==1){observation.peaks[0].validity=PeakValidity::Ambiguous;}
        if(fault==2)observation.complete=false;
        if(fault==3)observation.peaks[0].rawPotential=std::numeric_limits<double>::quiet_NaN();
        session.Consume(observation,"initial");EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);
        EXPECT_EQ(session.AppliedEdits(),0u);EXPECT_TRUE(session.Evidence().empty());EXPECT_FALSE(session.Certificate());
    }
}
}
