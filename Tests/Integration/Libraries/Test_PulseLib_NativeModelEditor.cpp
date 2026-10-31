#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseChannel.h"
#include "NPulseSynapse.h"
#include "NConstGenerator.h"
#include "NNeuronPostTrainTune.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ModelInspection.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/NativeLearnedState.h"
#include "TimeLearner/NativeRecognitionState.h"
#include "TimeLearner/NativeThresholdCandidate.h"
#include "TimeLearner/NativeCalibrationProposal.h"
#include "TimeLearner/NativeCalibrationAssessment.h"
#include "TimeLearner/NativeCalibratedState.h"
#include "TimeLearner/NativeRecognitionObservationValidation.h"
#include "TimeLearner/NativeThresholdSupport.h"
#include "TimeLearner/NativeTrainingBindings.h"
#include "TimeLearner/NativePostTuneBoundary.h"
#include "TimeLearner/NumericChecks.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../Rdk/Core/Engine/UComponentFactory.h"
#include <QFile>
#include <QDir>
#include <QJsonArray>
#include <QJsonDocument>
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
#include <cmath>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
template<class Learner> class ImportRollbackLearner : public Learner {
public:
    bool failNeuronAttach=false;
    void RefreshGraphAliases() {
        this->Neuron=this->template GetComponentL<NPulseNeuron>("Neuron",true);
        this->Dataset=this->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    }
    ImportRollbackLearner* New(void) override { return new ImportRollbackLearner; }
protected:
    void ABeforeAddComponent(UEPtr<UContainer> child,UEPtr<UIPointer> pointer=0) override
    {
        Learner::ABeforeAddComponent(child,pointer);
        if(failNeuronAttach && child->GetName()=="Neuron")
        {failNeuronAttach=false;throw std::runtime_error("injected_import_neuron_attach_failure");}
    }
};
class PostTuneRebuildBranch : public NNeuronTimeLearnerBranch {
public:
    bool failNeuronAttach=false;
    PostTuneRebuildBranch* New(void) override {return new PostTuneRebuildBranch;}
    void PreparePostTune(int mode)
    {
        TrainingPhase=4; // Public legacy TrainingPhase value: PostTune.
        PostTrainTipResistanceMode=mode;
        TipResistanceCanonFloor=3.e8;TipResistanceCanonLast=4.e8;
        PostTuneTipSnapshot=TipSynapseResistance.GetData();PostTuneTrialTips=PostTuneTipSnapshot;
        ApplyPostTrainTipMode(false);ApplyPulseGeneratorMute();
    }
    bool Reconstruct(){return RebuildCableForPostTuneProbes();}
protected:
    void ABeforeAddComponent(UEPtr<UContainer> child,UEPtr<UIPointer> pointer=0) override
    {
        NNeuronTimeLearnerBranch::ABeforeAddComponent(child,pointer);
        if(failNeuronAttach && child->GetName()=="Neuron")
        {failNeuronAttach=false;throw std::runtime_error("injected_posttune_neuron_attach_failure");}
    }
};
template<class Learner> class PostTuneStimulusLearner : public Learner {
public:
    PostTuneStimulusLearner* New(void) override {return new PostTuneStimulusLearner;}
    void ArmPresentations(const std::vector<std::vector<double>>& patterns)
    {
        // The public legacy phase values differ: Classic PostTune=3,
        // Branch PostTune=4 (Branch reserves 3 for parallel calibration).
        this->TrainingPhase=std::is_base_of<NNeuronTimeLearnerBranch,Learner>::value?4:3;
        this->PostTrainTuneComplete=false;
        this->PostTuneFreeRunActive=false;this->ResetNeuronBeforeTrainBurst=false;
        this->PostTunePatterns=patterns;this->PostTuneTargetIsi=patterns.front();
    }
    bool Present(int index){return this->PushPostTunePattern(index);}
    void ObserveFirstPulse(double now){this->BeginTrainingIteration(now);}
    std::vector<double> ExpectedTimes() const {return this->ExpectedPulseRelTimes;}
    std::vector<double> CapturedTarget() const {return this->PostTuneTargetIsi;}
};
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
    bool branch=std::is_base_of<NNeuronTimeLearnerBranch,Learner>::value;
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
               bool cold=false,int neuronMode=2,int learnerMode=1,bool domainInhibitionProfile=false,
               const std::string& learnerClass={},int initialFirstSynapses=1,double initialThreshold=1.)
        :frequency(f),normalization(mode),inputCount(inputs),tightBurst(tight)
    {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        if(!environment->CreateModel("NModel"))throw std::runtime_error("editor_fixture_model");model=environment->GetModel();
        name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(f)+"_N"+std::to_string(mode)+"_"+suffix;
        StorageProfileSpec profile;profile.name=name;profile.frequencyHz=f;profile.neuronBaseClass="NSPNeuronGen";
        if(domainInhibitionProfile)profile.body.inhChannel.capacity=.15e-9;
        profile.initialThreshold=initialThreshold;profile.ltMembrane=profile.body;profile.ltMembrane->excChannel.capacity=.3e-9;
        const auto registered=RegisterStorageProfile(core.storage,environment,profile);
        learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(learnerClass.empty()?
            (branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"):learnerClass));
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
            for(std::size_t i=0;i<lengths.size();++i)
                initial.inputs.push_back({lengths[i],i==0?initialFirstSynapses:1,std::nullopt});
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

template<class Learner> void NativeAbsoluteClockProbe(unsigned frequency,double origin)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    struct ClockRestore {
        UEPtr<UEnvironment> environment;ULongTime previous;
        ~ClockRestore(){environment->GetTime().SetTime(previous);}
    } restore{core.environment,core.environment->GetTime().GetTime()};
    core.environment->GetTime().SetTime(ULongTime(origin*1000000.));
    EditingRig<Learner> rig(frequency,1,"absolute_clock_"+std::to_string(int(origin)));
    const auto result=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true);
    ASSERT_EQ(result.status,NativeProbeStatus::Completed);ASSERT_TRUE(result.observation);
    EXPECT_TRUE(result.observation->complete);EXPECT_TRUE(result.observation->valid);
    for(const auto& reason:result.observation->reasons)ADD_FAILURE()<<reason;
}
TEST(NativeSamplingClock,Classic2000At131){NativeAbsoluteClockProbe<NNeuronTimeLearner>(2000,131.);}
TEST(NativeSamplingClock,Branch2000At131){NativeAbsoluteClockProbe<NNeuronTimeLearnerBranch>(2000,131.);}
TEST(NativeSamplingClock,Classic20000At131){NativeAbsoluteClockProbe<NNeuronTimeLearner>(20000,131.);}
TEST(NativeSamplingClock,Branch20000At131){NativeAbsoluteClockProbe<NNeuronTimeLearnerBranch>(20000,131.);}
TEST(NativeSamplingClock,Classic2000AtMillion){NativeAbsoluteClockProbe<NNeuronTimeLearner>(2000,1000000.);}
TEST(NativeSamplingClock,Branch2000AtMillion){NativeAbsoluteClockProbe<NNeuronTimeLearnerBranch>(2000,1000000.);}
TEST(NativeSamplingClock,Classic20000AtMillion){NativeAbsoluteClockProbe<NNeuronTimeLearner>(20000,1000000.);}
TEST(NativeSamplingClock,Branch20000AtMillion){NativeAbsoluteClockProbe<NNeuronTimeLearnerBranch>(20000,1000000.);}

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

template<class Learner> void NativeResistanceDomainSearch(unsigned frequency=2000)
{
    EditingRig<Learner> rig(frequency,1,"effective_resistance_domain");auto plan=TrainingPlan(rig);
    plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    for(auto& bound:plan.search.bounds)bound.maximumLength=bound.minimumLength;
    plan.search.bounds[0].minimumResistance=.5e6;plan.search.bounds[0].maximumResistance=1.e9;
    plan.search.maximumCandidatesPerInput=3;plan.search.resistanceSubdivisionDepth=0;
    std::size_t observations=0;std::ostringstream trace;
    plan.probe.onPrepared=[&](const auto&,const auto&) {
        trace.str({});trace.clear();trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)trace<<",soma"<<i;trace<<'\n';
    };
    plan.probe.onSample=[&](const auto& frame) {
        trace<<frame.time<<','<<frame.stimulus;for(double value:frame.potentials)trace<<','<<value;trace<<'\n';
    };
    plan.observationSink=[&](const auto& packet) {
        const auto stem=rig.name+"_domain_trial_"+std::to_string(++observations);
        Artifact(stem+".json",QJsonDocument(EncodeNativeProbeEvidence(packet)).toJson());
        Artifact(stem+".csv",QByteArray::fromStdString(trace.str()));
    };
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,unsigned(plan.maximumModelSeconds*rig.frequency)+100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();ASSERT_TRUE(service.Search())<<service.Reason();
    Artifact(rig.name+"_domain_summary.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    EXPECT_GE(service.Search()->AppliedEdits(),1u);EXPECT_GE(service.Search()->Evidence().size(),2u);
    ASSERT_FALSE(service.Search()->Domains().empty());
    const auto& firstDomain=service.Search()->Domains().front();ASSERT_EQ(firstDomain.status,ResistanceDomainStatus::Available);
    const auto lower=std::max(plan.search.bounds[0].minimumResistance,firstDomain.minimumResistance);
    EXPECT_TRUE(std::any_of(service.Search()->Evidence().begin(),service.Search()->Evidence().end(),[&](const auto& candidate) {
        return candidate.inputIndex==0 && candidate.parameters.resistance==lower;
    }))<<"effective domain lower endpoint must be physically measured";
    EXPECT_LE(service.Search()->Domains().size(),2*plan.search.maximumCandidatesPerInput+1);
    for(const auto& rejected:service.Search()->Rejected())
    {
        EXPECT_EQ(rejected.reason.find("channel_step_not_certified_strictly_stable"),std::string::npos)
            <<"candidate mesh must use effective physical domain: "<<rejected.reason;
        EXPECT_EQ(rejected.reason.find("candidate_outside_effective_resistance_interval"),std::string::npos)
            <<"candidate mesh must use effective physical domain: "<<rejected.reason;
    }
    // Convergence is reported from actual residuals, not required by this
    // candidate-domain fixture in either direction.
}
TEST(NativeResistanceDomains,ClassicSearchUsesEffectiveDomain){NativeResistanceDomainSearch<NNeuronTimeLearner>();}
TEST(NativeResistanceDomains,BranchSearchUsesEffectiveDomain){NativeResistanceDomainSearch<NNeuronTimeLearnerBranch>();}
TEST(NativeResistanceDomains,ClassicSearchUsesEffectiveDomain20000){NativeResistanceDomainSearch<NNeuronTimeLearner>(20000);}
TEST(NativeResistanceDomains,BranchSearchUsesEffectiveDomain20000){NativeResistanceDomainSearch<NNeuronTimeLearnerBranch>(20000);}

void NativeBranchDomainGeometry(bool canSeparate)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,1,canSeparate?"domain_separated_banks":"domain_locked_banks",false,4,true);
    auto plan=TrainingPlan(rig,0.);plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    const auto initial=rig.learner->ReadNativeParameters();
    for(std::size_t i=0;i+1<plan.search.bounds.size();++i)
    {
        auto& b=plan.search.bounds[i];b.maximumLength=canSeparate?3:2;
        b.minimumResistance=.5e6;b.maximumResistance=1.e9;
    }
    plan.search.maximumCandidatesPerInput=12;
    struct Recording { std::size_t trials=0;std::ostringstream trace; };
    const auto recording=std::make_shared<Recording>();const auto stem=rig.name;
    plan.probe.onPrepared=[recording](const auto&,const auto&) {
        recording->trace.str({});recording->trace.clear();recording->trace.imbue(std::locale::classic());
        recording->trace<<std::setprecision(17)<<"time,stimulus,soma0\n";
    };
    plan.probe.onSample=[recording](const auto& frame) {
        recording->trace<<frame.time<<','<<frame.stimulus;for(double v:frame.potentials)recording->trace<<','<<v;recording->trace<<'\n';
    };
    plan.observationSink=[recording,stem](const auto& packet) {
        const auto name=stem+"_geometry_trial_"+std::to_string(++recording->trials);
        Artifact(name+".json",QJsonDocument(EncodeNativeProbeEvidence(packet)).toJson());
        Artifact(name+".csv",QByteArray::fromStdString(recording->trace.str()));
    };
    rig.learner->BeginNativeTraining(plan);bool measured=false;
    for(unsigned ticks=0;;++ticks)
    {
        ASSERT_LT(ticks,unsigned(plan.maximumModelSeconds*rig.frequency)+100u);
        const auto& service=rig.learner->NativeTrainingController();
        if(service.Search())for(const auto& e:service.Search()->Evidence())
        {
            if(e.inputIndex!=2 || e.fullParameters.size()!=4 || e.fullParameters[2].length!=2)continue;
            if(canSeparate)measured=measured || (e.fullParameters[1].length>2 && e.parameters.resistance!=initial[2].resistance);
            else measured=measured || e.fullParameters[1].length==2;
        }
        if(measured){rig.learner->IsNeedToTrain=false;break;}
        if(service.State()==NativeTrainingState::Finished)break;
        rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    }
    const auto& service=rig.learner->NativeTrainingController();
    Artifact(rig.name+"_geometry_summary.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    ASSERT_TRUE(service.Search())<<service.Reason();EXPECT_TRUE(measured)<<service.Reason();
    EXPECT_EQ(rig.learner->ReadNativeParameters().back(),initial.back());
    bool found=false;for(const auto& d:service.Search()->Domains())
    {
        if(d.inputIndex!=2 || d.geometry.size()!=4 || d.geometry[2].length!=2 || d.status!=ResistanceDomainStatus::Available)continue;
        if(canSeparate && d.geometry[1].length>2 && !d.lockedBySharedBank)found=true;
        if(!canSeparate && d.geometry[1].length==2 && d.lockedBySharedBank)
        {found=true;EXPECT_EQ(d.minimumResistance,d.maximumResistance);EXPECT_EQ(d.minimumResistance,initial[2].resistance);}
    }
    EXPECT_TRUE(found);EXPECT_FALSE(service.Certificate());
}
TEST(NativeResistanceDomains,BranchBoundedSharedBanksKeepSingletonGeometry){NativeBranchDomainGeometry(false);}
TEST(NativeResistanceDomains,BranchFreeUpstreamBanksCanSeparateForRsSearch){NativeBranchDomainGeometry(true);}

template<class Learner> void NativeDomainPreview()
{
    EditingRig<Learner> rig(2000,1,"domain_preview");auto values=rig.learner->ReadNativeParameters();const auto original=values;
    const auto early=rig.learner->AssessNativeResistanceDomain(values,0);
    EXPECT_EQ(early.status,ResistanceDomainStatus::Unsupported);EXPECT_EQ(early.reason,"native_domain_requires_consumed_probe_boundary");
    const auto first=rig.Probe();ASSERT_EQ(first.status,NativeProbeStatus::Completed);
    const auto before=rig.Revision();values[0].resistance=.5e6;
    const auto domain=rig.learner->AssessNativeResistanceDomain(values,0);
    ASSERT_EQ(domain.status,ResistanceDomainStatus::Available)<<domain.reason;
    EXPECT_FALSE(domain.modelMayHaveChanged);EXPECT_EQ(domain.baseModelRevision,before);EXPECT_FALSE(domain.previewModelRevision.empty());
    EXPECT_GT(domain.minimumResistance,values[0].resistance);EXPECT_LT(domain.minimumResistance,original[0].resistance);
    EXPECT_GT(domain.maximumResistance,original[0].resistance);EXPECT_FALSE(domain.lockedBySharedBank);EXPECT_FALSE(domain.channels.empty());
    EXPECT_EQ(rig.Revision(),before);EXPECT_EQ(rig.learner->ReadNativeParameters(),original);
    values[0].resistance=1.e9;const auto other=rig.learner->AssessNativeResistanceDomain(values,0);
    ASSERT_EQ(other.status,ResistanceDomainStatus::Available)<<other.reason;
    EXPECT_NEAR(other.minimumResistance,domain.minimumResistance,domain.minimumResistance*32*std::numeric_limits<double>::epsilon());
    EXPECT_EQ(other.maximumResistance,domain.maximumResistance);EXPECT_EQ(rig.Revision(),before);
    values[0].resistance=domain.minimumResistance;
    const auto applied=rig.learner->ApplyNativeParameters(values);ASSERT_EQ(applied.status,NativeEditStatus::Applied)<<applied.reason;
    const auto assessment=AssessNativeIntegration(rig.neuron,rig.source->Amplitude.GetData());EXPECT_TRUE(assessment.valid)<<assessment.reason;
    const auto probe=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true);
    EXPECT_EQ(probe.status,NativeProbeStatus::Completed);
    Artifact(rig.name+"_domain_preview.json",QJsonDocument(EncodeResistanceDomainAssessment(domain)).toJson());
}
TEST(NativeResistanceDomains,ClassicReadonlyPreview){NativeDomainPreview<NNeuronTimeLearner>();}
TEST(NativeResistanceDomains,BranchReadonlyPreview){NativeDomainPreview<NNeuronTimeLearnerBranch>();}

