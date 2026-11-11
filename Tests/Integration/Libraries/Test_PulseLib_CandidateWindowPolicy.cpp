#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/CandidateWindowPolicy.h"
#include <cmath>
#include <limits>
#include <type_traits>

namespace {
using namespace NMSDK::TimeLearner;
using Status=CandidateWindowComputationStatus;
static_assert(!std::is_default_constructible_v<CandidateWindowReferenceSeed>);
static_assert(!std::is_aggregate_v<CandidateWindowReferenceSeed>);
static_assert(!std::is_constructible_v<CandidateWindowReferenceSeed,CandidateWindowArithmeticSeed,std::string,std::string>);
static_assert(!std::is_convertible_v<CandidateWindowComputation,CandidateWindowReferenceSeed>);
static_assert(!std::is_invocable_v<decltype(&CalculateCandidateWindowArithmetic),const CandidateWindowPolicy&,
    const CandidateWindowArithmeticSeed&,const CandidateWindowCandidateFacts&,double>);
struct Fixture {
    CandidateWindowPolicy policy;
    CandidateWindowArithmeticSeed seed;
    CandidateWindowCandidateFacts current;
    Fixture() {
        seed.inputIndex=0;seed.firstFrame=60;seed.lastFrame=62;seed.referenceFrameCount=400;
        seed.grid.frequencyHz=2000;seed.grid.sourceOrigin="declared-source";seed.grid.sourcePatternBinding="declared-isi";
        seed.grid.sourceProfileBinding="declared-profile";seed.initialParameters={{2,1,100.},{1,2,150.}};
        current.grid=seed.grid;current.declaredMaximumSamples=400;current.parameters=seed.initialParameters;
        policy.maximumFeatureTerms=6;CandidateInputWindowPolicy p;p.delayFramesPerSegment=10;
        p.baseLeftGuardFrames=2;p.baseRightGuardFrames=3;p.lengthGuardFrames=2;p.synapseCountGuardFrames=3;
        p.resistanceChangeGuardFrames=4;p.capacitanceChangeGuardFrames=5;p.hardLastFrame=300;p.maximumWindowFrames=100;
        policy.inputs={p,p};
    }
    CandidateWindowComputation Compute() const{return CalculateCandidateWindowArithmetic(policy,seed,current);}
    void C0() {
        TrainingCapacitance c;c.origin=std::string(64,'a');c.maximumRelativeChange=.2;c.membraneScales={{"Dendrite1_1",1.}};
        seed.initialCapacitance=c;current.capacitance=c;policy.maximumFeatureTerms=16;
    }
};
void Window(const CandidateWindowComputation& r,std::uint64_t first,std::uint64_t last) {
    ASSERT_EQ(r.status,Status::Computed);ASSERT_TRUE(r.window);EXPECT_TRUE(r.reasons.empty());
    EXPECT_EQ(r.window->firstFrame,first);EXPECT_EQ(r.window->lastFrame,last);
}
void Rejected(const CandidateWindowComputation& r,Status expected) {
    EXPECT_EQ(r.status,expected);EXPECT_FALSE(r.window);EXPECT_FALSE(r.reasons.empty());
}
TEST(CandidateWindowPolicy,UnchangedCandidateKeepsReferencePlateauAndDeclaredMargins) {
    Fixture f;const auto r=f.Compute();Window(r,58,65);EXPECT_EQ(r.shiftFrames,0);EXPECT_EQ(r.uncertaintyFrames,0u);EXPECT_EQ(r.featureTerms,6u);
}
TEST(CandidateWindowPolicy,LengthGrowthDeclaresShiftedWindowBeforeAnyWaveformExists) {
    Fixture f;f.current.parameters[0].length=3;const auto r=f.Compute();Window(r,66,77);EXPECT_EQ(r.shiftFrames,10);EXPECT_EQ(r.lengthChange,1u);
}
TEST(CandidateWindowPolicy,LengthShorteningUsesCheckedSignedShift) {
    Fixture f;f.current.parameters[0].length=1;const auto r=f.Compute();Window(r,46,57);EXPECT_EQ(r.shiftFrames,-10);
}
TEST(CandidateWindowPolicy,OtherInputGeometryAddsUncertaintyWithoutChangingAssignedCenter) {
    Fixture f;f.current.parameters[1].length=4;const auto r=f.Compute();Window(r,52,71);EXPECT_EQ(r.shiftFrames,0);EXPECT_EQ(r.lengthChange,3u);
}
TEST(CandidateWindowPolicy,SynapseCountChangeContributesDeclaredUncertainty) {
    Fixture f;f.current.parameters[1].synapses=5;const auto r=f.Compute();Window(r,49,74);EXPECT_EQ(r.synapseCountChange,3u);
}
TEST(CandidateWindowPolicy,ResistanceChangeIsExactAndDoesNotAssumeLogarithmicLatency) {
    Fixture f;f.current.parameters[0].resistance=std::nextafter(100.,101.);const auto r=f.Compute();Window(r,54,69);EXPECT_EQ(r.resistanceChanges,1u);
}
TEST(CandidateWindowPolicy,CombinedActualFeaturesUseOneWindow) {
    Fixture f;f.C0();f.current.parameters[0].length=3;f.current.parameters[1].synapses=5;f.current.parameters[0].resistance=90.;
    f.current.capacitance->membraneScales["Dendrite1_1"]=1.1;const auto r=f.Compute();Window(r,48,95);EXPECT_EQ(r.uncertaintyFrames,20u);
}
TEST(CandidateWindowPolicy,OffDoesNotRequireCapacitanceOrArtificialUnitBaseline) {
    Fixture f;f.policy.inputs[0].capacitanceChangeGuardFrames=CandidateWindowMaximumExactCount;
    const auto r=f.Compute();Window(r,58,65);EXPECT_EQ(r.capacitanceChanges,0u);
}
TEST(CandidateWindowPolicy,ChangedCapacitanceUsesExistingEquivalenceSemantics) {
    Fixture f;f.C0();f.current.capacitance->membraneScales["Dendrite1_1"]=1.1;const auto r=f.Compute();Window(r,53,70);EXPECT_EQ(r.capacitanceChanges,1u);
}
TEST(CandidateWindowPolicy,NewUnitCapacitancePathDoesNotPretendCorrectionChanged) {
    Fixture f;f.C0();f.current.capacitance->membraneScales["Dendrite1_2"]=1.;const auto r=f.Compute();Window(r,58,65);
    EXPECT_EQ(r.capacitanceChanges,0u);EXPECT_EQ(r.featureTerms,9u);
}
TEST(CandidateWindowPolicy,CapacitanceOriginChangeCannotBeHiddenByWiderGuard) {
    Fixture f;f.C0();f.current.capacitance->origin=std::string(64,'b');Rejected(f.Compute(),Status::InputMismatch);
}
TEST(CandidateWindowPolicy,CapacitancePolicyChangeCannotBeHiddenByWiderGuard) {
    Fixture f;f.C0();f.current.capacitance->maximumRelativeChange=.3;Rejected(f.Compute(),Status::InputMismatch);
}
TEST(CandidateWindowPolicy,CapacitanceLossOrInventionIsRejected) {
    Fixture f;f.C0();const auto c=f.current.capacitance;f.current.capacitance.reset();Rejected(f.Compute(),Status::InputMismatch);
    f.seed.initialCapacitance.reset();f.current.capacitance=c;Rejected(f.Compute(),Status::InputMismatch);
}
TEST(CandidateWindowPolicy,NonfiniteCapacitanceIsNotAnUncertaintyEstimate) {
    Fixture f;f.C0();f.current.capacitance->membraneScales["Dendrite1_1"]=std::numeric_limits<double>::quiet_NaN();Rejected(f.Compute(),Status::InvalidSpecification);
}
TEST(CandidateWindowPolicy,FeatureBudgetIncludesBothCapacitanceInventories) {
    Fixture f;f.C0();f.policy.maximumFeatureTerms=7;Rejected(f.Compute(),Status::BudgetExhausted);
}
TEST(CandidateWindowPolicy,ParameterDimensionAndAssignedOrdinalAreCheckedBeforeScanning) {
    Fixture f;f.current.parameters.pop_back();Rejected(f.Compute(),Status::InputMismatch);f.current.parameters=f.seed.initialParameters;
    f.seed.inputIndex=2;Rejected(f.Compute(),Status::InputMismatch);f.seed.inputIndex=0;f.policy.inputs.pop_back();Rejected(f.Compute(),Status::InputMismatch);
}
TEST(CandidateWindowPolicy,DeclaredFeatureBudgetIsCheckedBeforeVectorWork) {
    Fixture f;f.policy.maximumFeatureTerms=5;Rejected(f.Compute(),Status::BudgetExhausted);
}
TEST(CandidateWindowPolicy,SourceAndGridBindingsMustMatchExactly) {
    Fixture f;f.current.grid.frequencyHz=20000;Rejected(f.Compute(),Status::InputMismatch);f.current.grid=f.seed.grid;
    f.current.grid.sourceOrigin="different";Rejected(f.Compute(),Status::InputMismatch);f.current.grid=f.seed.grid;
    f.current.grid.sourcePatternBinding="different";Rejected(f.Compute(),Status::InputMismatch);f.current.grid=f.seed.grid;
    f.current.grid.sourceProfileBinding="different";Rejected(f.Compute(),Status::InputMismatch);
}
TEST(CandidateWindowPolicy,MatchingUnknownFrameOriginDoesNotBecomeSupported) {
    Fixture f;f.seed.grid.frameOriginPolicy=f.current.grid.frameOriginPolicy="unknown-origin";Rejected(f.Compute(),Status::Unsupported);
}
TEST(CandidateWindowPolicy,MatchingUnknownSourcePhaseDoesNotBecomeSupported) {
    Fixture f;f.seed.grid.sourcePhasePolicy=f.current.grid.sourcePhasePolicy="unknown-phase";Rejected(f.Compute(),Status::Unsupported);
}
TEST(CandidateWindowPolicy,MatchingUnknownResetDoesNotBecomeSupported) {
    Fixture f;f.seed.grid.resetBinding=f.current.grid.resetBinding="unknown-reset";Rejected(f.Compute(),Status::Unsupported);
}
TEST(CandidateWindowPolicy,EmptyBindingsAndZeroFrequencyAreInvalid) {
    Fixture f;f.seed.grid.sourceOrigin=f.current.grid.sourceOrigin="";Rejected(f.Compute(),Status::InvalidSpecification);
    f.seed.grid=f.current.grid=CandidateWindowGridBinding{};Rejected(f.Compute(),Status::InvalidSpecification);
}
TEST(CandidateWindowPolicy,UnknownPolicySchemaAndStrategyFailClosed) {
    Fixture f;f.policy.schemaVersion=2;Rejected(f.Compute(),Status::Unsupported);f.policy.schemaVersion=1;
    f.policy.policyId="unknown";Rejected(f.Compute(),Status::Unsupported);
}
TEST(CandidateWindowPolicy,UnknownSeedCoordinateOrMultipleProposalModeFailClosed) {
    Fixture f;const auto original=f.policy;f.policy.seedRule="latest-best-residual";Rejected(f.Compute(),Status::Unsupported);f.policy=original;
    f.policy.coordinateMode="predicted-time";Rejected(f.Compute(),Status::Unsupported);f.policy=original;
    f.policy.proposalsPerLogicalRequest=2;Rejected(f.Compute(),Status::Unsupported);
}
TEST(CandidateWindowPolicy,InvalidReferenceFramesNeverBecomeAnOpaqueSeed) {
    Fixture f;f.seed.firstFrame=0;Rejected(f.Compute(),Status::InvalidSpecification);f.seed.firstFrame=63;Rejected(f.Compute(),Status::InvalidSpecification);
    f.seed.firstFrame=60;f.seed.lastFrame=399;Rejected(f.Compute(),Status::InvalidSpecification);
}
TEST(CandidateWindowPolicy,NonfiniteOrNonpositiveParameterFeaturesAreRejected) {
    Fixture f;f.current.parameters[0].resistance=std::numeric_limits<double>::infinity();Rejected(f.Compute(),Status::InvalidSpecification);
    f.current.parameters[0].resistance=-1.;Rejected(f.Compute(),Status::InvalidSpecification);f.current.parameters[0].resistance=100.;
    f.seed.initialParameters[0].length=0;Rejected(f.Compute(),Status::InvalidSpecification);f.seed.initialParameters[0].length=2;
    f.current.parameters[1].synapses=0;Rejected(f.Compute(),Status::InvalidSpecification);
}
TEST(CandidateWindowPolicy,InexactDeclaredCountIsRejected) {
    Fixture f;f.policy.inputs[0].baseLeftGuardFrames=CandidateWindowMaximumExactCount+1;Rejected(f.Compute(),Status::InvalidSpecification);
}
TEST(CandidateWindowPolicy,ShiftProductOverflowIsExplicit) {
    Fixture f;f.seed.initialParameters[0].length=1;f.current.parameters[0].length=std::numeric_limits<int>::max();
    f.policy.inputs[0].delayFramesPerSegment=CandidateWindowMaximumExactCount;Rejected(f.Compute(),Status::ArithmeticOverflow);
}
TEST(CandidateWindowPolicy,UncertaintyProductOverflowIsExplicit) {
    Fixture f;f.current.parameters[0].length=3;f.current.parameters[1].length=2;
    f.policy.inputs[0].lengthGuardFrames=CandidateWindowMaximumExactCount;Rejected(f.Compute(),Status::ArithmeticOverflow);
}
TEST(CandidateWindowPolicy,GuardSumOverflowIsExplicit) {
    Fixture f;f.current.parameters[0].length=3;f.policy.inputs[0].baseLeftGuardFrames=CandidateWindowMaximumExactCount;
    Rejected(f.Compute(),Status::ArithmeticOverflow);
}
TEST(CandidateWindowPolicy,SignedFrameAdditionOverflowIsExplicit) {
    Fixture f;f.seed.referenceFrameCount=CandidateWindowMaximumExactCount;f.seed.firstFrame=f.seed.lastFrame=CandidateWindowMaximumExactCount-2;
    f.current.declaredMaximumSamples=CandidateWindowMaximumExactCount;for(auto& p:f.policy.inputs)p.hardLastFrame=CandidateWindowMaximumExactCount-1;
    f.current.parameters[0].length=3;Rejected(f.Compute(),Status::ArithmeticOverflow);
}
TEST(CandidateWindowPolicy,NegativeWindowIsRejectedWithoutClamping) {
    Fixture f;f.seed.firstFrame=3;f.seed.lastFrame=4;f.current.parameters[0].length=1;Rejected(f.Compute(),Status::OutsideEnvelope);
}
TEST(CandidateWindowPolicy,HardEnvelopeDoesNotSilentlyTrimTheWindow) {
    Fixture f;f.policy.inputs[0].hardFirstFrame=59;Rejected(f.Compute(),Status::OutsideEnvelope);
    f.policy.inputs[0].hardFirstFrame=0;f.policy.inputs[0].hardLastFrame=64;Rejected(f.Compute(),Status::OutsideEnvelope);
}
TEST(CandidateWindowPolicy,MaximumWidthIsInclusiveAndExplicit) {
    Fixture f;f.policy.inputs[0].maximumWindowFrames=8;Window(f.Compute(),58,65);
    f.policy.inputs[0].maximumWindowFrames=7;Rejected(f.Compute(),Status::OutsideEnvelope);
}
TEST(CandidateWindowPolicy,DeclaredSampleBudgetMustContainTheWholePolicyEnvelope) {
    Fixture f;f.current.declaredMaximumSamples=300;Rejected(f.Compute(),Status::InvalidSpecification);
}
TEST(CandidateWindowPolicy,ReferenceAndCandidateFramesRemainIndependentOfAbsoluteClock) {
    Fixture f;const auto before=f.Compute();const auto again=f.Compute();Window(before,58,65);EXPECT_EQ(before.window,again.window);
    // No absolute time/event/residual or waveform argument exists. Actual
    // native phase/event checks and timestamp projection belong to the bridge.
    EXPECT_EQ(f.seed.firstFrame,60u);EXPECT_EQ(f.seed.lastFrame,62u);
}
TEST(CandidateWindowPolicy,IdenticalCandidateAfterOtherArithmeticCallKeepsItsRecipeData) {
    Fixture f;const auto original=f.Compute();f.current.parameters[0].length=3;Window(f.Compute(),66,77);
    f.current.parameters=f.seed.initialParameters;const auto restored=f.Compute();EXPECT_EQ(restored.window,original.window);EXPECT_EQ(restored.shiftFrames,original.shiftFrames);
}
TEST(CandidateWindowPolicy,N4AndN6DistinctAttachmentFactsStayDimensioned) {
    for(std::size_t n:{4u,6u}) {Fixture f;f.seed.initialParameters.clear();for(std::size_t i=0;i<n;++i)f.seed.initialParameters.push_back({int(n-i),1,100.});
        f.current.parameters=f.seed.initialParameters;f.policy.inputs.resize(n,f.policy.inputs[0]);f.policy.maximumFeatureTerms=3*n;f.seed.inputIndex=n-1;
        ++f.current.parameters[0].length;const auto r=f.Compute();Window(r,56,67);EXPECT_EQ(r.shiftFrames,0);EXPECT_EQ(r.featureTerms,3*n);
    }
    // Arithmetic dimension coverage is NOT native distinct-bank routing proof.
}
TEST(CandidateWindowPolicy,SingleInputArithmeticDoesNotClaimNativeTrainSupport) {
    Fixture f;f.seed.initialParameters.resize(1);f.current.parameters.resize(1);f.policy.inputs.resize(1);f.policy.maximumFeatureTerms=3;Window(f.Compute(),58,65);
}
TEST(CandidateWindowPolicy,UnknownStatusNameRemainsUnknown) {
    EXPECT_STREQ(CandidateWindowComputationStatusName(static_cast<Status>(999)),"unknown");
}
}
