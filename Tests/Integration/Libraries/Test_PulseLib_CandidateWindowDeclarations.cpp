#include <gtest/gtest.h>
#include "TimeLearner/CandidateWindowTrainingDeclarations.h"
#include "TimeLearner/FinalVerification.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/CompositeTrainingDeclarations.h"
#include <QJsonArray>
#include <limits>
#include <type_traits>

namespace {
using namespace NMSDK::TimeLearner;
static_assert(!std::is_default_constructible_v<CandidateWindowReferenceSet>);
static_assert(!std::is_aggregate_v<CandidateWindowReferenceSet>);
static_assert(!std::is_default_constructible_v<NativeCandidateWindowSnapshot>);
static_assert(!std::is_aggregate_v<NativeCandidateWindowSnapshot>);
static_assert(!std::is_default_constructible_v<PreparedCandidateWindowProposal>);
static_assert(!std::is_aggregate_v<PreparedCandidateWindowProposal>);
static_assert(!std::is_default_constructible_v<ReplayedCandidateWindowProposal>);
static_assert(!std::is_aggregate_v<ReplayedCandidateWindowProposal>);
VerificationProtocol DeclaredProtocol() {
    VerificationProtocol p;p.schemaVersion=5;p.revision="candidate-window-declaration-test";p.sampleId="sample";
    p.patternHash="declared-pattern";p.originStimulusId="pulse0";p.stimulusIds={"pulse0","pulse1"};
    p.inputs={{"input0","pulse0"},{"input1","pulse1"}};p.maximumSampleGap=1./2000;
    p.stimulusProfile=StimulusProfile{"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
    CandidateWindowMeasurementContract c;c.referenceInputWindows={{.009,.07},{.089,.15}};
    c.contextPolicy.timeComparisonTolerance=1e-10;c.contextPolicy.maximumSamples=512;
    c.contextPolicy.maximumTotalSamples=2048;c.contextPolicy.maximumNativeProbes=4;
    c.geometryPolicy.maximumInputs=2;c.geometryPolicy.maximumSamples=512;c.geometryPolicy.maximumTotalSamples=2048;
    c.candidateWindowPolicy.maximumFeatureTerms=64;c.candidateWindowPolicy.inputs.resize(2);
    for(auto& i:c.candidateWindowPolicy.inputs) {
        i.delayFramesPerSegment=20;i.baseLeftGuardFrames=10;i.baseRightGuardFrames=10;
        i.hardFirstFrame=1;i.hardLastFrame=400;i.maximumWindowFrames=100;
    }
    p.candidateWindowMeasurement=c;return p;
}
CandidateWindowBasinSpecification FrameSpec() {
    CandidateWindowBasinSpecification s;s.groupId="group";s.inputId="input1";s.assignedInput=1;
    s.coordinateMode=CandidateWindowCoordinateMode::CandidateFrame;s.candidateFrame=CandidateFrameWindow{13,23};return s;
}
}
TEST(CandidateWindowDeclarations,Protocol5RoundtripPreservesExplicitReferenceWindowsAndFullPolicy) {
    const auto p=DeclaredProtocol();const auto wire=EncodeVerificationProtocol(p);
    EXPECT_EQ(DecodeVerificationProtocol(wire),p);
    const auto c=wire["composite_measurement"].toObject();EXPECT_TRUE(c.contains("reference_input_windows"));
    EXPECT_FALSE(c.contains("input_windows"));EXPECT_EQ(c["candidate_window_policy"].toObject()["inputs"].toArray().size(),2);
}
TEST(CandidateWindowDeclarations,Protocol4KeepsItsFixedWindowWire) {
    auto p=DeclaredProtocol();const auto c=*p.candidateWindowMeasurement;p.schemaVersion=4;p.candidateWindowMeasurement.reset();
    CompositeMeasurementContract fixed;fixed.contextPolicy=c.contextPolicy;fixed.geometryPolicy=c.geometryPolicy;
    fixed.inputWindows=c.referenceInputWindows;p.compositeMeasurement=fixed;
    const auto wire=EncodeVerificationProtocol(p);EXPECT_EQ(DecodeVerificationProtocol(wire),p);
    EXPECT_TRUE(wire["composite_measurement"].toObject().contains("input_windows"));
    EXPECT_FALSE(wire["composite_measurement"].toObject().contains("candidate_window_policy"));
}
TEST(CandidateWindowDeclarations,Contract2CannotFallBackToOldInputWindowsAlias) {
    auto wire=EncodeCandidateWindowMeasurementContract(*DeclaredProtocol().candidateWindowMeasurement);
    wire["input_windows"]=wire.take("reference_input_windows");
    EXPECT_THROW(DecodeCandidateWindowMeasurementContract(wire),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,OldContractRejectsNewPolicyFields) {
    auto wire=EncodeCandidateWindowMeasurementContract(*DeclaredProtocol().candidateWindowMeasurement);
    EXPECT_THROW(DecodeCompositeMeasurementContract(wire),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,UnknownProtocolIsNotAnAtLeastFiveBranch) {
    auto wire=EncodeVerificationProtocol(DeclaredProtocol());wire["schema_version"]=6;
    EXPECT_THROW(DecodeVerificationProtocol(wire),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,BooleanPolicyVersionAndCountAreRejected) {
    auto wire=EncodeCandidateWindowPolicy(DeclaredProtocol().candidateWindowMeasurement->candidateWindowPolicy);
    wire["schema_version"]=true;EXPECT_THROW(DecodeCandidateWindowPolicy(wire),std::invalid_argument);
    wire=EncodeCandidateWindowPolicy(DeclaredProtocol().candidateWindowMeasurement->candidateWindowPolicy);
    wire["maximum_feature_terms"]=true;EXPECT_THROW(DecodeCandidateWindowPolicy(wire),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,IntegralNumericCountHasTheSameDeclaredMeaning) {
    auto wire=EncodeCandidateWindowPolicy(DeclaredProtocol().candidateWindowMeasurement->candidateWindowPolicy);
    wire["proposals_per_logical_request"]=1.;EXPECT_EQ(DecodeCandidateWindowPolicy(wire).proposalsPerLogicalRequest,1u);
}
TEST(CandidateWindowDeclarations,FeatureDimensionIsCheckedBeforePolicyScan) {
    auto wire=EncodeCandidateWindowPolicy(DeclaredProtocol().candidateWindowMeasurement->candidateWindowPolicy);
    wire["maximum_feature_terms"]=3;EXPECT_THROW(DecodeCandidateWindowPolicy(wire),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,UnknownPolicyAndMultipleProposalsAreRejected) {
    auto p=DeclaredProtocol();p.candidateWindowMeasurement->candidateWindowPolicy.policyId="future";
    EXPECT_THROW(ValidateVerificationProtocol(p),std::invalid_argument);
    p=DeclaredProtocol();p.candidateWindowMeasurement->candidateWindowPolicy.proposalsPerLogicalRequest=2;
    EXPECT_THROW(ValidateVerificationProtocol(p),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,DeclaredEnvelopeMustFitMaximumSamples) {
    auto p=DeclaredProtocol();p.candidateWindowMeasurement->candidateWindowPolicy.inputs[0].hardLastFrame=512;
    EXPECT_THROW(ValidateVerificationProtocol(p),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,FixedAndCandidateContractsCannotCoexist) {
    auto p=DeclaredProtocol();p.compositeMeasurement=CompositeMeasurementContract{};
    EXPECT_THROW(ValidateVerificationProtocol(p),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,RawReferenceCaptureCannotMintProtocol5Authority) {
    EXPECT_THROW(CapturedReferences::Capture(DeclaredProtocol(),{}),std::invalid_argument);
    EXPECT_THROW(CapturedReferences::CaptureComposite(DeclaredProtocol(),{}),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,FrameSpec2RoundtripDoesNotPretendFramesWereCaptured) {
    const auto s=FrameSpec();const auto wire=EncodeCandidateWindowBasinSpecification(s);
    const auto decoded=DecodeCandidateWindowBasinSpecification(wire);
    EXPECT_EQ(decoded.candidateFrame,s.candidateFrame);EXPECT_FALSE(decoded.referenceTime);
    EXPECT_EQ(wire["coordinate_mode"],QJsonValue("candidate_frame"));
}
TEST(CandidateWindowDeclarations,Spec2CannotCarryBothCoordinateKinds) {
    auto s=FrameSpec();s.referenceTime=CompositeInputWindow{.01,.03};
    EXPECT_THROW(EncodeCandidateWindowBasinSpecification(s),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,UnknownCoordinateAndBooleanFrameAreRejected) {
    auto wire=EncodeCandidateWindowBasinSpecification(FrameSpec());wire["coordinate_mode"]="future";
    EXPECT_THROW(DecodeCandidateWindowBasinSpecification(wire),std::invalid_argument);
    wire=EncodeCandidateWindowBasinSpecification(FrameSpec());auto frames=wire["candidate_frame"].toObject();
    frames["first_frame"]=true;wire["candidate_frame"]=frames;
    EXPECT_THROW(DecodeCandidateWindowBasinSpecification(wire),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,Spec2RejectsUnknownKeysAndMissingCoordinate) {
    auto wire=EncodeCandidateWindowBasinSpecification(FrameSpec());wire["predicted_peak"]=.02;
    EXPECT_THROW(DecodeCandidateWindowBasinSpecification(wire),std::invalid_argument);
    wire=EncodeCandidateWindowBasinSpecification(FrameSpec());wire.remove("candidate_frame");
    EXPECT_THROW(DecodeCandidateWindowBasinSpecification(wire),std::invalid_argument);
}
