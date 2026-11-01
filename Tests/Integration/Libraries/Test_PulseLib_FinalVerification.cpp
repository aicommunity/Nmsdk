#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
VerificationProtocol Protocol(std::size_t n,ProbeRouting routing=ProbeRouting::ClassicBurst)
{
    VerificationProtocol p;p.routing=routing;p.revision="native_protocol";p.sampleId="target";
    p.patternHash="configured_pattern";p.originStimulusId="p0";p.maximumSampleGap=.05;
    for(std::size_t i=0;i<n;++i){p.inputs.push_back({"i"+std::to_string(i),"p"+std::to_string(i)});p.stimulusIds.push_back("p"+std::to_string(i));}
    return p;
}
std::vector<double> Raw(std::size_t n){std::vector<double> v;for(std::size_t i=0;i<n;++i)v.push_back(.01+.001*i);return v;}
std::size_t Index(const VerificationProtocol& p,const std::string& id)
{
    return std::find_if(p.inputs.begin(),p.inputs.end(),[&](const auto& x){return x.id==id;})-p.inputs.begin();
}
PreparedVerificationProbe Prepared(const VerificationRequest& r)
{
    PreparedVerificationProbe result{r.routing,r.inputId,r.protocolRevision,r.baseModelRevision,"effective:"+r.trialId,r.epoch};
    if(r.routing==ProbeRouting::BranchSoloBurst)result.selectedInputIndex=r.inputIndex;
    return result;
}
ProbeObservation Observation(const VerificationProtocol& p,const PreparedVerificationProbe& context,
    const std::string& run,const std::string& trial,std::vector<double> raw={},
    std::vector<int> centers={},double baseline=0.,bool plateau=false,double origin=0.,double period=.05)
{
    const auto n=p.inputs.size();if(raw.empty())raw=Raw(n);if(centers.empty())centers.assign(n,12);
    const auto active=Index(p,context.inputId);const bool branch=p.routing==ProbeRouting::BranchSoloBurst;
    ProbeSpec s;s.runId=run;s.trialId=trial;s.sampleId=p.sampleId;s.patternHash=p.patternHash;
    s.schemaVersion=p.schemaVersion;s.stimulusProfile=p.stimulusProfile;s.waveAssignment=p.waveAssignment;
    s.peakSelection=p.peakSelection;
    const double duration=20.*period;
    s.modelRevision=context.effectiveModelRevision;s.begin=origin;s.end=origin+duration;s.maximumSampleGap=period;
    s.maximumSamples=21;s.minimumAmplitude=p.minimumAmplitude;s.expectedStimulusIds=p.stimulusIds;
    s.baseline.assign(branch?1:n,baseline);
    for(std::size_t i=0;i<n;++i)
        if(!branch || i==active)s.windows.push_back({p.inputs[i].id,branch?0:i,s.begin,s.end,p.inputs[i].stimulusId});
    ProbeRecorder recorder(s);
    for(int tick=0;tick<=20;++tick)
    {
        std::vector<double> values(branch?1:n,baseline);
        for(std::size_t i=0;i<n;++i)
            if(!branch || i==active)
            {
                double shape=std::max(0.,1.-std::abs(tick-centers[i])/2.);
                if(plateau && tick==centers[i]+1)shape=1.;
                values[branch?0:i]=baseline+(raw[i]-baseline)*shape;
            }
        recorder.Observe(origin+double(tick)/20.*duration,values,context.effectiveModelRevision);
    }
    for(std::size_t i=0;i<n;++i)recorder.RecordStimulus(p.stimulusIds[i],origin+double(i+1)/20.*duration);
    return recorder.Close(s.end,context.effectiveModelRevision,"window_closed");
}
TEST(TimeLearnerClock,FinalMeasurementCoverageUsesAbsoluteEndpoints)
{
    for(double origin:{131.,1000000.})for(double period:{.0005,.00005})
    {
        auto protocol=Protocol(1);protocol.maximumSampleGap=period;
        PreparedVerificationProbe context{protocol.routing,"i0",protocol.revision,"initial","effective",0};
        const auto observation=Observation(protocol,context,"clock","clock_trial",{},{},0.,false,origin,period);
        ASSERT_TRUE(observation.valid);EXPECT_NO_THROW(ValidateProbeMeasurement(protocol,0,context,observation));
    }
}
CapturedReferences References(const VerificationProtocol& p,std::vector<double> raw={},double baseline=0.)
{
    std::vector<ReferenceEvidence> evidence;
    for(std::size_t i=0;i<p.inputs.size();++i)
    {
        PreparedVerificationProbe context{p.routing,p.inputs[i].id,p.revision,"initial_model","reference_effective_"+std::to_string(i),0};
        if(p.schemaVersion==3 && p.routing==ProbeRouting::BranchSoloBurst)context.selectedInputIndex=i;
        evidence.push_back({context,Observation(p,context,"capture","reference_"+std::to_string(i),raw,{},baseline)});
    }
    return CapturedReferences::Capture(p,evidence);
}
ProbeObservation FullClassicPair(const VerificationProtocol& p,const PreparedVerificationProbe& context,
    const std::string& run,const std::string& trial,bool wrongChannel=false)
{
    ProbeSpec s;s.schemaVersion=p.schemaVersion;s.waveAssignment=p.waveAssignment;s.stimulusProfile=p.stimulusProfile;
    s.peakSelection=p.peakSelection;
    s.runId=run;s.trialId=trial;s.sampleId=p.sampleId;s.patternHash=p.patternHash;s.modelRevision=context.effectiveModelRevision;
    s.begin=0.;s.end=1.;s.maximumSampleGap=.05;s.maximumSamples=21;s.baseline={0.,0.};s.expectedStimulusIds=p.stimulusIds;
    s.windows={{"i0",wrongChannel?1u:0u,wrongChannel?.3:.5,wrongChannel?.5:.7,"p0"},{"i1",1,.5,.7,"p1"}};
    if(p.peakSelection==PeakSelectionPolicy::AssignedBurstWave)
        for(auto& window:s.windows){window.begin=0.;window.end=1.;}
    ProbeRecorder recorder(s);
    for(int tick=0;tick<=20;++tick)
    {
        const auto triangle=[&](int center){return std::max(0.,1.-std::abs(tick-center)/2.);};
        recorder.Observe(double(tick)/20.,{.01*(triangle(12)+triangle(16)),.011*(triangle(8)+triangle(12))},context.effectiveModelRevision);
    }
    recorder.RecordStimulus("p0",.05);recorder.RecordStimulus("p1",.1);
    return recorder.Close(1.,context.effectiveModelRevision,"window_closed");
}
VerificationConfig Configuration(std::size_t maximum=32)
{VerificationConfig c;c.runId="verification_attempt";c.currentModelRevision="learned_model";c.maximumProbes=maximum;return c;}
void Complete(FinalVerificationSession& session,const VerificationProtocol& p,std::vector<double> raw={},
              std::vector<int> centers={},double baseline=0.,bool plateau=false)
{
    while(auto request=session.NextRequest())
    {
        const auto prepared=Prepared(*request);session.Arm(prepared);
        session.Consume(Observation(p,prepared,request->runId,request->trialId,raw,centers,baseline,plateau),request->baseModelRevision);
    }
}

