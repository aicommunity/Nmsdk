#include <gtest/gtest.h>
#include "TimeLearner/CandidateWindowTrainingDeclarations.h"
#include "TimeLearner/FinalVerification.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/CompositeTrainingDeclarations.h"
#include "TimeLearner/BoundedTraining.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include <QJsonDocument>
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
TEST(CandidateWindowDeclarations,StandalonePolicyRejectsInvalidHardIntervalAndWidth) {
    auto policy=DeclaredProtocol().candidateWindowMeasurement->candidateWindowPolicy;
    auto wire=EncodeCandidateWindowPolicy(policy);auto inputs=wire["inputs"].toArray();auto first=inputs[0].toObject();
    first["hard_last_frame"]=first["hard_first_frame"];inputs[0]=first;wire["inputs"]=inputs;
    EXPECT_THROW(DecodeCandidateWindowPolicy(wire),std::invalid_argument);
    policy.inputs[0].maximumWindowFrames=1;EXPECT_THROW(EncodeCandidateWindowPolicy(policy),std::invalid_argument);
}
TEST(CandidateWindowDeclarations,BoundedTrainingExplicitlyBlocksProtocol5BeforeReferenceFactoryExists) {
    try {ValidateBoundedTrainingInputs(DeclaredProtocol(),BoundedTrainingConfig{},{});FAIL()<<"protocol5 accepted by legacy bounded path";}
    catch(const std::invalid_argument& e){EXPECT_STREQ(e.what(),"candidate_window_training_requires_proposal_admission");}
}

