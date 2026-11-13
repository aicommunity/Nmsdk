#include <gtest/gtest.h>
#include "TimeLearner/BoundedTraining.h"
#include "TimeLearner/CandidateRecoveryEvidenceJson.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <algorithm>
#include <cmath>
#include <limits>
#include <functional>
#include <map>
#include <set>


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

TEST(BoundedTrainingN1GeometryFairness, ValidDenseResistanceMeshDoesNotStarveOtherLengthsInEitherRecoveryMode)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        std::vector<std::vector<InputParameters>> retryCandidates;
        for(const auto recovery:{InvalidMeasurementRecovery::RetrySameCandidate,
                                 InvalidMeasurementRecovery::AdvanceUnassignedBurst})
        {
            SCOPED_TRACE(::testing::Message()<<int(routing)<<'/'<<int(recovery));
            const auto protocol=Protocol(2,routing);
            auto cfg=Configuration(2,Normalization::TipResistance);
            cfg.invalidMeasurementRecovery=recovery;cfg.maximumInvalidObservations=1;
            cfg.resistanceSubdivisionDepth=8;cfg.maximumProbes=12;
            cfg.bounds={{1,4,1,1,1.,100.},{1,1,1,1,10.,10.}};
            BoundedTrainingSession session(References(protocol),cfg,{{1,1,10.},{1,1,10.}},true);
            DriveTraining(session,protocol,[&](const TrainingAction&,auto&,auto& raw) {
                // Deliberately valid but unsynchronized/un-normalized measured
                // responses. This tests controller scheduling, not cable physics.
                raw[0]+=.002;
            },[&](const TrainingAction& action) {
                ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;
                d.baseModelRevision=action.baseModelRevision;d.geometry=action.parameters;
                d.inputIndex=action.inputIndex;d.sourceAmplitude=1.;
                d.previewModelRevision="geometry-"+std::to_string(action.parameters[0].length);
                const bool locked=routing==ProbeRouting::BranchSoloBurst &&
                    action.parameters[0].length==action.parameters[1].length;
                d.minimumResistance=locked?10.:1.;d.maximumResistance=locked?10.:100.;return d;
            });
            std::set<int> lengths;std::vector<std::vector<InputParameters>> candidates;
            for(const auto& measured:session.Evidence())
            {
                ASSERT_EQ(measured.inputIndex,0u);
                lengths.insert(measured.parameters.length);candidates.push_back(measured.fullParameters);
            }
            EXPECT_TRUE(lengths.contains(3));EXPECT_TRUE(lengths.contains(4));
            EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
            EXPECT_TRUE(session.Recoveries().empty());
            EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
            if(recovery==InvalidMeasurementRecovery::RetrySameCandidate)retryCandidates=candidates;
            else EXPECT_EQ(candidates,retryCandidates);
            // Each finite observation remains evidence for a nonexact result.
            EXPECT_FALSE(session.Status()==TrainingStatus::Exact);
        }
    }
}

void CheckFiniteCandidateRanking(ProbeRouting routing,Normalization normalization,bool overflow)
{
    // Production session and recorder; only the measured physical response is
    // controlled here. All three legal geometries are actually consumed.
    for(const int axes:(overflow?std::vector<int>{1,2}:std::vector<int>{1,2,3}))
    {
        SCOPED_TRACE(axes);
        const auto protocol=Protocol(2,routing);auto config=Configuration(2,normalization);
        config.maximumCandidatesPerInput=3;
        config.bounds={{2,4,1,1,10.,10.},{1,1,1,1,10.,10.}};
        const double tolerance=overflow?std::numeric_limits<double>::denorm_min():0.;
        config.tolerances.sync=(axes&1)?tolerance:1.;
        config.tolerances.amplitudeAbsolute=(axes&2)?tolerance:1e-5;
        config.tolerances.amplitudeRelative=0.;
        BoundedTrainingSession session(References(protocol),config,{{2,1,10.},{1,1,10.}});
        DriveTraining(session,protocol,[&](const TrainingAction& action,auto& delay,auto& raw) {
            const int length=action.parameters[0].length;
            const double residual=length==2?.006:(length==3?.002:.001);
            // The anchor input is excited 0.1 s after input0. Arrival is
            // relative to originStimulusId, not the input's own pulse.
            if(axes&1)delay[0]=.13+(length==2?.06:(length==3?.02:.01));
            if(axes&2)raw[0]+=residual;
        });
        EXPECT_EQ(session.Parameters()[0].length,4);
        EXPECT_EQ(session.Parameters()[0].synapses,1);
        EXPECT_EQ(session.Parameters()[0].resistance,10.);
        EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        EXPECT_EQ(session.Reason(),"maximum_sweeps_exhausted");
        ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
        std::set<int> measured;
        for(const auto& evidence:session.Evidence())
        {
            measured.insert(evidence.parameters.length);
            const int length=evidence.parameters.length;
            if(axes&1){EXPECT_NEAR(std::max(std::fabs(evidence.timingResidualLow),std::fabs(evidence.timingResidualHigh)),
                length==2?.06:(length==3?.02:.01),1e-12);}
            if(axes&2){EXPECT_NEAR(evidence.amplitudeResidual,length==2?.006:(length==3?.002:.001),1e-12);}
        }
        EXPECT_EQ(measured,(std::set<int>{2,3,4}));
    }
}

TEST(BoundedTrainingFiniteRanking,ClassicN0Zero){CheckFiniteCandidateRanking(ProbeRouting::ClassicBurst,Normalization::SynapseCount,false);}
TEST(BoundedTrainingFiniteRanking,ClassicN1Zero){CheckFiniteCandidateRanking(ProbeRouting::ClassicBurst,Normalization::TipResistance,false);}
TEST(BoundedTrainingFiniteRanking,BranchN0Zero){CheckFiniteCandidateRanking(ProbeRouting::BranchSoloBurst,Normalization::SynapseCount,false);}
TEST(BoundedTrainingFiniteRanking,BranchN1Zero){CheckFiniteCandidateRanking(ProbeRouting::BranchSoloBurst,Normalization::TipResistance,false);}
TEST(BoundedTrainingFiniteRanking,ClassicN0Overflow){CheckFiniteCandidateRanking(ProbeRouting::ClassicBurst,Normalization::SynapseCount,true);}
TEST(BoundedTrainingFiniteRanking,ClassicN1Overflow){CheckFiniteCandidateRanking(ProbeRouting::ClassicBurst,Normalization::TipResistance,true);}
TEST(BoundedTrainingFiniteRanking,BranchN0Overflow){CheckFiniteCandidateRanking(ProbeRouting::BranchSoloBurst,Normalization::SynapseCount,true);}
TEST(BoundedTrainingFiniteRanking,BranchN1Overflow){CheckFiniteCandidateRanking(ProbeRouting::BranchSoloBurst,Normalization::TipResistance,true);}

TEST(UnassignedBurstCandidate,OnlyClosedMissingOrExtraBurstWavesCanAuthorizeAdvancing)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const std::size_t n:{1u,2u,4u,6u})
    {
        SCOPED_TRACE(n);const auto p=Protocol(n,routing);const auto prepared=Prepare(p,0,"initial",0);
        const std::vector<double> delay(n,.03);auto raw=Raw(n);
        const auto valid=Observe(p,prepared,0,"run","valid",delay,raw);
        ASSERT_TRUE(valid.valid);EXPECT_FALSE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,valid));
        raw[0]=-.065;
        const auto missing=Observe(p,prepared,0,"run","missing",delay,raw);
        ASSERT_TRUE(missing.complete);ASSERT_FALSE(missing.valid);
        EXPECT_TRUE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,missing));
        raw=Raw(n);
        const auto extra=Observe(p,prepared,0,"run","extra",delay,raw,true);
        ASSERT_TRUE(extra.complete);ASSERT_FALSE(extra.valid);
        EXPECT_TRUE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,extra));
    }
}

TEST(UnassignedBurstCandidate,CorruptionAndOtherFailureCausesCannotAuthorizeAdvancing)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);const auto prepared=Prepare(p,0,"initial",0);
        const auto missing=Observe(p,prepared,0,"run","missing",{.03,.03},{-.065,-.054});
        ASSERT_TRUE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,missing));
        const std::vector<std::function<void(ProbeObservation&)>> corruptions{
            [](auto& o){o.complete=false;},
            [](auto& o){o.specification.patternHash="different_pattern";},
            [](auto& o){o.specification.modelRevision="different_physics";},
            [](auto& o){o.specification.stimulusProfile->frequencyHz=20000.;},
            [](auto& o){o.endReason="external_stop";},
            [](auto& o){o.sampleCount=2;},
            [](auto& o){o.reasons.push_back("nonfinite_sample");},
            [](auto& o){o.reasons.push_back("sample_gap");},
            [](auto& o){o.stimuli[1].id=o.stimuli[0].id;},
            [](auto& o){o.stimuli[1].time=o.stimuli[0].time;},
            [](auto& o){o.peaks[0].amplitude=0.;},
            [](auto& o){o.peaks[0].validity=PeakValidity::Clipped;},
            [](auto& o){o.burstAssignments[0].channel=100;},
            [](auto& o){o.spikes.push_back({0,.5});},
            [](auto& o){o.reasons.push_back(o.reasons.front());}
        };
        for(std::size_t i=0;i<corruptions.size();++i)
        {
            SCOPED_TRACE(i);auto altered=missing;corruptions[i](altered);
            EXPECT_FALSE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,altered));
        }
        auto extra=Observe(p,prepared,0,"run","extra",{.03,.03},Raw(2),true);
        ASSERT_TRUE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,extra));
        extra.burstAssignments[0].waves[0].amplitude=std::numeric_limits<double>::quiet_NaN();
        EXPECT_FALSE(CanAdvanceUnassignedBurstCandidate(p,0,prepared,extra));
    }
}

