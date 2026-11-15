#include <gtest/gtest.h>
#include "TimeLearner/CandidateWindowProposalReplay.h"
#include "TimeLearner/ModelIdentity.h"
#include <QJsonDocument>
#include <limits>
#include <type_traits>

namespace {
using namespace NMSDK::TimeLearner;
static_assert(!std::is_default_constructible_v<ReplayedCandidateWindowBinding>);
static_assert(!std::is_aggregate_v<ReplayedCandidateWindowBinding>);
static_assert(!std::is_constructible_v<ReplayedCandidateWindowProposal,CandidateWindowProposalRecord>);
std::string DataHash(const QJsonValue& v){return NmsdkTools::CanonicalModelDataSha256(v).toStdString();}
std::string DataHash(const char* text){return DataHash(QJsonValue(QString::fromLatin1(text)));}
void BindData(CandidateWindowProposalRecord& r) {
    r.windowRecipeId=DataHash(CandidateWindowRecipeContent(r));r.measurementInstanceId=DataHash(CandidateWindowInstanceContent(r));
}
// Synthetic DATA exercises the document boundary only. These strings and facts
// never construct an opaque ReferenceSet or assert actual native execution.
CandidateWindowProposalRecord UntrustedData() {
    CandidateWindowProposalRecord r;r.sourceOrigin=DataHash("syntactic source");r.ownerFamilyBinding=DataHash("syntactic family");
    r.referenceProofId=DataHash("syntactic reference");r.protocolBinding=DataHash("syntactic protocol");
    r.candidateBinding=DataHash("syntactic candidate");r.candidateModelRevision=DataHash("syntactic model");
    r.referenceGroupId="reference-data";r.attemptId="attempt-data";r.runId=r.attemptId;r.trialId=r.runId+"/search/1";
    r.groupId=r.trialId+"/composite/1";r.inputId="input0";
    auto& s=r.reference;s.firstFrame=s.lastFrame=40;s.referenceFrameCount=512;s.grid.frequencyHz=2000;
    s.grid.sourceOrigin=r.sourceOrigin;s.grid.sourcePatternBinding=DataHash("syntactic pattern");s.grid.sourceProfileBinding=DataHash("syntactic profile");
    s.initialParameters={{2,1,1000.},{1,1,1000.}};r.candidate.grid=s.grid;r.candidate.declaredMaximumSamples=512;
    r.candidate.parameters={{3,1,1000.},{1,1,1000.}};
    CandidateWindowPolicy p;p.maximumFeatureTerms=64;p.inputs.resize(2);for(auto& i:p.inputs) {
        i.delayFramesPerSegment=20;i.baseLeftGuardFrames=i.baseRightGuardFrames=10;i.hardFirstFrame=1;i.hardLastFrame=400;i.maximumWindowFrames=100;
    }
    r.policyBinding=DataHash(EncodeCandidateWindowPolicy(p));r.computation=CalculateCandidateWindowArithmetic(p,s,r.candidate);BindData(r);return r;
}
}
TEST(CandidateWindowProposalData,StrictDataRoundtripDoesNotMintOpaqueReferenceOrReplayAuthority) {
    const auto data=UntrustedData();const auto encoded=EncodeCandidateWindowProposalData(data);
    EXPECT_EQ(EncodeCandidateWindowProposalData(DecodeCandidateWindowProposalData(encoded)),encoded);
    EXPECT_EQ(EncodeCandidateWindowProposalData(DecodeCandidateWindowProposalData(QJsonDocument(encoded).toJson())),encoded);
}
TEST(CandidateWindowProposalData,BooleanSchemaCannotEqualOne) {
    auto wire=EncodeCandidateWindowProposalData(UntrustedData());wire["schema_version"]=true;
    EXPECT_THROW(DecodeCandidateWindowProposalData(wire),std::invalid_argument);
}
TEST(CandidateWindowProposalData,BooleanZeroIndicesAndEpochAreNotCounts) {
    for(const char* field:{"input_index","channel","model_epoch"}) {
        auto wire=EncodeCandidateWindowProposalData(UntrustedData());wire[field]=false;
        EXPECT_THROW(DecodeCandidateWindowProposalData(wire),std::invalid_argument)<<field;
    }
}
TEST(CandidateWindowProposalData,InexactSignedShiftAndAbsurdIndexAreRejectedBeforeUse) {
    auto wire=EncodeCandidateWindowProposalData(UntrustedData());auto c=wire["computation"].toObject();c["shift_frames"]=9007199254740992.;wire["computation"]=c;
    EXPECT_THROW(DecodeCandidateWindowProposalData(wire),std::invalid_argument);
    wire=EncodeCandidateWindowProposalData(UntrustedData());wire["input_index"]=1e300;
    EXPECT_THROW(DecodeCandidateWindowProposalData(wire),std::invalid_argument);
}
TEST(CandidateWindowProposalData,NonfiniteFeatureDoesNotBecomeAProposal) {
    auto r=UntrustedData();r.candidate.parameters[0].resistance=std::numeric_limits<double>::quiet_NaN();
    EXPECT_THROW(EncodeCandidateWindowProposalData(r),std::invalid_argument);
}
TEST(CandidateWindowProposalData,ChangedGridCannotHideBehindRehashedIdentifiers) {
    auto r=UntrustedData();r.candidate.grid.frequencyHz=20000;BindData(r);
    EXPECT_THROW(EncodeCandidateWindowProposalData(r),std::invalid_argument);
}
TEST(CandidateWindowProposalData,ReferenceEdgeIsNotAnInteriorPlateauSeed) {
    auto r=UntrustedData();r.reference.firstFrame=0;BindData(r);
    EXPECT_THROW(EncodeCandidateWindowProposalData(r),std::invalid_argument);
}
TEST(CandidateWindowProposalData,DeclaredSampleBudgetMustContainCandidateInterval) {
    auto r=UntrustedData();r.candidate.declaredMaximumSamples=r.computation.window->lastFrame;BindData(r);
    EXPECT_THROW(EncodeCandidateWindowProposalData(r),std::invalid_argument);
}
TEST(CandidateWindowProposalData,OffKeepsBothCapacitanceStatesNull) {
    const auto wire=EncodeCandidateWindowProposalData(UntrustedData());EXPECT_TRUE(wire["reference"].toObject()["initial_capacitance"].isNull());
    EXPECT_TRUE(wire["candidate"].toObject()["capacitance"].isNull());EXPECT_EQ(wire["computation"].toObject()["capacitance_changes"],QJsonValue(0));
}
TEST(CandidateWindowProposalData,SameValueDuplicateJsonFieldIsRejectedAtByteBoundary) {
    auto bytes=QJsonDocument(EncodeCandidateWindowProposalData(UntrustedData())).toJson(QJsonDocument::Compact);bytes.chop(1);bytes+=",\"schema_version\":1}";
    EXPECT_THROW(DecodeCandidateWindowProposalData(bytes),std::invalid_argument);
}
TEST(CandidateWindowProposalData,PredictedPeakIsNotARecognizedDataField) {
    auto wire=EncodeCandidateWindowProposalData(UntrustedData());wire["predicted_peak"]=.03;
    EXPECT_THROW(DecodeCandidateWindowProposalData(wire),std::invalid_argument);
}
TEST(CandidateWindowProposalData,ChangedComputationWithoutHashRebindingIsRejected) {
    auto wire=EncodeCandidateWindowProposalData(UntrustedData());auto c=wire["computation"].toObject();c["first_frame"]=51.;wire["computation"]=c;
    EXPECT_THROW(DecodeCandidateWindowProposalData(wire),std::invalid_argument);
}
TEST(CandidateWindowProposalData,ReboundFalseComputationIsStillOnlyDataAndNeedsOpaqueReplay) {
    auto r=UntrustedData();++r.computation.window->firstFrame;BindData(r);
    // No complete policy/reference/native binding is available at this DATA
    // layer. Shared Replay must reject this claim against actual closed inputs.
    EXPECT_NO_THROW(DecodeCandidateWindowProposalData(EncodeCandidateWindowProposalData(r)));
}
TEST(CandidateWindowProposalData,GroupRelabelChangesInstanceWithoutChangingRecipe) {
    auto a=UntrustedData(),b=a;b.trialId=b.runId+"/search/2";b.groupId=b.trialId+"/composite/2";BindData(b);
    EXPECT_EQ(a.windowRecipeId,b.windowRecipeId);EXPECT_NE(a.measurementInstanceId,b.measurementInstanceId);
}
TEST(CandidateWindowProposalData,ChangedCandidateEpochAndPolicyChangeRecipe) {
    const auto a=UntrustedData();auto b=a;++b.modelEpoch;BindData(b);EXPECT_NE(a.windowRecipeId,b.windowRecipeId);
    b=a;b.policyBinding=DataHash("another policy");BindData(b);EXPECT_NE(a.windowRecipeId,b.windowRecipeId);
    b=a;b.candidateModelRevision=DataHash("another candidate");BindData(b);EXPECT_NE(a.windowRecipeId,b.windowRecipeId);
}
TEST(CandidateWindowProposalData,MalformedHashAndEmptyReferenceCannotBecomeDataProof) {
    auto r=UntrustedData();r.referenceProofId="true";BindData(r);EXPECT_THROW(EncodeCandidateWindowProposalData(r),std::invalid_argument);
    r=UntrustedData();r.referenceProofId.clear();BindData(r);EXPECT_THROW(EncodeCandidateWindowProposalData(r),std::invalid_argument);
}
