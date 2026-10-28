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

ProbeObservation ClockObservation(double origin,double step,bool omitFrame)
{
    auto s=Specification();s.begin=origin;s.end=origin+10.*step;s.maximumSampleGap=step;
    s.windows[0].begin=s.begin;s.windows[0].end=s.end;ProbeRecorder recorder(s);
    for(std::size_t i=0;i<onePeak.size();++i)
        if(!omitFrame || i!=7)recorder.Observe(origin+double(i)*step,{2.+onePeak[i]},"model_1");
    recorder.RecordStimulus("pulse",origin+step);
    return recorder.Close(s.end,"model_1","closed");
}
TEST(TimeLearnerClock,RecorderAbsoluteOriginsPreserveDeclaredSampling)
{
    for(double origin:{131.,1000000.})for(double step:{.0005,.00005})
    {
        SCOPED_TRACE(::testing::Message()<<"origin="<<origin<<" step="<<step);
        const auto o=ClockObservation(origin,step,false);
        EXPECT_TRUE(o.complete);EXPECT_TRUE(o.valid);EXPECT_FALSE(Has(o,"sample_gap"));
    }
}
TEST(TimeLearnerClock,RecorderAbsoluteOriginsStillRejectDroppedFrames)
{
    for(double origin:{131.,1000000.})for(double step:{.0005,.00005})
    {
        const auto o=ClockObservation(origin,step,true);
        EXPECT_FALSE(o.complete);EXPECT_FALSE(o.valid);EXPECT_TRUE(Has(o,"sample_gap"));
    }
}
TEST(TimeLearnerClock,UnresolvableTimestampScaleIsRejected)
{
    auto s=Specification();s.begin=1.e12;s.end=s.begin+1.;s.maximumSampleGap=.0005;
    s.windows[0].begin=s.begin;s.windows[0].end=s.end;
    EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
}