void RecoveryCase(ProbeRouting routing,Normalization normalization,bool failAnchor,bool extra,
                  InvalidMeasurementRecovery policy,bool alwaysInvalid=false,std::size_t allowance=1,
                  std::size_t candidateLimit=3)
{
    const auto p=Protocol(2,routing);auto cfg=Configuration(2,normalization);
    cfg.invalidMeasurementRecovery=policy;cfg.maximumInvalidObservations=allowance;
    cfg.maximumCandidatesPerInput=candidateLimit;cfg.bounds={{1,3,1,1,10.,10.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    unsigned steps=0,rejections=0;
    while(const auto action=session.NextAction())
    {
        ASSERT_LT(++steps,40u);
        if(action->kind==TrainingActionKind::Edit)
        {session.Applied(action->serial,action->parameters,"changed"+std::to_string(action->serial));continue;}
        ASSERT_EQ(action->kind,TrainingActionKind::Probe);
        const auto prepared=Prepare(p,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);auto raw=Raw(2);
        const bool reject=!action->finalVerification && action->inputIndex==(failAnchor?1u:0u) &&
            (alwaysInvalid || rejections==0);
        if(reject){++rejections;if(!extra)raw[action->inputIndex]=-.065;}
        session.Consume(Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.13,.03},raw,
                               reject && extra),action->baseModelRevision);
        if(reject && policy==InvalidMeasurementRecovery::AdvanceUnassignedBurst)
        {
            ASSERT_EQ(session.Recoveries().size(),rejections);const auto& event=session.Recoveries().back();
            EXPECT_EQ(event.actionSerial,action->serial);EXPECT_EQ(event.inputIndex,action->inputIndex);
            EXPECT_EQ(event.candidateInputIndex,0u);EXPECT_EQ(event.sweep,0u);
            EXPECT_EQ(event.runId,action->runId);EXPECT_EQ(event.trialId,action->trialId);
            EXPECT_EQ(event.modelEpoch,action->modelEpoch);EXPECT_EQ(event.baseModelRevision,action->baseModelRevision);
            EXPECT_EQ(event.effectiveModelRevision,prepared.effectiveModelRevision);EXPECT_EQ(event.anchor,failAnchor);
            EXPECT_EQ(event.fullParameters,action->parameters);EXPECT_FALSE(event.capacitance);
            EXPECT_EQ(event.validity,extra?PeakValidity::Ambiguous:PeakValidity::Missing);
            EXPECT_EQ(event.invalidBefore,rejections-1);EXPECT_EQ(event.invalidAfter,rejections);
            EXPECT_EQ(event.statusAfter,session.Status());EXPECT_EQ(event.reasonAfter,session.Reason());
            EXPECT_EQ(event.disposition,rejections>allowance?CandidateRecoveryDisposition::InvalidBudgetStop:
                CandidateRecoveryDisposition::CursorAdvanced);
            const auto encoded=EncodeCandidateRecoveryEvidence(event);
            EXPECT_EQ(encoded["invalid_after"],QJsonValue(double(rejections)));
            EXPECT_EQ(encoded["trial_id"],QJsonValue(QString::fromStdString(action->trialId)));
            EXPECT_EQ(encoded["phase"],QJsonValue(failAnchor?"anchor":"input"));
            EXPECT_EQ(QJsonDocument::fromJson(QJsonDocument(encoded).toJson()).object(),encoded);
        }
        if(policy==InvalidMeasurementRecovery::RetrySameCandidate)EXPECT_TRUE(session.Recoveries().empty());
    }
    EXPECT_EQ(session.InvalidObservations(),rejections);
    if(alwaysInvalid)
    {
        EXPECT_FALSE(session.Certificate());EXPECT_TRUE(session.Evidence().empty());
        if(allowance<candidateLimit)
        {EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);EXPECT_EQ(rejections,allowance+1);}
        else
        {
            EXPECT_EQ(session.Status(),TrainingStatus::SearchUnresolved);
            EXPECT_EQ(session.Reason(),"no_measured_candidate_in_declared_search");EXPECT_EQ(rejections,candidateLimit);
        }
        return;
    }
    EXPECT_EQ(rejections,1u);ASSERT_EQ(session.Status(),TrainingStatus::Exact)<<session.Reason();
    ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    const bool advances=policy==InvalidMeasurementRecovery::AdvanceUnassignedBurst;
    EXPECT_EQ(session.Parameters()[0].length,advances?2:1);EXPECT_EQ(session.AppliedEdits(),advances?1u:0u);
    ASSERT_FALSE(session.Evidence().empty());
    for(const auto& evidence:session.Evidence())EXPECT_EQ(evidence.parameters.length,advances?2:1);
    EXPECT_EQ(session.Certificate()->Residuals().size(),2u);
}

TEST(BoundedCandidateRecovery,OptInAdvancesWhileDefaultRetriesTheSameCandidate)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const auto normalization:{Normalization::SynapseCount,Normalization::TipResistance})
    for(const bool anchor:{false,true})for(const bool extra:{false,true})
    for(const auto policy:{InvalidMeasurementRecovery::RetrySameCandidate,InvalidMeasurementRecovery::AdvanceUnassignedBurst})
    {
        SCOPED_TRACE(::testing::Message()<<int(routing)<<'/'<<int(normalization)<<'/'<<anchor<<'/'<<extra<<'/'<<int(policy));
        RecoveryCase(routing,normalization,anchor,extra,policy);
    }
}

TEST(BoundedCandidateRecovery,AdvancingDoesNotReplenishInvalidBudgetOrInventFeasibility)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const auto normalization:{Normalization::SynapseCount,Normalization::TipResistance})
    {
        RecoveryCase(routing,normalization,false,false,InvalidMeasurementRecovery::AdvanceUnassignedBurst,true,1,3);
        RecoveryCase(routing,normalization,true,true,InvalidMeasurementRecovery::AdvanceUnassignedBurst,true,5,2);
    }
}

TEST(BoundedCandidateRecovery,FinalVerificationNeverSkipsAnUnassignedInput)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const auto normalization:{Normalization::SynapseCount,Normalization::TipResistance})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration(2,normalization);
        cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
        cfg.maximumInvalidObservations=1;cfg.bounds.assign(2,{1,1,1,1,10.,10.});
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});unsigned steps=0,badFinals=0;
        while(const auto action=session.NextAction())
        {
            ASSERT_LT(++steps,20u);ASSERT_EQ(action->kind,TrainingActionKind::Probe);
            const auto prepared=Prepare(p,action->inputIndex,action->baseModelRevision,action->modelEpoch);
            session.Arm(action->serial,prepared);auto raw=Raw(2);
            if(action->finalVerification){raw[action->inputIndex]=-.065;++badFinals;}
            session.Consume(Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.13,.03},raw),action->baseModelRevision);
        }
        EXPECT_EQ(badFinals,2u);EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);
        EXPECT_FALSE(session.Certificate());EXPECT_EQ(session.AppliedEdits(),0u);
        EXPECT_TRUE(session.Recoveries().empty());EXPECT_EQ(session.InvalidObservations(),badFinals);
    }
}

TEST(BoundedCandidateRecovery,OtherObservationFailuresCannotAdvanceTheCandidateCursor)
{
    const std::vector<std::function<void(ProbeObservation&)>> corruptions{
        [](auto& o){o.specification.patternHash="wrong_pattern";},
        [](auto& o){o.complete=false;},
        [](auto& o){o.burstAssignments[0].waves[0].amplitude=std::numeric_limits<double>::quiet_NaN();},
        [](auto& o){o.valid=false;o.reasons={"sample_gap"};},
        [](auto& o){o.endReason="model_time_budget_exhausted";o.valid=false;}
    };
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(std::size_t i=0;i<corruptions.size();++i)
    {
        SCOPED_TRACE(i);const auto p=Protocol(2,routing);auto cfg=Configuration();
        cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;cfg.maximumInvalidObservations=1;
        cfg.bounds={{1,3,1,1,10.,10.},{1,1,1,1,10.,10.}};
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});unsigned steps=0,bad=0;
        while(const auto action=session.NextAction())
        {
            ASSERT_LT(++steps,10u);ASSERT_EQ(action->kind,TrainingActionKind::Probe);
            const auto prepared=Prepare(p,action->inputIndex,action->baseModelRevision,action->modelEpoch);
            session.Arm(action->serial,prepared);
            auto observation=Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.13,.03},Raw(2));
            if(action->inputIndex==0){corruptions[i](observation);++bad;}
            session.Consume(observation,action->baseModelRevision);
        }
        EXPECT_EQ(bad,2u);EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);
        EXPECT_EQ(session.AppliedEdits(),0u);EXPECT_EQ(session.Parameters()[0].length,1);EXPECT_FALSE(session.Certificate());
    }
}

TEST(BoundedCandidateRecovery,ZeroAllowanceAndUnknownPoliciesAreRejected)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,1,10.},{1,1,10.}})),std::invalid_argument);
    cfg.maximumInvalidObservations=1;cfg.invalidMeasurementRecovery=static_cast<InvalidMeasurementRecovery>(99);
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,1,10.},{1,1,10.}})),std::invalid_argument);
}

