#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseChannel.h"
#include "NPulseSynapse.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ModelInspection.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QFile>
#include <QDir>
#include <QJsonArray>
#include <QJsonDocument>
#include <sstream>
#include <iomanip>
#include <locale>
#include <cstdlib>
#include <type_traits>
#include <limits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
void Artifact(const std::string& name,const QByteArray& data)
{
    if(const auto directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(directory)));
        QFile file(QString::fromLocal8Bit(directory)+"/"+QString::fromStdString(name));
        ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_EQ(file.write(data),data.size());
    }
}
template<class Learner> struct EditingRig {
    bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    unsigned frequency;int normalization;
    std::size_t inputCount=2;
    std::string name;
    UEPtr<UEnvironment> environment;
    UEPtr<UContainer> model;
    UEPtr<Learner> learner;
    UEPtr<NPulseNeuron> neuron;
    UEPtr<NPulseGeneratorTransit> source;
    NmsdkTools::ModelBoundarySources ports;
    std::size_t serial=0;
    double duration=.18;
    std::vector<double> isi{.01,.08};bool tightBurst=false;
    EditingRig(unsigned f,int mode,const std::string& suffix,bool tight=false,std::size_t inputs=2)
        :frequency(f),normalization(mode),inputCount(inputs),tightBurst(tight)
    {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        if(!environment->CreateModel("NModel"))throw std::runtime_error("editor_fixture_model");model=environment->GetModel();
        name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(f)+"_N"+std::to_string(mode)+"_"+suffix;
        StorageProfileSpec profile;profile.name=name;profile.frequencyHz=f;profile.neuronBaseClass="NSPNeuronGen";
        profile.initialThreshold=1.;profile.ltMembrane=profile.body;profile.ltMembrane->excChannel.capacity=.3e-9;
        const auto registered=RegisterStorageProfile(core.storage,environment,profile);
        learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        if(!learner)throw std::runtime_error("editor_fixture_learner");
        learner->Name="Learner";learner->StructureBuildMode=1;learner->NumInputDendrite=int(inputCount);
        std::vector<int> lengths(inputCount,1);if(inputCount==2)lengths[0]=2;
        learner->NeuronClassName=registered.neuronClass;learner->DendriteLength=lengths;
        learner->NormalizationMode=mode;learner->CalculateMode=1;learner->EnablePostTrainTuning=false;
        learner->AutoCalibrateFixedLTZThreshold=false;
        if(tight){duration=.08;isi={.005,.03};}
        else if(inputCount!=2){isi.assign(inputCount,.08);isi[0]=.01;duration=.01+.08*(inputCount-1)+.09;}
        MDMatrix<double> pattern;pattern.Assign(int(inputCount),1,0.);
        for(std::size_t i=0;i<inputCount;++i)pattern(int(i),0)=isi[i];learner->InputPattern=pattern;
        UEPtr<UContainer> component=learner;
        if(model->AddComponent(component)==ForbiddenId)throw std::runtime_error("editor_fixture_attach");
        model->SetGlobalTimeStep(f);model->Init();model->Reset();
        Artifact(name+"_startup_before.json",QJsonDocument(NmsdkTools::InspectModel(learner)).toJson());
        // The native scheduler completes ordinary lazy child initialization.
        // Capture fresh handles afterwards; the probe itself resets its physical
        // subtree before arming, so this is not training or a dynamic checkpoint.
        model->Calculate();environment->IncreaseModelTimeByStep();
        Artifact(name+"_startup_after.json",QJsonDocument(NmsdkTools::InspectModel(learner)).toJson());
        neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        source=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        if(!neuron || !source)throw std::runtime_error("editor_fixture_graph");ports.emplace(&source->Output,"burst");
    }
    ~EditingRig(){if(auto net=dynamic_pointer_cast<UNet>(model))net->BreakLinks();environment->DestroyModel();}
    std::string Revision() const {
        auto identity=NmsdkTools::IdentifyModel(neuron.Get(),ports);
        if(!identity["valid"].toBool())throw std::runtime_error("editor_fixture_identity");
        return identity["sha256"].toString().toStdString();
    }
    NativeProbeResult Probe(std::size_t input=0,const TrainingAction* action=nullptr,BoundedTrainingSession* session=nullptr)
    {
        NativeProbeRequest request;request.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        request.activeInput=int(input);request.inputId="input"+std::to_string(input);request.protocolRevision="editing_burst_v1";
        request.baseModelRevision=Revision();request.readModelRevision=[this]{return Revision();};request.expectedInputIsi=isi;
        auto& s=request.specification;s.schemaVersion=3;s.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
        s.runId=action?action->runId:name;s.trialId=action?action->trialId:name+"/trial/"+std::to_string(++serial);
        QJsonArray actualPattern;for(double value:isi)actualPattern.append(value);
        s.sampleId="target";s.patternHash=NmsdkTools::CanonicalModelDataSha256(actualPattern).toStdString();
        s.end=duration;s.maximumSampleGap=1./frequency;
        s.maximumSamples=std::size_t((duration+.01)*frequency);
        for(std::size_t i=0;i<inputCount;++i)s.expectedStimulusIds.push_back("pulse"+std::to_string(i));
        double onset=0.;for(std::size_t i=0;i<=input;++i)onset+=isi[i];
        s.windows={{request.inputId,branch?0u:input,onset,onset+(tightBurst?.025:.065),"pulse"+std::to_string(input)}};
        if(action)request.modelEpoch=action->modelEpoch;
        if(session)request.onPrepared=[&](const auto& prepared,const ProbeSpec&){session->Arm(action->serial,prepared);};
        std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(unsigned i=0;i<(branch?1u:inputCount);++i)trace<<",soma"<<i;trace<<'\n';
        request.onSample=[&](const NativeProbeSample& sample) {
            trace<<sample.time<<','<<sample.stimulus;for(double potential:sample.potentials)trace<<','<<potential;trace<<'\n';
        };
        const auto trial=s.trialId;
        learner->QueueNativeProbe(std::move(request));unsigned ticks=0;
        while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
        {
            if(++ticks>unsigned((duration+.02)*frequency))throw std::runtime_error("editor_fixture_probe_budget");
            model->Calculate();environment->IncreaseModelTimeByStep();
        }
        auto result=learner->TakeNativeProbeResult();if(!result)throw std::runtime_error("missing_editor_fixture_result");
        Artifact(name+"_probe_"+std::to_string(++serial)+".csv",QByteArray::fromStdString(trace.str()));
        QJsonArray reasons,peaks;
        for(const auto& reason:result->reasons)reasons.append(QString::fromStdString(reason));
        if(result->observation)
        {
            for(const auto& reason:result->observation->reasons)reasons.append(QString::fromStdString(reason));
            for(const auto& peak:result->observation->peaks)peaks.append(QJsonObject{{"validity",PeakValidityName(peak.validity)},
                {"raw",peak.rawPotential?QJsonValue(*peak.rawPotential):QJsonValue(QJsonValue::Null)},
                {"time",peak.time?QJsonValue(*peak.time):QJsonValue(QJsonValue::Null)}});
        }
        Artifact(name+"_probe_"+std::to_string(serial)+".json",QJsonDocument(QJsonObject{
            {"trial_id",QString::fromStdString(trial)},{"status",NativeProbeStatusName(result->status)},
            {"base_revision",QString::fromStdString(result->currentBaseRevision)},
            {"valid",result->observation && result->observation->valid},{"complete",result->observation && result->observation->complete},
            {"reasons",reasons},{"peaks",peaks}}).toJson());
        return *result;
    }
};
template<class Learner> void CheckEdits(unsigned frequency,int normalization)
{
    EditingRig<Learner> rig(frequency,normalization,"native_model_edit");auto values=rig.learner->ReadNativeParameters();
    ASSERT_EQ(values.size(),2u);const auto initial=rig.Revision();
    const auto early=rig.learner->ApplyNativeParameters(values);EXPECT_EQ(early.status,NativeEditStatus::Rejected);
    EXPECT_EQ(early.reason,"native_edit_requires_consumed_probe_boundary");EXPECT_EQ(rig.Revision(),initial);
    auto first=rig.Probe();ASSERT_EQ(first.status,NativeProbeStatus::Completed);ASSERT_TRUE(first.observation);
    ASSERT_TRUE(first.observation->valid);
    const auto soma=rig.neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);ASSERT_TRUE(soma);
    const auto lt=rig.neuron->template GetComponentL<NPulseChannel>("LTMembrane.ExcChannel",true);ASSERT_TRUE(lt);
    soma->Capacity=1.41e-9;const double ltCapacity=lt->Capacity.GetData();
    const auto phase=rig.learner->TrainingPhase.GetData();const auto need=rig.learner->IsNeedToTrain.GetData();
    values[0].length=3;if(normalization==0)values[0].synapses=3;
    // Exercise the declared bank Rs also for N0: all newly created bank members
    // must get this learned value, while their other storage physics survives.
    values[0].resistance*=1.1;
    const auto beforeEdit=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);
    const auto edit=rig.learner->ApplyNativeParameters(values);
    Artifact(rig.name+"_edit.json",QJsonDocument(QJsonObject{{"status",NativeEditStatusName(edit.status)},
        {"reason",QString::fromStdString(edit.reason)},{"may_have_changed",edit.modelMayHaveChanged},
        {"before",beforeEdit},{"after",NmsdkTools::IdentifyModel(rig.neuron,rig.ports)}}).toJson());
    ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    EXPECT_EQ(edit.effective,values);EXPECT_TRUE(rig.learner->IsReady());EXPECT_TRUE(rig.learner->IsInit());
    for(int k=1;k<=values[0].synapses;++k)
    {
        auto member=rig.neuron->template GetComponentL<NPulseSynapse>("Dendrite1_3.ExcSynapse"+std::to_string(k),true);
        ASSERT_TRUE(member);EXPECT_EQ(member->Resistance.GetData(),values[0].resistance);
    }
    EXPECT_EQ(rig.learner->DendriteLength.GetData(),(std::vector<int>{3,1}));
    EXPECT_EQ(rig.learner->TrainingPhase.GetData(),phase);EXPECT_EQ(rig.learner->IsNeedToTrain.GetData(),need);
    EXPECT_EQ(soma->Capacity.GetData(),1.41e-9);EXPECT_EQ(lt->Capacity.GetData(),ltCapacity);
    EXPECT_EQ(rig.neuron->GetTimeStep(),frequency);
    if(normalization==1){ASSERT_EQ(edit.minimumResistance.size(),1u);EXPECT_GE(values[0].resistance,edit.minimumResistance[0]);}
    auto after=rig.Probe();ASSERT_EQ(after.status,NativeProbeStatus::Completed);ASSERT_TRUE(after.observation);EXPECT_TRUE(after.observation->valid);
    const auto accepted=rig.Revision();auto invalid=values;invalid[0].synapses=129;
    const auto rejected=rig.learner->ApplyNativeParameters(invalid);EXPECT_EQ(rejected.status,NativeEditStatus::Rejected);
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),accepted);
    auto unsafe=values;unsafe[0].resistance=1.;
    const auto listeners=rig.source->Output.GetNumConnectors();
    const auto unstable=rig.learner->ApplyNativeParameters(unsafe);
    EXPECT_EQ(unstable.status,NativeEditStatus::Rejected)<<unstable.reason;
    EXPECT_FALSE(unstable.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),accepted);
    EXPECT_EQ(rig.source->Output.GetNumConnectors(),listeners);
    // A valid rollback is another explicit boundary edit, never learner Reset.
    values[0].length=2;values[0].synapses=1;
    const auto shrink=rig.learner->ApplyNativeParameters(values);ASSERT_EQ(shrink.status,NativeEditStatus::Applied)<<shrink.reason;
    EXPECT_EQ(soma->Capacity.GetData(),1.41e-9);EXPECT_EQ(lt->Capacity.GetData(),ltCapacity);
    auto final=rig.Probe();ASSERT_EQ(final.status,NativeProbeStatus::Completed);ASSERT_TRUE(final.observation);EXPECT_TRUE(final.observation->valid);
    Artifact(rig.name+"_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}
TEST(NativeModelEditor, ClassicN0_2000){CheckEdits<NNeuronTimeLearner>(2000,0);}
TEST(NativeModelEditor, BranchN0_2000){CheckEdits<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeModelEditor, ClassicN1_2000){CheckEdits<NNeuronTimeLearner>(2000,1);}
TEST(NativeModelEditor, BranchN1_2000){CheckEdits<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativeModelEditor, ClassicN0_20000){CheckEdits<NNeuronTimeLearner>(20000,0);}
TEST(NativeModelEditor, BranchN0_20000){CheckEdits<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativeModelEditor, ClassicN1_20000){CheckEdits<NNeuronTimeLearner>(20000,1);}
TEST(NativeModelEditor, BranchN1_20000){CheckEdits<NNeuronTimeLearnerBranch>(20000,1);}

TEST(NativeModelEditor, TightBurstAfterGrowthRemainsAnExplicitInvalidObservation)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"tight_burst_after_growth",true);
    const auto first=rig.Probe();ASSERT_EQ(first.status,NativeProbeStatus::Completed);ASSERT_TRUE(first.observation);
    ASSERT_TRUE(first.observation->valid);
    const auto soma=rig.neuron->GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);ASSERT_TRUE(soma);soma->Capacity=1.41e-9;
    auto parameters=rig.learner->ReadNativeParameters();parameters[0].length=3;parameters[0].synapses=3;
    const auto edit=rig.learner->ApplyNativeParameters(parameters);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    const auto measured=rig.Probe();ASSERT_EQ(measured.status,NativeProbeStatus::Completed);ASSERT_TRUE(measured.observation);
    EXPECT_TRUE(measured.observation->complete);EXPECT_FALSE(measured.observation->valid);
    ASSERT_EQ(measured.observation->stimuli.size(),2u);ASSERT_EQ(measured.observation->burstAssignments.size(),1u);
    EXPECT_EQ(measured.observation->burstAssignments[0].validity,PeakValidity::Missing);
    EXPECT_LT(measured.observation->burstAssignments[0].waves.size(),2u);
}

