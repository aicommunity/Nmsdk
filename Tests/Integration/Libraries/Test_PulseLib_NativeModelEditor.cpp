#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseChannel.h"
#include "NPulseSynapse.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ModelInspection.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/NativeLearnedState.h"
#include "../Support/ConsoleLikeInit.h"
#include <QFile>
#include <QDir>
#include <QJsonArray>
#include <QJsonDocument>
#include <QCoreApplication>
#include <QProcess>
#include <QProcessEnvironment>
#include <QTemporaryDir>
#include <sstream>
#include <iomanip>
#include <locale>
#include <cstdlib>
#include <type_traits>
#include <limits>
#include <chrono>
#include <algorithm>

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
    double constructionTime=0.;
    std::vector<double> isi{.01,.08};bool tightBurst=false;
    EditingRig(unsigned f,int mode,const std::string& suffix,bool tight=false,std::size_t inputs=2,
               bool cold=false,int neuronMode=2,int learnerMode=1)
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
        learner->Name="Learner";learner->StructureBuildMode=learnerMode;learner->NumInputDendrite=int(inputCount);
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
        model->SetGlobalTimeStep(f);
        constructionTime=environment->GetTime().GetDoubleTime();
        if(cold)
        {
            NativeModelSpec initial;initial.branch=branch;initial.frequencyHz=f;initial.neuronClass=registered.neuronClass;
            initial.neuronStructureMode=neuronMode;initial.normalization=mode?Normalization::TipResistance:Normalization::SynapseCount;
            initial.editPolicy.normalization=initial.normalization;initial.editPolicy.maximumCableLength=8;
            initial.editPolicy.preserveAllocatedCable=learnerMode==0;initial.initialIsi=isi;
            for(int length:lengths)initial.inputs.push_back({length,1,std::nullopt});
            if(neuronMode==1)initial.allocatedCableLengths.assign(branch?1:inputCount,3);
            if(neuronMode==0)
            {
                auto prototype=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(registered.neuronClass));
                if(!prototype)throw std::runtime_error("native_explicit_profile");
                prototype->SetEnvironment(environment);prototype->UnInit();prototype->SetGlobalTimeStep(f);
                prototype->StructureBuildMode=2;prototype->NumSomaMembraneParts=branch?1:int(inputCount);
                prototype->NumDendriteMembranePartsVec=branch?std::vector<int>{*std::max_element(lengths.begin(),lengths.end())}:lengths;
                prototype->Build();prototype->Init();prototype->StructureBuildMode=0;prototype->Build();prototype->Init();
                initial.neuronClass=name+"_ExplicitImage";RegisterClassImage(core.storage,initial.neuronClass,prototype);
                core.storage->ReturnObject(prototype);
            }
            const auto result=learner->ConstructNativeModel(initial);
            Artifact(name+"_construction.json",QJsonDocument(QJsonObject{{"status",NativeModelBuildStatusName(result.status)},
                {"reason",QString::fromStdString(result.reason)},{"revision",QString::fromStdString(result.modelRevision)}}).toJson());
            if(result.status!=NativeModelBuildStatus::Constructed)throw std::runtime_error("native_cold_construction:"+result.reason);
        }
        model->Init();model->Reset();
        Artifact(name+"_startup_before.json",QJsonDocument(NmsdkTools::InspectModel(learner)).toJson());
        // The native scheduler completes ordinary lazy child initialization.
        // Capture fresh handles afterwards; the probe itself resets its physical
        // subtree before arming, so this is not training or a dynamic checkpoint.
        if(!cold){model->Calculate();environment->IncreaseModelTimeByStep();}
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
    NativeProbeResult Probe(std::size_t input=0,const TrainingAction* action=nullptr,BoundedTrainingSession* session=nullptr,
        PeakSelectionPolicy selection=PeakSelectionPolicy::IsolatedWindow,bool wide=false,bool useObserver=false,
        std::function<void(const NativeProbeSample&)> sampleSink={})
    {
        NativeProbeRequest request;request.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        request.activeInput=int(input);request.inputId="input"+std::to_string(input);request.protocolRevision="editing_burst_v1";
        request.baseModelRevision=Revision();request.readModelRevision=[this]{return Revision();};request.expectedInputIsi=isi;
        auto observer=std::make_shared<NmsdkTools::ModelRevisionObserver>();
        if(useObserver)
        {
            request.readModelRevision=[this,observer]{return observer->Read(neuron,ports).toStdString();};
            request.readFullModelRevision=[this,observer]{return observer->Read(neuron,ports,true).toStdString();};
        }
        auto& s=request.specification;s.schemaVersion=3;s.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
        s.peakSelection=selection;
        s.runId=action?action->runId:name;s.trialId=action?action->trialId:name+"/trial/"+std::to_string(++serial);
        QJsonArray actualPattern;for(double value:isi)actualPattern.append(value);
        s.sampleId="target";s.patternHash=NmsdkTools::CanonicalModelDataSha256(actualPattern).toStdString();
        s.end=duration;s.maximumSampleGap=1./frequency;
        s.maximumSamples=std::size_t((duration+.01)*frequency);
        for(std::size_t i=0;i<inputCount;++i)s.expectedStimulusIds.push_back("pulse"+std::to_string(i));
        double onset=0.;for(std::size_t i=0;i<=input;++i)onset+=isi[i];
        s.windows={{request.inputId,branch?0u:input,onset,onset+(tightBurst?.025:.065),"pulse"+std::to_string(input)}};
        if(wide){s.windows[0].begin=0.;s.windows[0].end=duration;}
        if(action)request.modelEpoch=action->modelEpoch;
        if(session)request.onPrepared=[&](const auto& prepared,const ProbeSpec&){session->Arm(action->serial,prepared);};
        std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(unsigned i=0;i<(branch?1u:inputCount);++i)trace<<",soma"<<i;trace<<'\n';
        request.onSample=[&](const NativeProbeSample& sample) {
            trace<<sample.time<<','<<sample.stimulus;for(double potential:sample.potentials)trace<<','<<potential;trace<<'\n';
            if(sampleSink)sampleSink(sample);
        };
        const auto trial=s.trialId;
        learner->QueueNativeProbe(std::move(request));unsigned ticks=0;
        while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
        {
            if(++ticks>unsigned((duration+.02)*frequency))throw std::runtime_error("editor_fixture_probe_budget");
            model->Calculate();environment->IncreaseModelTimeByStep();
        }
        auto result=learner->TakeNativeProbeResult();if(!result)throw std::runtime_error("missing_editor_fixture_result");
        if(useObserver){EXPECT_GE(observer->FullReads(),6u);EXPECT_GT(observer->CacheHits(),100u);}
        Artifact(name+"_probe_"+std::to_string(++serial)+".csv",QByteArray::fromStdString(trace.str()));
        if(wide)Artifact(name+"_probe_"+std::to_string(serial)+"_evidence.json",QJsonDocument(EncodeNativeProbeEvidence(*result)).toJson());
        if(useObserver)Artifact(name+"_observer_counts_"+std::to_string(serial)+".json",QJsonDocument(QJsonObject{
            {"full_reads",double(observer->FullReads())},{"cache_hits",double(observer->CacheHits())}}).toJson());
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

template<class Learner> void ColdModel(unsigned frequency,int neuronMode,int learnerMode,int normalization,std::size_t inputs=2)
{
    const auto suffix="cold_mode"+std::to_string(neuronMode)+"_learner"+std::to_string(learnerMode)+"_inputs"+std::to_string(inputs);
    EditingRig<Learner> rig(frequency,normalization,suffix,false,inputs,true,neuronMode,learnerMode);
    EXPECT_TRUE(rig.learner->NativeModelEditFailure().empty());
    EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),rig.constructionTime); // No warm-up time advance.
    EXPECT_EQ(rig.neuron->StructureBuildMode.GetData(),neuronMode);
    EXPECT_EQ(rig.learner->StructureBuildMode.GetData(),learnerMode);
    const auto first=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true);
    ASSERT_EQ(first.status,NativeProbeStatus::Completed);ASSERT_TRUE(first.observation);ASSERT_TRUE(first.observation->valid);
    const auto oldNeuron=rig.neuron.Get();
    const auto oldDataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true).Get();
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);
    auto lt=rig.neuron->template GetComponentL<NPulseChannel>("LTMembrane.ExcChannel",true);ASSERT_TRUE(lt);
    const double ltCapacity=lt->Capacity.GetData();channel->Capacity=1.41e-9;
    auto values=rig.learner->ReadNativeParameters();values[0].resistance*=1.1;
    // Split coincident labels only through a valid coupled attachment edit.
    if(inputs==2 && neuronMode!=0)values[0].length=3;
    else if(inputs>2)for(auto& p:values)p.resistance=values[0].resistance;
    const auto edit=rig.learner->ApplyNativeParameters(values);ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
    const auto before=rig.Revision();EXPECT_EQ(channel->Capacity.GetData(),1.41e-9);
    ASSERT_TRUE(rig.learner->SetNeuronClassName(rig.learner->NeuronClassName.GetData()));ASSERT_FALSE(rig.learner->IsReady());
    EXPECT_TRUE(rig.learner->Build());ASSERT_TRUE(rig.learner->IsReady());
    EXPECT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
    EXPECT_EQ(rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true).Get(),oldNeuron);
    EXPECT_EQ(rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true).Get(),oldDataset);
    EXPECT_EQ(rig.Revision(),before);EXPECT_EQ(channel->Capacity.GetData(),1.41e-9);EXPECT_EQ(lt->Capacity.GetData(),ltCapacity);
    EXPECT_EQ(rig.learner->ReadNativeParameters(),values);
    rig.learner->Reset();EXPECT_EQ(rig.Revision(),before);
    rig.learner->UnInit();rig.learner->Init();EXPECT_EQ(rig.Revision(),before);
    const auto final=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true);
    ASSERT_EQ(final.status,NativeProbeStatus::Completed);ASSERT_TRUE(final.observation);EXPECT_TRUE(final.observation->valid);
    Artifact(rig.name+"_preserved_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}
TEST(NativeModelBuilder,ClassicVector2000){ColdModel<NNeuronTimeLearner>(2000,2,1,0);}
TEST(NativeModelBuilder,BranchVector2000){ColdModel<NNeuronTimeLearnerBranch>(2000,2,1,0);}
TEST(NativeModelBuilder,ClassicVector20000){ColdModel<NNeuronTimeLearner>(20000,2,1,0);}
TEST(NativeModelBuilder,BranchVector20000){ColdModel<NNeuronTimeLearnerBranch>(20000,2,1,0);}
TEST(NativeModelBuilder,ClassicScalar2000){ColdModel<NNeuronTimeLearner>(2000,1,1,0);}
TEST(NativeModelBuilder,BranchScalar2000){ColdModel<NNeuronTimeLearnerBranch>(2000,1,1,0);}
TEST(NativeModelBuilder,ClassicScalar20000){ColdModel<NNeuronTimeLearner>(20000,1,1,0);}
TEST(NativeModelBuilder,BranchScalar20000){ColdModel<NNeuronTimeLearnerBranch>(20000,1,1,0);}
TEST(NativeModelBuilder,ClassicExplicit2000){ColdModel<NNeuronTimeLearner>(2000,0,0,0);}
TEST(NativeModelBuilder,BranchExplicit2000){ColdModel<NNeuronTimeLearnerBranch>(2000,0,0,0);}
TEST(NativeModelBuilder,ClassicExplicit20000){ColdModel<NNeuronTimeLearner>(20000,0,0,0);}
TEST(NativeModelBuilder,BranchExplicit20000){ColdModel<NNeuronTimeLearnerBranch>(20000,0,0,0);}
TEST(NativeModelBuilder,ClassicParametric2000){ColdModel<NNeuronTimeLearner>(2000,2,0,1);}
TEST(NativeModelBuilder,BranchParametric2000){ColdModel<NNeuronTimeLearnerBranch>(2000,2,0,1);}
TEST(NativeModelBuilder,ClassicParametric20000){ColdModel<NNeuronTimeLearner>(20000,2,0,1);}
TEST(NativeModelBuilder,BranchParametric20000){ColdModel<NNeuronTimeLearnerBranch>(20000,2,0,1);}
TEST(NativeModelBuilder,ClassicSixInputs){ColdModel<NNeuronTimeLearner>(2000,2,1,0,6);}
TEST(NativeModelBuilder,BranchSixSharedInputs){ColdModel<NNeuronTimeLearnerBranch>(2000,2,1,0,6);}

template<class Learner> void ColdDeclaredBanks(bool inhibition)
{
    EditingRig<Learner> rig(2000,0,inhibition?"cold_declared_inhibition":"cold_multiple_synapses",false,2,true);
    NativeEditSpec policy;policy.maximumCableLength=8;
    auto spec=DescribeNativeLearnerModel(*rig.learner,rig.branch,Normalization::SynapseCount,
        rig.learner->DendriteLength.GetData(),policy);
    spec.allocatedCableLengths.clear();
    for(std::size_t i=0;i<spec.inputs.size();++i)
    {spec.inputs[i].synapses=inhibition?1:3;spec.inputs[i].resistance=inhibition?86e6:258e6*(i+1);}
    if(inhibition)for(std::size_t i=0;i<spec.inputs.size();++i)
        for(int offset:{1,2})spec.editPolicy.inhibition.push_back({i,offset,8600e6});
    const auto built=rig.learner->ConstructNativeModel(spec);
    ASSERT_EQ(built.status,NativeModelBuildStatus::Constructed)<<built.reason;
    rig.model->Init();rig.model->Reset();
    EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),rig.constructionTime);
    rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
    rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    ASSERT_TRUE(rig.neuron);ASSERT_TRUE(rig.source);rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    const auto path=[&](std::size_t input,int position,const std::string& member) {
        return "Dendrite"+std::to_string(rig.branch?1:input+1)+"_"+std::to_string(position)+"."+member;
    };
    for(std::size_t i=0;i<spec.inputs.size();++i)for(int k=1;k<=spec.inputs[i].synapses;++k)
    {
        auto member=rig.neuron->template GetComponentL<NPulseSynapse>(path(i,spec.inputs[i].attachment,"ExcSynapse"+std::to_string(k)),true);
        ASSERT_TRUE(member);EXPECT_EQ(member->Resistance.GetData(),*spec.inputs[i].resistance);
        ASSERT_EQ(member->Input.GetDataSources().size(),1u);
        EXPECT_EQ(member->Input.GetDataSources().front(),&rig.source->Output);
    }
    const auto checkRouting=[&](int activeLength) {
        auto active=rig.neuron->template GetComponentL<NPulseSynapse>(path(0,activeLength,"ExcSynapse1"),true);
        ASSERT_TRUE(active);ASSERT_EQ(active->Input.GetDataSources().size(),1u);
        EXPECT_EQ(active->Input.GetDataSources().front(),&rig.source->Output);
        if(rig.branch)
        {
            auto other=rig.neuron->template GetComponentL<NPulseSynapse>(path(1,1,"ExcSynapse1"),true);
            ASSERT_TRUE(other);EXPECT_TRUE(other->Input.GetDataSources().empty());
        }
        if(inhibition)for(std::size_t i=0;i<2;++i)for(int offset:{1,2})
        {
            const int position=(i?1:activeLength)+offset;
            auto member=rig.neuron->template GetComponentL<NPulseSynapse>(path(i,position,"InhSynapse1"),true);
            ASSERT_TRUE(member);
            const bool selected=!rig.branch || position==activeLength+1 || position==activeLength+2;
            if(selected){ASSERT_EQ(member->Input.GetDataSources().size(),1u);EXPECT_EQ(member->Input.GetDataSources().front(),&rig.source->Output);}
            else EXPECT_TRUE(member->Input.GetDataSources().empty());
        }
    };
    const auto before=rig.Revision();bool inspected=false;
    const auto first=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const NativeProbeSample&){if(!inspected){inspected=true;checkRouting(2);}});
    ASSERT_TRUE(inspected);ASSERT_EQ(first.status,NativeProbeStatus::Completed);ASSERT_TRUE(first.observation);
    EXPECT_TRUE(first.observation->complete);EXPECT_EQ(rig.Revision(),before);
    // Routing/physical graph checks remain meaningful if inhibition changes the
    // measured wave assignment; such an observation must retain its actual validity.
    if(!inhibition)EXPECT_TRUE(first.observation->valid);
    if(inhibition)
    {
        auto parameters=rig.learner->ReadNativeParameters();parameters[0].length=3;parameters[0].resistance*=1.1;
        const auto edited=rig.learner->ApplyNativeParameters(parameters);
        ASSERT_EQ(edited.status,NativeEditStatus::Applied)<<edited.reason;
        for(std::size_t i=0;i<2;++i)for(int offset:{1,2})
        {
            auto member=rig.neuron->template GetComponentL<NPulseSynapse>(path(i,parameters[i].length+offset,"InhSynapse1"),true);
            ASSERT_TRUE(member);EXPECT_DOUBLE_EQ(member->Resistance.GetData(),8600e6*(i?1.:1.1));
        }
        const auto revised=rig.Revision();inspected=false;
        const auto after=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
            [&](const NativeProbeSample&){if(!inspected){inspected=true;checkRouting(3);}});
        ASSERT_TRUE(inspected);ASSERT_EQ(after.status,NativeProbeStatus::Completed);ASSERT_TRUE(after.observation);
        EXPECT_TRUE(after.observation->complete);EXPECT_EQ(rig.Revision(),revised);
    }
    Artifact(rig.name+"_declared_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}
TEST(NativeModelBuilder,ClassicColdMultipleSynapses){ColdDeclaredBanks<NNeuronTimeLearner>(false);}
TEST(NativeModelBuilder,BranchColdMultipleSynapses){ColdDeclaredBanks<NNeuronTimeLearnerBranch>(false);}
TEST(NativeModelBuilder,ClassicColdDeclaredInhibition){ColdDeclaredBanks<NNeuronTimeLearner>(true);}
TEST(NativeModelBuilder,BranchColdDeclaredInhibition){ColdDeclaredBanks<NNeuronTimeLearnerBranch>(true);}

TEST(NativeModelBuilder,InvalidSpecAndExternalListenersRejectBeforeReplacingTheLiveModel)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"cold_rejection");const auto before=rig.Revision();
    NativeEditSpec policy;policy.maximumCableLength=8;
    auto s=DescribeNativeLearnerModel(*rig.learner,false,Normalization::SynapseCount,rig.learner->DendriteLength.GetData(),policy);
    auto invalid=s;invalid.initialIsi[0]=std::numeric_limits<double>::quiet_NaN();
    auto rejected=rig.learner->ConstructNativeModel(invalid);EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),before);
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto tap=dynamic_pointer_cast<NPulseGeneratorTransit>(core.storage->TakeObject("NPulseGeneratorTransit"));ASSERT_TRUE(tap);
    tap->Name="ColdExternalListener";UEPtr<UContainer> node=tap;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);tap->Init();
    ASSERT_TRUE(tap->Input.SetPointer(0,&rig.source->Output));const auto inputs=tap->Input.GetDataSources();
    rejected=rig.learner->ConstructNativeModel(s);EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);
    EXPECT_EQ(rejected.reason,"native_cold_replace_has_external_listener");EXPECT_EQ(rig.Revision(),before);
    EXPECT_EQ(tap->Input.GetDataSources(),inputs);
}