ProbeSpec BurstSpecification(unsigned schema=3)
{
    auto s=Specification();s.schemaVersion=schema;s.maximumSampleGap=.05;s.maximumSamples=21;
    s.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    s.expectedStimulusIds={"p0","p1"};s.windows={{"i1",0,.3,.55,"p1"}};
    if(schema==3)s.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    return s;
}
std::vector<double> TwoWaves()
{
    std::vector<double> v(21,0.);v[7]=.01;v[8]=.02;v[9]=.01;
    v[15]=.015;v[16]=.03;v[17]=.015;return v;
}
ProbeObservation BurstObservation(ProbeSpec s,std::vector<double> v=TwoWaves(),
    std::vector<StimulusObservation> events={{"p0",.1},{"p1",.3}})
{
    ProbeRecorder recorder(s);
    for(std::size_t i=0;i<v.size();++i)recorder.Observe(double(i)/20.,{2.+v[i]},"model_1");
    for(const auto& event:events)recorder.RecordStimulus(event.id,event.time);
    return recorder.Close(1.,"model_1","closed");
}
TEST(TimeLearnerBurstAssignment, HistoricalWindowOnlyCanMislabelAnEarlierDelayedWave)
{
    const auto old=BurstObservation(BurstSpecification(2));
    ASSERT_TRUE(old.valid);ASSERT_EQ(old.peaks.size(),1u);
    EXPECT_EQ(old.peaks[0].stimulusId,"p1");EXPECT_DOUBLE_EQ(*old.peaks[0].time,.4);
    // This constructed trace's p0 wave is at .4, p1 wave at .8. A window
    // label and positive delay alone do not establish the wave's origin.
    const auto current=BurstObservation(BurstSpecification());
    EXPECT_FALSE(current.valid);EXPECT_TRUE(current.complete);
    EXPECT_TRUE(Has(current,"burst_window_assignment_mismatch:i1"));
    EXPECT_EQ(current.peaks[0].validity,PeakValidity::Ambiguous);EXPECT_FALSE(current.peaks[0].time);
    ASSERT_EQ(current.burstAssignments.size(),1u);ASSERT_EQ(current.burstAssignments[0].waves.size(),2u);
    EXPECT_EQ(current.burstAssignments[0].waves[0].stimulusId,"p0");
    EXPECT_EQ(current.burstAssignments[0].waves[1].stimulusId,"p1");
}
TEST(TimeLearnerBurstAssignment, UsesMeasuredWholeSequenceWithCorrectWindow)
{
    auto s=BurstSpecification();s.windows[0].begin=.7;s.windows[0].end=.9;
    const auto o=BurstObservation(s);ASSERT_TRUE(o.valid);ASSERT_EQ(o.peaks.size(),1u);
    EXPECT_DOUBLE_EQ(*o.peaks[0].time,.8);EXPECT_DOUBLE_EQ(*o.peaks[0].rawPotential,2.03);
    EXPECT_DOUBLE_EQ(*o.peaks[0].delayFromStimulus,.8-.3);
}
TEST(TimeLearnerBurstAssignment, AssignedPolicySelectsTheActualLaterWaveInAWideWindow)
{
    auto s=BurstSpecification();s.windows[0].begin=0.;s.windows[0].end=1.;
    const auto isolated=BurstObservation(s);EXPECT_FALSE(isolated.valid);
    EXPECT_EQ(isolated.peaks[0].validity,PeakValidity::Ambiguous);
    s.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    const auto assigned=BurstObservation(s);ASSERT_TRUE(assigned.valid);
    EXPECT_EQ(assigned.peaks[0].candidateCount,1u);
    EXPECT_DOUBLE_EQ(*assigned.peaks[0].time,.8);
    EXPECT_DOUBLE_EQ(*assigned.peaks[0].delayFromStimulus,.8-.3);
    // The earlier wave at .4 is after p1's actual onset too. The full
    // measured sequence, not onset or a delay estimate, selects p1's wave.
    s.windows[0].stimulusId="p0";
    const auto first=BurstObservation(s);ASSERT_TRUE(first.valid);
    EXPECT_DOUBLE_EQ(*first.peaks[0].time,.4);
}
TEST(TimeLearnerBurstAssignment, AssignedPolicyRequiresSamplesAroundTheSelectedPlateau)
{
    auto s=BurstSpecification();s.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(const auto bounds:std::vector<std::pair<double,double>>{{.751,.9},{.7,.849},{0.,.6}})
    {
        s.windows[0].begin=bounds.first;s.windows[0].end=bounds.second;
        const auto o=BurstObservation(s);EXPECT_FALSE(o.valid);
        EXPECT_EQ(o.peaks[0].validity,PeakValidity::Clipped);EXPECT_FALSE(o.peaks[0].time);
    }
    s.windows[0].begin=.75;s.windows[0].end=.9;
    auto trace=TwoWaves();trace[17]=.03;trace[18]=.01;
    const auto plateau=BurstObservation(s,trace);ASSERT_TRUE(plateau.valid);
    EXPECT_DOUBLE_EQ(*plateau.peaks[0].time,.8);EXPECT_DOUBLE_EQ(*plateau.peaks[0].plateauEnd,.85);
}
TEST(TimeLearnerBurstAssignment, AssignedPolicyCannotFillMissingWavesOrChangeHistoricalSchemas)
{
    auto s=BurstSpecification();s.windows[0].begin=0.;s.windows[0].end=1.;
    s.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    auto missing=TwoWaves();missing[15]=missing[16]=missing[17]=0.;
    EXPECT_FALSE(BurstObservation(s,missing).valid);
    auto extra=TwoWaves();extra[2]=.01;EXPECT_FALSE(BurstObservation(s,extra).valid);
    s.schemaVersion=2;s.waveAssignment=WaveAssignmentPolicy::WindowOnly;
    EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s=BurstSpecification();s.peakSelection=static_cast<PeakSelectionPolicy>(123);
    EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
}
TEST(TimeLearnerBurstAssignment, MissingAndExtraWavesCannotBeRelabelled)
{
    auto missing=TwoWaves();missing[15]=missing[16]=missing[17]=0.;
    const auto m=BurstObservation(BurstSpecification(),missing);
    EXPECT_FALSE(m.valid);EXPECT_EQ(m.peaks[0].validity,PeakValidity::Missing);
    EXPECT_TRUE(Has(m,"burst_missing:0"));
    auto extra=TwoWaves();extra[2]=.01;
    const auto e=BurstObservation(BurstSpecification(),extra);
    EXPECT_FALSE(e.valid);EXPECT_EQ(e.peaks[0].validity,PeakValidity::Ambiguous);
    EXPECT_TRUE(Has(e,"burst_ambiguous:0"));
    for(const auto& w:e.burstAssignments[0].waves)EXPECT_TRUE(w.stimulusId.empty());
}
TEST(TimeLearnerBurstAssignment, BoundaryAndPlateauRemainMeasured)
{
    auto clipped=TwoWaves();clipped[15]=clipped[16]=clipped[17]=0.;
    clipped[18]=.01;clipped[19]=.02;clipped[20]=.03;
    const auto c=BurstObservation(BurstSpecification(),clipped);
    EXPECT_FALSE(c.valid);EXPECT_TRUE(Has(c,"burst_clipped:0"));
    auto s=BurstSpecification();s.windows[0].inputId="i0";s.windows[0].stimulusId="p0";
    auto plateau=TwoWaves();plateau[9]=.02;plateau[10]=.01;
    const auto p=BurstObservation(s,plateau);ASSERT_TRUE(p.valid);
    EXPECT_DOUBLE_EQ(*p.peaks[0].time,.4);EXPECT_DOUBLE_EQ(*p.peaks[0].plateauEnd,.45);
}
TEST(TimeLearnerBurstAssignment, SourceOrderAndSimultaneousEventsDoNotCreateAnAssignment)
{
    for(const auto& events:std::vector<std::vector<StimulusObservation>>{
        {{"p1",.1},{"p0",.3}},{{"p0",.1},{"p1",.1}}})
    {
        const auto o=BurstObservation(BurstSpecification(),TwoWaves(),events);
        EXPECT_FALSE(o.valid);EXPECT_TRUE(Has(o,"burst_ambiguous:0"));
    }
}
TEST(TimeLearnerBurstAssignment, ExplicitSchemaCannotRetroactivelyChangeHistoricalCriteria)
{
    auto s=BurstSpecification();s.schemaVersion=2;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s.schemaVersion=3;s.waveAssignment=WaveAssignmentPolicy::WindowOnly;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;s.stimulusProfile.reset();EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
}
TEST(TimeLearnerBurstAssignment, SamplesOutsideTheDeclaredBurstDoNotAddAResponseWave)
{
    auto s=BurstSpecification();s.begin=.2;s.windows[0].begin=.7;s.windows[0].end=.9;
    auto trace=TwoWaves();trace[2]=.01;
    const auto o=BurstObservation(s,trace,{{"p0",.3},{"p1",.5}});
    ASSERT_TRUE(o.valid);EXPECT_EQ(o.burstAssignments[0].waves.size(),2u);
}

