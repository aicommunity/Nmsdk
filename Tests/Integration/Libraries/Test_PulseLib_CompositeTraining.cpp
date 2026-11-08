#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseSynapse.h"
#include "NPulseChannel.h"
#include "TimeLearner/NativeCompositeTrainingAttempt.h"
#include "TimeLearner/NativeLearnerLifecycle.h"
#include "TimeLearner/CompositeTrainingDeclarations.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/MatchedOmissionEvidenceJson.h"
#include "TimeLearner/NativeCompositeTrainingEvidence.h"
#include "TimeLearner/ModelArchive.h"
#include "TimeLearner/CompositePortableTrainingProof.h"
#include "TimeLearner/CandidateWindowTrainingDeclarations.h"
#include "TimeLearner/NativeCandidateWindowBindings.h"
#include "TimeLearner/CandidateWindowProposalReplay.h"
#include "TimeLearner/CandidateWindowMeasurementEvidence.h"
#include "TimeLearner/CandidateWindowPortableReferences.h"
#include "TimeLearner/NativeLearnedState.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerCompositeArtifacts.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerProbeEvidenceWriter.h"
#include <QTemporaryDir>
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QDir>
#include <QCryptographicHash>
#include <QFile>
#include <cstdlib>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <type_traits>
#include <thread>

namespace {
using namespace RDK;using namespace NMSDK;using namespace NMSDK::TimeLearner;
static_assert(!std::is_default_constructible_v<PreparedCompositeMeasurement>);
static_assert(!std::is_default_constructible_v<ValidatedCompositeMeasurement>);
static_assert(!std::is_aggregate_v<PreparedCompositeMeasurement>);
static_assert(!std::is_aggregate_v<ValidatedCompositeMeasurement>);
static_assert(!std::is_default_constructible_v<DecodedNativeCompositeArchive>);
static_assert(!std::is_aggregate_v<DecodedNativeCompositeArchive>);
static_assert(!std::is_default_constructible_v<CompositePortableTrainingProof>);
static_assert(!std::is_aggregate_v<CompositePortableTrainingProof>);
void Require(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
double Wall(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
class CompositeTrainingFlag : public UNet {
public:
    UProperty<bool,CompositeTrainingFlag,ptOutput | ptPubState> Value;
    CompositeTrainingFlag():Value("Value",this){}
    CompositeTrainingFlag* New(void) override{return new CompositeTrainingFlag;}
};
template<class Owner> class NativeCompositeFixture {
public:
    static constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    UEPtr<UStorage> storage;UEPtr<UEnvironment> environment;UEPtr<UNet> model;UEPtr<Owner> owner;
    NativeModelSpec modelSpec;
    UEPtr<CompositeTrainingFlag> flag;
    VerificationProtocol protocol;NativeProbeRequest prototype;
    std::unique_ptr<NativeCompositeTrainingAttempt> attempt;
    std::vector<ValidatedCompositeMeasurement> referenceMeasurements;
    std::map<std::string,ValidatedProbeMeasurement> observedScalars;
    std::vector<double> groupBegins;
    unsigned frequency;std::size_t rawSamples=0,preparations=0;
    NativeCompositeFixture(unsigned hz=2000,bool merged=false,std::size_t groupBudget=64,bool bindC0=false,bool n0=false,bool connectedNeed=false,std::size_t dimension=2,double wallBudget=0.,bool distinctAttachments=false):frequency(hz) {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);environment->GetTime().SetTime(0);
        Require(environment->CreateModel("NModel"),"composite_fixture_model");model=dynamic_pointer_cast<UNet>(environment->GetModel());
        Require(bool(model),"composite_fixture_root");model->SetGlobalTimeStep(hz);
        const auto* test=::testing::UnitTest::GetInstance()->current_test_info();
        StorageProfileSpec profile;profile.name=std::string(test->test_suite_name())+"_"+test->name();
        profile.frequencyHz=hz;profile.neuronBaseClass="NSPNeuronGen";profile.initialThreshold=1.;
        const auto registered=RegisterStorageProfile(core.storage,environment,profile);
        owner=dynamic_pointer_cast<Owner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        Require(bool(owner),"composite_fixture_owner");owner->Name="Learner";owner->SetGlobalTimeStep(hz);
        owner->ControllerVersion=1;owner->CalculateMode=1;owner->StructureBuildMode=1;
        owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;owner->IsNeedToTrain=false;
        UEPtr<UContainer> component=owner;Require(model->AddComponent(component)!=ForbiddenId,"composite_fixture_attach");
        NativeModelSpec s;s.branch=branch;s.frequencyHz=hz;s.neuronClass=registered.neuronClass;
        s.normalization=n0?Normalization::SynapseCount:Normalization::TipResistance;
        s.editPolicy.normalization=s.normalization;s.editPolicy.maximumCableLength=8;
        for(std::size_t i=0;i<dimension;++i){s.inputs.push_back({distinctAttachments?int(dimension-i):(i+1==dimension?1:2),1,{}});s.initialIsi.push_back(i?((merged && i==1)?.001:.08):.01);}
        modelSpec=s;
        const auto built=owner->ConstructNativeModel(s);Require(built.status==NativeModelBuildStatus::Constructed,built.reason.c_str());
        model->Init();model->Reset();
        owner->IsNeedToTrain=true;
        if(connectedNeed) {
            flag=UEPtr<CompositeTrainingFlag>(new CompositeTrainingFlag);flag->SetStorage(storage);flag->SetEnvironment(environment);flag->Default();
            flag->Name="TrainingFlag";flag->Activity=true;flag->SetGlobalTimeStep(hz);UEPtr<UContainer> node=flag;
            Require(model->AddComponent(node)!=ForbiddenId,"composite_fixture_flag_attach");flag->Init();flag->Value=true;
            Require(owner->IsNeedToTrain.SetPointer(0,&flag->Value),"composite_fixture_flag_connection");
            Require(owner->IsNeedToTrain.GetData(),"composite_fixture_connected_request");
        }
        if(bindC0)owner->BindNativeTrainingCapacitance(.2);
        const auto generator=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        Require(bool(generator),"composite_fixture_source");QJsonArray pattern;for(double gap:s.initialIsi)pattern.append(gap);
        protocol.schemaVersion=4;protocol.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        protocol.revision="native-declared-basin-train-fixture-v1";protocol.sampleId="sample0";
        protocol.patternHash=NmsdkTools::CanonicalModelDataSha256(pattern).toStdString();protocol.originStimulusId="pulse0";
        for(std::size_t i=0;i<dimension;++i){const auto pulse="pulse"+std::to_string(i);protocol.inputs.push_back({"input"+std::to_string(i),pulse});protocol.stimulusIds.push_back(pulse);}
        protocol.maximumSampleGap=1./hz;protocol.stimulusProfile=StimulusProfile{generator->GetCompClassName(),
            generator->Amplitude.GetData(),generator->PulseLength.GetData(),double(generator->GetTimeStep()),
            generator->FrequencyDeviation.GetData(),generator->UseTransitSignal.GetData(),generator->UsePatternOutput.GetData()};
        double onset=0.;CompositeMeasurementContract contract;for(double isi:s.initialIsi){onset+=isi;contract.inputWindows.push_back({onset-.001,onset+.06});}
        if(dimension==2)contract.inputWindows.front()={.009,.07}; // Preserve the frozen two-input fixture bit-for-bit.
        const double duration=onset+.08;
        if(distinctAttachments)for(auto& w:contract.inputWindows)w.endOffset=std::min(w.beginOffset+.121,duration);
        auto& context=contract.contextPolicy;context.timeComparisonTolerance=1e-10;context.baselineAbsolute=1e-12;
        context.repeatabilityAbsolute=1e-10;context.influenceAbsolute=1e-6;
        context.maximumSamples=std::size_t((duration+.1)*hz);context.maximumTotalSamples=context.maximumSamples*(dimension+2);context.maximumNativeProbes=dimension+2;
        contract.geometryPolicy.maximumInputs=dimension;contract.geometryPolicy.maximumSamples=context.maximumSamples;
        contract.geometryPolicy.maximumTotalSamples=context.maximumTotalSamples;contract.geometryPolicy.repeatabilityAbsolute=1e-10;
        protocol.compositeMeasurement=contract;
        auto& p=prototype.specification;p.schemaVersion=3;p.sampleId=protocol.sampleId;p.patternHash=protocol.patternHash;
        p.end=duration;p.maximumSampleGap=protocol.maximumSampleGap;p.minimumAmplitude=protocol.minimumAmplitude;
        p.maximumSamples=context.maximumSamples;p.stimulusProfile=protocol.stimulusProfile;p.expectedStimulusIds=protocol.stimulusIds;
        prototype.expectedInputIsi=s.initialIsi;
        prototype.onPrepared=[this](const auto&,const auto&){++preparations;};
        prototype.onSample=[this](const auto&){++rawSamples;};
        // Explicit real-clock budgets; high-frequency native/replay work is
        // intentionally not measured with a zero or synthetic wall clock.
        CompositeAttemptLimits limits{groupBudget,(dimension+2)*groupBudget,context.maximumTotalSamples*groupBudget,120.,wallBudget>0.?wallBudget:(hz==20000?7200.:1800.)};
        attempt=std::make_unique<NativeCompositeTrainingAttempt>(*owner,protocol,limits,Time(),Wall());
    }
    ~NativeCompositeFixture(){attempt.reset();if(model)model->BreakLinks();environment->DestroyModel();}
    double Time() const{return environment->GetTime().GetDoubleTime();}
    std::string Revision() const {
        const auto n=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        const auto g=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        const auto id=NmsdkTools::IdentifyModel(n.Get(),{{&g->Output,"burst"}});Require(id["valid"].toBool(),"composite_fixture_identity");
        return id["sha256"].toString().toStdString();
    }
    VerificationRequest Request(std::size_t input,const std::string& run,const std::string& trial,std::size_t epoch=0) const {
        return {run,trial,protocol.inputs.at(input).id,protocol.sampleId,protocol.patternHash,protocol.revision,Revision(),protocol.routing,epoch,input};
    }
    void Run(const VerificationRequest& request,CompositeMeasurementPurpose purpose,
        std::function<void(const PreparedCompositeMeasurement&)> prepared={},std::function<void()> tick={},double groupLimit=2.,double groupWall=0.) {
        attempt->StartMeasurement(request,purpose,prototype,groupLimit,groupWall>0.?groupWall:(frequency==20000?1200.:300.),Time(),Wall(),std::move(prepared));
        std::size_t ticks=0;while(attempt->Running() && ticks++<std::size_t(groupLimit*frequency)) {
            attempt->BeforeTick(Time(),Wall());if(!attempt->Running())break;
            model->Calculate();attempt->AfterTick(Time(),Wall());environment->IncreaseModelTimeByStep();if(tick)tick();
        }
        Require(!attempt->Running(),"composite_fixture_tick_budget");
        if(attempt->Measurement()) {
            const auto& full=attempt->Group()->witness.fullBefore.observation;
            const auto& peak=*attempt->Selection()->geometry->measuredMaximum;
            const auto origin=std::find_if(full.events.begin(),full.events.end(),[&](const auto& e){return e.id==protocol.originStimulusId;});
            Require(origin!=full.events.end(),"composite_fixture_actual_origin_missing");
            const auto channel=branch?0u:request.inputIndex;
            EXPECT_DOUBLE_EQ(peak.rawPotential,full.channels.at(channel).samples.at(peak.firstSample).rawPotential);
            observedScalars.emplace(request.trialId,ValidatedProbeMeasurement{peak.rawPotential,peak.time-origin->time,peak.plateauEnd-origin->time});
            groupBegins.push_back(full.begin);
        }
    }
    CapturedReferences Capture() {
        referenceMeasurements.clear();
        for(std::size_t i=0;i<2;++i) {
            Run(Request(i,"capture","capture/"+std::to_string(i)),CompositeMeasurementPurpose::Reference);
            Require(bool(attempt->Measurement()),attempt->RejectionReason().c_str());referenceMeasurements.push_back(*attempt->Measurement());
        }
        return CapturedReferences::CaptureComposite(protocol,referenceMeasurements);
    }
};
template<class Owner> void SearchAndFinal(unsigned hz,bool boundC0=false,bool n0=false) {
    NativeCompositeFixture<Owner> f(hz,false,64,boundC0,n0);const auto refs=f.Capture();
    EXPECT_EQ(f.owner->OwnedNativeCapacitanceState().isEmpty(),!boundC0); // Off requires no artificial C0.
    BoundedTrainingConfig cfg;cfg.runId="search";cfg.initialModelRevision=f.Revision();cfg.maximumProbes=32;
    cfg.maximumEdits=8;cfg.maximumCandidatesPerInput=2;cfg.normalization=n0?Normalization::SynapseCount:Normalization::TipResistance;
    cfg.n0CandidateRepeats=n0?2:1;cfg.tolerances.sync=.2;
    const auto parameters=f.owner->ReadNativeParameters();for(const auto& p:parameters)
        cfg.bounds.push_back({p.length,p.length,p.synapses,p.synapses,p.resistance,p.resistance});
    BoundedTrainingSession search(refs,cfg,parameters,false,f.owner->ReadNativeTrainingCapacitance());std::size_t logical=0;
    while(const auto action=search.NextAction()) {
        ASSERT_EQ(action->kind,TrainingActionKind::Probe);ASSERT_LT(++logical,32u);
        const auto request=f.Request(action->inputIndex,action->runId,action->trialId,action->modelEpoch);
        std::size_t armed=0;f.Run(request,action->finalVerification?CompositeMeasurementPurpose::Final:CompositeMeasurementPurpose::Search,
            [&](const auto& prepared){++armed;search.ArmComposite(action->serial,prepared);});
        ASSERT_EQ(armed,1u);ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
        search.ConsumeComposite(*f.attempt->Measurement(),f.Revision());
    }
    ASSERT_EQ(search.Status(),TrainingStatus::Exact)<<search.Reason();ASSERT_TRUE(search.Certificate());
    const auto& certificate=*search.Certificate();EXPECT_TRUE(certificate.Exact());EXPECT_EQ(certificate.SchemaVersion(),2u);
    ASSERT_EQ(certificate.CompositeProofIds().size(),2u);EXPECT_NE(certificate.CompositeProofIds()[0],certificate.CompositeProofIds()[1]);
    EXPECT_TRUE(certificate.Matches(f.Revision(),refs,cfg.tolerances,ModelStateKind::LearnedSolo,search.ModelEpoch()));
    EXPECT_FALSE(certificate.Matches(f.Revision(),refs,cfg.tolerances,ModelStateKind::Recognition,search.ModelEpoch()));
    EXPECT_EQ(search.IssuedProbes(),logical);EXPECT_EQ(f.preparations,(logical+2)*4);
    EXPECT_EQ(f.attempt->IssuedNativeProbes(),(logical+2)*4);EXPECT_EQ(f.attempt->RetainedSamples(),f.rawSamples);
    if(n0){ASSERT_EQ(search.CandidateRepeats().size(),1u);EXPECT_EQ(search.CandidateRepeats()[0].trialIds.size(),2u);EXPECT_TRUE(search.CandidateRepeats()[0].complete);}
    const auto encodedCertificate=EncodeTrainingCertificate(certificate);EXPECT_EQ(encodedCertificate["schema_version"].toInt(),2);
    EXPECT_EQ(encodedCertificate["method_id"],QJsonValue(DeclaredWindowBasinResult::MethodId()));
    auto unsignedCertificate=encodedCertificate;unsignedCertificate.remove("semantic_certificate_id");
    EXPECT_EQ(encodedCertificate["semantic_certificate_id"],QJsonValue(NmsdkTools::CanonicalModelDataSha256(unsignedCertificate)));
    ASSERT_GT(f.groupBegins.at(1)-f.groupBegins.at(0),cfg.tolerances.sync);
    const auto& anchor=f.observedScalars.at(certificate.Residuals().back().trialId);
    for(std::size_t i=0;i<2;++i) {
        const auto& residual=certificate.Residuals()[i];const auto& actual=f.observedScalars.at(residual.trialId);
        EXPECT_DOUBLE_EQ(residual.targetRawPotential,refs.Inputs()[i].rawPotential);
        EXPECT_DOUBLE_EQ(refs.Inputs()[i].rawPotential,f.observedScalars.at(refs.Inputs()[i].trialId).rawPotential);
        EXPECT_DOUBLE_EQ(residual.measuredRawPotential,actual.rawPotential);
        EXPECT_DOUBLE_EQ(residual.timingResidualLow,i+1==2?0.:actual.arrival-anchor.plateauEnd);
        EXPECT_DOUBLE_EQ(residual.timingResidualHigh,i+1==2?0.:actual.plateauEnd-anchor.arrival);
    }
}
template<class Owner> void WrongPurpose() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();VerificationConfig cfg{"final",f.Revision(),4,0,0};
    FinalVerificationSession final(refs,cfg);const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Reference,[&](const auto& p){final.ArmComposite(p);});
    EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(final.Certificate());EXPECT_EQ(final.AcceptedInputs(),0u);
}
template<class Owner> void StoppedGroup() {
    NativeCompositeFixture<Owner> f;bool stopped=false;
    f.Run(f.Request(0,"stop","stop/0"),CompositeMeasurementPurpose::Reference,{},[&](){
        if(!stopped && f.attempt->IssuedNativeProbes()>=2){stopped=true;f.attempt->Cancel("external_stop_test");}
    });
    EXPECT_TRUE(stopped);EXPECT_FALSE(f.attempt->Measurement());EXPECT_FALSE(f.attempt->RejectionReason().empty());
    EXPECT_GT(f.rawSamples,0u);EXPECT_EQ(f.attempt->RetainedSamples(),f.rawSamples);
}
template<class Owner> void ChangedPhysicalGraph(bool cachedRevision=false) {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();VerificationConfig cfg{"final",f.Revision(),4,0,0};
    FinalVerificationSession final(refs,cfg);const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
    ASSERT_TRUE(f.attempt->Measurement());const auto proof=*f.attempt->Measurement();
    auto requested=f.owner->ReadNativeParameters();requested[0].resistance*=1.01;
    const auto changed=f.owner->ApplyNativeParameters(requested);ASSERT_EQ(changed.status,NativeEditStatus::Applied)<<changed.reason;
    ASSERT_NE(f.Revision(),request->baseModelRevision);final.ConsumeComposite(proof,cachedRevision?request->baseModelRevision:f.Revision());
    EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());EXPECT_EQ(final.ModelEpoch(),cachedRevision?0u:1u);
    if(cachedRevision)EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);
}
template<class Owner> void ExpiredLiveProof() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();FinalVerificationSession final(refs,{"final",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
    ASSERT_TRUE(f.attempt->Measurement());const auto proof=*f.attempt->Measurement();f.attempt->Cancel("end_attempt");
    final.ConsumeComposite(proof,f.Revision());EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);
    EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
}
template<class Owner> void MergedVertex() {
    NativeCompositeFixture<Owner> f(2000,true);f.Run(f.Request(0,"merged","merged/0"),CompositeMeasurementPurpose::Reference);
    EXPECT_FALSE(f.attempt->Measurement());EXPECT_FALSE(f.attempt->RejectionReason().empty());
    ASSERT_TRUE(f.attempt->Group());EXPECT_EQ(f.attempt->Group()->reason,"omission_group_closed");
}
template<class Owner> void RawAdmission() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();FinalVerificationSession final(refs,{"final",f.Revision(),4,0,0});
    ASSERT_TRUE(final.NextRequest());PreparedVerificationProbe raw;
    EXPECT_THROW(final.Arm(raw),std::invalid_argument);EXPECT_EQ(final.IssuedProbes(),0u);
    EXPECT_THROW(final.Consume(ProbeObservation{},f.Revision()),std::invalid_argument);EXPECT_FALSE(final.Certificate());
    EXPECT_THROW(CapturedReferences::Capture(f.protocol,{}),std::invalid_argument);
    // Protocol4 now has an explicit portable declaration codec. Encoding it
    // grants neither raw admission nor a live composite measurement lease.
    const auto declaration=EncodeVerificationProtocol(f.protocol);EXPECT_EQ(declaration["schema_version"],QJsonValue(4));
    EXPECT_EQ(DecodeVerificationProtocol(declaration),f.protocol);
    auto stripped=declaration;stripped.remove("composite_measurement");EXPECT_THROW(DecodeVerificationProtocol(stripped),std::invalid_argument);
    auto mislabeled=declaration;mislabeled["schema_version"]=3;EXPECT_THROW(DecodeVerificationProtocol(mislabeled),std::invalid_argument);
    EXPECT_EQ(final.IssuedProbes(),0u);EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
}
template<class Owner> void ReplayedGroup() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();FinalVerificationSession final(refs,{"final",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
    ASSERT_TRUE(f.attempt->Measurement());const auto proof=*f.attempt->Measurement();final.ConsumeComposite(proof,f.Revision());
    ASSERT_EQ(final.AcceptedInputs(),1u);ASSERT_TRUE(final.NextRequest());final.ArmComposite(proof.Prepared());
    EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_EQ(final.AcceptedInputs(),1u);EXPECT_FALSE(final.Certificate());
}
template<class Owner> void ChangedDeclaredWindow() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();auto changed=f.protocol;
    changed.compositeMeasurement->inputWindows[0].endOffset+=.001;
    EXPECT_THROW(CapturedReferences::CaptureComposite(changed,f.referenceMeasurements),std::invalid_argument);
    EXPECT_NE(refs.Inputs()[0].measurementGroupId,refs.Inputs()[1].measurementGroupId);
    EXPECT_NE(refs.Inputs()[0].semanticProofId,refs.Inputs()[1].semanticProofId);
}
template<class Owner> void GroupBudget() {
    NativeCompositeFixture<Owner> f(2000,false,1);f.Run(f.Request(0,"budget","budget/0"),CompositeMeasurementPurpose::Reference);
    ASSERT_TRUE(f.attempt->Measurement());const auto raw=f.attempt->IssuedNativeProbes();const auto frames=f.rawSamples;
    EXPECT_THROW(f.attempt->StartMeasurement(f.Request(1,"budget","budget/1"),CompositeMeasurementPurpose::Reference,
        f.prototype,2.,60.,f.Time(),Wall()),std::invalid_argument);
    EXPECT_FALSE(f.attempt->Measurement());EXPECT_EQ(f.attempt->IssuedGroups(),1u);
    EXPECT_EQ(f.attempt->IssuedNativeProbes(),raw);EXPECT_EQ(f.rawSamples,frames);EXPECT_EQ(raw,4u);
}
template<class Owner> void DefaultSyncOutsideTolerance() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();VerificationConfig cfg{"default_sync",f.Revision(),4,0,0};
    ASSERT_DOUBLE_EQ(cfg.tolerances.sync,.02);FinalVerificationSession final(refs,cfg);
    while(const auto request=final.NextRequest()) {
        f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
        ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();final.ConsumeComposite(*f.attempt->Measurement(),f.Revision());
    }
    ASSERT_EQ(final.Status(),VerificationStatus::OutsideTolerance);ASSERT_TRUE(final.Certificate());
    EXPECT_FALSE(final.Certificate()->Exact());EXPECT_DOUBLE_EQ(final.Certificate()->Tolerances().sync,.02);
    EXPECT_DOUBLE_EQ(final.Certificate()->Tolerances().amplitudeAbsolute,1e-5);
    bool observedOutside=false;for(const auto& r:final.Certificate()->Residuals()) {
        EXPECT_TRUE(r.withinAmplitude);if(!r.withinTiming)observedOutside=true;
    }
    EXPECT_TRUE(observedOutside);
}
template<class Owner> void OwnerResetInvalidatesProof() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();FinalVerificationSession final(refs,{"reset_final",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
    ASSERT_TRUE(f.attempt->Measurement());const auto proof=*f.attempt->Measurement();const auto physical=f.Revision();
    f.owner->Reset();EXPECT_EQ(f.Revision(),physical);final.ConsumeComposite(proof,f.Revision());
    EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
}
template<class Owner> void OwnerDefaultOrPoolInvalidatesProof(bool pool) {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();FinalVerificationSession final(refs,{"lifecycle_final",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
    ASSERT_TRUE(f.attempt->Measurement());const auto proof=*f.attempt->Measurement();const auto physical=f.Revision();
    if(pool) {
        f.model->DelComponent("Learner",false);f.storage->ReturnObject(f.owner);
        const auto reused=dynamic_pointer_cast<Owner>(f.storage->TakeObject(NativeCompositeFixture<Owner>::branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        ASSERT_TRUE(reused);ASSERT_EQ(reused,f.owner);f.owner=reused;f.owner->Name="Learner";
        UEPtr<UContainer> component=f.owner;ASSERT_NE(f.model->AddComponent(component),ForbiddenId);
    }
    else f.owner->Default();
    f.owner->SetGlobalTimeStep(f.frequency);f.owner->ControllerVersion=1;f.owner->CalculateMode=1;f.owner->StructureBuildMode=1;
    f.owner->EnablePostTrainTuning=false;f.owner->AutoCalibrateFixedLTZThreshold=false;f.owner->IsNeedToTrain=false;
    const auto rebuilt=f.owner->ConstructNativeModel(f.modelSpec);ASSERT_EQ(rebuilt.status,NativeModelBuildStatus::Constructed)<<rebuilt.reason;
    f.model->Init();f.model->Reset();f.owner->IsNeedToTrain=true;
    ASSERT_EQ(f.Revision(),physical);ASSERT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Idle);
    final.ConsumeComposite(proof,f.Revision());EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);
    EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());EXPECT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Idle);
}
template<class Owner> void PreparedOwnerReset() {
    NativeCompositeFixture<Owner> f;const auto refs=f.Capture();FinalVerificationSession final(refs,{"prepared_reset",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);std::optional<PreparedCompositeMeasurement> prepared;bool reset=false;
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){prepared=p;},[&](){
        if(prepared && !reset){reset=true;f.owner->Reset();}
    });
    ASSERT_TRUE(reset);ASSERT_TRUE(prepared);EXPECT_FALSE(f.attempt->Measurement());
    final.ArmComposite(*prepared);EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);
    EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());EXPECT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Idle);
}
enum class RequestStop { Setter,DirectData,Connected };
template<class Owner> void RequestRemovedBeforeFinalConsume(RequestStop mode) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,false,mode==RequestStop::Connected);const auto refs=f.Capture();
    VerificationConfig cfg{"request_final",f.Revision(),4,0,0};cfg.tolerances.sync=.2;FinalVerificationSession final(refs,cfg);
    for(std::size_t input=0;input<2;++input) {
        const auto request=final.NextRequest();ASSERT_TRUE(request);
        f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmComposite(p);});
        ASSERT_TRUE(f.attempt->Measurement());const auto proof=*f.attempt->Measurement();
        if(input==1) {
            const auto model=f.Revision();
            if(mode==RequestStop::Setter)f.owner->IsNeedToTrain=false;
            else if(mode==RequestStop::DirectData)f.owner->IsNeedToTrain.SetDataDirect(false);
            else {ASSERT_TRUE(f.flag);f.flag->Value=false;ASSERT_TRUE(f.owner->IsNeedToTrain.IsConnected());}
            EXPECT_FALSE(f.owner->IsNeedToTrain.GetData());EXPECT_EQ(f.Revision(),model);
        }
        final.ConsumeComposite(proof,f.Revision());
    }
    EXPECT_EQ(final.Status(),VerificationStatus::ExternalStop);EXPECT_EQ(final.AcceptedInputs(),1u);
    EXPECT_EQ(final.InvalidObservations(),0u);EXPECT_FALSE(final.Certificate());
}
template<class Owner> void DirectRequestRemovedDuringGroup() {
    NativeCompositeFixture<Owner> f;bool removed=false;
    f.Run(f.Request(0,"request_partial","request_partial/0"),CompositeMeasurementPurpose::Reference,{},[&](){
        if(!removed && f.rawSamples){removed=true;f.owner->IsNeedToTrain.SetDataDirect(false);}
    });
    EXPECT_TRUE(removed);EXPECT_FALSE(f.attempt->Measurement());EXPECT_FALSE(f.attempt->RejectionReason().empty());
    ASSERT_TRUE(f.attempt->Group());EXPECT_NE(f.attempt->Group()->reason,"omission_group_closed");
    EXPECT_EQ(f.attempt->RetainedSamples(),f.rawSamples);
}
}
TEST(NativeCompositeTraining,ClassicCaptureSearchFinal2000){SearchAndFinal<NNeuronTimeLearner>(2000);}
TEST(NativeCompositeTraining,BranchCaptureSearchFinal2000){SearchAndFinal<NNeuronTimeLearnerBranch>(2000);}
TEST(NativeCompositeTraining,ClassicCaptureSearchFinal20000){SearchAndFinal<NNeuronTimeLearner>(20000);}
TEST(NativeCompositeTraining,BranchCaptureSearchFinal20000){SearchAndFinal<NNeuronTimeLearnerBranch>(20000);}
TEST(NativeCompositeTraining,ClassicReferencePurposeCannotCertifyFinal){WrongPurpose<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchReferencePurposeCannotCertifyFinal){WrongPurpose<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicStoppedPartialGroupCannotCreateProof){StoppedGroup<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchStoppedPartialGroupCannotCreateProof){StoppedGroup<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicPhysicalEditInvalidatesFinal){ChangedPhysicalGraph<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchPhysicalEditInvalidatesFinal){ChangedPhysicalGraph<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicExpiredLiveAttemptRejectsClosedProof){ExpiredLiveProof<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchExpiredLiveAttemptRejectsClosedProof){ExpiredLiveProof<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicMergedVertexRemainsRejected){MergedVertex<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchMergedVertexRemainsRejected){MergedVertex<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicRawProbeCannotEnterCompositeProtocol){RawAdmission<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchRawProbeCannotEnterCompositeProtocol){RawAdmission<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicClosedGroupCannotServeNextFinalInput){ReplayedGroup<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchClosedGroupCannotServeNextFinalInput){ReplayedGroup<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicChangedDeclaredWindowCannotRelabelCapture){ChangedDeclaredWindow<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchChangedDeclaredWindowCannotRelabelCapture){ChangedDeclaredWindow<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicExistingC0CaptureSearchFinal2000){SearchAndFinal<NNeuronTimeLearner>(2000,true);}
TEST(NativeCompositeTraining,BranchExistingC0CaptureSearchFinal2000){SearchAndFinal<NNeuronTimeLearnerBranch>(2000,true);}
TEST(NativeCompositeTraining,ClassicGroupBudgetRejectsBeforeNativeQueue){GroupBudget<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchGroupBudgetRejectsBeforeNativeQueue){GroupBudget<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicCachedRevisionCannotHideActualPhysicalEdit){ChangedPhysicalGraph<NNeuronTimeLearner>(true);}
TEST(NativeCompositeTraining,BranchCachedRevisionCannotHideActualPhysicalEdit){ChangedPhysicalGraph<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCompositeTraining,ClassicDefaultSyncRemainsOutsideTolerance){DefaultSyncOutsideTolerance<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchDefaultSyncRemainsOutsideTolerance){DefaultSyncOutsideTolerance<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicOwnerResetExpiresUnchangedPhysicalProof){OwnerResetInvalidatesProof<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchOwnerResetExpiresUnchangedPhysicalProof){OwnerResetInvalidatesProof<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicOwnerDefaultReconstructExpiresIdenticalProof){OwnerDefaultOrPoolInvalidatesProof<NNeuronTimeLearner>(false);}
TEST(NativeCompositeTraining,BranchOwnerDefaultReconstructExpiresIdenticalProof){OwnerDefaultOrPoolInvalidatesProof<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCompositeTraining,ClassicPoolReuseReconstructExpiresIdenticalProof){OwnerDefaultOrPoolInvalidatesProof<NNeuronTimeLearner>(true);}
TEST(NativeCompositeTraining,BranchPoolReuseReconstructExpiresIdenticalProof){OwnerDefaultOrPoolInvalidatesProof<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCompositeTraining,ClassicPreparedDeclarationExpiresAfterOwnerReset){PreparedOwnerReset<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchPreparedDeclarationExpiresAfterOwnerReset){PreparedOwnerReset<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeTraining,ClassicN0FreshRepeatCaptureSearchFinal2000){SearchAndFinal<NNeuronTimeLearner>(2000,false,true);}
TEST(NativeCompositeTraining,BranchN0FreshRepeatCaptureSearchFinal2000){SearchAndFinal<NNeuronTimeLearnerBranch>(2000,false,true);}
TEST(NativeCompositeTraining,ClassicSetterStopBetweenFinalCloseAndConsume){RequestRemovedBeforeFinalConsume<NNeuronTimeLearner>(RequestStop::Setter);}
TEST(NativeCompositeTraining,BranchSetterStopBetweenFinalCloseAndConsume){RequestRemovedBeforeFinalConsume<NNeuronTimeLearnerBranch>(RequestStop::Setter);}
TEST(NativeCompositeTraining,ClassicDirectDataStopBetweenFinalCloseAndConsume){RequestRemovedBeforeFinalConsume<NNeuronTimeLearner>(RequestStop::DirectData);}
TEST(NativeCompositeTraining,BranchDirectDataStopBetweenFinalCloseAndConsume){RequestRemovedBeforeFinalConsume<NNeuronTimeLearnerBranch>(RequestStop::DirectData);}
TEST(NativeCompositeTraining,ClassicConnectedStopBetweenFinalCloseAndConsume){RequestRemovedBeforeFinalConsume<NNeuronTimeLearner>(RequestStop::Connected);}
TEST(NativeCompositeTraining,BranchConnectedStopBetweenFinalCloseAndConsume){RequestRemovedBeforeFinalConsume<NNeuronTimeLearnerBranch>(RequestStop::Connected);}
TEST(NativeCompositeTraining,ClassicDirectDataStopDuringNativeGroup){DirectRequestRemovedDuringGroup<NNeuronTimeLearner>();}
TEST(NativeCompositeTraining,BranchDirectDataStopDuringNativeGroup){DirectRequestRemovedDuringGroup<NNeuronTimeLearnerBranch>();}