TEST(NativeModelBuilder,AdoptionPreservesEffectiveIndividualPhysicsAndRejectsWrongOverlay)
{
    EditingRig<NNeuronTimeLearner> rig(2000,1,"native_adoption");
    auto channel=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);channel->Capacity=1.37e-9;
    NativeEditSpec policy;policy.normalization=Normalization::TipResistance;policy.maximumCableLength=8;
    auto s=DescribeNativeLearnerModel(*rig.learner,false,Normalization::TipResistance,rig.learner->DendriteLength.GetData(),policy);
    const auto before=rig.Revision();auto wrong=s;wrong.inputs[0].resistance=*wrong.inputs[0].resistance*1.1;
    auto rejected=rig.learner->AdoptNativeModel(wrong);EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_EQ(rig.Revision(),before);
    const auto adopted=rig.learner->AdoptNativeModel(s);ASSERT_EQ(adopted.status,NativeModelBuildStatus::Adopted)<<adopted.reason;
    EXPECT_EQ(adopted.modelRevision,before);rig.learner->Build();EXPECT_TRUE(rig.learner->NativeModelEditFailure().empty());
    EXPECT_EQ(rig.Revision(),before);EXPECT_EQ(channel->Capacity.GetData(),1.37e-9);
}
TEST(NativeModelBuilder,AdoptsLegacyBranchMutedBaselineWithoutChangingBindings)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,0,"adopt_muted_baseline");
    NativeEditSpec policy;policy.maximumCableLength=8;
    auto s=DescribeNativeLearnerModel(*rig.learner,true,Normalization::SynapseCount,rig.learner->DendriteLength.GetData(),policy);
    ASSERT_TRUE(s.allowMutedInputBaseline);const auto before=rig.Revision();
    const auto adopted=rig.learner->AdoptNativeModel(s);ASSERT_EQ(adopted.status,NativeModelBuildStatus::Adopted)<<adopted.reason;
    rig.learner->Build();ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty());EXPECT_EQ(rig.Revision(),before);
    const auto measured=rig.Probe();ASSERT_EQ(measured.status,NativeProbeStatus::Completed);
    ASSERT_TRUE(measured.observation);EXPECT_TRUE(measured.observation->valid);EXPECT_EQ(rig.Revision(),before);
}