template<class Learner> void NativeDomainInhibition()
{
    EditingRig<Learner> rig(2000,1,"domain_inhibition",false,2,true,2,1,true);
    NativeEditSpec policy;policy.normalization=Normalization::TipResistance;policy.maximumCableLength=8;
    auto spec=DescribeNativeLearnerModel(*rig.learner,rig.branch,Normalization::TipResistance,rig.learner->DendriteLength.GetData(),policy);
    spec.allocatedCableLengths.clear();
    for(std::size_t i=0;i<spec.inputs.size();++i)spec.editPolicy.inhibition.push_back({i,1,*spec.inputs[i].resistance});
    double minimum[2]{};
    for(int scaled=0;scaled!=2;++scaled)
    {
        spec.scaleInhibitionWithInput=scaled!=0;const auto built=rig.learner->ConstructNativeModel(spec);
        ASSERT_EQ(built.status,NativeModelBuildStatus::Constructed)<<built.reason;rig.model->Init();rig.model->Reset();
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
        const auto initial=rig.Probe();ASSERT_NE(initial.status,NativeProbeStatus::Running);
        const auto before=rig.Revision();auto values=rig.learner->ReadNativeParameters();values[0].resistance=.5e6;
        const auto domain=rig.learner->AssessNativeResistanceDomain(values,0);
        ASSERT_EQ(domain.status,ResistanceDomainStatus::Available)<<domain.reason;minimum[scaled]=domain.minimumResistance;
        EXPECT_EQ(rig.Revision(),before);EXPECT_FALSE(domain.modelMayHaveChanged);
        bool variableInhibition=false;for(const auto& c:domain.channels)if(c.path.find("InhChannel")!=std::string::npos)variableInhibition=true;
        EXPECT_EQ(variableInhibition,scaled!=0);
        Artifact(rig.name+(scaled?"_scaled_domain.json":"_fixed_domain.json"),
            QJsonDocument(EncodeResistanceDomainAssessment(domain)).toJson());
    }
    EXPECT_GT(minimum[1],minimum[0]);
}
TEST(NativeResistanceDomains,ClassicScaledInhibitionDomain){NativeDomainInhibition<NNeuronTimeLearner>();}
TEST(NativeResistanceDomains,BranchScaledInhibitionDomain){NativeDomainInhibition<NNeuronTimeLearnerBranch>();}

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
template<class Learner> void ConfiguredTraining(int normalization,bool fromXml=false,bool n0Repeats=false)
{
    EditingRig<Learner> rig(2000,normalization,n0Repeats?"configured_repeats":fromXml?"configured_file":"configured_service");auto configuration=Configuration(rig);
    if(n0Repeats)configuration.search.n0CandidateRepeats=2;
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
    if(n0Repeats)
    {
        ASSERT_FALSE(service.Search()->CandidateRepeats().empty());
        for(const auto& group:service.Search()->CandidateRepeats())
        {EXPECT_EQ(group.trialIds.size(),2u);EXPECT_EQ(group.anchorTrialIds.size(),2u);}
        EXPECT_EQ(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())["schema_version"],QJsonValue(2));
    }
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
TEST(ConfiguredNativeTrainingN0Repeats,ClassicNativePairs){ConfiguredTraining<NNeuronTimeLearner>(0,false,true);}
TEST(ConfiguredNativeTrainingN0Repeats,BranchNativePairs){ConfiguredTraining<NNeuronTimeLearnerBranch>(0,false,true);}
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
TEST(ConfiguredNativeTrainingN0Repeats,Schema2DeclaresPolicyAndSchema1DoesNotSilentlyChange)
{
    EditingRig<NNeuronTimeLearner> rig(2000,0,"configured_repeat_codec");auto c=Configuration(rig);
    const auto legacy=EncodeConfiguredNativeTraining(c);EXPECT_EQ(legacy["schema_version"],QJsonValue(1));
    EXPECT_EQ(DecodeConfiguredNativeTraining(legacy).search.n0CandidateRepeats,1u);
    c.search.n0CandidateRepeats=2;const auto repeated=EncodeConfiguredNativeTraining(c);
    EXPECT_EQ(repeated["schema_version"],QJsonValue(2));
    EXPECT_EQ(DecodeConfiguredNativeTraining(repeated).search.n0CandidateRepeats,2u);
    EXPECT_EQ(EncodeConfiguredNativeTraining(DecodeConfiguredNativeTraining(repeated)),repeated);
    auto invalid=repeated;invalid["schema_version"]=1;
    EXPECT_THROW(DecodeConfiguredNativeTraining(invalid),std::invalid_argument);
    for(const auto value:{QJsonValue(true),QJsonValue(1),QJsonValue(129),QJsonValue(2.5)})
    {
        invalid=repeated;auto search=invalid["search"].toObject();search["n0_candidate_repeats"]=value;invalid["search"]=search;
        EXPECT_THROW(DecodeConfiguredNativeTraining(invalid),std::invalid_argument);
    }
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
    const bool stopped=package["kind"]==QJsonValue("timelearner_stopped_state");
    const auto c=DecodeConfiguredNativeTraining(package["configuration"].toObject());
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    EXPECT_FALSE(core.storage->CheckClass(c.model.neuronClass));
    core.environment->SetUseIndTimeStepFlag(false);
    core.environment->DestroyModel();ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto model=core.environment->GetModel();model->SetGlobalTimeStep(c.model.frequencyHz);
    auto learner=dynamic_pointer_cast<UNet>(core.storage->TakeObject(c.model.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(learner);
    learner->Name="FrozenLearner";UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    learner->SetGlobalTimeStep(c.model.frequencyHz);
    const auto run=[&]<class Learner>(UEPtr<Learner> target) {
        const auto result=target->ImportNativeLearnedState(package,stopped?"native-stopped-boundary-fixture-v1":"native-learned-boundary-fixture-v1");
        ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;target->Build();target->Init();model->Init();model->Reset();
        ASSERT_TRUE(target->NativeModelEditFailure().empty())<<target->NativeModelEditFailure();
        auto neuron=target->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto source=target->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(neuron);ASSERT_TRUE(source);
        const auto identity=NmsdkTools::IdentifyModel(neuron,{{&source->Output,"burst"}});
        ASSERT_EQ(identity["sha256"],package["model_revision"]);ASSERT_EQ(bool(target->NativeTrainingController().Certificate()),!stopped);
        ASSERT_FALSE(target->IsNeedToTrain.GetData());
        if(const auto start=std::getenv("TIMELEARNER_LEARNED_START_US"))core.environment->GetTime().SetTime(std::stoull(start));
        auto request=target->NativeTrainingController().Plan().probe;
        request.activeInput=0;request.inputId=target->NativeTrainingController().Plan().protocol.inputs[0].id;
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
        QJsonObject record{{"model",identity},{"certificate",stopped?QJsonValue(QJsonValue::Null):QJsonValue(EncodeTrainingCertificate(*target->NativeTrainingController().Certificate()))},
            {"probe",EncodeNativeProbeEvidence(*probe)},{"need",target->IsNeedToTrain.GetData()}};
        QFile json(QString::fromLocal8Bit(output));ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        ASSERT_GT(json.write(QJsonDocument(record).toJson()),0);json.close();
        QFile csv(QString::fromLocal8Bit(output)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_GT(csv.write(QByteArray::fromStdString(trace.str())),0);
    };
    if(c.model.branch)run(dynamic_pointer_cast<NNeuronTimeLearnerBranch>(learner));else run(dynamic_pointer_cast<NNeuronTimeLearner>(learner));
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}


enum class RecognitionCase { Identity,Scaled,Clipped,SharedConflict,OwnedIdentity,OwnedScaled,OwnedClipped,OwnedFreshIdentity,OwnedFreshScaled,ThresholdCandidates,ThresholdPotential,CalibratedThreshold };

template<class Learner> void FrozenTrialChecks(EditingRig<Learner>& rig,const QJsonObject& package,
    bool recordThresholdPotential=false,std::vector<NativeRecognitionTrialRequest>* declaredRequests=nullptr,
    std::vector<NativeRecognitionTrialObservation>* recorded=nullptr)
{
    const auto target=rig.learner->InputPattern.GetData();const auto frozen=rig.Revision();
    const std::string implementation="native-learned-boundary-fixture-v1";
    auto make=[&](int index,bool foil,RecognitionResetPolicy policy) {
        NativeRecognitionTrialRequest request;request.runId=rig.name+"_frozen";request.trialId="trial_"+std::to_string(index);
        request.recordThresholdPotential=recordThresholdPotential;
        request.sampleId=foil?(recordThresholdPotential?"foil_dispersed":"foil_reverse"):"training_target";request.label=foil?"foil":"target";
        request.resetPolicy=policy;request.pattern=target;
        if(foil)
        {
            if(recordThresholdPotential){for(int row=1;row<target.GetRows();++row)request.pattern(row,0)=target(row,0)*8.;}
            else for(int row=0;row<target.GetRows();++row)request.pattern(row,0)=target(target.GetRows()-row-1,0);
        }
        QJsonArray values;double span=0.;
        for(int row=0;row<target.GetRows();++row){values.append(request.pattern(row,0));span+=request.pattern(row,0);}
        request.patternHash=NmsdkTools::CanonicalModelDataSha256(values).toStdString();
        request.duration=std::ceil((span+.03)*rig.frequency)/rig.frequency;return request;
    };
    auto tick=[&] { rig.model->Calculate();rig.environment->IncreaseModelTimeByStep(); };
    std::size_t observedSpikes=0;
    if(recorded)recorded->clear();
    if(declaredRequests)
    {
        declaredRequests->clear();for(int i=0;i<4;++i)declaredRequests->push_back(make(i,i%2==1,i<2?RecognitionResetPolicy::PerTrial:RecognitionResetPolicy::PreserveNeuronDynamics));
        if(recordThresholdPotential)
        {
        QJsonArray trialDesign;
        for(const auto& q:*declaredRequests)
        {
            QJsonArray pattern;for(int row=0;row<q.pattern.GetRows();++row)pattern.append(q.pattern(row,0));
            trialDesign.append(QJsonObject{{"trial_id",QString::fromStdString(q.trialId)},
                {"sample_id",QString::fromStdString(q.sampleId)},{"label",QString::fromStdString(q.label)},
                {"pattern_isi",pattern},{"pattern_hash",QString::fromStdString(q.patternHash)},
                {"duration",q.duration},{"maximum_samples",double(q.maximumSamples)},
                {"reset_policy",q.resetPolicy==RecognitionResetPolicy::PerTrial?"reset_per_trial":"preserve_neuron_dynamics"}});
        }
        Artifact(rig.name+"_calibration_design.json",QJsonDocument(QJsonObject{{"kind","native_threshold_potential_fixture_design"},
            {"schema_version",2},{"run_id",QString::fromStdString(rig.name+"_frozen")},{"model_revision",package["model_revision"]},
            {"declared_trials",trialDesign},{"observation_schema_version",2},
            {"proposal_threshold_bounds",QJsonObject{{"minimum",1.e-6},{"maximum",1.}}},
            {"criterion",QJsonObject{{"id","post_anchor_target_whole_window_foil_v1"},{"anchor","last_stimulus"},
                {"begin_offset",0.},{"end_offset",QJsonValue(QJsonValue::Null)},{"reject_target_outside_window",true}}},
            {"primary_trial_ids",QJsonArray{"trial_0","trial_1"}},
            {"robustness_trial_ids",QJsonArray{"trial_2","trial_3"}},{"foil_rule","first_isi_preserved_remaining_isi_times_8"},
            {"calibration_scope","reset_per_trial"},{"record_threshold_potential",true}}).toJson());
        }
    }
    for(int i=0;i<4;++i)
    {
        auto request=make(i,i%2==1,i<2?RecognitionResetPolicy::PerTrial:RecognitionResetPolicy::PreserveNeuronDynamics);
        rig.learner->QueueNativeRecognitionTrial(request);
        EXPECT_THROW(rig.learner->QueueNativeRecognitionTrial(request),std::logic_error);
        std::optional<NativeRecognitionTrialObservation> result;
        std::vector<std::pair<double,double>> independentPotential;
        auto zone=rig.neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
        // The dispersed foil can exceed 10000 ticks at 20 kHz. Close the
        // declared physical window; a fixed tick cap changes the protocol.
        const auto requiredTicks=std::size_t(std::ceil(request.duration*rig.frequency))+2;
        ASSERT_LE(requiredTicks,request.maximumSamples+1);
        for(std::size_t n=0;n<requiredTicks && !result;++n)
        {
            const auto time=rig.environment->GetTime().GetDoubleTime();tick();
            if(recordThresholdPotential)independentPotential.emplace_back(time,zone->Potential.GetData());
            result=rig.learner->TakeNativeRecognitionTrialResult();
        }
        ASSERT_TRUE(result);Artifact(rig.name+"_frozen_trial_"+std::to_string(i)+".json",QJsonDocument(NativeRecognitionTrialJson(*result)).toJson());
        ASSERT_TRUE(result->valid)<<result->reason;EXPECT_TRUE(result->complete);EXPECT_TRUE(result->armed);
        EXPECT_EQ(result->stimulusTimes.size(),std::size_t(rig.inputCount));
        EXPECT_EQ(result->samples.size(),std::size_t(std::round(request.duration*rig.frequency))+1);
        EXPECT_EQ(result->modelBefore,frozen);EXPECT_EQ(result->modelAfter,frozen);
        if(recordThresholdPotential)
        {
            ASSERT_EQ(independentPotential.size(),result->samples.size());
            EXPECT_EQ(result->thresholdPotentialPath,"$.LTZone.Potential");
            EXPECT_EQ(result->thresholdPotentialClass,zone->GetCompClassName());
            for(std::size_t n=0;n<result->samples.size();++n)
            {
                EXPECT_DOUBLE_EQ(result->samples[n].time,independentPotential[n].first);
                EXPECT_DOUBLE_EQ(result->samples[n].thresholdPotential,independentPotential[n].second);
            }
            const auto json=NativeRecognitionTrialJson(*result);
            EXPECT_EQ(json["schema_version"],QJsonValue(2));
            EXPECT_TRUE(json["samples"].toArray().first().toObject().contains("lt_potential"));
        }
        observedSpikes+=result->spikeTimes.size();
        EXPECT_TRUE(NativeTrainingPatternEqual(rig.learner->InputPattern.GetData(),target));
        EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),package);
        EXPECT_THROW(rig.learner->QueueNativeRecognitionTrial(request),std::runtime_error);
        if(recorded)recorded->push_back(*result);
    }
    if(rig.name.find("spiking")!=std::string::npos)EXPECT_GT(observedSpikes,0u);
    auto cancelled=make(4,false,RecognitionResetPolicy::PerTrial);
    rig.learner->QueueNativeRecognitionTrial(cancelled);tick();
    rig.learner->CancelNativeRecognitionTrial("explicit_cancel");
    auto stopped=rig.learner->TakeNativeRecognitionTrialResult();ASSERT_TRUE(stopped);
    EXPECT_FALSE(stopped->valid);EXPECT_FALSE(stopped->complete);EXPECT_EQ(stopped->reason,"explicit_cancel");
    Artifact(rig.name+"_frozen_trial_cancelled.json",QJsonDocument(NativeRecognitionTrialJson(*stopped)).toJson());
    auto gap=make(5,false,RecognitionResetPolicy::PerTrial);rig.learner->QueueNativeRecognitionTrial(gap);tick();
    rig.environment->IncreaseModelTimeByStep();tick();
    auto dropped=rig.learner->TakeNativeRecognitionTrialResult();ASSERT_TRUE(dropped);
    EXPECT_FALSE(dropped->valid);EXPECT_FALSE(dropped->complete);EXPECT_EQ(dropped->reason,"recognition_sample_gap");
    Artifact(rig.name+"_frozen_trial_gap.json",QJsonDocument(NativeRecognitionTrialJson(*dropped)).toJson());
    EXPECT_TRUE(rig.learner->NativeModelEditFailure().empty());EXPECT_EQ(rig.Revision(),frozen);
}

void CalibrationAssessmentChecks(const std::string& name,
    const std::vector<NativeRecognitionTrialRequest>& expected,
    const std::vector<NativeRecognitionTrialObservation>& observations,const std::string& targetHash)
{
    ASSERT_EQ(expected.size(),4u);ASSERT_EQ(observations.size(),4u);
    const auto assessed=AssessNativeThresholdResponses(expected,observations,targetHash,CalibrationResponseWindow{});
    std::vector<NativeRecognitionTrialObservation> loaded;
    for(std::size_t i=0;i<expected.size();++i)
    {
        const auto encoded=NativeRecognitionTrialJson(observations[i]);
        const auto text=QJsonDocument(encoded).toJson(QJsonDocument::Compact).toStdString();
        loaded.push_back(ParseNativeRecognitionObservation(text,expected[i]));
        EXPECT_EQ(NativeRecognitionTrialJson(loaded.back()),encoded);
        auto changed=encoded;changed["spike_count"]=false;
        EXPECT_THROW(DecodeNativeRecognitionObservation(changed,expected[i]),std::invalid_argument);
        changed=encoded;changed["censored"]=true;
        EXPECT_THROW(DecodeNativeRecognitionObservation(changed,expected[i]),std::invalid_argument);
        changed=encoded;changed["unrecognized_claim"]=true;
        EXPECT_THROW(DecodeNativeRecognitionObservation(changed,expected[i]),std::invalid_argument);
        changed=encoded;changed.remove("relative_stimulus_times");
        EXPECT_THROW(DecodeNativeRecognitionObservation(changed,expected[i]),std::invalid_argument);
        changed=encoded;auto frames=changed["samples"].toArray();auto frame=frames[0].toObject();
        frame["soma"]=QJsonArray{QJsonValue(QJsonValue::Null)};frames[0]=frame;changed["samples"]=frames;
        EXPECT_THROW(DecodeNativeRecognitionObservation(changed,expected[i]),std::invalid_argument);
        auto other=expected[i];other.duration+=1./observations[i].frequencyHz;
        EXPECT_THROW(DecodeNativeRecognitionObservation(encoded,other),std::invalid_argument);
        other=expected[i];other.maximumSamples+=1;
        EXPECT_THROW(DecodeNativeRecognitionObservation(encoded,other),std::invalid_argument);
        EXPECT_THROW(ParseNativeRecognitionObservation(text,expected[i],text.size()-1),std::invalid_argument);
        const auto duplicated=std::string("{\"kind\":\"native_recognition_trial\",")+text.substr(1);
        EXPECT_THROW(ParseNativeRecognitionObservation(duplicated,expected[i]),std::invalid_argument);
    }
    EXPECT_EQ(AssessNativeThresholdResponses(expected,loaded,targetHash,CalibrationResponseWindow{}).evidence,assessed.evidence);
    Artifact(name+"_calibration_persistence.json",QJsonDocument(QJsonObject{
        {"kind","native_calibration_observation_roundtrip"},{"schema_version",1},
        {"trials",int(loaded.size())},{"assessment_sha256",assessed.evidence["sha256"]},
        {"equal",true},{"calibrated",false}}).toJson());
    if(name.find("_candidate_high")!=std::string::npos)
    {
        EXPECT_FALSE(assessed.criterionMet);EXPECT_EQ(assessed.targetViolations,2u);
        EXPECT_EQ(assessed.foilResponses,0u);
    }
    Artifact(name+"_calibration_assessment.json",QJsonDocument(assessed.evidence).toJson());
    std::vector<NativeRecognitionTrialRequest> primary(expected.begin(),expected.begin()+2);
    std::vector<NativeRecognitionTrialObservation> measured(observations.begin(),observations.begin()+2);
    const auto primaryResult=AssessNativeThresholdResponses(primary,measured,targetHash,CalibrationResponseWindow{});
    Artifact(name+"_primary_calibration_assessment.json",QJsonDocument(primaryResult.evidence).toJson());
    auto reordered=observations;std::reverse(reordered.begin(),reordered.end());
    EXPECT_EQ(AssessNativeThresholdResponses(expected,reordered,targetHash,CalibrationResponseWindow{}).evidence,assessed.evidence);
    // Corrupt real observations without changing the physical model or filling
    // missing samples from an expected waveform. The production validator must
    // reject even when the stale complete/valid flags are still true.
    auto damaged=observations;damaged[0].samples[0].somaPotentials[0]=std::numeric_limits<double>::quiet_NaN();
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;damaged[0].samples[0].spikeHistory.push_back(std::numeric_limits<double>::quiet_NaN());
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;
    if(damaged[0].spikeTimes.empty())damaged[0].spikeTimes.push_back(damaged[0].begin);else damaged[0].spikeTimes.pop_back();
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;damaged[0].stimulusTimes[0]+=2./damaged[0].frequencyHz;
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;damaged[0].samples.erase(damaged[0].samples.begin()+1);
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;auto extra=damaged[0].samples.front();extra.time+=.25/damaged[0].frequencyHz;
    damaged[0].samples.insert(damaged[0].samples.begin()+1,extra);
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;damaged[0].complete=false;
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    damaged=observations;damaged.pop_back();
    EXPECT_THROW(AssessNativeThresholdResponses(expected,damaged,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    auto wrong=expected;wrong[0].maximumSamples-=1;
    EXPECT_THROW(AssessNativeThresholdResponses(wrong,observations,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
    wrong=expected;std::swap(wrong[0],wrong[1]);
    EXPECT_THROW(AssessNativeThresholdResponses(wrong,observations,targetHash,CalibrationResponseWindow{}),std::invalid_argument);
}

template<class Learner> void RecognitionOwnerChecks(EditingRig<Learner>& rig,const QJsonObject& source,RecognitionCase scenario)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string implementation="native-learned-boundary-fixture-v1";
    const auto sourceCopy=source;NativeRecognitionSpec spec;
    const bool fresh=scenario==RecognitionCase::OwnedFreshIdentity || scenario==RecognitionCase::OwnedFreshScaled;
    auto trainingOwner=rig.learner;auto trainingNeuron=rig.neuron;auto trainingGenerator=rig.source;
    const auto trainingBefore=rig.Revision();
    if(scenario==RecognitionCase::OwnedScaled || scenario==RecognitionCase::OwnedClipped || scenario==RecognitionCase::OwnedFreshScaled)
    {
        spec.mode=RecognitionConversionMode::HistoricalBranchN1;
        for(const auto& p:rig.learner->ReadNativeParameters())
            spec.resistanceBounds.push_back(scenario==RecognitionCase::OwnedClipped?
                RecognitionResistanceBounds{1.5*p.resistance,1.5*p.resistance}:RecognitionResistanceBounds{1.e6,1.e12});
    }
    const auto package=ConvertNativeSoloToRecognition(source,spec,core.storage,core.environment,implementation);
    Artifact(rig.name+"_owner_recognition_state.json",QJsonDocument(package).toJson());
    auto reference=PrepareNativeRecognitionState(package,core.storage,core.environment,implementation);
    rig.learner->IsNeedToTrain=false;
    int beforeVersion=-1,beforeInputs=-1;
    if(fresh)
    {
        auto target=dynamic_pointer_cast<Learner>(core.storage->TakeObject(rig.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(target);
        ASSERT_NE(target.Get(),trainingOwner.Get());beforeVersion=target->ControllerVersion.GetData();beforeInputs=target->NumInputDendrite.GetData();
        EXPECT_EQ(beforeVersion,1);EXPECT_FALSE(target->ConfiguredModelInitialized.GetData());
        EXPECT_FALSE(target->HasNativeRecognitionState());EXPECT_FALSE(target->NativeTrainingController().Certificate());
        target->Name="RecognitionTestLearner";target->SetEnvironment(rig.environment);target->SetGlobalTimeStep(rig.frequency);
        UEPtr<UContainer> node=target;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);rig.learner=target;
    }
    const auto clock=rig.environment->GetTime().GetTime();
    auto refresh=[&] {
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    };
    auto installed=rig.learner->ImportNativeRecognitionState(package,implementation);
    Artifact(rig.name+"_owner_recognition_import.json",QJsonDocument(QJsonObject{
        {"kind","native_recognition_owner_import"},{"schema_version",1},{"status",NativeModelBuildStatusName(installed.status)},
        {"reason",QString::fromStdString(installed.reason)},{"model_may_have_changed",installed.modelMayHaveChanged},
        {"installed",rig.learner->HasNativeRecognitionState()},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;refresh();
    ASSERT_TRUE(rig.learner->HasNativeRecognitionState());EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
    EXPECT_EQ(rig.learner->ReadNativeParameters(),reference->parameters);
    EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());EXPECT_FALSE(rig.learner->NativeTrainingController().References());
    EXPECT_EQ(rig.learner->NativeTrainingController().State(),NativeTrainingState::Idle);
    EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());
    rig.learner->Build();rig.learner->Init();rig.learner->Reset();
    ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
    EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),package);
    EXPECT_THROW(rig.learner->ExportNativeLearnedState(implementation),std::logic_error);
    EXPECT_THROW(rig.learner->BeginNativeTraining(TrainingPlan(rig)),std::logic_error);
    EXPECT_THROW(rig.learner->QueueNativeProbe(NativeProbeRequest{}),std::logic_error);
    EXPECT_FALSE(rig.learner->SetIsNeedToTrain(true));EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());
    auto requested=reference->parameters;requested[0].resistance*=1.01;
    auto blocked=rig.learner->ApplyNativeParameters(requested);EXPECT_EQ(blocked.status,NativeEditStatus::Rejected);
    EXPECT_EQ(blocked.reason,"native_recognition_model_is_frozen");EXPECT_FALSE(blocked.modelMayHaveChanged);
    // Reinstall from the same immutable source package, never scale live Rs again.
    installed=rig.learner->ImportNativeRecognitionState(package,implementation);
    ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;refresh();
    rig.learner->Build();rig.learner->Init();rig.learner->Reset();
    EXPECT_EQ(rig.learner->ReadNativeParameters(),reference->parameters);
    auto forged=package;forged["recognition_certificate"]=source["certificate"];forged.remove("sha256");
    forged["sha256"]=NmsdkTools::CanonicalModelDataSha256(forged);
    const auto beforeReject=rig.Revision();const auto rejected=rig.learner->ImportNativeRecognitionState(forged,implementation);
    EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(rejected.modelMayHaveChanged);
    EXPECT_EQ(rig.Revision(),beforeReject);EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),package);
    reference->dataset->Name="RecognitionReferenceData";reference->neuron->Name="RecognitionReferenceNeuron";
    for(UEPtr<UContainer> node:{UEPtr<UContainer>(reference->dataset.Get()),UEPtr<UContainer>(reference->neuron.Get())})
    {ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);node->Init();node->Reset();}
    auto other=reference->dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(other);
    auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
    dataset->StateGeneration=1;reference->dataset->StateGeneration=1;
    const double begin=rig.environment->GetTime().GetDoubleTime(),end=begin+rig.duration+.01;
    const auto channels=rig.branch?1u:rig.inputCount;const auto frames=unsigned(std::ceil((rig.duration+.01)*rig.frequency))+3;
    std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus_a,stimulus_b";
    for(std::size_t i=0;i<channels;++i)trace<<",soma_a"<<i<<",soma_b"<<i;trace<<'\n';
    const auto frozenBefore=rig.Revision();const auto trial=rig.name+"/owned-recognition";
    Artifact(rig.name+"_owner_recognition_probe_spec.json",QJsonDocument(QJsonObject{
        {"kind","native_recognition_frozen_probe"},{"schema_version",1},{"run_id",QString::fromStdString(rig.name)},
        {"trial_id",QString::fromStdString(trial)},{"model_revision",package["model_revision"]},
        {"pattern_hash",source["protocol"].toObject()["pattern_hash"]},{"begin",begin},{"end",end},
        {"maximum_sample_gap",1./rig.frequency},{"maximum_samples",double(frames)},{"channels",double(channels)},
        {"record_spikes",false},{"measurement","paired_soma_transport"}}).toJson());
    bool complete=false,emitted=false;unsigned samples=0;double last=begin,variation=0.,maximum=0.;
    std::vector<double> low(channels,std::numeric_limits<double>::infinity()),high(channels,-std::numeric_limits<double>::infinity());
    for(unsigned tick=0;tick<frames;++tick)
    {
        rig.model->Calculate();last=rig.environment->GetTime().GetDoubleTime();
        ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
        const double a=rig.source->Output(0,0),b=other->Output(0,0);EXPECT_DOUBLE_EQ(a,b);emitted=emitted || a>0.;
        trace<<last<<','<<a<<','<<b;
        for(std::size_t i=0;i<channels;++i)
        {
            const auto path="Soma"+std::to_string(i+1);auto x=rig.neuron->template GetComponentL<NPulseMembrane>(path,true);
            auto y=reference->neuron->template GetComponentL<NPulseMembrane>(path,true);ASSERT_TRUE(x);ASSERT_TRUE(y);
            const double va=x->SumPotential(0,0),vb=y->SumPotential(0,0);EXPECT_DOUBLE_EQ(va,vb);
            maximum=std::max(maximum,std::fabs(va));
            low[i]=std::min(low[i],va);high[i]=std::max(high[i],va);trace<<','<<va<<','<<vb;
        }
        trace<<'\n';++samples;rig.environment->IncreaseModelTimeByStep();if(!Detail::After(end,last)){complete=true;break;}
    }
    for(std::size_t i=0;i<channels;++i)variation=std::max(variation,high[i]-low[i]);
    EXPECT_TRUE(complete);EXPECT_TRUE(emitted);EXPECT_GT(variation,1.e-6);
    const auto frozenAfter=rig.Revision();
    const auto referenceAfter=NmsdkTools::IdentifyModel(reference->neuron,{{&other->Output,"burst"}})["sha256"].toString().toStdString();
    EXPECT_EQ(frozenBefore,package["model_revision"].toString().toStdString());EXPECT_EQ(frozenAfter,frozenBefore);EXPECT_EQ(referenceAfter,frozenBefore);
    EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),package);EXPECT_EQ(source,sourceCopy);
    EXPECT_EQ(rig.learner->NativeTrainingController().State(),NativeTrainingState::Idle);
    EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());
    Artifact(rig.name+"_owner_recognition_wave.csv",QByteArray::fromStdString(trace.str()));
    Artifact(rig.name+"_owner_recognition_observation.json",QJsonDocument(QJsonObject{
        {"kind","native_recognition_owner_observation"},{"schema_version",2},{"model_revision",package["model_revision"]},
        {"source_solo_revision",source["model_revision"]},{"source_solo_sha256",source["sha256"]},
        {"begin",begin},{"end",end},{"last_sample_time",last},{"maximum_sample_gap",1./rig.frequency},
        {"sample_count",double(samples)},{"channels",double(channels)},{"inputs",double(rig.inputCount)},
        {"trial_id",QString::fromStdString(trial)},{"frozen_before",QString::fromStdString(frozenBefore)},
        {"frozen_after_owner",QString::fromStdString(frozenAfter)},{"frozen_after_reference",QString::fromStdString(referenceAfter)},
        {"maximum_soma",maximum},{"need",rig.learner->IsNeedToTrain.GetData()},
        {"complete",complete},{"emitted",emitted},{"soma_variation",variation},{"record_spikes",false},
        {"recognition_certificate",QJsonValue(QJsonValue::Null)},
        {"training_controller_installed",bool(rig.learner->NativeTrainingController().Certificate()) ||
            bool(rig.learner->NativeTrainingController().References()) || rig.learner->NativeTrainingController().State()!=NativeTrainingState::Idle},
        {"rejected_certificate_reason",QString::fromStdString(rejected.reason)},
        {"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    if(fresh)
    {
        const auto trainingAfter=NmsdkTools::IdentifyModel(trainingNeuron,{{&trainingGenerator->Output,"burst"}})["sha256"].toString().toStdString();
        EXPECT_EQ(trainingBefore,trainingAfter);EXPECT_EQ(source,sourceCopy);
        Artifact(rig.name+"_owner_recognition_transfer.json",QJsonDocument(QJsonObject{
            {"kind","native_recognition_fresh_owner_transfer"},{"schema_version",1},
            {"source_owner",QString::fromStdString(trainingOwner->GetName())},{"test_owner",QString::fromStdString(rig.learner->GetName())},
            {"distinct_owners",trainingOwner.Get()!=rig.learner.Get()},{"target_controller_version_before",beforeVersion},
            {"target_inputs_before",beforeInputs},{"target_controller_version_after",rig.learner->ControllerVersion.GetData()},
            {"target_inputs_after",rig.learner->NumInputDendrite.GetData()},
            {"source_model_before",QString::fromStdString(trainingBefore)},{"source_model_after",QString::fromStdString(trainingAfter)},
            {"target_model",QString::fromStdString(frozenAfter)},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    }
    if(fresh)FrozenTrialChecks(rig,package);
    // A direct physical edit is discovered before the next child calculation.
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);
    channel->Capacity=channel->Capacity.GetData()*1.01;rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    EXPECT_EQ(rig.learner->NativeModelEditFailure(),"native_recognition_model_changed");
    EXPECT_THROW(rig.learner->ExportNativeRecognitionState(implementation),std::logic_error);
    Artifact(rig.name+"_owner_recognition_guard.json",QJsonDocument(QJsonObject{
        {"kind","native_recognition_owner_guard"},{"schema_version",1},{"physical_edit_detected",!rig.learner->NativeModelEditFailure().empty()},
        {"reason",QString::fromStdString(rig.learner->NativeModelEditFailure())},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}

template<class Learner> void ThresholdCandidateChecks(EditingRig<Learner>& rig,const QJsonObject& solo,bool recordThresholdPotential=false,bool finalizeCalibration=false)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string implementation="native-learned-boundary-fixture-v1";
    const auto source=ConvertNativeSoloToRecognition(solo,NativeRecognitionSpec{},core.storage,core.environment,implementation);
    const auto sourceCopy=source;const auto original=rig.Revision();
    Artifact(rig.name+"_threshold_source.json",QJsonDocument(source).toJson());
    for(double invalid:{std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
        EXPECT_THROW(CreateNativeThresholdCandidate(source,invalid,core.storage,core.environment,implementation),std::invalid_argument);
    for(double finiteThreshold:{0.,-1.})
    {
        const auto clock=rig.environment->GetTime().GetTime();
        const auto signedCandidate=CreateNativeThresholdCandidate(source,finiteThreshold,core.storage,core.environment,implementation);
        auto prepared=PrepareNativeRecognitionState(signedCandidate,core.storage,core.environment,implementation);
        auto zone=prepared->neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
        EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),finiteThreshold);EXPECT_EQ(source,sourceCopy);
        EXPECT_EQ(rig.Revision(),original);
        EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
        Artifact(rig.name+(finiteThreshold==0.?"_numeric_domain_zero_candidate.json":"_numeric_domain_negative_candidate.json"),
            QJsonDocument(signedCandidate).toJson());
    }
    const auto baseName=rig.name;
    std::optional<NativeThresholdProposal> pendingProposal;
    for(double threshold:{1.e-4,1.})
    {
        const auto candidateClock=rig.environment->GetTime().GetTime();
        const auto candidate=CreateNativeThresholdCandidate(source,threshold,core.storage,core.environment,implementation);
        EXPECT_EQ(source,sourceCopy);EXPECT_EQ(rig.environment->GetTime().GetTime(),candidateClock);
        // The source learner has not been replaced or calculated by construction.
        if(threshold==1.e-4)EXPECT_EQ(rig.Revision(),original);
        const auto repeated=CreateNativeThresholdCandidate(source,threshold,core.storage,core.environment,implementation);
        EXPECT_EQ(candidate,repeated);
        if(threshold==1.e-4)
        {
            auto legacy=candidate;auto legacyRecord=legacy["candidate_record"].toObject();
            legacyRecord["algorithm"]="explicit-native-threshold-v1";legacy["candidate_record"]=legacyRecord;
            auto archive=legacy["neuron"].toObject();auto metadata=archive["metadata"].toObject();
            auto calibration=metadata["calibration"].toObject();calibration["candidate_record"]=legacyRecord;
            metadata["calibration"]=calibration;archive["metadata"]=metadata;archive.remove("sha256");
            archive["sha256"]=NmsdkTools::CanonicalModelDataSha256(archive);legacy["neuron"]=archive;
            legacy.remove("sha256");legacy["sha256"]=NmsdkTools::CanonicalModelDataSha256(legacy);
            auto loaded=PrepareNativeRecognitionState(legacy,core.storage,core.environment,implementation);
            EXPECT_EQ(loaded->modelRevision,candidate["model_revision"].toString().toStdString());
            Artifact(baseName+"_legacy_v1_candidate.json",QJsonDocument(legacy).toJson());
        }
        EXPECT_THROW(CreateNativeThresholdCandidate(candidate,threshold,core.storage,core.environment,implementation),std::invalid_argument);
        auto forged=candidate;auto record=forged["candidate_record"].toObject();record["calibrated"]=true;forged["candidate_record"]=record;
        forged.remove("sha256");forged["sha256"]=NmsdkTools::CanonicalModelDataSha256(forged);
        EXPECT_THROW(PrepareNativeRecognitionState(forged,core.storage,core.environment,implementation),std::invalid_argument);
        rig.learner->IsNeedToTrain=false;
        const auto installed=rig.learner->ImportNativeRecognitionState(candidate,implementation);
        ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
        rig.learner->Build();rig.learner->Init();rig.learner->Reset();
        ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
        auto zone=rig.neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
        EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),threshold);
        EXPECT_EQ(rig.Revision(),candidate["model_revision"].toString().toStdString());
        EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());
        rig.name=baseName+(threshold<.001?(!recordThresholdPotential && rig.frequency==2000?"_candidate_spiking":"_candidate_low"):"_candidate_high");
        Artifact(rig.name+"_recognition_candidate.json",QJsonDocument(candidate).toJson());
        std::vector<NativeRecognitionTrialRequest> declared;
        std::vector<NativeRecognitionTrialObservation> observations;
        FrozenTrialChecks(rig,candidate,recordThresholdPotential,&declared,&observations);
        const auto trainingHash=solo["protocol"].toObject()["pattern_hash"].toString().toStdString();
        CalibrationAssessmentChecks(rig.name,declared,observations,trainingHash);
        if(recordThresholdPotential && threshold==1.)
        {
            const auto hash=solo["protocol"].toObject()["pattern_hash"].toString().toStdString();
            ASSERT_EQ(observations.size(),4u);ASSERT_EQ(declared.size(),4u);
            std::vector<NativeRecognitionTrialRequest> primary(declared.begin(),declared.begin()+2);
            std::vector<NativeRecognitionTrialObservation> measured(observations.begin(),observations.begin()+2);
            const auto proposal=ProposeNativeThreshold(primary,measured,hash,CalibrationResponseWindow{},1.e-6,1.);
            pendingProposal=proposal;
            Artifact(baseName+"_threshold_proposal.json",QJsonDocument(proposal.evidence).toJson());
            const auto signedBounds=ProposeNativeThreshold(primary,measured,hash,CalibrationResponseWindow{},-.1,1.);
            Artifact(baseName+"_signed_bounds_threshold_proposal.json",QJsonDocument(signedBounds.evidence).toJson());
            std::reverse(measured.begin(),measured.end());
            EXPECT_EQ(ProposeNativeThreshold(primary,measured,hash,CalibrationResponseWindow{},1.e-6,1.).evidence,proposal.evidence);
            if(proposal.threshold)
            {
                const auto atBound=ProposeNativeThreshold(primary,measured,hash,CalibrationResponseWindow{},*proposal.threshold,*proposal.threshold);
                ASSERT_TRUE(atBound.threshold);EXPECT_DOUBLE_EQ(*atBound.threshold,*proposal.threshold);
            }
            auto damaged=measured;damaged[0].samples[0].thresholdPotential=std::numeric_limits<double>::quiet_NaN();
            EXPECT_THROW(ProposeNativeThreshold(primary,damaged,hash,CalibrationResponseWindow{},1.e-6,1.),std::invalid_argument);
            damaged=measured;damaged[0].spikeTimes.push_back(damaged[0].begin);
            EXPECT_THROW(ProposeNativeThreshold(primary,damaged,hash,CalibrationResponseWindow{},1.e-6,1.),std::invalid_argument);
            measured.pop_back();EXPECT_THROW(ProposeNativeThreshold(primary,measured,hash,CalibrationResponseWindow{},1.e-6,1.),std::invalid_argument);
        }
        EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),candidate);
        EXPECT_EQ(source,sourceCopy);
    }
    rig.name=baseName;
    if(pendingProposal && pendingProposal->threshold)
    {
        const auto candidate=CreateNativeThresholdCandidate(source,*pendingProposal->threshold,core.storage,core.environment,implementation);
        Artifact(baseName+"_proposal_candidate.json",QJsonDocument(candidate).toJson());
        Artifact(baseName+"_proposal_protocol.json",QJsonDocument(QJsonObject{
            {"kind","native_threshold_proposal_execution"},{"schema_version",1},
            {"source_recognition_sha256",source["sha256"]},{"proposal_sha256",pendingProposal->evidence["sha256"]},
            {"candidate_sha256",candidate["sha256"]},{"primary_policy","reset_per_trial"},
            {"search_run_id",QString::fromStdString(baseName+"_proposal_search_frozen")},
            {"confirmation_run_id",QString::fromStdString(baseName+"_proposal_confirmation_frozen")},
            {"confirmation_policy","fresh_native_import_from_same_source"},
            {"final_state_policy","restore_original_recognition"},{"calibrated",false}}).toJson());
        NativeCalibrationMatrix search,confirmation;
        for(const std::string phase:{"proposal_search","proposal_confirmation"})
        {
            // Reconstruct both runs separately through production import.
            // There is no parameter overlay on the previous live graph.
            const auto rebuilt=CreateNativeThresholdCandidate(source,*pendingProposal->threshold,core.storage,core.environment,implementation);
            ASSERT_EQ(rebuilt,candidate);
            const auto imported=rig.learner->ImportNativeRecognitionState(rebuilt,implementation);
            ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
            rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
            rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
            rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
            rig.learner->Build();rig.learner->Init();rig.learner->Reset();
            rig.name=baseName+"_"+phase;
            std::vector<NativeRecognitionTrialRequest> requests;
            std::vector<NativeRecognitionTrialObservation> observations;
            FrozenTrialChecks(rig,candidate,true,&requests,&observations);
            CalibrationAssessmentChecks(rig.name,requests,observations,solo["protocol"].toObject()["pattern_hash"].toString().toStdString());
            auto& matrix=phase=="proposal_search"?search:confirmation;
            matrix.requests.assign(requests.begin(),requests.begin()+2);
            matrix.observations.assign(observations.begin(),observations.begin()+2);
        }
        if(finalizeCalibration)
        {
            NativeThresholdConfirmationSpec specification;
            specification.dataPartitionId="explicit-primary-pair";specification.attemptId=baseName;
            specification.clockId=baseName+"/same-native-clock";
            const auto time=rig.environment->GetTime().GetTime();
            const auto calibrated=CreateNativeCalibratedState(candidate,specification,search,confirmation,core.storage,core.environment,implementation);
            EXPECT_EQ(rig.environment->GetTime().GetTime(),time);
            EXPECT_EQ(calibrated["model_revision"],candidate["model_revision"]);
            Artifact(baseName+"_calibrated_state.json",QJsonDocument(calibrated).toJson());
            auto replay=confirmation;replay.requests=search.requests;replay.observations=search.observations;
            EXPECT_THROW(CreateNativeCalibratedState(candidate,specification,search,replay,core.storage,core.environment,implementation),std::invalid_argument);
            auto changed=confirmation;changed.requests[0].duration+=1./rig.frequency;
            EXPECT_THROW(CreateNativeCalibratedState(candidate,specification,search,changed,core.storage,core.environment,implementation),std::invalid_argument);
            changed=confirmation;
            for(auto& observation:changed.observations)observation.thresholdPotentialPath="$.WrongZone.Potential";
            EXPECT_THROW(CreateNativeCalibratedState(candidate,specification,search,changed,core.storage,core.environment,implementation),std::invalid_argument);
            changed=confirmation;
            for(auto& observation:changed.observations)for(auto& sample:observation.samples)sample.somaPotentials.push_back(0.);
            EXPECT_THROW(CreateNativeCalibratedState(candidate,specification,search,changed,core.storage,core.environment,implementation),std::invalid_argument);
            changed=confirmation;
            for(auto& observation:changed.observations)if(observation.request.label=="target")
            {
                observation.spikeTimes.clear();for(auto& sample:observation.samples)sample.spikeHistory.clear();
            }
            EXPECT_THROW(CreateNativeCalibratedState(candidate,specification,search,changed,core.storage,core.environment,implementation),std::invalid_argument);
            auto prepared=PrepareNativeRecognitionState(calibrated,core.storage,core.environment,implementation);
            EXPECT_TRUE(prepared->calibrationConfirmed);EXPECT_EQ(prepared->modelRevision,rig.Revision());
            auto imported=rig.learner->ImportNativeRecognitionState(calibrated,implementation);
            ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
            rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
            rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
            rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
            rig.learner->Build();rig.learner->Init();rig.learner->Reset();
            EXPECT_DOUBLE_EQ(rig.learner->CalibratedFixedLTZThreshold.GetData(),*pendingProposal->threshold);
            EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),calibrated);
            EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());
            auto damaged=calibrated;auto proof=damaged["calibration_proof"].toObject();
            proof["grid_selection_verified"]=true;proof.remove("sha256");proof["sha256"]=NmsdkTools::CanonicalModelDataSha256(proof);
            damaged["calibration_proof"]=proof;damaged.remove("sha256");damaged["sha256"]=NmsdkTools::CanonicalModelDataSha256(damaged);
            const auto rejected=rig.learner->ImportNativeRecognitionState(damaged,implementation);
            EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(rejected.modelMayHaveChanged);
            EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),calibrated);
            rig.name=baseName+"_calibrated";
            FrozenTrialChecks(rig,calibrated,true);
            EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),calibrated);
        }
    }
    else if(finalizeCalibration)FAIL()<<"required primary-pair calibration control produced no candidate";
    if(recordThresholdPotential)
    {
        const auto restored=rig.learner->ImportNativeRecognitionState(source,implementation);
        ASSERT_EQ(restored.status,NativeModelBuildStatus::Adopted)<<restored.reason;
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
        rig.learner->Build();rig.learner->Init();rig.learner->Reset();
        EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
        EXPECT_EQ(rig.Revision(),source["model_revision"].toString().toStdString());
        rig.name=baseName;
        Artifact(baseName+"_proposal_restoration.json",QJsonDocument(QJsonObject{
            {"kind","native_threshold_proposal_restoration"},{"schema_version",1},{"model_revision",source["model_revision"]},
            {"source_recognition_sha256",source["sha256"]},{"restored",true},{"calibrated",false}}).toJson());
    }
}