TEST(NativeModelEditor, CoupledColdBranchFourInputsUseSharedPhysicalBanks)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,0,"coupled_cold_four",false,4);
    const auto first=rig.Probe(2);ASSERT_EQ(first.status,NativeProbeStatus::Completed);
    ASSERT_TRUE(first.observation);ASSERT_TRUE(first.observation->valid);
    auto values=rig.learner->ReadNativeParameters();ASSERT_EQ(values.size(),4u);
    for(const auto& value:values)EXPECT_EQ(value.length,1);
    for(std::size_t i=0;i<3;++i)values[i].length=2;
    const auto edit=rig.learner->ApplyNativeParameters(values);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    EXPECT_EQ(edit.effective,values);EXPECT_EQ(rig.learner->DendriteLength.GetData(),(std::vector<int>{2,2,2,1}));
    EXPECT_EQ(rig.neuron->NumDendriteMembranePartsVec.GetData(),(std::vector<int>{2}));
    auto bank=rig.neuron->GetComponentL<NPulseMembrane>("Dendrite1_2",true);ASSERT_TRUE(bank);
    EXPECT_EQ(bank->NumExcitatorySynapses.GetData(),1);
    const auto fresh=rig.Probe(2);ASSERT_EQ(fresh.status,NativeProbeStatus::Completed);
    ASSERT_TRUE(fresh.observation);EXPECT_TRUE(fresh.observation->valid);
    EXPECT_EQ(fresh.observation->stimuli.size(),4u);ASSERT_TRUE(fresh.prepared);
    EXPECT_EQ(fresh.prepared->selectedInputIndex,std::optional<std::size_t>(2));
    Artifact(rig.name+"_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}

template<class Learner> void CheckHeterogeneousBank()
{
    EditingRig<Learner> rig(2000,0,"heterogeneous_bank");
    const auto first=rig.Probe();ASSERT_EQ(first.status,NativeProbeStatus::Completed);
    auto values=rig.learner->ReadNativeParameters();values[0].synapses=2;
    const auto edit=rig.learner->ApplyNativeParameters(values);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    auto second=rig.neuron->template GetComponentL<NPulseSynapse>("Dendrite1_2.ExcSynapse2",true);ASSERT_TRUE(second);
    second->Resistance=values[0].resistance*1.1;
    const auto before=rig.Revision();
    EXPECT_THROW(rig.learner->ReadNativeParameters(),std::runtime_error);
    const auto rejected=rig.learner->ApplyNativeParameters(values);
    EXPECT_EQ(rejected.status,NativeEditStatus::Rejected);
    EXPECT_EQ(rejected.reason,"heterogeneous_native_input_bank_resistance");
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),before);
    EXPECT_EQ(second->Resistance.GetData(),values[0].resistance*1.1);
    Artifact(rig.name+"_rejection.json",QJsonDocument(QJsonObject{
        {"status",NativeEditStatusName(rejected.status)},{"reason",QString::fromStdString(rejected.reason)},
        {"may_have_changed",rejected.modelMayHaveChanged},{"before",QString::fromStdString(before)},
        {"after",QString::fromStdString(rig.Revision())},
        {"first_rs",values[0].resistance},{"second_rs",second->Resistance.GetData()}}).toJson());
}