template<class Learner> void AssignedNativeWindow()
{
    EditingRig<Learner> rig(2000,0,"assigned_window");const auto before=rig.Revision();
    const auto isolated=rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true);
    ASSERT_TRUE(isolated.observation);EXPECT_FALSE(isolated.observation->valid);
    ASSERT_EQ(isolated.observation->peaks.size(),1u);
    EXPECT_EQ(isolated.observation->peaks[0].validity,PeakValidity::Ambiguous);
    const auto assigned=rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true);
    ASSERT_EQ(assigned.status,NativeProbeStatus::Completed);ASSERT_TRUE(assigned.observation);
    ASSERT_TRUE(assigned.observation->valid);ASSERT_EQ(assigned.observation->burstAssignments.size(),1u);
    const auto& waves=assigned.observation->burstAssignments[0].waves;ASSERT_EQ(waves.size(),2u);
    ASSERT_EQ(assigned.observation->peaks.size(),1u);const auto& peak=assigned.observation->peaks[0];
    EXPECT_EQ(peak.time,waves[1].time);EXPECT_EQ(peak.rawPotential,waves[1].rawPotential);
    EXPECT_EQ(peak.stimulusId,"pulse1");EXPECT_EQ(assigned.observation->specification.peakSelection,PeakSelectionPolicy::AssignedBurstWave);
    EXPECT_EQ(rig.Revision(),before);
    // The selected policy changes measurement, never the physical response.
    const auto& oldWaves=isolated.observation->burstAssignments[0].waves;ASSERT_EQ(oldWaves.size(),waves.size());
    for(std::size_t i=0;i<waves.size();++i)
    {
        EXPECT_DOUBLE_EQ(oldWaves[i].rawPotential,waves[i].rawPotential);
        EXPECT_NEAR(oldWaves[i].time-isolated.observation->specification.begin,
            waves[i].time-assigned.observation->specification.begin,1e-12);
    }
}
TEST(NativeAssignedWindow,ClassicMeasuresTheAssignedWaveWithoutChangingPhysics){AssignedNativeWindow<NNeuronTimeLearner>();}
TEST(NativeAssignedWindow,BranchMeasuresTheAssignedWaveWithoutChangingPhysics){AssignedNativeWindow<NNeuronTimeLearnerBranch>();}