namespace {
template<class Owner> NativeTrainingPlan ServicePlan(NativeCompositeFixture<Owner>& f,double sync=.2) {
    NativeTrainingPlan p;p.protocol=f.protocol;p.probe=f.prototype;
    // The service validates the request declaration BEFORE creating its actor.
    // Direct actor fixtures fill these fields when a logical group is queued.
    p.probe.routing=p.protocol.routing;p.probe.protocolRevision=p.protocol.revision;
    p.maximumReferenceProbes=4;p.maximumInvalidReferenceProbes=0;p.maximumModelSeconds=120.;p.maximumWallSeconds=1800.;
    p.search.runId="actual-native-composite-service";p.search.initialModelRevision=f.Revision();
    p.search.maximumProbes=32;p.search.maximumEdits=4;p.search.maximumCandidatesPerInput=1;
    p.search.normalization=Normalization::SynapseCount;p.search.n0CandidateRepeats=1;p.search.tolerances.sync=sync;
    for(const auto& actual:f.owner->ReadNativeParameters())
        p.search.bounds.push_back({actual.length,actual.length,actual.synapses,actual.synapses,actual.resistance,actual.resistance});
    for(std::size_t i=0;i<f.protocol.inputs.size();++i) {
        const auto& w=f.protocol.compositeMeasurement->inputWindows[i];
        p.inputWindows.push_back({f.protocol.inputs[i].id,NativeCompositeFixture<Owner>::branch?0u:i,
            w.beginOffset,w.endOffset,f.protocol.inputs[i].stimulusId});
    }
    NativeCompositeTrainingPolicy policy;policy.contextPolicy=f.protocol.compositeMeasurement->contextPolicy;
    policy.geometryPolicy=f.protocol.compositeMeasurement->geometryPolicy;policy.maximumGroups=64;
    policy.maximumNativeProbes=256;policy.maximumTotalSamples=64*policy.contextPolicy.maximumTotalSamples;
    policy.maximumTotalPrimaryBytes=64*1024*1024;policy.maximumGroupModelSeconds=2.;policy.maximumGroupWallSeconds=300.;
    p.composite=policy;return p;
}
template<class Owner> void ServiceTicks(NativeCompositeFixture<Owner>& f,std::function<void()> afterTick={}) {
    std::size_t ticks=0;
    while(f.owner->NativeTrainingController().State()!=NativeTrainingState::Finished && ++ticks<120*2000) {
        f.model->Calculate();f.environment->IncreaseModelTimeByStep();if(afterTick)afterTick();
    }
    ASSERT_LT(ticks,120*2000u)<<f.owner->NativeTrainingController().Reason();
}
template<class Owner> void ServiceStart(NativeCompositeFixture<Owner>& f,NativeTrainingPlan plan) {
    f.attempt.reset();f.owner->BeginNativeTraining(std::move(plan));
    ASSERT_EQ(f.owner->NativeTrainingController().State(),NativeTrainingState::CapturingReferences)
        <<f.owner->NativeTrainingController().Reason();
}
template<class Owner> void ServiceExact(int mode) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);f.owner->CalculateMode=mode;
    std::size_t rawClosed=0;auto p=ServicePlan(f);p.observationSink=[&](const auto&){++rawClosed;};
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();ASSERT_TRUE(service.Certificate());
    ASSERT_TRUE(service.References());EXPECT_EQ(service.Certificate()->SchemaVersion(),2u);
    EXPECT_TRUE(f.owner->OwnedNativeCapacitanceState().isEmpty());
    EXPECT_EQ(service.CompositeReferenceGroupIds().size(),2u);EXPECT_EQ(service.CompositeFinalGroupIds().size(),2u);
    EXPECT_EQ(rawClosed,service.CompositeNativeProbes());EXPECT_EQ(rawClosed,f.preparations);
    EXPECT_EQ(rawClosed,4*service.CompositeGroups());EXPECT_EQ(service.CompositeSampledFrames(),f.rawSamples);
    EXPECT_EQ(service.Search()->IssuedProbes(),service.CompositeGroups()-2);
    EXPECT_EQ(service.Search()->AcceptedCompositeObservations(),service.Search()->IssuedProbes());
    std::size_t primary=0;for(const auto& record:service.CompositeMeasurements()) {
        EXPECT_TRUE(record.consumed);EXPECT_EQ(record.rawTrials.size(),4u);EXPECT_EQ(record.group.packets.size(),4u);
        EXPECT_TRUE(record.capacitanceWitnesses.empty());EXPECT_TRUE(record.nativeTrialWitnessIds.empty());
        primary+=CompositeRecordPrimaryBytes(record);
    }
    EXPECT_EQ(primary,service.CompositePrimaryBytes());
    const auto& source=service.CompositeSourceBinding();EXPECT_EQ(source["schema_version"].toInt(),2);
    EXPECT_TRUE(source["initial_native_snapshot"].isObject());EXPECT_TRUE(source["initial_dataset"].isObject());
}
template<class Owner> void ServiceDefaultSync() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f,.02);
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);EXPECT_FALSE(service.Certificate());
    ASSERT_TRUE(service.Search());const auto& negativeFinal=service.Search()->Certificate();ASSERT_TRUE(negativeFinal);
    // One configured sweep cannot promote an outside-tolerance final pass.
    EXPECT_FALSE(negativeFinal->Exact());EXPECT_DOUBLE_EQ(negativeFinal->Tolerances().sync,.02);
    EXPECT_GT(std::max(std::fabs(negativeFinal->Residuals().front().timingResidualLow),
        std::fabs(negativeFinal->Residuals().front().timingResidualHigh)),.02);
}
template<class Owner> void ServiceWarmReset() {
    NativeCompositeFixture<Owner> f(2000,false,64,true,true);auto p=ServicePlan(f);ServiceStart(f,p);ServiceTicks(f);
    const auto& old=f.owner->NativeTrainingController();ASSERT_EQ(old.Outcome(),TrainingStatus::Exact)<<old.Reason();
    const auto source=old.CompositeSourceBinding();const auto references=old.CompositeReferenceGroupIds();
    const auto oldProof=old.Certificate()->CompositeProofIds();const auto oldC0=f.owner->ReadNativeTrainingCapacitance()->origin;
    const auto prepared=f.preparations;f.owner->Reset();
    ASSERT_EQ(f.owner->NativeTrainingController().State(),NativeTrainingState::Idle);
    ASSERT_TRUE(f.owner->NativeTrainingController().References());
    f.owner->BeginNativeTraining(p);ASSERT_EQ(f.owner->NativeTrainingController().State(),NativeTrainingState::Searching)
        <<f.owner->NativeTrainingController().Reason();ServiceTicks(f);
    const auto& warm=f.owner->NativeTrainingController();ASSERT_EQ(warm.Outcome(),TrainingStatus::Exact)<<warm.Reason();
    EXPECT_EQ(warm.CompositeSourceBinding(),source);EXPECT_EQ(warm.CompositeReferenceGroupIds(),references);
    EXPECT_NE(warm.Certificate()->CompositeProofIds(),oldProof);EXPECT_EQ(f.owner->ReadNativeTrainingCapacitance()->origin,oldC0);
    EXPECT_EQ(f.preparations-prepared,4*warm.Search()->IssuedProbes());EXPECT_EQ(warm.SessionAttempt(),2u);
    EXPECT_EQ(warm.CompositeNativeProbes(),f.preparations-prepared);
    ASSERT_GE(warm.CompositeMeasurements().size(),2u);
    EXPECT_NE(warm.CompositeMeasurements().front().liveAttemptBinding,warm.CompositeMeasurements().back().liveAttemptBinding);
}
template<class Owner> void ServiceStopBeforeConsume(bool setter) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);bool stopped=false;
    p.beforeCompositeConsume=[&](const NativeCompositeMeasurementRecord& record){
        if(record.purpose==CompositeMeasurementPurpose::Final && !stopped) {
            stopped=true;if(setter)f.owner->IsNeedToTrain=false;else f.owner->IsNeedToTrain.SetDataDirect(false);
        }
    };
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_TRUE(stopped);EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);EXPECT_FALSE(service.Certificate());
    EXPECT_TRUE(service.CompositeFinalGroupIds().empty());ASSERT_FALSE(service.CompositeMeasurements().empty());
    EXPECT_FALSE(service.CompositeMeasurements().back().consumed);
}
template<class Owner> void ServicePreparedStop() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t prepared=0,closed=0;
    const auto original=p.probe.onPrepared;p.probe.onPrepared=[&](const auto& a,const auto& s){if(original)original(a,s);++prepared;f.owner->IsNeedToTrain=false;};
    p.observationSink=[&](const auto& result){++closed;EXPECT_EQ(result.status,NativeProbeStatus::Cancelled);};
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);EXPECT_EQ(prepared,1u);EXPECT_EQ(closed,1u);
    EXPECT_EQ(f.rawSamples,0u);EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    ASSERT_EQ(service.CompositeMeasurements().size(),1u);EXPECT_FALSE(service.CompositeMeasurements()[0].consumed);
    EXPECT_EQ(service.CompositeMeasurements()[0].rawTrials.size(),1u);
}
enum class RawSinkAction { Throw,Reset,Default,Retarget,RecursiveStop };
template<class Owner> void ServicePreparedSinkAction(RawSinkAction action) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t closed=0;
    const auto original=p.probe.onPrepared;p.probe.onPrepared=[&](const auto& a,const auto& s){
        if(original)original(a,s);f.owner->IsNeedToTrain=false;
    };
    p.observationSink=[&](const NativeProbeResult& packet){
        ++closed;EXPECT_EQ(closed,1u);EXPECT_EQ(packet.status,NativeProbeStatus::Cancelled);
        EXPECT_TRUE(packet.requiresFreshVerification);ASSERT_TRUE(packet.observation);EXPECT_FALSE(packet.observation->valid);
        EXPECT_EQ(f.owner->NativeTrainingController().State(),NativeTrainingState::Finished);
        if(action==RawSinkAction::Throw)throw std::runtime_error("intentional_cancelled_raw_sink_failure");
        if(action==RawSinkAction::Reset)f.owner->Reset();
        if(action==RawSinkAction::Default)f.owner->Default();
        if(action==RawSinkAction::Retarget){auto target=f.owner->InputPattern.GetData();target(1,0)+=.01;f.owner->InputPattern=target;}
        if(action==RawSinkAction::RecursiveStop){f.owner->IsNeedToTrain=false;f.owner->IsNeedToTrain=false;}
    };
    ServiceStart(f,p);
    for(std::size_t ticks=0;ticks<4000 && !closed;++ticks){f.model->Calculate();f.environment->IncreaseModelTimeByStep();}
    ASSERT_EQ(closed,1u);EXPECT_EQ(f.rawSamples,0u);const auto& service=f.owner->NativeTrainingController();
    EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    if(action==RawSinkAction::Reset){EXPECT_EQ(service.State(),NativeTrainingState::Idle);EXPECT_FALSE(service.CompositeSourceBinding().isEmpty());}
    else if(action==RawSinkAction::Default){EXPECT_EQ(service.State(),NativeTrainingState::Idle);EXPECT_TRUE(service.CompositeSourceBinding().isEmpty());EXPECT_TRUE(service.CompositeMeasurements().empty());}
    else if(action==RawSinkAction::Retarget){EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidModel);EXPECT_TRUE(service.CompositeSourceBinding().isEmpty());}
    else {
        EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);
        ASSERT_EQ(service.CompositeMeasurements().size(),1u);EXPECT_FALSE(service.CompositeMeasurements()[0].consumed);
        ASSERT_EQ(service.CompositeMeasurements()[0].rawTrials.size(),1u);EXPECT_TRUE(service.CompositeMeasurements()[0].rawTrials[0].packet);
        if(action==RawSinkAction::Throw)EXPECT_NE(service.Reason().find("raw_sink_failed"),std::string::npos);
    }
}
template<class Owner> void ServiceWarmDoesNotReplayCancelledRaw() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t closed=0;bool stopOnce=true;
    std::set<std::pair<std::string,std::string>> identities;
    const auto original=p.probe.onPrepared;p.probe.onPrepared=[&](const auto& a,const auto& s){
        if(original)original(a,s);if(stopOnce){stopOnce=false;f.owner->IsNeedToTrain=false;}
    };
    p.observationSink=[&](const NativeProbeResult& packet){
        ++closed;ASSERT_TRUE(packet.requestedSpecification);
        EXPECT_TRUE(identities.emplace(packet.requestedSpecification->runId,packet.requestedSpecification->trialId).second);
    };
    ServiceStart(f,p);ServiceTicks(f);ASSERT_EQ(closed,1u);ASSERT_EQ(f.owner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
    f.owner->Reset();f.owner->BeginNativeTraining(p);EXPECT_EQ(closed,1u);ServiceTicks(f);
    const auto& service=f.owner->NativeTrainingController();EXPECT_EQ(service.SessionAttempt(),2u);
    EXPECT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();EXPECT_TRUE(service.Certificate());
    EXPECT_EQ(closed,1+service.CompositeNativeProbes());EXPECT_EQ(identities.size(),closed);
}
template<class Owner> void ServiceNormalSink(bool reset) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t closed=0;
    p.observationSink=[&](const NativeProbeResult& packet){
        ++closed;EXPECT_EQ(packet.status,NativeProbeStatus::Completed);
        if(reset)f.owner->Reset();else throw std::runtime_error("intentional_normal_raw_sink_failure");
    };
    ServiceStart(f,p);
    for(std::size_t ticks=0;ticks<4000 && !closed;++ticks){f.model->Calculate();f.environment->IncreaseModelTimeByStep();}
    ASSERT_EQ(closed,1u);const auto& service=f.owner->NativeTrainingController();
    EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    if(reset)EXPECT_EQ(service.State(),NativeTrainingState::Idle);
    else {EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);EXPECT_NE(service.Reason().find("raw_sink_failed"),std::string::npos);}
}
template<class Owner> void ServiceInvalidRawStillDelivered() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t closed=0;bool changed=false;
    const auto original=p.probe.onSample;p.probe.onSample=[&](const auto& frame){
        if(original)original(frame);if(changed)return;changed=true;
        // Deliberate actual-physics fault, not a fabricated rejected packet.
        auto synapse=f.owner->template GetComponentL<NPulseSynapse>("Neuron.Dendrite1_2.ExcSynapse1",true);
        ASSERT_TRUE(synapse);synapse->Resistance=synapse->Resistance.GetData()*1.01;
    };
    p.observationSink=[&](const NativeProbeResult& packet){
        ++closed;ASSERT_TRUE(packet.requestedSpecification);ASSERT_TRUE(packet.observation);
        EXPECT_TRUE(packet.status!=NativeProbeStatus::Completed || !packet.observation->valid);
    };
    ServiceStart(f,p);ServiceTicks(f);EXPECT_TRUE(changed);EXPECT_EQ(closed,1u);
    const auto& service=f.owner->NativeTrainingController();EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);
    ASSERT_EQ(service.CompositeMeasurements().size(),1u);ASSERT_EQ(service.CompositeMeasurements()[0].rawTrials.size(),1u);
    EXPECT_TRUE(service.CompositeMeasurements()[0].rawTrials[0].packet);EXPECT_FALSE(service.CompositeMeasurements()[0].consumed);
}
template<class Owner> void ServiceSlowRawSinkUsesRealDeadline() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t closed=0;double elapsed=0.;
    p.maximumWallSeconds=1800.;p.composite->maximumGroupWallSeconds=15.;
    p.observationSink=[&](const NativeProbeResult& packet){
        ++closed;EXPECT_EQ(packet.status,NativeProbeStatus::Completed);
        if(closed==f.protocol.inputs.size()+2) {
            const double before=NativeTrainingWallTime();std::this_thread::sleep_for(std::chrono::seconds(16));
            elapsed=NativeTrainingWallTime()-before;
        }
    };
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_GE(elapsed,15.);EXPECT_EQ(closed,f.protocol.inputs.size()+2);
    EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    EXPECT_NE(service.Reason().find("group_time_budget"),std::string::npos);
    ASSERT_EQ(service.CompositeMeasurements().size(),1u);EXPECT_FALSE(service.CompositeMeasurements()[0].consumed);
}
template<class Owner> void ServiceCancelWithChangedC0StillTerminalizes() {
    NativeCompositeFixture<Owner> f(2000,false,64,true,true);auto p=ServicePlan(f);std::size_t closed=0;
    const auto original=p.probe.onPrepared;p.probe.onPrepared=[&](const auto& a,const auto& s){
        if(original)original(a,s);
        auto channel=f.owner->template GetComponentL<NPulseChannel>("Neuron.Dendrite1_2.ExcChannel",true);
        ASSERT_TRUE(channel);channel->Capacity=channel->Capacity.GetData()*1.01;
        f.owner->IsNeedToTrain=false;
    };
    p.observationSink=[&](const NativeProbeResult& packet){++closed;EXPECT_TRUE(packet.requiresFreshVerification);};
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_EQ(closed,1u);EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);
    EXPECT_FALSE(service.Certificate());EXPECT_FALSE(service.References());
    EXPECT_NE(service.Reason().find("cancel_C0_unverified"),std::string::npos);
    ASSERT_EQ(service.CompositeMeasurements().size(),1u);const auto& record=service.CompositeMeasurements()[0];
    EXPECT_FALSE(record.consumed);EXPECT_FALSE(record.capacitanceWitnesses.empty());
    ASSERT_EQ(record.rawTrials.size(),1u);EXPECT_TRUE(record.rawTrials[0].packet);
}
template<class Owner> void ServiceRecordSinkLifetime(bool postConsume,bool throws) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t fired=0;
    const auto callback=[&](const NativeCompositeMeasurementRecord& record){
        if(postConsume && throws && !(record.purpose==CompositeMeasurementPurpose::Final && record.consumed &&
            f.owner->NativeTrainingController().CompositeFinalGroupIds().size()==f.protocol.inputs.size()))return;
        ++fired;EXPECT_EQ(fired,1u);const auto id=record.groupId,origin=record.sourceOrigin;
        const auto count=record.rawTrials.size();EXPECT_FALSE(f.owner->NativeTrainingController().Certificate());
        if(throws)throw std::runtime_error("intentional_composite_record_sink_failure");
        f.owner->Default();
        // These references must name an independent snapshot after Default has
        // destroyed the service plan and its original records vector.
        EXPECT_EQ(record.groupId,id);EXPECT_EQ(record.sourceOrigin,origin);EXPECT_EQ(record.rawTrials.size(),count);
    };
    if(postConsume)p.compositeSink=callback;else p.beforeCompositeConsume=callback;
    ServiceStart(f,p);
    for(std::size_t ticks=0;ticks<120*2000 && !fired;++ticks){f.model->Calculate();f.environment->IncreaseModelTimeByStep();}
    ASSERT_EQ(fired,1u);const auto& service=f.owner->NativeTrainingController();EXPECT_FALSE(service.Certificate());
    if(throws){EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);EXPECT_NE(service.Reason().find("sink_failed"),std::string::npos);}
    else {EXPECT_EQ(service.State(),NativeTrainingState::Idle);EXPECT_TRUE(service.CompositeSourceBinding().isEmpty());EXPECT_TRUE(service.CompositeMeasurements().empty());}
}
template<class Owner> void ServiceLastCompositeSinkUsesRealGroupDeadline() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);bool slept=false;double elapsed=0.;
    p.maximumWallSeconds=1800.;p.composite->maximumGroupWallSeconds=15.;
    p.compositeSink=[&](const NativeCompositeMeasurementRecord& record){
        if(record.purpose!=CompositeMeasurementPurpose::Final || !record.consumed ||
            f.owner->NativeTrainingController().CompositeFinalGroupIds().size()!=f.protocol.inputs.size())return;
        EXPECT_FALSE(f.owner->NativeTrainingController().Certificate());
        slept=true;const double before=NativeTrainingWallTime();std::this_thread::sleep_for(std::chrono::seconds(16));
        elapsed=NativeTrainingWallTime()-before;
    };
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_TRUE(slept);EXPECT_GE(elapsed,15.);EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);
    EXPECT_FALSE(service.Certificate());EXPECT_NE(service.Reason().find("group_time_budget"),std::string::npos);
}
enum class MutableSinkStage { Raw,BeforeConsume,Composite };
template<class Owner> void ServiceMutableNthStop(MutableSinkStage stage) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);std::size_t seen=0;bool hit=false;
    if(stage==MutableSinkStage::Raw) {
        p.observationSink=[&,inside=0u](const NativeProbeResult&) mutable {
            ++seen;if(++inside==2){hit=true;f.owner->IsNeedToTrain=false;}
        };
    } else {
        const auto sink=[&,inside=0u](const NativeCompositeMeasurementRecord&) mutable {
            ++seen;if(++inside==2){hit=true;f.owner->IsNeedToTrain=false;}
        };
        if(stage==MutableSinkStage::BeforeConsume)p.beforeCompositeConsume=sink;else p.compositeSink=sink;
    }
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_TRUE(hit);EXPECT_EQ(seen,2u);EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);
    EXPECT_FALSE(service.Certificate());
}
template<class Owner> void ObsoleteActorCannotCancelForeignProbe() {
    {
    NativeCompositeFixture<Owner> f;const auto logical=f.Request(0,"old-owner","old-owner/1");
    f.attempt->StartMeasurement(logical,CompositeMeasurementPurpose::Reference,f.prototype,2.,300.,f.Time(),Wall());
    f.attempt->BeforeTick(f.Time(),Wall());ASSERT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Queued);
    f.owner->CancelNativeProbe("fixture_closes_old_trial");const auto old=f.owner->TakeNativeProbeResult();
    ASSERT_TRUE(old);ASSERT_TRUE(old->requestedSpecification);
    EXPECT_NE(old->status,NativeProbeStatus::Completed);EXPECT_TRUE(old->requiresFreshVerification);
    EXPECT_EQ(old->requestedSpecification->runId,"old-owner");
    auto foreign=f.prototype;foreign.specification.runId="separate-probe";foreign.specification.trialId="separate-probe/1";
    foreign.routing=f.protocol.routing;foreign.activeInput=0;foreign.inputId=f.protocol.inputs[0].id;
    foreign.protocolRevision=f.protocol.revision;foreign.baseModelRevision=f.Revision();
    foreign.readModelRevision=[&](){return f.Revision();};foreign.readFullModelRevision=foreign.readModelRevision;
    f.owner->QueueNativeProbe(foreign);f.attempt.reset();
    EXPECT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Queued);
    f.owner->CancelNativeProbe("fixture_closes_its_separate_probe");const auto result=f.owner->TakeNativeProbeResult();
    ASSERT_TRUE(result);ASSERT_TRUE(result->requestedSpecification);
    EXPECT_EQ(result->requestedSpecification->trialId,"separate-probe/1");
    }
    {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);
    const auto original=p.probe.onPrepared;p.probe.onPrepared=[&](const auto& a,const auto& s){if(original)original(a,s);f.owner->IsNeedToTrain=false;};
    ServiceStart(f,p);ServiceTicks(f);ASSERT_EQ(f.owner->NativeTrainingController().ObservedPackets().size(),1u);
    const auto old=f.owner->NativeTrainingController().ObservedPackets()[0];ASSERT_TRUE(old.requestedSpecification);
    f.owner->Reset();auto foreign=p.probe;foreign.specification=*old.requestedSpecification;
    foreign.activeInput=0;foreign.inputId=f.protocol.inputs[0].id;foreign.baseModelRevision=f.Revision();
    foreign.readModelRevision=[&](){return f.Revision();};foreign.readFullModelRevision=foreign.readModelRevision;
    // Reset permits the same text IDs, but this is a new actual executor
    // creation. The old service hook must not cancel or consume that request.
    f.owner->QueueNativeProbe(foreign);
    NativeLearnerLifecycle::InterruptComposite(*f.owner,"fixture_obsolete_service_hook");
    EXPECT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Queued);
    f.owner->CancelNativeProbe("fixture_closes_reused_text_id_probe");const auto result=f.owner->TakeNativeProbeResult();
    ASSERT_TRUE(result);ASSERT_TRUE(result->requestedSpecification);
    EXPECT_EQ(result->requestedSpecification->trialId,old.requestedSpecification->trialId);
    }
}
template<class Owner> void ActorDestructorDoesNotNotifyApplication() {
    NativeCompositeFixture<Owner> f;std::size_t callbacks=0;const auto request=f.Request(0,"destructor","destructor/1");
    f.attempt->StartMeasurement(request,CompositeMeasurementPurpose::Reference,f.prototype,2.,300.,f.Time(),Wall(),{},{},
        [&](const auto&){++callbacks;});
    f.attempt->BeforeTick(f.Time(),Wall());ASSERT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Queued);
    f.attempt.reset();EXPECT_EQ(callbacks,0u);EXPECT_NE(f.owner->NativeProbeState(),NativeProbeStatus::Queued);
}
template<class Owner> void ServicePartialReset(bool useDefault) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);ServiceStart(f,p);
    bool interrupted=false;
    for(std::size_t ticks=0;ticks<4000 && !interrupted;++ticks) {
        f.model->Calculate();f.environment->IncreaseModelTimeByStep();
        if(f.rawSamples) {interrupted=true;if(useDefault)f.owner->Default();else f.owner->Reset();}
    }
    EXPECT_TRUE(interrupted);const auto& service=f.owner->NativeTrainingController();
    EXPECT_EQ(service.State(),NativeTrainingState::Idle);EXPECT_FALSE(service.Certificate());
    if(useDefault){EXPECT_TRUE(service.CompositeSourceBinding().isEmpty());EXPECT_TRUE(service.CompositeMeasurements().empty());}
    else {EXPECT_FALSE(service.CompositeSourceBinding().isEmpty());ASSERT_EQ(service.CompositeMeasurements().size(),1u);
        EXPECT_FALSE(service.CompositeMeasurements().back().consumed);EXPECT_GT(service.CompositeMeasurements().back().sampledFrames,0u);}
}
template<class Owner> void ServiceRetarget() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);ServiceStart(f,p);
    for(std::size_t ticks=0;ticks<4000 && !f.rawSamples;++ticks){f.model->Calculate();f.environment->IncreaseModelTimeByStep();}
    ASSERT_GT(f.rawSamples,0u);auto target=f.owner->InputPattern.GetData();target(1,0)+=.01;
    f.owner->InputPattern=target;const auto& service=f.owner->NativeTrainingController();
    EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidModel);EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    EXPECT_TRUE(service.CompositeSourceBinding().isEmpty());EXPECT_TRUE(service.CompositeMeasurements().empty());
}
template<class Owner> void ServicePrimaryBudget() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto p=ServicePlan(f);p.composite->maximumTotalPrimaryBytes=1;
    ServiceStart(f,p);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
    EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);EXPECT_EQ(f.preparations,0u);EXPECT_EQ(f.rawSamples,0u);
    EXPECT_TRUE(service.CompositeMeasurements().empty());EXPECT_FALSE(service.Certificate());
}
}
TEST(NativeCompositeService,ClassicCalculateMode0Exact){ServiceExact<NNeuronTimeLearner>(0);}
TEST(NativeCompositeService,ClassicCalculateMode1Exact){ServiceExact<NNeuronTimeLearner>(1);}
TEST(NativeCompositeService,BranchCalculateMode0Exact){ServiceExact<NNeuronTimeLearnerBranch>(0);}
TEST(NativeCompositeService,BranchCalculateMode1Exact){ServiceExact<NNeuronTimeLearnerBranch>(1);}
TEST(NativeCompositeService,ClassicDefaultSyncOutsideTolerance){ServiceDefaultSync<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchDefaultSyncOutsideTolerance){ServiceDefaultSync<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicWarmResetPreservesInitialFamilyAndC0){ServiceWarmReset<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchWarmResetPreservesInitialFamilyAndC0){ServiceWarmReset<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicSetterStopBeforeFinalConsume){ServiceStopBeforeConsume<NNeuronTimeLearner>(true);}
TEST(NativeCompositeService,BranchSetterStopBeforeFinalConsume){ServiceStopBeforeConsume<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCompositeService,ClassicDirectDataStopBeforeFinalConsume){ServiceStopBeforeConsume<NNeuronTimeLearner>(false);}
TEST(NativeCompositeService,BranchDirectDataStopBeforeFinalConsume){ServiceStopBeforeConsume<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCompositeService,ClassicPreparedStopHasSingleRawResult){ServicePreparedStop<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchPreparedStopHasSingleRawResult){ServicePreparedStop<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicCancelledSinkThrowIsSingleAttempt){ServicePreparedSinkAction<NNeuronTimeLearner>(RawSinkAction::Throw);}
TEST(NativeCompositeService,BranchCancelledSinkThrowIsSingleAttempt){ServicePreparedSinkAction<NNeuronTimeLearnerBranch>(RawSinkAction::Throw);}
TEST(NativeCompositeService,ClassicCancelledSinkResetDoesNotFinishOldControl){ServicePreparedSinkAction<NNeuronTimeLearner>(RawSinkAction::Reset);}
TEST(NativeCompositeService,BranchCancelledSinkResetDoesNotFinishOldControl){ServicePreparedSinkAction<NNeuronTimeLearnerBranch>(RawSinkAction::Reset);}
TEST(NativeCompositeService,ClassicCancelledSinkDefaultCannotReviveFamily){ServicePreparedSinkAction<NNeuronTimeLearner>(RawSinkAction::Default);}
TEST(NativeCompositeService,BranchCancelledSinkDefaultCannotReviveFamily){ServicePreparedSinkAction<NNeuronTimeLearnerBranch>(RawSinkAction::Default);}
TEST(NativeCompositeService,ClassicCancelledSinkRetargetCannotBeOverwritten){ServicePreparedSinkAction<NNeuronTimeLearner>(RawSinkAction::Retarget);}
TEST(NativeCompositeService,BranchCancelledSinkRetargetCannotBeOverwritten){ServicePreparedSinkAction<NNeuronTimeLearnerBranch>(RawSinkAction::Retarget);}
TEST(NativeCompositeService,ClassicRecursiveStopDoesNotRepeatRawDelivery){ServicePreparedSinkAction<NNeuronTimeLearner>(RawSinkAction::RecursiveStop);}
TEST(NativeCompositeService,BranchRecursiveStopDoesNotRepeatRawDelivery){ServicePreparedSinkAction<NNeuronTimeLearnerBranch>(RawSinkAction::RecursiveStop);}
TEST(NativeCompositeService,ClassicWarmDoesNotReplayCancelledRaw){ServiceWarmDoesNotReplayCancelledRaw<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchWarmDoesNotReplayCancelledRaw){ServiceWarmDoesNotReplayCancelledRaw<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicNormalSinkThrowStopsBeforeConsume){ServiceNormalSink<NNeuronTimeLearner>(false);}
TEST(NativeCompositeService,BranchNormalSinkThrowStopsBeforeConsume){ServiceNormalSink<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCompositeService,ClassicNormalSinkResetHasNoStaleContinuation){ServiceNormalSink<NNeuronTimeLearner>(true);}
TEST(NativeCompositeService,BranchNormalSinkResetHasNoStaleContinuation){ServiceNormalSink<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCompositeService,ClassicInvalidActualPacketStillReachesSink){ServiceInvalidRawStillDelivered<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchInvalidActualPacketStillReachesSink){ServiceInvalidRawStillDelivered<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicSlowSinkCannotCrossRealDeadlineIntoConsume){ServiceSlowRawSinkUsesRealDeadline<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchSlowSinkCannotCrossRealDeadlineIntoConsume){ServiceSlowRawSinkUsesRealDeadline<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicObsoleteActorCannotCancelForeignProbe){ObsoleteActorCannotCancelForeignProbe<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchObsoleteActorCannotCancelForeignProbe){ObsoleteActorCannotCancelForeignProbe<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicDestructorDoesNotNotifyApplication){ActorDestructorDoesNotNotifyApplication<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchDestructorDoesNotNotifyApplication){ActorDestructorDoesNotNotifyApplication<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicC0MutationCannotPreventCancelledTerminalization){ServiceCancelWithChangedC0StillTerminalizes<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchC0MutationCannotPreventCancelledTerminalization){ServiceCancelWithChangedC0StillTerminalizes<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicBeforeConsumeDefaultUsesStableRecord){ServiceRecordSinkLifetime<NNeuronTimeLearner>(false,false);}
TEST(NativeCompositeService,BranchBeforeConsumeDefaultUsesStableRecord){ServiceRecordSinkLifetime<NNeuronTimeLearnerBranch>(false,false);}
TEST(NativeCompositeService,ClassicBeforeConsumeThrowStopsWithoutCertificate){ServiceRecordSinkLifetime<NNeuronTimeLearner>(false,true);}
TEST(NativeCompositeService,BranchBeforeConsumeThrowStopsWithoutCertificate){ServiceRecordSinkLifetime<NNeuronTimeLearnerBranch>(false,true);}
TEST(NativeCompositeService,ClassicCompositeSinkDefaultUsesStableRecord){ServiceRecordSinkLifetime<NNeuronTimeLearner>(true,false);}
TEST(NativeCompositeService,BranchCompositeSinkDefaultUsesStableRecord){ServiceRecordSinkLifetime<NNeuronTimeLearnerBranch>(true,false);}
TEST(NativeCompositeService,ClassicLastCompositeSinkThrowCannotPublishExact){ServiceRecordSinkLifetime<NNeuronTimeLearner>(true,true);}
TEST(NativeCompositeService,BranchLastCompositeSinkThrowCannotPublishExact){ServiceRecordSinkLifetime<NNeuronTimeLearnerBranch>(true,true);}
TEST(NativeCompositeService,ClassicLastCompositeSinkCannotCrossRealGroupDeadline){ServiceLastCompositeSinkUsesRealGroupDeadline<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchLastCompositeSinkCannotCrossRealGroupDeadline){ServiceLastCompositeSinkUsesRealGroupDeadline<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicMutableRawSinkStopsOnSecondActualPacket){ServiceMutableNthStop<NNeuronTimeLearner>(MutableSinkStage::Raw);}
TEST(NativeCompositeService,BranchMutableRawSinkStopsOnSecondActualPacket){ServiceMutableNthStop<NNeuronTimeLearnerBranch>(MutableSinkStage::Raw);}
TEST(NativeCompositeService,ClassicMutableBeforeConsumeStopsOnSecondActualGroup){ServiceMutableNthStop<NNeuronTimeLearner>(MutableSinkStage::BeforeConsume);}
TEST(NativeCompositeService,BranchMutableBeforeConsumeStopsOnSecondActualGroup){ServiceMutableNthStop<NNeuronTimeLearnerBranch>(MutableSinkStage::BeforeConsume);}
TEST(NativeCompositeService,ClassicMutableCompositeSinkStopsOnSecondActualGroup){ServiceMutableNthStop<NNeuronTimeLearner>(MutableSinkStage::Composite);}
TEST(NativeCompositeService,BranchMutableCompositeSinkStopsOnSecondActualGroup){ServiceMutableNthStop<NNeuronTimeLearnerBranch>(MutableSinkStage::Composite);}
TEST(NativeCompositeService,ClassicResetPreservesPartialEvidence){ServicePartialReset<NNeuronTimeLearner>(false);}
TEST(NativeCompositeService,BranchResetPreservesPartialEvidence){ServicePartialReset<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCompositeService,ClassicDefaultInvalidatesSourceFamily){ServicePartialReset<NNeuronTimeLearner>(true);}
TEST(NativeCompositeService,BranchDefaultInvalidatesSourceFamily){ServicePartialReset<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCompositeService,ClassicRetargetInvalidatesSourceFamily){ServiceRetarget<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchRetargetInvalidatesSourceFamily){ServiceRetarget<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeService,ClassicPrimaryBudgetStopsBeforeQueue){ServicePrimaryBudget<NNeuronTimeLearner>();}
TEST(NativeCompositeService,BranchPrimaryBudgetStopsBeforeQueue){ServicePrimaryBudget<NNeuronTimeLearnerBranch>();}