template<class Learner> void RecognitionChecks(EditingRig<Learner>& rig,const QJsonObject& source,RecognitionCase scenario)
{
    if(scenario==RecognitionCase::ThresholdCandidates){ThresholdCandidateChecks(rig,source);return;}
    if(scenario==RecognitionCase::ThresholdPotential){ThresholdCandidateChecks(rig,source,true);return;}
    if(scenario==RecognitionCase::CalibratedThreshold){ThresholdCandidateChecks(rig,source,true,true);return;}
    if(scenario==RecognitionCase::OwnedIdentity || scenario==RecognitionCase::OwnedScaled || scenario==RecognitionCase::OwnedClipped ||
       scenario==RecognitionCase::OwnedFreshIdentity || scenario==RecognitionCase::OwnedFreshScaled)
    {RecognitionOwnerChecks(rig,source,scenario);return;}
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string implementation="native-learned-boundary-fixture-v1";
    const auto original=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();
    const auto sourceCopy=source;const auto clock=rig.environment->GetTime().GetTime();NativeRecognitionSpec spec;
    if(scenario!=RecognitionCase::Identity)
    {
        spec.mode=RecognitionConversionMode::HistoricalBranchN1;
        for(std::size_t i=0;i<parameters.size();++i)
        {
            const auto& p=parameters[i];const double fixed=p.resistance*(scenario==RecognitionCase::SharedConflict?1.1+.1*double(i):1.5);
            spec.resistanceBounds.push_back(scenario==RecognitionCase::Clipped || scenario==RecognitionCase::SharedConflict?
                RecognitionResistanceBounds{fixed,fixed}:RecognitionResistanceBounds{1.e6,1.e12});
        }
    }
    if(scenario==RecognitionCase::SharedConflict)
    {
        ASSERT_GT(parameters.size(),1u);EXPECT_EQ(parameters[0].length,parameters[1].length);
        std::string reason;try {ConvertNativeSoloToRecognition(source,spec,core.storage,core.environment,implementation);}
        catch(const std::exception& error){reason=error.what();}
        EXPECT_EQ(reason,"shared_recognition_bank_conflict");
        EXPECT_EQ(source,sourceCopy);EXPECT_EQ(rig.Revision(),original);EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
        EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
        Artifact(rig.name+"_recognition_rejected.json",QJsonDocument(QJsonObject{{"reason",QString::fromStdString(reason)},
            {"source_sha256",source["sha256"]},{"source_revision",source["model_revision"]},{"source_unchanged",rig.Revision()==original}}).toJson());
        return;
    }
    const auto recognition=ConvertNativeSoloToRecognition(source,spec,core.storage,core.environment,implementation);
    const auto repeated=ConvertNativeSoloToRecognition(source,spec,core.storage,core.environment,implementation);
    EXPECT_EQ(recognition["model_revision"],repeated["model_revision"]);EXPECT_EQ(recognition["conversion_record"],repeated["conversion_record"]);
    EXPECT_EQ(source,sourceCopy);EXPECT_EQ(rig.Revision(),original);EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    EXPECT_EQ(rig.environment->GetTime().GetTime(),clock)<<"conversion/import must not calculate the physical tree";
    EXPECT_TRUE(recognition["recognition_certificate"].isNull());
    const auto metadata=recognition["neuron"].toObject()["metadata"].toObject();
    EXPECT_EQ(metadata["training"].toObject()["certificate"].toObject()["state_identity"],source["model_revision"]);
    EXPECT_EQ(metadata["recognition_verification"].toObject()["status"],QJsonValue("unverified"));
    EXPECT_TRUE(metadata["recognition_verification"].toObject()["certificate"].isNull());
    EXPECT_EQ(ParseNativeRecognitionState(QJsonDocument(recognition).toJson(QJsonDocument::Compact).toStdString()),recognition);
    if(scenario==RecognitionCase::Identity || parameters.size()==1)EXPECT_EQ(recognition["model_revision"],source["model_revision"]);
    else EXPECT_NE(recognition["model_revision"],source["model_revision"]);
    const auto decisions=recognition["conversion_record"].toObject()["decisions"].toArray();ASSERT_EQ(decisions.size(),int(parameters.size()));
    if(scenario!=RecognitionCase::Identity && parameters.size()>1)
    {
        EXPECT_DOUBLE_EQ(decisions[0].toObject()["factor"].toDouble(),2.);
        if(scenario==RecognitionCase::Clipped)EXPECT_TRUE(decisions[0].toObject()["clipped"].toBool());
    }
    Artifact(rig.name+"_recognition_state.json",QJsonDocument(recognition).toJson());
    auto a=PrepareNativeRecognitionState(recognition,core.storage,core.environment,implementation);
    auto b=PrepareNativeRecognitionState(recognition,core.storage,core.environment,implementation);
    ASSERT_TRUE(a->neuron);ASSERT_TRUE(b->neuron);EXPECT_EQ(a->parameters,b->parameters);
    EXPECT_EQ(a->modelRevision,recognition["model_revision"].toString().toStdString());
    const auto signedPackage=[](QJsonObject value) {value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;};
    auto forged=recognition;forged["recognition_certificate"]=source["certificate"];
    EXPECT_THROW(PrepareNativeRecognitionState(signedPackage(forged),core.storage,core.environment,implementation),std::exception);
    forged=recognition;auto record=forged["conversion_record"].toObject();auto changed=record["decisions"].toArray();
    auto first=changed[0].toObject();first["applied_resistance"]=first["applied_resistance"].toDouble()*1.1;changed[0]=first;
    record["decisions"]=changed;forged["conversion_record"]=record;
    EXPECT_THROW(PrepareNativeRecognitionState(signedPackage(forged),core.storage,core.environment,implementation),std::exception);
    EXPECT_THROW(ConvertNativeSoloToRecognition(recognition,spec,core.storage,core.environment,implementation),std::invalid_argument);
    EXPECT_EQ(rig.Revision(),original);EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
    const auto sourceFor=[](const auto& state){return state->dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);};
    auto sourceA=sourceFor(a),sourceB=sourceFor(b);ASSERT_TRUE(sourceA);ASSERT_TRUE(sourceB);
    a->dataset->Name="RecognitionDataA";a->neuron->Name="RecognitionNeuronA";
    b->dataset->Name="RecognitionDataB";b->neuron->Name="RecognitionNeuronB";
    for(UEPtr<UContainer> node:{UEPtr<UContainer>(a->dataset.Get()),UEPtr<UContainer>(a->neuron.Get()),
                             UEPtr<UContainer>(b->dataset.Get()),UEPtr<UContainer>(b->neuron.Get())})
    {ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);node->Init();node->Reset();}
    const auto revision=[&](const auto& state,const auto& stimulus){return NmsdkTools::IdentifyModel(state->neuron,{{&stimulus->Output,"burst"}}).value("sha256");};
    EXPECT_EQ(revision(a,sourceA),recognition["model_revision"]);EXPECT_EQ(revision(b,sourceB),recognition["model_revision"]);
    a->dataset->StateGeneration=1;b->dataset->StateGeneration=1;
    std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus_a,stimulus_b";
    const auto somas=rig.branch?1u:rig.inputCount;for(std::size_t i=0;i<somas;++i)trace<<",soma_a"<<i<<",soma_b"<<i;trace<<'\n';
    const double begin=rig.environment->GetTime().GetDoubleTime(),end=begin+rig.duration+.01;
    const unsigned maximumFrames=unsigned(std::ceil((rig.duration+.01)*rig.frequency))+3;
    const QJsonObject frozenSpec{{"kind","native_recognition_frozen_probe"},{"schema_version",1},
        {"run_id",QString::fromStdString(rig.name)},{"trial_id",QString::fromStdString(rig.name+"/roundtrip")},
        {"model_revision",recognition["model_revision"]},{"pattern_hash",source["protocol"].toObject()["pattern_hash"]},
        {"begin",begin},{"end",end},{"maximum_sample_gap",1./rig.frequency},{"maximum_samples",double(maximumFrames)},
        {"channels",double(somas)},{"record_spikes",false},{"measurement","paired_soma_transport"}};
    Artifact(rig.name+"_recognition_probe_spec.json",QJsonDocument(frozenSpec).toJson());
    bool emitted=false,complete=false;double maximum=0.,lastTime=begin;unsigned samples=0;
    std::vector<double> minimumPotential(somas,std::numeric_limits<double>::infinity());
    std::vector<double> maximumPotential(somas,-std::numeric_limits<double>::infinity());
    for(unsigned tick=0;tick<maximumFrames;++tick)
    {
        rig.model->Calculate();const double time=rig.environment->GetTime().GetDoubleTime();
        const double x=sourceA->Output(0,0),y=sourceB->Output(0,0);EXPECT_DOUBLE_EQ(x,y);emitted=emitted || x>0.;trace<<time<<','<<x<<','<<y;
        for(std::size_t i=0;i<somas;++i)
        {
            const auto path="Soma"+std::to_string(i+1);auto sa=a->neuron->template GetComponentL<NPulseMembrane>(path,true);
            auto sb=b->neuron->template GetComponentL<NPulseMembrane>(path,true);ASSERT_TRUE(sa);ASSERT_TRUE(sb);
            const double va=sa->SumPotential(0,0),vb=sb->SumPotential(0,0);EXPECT_DOUBLE_EQ(va,vb);
            minimumPotential[i]=std::min(minimumPotential[i],va);maximumPotential[i]=std::max(maximumPotential[i],va);
            maximum=std::max(maximum,std::fabs(va));trace<<','<<va<<','<<vb;
        }
        trace<<'\n';lastTime=time;++samples;rig.environment->IncreaseModelTimeByStep();
        if(!Detail::After(end,time)){complete=true;break;}
    }
    double variation=0.;for(std::size_t i=0;i<somas;++i)variation=std::max(variation,maximumPotential[i]-minimumPotential[i]);
    EXPECT_TRUE(complete);EXPECT_TRUE(emitted);EXPECT_GT(variation,1.e-6)<<"a constant rest potential cannot prove waveform roundtrip";
    EXPECT_EQ(revision(a,sourceA),recognition["model_revision"]);EXPECT_EQ(revision(b,sourceB),recognition["model_revision"]);
    Artifact(rig.name+"_recognition_roundtrip.csv",QByteArray::fromStdString(trace.str()));
    Artifact(rig.name+"_recognition_roundtrip.json",QJsonDocument(QJsonObject{{"kind","native_recognition_roundtrip_observation"},{"schema_version",1},
        {"model_revision",recognition["model_revision"]},{"trial_id",frozenSpec["trial_id"]},{"complete",complete},
        {"sample_count",double(samples)},{"last_sample_time",lastTime},{"emitted",emitted},{"maximum_soma",maximum},
        {"soma_variation",variation},
        {"frozen_after",revision(a,sourceA)},{"frozen_after_b",revision(b,sourceB)},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}

TEST(NativeRecognitionState,FreshProcessImport)
{
    const auto input=std::getenv("TIMELEARNER_RECOGNITION_IMPORT");
    if(!input)GTEST_SKIP()<<"Executed by immutable recognition replay job in a fresh process";
    const auto specification=std::getenv("TIMELEARNER_RECOGNITION_SPEC");ASSERT_TRUE(specification);
    const auto output=std::getenv("TIMELEARNER_RECOGNITION_OUTPUT");ASSERT_TRUE(output);
    QFile file(QString::fromLocal8Bit(input));ASSERT_TRUE(file.open(QIODevice::ReadOnly));
    const auto package=ParseNativeRecognitionState(file.readAll().toStdString());
    QFile specFile(QString::fromLocal8Bit(specification));ASSERT_TRUE(specFile.open(QIODevice::ReadOnly));
    QJsonParseError parseError;const auto document=QJsonDocument::fromJson(specFile.readAll(),&parseError);
    ASSERT_EQ(parseError.error,QJsonParseError::NoError);ASSERT_TRUE(document.isObject());const auto spec=document.object();
    ASSERT_EQ(spec["schema_version"],QJsonValue(1));ASSERT_EQ(spec["kind"],QJsonValue("native_recognition_frozen_probe"));
    ASSERT_EQ(spec["measurement"],QJsonValue("paired_soma_transport"));ASSERT_EQ(spec["record_spikes"],QJsonValue(false));
    ASSERT_EQ(spec["model_revision"],package["model_revision"]);
    const auto sourceSolo=package["source_solo"].toObject();
    ASSERT_EQ(spec["pattern_hash"],sourceSolo["protocol"].toObject()["pattern_hash"]);
    const auto configuration=DecodeConfiguredNativeTraining(sourceSolo["configuration"].toObject());
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    EXPECT_FALSE(core.storage->CheckClass(configuration.model.neuronClass));
    core.environment->SetUseIndTimeStepFlag(false);core.environment->DestroyModel();
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();
    model->SetGlobalTimeStep(configuration.model.frequencyHz);
    // Generator Reset captures the current clock. Set the declared onset before
    // importing/initializing the physical tree, never after its Reset.
    const double begin=spec["begin"].toDouble(-1.),end=spec["end"].toDouble(-1.);
    ASSERT_TRUE(std::isfinite(begin) && std::isfinite(end) && begin>=0. && end>begin);
    const auto beginUs=std::llround(begin*1.e6);ASSERT_GE(beginUs,0);
    core.environment->GetTime().SetTime(static_cast<unsigned long long>(beginUs));
    ASSERT_FALSE(Detail::After(begin,core.environment->GetTime().GetDoubleTime()));
    ASSERT_FALSE(Detail::After(core.environment->GetTime().GetDoubleTime(),begin));
    auto state=PrepareNativeRecognitionState(package,core.storage,core.environment,"native-learned-boundary-fixture-v1");
    ASSERT_TRUE(state->neuron);ASSERT_TRUE(state->dataset);
    auto generator=state->dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
    state->dataset->Name="RecognitionReplayData";state->neuron->Name="RecognitionReplayNeuron";
    for(UEPtr<UContainer> node:{UEPtr<UContainer>(state->dataset.Get()),UEPtr<UContainer>(state->neuron.Get())})
    {ASSERT_NE(model->AddComponent(node),ForbiddenId);}
    // The fresh root has no initialized parent fixture. Initialize the complete
    // tree natively; initializing its children alone does not arm its scheduler.
    model->Init();model->Reset();ASSERT_TRUE(model->IsInit());
    const auto revision=[&]{return NmsdkTools::IdentifyModel(state->neuron,{{&generator->Output,"burst"}}).value("sha256");};
    ASSERT_EQ(revision(),package["model_revision"]);
    const auto channels=configuration.model.branch?1u:configuration.model.inputs.size();
    ASSERT_EQ(spec["channels"].toDouble(),double(channels));
    ASSERT_DOUBLE_EQ(spec["maximum_sample_gap"].toDouble(),1./configuration.model.frequencyHz);
    const double budget=spec["maximum_samples"].toDouble();
    ASSERT_TRUE(std::isfinite(budget) && budget>=1. && budget==std::floor(budget) && budget<=1000000.);
    state->dataset->StateGeneration=1;
    std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
    for(std::size_t i=0;i<channels;++i)trace<<",soma"<<i;trace<<'\n';
    bool complete=false,emitted=false;unsigned samples=0;double lastTime=begin,variation=0.;
    std::vector<double> low(channels,std::numeric_limits<double>::infinity()),high(channels,-std::numeric_limits<double>::infinity());
    for(unsigned tick=0;tick<unsigned(budget);++tick)
    {
        model->Calculate();const double time=core.environment->GetTime().GetDoubleTime(),stimulus=generator->Output(0,0);
        ASSERT_TRUE(std::isfinite(time) && std::isfinite(stimulus));emitted=emitted || stimulus>0.;trace<<time<<','<<stimulus;
        for(std::size_t i=0;i<channels;++i)
        {
            auto soma=state->neuron->GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);
            const double value=soma->SumPotential(0,0);ASSERT_TRUE(std::isfinite(value));trace<<','<<value;
            low[i]=std::min(low[i],value);high[i]=std::max(high[i],value);
        }
        trace<<'\n';lastTime=time;++samples;core.environment->IncreaseModelTimeByStep();
        if(!Detail::After(end,time)){complete=true;break;}
    }
    for(std::size_t i=0;i<channels;++i)variation=std::max(variation,high[i]-low[i]);
    ASSERT_TRUE(complete);ASSERT_TRUE(emitted);ASSERT_GT(variation,1.e-6);ASSERT_EQ(revision(),package["model_revision"]);
    const QJsonObject record{{"kind","native_recognition_fresh_process_observation"},{"schema_version",1},
        {"trial_id",spec["trial_id"]},{"model_revision",package["model_revision"]},{"complete",complete},
        {"sample_count",double(samples)},{"last_sample_time",lastTime},{"emitted",emitted},{"soma_variation",variation},
        {"frozen_after",revision()},{"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    QFile json(QString::fromLocal8Bit(output));ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
    ASSERT_GT(json.write(QJsonDocument(record).toJson()),0);json.close();
    QFile csv(QString::fromLocal8Bit(output)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
    ASSERT_GT(csv.write(QByteArray::fromStdString(trace.str())),0);csv.close();
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}

TEST(NativeRecognitionOwner,FreshProcessImport)
{
    const auto input=std::getenv("TIMELEARNER_RECOGNITION_OWNER_IMPORT");
    if(!input)GTEST_SKIP()<<"Executed by immutable recognition replay job in a fresh process";
    const auto specification=std::getenv("TIMELEARNER_RECOGNITION_OWNER_SPEC");ASSERT_TRUE(specification);
    const auto output=std::getenv("TIMELEARNER_RECOGNITION_OWNER_OUTPUT");ASSERT_TRUE(output);
    QFile file(QString::fromLocal8Bit(input));ASSERT_TRUE(file.open(QIODevice::ReadOnly));
    const auto package=ParseNativeRecognitionState(file.readAll().toStdString());
    QFile specFile(QString::fromLocal8Bit(specification));ASSERT_TRUE(specFile.open(QIODevice::ReadOnly));
    QJsonParseError parseError;const auto document=QJsonDocument::fromJson(specFile.readAll(),&parseError);
    ASSERT_EQ(parseError.error,QJsonParseError::NoError);ASSERT_TRUE(document.isObject());const auto spec=document.object();
    ASSERT_EQ(spec["schema_version"],QJsonValue(1));ASSERT_EQ(spec["kind"],QJsonValue("native_recognition_frozen_probe"));
    ASSERT_EQ(spec["measurement"],QJsonValue("paired_soma_transport"));ASSERT_EQ(spec["record_spikes"],QJsonValue(false));
    ASSERT_EQ(spec["model_revision"],package["model_revision"]);
    const auto sourceSolo=package["source_solo"].toObject();
    ASSERT_EQ(spec["pattern_hash"],sourceSolo["protocol"].toObject()["pattern_hash"]);
    const auto configuration=DecodeConfiguredNativeTraining(sourceSolo["configuration"].toObject());
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    EXPECT_FALSE(core.storage->CheckClass(configuration.model.neuronClass));
    core.environment->SetUseIndTimeStepFlag(false);core.environment->DestroyModel();
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();
    model->SetGlobalTimeStep(configuration.model.frequencyHz);
    // Generator Reset captures the current clock. Set the declared onset before
    // importing/initializing the physical tree, never after its Reset.
    const double begin=spec["begin"].toDouble(-1.),end=spec["end"].toDouble(-1.);
    ASSERT_TRUE(std::isfinite(begin) && std::isfinite(end) && begin>=0. && end>begin);
    const auto beginUs=std::llround(begin*1.e6);ASSERT_GE(beginUs,0);
    core.environment->GetTime().SetTime(static_cast<unsigned long long>(beginUs));
    ASSERT_FALSE(Detail::After(begin,core.environment->GetTime().GetDoubleTime()));
    ASSERT_FALSE(Detail::After(core.environment->GetTime().GetDoubleTime(),begin));
    struct OwnedGraph {UEPtr<NPulseNeuron> neuron;UEPtr<NDatasetMatrix> dataset;};
    auto state=std::make_unique<OwnedGraph>();UEPtr<UNet> owner;
    std::function<std::string()> failure;std::function<QJsonObject()> exportState;
    int beforeVersion=-1,afterVersion=-1;
    const auto install=[&](auto learner) {
        ASSERT_TRUE(learner);beforeVersion=learner->ControllerVersion.GetData();EXPECT_EQ(beforeVersion,1);
        EXPECT_FALSE(learner->ConfiguredModelInitialized.GetData());EXPECT_FALSE(learner->HasNativeRecognitionState());
        learner->Name="FreshRecognitionLearner";learner->SetEnvironment(core.environment);
        learner->SetGlobalTimeStep(configuration.model.frequencyHz);UEPtr<UContainer> node=learner;
        ASSERT_NE(model->AddComponent(node),ForbiddenId);
        const auto result=learner->ImportNativeRecognitionState(package,"native-learned-boundary-fixture-v1");
        ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;
        learner->Build();learner->Init();owner=learner;afterVersion=learner->ControllerVersion.GetData();
        EXPECT_EQ(afterVersion,sourceSolo["controller_version"].toInt());
        EXPECT_TRUE(learner->HasNativeRecognitionState());EXPECT_FALSE(learner->IsNeedToTrain.GetData());
        EXPECT_FALSE(learner->NativeTrainingController().Certificate());EXPECT_FALSE(learner->NativeTrainingController().References());
        state->neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        state->dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        failure=[learner]{return learner->NativeModelEditFailure();};
        exportState=[learner]{return learner->ExportNativeRecognitionState("native-learned-boundary-fixture-v1");};
    };
    if(configuration.model.branch)install(dynamic_pointer_cast<NNeuronTimeLearnerBranch>(core.storage->TakeObject("NNeuronTimeLearnerBranch")));
    else install(dynamic_pointer_cast<NNeuronTimeLearner>(core.storage->TakeObject("NNeuronTimeLearner")));
    ASSERT_TRUE(owner);ASSERT_TRUE(state->neuron);ASSERT_TRUE(state->dataset);
    auto generator=state->dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
    // The fresh root has no initialized parent fixture. Initialize the complete
    // tree natively; initializing its children alone does not arm its scheduler.
    model->Init();model->Reset();ASSERT_TRUE(model->IsInit());
    const auto revision=[&]{return NmsdkTools::IdentifyModel(state->neuron,{{&generator->Output,"burst"}}).value("sha256");};
    ASSERT_EQ(revision(),package["model_revision"]);const auto frozenBefore=revision();
    ASSERT_TRUE(failure().empty())<<failure();ASSERT_EQ(exportState(),package);
    const auto channels=configuration.model.branch?1u:configuration.model.inputs.size();
    ASSERT_EQ(spec["channels"].toDouble(),double(channels));
    ASSERT_DOUBLE_EQ(spec["maximum_sample_gap"].toDouble(),1./configuration.model.frequencyHz);
    const double budget=spec["maximum_samples"].toDouble();
    ASSERT_TRUE(std::isfinite(budget) && budget>=1. && budget==std::floor(budget) && budget<=1000000.);
    state->dataset->StateGeneration=1;
    std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
    for(std::size_t i=0;i<channels;++i)trace<<",soma"<<i;trace<<'\n';
    bool complete=false,emitted=false;unsigned samples=0;double lastTime=begin,variation=0.;
    std::vector<double> low(channels,std::numeric_limits<double>::infinity()),high(channels,-std::numeric_limits<double>::infinity());
    for(unsigned tick=0;tick<unsigned(budget);++tick)
    {
        model->Calculate();ASSERT_TRUE(failure().empty())<<failure();const double time=core.environment->GetTime().GetDoubleTime(),stimulus=generator->Output(0,0);
        ASSERT_TRUE(std::isfinite(time) && std::isfinite(stimulus));emitted=emitted || stimulus>0.;trace<<time<<','<<stimulus;
        for(std::size_t i=0;i<channels;++i)
        {
            auto soma=state->neuron->GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);
            const double value=soma->SumPotential(0,0);ASSERT_TRUE(std::isfinite(value));trace<<','<<value;
            low[i]=std::min(low[i],value);high[i]=std::max(high[i],value);
        }
        trace<<'\n';lastTime=time;++samples;core.environment->IncreaseModelTimeByStep();
        if(!Detail::After(end,time)){complete=true;break;}
    }
    for(std::size_t i=0;i<channels;++i)variation=std::max(variation,high[i]-low[i]);
    ASSERT_TRUE(complete);ASSERT_TRUE(emitted);ASSERT_GT(variation,1.e-6);ASSERT_EQ(revision(),package["model_revision"]);
    const QJsonObject record{{"kind","native_recognition_owner_fresh_process_observation"},{"schema_version",1},
        {"trial_id",spec["trial_id"]},{"model_revision",package["model_revision"]},{"complete",complete},
        {"sample_count",double(samples)},{"last_sample_time",lastTime},{"emitted",emitted},{"soma_variation",variation},
        {"frozen_before",frozenBefore},{"frozen_after",revision()},
        {"controller_version_before",beforeVersion},{"controller_version_after",afterVersion},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    EXPECT_EQ(exportState(),package);
    QFile json(QString::fromLocal8Bit(output));ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
    ASSERT_GT(json.write(QJsonDocument(record).toJson()),0);json.close();
    QFile csv(QString::fromLocal8Bit(output)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
    ASSERT_GT(csv.write(QByteArray::fromStdString(trace.str())),0);csv.close();
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}

void RepeatedBoundarySummary(const NativeTrainingService& service,const std::string& revision,
    const std::vector<InputParameters>& parameters,const std::string& artifact)
{
    EXPECT_EQ(service.Configuration().n0CandidateRepeats,2u);EXPECT_FALSE(service.Search());
    const auto summary=EncodeNativeTrainingState(service,revision,parameters);
    EXPECT_EQ(summary["schema_version"],QJsonValue(2));
    EXPECT_EQ(summary["search_history_retained"],QJsonValue(false));
    EXPECT_TRUE(summary["candidate_repeat_groups"].isArray());
    EXPECT_TRUE(summary["candidate_repeat_groups"].toArray().isEmpty());
    EXPECT_TRUE(summary["candidates"].toArray().isEmpty());
    Artifact(artifact,QJsonDocument(summary).toJson());
}
template<class Learner> void LearnedBoundary(int normalization,double sync=.02,unsigned frequency=2000,std::size_t inputs=2,bool configured=false,
    std::optional<RecognitionCase> recognition={},bool automatic=false,double initialThreshold=1.,unsigned n0Repeats=1,
    double fixtureWallSeconds=600.)
{
    ASSERT_TRUE(std::isfinite(fixtureWallSeconds) && fixtureWallSeconds>0.);
    auto suffix=std::string(sync==.02?"learned_boundary":"learned_boundary_explicit_tolerance");
    if(inputs!=2)suffix+="_inputs"+std::to_string(inputs);if(configured)suffix+="_configured";if(automatic)suffix+="_automatic";
    if(recognition)suffix+="_recognition_"+std::to_string(int(*recognition));
    if(initialThreshold!=1.)suffix+="_spiking";
    if(n0Repeats>1)suffix+="_repeat"+std::to_string(n0Repeats);
    EditingRig<Learner> rig(frequency,normalization,suffix,false,inputs,!configured,2,1,false,{},1,initialThreshold);
    if(automatic)rig.learner->CalculateMode=0;
    std::optional<ConfiguredNativeTraining> configuredPlan;
    if(configured)
    {
        configuredPlan=Configuration(rig);configuredPlan->search.tolerances.sync=sync;
        configuredPlan->maximumWallSeconds=fixtureWallSeconds;
        configuredPlan->search.n0CandidateRepeats=n0Repeats;
        rig.learner->ControllerVersion=2;rig.learner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(*configuredPlan)).toJson(QJsonDocument::Compact).toStdString();
        rig.learner->Build();rig.learner->Init();ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    }
    auto initialZone=rig.neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(initialZone);
    ASSERT_DOUBLE_EQ(initialZone->Threshold.GetData(),initialThreshold);
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);channel->Capacity=1.41e-9;
    auto plan=TrainingPlan(rig,sync);plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    plan.maximumWallSeconds=fixtureWallSeconds;
    plan.search.n0CandidateRepeats=n0Repeats;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    if(inputs>2)
    {
        // A dimensional transport control, with declared fixed geometry and
        // explicit broad timing tolerance; not convergence at default 0.02.
        for(auto& b:plan.search.bounds){b.maximumLength=b.minimumLength;b.maximumSynapses=b.minimumSynapses;b.maximumResistance=b.minimumResistance;}
        plan.maximumModelSeconds=120.;
        // This is a dimensional transport/trace control, not a wall-time
        // benchmark. Keep a declared finite budget that accommodates the
        // instrumented six-input graph. The 600-second ASan failure is kept
        // as a separate attempt; physical tolerances/model-time stay intact.
        plan.maximumWallSeconds=1800.;
    }
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
    if(configured)rig.learner->SetConfiguredNativeEvidenceSinks({plan.probe.onPrepared,plan.probe.onSample,plan.observationSink});
    else rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,unsigned(plan.maximumModelSeconds*frequency)+100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();ASSERT_TRUE(service.Certificate())<<service.Reason();
    if(sync==.2 && inputs==2 && n0Repeats==1)EXPECT_TRUE(service.Certificate()->Exact());
    ASSERT_EQ(service.ReferencePackets().size(),inputs);ASSERT_EQ(service.FinalPackets().size(),inputs);
    for(const auto& packet:service.ReferencePackets())EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(EncodeNativeProbeEvidence(packet))),EncodeNativeProbeEvidence(packet));
    for(const auto& packet:service.FinalPackets())EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(EncodeNativeProbeEvidence(packet))),EncodeNativeProbeEvidence(packet));
    const auto original=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();const auto references=service.References()->Inputs();
    const auto certificate=EncodeTrainingCertificate(*service.Certificate());
    Artifact(rig.name+"_learned_summary.json",QJsonDocument(EncodeNativeTrainingState(service,original,parameters)).toJson());
    const std::string implementation="native-learned-boundary-fixture-v1";
    const auto package=rig.learner->ExportNativeLearnedState(implementation);
    if(n0Repeats>1)
    {
        EXPECT_EQ(package["configuration"].toObject()["schema_version"],QJsonValue(2));
        EXPECT_EQ(package["configuration"].toObject()["search"].toObject()["n0_candidate_repeats"],QJsonValue(2));
    }
    Artifact(rig.name+"_learned_state.json",QJsonDocument(package).toJson());
    EXPECT_EQ(ParseNativeLearnedState(QJsonDocument(package).toJson(QJsonDocument::Compact).toStdString()),package);
    if(recognition){RecognitionChecks(rig,package,*recognition);return;}
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto test=dynamic_pointer_cast<Learner>(core.storage->TakeObject(rig.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(test);
    test->Name="TestLearner";UEPtr<UContainer> node=test;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);test->SetGlobalTimeStep(frequency);
    const auto imported=test->ImportNativeLearnedState(package,implementation);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;test->Build();test->Init();
    ASSERT_TRUE(test->NativeModelEditFailure().empty())<<test->NativeModelEditFailure();
    if(n0Repeats>1)RepeatedBoundarySummary(test->NativeTrainingController(),original,parameters,rig.name+"_imported_summary.json");
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
    child.setProgram(QString::fromStdString(NmsdkTests::PulseLibTestExecutable()));child.setArguments({"--gtest_filter=NativeLearnedState.FreshProcessImport"});
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
    const auto resign=[](QJsonObject value) {
        value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;
    };
    const auto rejectWithoutMutation=[&](const QJsonObject& value) {
        const auto result=test->ImportNativeLearnedState(value,implementation);
        EXPECT_EQ(result.status,NativeModelBuildStatus::Rejected)<<result.reason;EXPECT_FALSE(result.modelMayHaveChanged);
        EXPECT_EQ(test->ReadNativeParameters(),parameters);
        EXPECT_EQ(NmsdkTools::IdentifyModel(testNeuron,{{&testSource->Output,"burst"}})["sha256"],package["model_revision"]);
        ASSERT_TRUE(test->NativeTrainingController().Certificate());EXPECT_EQ(EncodeTrainingCertificate(*test->NativeTrainingController().Certificate()),certificate);
    };
    corrupted=package;auto claim=corrupted["certificate"].toObject();claim["exact"]=!claim["exact"].toBool();corrupted["certificate"]=claim;
    rejectWithoutMutation(resign(corrupted));
    corrupted=package;auto finals=corrupted["final_packets"].toArray();ASSERT_FALSE(finals.isEmpty());finals.removeLast();corrupted["final_packets"]=finals;
    rejectWithoutMutation(resign(corrupted));
    corrupted=package;auto refs=corrupted["reference_packets"].toArray();auto packet=refs[0].toObject();auto observation=packet["observation"].toObject();
    auto peaks=observation["peaks"].toArray();auto peak=peaks[0].toObject();peak["raw_potential"]=peak["raw_potential"].toDouble()+.001;
    peaks[0]=peak;observation["peaks"]=peaks;packet["observation"]=observation;refs[0]=packet;corrupted["reference_packets"]=refs;
    rejectWithoutMutation(resign(corrupted));
    corrupted=package;auto archive=corrupted["neuron"].toObject();auto definitions=archive["class_definitions"].toArray();
    const auto rootClass=package["configuration"].toObject()["model"].toObject()["neuron_class"].toString();bool removed=false;
    for(int i=0;i<definitions.size();++i)if(definitions[i].toObject()["name"].toString()==rootClass){definitions.removeAt(i);removed=true;break;}
    ASSERT_TRUE(removed);archive["class_definitions"]=definitions;corrupted["neuron"]=resign(archive);rejectWithoutMutation(resign(corrupted));
    auto tap=dynamic_pointer_cast<NPulseGeneratorTransit>(core.storage->TakeObject("NPulseGeneratorTransit"));ASSERT_TRUE(tap);
    tap->Name="ImportedSourceListener";UEPtr<UContainer> tapNode=tap;ASSERT_NE(rig.model->AddComponent(tapNode),ForbiddenId);tap->Init();
    ASSERT_TRUE(tap->Input.SetPointer(0,&testSource->Output));rejectWithoutMutation(package);
    ASSERT_EQ(tap->Input.GetDataSources().size(),1u);EXPECT_EQ(tap->Input.GetDataSources().front(),&testSource->Output);tap->Input.DetachFrom();
    Artifact(rig.name+"_imported_model.json",QJsonDocument(identity).toJson());
    if(frequency==2000 && inputs==2 && normalization==0 && !configured)
    {
        // Use the native component factory and actual replacement path. The
        // one-shot hook fails only after the new dataset has been attached;
        // adding the old objects back must remain possible during rollback.
        using FaultOwner=ImportRollbackLearner<Learner>;
        const auto className=std::string(rig.branch?"LearnedImportRollbackBranch":"LearnedImportRollbackClassic");
        core.storage->AddClass(new UComponentFactoryMethod(core.storage,
            +[]() -> UComponent* {return new FaultOwner;},className),className);
        auto rollback=dynamic_pointer_cast<FaultOwner>(core.storage->TakeObject(className));ASSERT_TRUE(rollback);
        rollback->Name="RollbackLearner";UEPtr<UContainer> childNode=rollback;ASSERT_NE(rig.model->AddComponent(childNode),ForbiddenId);
        rollback->SetGlobalTimeStep(frequency);rollback->IsNeedToTrain.SetDataDirect(false);
        rollback->EnablePostTrainTuning=false;rollback->AutoCalibrateFixedLTZThreshold=false;
        const auto declaration=DecodeConfiguredNativeTraining(package["configuration"].toObject()).model;
        const auto constructed=rollback->ConstructNativeModel(declaration);
        ASSERT_EQ(constructed.status,NativeModelBuildStatus::Constructed)<<constructed.reason;rollback->Build();rollback->Init();
        auto oldNeuron=rollback->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto oldDataset=rollback->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        auto oldSource=oldDataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(oldSource);
        const auto oldIdentity=NmsdkTools::IdentifyModel(oldNeuron,{{&oldSource->Output,"burst"}});
        // Store an owning value. Indexing a temporary non-const QJsonObject
        // and deducing auto would retain a dangling QJsonValueRef instead.
        const QJsonValue oldHash=oldIdentity["sha256"];
        Artifact(rig.name+"_rollback_before_model.json",QJsonDocument(oldIdentity).toJson());
        const auto oldParameters=rollback->ReadNativeParameters();std::vector<NameT> oldOrder;rollback->GetComponentsList(oldOrder);
        const auto measure=[&](const std::string& phase,std::vector<NativeProbeSample>& samples) {
            auto probe=plan.probe;probe.activeInput=0;probe.inputId=plan.protocol.inputs[0].id;
            probe.baseModelRevision=oldHash.toString().toStdString();probe.modelEpoch=0;
            probe.specification.runId=rig.name+"/rollback";probe.specification.trialId=rig.name+"/rollback/"+phase;
            probe.specification.windows={plan.inputWindows[0]};probe.onPrepared={};
            probe.readModelRevision=[=]{return NmsdkTools::IdentifyModel(oldNeuron.Get(),{{&oldSource->Output,"burst"}})["sha256"].toString().toStdString();};
            probe.readFullModelRevision=probe.readModelRevision;
            probe.onSample=[&](const NativeProbeSample& sample){samples.push_back(sample);};
            rollback->QueueNativeProbe(std::move(probe));
            for(unsigned tick=0;rollback->NativeProbeState()==NativeProbeStatus::Queued || rollback->NativeProbeState()==NativeProbeStatus::Running;++tick)
            {ASSERT_LT(tick,unsigned((rig.duration+.02)*frequency));rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
            const auto result=rollback->TakeNativeProbeResult();ASSERT_TRUE(result);
            Artifact(rig.name+"_rollback_"+phase+"_evidence.json",QJsonDocument(EncodeNativeProbeEvidence(*result)).toJson());
            ASSERT_EQ(result->status,NativeProbeStatus::Completed)<<QJsonDocument(EncodeNativeProbeEvidence(*result)).toJson().constData();
            ASSERT_TRUE(result->observation);ASSERT_TRUE(result->observation->valid);
            std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"time,stimulus";
            for(std::size_t i=0;i<(rig.branch?1u:inputs);++i)csv<<",soma"<<i;csv<<'\n';
            for(const auto& sample:samples){csv<<sample.time<<','<<sample.stimulus;for(double p:sample.potentials)csv<<','<<p;csv<<'\n';}
            Artifact(rig.name+"_rollback_"+phase+".csv",QByteArray::fromStdString(csv.str()));
        };
        std::vector<NativeProbeSample> before,after;measure("before",before);ASSERT_FALSE(before.empty());
        rollback->failNeuronAttach=true;
        const auto failed=rollback->ImportNativeLearnedState(package,implementation);
        Artifact(rig.name+"_rollback_after_model.json",QJsonDocument(NmsdkTools::IdentifyModel(oldNeuron,{{&oldSource->Output,"burst"}})).toJson());
        EXPECT_EQ(failed.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(failed.modelMayHaveChanged);
        EXPECT_EQ(failed.reason,"injected_import_neuron_attach_failure");EXPECT_FALSE(rollback->failNeuronAttach);
        EXPECT_EQ(rollback->template GetComponentL<NPulseNeuron>("Neuron",true),oldNeuron);
        EXPECT_EQ(rollback->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true),oldDataset);
        std::vector<NameT> restoredOrder;rollback->GetComponentsList(restoredOrder);EXPECT_EQ(restoredOrder,oldOrder);
        EXPECT_EQ(NmsdkTools::IdentifyModel(oldNeuron,{{&oldSource->Output,"burst"}})["sha256"],oldHash);
        EXPECT_EQ(rollback->ReadNativeParameters(),oldParameters);EXPECT_TRUE(rollback->NativeModelEditFailure().empty());
        EXPECT_FALSE(rollback->NativeTrainingController().Certificate());EXPECT_FALSE(rollback->NativeTrainingController().References());
        measure("after",after);ASSERT_EQ(before.size(),after.size());
        for(std::size_t i=0;i<before.size();++i)
        {
            EXPECT_EQ(before[i].stimulus,after[i].stimulus);EXPECT_EQ(before[i].potentials,after[i].potentials);
            EXPECT_NEAR(before[i].time-before[0].time,after[i].time-after[0].time,32*std::numeric_limits<double>::epsilon()*std::max(1.,after[i].time));
        }
        Artifact(rig.name+"_rollback.json",QJsonDocument(QJsonObject{{"reason",QString::fromStdString(failed.reason)},
            {"changed",failed.modelMayHaveChanged},{"before",oldHash},
            {"after",NmsdkTools::IdentifyModel(oldNeuron,{{&oldSource->Output,"burst"}})["sha256"]}}).toJson());
    }
    if(sync==.2 && inputs==2)
    {
        // Resume from the imported completed boundary with the retained goal.
        // A new session must verify the model, not recapture amplitudes from
        // the learned geometry and silently redefine the original objective.
        auto warm=test->NativeTrainingController().Plan();warm.probe.onPrepared={};warm.probe.onSample={};
        std::size_t warmObservations=0;std::ostringstream warmTrace;
        warm.probe.onPrepared=[&](const auto&,const auto&) {
            warmTrace.str({});warmTrace.clear();warmTrace.imbue(std::locale::classic());
            warmTrace<<std::setprecision(17)<<"time,stimulus";
            for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)warmTrace<<",soma"<<i;warmTrace<<'\n';
        };
        warm.probe.onSample=[&](const NativeProbeSample& frame) {
            warmTrace<<frame.time<<','<<frame.stimulus;for(double value:frame.potentials)warmTrace<<','<<value;warmTrace<<'\n';
        };
        warm.observationSink=[&](const NativeProbeResult& packet) {
            const auto stem=rig.name+"_warm_trial_"+std::to_string(++warmObservations);
            Artifact(stem+".json",QJsonDocument(EncodeNativeProbeEvidence(packet)).toJson());
            Artifact(stem+".csv",QByteArray::fromStdString(warmTrace.str()));
        };
        const auto attempt=test->NativeTrainingController().SessionAttempt();
        test->BeginNativeTraining(std::move(warm));
        for(unsigned ticks=0;test->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
        {ASSERT_LT(ticks,60000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
        const auto& resumed=test->NativeTrainingController();
        ASSERT_TRUE(resumed.Certificate())<<resumed.Reason();EXPECT_TRUE(resumed.Certificate()->Exact());
        EXPECT_EQ(resumed.IssuedReferenceProbes(),0u);EXPECT_EQ(resumed.References()->Inputs(),references);
        EXPECT_EQ(resumed.SessionAttempt(),attempt+1);EXPECT_GT(warmObservations,0u);
        EXPECT_EQ(test->ReadNativeParameters(),parameters);
        Artifact(rig.name+"_warm_boundary.json",QJsonDocument(test->ExportNativeLearnedState(implementation)).toJson());
        Artifact(rig.name+"_warm_summary.json",QJsonDocument(EncodeNativeTrainingState(resumed,
            NmsdkTools::IdentifyModel(testNeuron,{{&testSource->Output,"burst"}})["sha256"].toString().toStdString(),test->ReadNativeParameters())).toJson());
    }
}
TEST(NativeLearnedState,ClassicN0){LearnedBoundary<NNeuronTimeLearner>(0);}
TEST(NativeThresholdContract,StorageAliasesUseActualImplementations)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    QJsonArray checked;
    for(const std::string name:{"NPulseLTZoneThreshold","NPulseLTZoneThresholdBio","NPulseLTZoneThresholdBio2",
        "NPLTZone","NPulseLTZoneIzhikevich","NPulseLTZoneIaF","NPulseLTZoneCable","NPSimpleLTZone","NCLTZone","NCSimpleLTZone"})
    {
        auto zone=dynamic_pointer_cast<NPulseLTZoneCommon>(core.storage->TakeObject(name));ASSERT_TRUE(zone)<<name;
        const bool supported=SupportsNativeScalarSpikeThreshold(*zone);
        if(name=="NPSimpleLTZone" || name=="NCLTZone" || name=="NCSimpleLTZone")
        {EXPECT_FALSE(supported)<<name;EXPECT_THROW(RequireNativeScalarSpikeThreshold(*zone),std::invalid_argument);}
        else EXPECT_TRUE(supported)<<name;
        if(name=="NPulseLTZoneIzhikevich")EXPECT_NE(dynamic_cast<NPulseLTZoneThreshold*>(zone.Get()),nullptr);
        if(name=="NPulseLTZoneIaF" || name=="NPulseLTZoneCable")EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),-.055);
        checked.append(QJsonObject{{"image",QString::fromStdString(name)},{"scalar_spike_threshold_supported",supported},
            {"threshold",zone->Threshold.GetData()}});
        core.storage->ReturnObject(zone);
    }
    Artifact("native_threshold_storage_contract.json",QJsonDocument(QJsonObject{{"kind","native_threshold_storage_contract"},
        {"schema_version",1},{"images",checked},{"calibrated",false}}).toJson());
}
TEST(NativeThresholdContract,SignedIaFImageProducesMeasuredSpike)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();
    auto source=dynamic_pointer_cast<NConstGenerator>(core.storage->TakeObject("NCGenerator"));ASSERT_TRUE(source);
    source->Name="Stimulus";UEPtr<UContainer> generator=source;ASSERT_NE(model->AddComponent(generator),ForbiddenId);
    auto zone=dynamic_pointer_cast<NPulseLTZoneCommon>(core.storage->TakeObject("NPulseLTZoneIaF"));ASSERT_TRUE(zone);
    zone->Name="LTZone";UEPtr<UContainer> component=zone;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    int slot=0;ASSERT_TRUE(source->Connect(zone,"Output","Inputs",slot,true));
    model->SetGlobalTimeStep(2000);model->Build();model->Init();model->Reset();
    EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),-.055);EXPECT_DOUBLE_EQ(zone->ThresholdOff.GetData(),-.07);
    QJsonArray frames;
    for(double input:{-.07,-.05,-.071})
    {
        source->Amplitude=input;
        const auto time=core.environment->GetTime().GetDoubleTime();model->Calculate();
        EXPECT_DOUBLE_EQ(zone->Potential.GetData(),input);
        frames.append(QJsonObject{{"time",time},{"input",input},{"decision_potential",zone->Potential.GetData()},
            {"lt_output",zone->Output(0,0)},{"spike_count",zone->OutputPulseTimes.GetCols()}});
        if(input==-.07)EXPECT_EQ(zone->OutputPulseTimes.GetCols(),0);
        if(input==-.05){EXPECT_EQ(zone->OutputPulseTimes.GetCols(),1);EXPECT_GT(zone->Output(0,0),0.);}
        if(input==-.071){EXPECT_EQ(zone->OutputPulseTimes.GetCols(),1);EXPECT_DOUBLE_EQ(zone->Output(0,0),0.);}
        core.environment->IncreaseModelTimeByStep();
    }
    Artifact("native_signed_threshold_control.json",QJsonDocument(QJsonObject{{"kind","native_signed_threshold_control"},
        {"schema_version",1},{"image","NPulseLTZoneIaF"},{"threshold",zone->Threshold.GetData()},{"frames",frames},
        {"scope","isolated LTZone component; no soma or pattern-recognition claim"},{"calibrated",false}}).toJson());
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}