TEST(BoundedCandidateRecovery,RetiringPartialN0RepeatsRequiresFreshMeasurementsOfTheNextPoint)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.n0CandidateRepeats=2;
        cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
        cfg.maximumInvalidObservations=1;cfg.bounds={{1,2,1,1,10.,10.},{1,1,1,1,10.,10.}};
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});unsigned steps=0,firstPoint=0;
        while(const auto action=session.NextAction())
        {
            ASSERT_LT(++steps,30u);
            if(action->kind==TrainingActionKind::Edit)
            {session.Applied(action->serial,action->parameters,"changed"+std::to_string(action->serial));continue;}
            const auto prepared=Prepare(p,action->inputIndex,action->baseModelRevision,action->modelEpoch);
            session.Arm(action->serial,prepared);auto raw=Raw(2);
            if(!action->finalVerification && action->inputIndex==0 && action->parameters[0].length==1 && ++firstPoint==2)
                raw[0]=-.065;
            session.Consume(Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.13,.03},raw),action->baseModelRevision);
        }
        ASSERT_EQ(session.Status(),TrainingStatus::Exact)<<session.Reason();ASSERT_EQ(session.CandidateRepeats().size(),2u);
        const auto& incomplete=session.CandidateRepeats()[0];const auto& complete=session.CandidateRepeats()[1];
        EXPECT_FALSE(incomplete.complete);EXPECT_EQ(incomplete.trialIds.size(),1u);
        EXPECT_TRUE(complete.complete);EXPECT_EQ(complete.trialIds.size(),2u);
        EXPECT_EQ(incomplete.fullParameters[0].length,1);EXPECT_EQ(complete.fullParameters[0].length,2);
        EXPECT_NE(complete.trialIds[0],complete.trialIds[1]);EXPECT_NE(complete.anchorTrialIds[0],complete.anchorTrialIds[1]);
    }
}

TEST(BoundedCandidateRecovery,UnassignedRestoredBestCannotReuseItsOldMeasuredCertificate)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
    cfg.maximumInvalidObservations=2;cfg.maximumCandidatesPerInput=2;
    cfg.bounds={{1,2,1,1,10.,10.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});unsigned steps=0,firstPoint=0;
    while(const auto action=session.NextAction())
    {
        ASSERT_LT(++steps,30u);
        if(action->kind==TrainingActionKind::Edit)
        {session.Applied(action->serial,action->parameters,"changed"+std::to_string(action->serial));continue;}
        const auto prepared=Prepare(p,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);auto raw=Raw(2);
        if(action->inputIndex==0 && action->parameters[0].length==1 && ++firstPoint==2)raw[0]=-.065;
        const double delay=action->parameters[0].length==1?.03:.01;
        session.Consume(Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{delay,.03},raw),action->baseModelRevision);
    }
    EXPECT_EQ(firstPoint,2u);EXPECT_EQ(session.Status(),TrainingStatus::SearchUnresolved);
    EXPECT_EQ(session.Reason(),"restored_best_candidate_has_unassigned_burst");EXPECT_FALSE(session.Certificate());
    EXPECT_EQ(session.Evidence().size(),2u);EXPECT_EQ(session.Parameters()[0].length,1);
    ASSERT_EQ(session.Recoveries().size(),1u);const auto& event=session.Recoveries().front();
    EXPECT_EQ(event.disposition,CandidateRecoveryDisposition::RestoredBestStop);
    EXPECT_EQ(event.statusAfter,TrainingStatus::SearchUnresolved);
    EXPECT_EQ(event.reasonAfter,"restored_best_candidate_has_unassigned_burst");
    EXPECT_EQ(event.invalidBefore,0u);EXPECT_EQ(event.invalidAfter,1u);
}

TEST(BoundedTrainingN0Repeats, SecondObservationCanRejectAnApparentlyExactCandidate)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.n0CandidateRepeats=2;
        cfg.tolerances.sync=1.;cfg.bounds={{2,2,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}});
        std::size_t initialSamples=0;
        DriveTraining(session,p,[&](const TrainingAction& action,auto&,auto& raw) {
            if(!action.finalVerification && action.inputIndex==0 && action.parameters[0].synapses==1)
                if(++initialSamples==2)raw[0]+=.002;
        });
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
        EXPECT_EQ(session.Parameters()[0].synapses,2);
        ASSERT_EQ(session.CandidateRepeats().size(),2u);
        const auto& first=session.CandidateRepeats()[0];
        EXPECT_FALSE(first.withinAmplitude);EXPECT_EQ(first.trialIds.size(),2u);
        EXPECT_NE(first.trialIds[0],first.trialIds[1]);EXPECT_NE(first.anchorTrialIds[0],first.anchorTrialIds[1]);
        EXPECT_NEAR(first.maximumRawPotential-first.minimumRawPotential,.002,1e-12);
        EXPECT_EQ(first.fullParameters[0].synapses,1);
        EXPECT_EQ(session.CandidateRepeats()[1].fullParameters[0].synapses,2);
        EXPECT_TRUE(session.CandidateRepeats()[1].withinAmplitude);
    }
}

TEST(BoundedTrainingN0Repeats, BudgetDoesNotTurnOneSuccessfulMeasurementIntoRepeatedEvidence)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.n0CandidateRepeats=2;cfg.maximumProbes=2;
    cfg.tolerances.sync=1.;
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,p);
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    ASSERT_EQ(session.CandidateRepeats().size(),1u);EXPECT_FALSE(session.CandidateRepeats()[0].complete);
    EXPECT_EQ(session.CandidateRepeats()[0].trialIds.size(),1u);EXPECT_EQ(session.Evidence().size(),1u);
    EXPECT_FALSE(session.Certificate());
}

TEST(BoundedTrainingN0Repeats, Cap128CanPassWithTwoActualMeasurements)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.n0CandidateRepeats=2;cfg.tolerances.sync=1.;
    BoundedTrainingSession session(References(p),cfg,{{1,128,10.},{1,1,10.}});
    DriveTraining(session,p);
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_EQ(session.CandidateRepeats().size(),1u);
    EXPECT_EQ(session.CandidateRepeats()[0].fullParameters[0].synapses,128);
    EXPECT_EQ(session.CandidateRepeats()[0].trialIds.size(),2u);
}

TEST(BoundedTrainingN0Repeats, NoOpN1AndInvalidRepeatCountsAreRejected)
{
    const auto p=Protocol();auto cfg=Configuration();
    for(const std::size_t repeats:{std::size_t(0),std::size_t(129)})
    {cfg.n0CandidateRepeats=repeats;EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,1,10.},{1,1,10.}})),std::invalid_argument);}
    cfg=Configuration(2,Normalization::TipResistance);cfg.n0CandidateRepeats=2;
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,1,10.},{1,1,10.}})),std::invalid_argument);
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

TEST(BoundedTraining, IndependentEffectiveDomainsDoNotRequireACommonInterval)
{
    const auto p=Protocol(3,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(3,Normalization::TipResistance);
    cfg.bounds={{3,3,1,1,1.,2.},{2,2,1,1,10.,20.},{1,1,1,1,100.,200.}};cfg.tolerances.sync=1.;
    BoundedTrainingSession session(References(p),cfg,{{3,1,1.5},{2,1,15.},{1,1,150.}},true);
    // This is an explicit synthetic arithmetic adapter, not physical evidence.
    // Native storage/preview integration is covered by NativeResistanceDomains.
    DriveTraining(session,p,[](const auto& a,auto&,auto& raw) {
        raw[0]+=(a.parameters[0].resistance==2.?0.:.001);raw[1]+=(a.parameters[1].resistance==20.?0.:.001);
    },[](const auto& a) {
        ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;d.baseModelRevision=a.baseModelRevision;
        d.previewModelRevision="scope"+std::to_string(a.inputIndex);d.geometry=a.parameters;d.inputIndex=a.inputIndex;
        d.minimumResistance=a.inputIndex?18.:1.7;d.maximumResistance=a.inputIndex?20.:2.;return d;
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);EXPECT_EQ(session.Parameters()[0].resistance,2.);
    EXPECT_EQ(session.Parameters()[1].resistance,20.);EXPECT_EQ(session.Parameters().back().resistance,150.);
    EXPECT_FALSE(session.Domains().empty());
}

TEST(BoundedTraining, EffectiveDomainContextAndNumbersAreValidatedBeforeAnEdit)
{
    const auto p=Protocol();const auto cfg=Configuration(2,Normalization::TipResistance);
    for(int fault=0;fault!=4;++fault)
    {
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}},true);
        for(int probe=0;probe!=2;++probe)
        {
            const auto a=session.NextAction();ASSERT_TRUE(a);ASSERT_EQ(a->kind,TrainingActionKind::Probe);
            const auto prepared=Prepare(p,a->inputIndex,a->baseModelRevision,a->modelEpoch);session.Arm(a->serial,prepared);
            session.Consume(Observe(p,prepared,a->inputIndex,a->runId,a->trialId,{.03,.03},Raw(2)),a->baseModelRevision);
        }
        const auto a=session.NextAction();ASSERT_TRUE(a);ASSERT_EQ(a->kind,TrainingActionKind::ResistanceDomain);
        ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;d.baseModelRevision=a->baseModelRevision;
        d.previewModelRevision="scope";d.geometry=a->parameters;d.inputIndex=a->inputIndex;d.minimumResistance=2.;d.maximumResistance=90.;
        if(fault==0)d.baseModelRevision="stale";
        if(fault==1)++d.geometry[0].length;
        if(fault==2)d.minimumResistance=std::numeric_limits<double>::quiet_NaN();
        if(fault==3){d.status=ResistanceDomainStatus::Failed;d.modelMayHaveChanged=true;}
        session.AssessedDomain(a->serial,d,a->baseModelRevision);
        EXPECT_EQ(session.Status(),TrainingStatus::InvalidModel);EXPECT_EQ(session.AppliedEdits(),0u);EXPECT_FALSE(session.Certificate());
    }
}