namespace {
template<class Owner> ConfiguredNativeTraining CompositeCold(NativeCompositeFixture<Owner>& f) {
    const auto p=ServicePlan(f);ConfiguredNativeTraining c;c.model=f.modelSpec;c.stimulusProfile=*f.protocol.stimulusProfile;
    c.runId="cold6-native-service";c.protocolRevision=f.protocol.revision;c.sampleId=f.protocol.sampleId;
    c.duration=f.prototype.specification.end;c.maximumSampleGap=f.protocol.maximumSampleGap;c.minimumAmplitude=f.protocol.minimumAmplitude;
    c.maximumSamples=f.prototype.specification.maximumSamples;c.peakSelection=PeakSelectionPolicy::IsolatedWindow;
    for(const auto& w:f.protocol.compositeMeasurement->inputWindows)c.windows.emplace_back(w.beginOffset,w.endOffset);
    c.search=p.search;c.search.runId=c.runId;c.search.initialModelRevision.clear();c.search.initialModelEpoch=0;
    c.maximumReferenceProbes=p.maximumReferenceProbes;c.maximumInvalidReferenceProbes=p.maximumInvalidReferenceProbes;
    c.maximumModelSeconds=p.maximumModelSeconds;c.maximumWallSeconds=p.maximumWallSeconds;c.composite=p.composite;return c;
}
template<class Owner> void ColdAndProtocolRoundtrip() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);const auto c=CompositeCold(f);
    const auto wire=EncodeConfiguredNativeTraining(c);EXPECT_EQ(wire["schema_version"].toInt(),6);
    EXPECT_EQ(EncodeConfiguredNativeTraining(DecodeConfiguredNativeTraining(wire)),wire);
    const auto protocol=MakeConfiguredNativeTrainingPlan(c).protocol;const auto encoded=EncodeVerificationProtocol(protocol);
    EXPECT_EQ(DecodeVerificationProtocol(encoded),protocol);EXPECT_EQ(encoded["schema_version"].toInt(),4);
    EXPECT_EQ(CompositeTrainingProtocolBinding(protocol),CompositeTrainingProtocolBinding(DecodeVerificationProtocol(encoded)));
    auto bad=wire;auto policy=bad["composite_measurement"].toObject();auto limits=policy["attempt_limits"].toObject();
    limits["maximum_groups"]=true;policy["attempt_limits"]=limits;bad["composite_measurement"]=policy;
    EXPECT_THROW(DecodeConfiguredNativeTraining(bad),std::invalid_argument);
    bad=wire;bad["base_schema_version"]=5;EXPECT_THROW(DecodeConfiguredNativeTraining(bad),std::invalid_argument);
    bad=wire;bad["schema_version"]=1;bad.remove("base_schema_version");EXPECT_THROW(DecodeConfiguredNativeTraining(bad),std::invalid_argument);
    auto source=wire["stimulus_profile"].toObject();source["use_transit_signal"]=true;bad=wire;bad["stimulus_profile"]=source;
    EXPECT_THROW(DecodeConfiguredNativeTraining(bad),std::invalid_argument);
    auto wrong=encoded;wrong["schema_version"]=3;EXPECT_THROW(DecodeVerificationProtocol(wrong),std::invalid_argument);
    wrong=encoded;auto geometry=wrong["composite_measurement"].toObject();geometry["unused"]=0;wrong["composite_measurement"]=geometry;
    EXPECT_THROW(DecodeVerificationProtocol(wrong),std::invalid_argument);
}
template<class Owner> void ColdAutostart(int mode) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);const auto c=CompositeCold(f);f.attempt.reset();
    // The production setter intentionally refuses ControllerVersion changes
    // while a native model is owned. Start a real cold owner before opting in.
    f.owner->Default();f.owner->SetGlobalTimeStep(2000);f.owner->EnablePostTrainTuning=false;
    f.owner->AutoCalibrateFixedLTZThreshold=false;f.owner->IsNeedToTrain=false;
    f.owner->CalculateMode=mode;f.owner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(c)).toJson(QJsonDocument::Compact).toStdString();
    f.owner->ControllerVersion=2;ASSERT_EQ(f.owner->ControllerVersion.GetData(),2);
    f.owner->Build();ASSERT_TRUE(f.owner->IsReady());f.model->Init();f.model->Reset();
    ASSERT_TRUE(f.owner->IsInit());ASSERT_TRUE(f.owner->ConfiguredModelInitialized.GetData());
    std::size_t raw=0,groups=0;ConfiguredNativeEvidenceSinks sinks;
    sinks.onPrepared=[&](const auto&,const auto&){++raw;};sinks.onComposite=[&](const auto&){++groups;};
    f.owner->SetConfiguredNativeEvidenceSinks(sinks);f.owner->IsNeedToTrain=true;ServiceTicks(f);
    const auto& service=f.owner->NativeTrainingController();ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();
    ASSERT_TRUE(service.Certificate());EXPECT_EQ(service.Plan().protocol.schemaVersion,4u);EXPECT_EQ(raw,4*groups);
    EXPECT_EQ(groups,service.CompositeGroups());EXPECT_EQ(raw,service.CompositeNativeProbes());
}
template<class Owner> void ActualDimensions(std::size_t n) {
    NativeCompositeFixture<Owner> f(2000,false,4,false,true,false,n,7200.);const auto groupLimit=(f.prototype.specification.end+.02)*(n+2)+.1;
    f.Run(f.Request(n-1,"dimensions","dimensions/last"),CompositeMeasurementPurpose::Reference,{},{},groupLimit,6000.);
    ASSERT_TRUE(f.attempt->Group());const auto& group=*f.attempt->Group();
    EXPECT_EQ(group.sourceIsi.size(),n);EXPECT_EQ(group.packets.size(),n+2);EXPECT_EQ(f.preparations,n+2);
    EXPECT_EQ(f.attempt->IssuedNativeProbes(),n+2);EXPECT_EQ(f.attempt->RetainedSamples(),f.rawSamples);
    ASSERT_TRUE(f.attempt->Selection())<<f.attempt->RejectionReason();
    EXPECT_NE(f.attempt->Selection()->status,NativeDeclaredWindowBasinStatus::Rejected);
    MatchedOmissionPrimary primary;std::vector<QString> paths;std::vector<const MatchedOmissionTrace*> traces{&group.witness.fullBefore};
    for(const auto& t:group.witness.omitEachInput)traces.push_back(&t);traces.push_back(&group.witness.fullAfter);
    for(std::size_t i=0;i<traces.size();++i){const auto path=QString("dimension-%1.csv").arg(qulonglong(i));paths.push_back(path);
        primary.emplace(path,EncodeMatchedOmissionPrimaryTrace(*traces[i],group.packets[i]));}
    EXPECT_NO_THROW(DecodeMatchedOmissionEvidence(EncodeMatchedOmissionEvidence(group,paths,primary),primary));
    if(f.attempt->Selection()->status==NativeDeclaredWindowBasinStatus::CausalityRejected) {
        EXPECT_FALSE(f.attempt->Measurement());EXPECT_FALSE(f.attempt->Selection()->geometry);EXPECT_FALSE(f.attempt->Selection()->reasons.empty());return;
    }
    ASSERT_TRUE(f.attempt->Selection()->geometry);const auto& selected=*f.attempt->Selection()->geometry;
    for(const auto& candidate:selected.candidates)EXPECT_EQ(candidate.controls.size(),n);
    if(selected.validity==DeclaredWindowBasinValidity::Valid && f.attempt->Selection()->status==NativeDeclaredWindowBasinStatus::Completed) {
        ASSERT_TRUE(f.attempt->Measurement());ASSERT_TRUE(selected.measuredMaximum);
        EXPECT_GE(selected.measuredMaximum->time,*f.attempt->Selection()->actualAssignedOnset);
    } else {EXPECT_FALSE(f.attempt->Measurement());EXPECT_FALSE(f.attempt->RejectionReason().empty());}
    // This is dimension/context/plumbing coverage, never a convergence claim.
}
}
TEST(NativeCompositeDeclarations,ClassicCold6AndProtocol4StrictRoundtrip){ColdAndProtocolRoundtrip<NNeuronTimeLearner>();}
TEST(NativeCompositeDeclarations,BranchCold6AndProtocol4StrictRoundtrip){ColdAndProtocolRoundtrip<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeAutostart,ClassicCalculateMode0){ColdAutostart<NNeuronTimeLearner>(0);}
TEST(NativeCompositeAutostart,ClassicCalculateMode1){ColdAutostart<NNeuronTimeLearner>(1);}
TEST(NativeCompositeAutostart,BranchCalculateMode0){ColdAutostart<NNeuronTimeLearnerBranch>(0);}
TEST(NativeCompositeAutostart,BranchCalculateMode1){ColdAutostart<NNeuronTimeLearnerBranch>(1);}
TEST(NativeCompositeDimensions,ClassicN4ActualLastInput){ActualDimensions<NNeuronTimeLearner>(4);}
TEST(NativeCompositeDimensions,BranchN4ActualLastInput){ActualDimensions<NNeuronTimeLearnerBranch>(4);}
TEST(NativeCompositeDimensions,ClassicN6ActualLastInput){ActualDimensions<NNeuronTimeLearner>(6);}
TEST(NativeCompositeDimensions,BranchN6ActualLastInput){ActualDimensions<NNeuronTimeLearnerBranch>(6);}

namespace {
void RebindArchive(QJsonObject& object){object.remove("artifact_document_sha256");object["artifact_document_sha256"]=NmsdkTools::CanonicalModelDataSha256(object);}
void SaveCompositeArchive(const NativeCompositeArchiveDocument& archive,const char* name) {
    const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");if(!output)return;const auto base=QString::fromLocal8Bit(output)+"/"+name;
    const auto write=[&](const QString& path,const QByteArray& bytes){const auto slash=path.lastIndexOf('/');Require(QDir().mkpath(path.left(slash)),"composite_archive_output_directory");
        QFile file(path);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"composite_archive_output_new_only");
        Require(file.write(bytes)==bytes.size() && file.flush(),"composite_archive_output_write");};
    write(base+"/composite-measurements/index.json",QJsonDocument(archive.document).toJson());
    for(const auto& [path,bytes]:archive.primary)write(base+"/"+path,bytes);
    const auto records=archive.document["records"].toArray();for(int i=0;i<records.size();++i)
        write(base+QString("/composite-measurements/group-%1.json").arg(i+1,6,10,QLatin1Char('0')),QJsonDocument(records[i].toObject()).toJson());
}
template<class Owner> void SaveCompositeBoundary(NativeCompositeFixture<Owner>& f,const char* name,std::optional<std::size_t> coreEpoch={}) {
    const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");if(!output)return;const auto base=QString::fromLocal8Bit(output)+"/"+name;
    Require(QDir().mkpath(base),"composite_boundary_output_directory");const auto write=[&](const char* name,const QJsonObject& data) {
        QFile file(base+"/"+name);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"composite_boundary_output_new_only");
        const auto bytes=QJsonDocument(data).toJson();Require(file.write(bytes)==bytes.size() && file.flush(),"composite_boundary_output_write");};
    const auto neuron=f.owner->template GetComponentL<NPulseNeuron>("Neuron",true);
    const auto dataset=f.owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    const auto generator=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    const auto snapshot=NmsdkTools::ExportPhysicalGraphForEdit(neuron.Get(),{{&generator->Output,"burst"}});
    QJsonArray parameters;for(const auto& p:f.owner->ReadNativeParameters())parameters.append(QJsonObject{
        {"length",p.length},{"synapses",p.synapses},{"resistance",p.resistance}});
    const auto& service=f.owner->NativeTrainingController();
    if(service.Plan().protocol.schemaVersion==4) {
        write("initial-configuration.json",service.CompositeInitialConfiguration());
        write("runtime-plan.json",EncodeCompositeRuntimePlan(service.Plan()));
    } else if(service.Plan().protocol.schemaVersion==5) {
        write("initial-configuration.json",service.CompositeInitialConfiguration());
        write("runtime-plan-scope.json",{{"kind","native_candidate_window_service_runtime_scope"},{"schema_version",1},
            {"runtime_plan2_exported",false},{"reason","separate runtime2/package6 codec stage pending"}});
    }
    QJsonObject boundary{
        {"kind","native_composite_fixture_actual_boundary"},{"schema_version",1},{"neuron",snapshot},
        {"dataset",NmsdkTools::ExportDatasetSnapshot(dataset.Get())},{"actual_inputs",parameters},
        {"model_revision",QString::fromStdString(f.Revision())},{"model_epoch",double(service.ModelEpoch())},
        {"optional_C0_state",f.owner->OwnedNativeCapacitanceState().isEmpty()?QJsonValue(QJsonValue::Null):QJsonValue(f.owner->OwnedNativeCapacitanceState())}};
    if(coreEpoch){boundary["model_epoch"]=double(*coreEpoch);boundary["model_epoch_scope"]="typed_core_controller";}
    write("after-model.json",boundary);
    QJsonArray references;if(service.References())for(const auto& ref:service.References()->Inputs())references.append(QJsonObject{
        {"input_id",QString::fromStdString(ref.id)},{"group_id",QString::fromStdString(ref.measurementGroupId)},
        {"semantic_proof_id",QString::fromStdString(ref.semanticProofId)},{"raw_potential",ref.rawPotential}});
    QJsonObject math{{"kind","native_composite_fixture_boundary_math"},{"schema_version",1},
        {"reference_complete",bool(service.References())},{"references",references},{"outcome",TrainingStatusName(service.Outcome())},
        {"reason",QString::fromStdString(service.Reason())},{"certificate",service.Certificate()?QJsonValue(EncodeTrainingCertificate(*service.Certificate())):QJsonValue(QJsonValue::Null)}};
    if(coreEpoch)math["scope"]="inactive_native_service_not_the_typed_core";
    write("boundary-math.json",math);
}
template<class Owner> QJsonObject& ActualServiceCertificateData(){static QJsonObject data;return data;}
template<class Owner> const NativeCompositeArchiveDocument& ActualServiceArchive() {
    // One real native service execution per topology/process. Later adversarial
    // cases replay immutable exported data; they do not synthesize waveforms.
    static std::optional<NativeCompositeArchiveDocument> archive;if(!archive) {
        NativeCompositeFixture<Owner> f(2000,false,64,false,true);ServiceStart(f,ServicePlan(f));ServiceTicks(f);
        const auto& service=f.owner->NativeTrainingController();Require(service.Outcome()==TrainingStatus::Exact,service.Reason().c_str());
        ActualServiceCertificateData<Owner>()=EncodeTrainingCertificate(*service.Certificate());
        archive=EncodeNativeCompositeTrainingArchive(service);const auto* name=NativeCompositeFixture<Owner>::branch?"branch-service":"classic-service";
        SaveCompositeArchive(*archive,name);SaveCompositeBoundary(f,name);
    }return *archive;
}
template<class Owner> void ArchiveRoundtrip() {
    const auto& archive=ActualServiceArchive<Owner>();const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document,[&](const QString& path){return archive.primary.at(path);});
    EXPECT_EQ(decoded.Document(),archive.document);EXPECT_EQ(decoded.ReferenceGroups().size(),2u);EXPECT_EQ(decoded.FinalGroups().size(),2u);
    EXPECT_EQ(decoded.Records().size(),archive.document["records"].toArray().size());
    const auto bytes=QJsonDocument(archive.document).toJson(QJsonDocument::Compact);EXPECT_NO_THROW(DecodeNativeCompositeTrainingArchive(bytes));
}
void MutateFirstRecord(QJsonObject& archive,const std::function<void(QJsonObject&)>& change) {
    auto records=archive["records"].toArray();auto record=records[0].toObject();change(record);records[0]=record;archive["records"]=records;RebindArchive(archive);
}
void ExpectArchiveReject(const std::function<void(QJsonObject&)>& change) {
    auto artifact=ActualServiceArchive<NNeuronTimeLearner>().document;change(artifact);EXPECT_THROW(DecodeNativeCompositeTrainingArchive(artifact),std::invalid_argument);
}
void ArchiveRename() {
    const auto& source=ActualServiceArchive<NNeuronTimeLearner>();auto renamed=source.document;auto records=renamed["records"].toArray();std::map<QString,QString> names;
    for(int i=0;i<records.size();++i){auto record=records[i].toObject();auto raw=record["raw_trials"].toArray();auto native=record["native_group"].toObject();auto traces=native["traces"].toArray();
        for(int j=0;j<raw.size();++j){auto item=raw[j].toObject();auto ref=item["primary_ref"].toObject();const auto old=ref["relative_path"].toString();const auto name="renamed/"+old;
            names.emplace(name,old);ref["relative_path"]=name;item["primary_ref"]=ref;raw[j]=item;auto trace=traces[j].toObject();trace["relative_path"]=name;traces[j]=trace;}
        record["raw_trials"]=raw;native["traces"]=traces;record["native_group"]=native;records[i]=record;}
    renamed["records"]=records;RebindArchive(renamed);EXPECT_NE(renamed["artifact_document_sha256"],source.document["artifact_document_sha256"]);
    const auto decoded=DecodeNativeCompositeTrainingArchive(renamed,[&](const QString& name){return source.primary.at(names.at(name));});
    ASSERT_EQ(decoded.Records().size(),source.document["records"].toArray().size());for(int i=0;i<records.size();++i)
        EXPECT_EQ(QString::fromStdString(decoded.Records()[i].semanticProofId),records[i].toObject()["measurement"].toObject()["semantic_proof_id"].toString());
}
void PartialArchive() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);ServiceStart(f,ServicePlan(f));bool stopped=false;
    ServiceTicks(f,[&](){if(f.rawSamples && !stopped){stopped=true;f.owner->IsNeedToTrain.SetDataDirect(false);}});
    ASSERT_EQ(f.owner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
    auto archive=EncodeNativeCompositeTrainingArchive(f.owner->NativeTrainingController());SaveCompositeArchive(archive,"classic-partial");SaveCompositeBoundary(f,"classic-partial");
    const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document);ASSERT_EQ(decoded.Records().size(),1u);
    EXPECT_FALSE(decoded.Records()[0].consumed);EXPECT_TRUE(decoded.Records()[0].semanticProofId.empty());EXPECT_TRUE(decoded.ReferenceGroups().empty());EXPECT_TRUE(decoded.FinalGroups().empty());
    MutateFirstRecord(archive.document,[](auto& r){r["consumed"]=true;r["training_requested_at_consume"]=true;});
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(archive.document),std::invalid_argument);
}
}
TEST(NativeCompositeArchive,ClassicActualServiceStrictReplay){ArchiveRoundtrip<NNeuronTimeLearner>();}
TEST(NativeCompositeArchive,BranchActualServiceStrictReplay){ArchiveRoundtrip<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeArchive,CsvRenameChangesDocumentOnly){ArchiveRename();}
TEST(NativeCompositeArchive,MissingExternalPrimaryCannotFallBack){const auto& a=ActualServiceArchive<NNeuronTimeLearner>();EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a.document,[](const QString&){return QByteArray{};}),std::invalid_argument);}
TEST(NativeCompositeArchive,ChangedExternalPrimaryRejected){const auto& a=ActualServiceArchive<NNeuronTimeLearner>();EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a.document,[&](const QString& p){return a.primary.at(p)+"0";}),std::invalid_argument);}
TEST(NativeCompositeArchive,ExtraEmbeddedBlobRejected){ExpectArchiveReject([](auto& a){auto blobs=a["primary_blobs"].toObject();const QByteArray bytes="unreferenced";blobs[QString::fromLatin1(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex())]=QJsonObject{{"bytes",double(bytes.size())},{"base64",QString::fromLatin1(bytes.toBase64())}};a["primary_blobs"]=blobs;RebindArchive(a);});}
TEST(NativeCompositeArchive,BooleanSchemaRejected){ExpectArchiveReject([](auto& a){a["schema_version"]=true;RebindArchive(a);});}
TEST(NativeCompositeArchive,BooleanCounterRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto c=r["counters"].toObject();c["native_probes"]=true;r["counters"]=c;});});}
TEST(NativeCompositeArchive,ChangedAttemptNamespaceRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){r["attempt_id"]="other-attempt";});});}
TEST(NativeCompositeArchive,ChangedCandidateModelRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto c=r["candidate_binding"].toObject();c["storage_images_sha256"]="changed";r["candidate_binding"]=c;r["candidate_witness_id"]=NmsdkTools::CanonicalModelDataSha256(c);});});}
TEST(NativeCompositeArchive,ChangedModelEpochRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto q=r["logical_request"].toObject();q["model_epoch"]=2;r["logical_request"]=q;});});}
TEST(NativeCompositeArchive,ChangedActualOriginRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto m=r["measurement"].toObject();m["actual_origin_time"]=m["actual_origin_time"].toDouble()+.01;r["measurement"]=m;});});}
TEST(NativeCompositeArchive,ChangedGeometryPolicyRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto policy=r["geometry_policy"].toObject();policy["repeatability_absolute"]=.5;r["geometry_policy"]=policy;});});}
TEST(NativeCompositeArchive,ChangedMeasuredPeakRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto m=r["measurement"].toObject();m["raw_potential"]=m["raw_potential"].toDouble()+1.;r["measurement"]=m;});});}
TEST(NativeCompositeArchive,ChangedActualEventTimestampRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto raw=r["raw_trials"].toArray();auto item=raw[0].toObject();auto events=item["actual_stimuli"].toArray();auto event=events[0].toObject();event["time"]=event["time"].toDouble()+.0005;events[0]=event;item["actual_stimuli"]=events;raw[0]=item;r["raw_trials"]=raw;});});}
TEST(NativeCompositeArchive,ChangedRawSpecificationRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto raw=r["raw_trials"].toArray();auto item=raw[0].toObject();auto spec=item["actual_specification"].toObject();spec["begin"]=spec["begin"].toDouble()+.0001;item["actual_specification"]=spec;raw[0]=item;r["raw_trials"]=raw;});});}
TEST(NativeCompositeArchive,MissingControlRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto raw=r["raw_trials"].toArray();raw.removeAt(1);r["raw_trials"]=raw;});});}
TEST(NativeCompositeArchive,DuplicateControlRejected){ExpectArchiveReject([](auto& a){MutateFirstRecord(a,[](auto& r){auto raw=r["raw_trials"].toArray();raw[1]=raw[0];r["raw_trials"]=raw;});});}
TEST(NativeCompositeArchive,StaleCurrentAttemptFinalsRejected){ExpectArchiveReject([](auto& a){a["current_attempt_id"]="another-current-attempt";auto c=a["counters"].toObject();c["attempt"]=QJsonObject{{"logical_groups",0},{"native_probes",0},{"sampled_frames",0}};a["counters"]=c;RebindArchive(a);});}
TEST(NativeCompositeArchive,ActualPartialStopNeverPromotes){PartialArchive();}

namespace {
template<class Owner> void SaveGrowthGroup(NativeCompositeFixture<Owner>& f,const char* stage) {
    const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");if(!output)return;
    const std::string relative=std::string(NativeCompositeFixture<Owner>::branch?"branch-growth/":"classic-growth/")+stage;
    const auto base=QString::fromLocal8Bit(output)+"/"+QString::fromStdString(relative);Require(QDir().mkpath(base),"growth_output_directory");
    const auto write=[&](const QString& name,const QByteArray& bytes){QFile file(base+"/"+name);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"growth_output_new_only");
        Require(file.write(bytes)==bytes.size() && file.flush(),"growth_output_write");};
    const auto& group=*f.attempt->Group();std::vector<const MatchedOmissionTrace*> traces{&group.witness.fullBefore};
    for(const auto& t:group.witness.omitEachInput)traces.push_back(&t);traces.push_back(&group.witness.fullAfter);
    MatchedOmissionPrimary primary;std::vector<QString> paths;for(std::size_t i=0;i<traces.size();++i) {
        const auto path=i==0?QString("full-before.csv"):i+1==traces.size()?QString("full-after.csv"):QString("omit-%1.csv").arg(qulonglong(i-1));
        paths.push_back(path);const auto bytes=EncodeMatchedOmissionPrimaryTrace(*traces[i],group.packets[i]);primary.emplace(path,bytes);write(path,bytes);
    }
    write("matched-witness.json",QJsonDocument(EncodeMatchedOmissionEvidence(group,paths,primary)).toJson());
    const auto& window=f.protocol.compositeMeasurement->inputWindows[0];write("declared-window.json",QJsonDocument(QJsonObject{
        {"kind","native_composite_window_limitation_fixture"},{"schema_version",1},{"diagnostic_only",true},{"training_certificate_eligible",false},
        {"source_binding",f.attempt->SourceBinding()},{"source_origin",QString::fromStdString(f.attempt->SourceOrigin())},
        {"assigned_input",0},{"window_begin_offset",window.beginOffset},{"window_end_offset",window.endOffset},
        {"geometry_policy",EncodeCompositeGeometryPolicy(f.protocol.compositeMeasurement->geometryPolicy)},
        {"selection",f.attempt->Selection()?QJsonValue(EncodeNativeCompositeSelection(*f.attempt->Selection())):QJsonValue(QJsonValue::Null)}}).toJson());
    SaveCompositeBoundary(f,relative.c_str());
}
template<class Owner> void GrowthLeavesInitialDeclaredWindow() {
    NativeCompositeFixture<Owner> f(2000,false,16,false,true);
    f.Run(f.Request(0,"growth-initial","growth-initial/0"),CompositeMeasurementPurpose::Reference);
    SaveGrowthGroup(f,"initial-broad");ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    const auto initial=*f.attempt->Selection()->geometry->measuredMaximum;
    const double initialOffset=initial.time-f.attempt->Group()->witness.fullBefore.observation.begin;
    // Declared NOW, before the edit and either subsequent independent group.
    // This is a geometry window, not a synchronization/training tolerance.
    const CompositeInputWindow initialWindow{initialOffset-.001,initial.plateauEnd-f.attempt->Group()->witness.fullBefore.observation.begin+.001};
    const auto broadWindow=f.protocol.compositeMeasurement->inputWindows[0];
    const auto resetAttempt=[&](){f.attempt.reset();const auto& c=f.protocol.compositeMeasurement->contextPolicy;
        f.attempt=std::make_unique<NativeCompositeTrainingAttempt>(*f.owner,f.protocol,
            CompositeAttemptLimits{16,64,16*c.maximumTotalSamples,120.,1800.},f.Time(),Wall());};
    f.protocol.compositeMeasurement->inputWindows[0]=initialWindow;resetAttempt();
    f.Run(f.Request(0,"growth-initial-tight","growth-initial-tight/0"),CompositeMeasurementPurpose::Reference);
    SaveGrowthGroup(f,"initial-tight");ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    f.attempt.reset();auto parameters=f.owner->ReadNativeParameters();ASSERT_EQ(parameters[0].length,2);
    parameters[0].length=3;const auto changed=f.owner->ApplyNativeParameters(parameters);
    ASSERT_EQ(changed.status,NativeEditStatus::Applied)<<changed.reason;
    f.protocol.compositeMeasurement->inputWindows[0]=broadWindow;
    resetAttempt();f.Run(f.Request(0,"growth-wide","growth-wide/0"),CompositeMeasurementPurpose::Reference);
    SaveGrowthGroup(f,"after-growth-wide");ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    const auto shifted=*f.attempt->Selection()->geometry->measuredMaximum;
    const auto shiftedOffset=shifted.time-f.attempt->Group()->witness.fullBefore.observation.begin;
    ASSERT_GT(shiftedOffset,initialWindow.endOffset); // Actual native measurement, no delay prediction.
    f.protocol.compositeMeasurement->inputWindows[0]=initialWindow;resetAttempt();
    f.Run(f.Request(0,"growth-initial-window","growth-initial-window/0"),CompositeMeasurementPurpose::Reference);
    SaveGrowthGroup(f,"after-growth-initial-window");ASSERT_TRUE(f.attempt->Selection());EXPECT_EQ(f.attempt->Selection()->status,NativeDeclaredWindowBasinStatus::Completed);
    ASSERT_TRUE(f.attempt->Selection()->geometry);EXPECT_NE(f.attempt->Selection()->geometry->validity,DeclaredWindowBasinValidity::Valid);
    EXPECT_FALSE(f.attempt->Measurement());EXPECT_FALSE(f.attempt->RejectionReason().empty());
    // These deliberately independent measurement families demonstrate a fixed
    // window limitation. They do not relabel an old capture or authorize Train.
}
}
TEST(NativeCompositeWindowLimitation,ClassicActualGrowthLeavesInitialWindow){GrowthLeavesInitialDeclaredWindow<NNeuronTimeLearner>();}
TEST(NativeCompositeWindowLimitation,BranchActualGrowthLeavesInitialWindow){GrowthLeavesInitialDeclaredWindow<NNeuronTimeLearnerBranch>();}

namespace {
void ActualC0Archive() {
    NativeCompositeFixture<NNeuronTimeLearnerBranch> f(2000,false,64,true,true);ServiceStart(f,ServicePlan(f));ServiceTicks(f);
    const auto& service=f.owner->NativeTrainingController();ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();
    const auto archive=EncodeNativeCompositeTrainingArchive(service);SaveCompositeArchive(archive,"branch-C0");SaveCompositeBoundary(f,"branch-C0");
    const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document);for(const auto& record:decoded.Records()) {
        ASSERT_EQ(record.nativeTrialWitnessIds.size(),4u);ASSERT_FALSE(record.capacitanceWitnesses.empty());
        for(const auto& [trial,id]:record.nativeTrialWitnessIds)EXPECT_EQ(record.capacitanceWitnesses.at(id).modelRevision,record.logical.baseModelRevision);
    }
}
void ActualWarmArchive() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);auto plan=ServicePlan(f);ServiceStart(f,plan);ServiceTicks(f);
    ASSERT_EQ(f.owner->NativeTrainingController().Outcome(),TrainingStatus::Exact);const auto initial=f.owner->NativeTrainingController().CompositeInitialConfiguration();
    const auto refs=f.owner->NativeTrainingController().CompositeReferenceGroupIds();f.owner->Reset();f.owner->BeginNativeTraining(plan);ServiceTicks(f);
    const auto& service=f.owner->NativeTrainingController();ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();
    const auto archive=EncodeNativeCompositeTrainingArchive(service);SaveCompositeArchive(archive,"classic-warm");SaveCompositeBoundary(f,"classic-warm");
    const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document);EXPECT_EQ(decoded.ReferenceGroups(),refs);EXPECT_EQ(service.CompositeInitialConfiguration(),initial);
    ASSERT_FALSE(decoded.Records().empty());EXPECT_NE(decoded.Records().front().attemptId,decoded.CurrentAttemptId());
    const auto counters=archive.document["counters"].toObject();EXPECT_EQ(counters["archive"].toObject()["groups"].toDouble(),
        counters["attempt"].toObject()["logical_groups"].toDouble()+2.);
}
void ActualAmbiguousArchive() {
    NativeCompositeFixture<NNeuronTimeLearnerBranch> f(2000,true,64,false,true);ServiceStart(f,ServicePlan(f));ServiceTicks(f);
    const auto& service=f.owner->NativeTrainingController();EXPECT_NE(service.Outcome(),TrainingStatus::Exact);EXPECT_FALSE(service.Certificate());
    const auto archive=EncodeNativeCompositeTrainingArchive(service);SaveCompositeArchive(archive,"branch-ambiguous");SaveCompositeBoundary(f,"branch-ambiguous");
    const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document);ASSERT_FALSE(decoded.Records().empty());const auto& record=decoded.Records().back();
    ASSERT_TRUE(record.selection);ASSERT_TRUE(record.selection->geometry);EXPECT_NE(record.selection->geometry->validity,DeclaredWindowBasinValidity::Valid);
    EXPECT_FALSE(record.consumed);EXPECT_TRUE(record.semanticProofId.empty());EXPECT_TRUE(decoded.FinalGroups().empty());
}
}
TEST(NativeCompositeArchive,ActualBoundC0RawWitnessesBindUnmutedBase){ActualC0Archive();}
TEST(NativeCompositeArchive,ActualWarmReferencesAreNotNewAttemptWork){ActualWarmArchive();}
TEST(NativeCompositeArchive,ActualMergedAmbiguousGroupStaysDiagnostic){ActualAmbiguousArchive();}

namespace {
template<class Owner> void SourceChangedBeforeConsume() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto plan=ServicePlan(f);bool changed=false;
    plan.beforeCompositeConsume=[&](const auto& record){if(record.purpose==CompositeMeasurementPurpose::Final && !changed){
        changed=true;const auto revision=f.Revision();const auto source=f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        source->Amplitude=1.5;EXPECT_EQ(f.Revision(),revision); // Source numbers are outside the neuron's boundary-port identity.
    }};
    ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();EXPECT_TRUE(changed);
    EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);EXPECT_FALSE(service.Certificate());EXPECT_TRUE(service.CompositeFinalGroupIds().empty());
    ASSERT_FALSE(service.CompositeMeasurements().empty());EXPECT_FALSE(service.CompositeMeasurements().back().consumed);
    EXPECT_NE(service.Reason().find("source_boundary_changed"),std::string::npos);
}
}
TEST(NativeCompositeSourceGuard,ClassicActualSourceChangedBetweenCloseAndConsume){SourceChangedBeforeConsume<NNeuronTimeLearner>();}
TEST(NativeCompositeSourceGuard,BranchActualSourceChangedBetweenCloseAndConsume){SourceChangedBeforeConsume<NNeuronTimeLearnerBranch>();}