TEST(NativeModelEditor,HeterogeneousClassicBankCannotBeFlattened)
{ CheckHeterogeneousBank<NNeuronTimeLearner>(); }
TEST(NativeModelEditor,HeterogeneousBranchBankCannotBeFlattened)
{ CheckHeterogeneousBank<NNeuronTimeLearnerBranch>(); }

template<class Learner> NativeTrainingPlan TrainingPlan(EditingRig<Learner>& rig,double sync=.02)
{
    NativeTrainingPlan plan;auto& p=plan.protocol;
    p.schemaVersion=3;p.routing=rig.branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
    p.revision="native_service_burst_v1";p.sampleId="target";p.originStimulusId="pulse0";
    QJsonArray pattern;for(double value:rig.isi)pattern.append(value);
    p.patternHash=NmsdkTools::CanonicalModelDataSha256(pattern).toStdString();
    p.maximumSampleGap=1./rig.frequency;p.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    p.stimulusProfile=StimulusProfile{rig.source->GetCompClassName(),rig.source->Amplitude.GetData(),
        rig.source->PulseLength.GetData(),double(rig.source->GetTimeStep()),rig.source->FrequencyDeviation.GetData(),
        rig.source->UseTransitSignal.GetData(),rig.source->UsePatternOutput.GetData()};
    auto& request=plan.probe;request.routing=p.routing;request.protocolRevision=p.revision;request.expectedInputIsi=rig.isi;
    auto& spec=request.specification;spec.schemaVersion=3;spec.waveAssignment=p.waveAssignment;
    spec.sampleId=p.sampleId;spec.patternHash=p.patternHash;spec.stimulusProfile=p.stimulusProfile;
    spec.end=rig.duration;spec.maximumSampleGap=p.maximumSampleGap;
    spec.maximumSamples=std::size_t((rig.duration+.01)*rig.frequency);
    double onset=0.;
    for(std::size_t i=0;i<rig.inputCount;++i)
    {
        const auto input="input"+std::to_string(i),stimulus="pulse"+std::to_string(i);
        p.inputs.push_back({input,stimulus});p.stimulusIds.push_back(stimulus);spec.expectedStimulusIds.push_back(stimulus);
        onset+=rig.isi[i];plan.inputWindows.push_back({input,rig.branch?0u:i,onset,onset+.065,stimulus});
    }
    plan.maximumReferenceProbes=rig.inputCount+1;plan.maximumModelSeconds=20.;plan.maximumWallSeconds=600.;
    auto& search=plan.search;search.runId=rig.name+"/automatic";search.tolerances.sync=sync;
    search.normalization=rig.normalization?Normalization::TipResistance:Normalization::SynapseCount;
    search.maximumProbes=64;search.maximumEdits=16;search.maximumCandidatesPerInput=4;
    search.maximumSweeps=1;search.resistanceSubdivisionDepth=0;
    const auto values=rig.learner->ReadNativeParameters();
    for(std::size_t i=0;i<values.size();++i)
    {
        const bool anchor=i+1==values.size();const auto& v=values[i];
        search.bounds.push_back({v.length,anchor?v.length:v.length+1,1,rig.normalization||anchor?1:2,
            v.resistance,rig.normalization&&!anchor?v.resistance*2.:v.resistance});
    }
    return plan;
}