TEST(BoundedTraining, EmptyEffectiveDomainsReachSweepBudgetWithFreshFinalMeasurements)
{
    const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);cfg.maximumCandidatesPerInput=2;
    for(auto& b:cfg.bounds)b.maximumLength=2;
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}},true);
    DriveTraining(session,p,{},[](const auto& a) {
        ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Unavailable;d.reason="synthetic_policy_no_interval";
        d.baseModelRevision=a.baseModelRevision;d.geometry=a.parameters;d.inputIndex=a.inputIndex;return d;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);ASSERT_TRUE(session.Certificate());
    EXPECT_FALSE(session.Certificate()->Exact());EXPECT_EQ(session.Certificate()->Residuals().size(),2u);
    EXPECT_EQ(session.AppliedEdits(),0u);EXPECT_FALSE(session.Domains().empty());
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
        EXPECT_EQ(session.Status(),exactAtCap?TrainingStatus::Exact:TrainingStatus::BudgetExhausted);
        ASSERT_TRUE(session.Certificate());EXPECT_EQ(session.Certificate()->Exact(),exactAtCap);
        if(exactAtCap){EXPECT_EQ(session.Parameters()[0].synapses,128);}
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
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);ASSERT_TRUE(session.Certificate());
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
    EXPECT_EQ(tied.Status(),TrainingStatus::BudgetExhausted);EXPECT_EQ(tied.AppliedEdits(),0u);
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,2,10.},{1,1,10.}})),std::invalid_argument);
    EXPECT_THROW((BoundedTrainingSession(References(p),cfg,{{1,1,11.},{1,1,10.}})),std::invalid_argument);
}

TEST(BoundedTraining, AppliedReadbackAndProbeRevisionAreMandatory)
{
    const auto p=Protocol();auto cfg=Configuration();BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,p); // Constant delays cannot synchronize these two inputs.
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
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

// Arithmetic decision controls only; real storage/Console verification must
// separately establish applicability to physical membrane dynamics.
TEST(BoundedTrainingN1Refinement, AMeasuredBracketCanReachBetweenMeshPointsButStillNeedsFreshFinalVerification)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const bool damageFinal:{false,true})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration(2,Normalization::TipResistance);
        cfg.bounds={{2,2,1,1,1.,16.},{1,1,1,1,10.,10.}};
        cfg.tolerances.sync=1.;cfg.resistanceSubdivisionDepth=1;cfg.maximumCandidatesPerInput=20;
        BoundedTrainingSession session(References(p),cfg,{{2,1,16.},{1,1,10.}},true);
        DriveTraining(session,p,[&](const auto& action,auto&,auto& raw) {
            raw[0]+=.001*std::log(action.parameters[0].resistance/6.);
            if(damageFinal && action.finalVerification)raw[0]+=.001;
        },[](const auto& action) {
            ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;d.baseModelRevision=action.baseModelRevision;
            d.previewModelRevision="one_unchanged_physical_scope";d.geometry=action.parameters;d.inputIndex=action.inputIndex;
            d.sourceAmplitude=1.;
            d.minimumResistance=1.;d.maximumResistance=16.;return d;
        });
        ASSERT_TRUE(session.Certificate());
        EXPECT_EQ(session.Status(),damageFinal?TrainingStatus::BudgetExhausted:TrainingStatus::Exact);
        EXPECT_EQ(session.Certificate()->Exact(),!damageFinal);
        EXPECT_NEAR(session.Parameters()[0].resistance,6.,.061);
        EXPECT_EQ(session.Parameters()[1].resistance,10.);
        EXPECT_TRUE(std::any_of(session.Evidence().begin(),session.Evidence().end(),[](const auto& e) {
            return e.parameters.resistance!=1. && e.parameters.resistance!=4. && e.parameters.resistance!=16.;
        }));
    }
}

TEST(BoundedTrainingN1Refinement, AChangedNormalizedPhysicalScopeOrSourceCannotReuseTheOldBracket)
{
    for(const bool changeSource:{false,true})
    {
    const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);
    cfg.bounds={{2,2,1,1,1.,16.},{1,1,1,1,10.,10.}};
    cfg.tolerances.sync=1.;cfg.resistanceSubdivisionDepth=1;cfg.maximumCandidatesPerInput=6;
    std::size_t measured=0;
    BoundedTrainingSession session(References(p),cfg,{{2,1,16.},{1,1,10.}},true);
    DriveTraining(session,p,[&](const auto& action,auto&,auto& raw) {
        raw[0]+=.001*std::log(action.parameters[0].resistance/6.);
        if(action.inputIndex==0 && !action.finalVerification)++measured;
    },[&](const auto& action) {
        ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;d.baseModelRevision=action.baseModelRevision;
        d.previewModelRevision=measured>=4 && !changeSource?"changed_scope":"original_scope";
        d.sourceAmplitude=measured>=4 && changeSource?2.:1.;
        d.geometry=action.parameters;d.inputIndex=action.inputIndex;d.minimumResistance=1.;d.maximumResistance=16.;return d;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
    for(const auto& e:session.Evidence())
        EXPECT_TRUE(e.parameters.resistance==1. || e.parameters.resistance==4. || e.parameters.resistance==16.);
    }
}

TEST(BoundedTraining, RejectedPreviewAdvancesOnlyWhenTheLiveModelStayedUnchanged)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.bounds[0].maximumSynapses=1;
    for(bool externalChange:{false,true})
    {
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
        for(unsigned i=0;i<2;++i)
        {
            const auto action=session.NextAction();ASSERT_TRUE(action);
            const auto prepared=Prepare(p,action->inputIndex,"initial",0);session.Arm(action->serial,prepared);
            session.Consume(Observe(p,prepared,action->inputIndex,action->runId,action->trialId,{.03,.03},Raw(2)),"initial");
        }
        const auto edit=session.NextAction();ASSERT_TRUE(edit);ASSERT_EQ(edit->kind,TrainingActionKind::Edit);
        ASSERT_EQ(edit->parameters[0].length,2);
        session.DeclineEdit(edit->serial,"unsafe_candidate",externalChange?"external_change":"initial");
        if(externalChange){EXPECT_EQ(session.Status(),TrainingStatus::InvalidModel);EXPECT_FALSE(session.Certificate());continue;}
        EXPECT_EQ(session.ModelEpoch(),0u);EXPECT_EQ(session.AppliedEdits(),0u);
        const auto next=session.NextAction();ASSERT_TRUE(next);ASSERT_EQ(next->kind,TrainingActionKind::Edit);
        EXPECT_EQ(next->parameters[0].length,3);session.Applied(next->serial,next->parameters,"accepted_length_3");
        DriveTraining(session,p,[](const auto& a,auto& delay,auto&){delay[0]=a.parameters[0].length==3?.13:.03;});
        EXPECT_EQ(session.Status(),TrainingStatus::Exact);EXPECT_EQ(session.AppliedEdits(),1u);
        ASSERT_EQ(session.Rejected().size(),1u);EXPECT_EQ(session.Rejected()[0].reason,"edit_rejected:unsafe_candidate");
    }
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

TEST(BoundedTraining, ColdBranchReverseOrderPropagatesOnlyUnvisitedAttachments)
{
    const auto p=Protocol(4,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(4);
    for(auto& b:cfg.bounds){b.maximumLength=4;b.maximumSynapses=1;}
    BoundedTrainingSession session(References(p),cfg,std::vector<InputParameters>(4,{1,1,10.}));
    DriveTraining(session,p,[](const TrainingAction& action,auto& delay,auto&) {
        for(std::size_t i=0;i<action.parameters.size();++i)
        {
            EXPECT_EQ(action.parameters[i].synapses,1);EXPECT_EQ(action.parameters[i].resistance,10.);
            delay[i]=.03+.1*(action.parameters[i].length-1);
            if(i){EXPECT_GE(action.parameters[i-1].length,action.parameters[i].length);}
        }
        EXPECT_EQ(action.parameters.back().length,1);
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_EQ(session.Parameters(),(std::vector<InputParameters>{{4,1,10.},{3,1,10.},{2,1,10.},{1,1,10.}}));
    ASSERT_GE(session.Evidence().size(),2u);EXPECT_EQ(session.Evidence()[0].inputIndex,2u);
    auto firstGrowth=std::find_if(session.Evidence().begin(),session.Evidence().end(),[](const auto& e){return e.inputIndex==2 && e.parameters.length==2;});
    ASSERT_NE(firstGrowth,session.Evidence().end());EXPECT_EQ(firstGrowth->parameterChangeCost,3.);
    EXPECT_EQ(session.Certificate()->Residuals().size(),4u);
}
}

namespace {
void JointN0Candidate(ProbeRouting routing)
{
    const auto p=Protocol(2,routing);auto cfg=Configuration();
    cfg.maximumCandidatesPerInput=3;
    cfg.bounds={{1,20,1,2,1.,100.},{1,1,1,1,1.,100.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const TrainingAction& action,auto& delay,auto& raw) {
        const auto& input=action.parameters[0];
        // Controlled response oracle, not a physical-neuron experiment:
        // L=2 has valid measured timing, and Ns=2 restores the captured raw
        // amplitude. Other lengths cannot synchronize at this small budget.
        delay[0]=input.length==2?.13:.03;
        if(input.synapses!=2)raw[0]+=.002;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);
    ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    EXPECT_EQ(session.Parameters()[0],(InputParameters{2,2,10.}));
    EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
    EXPECT_TRUE(std::any_of(session.Evidence().begin(),session.Evidence().end(),[](const auto& e) {
        return e.parameters.length==2 && e.parameters.synapses==2 && e.withinTiming && e.withinAmplitude;
    }));
}
}
TEST(BoundedTrainingN0Candidates, ClassicTimingReadyLengthGetsNearbyNsBeforeDistantLengths)
{JointN0Candidate(ProbeRouting::ClassicBurst);}
TEST(BoundedTrainingN0Candidates, BranchTimingReadyLengthGetsNearbyNsBeforeDistantLengths)
{JointN0Candidate(ProbeRouting::BranchSoloBurst);}

TEST(BoundedTrainingN0Candidates, LengthOnlySearchKeepsItsOriginalBudget)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=5;
        cfg.bounds={{1,20,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
        DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto&) {
            delay[0]=a.parameters[0].length==5?.13:.03;
        });
        ASSERT_EQ(session.Status(),TrainingStatus::Exact);
        EXPECT_EQ(session.Parameters()[0],(InputParameters{5,1,10.}));
        ASSERT_EQ(session.Evidence().size(),5u);
        for(const auto& e:session.Evidence())EXPECT_EQ(e.parameters.synapses,1);
    }
}
TEST(BoundedTrainingN0Candidates, WorseNeighborReturnsToLengthsAndIsNotIssuedTwice)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=40;
        cfg.bounds={{2,3,1,2,1.,100.},{1,1,1,1,1.,100.}};
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}});
        DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto& raw) {
            delay[0]=a.parameters[0].synapses==1?.13:.03;
            raw[0]+=.002;
        });
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
        // Four unique legal candidates, followed by the mandatory fresh best
        // restoration measurement. Priority points are not retried by fallback.
        ASSERT_EQ(session.Evidence().size(),5u);
        EXPECT_EQ(session.Evidence()[0].parameters,(InputParameters{2,1,10.}));
        EXPECT_EQ(session.Evidence()[1].parameters,(InputParameters{2,2,10.}));
        EXPECT_EQ(session.Evidence()[2].parameters,(InputParameters{3,1,10.}));
        for(std::size_t i=0;i<4;++i)for(std::size_t j=i+1;j<4;++j)
            EXPECT_NE(session.Evidence()[i].fullParameters,session.Evidence()[j].fullParameters);
    }
}
TEST(BoundedTrainingN0Candidates, PriorityWaitsForAllRequiredObservations)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.maximumCandidatesPerInput=3;cfg.n0CandidateRepeats=2;
    cfg.bounds={{1,20,1,2,1.,100.},{1,1,1,1,1.,100.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const TrainingAction& a,auto& delay,auto& raw) {
        delay[0]=a.parameters[0].length==2?.13:.03;
        if(a.parameters[0].synapses==1)raw[0]+=.002;
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);
    ASSERT_EQ(session.CandidateRepeats().size(),3u);
    for(const auto& group:session.CandidateRepeats())
    {
        EXPECT_TRUE(group.complete);ASSERT_EQ(group.trialIds.size(),2u);
        EXPECT_NE(group.trialIds[0],group.trialIds[1]);
        EXPECT_NE(group.anchorTrialIds[0],group.anchorTrialIds[1]);
    }
    EXPECT_EQ(session.CandidateRepeats().back().fullParameters[0],(InputParameters{2,2,10.}));
}