TEST(TimeLearnerProbe, UsesExplicitRestStateAndMeasuredPlateauWithoutInterpolation)
{
    auto s=Specification();s.windows.clear();
    for(int i=0;i<6;++i)s.windows.push_back({"input"+std::to_string(i),0,0.,1.,"pulse"});
    ProbeRecorder recorder(s);Samples(recorder,onePeak);recorder.RecordStimulus("pulse",.1);
    const auto result=recorder.Close(1.,"model_1","window_closed");
    ASSERT_TRUE(result.valid);EXPECT_TRUE(result.complete);ASSERT_EQ(result.peaks.size(),6u);
    for(const auto& peak:result.peaks)
    {
        EXPECT_EQ(peak.validity,PeakValidity::Valid);
        ASSERT_TRUE(peak.amplitude);ASSERT_TRUE(peak.time);ASSERT_TRUE(peak.rawPotential);
        ASSERT_TRUE(peak.plateauEnd);ASSERT_TRUE(peak.delayFromStimulus);
        EXPECT_NEAR(*peak.amplitude,.02,1e-14);
        EXPECT_DOUBLE_EQ(*peak.rawPotential,2.02);EXPECT_DOUBLE_EQ(*peak.time,.4);
        EXPECT_DOUBLE_EQ(*peak.plateauEnd,.5);EXPECT_EQ(peak.candidateCount,1u);
        EXPECT_NEAR(*peak.delayFromStimulus,.3,1e-14);
    }
    EXPECT_FALSE(result.specification.recordSpikes); // Unknown spike response.
}

TEST(TimeLearnerProbe, NativeSchemaRequiresFiniteSourcePhysicsWithoutInventingLegacyEvidence)
{
    auto s=Specification();s.schemaVersion=2;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    ProbeRecorder recorder(s);Samples(recorder,onePeak);recorder.RecordStimulus("pulse",.1);
    const auto measured=recorder.Close(1.,"model_1","closed");
    ASSERT_TRUE(measured.valid);EXPECT_EQ(measured.schemaVersion,2u);
    EXPECT_EQ(measured.specification.stimulusProfile,s.stimulusProfile);
    s.stimulusProfile->amplitude=std::numeric_limits<double>::quiet_NaN();
    EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
    s.stimulusProfile->amplitude=1.;s.schemaVersion=1;
    EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
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
        EXPECT_FALSE(result.peaks[0].time);EXPECT_FALSE(result.peaks[0].amplitude);
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
        if(mode!=1)EXPECT_FALSE(result.peaks[0].delayFromStimulus);
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
    s=Specification();s.begin=-1e308;s.end=1e308;EXPECT_THROW(ProbeRecorder{s},std::invalid_argument);
}

TEST(TimeLearnerProbe, FiniteTimestampsCannotHideAnOverflowedInterval)
{
    ProbeRecorder recorder(Specification());recorder.Observe(-1e308,{2.},"model_1");
    recorder.Observe(1e308,{2.},"model_1");
    auto result=recorder.Close(1.,"model_1","closed");
    EXPECT_FALSE(result.valid);EXPECT_TRUE(Has(result,"nonfinite_sample_interval"));
}

TEST(TimeLearnerProbe, PeakBeforeActualStimulusCannotBecomeAnAcceptedDelay)
{
    ProbeRecorder recorder(Specification());Samples(recorder,onePeak);
    recorder.RecordStimulus("pulse",.6);auto result=recorder.Close(1.,"model_1","closed");
    EXPECT_TRUE(result.complete);EXPECT_FALSE(result.valid);
    EXPECT_TRUE(Has(result,"peak_precedes_stimulus:input"));
    ASSERT_TRUE(result.peaks[0].delayFromStimulus);EXPECT_LT(*result.peaks[0].delayFromStimulus,0.);
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