template<class Learner> void CompareNativeRevisionProviders(unsigned frequency)
{
    EditingRig<Learner> rig(frequency,0,"revision_observer_ab");const auto hash=rig.Revision();
    std::vector<std::vector<double>> fullSamples,observedSamples;
    const auto capture=[](auto& output){return [&output](const NativeProbeSample& s){auto frame=s.potentials;frame.push_back(s.stimulus);output.push_back(std::move(frame));};};
    const auto start=std::chrono::steady_clock::now();
    const auto full=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,capture(fullSamples));
    const auto middle=std::chrono::steady_clock::now();
    const auto observed=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,capture(observedSamples));
    const auto end=std::chrono::steady_clock::now();
    ASSERT_EQ(full.status,NativeProbeStatus::Completed);ASSERT_EQ(observed.status,NativeProbeStatus::Completed);
    ASSERT_TRUE(full.observation);ASSERT_TRUE(observed.observation);EXPECT_TRUE(full.observation->valid);EXPECT_TRUE(observed.observation->valid);
    EXPECT_EQ(fullSamples,observedSamples);EXPECT_EQ(rig.Revision(),hash);
    EXPECT_EQ(full.currentBaseRevision,observed.currentBaseRevision);
    Artifact(rig.name+"_ab.json",QJsonDocument(QJsonObject{{"kind","native_revision_provider_ab"},
        {"frequency_hz",int(frequency)},{"branch",rig.branch},{"waveform_equal",fullSamples==observedSamples},
        {"sample_count",int(fullSamples.size())},{"model_revision",QString::fromStdString(hash)},
        {"full_seconds",std::chrono::duration<double>(middle-start).count()},
        {"observer_seconds",std::chrono::duration<double>(end-middle).count()}}).toJson());
}
TEST(NativeRevisionObserver,Classic2000){CompareNativeRevisionProviders<NNeuronTimeLearner>(2000);}
TEST(NativeRevisionObserver,Branch2000){CompareNativeRevisionProviders<NNeuronTimeLearnerBranch>(2000);}
TEST(NativeRevisionObserver,Classic20000){CompareNativeRevisionProviders<NNeuronTimeLearner>(20000);}
TEST(NativeRevisionObserver,Branch20000){CompareNativeRevisionProviders<NNeuronTimeLearnerBranch>(20000);}
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

