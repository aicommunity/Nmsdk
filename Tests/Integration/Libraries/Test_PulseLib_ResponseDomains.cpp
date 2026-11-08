#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ResponseDomainAssociation.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.h"
#include <algorithm>
#include <limits>
#include <type_traits>

namespace {
using namespace NMSDK::TimeLearner;
using Status=DomainAssociationStatus;
ResponseDomainObservation Observation()
{
    ResponseDomainObservation o;o.modelRevision="model";o.protocolRevision="protocol";
    o.runId="run";o.trialId="trial";o.sampleId="sample";o.patternHash="pattern";
    o.begin=0.;o.end=1.;o.maximumSampleGap=.1;o.minimumAmplitude=.5;o.complete=true;
    o.events={{"p0",.1},{"p1",.5}};
    ResponseDomainChannel c;c.channel=0;c.baseline=2.;
    const std::vector<double> values{2.,2.,3.,5.,3.,2.,3.,6.,3.,2.,2.};
    for(std::size_t i=0;i<values.size();++i)c.samples.push_back({double(i)/10.,values[i]});
    o.channels.push_back(c);return o;
}
ResponseDomainSpec Specification()
{
    ResponseDomainSpec s;s.modelRevision="model";s.protocolRevision="protocol";
    s.patternHash="pattern";
    s.stimulusIds={"p0","p1"};s.channelIds={0};s.domains={{0,"p0",.1,.5},{0,"p1",.5,.9}};return s;
}
TEST(ResponseDomains,LocalMaximumDoesNotBecomeTheHigherFullBurstMaximum)
{
    const auto r=AnalyzeDeclaredResponseDomains(Specification(),Observation());
    ASSERT_EQ(r.associations.size(),2u);ASSERT_EQ(r.channels[0].features.positiveMaxima.size(),2u);
    EXPECT_EQ(r.associations[0].status,Status::Hypothesis);EXPECT_EQ(r.associations[1].status,Status::Hypothesis);
    ASSERT_TRUE(r.associations[0].selectedMaximum);ASSERT_TRUE(r.associations[1].selectedMaximum);
    EXPECT_DOUBLE_EQ(r.channels[0].features.positiveMaxima[*r.associations[0].selectedMaximum].time,.3);
    EXPECT_DOUBLE_EQ(r.channels[0].features.positiveMaxima[*r.associations[1].selectedMaximum].time,.7);
    EXPECT_DOUBLE_EQ(r.channels[0].features.globalMaximum->time,.7);
    EXPECT_FALSE(r.TrainingCertificateEligible());
}
TEST(ResponseDomains,SmallerExtremaDoNotInvalidateTheUniqueLargestHypothesis)
{
    auto s=Specification();s.domains[0].begin=0.;auto o=Observation();
    o.channels[0].samples[1].rawPotential=3.;o.channels[0].samples[2].rawPotential=2.;
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    EXPECT_EQ(r.associations[0].status,Status::Hypothesis);EXPECT_EQ(r.associations[0].candidateMaxima.size(),2u);
    ASSERT_TRUE(r.associations[0].selectedMaximum);
    EXPECT_EQ(*r.associations[0].selectedMaximum,1u);
}
TEST(ResponseDomains,SeparatedEqualMaximaLeaveTimeAmbiguous)
{
    auto s=Specification();s.domains[0].begin=0.;auto o=Observation();
    o.channels[0].samples[1].rawPotential=5.;o.channels[0].samples[2].rawPotential=2.;
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    EXPECT_EQ(r.associations[0].status,Status::Ambiguous);EXPECT_FALSE(r.associations[0].selectedMaximum);
    EXPECT_EQ(r.associations[0].reason,"separated_largest_maxima_tie");
}
TEST(ResponseDomains,ContinuousPlateauRetainsMeasuredSampleEndpoints)
{
    auto o=Observation();o.channels[0].samples[2].rawPotential=5.;
    const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
    ASSERT_EQ(r.associations[0].status,Status::Hypothesis);
    const auto& p=r.channels[0].features.positiveMaxima[*r.associations[0].selectedMaximum];
    EXPECT_EQ(p.firstSample,2u);EXPECT_EQ(p.lastSample,3u);
    EXPECT_DOUBLE_EQ(p.time,.2);EXPECT_DOUBLE_EQ(p.plateauEnd,.3);
}
TEST(ResponseDomains,OneVertexCannotBeSelectedForTwoCompetingStimuli)
{
    auto s=Specification();s.domains[0].end=.9;s.domains[1].begin=.2;
    const auto r=AnalyzeDeclaredResponseDomains(s,Observation());
    for(const auto& a:r.associations){EXPECT_EQ(a.status,Status::Ambiguous);EXPECT_FALSE(a.selectedMaximum);}
    EXPECT_EQ(r.associations[0].competingStimulusIds,(std::vector<std::string>{"p1"}));
    EXPECT_EQ(r.associations[1].competingStimulusIds,(std::vector<std::string>{"p0"}));
}
TEST(ResponseDomains,PartiallyIntersectingPlateauStillHasACompetitor)
{
    auto s=Specification();s.domains[1].begin=.4;auto o=Observation();o.events[1].time=.2;
    o.channels[0].samples[4].rawPotential=5.;
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    EXPECT_EQ(r.associations[0].status,Status::Ambiguous);
    EXPECT_EQ(r.associations[0].competingStimulusIds,(std::vector<std::string>{"p1"}));
}
TEST(ResponseDomains,UnrelatedAbsentResponseDoesNotInvalidateLocalHypothesis)
{
    auto o=Observation();for(std::size_t i=6;i<=8;++i)o.channels[0].samples[i].rawPotential=2.;
    const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
    EXPECT_EQ(r.associations[0].status,Status::Hypothesis);EXPECT_EQ(r.associations[1].status,Status::NoCandidate);
    EXPECT_FALSE(r.TrainingCertificateEligible());
}
TEST(ResponseDomains,StimulusDuringPlateauRemainsACompetitor)
{
    for(double onset:{.35,.4,.45})
    {
        auto s=Specification();s.domains[1].begin=.35;auto o=Observation();o.events[1].time=onset;
        o.channels[0].samples[4].rawPotential=5.;
        const auto r=AnalyzeDeclaredResponseDomains(s,o);
        EXPECT_EQ(r.associations[0].status,onset<=.4?Status::Ambiguous:Status::Hypothesis);
    }
}
TEST(ResponseDomains,CompetitorDomainBeforeItsOwnOnsetCannotClaimAPlateau)
{
    auto s=Specification();s.domains[1]={0,"p1",.2,.34};auto o=Observation();o.events[1].time=.35;
    o.channels[0].samples[4].rawPotential=5.;
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(s,o).associations[0].status,Status::Hypothesis);
}
TEST(ResponseDomains,EveryCompetingPairMustBeDeclared)
{
    auto s=Specification();s.domains.pop_back();
    const auto r=AnalyzeDeclaredResponseDomains(s,Observation());
    EXPECT_EQ(r.associations[0].status,Status::InvalidSpecification);
    EXPECT_EQ(r.reasons,(std::vector<std::string>{"missing_competing_response_domain"}));
    EXPECT_EQ(r.channels[0].features.positiveMaxima.size(),2u);
}
TEST(ResponseDomains,DuplicateAndUnknownDomainPairsAreRejected)
{
    auto s=Specification();s.domains.push_back(s.domains[0]);
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(s,Observation()).associations[0].status,Status::InvalidSpecification);
    s=Specification();s.domains[1].stimulusId="foreign";
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(s,Observation()).associations[0].status,Status::InvalidSpecification);
}
TEST(ResponseDomains,RevisionMismatchPreservesFeaturesButRejectsApplicability)
{
    for(bool model:{true,false})
    {
        auto o=Observation();if(model)o.modelRevision="changed";else o.protocolRevision="changed";
        const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
        EXPECT_EQ(r.associations[0].status,Status::OutsideApplicability);
        EXPECT_EQ(r.channels[0].features.positiveMaxima.size(),2u);EXPECT_FALSE(r.associations[0].selectedMaximum);
    }
}
TEST(ResponseDomains,IncompleteAndDroppedFramesCannotYieldHypotheses)
{
    auto o=Observation();o.complete=false;
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(Specification(),o).associations[0].status,Status::Incomplete);
    o=Observation();o.channels[0].samples.erase(o.channels[0].samples.begin()+5);
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(Specification(),o).associations[0].status,Status::Incomplete);
}
TEST(ResponseDomains,NonfiniteAndNonmonotonicSamplesAreExplicit)
{
    for(bool time:{true,false})
    {
        auto o=Observation();
        if(time)o.channels[0].samples.back().time=o.channels[0].samples.front().time;
        else o.channels[0].samples.back().rawPotential=std::numeric_limits<double>::quiet_NaN();
        const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
        EXPECT_EQ(r.associations[0].status,Status::InvalidSamples);EXPECT_FALSE(r.associations[0].selectedMaximum);
    }
}
TEST(ResponseDomains,MaximumBeforeItsActualStimulusIsNotAssigned)
{
    auto o=Observation();o.events[0].time=.4;
    const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
    EXPECT_EQ(r.associations[0].status,Status::OutsideApplicability);
    EXPECT_EQ(r.associations[0].reason,"maximum_precedes_actual_stimulus");
    ASSERT_TRUE(r.associations[0].largestMeasuredMaximum);
    ASSERT_TRUE(r.associations[0].maximumOffsetLow);
    EXPECT_DOUBLE_EQ(*r.associations[0].maximumOffsetLow,.3-.4);
    EXPECT_DOUBLE_EQ(*r.associations[0].maximumOffsetHigh,.3-.4);
    EXPECT_FALSE(r.associations[0].selectedMaximum);
}
TEST(ResponseDomains,DomainBoundaryCannotTurnARisingEdgeIntoAMaximum)
{
    auto s=Specification();s.domains[0].end=.3;
    const auto r=AnalyzeDeclaredResponseDomains(s,Observation());
    EXPECT_EQ(r.associations[0].status,Status::Clipped);EXPECT_FALSE(r.associations[0].selectedMaximum);
}
TEST(ResponseDomains,EqualTimesOnDifferentPhysicalChannelsRemainIndependent)
{
    auto s=Specification();auto o=Observation();o.events[1].time=.2;
    o.channels.push_back(o.channels[0]);o.channels[1].channel=7;s.channelIds.push_back(7);
    s.domains[0]={0,"p0",.1,.5};s.domains[1]={0,"p1",.5,.9};
    s.domains.push_back({7,"p0",.5,.9});s.domains.push_back({7,"p1",.1,.5});
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    ASSERT_EQ(r.associations[0].status,Status::Hypothesis);ASSERT_EQ(r.associations[3].status,Status::Hypothesis);
    EXPECT_DOUBLE_EQ(r.channels[0].features.positiveMaxima[*r.associations[0].selectedMaximum].time,
                     r.channels[1].features.positiveMaxima[*r.associations[3].selectedMaximum].time);
}
TEST(ResponseDomains,WindowOnlyCounterexampleCannotBecomeTrainingEvidence)
{
    // A delayed p0 response at .3 can fall after p1 onset and inside p1's
    // incorrectly declared domain. Exclusivity is a hypothesis, not origin.
    auto s=Specification();s.domains={{0,"p0",0.,.2},{0,"p1",.2,.5}};
    auto o=Observation();o.events[1].time=.2;
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    EXPECT_EQ(r.associations[1].status,Status::Hypothesis);EXPECT_FALSE(r.TrainingCertificateEligible());
    static_assert(!std::is_convertible_v<ResponseDomainResult,ProbeObservation>);
    static_assert(!std::is_convertible_v<ResponseDomainResult,CapturedReferences>);
}
TEST(ResponseDomains,PermutationOfDomainsPreservesTheirResults)
{
    auto s=Specification();const auto before=AnalyzeDeclaredResponseDomains(s,Observation());
    std::reverse(s.domains.begin(),s.domains.end());const auto after=AnalyzeDeclaredResponseDomains(s,Observation());
    for(std::size_t i=0;i<2;++i)
    {
        EXPECT_EQ(before.associations[i].stimulusId,after.associations[1-i].stimulusId);
        EXPECT_EQ(before.associations[i].status,after.associations[1-i].status);
        EXPECT_EQ(before.associations[i].selectedMaximum,after.associations[1-i].selectedMaximum);
    }
}
TEST(ResponseDomains,AbsoluteClockOriginsPreserveTheAssociationGraph)
{
    for(double origin:{131.,1000000.})for(double step:{.0005,.00005})
    {
        auto o=Observation();auto s=Specification();o.begin=origin;o.end=origin+10.*step;o.maximumSampleGap=step;
        for(auto& event:o.events)event.time=origin+event.time*10.*step;
        for(auto& sample:o.channels[0].samples)sample.time=origin+sample.time*10.*step;
        for(auto& domain:s.domains){domain.begin=origin+domain.begin*10.*step;domain.end=origin+domain.end*10.*step;}
        const auto r=AnalyzeDeclaredResponseDomains(s,o);
        EXPECT_EQ(r.associations[0].status,Status::Hypothesis);EXPECT_EQ(r.associations[1].status,Status::Hypothesis);
    }
}
TEST(ResponseDomains,GuardSamplesPreserveOriginalIndexBinding)
{
    auto o=Observation();auto& samples=o.channels[0].samples;
    samples.insert(samples.begin(),{{-.2,2.},{-.1,2.}});
    samples.push_back({1.1,2.});samples.push_back({1.2,2.});
    const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
    ASSERT_EQ(r.associations[0].status,Status::Hypothesis);EXPECT_EQ(r.channels[0].firstSourceSample,2u);
    EXPECT_EQ(r.channels[0].features.positiveMaxima[*r.associations[0].selectedMaximum].firstSample,3u);
}
TEST(ResponseDomains,ChannelIdsDoNotDependOnObservationVectorOrder)
{
    auto s=Specification();auto o=Observation();
    o.channels.push_back(o.channels[0]);o.channels[1].channel=19;
    s.channelIds.push_back(19);s.domains.push_back({19,"p0",.1,.5});s.domains.push_back({19,"p1",.5,.9});
    std::reverse(o.channels.begin(),o.channels.end());
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    for(const auto& a:r.associations)EXPECT_EQ(a.status,Status::Hypothesis);
    EXPECT_EQ(r.channels[0].channel,19u);EXPECT_EQ(r.channels[1].channel,0u);
}
TEST(ResponseDomains,InvalidChannelCannotLeaveOtherAssociationsUsable)
{
    auto s=Specification();auto o=Observation();
    o.channels.push_back(o.channels[0]);o.channels[1].channel=19;
    o.channels[1].samples.back().rawPotential=std::numeric_limits<double>::quiet_NaN();
    s.channelIds.push_back(19);s.domains.push_back({19,"p0",.1,.5});s.domains.push_back({19,"p1",.5,.9});
    const auto r=AnalyzeDeclaredResponseDomains(s,o);
    for(const auto& a:r.associations){EXPECT_EQ(a.status,Status::InvalidSamples);EXPECT_FALSE(a.selectedMaximum);}
    EXPECT_EQ(r.channels[0].features.positiveMaxima.size(),2u);
}
TEST(ResponseDomains,UnknownSchemaAndMalformedInventoriesAreRejected)
{
    auto s=Specification();s.schemaVersion=2;
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(s,Observation()).associations[0].status,Status::InvalidSpecification);
    s=Specification();s.domains[0].begin=std::numeric_limits<double>::quiet_NaN();
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(s,Observation()).associations[0].status,Status::InvalidSpecification);
    auto o=Observation();o.events.pop_back();
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(Specification(),o).associations[0].status,Status::InvalidSpecification);
    o=Observation();o.maximumSampleGap=0.;
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(Specification(),o).associations[0].status,Status::InvalidSpecification);
}
TEST(ResponseDomains,PatternChangesAndMissingProvenanceCannotProduceHypotheses)
{
    auto o=Observation();o.patternHash="different_pattern";
    const auto r=AnalyzeDeclaredResponseDomains(Specification(),o);
    EXPECT_EQ(r.associations[0].status,Status::OutsideApplicability);
    EXPECT_EQ(r.runId,o.runId);EXPECT_EQ(r.trialId,o.trialId);EXPECT_EQ(r.sampleId,o.sampleId);
    EXPECT_EQ(r.patternHash,o.patternHash);EXPECT_EQ(r.modelRevision,o.modelRevision);
    o=Observation();o.trialId.clear();
    EXPECT_EQ(AnalyzeDeclaredResponseDomains(Specification(),o).associations[0].status,Status::InvalidSpecification);
}
TEST(ResponseDomains,InputDimensionHasNoFourImpulseLimit)
{
    for(std::size_t n:{1u,2u,4u,6u})
    {
        ResponseDomainObservation o;o.modelRevision="model";o.protocolRevision="protocol";
        o.runId="run";o.trialId="trial";o.sampleId="sample";o.patternHash="pattern";
        o.begin=0.;o.end=double(n*20+20)*.01;o.maximumSampleGap=.01;o.minimumAmplitude=.5;o.complete=true;
        ResponseDomainSpec s;s.modelRevision=o.modelRevision;s.protocolRevision=o.protocolRevision;s.patternHash=o.patternHash;s.channelIds={19};
        ResponseDomainChannel channel;channel.channel=19;channel.baseline=2.;
        for(std::size_t i=0;i<=n*20+20;++i)channel.samples.push_back({double(i)*.01,2.});
        for(std::size_t i=0;i<n;++i)
        {
            const auto id="p"+std::to_string(i);o.events.push_back({id,double(i)*.2+.05});s.stimulusIds.push_back(id);
            s.domains.push_back({19,id,double(i)*.2,double(i+1)*.2});
            channel.samples[i*20+10].rawPotential=3.+double(i);
        }
        o.channels.push_back(std::move(channel));const auto r=AnalyzeDeclaredResponseDomains(s,o);
        ASSERT_EQ(r.associations.size(),n);
        for(const auto& a:r.associations)EXPECT_EQ(a.status,Status::Hypothesis);
        EXPECT_FALSE(r.TrainingCertificateEligible());
    }
}
}
