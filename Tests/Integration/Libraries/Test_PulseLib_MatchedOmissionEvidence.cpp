#include <gtest/gtest.h>
#include "TimeLearner/MatchedOmissionEvidenceJson.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/StimulusSubset.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <functional>
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
std::string MatchedIsiHash(const std::vector<double>& values)
{
    QJsonArray array;for(double value:values)array.append(value);
    return NmsdkTools::CanonicalModelDataSha256(array).toStdString();
}
struct MatchedCodecFixture {
    NativeMatchedOmissionResult result;
    std::vector<QString> paths;
    MatchedOmissionPrimary primary;
    explicit MatchedCodecFixture(bool shared=false,bool branch=false) {
        result.policy.comparisonRadiusTicks=1;result.policy.timeComparisonTolerance=1e-12;
        result.policy.maximumSamples=13;result.policy.maximumTotalSamples=52;
        result.policy.maximumNativeProbes=4;result.policy.influenceAbsolute=.1;
        result.sourceIsi={.1,.5};result.appliedSourceIsi=result.sourceIsi;
        result.maximumModelSeconds=10.;result.maximumWallSeconds=60.;
        auto& s=result.specification;s.runId="portable";s.groupId="portable/group";s.sampleId="sample";
        s.protocolRevision="protocol";s.inputId=branch?"right-path":"input0";
        s.baseModelRevision="base";s.effectiveModelRevision="effective";s.modelEpoch=7;
        s.patternHash=MatchedIsiHash(result.sourceIsi);s.resetBinding="native-neuron-dataset-reset-before-children-v1";
        s.modelInstanceBinding="declared-unit-instance";s.assignedInput=branch?1:0;s.channel=0;
        s.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        s.stimulusIds={"pulse0","pulse1"};s.physicalChannelPaths=branch?
            std::vector<std::string>{"Neuron.Soma1"}:std::vector<std::string>{"Neuron.Soma1","Neuron.Soma2"};
        s.duration=1.2;s.minimumAmplitude=.5;
        s.stimulusProfile.generatorClass="NPulseGeneratorTransit";s.stimulusProfile.amplitude=1.;
        s.stimulusProfile.pulseLength=.1;s.stimulusProfile.frequencyHz=10.;
        const std::vector<std::vector<std::size_t>> masks{{0,1},{1},{0},{0,1}};
        const std::vector<double> full{0.,0.,1.,3.,1.,0.,0.,0.,shared?4.:2.,0.,0.,0.,0.};
        const std::vector<double> omit0{0.,0.,0.,0.,0.,0.,0.,0.,2.,0.,0.,0.,0.};
        const std::vector<double> omit1{0.,0.,1.,3.,1.,0.,0.,0.,shared?2.:0.,0.,0.,0.,0.};
        for(std::size_t index=0;index<4;++index) {
            const auto mask=masks[index];const auto presented=PlanStimulusSubset(result.sourceIsi,mask).presentedIsi;
            const auto& signal=index==1?omit0:index==2?omit1:full;
            const double begin=double(index)*2.;
            ProbeSpec actual;actual.schemaVersion=6;actual.runId=s.runId;
            actual.trialId=s.groupId+"/native/"+std::to_string(index);actual.sampleId=s.sampleId;
            actual.patternHash=MatchedIsiHash(presented);actual.modelRevision=s.effectiveModelRevision;
            actual.begin=begin;actual.end=begin+s.duration;actual.maximumSamples=13;
            actual.maximumSampleGap=.1;actual.minimumAmplitude=.5;
            actual.baseline.assign(s.physicalChannelPaths.size(),2.);actual.stimulusProfile=s.stimulusProfile;
            actual.stimulusSubset=StimulusSubsetCharacterization{s.patternHash,2,mask};
            for(auto ordinal:mask)actual.expectedStimulusIds.push_back(s.stimulusIds[ordinal]);
            PreparedVerificationProbe prepared{s.routing,s.inputId,s.protocolRevision,s.baseModelRevision,
                                                s.effectiveModelRevision,s.modelEpoch};
            if(branch)prepared.selectedInputIndex=s.assignedInput;
            NativeResponseDomainCapture capture;capture.Arm(prepared,actual,s.physicalChannelPaths);
            ProbeRecorder recorder(actual);
            for(std::size_t frame=0;frame<13;++frame) {
                NativeProbeSample sample;sample.time=begin+double(frame)/10.;
                sample.effectiveModelRevision=s.effectiveModelRevision;sample.potentials.assign(actual.baseline.size(),2.);
                sample.potentials[0]+=signal[frame];
                for(auto ordinal:mask)if(frame==(ordinal==0?1u:6u)) {
                    sample.stimulus=1.;sample.newStimuli.push_back({s.stimulusIds[ordinal],sample.time});
                    recorder.RecordStimulus(s.stimulusIds[ordinal],sample.time);
                }
                capture.Append(sample);recorder.Observe(sample.time,sample.potentials,sample.effectiveModelRevision);
            }
            NativeProbeResult native;native.status=NativeProbeStatus::Completed;native.prepared=prepared;
            native.currentBaseRevision=s.baseModelRevision;native.requestedSpecification=actual;
            native.requestedSpecification->begin=0.;native.requestedSpecification->end=s.duration;
            native.requestedSpecification->baseline.clear();native.requestedSpecification->modelRevision.clear();
            native.observation=recorder.Close(actual.end,s.effectiveModelRevision,"window_closed");
            capture.CloseNative(native);
            MatchedOmissionTrace trace;trace.groupId=s.groupId;trace.sourcePatternHash=s.patternHash;
            trace.resetBinding=s.resetBinding;trace.modelInstanceBinding=s.modelInstanceBinding;
            trace.currentBaseRevision=s.baseModelRevision;trace.prepared=prepared;trace.observation=capture.Observation();
            trace.physicalChannelPaths=s.physicalChannelPaths;trace.presentedOrdinals=mask;
            trace.stimulusProfile=s.stimulusProfile;trace.stimulusSamples=capture.StimulusSamples();
            trace.nativeCompleted=true;trace.fullMaskRestored=true;
            const auto name=QString("nested/native-%1.csv").arg(qulonglong(index));paths.push_back(name);
            primary.emplace(name,EncodeMatchedOmissionPrimaryTrace(trace,native));
            result.packets.push_back(native);result.appliedPresentedIsi.push_back(presented);
            if(index==0)result.witness.fullBefore=trace;
            else if(index==3)result.witness.fullAfter=trace;
            else result.witness.omitEachInput.push_back(trace);
        }
        result.assignment=SelectMatchedOmissionMaximum(s,result.policy,result.witness);
        result.reason="omission_group_closed";
    }
    QJsonObject Encode() const {return EncodeMatchedOmissionEvidence(result,paths,primary);}
};
void ChangeTrace(QJsonObject& object,int index,const std::function<void(QJsonObject&)>& change)
{
    auto traces=object["traces"].toArray();auto trace=traces[index].toObject();change(trace);traces[index]=trace;object["traces"]=traces;
}
TEST(MatchedOmissionCodec,CompleteClassicRoundtripRecomputesAssignment)
{
    MatchedCodecFixture f;const auto encoded=f.Encode();const auto decoded=DecodeMatchedOmissionEvidence(encoded,f.primary);
    ASSERT_TRUE(decoded.assignment);EXPECT_EQ(decoded.assignment->validity,MatchedOmissionValidity::Valid);
    EXPECT_EQ(EncodeMatchedOmissionEvidence(decoded,f.paths,f.primary),encoded);
    EXPECT_EQ(decoded.sourceIsi,f.result.sourceIsi);EXPECT_EQ(decoded.appliedPresentedIsi,f.result.appliedPresentedIsi);
    EXPECT_FALSE(encoded["training_certificate_eligible"].toBool());
}
TEST(MatchedOmissionCodec,BranchSelectorAndNonconventionalInputIdSurvive)
{
    MatchedCodecFixture f(false,true);const auto decoded=DecodeMatchedOmissionEvidence(f.Encode(),f.primary);
    ASSERT_TRUE(decoded.assignment);EXPECT_EQ(decoded.assignment->validity,MatchedOmissionValidity::Valid);
    EXPECT_EQ(decoded.specification.inputId,"right-path");EXPECT_EQ(decoded.specification.assignedInput,1u);
    ASSERT_TRUE(decoded.assignment->selectedFullMaximum);EXPECT_EQ(*decoded.assignment->selectedFullMaximum,1u);
}
TEST(MatchedOmissionCodec,CompleteAmbiguousOutcomeIsPreservedWithoutCertificate)
{
    MatchedCodecFixture f(true);auto encoded=f.Encode();auto decoded=DecodeMatchedOmissionEvidence(encoded,f.primary);
    ASSERT_TRUE(decoded.assignment);EXPECT_EQ(decoded.assignment->validity,MatchedOmissionValidity::Ambiguous);
    EXPECT_FALSE(decoded.assignment->selectedFullMaximum);EXPECT_FALSE(encoded["training_certificate_eligible"].toBool());
}
TEST(MatchedOmissionCodec,PartialGroupIsNeverExportedAsComplete)
{
    MatchedCodecFixture f;f.result.witness.fullAfter={};f.result.assignment.reset();
    EXPECT_THROW(f.Encode(),std::invalid_argument);
}
TEST(MatchedOmissionCodec,AppliedReadbacksCannotBeFilledFromUnverifiedPlan)
{
    MatchedCodecFixture f;f.result.appliedSourceIsi.clear();EXPECT_THROW(f.Encode(),std::invalid_argument);
    MatchedCodecFixture g;g.result.appliedPresentedIsi[1][0]+=.1;EXPECT_THROW(g.Encode(),std::invalid_argument);
}
TEST(MatchedOmissionCodec,UnknownSchemaAndUnknownFieldsAreRejected)
{
    MatchedCodecFixture f;auto object=f.Encode();object["schema_version"]=2;EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
    object=f.Encode();object["unknown"]=true;EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,RawDuplicateJsonKeysAreRejected)
{
    MatchedCodecFixture f;auto raw=QJsonDocument(f.Encode()).toJson(QJsonDocument::Compact);
    raw.insert(1,"\"schema_version\":1,");EXPECT_THROW(DecodeMatchedOmissionEvidence(raw,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,MissingDuplicateAndExtraPrimaryAreRejected)
{
    MatchedCodecFixture f;auto object=f.Encode();auto missing=f.primary;missing.erase(f.paths[1]);
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,missing),std::invalid_argument);
    auto extra=f.primary;extra.emplace("extra.csv",QByteArray());EXPECT_THROW(DecodeMatchedOmissionEvidence(object,extra),std::invalid_argument);
    ChangeTrace(object,1,[&](auto& trace){trace["relative_path"]=f.paths[0];});
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,EscapingTracePathsAreRejected)
{
    MatchedCodecFixture f;auto object=f.Encode();ChangeTrace(object,0,[](auto& trace){trace["relative_path"]="../outside.csv";});
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
    auto paths=f.paths;paths[0]="/outside.csv";EXPECT_THROW(EncodeMatchedOmissionEvidence(f.result,paths,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,NativePacketMutationCannotHideBehindClosedFlags)
{
    MatchedCodecFixture f;auto object=f.Encode();ChangeTrace(object,1,[](auto& trace){auto native=trace["native_evidence"].toObject();
        auto prepared=native["prepared"].toObject();prepared["model_epoch"]=8;native["prepared"]=prepared;trace["native_evidence"]=native;});
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,UnsupportedNativeAttestationCannotBeInvented)
{
    MatchedCodecFixture f;auto object=f.Encode();auto attestation=object["attestation"].toObject();
    attestation["native_execution_verified"]=true;object["attestation"]=attestation;
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,ElapsedWallTimeIsNotInventedFromModelTime)
{
    MatchedCodecFixture f;auto object=f.Encode();auto time=object["time_budget"].toObject();
    time["elapsed_wall_seconds"]=1.;object["time_budget"]=time;EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,SampleAndProbeBudgetsAreValidated)
{
    MatchedCodecFixture f;f.result.policy.maximumSamples=12;EXPECT_THROW(f.Encode(),std::invalid_argument);
    MatchedCodecFixture g;g.result.policy.maximumTotalSamples=51;EXPECT_THROW(g.Encode(),std::invalid_argument);
    MatchedCodecFixture h;h.result.policy.maximumNativeProbes=3;EXPECT_THROW(h.Encode(),std::invalid_argument);
}
TEST(MatchedOmissionCodec,SourceAndPresentedIsiHashesAreRecomputed)
{
    MatchedCodecFixture f;auto object=f.Encode();auto source=object["source"].toObject();source["planned_sha256"]="other";object["source"]=source;
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
    object=f.Encode();ChangeTrace(object,1,[](auto& trace){trace["presented_pattern_sha256"]="other";});
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,StoredAssignmentMustMatchFreshSelection)
{
    MatchedCodecFixture f;auto object=f.Encode();auto assignment=object["assignment"].toObject();
    assignment["selected_full_maximum"]=1;object["assignment"]=assignment;
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
    f.result.assignment->measuredMaximum->amplitude+=1.;EXPECT_THROW(f.Encode(),std::invalid_argument);
}
TEST(MatchedOmissionCodec,IncompleteRestorationBindingRejectsCompleteClaim)
{
    MatchedCodecFixture f;auto object=f.Encode();ChangeTrace(object,1,[](auto& trace){auto binding=trace["binding"].toObject();
        binding["full_mask_restored"]=false;trace["binding"]=binding;});
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,DeclaredModelBudgetCannotBeLessThanObservedSpan)
{
    MatchedCodecFixture f;f.result.maximumModelSeconds=7.;EXPECT_THROW(f.Encode(),std::invalid_argument);
}
TEST(MatchedOmissionCodec,NonfiniteSourceCannotBeSerializedAsNull)
{
    MatchedCodecFixture f;f.result.sourceIsi[0]=std::numeric_limits<double>::quiet_NaN();EXPECT_THROW(f.Encode(),std::invalid_argument);
}
TEST(MatchedOmissionCodec,ControlOrderAndMaskCannotBeReassigned)
{
    MatchedCodecFixture f;auto object=f.Encode();ChangeTrace(object,1,[](auto& trace){trace["omitted_input"]=1;});
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
TEST(MatchedOmissionCodec,RecognitionAndTrainingClaimsRemainSeparate)
{
    MatchedCodecFixture f;auto object=f.Encode();object["training_certificate_eligible"]=true;
    EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
    object=f.Encode();object["scientific_verdict"]="PASS";EXPECT_THROW(DecodeMatchedOmissionEvidence(object,f.primary),std::invalid_argument);
}
}