template<class Learner> void RunNativeTraining(int normalization)
{
    EditingRig<Learner> rig(2000,normalization,"automatic_service");
    auto plan=TrainingPlan(rig);std::size_t observations=0,frames=0;
    std::string trial;std::ostringstream trace;
    plan.probe.onPrepared=[&](const PreparedVerificationProbe&,const ProbeSpec& spec) {
        trial=spec.trialId;trace.str({});trace.clear();trace.imbue(std::locale::classic());
        trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)trace<<",soma"<<i;trace<<'\n';
    };
    plan.probe.onSample=[&](const NativeProbeSample& sample) {
        ++frames;trace<<sample.time<<','<<sample.stimulus;
        for(double value:sample.potentials)trace<<','<<value;trace<<'\n';
    };
    plan.observationSink=[&](const NativeProbeResult& result) {
        ++observations;
        ASSERT_TRUE(result.observation);EXPECT_EQ(result.observation->specification.trialId,trial);
        const auto evidence=EncodeNativeProbeEvidence(result);
        EXPECT_EQ(evidence["observation"].toObject()["specification"].toObject()["trial_id"].toString(),QString::fromStdString(trial));
        Artifact(rig.name+"_service_"+std::to_string(observations)+".json",QJsonDocument(evidence).toJson());
        Artifact(rig.name+"_service_"+std::to_string(observations)+".csv",QByteArray::fromStdString(trace.str()));
    };
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {
        ASSERT_LT(ticks,40000u);
        rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    }
    const auto& service=rig.learner->NativeTrainingController();
    ASSERT_EQ(service.Outcome(),TrainingStatus::SearchUnresolved)<<service.Reason();
    ASSERT_TRUE(service.References());EXPECT_EQ(service.References()->Inputs().size(),2u);
    ASSERT_TRUE(service.Search());EXPECT_GE(service.Search()->AppliedEdits(),1u);
    EXPECT_EQ(service.Search()->Status(),TrainingStatus::SearchUnresolved);
    ASSERT_TRUE(service.Certificate());EXPECT_FALSE(service.Certificate()->Exact());
    EXPECT_TRUE(service.Certificate()->Matches(rig.Revision(),*service.References(),plan.search.tolerances,
        ModelStateKind::LearnedSolo,service.Search()->ModelEpoch()));
    EXPECT_EQ(observations,service.IssuedReferenceProbes()+service.Search()->IssuedProbes());EXPECT_GT(frames,0u);
    auto summary=EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters());
    summary["implementation_control"]=true;
    EXPECT_TRUE(summary["certificate_matches_actual_model"].toBool());
    EXPECT_FALSE(summary["certificate"].toObject()["exact"].toBool());
    EXPECT_EQ(summary["actual_parameters"],summary["accepted_parameters"]);
    Artifact(rig.name+"_training_summary.json",QJsonDocument(summary).toJson());
    // Reset keeps the physical model and captured goal. It must not invoke
    // legacy XML anchor reload or return to an untrained structure.
    const auto before=rig.Revision();const auto references=service.References()->Inputs();
    rig.learner->Reset();EXPECT_EQ(rig.Revision(),before);
    ASSERT_TRUE(rig.learner->NativeTrainingController().References());
    EXPECT_EQ(rig.learner->NativeTrainingController().References()->Inputs(),references);
    EXPECT_EQ(rig.learner->NativeTrainingController().State(),NativeTrainingState::Idle);
    Artifact(rig.name+"_service_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}
TEST(NativeTrainingService,ClassicN0SearchAndFreshNegativeFinalGate){RunNativeTraining<NNeuronTimeLearner>(0);}
TEST(NativeTrainingService,BranchN0SearchAndFreshNegativeFinalGate){RunNativeTraining<NNeuronTimeLearnerBranch>(0);}
TEST(NativeTrainingService,ClassicN1SearchAndFreshNegativeFinalGate){RunNativeTraining<NNeuronTimeLearner>(1);}
TEST(NativeTrainingService,BranchN1SearchAndFreshNegativeFinalGate){RunNativeTraining<NNeuronTimeLearnerBranch>(1);}

TEST(NativeTrainingService,ExactAutoCompletionResetWarmRestartAndRetarget)
{
    EditingRig<NNeuronTimeLearner> rig(2000,1,"service_exact_warm");rig.learner->CalculateMode=0;
    auto plan=TrainingPlan(rig,.2);
    for(auto& bound:plan.search.bounds){bound.maximumLength=bound.minimumLength;bound.maximumResistance=bound.minimumResistance;}
    const auto run=[&] {
        rig.learner->BeginNativeTraining(plan);
        for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
        {ASSERT_LT(ticks,20000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    };
    run();const auto& service=rig.learner->NativeTrainingController();
    ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();ASSERT_TRUE(service.Certificate());
    EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());EXPECT_TRUE(service.Certificate()->Exact());
    const auto captured=service.References()->Inputs();const auto hash=rig.Revision();
    ASSERT_EQ(service.ReferenceObservations().size(),2u);
    const auto originalReferenceTrial=service.ReferenceObservations()[0].observation.specification.trialId;
    rig.learner->Reset();EXPECT_EQ(rig.Revision(),hash);ASSERT_TRUE(service.Certificate());
    ASSERT_EQ(service.ReferenceObservations().size(),2u);
    run();EXPECT_EQ(service.Outcome(),TrainingStatus::Exact);EXPECT_EQ(service.IssuedReferenceProbes(),0u);
    ASSERT_TRUE(service.References());EXPECT_EQ(service.References()->Inputs(),captured);
    ASSERT_EQ(service.ReferenceObservations().size(),2u);
    EXPECT_EQ(service.ReferenceObservations()[0].observation.specification.trialId,originalReferenceTrial);
    auto pattern=rig.learner->InputPattern.GetData();pattern(1,0)+=.01;rig.learner->InputPattern=pattern;
    EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    EXPECT_TRUE(service.ReferenceObservations().empty());
    EXPECT_NE(service.Outcome(),TrainingStatus::Exact);
}

template<class Learner> void StopNativeTraining()
{
    EditingRig<Learner> rig(2000,0,"service_external_stop");auto plan=TrainingPlan(rig);
    std::vector<NativeProbeResult> recorded;plan.observationSink=[&](const auto& result){recorded.push_back(result);};
    const auto before=rig.Revision();rig.learner->BeginNativeTraining(plan);
    for(unsigned i=0;i<10;++i){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    EXPECT_EQ(rig.learner->NativeProbeState(),NativeProbeStatus::Running);
    rig.learner->IsNeedToTrain=false;const auto& service=rig.learner->NativeTrainingController();
    EXPECT_EQ(service.State(),NativeTrainingState::Finished);EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);
    EXPECT_FALSE(service.Certificate());EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());
    ASSERT_EQ(recorded.size(),1u);ASSERT_TRUE(recorded[0].requestedSpecification);
    ASSERT_TRUE(recorded[0].observation);EXPECT_FALSE(recorded[0].observation->complete);
    EXPECT_EQ(recorded[0].status,NativeProbeStatus::Cancelled);EXPECT_EQ(rig.Revision(),before);
    Artifact(rig.name+"_cancelled.json",QJsonDocument(EncodeNativeProbeEvidence(recorded[0])).toJson());
}
TEST(NativeTrainingService,ClassicExternalStopPreservesCensoredEvidence){StopNativeTraining<NNeuronTimeLearner>();}
TEST(NativeTrainingService,BranchExternalStopPreservesCensoredEvidence){StopNativeTraining<NNeuronTimeLearnerBranch>();}

TEST(NativeTrainingService,ModelTimeBudgetCannotManufactureConvergence)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,1,"service_deadline");auto plan=TrainingPlan(rig);
    plan.maximumModelSeconds=.002;std::vector<NativeProbeResult> recorded;
    plan.observationSink=[&](const auto& result){recorded.push_back(result);};rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,20u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    EXPECT_EQ(rig.learner->NativeTrainingController().Outcome(),TrainingStatus::BudgetExhausted);
    EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());ASSERT_EQ(recorded.size(),1u);
    EXPECT_EQ(recorded[0].status,NativeProbeStatus::Cancelled);
    Artifact(rig.name+"_budget.json",QJsonDocument(EncodeNativeProbeEvidence(recorded[0])).toJson());
}