namespace {
void MeasuredLengthCandidate(ProbeRouting routing,Normalization normalization)
{
    const auto p=Protocol(2,routing);auto cfg=Configuration(2,normalization);
    cfg.maximumCandidatesPerInput=4;
    cfg.bounds={{2,20,1,1,10.,10.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const TrainingAction& action,auto& delay,auto&) {
        // Controlled response oracle, not a physical-neuron experiment. Three
        // completed lengths predict L12, outside the four-point nearest mesh.
        // Every candidate and the final all-input gate are still observed.
        delay[0]=.03+.01*(action.parameters[0].length-2);
    });
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);
    ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    EXPECT_EQ(session.Parameters()[0],(InputParameters{12,1,10.}));
    EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
    EXPECT_LE(session.Evidence().size(),4u);
    EXPECT_TRUE(std::any_of(session.Evidence().begin(),session.Evidence().end(),[](const auto& e) {
        return e.parameters.length==12 && e.withinTiming && e.withinAmplitude;
    }));
}
}
TEST(BoundedTrainingLengthCandidates, ClassicN0UsesMeasuredDelayTrendWithinOriginalBudget)
{MeasuredLengthCandidate(ProbeRouting::ClassicBurst,Normalization::SynapseCount);}
TEST(BoundedTrainingLengthCandidates, BranchN0UsesMeasuredDelayTrendWithinOriginalBudget)
{MeasuredLengthCandidate(ProbeRouting::BranchSoloBurst,Normalization::SynapseCount);}
TEST(BoundedTrainingLengthCandidates, ClassicN1UsesMeasuredDelayTrendWithinOriginalBudget)
{MeasuredLengthCandidate(ProbeRouting::ClassicBurst,Normalization::TipResistance);}
TEST(BoundedTrainingLengthCandidates, BranchN1UsesMeasuredDelayTrendWithinOriginalBudget)
{MeasuredLengthCandidate(ProbeRouting::BranchSoloBurst,Normalization::TipResistance);}


TEST(BoundedTrainingLengthCandidates, PredictedPointIsMeasuredAndCannotBypassTheFinalGate)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const bool damageFinal:{false,true})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=4;
        cfg.bounds={{2,20,1,1,10.,10.},{1,1,1,1,10.,10.}};
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}});
        DriveTraining(session,p,[&](const auto& action,auto& delay,auto&) {
            const int length=action.parameters[0].length;
            delay[0]=.03+.01*(length-2);
            if(length==12 && (!damageFinal || action.finalVerification))delay[0]=.03;
        });
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
        EXPECT_TRUE(std::any_of(session.Evidence().begin(),session.Evidence().end(),[](const auto& e){return e.parameters.length==12;}));
    }
}
TEST(BoundedTrainingLengthCandidates, N0ProposalWaitsForRequiredCandidateRepetitions)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.maximumCandidatesPerInput=4;cfg.n0CandidateRepeats=2;
    cfg.bounds={{2,20,1,1,10.,10.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}});
    DriveTraining(session,p,[](const auto& action,auto& delay,auto&) {
        delay[0]=.03+.01*(action.parameters[0].length-2);
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);
    ASSERT_EQ(session.CandidateRepeats().size(),4u);
    for(const auto& group:session.CandidateRepeats())
    {EXPECT_TRUE(group.complete);EXPECT_EQ(group.trialIds.size(),2u);EXPECT_EQ(group.anchorTrialIds.size(),2u);}
    EXPECT_EQ(session.Parameters()[0].length,12);
}
TEST(BoundedTrainingLengthCandidates, N1ProposedGeometryStillRequiresItsEffectiveResistanceDomain)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration(2,Normalization::TipResistance);
        cfg.maximumCandidatesPerInput=5;
        cfg.bounds={{2,20,1,1,10.,10.},{1,1,1,1,10.,10.}};
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},true);
        DriveTraining(session,p,[](const auto& action,auto& delay,auto&) {
            delay[0]=.03+.01*(action.parameters[0].length-2);
        },[](const auto& action) {
            // Controlled domain adapter; actual physical domains are checked
            // separately by native storage/Console experiments.
            ResistanceDomainAssessment d;d.status=ResistanceDomainStatus::Available;
            d.baseModelRevision=action.baseModelRevision;d.geometry=action.parameters;d.inputIndex=action.inputIndex;
            d.previewModelRevision="length_scope_"+std::to_string(action.parameters[0].length);
            d.minimumResistance=d.maximumResistance=10.;d.sourceAmplitude=1.;return d;
        });
        EXPECT_EQ(session.Status(),TrainingStatus::Exact);
        EXPECT_TRUE(std::any_of(session.Domains().begin(),session.Domains().end(),[](const auto& d){return d.geometry[0].length==12;}));
        EXPECT_EQ(session.Parameters()[0].length,12);
    }
}
TEST(BoundedTrainingLengthCandidates, NonmonotoneMeasurementsRetainTheBoundedLengthScan)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration();cfg.maximumCandidatesPerInput=4;
        cfg.bounds={{2,20,1,1,10.,10.},{1,1,1,1,10.,10.}};
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}});
        DriveTraining(session,p,[](const auto& action,auto& delay,auto&) {
            const int length=action.parameters[0].length;
            delay[0]=length==2?.03:length==3?.05:length==4?.04:.13;
        });
        EXPECT_EQ(session.Status(),TrainingStatus::Exact);EXPECT_EQ(session.Parameters()[0].length,5);
        ASSERT_EQ(session.Evidence().size(),4u);
        for(std::size_t i=0;i<4;++i)EXPECT_EQ(session.Evidence()[i].parameters.length,int(i)+2);
    }
}


