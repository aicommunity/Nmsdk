#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/MatchedOmissionAssignment.h"
#include <algorithm>
#include <functional>
#include <limits>

namespace {
using namespace NMSDK::TimeLearner;
using Validity=MatchedOmissionValidity;

struct Fixture {
    MatchedOmissionSpecification specification;
    MatchedOmissionPolicy policy;
    MatchedOmissionWitness witness;
    const std::vector<double> full{2.,2.,3.,5.,3.,2.,3.,6.,3.,2.,2.};
    const std::vector<double> omit0{2.,2.,2.,2.,2.,2.,3.,6.,3.,2.,2.};
    const std::vector<double> omit1{2.,2.,3.,5.,3.,2.,2.,2.,2.,2.,2.};

    Fixture() {
        auto& s=specification;
        s.runId="run";s.groupId="measurement0";s.sampleId="target";s.protocolRevision="omission-protocol1";
        s.patternHash="full-pattern";s.inputId="input0";s.baseModelRevision="base";s.effectiveModelRevision="effective";
        s.resetBinding="native-reset-v1";s.modelInstanceBinding="instance0";s.modelEpoch=4;
        s.stimulusIds={"p0","p1"};s.physicalChannelPaths={"Soma1","Soma2"};
        s.stimulusProfile={"NPulseGeneratorTransit",1.,.1,10.,0.,false,false};
        s.duration=1.;s.minimumAmplitude=.5;
        policy.maximumSamples=11;policy.maximumTotalSamples=44;policy.maximumNativeProbes=4;
        policy.timeComparisonTolerance=1e-12;policy.influenceAbsolute=.25;
        witness.fullBefore=Trace("full-before",{0,1},0.,full);
        witness.omitEachInput={Trace("omit0",{1},1.,omit0),Trace("omit1",{0},2.,omit1)};
        witness.fullAfter=Trace("full-after",{0,1},3.,full);
    }
    MatchedOmissionTrace Trace(const std::string& trial,std::vector<std::size_t> mask,
                              double origin,const std::vector<double>& values) const {
        const auto& s=specification;MatchedOmissionTrace t;
        t.groupId=s.groupId;t.sourcePatternHash=s.patternHash;t.resetBinding=s.resetBinding;
        t.modelInstanceBinding=s.modelInstanceBinding;t.currentBaseRevision=s.baseModelRevision;
        t.prepared={s.routing,s.inputId,s.protocolRevision,s.baseModelRevision,s.effectiveModelRevision,s.modelEpoch};
        t.physicalChannelPaths=s.physicalChannelPaths;t.presentedOrdinals=std::move(mask);t.stimulusProfile=s.stimulusProfile;
        t.nativeCompleted=true;t.fullMaskRestored=true;
        auto& o=t.observation;o.runId=s.runId;o.trialId=trial;o.sampleId=s.sampleId;
        o.patternHash=t.presentedOrdinals.size()==s.stimulusIds.size()?s.patternHash:trial+"-pattern";
        o.modelRevision=s.effectiveModelRevision;o.protocolRevision=s.protocolRevision;
        o.begin=origin;o.end=origin+s.duration;o.maximumSampleGap=.1;o.minimumAmplitude=s.minimumAmplitude;o.complete=true;
        for(std::size_t channel=0;channel<s.physicalChannelPaths.size();++channel) {
            ResponseDomainChannel c;c.channel=channel;c.baseline=2.;
            for(std::size_t i=0;i<values.size();++i)c.samples.push_back({origin+double(i)/10.,channel==0?values[i]:2.});
            o.channels.push_back(std::move(c));
        }
        t.stimulusSamples.assign(values.size(),0.);
        for(const auto ordinal:t.presentedOrdinals) {
            const auto frame=ordinal==0?1u:5u;
            o.events.push_back({s.stimulusIds[ordinal],o.channels[0].samples[frame].time});
            t.stimulusSamples[frame]=s.stimulusProfile.amplitude;
        }
        return t;
    }
    std::vector<MatchedOmissionTrace*> Traces() {
        std::vector<MatchedOmissionTrace*> traces{&witness.fullBefore,&witness.fullAfter};
        for(auto& t:witness.omitEachInput)traces.push_back(&t);return traces;
    }
    void Values(MatchedOmissionTrace& t,const std::vector<double>& values) {
        for(std::size_t i=0;i<values.size();++i)t.observation.channels[specification.channel].samples[i].rawPotential=values[i];
    }
    void Responses(const std::vector<double>& f,const std::vector<double>& o0,const std::vector<double>& o1) {
        Values(witness.fullBefore,f);Values(witness.fullAfter,f);
        Values(witness.omitEachInput[0],o0);Values(witness.omitEachInput[1],o1);
    }
    void Assigned(std::size_t input) {
        specification.assignedInput=input;specification.channel=input;specification.inputId="input"+std::to_string(input);
        for(auto* t:Traces()) {
            t->prepared.inputId=specification.inputId;
            if(input)for(std::size_t i=0;i<t->observation.channels[0].samples.size();++i)
                t->observation.channels[input].samples[i].rawPotential=t->observation.channels[0].samples[i].rawPotential;
        }
    }
    void EventFrames(std::size_t p0,std::size_t p1) {
        for(auto* t:Traces()) {
            t->observation.events.clear();std::fill(t->stimulusSamples.begin(),t->stimulusSamples.end(),0.);
            for(const auto ordinal:t->presentedOrdinals) {
                const auto frame=ordinal==0?p0:p1;
                t->observation.events.push_back({specification.stimulusIds[ordinal],t->observation.channels[0].samples[frame].time});
                t->stimulusSamples[frame]=1.;
            }
        }
    }
    MatchedOmissionResult Select() const {return SelectMatchedOmissionMaximum(specification,policy,witness);}
};

void NoMeasurement(const MatchedOmissionResult& result) {
    EXPECT_NE(result.validity,Validity::Valid);EXPECT_FALSE(result.selectedFullMaximum);EXPECT_FALSE(result.measuredMaximum);
    EXPECT_FALSE(result.reasons.empty());
}

TEST(MatchedOmissionAssignment,SelectsActualAssignedPeakInsteadOfGlobalOrDifferenceMaximum)
{
    Fixture f;auto control=f.omit0;control[2]=2.5;control[3]=3.;control[4]=2.5;
    f.Values(f.witness.omitEachInput[0],control);
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->rawPotential,5.);EXPECT_DOUBLE_EQ(r.measuredMaximum->amplitude,3.);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,.3); // Global is 6 at .7; largest difference is not the measured value.
    ASSERT_TRUE(r.selectedFullMaximum);EXPECT_EQ(r.maxima[*r.selectedFullMaximum].supportedInputs,(std::vector<std::size_t>{0}));
}
TEST(MatchedOmissionAssignment,MissingUnrelatedResponseDoesNotInvalidateTheAssignedMaximum)
{
    Fixture f;std::vector<double> absent(11,2.);f.Responses(f.omit1,absent,f.omit1);
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->rawPotential,5.);
}
TEST(MatchedOmissionAssignment,ControlVectorOrderDoesNotChangeSourceOrdinalIdentity)
{
    Fixture f;std::reverse(f.witness.omitEachInput.begin(),f.witness.omitEachInput.end());
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,.3);
}
TEST(MatchedOmissionAssignment,SmallerAssignedExtremaPermitTheUniqueHighestActualMaximum)
{
    Fixture f;auto full=f.full;full[2]=3.;full[3]=2.;full[4]=5.;auto other=f.omit1;
    other[2]=3.;other[3]=2.;other[4]=5.;f.Responses(full,f.omit0,other);
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,.4);EXPECT_DOUBLE_EQ(r.measuredMaximum->rawPotential,5.);
}
TEST(MatchedOmissionAssignment,DelayedPriorWaveCannotBeRelabelledAsTheMissingAssignedResponse)
{
    Fixture f;f.Assigned(1);f.EventFrames(1,3);
    const std::vector<double> prior{2.,2.,2.,3.,8.,3.,2.,2.,2.,2.,2.};
    f.Responses(prior,std::vector<double>(11,2.),prior);
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Missing);
}
TEST(MatchedOmissionAssignment,EarlierHigherGlobalMaximumDoesNotReplaceLaterAssignedPeak)
{
    Fixture f;f.Assigned(1);auto full=f.full;full[3]=9.;auto omittedOther=f.omit1;omittedOther[3]=9.;
    f.Responses(full,f.omit0,omittedOther);
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,.7);EXPECT_DOUBLE_EQ(r.measuredMaximum->rawPotential,6.);
}
TEST(MatchedOmissionAssignment,SharedVertexSupportedByTwoImpulsesIsAmbiguous)
{
    Fixture f;auto other=f.omit1;other[2]=other[3]=other[4]=2.;f.Values(f.witness.omitEachInput[1],other);
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Ambiguous);
}
TEST(MatchedOmissionAssignment,OppositeSignedNonlinearInfluenceStillMakesThePeakShared)
{
    Fixture f;auto other=f.omit1;other[3]=7.;f.Values(f.witness.omitEachInput[1],other);
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Ambiguous);
}
TEST(MatchedOmissionAssignment,HigherSharedPeakCannotBeHiddenByASmallerExclusivePeak)
{
    Fixture f;auto full=f.full;full[2]=3.;full[3]=2.;full[4]=5.;auto omitOther=f.omit1;
    omitOther[2]=3.;omitOther[3]=2.;omitOther[4]=2.;f.Responses(full,f.omit0,omitOther);
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Ambiguous);
}
TEST(MatchedOmissionAssignment,RepeatUncertaintyAtTheInfluenceThresholdRemainsUnknown)
{
    Fixture f;f.policy.repeatabilityAbsolute=.2;
    f.witness.fullAfter.observation.channels[0].samples[3].rawPotential=5.1;
    auto control=f.full;control[3]=4.8;f.Values(f.witness.omitEachInput[0],control);
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Ambiguous);
    EXPECT_TRUE(std::any_of(r.maxima.begin(),r.maxima.end(),[](const auto& m){return m.unknown;}));
}
TEST(MatchedOmissionAssignment,TiedSeparatedAssignedMaximaLeaveTheMeasurementAmbiguous)
{
    Fixture f;auto full=f.full;full[2]=5.;full[3]=2.;full[4]=5.;auto other=f.omit1;
    other[2]=5.;other[3]=2.;other[4]=5.;f.Responses(full,f.omit0,other);
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Ambiguous);
}
TEST(MatchedOmissionAssignment,ContinuousPlateauRetainsItsActualFirstAndLastSamples)
{
    Fixture f;auto full=f.full;full[2]=full[3]=full[4]=5.;auto other=f.omit1;
    other[2]=other[3]=other[4]=5.;f.Responses(full,f.omit0,other);
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_EQ(r.measuredMaximum->firstSample,2u);EXPECT_EQ(r.measuredMaximum->lastSample,4u);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,.2);EXPECT_DOUBLE_EQ(r.measuredMaximum->plateauEnd,.4);
}
TEST(MatchedOmissionAssignment,BoundaryClippingCannotBeAcceptedAsAnAssignedPeak)
{
    Fixture f;auto full=f.full;auto other=f.omit1;full[9]=other[9]=4.;full[10]=other[10]=8.;
    f.Responses(full,f.omit0,other);const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Clipped);
}
TEST(MatchedOmissionAssignment,NoAssignedInfluenceProducesMissingInsteadOfBorrowingAnotherPeak)
{
    Fixture f;f.Responses(f.omit0,f.omit0,std::vector<double>(11,2.));
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Missing);
}
TEST(MatchedOmissionAssignment,SingleInputIsExplicitlyLeftToTheExistingSingleImpulsePath)
{
    Fixture f;f.specification.stimulusIds={"p0"};f.specification.physicalChannelPaths={"Soma1"};
    f.witness.omitEachInput.clear();f.policy.maximumNativeProbes=2;f.policy.maximumTotalSamples=22;
    for(auto* t:f.Traces()) {
        t->physicalChannelPaths={"Soma1"};t->presentedOrdinals={0};t->observation.channels.resize(1);
        t->observation.events.resize(1);t->stimulusSamples[5]=0.;
    }
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::Unsupported);
}
TEST(MatchedOmissionAssignment,MissingAndDuplicateOmissionControlsCannotCloseAWitness)
{
    Fixture missing;missing.witness.omitEachInput.pop_back();NoMeasurement(missing.Select());
    Fixture duplicate;duplicate.witness.omitEachInput[1]=duplicate.witness.omitEachInput[0];NoMeasurement(duplicate.Select());
    Fixture reused;reused.witness.omitEachInput[1].observation.trialId=reused.witness.omitEachInput[0].observation.trialId;
    NoMeasurement(reused.Select());
}
TEST(MatchedOmissionAssignment,FullAndOmissionMasksMustBeTheDeclaredOriginalSourceOrdinals)
{
    Fixture full;full.witness.fullBefore.presentedOrdinals={0};NoMeasurement(full.Select());
    Fixture omission;omission.witness.omitEachInput[0].presentedOrdinals={0,1};NoMeasurement(omission.Select());
    Fixture unknown;unknown.witness.omitEachInput[0].presentedOrdinals={2};NoMeasurement(unknown.Select());
}
TEST(MatchedOmissionAssignment,ModelEpochResetInstanceAndSourceBindingsCannotChangeBetweenControls)
{
    using Edit=std::function<void(MatchedOmissionTrace&)>;
    const std::vector<Edit> edits{
        [](auto& t){t.prepared.baseModelRevision="other";},[](auto& t){t.prepared.effectiveModelRevision="other";},
        [](auto& t){++t.prepared.modelEpoch;},[](auto& t){t.observation.modelRevision="other";},
        [](auto& t){t.resetBinding="other";},[](auto& t){t.modelInstanceBinding="other";},
        [](auto& t){t.sourcePatternHash="other";},[](auto& t){t.currentBaseRevision="other";},
        [](auto& t){t.groupId="other";},[](auto& t){t.prepared.inputId="input1";}
    };
    for(std::size_t i=0;i<edits.size();++i){SCOPED_TRACE(i);Fixture f;edits[i](f.witness.omitEachInput[0]);NoMeasurement(f.Select());}
}
TEST(MatchedOmissionAssignment,BaselineChangeCannotMasqueradeAsImpulseInfluence)
{
    Fixture f;f.witness.omitEachInput[0].observation.channels[0].baseline=3.;NoMeasurement(f.Select());
}
TEST(MatchedOmissionAssignment,RetainedActualEventMustRemainAtTheSameNativeFrame)
{
    Fixture f;auto& control=f.witness.omitEachInput[0];
    control.observation.events[0].time=control.observation.channels[0].samples[6].time;
    control.stimulusSamples[5]=0.;control.stimulusSamples[6]=1.;NoMeasurement(f.Select());
    Fixture withinFrame;withinFrame.witness.omitEachInput[0].observation.events[0].time+=.001;
    NoMeasurement(withinFrame.Select()); // Still below half a tick, but exceeds the declared comparison error.
}
TEST(MatchedOmissionAssignment,SubtickClockRoundoffDoesNotPermitAWholeTickDrift)
{
    Fixture f;f.policy.timeComparisonTolerance=.049;
    for(auto& channel:f.witness.omitEachInput[0].observation.channels)
        channel.samples[5].time+=.1;
    NoMeasurement(f.Select());
}
TEST(MatchedOmissionAssignment,AbsoluteClockOriginsUseExplicitSubHalfTickToleranceWithoutInterpolation)
{
    Fixture f;f.policy.timeComparisonTolerance=1e-8;
    for(auto* t:f.Traces()) {
        t->observation.begin+=1000000.;t->observation.end+=1000000.;
        for(auto& e:t->observation.events)e.time+=1000000.;
        for(auto& c:t->observation.channels)for(auto& sample:c.samples)sample.time+=1000000.;
    }
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,f.witness.fullBefore.observation.channels[0].samples[3].time);
}
TEST(MatchedOmissionAssignment,NativeGroupsCannotOverlapTheLastActualFrameBeyondTheDeclaredEnd)
{
    Fixture f;f.specification.duration=.95;
    for(auto* t:f.Traces())t->observation.end=t->observation.begin+f.specification.duration;
    auto& overlap=f.witness.omitEachInput[0];overlap.observation.begin-=.05;overlap.observation.end-=.05;
    for(auto& event:overlap.observation.events)event.time-=.05;
    for(auto& channel:overlap.observation.channels)for(auto& sample:channel.samples)sample.time-=.05;
    // FullBefore ends at .95 by declaration, but its native closing sample is
    // at 1.0. Starting another native probe at .95 would overlap actual execution.
    NoMeasurement(f.Select());
}
TEST(MatchedOmissionAssignment,MissingDuplicateOrWronglyNamedActualEventsCannotBeIgnored)
{
    Fixture missing;missing.witness.omitEachInput[0].observation.events.clear();NoMeasurement(missing.Select());
    Fixture duplicate;duplicate.witness.fullAfter.observation.events.push_back(duplicate.witness.fullAfter.observation.events[0]);NoMeasurement(duplicate.Select());
    Fixture renamed;renamed.witness.omitEachInput[0].observation.events[0].id="p0";NoMeasurement(renamed.Select());
}
TEST(MatchedOmissionAssignment,NonfinitePotentialStimulusOrBaselineNeverProducesAMeasurement)
{
    Fixture potential;potential.witness.omitEachInput[0].observation.channels[0].samples[3].rawPotential=std::numeric_limits<double>::quiet_NaN();NoMeasurement(potential.Select());
    Fixture stimulus;stimulus.witness.fullBefore.stimulusSamples[2]=std::numeric_limits<double>::infinity();NoMeasurement(stimulus.Select());
    Fixture baseline;baseline.witness.fullAfter.observation.channels[0].baseline=std::numeric_limits<double>::quiet_NaN();NoMeasurement(baseline.Select());
}
TEST(MatchedOmissionAssignment,DroppedFramesAndIncompleteOrUnrestoredNativeClosureDoNotCloseAGroup)
{
    Fixture gap;gap.witness.omitEachInput[0].observation.channels[0].samples.erase(gap.witness.omitEachInput[0].observation.channels[0].samples.begin()+4);NoMeasurement(gap.Select());
    Fixture incomplete;incomplete.witness.fullAfter.observation.complete=false;NoMeasurement(incomplete.Select());
    Fixture failed;failed.witness.omitEachInput[0].nativeCompleted=false;NoMeasurement(failed.Select());
    Fixture unrestored;unrestored.witness.omitEachInput[0].fullMaskRestored=false;NoMeasurement(unrestored.Select());
}
TEST(MatchedOmissionAssignment,EveryActualNativeProbeAndSampleCountsAgainstItsBudget)
{
    Fixture perProbe;perProbe.policy.maximumSamples=10;EXPECT_EQ(perProbe.Select().validity,Validity::BudgetExhausted);
    Fixture total;total.policy.maximumTotalSamples=43;EXPECT_EQ(total.Select().validity,Validity::BudgetExhausted);
    Fixture probes;probes.policy.maximumNativeProbes=3;EXPECT_EQ(probes.Select().validity,Validity::BudgetExhausted);
}
TEST(MatchedOmissionAssignment,UndeclaredNonfiniteOrHalfTickTimingToleranceIsInvalid)
{
    for(double value:{std::numeric_limits<double>::quiet_NaN(),-.01,.05,std::numeric_limits<double>::infinity()}) {
        Fixture f;f.policy.timeComparisonTolerance=value;NoMeasurement(f.Select());
    }
}
TEST(MatchedOmissionAssignment,RemovedSourceRegionsMustBeZeroAndRetainedPulseShapesMustMatch)
{
    Fixture removed;removed.witness.omitEachInput[0].stimulusSamples[1]=1.;NoMeasurement(removed.Select());
    Fixture retained;retained.witness.omitEachInput[1].stimulusSamples[1]=.5;NoMeasurement(retained.Select());
    Fixture extended;extended.witness.omitEachInput[1].stimulusSamples[2]=1.;NoMeasurement(extended.Select());
    Fixture physics;physics.witness.omitEachInput[0].stimulusProfile.amplitude=2.;NoMeasurement(physics.Select());
}
TEST(MatchedOmissionAssignment,FullBeforeAndAfterMustRepeatWithinTheirSeparateTolerance)
{
    Fixture f;f.witness.fullAfter.observation.channels[0].samples[3].rawPotential+=.5;
    const auto r=f.Select();NoMeasurement(r);EXPECT_EQ(r.validity,Validity::NonRepeatable);
}
TEST(MatchedOmissionAssignment,PolicyPreflightDoesNotRequireAnAlreadyPreparedEffectiveRevision)
{
    Fixture f;f.specification.effectiveModelRevision.clear();
    const auto r=ValidateMatchedOmissionPolicy(f.policy,f.specification.stimulusProfile,f.specification.stimulusIds.size());
    EXPECT_EQ(r.validity,Validity::Valid);EXPECT_TRUE(r.reasons.empty());
    EXPECT_FALSE(r.selectedFullMaximum);EXPECT_FALSE(r.measuredMaximum);
}
TEST(MatchedOmissionAssignment,SwappingAssignedPeakHeightsWithinPointwiseToleranceDoesNotFixAnUnstableWinner)
{
    Fixture f;f.policy.repeatabilityAbsolute=.11;
    auto full=f.full;full[2]=5.;full[3]=2.;full[4]=4.9;
    auto other=f.omit1;other[2]=5.;other[3]=2.;other[4]=4.9;
    f.Responses(full,f.omit0,other);
    f.witness.fullAfter.observation.channels[0].samples[2].rawPotential=4.9;
    f.witness.fullAfter.observation.channels[0].samples[4].rawPotential=5.;
    const auto r=f.Select();NoMeasurement(r);
    EXPECT_TRUE(r.validity==Validity::NonRepeatable || r.validity==Validity::Ambiguous);
}
TEST(MatchedOmissionAssignment,MovingPlateauEndpointsWithinPointwiseToleranceDoesNotFixAnUnstableArrival)
{
    Fixture f;f.policy.repeatabilityAbsolute=.11;
    auto full=f.full;full[2]=5.;full[3]=5.;full[4]=4.9;
    auto other=f.omit1;other[2]=5.;other[3]=5.;other[4]=4.9;
    f.Responses(full,f.omit0,other);
    f.witness.fullAfter.observation.channels[0].samples[2].rawPotential=4.9;
    f.witness.fullAfter.observation.channels[0].samples[4].rawPotential=5.;
    const auto r=f.Select();NoMeasurement(r);
    EXPECT_TRUE(r.validity==Validity::NonRepeatable || r.validity==Validity::Ambiguous);
}
TEST(MatchedOmissionAssignment,BranchSoloSelectorBindsTheAssignedInputToItsSinglePhysicalChannel)
{
    Fixture f;f.specification.routing=ProbeRouting::BranchSoloBurst;
    f.specification.assignedInput=1;f.specification.channel=0;f.specification.inputId="input1";
    f.specification.physicalChannelPaths={"Soma1"};
    for(auto* t:f.Traces()) {
        t->prepared.routing=ProbeRouting::BranchSoloBurst;t->prepared.inputId="input1";t->prepared.selectedInputIndex=1;
        t->physicalChannelPaths={"Soma1"};t->observation.channels.resize(1);
    }
    const auto r=f.Select();ASSERT_EQ(r.validity,Validity::Valid);ASSERT_TRUE(r.measuredMaximum);
    EXPECT_DOUBLE_EQ(r.measuredMaximum->time,.7);EXPECT_DOUBLE_EQ(r.measuredMaximum->rawPotential,6.);
    f.witness.omitEachInput[0].prepared.selectedInputIndex=0;NoMeasurement(f.Select());
}
TEST(MatchedOmissionAssignment,ChannelMappingsAndNativeSoloSelectorsAreBoundToTheAssignedInput)
{
    Fixture swapped;std::swap(swapped.witness.omitEachInput[0].physicalChannelPaths[0],swapped.witness.omitEachInput[0].physicalChannelPaths[1]);NoMeasurement(swapped.Select());
    Fixture selected;selected.witness.fullBefore.prepared.selectedInputIndex=0;NoMeasurement(selected.Select());
}
}