TEST(NativeTrainingService,DeclaredPatternHashMustMatchTheActualNativeDataset)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"service_spoofed_hash");auto plan=TrainingPlan(rig);
    plan.protocol.patternHash=plan.probe.specification.patternHash="unverified_declared_hash";
    std::vector<NativeProbeResult> recorded;plan.observationSink=[&](const auto& result){recorded.push_back(result);};
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,20u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);
    EXPECT_EQ(service.Reason(),"native_pattern_hash_mismatch");EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    ASSERT_EQ(recorded.size(),1u);ASSERT_TRUE(recorded[0].requestedSpecification);
    EXPECT_FALSE(recorded[0].requestedSpecification->trialId.empty());
    Artifact(rig.name+"_rejected.json",QJsonDocument(EncodeNativeProbeEvidence(recorded[0])).toJson());
}

TEST(NativeTrainingService,EvidenceEncoderRejectsNonfiniteNumbers)
{
    NativeProbeResult result;result.requestedSpecification=ProbeSpec{};
    result.requestedSpecification->end=std::numeric_limits<double>::infinity();
    EXPECT_THROW(EncodeNativeProbeEvidence(result),std::invalid_argument);
}

TEST(NativeTrainingService,InvalidSearchDomainIsRejectedBeforeAnyReferenceProbe)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"service_invalid_domain");auto plan=TrainingPlan(rig);
    plan.search.bounds[0].maximumSynapses=129;unsigned observations=0;
    plan.observationSink=[&](const auto&){++observations;};const auto before=rig.Revision();
    rig.learner->BeginNativeTraining(plan);const auto& service=rig.learner->NativeTrainingController();
    EXPECT_EQ(service.State(),NativeTrainingState::Finished);EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidModel);
    EXPECT_EQ(service.Reason(),"invalid_per_input_search_bounds");EXPECT_EQ(service.IssuedReferenceProbes(),0u);
    EXPECT_EQ(observations,0u);EXPECT_EQ(rig.Revision(),before);
    rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    EXPECT_EQ(service.IssuedReferenceProbes(),0u);EXPECT_EQ(observations,0u);
}