namespace {
template<class Owner> void PortableFinalMath() {
    const auto& source=ActualServiceArchive<Owner>();const auto& expected=ActualServiceCertificateData<Owner>();
    const auto decoded=DecodeNativeCompositeTrainingArchive(source.document);const auto t=expected["tolerances"].toObject();
    const VerificationTolerances tolerances{t["amplitude_absolute"].toDouble(),t["amplitude_relative"].toDouble(),t["sync"].toDouble()};
    const auto proof=CompositePortableTrainingProof::Replay(decoded,tolerances,expected["model_revision"].toString().toStdString(),std::size_t(expected["model_epoch"].toDouble()));
    ASSERT_TRUE(proof.References());ASSERT_TRUE(proof.Certificate());EXPECT_EQ(EncodeTrainingCertificate(*proof.Certificate()),expected);
    EXPECT_FALSE(proof.Certificate()->Matches(proof.ModelRevision(),*proof.References(),tolerances,ModelStateKind::Recognition,proof.ModelEpoch()));
    EXPECT_THROW(CompositePortableTrainingProof::Replay(decoded,tolerances,"different-model",proof.ModelEpoch()),std::invalid_argument);
    EXPECT_THROW(CompositePortableTrainingProof::Replay(decoded,tolerances,proof.ModelRevision(),proof.ModelEpoch()+1),std::invalid_argument);
}
void PortableDefaultSync() {
    const auto& source=ActualServiceArchive<NNeuronTimeLearner>();const auto& expected=ActualServiceCertificateData<NNeuronTimeLearner>();
    const auto proof=CompositePortableTrainingProof::Replay(DecodeNativeCompositeTrainingArchive(source.document),
        {1e-5,0.,.02},expected["model_revision"].toString().toStdString(),std::size_t(expected["model_epoch"].toDouble()));
    ASSERT_TRUE(proof.Certificate());EXPECT_FALSE(proof.Certificate()->Exact());EXPECT_DOUBLE_EQ(proof.Certificate()->Tolerances().sync,.02);
    EXPECT_GT(std::max(std::fabs(proof.Certificate()->Residuals().front().timingResidualLow),
        std::fabs(proof.Certificate()->Residuals().front().timingResidualHigh)),.02);
}
const NativeCompositeArchiveDocument& ActualTwoSweepArchive() {
    static std::optional<NativeCompositeArchiveDocument> archive;if(!archive) {
        NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);auto plan=ServicePlan(f,.02);plan.search.maximumSweeps=2;
        ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
        Require(service.Outcome()==TrainingStatus::BudgetExhausted,"two_sweep_fixture_must_not_promote_outside_tolerance");Require(!service.Certificate(),"two_sweep_fixture_certificate");
        archive=EncodeNativeCompositeTrainingArchive(service);SaveCompositeArchive(*archive,"classic-two-final-sweeps");SaveCompositeBoundary(f,"classic-two-final-sweeps");
    }return *archive;
}
void FreshFinalSweeps(int selection) {
    const auto& source=ActualTwoSweepArchive();auto object=source.document;const auto decoded=DecodeNativeCompositeTrainingArchive(object);
    std::map<std::string,std::vector<std::string>> runs;for(const auto& record:decoded.Records())if(record.purpose==CompositeMeasurementPurpose::Final && record.consumed)
        runs[record.logical.runId].push_back(record.groupId);
    ASSERT_EQ(runs.size(),2u);for(const auto& [run,groups]:runs)EXPECT_EQ(groups.size(),2u);
    if(selection) {
        auto finals=object["final_group_ids"].toArray();const auto first=runs.begin()->second.front();finals[0]=QString::fromStdString(first);
        if(selection==2)finals[1]=QString::fromStdString(runs.begin()->second.back());
        object["final_group_ids"]=finals;RebindArchive(object);EXPECT_THROW(DecodeNativeCompositeTrainingArchive(object),std::invalid_argument);
    } else {
        const auto current=decoded.FinalGroups();ASSERT_EQ(current.size(),2u);for(const auto& id:current) {
            const auto found=std::find_if(decoded.Records().begin(),decoded.Records().end(),[&](const auto& r){return r.groupId==id;});
            ASSERT_NE(found,decoded.Records().end());EXPECT_EQ(found->logical.runId,runs.rbegin()->first);
        }
    }
}
template<class Owner> void RejectedWarmRetainsHistoricalData() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto plan=ServicePlan(f);ServiceStart(f,plan);ServiceTicks(f);
    const auto& before=f.owner->NativeTrainingController();ASSERT_EQ(before.Outcome(),TrainingStatus::Exact);
    const auto oldSource=before.CompositeSourceBinding();const auto refs=before.CompositeReferenceGroupIds();const auto count=before.CompositeMeasurements().size();
    const auto raw=f.preparations;const auto attempt=before.SessionAttempt();f.owner->Reset();plan.composite->maximumTotalPrimaryBytes=1;
    f.owner->BeginNativeTraining(plan);const auto& failed=f.owner->NativeTrainingController();EXPECT_EQ(failed.Outcome(),TrainingStatus::InvalidModel);
    EXPECT_FALSE(failed.Certificate());EXPECT_EQ(failed.SessionAttempt(),attempt);EXPECT_EQ(f.preparations,raw);
    EXPECT_EQ(failed.CompositeSourceBinding(),oldSource);EXPECT_EQ(failed.CompositeReferenceGroupIds(),refs);EXPECT_EQ(failed.CompositeMeasurements().size(),count);
    EXPECT_NO_THROW(DecodeNativeCompositeTrainingArchive(EncodeNativeCompositeTrainingArchive(failed).document));
}
}
TEST(NativeCompositePortableMath,ClassicMatchesLiveCertificateByteSemantics){PortableFinalMath<NNeuronTimeLearner>();}
TEST(NativeCompositePortableMath,BranchMatchesLiveCertificateByteSemantics){PortableFinalMath<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositePortableMath,DefaultSyncRemainsOutsideTolerance){PortableDefaultSync();}
TEST(NativeCompositePortableMath,CurrentFinalSetUsesOnlyLatestActualSweep){FreshFinalSweeps(0);}
TEST(NativeCompositePortableMath,MixedActualFinalSweepsRejected){FreshFinalSweeps(1);}
TEST(NativeCompositePortableMath,ClassicRejectedWarmKeepsHistoricalReferenceData){RejectedWarmRetainsHistoricalData<NNeuronTimeLearner>();}
TEST(NativeCompositePortableMath,BranchRejectedWarmKeepsHistoricalReferenceData){RejectedWarmRetainsHistoricalData<NNeuronTimeLearnerBranch>();}

TEST(NativeCompositePortableMath,WholeOlderActualFinalSweepRejected){FreshFinalSweeps(2);}


namespace {
constexpr const char* CompositePackageImplementation="native-composite-package-fixture-v1";
template<class Owner> void ConfigurePortableCold(NativeCompositeFixture<Owner>& f,bool c0=false,bool growth=false) {
    auto c=CompositeCold(f);c.recordCapacitanceHistory=c0;c.capacitanceMaximumRelativeChange=c0?.2:0.;
    if(growth){c.search.bounds.front().maximumLength=3;c.search.tolerances.sync=.02;c.search.maximumSweeps=2;}
    f.attempt.reset();
    f.owner->Default();f.owner->SetGlobalTimeStep(2000);f.owner->EnablePostTrainTuning=false;
    f.owner->AutoCalibrateFixedLTZThreshold=false;f.owner->IsNeedToTrain=false;f.owner->CalculateMode=1;
    f.owner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(c)).toJson(QJsonDocument::Compact).toStdString();
    f.owner->ControllerVersion=2;Require(f.owner->ControllerVersion.GetData()==2,"package_fixture_controller_readback");
    f.owner->Build();f.model->Init();f.model->Reset();Require(f.owner->IsReady() && f.owner->IsInit(),"package_fixture_not_ready");
    Require(f.owner->ConfiguredModelInitialized.GetData(),"package_fixture_cold_not_constructed");
}
void SavePortableObject(const char* directory,const char* name,const QJsonObject& document) {
    const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");if(!output)return;
    const auto base=QString::fromLocal8Bit(output)+"/"+directory;Require(QDir().mkpath(base),"package_fixture_directory");
    QFile file(base+"/"+name);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"package_fixture_new_only");
    const auto bytes=QJsonDocument(document).toJson();Require(file.write(bytes)==bytes.size() && file.flush(),"package_fixture_write");
}
template<class Owner> void SavePortableBoundary(NativeCompositeFixture<Owner>& f,const char* name,const QJsonObject& package) {
    SaveCompositeArchive(EncodeNativeCompositeTrainingArchive(f.owner->NativeTrainingController()),name);SaveCompositeBoundary(f,name);
    const bool stopped=package["kind"]==QJsonValue("timelearner_stopped_state");
    SavePortableObject(name,stopped?"train_stopped_state.json":"train_learned_state.json",package);
    SavePortableObject(name,stopped?"train_stopped_summary.json":"train_learned_summary.json",
        EncodeNativeTrainingState(f.owner->NativeTrainingController(),f.Revision(),f.owner->ReadNativeParameters()));
}
template<class Owner,bool C0=false> const QJsonObject& ActualPortablePackage() {
    static QJsonObject package;if(package.isEmpty()) {
        NativeCompositeFixture<Owner> f(2000,false,64,false,true);ConfigurePortableCold(f,C0);f.owner->IsNeedToTrain=true;ServiceTicks(f);
        Require(f.owner->NativeTrainingController().Outcome()==TrainingStatus::Exact,f.owner->NativeTrainingController().Reason().c_str());
        package=f.owner->ExportNativeLearnedState(CompositePackageImplementation);
        const auto name=C0?(NativeCompositeFixture<Owner>::branch?"package5-branch-C0":"package5-classic-C0"):
            (NativeCompositeFixture<Owner>::branch?"package5-branch":"package5-classic");SavePortableBoundary(f,name,package);
    }return package;
}
template<class Owner,bool C0=false> void PortablePackageRoundtrip(bool warm) {
    const auto source=ActualPortablePackage<Owner,C0>();NativeCompositeFixture<Owner> f(2000,false,64,false,true);f.attempt.reset();f.owner->IsNeedToTrain=false;
    const auto imported=f.owner->ImportNativeLearnedState(source,CompositePackageImplementation);ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    const auto& service=f.owner->NativeTrainingController();ASSERT_TRUE(service.Certificate());ASSERT_TRUE(service.References());
    EXPECT_EQ(f.Revision(),source["model_revision"].toString().toStdString());EXPECT_EQ(service.Plan().protocol.schemaVersion,4u);
    EXPECT_EQ(service.CompositeSourceBinding(),source["measurement_archive"].toObject()["source_binding"].toObject());
    EXPECT_FALSE(f.owner->IsNeedToTrain.GetData());EXPECT_EQ(f.owner->NativeProbeState(),NativeProbeStatus::Idle);
    const auto summary=EncodeNativeTrainingState(service,f.Revision(),f.owner->ReadNativeParameters());EXPECT_EQ(summary["schema_version"].toInt(),6);
    EXPECT_EQ(summary["search_history_retained"],QJsonValue(false));EXPECT_TRUE(summary["search_probes"].isNull());EXPECT_TRUE(summary["accepted_parameters"].isNull());
    EXPECT_EQ(f.owner->ExportNativeLearnedState(CompositePackageImplementation),source);
    if(!warm)return;
    const auto family=service.CompositeOwnerFamilyBinding();const auto binding=service.CompositeSourceBinding();const auto ids=service.CompositeReferenceGroupIds();
    const auto capture=service.CaptureRevision();const auto oldAttempt=service.SessionAttempt();const auto oldOrigin=f.owner->ReadNativeTrainingCapacitance();
    f.owner->Build();f.model->Init();f.model->Reset();ASSERT_TRUE(f.owner->IsReady());f.owner->IsNeedToTrain=true;ServiceTicks(f);
    const auto& restarted=f.owner->NativeTrainingController();ASSERT_EQ(restarted.Outcome(),TrainingStatus::Exact)<<restarted.Reason();
    EXPECT_EQ(restarted.CompositeSourceBinding(),binding);EXPECT_EQ(restarted.CompositeOwnerFamilyBinding(),family);EXPECT_EQ(restarted.CompositeReferenceGroupIds(),ids);
    EXPECT_EQ(restarted.CaptureRevision(),capture);EXPECT_EQ(restarted.SessionAttempt(),oldAttempt+1);EXPECT_EQ(f.owner->ReadNativeTrainingCapacitance(),oldOrigin);
    EXPECT_NE(restarted.Configuration().runId,source["runtime_plan"].toObject()["run_id"].toString().toStdString());
    const auto result=f.owner->ExportNativeLearnedState(CompositePackageImplementation);
    SavePortableBoundary(f,NativeCompositeFixture<Owner>::branch?(C0?"package5-branch-C0-warm":"package5-branch-warm"):
        (C0?"package5-classic-C0-warm":"package5-classic-warm"),result);
}
template<class Owner> const QJsonObject& ActualEditedStoppedPackage() {
    static QJsonObject package;if(package.isEmpty()) {
        NativeCompositeFixture<Owner> f(2000,false,64,false,true);ConfigurePortableCold(f,false,true);f.owner->IsNeedToTrain=true;
        bool edited=false;for(std::size_t tick=0;tick<60000 && f.owner->NativeTrainingController().State()!=NativeTrainingState::Finished;++tick) {
            f.model->Calculate();f.environment->IncreaseModelTimeByStep();
            if(f.owner->ReadNativeParameters().front().length==3){edited=true;f.owner->IsNeedToTrain=false;break;}
        }
        Require(edited,"owned_search_did_not_reach_declared_growth_control");
        Require(f.owner->NativeTrainingController().State()==NativeTrainingState::Finished,"edited_package_not_stopped");
        package=f.owner->ExportNativeLearnedState(CompositePackageImplementation);
        SavePortableBoundary(f,NativeCompositeFixture<Owner>::branch?"package5-branch-edited-stopped":"package5-classic-edited-stopped",package);
    }return package;
}
template<class Owner> void PortableEditedStopped() {
    const auto source=ActualEditedStoppedPackage<Owner>();NativeCompositeFixture<Owner> f(2000,false,64,false,true);f.attempt.reset();f.owner->IsNeedToTrain=false;
    ASSERT_EQ(source["schema_version"].toInt(),5);ASSERT_TRUE(source["certificate"].isNull());
    const auto imported=f.owner->ImportNativeLearnedState(source,CompositePackageImplementation);ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    EXPECT_EQ(f.owner->ReadNativeParameters().front().length,3);EXPECT_EQ(f.Revision(),source["model_revision"].toString().toStdString());
    EXPECT_NE(f.Revision(),source["capture_revision"].toString().toStdString());EXPECT_FALSE(f.owner->NativeTrainingController().Certificate());
    EXPECT_EQ(source["configuration"].toObject()["model"].toObject()["inputs"].toArray().at(0).toObject()["attachment"].toInt(),2);
    EXPECT_EQ(f.owner->ExportNativeLearnedState(CompositePackageImplementation),source);
}
template<class Owner> void PortablePartialStopped() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);ConfigurePortableCold(f);bool interrupted=false;ConfiguredNativeEvidenceSinks sinks;
    std::size_t sampled=0;sinks.onSample=[&](const auto&){++sampled;};
    f.owner->SetConfiguredNativeEvidenceSinks(sinks);f.owner->IsNeedToTrain=true;
    for(std::size_t tick=0;tick<4000 && !interrupted;++tick){f.model->Calculate();f.environment->IncreaseModelTimeByStep();
        if(sampled){interrupted=true;f.owner->IsNeedToTrain=false;}}
    ASSERT_TRUE(interrupted);
    const auto source=f.owner->ExportNativeLearnedState(CompositePackageImplementation);EXPECT_TRUE(source["certificate"].isNull());EXPECT_EQ(source["reference_complete"],QJsonValue(false));
    SavePortableBoundary(f,NativeCompositeFixture<Owner>::branch?"package5-branch-partial":"package5-classic-partial",source);
    const auto prepared=PrepareNativeLearnedState(source,f.storage,f.environment,CompositePackageImplementation);EXPECT_FALSE(prepared->service.References());EXPECT_FALSE(prepared->service.Certificate());
    EXPECT_EQ(prepared->service.CompositeMeasurements().size(),1u);EXPECT_FALSE(prepared->service.CompositeMeasurements().front().consumed);
}
void RebindPortable(QJsonObject& source){source.remove("sha256");source["sha256"]=NmsdkTools::CanonicalModelDataSha256(source);}
void PortableTamper(unsigned kind) {
    auto source=ActualPortablePackage<NNeuronTimeLearner>();NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);
    if(kind==0)source["unreleased_unknown_field"]=true;
    if(kind==1){auto values=source["trained_inputs"].toArray();auto first=values[0].toObject();first["length"]=3;values[0]=first;source["trained_inputs"]=values;}
    if(kind==2){auto cert=source["certificate"].toObject();cert["exact"]=false;source["certificate"]=cert;}
    if(kind==3){auto cfg=source["configuration"].toObject();auto model=cfg["model"].toObject();auto values=model["inputs"].toArray();auto first=values[0].toObject();
        first["attachment"]=3;values[0]=first;model["inputs"]=values;cfg["model"]=model;source["configuration"]=cfg;}
    if(kind==4){auto runtime=source["runtime_plan"].toObject();runtime["initial_model_revision"]="fake-template";source["runtime_plan"]=runtime;}
    RebindPortable(source);EXPECT_THROW(PrepareNativeLearnedState(source,f.storage,f.environment,CompositePackageImplementation),std::invalid_argument);
}
}
TEST(NativeCompositePackage,ClassicPhysicalRoundtrip){PortablePackageRoundtrip<NNeuronTimeLearner>(false);}
TEST(NativeCompositePackage,BranchPhysicalRoundtrip){PortablePackageRoundtrip<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCompositePackage,ClassicImportedWarmPreservesInitialFamily){PortablePackageRoundtrip<NNeuronTimeLearner>(true);}
TEST(NativeCompositePackage,BranchImportedWarmPreservesInitialFamily){PortablePackageRoundtrip<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCompositePackage,ClassicImportedC0WarmPreservesBaseline){PortablePackageRoundtrip<NNeuronTimeLearner,true>(true);}
TEST(NativeCompositePackage,BranchImportedC0WarmPreservesBaseline){PortablePackageRoundtrip<NNeuronTimeLearnerBranch,true>(true);}
TEST(NativeCompositePackage,ClassicStoppedActualEditIsNotInitialTemplate){PortableEditedStopped<NNeuronTimeLearner>();}
TEST(NativeCompositePackage,BranchStoppedActualEditIsNotInitialTemplate){PortableEditedStopped<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositePackage,ClassicPartialGroupNeverClaimsClosure){PortablePartialStopped<NNeuronTimeLearner>();}
TEST(NativeCompositePackage,BranchPartialGroupNeverClaimsClosure){PortablePartialStopped<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositePackage,UnknownPackageFieldRejected){PortableTamper(0);}
TEST(NativeCompositePackage,ChangedCurrentParametersRejected){PortableTamper(1);}
TEST(NativeCompositePackage,ChangedCertificateRejected){PortableTamper(2);}
TEST(NativeCompositePackage,FakeInitialTemplateRejected){PortableTamper(3);}
TEST(NativeCompositePackage,RuntimeInitialModelRelabelRejected){PortableTamper(4);}


namespace {
QByteArray CompositeFile(const QString& directory,const QString& name) {
    QFile file(QDir(directory).filePath(name));Require(file.open(QIODevice::ReadOnly),"composite_writer_test_primary_missing");return file.readAll();
}
template<class Owner> void PortableArtifactMirror(bool tamper=false,bool duplicate=false) {
    const auto package=ActualPortablePackage<Owner>();QTemporaryDir directory;ASSERT_TRUE(directory.isValid());QJsonArray artifacts;
    const auto ref=NmsdkWorker::PublishNativeCompositeArchive(directory.path(),package,artifacts).toObject();
    const auto index=ParseStrictNativeJsonObject(CompositeFile(directory.path(),"composite-measurements/index.json").toStdString());
    EXPECT_EQ(index,package["measurement_archive"].toObject());EXPECT_EQ(ref["bytes"],QJsonValue(double(CompositeFile(directory.path(),"composite-measurements/index.json").size())));
    const auto resolver=[&](const QString& name){return CompositeFile(directory.path(),name);};
    EXPECT_NO_THROW(DecodeNativeCompositeTrainingArchive(index,resolver));
    const auto records=index["records"].toArray();std::size_t primary=0;
    for(int i=0;i<records.size();++i) {
        const auto name=QString("composite-measurements/group-%1.json").arg(i+1,6,10,QLatin1Char('0'));
        EXPECT_EQ(ParseStrictNativeJsonObject(CompositeFile(directory.path(),name).toStdString()),records[i].toObject());
        primary+=std::size_t(records[i].toObject()["raw_trials"].toArray().size());
    }
    EXPECT_EQ(std::size_t(artifacts.size()),1+std::size_t(records.size())+primary);
    if(tamper){const auto path=records[0].toObject()["raw_trials"].toArray()[0].toObject()["primary_ref"].toObject()["relative_path"].toString();
        QFile file(QDir(directory.path()).filePath(path));ASSERT_TRUE(file.open(QIODevice::Append));ASSERT_EQ(file.write("0\n"),2);file.close();
        EXPECT_THROW(DecodeNativeCompositeTrainingArchive(index,resolver),std::invalid_argument);}
    if(duplicate){const auto before=CompositeFile(directory.path(),"composite-measurements/index.json");QJsonArray again;
        EXPECT_THROW(NmsdkWorker::PublishNativeCompositeArchive(directory.path(),package,again),std::invalid_argument);
        EXPECT_EQ(CompositeFile(directory.path(),"composite-measurements/index.json"),before);}
}
void PortableStreamCounters() {
    const auto package=ActualPortablePackage<NNeuronTimeLearner>();const auto archive=DecodeNativeCompositeTrainingArchive(package["measurement_archive"].toObject());
    QTemporaryDir directory;ASSERT_TRUE(directory.isValid());NmsdkWorker::EvidenceWriter stream(directory.path(),2);std::size_t trials=0,samples=0;
    for(const auto& record:archive.Records())for(const auto& raw:record.rawTrials) {
        ASSERT_TRUE(raw.packet);stream.Prepared(raw.prepared,raw.actual);for(const auto& sample:raw.samples){stream.Sample(sample);++samples;}
        stream.Observation(*raw.packet);++trials;
    }
    EXPECT_EQ(stream.NativeTrials(),trials);EXPECT_EQ(stream.SampledFrames(),samples);const auto files=stream.Finalize(false);EXPECT_EQ(std::size_t(files.size()),trials*2);
    const auto counters=package["measurement_archive"].toObject()["counters"].toObject()["attempt"].toObject();
    EXPECT_EQ(stream.NativeTrials(),std::size_t(counters["native_probes"].toDouble()));EXPECT_EQ(stream.SampledFrames(),std::size_t(counters["sampled_frames"].toDouble()));
}
void PortableExecutionEnvelope(bool preflight) {
    const QJsonObject base{{"kind",preflight?"timelearner_native_preflight_execution":"timelearner_native_training_execution"},
        {"schema_version",1},{"execution",preflight?"completed":"training_start_failed"}};
    const auto execution=NmsdkWorker::WrapNativeCompositeExecution(true,base,{},QJsonValue(QJsonValue::Null),"actual-model",0,0,preflight);
    EXPECT_EQ(execution["schema_version"],QJsonValue(3));EXPECT_EQ(execution["base_schema_version"],QJsonValue(1));
    EXPECT_EQ(execution["model_semantic_hash"],QJsonValue("actual-model"));EXPECT_TRUE(execution["source_origin"].isNull());EXPECT_TRUE(execution["measurement_archive"].isNull());
    const auto counters=execution["composite_counters"].toObject();if(preflight){EXPECT_EQ(counters["attempt"].toObject()["logical_groups"],QJsonValue(0));
        EXPECT_EQ(counters["archive"].toObject()["groups"],QJsonValue(0));}else{EXPECT_TRUE(counters["attempt"].isNull());EXPECT_TRUE(counters["archive"].isNull());}
    EXPECT_EQ(NmsdkWorker::WrapNativeCompositeExecution(false,base,{},QJsonValue(QJsonValue::Null),"actual-model",0,0),NmsdkWorker::Signed(base));
}
}
TEST(NativeCompositeConsoleArtifacts,ClassicAllPrimaryAndSidecarsMirrored){PortableArtifactMirror<NNeuronTimeLearner>();}
TEST(NativeCompositeConsoleArtifacts,BranchAllPrimaryAndSidecarsMirrored){PortableArtifactMirror<NNeuronTimeLearnerBranch>();}
TEST(NativeCompositeConsoleArtifacts,TamperedExternalMirrorRejected){PortableArtifactMirror<NNeuronTimeLearner>(true);}
TEST(NativeCompositeConsoleArtifacts,ExistingPrimaryNeverOverwritten){PortableArtifactMirror<NNeuronTimeLearner>(false,true);}
TEST(NativeCompositeConsoleArtifacts,ActualAllNPlus2StreamCounters){PortableStreamCounters();}
TEST(NativeCompositeConsoleArtifacts,PreflightKnownZeroAccounting){PortableExecutionEnvelope(true);}
TEST(NativeCompositeConsoleArtifacts,FailedStartNeverInventsArchiveAccounting){PortableExecutionEnvelope(false);}


namespace {
template<class Owner> void ActualPortableCliJob(bool defaultSync) {
    const auto package=ActualPortablePackage<Owner>();auto configuration=package["configuration"].toObject();
    configuration["run_id"]=QString("cli-composite-%1%2").arg(NativeCompositeFixture<Owner>::branch?"branch":"classic",defaultSync?"-default-sync":"");
    if(defaultSync){auto search=configuration["search"].toObject();auto tolerances=search["tolerances"].toObject();tolerances["sync"]=.02;
        search["tolerances"]=tolerances;search["maximum_sweeps"]=1;configuration["search"]=search;}
    const auto decoded=DecodeConfiguredNativeTraining(configuration);EXPECT_TRUE(decoded.composite);EXPECT_EQ(MakeConfiguredNativeTrainingPlan(decoded).protocol.schemaVersion,4u);
    const auto job=NmsdkWorker::Signed({{"kind","timelearner_native_training_job"},{"schema_version",1},
        {"owner_class",NativeCompositeFixture<Owner>::branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"},
        {"implementation_id",CompositePackageImplementation},{"configuration",configuration},{"profile_archives",QJsonArray{package["neuron"]}},
        {"optional_modes",QJsonObject{{"sync_capacitance_trim",0},{"post_train_tuning",false},{"auto_calibrate_threshold",false}}},
        {"calculate_mode",1},{"structure_build_mode",1},{"maximum_model_ticks",240000}});
    const auto name=NativeCompositeFixture<Owner>::branch?(defaultSync?"branch-default-sync-job.json":"branch-job.json"):
        (defaultSync?"classic-default-sync-job.json":"classic-job.json");SavePortableObject("native-composite-cli-inputs",name,job);
    EXPECT_EQ(job["configuration"].toObject()["model"].toObject()["inputs"].toArray()[0].toObject()["attachment"],QJsonValue(2));
    EXPECT_EQ(decoded.search.tolerances.sync,defaultSync?.02:.2);
    // The remote CLI must execute these actual profile/source declarations;
    // writing a job is not evidence that Train/evaluate ran or converged.
}
}
TEST(NativeCompositeConsoleJobs,ClassicActualProfileCold6Job){ActualPortableCliJob<NNeuronTimeLearner>(false);}
TEST(NativeCompositeConsoleJobs,BranchActualProfileCold6Job){ActualPortableCliJob<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCompositeConsoleJobs,ClassicDefaultSyncMustNotBecomeExact){ActualPortableCliJob<NNeuronTimeLearner>(true);}
TEST(NativeCompositeConsoleJobs,BranchDefaultSyncMustNotBecomeExact){ActualPortableCliJob<NNeuronTimeLearnerBranch>(true);}

namespace {
enum class FrameSpecTamper { None,MissingFrames,DuplicateControl,MissingControl,ChangedModel,ChangedEvent,ChangedRepeat,WrongGroup };
template<class Owner> void NativeFrameSpecification(FrameSpecTamper tamper=FrameSpecTamper::None,bool referenceTime=false,bool c0=false) {
    NativeCompositeFixture<Owner> f(2000,false,4,c0);
    // Fixed BEFORE queue, independent of the actual selected peak. This test
    // exercises native frame projection; it does not mint a policy proposal.
    CandidateWindowBasinSpecification declared;declared.inputId="input0";declared.assignedInput=0;
    declared.channel=NativeCompositeFixture<Owner>::branch?0u:0u;
    if(referenceTime)declared.referenceTime=CompositeInputWindow{.009,.07};
    else {declared.coordinateMode=CandidateWindowCoordinateMode::CandidateFrame;declared.candidateFrame=CandidateFrameWindow{18,140};}
    f.Run(f.Request(0,"frame-spec2","frame-spec2/reference"),CompositeMeasurementPurpose::Reference);
    ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();ASSERT_TRUE(f.attempt->Group());
    auto group=*f.attempt->Group();declared.groupId=group.specification.groupId;
    ASSERT_EQ(f.owner->OwnedNativeCapacitanceState().isEmpty(),!c0);
    const auto& original=*f.attempt->Selection()->geometry->measuredMaximum;
    if(tamper==FrameSpecTamper::MissingFrames)declared.candidateFrame=CandidateFrameWindow{18,100000};
    if(tamper==FrameSpecTamper::DuplicateControl)group.witness.omitEachInput.push_back(group.witness.omitEachInput.front());
    if(tamper==FrameSpecTamper::MissingControl)group.witness.omitEachInput.pop_back();
    if(tamper==FrameSpecTamper::ChangedModel)group.witness.fullBefore.currentBaseRevision="changed";
    if(tamper==FrameSpecTamper::ChangedEvent)group.witness.fullBefore.observation.events[0].time+=.0005;
    if(tamper==FrameSpecTamper::ChangedRepeat)group.witness.fullAfter.observation.channels[0].samples[30].rawPotential+=1.;
    if(tamper==FrameSpecTamper::WrongGroup)declared.groupId+="-wrong";
    const auto selected=SelectNativeDeclaredWindowBasinMaximum(declared,f.protocol.compositeMeasurement->geometryPolicy,group);
    if(tamper!=FrameSpecTamper::None) {
        EXPECT_EQ(selected.status,NativeDeclaredWindowBasinStatus::Rejected);EXPECT_FALSE(selected.geometry);EXPECT_FALSE(selected.reasons.empty());
        if(tamper==FrameSpecTamper::MissingFrames)EXPECT_EQ(selected.reasons.front(),"window_frames_not_captured");return;
    }
    ASSERT_EQ(selected.status,NativeDeclaredWindowBasinStatus::Completed);ASSERT_TRUE(selected.geometry);
    ASSERT_EQ(selected.geometry->validity,DeclaredWindowBasinValidity::Valid);ASSERT_TRUE(selected.geometry->measuredMaximum);
    const auto& peak=*selected.geometry->measuredMaximum;const auto& samples=group.witness.fullBefore.observation.channels[0].samples;
    EXPECT_DOUBLE_EQ(peak.rawPotential,original.rawPotential);EXPECT_DOUBLE_EQ(peak.time,original.time);
    EXPECT_DOUBLE_EQ(peak.time,samples.at(peak.firstSample).time);EXPECT_DOUBLE_EQ(peak.plateauEnd,samples.at(peak.lastSample).time);
    EXPECT_FALSE(NativeDeclaredWindowBasinResult::TrainingCertificateEligible);
    if(!referenceTime && !c0) {
        const std::string stage="frame-spec2-candidate";SaveGrowthGroup(f,stage.c_str());
        const std::string directory=std::string(NativeCompositeFixture<Owner>::branch?"branch-growth/":"classic-growth/")+stage;
        SavePortableObject(directory.c_str(),"frame-spec2.json",QJsonObject{{"kind","native_frame_spec2_diagnostic"},{"schema_version",1},
            {"training_certificate_eligible",false},{"frame_specification",EncodeCandidateWindowBasinSpecification(declared)},
            {"geometry_policy",EncodeCompositeGeometryPolicy(f.protocol.compositeMeasurement->geometryPolicy)},
            {"selection",EncodeNativeCompositeSelection(selected)}});
    }
}
}
TEST(NativeCandidateWindowFrames,ClassicActualFrameTimestampsAndOffWithoutC0){NativeFrameSpecification<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowFrames,BranchActualFrameTimestampsAndOffWithoutC0){NativeFrameSpecification<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowFrames,ClassicReferenceTimeSpec2KeepsSpec1Result){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::None,true);}
TEST(NativeCandidateWindowFrames,BranchReferenceTimeSpec2KeepsSpec1Result){NativeFrameSpecification<NNeuronTimeLearnerBranch>(FrameSpecTamper::None,true);}
TEST(NativeCandidateWindowFrames,ActualBoundC0DoesNotInventNewBaseline){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::None,false,true);}
TEST(NativeCandidateWindowFrames,MissingActualFramesNeverUseDtPadding){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::MissingFrames);}
TEST(NativeCandidateWindowFrames,DuplicateOmissionCannotReachGeometry){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::DuplicateControl);}
TEST(NativeCandidateWindowFrames,MissingOmissionCannotReachGeometry){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::MissingControl);}
TEST(NativeCandidateWindowFrames,ChangedActualModelCannotReachGeometry){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::ChangedModel);}
TEST(NativeCandidateWindowFrames,ChangedActualEventCannotReachGeometry){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::ChangedEvent);}
TEST(NativeCandidateWindowFrames,ChangedFullRepeatCannotReachGeometry){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::ChangedRepeat);}
TEST(NativeCandidateWindowFrames,ChangedDeclaredGroupCannotReachGeometry){NativeFrameSpecification<NNeuronTimeLearner>(FrameSpecTamper::WrongGroup);}