// Controller-only protocol checks use the production recorder and session.
// They do not attest native physical dynamics or scientific classification.
namespace {
void CheckSweepBudget(ProbeRouting routing,Normalization normalization)
{
    for(std::size_t sweeps:{1u,2u})
    {
        const auto protocol=Protocol(2,routing);auto config=Configuration(2,normalization);
        config.maximumSweeps=sweeps;config.maximumCandidatesPerInput=2;
        config.bounds.assign(2,{1,1,1,1,10.,10.});
        BoundedTrainingSession session(References(protocol),config,{{1,1,10.},{1,1,10.}});
        DriveTraining(session,protocol);
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        EXPECT_EQ(session.Reason(),"maximum_sweeps_exhausted");
        ASSERT_TRUE(session.Certificate());EXPECT_FALSE(session.Certificate()->Exact());
        EXPECT_EQ(session.Certificate()->Residuals().size(),2u);
        EXPECT_FALSE(session.NextAction());EXPECT_EQ(session.AppliedEdits(),0u);
    }
}
}
TEST(TrainingTermination,MaximumSweepsClassicN0){CheckSweepBudget(ProbeRouting::ClassicBurst,Normalization::SynapseCount);}
TEST(TrainingTermination,MaximumSweepsClassicN1){CheckSweepBudget(ProbeRouting::ClassicBurst,Normalization::TipResistance);}
TEST(TrainingTermination,MaximumSweepsBranchN0){CheckSweepBudget(ProbeRouting::BranchSoloBurst,Normalization::SynapseCount);}
TEST(TrainingTermination,MaximumSweepsBranchN1){CheckSweepBudget(ProbeRouting::BranchSoloBurst,Normalization::TipResistance);}
TEST(TrainingTermination,ExactAtLastAllowedSweepTakesPrecedence)
{
    const auto protocol=Protocol();auto config=Configuration();config.maximumCandidatesPerInput=2;
    config.bounds.assign(2,{1,1,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,{{1,1,10.},{1,1,10.}});
    DriveTraining(session,protocol,[](const auto& action,auto& delay,auto&) {
        if(action.finalVerification)delay[0]=.13;
    });
    EXPECT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_TRUE(session.Certificate()->Exact());EXPECT_FALSE(session.NextAction());
}
TEST(TrainingTermination,InvalidMeasurementsRemainInvalidObservation)
{
    const auto protocol=Protocol();auto config=Configuration();config.maximumCandidatesPerInput=2;
    config.maximumInvalidObservations=10;config.bounds.assign(2,{1,1,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,{{1,1,10.},{1,1,10.}});
    unsigned calls=0;
    while(const auto action=session.NextAction())
    {
        ASSERT_LT(++calls,20u);ASSERT_EQ(action->kind,TrainingActionKind::Probe);
        const auto prepared=Prepare(protocol,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);auto raw=Raw(2);
        if(action->inputIndex==0)raw[0]=-.065; // Actual flat recording: no candidate peak.
        session.Consume(Observe(protocol,prepared,action->inputIndex,action->runId,action->trialId,{.03,.03},raw),action->baseModelRevision);
    }
    EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);EXPECT_FALSE(session.Certificate());
    EXPECT_FALSE(session.Rejected().empty());
}

TEST(TrainingTermination,NoAdjustableInputsRemainSearchUnresolved)
{
    const auto protocol=Protocol(1);auto config=Configuration(1);
    config.bounds.assign(1,{1,1,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,{{1,1,10.}});
    DriveTraining(session,protocol,[](const auto&,auto&,auto& raw){raw[0]+=.001;});
    EXPECT_EQ(session.Status(),TrainingStatus::SearchUnresolved);ASSERT_TRUE(session.Certificate());
    EXPECT_EQ(session.Reason(),"no_adjustable_inputs_outside_tolerance");
    EXPECT_FALSE(session.Certificate()->Exact());EXPECT_EQ(session.AppliedEdits(),0u);
}

TEST(TrainingTermination,ProbeAndAdapterBudgetReasonsAreDistinct)
{
    const auto protocol=Protocol();auto config=Configuration();config.maximumProbes=1;
    BoundedTrainingSession probes(References(protocol),config,{{1,1,10.},{1,1,10.}});
    DriveTraining(probes,protocol);EXPECT_EQ(probes.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(probes.Reason(),"maximum_probes_exhausted");
    config.maximumProbes=100;
    BoundedTrainingSession adapter(References(protocol),config,{{1,1,10.},{1,1,10.}});
    ASSERT_TRUE(adapter.NextAction());adapter.ExhaustBudget();
    EXPECT_EQ(adapter.Status(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(adapter.Reason(),"adapter_execution_budget_exhausted");
}
TEST(TrainingTermination,FinalRejectionDoesNotBorrowEarlierSearchDiagnostic)
{
    const auto protocol=Protocol();auto config=Configuration();config.maximumInvalidObservations=1;
    config.maximumCandidatesPerInput=2;config.bounds.assign(2,{1,1,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,{{1,1,10.},{1,1,10.}});
    unsigned calls=0;bool rejectedSearch=false;
    while(const auto action=session.NextAction())
    {
        ASSERT_LT(++calls,30u);ASSERT_EQ(action->kind,TrainingActionKind::Probe);
        const auto prepared=Prepare(protocol,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);auto raw=Raw(2);
        if(!action->finalVerification && action->inputIndex==0 && !rejectedSearch)
        {raw[0]=-.065;rejectedSearch=true;}
        auto observation=Observe(protocol,prepared,action->inputIndex,action->runId,action->trialId,{.03,.03},raw);
        if(action->finalVerification)observation.specification.patternHash="corrupted_final_pattern";
        session.Consume(observation,action->baseModelRevision);
    }
    ASSERT_TRUE(rejectedSearch);EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);
    EXPECT_EQ(session.Reason().find("final_verification:"),0u);EXPECT_FALSE(session.Certificate());
}

// Exercise the production controller and recorder across search/final/sweep
// boundaries. A configured retry budget belongs to the entire attempt.
enum class InvalidBudgetScenario { SearchThenFinal, FinalThenNextSweep, FinalOnly, Zero };
void CheckAttemptInvalidBudget(ProbeRouting routing,Normalization normalization,InvalidBudgetScenario scenario,
                              bool invalidPreparation)
{
    const auto protocol=Protocol(2,routing);auto config=Configuration(2,normalization);
    config.maximumInvalidObservations=scenario==InvalidBudgetScenario::Zero?0:1;
    config.maximumSweeps=2;config.maximumCandidatesPerInput=2;
    config.bounds.assign(2,{1,1,1,1,10.,10.});
    BoundedTrainingSession session(References(protocol),config,{{1,1,10.},{1,1,10.}});
    unsigned calls=0,invalidInjected=0;bool searchRejected=false,finalRejected=false;
    bool outsideFirstFinal=false,secondSweep=false;
    while(const auto action=session.NextAction())
    {
        ASSERT_LT(++calls,40u);ASSERT_EQ(action->kind,TrainingActionKind::Probe);
        auto prepared=Prepare(protocol,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        const bool rejectFinal=action->finalVerification && !finalRejected;
        if(rejectFinal && invalidPreparation)
        {
            prepared.protocolRevision="corrupted_budget_preparation";
            session.Arm(action->serial,prepared);finalRejected=true;++invalidInjected;
            continue;
        }
        session.Arm(action->serial,prepared);auto raw=Raw(2);
        if(!action->finalVerification && outsideFirstFinal)secondSweep=true;
        const bool rejectSearch=!action->finalVerification && action->inputIndex==0 && !searchRejected &&
            (scenario==InvalidBudgetScenario::SearchThenFinal ||
             (scenario==InvalidBudgetScenario::FinalThenNextSweep && secondSweep));
        if(rejectSearch){raw[0]=-.065;searchRejected=true;++invalidInjected;}
        // Final observations stay valid until their pattern identity is
        // deliberately corrupted below; the search failure is a missing peak.
        const bool failFirstFinal=scenario==InvalidBudgetScenario::FinalThenNextSweep &&
            action->finalVerification && action->inputIndex==0 && finalRejected && !secondSweep;
        if(failFirstFinal){raw[0]+=.001;outsideFirstFinal=true;}
        auto observation=Observe(protocol,prepared,action->inputIndex,action->runId,action->trialId,{.13,.03},raw);
        if(rejectFinal)
        {
            ASSERT_TRUE(observation.valid);
            observation.specification.patternHash="corrupted_budget_probe";
            finalRejected=true;++invalidInjected;
        }
        session.Consume(observation,action->baseModelRevision);
    }
    ASSERT_TRUE(finalRejected);
    EXPECT_EQ(session.InvalidObservations(),invalidInjected);
    if(scenario==InvalidBudgetScenario::FinalOnly)
    {
        EXPECT_EQ(invalidInjected,1u);EXPECT_EQ(session.Status(),TrainingStatus::Exact);
        ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    }
    else
    {
        EXPECT_EQ(invalidInjected,scenario==InvalidBudgetScenario::Zero?1u:2u);
        EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);
        EXPECT_FALSE(session.Certificate());
        if(scenario!=InvalidBudgetScenario::Zero)EXPECT_TRUE(searchRejected);
        if(scenario==InvalidBudgetScenario::FinalThenNextSweep)EXPECT_TRUE(secondSweep);
    }
}

#define ATTEMPT_INVALID_BUDGET_TEST(name,routing,normalization) \
TEST(TrainingInvalidBudget,name) { \
    for(const bool invalidPreparation:{false,true}) \
    for(const auto scenario:{InvalidBudgetScenario::SearchThenFinal,InvalidBudgetScenario::FinalThenNextSweep, \
                            InvalidBudgetScenario::FinalOnly,InvalidBudgetScenario::Zero}) { \
        SCOPED_TRACE(::testing::Message()<<"scenario="<<static_cast<int>(scenario)<<" invalidPreparation="<<invalidPreparation); \
        CheckAttemptInvalidBudget(routing,normalization,scenario,invalidPreparation); \
    } \
}
ATTEMPT_INVALID_BUDGET_TEST(ClassicN0,ProbeRouting::ClassicBurst,Normalization::SynapseCount)
ATTEMPT_INVALID_BUDGET_TEST(ClassicN1,ProbeRouting::ClassicBurst,Normalization::TipResistance)
ATTEMPT_INVALID_BUDGET_TEST(BranchN0,ProbeRouting::BranchSoloBurst,Normalization::SynapseCount)
ATTEMPT_INVALID_BUDGET_TEST(BranchN1,ProbeRouting::BranchSoloBurst,Normalization::TipResistance)
#undef ATTEMPT_INVALID_BUDGET_TEST

namespace {
TrainingCapacitance OwnedCapacitance()
{return {std::string(64,'a'),.3,{{"Dendrite1_1",.9},{"Dendrite1_2",1.1},{"Dendrite1_5",.8},{"Dendrite2_1",1.}}};}
void UntilCapacitanceEdit(BoundedTrainingSession& session,const VerificationProtocol& protocol,TrainingAction& edit)
{
    for(unsigned step=0;step<32;++step)
    {
        const auto action=session.NextAction();ASSERT_TRUE(action);
        if(action->kind==TrainingActionKind::Edit){edit=*action;return;}
        ASSERT_EQ(action->kind,TrainingActionKind::Probe);
        const auto prepared=Prepare(protocol,action->inputIndex,action->baseModelRevision,action->modelEpoch);
        session.Arm(action->serial,prepared);auto raw=Raw(2);raw[0]+=.001;
        session.Consume(Observe(protocol,prepared,action->inputIndex,action->runId,action->trialId,{.03,.03},raw),action->baseModelRevision);
    }
    FAIL()<<"missing expected structural edit";
}
TEST(BoundedTrainingCapacitance, CompleteMapFollowsProbesCandidatesAndRepeats)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.n0CandidateRepeats=2;cfg.tolerances.sync=1.;
    cfg.bounds={{2,2,1,2,10.,10.},{1,1,1,1,10.,10.}};
    const auto state=OwnedCapacitance();
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},false,state);
    DriveTraining(session,p,[&](const auto& action,auto&,auto& raw) {
        EXPECT_EQ(action.capacitance,std::optional<TrainingCapacitance>(state));
        if(action.inputIndex==0 && action.parameters[0].synapses==1)raw[0]+=.001;
    });
    ASSERT_EQ(session.Status(),TrainingStatus::Exact);ASSERT_FALSE(session.Evidence().empty());
    for(const auto& e:session.Evidence())EXPECT_EQ(e.capacitance,std::optional<TrainingCapacitance>(state));
    for(const auto& group:session.CandidateRepeats())EXPECT_EQ(group.capacitance,std::optional<TrainingCapacitance>(state));
    EXPECT_EQ(session.Capacitance(),std::optional<TrainingCapacitance>(state));
}
TEST(BoundedTrainingCapacitance, UnitScaleExtensionIsRetainedAfterEdit)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.tolerances.sync=1.;
    cfg.bounds={{2,3,1,1,10.,10.},{1,1,1,1,10.,10.}};
    const auto initial=OwnedCapacitance();
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},false,initial);
    TrainingAction action;ASSERT_NO_FATAL_FAILURE(UntilCapacitanceEdit(session,p,action));
    auto effective=initial;effective.membraneScales["Dendrite1_3"]=1.;
    session.Applied(action.serial,action.parameters,"native-grown-model",effective);
    ASSERT_EQ(session.Capacitance(),std::optional<TrainingCapacitance>(effective));
    const auto next=session.NextAction();ASSERT_TRUE(next);EXPECT_EQ(next->capacitance,session.Capacitance());
    EXPECT_EQ(session.Status(),TrainingStatus::Searching);
}
TEST(BoundedTrainingCapacitance, LostDormantScaleRejectsOtherwiseMatchingInputReadback)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.bounds={{2,3,1,1,10.,10.},{1,1,1,1,10.,10.}};
    const auto initial=OwnedCapacitance();
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},false,initial);
    TrainingAction action;ASSERT_NO_FATAL_FAILURE(UntilCapacitanceEdit(session,p,action));
    auto wrong=initial;wrong.membraneScales.erase("Dendrite1_5");
    session.Applied(action.serial,action.parameters,"different-model",wrong);
    EXPECT_EQ(session.Status(),TrainingStatus::InvalidModel);EXPECT_FALSE(session.Certificate());
    EXPECT_EQ(session.Capacitance(),std::optional<TrainingCapacitance>(initial));
}
TEST(BoundedTrainingCapacitance, UndeclaredTrimOfNewChannelIsNotAUnitGrowthExtension)
{
    const auto p=Protocol();auto cfg=Configuration();cfg.bounds={{2,3,1,1,10.,10.},{1,1,1,1,10.,10.}};
    const auto initial=OwnedCapacitance();
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},false,initial);
    TrainingAction action;ASSERT_NO_FATAL_FAILURE(UntilCapacitanceEdit(session,p,action));
    auto wrong=initial;wrong.membraneScales["Dendrite1_3"]=.95;
    session.Applied(action.serial,action.parameters,"different-model",wrong);
    EXPECT_EQ(session.Status(),TrainingStatus::InvalidModel);EXPECT_FALSE(session.Certificate());
}
TEST(BoundedTrainingCapacitance, DomainCannotDiscardFullCapacitanceContext)
{
    const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);
    cfg.bounds={{2,3,1,1,1.,100.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},true,OwnedCapacitance());
    bool domainRequested=false;
    DriveTraining(session,p,[](const auto&,auto&,auto& raw){raw[0]+=.001;},[&](const auto& action) {
        domainRequested=true;EXPECT_TRUE(action.capacitance);
        ResistanceDomainAssessment result;result.status=ResistanceDomainStatus::Available;
        result.baseModelRevision=action.baseModelRevision;result.previewModelRevision="preview";
        result.geometry=action.parameters;result.inputIndex=action.inputIndex;
        result.minimumResistance=1.;result.maximumResistance=100.;
        return result; // Deliberately omits the requested C context.
    });
    EXPECT_TRUE(domainRequested);EXPECT_EQ(session.Status(),TrainingStatus::InvalidModel);EXPECT_FALSE(session.Certificate());
    EXPECT_NE(session.Reason().find("resistance_domain_context_mismatch"),std::string::npos);
}

