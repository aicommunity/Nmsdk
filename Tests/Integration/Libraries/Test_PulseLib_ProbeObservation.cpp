#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.h"
#include <algorithm>
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
ProbeSpec Specification()
{
    ProbeSpec s;s.runId="run";s.trialId="trial";s.sampleId="target";
    s.patternHash="fixture_pattern";s.modelRevision="model_1";
    s.begin=0.;s.end=1.;s.maximumSampleGap=.1;s.maximumSamples=11;
    s.baseline={2.};s.windows={{"input",0,0.,1.,"pulse"}};s.expectedStimulusIds={"pulse"};
    return s;
}
void Samples(ProbeRecorder& recorder,const std::vector<double>& deviations,
             const std::string& revision="model_1")
{
    for(std::size_t i=0;i<deviations.size();++i)
        recorder.Observe(double(i)/10.,{2.+deviations[i]},revision);
}
bool Has(const ProbeObservation& o,const std::string& reason)
{ return std::find(o.reasons.begin(),o.reasons.end(),reason)!=o.reasons.end(); }
const std::vector<double> onePeak{0.,0.,0.,.01,.02,.02,.01,0.,0.,0.,0.};

TEST(TimeLearnerProbe, UsesExplicitRestStateAndMeasuredPlateauWithoutInterpolation)
{
    auto s=Specification();s.windows.clear();
    for(int i=0;i<6;++i)s.windows.push_back({"input"+std::to_string(i),0,0.,1.,"pulse"});
    ProbeRecorder recorder(s);Samples(recorder,onePeak);recorder.RecordStimulus("pulse",.1);
    const auto result=recorder.Close(1.,"model_1","window_closed");
    ASSERT_TRUE(result.valid);EXPECT_TRUE(result.complete);ASSERT_EQ(result.peaks.size(),6u);
    for(const auto& peak:result.peaks)
    {
        EXPECT_EQ(peak.validity,PeakValidity::Valid);EXPECT_NEAR(peak.amplitude,.02,1e-14);
        EXPECT_DOUBLE_EQ(peak.rawPotential,2.02);EXPECT_DOUBLE_EQ(peak.time,.4);
        EXPECT_DOUBLE_EQ(peak.plateauEnd,.5);EXPECT_EQ(peak.candidateCount,1u);
        EXPECT_NEAR(peak.delayFromStimulus,.3,1e-14);
    }
    EXPECT_FALSE(result.specification.recordSpikes); // Unknown spike response.
}

TEST(TimeLearnerProbe, DistinguishesMissingAmbiguousAndClippedPeaks)
{
    const std::vector<std::pair<std::vector<double>,PeakValidity>> cases{
        {{0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.},PeakValidity::Missing},
        {{0.,.01,0.,0.,0.,.02,0.,0.,0.,0.,0.},PeakValidity::Ambiguous},
        {{0.,0.,0.,0.,0.,0.,0.,0.,.01,.02,.03},PeakValidity::Clipped}};
    for(const auto& test:cases)
    {
        ProbeRecorder recorder(Specification());Samples(recorder,test.first);
        recorder.RecordStimulus("pulse",.1);auto result=recorder.Close(1.,"model_1","closed");
        EXPECT_TRUE(result.complete);EXPECT_FALSE(result.valid);
        ASSERT_EQ(result.peaks.size(),1u);EXPECT_EQ(result.peaks[0].validity,test.second);
    }
}

TEST(TimeLearnerProbe, EarlyCloseAndSampleGapNeverCreateCompleteObservation)
{
    ProbeRecorder early(Specification());Samples(early,{0.,0.,0.,.01,.02,.01});
    early.RecordStimulus("pulse",.1);auto result=early.Close(.5,"model_1","timeout");
    EXPECT_FALSE(result.valid);EXPECT_FALSE(result.complete);EXPECT_TRUE(Has(result,"incomplete_observation"));
    ProbeRecorder gap(Specification());gap.Observe(0.,{2.},"model_1");gap.Observe(1.,{2.},"model_1");
    gap.RecordStimulus("pulse",.1);result=gap.Close(1.,"model_1","closed");
    EXPECT_FALSE(result.complete);EXPECT_TRUE(Has(result,"sample_gap"));
}