template<class Learner> void RunNativeTraining(int normalization,bool cold=false)
{
    EditingRig<Learner> rig(2000,normalization,cold?"automatic_cold_service":"automatic_service",false,2,cold);
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
TEST(NativeColdTrainingService,ClassicN0){RunNativeTraining<NNeuronTimeLearner>(0,true);}
TEST(NativeColdTrainingService,BranchN0){RunNativeTraining<NNeuronTimeLearnerBranch>(0,true);}
TEST(NativeColdTrainingService,ClassicN1){RunNativeTraining<NNeuronTimeLearner>(1,true);}
TEST(NativeColdTrainingService,BranchN1){RunNativeTraining<NNeuronTimeLearnerBranch>(1,true);}

template<class Learner> ConfiguredNativeTraining Configuration(EditingRig<Learner>& rig)
{
    const auto plan=TrainingPlan(rig);ConfiguredNativeTraining c;
    NativeEditSpec policy;policy.maximumCableLength=8;policy.normalization=plan.search.normalization;
    c.model=DescribeNativeLearnerModel(*rig.learner,rig.branch,plan.search.normalization,rig.learner->DendriteLength.GetData(),policy);
    c.model.allowMutedInputBaseline=false;c.runId=plan.search.runId;c.protocolRevision=plan.protocol.revision;
    c.sampleId=plan.protocol.sampleId;c.stimulusProfile=*plan.protocol.stimulusProfile;
    c.duration=rig.duration;c.maximumSampleGap=plan.protocol.maximumSampleGap;c.minimumAmplitude=plan.protocol.minimumAmplitude;
    c.maximumSamples=plan.probe.specification.maximumSamples;c.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(std::size_t i=0;i<rig.inputCount;++i)c.windows.emplace_back(0.,rig.duration);
    c.search=plan.search;c.maximumReferenceProbes=plan.maximumReferenceProbes;c.maximumModelSeconds=plan.maximumModelSeconds;
    c.maximumWallSeconds=plan.maximumWallSeconds;return c;
}
template<class Learner> void ConfiguredTraining(int normalization,bool fromXml=false)
{
    EditingRig<Learner> rig(2000,normalization,fromXml?"configured_file":"configured_service");const auto configuration=Configuration(rig);
    const auto encoded=QJsonDocument(EncodeConfiguredNativeTraining(configuration)).toJson(QJsonDocument::Compact);
    EXPECT_EQ(EncodeConfiguredNativeTraining(ParseConfiguredNativeTraining(encoded.toStdString())),EncodeConfiguredNativeTraining(configuration));
    auto oldNeuron=rig.neuron;const double time=rig.environment->GetTime().GetDoubleTime();
    rig.learner->ControllerVersion=2;rig.learner->ControllerConfiguration=encoded.toStdString();
    if(fromXml)
    {
        // Save a cold declaration before V2 Build. Exercise the actual native
        // file loader rather than assigning properties on the receiving object.
        USerStorageXML storage;ASSERT_TRUE(storage.Create("ConfiguredColdLearner"));
        ASSERT_FALSE(rig.learner->ConfiguredModelInitialized.GetData());
        ASSERT_TRUE(rig.learner->SaveComponent(&storage,true,ptPubParameter|ptPubState|pgSystem));
        std::string serialized;ASSERT_TRUE(storage.Save(serialized));Artifact(rig.name+"_cold_configuration.xml",QByteArray::fromStdString(serialized));
        ASSERT_TRUE(storage.SelectNode(rig.learner->GetName()));
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        auto loaded=dynamic_pointer_cast<Learner>(core.storage->TakeObject(rig.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(loaded);
        loaded->SetEnvironment(rig.environment);loaded->SetGlobalTimeStep(2000);loaded->Name="Learner";
        rig.model->DelComponent("Learner",true);UEPtr<UContainer> node=loaded;
        ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);ASSERT_TRUE(loaded->LoadComponent(&storage,true));rig.learner=loaded;
    }
    ASSERT_TRUE(rig.learner->Build());ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
    EXPECT_TRUE(rig.learner->ConfiguredModelInitialized.GetData());
    rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
    rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    if(!fromXml)ASSERT_NE(rig.neuron.Get(),oldNeuron.Get());rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    rig.learner->Init();EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),time);
    std::size_t observations=0;std::ostringstream trace;
    ConfiguredNativeEvidenceSinks sinks;
    sinks.onPrepared=[&](const auto&,const auto&) {
        trace.str({});trace.clear();trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)trace<<",soma"<<i;trace<<'\n';
    };
    sinks.onSample=[&](const NativeProbeSample& sample) {
        trace<<sample.time<<','<<sample.stimulus;for(double v:sample.potentials)trace<<','<<v;trace<<'\n';
    };
    sinks.onObservation=[&](const NativeProbeResult& result) {
        ++observations;const auto prefix=rig.name+(fromXml?"_xmlprobe_":"_service_");
        Artifact(prefix+std::to_string(observations)+".json",QJsonDocument(EncodeNativeProbeEvidence(result)).toJson());
        Artifact(prefix+std::to_string(observations)+".csv",QByteArray::fromStdString(trace.str()));
    };
    rig.learner->SetConfiguredNativeEvidenceSinks(std::move(sinks));
    // No BeginNativeTraining/ConstructNativeModel API invocation. Native Build
    // consumes serialized parameters, and the scheduler starts the controller.
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,40000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();
    ASSERT_EQ(service.Outcome(),TrainingStatus::SearchUnresolved)<<service.Reason();
    ASSERT_TRUE(service.References());ASSERT_TRUE(service.Certificate());EXPECT_FALSE(service.Certificate()->Exact());
    ASSERT_TRUE(service.Search());EXPECT_GT(service.Search()->AppliedEdits(),0u);
    EXPECT_EQ(observations,service.IssuedReferenceProbes()+service.Search()->IssuedProbes());
    EXPECT_TRUE(service.Certificate()->Matches(rig.Revision(),*service.References(),configuration.search.tolerances,
        ModelStateKind::LearnedSolo,service.ModelEpoch()));
    Artifact(rig.name+"_configuration.json",encoded);
    Artifact(rig.name+(fromXml?"_xml_summary.json":"_training_summary.json"),QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    const auto hash=rig.Revision();const auto references=service.References()->Inputs();
    EXPECT_FALSE(rig.learner->SetControllerConfiguration(encoded.toStdString()+" "));
    EXPECT_FALSE(rig.learner->SetControllerVersion(1));
    ASSERT_TRUE(rig.learner->SetNeuronClassName(rig.learner->NeuronClassName.GetData()));rig.learner->Build();
    EXPECT_EQ(rig.Revision(),hash);rig.learner->Reset();EXPECT_EQ(rig.Revision(),hash);
    ASSERT_TRUE(service.References());EXPECT_EQ(service.References()->Inputs(),references);
    Artifact(rig.name+"_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}
TEST(ConfiguredNativeTraining,ClassicN0){ConfiguredTraining<NNeuronTimeLearner>(0);}
TEST(ConfiguredNativeTraining,BranchN0){ConfiguredTraining<NNeuronTimeLearnerBranch>(0);}
TEST(ConfiguredNativeTraining,ClassicN1){ConfiguredTraining<NNeuronTimeLearner>(1);}
TEST(ConfiguredNativeTraining,BranchN1){ConfiguredTraining<NNeuronTimeLearnerBranch>(1);}
TEST(ConfiguredNativeTraining,ClassicColdXmlStartsTheController){ConfiguredTraining<NNeuronTimeLearner>(0,true);}
TEST(ConfiguredNativeTraining,BranchColdXmlStartsTheController){ConfiguredTraining<NNeuronTimeLearnerBranch>(1,true);}

TEST(ConfiguredNativeTraining,StrictCodecRejectsDuplicateUnknownAndCorruptFields)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"configured_invalid_codec");const auto c=Configuration(rig);
    const auto valid=EncodeConfiguredNativeTraining(c);const auto bytes=QJsonDocument(valid).toJson(QJsonDocument::Compact);
    auto duplicate=bytes;duplicate.insert(1,"\"schema_version\":1,");
    EXPECT_THROW(ParseConfiguredNativeTraining(duplicate.toStdString()),std::invalid_argument);
    duplicate=bytes;duplicate.insert(1,"\"run\\u005fid\":\"duplicate\",");
    EXPECT_THROW(ParseConfiguredNativeTraining(duplicate.toStdString()),std::invalid_argument);
    auto invalid=valid;invalid["unknown"]=true;EXPECT_THROW(DecodeConfiguredNativeTraining(invalid),std::invalid_argument);
    invalid=valid;invalid["maximum_samples"]=2.5;EXPECT_THROW(DecodeConfiguredNativeTraining(invalid),std::invalid_argument);
    invalid=valid;invalid["record_spikes"]=0;EXPECT_THROW(DecodeConfiguredNativeTraining(invalid),std::invalid_argument);
    invalid=valid;auto model=invalid["model"].toObject();auto inputs=model["inputs"].toArray();auto input=inputs[0].toObject();
    input["resistance"]=QJsonValue(QJsonValue::Null);inputs[0]=input;model["inputs"]=inputs;invalid["model"]=model;
    const auto omitted=DecodeConfiguredNativeTraining(invalid);EXPECT_FALSE(omitted.model.inputs[0].resistance);
    EXPECT_EQ(EncodeConfiguredNativeTraining(omitted),invalid);
    EXPECT_THROW(ParseConfiguredNativeTraining("{}"),std::invalid_argument);
}
TEST(ConfiguredNativeTraining,MissingConfigurationAndLoadedMarkerFailWithoutColdReset)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,0,"configured_saved_state_guard");
    const auto before=rig.Revision();const auto c=Configuration(rig);
    EXPECT_EQ(rig.learner->ControllerVersion.GetData(),1);EXPECT_FALSE(rig.learner->SetControllerVersion(3));
    rig.learner->ControllerVersion=2;EXPECT_TRUE(rig.learner->Build());
    EXPECT_EQ(rig.learner->NativeTrainingController().Outcome(),TrainingStatus::InvalidModel);EXPECT_EQ(rig.Revision(),before);
    rig.learner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(c)).toJson(QJsonDocument::Compact).toStdString();
    rig.learner->ConfiguredModelInitialized.SetDataDirect(true);EXPECT_TRUE(rig.learner->Build());
    EXPECT_EQ(rig.learner->NativeModelEditFailure(),"configured_trained_model_requires_explicit_state_import");
    EXPECT_EQ(rig.Revision(),before);EXPECT_FALSE(rig.learner->NativeTrainingController().References());
}