ResistanceDomainAssessment FairDomain(const TrainingAction& action,double low=1.,double high=100.)
{
    ResistanceDomainAssessment result;result.status=ResistanceDomainStatus::Available;
    result.baseModelRevision=action.baseModelRevision;result.geometry=action.parameters;
    result.inputIndex=action.inputIndex;result.minimumResistance=low;result.maximumResistance=high;
    result.previewModelRevision="fair_domain";
    for(const auto& p:action.parameters)result.previewModelRevision+="/"+std::to_string(p.length);
    return result;
}

TEST(BoundedTrainingN1LocalTurn, TimingReadyAmplitudeMissTriesAnotherRsBeforeOtherLengthsWithoutStarvingThem)
{
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    for(const bool losesTiming:{false,true})
    {
        const auto p=Protocol(2,routing);auto cfg=Configuration(2,Normalization::TipResistance);
        cfg.bounds={{2,4,1,1,1.,100.},{1,1,1,1,10.,10.}};
        cfg.maximumCandidatesPerInput=12;cfg.resistanceSubdivisionDepth=8;
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},true);
        std::map<int,int> assessments;
        DriveTraining(session,p,[&](const auto& a,auto& delay,auto& raw) {
            delay[0]=losesTiming && a.parameters[0].resistance!=10.?.03:.13;
            raw[0]+=.001; // No legal candidate is normalized; never invent Exact.
        },[&](const auto& a) {
            const auto visit=++assessments[a.parameters[0].length];
            // The local turn must reassess; its first interval is stale now.
            return FairDomain(a,visit==1?1.:2.,100.);
        });
        const auto& measured=session.Evidence();ASSERT_GE(measured.size(),5u);
        EXPECT_EQ(measured[0].parameters,(InputParameters{2,1,10.}));
        EXPECT_EQ(measured[1].parameters,(InputParameters{2,1,10.}));
        EXPECT_EQ(measured[2].parameters,(InputParameters{2,1,2.}));
        EXPECT_EQ(measured[3].parameters.length,3);
        EXPECT_NE(measured[1].anchorTrialId,measured[2].anchorTrialId);
        EXPECT_NE(measured[1].modelRevision,measured[2].modelRevision);
        EXPECT_GT(assessments[2],1);
        EXPECT_TRUE(std::any_of(measured.begin(),measured.end(),[](const auto& e){return e.parameters.length==4;}));
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        EXPECT_LE(session.IssuedProbes(),cfg.maximumProbes);
        EXPECT_LE(session.AppliedEdits(),cfg.maximumEdits);
        EXPECT_EQ(session.Parameters()[1],(InputParameters{1,1,10.}));
        EXPECT_FALSE(session.Status()==TrainingStatus::Exact);
    }
}

TEST(BoundedTrainingN1LocalTurn, SingletonDomainYieldsAndGlobalProbeBudgetStillStopsTheLocalTurn)
{
    for(const bool singleton:{false,true})
    {
        const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);
        cfg.bounds={{2,4,1,1,1.,100.},{1,1,1,1,10.,10.}};
        cfg.maximumProbes=singleton?12:4;
        BoundedTrainingSession session(References(p),cfg,{{2,1,10.},{1,1,10.}},true);
        DriveTraining(session,p,[](const auto&,auto& delay,auto& raw){delay[0]=.13;raw[0]+=.001;},
            [&](const auto& a){return FairDomain(a,singleton?10.:1.,singleton?10.:100.);});
        EXPECT_EQ(session.Status(),TrainingStatus::BudgetExhausted);
        EXPECT_LE(session.IssuedProbes(),cfg.maximumProbes);
        if(singleton)
            EXPECT_TRUE(std::any_of(session.Evidence().begin(),session.Evidence().end(),
                [](const auto& e){return e.parameters.length==4;}));
        else {
            EXPECT_EQ(session.IssuedProbes(),4u);EXPECT_EQ(session.Evidence().size(),2u);
            EXPECT_FALSE(session.Certificate());
        }
    }
}