namespace {
template<class Owner> CandidateWindowPhysicalReadback ActualBankData(NativeCompositeFixture<Owner>& f) {
    // Attachment EXPECTATIONS in tests come from the separately declared fixture
    // model, not from the readback helper's output or its path formatter.
    std::vector<int> attachments;for(const auto& p:f.owner->ReadNativeParameters())attachments.push_back(p.length);
    return ReadNativeCandidateWindowPhysical(f.owner->NativeProbeModelBindings(),attachments,f.protocol,f.modelSpec,
        f.owner->ReadNativeTrainingCapacitance());
}
template<class Owner> void ExpectDeclaredBanks(NativeCompositeFixture<Owner>& f,const CandidateWindowPhysicalReadback& data) {
    ASSERT_EQ(data.inputBanks.size(),f.modelSpec.inputs.size());ASSERT_EQ(data.parameters.size(),f.modelSpec.inputs.size());
    for(std::size_t i=0;i<f.modelSpec.inputs.size();++i) {
        const auto& spec=f.modelSpec.inputs[i];const auto& bank=data.inputBanks[i];
        const std::string path="$.Dendrite"+std::to_string(NativeCompositeFixture<Owner>::branch?1:i+1)+"_"+std::to_string(spec.attachment);
        EXPECT_EQ(data.parameters[i].length,spec.attachment);EXPECT_EQ(data.parameters[i].synapses,spec.synapses);
        EXPECT_EQ(bank.inputOrdinal,i);EXPECT_EQ(bank.inputId,"input"+std::to_string(i));EXPECT_EQ(bank.stimulusId,"pulse"+std::to_string(i));
        EXPECT_EQ(bank.bankPath,path);EXPECT_EQ(bank.receiverPath,path+".ExcChannel");
        ASSERT_EQ(bank.excitationSynapsePaths.size(),std::size_t(spec.synapses));
        EXPECT_EQ(bank.excitationSynapsePaths.front(),path+".ExcSynapse1");
    }
}
template<class Owner> void ActualDistinctBankData(std::size_t n) {
    NativeCompositeFixture<Owner> f(2000,false,n+2,false,true,false,n,7200.,true);const auto data=ActualBankData(f);
    ExpectDeclaredBanks(f,data);EXPECT_FALSE(data.capacitance);EXPECT_EQ(f.preparations,0u);
    for(std::size_t i=0;i<n;++i)EXPECT_EQ(f.modelSpec.inputs[i].attachment,int(n-i));
    if(NativeCompositeFixture<Owner>::branch) {std::set<std::string> banks;for(const auto& b:data.inputBanks)banks.insert(b.bankPath);EXPECT_EQ(banks.size(),n);}
}
template<class Owner> void SaveNativeRoutingControl(NativeCompositeFixture<Owner>& f,std::size_t input,
    const CandidateWindowPhysicalReadback& before,const CandidateWindowPhysicalReadback& after,const QJsonArray& prepared) {
    const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");if(!output)return;
    const std::string directory=std::string(NativeCompositeFixture<Owner>::branch?"branch-distinct-routing-N":"classic-distinct-routing-N")+
        std::to_string(f.modelSpec.inputs.size())+"/input-"+std::to_string(input);
    const auto base=QString::fromLocal8Bit(output)+"/"+QString::fromStdString(directory);Require(QDir().mkpath(base),"routing_output_directory");
    const auto write=[&](const QString& name,const QByteArray& bytes){QFile file(base+"/"+name);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"routing_output_new_only");
        Require(file.write(bytes)==bytes.size() && file.flush(),"routing_output_write");};
    const auto& group=*f.attempt->Group();std::vector<const MatchedOmissionTrace*> traces{&group.witness.fullBefore};
    for(const auto& t:group.witness.omitEachInput)traces.push_back(&t);traces.push_back(&group.witness.fullAfter);
    MatchedOmissionPrimary primary;std::vector<QString> paths;
    for(std::size_t i=0;i<traces.size();++i) {
        const auto name=i==0?QString("full-before.csv"):i+1==traces.size()?QString("full-after.csv"):QString("omit-%1.csv").arg(qulonglong(i-1));
        const auto bytes=EncodeMatchedOmissionPrimaryTrace(*traces[i],group.packets[i]);paths.push_back(name);primary.emplace(name,bytes);write(name,bytes);
    }
    write("matched-witness.json",QJsonDocument(EncodeMatchedOmissionEvidence(group,paths,primary)).toJson());
    write("routing.json",QJsonDocument(QJsonObject{{"kind","native_candidate_window_routing_control"},{"schema_version",1},
        {"diagnostic_only",true},{"training_certificate_eligible",false},{"protocol",EncodeVerificationProtocol(f.protocol)},
        {"expected_fixture_model",EncodeNativeModelSpec(f.modelSpec)},{"assigned_input",double(input)},
        {"source_binding",f.attempt->SourceBinding()},{"source_origin",QString::fromStdString(f.attempt->SourceOrigin())},
        {"before",EncodeCandidateWindowPhysicalReadback(before)},{"after",EncodeCandidateWindowPhysicalReadback(after)},
        {"prepared_routes",prepared},{"selection",f.attempt->Selection()?QJsonValue(EncodeNativeCompositeSelection(*f.attempt->Selection())):QJsonValue(QJsonValue::Null)}}).toJson());
    SaveCompositeBoundary(f,directory.c_str());
}
template<class Owner> void ActualDistinctBankRouting(std::size_t n) {
    NativeCompositeFixture<Owner> f(2000,false,n+2,false,true,false,n,7200.,true);const auto initial=f.Revision();
    for(std::size_t input=0;input<n;++input) {
        const auto before=ActualBankData(f);ExpectDeclaredBanks(f,before);QJsonArray preparations;const auto caller=f.prototype.onPrepared;
        f.prototype.onPrepared=[&,input,caller](const auto& prepared,const auto& spec) {
            if(caller)caller(prepared,spec);const auto b=f.owner->NativeProbeModelBindings();
            EXPECT_NO_THROW(ValidateNativeCandidateWindowPreparedSelector(b,before,f.protocol,f.modelSpec,input,prepared));
            const auto source=f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
            QJsonArray connected;
            for(std::size_t i=0;i<n;++i) {
                const auto name="Dendrite"+std::to_string(NativeCompositeFixture<Owner>::branch?1:i+1)+"_"+std::to_string(f.modelSpec.inputs[i].attachment)+".ExcSynapse1";
                const auto synapse=b.neuron->template GetComponentL<NPulseSynapseCommon>(name,true);ASSERT_TRUE(synapse);
                const auto links=synapse->Input.GetDataSources();const bool active=links.size()==1 && links.front()==&source->Output;
                EXPECT_EQ(active,NativeCompositeFixture<Owner>::branch?i==input:true);connected.append(active);
                if(NativeCompositeFixture<Owner>::branch && i==input) {ASSERT_FALSE(b.soloSynapses.empty());EXPECT_EQ(b.soloSynapses.front(),synapse.Get());}
            }
            const auto identity=NmsdkTools::IdentifyModel(b.neuron.Get(),{{&source->Output,"burst"}});
            EXPECT_EQ(identity["sha256"],QJsonValue(QString::fromStdString(prepared.effectiveModelRevision)));
            preparations.append(QJsonObject{{"prepared",EncodeNativeProbePreparation(prepared)},{"actual_effective_identity",identity},{"actual_fixture_bank_connections",connected}});
        };
        const auto limit=(f.prototype.specification.end+.02)*(n+2)+.1;
        f.Run(f.Request(input,"distinct-routing","distinct-routing/"+std::to_string(input)),CompositeMeasurementPurpose::Reference,{},{},limit,600.);
        f.prototype.onPrepared=caller;ASSERT_TRUE(f.attempt->Group());const auto& group=*f.attempt->Group();
        ASSERT_EQ(group.reason,"omission_group_closed")<<f.attempt->RejectionReason();EXPECT_EQ(group.packets.size(),n+2);
        EXPECT_EQ(std::size_t(preparations.size()),n+2);const auto after=ActualBankData(f);ExpectDeclaredBanks(f,after);
        EXPECT_EQ(EncodeCandidateWindowPhysicalReadback(before),EncodeCandidateWindowPhysicalReadback(after));EXPECT_EQ(f.Revision(),initial);
        SaveNativeRoutingControl(f,input,before,after,preparations);
        // Geometry may honestly be Missing/Ambiguous for a declared window.
        // Routing/source dimension coverage makes no Exact or allN target claim.
    }
}
void SharedBankReadbackIsLegitimateData() {
    NativeCompositeFixture<NNeuronTimeLearnerBranch> f(2000,false,4,false,true,false,4);const auto data=ActualBankData(f);
    ExpectDeclaredBanks(f,data);ASSERT_EQ(data.inputBanks.size(),4u);
    EXPECT_EQ(data.inputBanks[0].bankPath,data.inputBanks[1].bankPath);EXPECT_EQ(data.inputBanks[1].bankPath,data.inputBanks[2].bankPath);
    EXPECT_NE(data.inputBanks[2].bankPath,data.inputBanks[3].bankPath);
}
void ActualWrongSelectorDataIsRejected() {
    NativeCompositeFixture<NNeuronTimeLearnerBranch> f(2000,false,4,false,true,false,2,1800.,true);const auto before=ActualBankData(f);
    const auto caller=f.prototype.onPrepared;std::size_t checked=0;
    f.prototype.onPrepared=[&](const auto& prepared,const auto& spec) {
        if(caller)caller(prepared,spec);auto b=f.owner->NativeProbeModelBindings();
        EXPECT_NO_THROW(ValidateNativeCandidateWindowPreparedSelector(b,before,f.protocol,f.modelSpec,1,prepared));
        const auto wrong=b.neuron->GetComponentL<NPulseSynapseCommon>("Dendrite1_2.ExcSynapse1",true);ASSERT_TRUE(wrong);ASSERT_FALSE(b.soloSynapses.empty());
        b.soloSynapses[0]=wrong.Get();EXPECT_THROW(ValidateNativeCandidateWindowPreparedSelector(b,before,f.protocol,f.modelSpec,1,prepared),std::invalid_argument);++checked;
    };
    f.Run(f.Request(1,"wrong-selector","wrong-selector/reference"),CompositeMeasurementPurpose::Reference);EXPECT_EQ(checked,4u);
}
}
TEST(NativeCandidateWindowBanks,ClassicN4ActualDistinctBankReadback){ActualDistinctBankData<NNeuronTimeLearner>(4);}
TEST(NativeCandidateWindowBanks,BranchN4ActualDistinctBankReadback){ActualDistinctBankData<NNeuronTimeLearnerBranch>(4);}
TEST(NativeCandidateWindowBanks,ClassicN6ActualDistinctBankReadback){ActualDistinctBankData<NNeuronTimeLearner>(6);}
TEST(NativeCandidateWindowBanks,BranchN6ActualDistinctBankReadback){ActualDistinctBankData<NNeuronTimeLearnerBranch>(6);}
TEST(NativeCandidateWindowBanks,ClassicN4EachActualInputRoutesNPlus2){ActualDistinctBankRouting<NNeuronTimeLearner>(4);}
TEST(NativeCandidateWindowBanks,BranchN4EachActualInputRoutesNPlus2){ActualDistinctBankRouting<NNeuronTimeLearnerBranch>(4);}
TEST(NativeCandidateWindowBanks,ClassicN6EachActualInputRoutesNPlus2){ActualDistinctBankRouting<NNeuronTimeLearner>(6);}
TEST(NativeCandidateWindowBanks,BranchN6EachActualInputRoutesNPlus2){ActualDistinctBankRouting<NNeuronTimeLearnerBranch>(6);}
TEST(NativeCandidateWindowBanks,BranchSharedBankIsLegitimateButNotDistinct){SharedBankReadbackIsLegitimateData();}
TEST(NativeCandidateWindowBanks,ActualPreparedWrongBankDescriptorRejected){ActualWrongSelectorDataIsRejected();}

namespace {
template<class Owner> void EnableCandidateWindow(NativeCompositeFixture<Owner>& f,const std::string& attemptId="candidate-attempt",
    std::size_t primaryBudget=128u*1024u*1024u) {
    f.attempt.reset();const auto fixed=*f.protocol.compositeMeasurement;
    f.protocol.schemaVersion=5;f.protocol.compositeMeasurement.reset();CandidateWindowMeasurementContract c;
    c.contextPolicy=fixed.contextPolicy;c.geometryPolicy=fixed.geometryPolicy;c.referenceInputWindows=fixed.inputWindows;
    // A declared narrow source/reference window, not adjusted after seeing
    // this family's observations. Growth must use a new candidate-frame spec.
    c.referenceInputWindows.front().endOffset=.035;
    c.candidateWindowPolicy.maximumFeatureTerms=4096;c.candidateWindowPolicy.inputs.resize(f.protocol.inputs.size());
    for(auto& input:c.candidateWindowPolicy.inputs) {
        // An explicit engineering proposal, frozen before capture. Neither the
        // candidate waveform nor its residual is used to tune these values.
        input.delayFramesPerSegment=f.frequency/100;input.baseLeftGuardFrames=f.frequency/100;
        input.baseRightGuardFrames=f.frequency/100;input.hardFirstFrame=1;
        input.hardLastFrame=f.prototype.specification.maximumSamples-1;
        input.maximumWindowFrames=f.frequency/20;
    }
    f.protocol.candidateWindowMeasurement=c;
    const auto groups=64u;const auto n=f.protocol.inputs.size();
    f.attempt=std::make_unique<NativeCompositeTrainingAttempt>(*f.owner,f.protocol,
        CompositeAttemptLimits{groups,groups*(n+2),groups*c.contextPolicy.maximumTotalSamples,120.,7200.},
        NativeCandidateWindowAttemptDeclaration{attemptId,primaryBudget},f.Time(),Wall());
}
template<class Owner> void SaveCandidateWindowGroup(NativeCompositeFixture<Owner>& f,const std::string& stage) {
    const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT");if(!output)return;
    const std::string directory=std::string(NativeCompositeFixture<Owner>::branch?"branch-native-window5/":"classic-native-window5/")+stage;
    const auto base=QString::fromLocal8Bit(output)+"/"+QString::fromStdString(directory);Require(QDir().mkpath(base),"window5_output_directory");
    const auto write=[&](const QString& name,const QByteArray& bytes){QFile file(base+"/"+name);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"window5_output_new_only");
        Require(file.write(bytes)==bytes.size() && file.flush(),"window5_output_write");};
    const auto record=f.attempt->Record();QJsonArray raw;
    for(std::size_t i=0;i<record.rawTrials.size();++i) {
        const auto& trial=record.rawTrials[i];const auto path=QString("raw-%1.csv").arg(qulonglong(i));
        write(path,EncodeCompositeRawPrimary(trial));raw.append(QJsonObject{{"path",path},{"prepared",EncodeNativeProbePreparation(trial.prepared)},
            {"actual_specification",EncodeNativeProbeSpecification(trial.actual)},{"packet",trial.packet?QJsonValue(EncodeNativeProbeEvidence(*trial.packet)):QJsonValue(QJsonValue::Null)}});
    }
    const auto& group=record.group;const bool complete=record.groupState==NativeMatchedOmissionState::Completed;
    if(complete) {
        std::vector<QString> paths;MatchedOmissionPrimary primary;
        for(std::size_t i=0;i<record.rawTrials.size();++i){const auto path=QString("raw-%1.csv").arg(qulonglong(i));paths.push_back(path);primary.emplace(path,EncodeCompositeRawPrimary(record.rawTrials[i]));}
        write("matched-witness.json",QJsonDocument(EncodeMatchedOmissionEvidence(group,paths,primary)).toJson());
    }
    write("window5-boundary.json",QJsonDocument(QJsonObject{{"kind","native_candidate_window5_factory_fixture"},{"schema_version",1},
        {"training_certificate_eligible",false},{"protocol",EncodeVerificationProtocol(f.protocol)},
        {"source_binding",f.attempt->SourceBinding()},{"source_origin",QString::fromStdString(f.attempt->SourceOrigin())},
        {"owner_family_binding",QString::fromStdString(f.attempt->OwnerFamilyBinding())},{"group_id",QString::fromStdString(record.groupId)},
        {"candidate_binding",ParseStrictNativeJsonObject(record.candidateBindingJson,128u*1024u*1024u)},
        {"method_specification",record.candidateWindowSpecification?QJsonValue(EncodeCandidateWindowBasinSpecification(*record.candidateWindowSpecification)):QJsonValue(QJsonValue::Null)},
        {"proposal",record.windowProposal?QJsonValue(EncodeCandidateWindowProposalData(*record.windowProposal)):QJsonValue(QJsonValue::Null)},
        {"semantic_proof_id",QString::fromStdString(record.semanticProofId)},{"complete_group",complete},{"raw_trials",raw},
        {"reason",QString::fromStdString(record.reason)},{"selection",record.selection?QJsonValue(EncodeNativeCompositeSelection(*record.selection)):QJsonValue(QJsonValue::Null)}}).toJson());
    SaveCompositeBoundary(f,directory.c_str());
}
template<class Owner> CapturedReferences CaptureWindowReferences(NativeCompositeFixture<Owner>& f,bool save=true,const std::string& prefix="reference",
    const std::string& attemptId="candidate-attempt") {
    f.referenceMeasurements.clear();
    for(std::size_t i=0;i<f.protocol.inputs.size();++i) {
        const std::string run=attemptId+"/capture/1";
        f.Run(f.Request(i,run,run+"/"+std::to_string(i)),CompositeMeasurementPurpose::Reference);
        if(save)SaveCandidateWindowGroup(f,prefix+"-"+std::to_string(i));
        Require(bool(f.attempt->Measurement()),f.attempt->RejectionReason().c_str());
        f.referenceMeasurements.push_back(*f.attempt->Measurement());EXPECT_EQ(f.attempt->CandidateWindowReferences(),nullptr);
    }
    auto references=CapturedReferences::CaptureComposite(f.protocol,f.referenceMeasurements);
    f.attempt->CompleteCandidateWindowReferences(references);return references;
}
template<class Owner> void WindowReferencesThenCandidate(unsigned hz=2000,bool c0=false,bool growth=false) {
    NativeCompositeFixture<Owner> f(hz,false,64,c0,true);EnableCandidateWindow(f);
    const auto initial=f.owner->ReadNativeParameters();const auto originalC0=f.owner->OwnedNativeCapacitanceState();
    const auto refs=CaptureWindowReferences(f);ASSERT_TRUE(f.attempt->CandidateWindowReferences());
    EXPECT_EQ(f.attempt->CandidateWindowReferences()->InputCount(),2u);EXPECT_EQ(refs.Inputs().size(),2u);
    const auto origin=f.attempt->SourceOrigin(),family=f.attempt->OwnerFamilyBinding();
    if(growth) {
        auto parameters=initial;parameters[0].length=3;const auto edit=f.owner->ApplyNativeParameters(parameters);
        ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;ASSERT_NE(f.Revision(),refs.InitialModelRevision());
    }
    const auto request=f.Request(0,"candidate-attempt","candidate-attempt/search/1",growth?1:0);
    bool prepared=false;f.Run(request,CompositeMeasurementPurpose::Search,[&](const auto&){prepared=true;});
    SaveCandidateWindowGroup(f,growth?"candidate-growth":c0?"candidate-C0":hz==20000?"candidate-20000":"candidate");
    ASSERT_TRUE(prepared);ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    const auto record=f.attempt->Record();ASSERT_TRUE(record.windowProposal);ASSERT_TRUE(record.candidateWindowSpecification);
    const auto& proposal=*record.windowProposal;EXPECT_EQ(proposal.reference.initialParameters,initial);
    EXPECT_EQ(proposal.referenceProofId,refs.Inputs()[0].semanticProofId);EXPECT_EQ(proposal.sourceOrigin,origin);EXPECT_EQ(proposal.ownerFamilyBinding,family);
    EXPECT_EQ(record.candidateWindowSpecification->coordinateMode,CandidateWindowCoordinateMode::CandidateFrame);
    EXPECT_EQ(record.candidateWindowSpecification->candidateFrame,proposal.computation.window);
    const auto& peak=*record.selection->geometry->measuredMaximum;const auto& full=record.group.witness.fullBefore.observation;
    const auto& samples=full.channels.at(0).samples;
    EXPECT_DOUBLE_EQ(peak.time,samples.at(peak.firstSample).time);EXPECT_DOUBLE_EQ(peak.rawPotential,samples.at(peak.firstSample).rawPotential);
    EXPECT_GE(peak.firstSample,proposal.computation.window->firstFrame);EXPECT_LE(peak.lastSample,proposal.computation.window->lastFrame);
    if(growth) {
        EXPECT_GT(peak.firstSample,proposal.reference.lastFrame+std::uint64_t(hz/1000));
        EXPECT_GT(peak.time-full.begin,f.protocol.candidateWindowMeasurement->referenceInputWindows[0].endOffset);
        EXPECT_EQ(proposal.computation.lengthChange,1u);EXPECT_EQ(proposal.computation.shiftFrames,std::int64_t(hz/100));
    }
    EXPECT_EQ(f.owner->OwnedNativeCapacitanceState(),originalC0); // Off has no invented baseline; bound C0 remains the original family.
    EXPECT_EQ(record.semanticProofId,CandidateWindowTrainingSemanticProofId(f.protocol,record));
    const auto binding=CandidateWindowProposalReplayFactory::CheckCandidateBinding(*f.attempt->CandidateWindowReferences(),f.protocol,
        ParseStrictNativeJsonObject(record.candidateBindingJson,128u*1024u*1024u));
    EXPECT_NO_THROW(CandidateWindowProposalReplayFactory::Replay(*f.attempt->CandidateWindowReferences(),f.protocol,binding,request,
        "candidate-attempt",record.groupId,f.prototype.specification.maximumSamples,CompositeMeasurementPurpose::Search,proposal));
    auto falseArithmetic=proposal;++falseArithmetic.computation.shiftFrames;
    falseArithmetic.windowRecipeId=NmsdkTools::CanonicalModelDataSha256(CandidateWindowRecipeContent(falseArithmetic)).toStdString();
    falseArithmetic.measurementInstanceId=NmsdkTools::CanonicalModelDataSha256(CandidateWindowInstanceContent(falseArithmetic)).toStdString();
    EXPECT_THROW(CandidateWindowProposalReplayFactory::Replay(*f.attempt->CandidateWindowReferences(),f.protocol,binding,request,
        "candidate-attempt",record.groupId,f.prototype.specification.maximumSamples,CompositeMeasurementPurpose::Search,falseArithmetic),std::invalid_argument);
    // This step supplies measurement factories, not a new search/final admission.
    FinalVerificationSession final(refs,{"candidate-attempt/final/1",f.Revision(),4,0,0});ASSERT_TRUE(final.NextRequest());
    EXPECT_THROW(final.ArmComposite(f.attempt->Measurement()->Prepared()),std::invalid_argument);
    EXPECT_THROW(final.ConsumeComposite(*f.attempt->Measurement(),f.Revision()),std::invalid_argument);EXPECT_FALSE(final.Certificate());
}
enum class WindowReferenceStop { NeedSetter,NeedDirect,NeedConnected,Reset,Default,ChangedModel,RebuiltSameSemanticGraph };
template<class Owner> void WindowReferenceBoundary(WindowReferenceStop action) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true,action==WindowReferenceStop::NeedConnected);EnableCandidateWindow(f);
    std::vector<ValidatedCompositeMeasurement> evidence;
    for(std::size_t i=0;i<2;++i){const std::string run="candidate-attempt/capture/1";
        f.Run(f.Request(i,run,run+"/"+std::to_string(i)),CompositeMeasurementPurpose::Reference);
        ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();evidence.push_back(*f.attempt->Measurement());}
    const auto refs=CapturedReferences::CaptureComposite(f.protocol,evidence);
    if(action==WindowReferenceStop::NeedSetter)f.owner->IsNeedToTrain=false;
    if(action==WindowReferenceStop::NeedDirect)f.owner->IsNeedToTrain.SetDataDirect(false);
    if(action==WindowReferenceStop::NeedConnected)f.flag->Value=false;
    if(action==WindowReferenceStop::Reset)f.owner->Reset();
    if(action==WindowReferenceStop::Default)f.owner->Default();
    if(action==WindowReferenceStop::ChangedModel){auto p=f.owner->ReadNativeParameters();p[0].resistance*=1.01;
        ASSERT_EQ(f.owner->ApplyNativeParameters(p).status,NativeEditStatus::Applied);}
    if(action==WindowReferenceStop::RebuiltSameSemanticGraph) {
        const auto original=f.owner->ReadNativeParameters();auto grown=original;grown[0].length=3;
        ASSERT_EQ(f.owner->ApplyNativeParameters(grown).status,NativeEditStatus::Applied);
        ASSERT_EQ(f.owner->ApplyNativeParameters(original).status,NativeEditStatus::Applied);
        ASSERT_EQ(f.Revision(),refs.InitialModelRevision());
    }
    EXPECT_THROW(f.attempt->CompleteCandidateWindowReferences(refs),std::exception);EXPECT_EQ(f.attempt->CandidateWindowReferences(),nullptr);
}
void PartialWindowReferencesCannotQueueCandidate() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);
    f.Run(f.Request(0,"candidate-attempt/capture/1","candidate-attempt/capture/1/0"),CompositeMeasurementPurpose::Reference);
    ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();EXPECT_EQ(f.attempt->CandidateWindowReferences(),nullptr);
    EXPECT_THROW(CapturedReferences::CaptureComposite(f.protocol,{*f.attempt->Measurement()}),std::invalid_argument);
    EXPECT_THROW(f.attempt->StartMeasurement(f.Request(0,"candidate-attempt","candidate-attempt/search/1"),CompositeMeasurementPurpose::Search,
        f.prototype,2.,300.,f.Time(),Wall()),std::invalid_argument);
    EXPECT_EQ(f.attempt->IssuedNativeProbes(),4u);
}
void WindowPrimaryReservationRejectsBeforeQueue() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f,"candidate-attempt",1);
    EXPECT_THROW(f.attempt->StartMeasurement(f.Request(0,"candidate-attempt/capture/1","candidate-attempt/capture/1/0"),CompositeMeasurementPurpose::Reference,
        f.prototype,2.,300.,f.Time(),Wall()),CompositeTrainingBudgetExhausted);
    EXPECT_EQ(f.attempt->IssuedNativeProbes(),0u);EXPECT_EQ(f.rawSamples,0u);
}
}
TEST(NativeCandidateWindowFactory,ClassicCompleteReferencesAndActualReplayedCandidate){WindowReferencesThenCandidate<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowFactory,BranchCompleteReferencesAndActualReplayedCandidate){WindowReferencesThenCandidate<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowFactory,Classic20000ActualReplayedCandidate){WindowReferencesThenCandidate<NNeuronTimeLearner>(20000);}
TEST(NativeCandidateWindowFactory,Branch20000ActualReplayedCandidate){WindowReferencesThenCandidate<NNeuronTimeLearnerBranch>(20000);}
TEST(NativeCandidateWindowFactory,ClassicGrowthKeepsImmutableP0AndUsesMovedFrameWindow){WindowReferencesThenCandidate<NNeuronTimeLearner>(2000,false,true);}
TEST(NativeCandidateWindowFactory,BranchGrowthKeepsImmutableP0AndUsesMovedFrameWindow){WindowReferencesThenCandidate<NNeuronTimeLearnerBranch>(2000,false,true);}
TEST(NativeCandidateWindowFactory,BoundC0UsesOriginalFamily){WindowReferencesThenCandidate<NNeuronTimeLearner>(2000,true);}
TEST(NativeCandidateWindowFactory,PartialReferencesNeverReleaseSeedSet){PartialWindowReferencesCannotQueueCandidate();}
TEST(NativeCandidateWindowFactory,PrimaryByteReservationBeforeQueue){WindowPrimaryReservationRejectsBeforeQueue();}
TEST(NativeCandidateWindowFactory,NeedSetterFalseBeforeReferenceCompletion){WindowReferenceBoundary<NNeuronTimeLearner>(WindowReferenceStop::NeedSetter);}
TEST(NativeCandidateWindowFactory,NeedDirectFalseBeforeReferenceCompletion){WindowReferenceBoundary<NNeuronTimeLearner>(WindowReferenceStop::NeedDirect);}
TEST(NativeCandidateWindowFactory,ConnectedNeedFalseBeforeReferenceCompletion){WindowReferenceBoundary<NNeuronTimeLearnerBranch>(WindowReferenceStop::NeedConnected);}
TEST(NativeCandidateWindowFactory,OwnerResetExpiresPreparedReferences){WindowReferenceBoundary<NNeuronTimeLearner>(WindowReferenceStop::Reset);}
TEST(NativeCandidateWindowFactory,OwnerDefaultExpiresPreparedReferences){WindowReferenceBoundary<NNeuronTimeLearnerBranch>(WindowReferenceStop::Default);}
TEST(NativeCandidateWindowFactory,ChangedNativeModelBeforeReferenceCompletion){WindowReferenceBoundary<NNeuronTimeLearner>(WindowReferenceStop::ChangedModel);}
TEST(NativeCandidateWindowFactory,RebuiltSameSemanticGraphCannotReviveReferences){WindowReferenceBoundary<NNeuronTimeLearner>(WindowReferenceStop::RebuiltSameSemanticGraph);}