template<class Learner> void ConfiguredLoadGuard(bool xml,bool copyState=false)
{
    EditingRig<Learner> rig(2000,0,xml?"configured_xml_guard":copyState?"configured_state_copy_guard":"configured_parameter_copy_guard");
    const auto configuration=QJsonDocument(EncodeConfiguredNativeTraining(Configuration(rig))).toJson(QJsonDocument::Compact).toStdString();
    rig.learner->ControllerVersion=2;rig.learner->ControllerConfiguration=configuration;
    rig.learner->Build();rig.learner->Init();ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty());
    rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);
    channel->Capacity=1.37e-9;rig.learner->IsNeedToTrain=false;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto target=dynamic_pointer_cast<Learner>(core.storage->TakeObject(rig.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(target);
    target->SetEnvironment(rig.environment);target->SetGlobalTimeStep(2000);
    if(xml)
    {
        USerStorageXML storage;ASSERT_TRUE(storage.Create("ConfiguredLearnerGuard"));
        ASSERT_TRUE(rig.learner->SaveComponent(&storage,true,ptPubParameter|ptPubState|pgSystem));
        std::string serialized;ASSERT_TRUE(storage.Save(serialized));
        Artifact(rig.name+"_learner.xml",QByteArray::fromStdString(serialized));
        ASSERT_TRUE(storage.SelectNode(rig.learner->GetName()));target->Name=rig.learner->GetName();
        ASSERT_TRUE(target->LoadComponent(&storage,true));
    }
    else ASSERT_TRUE(rig.learner->Copy(target,core.storage,copyState));
    EXPECT_EQ(target->ControllerVersion.GetData(),2);EXPECT_TRUE(target->ConfiguredModelInitialized.GetData());
    EXPECT_EQ(target->ControllerConfiguration.GetData(),configuration);EXPECT_TRUE(target->Build());
    EXPECT_EQ(target->NativeModelEditFailure(),"configured_trained_model_requires_explicit_state_import");
    auto loaded=target->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(loaded);
    auto capacity=loaded->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(capacity);
    EXPECT_EQ(capacity->Capacity.GetData(),1.37e-9);EXPECT_FALSE(target->NativeTrainingController().References());
    Artifact(rig.name+"_guard.json",QJsonDocument(QJsonObject{{"operation",xml?"xml_load":copyState?"copy_state":"copy_parameters"},
        {"diagnostic",QString::fromStdString(target->NativeModelEditFailure())},{"preserved_capacity",capacity->Capacity.GetData()}}).toJson());
    target->BreakLinks();core.storage->ReturnObject(target);
}
TEST(ConfiguredNativeTraining,ClassicXmlLoadDoesNotColdReset){ConfiguredLoadGuard<NNeuronTimeLearner>(true);}
TEST(ConfiguredNativeTraining,BranchXmlLoadDoesNotColdReset){ConfiguredLoadGuard<NNeuronTimeLearnerBranch>(true);}
TEST(ConfiguredNativeTraining,ClassicCopyWithoutStateDoesNotColdReset){ConfiguredLoadGuard<NNeuronTimeLearner>(false);}
TEST(ConfiguredNativeTraining,BranchCopyWithoutStateDoesNotColdReset){ConfiguredLoadGuard<NNeuronTimeLearnerBranch>(false);}
TEST(ConfiguredNativeTraining,ClassicCopyWithStateDoesNotColdReset){ConfiguredLoadGuard<NNeuronTimeLearner>(false,true);}
TEST(ConfiguredNativeTraining,BranchCopyWithStateDoesNotColdReset){ConfiguredLoadGuard<NNeuronTimeLearnerBranch>(false,true);}

TEST(NativeLearnedState,FreshProcessImport)
{
    const auto input=std::getenv("TIMELEARNER_LEARNED_IMPORT");
    if(!input)GTEST_SKIP()<<"Executed by completed-state fresh-process parent or cross-host control";
    const auto output=std::getenv("TIMELEARNER_LEARNED_OUTPUT");ASSERT_TRUE(output);
    QFile file(QString::fromLocal8Bit(input));ASSERT_TRUE(file.open(QIODevice::ReadOnly));
    const auto package=ParseNativeLearnedState(file.readAll().toStdString());
    const auto c=DecodeConfiguredNativeTraining(package["configuration"].toObject());
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    EXPECT_FALSE(core.storage->CheckClass(c.model.neuronClass));
    core.environment->DestroyModel();ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto model=core.environment->GetModel();model->SetGlobalTimeStep(c.model.frequencyHz);
    auto learner=dynamic_pointer_cast<UNet>(core.storage->TakeObject(c.model.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(learner);
    learner->Name="FrozenLearner";UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    learner->SetGlobalTimeStep(c.model.frequencyHz);
    const auto run=[&]<class Learner>(UEPtr<Learner> target) {
        const auto result=target->ImportNativeLearnedState(package,"native-learned-boundary-fixture-v1");
        ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;target->Build();target->Init();
        ASSERT_TRUE(target->NativeModelEditFailure().empty())<<target->NativeModelEditFailure();
        auto neuron=target->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto source=target->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(neuron);ASSERT_TRUE(source);
        const auto identity=NmsdkTools::IdentifyModel(neuron,{{&source->Output,"burst"}});
        ASSERT_EQ(identity["sha256"],package["model_revision"]);ASSERT_TRUE(target->NativeTrainingController().Certificate());
        ASSERT_FALSE(target->IsNeedToTrain.GetData());
        if(const auto start=std::getenv("TIMELEARNER_LEARNED_START_US"))core.environment->GetTime().SetTime(std::stoull(start));
        auto request=target->NativeTrainingController().Plan().probe;
        request.activeInput=0;request.inputId=target->NativeTrainingController().References()->Protocol().inputs[0].id;
        request.baseModelRevision=package["model_revision"].toString().toStdString();request.modelEpoch=target->NativeTrainingController().ModelEpoch();
        request.specification.runId="fresh-learned-import";request.specification.trialId="fresh-learned-import/probe";
        request.specification.windows={target->NativeTrainingController().Plan().inputWindows[0]};
        auto observer=std::make_shared<NmsdkTools::ModelRevisionObserver>();
        request.readModelRevision=[=]{return observer->Read(neuron.Get(),{{&source->Output,"burst"}}).toStdString();};
        request.readFullModelRevision=[=]{return observer->Read(neuron.Get(),{{&source->Output,"burst"}},true).toStdString();};
        std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(c.model.branch?1:c.model.inputs.size());++i)trace<<",soma"<<i;trace<<'\n';
        request.onSample=[&](const NativeProbeSample& sample) {
            trace<<sample.time<<','<<sample.stimulus;for(double value:sample.potentials)trace<<','<<value;trace<<'\n';
        };
        target->QueueNativeProbe(std::move(request));
        for(unsigned tick=0;target->NativeProbeState()==NativeProbeStatus::Queued || target->NativeProbeState()==NativeProbeStatus::Running;++tick)
        {ASSERT_LT(tick,unsigned((c.duration+.02)*c.model.frequencyHz));model->Calculate();core.environment->IncreaseModelTimeByStep();}
        const auto probe=target->TakeNativeProbeResult();ASSERT_TRUE(probe);ASSERT_EQ(probe->status,NativeProbeStatus::Completed);
        ASSERT_TRUE(probe->observation);ASSERT_TRUE(probe->observation->valid);
        EXPECT_EQ(NmsdkTools::IdentifyModel(neuron,{{&source->Output,"burst"}})["sha256"],package["model_revision"]);
        QJsonObject record{{"model",identity},{"certificate",EncodeTrainingCertificate(*target->NativeTrainingController().Certificate())},
            {"probe",EncodeNativeProbeEvidence(*probe)},{"need",target->IsNeedToTrain.GetData()}};
        QFile json(QString::fromLocal8Bit(output));ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        ASSERT_GT(json.write(QJsonDocument(record).toJson()),0);json.close();
        QFile csv(QString::fromLocal8Bit(output)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_GT(csv.write(QByteArray::fromStdString(trace.str())),0);
    };
    if(c.model.branch)run(dynamic_pointer_cast<NNeuronTimeLearnerBranch>(learner));else run(dynamic_pointer_cast<NNeuronTimeLearner>(learner));
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}

template<class Learner> void LearnedBoundary(int normalization,double sync=.02)
{
    EditingRig<Learner> rig(2000,normalization,sync==.02?"learned_boundary":"learned_boundary_explicit_tolerance",false,2,true);
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);channel->Capacity=1.41e-9;
    auto plan=TrainingPlan(rig,sync);plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    std::ostringstream trace;std::size_t observations=0;
    plan.probe.onPrepared=[&](const auto&,const auto&) {
        trace.str({});trace.clear();trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)trace<<",soma"<<i;trace<<'\n';
    };
    plan.probe.onSample=[&](const NativeProbeSample& sample) {
        trace<<sample.time<<','<<sample.stimulus;for(double value:sample.potentials)trace<<','<<value;trace<<'\n';
    };
    plan.observationSink=[&](const NativeProbeResult& result) {
        const auto base=rig.name+"_state_trial_"+std::to_string(++observations);
        Artifact(base+".json",QJsonDocument(EncodeNativeProbeEvidence(result)).toJson());
        Artifact(base+".csv",QByteArray::fromStdString(trace.str()));
    };
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,40000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();ASSERT_TRUE(service.Certificate())<<service.Reason();
    if(sync==.2)EXPECT_TRUE(service.Certificate()->Exact());
    ASSERT_EQ(service.ReferencePackets().size(),2u);ASSERT_EQ(service.FinalPackets().size(),2u);
    for(const auto& packet:service.ReferencePackets())EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(EncodeNativeProbeEvidence(packet))),EncodeNativeProbeEvidence(packet));
    for(const auto& packet:service.FinalPackets())EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(EncodeNativeProbeEvidence(packet))),EncodeNativeProbeEvidence(packet));
    const auto original=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();const auto references=service.References()->Inputs();
    const auto certificate=EncodeTrainingCertificate(*service.Certificate());
    const std::string implementation="native-learned-boundary-fixture-v1";
    const auto package=rig.learner->ExportNativeLearnedState(implementation);
    Artifact(rig.name+"_learned_state.json",QJsonDocument(package).toJson());
    EXPECT_EQ(ParseNativeLearnedState(QJsonDocument(package).toJson(QJsonDocument::Compact).toStdString()),package);
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto test=dynamic_pointer_cast<Learner>(core.storage->TakeObject(rig.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(test);
    test->Name="TestLearner";UEPtr<UContainer> node=test;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);test->SetGlobalTimeStep(2000);
    const auto imported=test->ImportNativeLearnedState(package,implementation);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;test->Build();test->Init();
    ASSERT_TRUE(test->NativeModelEditFailure().empty())<<test->NativeModelEditFailure();
    auto testNeuron=test->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto testSource=test->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(testNeuron);ASSERT_TRUE(testSource);
    const auto identity=NmsdkTools::IdentifyModel(testNeuron,{{&testSource->Output,"burst"}});
    EXPECT_EQ(identity["sha256"].toString().toStdString(),original);EXPECT_EQ(test->ReadNativeParameters(),parameters);
    ASSERT_TRUE(test->NativeTrainingController().Certificate());EXPECT_EQ(EncodeTrainingCertificate(*test->NativeTrainingController().Certificate()),certificate);
    EXPECT_EQ(test->NativeTrainingController().References()->Inputs(),references);EXPECT_FALSE(test->IsNeedToTrain.GetData());
    auto importedChannel=testNeuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(importedChannel);
    EXPECT_EQ(importedChannel->Capacity.GetData(),1.41e-9);
    // Both independent generators are armed on the same native tick. Compare
    // actual complete stimuli/soma traces, without nested Calculate or a
    // reconstructed analytical waveform. Only trial IDs differ.
    std::vector<NativeProbeSample> originalFrames,importedFrames;
    auto request=plan.probe;request.activeInput=0;request.inputId=plan.protocol.inputs[0].id;
    request.baseModelRevision=original;request.modelEpoch=service.ModelEpoch();request.specification.runId=rig.name+"/frozen";
    request.specification.trialId=rig.name+"/frozen/test";request.specification.windows={plan.inputWindows[0]};
    auto observer=std::make_shared<NmsdkTools::ModelRevisionObserver>();
    request.readModelRevision=[=]{return observer->Read(testNeuron.Get(),{{&testSource->Output,"burst"}}).toStdString();};
    request.readFullModelRevision=[=]{return observer->Read(testNeuron.Get(),{{&testSource->Output,"burst"}},true).toStdString();};
    request.onPrepared={};request.onSample=[&](const NativeProbeSample& frame){importedFrames.push_back(frame);};
    const auto frozenStart=rig.environment->GetTime().GetTime();test->QueueNativeProbe(std::move(request));
    const auto waveform=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const NativeProbeSample& frame){originalFrames.push_back(frame);});
    ASSERT_EQ(waveform.status,NativeProbeStatus::Completed);ASSERT_TRUE(waveform.observation);ASSERT_TRUE(waveform.observation->valid);
    const auto importedProbe=test->TakeNativeProbeResult();ASSERT_TRUE(importedProbe);ASSERT_EQ(importedProbe->status,NativeProbeStatus::Completed);
    ASSERT_TRUE(importedProbe->observation);ASSERT_TRUE(importedProbe->observation->valid);
    ASSERT_EQ(originalFrames.size(),importedFrames.size());ASSERT_FALSE(originalFrames.empty());
    std::ostringstream frozen;frozen.imbue(std::locale::classic());frozen<<std::setprecision(17)<<"time,stimulus";
    for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)frozen<<",soma"<<i;frozen<<'\n';
    for(std::size_t i=0;i<originalFrames.size();++i)
    {
        EXPECT_EQ(originalFrames[i].time,importedFrames[i].time);EXPECT_EQ(originalFrames[i].stimulus,importedFrames[i].stimulus);
        EXPECT_EQ(originalFrames[i].potentials,importedFrames[i].potentials);
        const auto& frame=importedFrames[i];frozen<<frame.time<<','<<frame.stimulus;for(double value:frame.potentials)frozen<<','<<value;frozen<<'\n';
    }
    Artifact(rig.name+"_frozen_test.csv",QByteArray::fromStdString(frozen.str()));
    Artifact(rig.name+"_frozen_test_evidence.json",QJsonDocument(EncodeNativeProbeEvidence(*importedProbe)).toJson());
    EXPECT_EQ(test->ReadNativeParameters(),parameters);EXPECT_EQ(rig.Revision(),original);
    QTemporaryDir directory;ASSERT_TRUE(directory.isValid());
    const auto path=directory.path()+"/learned.json",output=directory.path()+"/imported.json";
    QFile serialized(path);ASSERT_TRUE(serialized.open(QIODevice::WriteOnly|QIODevice::NewOnly));
    ASSERT_GT(serialized.write(QJsonDocument(package).toJson()),0);serialized.close();
    QProcess child;auto childEnv=QProcessEnvironment::systemEnvironment();
    childEnv.insert("TIMELEARNER_LEARNED_IMPORT",path);childEnv.insert("TIMELEARNER_LEARNED_OUTPUT",output);
    childEnv.insert("TIMELEARNER_LEARNED_START_US",QString::number(frozenStart));child.setProcessEnvironment(childEnv);
    child.setProgram(QCoreApplication::applicationFilePath());child.setArguments({"--gtest_filter=NativeLearnedState.FreshProcessImport"});
    child.start();ASSERT_TRUE(child.waitForStarted(30000));ASSERT_TRUE(child.waitForFinished(120000));
    Artifact(rig.name+"_fresh_process.log",child.readAllStandardOutput()+child.readAllStandardError());ASSERT_EQ(child.exitCode(),0);
    QFile loaded(output);ASSERT_TRUE(loaded.open(QIODevice::ReadOnly));const auto record=QJsonDocument::fromJson(loaded.readAll()).object();
    EXPECT_EQ(record["model"].toObject()["sha256"],package["model_revision"]);EXPECT_EQ(record["certificate"].toObject(),certificate);
    Artifact(rig.name+"_fresh_process.json",QJsonDocument(record).toJson());
    QFile csv(output+".csv");ASSERT_TRUE(csv.open(QIODevice::ReadOnly));const auto freshTrace=csv.readAll();
    EXPECT_EQ(freshTrace,QByteArray::fromStdString(frozen.str()));Artifact(rig.name+"_fresh_process.csv",freshTrace);
    // The receiver must not turn this finished boundary into a new cold run.
    for(unsigned i=0;i<8;++i){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    EXPECT_FALSE(test->IsNeedToTrain.GetData());EXPECT_EQ(test->ReadNativeParameters(),parameters);
    test->Reset();EXPECT_EQ(test->NativeTrainingController().References()->Inputs(),references);
    EXPECT_EQ(test->ExportNativeLearnedState(implementation)["model_revision"],package["model_revision"]);
    auto corrupted=package;corrupted["model_revision"]="corrupt";
    const auto rejected=test->ImportNativeLearnedState(corrupted,implementation);EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(test->ReadNativeParameters(),parameters);
    Artifact(rig.name+"_imported_model.json",QJsonDocument(identity).toJson());
}
TEST(NativeLearnedState,ClassicN0){LearnedBoundary<NNeuronTimeLearner>(0);}
TEST(NativeLearnedState,BranchN0){LearnedBoundary<NNeuronTimeLearnerBranch>(0);}
TEST(NativeLearnedState,ClassicN1){LearnedBoundary<NNeuronTimeLearner>(1);}
TEST(NativeLearnedState,BranchN1){LearnedBoundary<NNeuronTimeLearnerBranch>(1);}
TEST(NativeLearnedState,ExactCertificateWithExplicitPointTwoTolerance){LearnedBoundary<NNeuronTimeLearner>(1,.2);}

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