TEST(NativeIntegration, ActualSecretionWeightPsiAndTimeStepAreUsed)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"integration_bound");
    auto synapse=rig.neuron->GetComponentL<NPulseSynapse>("Dendrite1_2.ExcSynapse1",true);ASSERT_TRUE(synapse);
    auto channel=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);ASSERT_TRUE(channel);
    const auto bound=[&]() {
        const auto result=AssessNativeIntegration(rig.neuron,rig.source->Amplitude.GetData());
        EXPECT_TRUE(result.valid)<<result.reason;
        const auto path=channel->GetLongName(rig.neuron.Get());
        auto found=std::find_if(result.channels.begin(),result.channels.end(),[&](const auto& c){return c.path==path;});
        if(found==result.channels.end())throw std::runtime_error("missing_test_channel_bound");return found->maximumConductance;
    };
    const auto original=bound();synapse->Weight=2.;EXPECT_DOUBLE_EQ(bound(),original*2.);
    synapse->UsePresynapticInhibition=true;synapse->InhibitionCoeff=2.5;synapse->Build();synapse->Init();
    EXPECT_DOUBLE_EQ(bound(),original*2.);
    const auto secretion=synapse->SecretionTC.GetData();synapse->SecretionTC=1e-6;
    const auto badSecretion=AssessNativeIntegration(rig.neuron,rig.source->Amplitude.GetData());
    EXPECT_FALSE(badSecretion.valid);EXPECT_EQ(badSecretion.reason,"unstable_synapse_discretization");
    synapse->SecretionTC=secretion;const auto capacity=channel->Capacity.GetData();channel->Capacity=1e-18;
    const auto badCapacity=AssessNativeIntegration(rig.neuron,rig.source->Amplitude.GetData());
    EXPECT_FALSE(badCapacity.valid);EXPECT_EQ(badCapacity.reason,"channel_step_not_certified_strictly_stable");
    channel->Capacity=capacity;EXPECT_TRUE(AssessNativeIntegration(rig.neuron,rig.source->Amplitude.GetData()).valid);
}