TEST(BoundedTrainingFairDomains,ValidMeasurementsVisitGeometriesIndependentlyOfRecovery)
{
    for(const auto policy:{InvalidMeasurementRecovery::RetrySameCandidate,InvalidMeasurementRecovery::AdvanceUnassignedBurst})
    {
        const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);
        cfg.invalidMeasurementRecovery=policy;cfg.maximumInvalidObservations=32;
        cfg.resistanceSubdivisionDepth=0;cfg.bounds={{1,3,1,1,1.,100.},{1,1,1,1,10.,10.}};
        BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}},true);
        DriveTraining(session,p,[](const auto&,auto&,auto& raw){raw[0]+=.001;},
            [](const auto& action){return FairDomain(action);});
        std::set<std::pair<int,double>> covered;
        std::size_t firstLength3=10000,firstOtherResistance=10000,index=0;
        for(const auto& e:session.Evidence())
        {
            if(e.inputIndex!=0)continue;
            covered.insert({e.parameters.length,e.parameters.resistance});
            if(e.parameters.length==3)firstLength3=std::min(firstLength3,index);
            if(e.parameters.length==1 && e.parameters.resistance!=10.)firstOtherResistance=std::min(firstOtherResistance,index);
            ++index;
        }
        // The same finite mesh survives the order change, including revisits.
        for(int length=1;length<=3;++length)for(double resistance:{1.,10.,100.})
            EXPECT_TRUE(covered.contains({length,resistance}));
        EXPECT_LT(firstLength3,firstOtherResistance);
        EXPECT_NE(session.Status(),TrainingStatus::Exact);
        EXPECT_LE(session.IssuedProbes(),cfg.maximumProbes);
    }
}

TEST(BoundedTrainingFairDomains,SmallInvalidBudgetCoversSeveralGeometriesWithoutAcceptingMissingWaves)
{
    const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);
    cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
    cfg.maximumInvalidObservations=2;cfg.resistanceSubdivisionDepth=2;
    cfg.bounds={{1,4,1,1,1.,100.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}},true);
    std::size_t iterations=0;
    while(const auto a=session.NextAction())
    {
        ASSERT_LT(++iterations,200u);
        if(a->kind==TrainingActionKind::Edit)
        {session.Applied(a->serial,a->parameters,"fair_edit"+std::to_string(a->serial));continue;}
        if(a->kind==TrainingActionKind::ResistanceDomain)
        {session.AssessedDomain(a->serial,FairDomain(*a),a->baseModelRevision);continue;}
        const auto prepared=Prepare(p,a->inputIndex,a->baseModelRevision,a->modelEpoch);
        session.Arm(a->serial,prepared);
        const bool extra=a->inputIndex==0 && a->serial>2;
        auto observation=Observe(p,prepared,a->inputIndex,a->runId,a->trialId,{.03,.03},Raw(2),extra);
        session.Consume(observation,a->baseModelRevision);
    }
    EXPECT_EQ(session.Status(),TrainingStatus::InvalidObservation);EXPECT_FALSE(session.Certificate());
    EXPECT_EQ(session.InvalidObservations(),3u);
    ASSERT_EQ(session.Recoveries().size(),3u);
    std::set<int> lengths;
    for(const auto& event:session.Recoveries())lengths.insert(event.fullParameters[0].length);
    EXPECT_EQ(lengths.size(),3u);
    EXPECT_EQ(session.Recoveries().back().disposition,CandidateRecoveryDisposition::InvalidBudgetStop);
    EXPECT_EQ(session.Recoveries().back().invalidBefore,2u);
}

TEST(BoundedTrainingFairDomains,EveryGeometryReturnReassessesChangedBoundsBeforeAnEdit)
{
    const auto p=Protocol();auto cfg=Configuration(2,Normalization::TipResistance);
    cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
    cfg.maximumInvalidObservations=8;cfg.resistanceSubdivisionDepth=0;
    cfg.bounds={{1,3,1,1,1.,100.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.}},true);
    std::map<int,int> assessments;std::map<int,std::pair<double,double>> liveBounds;
    int inputObservations=0;
    DriveTraining(session,p,[&](const auto& a,auto&,auto& raw) {
        raw[0]+=.001;
        if(a.inputIndex==0 && liveBounds.contains(a.parameters[0].length))
        {
            const auto [low,high]=liveBounds.at(a.parameters[0].length);
            EXPECT_GE(a.parameters[0].resistance,low);EXPECT_LE(a.parameters[0].resistance,high);
        }
        // Bounds intentionally change between assessed visits in this adapter.
        // Stop before restore-best/final phases: this case checks live cursor
        // reassessment, not feasibility of historical best under changed physics.
        if(a.inputIndex==0 && ++inputObservations==8)session.ExternalStop();
    },[&](const auto& action) {
        const int length=action.parameters[0].length;
        const bool changed=++assessments[length]>1;
        const auto bounds=changed?std::pair{20.,30.}:std::pair{1.,100.};
        liveBounds[length]=bounds;
        return FairDomain(action,bounds.first,bounds.second);
    });
    for(int length=1;length<=3;++length)EXPECT_GT(assessments[length],1);
    EXPECT_EQ(session.Status(),TrainingStatus::ExternalStop);
}

TEST(BoundedTrainingFairDomains,BranchVariantsRetainPhysicalBankLegalityAndTheFixedReference)
{
    const auto p=Protocol(3,ProbeRouting::BranchSoloBurst);auto cfg=Configuration(3,Normalization::TipResistance);
    cfg.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;
    cfg.maximumInvalidObservations=8;cfg.resistanceSubdivisionDepth=0;cfg.maximumCandidatesPerInput=24;
    cfg.bounds={{1,5,1,1,1.,100.},{1,4,1,1,1.,100.},{1,1,1,1,10.,10.}};
    BoundedTrainingSession session(References(p),cfg,{{1,1,10.},{1,1,10.},{1,1,10.}},true);
    DriveTraining(session,p,[](const auto&,auto&,auto& raw){raw[0]+=.001;raw[1]+=.001;},
        [](const auto& action){return FairDomain(action);});
    ASSERT_FALSE(session.Evidence().empty());
    EXPECT_EQ(session.Evidence().front().inputIndex,1u);
    std::set<std::vector<int>> geometries;
    bool reachedUpstreamInput=false;
    for(const auto& e:session.Evidence())
    {
        // Reverse order starts at1, then legitimately continues with0 once
        // that input's bounded search ends. Check bank legality throughout;
        // geometry coverage below belongs only to the first selected input.
        EXPECT_LE(e.inputIndex,1u);
        if(e.inputIndex==0)reachedUpstreamInput=true;
        else EXPECT_FALSE(reachedUpstreamInput);
        const auto& ps=e.fullParameters;
        EXPECT_GE(ps[0].length,ps[1].length);EXPECT_GE(ps[1].length,ps[2].length);
        EXPECT_EQ(ps[2],(InputParameters{1,1,10.}));
        for(std::size_t i=0;i+1<ps.size();++i)
            if(ps[i].length==ps[i+1].length)EXPECT_EQ(ps[i].resistance,ps[i+1].resistance);
        if(e.inputIndex==1)geometries.insert({ps[0].length,ps[1].length,ps[2].length});
    }
    EXPECT_GE(geometries.size(),4u);EXPECT_NE(session.Status(),TrainingStatus::Exact);
}

TEST(CandidateRecoveryEvidenceCodec,FullOwnedCapacitanceSurvivesJson)
{
    CandidateRecoveryEvidence e;e.actionSerial=7;e.inputIndex=e.candidateInputIndex=0;e.sweep=1;e.modelEpoch=3;
    e.runId="run/session/1";e.trialId=e.runId+"/search/7";e.baseModelRevision=std::string(64,'a');
    e.effectiveModelRevision=std::string(64,'b');e.invalidBefore=1;e.invalidAfter=2;
    e.fullParameters={{2,3,10.},{1,1,20.}};e.capacitance=OwnedCapacitance();
    e.disposition=CandidateRecoveryDisposition::CursorAdvanced;e.statusAfter=TrainingStatus::Searching;
    const auto encoded=EncodeCandidateRecoveryEvidence(e);
    EXPECT_EQ(encoded.size(),18);EXPECT_EQ(encoded["disposition"],QJsonValue("cursor_advanced"));
    EXPECT_EQ(encoded["full_parameters"].toArray().size(),2);
    EXPECT_EQ(encoded["full_parameters"].toArray()[0].toObject()["synapses"],QJsonValue(3));
    const auto capacitance=encoded["capacitance"].toObject();EXPECT_EQ(capacitance["membrane_scales"].toObject().size(),4);
    EXPECT_EQ(capacitance["membrane_scales"].toObject()["Dendrite1_2"],QJsonValue(1.1));
    EXPECT_EQ(QJsonDocument::fromJson(QJsonDocument(encoded).toJson()).object(),encoded);
    EXPECT_FALSE(encoded.contains("certificate"));EXPECT_FALSE(encoded.contains("evaluation_verdict"));
}
TEST(CandidateRecoveryEvidenceCodec,RejectsUnknownEnumsAndNonfiniteOrInexactNumbers)
{
    CandidateRecoveryEvidence e;e.fullParameters={{1,1,10.}};
    auto bad=e;bad.disposition=static_cast<CandidateRecoveryDisposition>(999);
    EXPECT_THROW(EncodeCandidateRecoveryEvidence(bad),std::invalid_argument);
    bad=e;bad.validity=PeakValidity::Valid;EXPECT_THROW(EncodeCandidateRecoveryEvidence(bad),std::invalid_argument);
    bad=e;bad.statusAfter=static_cast<TrainingStatus>(999);EXPECT_THROW(EncodeCandidateRecoveryEvidence(bad),std::invalid_argument);
    bad=e;bad.fullParameters[0].resistance=std::numeric_limits<double>::quiet_NaN();
    EXPECT_THROW(EncodeCandidateRecoveryEvidence(bad),std::invalid_argument);
    bad=e;bad.capacitance=OwnedCapacitance();bad.capacitance->membraneScales.begin()->second=std::numeric_limits<double>::infinity();
    EXPECT_THROW(EncodeCandidateRecoveryEvidence(bad),std::invalid_argument);
    if(sizeof(std::size_t)>=8)
    {bad=e;bad.invalidAfter=static_cast<std::size_t>(9007199254740992ULL);EXPECT_THROW(EncodeCandidateRecoveryEvidence(bad),std::invalid_argument);}
}
}