namespace {
template<class Owner> const NativeCompositeArchiveDocument& ActualWindowArchive(bool c0=false) {
    static std::map<bool,NativeCompositeArchiveDocument> cached;const auto found=cached.find(c0);if(found!=cached.end())return found->second;
    NativeCompositeFixture<Owner> f(2000,false,64,c0,true);EnableCandidateWindow(f);CaptureWindowReferences(f);
    f.Run(f.Request(0,"candidate-attempt","candidate-attempt/search/1"),CompositeMeasurementPurpose::Search);
    Require(bool(f.attempt->Measurement()),f.attempt->RejectionReason().c_str());
    auto archive=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);
    const auto name=NativeCompositeFixture<Owner>::branch?(c0?"branch-window-archive2-C0":"branch-window-archive2"):
        (c0?"classic-window-archive2-C0":"classic-window-archive2");
    SaveCompositeArchive(archive,name);SaveCompositeBoundary(f,name);
    return cached.emplace(c0,std::move(archive)).first->second;
}
template<class Owner> void WindowArchiveReplay(bool c0=false) {
    const auto& archive=ActualWindowArchive<Owner>(c0);const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document,[&](const QString& p){return archive.primary.at(p);});
    EXPECT_EQ(decoded.Document(),archive.document);EXPECT_EQ(decoded.Protocol().schemaVersion,5u);EXPECT_EQ(decoded.ReferenceGroups().size(),2u);
    EXPECT_TRUE(decoded.FinalGroups().empty());const auto refs=CandidateWindowPortableReferenceFactory::Replay(decoded);
    EXPECT_EQ(refs.InputCount(),2u);EXPECT_EQ(refs.SourceOrigin(),decoded.SourceOrigin());EXPECT_EQ(refs.OwnerFamilyBinding(),decoded.OwnerFamilyBinding());
    EXPECT_NO_THROW(DecodeNativeCompositeTrainingArchive(QJsonDocument(archive.document).toJson(QJsonDocument::Compact)));
    EXPECT_THROW(CompositePortableTrainingProof::Replay(decoded,VerificationTolerances{},decoded.Records().back().logical.baseModelRevision,0),std::invalid_argument);
}
void WindowArchiveReject(const std::function<void(QJsonObject&)>& tamper) {
    auto data=ActualWindowArchive<NNeuronTimeLearner>().document;tamper(data);RebindArchive(data);
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(data),std::invalid_argument);
}
void MutateWindowRecord(QJsonObject& data,int index,const std::function<void(QJsonObject&)>& tamper) {
    auto records=data["records"].toArray();auto record=records[index].toObject();tamper(record);records[index]=record;data["records"]=records;
}
void WindowArchiveRename() {
    const auto& source=ActualWindowArchive<NNeuronTimeLearner>();auto data=source.document;auto records=data["records"].toArray();std::map<QString,QString> names;
    for(int i=0;i<records.size();++i) {auto record=records[i].toObject();auto raw=record["raw_trials"].toArray();auto native=record["native_group"].toObject();auto traces=native["traces"].toArray();
        for(int j=0;j<raw.size();++j){auto item=raw[j].toObject();auto ref=item["primary_ref"].toObject();const auto old=ref["relative_path"].toString();const auto name="renamed/"+old;
            names.emplace(name,old);ref["relative_path"]=name;item["primary_ref"]=ref;raw[j]=item;auto trace=traces[j].toObject();trace["relative_path"]=name;traces[j]=trace;}
        record["raw_trials"]=raw;native["traces"]=traces;record["native_group"]=native;records[i]=record;}
    data["records"]=records;RebindArchive(data);EXPECT_NE(data["artifact_document_sha256"],source.document["artifact_document_sha256"]);
    const auto replay=DecodeNativeCompositeTrainingArchive(data,[&](const QString& name){return source.primary.at(names.at(name));});
    const auto original=DecodeNativeCompositeTrainingArchive(source.document);ASSERT_EQ(replay.Records().size(),original.Records().size());
    for(std::size_t i=0;i<replay.Records().size();++i)EXPECT_EQ(replay.Records()[i].semanticProofId,original.Records()[i].semanticProofId);
}
void ReboundWindowClaimStillRequiresReplay(bool falsePhysicalReadback) {
    const auto& original=ActualWindowArchive<NNeuronTimeLearner>();const auto decoded=DecodeNativeCompositeTrainingArchive(original.document);
    auto record=decoded.Records().back();ASSERT_TRUE(record.windowProposal);auto& proposal=*record.windowProposal;
    if(falsePhysicalReadback) {
        auto binding=ParseStrictNativeJsonObject(record.candidateBindingJson,128u*1024u*1024u);auto physical=binding["physical_readback"].toObject();
        auto values=physical["parameters"].toArray();auto first=values[0].toObject();first["resistance"]=first["resistance"].toDouble()*1.1;
        values[0]=first;physical["parameters"]=values;binding["physical_readback"]=physical;
        record.candidateBindingJson=QJsonDocument(binding).toJson(QJsonDocument::Compact).toStdString();
        proposal.candidateBinding=NmsdkTools::CanonicalModelDataSha256(binding).toStdString();proposal.candidate.parameters[0].resistance*=1.1;
        proposal.computation=CalculateCandidateWindowArithmetic(decoded.Protocol().candidateWindowMeasurement->candidateWindowPolicy,proposal.reference,proposal.candidate);
        ASSERT_EQ(proposal.computation.status,CandidateWindowComputationStatus::Computed);
    } else ++proposal.computation.shiftFrames;
    proposal.windowRecipeId=NmsdkTools::CanonicalModelDataSha256(CandidateWindowRecipeContent(proposal)).toStdString();
    proposal.measurementInstanceId=NmsdkTools::CanonicalModelDataSha256(CandidateWindowInstanceContent(proposal)).toStdString();
    EXPECT_NO_THROW(DecodeCandidateWindowProposalData(EncodeCandidateWindowProposalData(proposal)));
    record.semanticProofId=CandidateWindowTrainingSemanticProofId(decoded.Protocol(),record);
    auto data=original.document;MutateWindowRecord(data,2,[&](auto& wire){wire["window_proposal"]=EncodeCandidateWindowProposalData(proposal);
        const auto binding=ParseStrictNativeJsonObject(record.candidateBindingJson,128u*1024u*1024u);wire["candidate_binding"]=binding;
        wire["candidate_witness_id"]=NmsdkTools::CanonicalModelDataSha256(binding);auto measured=wire["measurement"].toObject();
        measured["semantic_proof_id"]=QString::fromStdString(record.semanticProofId);wire["measurement"]=measured;});RebindArchive(data);
    // Every public content ID is self-consistent; rejection must still follow
    // from real graph/control-knob or independently recomputed policy facts.
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(data),std::invalid_argument);
}
void WindowInstanceBindingIsSemanticContent() {
    const auto& original=ActualWindowArchive<NNeuronTimeLearner>();const auto decoded=DecodeNativeCompositeTrainingArchive(original.document);
    auto record=decoded.Records().back();const auto changed=record.group.specification.modelInstanceBinding+"-changed";
    record.group.specification.modelInstanceBinding=changed;record.group.witness.fullBefore.modelInstanceBinding=changed;
    record.group.witness.fullAfter.modelInstanceBinding=changed;for(auto& control:record.group.witness.omitEachInput)control.modelInstanceBinding=changed;
    EXPECT_NE(CandidateWindowTrainingSemanticProofId(decoded.Protocol(),record),record.semanticProofId);
    auto data=original.document;MutateWindowRecord(data,2,[&](auto& r){auto native=r["native_group"].toObject();
        auto spec=native["specification"].toObject();spec["model_instance_binding"]=QString::fromStdString(changed);native["specification"]=spec;
        auto traces=native["traces"].toArray();for(int i=0;i<traces.size();++i){auto trace=traces[i].toObject();auto binding=trace["binding"].toObject();
            binding["model_instance_binding"]=QString::fromStdString(changed);trace["binding"]=binding;traces[i]=trace;}
        native["traces"]=traces;r["native_group"]=native;});RebindArchive(data);
    // Consistent changed opaque labels are DATA, not a new execution claim.
    // They nevertheless cannot reuse the previous measurement content ID.
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(data),std::invalid_argument);
}
template<class Owner> void WindowArchiveWarm(bool c0=false) {
    NativeCompositeFixture<Owner> f(2000,false,64,c0,true);EnableCandidateWindow(f);const auto references=CaptureWindowReferences(f);
    const auto cold=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);const auto replay=DecodeNativeCompositeTrainingArchive(cold.document);
    const auto originalParameters=f.owner->ReadNativeParameters();const auto source=f.attempt->SourceOrigin(),family=f.attempt->OwnerFamilyBinding();
    f.attempt.reset();auto candidate=originalParameters;candidate[0].length=3;
    const auto edit=f.owner->ApplyNativeParameters(candidate);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    f.owner->Reset();f.owner->IsNeedToTrain=true;const auto& context=f.protocol.candidateWindowMeasurement->contextPolicy;
    f.attempt=std::make_unique<NativeCompositeTrainingAttempt>(*f.owner,replay,CompositeAttemptLimits{64,256,64*context.maximumTotalSamples,120.,7200.},
        NativeCandidateWindowAttemptDeclaration{"warm-candidate",128u*1024u*1024u},f.Time(),Wall());
    ASSERT_TRUE(f.attempt->CandidateWindowReferences());EXPECT_EQ(f.attempt->SourceOrigin(),source);EXPECT_EQ(f.attempt->OwnerFamilyBinding(),family);
    EXPECT_EQ(f.attempt->IssuedGroups(),0u);EXPECT_EQ(f.attempt->IssuedNativeProbes(),0u);
    f.Run(f.Request(0,"warm-candidate","warm-candidate/search/1",1),CompositeMeasurementPurpose::Search);ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    const auto record=f.attempt->Record();ASSERT_TRUE(record.windowProposal);EXPECT_EQ(record.windowProposal->reference.initialParameters,originalParameters);
    EXPECT_EQ(record.windowProposal->referenceProofId,references.Inputs()[0].semanticProofId);EXPECT_EQ(record.windowProposal->computation.lengthChange,1u);
    EXPECT_EQ(f.attempt->CandidateWindowRecords().size(),3u);const auto after=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);
    const auto decoded=DecodeNativeCompositeTrainingArchive(after.document);EXPECT_EQ(decoded.ReferenceGroups(),replay.ReferenceGroups());
    EXPECT_EQ(decoded.CurrentAttemptId(),"warm-candidate");EXPECT_EQ(decoded.Records()[0].semanticProofId,replay.Records()[0].semanticProofId);
    const auto counters=after.document["counters"].toObject();EXPECT_EQ(counters["attempt"].toObject()["logical_groups"],QJsonValue(1));
    EXPECT_EQ(counters["archive"].toObject()["groups"],QJsonValue(3));
    const auto name=NativeCompositeFixture<Owner>::branch?(c0?"branch-window-warm2-C0":"branch-window-warm2"):(c0?"classic-window-warm2-C0":"classic-window-warm2");
    SaveCompositeArchive(after,name);SaveCompositeBoundary(f,name);
}
void WindowPartialArchive() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);CaptureWindowReferences(f);
    bool stopped=false;f.Run(f.Request(0,"candidate-attempt","candidate-attempt/search/1"),CompositeMeasurementPurpose::Search,{},[&](){
        if(!stopped && f.rawSamples){stopped=true;f.owner->IsNeedToTrain.SetDataDirect(false);}});
    ASSERT_TRUE(stopped);EXPECT_FALSE(f.attempt->Measurement());const auto archive=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);
    const auto replay=DecodeNativeCompositeTrainingArchive(archive.document);ASSERT_EQ(replay.Records().size(),3u);
    EXPECT_FALSE(replay.Records().back().consumed);EXPECT_TRUE(replay.Records().back().semanticProofId.empty());
    EXPECT_NO_THROW(CandidateWindowPortableReferenceFactory::Replay(replay));SaveCompositeArchive(archive,"classic-window-partial2");SaveCompositeBoundary(f,"classic-window-partial2");
    auto promoted=archive.document;MutateWindowRecord(promoted,2,[](auto& r){r["consumed"]=true;r["training_requested_at_consume"]=true;});RebindArchive(promoted);
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(promoted),std::invalid_argument);
}
template<class Owner> void WindowDimensionArchive(std::size_t n) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true,false,n,7200.,true);EnableCandidateWindow(f);
    for(std::size_t input=0;input<n;++input) {
        const std::string run="candidate-attempt/capture/1";const auto limit=(f.prototype.specification.end+.02)*(n+2)+.1;
        f.Run(f.Request(input,run,run+"/"+std::to_string(input)),CompositeMeasurementPurpose::Reference,{},{},limit,600.);
        ASSERT_TRUE(f.attempt->Group());const auto record=f.attempt->Record();ASSERT_EQ(record.groupState,NativeMatchedOmissionState::Completed)<<record.reason;
        EXPECT_EQ(record.group.packets.size(),n+2);EXPECT_EQ(record.rawTrials.size(),n+2);EXPECT_EQ(record.logical.inputIndex,input);
        EXPECT_EQ(f.attempt->CandidateWindowReferences(),nullptr);
        // Independent declared fixture expectations, not helper-formatted paths.
        const auto readback=ParseStrictNativeJsonObject(record.candidateBindingJson,128u*1024u*1024u)["physical_readback"].toObject()["input_banks"].toArray();
        ASSERT_EQ(std::size_t(readback.size()),n);
        for(std::size_t i=0;i<n;++i)EXPECT_EQ(readback[int(i)].toObject()["bank_path"],QString("$.Dendrite%1_%2").arg(NativeCompositeFixture<Owner>::branch?1:int(i+1)).arg(int(n-i)));
    }
    const auto archive=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document);
    EXPECT_EQ(decoded.Records().size(),n);EXPECT_TRUE(decoded.ReferenceGroups().empty());EXPECT_TRUE(decoded.FinalGroups().empty());
    EXPECT_THROW(CandidateWindowPortableReferenceFactory::Replay(decoded),std::invalid_argument);
    const auto name=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-distinct2-N":"classic-window-distinct2-N")+std::to_string(n);
    SaveCompositeArchive(archive,name.c_str());SaveCompositeBoundary(f,name.c_str());
    // Positive actual dimension/routing closure; geometry/targets remain
    // honestly unpromoted. This does not promise allN training convergence.
}
}
TEST(NativeCandidateWindowArchive,ClassicActualPrimaryReplaysCompleteReferencesAndProposal){WindowArchiveReplay<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowArchive,BranchActualPrimaryReplaysCompleteReferencesAndProposal){WindowArchiveReplay<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowArchive,ActualBoundC0MapsReplayedWithoutFakeBaseline){WindowArchiveReplay<NNeuronTimeLearner>(true);}
TEST(NativeCandidateWindowArchive,CsvRenameChangesArtifactDocumentOnly){WindowArchiveRename();}
TEST(NativeCandidateWindowArchive,MissingExternalPrimaryNeverFallsBack){const auto& a=ActualWindowArchive<NNeuronTimeLearner>();EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a.document,[](const QString&){return QByteArray{};}),std::invalid_argument);}
TEST(NativeCandidateWindowArchive,ChangedPrimaryRejected){const auto& a=ActualWindowArchive<NNeuronTimeLearner>();EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a.document,[&](const QString& p){return a.primary.at(p)+"0";}),std::invalid_argument);}
TEST(NativeCandidateWindowArchive,NewRecordCannotMasqueradeAsArchive1){WindowArchiveReject([](auto& a){a["schema_version"]=1;});}
TEST(NativeCandidateWindowArchive,Protocol4CannotCarryArchive2){WindowArchiveReject([](auto& a){auto p=a["protocol"].toObject();p["schema_version"]=4;a["protocol"]=p;});}
TEST(NativeCandidateWindowArchive,IncompleteSelectedReferencesCannotMintProposalAuthority){WindowArchiveReject([](auto& a){auto refs=a["reference_group_ids"].toArray();refs.removeLast();a["reference_group_ids"]=refs;});}
TEST(NativeCandidateWindowArchive,ChangedReferenceFrameOrNativeInstanceBindingRejected){WindowArchiveReject([](auto& a){MutateWindowRecord(a,2,[](auto& r){auto p=r["window_proposal"].toObject();auto seed=p["reference"].toObject();seed["first_frame"]=seed["first_frame"].toDouble()+1;p["reference"]=seed;r["window_proposal"]=p;});});WindowInstanceBindingIsSemanticContent();}
TEST(NativeCandidateWindowArchive,ChangedPolicyRejectedBeforeAuthority){WindowArchiveReject([](auto& a){auto p=a["protocol"].toObject();auto c=p["composite_measurement"].toObject();auto w=c["candidate_window_policy"].toObject();w["maximum_feature_terms"]=true;c["candidate_window_policy"]=w;p["composite_measurement"]=c;a["protocol"]=p;});}
TEST(NativeCandidateWindowArchive,ChangedCandidateReadbackRejected){WindowArchiveReject([](auto& a){MutateWindowRecord(a,2,[](auto& r){auto b=r["candidate_binding"].toObject();auto physical=b["physical_readback"].toObject();auto parameters=physical["parameters"].toArray();auto first=parameters[0].toObject();first["resistance"]=first["resistance"].toDouble()*1.1;parameters[0]=first;physical["parameters"]=parameters;b["physical_readback"]=physical;r["candidate_binding"]=b;r["candidate_witness_id"]=NmsdkTools::CanonicalModelDataSha256(b);});});}
TEST(NativeCandidateWindowArchive,ReboundFalseReadbackAndProofStillFailActualGraphReplay){ReboundWindowClaimStillRequiresReplay(true);}
TEST(NativeCandidateWindowArchive,ReboundFalseArithmeticAndProofStillFailPolicyReplay){ReboundWindowClaimStillRequiresReplay(false);}
TEST(NativeCandidateWindowArchive,ChangedPrimaryByteCapChangesSemanticProof){WindowArchiveReject([](auto& a){MutateWindowRecord(a,2,[](auto& r){auto b=r["budgets"].toObject();b["maximum_total_primary_bytes"]=b["maximum_total_primary_bytes"].toDouble()-1;r["budgets"]=b;});});}
TEST(NativeCandidateWindowArchive,ChangedAttemptRelabelCannotReuseProof){WindowArchiveReject([](auto& a){MutateWindowRecord(a,2,[](auto& r){r["attempt_id"]="relabelled";});});}
TEST(NativeCandidateWindowArchive,ActualPartialCandidateIsNeverPromoted){WindowPartialArchive();}
TEST(NativeCandidateWindowArchive,ClassicWarmUsesPortableOriginalReferencesAfterGrowth){WindowArchiveWarm<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowArchive,BranchWarmUsesPortableOriginalReferencesAfterGrowth){WindowArchiveWarm<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowArchive,BoundC0WarmKeepsOriginalFamily){WindowArchiveWarm<NNeuronTimeLearner>(true);}
TEST(NativeCandidateWindowArchive,ClassicN4ActualDistinctAllOrdinalClosure){WindowDimensionArchive<NNeuronTimeLearner>(4);}
TEST(NativeCandidateWindowArchive,BranchN4ActualDistinctAllOrdinalClosure){WindowDimensionArchive<NNeuronTimeLearnerBranch>(4);}
TEST(NativeCandidateWindowArchive,ClassicN6ActualDistinctAllOrdinalClosure){WindowDimensionArchive<NNeuronTimeLearner>(6);}
TEST(NativeCandidateWindowArchive,BranchN6ActualDistinctAllOrdinalClosure){WindowDimensionArchive<NNeuronTimeLearnerBranch>(6);}

namespace {
const NativeCompositeArchiveDocument& ActualRetainedWindowBudgetArchive(bool withMiddleCandidate=false) {
    static std::map<bool,NativeCompositeArchiveDocument> cached;const auto found=cached.find(withMiddleCandidate);if(found!=cached.end())return found->second;
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);CaptureWindowReferences(f,false);
    const auto limits=CompositeAttemptLimits{64,256,64*f.protocol.candidateWindowMeasurement->contextPolicy.maximumTotalSamples,120.,7200.};
    const auto original=DecodeNativeCompositeTrainingArchive(EncodeNativeCandidateWindowTrainingArchive(*f.attempt).document);
    f.attempt.reset();f.owner->Reset();f.owner->IsNeedToTrain=true;
    f.attempt=std::make_unique<NativeCompositeTrainingAttempt>(*f.owner,original,limits,
        NativeCandidateWindowAttemptDeclaration{"budget-attempt-B",256u*1024u*1024u},f.Time(),Wall());
    if(withMiddleCandidate) {
        f.Run(f.Request(0,"budget-attempt-B","budget-attempt-B/search/1"),CompositeMeasurementPurpose::Search);
        Require(bool(f.attempt->Measurement()),f.attempt->RejectionReason().c_str());
        const auto middle=DecodeNativeCompositeTrainingArchive(EncodeNativeCandidateWindowTrainingArchive(*f.attempt).document);
        f.attempt.reset();f.owner->Reset();f.owner->IsNeedToTrain=true;
        f.attempt=std::make_unique<NativeCompositeTrainingAttempt>(*f.owner,middle,limits,
            NativeCandidateWindowAttemptDeclaration{"budget-attempt-C",512u*1024u*1024u},f.Time(),Wall());
    }
    // The current warm attempt has NO observations. It is a declaration with
    // zero current counters, not an invented native execution or certificate.
    Require(f.attempt->IssuedGroups()==0,"budget_fixture_current_attempt_not_empty");
    auto archive=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);
    const auto name=withMiddleCandidate?"classic-window-budget-A-B-empty-C":"classic-window-budget-refs-A-empty-B";
    SaveCompositeArchive(archive,name);SaveCompositeBoundary(f,name);
    return cached.emplace(withMiddleCandidate,std::move(archive)).first->second;
}
void RebindHistoricalWindowCap(QJsonObject& document,const std::string& attempt,std::size_t cap) {
    const auto decoded=DecodeNativeCompositeTrainingArchive(document);auto wire=document["records"].toArray();std::size_t changed=0;
    for(std::size_t i=0;i<decoded.Records().size();++i)if(decoded.Records()[i].attemptId==attempt) {
        auto record=decoded.Records()[i];record.policy.maximumTotalPrimaryBytes=cap;
        record.semanticProofId=CandidateWindowTrainingSemanticProofId(decoded.Protocol(),record);
        auto item=wire[int(i)].toObject();auto budget=item["budgets"].toObject();budget["maximum_total_primary_bytes"]=double(cap);item["budgets"]=budget;
        auto measurement=item["measurement"].toObject();measurement["semantic_proof_id"]=QString::fromStdString(record.semanticProofId);item["measurement"]=measurement;
        wire[int(i)]=item;++changed;
    }
    Require(changed>0,"budget_fixture_no_historical_records_changed");document["records"]=wire;RebindArchive(document);
}
void HistoricalAttemptTotalMustFitItsOwnCap() {
    auto document=ActualRetainedWindowBudgetArchive().document;const auto decoded=DecodeNativeCompositeTrainingArchive(document);
    ASSERT_EQ(decoded.Records().size(),2u);EXPECT_EQ(decoded.CurrentAttemptId(),"budget-attempt-B");
    EXPECT_TRUE(std::all_of(decoded.Records().begin(),decoded.Records().end(),[](const auto& r){return r.purpose==CompositeMeasurementPurpose::Reference && !r.windowProposal;}));
    std::size_t total=0,largest=0;for(const auto& r:decoded.Records()){const auto bytes=CompositeRecordPrimaryBytes(r);total+=bytes;largest=std::max(largest,bytes);}
    ASSERT_GT(total,largest+1);const auto falseCap=largest+(total-largest)/2;ASSERT_GT(falseCap,largest);ASSERT_LT(falseCap,total);
    RebindHistoricalWindowCap(document,"candidate-attempt",falseCap);
    // All individual records fit. Every public measurement/document content ID
    // was rebound, no candidate proposal can reject this refs-only counterexample.
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(document),std::invalid_argument);
}
void HistoricalLaterCapMustIncludeRetainedEarlierReferences() {
    auto document=ActualRetainedWindowBudgetArchive(true).document;const auto decoded=DecodeNativeCompositeTrainingArchive(document);
    ASSERT_EQ(decoded.Records().size(),3u);EXPECT_EQ(decoded.CurrentAttemptId(),"budget-attempt-C");
    const auto prior=CompositeRecordPrimaryBytes(decoded.Records()[0])+CompositeRecordPrimaryBytes(decoded.Records()[1]);
    const auto own=CompositeRecordPrimaryBytes(decoded.Records()[2]);ASSERT_GT(prior,own+1);
    const auto falseCap=prior-1;ASSERT_GT(falseCap,own);RebindHistoricalWindowCap(document,"budget-attempt-B",falseCap);
    // B's own sum fits, but B's cap could not even retain original A refs.
    // C's larger CURRENT cap cannot retroactively make that history affordable.
    EXPECT_THROW(DecodeNativeCompositeTrainingArchive(document),std::invalid_argument);
}
}
TEST(NativeCandidateWindowBudgetReplay,ActualRefsOnlyHistoryAndEmptyHigherCapWarmReplay){const auto& a=ActualRetainedWindowBudgetArchive();const auto d=DecodeNativeCompositeTrainingArchive(a.document);EXPECT_EQ(d.CurrentAttemptId(),"budget-attempt-B");EXPECT_EQ(a.document["counters"].toObject()["attempt"].toObject()["logical_groups"],QJsonValue(0));EXPECT_NO_THROW(CandidateWindowPortableReferenceFactory::Replay(d));}
TEST(NativeCandidateWindowBudgetReplay,RehashedHistoricalAttemptCapCannotHideBehindNewLargerCap){HistoricalAttemptTotalMustFitItsOwnCap();}
TEST(NativeCandidateWindowBudgetReplay,RehashedLaterAttemptCapMustIncludeRetainedOriginalRefs){HistoricalLaterCapMustIncludeRetainedEarlierReferences();}
TEST(NativeCandidateWindowBudgetReplay,EmptyWarmCurrentCapCannotDropRetainedEarlierBytes){auto a=ActualRetainedWindowBudgetArchive().document;const auto d=DecodeNativeCompositeTrainingArchive(a);std::size_t bytes=0;for(const auto& r:d.Records())bytes+=CompositeRecordPrimaryBytes(r);ASSERT_GT(bytes,1u);a["maximum_total_primary_bytes"]=double(bytes-1);RebindArchive(a);EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a),std::invalid_argument);}
TEST(NativeCandidateWindowBudgetReplay,RetainedGroupsCannotReverseIssuedOrder){auto a=ActualRetainedWindowBudgetArchive().document;auto r=a["records"].toArray();ASSERT_EQ(r.size(),2);const auto first=r[0];r[0]=r[1];r[1]=first;a["records"]=r;RebindArchive(a);EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a),std::invalid_argument);}
TEST(NativeCandidateWindowBudgetReplay,CandidateCannotBeMovedBeforeItsOriginalReferences){auto a=ActualRetainedWindowBudgetArchive(true).document;auto r=a["records"].toArray();ASSERT_EQ(r.size(),3);QJsonArray moved{r[2],r[0],r[1]};a["records"]=moved;RebindArchive(a);EXPECT_THROW(DecodeNativeCompositeTrainingArchive(a),std::invalid_argument);}

namespace {
template<class Owner> void SaveWindowCoreCertificate(NativeCompositeFixture<Owner>& f,const char* stage,const TrainingCertificate& certificate) {
    const auto name=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-core5/":"classic-window-core5/")+stage;
    SavePortableObject(name.c_str(),"certificate3.json",QJsonObject{{"kind","native_candidate_window_typed_core_boundary"},{"schema_version",1},
        {"scope","typed_core_before_service_package6"},{"protocol",EncodeVerificationProtocol(f.protocol)},
        {"source_origin",QString::fromStdString(f.attempt->SourceOrigin())},{"source_binding",f.attempt->SourceBinding()},
        {"model_revision",QString::fromStdString(f.Revision())},{"certificate",EncodeTrainingCertificate(certificate)}});
    SaveCompositeArchive(EncodeNativeCandidateWindowTrainingArchive(*f.attempt),name.c_str());SaveCompositeBoundary(f,name.c_str(),certificate.ModelEpoch());
    // The archive here remains the actor measurement journal (no service
    // consumption/final selection). This is not a completed package6 export.
}
template<class Owner> void WindowTypedSearch(bool n0=true,bool c0=false) {
    NativeCompositeFixture<Owner> f(2000,false,64,c0,n0);EnableCandidateWindow(f);const auto references=CaptureWindowReferences(f);
    ASSERT_TRUE(f.attempt->CandidateWindowReferences());const auto closed=*f.attempt->CandidateWindowReferences();
    BoundedTrainingConfig cfg;cfg.runId="candidate-attempt";cfg.initialModelRevision=f.Revision();cfg.maximumProbes=32;cfg.maximumEdits=8;
    cfg.maximumCandidatesPerInput=2;cfg.maximumSweeps=1;cfg.normalization=n0?Normalization::SynapseCount:Normalization::TipResistance;
    cfg.n0CandidateRepeats=n0?2:1;cfg.tolerances.sync=.2;
    const auto parameters=f.owner->ReadNativeParameters();for(const auto& p:parameters)cfg.bounds.push_back({p.length,p.length,p.synapses,p.synapses,p.resistance,p.resistance});
    // This fixed-parameter standalone core fixture does not claim native N1
    // service/domain orchestration; that remains the next service substep.
    BoundedTrainingSession search(references,closed,cfg,parameters,false,f.owner->ReadNativeTrainingCapacitance());std::size_t logical=0;
    while(const auto action=search.NextAction()) {
        ASSERT_EQ(action->kind,TrainingActionKind::Probe);ASSERT_LT(++logical,32u);
        const auto request=f.Request(action->inputIndex,action->runId,action->trialId,action->modelEpoch);std::size_t arms=0;
        const auto rawPrepared=f.prototype.onPrepared;f.prototype.onPrepared=[&,rawPrepared,serial=action->serial](const auto& p,const auto& spec){
            if(rawPrepared)rawPrepared(p,spec);EXPECT_THROW(search.Arm(serial,p),std::invalid_argument);
        };
        f.Run(request,action->finalVerification?CompositeMeasurementPurpose::Final:CompositeMeasurementPurpose::Search,[&,serial=action->serial](const auto& p){
            ++arms;EXPECT_THROW(search.ArmComposite(serial,p),std::invalid_argument);search.ArmCandidateWindow(serial,p);
        });
        f.prototype.onPrepared=rawPrepared;
        SaveCandidateWindowGroup(f,"core-search-"+std::to_string(action->serial));ASSERT_EQ(arms,1u);
        ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
        ASSERT_TRUE(f.attempt->Group()->packets.front().observation);
        EXPECT_THROW(search.Consume(*f.attempt->Group()->packets.front().observation,f.Revision()),std::invalid_argument);
        EXPECT_THROW(search.ConsumeComposite(*f.attempt->Measurement(),f.Revision()),std::invalid_argument);
        search.ConsumeCandidateWindow(*f.attempt->Measurement(),f.Revision());
    }
    ASSERT_EQ(search.Status(),TrainingStatus::Exact)<<search.Reason();ASSERT_TRUE(search.Certificate());const auto& cert=*search.Certificate();
    EXPECT_EQ(cert.SchemaVersion(),3u);EXPECT_EQ(cert.CompositeProofIds().size(),2u);EXPECT_EQ(cert.FinalWindowRecipeIds().size(),2u);
    EXPECT_EQ(cert.FinalMeasurementInstanceIds().size(),2u);EXPECT_EQ(cert.CandidateWindowAttemptId(),"candidate-attempt");
    EXPECT_TRUE(cert.Matches(f.Revision(),references,cfg.tolerances,ModelStateKind::LearnedSolo,search.ModelEpoch()));
    EXPECT_FALSE(cert.Matches(f.Revision(),references,cfg.tolerances,ModelStateKind::Recognition,search.ModelEpoch()));
    EXPECT_EQ(f.attempt->IssuedGroups(),logical+2);EXPECT_EQ(f.attempt->IssuedNativeProbes(),(logical+2)*4);EXPECT_EQ(search.IssuedProbes(),logical);
    if(n0){ASSERT_EQ(search.CandidateRepeats().size(),1u);EXPECT_EQ(search.CandidateRepeats()[0].trialIds.size(),2u);}
    EXPECT_EQ(f.owner->OwnedNativeCapacitanceState().isEmpty(),!c0);
    const auto wire=EncodeTrainingCertificate(cert);EXPECT_EQ(wire["schema_version"],QJsonValue(3));
    EXPECT_EQ(wire["protocol_binding"],QJsonValue(NmsdkTools::CanonicalModelDataSha256(EncodeVerificationProtocol(f.protocol))));
    auto unsignedWire=wire;unsignedWire.remove("semantic_certificate_id");EXPECT_EQ(wire["semantic_certificate_id"],QJsonValue(NmsdkTools::CanonicalModelDataSha256(unsignedWire)));
    SaveWindowCoreCertificate(f,n0?c0?"search-N0-C0":"search-N0":"search-N1-fixed",cert);
    QJsonArray evidence;for(const auto& e:search.Evidence())evidence.append(QJsonObject{{"input_index",double(e.inputIndex)},
        {"trial_id",QString::fromStdString(e.trialId)},{"anchor_trial_id",QString::fromStdString(e.anchorTrialId)},
        {"model_revision",QString::fromStdString(e.modelRevision)},{"model_epoch",double(e.modelEpoch)},
        {"actual_raw_potential",e.measuredRawPotential},{"amplitude_residual",e.amplitudeResidual},
        {"timing_low",e.timingResidualLow},{"timing_high",e.timingResidualHigh},{"within_amplitude",e.withinAmplitude},{"within_timing",e.withinTiming}});
    const auto dir=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-core5/":"classic-window-core5/")+(n0?c0?"search-N0-C0":"search-N0":"search-N1-fixed");
    SavePortableObject(dir.c_str(),"core-search.json",QJsonObject{{"kind","native_candidate_window_core_search"},{"schema_version",1},
        {"normalization",n0?"N0":"N1"},{"standalone_fixed_parameters",true},{"native_N1_domain_service_exercised",false},
        {"outcome",TrainingStatusName(search.Status())},{"reason",QString::fromStdString(search.Reason())},
        {"issued_core_probes",double(search.IssuedProbes())},{"native_probes",double(f.attempt->IssuedNativeProbes())},
        {"raw_samples",double(f.attempt->RetainedSamples())},{"n0_candidate_repeats",double(cfg.n0CandidateRepeats)},{"candidate_evidence",evidence}});
}
template<class Owner> void WindowTypedFinal(unsigned hz=2000,bool defaultSync=false,bool c0=false) {
    NativeCompositeFixture<Owner> f(hz,false,64,c0,true);EnableCandidateWindow(f);const auto refs=CaptureWindowReferences(f);
    VerificationConfig cfg{"candidate-attempt/final/1",f.Revision(),4,0,0};if(!defaultSync)cfg.tolerances.sync=.2;
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),cfg);std::size_t probes=0;
    while(const auto request=final.NextRequest()) {
        f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& prepared){final.ArmCandidateWindow(prepared);});
        SaveCandidateWindowGroup(f,"core-final-"+std::to_string(++probes));ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
        final.ConsumeCandidateWindow(*f.attempt->Measurement(),f.Revision());
    }
    ASSERT_TRUE(final.Certificate());const auto& cert=*final.Certificate();EXPECT_EQ(cert.SchemaVersion(),3u);EXPECT_EQ(final.AcceptedInputs(),2u);
    EXPECT_EQ(cert.Exact(),!defaultSync);EXPECT_EQ(final.Status(),defaultSync?VerificationStatus::OutsideTolerance:VerificationStatus::Exact);
    EXPECT_EQ(cert.Tolerances().sync,defaultSync?.02:.2);EXPECT_EQ(cert.Tolerances().amplitudeAbsolute,1e-5);EXPECT_EQ(f.protocol.minimumAmplitude,1e-6);
    ASSERT_GE(f.groupBegins.size(),4u);EXPECT_GT(f.groupBegins.back()-f.groupBegins[f.groupBegins.size()-2],cfg.tolerances.sync);
    const auto& anchor=f.observedScalars.at(cert.Residuals().back().trialId);
    for(std::size_t i=0;i<2;++i){const auto& r=cert.Residuals()[i];const auto& actual=f.observedScalars.at(r.trialId);
        EXPECT_DOUBLE_EQ(r.targetRawPotential,refs.Inputs()[i].rawPotential);EXPECT_DOUBLE_EQ(r.measuredRawPotential,actual.rawPotential);
        EXPECT_DOUBLE_EQ(r.timingResidualLow,i==1?0.:actual.arrival-anchor.plateauEnd);EXPECT_DOUBLE_EQ(r.timingResidualHigh,i==1?0.:actual.plateauEnd-anchor.arrival);}
    SaveWindowCoreCertificate(f,defaultSync?"default-sync":hz==20000?"final-20000":c0?"final-C0":"final",cert);
}
enum class CoreWindowRevocation { NeedSetter,NeedDirect,NeedConnected,Reset,Default,Edit,StructuralABA,C0Edit };
template<class Owner> void WindowCoreConsumeRevoked(CoreWindowRevocation kind) {
    const bool c0=kind==CoreWindowRevocation::C0Edit;
    NativeCompositeFixture<Owner> f(2000,false,64,c0,true,kind==CoreWindowRevocation::NeedConnected);EnableCandidateWindow(f);
    const auto refs=CaptureWindowReferences(f);FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),{"candidate-attempt/final/1",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmCandidateWindow(p);});
    SaveCandidateWindowGroup(f,"core-before-revocation");ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    const auto measurement=*f.attempt->Measurement();const auto cachedRevision=f.Revision();
    if(kind==CoreWindowRevocation::NeedSetter)f.owner->IsNeedToTrain=false;
    if(kind==CoreWindowRevocation::NeedDirect)f.owner->IsNeedToTrain.SetDataDirect(false);
    if(kind==CoreWindowRevocation::NeedConnected)f.flag->Value=false;
    if(kind==CoreWindowRevocation::Reset)f.owner->Reset();
    if(kind==CoreWindowRevocation::Default)f.owner->Default();
    if(kind==CoreWindowRevocation::Edit || kind==CoreWindowRevocation::StructuralABA) {
        const auto original=f.owner->ReadNativeParameters();auto changed=original;changed[0].length=3;
        ASSERT_EQ(f.owner->ApplyNativeParameters(changed).status,NativeEditStatus::Applied);
        if(kind==CoreWindowRevocation::StructuralABA){ASSERT_EQ(f.owner->ApplyNativeParameters(original).status,NativeEditStatus::Applied);ASSERT_EQ(f.Revision(),cachedRevision);}
    }
    if(kind==CoreWindowRevocation::C0Edit) {
        auto correction=f.owner->ReadNativeTrainingCapacitance();ASSERT_TRUE(correction);ASSERT_FALSE(correction->membraneScales.empty());
        correction->membraneScales.begin()->second=1.01;
        const auto edit=f.owner->ApplyNativeTrainingParameters(f.owner->ReadNativeParameters(),correction);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    }
    // Cached caller strings cannot revive the actual expired/changed owner.
    final.ConsumeCandidateWindow(measurement,cachedRevision);EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
    EXPECT_EQ(final.Status(),kind==CoreWindowRevocation::NeedSetter || kind==CoreWindowRevocation::NeedDirect || kind==CoreWindowRevocation::NeedConnected?
        VerificationStatus::ExternalStop:VerificationStatus::InvalidObservation);
    const auto directory=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-core5/":"classic-window-core5/")+"revoked";
    const bool graph=bool(f.owner->template GetComponentL<NPulseNeuron>("Neuron",true)) &&
        bool(f.owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true)) &&
        bool(f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true));
    const bool inspect=graph && kind!=CoreWindowRevocation::Default;
    SavePortableObject(directory.c_str(),"core-revocation.json",QJsonObject{{"kind","native_candidate_window_core_revocation"},{"schema_version",1},
        {"revocation_case",int(kind)},{"actual_final_status",VerificationStatusName(final.Status())},{"accepted_inputs",double(final.AcceptedInputs())},
        {"cached_model_revision_before",QString::fromStdString(cachedRevision)},{"actual_graph_available_after",graph},
        {"actual_model_revision_read",inspect},{"actual_model_revision_after",inspect?QJsonValue(QString::fromStdString(f.Revision())):QJsonValue(QJsonValue::Null)},
        {"certificate",final.Certificate()?QJsonValue(EncodeTrainingCertificate(*final.Certificate())):QJsonValue(QJsonValue::Null)}});
    if(inspect)SaveCompositeBoundary(f,directory.c_str(),final.ModelEpoch());
}
void ReferenceAndLegacyTokensCannotEnterWindowFinal() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto refs=CaptureWindowReferences(f);
    FinalVerificationSession noClosed(refs,{"candidate-attempt/final/1",f.Revision(),4,0,0});ASSERT_TRUE(noClosed.NextRequest());
    const auto& raw=f.attempt->Group()->packets.front();ASSERT_TRUE(raw.prepared);ASSERT_TRUE(raw.observation);
    EXPECT_THROW(noClosed.Arm(*raw.prepared),std::invalid_argument);EXPECT_THROW(noClosed.Consume(*raw.observation,f.Revision()),std::invalid_argument);
    EXPECT_THROW(noClosed.ArmCandidateWindow(f.referenceMeasurements[0].Prepared()),std::invalid_argument);
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),{"candidate-attempt/final/1",f.Revision(),4,0,0});ASSERT_TRUE(final.NextRequest());
    final.ArmCandidateWindow(f.referenceMeasurements[0].Prepared());EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(final.Certificate());
}
void SearchAndOldSweepCannotEnterWindowFinal(bool oldSweep) {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto refs=CaptureWindowReferences(f);
    const auto source=oldSweep?f.Request(0,"candidate-attempt/final/1","candidate-attempt/final/1/verify/0/1"):
        f.Request(0,"candidate-attempt","candidate-attempt/search/1");
    f.Run(source,oldSweep?CompositeMeasurementPurpose::Final:CompositeMeasurementPurpose::Search);ASSERT_TRUE(f.attempt->Measurement());
    SaveCandidateWindowGroup(f,"core-wrong-purpose-or-sweep");
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),{"candidate-attempt/final/2",f.Revision(),4,0,0});ASSERT_TRUE(final.NextRequest());
    final.ArmCandidateWindow(f.attempt->Measurement()->Prepared());EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_FALSE(final.Certificate());
}
void WindowCoreRejectsAnotherClosedFamily() {
    std::optional<CandidateWindowReferenceSet> old;
    {NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);CaptureWindowReferences(f,true,"family-A");old=*f.attempt->CandidateWindowReferences();}
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto refs=CaptureWindowReferences(f,true,"family-B");
    ASSERT_NE(old->OwnerFamilyBinding(),f.attempt->OwnerFamilyBinding());
    EXPECT_THROW(FinalVerificationSession(refs,*old,VerificationConfig{"candidate-attempt/final/1",f.Revision(),4,0,0}),std::invalid_argument);
}
void WindowCoreModelDeadlineIncludesDelayedAdmission() {
    NativeCompositeFixture<NNeuronTimeLearner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto refs=CaptureWindowReferences(f);
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),{"candidate-attempt/final/1",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmCandidateWindow(p);});
    ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();SaveCandidateWindowGroup(f,"core-before-deadline");
    const auto measured=*f.attempt->Measurement();const auto revision=f.Revision();const auto raw=f.rawSamples;const auto native=f.attempt->IssuedNativeProbes();
    // Advance the REAL scheduler/model clock once per tick, not a zero/fake
    // clock or a sleep too short to prove that a native callback was reached.
    for(unsigned tick=0;tick<4200;++tick){f.model->Calculate();f.environment->IncreaseModelTimeByStep();}
    ASSERT_EQ(f.Revision(),revision);EXPECT_EQ(f.rawSamples,raw);EXPECT_EQ(f.attempt->IssuedNativeProbes(),native);
    final.ConsumeCandidateWindow(measured,revision);EXPECT_EQ(final.Status(),VerificationStatus::BudgetExhausted);
    EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
}
void WindowCoreBranchEditInvalidatesAllFinalInputs() {
    NativeCompositeFixture<NNeuronTimeLearnerBranch> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto refs=CaptureWindowReferences(f);
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),{"candidate-attempt/final/1",f.Revision(),4,0,0});
    const auto request=final.NextRequest();ASSERT_TRUE(request);ASSERT_EQ(request->inputIndex,1u);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmCandidateWindow(p);});ASSERT_TRUE(f.attempt->Measurement());
    SaveCandidateWindowGroup(f,"core-before-branch-edit");final.ConsumeCandidateWindow(*f.attempt->Measurement(),f.Revision());ASSERT_EQ(final.AcceptedInputs(),1u);
    auto changed=f.owner->ReadNativeParameters();changed[0].length=3;const auto edit=f.owner->ApplyNativeParameters(changed);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    final.Invalidate(f.Revision());EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_EQ(final.ModelEpoch(),1u);EXPECT_FALSE(final.Certificate());
    const auto fresh=final.NextRequest();ASSERT_TRUE(fresh);EXPECT_EQ(fresh->inputIndex,1u);EXPECT_EQ(fresh->epoch,1u);EXPECT_NE(fresh->trialId,request->trialId);
    EXPECT_EQ(fresh->baseModelRevision,f.Revision());SaveCompositeBoundary(f,"branch-window-core5/after-coupled-edit",final.ModelEpoch());
}
}
TEST(NativeCandidateWindowTrainingCore,ClassicN0FreshSearchAndFinalCertificate3){WindowTypedSearch<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowTrainingCore,BranchN0FreshSearchAndFinalCertificate3){WindowTypedSearch<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowTrainingCore,ClassicN1FixedParameterStandaloneCore){WindowTypedSearch<NNeuronTimeLearner>(false);}
TEST(NativeCandidateWindowTrainingCore,BranchN1FixedParameterStandaloneCore){WindowTypedSearch<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCandidateWindowTrainingCore,ClassicBoundC0KeepsOriginalTargetFamily){WindowTypedSearch<NNeuronTimeLearner>(true,true);}
TEST(NativeCandidateWindowTrainingCore,BranchBoundC0FreshAllNFinal){WindowTypedFinal<NNeuronTimeLearnerBranch>(2000,false,true);}
TEST(NativeCandidateWindowTrainingCore,Classic20000FreshActualFinal){WindowTypedFinal<NNeuronTimeLearner>(20000);}
TEST(NativeCandidateWindowTrainingCore,Branch20000FreshActualFinal){WindowTypedFinal<NNeuronTimeLearnerBranch>(20000);}
TEST(NativeCandidateWindowTrainingCore,ClassicDefaultSyncRemainsOutsideTolerance){WindowTypedFinal<NNeuronTimeLearner>(2000,true);}
TEST(NativeCandidateWindowTrainingCore,BranchDefaultSyncRemainsOutsideTolerance){WindowTypedFinal<NNeuronTimeLearnerBranch>(2000,true);}
TEST(NativeCandidateWindowTrainingCore,SetterFalseBetweenCloseAndConsume){WindowCoreConsumeRevoked<NNeuronTimeLearner>(CoreWindowRevocation::NeedSetter);}
TEST(NativeCandidateWindowTrainingCore,DirectFalseBetweenCloseAndConsume){WindowCoreConsumeRevoked<NNeuronTimeLearnerBranch>(CoreWindowRevocation::NeedDirect);}
TEST(NativeCandidateWindowTrainingCore,ConnectedFalseBetweenCloseAndConsume){WindowCoreConsumeRevoked<NNeuronTimeLearner>(CoreWindowRevocation::NeedConnected);}
TEST(NativeCandidateWindowTrainingCore,OwnerResetExpiresClosedMeasurement){WindowCoreConsumeRevoked<NNeuronTimeLearner>(CoreWindowRevocation::Reset);}
TEST(NativeCandidateWindowTrainingCore,OwnerDefaultExpiresClosedMeasurement){WindowCoreConsumeRevoked<NNeuronTimeLearnerBranch>(CoreWindowRevocation::Default);}
TEST(NativeCandidateWindowTrainingCore,ActualStructuralEditDefeatsCachedRevision){WindowCoreConsumeRevoked<NNeuronTimeLearner>(CoreWindowRevocation::Edit);}
TEST(NativeCandidateWindowTrainingCore,SameSemanticGraphAfterRebuildCannotReviveMeasurement){WindowCoreConsumeRevoked<NNeuronTimeLearner>(CoreWindowRevocation::StructuralABA);}
TEST(NativeCandidateWindowTrainingCore,OwnedC0EditDefeatsCachedRevision){WindowCoreConsumeRevoked<NNeuronTimeLearner>(CoreWindowRevocation::C0Edit);}
TEST(NativeCandidateWindowTrainingCore,ReferenceAndUnqualifiedLegacyApiCannotArmFinal){ReferenceAndLegacyTokensCannotEnterWindowFinal();}
TEST(NativeCandidateWindowTrainingCore,SearchPurposeCannotBecomeFinal){SearchAndOldSweepCannotEnterWindowFinal(false);}
TEST(NativeCandidateWindowTrainingCore,PreviousWholeSweepCannotArmNewFinal){SearchAndOldSweepCannotEnterWindowFinal(true);}
TEST(NativeCandidateWindowTrainingCore,IdenticalModelDifferentOwnerFamilyCannotReplaceOriginalRefs){WindowCoreRejectsAnotherClosedFamily();}
TEST(NativeCandidateWindowTrainingCore,RealModelClockDeadlineGuardsDelayedConsume){WindowCoreModelDeadlineIncludesDelayedAdmission();}
TEST(NativeCandidateWindowTrainingCore,BranchControlledEditRequiresFreshAllNFinal){WindowCoreBranchEditInvalidatesAllFinalInputs();}

