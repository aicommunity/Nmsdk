#pragma once
#include <gtest/gtest.h>
#include "TimeLearner/BoundedTraining.h"
#include <algorithm>
#include <cmath>
#include <functional>
#include <string>
#include <vector>

// Shared controlled-observation fixture; no production implementation is copied.
namespace NmsdkBoundedTrainingTest {
using namespace NMSDK::TimeLearner;
inline VerificationProtocol Protocol(std::size_t n=2,ProbeRouting routing=ProbeRouting::ClassicBurst)
{
    VerificationProtocol p;p.schemaVersion=3;p.routing=routing;p.revision="bounded_burst_v1";
    p.sampleId="target";p.patternHash="actual_burst_hash";p.originStimulusId="p0";
    p.maximumSampleGap=.005;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    for(std::size_t i=0;i<n;++i){p.inputs.push_back({"i"+std::to_string(i),"p"+std::to_string(i)});p.stimulusIds.push_back("p"+std::to_string(i));}
    return p;
}
inline PreparedVerificationProbe Prepare(const VerificationProtocol& p,std::size_t index,const std::string& revision,std::size_t epoch)
{
    PreparedVerificationProbe result{p.routing,p.inputs.at(index).id,p.revision,revision,
        revision+"/route/"+std::to_string(index),epoch,{}};
    if(p.routing==ProbeRouting::BranchSoloBurst)result.selectedInputIndex=index;
    return result;
}
inline ProbeObservation Observe(const VerificationProtocol& p,const PreparedVerificationProbe& prepared,
    std::size_t index,const std::string& run,const std::string& trial,
    const std::vector<double>& delay,const std::vector<double>& raw,bool extraWave=false)
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
            if(extraWave && input==index)
                values[channel]+=.00002*std::max(0.,1.-std::abs(tick-150)/2.);
        }
        recorder.Observe(time,values,prepared.effectiveModelRevision);
    }
    for(std::size_t pulse=0;pulse<n;++pulse)recorder.RecordStimulus(p.stimulusIds[pulse],.05+.1*pulse);
    return recorder.Close(1.,prepared.effectiveModelRevision,"window_closed");
}
inline std::vector<double> Raw(std::size_t n){std::vector<double> result;for(std::size_t i=0;i<n;++i)result.push_back(-.055+.001*i);return result;}
inline CapturedReferences References(const VerificationProtocol& p)
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
inline BoundedTrainingConfig Configuration(std::size_t n=2,Normalization normalization=Normalization::SynapseCount)
{
    BoundedTrainingConfig cfg;cfg.runId="training";cfg.initialModelRevision="initial";
    cfg.maximumProbes=1000;cfg.maximumEdits=1000;cfg.maximumCandidatesPerInput=128;cfg.maximumSweeps=1;
    cfg.normalization=normalization;cfg.tolerances.sync=.005;cfg.resistanceSubdivisionDepth=2;
    cfg.bounds.assign(n,{1,3,1,128,1.,100.});return cfg;
}
using Response=std::function<void(const TrainingAction&,std::vector<double>&,std::vector<double>&)>;
using DomainProvider=std::function<ResistanceDomainAssessment(const TrainingAction&)>;
inline void DriveTraining(BoundedTrainingSession& session,const VerificationProtocol& protocol,const Response& response={},const DomainProvider& domain={})
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

}