template<class Learner> void CalibrationBoundaryFixture(int normalization,unsigned frequency,bool potential=false)
{
    // Explicit transport-fixture allowance, recorded in configuration/state.
    // ASan at 20 kHz exhausted 600 s while building the source model. Production
    // defaults, model-time budget, tolerances and search bounds are unchanged.
    LearnedBoundary<Learner>(normalization,.02,frequency,2,true,
        potential?RecognitionCase::ThresholdPotential:RecognitionCase::ThresholdCandidates,false,1.,1,1800.);
}
TEST(NativeThresholdCandidate,ClassicN0_2000){CalibrationBoundaryFixture<NNeuronTimeLearner>(0,2000);}
TEST(NativeThresholdPotential,ClassicN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,2000,true);}
TEST(NativeThresholdPotential,BranchN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,2000,true);}
TEST(NativeThresholdPotential,ClassicN1_20000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,20000,true);}
TEST(NativeThresholdPotential,BranchN1_20000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,20000,true);}
TEST(NativeCalibrationPersistence,ClassicN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,2000,true);}
TEST(NativeCalibrationPersistence,BranchN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,2000,true);}
TEST(NativeCalibratedState,ClassicN1_2000){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,true,RecognitionCase::CalibratedThreshold,false,1.,1,1800.);}
TEST(NativeCalibratedState,BranchN1_2000){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::CalibratedThreshold,false,1.,1,1800.);}
TEST(NativeThresholdCandidate,ClassicN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,2000);}
TEST(NativeThresholdCandidate,BranchN0_2000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(0,2000);}
TEST(NativeThresholdCandidate,BranchN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,2000);}
TEST(NativeThresholdCandidate,ClassicN0_20000){CalibrationBoundaryFixture<NNeuronTimeLearner>(0,20000);}
TEST(NativeThresholdCandidate,ClassicN1_20000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,20000);}
TEST(NativeThresholdCandidate,BranchN0_20000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(0,20000);}
TEST(NativeThresholdCandidate,BranchN1_20000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,20000);}
TEST(NativeLearnedState,BranchN0){LearnedBoundary<NNeuronTimeLearnerBranch>(0);}
TEST(NativeLearnedState,ClassicN1){LearnedBoundary<NNeuronTimeLearner>(1);}
TEST(NativeLearnedState,BranchN1){LearnedBoundary<NNeuronTimeLearnerBranch>(1);}
TEST(NativeLearnedState,ExactCertificateWithExplicitPointTwoTolerance){LearnedBoundary<NNeuronTimeLearner>(1,.2);}
TEST(NativeLearnedState,ClassicN0_20000){LearnedBoundary<NNeuronTimeLearner>(0,.02,20000);}
TEST(NativeLearnedState,BranchN0_20000){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,20000);}
TEST(NativeLearnedState,ClassicN1_20000){LearnedBoundary<NNeuronTimeLearner>(1,.02,20000);}
TEST(NativeLearnedState,BranchN1_20000){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,20000);}
TEST(NativeLearnedState,ClassicConfiguredN1){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,true);}
TEST(NativeLearnedState,BranchConfiguredN0){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,true);}
TEST(NativeLearnedState,ClassicConfiguredN0Repeated){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,true,{},false,1.,2);}
TEST(NativeLearnedState,BranchConfiguredN0Repeated){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,true,{},false,1.,2);}
TEST(NativeLearnedState,ClassicConfiguredN0RepeatedWarm){LearnedBoundary<NNeuronTimeLearner>(0,.2,2000,2,true,{},false,1.,2);}
TEST(NativeLearnedState,BranchConfiguredN0RepeatedWarm){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.2,2000,2,true,{},false,1.,2);}
TEST(NativeLearnedState,ClassicOneInput){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,1);}
TEST(NativeLearnedState,BranchOneInput){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,1);}
TEST(NativeLearnedState,BranchFourInputsExplicitPointFiveTolerance){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.5,2000,4);}
TEST(NativeLearnedState,ClassicSixInputsExplicitOneTolerance){LearnedBoundary<NNeuronTimeLearner>(0,1.,2000,6);}
TEST(NativeLearnedState,BranchSixSharedInputsExplicitOneTolerance){LearnedBoundary<NNeuronTimeLearnerBranch>(0,1.,2000,6);}