TEST(NativeModelEditor, ExplicitGraphPreservesUnownedBanksAndRejectsMissingAttachments)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"explicit_graph_ownership");
    auto initial=rig.Probe();ASSERT_EQ(initial.status,NativeProbeStatus::Completed);
    // Configure the existing graph through ordinary component setters. This is
    // setup, not an extra Build sequence performed by the editor.
    rig.learner->StructureBuildMode=0;rig.learner->Build();
    rig.neuron->StructureBuildMode=0;rig.neuron->Build();rig.neuron->Init();rig.neuron->Reset();
    rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    auto unowned=rig.neuron->GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);ASSERT_TRUE(unowned);
    unowned->Resistance=321e6;
    ASSERT_TRUE(rig.neuron->CreateLink("NegGenerator","Output","Dendrite1_1.ExcSynapse1","Input",-1,true));
    const auto source=unowned->Input.GetDataSources();ASSERT_EQ(source.size(),1u);
    auto parameters=rig.learner->ReadNativeParameters();parameters[0].synapses=2;
    const auto edit=rig.learner->ApplyNativeParameters(parameters);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    EXPECT_EQ(unowned->Resistance.GetData(),321e6);EXPECT_EQ(unowned->Input.GetDataSources(),source);
    EXPECT_EQ(rig.neuron->GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true).Get(),unowned.Get());
    const auto before=rig.Revision();parameters[0].length=3;
    const auto missing=rig.learner->ApplyNativeParameters(parameters);
    EXPECT_EQ(missing.status,NativeEditStatus::Rejected);EXPECT_EQ(missing.reason,"attachment_outside_explicit_graph");
    EXPECT_FALSE(missing.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),before);
    const auto observation=rig.Probe();ASSERT_EQ(observation.status,NativeProbeStatus::Completed);
    ASSERT_TRUE(observation.observation);EXPECT_TRUE(observation.observation->valid);
}