namespace {
template<class Owner> void ExpectWindowReferenceStage(const NativeCompositeFixture<Owner>& f,std::size_t count,bool complete) {
    EXPECT_EQ(bool(f.attempt->CandidateWindowReferences()),complete);
    ASSERT_EQ(f.attempt->CandidateWindowRecords().size(),count);
    for(const auto& record:f.attempt->CandidateWindowRecords()) {
        EXPECT_EQ(record.purpose,CompositeMeasurementPurpose::Reference);EXPECT_EQ(record.consumed,complete);
        if(complete)EXPECT_EQ(record.trainingRequestedAtConsume,std::optional<bool>(true));
        else EXPECT_FALSE(record.trainingRequestedAtConsume);
    }
}
template<class Owner> std::vector<ValidatedCompositeMeasurement> StageWindowAllReferences(NativeCompositeFixture<Owner>& f,const std::string& prefix) {
    std::vector<ValidatedCompositeMeasurement> measurements;
    for(std::size_t input=0;input<f.protocol.inputs.size();++input) {
        const std::string run="candidate-attempt/capture/1";
        f.Run(f.Request(input,run,run+"/"+std::to_string(input)),CompositeMeasurementPurpose::Reference);
        Require(bool(f.attempt->Measurement()),f.attempt->RejectionReason().c_str());
        measurements.push_back(*f.attempt->Measurement());ExpectWindowReferenceStage(f,input+1,false);
        SaveCandidateWindowGroup(f,prefix+"-"+std::to_string(input));
    }
    return measurements;
}
template<class Owner> void SaveWindowReferenceRelease(NativeCompositeFixture<Owner>& f,const char* stage) {
    const auto name=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-reference-release5/":"classic-window-reference-release5/")+stage;
    const auto* closed=f.attempt->CandidateWindowReferences();QJsonArray groups,proofs,targets;
    if(closed){for(const auto& id:closed->ReferenceGroupIds())groups.append(QString::fromStdString(id));
        for(const auto& id:closed->ReferenceProofIds())proofs.append(QString::fromStdString(id));for(const auto raw:closed->TargetRawPotentials())targets.append(raw);}
    SaveCompositeArchive(EncodeNativeCandidateWindowTrainingArchive(*f.attempt),name.c_str());
    SavePortableObject(name.c_str(),"reference-release.json",{{"kind","native_candidate_window_reference_release_boundary"},{"schema_version",1},
        {"scope","actor_allN_release_before_service5"},{"reference_complete",bool(closed)},
        {"selected_original_group_ids",groups},{"selected_original_proof_ids",proofs},{"actual_original_raw_targets",targets},
        {"service_or_package6_completed",false}});
}
template<class Owner> void WindowReferenceReleaseCommitsAllN() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);EnableCandidateWindow(f);
    const auto measured=StageWindowAllReferences(f,"release-staged");const auto refs=CapturedReferences::CaptureComposite(f.protocol,measured);
    ExpectWindowReferenceStage(f,2,false);SaveWindowReferenceRelease(f,"before-complete");
    f.attempt->CompleteCandidateWindowReferences(refs);ExpectWindowReferenceStage(f,2,true);
    ASSERT_TRUE(f.attempt->CandidateWindowReferences());EXPECT_EQ(f.attempt->CandidateWindowReferences()->TargetRawPotentials().size(),2u);
    for(std::size_t i=0;i<2;++i)EXPECT_DOUBLE_EQ(f.attempt->CandidateWindowReferences()->TargetRawPotentials()[i],refs.Inputs()[i].rawPotential);
    SaveWindowReferenceRelease(f,"complete");
}
template<class Owner> void WindowReferenceReleaseRejectsOtherFamily() {
    std::optional<CapturedReferences> previous;
    {NativeCompositeFixture<Owner> f(2000,false,64,false,true);EnableCandidateWindow(f);previous=CaptureWindowReferences(f,true,"release-family-A");}
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto measured=StageWindowAllReferences(f,"release-family-B");
    const auto refs=CapturedReferences::CaptureComposite(f.protocol,measured);ASSERT_NE(previous->CompositeOwnerScope(),refs.CompositeOwnerScope());
    const auto before=EncodeNativeCandidateWindowTrainingArchive(*f.attempt).document;
    EXPECT_THROW(f.attempt->CompleteCandidateWindowReferences(*previous),std::invalid_argument);
    ExpectWindowReferenceStage(f,2,false);EXPECT_EQ(EncodeNativeCandidateWindowTrainingArchive(*f.attempt).document,before);
    SaveWindowReferenceRelease(f,"wrong-family-not-promoted");
    f.attempt->CompleteCandidateWindowReferences(refs);ExpectWindowReferenceStage(f,2,true);SaveWindowReferenceRelease(f,"correct-family-after-refusal");
}
template<class Owner> void WindowReferenceReleaseRejectsDuplicateEvidence() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto measured=StageWindowAllReferences(f,"release-duplicate-control");
    const std::vector<ValidatedCompositeMeasurement> duplicate{measured[0],measured[0]};
    EXPECT_THROW(CapturedReferences::CaptureComposite(f.protocol,duplicate),std::invalid_argument);ExpectWindowReferenceStage(f,2,false);
    SaveWindowReferenceRelease(f,"duplicate-data-not-promoted");
    const auto refs=CapturedReferences::CaptureComposite(f.protocol,measured);f.attempt->CompleteCandidateWindowReferences(refs);
    ExpectWindowReferenceStage(f,2,true);SaveWindowReferenceRelease(f,"complete-after-duplicate-refusal");
}
enum class WindowReleaseRevocation { StructuralEdit,Reset,Default };
template<class Owner> void WindowReferenceReleaseRechecksOwner(WindowReleaseRevocation kind) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);EnableCandidateWindow(f);const auto measured=StageWindowAllReferences(f,"release-before-revocation");
    const auto refs=CapturedReferences::CaptureComposite(f.protocol,measured);SaveWindowReferenceRelease(f,"before-revocation");
    const auto before=EncodeNativeCandidateWindowTrainingArchive(*f.attempt).document;
    if(kind==WindowReleaseRevocation::StructuralEdit){auto p=f.owner->ReadNativeParameters();p[0].length=3;
        const auto edit=f.owner->ApplyNativeParameters(p);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;}
    else if(kind==WindowReleaseRevocation::Reset)f.owner->Reset();else f.owner->Default();
    EXPECT_THROW(f.attempt->CompleteCandidateWindowReferences(refs),std::invalid_argument);ExpectWindowReferenceStage(f,2,false);
    EXPECT_EQ(EncodeNativeCandidateWindowTrainingArchive(*f.attempt).document,before);SaveWindowReferenceRelease(f,"revoked-not-promoted");
    if(kind==WindowReleaseRevocation::StructuralEdit)SaveCompositeBoundary(f,NativeCompositeFixture<Owner>::branch?
        "branch-window-reference-release5/actual-after-edit":"classic-window-reference-release5/actual-after-edit",0);
}
}
TEST(NativeCandidateWindowReferenceRelease,ClassicStagedPrefixCommitsOnlyAsCompleteAllN){WindowReferenceReleaseCommitsAllN<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowReferenceRelease,BranchStagedPrefixCommitsOnlyAsCompleteAllN){WindowReferenceReleaseCommitsAllN<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowReferenceRelease,ClassicWrongFamilyCannotPromoteAnyRecord){WindowReferenceReleaseRejectsOtherFamily<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowReferenceRelease,BranchWrongFamilyCannotPromoteAnyRecord){WindowReferenceReleaseRejectsOtherFamily<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowReferenceRelease,ClassicDuplicateEvidenceDoesNotPromotePrefix){WindowReferenceReleaseRejectsDuplicateEvidence<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowReferenceRelease,BranchDuplicateEvidenceDoesNotPromotePrefix){WindowReferenceReleaseRejectsDuplicateEvidence<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowReferenceRelease,ClassicActualEditBeforeReleaseIsRejected){WindowReferenceReleaseRechecksOwner<NNeuronTimeLearner>(WindowReleaseRevocation::StructuralEdit);}
TEST(NativeCandidateWindowReferenceRelease,BranchActualEditBeforeReleaseIsRejected){WindowReferenceReleaseRechecksOwner<NNeuronTimeLearnerBranch>(WindowReleaseRevocation::StructuralEdit);}
TEST(NativeCandidateWindowReferenceRelease,ClassicOwnerResetBeforeReleaseIsRejected){WindowReferenceReleaseRechecksOwner<NNeuronTimeLearner>(WindowReleaseRevocation::Reset);}
TEST(NativeCandidateWindowReferenceRelease,BranchOwnerDefaultBeforeReleaseIsRejected){WindowReferenceReleaseRechecksOwner<NNeuronTimeLearnerBranch>(WindowReleaseRevocation::Default);}

namespace {
template<class Owner> ConfiguredNativeTraining ActualCold7Declaration(NativeCompositeFixture<Owner>& f) {
    auto c=CompositeCold(f);EnableCandidateWindow(f);c.composite->schemaVersion=2;
    c.candidateWindowPolicy=f.protocol.candidateWindowMeasurement->candidateWindowPolicy;c.windows.clear();
    for(const auto& w:f.protocol.candidateWindowMeasurement->referenceInputWindows)c.windows.emplace_back(w.beginOffset,w.endOffset);
    return c;
}
template<class Owner> void ActualCold7InitialReadback() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto c=ActualCold7Declaration(f);f.attempt.reset();
    for(auto& b:c.search.bounds){b.minimumLength=1;b.maximumLength=8;b.minimumSynapses=1;b.maximumSynapses=3;}
    auto actual=f.owner->ReadNativeParameters();actual[0].length=3;actual[0].synapses=2;
    const auto edit=f.owner->ApplyNativeParameters(actual);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    actual=f.owner->ReadNativeParameters();const auto plan=MakeConfiguredNativeTrainingPlan(c);
    const auto captured=CaptureCandidateWindowInitialConfiguration(f.modelSpec,plan,actual,0.);
    const auto wire=EncodeConfiguredNativeTraining(captured);EXPECT_EQ(wire["schema_version"],QJsonValue(7));
    EXPECT_EQ(captured.model.inputs[0].attachment,3);EXPECT_EQ(captured.model.inputs[0].synapses,2);
    ASSERT_TRUE(captured.model.inputs[0].resistance);EXPECT_DOUBLE_EQ(*captured.model.inputs[0].resistance,actual[0].resistance);
    EXPECT_EQ(f.modelSpec.inputs[0].attachment,2);EXPECT_FALSE(f.modelSpec.inputs[0].resistance);
    EXPECT_TRUE(captured.search.initialModelRevision.empty());EXPECT_EQ(captured.search.initialModelEpoch,0u);
    EXPECT_FALSE(captured.recordCapacitanceHistory);EXPECT_TRUE(f.owner->OwnedNativeCapacitanceState().isEmpty());
    EXPECT_EQ(EncodeConfiguredNativeTraining(DecodeConfiguredNativeTraining(wire)),wire);
    EXPECT_EQ(MakeConfiguredNativeTrainingPlan(captured).protocol.candidateWindowMeasurement->referenceInputWindows,
        plan.protocol.candidateWindowMeasurement->referenceInputWindows);
    const auto name=NativeCompositeFixture<Owner>::branch?"cold7-native-initial-declarations/branch":"cold7-native-initial-declarations/classic";
    SavePortableObject(name,"initial-configuration.json",wire);SaveCompositeBoundary(f,name);
    SavePortableObject(name,"declaration-scope.json",{{"kind","native_candidate_window_initial_declaration_scope"},{"schema_version",1},
        {"actual_model_revision",QString::fromStdString(f.Revision())},{"native_groups_issued",0},{"training_executed",false},
        {"scope","actual initial graph readback and declaration only; no selected peak or certificate"}});
}
template<class Owner> void ActualCold7InitialBindingRefusal(bool wrongWindow) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);const auto c=ActualCold7Declaration(f);auto plan=MakeConfiguredNativeTrainingPlan(c);
    if(wrongWindow)plan.inputWindows[0].end+=.001;else plan.composite->geometryPolicy.repeatabilityAbsolute+=1e-6;
    EXPECT_THROW(CaptureCandidateWindowInitialConfiguration(f.modelSpec,plan,f.owner->ReadNativeParameters(),0.),std::invalid_argument);
    EXPECT_EQ(f.attempt->IssuedGroups(),0u);EXPECT_FALSE(f.attempt->CandidateWindowReferences());
    const auto name=wrongWindow?"cold7-native-initial-declarations/wrong-reference-window":"cold7-native-initial-declarations/wrong-common-policy";
    SavePortableObject(name,"original-configuration.json",EncodeConfiguredNativeTraining(c));SaveCompositeBoundary(f,name);
}
}
TEST(NativeCandidateWindowCold7,ClassicInitialDeclarationUsesActualParametersRatherThanTemplate){ActualCold7InitialReadback<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowCold7,BranchInitialDeclarationUsesActualParametersRatherThanTemplate){ActualCold7InitialReadback<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowCold7,ActualCommonPolicyMismatchCannotBecomeInitialDeclaration){ActualCold7InitialBindingRefusal<NNeuronTimeLearner>(false);}
TEST(NativeCandidateWindowCold7,ActualReferenceWindowMismatchCannotBecomeInitialDeclaration){ActualCold7InitialBindingRefusal<NNeuronTimeLearnerBranch>(true);}

namespace {
template<class Owner> void CandidateWindowServiceStartsBeforeAnyNativeQueue() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);const auto configuration=ActualCold7Declaration(f);
    const auto plan=MakeConfiguredNativeTrainingPlan(configuration);const auto initial=f.Revision();f.attempt.reset();
    f.owner->BeginNativeTraining(plan);const auto& service=f.owner->NativeTrainingController();
    ASSERT_EQ(service.State(),NativeTrainingState::CapturingReferences)<<service.Reason();
    EXPECT_EQ(service.SessionAttempt(),1u);EXPECT_EQ(service.Plan().protocol.schemaVersion,5u);
    EXPECT_EQ(service.Configuration().runId,configuration.runId+"/session/1");
    EXPECT_EQ(service.CompositeInitialConfiguration()["schema_version"],QJsonValue(7));
    EXPECT_EQ(service.CompositeInitialConfiguration()["run_id"],QJsonValue(QString::fromStdString(configuration.runId)));
    EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());EXPECT_TRUE(service.CompositeReferenceGroupIds().empty());
    EXPECT_EQ(service.CompositeGroups(),0u);EXPECT_EQ(service.CompositeNativeProbes(),0u);EXPECT_EQ(service.CompositeSampledFrames(),0u);
    EXPECT_EQ(f.Revision(),initial);EXPECT_TRUE(f.owner->OwnedNativeCapacitanceState().isEmpty());
    const auto archive=EncodeNativeCandidateWindowServiceArchive(service);const auto decoded=DecodeNativeCompositeTrainingArchive(archive.document);
    EXPECT_EQ(decoded.CurrentAttemptId(),service.Configuration().runId);EXPECT_TRUE(decoded.Records().empty());EXPECT_TRUE(decoded.ReferenceGroups().empty());
    const auto name=NativeCompositeFixture<Owner>::branch?"branch-native-window-service5/bootstrap":"classic-native-window-service5/bootstrap";
    SaveCompositeArchive(archive,name);SaveCompositeBoundary(f,name);f.owner->IsNeedToTrain=false;
    EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);EXPECT_FALSE(service.Certificate());EXPECT_EQ(service.CompositeNativeProbes(),0u);
}
}
TEST(NativeCandidateWindowServiceBootstrap,ClassicIdentityAndCold7ExistBeforeFirstQueue){CandidateWindowServiceStartsBeforeAnyNativeQueue<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowServiceBootstrap,BranchIdentityAndCold7ExistBeforeFirstQueue){CandidateWindowServiceStartsBeforeAnyNativeQueue<NNeuronTimeLearnerBranch>();}