TEST(NativeRecognitionOwner,ClassicFreshDestination){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,true,RecognitionCase::OwnedFreshIdentity);}
TEST(NativeRecognitionOwner,BranchFreshDestination){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::OwnedFreshScaled);}
TEST(NativeRecognitionOwner,ClassicSpikingFreshDestination){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,true,RecognitionCase::OwnedFreshIdentity,false,.0001);}
TEST(NativeRecognitionOwner,BranchSpikingFreshDestination){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::OwnedFreshScaled,false,.0001);}
TEST(NativeRecognitionOwner,ClassicN0){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,false,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,BranchN0){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,false,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,ClassicN1){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,false,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,BranchN1){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,BranchN1Scale){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::OwnedScaled);}
TEST(NativeRecognitionOwner,BranchN1Clip){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::OwnedClipped);}
TEST(NativeRecognitionOwner,BranchSingleInput){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,1,false,RecognitionCase::OwnedScaled);}
TEST(NativeRecognitionOwner,BranchSixShared){LearnedBoundary<NNeuronTimeLearnerBranch>(0,1.,2000,6,false,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,ClassicConfigured){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,true,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,BranchConfigured){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::OwnedIdentity);}
TEST(NativeRecognitionOwner,ClassicAutomatic){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,false,RecognitionCase::OwnedIdentity,true);}
TEST(NativeRecognitionOwner,BranchAutomatic){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,false,RecognitionCase::OwnedIdentity,true);}

TEST(NativeRecognitionState,ClassicN0Identity){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,false,RecognitionCase::Identity);}
TEST(NativeRecognitionState,BranchN0Identity){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,false,RecognitionCase::Identity);}
TEST(NativeRecognitionState,ClassicN1Identity){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,false,RecognitionCase::Identity);}
TEST(NativeRecognitionState,BranchN1Identity){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::Identity);}
TEST(NativeRecognitionState,BranchN1HistoricalScale){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::Scaled);}
TEST(NativeRecognitionState,BranchN1ExplicitClipping){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::Clipped);}
TEST(NativeRecognitionState,BranchN1SingleInput){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,1,false,RecognitionCase::Scaled);}
TEST(NativeRecognitionState,BranchN0SixSharedInputs){LearnedBoundary<NNeuronTimeLearnerBranch>(0,1.,2000,6,false,RecognitionCase::Identity);}
TEST(NativeRecognitionState,ConflictingSharedBankIsRejectedWithoutChangingSource)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,1.,2000,4,false,RecognitionCase::SharedConflict);}
TEST(NativeRecognitionState,SpecIsStrictAndRoundtrips)
{
    NativeRecognitionSpec spec;const auto identity=EncodeNativeRecognitionSpec(spec);
    EXPECT_EQ(EncodeNativeRecognitionSpec(DecodeNativeRecognitionSpec(identity)),identity);
    spec.mode=RecognitionConversionMode::HistoricalBranchN1;spec.resistanceBounds={{1.e6,1.e9},{2.e6,2.e9}};
    const auto scaled=EncodeNativeRecognitionSpec(spec);EXPECT_EQ(EncodeNativeRecognitionSpec(DecodeNativeRecognitionSpec(scaled)),scaled);
    auto invalid=scaled;invalid["reserved"]=1;EXPECT_THROW(DecodeNativeRecognitionSpec(invalid),std::invalid_argument);
    invalid=scaled;invalid["schema_version"]=2;EXPECT_THROW(DecodeNativeRecognitionSpec(invalid),std::invalid_argument);
    spec.resistanceBounds[0]={2.,1.};EXPECT_THROW(EncodeNativeRecognitionSpec(spec),std::invalid_argument);
    spec.mode=RecognitionConversionMode::Identity;spec.resistanceBounds={{1.,2.}};
    EXPECT_THROW(EncodeNativeRecognitionSpec(spec),std::invalid_argument);
}
TEST(NativeRecognitionState,StoppedPackageCannotBecomeCompletedRecognition)
{
    const QJsonObject stopped{{"kind","timelearner_stopped_state"},{"state_kind","diagnostic"}};
    std::string reason;
    try {ConvertNativeSoloToRecognition(stopped,{},UEPtr<UStorage>{},UEPtr<UEnvironment>{},"test");}
    catch(const std::invalid_argument& error){reason=error.what();}
    EXPECT_EQ(reason,"recognition_requires_completed_solo");
}