namespace {
ConfiguredNativeTraining Cold7Declaration() {
    const auto p=DeclaredProtocol();ConfiguredNativeTraining c;c.model.frequencyHz=2000;c.model.neuronClass="declared-neuron-storage-image";
    c.model.inputs={{2,1,100.},{1,1,100.}};c.model.initialIsi={.01,.08};c.model.editPolicy.maximumCableLength=8;
    c.stimulusProfile=*p.stimulusProfile;c.runId="cold7-declaration";c.protocolRevision=p.revision;c.sampleId=p.sampleId;
    c.duration=.17;c.maximumSampleGap=p.maximumSampleGap;c.maximumSamples=512;c.maximumReferenceProbes=2;
    c.maximumModelSeconds=120.;c.maximumWallSeconds=1800.;c.windows={{.009,.07},{.089,.15}};
    c.search.maximumProbes=64;c.search.maximumEdits=8;c.search.maximumCandidatesPerInput=32;
    c.search.bounds={{1,8,1,4,1.,1000.},{1,8,1,4,1.,1000.}};
    NativeCompositeTrainingPolicy common;common.schemaVersion=2;common.contextPolicy=p.candidateWindowMeasurement->contextPolicy;
    common.geometryPolicy=p.candidateWindowMeasurement->geometryPolicy;common.maximumGroups=64;common.maximumNativeProbes=256;
    common.maximumTotalSamples=64*2048;common.maximumTotalPrimaryBytes=64*1024*1024;common.maximumGroupModelSeconds=2.;common.maximumGroupWallSeconds=300.;
    c.composite=common;c.candidateWindowPolicy=p.candidateWindowMeasurement->candidateWindowPolicy;return c;
}
}
TEST(CandidateWindowCold7,ExplicitRoundtripBuildsProtocol5WithOriginalReferenceWindows) {
    const auto c=Cold7Declaration();const auto wire=EncodeConfiguredNativeTraining(c);const auto plan=MakeConfiguredNativeTrainingPlan(c);
    EXPECT_EQ(wire["schema_version"],QJsonValue(7));EXPECT_EQ(wire["base_schema_version"],QJsonValue(1));
    EXPECT_EQ(EncodeConfiguredNativeTraining(DecodeConfiguredNativeTraining(wire)),wire);
    EXPECT_EQ(plan.protocol.schemaVersion,5u);EXPECT_FALSE(plan.protocol.compositeMeasurement);
    ASSERT_TRUE(plan.protocol.candidateWindowMeasurement);EXPECT_EQ(plan.protocol.candidateWindowMeasurement->referenceInputWindows[0],(CompositeInputWindow{.009,.07}));
    EXPECT_EQ(plan.protocol.candidateWindowMeasurement->candidateWindowPolicy,*c.candidateWindowPolicy);
    EXPECT_EQ(plan.search.tolerances.sync,.02);EXPECT_EQ(plan.search.tolerances.amplitudeAbsolute,1e-5);EXPECT_EQ(plan.protocol.minimumAmplitude,1e-6);
}
TEST(CandidateWindowCold7,EveryRepeatAndCapacitanceBaseKeepsItsOwnDeclaration) {
    for(int base=1;base<=4;++base){auto c=Cold7Declaration();if(base>=2)c.search.n0CandidateRepeats=2;
        if(base>=3){c.recordCapacitanceHistory=true;c.capacitanceMaximumRelativeChange=.2;}
        if(base==4)c.search.capacitanceSearch=CapacitanceSearchPolicy{};
        const auto wire=EncodeConfiguredNativeTraining(c);EXPECT_EQ(wire["base_schema_version"],QJsonValue(base));
        EXPECT_EQ(EncodeConfiguredNativeTraining(DecodeConfiguredNativeTraining(wire)),wire);}
}
TEST(CandidateWindowCold7,Cold6RejectsCandidatePolicyInsteadOfPromotingVersion) {
    auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());wire["schema_version"]=6;
    EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
}
TEST(CandidateWindowCold7,MissingCommonOrCandidatePolicyCannotUseDefaults) {
    auto c=Cold7Declaration();c.composite.reset();EXPECT_THROW(EncodeConfiguredNativeTraining(c),std::invalid_argument);
    auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());auto common=wire["composite_measurement"].toObject();common.remove("candidate_window_policy");
    wire["composite_measurement"]=common;EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
}
TEST(CandidateWindowCold7,OldFlatSchemasRefuseNewEnvelopeFields) {
    for(int schema=1;schema<=4;++schema){auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());wire["schema_version"]=schema;
        EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);}
}
TEST(CandidateWindowCold7,BooleanSchemaAndCountsRemainInvalid) {
    const auto original=EncodeConfiguredNativeTraining(Cold7Declaration());auto wire=original;wire["schema_version"]=true;
    EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
    wire=original;auto common=wire["composite_measurement"].toObject();auto limits=common["attempt_limits"].toObject();limits["maximum_groups"]=true;
    common["attempt_limits"]=limits;wire["composite_measurement"]=common;EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
}
TEST(CandidateWindowCold7,UnknownVersionsAndNestedBasesAreNotAtLeastSeven) {
    for(int version:{5,6,7}){auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());wire["base_schema_version"]=version;
        EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);}
    auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());wire["schema_version"]=8;EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
    wire=EncodeConfiguredNativeTraining(Cold7Declaration());auto common=wire["composite_measurement"].toObject();common["schema_version"]=3;
    wire["composite_measurement"]=common;EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
}
TEST(CandidateWindowCold7,AdvanceUnassignedRawRecoveryIsNotSilentlyTransferred) {
    auto c=Cold7Declaration();c.search.invalidMeasurementRecovery=InvalidMeasurementRecovery::AdvanceUnassignedBurst;c.search.maximumInvalidObservations=1;
    EXPECT_THROW(EncodeConfiguredNativeTraining(c),std::invalid_argument);
}
TEST(CandidateWindowCold7,TipResistanceNormalizationDoesNotChangeTolerances) {
    auto c=Cold7Declaration();c.model.normalization=c.model.editPolicy.normalization=c.search.normalization=Normalization::TipResistance;
    const auto p=MakeConfiguredNativeTrainingPlan(DecodeConfiguredNativeTraining(EncodeConfiguredNativeTraining(c)));
    EXPECT_EQ(p.search.normalization,Normalization::TipResistance);EXPECT_EQ(p.search.tolerances.sync,.02);EXPECT_EQ(p.search.n0CandidateRepeats,1u);
}
TEST(CandidateWindowCold7,SingleInputUsesOldScalarPathAndExplicitlyRefusesNewMethod) {
    auto c=Cold7Declaration();c.model.inputs.resize(1);c.model.initialIsi.resize(1);c.windows.resize(1);c.search.bounds.resize(1);c.candidateWindowPolicy->inputs.resize(1);
    try{MakeConfiguredNativeTrainingPlan(c);FAIL()<<"single-input new method accepted";}catch(const std::invalid_argument& e){EXPECT_STREQ(e.what(),"candidate_window_multi_input_method_requires_at_least_two_inputs");}
    c.candidateWindowPolicy.reset();c.composite.reset();EXPECT_EQ(MakeConfiguredNativeTrainingPlan(c).protocol.schemaVersion,3u);
}
TEST(CandidateWindowCold7,PolicyCannotCarryCapturedSeedsOrEligibilityFlag) {
    auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());auto common=wire["composite_measurement"].toObject();auto policy=common["candidate_window_policy"].toObject();
    policy["reference_valid"]=true;common["candidate_window_policy"]=policy;wire["composite_measurement"]=common;
    EXPECT_THROW(DecodeConfiguredNativeTraining(wire),std::invalid_argument);
}
TEST(CandidateWindowCold7,CapacitanceOffNeverInventsHistoryOrCheckpointFields) {
    const auto wire=EncodeConfiguredNativeTraining(Cold7Declaration());EXPECT_FALSE(wire.contains("capacitance_history"));EXPECT_FALSE(wire.contains("capacitance_search"));
    EXPECT_FALSE(wire.contains("initial_model_revision"));EXPECT_FALSE(wire.contains("reference_group_ids"));
    const auto parsed=ParseConfiguredNativeTraining(QJsonDocument(wire).toJson(QJsonDocument::Compact).toStdString());
    EXPECT_FALSE(parsed.recordCapacitanceHistory);EXPECT_FALSE(parsed.search.capacitanceSearch);EXPECT_EQ(parsed.capacitanceMaximumRelativeChange,0.);
}
TEST(CandidateWindowCold7,InitialDeclarationCannotNormalizeAwayMissingActualOrigin) {
    const auto c=Cold7Declaration();auto p=MakeConfiguredNativeTrainingPlan(c);p.protocol.originStimulusId="missing-origin";
    EXPECT_THROW(CaptureCandidateWindowInitialConfiguration(c.model,p,{{2,1,100.},{1,1,100.}},0.),std::invalid_argument);
}
TEST(CandidateWindowCold7,InitialDeclarationCannotNormalizeAwayWrongProtocolAssignment) {
    const auto c=Cold7Declaration();auto p=MakeConfiguredNativeTrainingPlan(c);p.protocol.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    EXPECT_THROW(CaptureCandidateWindowInitialConfiguration(c.model,p,{{2,1,100.},{1,1,100.}},0.),std::invalid_argument);
}
