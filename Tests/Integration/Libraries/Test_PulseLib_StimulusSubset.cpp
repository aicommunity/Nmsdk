#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StimulusSubset.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.h"
#include <limits>
#include <stdexcept>
#include <algorithm>
using namespace NMSDK::TimeLearner;

TEST(StimulusSubset, FullSelectionPreservesOriginalIntervals)
{
    const std::vector<double> source{.01,.08,.16,.24};
    const auto result=PlanStimulusSubset(source,{0,1,2,3});
    EXPECT_EQ(result.presentedIsi,source);EXPECT_EQ(result.sourceOffsets.size(),4u);
}
TEST(StimulusSubset, RemovingInteriorEventKeepsSourceOrdinals)
{
    const auto result=PlanStimulusSubset({.125,.125,.25,.5},{0,2,3});
    EXPECT_EQ(result.presentedIsi,(std::vector<double>{.125,.375,.5}));
    EXPECT_EQ(result.sourceOffsets,(std::vector<double>{.125,.5,1.}));
}
TEST(StimulusSubset, LaterSingleImpulseKeepsItsOriginalRequestedTime)
{
    const auto result=PlanStimulusSubset({.125,.125,.25,.5},{3});
    EXPECT_EQ(result.presentedIsi,(std::vector<double>{1.}));
    EXPECT_EQ(result.sourceOffsets,(std::vector<double>{1.}));
}
TEST(StimulusSubset, ZeroIntervalsArePreservedWithoutInventingEvents)
{
    const auto result=PlanStimulusSubset({0.,0.,.25},{0,1,2});
    EXPECT_EQ(result.presentedIsi,(std::vector<double>{0.,0.,.25}));
    // Native duplicate-time emission validity is a separate measured contract.
    EXPECT_EQ(result.sourceOffsets,(std::vector<double>{0.,0.,.25}));
}
TEST(StimulusSubset, RejectsEmptyAndInvalidOrdinals)
{
    EXPECT_THROW(PlanStimulusSubset({},{}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.},{}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.},{1}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.,2.},{1,0}),std::invalid_argument);
    EXPECT_THROW(PlanStimulusSubset({1.,2.},{0,0}),std::invalid_argument);
}
TEST(StimulusSubset, RejectsInvalidUnselectedSourceIntervals)
{
    for(double value:{-1.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
        EXPECT_THROW(PlanStimulusSubset({.1,value},{0}),std::invalid_argument);
}
TEST(StimulusSubset, RejectsOverflowEvenAfterLastSelectedEvent)
{
    const auto huge=std::numeric_limits<double>::max();
    EXPECT_THROW(PlanStimulusSubset({.1,huge,huge},{0}),std::invalid_argument);
}

namespace {
ProbeSpec SubsetSpec()
{
    ProbeSpec s;s.schemaVersion=6;s.runId="subset";s.trialId="subset/trial";s.sampleId="sample";
    s.patternHash="presented";s.modelRevision="model";s.end=4.;s.maximumSampleGap=1.;s.maximumSamples=5;
    s.baseline={0.,0.,0.,0.};s.expectedStimulusIds={"pulse0","pulse2"};
    s.stimulusProfile=StimulusProfile{"source",1.,1.,1.,0.,false,false};
    s.stimulusSubset=StimulusSubsetCharacterization{"original",4,{0,2}};return s;
}
ProbeObservation CompleteSubset()
{
    ProbeRecorder recorder(SubsetSpec());
    for(int t=0;t<=4;++t)recorder.Observe(t,{0.,1.,2.,3.},"model");
    recorder.RecordStimulus("pulse0",1.);recorder.RecordStimulus("pulse2",3.);
    return recorder.Close(4.,"model","window_closed");
}
}
TEST(StimulusSubsetObservation, CompleteWaveformDoesNotAssignPeaksOrClaimSpikes)
{
    const auto o=CompleteSubset();EXPECT_TRUE(o.complete);EXPECT_TRUE(o.valid);
    EXPECT_EQ(o.sampleCount,5u);EXPECT_EQ(o.stimuli.size(),2u);
    EXPECT_TRUE(o.peaks.empty());EXPECT_TRUE(o.burstAssignments.empty());EXPECT_TRUE(o.spikes.empty());
}
TEST(StimulusSubsetObservation, MissingRetainedEventIsInvalid)
{
    ProbeRecorder recorder(SubsetSpec());
    for(int t=0;t<=4;++t)recorder.Observe(t,{0.,0.,0.,0.},"model");
    recorder.RecordStimulus("pulse0",1.);const auto o=recorder.Close(4.,"model","window_closed");
    EXPECT_TRUE(o.complete);EXPECT_FALSE(o.valid);
    EXPECT_NE(std::find(o.reasons.begin(),o.reasons.end(),"missing_stimulus"),o.reasons.end());
}
TEST(StimulusSubsetObservation, MetadataCannotBeUsedInLegacyTrainingSchemas)
{
    for(unsigned version:{1u,2u,3u})
    {
        auto s=SubsetSpec();s.schemaVersion=version;
        s.windows={{"input0",0,0.,4.,"pulse0"},{"input2",2,0.,4.,"pulse2"}};
        if(version==1)s.stimulusProfile.reset();
        if(version==3)s.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
        const auto metadata=s.stimulusSubset;s.stimulusSubset.reset();
        EXPECT_NO_THROW((void)ProbeRecorder(s));
        s.stimulusSubset=metadata;EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
    }
    auto s=SubsetSpec();s.characterization=SinglePulseCharacterization{"original",4,0};
    EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
}
TEST(StimulusSubsetObservation, SourceOrdinalIdentityCannotBeRelabelled)
{
    auto s=SubsetSpec();s.expectedStimulusIds[1]="pulse1";EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
    s=SubsetSpec();s.stimulusSubset->sourceOrdinals={2,0};EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
    s=SubsetSpec();s.stimulusSubset->physicalInputCount=2;EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
}
TEST(StimulusSubsetObservation, PeakAndSpikeClaimsAreForbidden)
{
    auto s=SubsetSpec();s.windows={{"input0",0,0.,4.,"pulse0"}};EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
    s=SubsetSpec();s.recordSpikes=true;EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
    s=SubsetSpec();s.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
    s=SubsetSpec();s.peakSelection=PeakSelectionPolicy::SingleImpulseMaximum;EXPECT_THROW((void)ProbeRecorder(s),std::invalid_argument);
}
TEST(StimulusSubsetObservation, NonfiniteSampleCannotProduceACompleteDiagnostic)
{
    ProbeRecorder recorder(SubsetSpec());
    for(int t=0;t<=4;++t)recorder.Observe(t,{t==2?std::numeric_limits<double>::quiet_NaN():0.,0.,0.,0.},"model");
    recorder.RecordStimulus("pulse0",1.);recorder.RecordStimulus("pulse2",3.);
    const auto o=recorder.Close(4.,"model","window_closed");EXPECT_FALSE(o.complete);EXPECT_FALSE(o.valid);
}
TEST(StimulusSubsetObservation, RelabellingSchemaCannotLaunderATrainingCertificate)
{
    auto o=CompleteSubset();o.schemaVersion=2;o.specification.schemaVersion=2;
    VerificationProtocol p;p.schemaVersion=2;p.revision="protocol";p.sampleId="sample";p.patternHash="presented";
    p.originStimulusId="pulse0";p.inputs={{"input0","pulse0"},{"input2","pulse2"}};
    p.stimulusIds={"pulse0","pulse2"};p.maximumSampleGap=1.;p.stimulusProfile=o.specification.stimulusProfile;
    PreparedVerificationProbe context{ProbeRouting::ClassicBurst,"input0","protocol","base","model",0};
    ValidateVerificationProtocol(p);
    std::string reason;
    try{ValidateProbeMeasurement(p,0,context,o);}catch(const std::invalid_argument& error){reason=error.what();}
    EXPECT_EQ(reason,"diagnostic_probe_cannot_certify_training");
    auto second=context;second.inputId="input2";
    EXPECT_THROW(CapturedReferences::Capture(p,{{context,o},{second,o}}),std::invalid_argument);
}