TEST(FinalVerification, RequiresEveryInputAndMeasuredReferenceForDimensionsOneThroughSix)
{
    for(auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
        for(std::size_t n:{1u,2u,4u,6u})
        {
            const auto p=Protocol(n,routing);const auto refs=References(p);
            FinalVerificationSession session(refs,Configuration());
            EXPECT_EQ(session.AcceptedInputs(),0u);EXPECT_FALSE(session.Certificate());
            const auto first=session.NextRequest();ASSERT_TRUE(first);
            EXPECT_EQ(first->inputId,routing==ProbeRouting::ClassicBurst?"i0":"i"+std::to_string(n-1));
            Complete(session,p);
            EXPECT_EQ(session.Status(),VerificationStatus::Exact);EXPECT_EQ(session.AcceptedInputs(),n);
            ASSERT_TRUE(session.Certificate());EXPECT_EQ(session.Certificate()->Residuals().size(),n);
            EXPECT_TRUE(session.Certificate()->Exact());
        }
}

TEST(FinalVerification, NativeSourcePhysicsCannotChangeBetweenReferencesAndVerification)
{
    auto p=Protocol(1);p.schemaVersion=2;p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    const auto references=References(p);
    FinalVerificationSession good(references,Configuration());Complete(good,p);
    ASSERT_EQ(good.Status(),VerificationStatus::Exact);
    for(int factor=0;factor<6;++factor)
    {
        FinalVerificationSession session(references,Configuration());const auto r=session.NextRequest();ASSERT_TRUE(r);
        const auto prepared=Prepared(*r);session.Arm(prepared);auto changed=p;
        switch(factor)
        {
        case 0:changed.stimulusProfile->amplitude+=1e-12;break;
        case 1:changed.stimulusProfile->pulseLength*=2.;break;
        case 2:changed.stimulusProfile->frequencyHz*=10.;break;
        case 3:changed.stimulusProfile->generatorClass="other_image";break;
        case 4:changed.stimulusProfile->useTransitSignal=true;break;
        case 5:changed.schemaVersion=1;changed.stimulusProfile.reset();break;
        }
        auto measured=Observation(changed,prepared,r->runId,r->trialId);
        ASSERT_TRUE(measured.valid); // Identical peaks cannot validate a different source.
        session.Consume(measured,r->baseModelRevision);
        EXPECT_EQ(session.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(session.Certificate());
    }
}

TEST(FinalVerification, LocalSuccessDoesNotReplaceFreshGlobalSweep)
{
    const auto p=Protocol(4,ProbeRouting::BranchSoloBurst);const auto refs=References(p);
    FinalVerificationSession session(refs,Configuration());
    const auto r=session.NextRequest();ASSERT_TRUE(r);const auto prepared=Prepared(*r);session.Arm(prepared);
    EXPECT_TRUE(session.WaitingForObservation());EXPECT_FALSE(session.NextRequest());
    session.Consume(Observation(p,prepared,r->runId,r->trialId),r->baseModelRevision);
    EXPECT_EQ(session.AcceptedInputs(),1u);EXPECT_EQ(session.Status(),VerificationStatus::Collecting);
    EXPECT_FALSE(session.Certificate());
    auto wrong=Prepared(*session.NextRequest());wrong.inputId.clear();session.Arm(wrong);
    EXPECT_EQ(session.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(session.Certificate());
}

TEST(FinalVerification, UsesFreshAnchorTimingAndPreservesSignedTimingResiduals)
{
    const auto p=Protocol(2);const auto refs=References(p);
    FinalVerificationSession shifted(refs,Configuration());Complete(shifted,p,{},std::vector<int>{14,14});
    ASSERT_EQ(shifted.Status(),VerificationStatus::Exact); // Initial anchor was at sample 12.
    FinalVerificationSession early(refs,Configuration());Complete(early,p,{},std::vector<int>{10,12});
    ASSERT_EQ(early.Status(),VerificationStatus::OutsideTolerance);ASSERT_TRUE(early.Certificate());
    EXPECT_NEAR(early.Certificate()->Residuals()[0].timingResidualLow,-.1,1e-14);
    EXPECT_NEAR(early.Certificate()->Residuals()[0].timingResidualHigh,-.1,1e-14);
}

TEST(FinalVerification, DoesNotReplaceOriginalTolerancesWithPercentOrOneTimeStep)
{
    const auto p=Protocol(2);const auto refs=References(p);auto raw=Raw(2);raw[0]+=2e-5;
    FinalVerificationSession session(refs,Configuration());Complete(session,p,raw);
    ASSERT_EQ(session.Status(),VerificationStatus::OutsideTolerance);ASSERT_TRUE(session.Certificate());
    EXPECT_DOUBLE_EQ(session.Certificate()->Residuals()[0].amplitudeTolerance,1e-5);
    FinalVerificationSession strict(refs,Configuration());Complete(strict,p,{},std::vector<int>{11,12});
    EXPECT_EQ(strict.Status(),VerificationStatus::OutsideTolerance);
    auto c=Configuration();c.tolerances.sync=.11;
    FinalVerificationSession declared(refs,c);Complete(declared,p,{},std::vector<int>{10,12});
    EXPECT_EQ(declared.Status(),VerificationStatus::Exact);
}

TEST(FinalVerification, CapturedPerInputUsesRawPotentialNotChangedBaselineDeviation)
{
    const auto p=Protocol(1);
    for(const auto& [raw,baseline]:std::vector<std::pair<double,double>>{{2.03125,2.},{0.,-1.},{-.5,-1.}})
    {
        const auto refs=References(p,{raw},baseline);
        FinalVerificationSession session(refs,Configuration());Complete(session,p,{raw},{},baseline-1.);
        ASSERT_EQ(session.Status(),VerificationStatus::Exact);ASSERT_TRUE(session.Certificate());
        EXPECT_DOUBLE_EQ(session.Certificate()->Residuals()[0].targetRawPotential,raw);
        EXPECT_DOUBLE_EQ(session.Certificate()->Residuals()[0].amplitudeResidual,0.);
    }
}

TEST(FinalVerification, PlateauUncertaintyCannotBeHiddenBySelectingItsFirstSample)
{
    const auto p=Protocol(2);const auto refs=References(p);
    FinalVerificationSession session(refs,Configuration());Complete(session,p,{},{},0.,true);
    ASSERT_EQ(session.Status(),VerificationStatus::OutsideTolerance);ASSERT_TRUE(session.Certificate());
    EXPECT_NEAR(session.Certificate()->Residuals()[0].timingResidualLow,-.05,1e-14);
    EXPECT_NEAR(session.Certificate()->Residuals()[0].timingResidualHigh,.05,1e-14);
}

TEST(FinalVerification, ModelChangeInvalidatesAllInputsEvenWhenSameHashIsRestored)
{
    const auto p=Protocol(2);const auto refs=References(p);FinalVerificationSession session(refs,Configuration());
    auto old=session.NextRequest();auto prepared=Prepared(*old);session.Arm(prepared);
    const auto data=Observation(p,prepared,old->runId,old->trialId);session.Consume(data,old->baseModelRevision);
    ASSERT_EQ(session.AcceptedInputs(),1u);
    session.Invalidate("learned_model");EXPECT_EQ(session.AcceptedInputs(),0u);EXPECT_EQ(session.ModelEpoch(),1u);
    const auto next=session.NextRequest();ASSERT_TRUE(next);EXPECT_NE(next->trialId,old->trialId);
    session.Arm(Prepared(*next));session.Consume(data,next->baseModelRevision);
    EXPECT_EQ(session.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(session.Certificate());
}

TEST(FinalVerification, CertificateBindsReferencesCriteriaEpochAndSoloState)
{
    const auto p=Protocol(1);const auto refs=References(p);const auto c=Configuration();
    FinalVerificationSession session(refs,c);Complete(session,p);ASSERT_TRUE(session.Certificate());
    const auto certificate=*session.Certificate();
    EXPECT_TRUE(certificate.Matches(c.currentModelRevision,refs,c.tolerances,ModelStateKind::LearnedSolo,0));
    EXPECT_FALSE(certificate.Matches(c.currentModelRevision,refs,c.tolerances,ModelStateKind::Recognition,0));
    auto loosened=c.tolerances;loosened.amplitudeRelative=.01;
    EXPECT_FALSE(certificate.Matches(c.currentModelRevision,refs,loosened,ModelStateKind::LearnedSolo,0));
    session.Invalidate(c.currentModelRevision);EXPECT_FALSE(session.Certificate());
    EXPECT_FALSE(certificate.Matches(c.currentModelRevision,refs,c.tolerances,ModelStateKind::LearnedSolo,session.ModelEpoch()));
    const auto other=References(p,{.02});
    EXPECT_FALSE(certificate.Matches(c.currentModelRevision,other,c.tolerances,ModelStateKind::LearnedSolo,0));
}

TEST(FinalVerification, ExternalStopAndBudgetExhaustionCannotIssueExact)
{
    const auto p=Protocol(4);const auto refs=References(p);
    FinalVerificationSession limited(refs,Configuration(2));Complete(limited,p);
    EXPECT_EQ(limited.Status(),VerificationStatus::BudgetExhausted);EXPECT_FALSE(limited.Certificate());
    FinalVerificationSession stopped(refs,Configuration());auto r=stopped.NextRequest();stopped.Arm(Prepared(*r));
    stopped.ExternalStop();stopped.Consume(Observation(p,Prepared(*r),r->runId,r->trialId),r->baseModelRevision);
    EXPECT_EQ(stopped.Status(),VerificationStatus::ExternalStop);EXPECT_FALSE(stopped.Certificate());
    FinalVerificationSession timeout(refs,Configuration());timeout.ExhaustBudget();
    EXPECT_EQ(timeout.Status(),VerificationStatus::BudgetExhausted);EXPECT_FALSE(timeout.Certificate());
}

TEST(FinalVerification, BoundedRecoveryUsesANewTrialAndNeverTheRejectedMeasurement)
{
    const auto p=Protocol(1);const auto refs=References(p);auto c=Configuration(2);c.maximumInvalidObservations=1;
    FinalVerificationSession session(refs,c);auto old=session.NextRequest();const auto prepared=Prepared(*old);
    session.Arm(prepared);session.Consume(Observation(p,prepared,old->runId,old->trialId,{0.}),old->baseModelRevision);
    EXPECT_EQ(session.Status(),VerificationStatus::Collecting);EXPECT_EQ(session.AcceptedInputs(),0u);
    auto retry=session.NextRequest();ASSERT_TRUE(retry);EXPECT_NE(retry->trialId,old->trialId);
    Complete(session,p);ASSERT_EQ(session.Status(),VerificationStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_EQ(session.Rejected().size(),1u);EXPECT_EQ(session.IssuedProbes(),2u);
    EXPECT_EQ(session.Certificate()->Residuals()[0].trialId,retry->trialId);
}

TEST(FinalVerification, DoesNotTrustValidFlagForMalformedNumericsOrSchema)
{
    const auto p=Protocol(1);const auto refs=References(p);
    for(int corruption=0;corruption<4;++corruption)
    {
        FinalVerificationSession session(refs,Configuration());auto r=session.NextRequest();const auto prepared=Prepared(*r);session.Arm(prepared);
        auto data=Observation(p,prepared,r->runId,r->trialId);
        if(corruption==0)data.peaks[0].rawPotential=std::numeric_limits<double>::quiet_NaN();
        if(corruption==1)data.schemaVersion=2;
        if(corruption==2)data.peaks[0].delayFromStimulus=17.;
        if(corruption==3)data.stimuli.push_back(data.stimuli[0]);
        session.Consume(data,r->baseModelRevision);
        EXPECT_EQ(session.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(session.Certificate());
    }
}

TEST(FinalVerification, CapturingReferencesRequiresAllInputsAndOneInitialModel)
{
    const auto p=Protocol(2,ProbeRouting::BranchSoloBurst);
    EXPECT_THROW(CapturedReferences::Capture(p,{}),std::invalid_argument);
    std::vector<ReferenceEvidence> evidence;
    for(std::size_t i=0;i<2;++i)
    {
        PreparedVerificationProbe prepared{p.routing,p.inputs[i].id,p.revision,"initial_"+std::to_string(i),"effective",0};
        evidence.push_back({prepared,Observation(p,prepared,"capture","ref"+std::to_string(i))});
    }
    EXPECT_THROW(CapturedReferences::Capture(p,evidence),std::invalid_argument);
}

TEST(FinalVerification, WholeBurstPolicyBindsReferencesAndCertificate)
{
    auto p=Protocol(1);p.schemaVersion=3;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    const auto refs=References(p);FinalVerificationSession session(refs,Configuration());Complete(session,p);
    ASSERT_EQ(session.Status(),VerificationStatus::Exact);ASSERT_TRUE(session.Certificate());
    EXPECT_EQ(session.Certificate()->Protocol().waveAssignment,WaveAssignmentPolicy::OrderedWholeBurst);
    EXPECT_EQ(session.Certificate()->Protocol().schemaVersion,3u);
    for(int fault=0;fault<5;++fault)
    {
        FinalVerificationSession invalid(refs,Configuration());auto r=invalid.NextRequest();ASSERT_TRUE(r);
        const auto prepared=Prepared(*r);invalid.Arm(prepared);
        auto data=Observation(p,prepared,r->runId,r->trialId);ASSERT_TRUE(data.valid);
        switch(fault)
        {
        case 0:data.burstAssignments.clear();break;
        case 1:data.burstAssignments[0].waves[0].stimulusId="other";break;
        case 2:data.burstAssignments[0].waves[0].time+=.05;break;
        case 3:data.burstAssignments[0].validity=PeakValidity::Ambiguous;break;
        case 4:data.specification.waveAssignment=WaveAssignmentPolicy::WindowOnly;break;
        }
        invalid.Consume(data,r->baseModelRevision);
        EXPECT_EQ(invalid.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(invalid.Certificate());
    }
}

TEST(FinalVerification, Schema3RequiresOwnPhysicalChannelAndCompleteModelDimensions)
{
    auto p=Protocol(2);p.schemaVersion=3;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    std::vector<ReferenceEvidence> good,bad;
    for(std::size_t i=0;i<2;++i)
    {
        PreparedVerificationProbe context{p.routing,p.inputs[i].id,p.revision,"initial_model","reference_effective",0};
        auto correct=FullClassicPair(p,context,"capture","good");ASSERT_TRUE(correct.valid);
        auto wrong=FullClassicPair(p,context,"capture","wrong",true);ASSERT_TRUE(wrong.valid);
        good.push_back({context,correct});bad.push_back({context,wrong});
    }
    const auto refs=CapturedReferences::Capture(p,good);
    EXPECT_THROW(CapturedReferences::Capture(p,bad),std::invalid_argument);
    FinalVerificationSession session(refs,Configuration());
    while(auto r=session.NextRequest())
    {
        const auto context=Prepared(*r);session.Arm(context);
        session.Consume(FullClassicPair(p,context,r->runId,r->trialId),r->baseModelRevision);
    }
    EXPECT_EQ(session.Status(),VerificationStatus::Exact);
    auto reordered=p;std::swap(reordered.inputs[0].stimulusId,reordered.inputs[1].stimulusId);
    EXPECT_THROW(CapturedReferences::Capture(reordered,good),std::invalid_argument);
    auto one=Protocol(1);one.schemaVersion=3;one.waveAssignment=p.waveAssignment;one.stimulusProfile=p.stimulusProfile;
    PreparedVerificationProbe context{one.routing,"i0",one.revision,"initial_model","reference_effective",0};
    auto extra=Observation(one,context,"capture","extra_dimension");ASSERT_TRUE(extra.valid);
    extra.specification.baseline.push_back(0.);
    EXPECT_THROW(CapturedReferences::Capture(one,{{context,extra}}),std::invalid_argument);
}

TEST(FinalVerification, AssignedPolicyBindsReferencesAndCertificateAndRejectsPolicyChanges)
{
    auto p=Protocol(2);p.schemaVersion=3;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    p.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    std::vector<ReferenceEvidence> evidence;
    for(std::size_t i=0;i<2;++i)
    {
        PreparedVerificationProbe ctx{p.routing,p.inputs[i].id,p.revision,"initial_model","reference_effective",0};
        auto o=FullClassicPair(p,ctx,"capture","ref"+std::to_string(i));ASSERT_TRUE(o.valid);
        evidence.push_back({ctx,o});
    }
    const auto refs=CapturedReferences::Capture(p,evidence);FinalVerificationSession session(refs,Configuration());
    while(auto r=session.NextRequest())
    {
        const auto ctx=Prepared(*r);session.Arm(ctx);
        session.Consume(FullClassicPair(p,ctx,r->runId,r->trialId),r->baseModelRevision);
    }
    ASSERT_TRUE(session.Certificate());EXPECT_TRUE(session.Certificate()->Exact());
    EXPECT_EQ(session.Certificate()->Protocol().peakSelection,PeakSelectionPolicy::AssignedBurstWave);
    auto changed=p;changed.peakSelection=PeakSelectionPolicy::IsolatedWindow;
    EXPECT_THROW(CapturedReferences::Capture(changed,evidence),std::invalid_argument);
    auto legacy=p;legacy.schemaVersion=2;legacy.waveAssignment=WaveAssignmentPolicy::WindowOnly;
    EXPECT_THROW(ValidateVerificationProtocol(legacy),std::invalid_argument);
    auto unknown=p;unknown.peakSelection=static_cast<PeakSelectionPolicy>(42);
    EXPECT_THROW(ValidateVerificationProtocol(unknown),std::invalid_argument);
}

TEST(FinalVerification, Schema3BranchRequiresActualSelectedInputBeforeArming)
{
    auto p=Protocol(1,ProbeRouting::BranchSoloBurst);p.schemaVersion=3;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    const auto refs=References(p);FinalVerificationSession valid(refs,Configuration());Complete(valid,p);
    ASSERT_EQ(valid.Status(),VerificationStatus::Exact);
    for(bool missing:{false,true})
    {
        FinalVerificationSession invalid(refs,Configuration());const auto r=invalid.NextRequest();ASSERT_TRUE(r);
        auto context=Prepared(*r);
        if(missing)context.selectedInputIndex.reset();else context.selectedInputIndex=1;
        invalid.Arm(context);EXPECT_EQ(invalid.Status(),VerificationStatus::InvalidObservation);
        EXPECT_FALSE(invalid.WaitingForObservation());EXPECT_FALSE(invalid.Certificate());
        ASSERT_EQ(invalid.Rejected().size(),1u);EXPECT_EQ(invalid.Rejected()[0].reason,"prepared_physical_input_mismatch");
    }
}

TEST(FinalVerification, UnknownOrChangedRuntimeContextInvalidatesPreviouslyVerifiedInputs)
{
    const auto p=Protocol(2);const auto refs=References(p);
    for(bool knownEdit:{false,true})
    {
        FinalVerificationSession session(refs,Configuration());auto first=session.NextRequest();auto prepared=Prepared(*first);
        session.Arm(prepared);session.Consume(Observation(p,prepared,first->runId,first->trialId),first->baseModelRevision);
        ASSERT_EQ(session.AcceptedInputs(),1u);
        auto second=session.NextRequest();prepared=Prepared(*second);session.Arm(prepared);
        auto data=Observation(p,prepared,second->runId,second->trialId);
        if(knownEdit){data.reasons={"model_revision_changed"};data.valid=false;}
        session.Consume(data,knownEdit?second->baseModelRevision:std::string{});
        EXPECT_EQ(session.AcceptedInputs(),0u);EXPECT_EQ(session.Status(),VerificationStatus::InvalidObservation);
        EXPECT_FALSE(session.Certificate());EXPECT_EQ(session.ModelEpoch(),1u);
    }
}
}