TEST(TimeLearnerProbe, RejectsNonfiniteSamplesIncludingDeviationOverflow)
{
    for(double bad:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
    {
        ProbeRecorder recorder(Specification());recorder.Observe(0.,{bad},"model_1");
        Samples(recorder,onePeak);recorder.RecordStimulus("pulse",.1);
        auto result=recorder.Close(1.,"model_1","closed");
        EXPECT_FALSE(result.valid);EXPECT_TRUE(Has(result,"nonfinite_sample"));
    }
    auto s=Specification();s.baseline={-1e308};ProbeRecorder recorder(s);
    recorder.Observe(0.,{1e308},"model_1");
    EXPECT_TRUE(Has(recorder.Close(1.,"model_1","closed"),"nonfinite_sample"));
}

TEST(TimeLearnerProbe, RevisionChangePersistsEvenIfOriginalModelIsRestored)
{
    ProbeRecorder recorder(Specification());Samples(recorder,onePeak,"model_2");
    recorder.RecordStimulus("pulse",.1);auto result=recorder.Close(1.,"model_1","closed");
    EXPECT_TRUE(result.complete);EXPECT_FALSE(result.valid);EXPECT_TRUE(Has(result,"model_revision_changed"));
}

TEST(TimeLearnerProbe, StimulusCompletenessAndUniqueIdsAreRequired)
{
    for(int mode=0;mode<3;++mode)
    {
        ProbeRecorder recorder(Specification());Samples(recorder,onePeak);
        if(mode==1){recorder.RecordStimulus("pulse",.1);recorder.RecordStimulus("pulse",.2);}
        if(mode==2)recorder.RecordStimulus("unknown",.1);
        auto result=recorder.Close(1.,"model_1","closed");EXPECT_FALSE(result.valid);
        EXPECT_TRUE(Has(result,mode==1?"duplicate_stimulus_id":"missing_stimulus"));
    }
}

TEST(TimeLearnerProbe, SampleBudgetAndOrderingAreExplicitFailures)
{
    auto s=Specification();s.maximumSamples=3;ProbeRecorder limited(s);Samples(limited,onePeak);
    EXPECT_TRUE(Has(limited.Close(1.,"model_1","closed"),"sample_budget_exhausted"));
    ProbeRecorder duplicate(Specification());duplicate.Observe(0.,{2.},"model_1");duplicate.Observe(0.,{2.},"model_1");
    EXPECT_TRUE(Has(duplicate.Close(1.,"model_1","closed"),"nonmonotonic_sample_time"));
}

TEST(TimeLearnerProbe, SpikeTimesAreExplicitAndDuplicateSpikeInvalidatesObservation)
{
    auto s=Specification();s.recordSpikes=true;ProbeRecorder recorder(s);Samples(recorder,onePeak);
    recorder.RecordStimulus("pulse",.1);recorder.RecordSpike(0,.4);
    auto result=recorder.Close(1.,"model_1","closed");ASSERT_TRUE(result.valid);
    ASSERT_EQ(result.spikes.size(),1u);EXPECT_DOUBLE_EQ(result.spikes[0].time,.4);
    ProbeRecorder duplicate(s);Samples(duplicate,onePeak);duplicate.RecordStimulus("pulse",.1);
    duplicate.RecordSpike(0,.4);duplicate.RecordSpike(0,.4);
    EXPECT_TRUE(Has(duplicate.Close(1.,"model_1","closed"),"duplicate_spike"));
}

TEST(TimeLearnerProbe, RejectsUnknownSchemaAndInvalidWindowOrDimensions)
{
    auto s=Specification();s.schemaVersion=2;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s=Specification();s.windows[0].channel=1;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s=Specification();s.windows[0].end=2.;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s=Specification();s.expectedStimulusIds={"pulse","pulse"};EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s=Specification();s.modelRevision.clear();EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
}

TEST(TimeLearnerProbe, PeakBeforeActualStimulusCannotBecomeAnAcceptedDelay)
{
    ProbeRecorder recorder(Specification());Samples(recorder,onePeak);
    recorder.RecordStimulus("pulse",.6);auto result=recorder.Close(1.,"model_1","closed");
    EXPECT_TRUE(result.complete);EXPECT_FALSE(result.valid);
    EXPECT_TRUE(Has(result,"peak_precedes_stimulus:input"));
    EXPECT_LT(result.peaks[0].delayFromStimulus,0.);
}

TEST(TimeLearnerProbe, LateSpikeIsRetainedAndDisabledCaptureIsNotASilentResponse)
{
    auto s=Specification();s.recordSpikes=true;ProbeRecorder enabled(s);Samples(enabled,onePeak);
    enabled.RecordStimulus("pulse",.1);enabled.RecordSpike(0,.9);
    const auto observed=enabled.Close(1.,"model_1","closed");ASSERT_TRUE(observed.valid);
    ASSERT_EQ(observed.spikes.size(),1u);EXPECT_DOUBLE_EQ(observed.spikes[0].time,.9);
    s.recordSpikes=false;ProbeRecorder disabled(s);Samples(disabled,onePeak);
    disabled.RecordStimulus("pulse",.1);disabled.RecordSpike(0,.9);
    EXPECT_TRUE(Has(disabled.Close(1.,"model_1","closed"),"unexpected_spike_channel"));
}

TEST(TimeLearnerProbe, RejectsWrongSampleDimensionAndWritesAfterClosure)
{
    ProbeRecorder recorder(Specification());recorder.Observe(0.,{2.,2.},"model_1");
    Samples(recorder,onePeak);recorder.RecordStimulus("pulse",.1);
    const auto result=recorder.Close(1.,"model_1","closed");
    EXPECT_FALSE(result.valid);EXPECT_TRUE(Has(result,"invalid_sample"));
    EXPECT_THROW(recorder.Observe(2.,{2.},"model_1"),std::logic_error);
    EXPECT_THROW(recorder.Close(2.,"model_1","closed"),std::logic_error);
}
}