class ConnectedTrainingFlag : public UNet {
public:
    UProperty<bool,ConnectedTrainingFlag,ptOutput | ptPubState> Value;
    ConnectedTrainingFlag():Value("Value",this){}
    ConnectedTrainingFlag* New(void) override {return new ConnectedTrainingFlag;}
};
enum class ConnectedStopPoint { Early,Partial,Search,AfterSample,KeepTrue };
template<class Learner> void ConnectedStop(ConnectedStopPoint point,int calculateMode)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    EditingRig<Learner> rig(2000,1,"connected_stop_"+std::to_string(int(point))+"_mode"+std::to_string(calculateMode),false,2,false);
    rig.learner->CalculateMode=calculateMode;
    const auto configuration=Configuration(rig);
    rig.learner->ControllerVersion=2;
    rig.learner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(configuration)).toJson(QJsonDocument::Compact).toStdString();
    rig.learner->Build();rig.learner->Init();ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty());
    rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
    rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    UEPtr<ConnectedTrainingFlag> flag(new ConnectedTrainingFlag);
    flag->SetStorage(core.storage);flag->SetEnvironment(core.environment);flag->Default();
    flag->Name="ExternalTrainingFlag";flag->Activity=true;flag->SetGlobalTimeStep(rig.frequency);
    UEPtr<UContainer> node=flag;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);flag->Init();flag->Value=true;
    ASSERT_TRUE(rig.learner->IsNeedToTrain.SetPointer(0,&flag->Value));
    ASSERT_TRUE(rig.learner->IsNeedToTrain.IsConnected());ASSERT_TRUE(rig.learner->IsNeedToTrain.GetData());
    auto plan=TrainingPlan(rig);bool requested=false;std::size_t observations=0;
    std::vector<InputParameters> parametersAtStop;
    std::ostringstream trace;
    plan.probe.onPrepared=[&](const auto&,const auto&) {
        trace.str({});trace.clear();trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)trace<<",soma"<<i;trace<<'\n';
    };
    plan.probe.onSample=[&](const NativeProbeSample& frame) {
        trace<<frame.time<<','<<frame.stimulus;for(double value:frame.potentials)trace<<','<<value;trace<<'\n';
        if(point==ConnectedStopPoint::AfterSample && !requested)
        {parametersAtStop=rig.learner->ReadNativeParameters();flag->Value=false;requested=true;}
    };
    plan.observationSink=[&](const NativeProbeResult& packet) {
        const auto stem=rig.name+"_stopped_trial_"+std::to_string(++observations);
        Artifact(stem+".json",QJsonDocument(EncodeNativeProbeEvidence(packet)).toJson());
        Artifact(stem+".csv",QByteArray::fromStdString(trace.str()));
    };
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;;++ticks)
    {
        ASSERT_LT(ticks,40000u);const auto& service=rig.learner->NativeTrainingController();
        if(point==ConnectedStopPoint::KeepTrue && ticks==20)break;
        if((point==ConnectedStopPoint::Early && ticks==10) ||
           (point==ConnectedStopPoint::Partial && service.ReferencePackets().size()==1) ||
           (point==ConnectedStopPoint::Search && service.Search() && service.Search()->AppliedEdits()>0))
        {parametersAtStop=rig.learner->ReadNativeParameters();flag->Value=false;requested=true;}
        rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
        if(requested)break; // The stop must be observed in this native tick.
        ASSERT_NE(service.State(),NativeTrainingState::Finished)<<service.Reason();
    }
    const auto& service=rig.learner->NativeTrainingController();
    const bool keep=point==ConnectedStopPoint::KeepTrue;
    Artifact(rig.name+"_connected_stop.json",QJsonDocument(QJsonObject{
        {"kind","native_connected_training_stop"},{"schema_version",1},{"calculate_mode",calculateMode},
        {"controller_version",rig.learner->ControllerVersion.GetData()},
        {"stop_point",int(point)},{"connected",rig.learner->IsNeedToTrain.IsConnected()},
        {"source_value",flag->Value.GetData()},{"learner_need",rig.learner->IsNeedToTrain.GetData()},
        {"stop_requested",requested},{"state",NativeTrainingStateName(service.State())},
        {"outcome",TrainingStatusName(service.Outcome())},{"reason",QString::fromStdString(service.Reason())},
        {"certificate_present",bool(service.Certificate())},{"reference_packets",double(service.ReferencePackets().size())},
        {"observed_packets",double(service.ObservedPackets().size())},{"probe_state",NativeProbeStatusName(rig.learner->NativeProbeState())},
        {"parameters_preserved",keep || parametersAtStop==rig.learner->ReadNativeParameters()},
        {"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    EXPECT_EQ(flag->Value.GetData(),keep);EXPECT_EQ(rig.learner->IsNeedToTrain.GetData(),keep);
    EXPECT_TRUE(rig.learner->IsNeedToTrain.IsConnected());EXPECT_FALSE(service.Certificate());
    if(keep)
    {EXPECT_EQ(service.State(),NativeTrainingState::CapturingReferences);EXPECT_EQ(service.Outcome(),TrainingStatus::Searching);}
    else
    {
        ASSERT_EQ(service.State(),NativeTrainingState::Finished);
        EXPECT_EQ(service.Outcome(),TrainingStatus::ExternalStop);EXPECT_EQ(service.Reason(),"external_stop");
        EXPECT_EQ(rig.learner->ReadNativeParameters(),parametersAtStop);
        EXPECT_NE(rig.learner->NativeProbeState(),NativeProbeStatus::Queued);EXPECT_NE(rig.learner->NativeProbeState(),NativeProbeStatus::Running);
        const auto state=rig.learner->ExportNativeLearnedState("native-connected-stop-fixture-v1");
        EXPECT_EQ(state["kind"].toString(),"timelearner_stopped_state");
        Artifact(rig.name+"_stopped_state.json",QJsonDocument(state).toJson());
        Artifact(rig.name+"_stopped_summary.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    }
    rig.learner->IsNeedToTrain.DetachFrom();
    if(keep)rig.learner->IsNeedToTrain=false; // Local cleanup after the positive-control observation.
}
#define CONNECTED_STOP_TESTS(TOPOLOGY,TYPE,MODE) \
TEST(NativeConnectedStop,TOPOLOGY##MODE##Early){ConnectedStop<TYPE>(ConnectedStopPoint::Early,MODE);} \
TEST(NativeConnectedStop,TOPOLOGY##MODE##Partial){ConnectedStop<TYPE>(ConnectedStopPoint::Partial,MODE);} \
TEST(NativeConnectedStop,TOPOLOGY##MODE##Search){ConnectedStop<TYPE>(ConnectedStopPoint::Search,MODE);} \
TEST(NativeConnectedStop,TOPOLOGY##MODE##AfterSample){ConnectedStop<TYPE>(ConnectedStopPoint::AfterSample,MODE);} \
TEST(NativeConnectedStop,TOPOLOGY##MODE##KeepTrue){ConnectedStop<TYPE>(ConnectedStopPoint::KeepTrue,MODE);}
CONNECTED_STOP_TESTS(Classic,NNeuronTimeLearner,0)
CONNECTED_STOP_TESTS(Classic,NNeuronTimeLearner,1)
CONNECTED_STOP_TESTS(Branch,NNeuronTimeLearnerBranch,0)
CONNECTED_STOP_TESTS(Branch,NNeuronTimeLearnerBranch,1)
#undef CONNECTED_STOP_TESTS

enum class StoppedCase { Early, Partial, BudgetEarly, BudgetSearch, Search, Final, InvalidProbe, ChangedPartial, RepeatPartial };
template<class Learner> void StoppedBoundary(StoppedCase scenario,const std::string& label,int normalization=1,bool configured=false,unsigned n0Repeats=1)
{
    EditingRig<Learner> rig(2000,normalization,"stopped_"+label);auto plan=TrainingPlan(rig);
    plan.search.n0CandidateRepeats=n0Repeats;
    if(configured)
    {
        auto configuration=Configuration(rig);configuration.search.n0CandidateRepeats=n0Repeats;rig.learner->ControllerVersion=2;
        rig.learner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(configuration)).toJson(QJsonDocument::Compact).toStdString();
        rig.learner->Build();rig.learner->Init();ASSERT_TRUE(rig.learner->NativeModelEditFailure().empty())<<rig.learner->NativeModelEditFailure();
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");plan=MakeConfiguredNativeTrainingPlan(configuration);
    }
    if(scenario==StoppedCase::BudgetEarly)plan.maximumModelSeconds=.002;
    if(scenario==StoppedCase::BudgetSearch)plan.search.maximumProbes=3;
    if(scenario==StoppedCase::InvalidProbe)plan.probe.onPrepared=[](const auto&,const auto&) {
        throw std::runtime_error("injected_stopped_probe_failure");
    };
    std::size_t observations=0;std::ostringstream trace;
    const auto prepare=plan.probe.onPrepared;
    plan.probe.onPrepared=[&](const auto& prepared,const auto& spec) {
        trace.str({});trace.clear();trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)trace<<",soma"<<i;trace<<'\n';
        if(prepare)prepare(prepared,spec);
    };
    plan.probe.onSample=[&](const auto& frame) {
        trace<<frame.time<<','<<frame.stimulus;for(double value:frame.potentials)trace<<','<<value;trace<<'\n';
    };
    plan.observationSink=[&](const auto& packet) {
        const auto stem=rig.name+"_stopped_trial_"+std::to_string(++observations);
        Artifact(stem+".json",QJsonDocument(EncodeNativeProbeEvidence(packet)).toJson());
        Artifact(stem+".csv",QByteArray::fromStdString(trace.str()));
    };
    if(configured)rig.learner->SetConfiguredNativeEvidenceSinks({plan.probe.onPrepared,plan.probe.onSample,plan.observationSink});
    else rig.learner->BeginNativeTraining(plan);
    bool changed=false;
    for(unsigned ticks=0;;++ticks)
    {
        ASSERT_LT(ticks,40000u);const auto& service=rig.learner->NativeTrainingController();
        if(service.State()==NativeTrainingState::Finished)break;
        const bool partial=service.ReferencePackets().size()==1;
        if(scenario==StoppedCase::ChangedPartial && partial && !changed)
        {
            auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);
            ASSERT_TRUE(channel);channel->Capacity=1.43e-9;changed=true;
        }
        if((scenario==StoppedCase::Early && ticks==10) || (scenario==StoppedCase::Partial && partial) ||
           (scenario==StoppedCase::Search && service.Search() && service.Search()->AppliedEdits()>0) ||
           (scenario==StoppedCase::RepeatPartial && service.Search() && !service.Search()->Evidence().empty()) ||
           (scenario==StoppedCase::Final && service.FinalPackets().size()==1))
        {rig.learner->IsNeedToTrain=false;break;}
        rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    }
    const auto& service=rig.learner->NativeTrainingController();
    ASSERT_EQ(service.State(),NativeTrainingState::Finished);ASSERT_FALSE(service.Certificate());
    if(scenario==StoppedCase::RepeatPartial)
    {
        ASSERT_TRUE(service.Search());ASSERT_EQ(service.Search()->CandidateRepeats().size(),1u);
        const auto& group=service.Search()->CandidateRepeats().front();
        EXPECT_FALSE(group.complete);EXPECT_EQ(group.trialIds.size(),1u);EXPECT_EQ(group.rawPotentials.size(),1u);
    }
    const auto expected=(scenario==StoppedCase::BudgetEarly || scenario==StoppedCase::BudgetSearch)?TrainingStatus::BudgetExhausted:
        (scenario==StoppedCase::ChangedPartial?TrainingStatus::InvalidModel:
         (scenario==StoppedCase::InvalidProbe?TrainingStatus::InvalidObservation:TrainingStatus::ExternalStop));
    ASSERT_EQ(service.Outcome(),expected)<<service.Reason();
    if(scenario==StoppedCase::Early || scenario==StoppedCase::BudgetEarly || scenario==StoppedCase::InvalidProbe)
        EXPECT_TRUE(service.ReferencePackets().empty());
    if(scenario==StoppedCase::Partial || scenario==StoppedCase::ChangedPartial)EXPECT_EQ(service.ReferencePackets().size(),1u);
    if(scenario==StoppedCase::Search || scenario==StoppedCase::BudgetSearch || scenario==StoppedCase::Final)ASSERT_TRUE(service.References());
    if(scenario==StoppedCase::Final)EXPECT_EQ(service.FinalPackets().size(),1u);
    ASSERT_FALSE(service.ObservedPackets().empty());
    const std::string implementation="native-stopped-boundary-fixture-v1";
    const auto package=rig.learner->ExportNativeLearnedState(implementation);
    EXPECT_EQ(package["kind"],QJsonValue("timelearner_stopped_state"));EXPECT_TRUE(package["certificate"].isNull());
    EXPECT_EQ(package["reason"].toString().toStdString(),service.Reason());
    EXPECT_EQ(package["observed_packets"].toArray().size(),int(service.ObservedPackets().size()));
    EXPECT_EQ(ParseNativeLearnedState(QJsonDocument(package).toJson().toStdString()),package);
    Artifact(rig.name+"_stopped_state.json",QJsonDocument(package).toJson());
    Artifact(rig.name+"_stopped_summary.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    auto test=dynamic_pointer_cast<Learner>(core.storage->TakeObject(rig.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(test);
    test->Name="StoppedTest";UEPtr<UContainer> node=test;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);test->SetGlobalTimeStep(rig.frequency);
    const auto imported=test->ImportNativeLearnedState(package,implementation);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;test->Build();test->Init();
    const auto& restored=test->NativeTrainingController();ASSERT_FALSE(restored.Certificate());
    if(n0Repeats>1)RepeatedBoundarySummary(restored,package["model_revision"].toString().toStdString(),test->ReadNativeParameters(),rig.name+"_imported_summary.json");
    EXPECT_EQ(restored.Outcome(),expected);EXPECT_EQ(restored.Reason(),service.Reason());EXPECT_FALSE(test->IsNeedToTrain.GetData());
    EXPECT_EQ(test->ReadNativeParameters(),rig.learner->ReadNativeParameters());
    auto testNeuron=test->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto testSource=test->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(testNeuron);ASSERT_TRUE(testSource);
    const auto importedRevision=[&]{return NmsdkTools::IdentifyModel(testNeuron,{{&testSource->Output,"burst"}})["sha256"].toString().toStdString();};
    EXPECT_EQ(importedRevision(),rig.Revision());
    const auto resign=[](QJsonObject value){value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;};
    const auto reject=[&](QJsonObject value) {
        const auto result=test->ImportNativeLearnedState(resign(value),implementation);
        EXPECT_EQ(result.status,NativeModelBuildStatus::Rejected)<<result.reason;EXPECT_FALSE(result.modelMayHaveChanged);
        EXPECT_EQ(importedRevision(),rig.Revision());EXPECT_FALSE(restored.Certificate());EXPECT_EQ(restored.Outcome(),expected);
    };
    auto corrupt=package;corrupt["training_outcome"]="exact";reject(corrupt);
    corrupt=package;corrupt["certificate"]=QJsonObject{{"exact",true}};reject(corrupt);
    corrupt=package;corrupt["reference_complete"]=!package["reference_complete"].toBool();reject(corrupt);
    corrupt=package;corrupt["capture_revision"]="wrong-capture";reject(corrupt);
    corrupt=package;auto duplicate=corrupt["observed_packets"].toArray();ASSERT_FALSE(duplicate.isEmpty());
    duplicate.append(duplicate[0]);corrupt["observed_packets"]=duplicate;reject(corrupt);
    if(!package["final_packets"].toArray().isEmpty())
    {corrupt=package;corrupt["observed_packets"]=QJsonArray{};reject(corrupt);}
    // Frozen evaluation uses the real native scheduler. Neither stopped model
    // may restart its controller or manufacture a successful certificate.
    std::vector<NativeProbeSample> originalFrames,importedFrames;
    auto request=plan.probe;request.activeInput=0;request.inputId=plan.protocol.inputs[0].id;
    request.baseModelRevision=rig.Revision();request.modelEpoch=restored.ModelEpoch();
    request.specification.runId=rig.name+"/frozen";request.specification.trialId=rig.name+"/frozen/test";
    request.specification.windows={plan.inputWindows[0]};request.onPrepared={};
    auto observer=std::make_shared<NmsdkTools::ModelRevisionObserver>();
    request.readModelRevision=[=]{return observer->Read(testNeuron.Get(),{{&testSource->Output,"burst"}}).toStdString();};
    request.readFullModelRevision=[=]{return observer->Read(testNeuron.Get(),{{&testSource->Output,"burst"}},true).toStdString();};
    request.onSample=[&](const auto& frame){importedFrames.push_back(frame);};
    const auto frozenStart=rig.environment->GetTime().GetTime();test->QueueNativeProbe(std::move(request));
    const auto originalProbe=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const auto& frame){originalFrames.push_back(frame);});
    ASSERT_EQ(originalProbe.status,NativeProbeStatus::Completed);const auto frozen=test->TakeNativeProbeResult();ASSERT_TRUE(frozen);
    ASSERT_EQ(frozen->status,NativeProbeStatus::Completed);ASSERT_FALSE(originalFrames.empty());ASSERT_EQ(originalFrames.size(),importedFrames.size());
    for(std::size_t i=0;i<originalFrames.size();++i)
    {EXPECT_EQ(originalFrames[i].time,importedFrames[i].time);EXPECT_EQ(originalFrames[i].stimulus,importedFrames[i].stimulus);EXPECT_EQ(originalFrames[i].potentials,importedFrames[i].potentials);}
    std::ostringstream frozenTrace;frozenTrace.imbue(std::locale::classic());frozenTrace<<std::setprecision(17)<<"time,stimulus";
    for(std::size_t i=0;i<(rig.branch?1u:rig.inputCount);++i)frozenTrace<<",soma"<<i;frozenTrace<<'\n';
    for(const auto& frame:importedFrames){frozenTrace<<frame.time<<','<<frame.stimulus;for(double value:frame.potentials)frozenTrace<<','<<value;frozenTrace<<'\n';}
    Artifact(rig.name+"_frozen.csv",QByteArray::fromStdString(frozenTrace.str()));
    Artifact(rig.name+"_frozen_evidence.json",QJsonDocument(EncodeNativeProbeEvidence(*frozen)).toJson());
    QTemporaryDir directory;ASSERT_TRUE(directory.isValid());const auto path=directory.path()+"/stopped.json",output=directory.path()+"/fresh.json";
    QFile serialized(path);ASSERT_TRUE(serialized.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_GT(serialized.write(QJsonDocument(package).toJson()),0);serialized.close();
    QProcess child;auto childEnv=QProcessEnvironment::systemEnvironment();childEnv.insert("TIMELEARNER_LEARNED_IMPORT",path);
    childEnv.insert("TIMELEARNER_LEARNED_OUTPUT",output);childEnv.insert("TIMELEARNER_LEARNED_START_US",QString::number(frozenStart));
    child.setProcessEnvironment(childEnv);child.setProgram(QString::fromStdString(NmsdkTests::PulseLibTestExecutable()));
    child.setArguments({"--gtest_filter=NativeLearnedState.FreshProcessImport"});child.start();ASSERT_TRUE(child.waitForStarted(30000));ASSERT_TRUE(child.waitForFinished(120000));
    Artifact(rig.name+"_fresh_process.log",child.readAllStandardOutput()+child.readAllStandardError());ASSERT_EQ(child.exitCode(),0);
    QFile fresh(output);ASSERT_TRUE(fresh.open(QIODevice::ReadOnly));const auto record=QJsonDocument::fromJson(fresh.readAll()).object();
    EXPECT_TRUE(record["certificate"].isNull());EXPECT_EQ(record["model"].toObject()["sha256"],package["model_revision"]);
    Artifact(rig.name+"_fresh_process.json",QJsonDocument(record).toJson());
    QFile freshCsv(output+".csv");ASSERT_TRUE(freshCsv.open(QIODevice::ReadOnly));const auto bytes=freshCsv.readAll();
    EXPECT_EQ(bytes,QByteArray::fromStdString(frozenTrace.str()));Artifact(rig.name+"_fresh_process.csv",bytes);
    EXPECT_EQ(importedRevision(),rig.Revision());EXPECT_FALSE(restored.Certificate());
    // A warm attempt is a new search from an explicit boundary, never a
    // continuation of a half-integrated probe. Complete goals are retained.
    const bool complete=bool(restored.References());const auto previousAttempt=restored.SessionAttempt();
    const auto capture=complete?restored.References()->Inputs():std::vector<CapturedInputReference>{};
    test->Reset();test->BeginNativeTraining(plan);
    if(scenario==StoppedCase::ChangedPartial)
    {
        EXPECT_EQ(restored.State(),NativeTrainingState::Finished);EXPECT_EQ(restored.Outcome(),TrainingStatus::InvalidModel);
        EXPECT_EQ(restored.Reason(),"incomplete_reference_capture_requires_original_model_or_explicit_cold_restart");
        EXPECT_FALSE(restored.References());EXPECT_EQ(restored.SessionAttempt(),previousAttempt);
    }
    else
    {
        EXPECT_EQ(restored.SessionAttempt(),previousAttempt+1);EXPECT_FALSE(restored.Certificate());
        if(complete){ASSERT_TRUE(restored.References());EXPECT_EQ(restored.References()->Inputs(),capture);EXPECT_EQ(restored.IssuedReferenceProbes(),0u);}
        else EXPECT_FALSE(restored.References());
        test->IsNeedToTrain=false;
    }
    const auto stoppedAgain=test->ExportNativeLearnedState(implementation);
    EXPECT_EQ(stoppedAgain["kind"],QJsonValue("timelearner_stopped_state"));EXPECT_TRUE(stoppedAgain["certificate"].isNull());
    EXPECT_EQ(stoppedAgain["model_revision"],package["model_revision"]);
    EXPECT_EQ(stoppedAgain["reference_complete"].toBool(),complete);
    if(scenario!=StoppedCase::ChangedPartial)EXPECT_EQ(stoppedAgain["session_attempt"].toDouble(),double(previousAttempt+1));
    Artifact(rig.name+"_warm_boundary.json",QJsonDocument(stoppedAgain).toJson());
    Artifact(rig.name+"_restored_summary.json",QJsonDocument(EncodeNativeTrainingState(restored,importedRevision(),test->ReadNativeParameters())).toJson());
}
#define STOPPED_CASE(Name,Value) \
TEST(NativeStoppedState,Classic##Name){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::Value,#Name);} \
TEST(NativeStoppedState,Branch##Name){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::Value,#Name);}
STOPPED_CASE(Early,Early)
STOPPED_CASE(Partial,Partial)
STOPPED_CASE(BudgetEarly,BudgetEarly)
STOPPED_CASE(BudgetSearch,BudgetSearch)
STOPPED_CASE(Search,Search)
STOPPED_CASE(Final,Final)
STOPPED_CASE(InvalidProbe,InvalidProbe)
STOPPED_CASE(ChangedPartial,ChangedPartial)
#undef STOPPED_CASE
TEST(NativeStoppedState,ClassicN0BudgetSearch){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::BudgetSearch,"N0BudgetSearch",0);}
TEST(NativeStoppedState,BranchN0BudgetSearch){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::BudgetSearch,"N0BudgetSearch",0);}
TEST(NativeStoppedState,ClassicConfiguredPartial){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::Partial,"ConfiguredPartial",1,true);}
TEST(NativeStoppedState,BranchConfiguredPartial){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::Partial,"ConfiguredPartial",0,true);}
TEST(NativeStoppedState,ClassicN0RepeatedEarly){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::Early,"N0RepeatedEarly",0,true,2);}
TEST(NativeStoppedState,BranchN0RepeatedEarly){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::Early,"N0RepeatedEarly",0,true,2);}
TEST(NativeStoppedState,ClassicN0RepeatedCapture){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::Partial,"N0RepeatedCapture",0,true,2);}
TEST(NativeStoppedState,BranchN0RepeatedCapture){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::Partial,"N0RepeatedCapture",0,true,2);}
TEST(NativeStoppedState,ClassicN0RepeatedHalfCandidate){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::RepeatPartial,"N0RepeatedHalfCandidate",0,true,2);}
TEST(NativeStoppedState,BranchN0RepeatedHalfCandidate){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::RepeatPartial,"N0RepeatedHalfCandidate",0,true,2);}

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

template<class Learner> void PostTuneTransientStimulus(unsigned frequency)
{
    using Owner=PostTuneStimulusLearner<Learner>;
    constexpr bool branch=std::is_base_of<NNeuronTimeLearnerBranch,Learner>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string image=branch?"PostTuneStimulusBranchFixture":"PostTuneStimulusClassicFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new Owner;},image),image);
    EditingRig<Owner> rig(frequency,1,"posttune_transient",false,2,true,2,1,false,image);
    const auto goal=rig.learner->InputPattern.GetData();rig.neuron->TrainingPattern=goal;
    const std::vector<std::vector<double>> patterns{rig.isi,{.02,.12},{0.,.06}};
    rig.learner->ArmPresentations(patterns);const auto original=rig.Revision();
    const auto values=[](const MDMatrix<double>& matrix) {
        QJsonArray result;for(int i=0;i<matrix.GetRows();++i)result.append(matrix(i,0));return result;
    };
    for(int index=1;index<3;++index)
    {
        rig.environment->GetTime().SetTime(1000000);
        ASSERT_TRUE(rig.learner->Present(index));
        auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
        EXPECT_EQ(values(dataset->MatrixData.GetData()),QJsonArray({patterns[index][0],patterns[index][1]}));
        EXPECT_TRUE(NativeTrainingPatternEqual(rig.learner->InputPattern.GetData(),goal));
        EXPECT_TRUE(NativeTrainingPatternEqual(rig.neuron->TrainingPattern.GetData(),goal));
        EXPECT_EQ(rig.learner->CapturedTarget(),patterns.front());EXPECT_EQ(rig.Revision(),original);
        dataset->AdvanceSampleAfterBurst=true;dataset->LoopSamples=false;dataset->StateGeneration=2;
        dataset->Reset();rig.neuron->Reset();dataset->StateGeneration=2;
        const auto stem=rig.name+"_presentation_"+std::to_string(index);
        const double begin=rig.environment->GetTime().GetDoubleTime(),end=begin+.22;
        const unsigned maximum=unsigned(std::ceil(.22*frequency))+3;
        const auto presented=values(dataset->MatrixData.GetData());
        const QJsonObject spec{{"kind","posttune_transient_presentation"},{"schema_version",1},
            {"topology",branch?"branch":"classic"},
            {"trial_id",QString::fromStdString(stem)},{"training_goal",values(goal)},{"presented_isi",presented},
            {"pattern_hash",NmsdkTools::CanonicalModelDataSha256(presented)},
            {"begin",begin},{"end",end},{"maximum_sample_gap",1./frequency},{"maximum_samples",double(maximum)},
            {"channels",branch?1:2},
            {"generation_mode",2},{"advance_sample_after_burst",true},{"loop_samples",false},
            {"model_revision",QString::fromStdString(original)},{"record_spikes",false}};
        Artifact(stem+"_spec.json",QJsonDocument(spec).toJson());
        std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<(branch?1u:2u);++i)trace<<",soma"<<i;
        for(int i=0;i<goal.GetRows();++i)trace<<",training_goal"<<i;
        for(int i=0;i<goal.GetRows();++i)trace<<",presented_isi"<<i;
        trace<<'\n';
        QJsonArray onsets,presentedAtFirst;int phaseAtFirst=-1;double previous=0.,last=begin;
        std::vector<double> lower(branch?1u:2u,std::numeric_limits<double>::infinity()),upper(branch?1u:2u,-std::numeric_limits<double>::infinity());
        bool complete=false;unsigned samples=0;
        for(unsigned tick=0;tick<maximum;++tick)
        {
            rig.model->Calculate();const double time=rig.environment->GetTime().GetDoubleTime(),stimulus=rig.source->Output(0,0);
            ASSERT_TRUE(std::isfinite(stimulus));trace<<time<<','<<stimulus;
            if(stimulus>0. && previous<=0.)
            {
                if(onsets.isEmpty())
                {
                    presentedAtFirst=values(dataset->MatrixData.GetData());phaseAtFirst=rig.learner->TrainingPhase.GetData();
                    rig.learner->ObserveFirstPulse(time);
                }
                onsets.append(time);
            }
            previous=stimulus;
            for(std::size_t i=0;i<(branch?1u:2u);++i)
            {
                auto soma=rig.neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);
                const double value=soma->SumPotential(0,0);ASSERT_TRUE(std::isfinite(value));trace<<','<<value;
                lower[i]=std::min(lower[i],value);upper[i]=std::max(upper[i],value);
            }
            const auto& currentGoal=rig.learner->InputPattern.GetData();
            const auto& currentStimulus=dataset->MatrixData.GetData();
            for(int i=0;i<goal.GetRows();++i)trace<<','<<(currentGoal.GetRows()>i && currentGoal.GetCols()==1?currentGoal(i,0):std::numeric_limits<double>::quiet_NaN());
            for(int i=0;i<goal.GetRows();++i)trace<<','<<(currentStimulus.GetRows()>i && currentStimulus.GetCols()==1?currentStimulus(i,0):std::numeric_limits<double>::quiet_NaN());
            trace<<'\n';last=time;++samples;rig.environment->IncreaseModelTimeByStep();
            if(!Detail::After(end,time)){complete=true;break;}
        }
        EXPECT_TRUE(complete);ASSERT_EQ(onsets.size(),2);
        double variation=0.;for(std::size_t i=0;i<lower.size();++i)variation=std::max(variation,upper[i]-lower[i]);EXPECT_GT(variation,1.e-6);
        const auto expected=rig.learner->ExpectedTimes();ASSERT_EQ(expected.size(),2u);
        EXPECT_DOUBLE_EQ(expected[0],0.);EXPECT_DOUBLE_EQ(expected[1],patterns[index][1]);
        EXPECT_NEAR(onsets[1].toDouble()-onsets[0].toDouble(),expected[1],1./frequency+1.e-12);
        const bool goalPreserved=NativeTrainingPatternEqual(rig.learner->InputPattern.GetData(),goal) &&
            NativeTrainingPatternEqual(rig.neuron->TrainingPattern.GetData(),goal) && rig.learner->CapturedTarget()==patterns.front();
        EXPECT_TRUE(goalPreserved);EXPECT_EQ(rig.Revision(),original);
        QJsonArray expectedTimes;for(double value:expected)expectedTimes.append(value);
        Artifact(stem+".csv",QByteArray::fromStdString(trace.str()));
        QJsonObject observation{{"kind","posttune_transient_observation"},{"schema_version",1},
            {"trial_id",spec["trial_id"]},{"complete",complete},{"sample_count",double(samples)},
            {"last_sample_time",last},{"onsets",onsets},{"expected_relative_times",expectedTimes},
            {"presented_at_first",presentedAtFirst},{"presented_after",values(dataset->MatrixData.GetData())},
            {"phase_at_first",phaseAtFirst},{"phase_after",rig.learner->TrainingPhase.GetData()},
            {"training_goal_after",values(rig.learner->InputPattern.GetData())},{"material_goal_after",values(rig.neuron->TrainingPattern.GetData())},
            {"goal_preserved",goalPreserved},{"frozen_after",QString::fromStdString(rig.Revision())},
            {"scientific_verdict",QJsonValue(QJsonValue::Null)}};
        Artifact(stem+"_observation.json",QJsonDocument(observation).toJson());
    }
    const auto lastGoal=values(rig.learner->InputPattern.GetData());const auto clock=rig.environment->GetTime().GetTime();
    EXPECT_FALSE(rig.learner->Present(-1));EXPECT_FALSE(rig.learner->Present(int(patterns.size())));
    EXPECT_EQ(values(rig.learner->InputPattern.GetData()),lastGoal);EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
}
TEST(PostTuneTransientStimulus,Classic2000){PostTuneTransientStimulus<NNeuronTimeLearner>(2000);}
TEST(PostTuneTransientStimulus,Branch2000){PostTuneTransientStimulus<NNeuronTimeLearnerBranch>(2000);}
TEST(PostTuneTransientStimulus,Classic20000){PostTuneTransientStimulus<NNeuronTimeLearner>(20000);}
TEST(PostTuneTransientStimulus,Branch20000){PostTuneTransientStimulus<NNeuronTimeLearnerBranch>(20000);}