namespace {
template<class Owner> NativeTrainingPlan ActualWindowServicePlan(NativeCompositeFixture<Owner>& f,double sync=.2,bool repeat=true,bool c0=false) {
    auto c=ActualCold7Declaration(f);c.runId="actual-native-window-service5";c.search.runId=c.runId;
    c.search.normalization=f.modelSpec.normalization;c.search.n0CandidateRepeats=repeat && c.search.normalization==Normalization::SynapseCount?2:1;
    c.search.maximumSweeps=1;c.search.tolerances.sync=sync;c.maximumWallSeconds=7200.;
    if(c0){c.recordCapacitanceHistory=true;c.capacitanceMaximumRelativeChange=.2;}
    auto plan=MakeConfiguredNativeTrainingPlan(c);plan.probe.onPrepared=f.prototype.onPrepared;plan.probe.onSample=f.prototype.onSample;return plan;
}
template<class Owner> void SaveWindowService(NativeCompositeFixture<Owner>& f,const std::string& stage) {
    const auto name=std::string(NativeCompositeFixture<Owner>::branch?"branch-native-window-service5/":"classic-native-window-service5/")+stage;
    const auto& service=f.owner->NativeTrainingController();const auto archive=EncodeNativeCandidateWindowServiceArchive(service);
    SaveCompositeArchive(archive,name.c_str());SaveCompositeBoundary(f,name.c_str());QJsonArray evidence,domains,references;
    if(service.References())for(const auto& r:service.References()->Inputs())references.append(QJsonObject{{"input_id",QString::fromStdString(r.id)},
        {"group_id",QString::fromStdString(r.measurementGroupId)},{"semantic_proof_id",QString::fromStdString(r.semanticProofId)},{"actual_raw_target",r.rawPotential}});
    const auto& policy=*service.Plan().composite;
    if(service.Search()) {
        for(const auto& d:service.Search()->Domains())domains.append(EncodeResistanceDomainAssessment(d));
        for(const auto& e:service.Search()->Evidence())evidence.append(QJsonObject{{"input_index",double(e.inputIndex)},
            {"trial_id",QString::fromStdString(e.trialId)},{"anchor_trial_id",QString::fromStdString(e.anchorTrialId)},
            {"model_revision",QString::fromStdString(e.modelRevision)},{"model_epoch",double(e.modelEpoch)},
            {"actual_raw_potential",e.measuredRawPotential},{"amplitude_residual",e.amplitudeResidual},
            {"timing_low",e.timingResidualLow},{"timing_high",e.timingResidualHigh},
            {"within_amplitude",e.withinAmplitude},{"within_timing",e.withinTiming}});
    }
    SavePortableObject(name.c_str(),"service5-boundary.json",{{"kind","native_candidate_window_service_boundary"},{"schema_version",1},
        {"scope","actual Service5 before separate runtime2/learned6/summary7 codec stage"},{"outcome",TrainingStatusName(service.Outcome())},
        {"reason",QString::fromStdString(service.Reason())},{"session_attempt",double(service.SessionAttempt())},
        {"model_epoch",double(service.ModelEpoch())},{"reference_complete",bool(service.References())},
        {"original_references",references},{"current_attempt_id",QString::fromStdString(service.Configuration().runId)},
        {"current_attempt_limits",QJsonObject{{"maximum_groups",double(policy.maximumGroups)},{"maximum_native_probes",double(policy.maximumNativeProbes)},
            {"maximum_total_samples",double(policy.maximumTotalSamples)},{"maximum_model_seconds",service.Plan().maximumModelSeconds},
            {"maximum_wall_seconds",service.Plan().maximumWallSeconds},{"maximum_group_model_seconds",policy.maximumGroupModelSeconds},
            {"maximum_group_wall_seconds",policy.maximumGroupWallSeconds},{"maximum_total_primary_bytes",double(policy.maximumTotalPrimaryBytes)}}},
        {"certificate",service.Certificate()?QJsonValue(EncodeTrainingCertificate(*service.Certificate())):QJsonValue(QJsonValue::Null)},
        {"last_core_certificate",service.Search() && service.Search()->Certificate()?QJsonValue(EncodeTrainingCertificate(*service.Search()->Certificate())):QJsonValue(QJsonValue::Null)},
        {"actual_candidate_evidence",evidence},{"actual_resistance_domains",domains},{"completed_portable_package6",false}});
}
template<class Owner> void WindowServiceExact(int mode,bool n0=true,bool c0=false,bool defaultSync=false) {
    NativeCompositeFixture<Owner> f(2000,false,64,c0,n0);auto plan=ActualWindowServicePlan(f,defaultSync?.02:.2,true,c0);f.owner->CalculateMode=mode;
    std::size_t rawClosed=0,completeReferences=0,finals=0;plan.observationSink=[&](const auto&){++rawClosed;};
    plan.compositeSink=[&](const auto& record){const auto& service=f.owner->NativeTrainingController();
        if(record.purpose==CompositeMeasurementPurpose::Reference) {
            ++completeReferences;
            if(completeReferences==1){EXPECT_FALSE(service.References());EXPECT_TRUE(service.CompositeReferenceGroupIds().empty());EXPECT_FALSE(record.consumed);EXPECT_FALSE(record.trainingRequestedAtConsume);}
            else {ASSERT_TRUE(service.References());EXPECT_EQ(service.CompositeReferenceGroupIds().size(),2u);
                for(const auto& r:service.CompositeMeasurements())if(r.purpose==CompositeMeasurementPurpose::Reference){EXPECT_TRUE(r.consumed);EXPECT_EQ(r.trainingRequestedAtConsume,std::optional<bool>(true));}}
        }
        if(record.purpose==CompositeMeasurementPurpose::Final && record.consumed){++finals;EXPECT_FALSE(service.Certificate());}
    };
    ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();ASSERT_TRUE(service.Search());ASSERT_TRUE(service.References());
    EXPECT_EQ(service.Outcome(),defaultSync?TrainingStatus::BudgetExhausted:TrainingStatus::Exact)<<service.Reason();
    if(defaultSync){EXPECT_FALSE(service.Certificate());ASSERT_TRUE(service.Search()->Certificate());EXPECT_FALSE(service.Search()->Certificate()->Exact());}
    else {ASSERT_TRUE(service.Certificate());EXPECT_EQ(service.Certificate()->SchemaVersion(),3u);EXPECT_TRUE(service.Certificate()->Exact());}
    EXPECT_EQ(completeReferences,2u);EXPECT_EQ(finals,2u);EXPECT_EQ(rawClosed,service.CompositeNativeProbes());EXPECT_EQ(rawClosed,f.preparations);
    EXPECT_EQ(service.CompositeSampledFrames(),f.rawSamples);EXPECT_EQ(service.CompositeNativeProbes(),4*service.CompositeGroups());
    EXPECT_EQ(service.Search()->IssuedProbes(),service.CompositeGroups()-2);EXPECT_EQ(service.Configuration().tolerances.sync,defaultSync?.02:.2);
    EXPECT_EQ(service.Configuration().tolerances.amplitudeAbsolute,1e-5);EXPECT_EQ(service.Plan().protocol.minimumAmplitude,1e-6);
    if(n0) {ASSERT_FALSE(service.Search()->CandidateRepeats().empty());EXPECT_EQ(service.Search()->CandidateRepeats()[0].trialIds.size(),2u);}
    else {ASSERT_FALSE(service.Search()->Domains().empty());for(const auto& domain:service.Search()->Domains())EXPECT_EQ(domain.status,ResistanceDomainStatus::Available);}
    for(const auto& r:service.CompositeMeasurements()){EXPECT_EQ(r.attemptId,service.Configuration().runId);EXPECT_EQ(r.semanticProofId,CandidateWindowTrainingSemanticProofId(service.Plan().protocol,r));
        EXPECT_EQ(r.policy.maximumGroupModelSeconds,r.maximumGroupModelSeconds);EXPECT_EQ(r.policy.maximumGroupWallSeconds,r.maximumGroupWallSeconds);}
    if(c0){for(const auto& r:service.CompositeMeasurements()){ASSERT_EQ(r.nativeTrialWitnessIds.size(),4u);for(const auto& [trial,id]:r.nativeTrialWitnessIds)
        EXPECT_EQ(r.capacitanceWitnesses.at(id).modelRevision,r.logical.baseModelRevision);}}
    else EXPECT_TRUE(f.owner->OwnedNativeCapacitanceState().isEmpty());
    SaveWindowService(f,defaultSync?"default-sync":c0?"bound-C0":n0?mode?"N0-mode1":"N0-mode0":"N1-real-domain");
}
template<class Owner> void WindowServiceGrowth(bool warm) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto plan=ActualWindowServicePlan(f,.02,false);plan.search.maximumCandidatesPerInput=2;
    plan.search.bounds[0].minimumLength=2;plan.search.bounds[0].maximumLength=3;bool stoppedOnOwnedGrowth=false;
    ServiceStart(f,plan);
    ServiceTicks(f,[&](){const auto& service=f.owner->NativeTrainingController();if(warm && !stoppedOnOwnedGrowth && service.State()==NativeTrainingState::Searching &&
        service.ModelEpoch()>0 && f.owner->ReadNativeParameters()[0].length==3){stoppedOnOwnedGrowth=true;f.owner->IsNeedToTrain=false;}});
    const auto& first=f.owner->NativeTrainingController();ASSERT_TRUE(first.References());const auto references=*first.References();
    const auto source=first.CompositeSourceBinding();const auto initial=first.CompositeInitialConfiguration();const auto oldGroups=first.CompositeReferenceGroupIds();
    const auto history=first.CompositeMeasurements().size();ASSERT_TRUE(first.Search());EXPECT_GT(first.Search()->AppliedEdits(),0u);
    if(warm) {
        ASSERT_TRUE(stoppedOnOwnedGrowth);ASSERT_EQ(f.owner->ReadNativeParameters()[0].length,3);ASSERT_NE(f.Revision(),references.InitialModelRevision());
        SaveWindowService(f,"grown-before-warm");f.owner->Reset();bool stoppedOnFreshInput=false;
        plan.compositeSink=[&](const auto& record){if(record.purpose==CompositeMeasurementPurpose::Search && record.logical.inputIndex==0 && record.consumed){
            stoppedOnFreshInput=true;f.owner->IsNeedToTrain=false;}};
        f.owner->BeginNativeTraining(plan);ASSERT_EQ(first.State(),NativeTrainingState::Searching)<<first.Reason();EXPECT_EQ(first.SessionAttempt(),2u);
        EXPECT_EQ(first.CompositeMeasurements().size(),history);EXPECT_EQ(first.CompositeGroups(),0u);EXPECT_EQ(first.CompositeNativeProbes(),0u);
        EXPECT_EQ(first.References()->Inputs(),references.Inputs());EXPECT_EQ(f.owner->ReadNativeParameters()[0].length,3);
        ServiceTicks(f);ASSERT_TRUE(stoppedOnFreshInput);EXPECT_EQ(first.Outcome(),TrainingStatus::ExternalStop);EXPECT_FALSE(first.Certificate());
        EXPECT_EQ(first.CompositeSourceBinding(),source);EXPECT_EQ(first.CompositeInitialConfiguration(),initial);EXPECT_EQ(first.CompositeReferenceGroupIds(),oldGroups);
        EXPECT_GT(first.CompositeMeasurements().size(),history);
        for(const auto& r:first.CompositeMeasurements())if(r.attemptId==first.Configuration().runId && r.windowProposal)
            EXPECT_EQ(r.windowProposal->reference.initialParameters[0].length,2);
        for(const auto& id:oldGroups){const auto found=std::find_if(first.CompositeMeasurements().begin(),first.CompositeMeasurements().end(),[&](const auto& r){return r.groupId==id;});
            ASSERT_NE(found,first.CompositeMeasurements().end());EXPECT_NE(found->attemptId,first.Configuration().runId);}
        SaveWindowService(f,"warm-after-owned-growth");
    } else {
        EXPECT_NE(first.Outcome(),TrainingStatus::Exact);EXPECT_FALSE(first.Certificate());bool observedGrowth=false;
        for(const auto& r:first.CompositeMeasurements())if(r.purpose==CompositeMeasurementPurpose::Search && r.logical.inputIndex==0 && r.windowProposal &&
            r.windowProposal->candidate.parameters[0].length==3 && r.selection && r.selection->geometry && r.selection->geometry->measuredMaximum) {
            const auto& peak=*r.selection->geometry->measuredMaximum;EXPECT_GT(peak.time-r.group.witness.fullBefore.observation.begin,
                first.Plan().protocol.candidateWindowMeasurement->referenceInputWindows[0].endOffset);EXPECT_FALSE(r.semanticProofId.empty());observedGrowth=true;}
        EXPECT_TRUE(observedGrowth);EXPECT_EQ(first.CompositeFinalGroupIds().size(),2u);SaveWindowService(f,"actual-owned-growth-outside-initial-window");
    }
}
template<class Owner> void WindowServiceN1ActualDomain() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,false);auto plan=ActualWindowServicePlan(f,.02,false);plan.search.maximumCandidatesPerInput=2;
    // The initial physical candidate deliberately misses default sync. A
    // second bounded point requires the REAL native effective-domain action;
    // an engineering .2 immediate success would never reach that provider.
    ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();ASSERT_TRUE(service.Search());
    EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted)<<service.Reason();EXPECT_FALSE(service.Certificate());
    ASSERT_FALSE(service.Search()->Domains().empty());bool available=false;
    for(const auto& d:service.Search()->Domains())if(d.status==ResistanceDomainStatus::Available) {
        available=true;EXPECT_FALSE(d.previewModelJson.empty());EXPECT_FALSE(d.previewModelRevision.empty());EXPECT_EQ(d.geometry.size(),2u);
    }
    EXPECT_TRUE(available);EXPECT_EQ(service.Configuration().tolerances.sync,.02);EXPECT_EQ(service.Configuration().tolerances.amplitudeAbsolute,1e-5);
    EXPECT_EQ(service.CompositeFinalGroupIds().size(),2u);SaveWindowService(f,"N1-real-domain-default-sync");
}
template<class Owner> void WindowServicePartialWarm() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto plan=ActualWindowServicePlan(f,.2,false);bool stopped=false;
    plan.compositeSink=[&](const auto& r){if(!stopped && r.purpose==CompositeMeasurementPurpose::Reference && r.logical.inputIndex==0){stopped=true;f.owner->IsNeedToTrain=false;}};
    ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();ASSERT_TRUE(stopped);ASSERT_FALSE(service.References());
    ASSERT_EQ(service.CompositeMeasurements().size(),1u);const auto old=service.CompositeMeasurements()[0].groupId;const auto source=service.CompositeSourceBinding();
    EXPECT_FALSE(service.CompositeMeasurements()[0].consumed);EXPECT_FALSE(service.CompositeMeasurements()[0].trainingRequestedAtConsume);SaveWindowService(f,"partial-before-warm");
    f.owner->Reset();f.owner->BeginNativeTraining(plan);ASSERT_EQ(service.State(),NativeTrainingState::CapturingReferences)<<service.Reason();
    EXPECT_EQ(service.SessionAttempt(),2u);EXPECT_FALSE(service.References());EXPECT_EQ(service.CompositeGroups(),0u);ServiceTicks(f);
    ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();ASSERT_TRUE(service.References());EXPECT_EQ(service.CompositeSourceBinding(),source);
    ASSERT_FALSE(service.CompositeMeasurements().empty());EXPECT_EQ(service.CompositeMeasurements()[0].groupId,old);EXPECT_FALSE(service.CompositeMeasurements()[0].consumed);
    EXPECT_FALSE(service.CompositeMeasurements()[0].trainingRequestedAtConsume);for(const auto& id:service.CompositeReferenceGroupIds())EXPECT_NE(id,old);
    SaveWindowService(f,"partial-warm-fresh-allN");
}
enum class WindowServiceFault { NeedSetter,NeedDirect,NeedConnected,Source,FinalSinkStop,FinalSinkThrow };
template<class Owner> void WindowServiceRejectsCallbackFault(WindowServiceFault fault) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true,fault==WindowServiceFault::NeedConnected);auto plan=ActualWindowServicePlan(f,.2,false);bool reached=false;
    if(fault==WindowServiceFault::FinalSinkStop || fault==WindowServiceFault::FinalSinkThrow)plan.compositeSink=[&](const auto& r){
        if(r.purpose==CompositeMeasurementPurpose::Final && r.logical.inputIndex==(NativeCompositeFixture<Owner>::branch?0u:1u)) {
            reached=true;EXPECT_FALSE(f.owner->NativeTrainingController().Certificate());
            if(fault==WindowServiceFault::FinalSinkThrow)throw std::runtime_error("service5-final-sink-control");f.owner->IsNeedToTrain=false;}};
    else plan.beforeCompositeConsume=[&](const auto& r){if(r.purpose==CompositeMeasurementPurpose::Reference && r.logical.inputIndex==1){
        reached=true;EXPECT_FALSE(f.owner->NativeTrainingController().References());
        if(fault==WindowServiceFault::NeedSetter)f.owner->IsNeedToTrain=false;
        else if(fault==WindowServiceFault::NeedDirect)f.owner->IsNeedToTrain.SetDataDirect(false);
        else if(fault==WindowServiceFault::NeedConnected)f.flag->Value=false;
        else {const auto before=f.Revision();f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true)->Amplitude=1.5;EXPECT_EQ(f.Revision(),before);}}};
    ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();ASSERT_TRUE(reached);EXPECT_FALSE(service.Certificate());
    EXPECT_EQ(service.Outcome(),fault==WindowServiceFault::Source || fault==WindowServiceFault::FinalSinkThrow?TrainingStatus::InvalidObservation:TrainingStatus::ExternalStop);
    if(fault!=WindowServiceFault::FinalSinkStop && fault!=WindowServiceFault::FinalSinkThrow){EXPECT_FALSE(service.References());EXPECT_TRUE(service.CompositeReferenceGroupIds().empty());
        for(const auto& r:service.CompositeMeasurements()){EXPECT_FALSE(r.consumed);EXPECT_FALSE(r.trainingRequestedAtConsume);}}
    SaveWindowService(f,"callback-fault");
}
template<class Owner> void WindowServiceMergedIsDiagnostic() {
    NativeCompositeFixture<Owner> f(2000,true,64,false,true);auto plan=ActualWindowServicePlan(f,.2,false);ServiceStart(f,plan);ServiceTicks(f);
    const auto& service=f.owner->NativeTrainingController();EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    ASSERT_FALSE(service.CompositeMeasurements().empty());const auto& r=service.CompositeMeasurements().back();EXPECT_FALSE(r.consumed);
    ASSERT_TRUE(r.selection);ASSERT_TRUE(r.selection->geometry);EXPECT_NE(r.selection->geometry->validity,DeclaredWindowBasinValidity::Valid);SaveWindowService(f,"merged-diagnostic");
}
template<class Owner> void WindowServicePreservesClippedGroupBudget() {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto plan=ActualWindowServicePlan(f,.2,false);plan.maximumModelSeconds=.8;plan.composite->maximumGroupModelSeconds=.8;
    ServiceStart(f,plan);ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);
    EXPECT_FALSE(service.Certificate());EXPECT_FALSE(service.References());bool clipped=false;
    for(const auto& r:service.CompositeMeasurements()){EXPECT_EQ(r.policy.maximumGroupModelSeconds,r.maximumGroupModelSeconds);
        if(r.maximumGroupModelSeconds<plan.composite->maximumGroupModelSeconds){clipped=true;EXPECT_FALSE(r.consumed);EXPECT_NE(r.groupState,NativeMatchedOmissionState::Completed);}}
    EXPECT_TRUE(clipped);EXPECT_GT(service.CompositeSampledFrames(),0u);SaveWindowService(f,"actual-clipped-group-budget");
}
}
TEST(NativeCandidateWindowService,ClassicN0CalculateMode0FreshAllNFinal){WindowServiceExact<NNeuronTimeLearner>(0);}
TEST(NativeCandidateWindowService,BranchN0CalculateMode0FreshAllNFinal){WindowServiceExact<NNeuronTimeLearnerBranch>(0);}
TEST(NativeCandidateWindowService,ClassicN0CalculateMode1FreshAllNFinal){WindowServiceExact<NNeuronTimeLearner>(1);}
TEST(NativeCandidateWindowService,BranchN0CalculateMode1FreshAllNFinal){WindowServiceExact<NNeuronTimeLearnerBranch>(1);}
TEST(NativeCandidateWindowService,ClassicN1UsesActualEffectiveDomainProvider){WindowServiceN1ActualDomain<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowService,BranchN1UsesActualEffectiveDomainProvider){WindowServiceN1ActualDomain<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowService,ClassicDefaultSyncRemainsNonExact){WindowServiceExact<NNeuronTimeLearner>(1,true,false,true);}
TEST(NativeCandidateWindowService,BranchDefaultSyncRemainsNonExact){WindowServiceExact<NNeuronTimeLearnerBranch>(1,true,false,true);}
TEST(NativeCandidateWindowService,ClassicBoundC0WitnessesStayOnBaseRevision){WindowServiceExact<NNeuronTimeLearner>(1,true,true);}
TEST(NativeCandidateWindowService,BranchBoundC0WitnessesStayOnBaseRevision){WindowServiceExact<NNeuronTimeLearnerBranch>(1,true,true);}
TEST(NativeCandidateWindowService,ClassicWarmAfterOwnedGrowthKeepsOriginalTargetsAndHistory){WindowServiceGrowth<NNeuronTimeLearner>(true);}
TEST(NativeCandidateWindowService,BranchWarmAfterOwnedGrowthKeepsOriginalTargetsAndHistory){WindowServiceGrowth<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCandidateWindowService,ClassicPartialWarmDiscardsExpiredSeedsAndRecapturesAllN){WindowServicePartialWarm<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowService,BranchPartialWarmDiscardsExpiredSeedsAndRecapturesAllN){WindowServicePartialWarm<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowService,ClassicSetterFalseBeforeAllNDoesNotPromotePrefix){WindowServiceRejectsCallbackFault<NNeuronTimeLearner>(WindowServiceFault::NeedSetter);}
TEST(NativeCandidateWindowService,BranchDirectFalseBeforeAllNDoesNotPromotePrefix){WindowServiceRejectsCallbackFault<NNeuronTimeLearnerBranch>(WindowServiceFault::NeedDirect);}
TEST(NativeCandidateWindowService,ClassicConnectedFalseBeforeAllNDoesNotPromotePrefix){WindowServiceRejectsCallbackFault<NNeuronTimeLearner>(WindowServiceFault::NeedConnected);}
TEST(NativeCandidateWindowService,BranchActualSourceEditBeforeReleaseDoesNotPromotePrefix){WindowServiceRejectsCallbackFault<NNeuronTimeLearnerBranch>(WindowServiceFault::Source);}
TEST(NativeCandidateWindowService,ClassicLastSinkStopCannotPublishCertificate){WindowServiceRejectsCallbackFault<NNeuronTimeLearner>(WindowServiceFault::FinalSinkStop);}
TEST(NativeCandidateWindowService,BranchLastSinkThrowCannotPublishCertificate){WindowServiceRejectsCallbackFault<NNeuronTimeLearnerBranch>(WindowServiceFault::FinalSinkThrow);}
TEST(NativeCandidateWindowService,ClassicOwnedGrowthMeasuresPeakBeyondInitialReferenceWindow){WindowServiceGrowth<NNeuronTimeLearner>(false);}
TEST(NativeCandidateWindowService,BranchOwnedGrowthMeasuresPeakBeyondInitialReferenceWindow){WindowServiceGrowth<NNeuronTimeLearnerBranch>(false);}
TEST(NativeCandidateWindowService,ClassicMergedVertexRemainsDiagnostic){WindowServiceMergedIsDiagnostic<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowService,BranchMergedVertexRemainsDiagnostic){WindowServiceMergedIsDiagnostic<NNeuronTimeLearnerBranch>();}
TEST(NativeCandidateWindowService,ClassicActualClippedGroupBudgetIsNotReplacedByPlanCap){WindowServicePreservesClippedGroupBudget<NNeuronTimeLearner>();}
TEST(NativeCandidateWindowService,BranchActualClippedGroupBudgetIsNotReplacedByPlanCap){WindowServicePreservesClippedGroupBudget<NNeuronTimeLearnerBranch>();}

namespace {
template<class Owner> void WindowManualClosedMeasurementAuthority(bool foreignService) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);
    // Declare the foreign plan before the manual reference capture. This also
    // enables protocol5 once; no late window/source retarget is involved.
    const auto earliestAttemptModel=f.Time(),earliestAttemptWall=Wall();
    const auto foreignPlan=ActualWindowServicePlan(f,.2,false);
    const auto refs=CaptureWindowReferences(f);
    VerificationConfig config{"candidate-attempt/final/1",f.Revision(),4,0,0};config.tolerances.sync=.2;
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),config);
    const auto request=final.NextRequest();ASSERT_TRUE(request);
    // Keep the original, REAL group/attempt clocks alive across several later
    // native groups. A short default deadline would mask the ownership issue.
    constexpr double groupModelLimit=30.,groupWallLimit=3600.;
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmCandidateWindow(p);},{},groupModelLimit,groupWallLimit);
    ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();
    const auto pending=*f.attempt->Measurement();const auto pendingRecord=f.attempt->Record();
    const auto cachedRevision=f.Revision();const auto ownerLife=f.owner->ObserveLifecycle();
    const auto oldC0=f.owner->OwnedNativeCapacitanceState();ASSERT_TRUE(oldC0.isEmpty());
    ASSERT_TRUE(pendingRecord.windowProposal);ASSERT_TRUE(pendingRecord.candidateWindowSpecification);
    ASSERT_EQ(pendingRecord.windowProposal->candidateModelRevision,cachedRevision);
    const auto frozenProposal=EncodeCandidateWindowProposalData(*pendingRecord.windowProposal);
    const auto neuron=f.owner->template GetComponentL<NPulseNeuron>("Neuron",true);
    const auto dataset=f.owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    const auto source=f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    ASSERT_TRUE(neuron);ASSERT_TRUE(dataset);ASSERT_TRUE(source);
    const auto datasetIdentity=NmsdkTools::IdentifyModel(dataset.Get());ASSERT_TRUE(datasetIdentity["valid"].toBool());
    const auto beforeTime=f.Time();const auto oldGroups=f.attempt->IssuedGroups(),oldProbes=f.attempt->IssuedNativeProbes();
    const auto stage=foreignService?"foreign-service-old-pending":"own-next-group-old-pending";
    SaveCandidateWindowGroup(f,stage);
    const auto name=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-live-authority/":"classic-window-live-authority/")+
        (foreignService?"foreign-finished":"own-next-group");
    const auto historicalArchive=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);
    SaveCompositeArchive(historicalArchive,(name+"/old-manual-journal").c_str());
    ASSERT_EQ(final.AcceptedInputs(),0u);ASSERT_FALSE(final.Certificate());
    const auto oldFamily=f.attempt->OwnerFamilyBinding();
    std::unique_ptr<NativeCompositeTrainingAttempt> retainedManual;
    if(foreignService) {
        // Deliberately retain the old public manual actor. ServiceStart would
        // destroy it, preventing this exact takeover/release regression.
        retainedManual=std::move(f.attempt);
        f.owner->CalculateMode=1;f.owner->BeginNativeTraining(foreignPlan,true);
        ASSERT_EQ(f.owner->NativeTrainingController().State(),NativeTrainingState::CapturingReferences)
            <<f.owner->NativeTrainingController().Reason();
        ServiceTicks(f);const auto& service=f.owner->NativeTrainingController();
        ASSERT_EQ(service.State(),NativeTrainingState::Finished);ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();
        ASSERT_TRUE(service.Search());ASSERT_EQ(service.Search()->AppliedEdits(),0u);
        ASSERT_EQ(service.SessionAttempt(),1u);ASSERT_NE(service.CompositeOwnerFamilyBinding(),oldFamily);
        ASSERT_EQ(retainedManual->IssuedGroups(),oldGroups);ASSERT_EQ(retainedManual->IssuedNativeProbes(),oldProbes);
        SaveWindowService(f,"foreign-finished-while-manual-proof-pending");
    } else {
        // A new raw executor generation belonging to THIS manual actor must
        // not revoke an otherwise current closed measurement by itself.
        const auto next=f.Request(0,"candidate-attempt","candidate-attempt/search/999");
        f.Run(next,CompositeMeasurementPurpose::Search,{},{},groupModelLimit,groupWallLimit);
        ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();SaveCandidateWindowGroup(f,"own-intervening-group");
        ASSERT_EQ(f.attempt->IssuedGroups(),oldGroups+1);ASSERT_EQ(f.attempt->IssuedNativeProbes(),oldProbes+4);
        const auto ownRecord=f.attempt->Record();ASSERT_TRUE(ownRecord.windowProposal);
        ASSERT_EQ(ownRecord.windowProposal->candidateModelRevision,pendingRecord.windowProposal->candidateModelRevision);
        ASSERT_EQ(ownRecord.windowProposal->candidateBinding,pendingRecord.windowProposal->candidateBinding);
    }
    // Ordinary scheduler execution advanced native time. No Reset, Build,
    // source/parameter edit, graph replacement or synthetic clock is used.
    ASSERT_GT(f.Time(),beforeTime);ASSERT_TRUE(ownerLife.IsCurrent());ASSERT_TRUE(f.owner->IsNeedToTrain.GetData());
    ASSERT_EQ(f.owner->template GetComponentL<NPulseNeuron>("Neuron",true).Get(),neuron.Get());
    ASSERT_EQ(f.owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true).Get(),dataset.Get());
    ASSERT_EQ(f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true).Get(),source.Get());
    ASSERT_EQ(f.Revision(),cachedRevision);
    ASSERT_EQ(f.owner->OwnedNativeCapacitanceState(),oldC0);EXPECT_FALSE(f.owner->ReadNativeTrainingCapacitance());
    const auto afterDataset=NmsdkTools::IdentifyModel(dataset.Get());ASSERT_TRUE(afterDataset["valid"].toBool());
    ASSERT_EQ(afterDataset["model"],datasetIdentity["model"]);
    // Portable replay is intentionally independent of the current executor
    // owner. A takeover does not erase valid historical full/omit/repeat DATA.
    const auto historicalReplay=DecodeNativeCompositeTrainingArchive(historicalArchive.document);
    ASSERT_EQ(historicalReplay.ReferenceGroups().size(),2u);ASSERT_EQ(historicalReplay.Records().size(),3u);
    ASSERT_EQ(historicalReplay.Records().back().groupId,pendingRecord.groupId);
    ASSERT_EQ(historicalReplay.Records().back().semanticProofId,pending.SemanticProofId());
    ASSERT_TRUE(historicalReplay.Records().back().windowProposal);
    ASSERT_EQ(EncodeCandidateWindowProposalData(*historicalReplay.Records().back().windowProposal),frozenProposal);
    const auto admissionModel=f.Time(),admissionWall=Wall();
    ASSERT_LT(admissionModel-pendingRecord.startModel,pendingRecord.maximumGroupModelSeconds);
    ASSERT_LT(admissionWall-pendingRecord.startWall,pendingRecord.maximumGroupWallSeconds);
    // These REAL timestamps precede actor construction, so the differences
    // conservatively upper-bound the attempt's own elapsed values.
    ASSERT_LT(admissionModel-earliestAttemptModel,pendingRecord.attemptLimits.maximumModelSeconds);
    ASSERT_LT(admissionWall-earliestAttemptWall,pendingRecord.attemptLimits.maximumWallSeconds);
    final.ConsumeCandidateWindow(pending,cachedRevision);
    // Save the ACTUAL observation even when the proposed negative assertion
    // below is red. Historical data validity is not a current live lease.
    SavePortableObject(name.c_str(),"live-authority-observation.json",{{"kind","candidate_window_manual_live_authority_control"},{"schema_version",1},
        {"foreign_service_executed",foreignService},{"declared_expected_live_revocation",foreignService},
        {"old_group_id",QString::fromStdString(pendingRecord.groupId)},{"old_family",QString::fromStdString(oldFamily)},
        {"old_logical_run",QString::fromStdString(pendingRecord.logical.runId)},{"old_logical_trial",QString::fromStdString(pendingRecord.logical.trialId)},
        {"historical_measurement_primary_retained",true},{"historical_archive_replayed_after_intervening_work",true},
        {"historical_semantic_proof_id",QString::fromStdString(pending.SemanticProofId())},
        {"owner_lifecycle_current",ownerLife.IsCurrent()},{"actual_need_to_train",f.owner->IsNeedToTrain.GetData()},
        {"model_revision_before",QString::fromStdString(cachedRevision)},{"model_revision_after",QString::fromStdString(f.Revision())},
        {"group_start_model",pendingRecord.startModel},{"admission_model",admissionModel},{"group_model_limit",pendingRecord.maximumGroupModelSeconds},
        {"group_start_wall",pendingRecord.startWall},{"admission_wall",admissionWall},{"group_wall_limit",pendingRecord.maximumGroupWallSeconds},
        {"earliest_attempt_model",earliestAttemptModel},{"earliest_attempt_wall",earliestAttemptWall},
        {"attempt_model_limit",pendingRecord.attemptLimits.maximumModelSeconds},{"attempt_wall_limit",pendingRecord.attemptLimits.maximumWallSeconds},
        {"actual_C0_remains_absent",f.owner->OwnedNativeCapacitanceState().isEmpty()},
        {"executor_control_generation_publicly_observed",false},{"actual_final_status",VerificationStatusName(final.Status())},
        {"actual_accepted_inputs",double(final.AcceptedInputs())},{"certificate",final.Certificate()?QJsonValue(EncodeTrainingCertificate(*final.Certificate())):QJsonValue(QJsonValue::Null)}});
    SaveCompositeBoundary(f,name.c_str());
    if(foreignService) {
        // Expected control contract, not a claim that Pulse800 implements it.
        // Foreign Begin takes over the same executor; Finished/Need=true must
        // not revive the old actor's authority to accept a NEW final input.
        EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
    } else {
        ASSERT_EQ(final.AcceptedInputs(),1u);ASSERT_EQ(final.Status(),VerificationStatus::Collecting);
        const auto last=final.NextRequest();ASSERT_TRUE(last);
        f.Run(*last,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmCandidateWindow(p);},{},groupModelLimit,groupWallLimit);
        ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();SaveCandidateWindowGroup(f,"own-next-group-final-input1");
        final.ConsumeCandidateWindow(*f.attempt->Measurement(),f.Revision());
        ASSERT_TRUE(final.Certificate());EXPECT_EQ(final.AcceptedInputs(),2u);EXPECT_EQ(final.Status(),VerificationStatus::Exact);
        SaveWindowCoreCertificate(f,"own-next-groups-still-allowed",*final.Certificate());
        SaveCompositeArchive(EncodeNativeCandidateWindowTrainingArchive(*f.attempt),(name+"/after-own-groups-journal").c_str());
    }
}
}
TEST(NativeCandidateWindowManualAuthority,ClassicForeignBeginThenFinishedDoesNotReviveOldManualConsume){WindowManualClosedMeasurementAuthority<NNeuronTimeLearner>(true);}
TEST(NativeCandidateWindowManualAuthority,BranchForeignBeginThenFinishedDoesNotReviveOldManualConsume){WindowManualClosedMeasurementAuthority<NNeuronTimeLearnerBranch>(true);}
TEST(NativeCandidateWindowManualAuthority,ClassicOwnNextGroupsKeepCurrentClosedMeasurementUsable){WindowManualClosedMeasurementAuthority<NNeuronTimeLearner>(false);}
TEST(NativeCandidateWindowManualAuthority,BranchOwnNextGroupsKeepCurrentClosedMeasurementUsable){WindowManualClosedMeasurementAuthority<NNeuronTimeLearnerBranch>(false);}

namespace {
enum class ManualTakeoverKind { FailedBegin,ScalarThree,FixedFour };
template<class Owner> void WindowManualOtherServiceTakeover(ManualTakeoverKind kind) {
    NativeCompositeFixture<Owner> f(2000,false,64,false,true);auto legacy=CompositeCold(f);
    if(kind==ManualTakeoverKind::ScalarThree)legacy.composite.reset();
    auto foreign=MakeConfiguredNativeTrainingPlan(legacy);
    const auto earliestAttemptModel=f.Time(),earliestAttemptWall=Wall();
    if(kind==ManualTakeoverKind::FailedBegin) {
        foreign=ActualWindowServicePlan(f,.2,false);foreign.maximumReferenceProbes=0;
    } else EnableCandidateWindow(f);
    const auto refs=CaptureWindowReferences(f);VerificationConfig config{"candidate-attempt/final/1",f.Revision(),4,0,0};config.tolerances.sync=.2;
    FinalVerificationSession final(refs,*f.attempt->CandidateWindowReferences(),config);const auto request=final.NextRequest();ASSERT_TRUE(request);
    f.Run(*request,CompositeMeasurementPurpose::Final,[&](const auto& p){final.ArmCandidateWindow(p);},{},30.,3600.);
    ASSERT_TRUE(f.attempt->Measurement())<<f.attempt->RejectionReason();const auto pending=*f.attempt->Measurement();const auto record=f.attempt->Record();
    const auto beforeRevision=f.Revision();const auto beforeC0=f.owner->OwnedNativeCapacitanceState();
    const auto life=f.owner->ObserveLifecycle();const auto neuron=f.owner->template GetComponentL<NPulseNeuron>("Neuron",true);
    const auto dataset=f.owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    const auto source=f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    const auto beforeSource=NmsdkTools::IdentifyModel(dataset.Get());ASSERT_TRUE(beforeSource["valid"].toBool());ASSERT_TRUE(beforeC0.isEmpty());
    const auto name=std::string(NativeCompositeFixture<Owner>::branch?"branch-window-control-lifetime/":"classic-window-control-lifetime/")+
        (kind==ManualTakeoverKind::FailedBegin?"failed-begin":kind==ManualTakeoverKind::ScalarThree?"scalar3-takeover":"fixed4-takeover");
    SaveCandidateWindowGroup(f,"old-before-other-service");const auto historical=EncodeNativeCandidateWindowTrainingArchive(*f.attempt);
    SaveCompositeArchive(historical,(name+"/old-journal").c_str());
    std::size_t foreignSamples=0,foreignPrepared=0;std::unique_ptr<NmsdkWorker::EvidenceWriter> scalarWriter;
    if(kind==ManualTakeoverKind::ScalarThree) {
        // A real scalar3 source/probe dispatch, stopped by ACTUAL model time.
        // No Exact claim or invented complete scalar observation is needed.
        foreign.maximumModelSeconds=.03;foreign.maximumWallSeconds=7200.;
        if(const auto output=std::getenv("TIMELEARNER_COMPOSITE_OUTPUT")) {
            const auto directory=QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"/foreign-scalar3";
            Require(QDir().mkpath(directory),"control_lifetime_scalar_directory");
            scalarWriter=std::make_unique<NmsdkWorker::EvidenceWriter>(directory,NativeCompositeFixture<Owner>::branch?1u:2u);
        }
        foreign.probe.onPrepared=[&](const auto& p,const auto& s){++foreignPrepared;if(scalarWriter)scalarWriter->Prepared(p,s);};
        foreign.probe.onSample=[&](const auto& s){++foreignSamples;if(scalarWriter)scalarWriter->Sample(s);};
        foreign.observationSink=[&](const auto& p){if(scalarWriter)scalarWriter->Observation(p);};
    }
    if(kind==ManualTakeoverKind::FixedFour)foreign.maximumModelSeconds=.8;
    auto old=std::move(f.attempt);const auto beforeTime=f.Time();f.owner->CalculateMode=1;f.owner->BeginNativeTraining(foreign,true);
    const auto& service=f.owner->NativeTrainingController();
    if(kind==ManualTakeoverKind::FailedBegin) {
        ASSERT_EQ(service.State(),NativeTrainingState::Finished);ASSERT_EQ(service.Outcome(),TrainingStatus::InvalidModel);
        ASSERT_EQ(service.SessionAttempt(),0u);ASSERT_EQ(service.CompositeNativeProbes(),0u);ASSERT_EQ(f.Time(),beforeTime);
        ASSERT_TRUE(service.CompositeSourceBinding().isEmpty()); // Failed BEFORE any service-owned actor exists.
    } else {
        ASSERT_EQ(service.State(),NativeTrainingState::CapturingReferences)<<service.Reason();ASSERT_EQ(service.SessionAttempt(),1u);
        ASSERT_EQ(service.Plan().protocol.schemaVersion,kind==ManualTakeoverKind::ScalarThree?3u:4u);
        ServiceTicks(f);ASSERT_EQ(service.State(),NativeTrainingState::Finished);ASSERT_GT(f.Time(),beforeTime);
        ASSERT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted)<<service.Reason();
        EXPECT_FALSE(service.Search() && service.Search()->AppliedEdits());
        if(kind==ManualTakeoverKind::ScalarThree) {
            ASSERT_GT(foreignPrepared,0u);ASSERT_GT(foreignSamples,0u);ASSERT_FALSE(service.ObservedPackets().empty());
            if(scalarWriter)SavePortableObject((name+"/foreign-scalar3").c_str(),"artifacts.json",{{"primary_files",scalarWriter->FinalizeWithPrefix("foreign_scalar3_trial_")}});
        } else {
            ASSERT_GT(service.CompositeNativeProbes(),0u);
            SaveCompositeArchive(EncodeNativeCompositeTrainingArchive(service),(name+"/foreign-fixed4").c_str());
        }
    }
    ASSERT_TRUE(life.IsCurrent());ASSERT_TRUE(f.owner->IsNeedToTrain.GetData());ASSERT_EQ(f.Revision(),beforeRevision);
    ASSERT_EQ(f.owner->OwnedNativeCapacitanceState(),beforeC0);
    ASSERT_EQ(f.owner->template GetComponentL<NPulseNeuron>("Neuron",true).Get(),neuron.Get());
    ASSERT_EQ(f.owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true).Get(),dataset.Get());
    ASSERT_EQ(f.owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true).Get(),source.Get());
    const auto afterSource=NmsdkTools::IdentifyModel(dataset.Get());ASSERT_TRUE(afterSource["valid"].toBool());ASSERT_EQ(afterSource["model"],beforeSource["model"]);
    const auto replay=DecodeNativeCompositeTrainingArchive(historical.document);ASSERT_EQ(replay.Records().back().semanticProofId,pending.SemanticProofId());
    ASSERT_LT(f.Time()-record.startModel,record.maximumGroupModelSeconds);ASSERT_LT(Wall()-record.startWall,record.maximumGroupWallSeconds);
    ASSERT_LT(f.Time()-earliestAttemptModel,record.attemptLimits.maximumModelSeconds);ASSERT_LT(Wall()-earliestAttemptWall,record.attemptLimits.maximumWallSeconds);
    final.ConsumeCandidateWindow(pending,beforeRevision);
    QJsonArray rejections;for(const auto& r:final.Rejected())rejections.append(QString::fromStdString(r.reason));
    SavePortableObject(name.c_str(),"actual-authority-boundary.json",{{"kind","manual_control_lifetime_other_service_boundary"},{"schema_version",1},
        {"case",int(kind)},{"foreign_state",NativeTrainingStateName(service.State())},{"foreign_outcome",TrainingStatusName(service.Outcome())},
        {"foreign_reason",QString::fromStdString(service.Reason())},{"foreign_session_attempt",double(service.SessionAttempt())},
        {"foreign_prepared",double(foreignPrepared)},{"foreign_sampled_frames",double(foreignSamples)},
        {"actual_final_status",VerificationStatusName(final.Status())},{"actual_accepted_inputs",double(final.AcceptedInputs())},{"rejections",rejections},
        {"historical_archive_replayed",true},{"actual_need",f.owner->IsNeedToTrain.GetData()},
        {"actual_model_revision",QString::fromStdString(f.Revision())},{"native_time",f.Time()},{"group_start_model",record.startModel},
        {"group_model_limit",record.maximumGroupModelSeconds},{"actual_group_wall_elapsed",Wall()-record.startWall},{"group_wall_limit",record.maximumGroupWallSeconds}});
    SaveCompositeBoundary(f,name.c_str());EXPECT_EQ(final.Status(),VerificationStatus::InvalidObservation);EXPECT_EQ(final.AcceptedInputs(),0u);EXPECT_FALSE(final.Certificate());
    ASSERT_FALSE(final.Rejected().empty());EXPECT_EQ(final.Rejected().back().reason,"native_training_owner_control_replaced");
}
}
TEST(NativeManualControlLifetime,ClassicFailedBeginWithoutStoredCompositeRevokesClosedConsume){WindowManualOtherServiceTakeover<NNeuronTimeLearner>(ManualTakeoverKind::FailedBegin);}
TEST(NativeManualControlLifetime,BranchFailedBeginWithoutStoredCompositeRevokesClosedConsume){WindowManualOtherServiceTakeover<NNeuronTimeLearnerBranch>(ManualTakeoverKind::FailedBegin);}
TEST(NativeManualControlLifetime,ClassicActualScalar3TakeoverRevokesClosedConsume){WindowManualOtherServiceTakeover<NNeuronTimeLearner>(ManualTakeoverKind::ScalarThree);}
TEST(NativeManualControlLifetime,BranchActualScalar3TakeoverRevokesClosedConsume){WindowManualOtherServiceTakeover<NNeuronTimeLearnerBranch>(ManualTakeoverKind::ScalarThree);}
TEST(NativeManualControlLifetime,ClassicActualFixed4TakeoverRevokesClosedConsume){WindowManualOtherServiceTakeover<NNeuronTimeLearner>(ManualTakeoverKind::FixedFour);}
TEST(NativeManualControlLifetime,BranchActualFixed4TakeoverRevokesClosedConsume){WindowManualOtherServiceTakeover<NNeuronTimeLearnerBranch>(ManualTakeoverKind::FixedFour);}