TEST(NativeModelEditor, ShrinkCannotSilentlyDeleteAnExternalObservationSource)
{
  for(bool direct:{false,true})
  {
    EditingRig<NNeuronTimeLearner> rig(2000,0,direct?"external_observer_direct":"external_observer_native");
    const auto initial=rig.Probe();ASSERT_EQ(initial.status,NativeProbeStatus::Completed);
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto tap=dynamic_pointer_cast<NPulseGeneratorTransit>(core.storage->TakeObject("NPulseGeneratorTransit"));ASSERT_TRUE(tap);
    tap->Name="ExternalTap";UEPtr<UContainer> component=tap;ASSERT_NE(rig.model->AddComponent(component),ForbiddenId);tap->Init();
    auto monitored=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);ASSERT_TRUE(monitored);
    if(direct)ASSERT_TRUE(tap->Input.SetPointer(0,&monitored->Output));
    else {int slot=0;ASSERT_TRUE(monitored->Connect(tap.Get(),"Output","Input",slot,true));}
    const auto before=rig.Revision();const auto sources=tap->Input.GetDataSources();ASSERT_EQ(sources.size(),1u);
    auto parameters=rig.learner->ReadNativeParameters();parameters[0].length=1;
    const auto rejected=rig.learner->ApplyNativeParameters(parameters);
    EXPECT_EQ(rejected.status,NativeEditStatus::Rejected)<<rejected.reason;
    EXPECT_EQ(rejected.reason,"edit_would_remove_external_observation_source");
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),before);
    EXPECT_EQ(tap->Input.GetDataSources(),sources);
    Artifact(rig.name+"_observer_guard.json",QJsonDocument(QJsonObject{
        {"binding_kind",direct?"SetPointer":"UItem.Connect"},{"status",NativeEditStatusName(rejected.status)},
        {"reason",QString::fromStdString(rejected.reason)},{"may_have_changed",rejected.modelMayHaveChanged},
        {"native_reverse_count",monitored->GetNumAConnectors("Output")},
        {"property_reverse_count",int(monitored->Output.GetNumConnectors())},
        {"observer_preserved",tap->Input.GetDataSources()==sources},
        {"before",QString::fromStdString(before)},{"after",QString::fromStdString(rig.Revision())}}).toJson());
  }
}
}