template<class Learner> void ObserverSeesExternalPhysicsEdit()
{
    EditingRig<Learner> rig(2000,0,"observer_external_physics");auto plan=TrainingPlan(rig);
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);
    const double capacity=channel->Capacity.GetData();unsigned samples=0;std::vector<NativeProbeResult> recorded;
    plan.probe.onSample=[&](const NativeProbeSample&) {
        if(++samples==10)channel->Capacity=std::nextafter(capacity,std::numeric_limits<double>::infinity());
    };
    plan.observationSink=[&](const NativeProbeResult& result){recorded.push_back(result);};
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);
    EXPECT_EQ(service.Reason(),"model_revision_changed");EXPECT_EQ(samples,10u);
    EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());ASSERT_EQ(recorded.size(),1u);
    ASSERT_TRUE(recorded[0].observation);EXPECT_FALSE(recorded[0].observation->valid);
    EXPECT_TRUE(recorded[0].requiresFreshVerification);
    Artifact(rig.name+"_rejected.json",QJsonDocument(EncodeNativeProbeEvidence(recorded[0])).toJson());
}
TEST(NativeTrainingService,ClassicObserverDetectsTinyExternalPhysicsChange){ObserverSeesExternalPhysicsEdit<NNeuronTimeLearner>();}
TEST(NativeTrainingService,BranchObserverDetectsTinyExternalPhysicsChange){ObserverSeesExternalPhysicsEdit<NNeuronTimeLearnerBranch>();}

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