template<class Learner> void PostTuneGraphBoundary(unsigned frequency,int normalization,bool failAttach=false)
{
    using Owner=ImportRollbackLearner<Learner>;
    constexpr bool branch=std::is_base_of<NNeuronTimeLearnerBranch,Learner>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string image=branch?"PostTuneBoundaryBranchFixture":"PostTuneBoundaryClassicFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new Owner;},image),image);
    EditingRig<Owner> rig(frequency,normalization,"posttune_boundary"+std::string(failAttach?"_attach_failure":""),
        false,2,true,2,1,false,image,normalization==0?3:1);
    auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
    auto channel=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);
    auto second=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);ASSERT_TRUE(second);
    channel->Capacity=1.3e-9;second->Capacity=1.7e-9;rig.neuron->MembraneCapacity=0.;
    dataset->Delay=.013;dataset->AdvanceSampleAfterBurst=false;dataset->LoopSamples=true;
    const auto originalRevision=rig.Revision();
    const auto savedDataset=NmsdkTools::IdentifyModel(dataset);
    const double amplitude=rig.source->Amplitude.GetData();
    const auto checkpoint=NativeLearnerGraphCheckpoint::Capture(*rig.learner);ASSERT_TRUE(checkpoint);
    std::vector<NativeProbeSample> before,after;
    rig.environment->GetTime().SetTime(1000000);
    const auto baseline=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const auto& frame){before.push_back(frame);});
    ASSERT_EQ(baseline.status,NativeProbeStatus::Completed);ASSERT_FALSE(before.empty());
    ASSERT_EQ(rig.Revision(),originalRevision);
    channel->Capacity=2.7e-9;second->Capacity=3.1e-9;
    auto synapse=rig.neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_1.ExcSynapse1",true);ASSERT_TRUE(synapse);
    synapse->Resistance=synapse->Resistance.GetData()*1.25;
    auto pattern=dataset->MatrixData.GetData();pattern(0,0)+=.003;dataset->SetMatrixData(pattern);
    dataset->Delay=.05;dataset->AdvanceSampleAfterBurst=true;dataset->LoopSamples=false;
    rig.source->Amplitude=amplitude*.8;
    const auto candidate=rig.Revision();ASSERT_NE(candidate,originalRevision);
    const auto refresh=[&] {
        rig.learner->RefreshGraphAliases();
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        rig.source=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
        rig.ports={{&rig.source->Output,"burst"}};
    };
    if(failAttach)
    {
        const auto current=rig.neuron.Get();const auto clock=rig.environment->GetTime().GetTime();
        rig.learner->failNeuronAttach=true;
        const auto rejected=checkpoint->Restore(*rig.learner);refresh();
        EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected)<<rejected.reason;
        EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rig.neuron.Get(),current);
        EXPECT_EQ(rig.Revision(),candidate);EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
    }
    const auto clock=rig.environment->GetTime().GetTime();
    const auto restored=checkpoint->Restore(*rig.learner);refresh();
    ASSERT_EQ(restored.status,NativeModelBuildStatus::Adopted)<<restored.reason;
    EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);EXPECT_EQ(rig.Revision(),originalRevision);
    EXPECT_EQ(NmsdkTools::IdentifyModel(dataset),savedDataset);
    EXPECT_DOUBLE_EQ(dataset->Delay.GetData(),.013);EXPECT_TRUE(dataset->LoopSamples.GetData());
    EXPECT_FALSE(dataset->AdvanceSampleAfterBurst.GetData());EXPECT_DOUBLE_EQ(rig.source->Amplitude.GetData(),amplitude);
    EXPECT_EQ(dataset->MatrixData.GetRows(),2);EXPECT_DOUBLE_EQ(dataset->MatrixData(0,0),rig.isi[0]);
    EXPECT_DOUBLE_EQ(dataset->MatrixData(1,0),rig.isi[1]);
    EXPECT_DOUBLE_EQ(rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true)->Capacity.GetData(),1.3e-9);
    EXPECT_DOUBLE_EQ(rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true)->Capacity.GetData(),1.7e-9);
    if(normalization==0)ASSERT_TRUE(rig.neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_2.ExcSynapse3",true));
    rig.environment->GetTime().SetTime(1000000);
    const auto replay=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const auto& frame){after.push_back(frame);});
    ASSERT_EQ(replay.status,NativeProbeStatus::Completed);ASSERT_EQ(before.size(),after.size());
    bool exact=true;
    for(std::size_t i=0;i<before.size();++i)
    {
        const bool same=before[i].time==after[i].time && before[i].stimulus==after[i].stimulus && before[i].potentials==after[i].potentials;
        EXPECT_TRUE(same)<<i;exact=exact && same;
    }
    // Repeated rollback is derived from the same immutable boundary, not from
    // the state left by the preceding replay.
    const auto repeated=checkpoint->Restore(*rig.learner);refresh();
    EXPECT_EQ(repeated.status,NativeModelBuildStatus::Adopted)<<repeated.reason;
    EXPECT_EQ(rig.Revision(),originalRevision);
    Artifact(rig.name+"_boundary.json",QJsonDocument(QJsonObject{
        {"kind","native_posttune_graph_boundary"},{"schema_version",1},{"frequency_hz",int(frequency)},
        {"normalization",normalization},{"branch",branch},{"injected_attach_failure",failAttach},
        {"source_identity",checkpoint->NeuronIdentity()},{"restored_identity",NmsdkTools::IdentifyModel(rig.neuron,rig.ports)},
        {"dataset_identity",savedDataset},{"sample_pairs",double(before.size())},{"waveform_exact",exact},
        {"controller_checkpoint",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativePostTuneGraphBoundary,ClassicN0_2000){PostTuneGraphBoundary<NNeuronTimeLearner>(2000,0);}
TEST(NativePostTuneGraphBoundary,BranchN0_2000){PostTuneGraphBoundary<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativePostTuneGraphBoundary,ClassicN1_2000){PostTuneGraphBoundary<NNeuronTimeLearner>(2000,1);}
TEST(NativePostTuneGraphBoundary,BranchN1_2000){PostTuneGraphBoundary<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativePostTuneGraphBoundary,ClassicN0_20000){PostTuneGraphBoundary<NNeuronTimeLearner>(20000,0);}
TEST(NativePostTuneGraphBoundary,BranchN0_20000){PostTuneGraphBoundary<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativePostTuneGraphBoundary,ClassicN1_20000){PostTuneGraphBoundary<NNeuronTimeLearner>(20000,1);}
TEST(NativePostTuneGraphBoundary,BranchN1_20000){PostTuneGraphBoundary<NNeuronTimeLearnerBranch>(20000,1);}
TEST(NativePostTuneGraphBoundary,ClassicAttachFailure){PostTuneGraphBoundary<NNeuronTimeLearner>(2000,1,true);}
TEST(NativePostTuneGraphBoundary,BranchAttachFailure){PostTuneGraphBoundary<NNeuronTimeLearnerBranch>(2000,1,true);}

void RecordPostTuneBoundaryTrainingProof(NativeTrainingPlan& plan,const std::string& caseName,std::size_t channels)
{
    struct Trace {std::ostringstream csv;std::string trial;std::size_t packet=0;};
    auto trace=std::make_shared<Trace>();
    plan.probe.onPrepared=[trace,channels](const PreparedVerificationProbe&,const ProbeSpec& spec) {
        trace->trial=spec.trialId;trace->csv.str({});trace->csv.clear();trace->csv.imbue(std::locale::classic());
        trace->csv<<std::setprecision(17)<<"time,stimulus";
        for(std::size_t i=0;i<channels;++i)trace->csv<<",soma"<<i;trace->csv<<'\n';
    };
    plan.probe.onSample=[trace](const NativeProbeSample& sample) {
        trace->csv<<sample.time<<','<<sample.stimulus;
        for(double value:sample.potentials)trace->csv<<','<<value;trace->csv<<'\n';
    };
    plan.observationSink=[trace,caseName](const NativeProbeResult& result) {
        const auto name=caseName+"_training_proof_"+std::to_string(++trace->packet);
        Artifact(name+".json",QJsonDocument(EncodeNativeProbeEvidence(result)).toJson());
        if(result.observation && result.observation->specification.trialId==trace->trial)
            Artifact(name+".csv",QByteArray::fromStdString(trace->csv.str()));
    };
}

template<class Learner> void NativePostTuneOwnerPolicy(unsigned frequency,int normalization)
{
    EditingRig<Learner> rig(frequency,normalization,"posttune_owner_policy",false,2,true);
    if(frequency==20000)rig.learner->CalculateMode=0;
    auto plan=TrainingPlan(rig);plan.search.tolerances.sync=1.;
    RecordPostTuneBoundaryTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
    rig.learner->BeginNativeTraining(plan);
    for(unsigned tick=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++tick)
    {ASSERT_LT(tick,50000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();
    ASSERT_TRUE(service.Certificate())<<service.Reason();ASSERT_TRUE(service.References());
    ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();
    // CalculateMode=1 requires explicit release by its external owner. Stopping
    // an already completed service retains the existing measured certificate.
    if(rig.learner->CalculateMode.GetData()==1)rig.learner->IsNeedToTrain=false;
    ASSERT_FALSE(rig.learner->IsNeedToTrain.GetData());ASSERT_TRUE(service.Certificate());
    const auto certificate=EncodeTrainingCertificate(*service.Certificate());
    const auto before=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();
    const auto materialGoal=rig.neuron->TrainingPattern.GetData();
    const double threshold=rig.learner->LTZThreshold.GetData(),fixed=rig.learner->FixedLTZThreshold.GetData();
    const double calibrated=rig.learner->CalibratedFixedLTZThreshold.GetData();
    const bool useFixed=rig.learner->UseFixedLTZThreshold.GetData(),automatic=rig.learner->AutoCalibrateFixedLTZThreshold.GetData();
    const auto saved=NativePostTuneOwnerBoundary::Capture(*rig.learner);ASSERT_TRUE(saved);
    std::vector<NativeProbeSample> baseline,replay;
    rig.environment->GetTime().SetTime(1000000);
    const auto first=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const auto& sample){baseline.push_back(sample);});
    ASSERT_EQ(first.status,NativeProbeStatus::Completed);
    auto candidate=parameters;
    if(normalization==0)++candidate[0].synapses;else candidate[0].resistance*=1.1;
    const auto edited=rig.learner->ApplyNativeParameters(candidate);
    ASSERT_EQ(edited.status,NativeEditStatus::Applied)<<edited.reason;
    rig.learner->UseFixedLTZThreshold.SetDataDirect(true);rig.learner->FixedLTZThreshold=fixed+.02;
    rig.learner->LTZThreshold=threshold+.03;
    rig.learner->CalibratedFixedLTZThreshold.SetDataDirect(calibrated+.04);
    rig.learner->AutoCalibrateFixedLTZThreshold.SetDataDirect(!automatic);
    const auto result=saved->Restore(*rig.learner);
    ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;
    rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    rig.source=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);rig.ports={{&rig.source->Output,"burst"}};
    EXPECT_EQ(rig.Revision(),before);EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    EXPECT_TRUE(NativeTrainingPatternEqual(rig.neuron->TrainingPattern.GetData(),materialGoal));
    EXPECT_DOUBLE_EQ(rig.learner->LTZThreshold.GetData(),threshold);EXPECT_DOUBLE_EQ(rig.learner->FixedLTZThreshold.GetData(),fixed);
    EXPECT_DOUBLE_EQ(rig.learner->CalibratedFixedLTZThreshold.GetData(),calibrated);
    EXPECT_EQ(rig.learner->UseFixedLTZThreshold.GetData(),useFixed);EXPECT_EQ(rig.learner->AutoCalibrateFixedLTZThreshold.GetData(),automatic);
    ASSERT_TRUE(service.Certificate());ASSERT_TRUE(service.References());EXPECT_EQ(EncodeTrainingCertificate(*service.Certificate()),certificate);
    EXPECT_TRUE(service.Certificate()->Matches(before,*service.References(),service.Certificate()->Tolerances(),ModelStateKind::LearnedSolo,service.ModelEpoch()));
    rig.environment->GetTime().SetTime(1000000);
    const auto second=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true,
        [&](const auto& sample){replay.push_back(sample);});
    ASSERT_EQ(second.status,NativeProbeStatus::Completed);ASSERT_EQ(baseline.size(),replay.size());
    for(std::size_t i=0;i<baseline.size();++i)
    {EXPECT_EQ(baseline[i].time,replay[i].time);EXPECT_EQ(baseline[i].stimulus,replay[i].stimulus);EXPECT_EQ(baseline[i].potentials,replay[i].potentials);}
    Artifact(rig.name+"_owner_policy.json",QJsonDocument(QJsonObject{{"kind","native_posttune_owner_policy"},{"schema_version",1},
        {"source_model",QString::fromStdString(before)},{"restored_model",QString::fromStdString(rig.Revision())},
        {"source_solo_certificate",certificate},{"certificate_scope","learned_solo"},
        {"fixture_sync_tolerance",plan.search.tolerances.sync},{"calculate_mode",rig.learner->CalculateMode.GetData()},
        {"sample_pairs",double(baseline.size())},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
class NativeOwnerConfigSource : public UNet {
public:
    UProperty<double,NativeOwnerConfigSource,ptOutput|ptPubState> Resistance0,Resistance1;
    UProperty<int,NativeOwnerConfigSource,ptOutput|ptPubState> MaximumLength,Integer0,Integer1;
    NativeOwnerConfigSource():Resistance0("Resistance0",this),Resistance1("Resistance1",this),MaximumLength("MaximumLength",this),Integer0("Integer0",this),Integer1("Integer1",this){}
    NativeOwnerConfigSource* New(void) override {return new NativeOwnerConfigSource;}
};
template<class Learner> void RejectConnectedNativeOwnerConfiguration(bool importing,bool scalar,bool matching=false)
{
    EditingRig<Learner> rig(2000,0,std::string("owner_binding_")+(importing?"import_":"construct_")+(scalar?"scalar":"vector")+(matching?"_matching":""),false,2,true);
    NativeEditSpec policy;policy.maximumCableLength=8;
    const auto declaration=DescribeNativeLearnerModel(*rig.learner,rig.branch,Normalization::SynapseCount,
        rig.learner->DendriteLength.GetData(),policy);
    QJsonObject package;
    if(importing)
    {
        auto plan=TrainingPlan(rig);plan.search.tolerances.sync=1.;
        RecordPostTuneBoundaryTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
        rig.learner->BeginNativeTraining(plan);
        for(unsigned tick=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++tick)
        {ASSERT_LT(tick,50000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
        ASSERT_TRUE(rig.learner->NativeTrainingController().Certificate());rig.learner->IsNeedToTrain=false;
        package=rig.learner->ExportNativeLearnedState("native_owner_binding_v1");
        Artifact(rig.name+"_source_solo.json",QJsonDocument(package).toJson());
    }
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="NativeOwnerConfigSourceFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new NativeOwnerConfigSource;},image),image);
    auto source=dynamic_pointer_cast<NativeOwnerConfigSource>(core.storage->TakeObject(image));ASSERT_TRUE(source);
    source->Name="OwnerConfigSource";UEPtr<UContainer> component=source;
    ASSERT_NE(rig.model->AddComponent(component),ForbiddenId);source->Init();
    auto resistances=rig.learner->TipSynapseResistance.GetData();if(!matching)resistances[0]*=1.03125;
    const int maximum=rig.learner->MaxDendriteLength.GetData()+(matching?0:1);
    source->Resistance0=resistances[0];source->Resistance1=resistances[1];source->MaximumLength=maximum;
    if(scalar)ASSERT_TRUE(rig.learner->MaxDendriteLength.SetPointer(0,&source->MaximumLength));
    else
    {
        // A vector input collects scalar outputs; vector-to-vector SetPointer
        // is not this Rdk input protocol and cannot establish this control.
        ASSERT_TRUE(rig.learner->TipSynapseResistance.SetPointer(0,&source->Resistance0));
        ASSERT_TRUE(rig.learner->TipSynapseResistance.SetPointer(1,&source->Resistance1));
        ASSERT_EQ(rig.learner->TipSynapseResistance.GetData(),resistances);
    }
    const auto old=rig.learner->GetComponent("Neuron",true).Get();
    const auto result=importing?rig.learner->ImportNativeLearnedState(package,"native_owner_binding_v1"):
        rig.learner->ConstructNativeModel(declaration);
    QJsonArray before,after;for(double r:resistances)before.append(r);
    after.append(source->Resistance0.GetData());after.append(source->Resistance1.GetData());
    Artifact(rig.name+"_owner_binding.json",QJsonDocument(QJsonObject{
        {"kind","native_owner_configuration_binding"},{"schema_version",1},{"importing",importing},{"scalar",scalar},{"matching",matching},
        {"status",NativeModelBuildStatusName(result.status)},{"reason",QString::fromStdString(result.reason)},
        {"model_may_have_changed",result.modelMayHaveChanged},
        {"graph_replaced",rig.learner->GetComponent("Neuron",true).Get()!=old},
        {"source_vector_before",before},{"source_vector_after",after},
        {"source_scalar_before",maximum},{"source_scalar_after",source->MaximumLength.GetData()},
        {"requested_scalar",declaration.editPolicy.maximumCableLength},
        {"owner_scalar_after",rig.learner->MaxDendriteLength.GetData()},
        {"owner_vector_after",[&]{QJsonArray v;for(double r:rig.learner->TipSynapseResistance.GetData())v.append(r);return v;}()},
        {"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    EXPECT_EQ((std::vector<double>{source->Resistance0.GetData(),source->Resistance1.GetData()}),resistances);
    EXPECT_EQ(source->MaximumLength.GetData(),maximum);
    if(matching)
    {
        ASSERT_EQ(result.status,importing?NativeModelBuildStatus::Adopted:NativeModelBuildStatus::Constructed)<<result.reason;
    }
    else
    {
        ASSERT_EQ(result.status,NativeModelBuildStatus::Rejected)<<result.reason;
        EXPECT_EQ(result.reason,std::string("native_model_owner_assignment_is_external:")+
            (scalar?"MaxDendriteLength":"TipSynapseResistance"));
        EXPECT_FALSE(result.modelMayHaveChanged);EXPECT_EQ(rig.learner->GetComponent("Neuron",true).Get(),old);
    }
    if(scalar)
    {
        EXPECT_TRUE(rig.learner->MaxDendriteLength.IsConnected());
        EXPECT_EQ(rig.learner->MaxDendriteLength.GetDataSources(),(std::vector<const UIProperty*>{&source->MaximumLength}));
    }
    else
    {
        EXPECT_TRUE(rig.learner->TipSynapseResistance.IsConnected());
        EXPECT_EQ(rig.learner->TipSynapseResistance.GetDataSources(),(std::vector<const UIProperty*>{&source->Resistance0,&source->Resistance1}));
    }
    if(importing)
    {
        ASSERT_TRUE(rig.learner->NativeTrainingController().Certificate());
        EXPECT_EQ(EncodeTrainingCertificate(*rig.learner->NativeTrainingController().Certificate()),package["certificate"].toObject());
    }
}

// Native editor metadata uses the same Rdk collection protocol as construction:
// each connected vector is assembled from real scalar output properties.
template<class Learner> void NativeOwnerParameterBinding(int field,bool matching)
{
    const std::string property=field==0?"DendriteLength":field==1?"NumSynapse":"TipSynapseResistance";
    EditingRig<Learner> rig(2000,field==2?1:0,"editor_binding_"+property+(matching?"_matching":"_conflict"),false,2,true);
    const auto boundary=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,true);
    ASSERT_EQ(boundary.status,NativeProbeStatus::Completed);ASSERT_TRUE(boundary.observation);
    ASSERT_TRUE(boundary.observation->complete);ASSERT_TRUE(boundary.observation->valid);
    const auto previous=rig.learner->ReadNativeParameters();auto requested=previous;
    if(matching)
    {
        if(field==0)++requested[0].synapses;else ++requested[0].length;
    }
    else if(field==0)++requested[0].length;
    else if(field==1)++requested[0].synapses;
    else requested[0].resistance*=1.03125;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="NativeOwnerConfigSourceFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new NativeOwnerConfigSource;},image),image);
    auto source=dynamic_pointer_cast<NativeOwnerConfigSource>(core.storage->TakeObject(image));ASSERT_TRUE(source);
    source->Name="EditorConfigSource";UEPtr<UContainer> component=source;
    ASSERT_NE(rig.model->AddComponent(component),ForbiddenId);source->Init();
    source->Resistance0=previous[0].resistance;source->Resistance1=previous[1].resistance;
    source->Integer0=field==0?previous[0].length:previous[0].synapses;
    source->Integer1=field==0?previous[1].length:previous[1].synapses;
    if(field==2)
    {
        ASSERT_TRUE(rig.learner->TipSynapseResistance.SetPointer(0,&source->Resistance0));
        ASSERT_TRUE(rig.learner->TipSynapseResistance.SetPointer(1,&source->Resistance1));
    }
    else
    {
        auto& target=field==0?rig.learner->DendriteLength:rig.learner->NumSynapse;
        ASSERT_TRUE(target.SetPointer(0,&source->Integer0));ASSERT_TRUE(target.SetPointer(1,&source->Integer1));
    }
    const auto before=rig.Revision();const auto result=rig.learner->ApplyNativeParameters(requested);const auto after=rig.Revision();
    auto encode=[](const std::vector<InputParameters>& values){QJsonArray out;for(const auto& v:values)
        out.append(QJsonObject{{"length",v.length},{"synapses",v.synapses},{"resistance",v.resistance}});return out;};
    auto ints=[](const auto& values){QJsonArray out;for(auto v:values)out.append(v);return out;};
    Artifact(rig.name+"_editor_binding.json",QJsonDocument(QJsonObject{
        {"kind","native_owner_editor_binding"},{"schema_version",1},{"property",QString::fromStdString(property)},
        {"matching",matching},{"status",NativeEditStatusName(result.status)},{"reason",QString::fromStdString(result.reason)},
        {"model_may_have_changed",result.modelMayHaveChanged},{"model_before",QString::fromStdString(before)},
        {"model_after",QString::fromStdString(after)},{"previous",encode(previous)},{"requested",encode(requested)},
        {"effective",encode(result.effective)},{"owner_lengths",ints(rig.learner->DendriteLength.GetData())},
        {"owner_counts",ints(rig.learner->NumSynapse.GetData())},{"owner_resistances",ints(rig.learner->TipSynapseResistance.GetData())},
        {"source_integers",QJsonArray{source->Integer0.GetData(),source->Integer1.GetData()}},
        {"source_resistances",QJsonArray{source->Resistance0.GetData(),source->Resistance1.GetData()}},
        {"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    EXPECT_EQ(source->Integer0.GetData(),field==0?previous[0].length:previous[0].synapses);
    EXPECT_EQ(source->Integer1.GetData(),field==0?previous[1].length:previous[1].synapses);
    EXPECT_DOUBLE_EQ(source->Resistance0.GetData(),previous[0].resistance);EXPECT_DOUBLE_EQ(source->Resistance1.GetData(),previous[1].resistance);
    if(matching)
    {
        ASSERT_EQ(result.status,NativeEditStatus::Applied)<<result.reason;
        EXPECT_EQ(result.effective,requested);EXPECT_NE(before,after);
        EXPECT_EQ(rig.learner->ReadNativeParameters(),requested);
        for(std::size_t i=0;i<requested.size();++i)
        {
            EXPECT_EQ(rig.learner->DendriteLength.GetData()[i],requested[i].length);
            EXPECT_EQ(rig.learner->NumSynapse.GetData()[i],requested[i].synapses);
            EXPECT_DOUBLE_EQ(rig.learner->TipSynapseResistance.GetData()[i],requested[i].resistance);
        }
    }
    else
    {
        ASSERT_EQ(result.status,NativeEditStatus::Rejected)<<result.reason;
        EXPECT_EQ(result.reason,"native_model_owner_assignment_is_external:"+property);
        EXPECT_FALSE(result.modelMayHaveChanged);EXPECT_EQ(before,after);
        EXPECT_EQ(rig.learner->ReadNativeParameters(),previous);
    }
    if(field==2)EXPECT_EQ(rig.learner->TipSynapseResistance.GetDataSources(),(std::vector<const UIProperty*>{&source->Resistance0,&source->Resistance1}));
    else EXPECT_EQ((field==0?rig.learner->DendriteLength:rig.learner->NumSynapse).GetDataSources(),(std::vector<const UIProperty*>{&source->Integer0,&source->Integer1}));
}
TEST(NativeOwnerParameterBindings,ClassicLengthConflict){NativeOwnerParameterBinding<NNeuronTimeLearner>(0,false);}
TEST(NativeOwnerParameterBindings,BranchLengthConflict){NativeOwnerParameterBinding<NNeuronTimeLearnerBranch>(0,false);}
TEST(NativeOwnerParameterBindings,ClassicCountConflict){NativeOwnerParameterBinding<NNeuronTimeLearner>(1,false);}
TEST(NativeOwnerParameterBindings,BranchCountConflict){NativeOwnerParameterBinding<NNeuronTimeLearnerBranch>(1,false);}
TEST(NativeOwnerParameterBindings,ClassicResistanceConflict){NativeOwnerParameterBinding<NNeuronTimeLearner>(2,false);}
TEST(NativeOwnerParameterBindings,BranchResistanceConflict){NativeOwnerParameterBinding<NNeuronTimeLearnerBranch>(2,false);}
TEST(NativeOwnerParameterBindings,ClassicLengthMatching){NativeOwnerParameterBinding<NNeuronTimeLearner>(0,true);}
TEST(NativeOwnerParameterBindings,BranchLengthMatching){NativeOwnerParameterBinding<NNeuronTimeLearnerBranch>(0,true);}
TEST(NativeOwnerParameterBindings,ClassicCountMatching){NativeOwnerParameterBinding<NNeuronTimeLearner>(1,true);}
TEST(NativeOwnerParameterBindings,BranchCountMatching){NativeOwnerParameterBinding<NNeuronTimeLearnerBranch>(1,true);}
TEST(NativeOwnerParameterBindings,ClassicResistanceMatching){NativeOwnerParameterBinding<NNeuronTimeLearner>(2,true);}
TEST(NativeOwnerParameterBindings,BranchResistanceMatching){NativeOwnerParameterBinding<NNeuronTimeLearnerBranch>(2,true);}

TEST(NativeOwnerConfigurationBindings,ClassicConstructVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(false,false);}
TEST(NativeOwnerConfigurationBindings,BranchConstructVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(false,false);}
TEST(NativeOwnerConfigurationBindings,ClassicConstructScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(false,true);}
TEST(NativeOwnerConfigurationBindings,BranchConstructScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(false,true);}
TEST(NativeOwnerConfigurationBindings,ClassicImportVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(true,false);}
TEST(NativeOwnerConfigurationBindings,BranchImportVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(true,false);}
TEST(NativeOwnerConfigurationBindings,ClassicImportScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(true,true);}
TEST(NativeOwnerConfigurationBindings,BranchImportScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(true,true);}
TEST(NativeOwnerConfigurationBindings,ClassicMatchingConstructVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(false,false,true);}
TEST(NativeOwnerConfigurationBindings,BranchMatchingConstructVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(false,false,true);}
TEST(NativeOwnerConfigurationBindings,ClassicMatchingConstructScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(false,true,true);}
TEST(NativeOwnerConfigurationBindings,BranchMatchingConstructScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(false,true,true);}
TEST(NativeOwnerConfigurationBindings,ClassicMatchingImportVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(true,false,true);}
TEST(NativeOwnerConfigurationBindings,BranchMatchingImportVector){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(true,false,true);}
TEST(NativeOwnerConfigurationBindings,ClassicMatchingImportScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearner>(true,true,true);}
TEST(NativeOwnerConfigurationBindings,BranchMatchingImportScalar){RejectConnectedNativeOwnerConfiguration<NNeuronTimeLearnerBranch>(true,true,true);}

TEST(NativePostTuneOwnerPolicy,ClassicN0_2000){NativePostTuneOwnerPolicy<NNeuronTimeLearner>(2000,0);}
TEST(NativePostTuneOwnerPolicy,BranchN0_2000){NativePostTuneOwnerPolicy<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativePostTuneOwnerPolicy,ClassicN1_2000){NativePostTuneOwnerPolicy<NNeuronTimeLearner>(2000,1);}
TEST(NativePostTuneOwnerPolicy,BranchN1_2000){NativePostTuneOwnerPolicy<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativePostTuneOwnerPolicy,ClassicN1_20000){NativePostTuneOwnerPolicy<NNeuronTimeLearner>(20000,1);}
TEST(NativePostTuneOwnerPolicy,BranchN1_20000){NativePostTuneOwnerPolicy<NNeuronTimeLearnerBranch>(20000,1);}

class PostTunePolicyOutput : public UNet {
public:
    UProperty<double,PostTunePolicyOutput,ptOutput|ptPubState> Value;
    PostTunePolicyOutput():Value("Value",this){Value=.731;}
    PostTunePolicyOutput* New(void) override {return new PostTunePolicyOutput;}
};
TEST(NativePostTuneOwnerPolicy,ConnectedPropertyRejectsRestoreBeforeAnyEdit)
{
    EditingRig<NNeuronTimeLearner> rig(2000,1,"posttune_owner_connected",false,2,true);
    rig.learner->IsNeedToTrain.SetDataDirect(false);
    const auto saved=NativePostTuneOwnerBoundary::Capture(*rig.learner);
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="PostTunePolicyOutputFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new PostTunePolicyOutput;},image),image);
    auto output=dynamic_pointer_cast<PostTunePolicyOutput>(core.storage->TakeObject(image));ASSERT_TRUE(output);
    output->Name="PostTunePolicySource";UEPtr<UContainer> component=output;
    ASSERT_NE(rig.model->AddComponent(component),ForbiddenId);output->Init();
    ASSERT_TRUE(rig.learner->FixedLTZThreshold.SetPointer(0,&output->Value));
    const auto before=rig.Revision();const auto old=rig.neuron.Get();const double value=output->Value.GetData();
    const auto rejected=saved->Restore(*rig.learner);
    EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(rejected.modelMayHaveChanged);
    EXPECT_EQ(rejected.reason,"posttune_boundary_connected_owner_property");
    EXPECT_DOUBLE_EQ(output->Value.GetData(),value);EXPECT_EQ(rig.Revision(),before);
    EXPECT_EQ(rig.learner->GetComponent("Neuron",true).Get(),old);
    EXPECT_THROW(NativePostTuneOwnerBoundary::Capture(*rig.learner),std::logic_error);
    rig.learner->FixedLTZThreshold.DetachFrom();
}
TEST(NativePostTuneOwnerPolicy,RetargetIsNotOverwrittenByRollback)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,1,"posttune_owner_retarget",false,2,true);
    rig.learner->IsNeedToTrain.SetDataDirect(false);
    const auto saved=NativePostTuneOwnerBoundary::Capture(*rig.learner);
    auto pattern=rig.learner->InputPattern.GetData();pattern(1,0)+=.01;rig.learner->InputPattern=pattern;
    auto dataset=rig.learner->GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    rig.source=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);rig.ports={{&rig.source->Output,"burst"}};
    const auto before=rig.Revision();
    const auto rejected=saved->Restore(*rig.learner);
    EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(rejected.modelMayHaveChanged);
    EXPECT_EQ(rejected.reason,"posttune_boundary_training_target_changed");
    EXPECT_EQ(rig.Revision(),before);EXPECT_DOUBLE_EQ(rig.learner->InputPattern(1,0),pattern(1,0));
}

class PostTuneProvenanceLearner : public NNeuronTimeLearner {
public:
    PostTuneProvenanceLearner* New(void) override {return new PostTuneProvenanceLearner;}
    void ReplayBoundary(const std::string& referenceSuffix)
    {
        auto plan=NativeTrainingControl.Plan();auto references=NativeTrainingControl.ReferencePackets();
        auto finals=NativeTrainingControl.FinalPackets();
        const auto revision=NativeTrainingControl.Certificate()->ModelRevision();
        const auto epoch=NativeTrainingControl.ModelEpoch(),attempt=NativeTrainingControl.SessionAttempt();
        // Corruption/control metadata derived from ACTUAL observed packets;
        // these are not newly observed trials or a scientific replay claim.
        for(auto& packet:references)
        {
            if(packet.requestedSpecification)packet.requestedSpecification->trialId+=referenceSuffix;
            packet.observation->specification.trialId+=referenceSuffix;
        }
        NativeTrainingControl.RestoreBoundary(std::move(plan),std::move(references),std::move(finals),revision,epoch,attempt);
    }
};
TEST(NativePostTuneOwnerPolicy,EquivalentCertificateCannotHideChangedReferenceProvenance)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="PostTuneProvenanceFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new PostTuneProvenanceLearner;},image),image);
    EditingRig<PostTuneProvenanceLearner> rig(2000,0,"posttune_owner_provenance",false,2,true,2,1,false,image);
    auto plan=TrainingPlan(rig);plan.search.tolerances.sync=1.;
    RecordPostTuneBoundaryTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
    rig.learner->BeginNativeTraining(plan);
    for(unsigned tick=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++tick)
    {ASSERT_LT(tick,50000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    ASSERT_TRUE(rig.learner->NativeTrainingController().Certificate());
    ASSERT_EQ(rig.learner->NativeTrainingController().Outcome(),TrainingStatus::Exact);
    rig.learner->IsNeedToTrain=false;ASSERT_FALSE(rig.learner->IsNeedToTrain.GetData());
    // Normalize to the real completed-boundary import semantics on both sides:
    // reason/state/attempt/epoch/certificate remain equal after the second import.
    rig.learner->ReplayBoundary("");
    const auto& controller=rig.learner->NativeTrainingController();
    const auto certificate=EncodeTrainingCertificate(*controller.Certificate());
    const auto reason=controller.Reason(),revision=rig.Revision();
    const auto attempt=controller.SessionAttempt(),epoch=controller.ModelEpoch();
    const auto snapshot=NativePostTuneOwnerBoundary::Capture(*rig.learner);
    const auto previousTrial=controller.ReferencePackets().front().observation->specification.trialId;
    rig.learner->ReplayBoundary("/changed_provenance_control");
    ASSERT_EQ(EncodeTrainingCertificate(*controller.Certificate()),certificate);
    ASSERT_EQ(controller.Reason(),reason);ASSERT_EQ(controller.SessionAttempt(),attempt);ASSERT_EQ(controller.ModelEpoch(),epoch);
    ASSERT_NE(controller.ReferencePackets().front().observation->specification.trialId,previousTrial);
    const auto old=rig.neuron.Get();const auto rejected=snapshot->Restore(*rig.learner);
    ASSERT_EQ(rejected.status,NativeModelBuildStatus::Rejected)<<rejected.reason;
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rejected.reason,"posttune_boundary_training_controller_changed");
    EXPECT_EQ(rig.Revision(),revision);EXPECT_EQ(rig.learner->GetComponent("Neuron",true).Get(),old);
    Artifact(rig.name+"_provenance_guard.json",QJsonDocument(QJsonObject{
        {"kind","native_boundary_reference_provenance_guard"},{"schema_version",1},
        {"same_certificate",certificate},{"previous_reference_trial",QString::fromStdString(previousTrial)},
        {"new_reference_trial",QString::fromStdString(controller.ReferencePackets().front().observation->specification.trialId)},
        {"metadata_corruption_control",true},{"reason",QString::fromStdString(rejected.reason)},
        {"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}

enum class BoundaryRejection { OwnerReset,WrongOwner,OwnerMember,ExternalListener };
void RejectStalePostTuneBoundary(BoundaryRejection scenario)
{
    EditingRig<NNeuronTimeLearnerBranch> rig(2000,1,"boundary_guard_"+std::to_string(int(scenario)),false,2,true);
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const auto checkpoint=NativeLearnerGraphCheckpoint::Capture(*rig.learner);ASSERT_TRUE(checkpoint);
    UEPtr<NPulseGeneratorTransit> tap;
    if(scenario==BoundaryRejection::OwnerReset)rig.learner->Reset();
    if(scenario==BoundaryRejection::OwnerMember || scenario==BoundaryRejection::ExternalListener)
    {
        tap=dynamic_pointer_cast<NPulseGeneratorTransit>(core.storage->TakeObject("NPulseGeneratorTransit"));ASSERT_TRUE(tap);
        tap->Name="BoundaryGuardTap";UEPtr<UContainer> component=tap;
        auto& owner=scenario==BoundaryRejection::OwnerMember?static_cast<UNet&>(*rig.learner):*dynamic_pointer_cast<UNet>(rig.model);
        ASSERT_NE(owner.AddComponent(component),ForbiddenId);tap->Init();
        if(scenario==BoundaryRejection::ExternalListener)
        {
            auto channel=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(channel);
            ASSERT_TRUE(tap->Input.SetPointer(0,&channel->Output));
        }
    }
    const auto before=rig.Revision();const auto clock=rig.environment->GetTime().GetTime();
    const auto neuron=rig.neuron.Get();std::vector<NameT> order;rig.learner->GetComponentsList(order);
    const auto rejected=checkpoint->Restore(scenario==BoundaryRejection::WrongOwner?*dynamic_pointer_cast<UNet>(rig.model):*rig.learner);
    ASSERT_EQ(rejected.status,NativeModelBuildStatus::Rejected)<<rejected.reason;
    EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_FALSE(rejected.reason.empty());
    EXPECT_EQ(rig.learner->GetComponent("Neuron",true).Get(),neuron);EXPECT_EQ(rig.Revision(),before);
    EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
    std::vector<NameT> after;rig.learner->GetComponentsList(after);EXPECT_EQ(after,order);
    if(scenario==BoundaryRejection::OwnerReset)EXPECT_EQ(rejected.reason,"boundary_checkpoint_owner_lifecycle_changed");
    if(scenario==BoundaryRejection::WrongOwner)EXPECT_EQ(rejected.reason,"boundary_checkpoint_context_changed");
    if(scenario==BoundaryRejection::ExternalListener)
    {
        EXPECT_EQ(rejected.reason,"native_cold_replace_has_external_listener");
        ASSERT_EQ(tap->Input.GetDataSources().size(),1u);tap->Input.DetachFrom();
    }
    Artifact(rig.name+"_guard.json",QJsonDocument(QJsonObject{{"kind","native_boundary_guard"},{"schema_version",1},
        {"scenario",int(scenario)},{"reason",QString::fromStdString(rejected.reason)},
        {"unchanged_revision",QString::fromStdString(before)},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativePostTuneBoundaryGuards,OwnerResetInvalidatesCheckpoint){RejectStalePostTuneBoundary(BoundaryRejection::OwnerReset);}
TEST(NativePostTuneBoundaryGuards,DifferentOwnerCannotRestore){RejectStalePostTuneBoundary(BoundaryRejection::WrongOwner);}
TEST(NativePostTuneBoundaryGuards,OwnerMembershipChangeIsRejected){RejectStalePostTuneBoundary(BoundaryRejection::OwnerMember);}
TEST(NativePostTuneBoundaryGuards,ExternalListenerIsPreserved){RejectStalePostTuneBoundary(BoundaryRejection::ExternalListener);}

void PostTuneReconstruction(unsigned frequency,int mode,bool failAttach=false,bool listener=false,int normalization=1)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="PostTuneRebuildBranchFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new PostTuneRebuildBranch;},image),image);
    const auto suffix="posttune_native_mode"+std::to_string(mode)+(failAttach?"_rollback":listener?"_listener":"");
    EditingRig<PostTuneRebuildBranch> rig(frequency,normalization,suffix,false,2,true,2,1,false,image,normalization==0?3:1);
    if(normalization==0)
    {
        ASSERT_TRUE(rig.neuron->GetComponentL<NPulseSynapseCommon>("Dendrite1_2.ExcSynapse3",true));
    }
    auto exc=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);
    auto other=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
    auto inh=rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true);ASSERT_TRUE(exc);ASSERT_TRUE(other);ASSERT_TRUE(inh);
    exc->Capacity=1.3e-9;other->Capacity=1.7e-9;inh->Capacity=2.3e-9;
    // Parent zero is legal when physics is owned by heterogeneous child images.
    // Rebuilding must never replace these capacities with a 1 nF fallback.
    rig.neuron->MembraneCapacity=0.;rig.learner->PreparePostTune(mode);
    const auto before=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);const auto parameters=rig.learner->ReadNativeParameters();
    std::vector<NameT> order;rig.learner->GetComponentsList(order);const auto old=rig.neuron;
    const auto measure=[&](const std::string& phase,std::vector<NativeProbeSample>& frames) {
        rig.environment->GetTime().SetTime(1000000);
        auto dataset=rig.learner->GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
        // One complete declared presentation, followed by the full response
        // window. Dataset's default continuous policy would repeat the burst.
        dataset->AdvanceSampleAfterBurst=true;dataset->LoopSamples=false;
        dataset->Reset();rig.neuron->Reset();dataset->StateGeneration=2;
        auto soma=rig.neuron->GetComponentL<NPulseMembrane>("Soma1",true);ASSERT_TRUE(soma);
        const double begin=rig.environment->GetTime().GetDoubleTime(),end=begin+rig.duration;
        const unsigned maximumSamples=unsigned(std::ceil(rig.duration*frequency))+3;
        const auto revision=rig.Revision();NmsdkTools::ModelRevisionObserver observer;
        QJsonArray pattern;for(int i=0;i<dataset->MatrixData.GetRows();++i)pattern.append(dataset->MatrixData(i,0));
        const QJsonObject spec{{"kind","posttune_parallel_transport_spec"},{"schema_version",1},
            {"trial_id",QString::fromStdString(rig.name+"/"+phase)},{"model_revision",QString::fromStdString(revision)},
            {"begin",begin},{"end",end},{"maximum_sample_gap",1./frequency},{"maximum_samples",double(maximumSamples)},
            {"channels",1},{"record_spikes",false},{"input_isi",pattern},{"dataset_delay",dataset->Delay.GetData()},
            {"pattern_hash",NmsdkTools::CanonicalModelDataSha256(pattern)},{"generation_mode",2},
            {"advance_sample_after_burst",true},{"loop_samples",false}};
        Artifact(rig.name+"_"+phase+"_spec.json",QJsonDocument(spec).toJson());
        bool complete=false,emitted=false;double low=std::numeric_limits<double>::infinity(),high=-low;
        std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus,soma0\n";
        for(unsigned tick=0;tick<maximumSamples;++tick)
        {
            rig.model->Calculate();NativeProbeSample sample;
            sample.time=rig.environment->GetTime().GetDoubleTime();sample.stimulus=rig.source->Output(0,0);
            const double value=soma->SumPotential(0,0);ASSERT_TRUE(std::isfinite(sample.stimulus) && std::isfinite(value));
            sample.potentials={value};frames.push_back(sample);emitted=emitted || sample.stimulus>0.;low=std::min(low,value);high=std::max(high,value);
            EXPECT_EQ(observer.Read(rig.neuron,rig.ports).toStdString(),revision);
            trace<<sample.time<<','<<sample.stimulus<<','<<value<<'\n';rig.environment->IncreaseModelTimeByStep();
            if(!Detail::After(end,sample.time)){complete=true;break;}
        }
        ASSERT_FALSE(frames.empty());EXPECT_TRUE(complete);EXPECT_TRUE(emitted);EXPECT_GT(high-low,1.e-6);
        EXPECT_EQ(rig.Revision(),revision);
        Artifact(rig.name+"_"+phase+".csv",QByteArray::fromStdString(trace.str()));
        Artifact(rig.name+"_"+phase+"_observation.json",QJsonDocument(QJsonObject{
            {"kind","posttune_parallel_transport_observation"},{"schema_version",1},{"trial_id",spec["trial_id"]},
            {"model_revision",QString::fromStdString(revision)},{"frozen_after",QString::fromStdString(rig.Revision())},
            {"complete",complete},{"sample_count",double(frames.size())},{"last_sample_time",frames.back().time},
            {"emitted",emitted},{"soma_variation",high-low},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    };
    std::vector<NativeProbeSample> baseline,reconstructed;measure("before",baseline);ASSERT_FALSE(baseline.empty());
    EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),before);
    UEPtr<NPulseGeneratorTransit> tap;
    if(listener)
    {
        tap=dynamic_pointer_cast<NPulseGeneratorTransit>(core.storage->TakeObject("NPulseGeneratorTransit"));ASSERT_TRUE(tap);
        tap->Name="PostTuneExternalListener";UEPtr<UContainer> node=tap;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);tap->Init();
        ASSERT_TRUE(tap->Input.SetPointer(0,&other->Output));
    }
    const auto connectors=rig.source->Output.GetNumConnectors();const auto clock=rig.environment->GetTime().GetTime();
    rig.learner->failNeuronAttach=failAttach;const bool rebuilt=rig.learner->Reconstruct();
    EXPECT_EQ(rebuilt,!failAttach && !listener);EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
    rig.neuron=rig.learner->GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(rig.neuron);
    EXPECT_EQ(rig.neuron.Get()==old.Get(),failAttach || listener);
    EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),before);
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);EXPECT_EQ(rig.source->Output.GetNumConnectors(),connectors);
    if(normalization==0)
    {
        ASSERT_EQ(rig.learner->ReadNativeParameters()[0].synapses,3);
        ASSERT_TRUE(rig.neuron->GetComponentL<NPulseSynapseCommon>("Dendrite1_2.ExcSynapse3",true));
    }
    std::vector<NameT> afterOrder;rig.learner->GetComponentsList(afterOrder);EXPECT_EQ(afterOrder,order);
    EXPECT_DOUBLE_EQ(rig.neuron->MembraneCapacity.GetData(),0.);
    EXPECT_DOUBLE_EQ(rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true)->Capacity.GetData(),1.3e-9);
    EXPECT_DOUBLE_EQ(rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true)->Capacity.GetData(),1.7e-9);
    EXPECT_DOUBLE_EQ(rig.neuron->GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true)->Capacity.GetData(),2.3e-9);
    if(listener){ASSERT_EQ(tap->Input.GetDataSources().size(),1u);EXPECT_EQ(tap->Input.GetDataSources().front(),&other->Output);tap->Input.DetachFrom();}
    measure("after",reconstructed);ASSERT_EQ(baseline.size(),reconstructed.size());
    bool waveformExact=true;
    for(std::size_t i=0;i<baseline.size();++i)
    {
        const bool same=baseline[i].time==reconstructed[i].time && baseline[i].stimulus==reconstructed[i].stimulus && baseline[i].potentials==reconstructed[i].potentials;
        EXPECT_TRUE(same)<<i;waveformExact=waveformExact && same;
    }
    Artifact(rig.name+"_reconstruction.json",QJsonDocument(QJsonObject{{"kind","posttune_native_reconstruction"},{"schema_version",1},
        {"mode",mode},{"frequency",double(frequency)},
        {"reconstructed",rebuilt},{"injected_attach_failure",failAttach},{"external_listener",listener},
        {"before_model",before},{"after_model",NmsdkTools::IdentifyModel(rig.neuron,rig.ports)},
        {"samples",double(baseline.size())},{"waveform_exact",waveformExact},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativePostTuneReconstruction,Off){PostTuneReconstruction(2000,PostTrainTune::kPostTipOff);}
TEST(NativePostTuneReconstruction,CanonRmin){PostTuneReconstruction(2000,PostTrainTune::kPostTipCanonRmin);}
TEST(NativePostTuneReconstruction,FlatLastR){PostTuneReconstruction(2000,PostTrainTune::kPostTipFlatLastR);}
TEST(NativePostTuneReconstruction,KeepDone){PostTuneReconstruction(2000,PostTrainTune::kPostTipKeepDone);}
TEST(NativePostTuneReconstruction,SearchSyntheticSeed){PostTuneReconstruction(2000,PostTrainTune::kPostTipSearchSynthetic);}
TEST(NativePostTuneReconstruction,KeepDone20000){PostTuneReconstruction(20000,PostTrainTune::kPostTipKeepDone);}
TEST(NativePostTuneReconstruction,N0PreservesMultipleSynapses){PostTuneReconstruction(2000,PostTrainTune::kPostTipOff,false,false,0);}
TEST(NativePostTuneReconstruction,N0PreservesMultipleSynapses20000){PostTuneReconstruction(20000,PostTrainTune::kPostTipOff,false,false,0);}
TEST(NativePostTuneReconstruction,AttachFailureRollsBack){PostTuneReconstruction(2000,PostTrainTune::kPostTipKeepDone,true);}
TEST(NativePostTuneReconstruction,ExternalListenerRejectsBeforeReplacement){PostTuneReconstruction(2000,PostTrainTune::kPostTipKeepDone,false,true);}

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
