#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeCompositeTrainingAttempt.h"
#include "TimeLearner/CompositeTrainingDeclarations.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/MatchedOmissionEvidenceJson.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <limits>
#include <map>
#include <stdexcept>
#include <type_traits>

namespace {
using namespace RDK;using namespace NMSDK;using namespace NMSDK::TimeLearner;
static_assert(!std::is_default_constructible_v<PreparedCompositeMeasurement>);
static_assert(!std::is_default_constructible_v<ValidatedCompositeMeasurement>);
static_assert(!std::is_aggregate_v<PreparedCompositeMeasurement>);
static_assert(!std::is_aggregate_v<ValidatedCompositeMeasurement>);
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
    NativeCompositeFixture(unsigned hz=2000,bool merged=false,std::size_t groupBudget=64,bool bindC0=false,bool n0=false,bool connectedNeed=false,std::size_t dimension=2,double wallBudget=0.):frequency(hz) {
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
        for(std::size_t i=0;i<dimension;++i){s.inputs.push_back({i+1==dimension?1:2,1,{}});s.initialIsi.push_back(i?((merged && i==1)?.001:.08):.01);}
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
    EXPECT_THROW(EncodeTrainingCertificate(certificate),std::invalid_argument); // No fake old-schema export.
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
    EXPECT_THROW(EncodeVerificationProtocol(f.protocol),std::invalid_argument);
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
    EXPECT_NE(service.Outcome(),TrainingStatus::Exact);ASSERT_TRUE(service.Certificate());
    EXPECT_FALSE(service.Certificate()->Exact());EXPECT_DOUBLE_EQ(service.Certificate()->Tolerances().sync,.02);
    EXPECT_GT(std::max(std::fabs(service.Certificate()->Residuals().front().timingResidualLow),
        std::fabs(service.Certificate()->Residuals().front().timingResidualHigh)),.02);
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
    f.owner->CalculateMode=mode;f.owner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(c)).toJson(QJsonDocument::Compact).toStdString();
    f.owner->ControllerVersion=2;f.owner->Build();ASSERT_TRUE(f.owner->IsReady());
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
