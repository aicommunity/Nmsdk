#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseChannel.h"
#include "NPulseSynapse.h"
#include "NConstGenerator.h"
#include "NNeuronPostTrainTune.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ModelArchive.h"
#include "TimeLearner/ModelInspection.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/NativeLearnedState.h"
#include "TimeLearner/NativeRecognitionState.h"
#include "TimeLearner/NativeThresholdCandidate.h"
#include "TimeLearner/NativeCalibrationProposal.h"
#include "TimeLearner/NativeCalibrationAssessment.h"
#include "TimeLearner/NativeCalibratedState.h"
#include "TimeLearner/NativeThresholdCalibrationTransaction.h"
#include "TimeLearner/NativePostTuneTransaction.h"
#include "TimeLearner/NativeRecognitionObservationValidation.h"
#include "TimeLearner/NativeThresholdSupport.h"
#include "TimeLearner/NativeTrainingBindings.h"
#include "TimeLearner/NativePostTuneBoundary.h"
#include "TimeLearner/NativeFinalizationBoundary.h"
#include "TimeLearner/NumericChecks.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../Rdk/Core/Engine/UComponentFactory.h"
#include "../../../Rdk/Core/Engine/UNet.h"
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
#include <functional>

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
class CapacitanceResetFaultNeuron : public NPulseNeuron {
public:
    int resetsUntilFailure=0;
    int calculationsUntilFailure=0;
    std::function<void(double)> failureSink;
    CapacitanceResetFaultNeuron* New(void) override {return new CapacitanceResetFaultNeuron;}
protected:
    bool ABeforeReset(void) override {
        if(resetsUntilFailure>0 && --resetsUntilFailure==0)
        {
            auto channel=GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
            if(failureSink)failureSink(channel?channel->Capacity.GetData():0.);
            throw std::runtime_error("injected_joint_capacitance_live_reset");
        }
        return NPulseNeuron::ABeforeReset();
    }
    bool ABeforeCalculate(void) override {
        if(calculationsUntilFailure>0 && --calculationsUntilFailure==0)
            throw std::runtime_error("injected_native_child_calculate");
        return NPulseNeuron::ABeforeCalculate();
    }
};
class BuildContractFaultNeuron : public NPulseNeuron {
public:
    UProperty<MDMatrix<double>,BuildContractFaultNeuron,ptInput|ptPubState> TestInput;
    BuildContractFaultNeuron():TestInput("FaultInput",this) {}
    BuildContractFaultNeuron* New(void) override {return new BuildContractFaultNeuron;}
    void ArmBuildFailure() {armed=true;Ready=false;}
protected:
    bool ABeforeBuild(void) override {
        if(armed){armed=false;throw std::runtime_error("injected_native_child_build");}
        return NPulseNeuron::ABeforeBuild();
    }
private:
    bool armed=false;
};
class BorrowedBuildContractEnvironment : public UEnvironment {
public:
    void Borrow(UEPtr<UContainer> target,BuildContractFaultNeuron* structureFault=nullptr)
    {Model=target;fault=structureFault;Ready=false;}
    // This fixture borrows a real storage graph owned by EditingRig. It must
    // not return that graph to storage a second time in UEnvironment's dtor.
    ~BorrowedBuildContractEnvironment(){Model=0;}
protected:
    bool ACreateStructure(void) override {
        if(fault)fault->ArmBuildFailure();
        return true;
    }
private:
    BuildContractFaultNeuron* fault=nullptr;
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
template<class Learner> class PostTuneObservationLearner : public Learner {
public:
    PostTuneObservationLearner* New(void) override {return new PostTuneObservationLearner;}
    void SeedPreviousInference(bool withCompletedSamples)
    {
        this->IsNeedToTrain.SetDataDirect(false);this->TrainingPhase=2;
        this->EnablePostTrainTuning=true;this->EnablePostTrainMidThreshold=true;
        this->PostTrainMidMetric=PostTrainTune::kMidMetricSoma;
        this->FixedLTZThreshold.SetDataDirect(1.);this->PostTrainSilentThreshold=1.;
        this->PostTrainTuneComplete=false;this->PostTuneInferenceMidDone=false;
        this->PostTuneInferenceMidPending=false;this->PostTuneFreeRunActive=false;
        this->PostTuneResult=PostTrainTune::kResultSuccess;
        this->PostTuneRunInvalid=false;this->PostTuneRunTerminal=PostTrainTune::kResultNone;
        this->PostTuneSampleState.clear();
        if(withCompletedSamples)
        {
            PostTrainTune::SampleMetricState state;state.observed=true;state.finished=true;state.peak=.5;
            this->PostTuneSampleState.assign(2,state);
        }
    }
    bool StartMatrixInference(){return this->MaybeStartInferenceMidProbes();}
    void ObserveLiveMetric(){this->UpdatePostTuneFreeRunPeak();}
    bool AllSamplesValid() const {return PostTrainTune::AllSamplesValid(this->PostTuneSampleState);}
    bool AnySampleObserved() const {
        return std::any_of(this->PostTuneSampleState.begin(),this->PostTuneSampleState.end(),
            [](const auto& state){return state.observed || state.finished;});
    }
    std::size_t SampleCount() const {return this->PostTuneSampleState.size();}
    QJsonArray SampleStates() const {
        QJsonArray result;for(const auto& s:this->PostTuneSampleState)
            result.append(QJsonObject{{"peak",s.peak},{"observed",s.observed},{"finished",s.finished},{"finite_ok",s.finite_ok}});
        return result;
    }
    double LiveMetric() const {return this->ReadPostTuneLiveMetric();}
    bool IsNativeOwned() const {return this->NativeTrainingOwned;}
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
               const std::string& learnerClass={},int initialFirstSynapses=1,double initialThreshold=1.,
               const std::string& neuronBaseClass="NSPNeuronGen")
        :frequency(f),normalization(mode),inputCount(inputs),tightBurst(tight)
    {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        if(!environment->CreateModel("NModel"))throw std::runtime_error("editor_fixture_model");model=environment->GetModel();
        name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(f)+"_N"+std::to_string(mode)+"_"+suffix;
        StorageProfileSpec profile;profile.name=name;profile.frequencyHz=f;profile.neuronBaseClass=neuronBaseClass;
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

template<class Learner> void PrepareCapacitanceTransfer(EditingRig<Learner>& rig,NativeCapacitanceCorrection& correction)
{
    auto exc=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
    auto inh=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true);ASSERT_TRUE(exc && inh);
    exc->Capacity=.9e-9;inh->Capacity=.6e-9;
    correction.baseline=rig.learner->CaptureBoundNativeCapacitanceBaseline();correction.maximumRelativeChange=.2;
    correction.membraneScales={{"Dendrite1_2",1.1}};
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    const auto edited=rig.learner->ApplyNativeCapacitanceScale(correction.baseline,correction.membraneScales,correction.maximumRelativeChange);
    ASSERT_EQ(edited.status,NativeEditStatus::Applied)<<edited.reason;
}

void RecordNativeTrainingProof(NativeTrainingPlan& plan,const std::string& caseName,std::size_t channels);

template<class Learner> void NativeCapacitanceEdit(unsigned frequency,int normalization)
{
    EditingRig<Learner> rig(frequency,normalization,"capacitance_edit",false,2,true,2,1,false,{},normalization?1:2);
    const bool branch=std::is_same_v<Learner,NNeuronTimeLearnerBranch>;
    auto exc=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
    auto inh=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true);
    auto soma=rig.neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);
    auto lt=rig.neuron->template GetComponentL<NPulseChannel>("LTMembrane.ExcChannel",true);
    ASSERT_TRUE(exc && inh && soma && lt);
    exc->Capacity=.9e-9;inh->Capacity=.6e-9;soma->Capacity=1.4e-9;
    const double cExc=exc->Capacity.GetData(),cInh=inh->Capacity.GetData(),cSoma=soma->Capacity.GetData(),cLt=lt->Capacity.GetData();
    const auto original=rig.Revision();const auto baseline=rig.learner->CaptureNativeCapacitanceBaseline();
    Artifact(rig.name+"_capacitance_before_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron.Get(),rig.ports)).toJson());
    const auto decoded=QJsonDocument::fromJson(QJsonDocument(baseline).toJson()).object();ASSERT_EQ(decoded,baseline);
    EXPECT_DOUBLE_EQ(baseline["channels"].toObject()["Dendrite1_2.ExcChannel"].toDouble(),cExc);
    EXPECT_DOUBLE_EQ(baseline["channels"].toObject()["Dendrite1_2.InhChannel"].toDouble(),cInh);
    EXPECT_DOUBLE_EQ(baseline["channels"].toObject()["LTMembrane.ExcChannel"].toDouble(),cLt);
    const std::map<std::string,double> scales{{"Dendrite1_2",1.1}};
    EXPECT_EQ(rig.learner->ApplyNativeCapacitanceScale(baseline,scales,.1).status,NativeEditStatus::Rejected);
    std::vector<std::vector<double>> beforeWave,afterWave;std::vector<double> beforeInput,afterInput;
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true,false,
        [&](const NativeProbeSample& sample){beforeWave.push_back(sample.potentials);beforeInput.push_back(sample.stimulus);}).status,
        NativeProbeStatus::Completed);
    ASSERT_EQ(rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true).status,NativeProbeStatus::Completed);
    const auto first=rig.learner->ApplyNativeCapacitanceScale(decoded,scales,.1);
    ASSERT_EQ(first.status,NativeEditStatus::Applied)<<first.reason;
    EXPECT_NE(first.beforeRevision,first.afterRevision);EXPECT_EQ(first.beforeRevision,original);
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),cExc*1.1);EXPECT_DOUBLE_EQ(inh->Capacity.GetData(),cInh*1.1);
    EXPECT_DOUBLE_EQ(soma->Capacity.GetData(),cSoma);EXPECT_DOUBLE_EQ(lt->Capacity.GetData(),cLt);
    const auto edited=rig.Revision();const auto life=rig.neuron->ObserveLifecycle();
    Artifact(rig.name+"_capacitance_after_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron.Get(),rig.ports)).toJson());
    const auto repeat=rig.learner->ApplyNativeCapacitanceScale(decoded,scales,.1);
    ASSERT_EQ(repeat.status,NativeEditStatus::Applied)<<repeat.reason;
    EXPECT_EQ(rig.Revision(),edited);EXPECT_EQ(repeat.afterRevision,edited);EXPECT_TRUE(life.IsCurrent());
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),cExc*1.1);
    auto clone=dynamic_pointer_cast<NPulseNeuron>(NmsdkTools::ClonePhysicalGraphForEdit(rig.neuron,rig.ports));ASSERT_TRUE(clone);
    EXPECT_DOUBLE_EQ(clone->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true)->Capacity.GetData(),cExc*1.1);
    EXPECT_DOUBLE_EQ(clone->template GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true)->Capacity.GetData(),cInh*1.1);
    clone->BreakLinks();clone->GetStorage()->ReturnObject(clone);clone=0;
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true,false,
        [&](const NativeProbeSample& sample){afterWave.push_back(sample.potentials);afterInput.push_back(sample.stimulus);}).status,
        NativeProbeStatus::Completed);
    ASSERT_EQ(rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true).status,NativeProbeStatus::Completed);
    ASSERT_FALSE(beforeWave.empty());ASSERT_EQ(beforeWave.size(),afterWave.size());EXPECT_EQ(beforeInput,afterInput);
    double maximumWaveformChange=0.;
    for(std::size_t row=0;row<beforeWave.size();++row)
    {
        ASSERT_EQ(beforeWave[row].size(),afterWave[row].size());ASSERT_EQ(beforeWave[row].size(),branch?1u:2u);
        for(std::size_t channel=0;channel<beforeWave[row].size();++channel)
        {
            ASSERT_TRUE(std::isfinite(beforeWave[row][channel]) && std::isfinite(afterWave[row][channel]));
            maximumWaveformChange=std::max(maximumWaveformChange,std::fabs(beforeWave[row][channel]-afterWave[row][channel]));
        }
    }
    EXPECT_GT(maximumWaveformChange,0.)<<"Changing effective C must change the actual soma response to identical input samples";
    for(const double scale:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),1.2,1.e-12})
    {
        const auto rejected=rig.learner->ApplyNativeCapacitanceScale(baseline,{{"Dendrite1_2",scale}},scale==1.e-12?1.:.1);
        EXPECT_EQ(rejected.status,NativeEditStatus::Rejected)<<rejected.reason;
        EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_EQ(rig.Revision(),edited);
    }
    auto corrupt=baseline;corrupt["sha256"]=QString(64,'0');
    EXPECT_EQ(rig.learner->ApplyNativeCapacitanceScale(corrupt,scales,.1).status,NativeEditStatus::Rejected);
    auto invalidChannel=baseline;auto channels=invalidChannel["channels"].toObject();channels["LTMembrane.ExcChannel"]=0.;
    invalidChannel["channels"]=channels;invalidChannel.remove("sha256");
    invalidChannel["sha256"]=NmsdkTools::CanonicalModelDataSha256(invalidChannel);
    EXPECT_EQ(rig.learner->ApplyNativeCapacitanceScale(invalidChannel,scales,.1).reason,"invalid_capacitance_baseline_channel");
    EXPECT_EQ(rig.learner->ApplyNativeCapacitanceScale(baseline,{{"Soma1",1.1}},.1).status,NativeEditStatus::Rejected);
    EXPECT_EQ(rig.Revision(),edited);
    const auto restored=rig.learner->ApplyNativeCapacitanceScale(baseline,{{"Dendrite1_2",1.}},.1);
    ASSERT_EQ(restored.status,NativeEditStatus::Applied)<<restored.reason;EXPECT_EQ(rig.Revision(),original);
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),cExc);EXPECT_DOUBLE_EQ(inh->Capacity.GetData(),cInh);
    auto inputs=rig.learner->ReadNativeParameters();inputs[0].length=3;
    const auto growth=rig.learner->ApplyNativeParameters(inputs);ASSERT_EQ(growth.status,NativeEditStatus::Applied)<<growth.reason;
    exc=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
    inh=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true);ASSERT_TRUE(exc && inh);
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),cExc);EXPECT_DOUBLE_EQ(inh->Capacity.GetData(),cInh);
    const auto grown=rig.Revision();const auto unknown=rig.learner->ApplyNativeCapacitanceScale(baseline,{{"Dendrite1_3",1.1}},.1);
    EXPECT_EQ(unknown.status,NativeEditStatus::Rejected);EXPECT_EQ(unknown.reason,"missing_or_invalid_channel_capacitance_baseline");
    EXPECT_EQ(rig.Revision(),grown);
    QJsonObject receipt{{"baseline",baseline},{"applied",first.appliedChannels},
        {"before",QString::fromStdString(original)},{"after",QString::fromStdString(edited)},
        {"grown",QString::fromStdString(grown)},{"branch",branch},{"normalization",normalization},
        {"maximum_waveform_change",maximumWaveformChange},
        {"unknown_baseline_reason",QString::fromStdString(unknown.reason)}};
    Artifact(rig.name+"_capacitance_edit.json",QJsonDocument(receipt).toJson());
}

template<class Learner> void NativeCapacitanceOwnership(unsigned frequency,int normalization)
{
    EditingRig<Learner> rig(frequency,normalization,"capacitance_owner",false,2,true);
    NativeCapacitanceCorrection original;
    ASSERT_NO_FATAL_FAILURE(PrepareCapacitanceTransfer(rig,original));
    QJsonArray phases;
    const auto testId=std::string("NativeCapacitanceOwnership/")+(rig.branch?"Branch":"Classic")+
        "N"+std::to_string(normalization)+"At"+std::to_string(frequency);
    auto appendState=[&](const char* phase,const QJsonObject& state) {
        std::vector<std::string> imageRoots{"NDatasetMatrix","NPulseGeneratorTransit"};
        for(const auto& entry:original.baseline["storage_images"].toArray())
            imageRoots.push_back(entry.toObject()["name"].toString().toStdString());
        QJsonArray inputs;
        for(const auto& value:rig.learner->ReadNativeParameters())
            inputs.append(QJsonObject{{"length",value.length},{"synapses",value.synapses},{"resistance",value.resistance}});
        QJsonObject record{{"kind","native_capacitance_owner_snapshot"},{"schema_version",2},
            {"test_id",QString::fromStdString(testId)},{"phase",phase},{"state",state},
            {"input_parameters",inputs},
            {"declaration",original.baseline["model_spec"]},{"effective_model",NmsdkTools::IdentifyModel(rig.neuron,rig.ports)},
            {"class_definitions",NmsdkTools::CaptureModelImageDefinitions(rig.neuron,rig.ports,imageRoots)}};
        phases.append(record);
        Artifact(rig.name+"_ownership_"+phase+".json",QJsonDocument(record).toJson());
    };
    auto snapshot=[&](const char* phase) {
        const auto state=rig.learner->ImportedNativeCapacitanceState();
        const auto exc=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
        const auto inh=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true);
        appendState(phase,state);
        EXPECT_FALSE(state.isEmpty())<<"a successful bound edit must retain its original C0 automatically";
        if(!state.isEmpty())
        {
            EXPECT_NO_THROW(rig.learner->ValidateAppliedNativeCapacitanceState(state));
            EXPECT_EQ(state["baseline"].toObject()["model_revision"],original.baseline["model_revision"]);
            EXPECT_EQ(state["baseline"].toObject()["channels"].toObject()["Dendrite1_2.ExcChannel"],
                original.baseline["channels"].toObject()["Dendrite1_2.ExcChannel"]);
            EXPECT_EQ(state["membrane_scales"].toObject()["Dendrite1_2"],QJsonValue(1.1));
            EXPECT_EQ(state["applied_model_revision"],QJsonValue(QString::fromStdString(rig.Revision())));
        }
        EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),.9e-9*1.1);
        EXPECT_DOUBLE_EQ(inh->Capacity.GetData(),.6e-9*1.1);
        return state;
    };
    snapshot("first_bound_edit");
    // A subset edit must preserve the earlier absolute correction in the
    // owner's complete state, rather than replace its map with one entry.
    auto second=rig.learner->ApplyNativeCapacitanceScale(original.baseline,{{"Dendrite1_1",.9}},.2);
    ASSERT_EQ(second.status,NativeEditStatus::Applied)<<second.reason;
    const auto state=snapshot("second_membrane_edit");
    EXPECT_EQ(state["membrane_scales"].toObject()["Dendrite1_1"],QJsonValue(.9));
    const auto beforeReset=state;EXPECT_TRUE(rig.learner->Reset());
    EXPECT_EQ(snapshot("native_reset"),beforeReset);
    // Reset clears the executor's consumed-probe boundary. Re-establish it
    // through a real native observation before requesting the next edit.
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);

    auto candidate=rig.learner->ReadNativeParameters();candidate[0].length=3;
    const auto growth=rig.learner->ApplyNativeParameters(candidate);
    ASSERT_EQ(growth.status,NativeEditStatus::Applied)<<growth.reason;
    const auto growthState=snapshot("ordinary_growth_without_correction_argument");
    const auto extended=growthState["baseline"].toObject();
    EXPECT_EQ(extended["channel_origins"].toObject()["Dendrite1_3.ExcChannel"],QJsonValue("storage_image"));
    const auto added=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_3.ExcChannel",true);ASSERT_TRUE(added);
    EXPECT_GT(extended["channels"].toObject()["Dendrite1_3.ExcChannel"].toDouble(),0.);
    EXPECT_DOUBLE_EQ(added->Capacity.GetData(),extended["channels"].toObject()["Dendrite1_3.ExcChannel"].toDouble());
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    ASSERT_EQ(rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);

    const auto beforeShrink=rig.Revision();
    const auto beforeShrinkInputs=rig.learner->ReadNativeParameters();candidate[0].length=1;
    const auto shrink=rig.learner->ApplyNativeParameters(candidate);
    ASSERT_EQ(shrink.status,NativeEditStatus::Applied)<<shrink.reason;
    const auto dormant=rig.learner->OwnedNativeCapacitanceState();
    appendState("ordinary_shrink",dormant);
    EXPECT_EQ(dormant["schema_version"],QJsonValue(2));
    EXPECT_EQ(dormant["dormant_membrane_scales"].toObject()["Dendrite1_2"],QJsonValue(1.1));
    EXPECT_FALSE(dormant["membrane_scales"].toObject().contains("Dendrite1_2"));
    EXPECT_NO_THROW(rig.learner->ValidateAppliedNativeCapacitanceState(dormant));
    std::string dormantRevision;
    const auto decoded=ParseNativeCapacitanceState(QJsonDocument(dormant).toJson().toStdString(),dormantRevision);
    EXPECT_EQ(EncodeNativeCapacitanceState(decoded,dormantRevision),dormant);
    auto overlap=decoded;overlap.membraneScales["Dendrite1_2"]=1.;
    EXPECT_THROW(EncodeNativeCapacitanceState(overlap,dormantRevision),std::runtime_error);
    auto unknown=decoded;unknown.dormantMembraneScales["Dendrite1_999"]=1.;
    EXPECT_THROW(EncodeNativeCapacitanceState(unknown,dormantRevision),std::runtime_error);
    auto outside=decoded;outside.dormantMembraneScales["Dendrite1_2"]=1.3;
    EXPECT_THROW(EncodeNativeCapacitanceState(outside,dormantRevision),std::runtime_error);
    auto nonfinite=decoded;nonfinite.dormantMembraneScales["Dendrite1_2"]=std::numeric_limits<double>::quiet_NaN();
    EXPECT_THROW(EncodeNativeCapacitanceState(nonfinite,dormantRevision),std::runtime_error);
    auto falselyDormant=decoded;falselyDormant.membraneScales.erase("Dendrite1_1");
    falselyDormant.dormantMembraneScales["Dendrite1_1"]=.9;
    EXPECT_THROW({
        const auto invalidState=EncodeNativeCapacitanceState(falselyDormant,dormantRevision);
        rig.learner->ValidateAppliedNativeCapacitanceState(invalidState);
    },std::runtime_error);
    candidate[0].length=3;
    const auto regrowth=rig.learner->ApplyNativeParameters(candidate);
    ASSERT_EQ(regrowth.status,NativeEditStatus::Applied)<<regrowth.reason;
    const auto restored=snapshot("ordinary_regrowth_without_correction_argument");
    EXPECT_TRUE(restored["dormant_membrane_scales"].toObject().isEmpty());
    EXPECT_EQ(rig.learner->ReadNativeParameters(),beforeShrinkInputs);
    // The native editor releases formerly owned input banks while preserving
    // unowned banks. Equal L/Ns/Rs is not a claim of an identical whole graph.
    // Retain both actual identities; export/import still requires full identity.
    phases.append(QJsonObject{{"phase","bank_ownership_graph_transition"},
        {"before",QString::fromStdString(beforeShrink)},{"after",QString::fromStdString(rig.Revision())},
        {"whole_graph_equal",rig.Revision()==beforeShrink}});
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    ASSERT_EQ(rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);

    // Capturing a currently trimmed graph is not permission to replace the
    // original baseline and multiply it again. Rejection must be transactional.
    const auto rebased=rig.learner->CaptureBoundNativeCapacitanceBaseline();
    const auto beforeRevision=rig.Revision();
    const auto beforeState=rig.learner->ImportedNativeCapacitanceState();
    const auto refused=rig.learner->ApplyNativeCapacitanceScale(rebased,{{"Dendrite1_2",1.1}},.2);
    phases.append(QJsonObject{{"phase","rebase_attempt"},{"status",NativeEditStatusName(refused.status)},
        {"reason",QString::fromStdString(refused.reason)},{"before",QString::fromStdString(beforeRevision)},
        {"after",QString::fromStdString(rig.Revision())},{"state",rig.learner->ImportedNativeCapacitanceState()}});
    Artifact(rig.name+"_ownership.json",QJsonDocument(QJsonObject{{"kind","native_capacitance_ownership"},
        {"schema_version",1},{"frequency_hz",int(frequency)},{"normalization",normalization},
        {"branch",rig.branch},{"phases",phases},{"original_baseline",original.baseline},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    EXPECT_EQ(refused.status,NativeEditStatus::Rejected);EXPECT_EQ(rig.Revision(),beforeRevision);
    EXPECT_EQ(rig.learner->ImportedNativeCapacitanceState(),beforeState);
}
TEST(NativeCapacitanceOwnership,ClassicN0At2000){NativeCapacitanceOwnership<NNeuronTimeLearner>(2000,0);}
TEST(NativeCapacitanceOwnership,ClassicN1At2000){NativeCapacitanceOwnership<NNeuronTimeLearner>(2000,1);}
TEST(NativeCapacitanceOwnership,BranchN0At2000){NativeCapacitanceOwnership<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeCapacitanceOwnership,BranchN1At2000){NativeCapacitanceOwnership<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativeCapacitanceOwnership,ClassicN0At20000){NativeCapacitanceOwnership<NNeuronTimeLearner>(20000,0);}
TEST(NativeCapacitanceOwnership,ClassicN1At20000){NativeCapacitanceOwnership<NNeuronTimeLearner>(20000,1);}
TEST(NativeCapacitanceOwnership,BranchN0At20000){NativeCapacitanceOwnership<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativeCapacitanceOwnership,BranchN1At20000){NativeCapacitanceOwnership<NNeuronTimeLearnerBranch>(20000,1);}

template<class Learner> void NativeTrainingCapacitanceBridge(int normalization)
{
    EditingRig<Learner> rig(2000,normalization,"training_capacitance_bridge",false,2,true);
    QJsonArray phases;
    const auto record=[&](const std::string& phase) {
        const auto value=rig.learner->ReadNativeTrainingCapacitance();QJsonValue typed(QJsonValue::Null);
        const auto native=rig.learner->OwnedNativeCapacitanceState();
        std::vector<std::string> imageRoots;
        for(const auto& definition:native["baseline"].toObject()["storage_images"].toArray())
            imageRoots.push_back(definition.toObject()["name"].toString().toStdString());
        if(value)
        {
            QJsonObject scales;for(const auto& [path,scale]:value->membraneScales)scales[QString::fromStdString(path)]=scale;
            typed=QJsonObject{{"origin",QString::fromStdString(value->origin)},
                {"maximum_relative_change",value->maximumRelativeChange},{"membrane_scales",scales}};
        }
        const QJsonObject snapshot{{"phase",QString::fromStdString(phase)},
            {"native_state",native},{"controller_parameters",typed},
            {"storage_images",NmsdkTools::CaptureModelImageDefinitions(rig.neuron,rig.ports,imageRoots)},
            {"model",NmsdkTools::IdentifyModel(rig.neuron,rig.ports)}};
        const auto life=rig.neuron->ObserveLifecycle();
        const auto epoch=rig.learner->NativeTrainingController().ModelEpoch();
        const auto witness=rig.learner->ReadNativeTrainingCapacitanceWitness();
        ASSERT_EQ(bool(witness),bool(value));
        if(witness)
        {
            EXPECT_EQ(witness->parameters,*value);
            EXPECT_EQ(witness->modelRevision,rig.Revision());
            EXPECT_EQ(QJsonDocument::fromJson(QByteArray::fromStdString(witness->modelIdentityJson)).object(),snapshot["model"].toObject());
            EXPECT_EQ(QJsonDocument::fromJson(QByteArray::fromStdString(witness->nativeStateJson)).object(),native);
            EXPECT_EQ(QJsonDocument::fromJson(QByteArray::fromStdString(witness->storageImagesJson)).array(),snapshot["storage_images"].toArray());
        }
        EXPECT_TRUE(life.IsCurrent());EXPECT_EQ(epoch,rig.learner->NativeTrainingController().ModelEpoch());
        EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),snapshot["model"].toObject());
        EXPECT_EQ(rig.learner->OwnedNativeCapacitanceState(),native);
        phases.append(snapshot);Artifact(rig.name+"_bridge_"+phase+".json",QJsonDocument(snapshot).toJson());
    };
    const auto initial=rig.Revision();const auto initialLife=rig.neuron->ObserveLifecycle();
    EXPECT_FALSE(rig.learner->ReadNativeTrainingCapacitance());EXPECT_TRUE(initialLife.IsCurrent());
    EXPECT_EQ(initial,rig.Revision());EXPECT_TRUE(rig.learner->OwnedNativeCapacitanceState().isEmpty());record("unbound");
    TrainingCapacitance fabricated{std::string(64,'a'),.2,{{"Dendrite1_1",1.}}};
    const auto unbound=rig.learner->ApplyNativeTrainingParameters(rig.learner->ReadNativeParameters(),fabricated);
    ASSERT_EQ(unbound.status,NativeEditStatus::Rejected);EXPECT_EQ(unbound.reason,"training_capacitance_requires_owned_baseline");
    EXPECT_EQ(initial,rig.Revision());EXPECT_TRUE(rig.learner->OwnedNativeCapacitanceState().isEmpty());
    auto retained=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(retained);
    retained->Capacity=1.41e-9;
    NativeCapacitanceCorrection correction;ASSERT_NO_FATAL_FAILURE(PrepareCapacitanceTransfer(rig,correction));
    const auto captured=rig.learner->ReadNativeTrainingCapacitance();ASSERT_TRUE(captured);
    ASSERT_EQ(captured->membraneScales.at("Dendrite1_2"),1.1);EXPECT_EQ(captured->membraneScales.at("Dendrite1_1"),1.);
    const auto origin=captured->origin;const auto baselineDigest=correction.baseline["sha256"];
    const auto boundRevision=rig.Revision();const auto boundLife=rig.neuron->ObserveLifecycle();
    EXPECT_EQ(rig.learner->ReadNativeTrainingCapacitance(),captured);EXPECT_TRUE(boundLife.IsCurrent());
    EXPECT_EQ(boundRevision,rig.Revision());record("captured");
    // A witness must not launder changed live C through an unchanged owner.
    const auto retainedCapacity=retained->Capacity.GetData();retained->Capacity=retainedCapacity*1.01;
    const auto foreignRevision=rig.Revision();const auto foreignLife=rig.neuron->ObserveLifecycle();
    EXPECT_THROW(rig.learner->ReadNativeTrainingCapacitanceWitness(),std::invalid_argument);
    EXPECT_EQ(rig.Revision(),foreignRevision);EXPECT_TRUE(foreignLife.IsCurrent());
    retained->Capacity=retainedCapacity;EXPECT_EQ(rig.Revision(),boundRevision);
    bool refusedRunning=false;
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,
        [&](const NativeProbeSample&) {
            if(refusedRunning)return;
            try{rig.learner->ReadNativeTrainingCapacitanceWitness();ADD_FAILURE()<<"witness accepted during native probe";}
            catch(const std::invalid_argument& error)
            {EXPECT_EQ(std::string(error.what()),"training_capacitance_read_during_probe");refusedRunning=true;}
        }).status,NativeProbeStatus::Completed);
    EXPECT_TRUE(refusedRunning);
    auto geometry=rig.learner->ReadNativeParameters();geometry[0].length=3;
    const auto grown=rig.learner->ApplyNativeParameters(geometry);ASSERT_EQ(grown.status,NativeEditStatus::Applied)<<grown.reason;
    const auto afterGrowth=rig.learner->ReadNativeTrainingCapacitance();ASSERT_TRUE(afterGrowth);
    EXPECT_EQ(afterGrowth->origin,origin);EXPECT_EQ(afterGrowth->membraneScales.at("Dendrite1_3"),1.);
    EXPECT_EQ(afterGrowth->membraneScales.at("Dendrite1_2"),1.1);
    EXPECT_NE(rig.learner->OwnedNativeCapacitanceState()["baseline"].toObject()["sha256"],baselineDigest);record("ordinary_growth");
    auto requested=*afterGrowth;requested.membraneScales["Dendrite1_1"]=1.05;geometry[0].length=1;
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    const auto shrunk=rig.learner->ApplyNativeTrainingParameters(geometry,requested);
    ASSERT_EQ(shrunk.status,NativeEditStatus::Applied)<<shrunk.reason;
    const auto afterShrink=rig.learner->ReadNativeTrainingCapacitance();ASSERT_TRUE(afterShrink);
    EXPECT_EQ(afterShrink->origin,origin);EXPECT_EQ(afterShrink->membraneScales,requested.membraneScales);
    ASSERT_FALSE(rig.neuron->GetComponentL("Dendrite1_2",true));
    EXPECT_EQ(rig.learner->OwnedNativeCapacitanceState()["dormant_membrane_scales"].toObject()["Dendrite1_2"],QJsonValue(1.1));
    retained=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(retained);
    EXPECT_DOUBLE_EQ(retained->Capacity.GetData(),1.41e-9*1.05);record("joint_shrink");
    const auto reject=[&](const std::optional<TrainingCapacitance>& invalid,const std::string& reason) {
        ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
        const auto before=NmsdkTools::IdentifyModel(rig.neuron,rig.ports),owned=rig.learner->OwnedNativeCapacitanceState();
        const auto failure=rig.learner->ApplyNativeTrainingParameters(rig.learner->ReadNativeParameters(),invalid);
        EXPECT_EQ(failure.status,NativeEditStatus::Rejected);EXPECT_FALSE(failure.modelMayHaveChanged);EXPECT_EQ(failure.reason,reason);
        EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),before);EXPECT_EQ(rig.learner->OwnedNativeCapacitanceState(),owned);
    };
    auto invalid=*afterShrink;invalid.origin=std::string(64,origin.front()=='a'?'b':'a');
    ASSERT_NO_FATAL_FAILURE(reject(invalid,"training_capacitance_origin_or_policy_changed"));
    invalid=*afterShrink;invalid.maximumRelativeChange=.3;
    ASSERT_NO_FATAL_FAILURE(reject(invalid,"training_capacitance_origin_or_policy_changed"));
    invalid=*afterShrink;invalid.membraneScales.erase("Dendrite1_2");
    ASSERT_NO_FATAL_FAILURE(reject(invalid,"training_capacitance_history_lost"));
    ASSERT_NO_FATAL_FAILURE(reject(std::nullopt,"training_capacitance_state_required"));
    invalid=*afterShrink;invalid.membraneScales["Dendrite1_1"]=std::numeric_limits<double>::quiet_NaN();
    ASSERT_NO_FATAL_FAILURE(reject(invalid,"invalid_training_capacitance_scale"));
    invalid=*afterShrink;invalid.membraneScales["Dendrite1_999"]=1.;
    ASSERT_NO_FATAL_FAILURE(reject(invalid,"unknown_capacitance_membrane_baseline"));record("rejections_preserve_model");
    auto future=*afterShrink;future.membraneScales["Dendrite1_4"]=.95;
    geometry=rig.learner->ReadNativeParameters();geometry[0].length=4;
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    std::string domainRevision;
    if(normalization==1)
    {
        const auto live=NmsdkTools::IdentifyModel(rig.neuron,rig.ports),owned=rig.learner->OwnedNativeCapacitanceState();
        const auto domain=rig.learner->AssessNativeTrainingResistanceDomain(geometry,0,future);
        ASSERT_TRUE(domain.status==ResistanceDomainStatus::Available || domain.status==ResistanceDomainStatus::Unavailable)<<domain.reason;
        EXPECT_FALSE(domain.modelMayHaveChanged);EXPECT_EQ(domain.capacitance,std::optional<TrainingCapacitance>(future));
        ASSERT_TRUE(domain.effectiveCapacitance);EXPECT_TRUE(TrainingCapacitanceReadbackMatches(future,domain.effectiveCapacitance));
        EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),live);EXPECT_EQ(rig.learner->OwnedNativeCapacitanceState(),owned);
        const auto encoded=EncodeResistanceDomainAssessment(domain);EXPECT_EQ(encoded["schema_version"],QJsonValue(3));
        Artifact(rig.name+"_domain.json",QJsonDocument(encoded).toJson());domainRevision=domain.previewModelRevision;
        std::string ownedRevision;
        auto legacyCorrection=ParseNativeCapacitanceState(QJsonDocument(owned).toJson(QJsonDocument::Compact).toStdString(),ownedRevision);
        legacyCorrection.membraneScales=future.membraneScales;legacyCorrection.dormantMembraneScales.clear();
        const auto legacyDomain=rig.learner->AssessNativeResistanceDomain(geometry,0,legacyCorrection);
        EXPECT_EQ(legacyDomain.status,domain.status);EXPECT_EQ(legacyDomain.previewModelRevision,domainRevision);
        EXPECT_EQ(legacyDomain.minimumResistance,domain.minimumResistance);EXPECT_EQ(legacyDomain.maximumResistance,domain.maximumResistance);
        EXPECT_FALSE(legacyDomain.capacitance);EXPECT_FALSE(legacyDomain.effectiveCapacitance);
        const auto legacyEncoded=EncodeResistanceDomainAssessment(legacyDomain);EXPECT_EQ(legacyEncoded["schema_version"],QJsonValue(2));
        Artifact(rig.name+"_domain_legacy.json",QJsonDocument(legacyEncoded).toJson());
        auto invalidDomain=future;invalidDomain.maximumRelativeChange=.3;
        const auto rejected=rig.learner->AssessNativeTrainingResistanceDomain(geometry,0,invalidDomain);
        EXPECT_EQ(rejected.status,ResistanceDomainStatus::Unsupported);EXPECT_EQ(rejected.reason,"training_capacitance_origin_or_policy_changed");
        EXPECT_FALSE(rejected.modelMayHaveChanged);EXPECT_FALSE(rejected.effectiveCapacitance);
        EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),live);EXPECT_EQ(rig.learner->OwnedNativeCapacitanceState(),owned);
        Artifact(rig.name+"_domain_rejected.json",QJsonDocument(EncodeResistanceDomainAssessment(rejected)).toJson());
    }
    const auto joint=rig.learner->ApplyNativeTrainingParameters(geometry,future);
    ASSERT_EQ(joint.status,NativeEditStatus::Applied)<<joint.reason;
    if(normalization==1)EXPECT_EQ(rig.Revision(),domainRevision);
    const auto final=rig.learner->ReadNativeTrainingCapacitance();ASSERT_TRUE(final);
    EXPECT_EQ(final->origin,origin);EXPECT_EQ(final->membraneScales.at("Dendrite1_4"),.95);
    EXPECT_EQ(final->membraneScales.at("Dendrite1_2"),1.1);
    const auto state=rig.learner->OwnedNativeCapacitanceState(),baseline=state["baseline"].toObject();
    // Indexing this temporary QJsonObject yields a borrowed QJsonValueRef.
    // Keep an owning value before later allocations/storage reads occur.
    const QJsonValue c0=baseline["channels"].toObject()["Dendrite1_4.ExcChannel"];ASSERT_TRUE(c0.isDouble());ASSERT_GT(c0.toDouble(),0.);
    EXPECT_EQ(baseline["channel_origins"].toObject()["Dendrite1_4.ExcChannel"],QJsonValue("storage_image"));
    const auto created=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_4.ExcChannel",true);ASSERT_TRUE(created);
    EXPECT_DOUBLE_EQ(created->Capacity.GetData(),c0.toDouble()*.95);record("joint_growth");
    for(std::size_t input=0;input<rig.inputCount;++input)
    {
        ASSERT_EQ(rig.Probe(input,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
        EXPECT_EQ(rig.learner->ReadNativeTrainingCapacitance(),final);
    }
    Artifact(rig.name+"_bridge.json",QJsonDocument(QJsonObject{{"kind","native_training_capacitance_bridge"},
        {"schema_version",1},{"branch",rig.branch},{"normalization",normalization},{"phases",phases},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativeTrainingCapacitanceBridge,ClassicN0){NativeTrainingCapacitanceBridge<NNeuronTimeLearner>(0);}
TEST(NativeTrainingCapacitanceBridge,ClassicN1){NativeTrainingCapacitanceBridge<NNeuronTimeLearner>(1);}
TEST(NativeTrainingCapacitanceBridge,BranchN0){NativeTrainingCapacitanceBridge<NNeuronTimeLearnerBranch>(0);}
TEST(NativeTrainingCapacitanceBridge,BranchN1){NativeTrainingCapacitanceBridge<NNeuronTimeLearnerBranch>(1);}

template<class Learner> void NativeTrainingCapacitanceBinding(int normalization)
{
    EditingRig<Learner> rig(2000,normalization,"training_capacitance_binding",false,2,true);
    auto retained=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);
    auto distinct=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
    ASSERT_TRUE(retained);ASSERT_TRUE(distinct);retained->Capacity=1.41e-9;distinct->Capacity=.9e-9;
    QJsonArray phases;
    const auto record=[&](const char* phase) {
        const auto state=rig.learner->OwnedNativeCapacitanceState();
        const auto typed=rig.learner->ReadNativeTrainingCapacitance();QJsonValue controller(QJsonValue::Null);
        std::vector<std::string> roots;
        for(const auto& definition:state["baseline"].toObject()["storage_images"].toArray())
            roots.push_back(definition.toObject()["name"].toString().toStdString());
        if(typed)
        {
            QJsonObject scales;for(const auto& [path,value]:typed->membraneScales)scales[QString::fromStdString(path)]=value;
            controller=QJsonObject{{"origin",QString::fromStdString(typed->origin)},
                {"maximum_relative_change",typed->maximumRelativeChange},{"membrane_scales",scales}};
        }
        phases.append(QJsonObject{{"phase",phase},{"native_state",state},{"controller_parameters",controller},
            {"model",NmsdkTools::IdentifyModel(rig.neuron,rig.ports)},
            {"storage_images",NmsdkTools::CaptureModelImageDefinitions(rig.neuron,rig.ports,roots)}});
    };
    const auto reject=[&](double limit,const std::string& reason) {
        const auto before=NmsdkTools::IdentifyModel(rig.neuron,rig.ports),state=rig.learner->OwnedNativeCapacitanceState();
        const auto life=rig.neuron->ObserveLifecycle();
        try{rig.learner->BindNativeTrainingCapacitance(limit);ADD_FAILURE()<<"expected binding refusal";}
        catch(const std::exception& error){EXPECT_EQ(std::string(error.what()),reason);}
        EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),before);EXPECT_TRUE(life.IsCurrent());
        EXPECT_EQ(rig.learner->OwnedNativeCapacitanceState(),state);
    };
    EXPECT_FALSE(rig.learner->ReadNativeTrainingCapacitance());record("unbound");
    ASSERT_NO_FATAL_FAILURE(reject(std::numeric_limits<double>::quiet_NaN(),"invalid_training_capacitance_binding_policy"));
    const auto initial=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);
    const auto parameters=rig.learner->ReadNativeParameters();
    const auto life=rig.neuron->ObserveLifecycle();const auto epoch=rig.learner->NativeTrainingController().ModelEpoch();
    ASSERT_EQ(rig.learner->NativeProbeState(),NativeProbeStatus::Idle);
    const auto bound=rig.learner->BindNativeTrainingCapacitance(.2);
    EXPECT_EQ(NmsdkTools::IdentifyModel(rig.neuron,rig.ports),initial);EXPECT_TRUE(life.IsCurrent());
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);EXPECT_EQ(rig.learner->NativeProbeState(),NativeProbeStatus::Idle);
    EXPECT_EQ(rig.learner->NativeTrainingController().ModelEpoch(),epoch);
    const auto baseline=bound["baseline"].toObject();
    EXPECT_EQ(baseline["model_revision"],initial["sha256"]);
    EXPECT_EQ(baseline["channels"].toObject()["Dendrite1_1.ExcChannel"],QJsonValue(1.41e-9));
    EXPECT_EQ(baseline["channels"].toObject()["Dendrite1_2.ExcChannel"],QJsonValue(.9e-9));
    const auto typed=rig.learner->ReadNativeTrainingCapacitance();ASSERT_TRUE(typed);
    for(const auto& [path,value]:typed->membraneScales)EXPECT_DOUBLE_EQ(value,1.);
    EXPECT_EQ(rig.learner->BindNativeTrainingCapacitance(.2),bound);EXPECT_TRUE(life.IsCurrent());record("bound");
    ASSERT_NO_FATAL_FAILURE(reject(.3,"training_capacitance_origin_or_policy_changed"));
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    auto requested=*typed;requested.membraneScales["Dendrite1_1"]=1.05;
    const auto edited=rig.learner->ApplyNativeTrainingParameters(parameters,requested);
    ASSERT_EQ(edited.status,NativeEditStatus::Applied)<<edited.reason;
    const auto trimmed=rig.learner->OwnedNativeCapacitanceState();const auto revision=rig.Revision();
    const auto trimmedLife=rig.neuron->ObserveLifecycle();
    EXPECT_EQ(rig.learner->BindNativeTrainingCapacitance(.2),trimmed);EXPECT_TRUE(trimmedLife.IsCurrent());
    EXPECT_EQ(rig.Revision(),revision);EXPECT_EQ(trimmed["baseline"],bound["baseline"]);
    EXPECT_EQ(rig.learner->ReadNativeTrainingCapacitance()->origin,typed->origin);
    retained=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(retained);
    EXPECT_DOUBLE_EQ(retained->Capacity.GetData(),1.41e-9*1.05);record("trimmed");
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    Artifact(rig.name+"_binding.json",QJsonDocument(QJsonObject{{"kind","native_training_capacitance_binding"},
        {"schema_version",1},{"branch",rig.branch},{"normalization",normalization},{"phases",phases},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativeTrainingCapacitanceBinding,ClassicN0){NativeTrainingCapacitanceBinding<NNeuronTimeLearner>(0);}
TEST(NativeTrainingCapacitanceBinding,ClassicN1){NativeTrainingCapacitanceBinding<NNeuronTimeLearner>(1);}
TEST(NativeTrainingCapacitanceBinding,BranchN0){NativeTrainingCapacitanceBinding<NNeuronTimeLearnerBranch>(0);}
TEST(NativeTrainingCapacitanceBinding,BranchN1){NativeTrainingCapacitanceBinding<NNeuronTimeLearnerBranch>(1);}

template<class Learner> void BoundCapacitanceGrowth(unsigned frequency,int normalization)
{
    EditingRig<Learner> rig(frequency,normalization,"bound_capacitance",false,2,true);
    auto exc=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
    auto inh=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.InhChannel",true);ASSERT_TRUE(exc && inh);
    exc->Capacity=.9e-9;inh->Capacity=.6e-9;
    const auto baseline=rig.learner->CaptureBoundNativeCapacitanceBaseline();ASSERT_EQ(baseline["schema_version"],QJsonValue(2));
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    NativeCapacitanceCorrection correction;correction.baseline=baseline;correction.maximumRelativeChange=.2;
    correction.membraneScales={{"Dendrite1_2",1.1}};
    const auto applied=rig.learner->ApplyNativeCapacitanceScale(baseline,correction.membraneScales,.2);
    ASSERT_EQ(applied.status,NativeEditStatus::Applied)<<applied.reason;
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),.9e-9*1.1);EXPECT_DOUBLE_EQ(inh->Capacity.GetData(),.6e-9*1.1);
    auto state=EncodeNativeCapacitanceState(correction,rig.Revision());std::string revision;
    const auto decoded=ParseNativeCapacitanceState(QJsonDocument(state).toJson().toStdString(),revision);
    EXPECT_EQ(decoded.baseline,baseline);EXPECT_EQ(revision,rig.Revision());
    EXPECT_NO_THROW(rig.learner->ValidateAppliedNativeCapacitanceState(state));
    auto falseBaseline=baseline;auto channels=falseBaseline["channels"].toObject();channels["Dendrite1_2.ExcChannel"]=1.e-9;
    falseBaseline["channels"]=channels;falseBaseline.remove("sha256");falseBaseline["sha256"]=NmsdkTools::CanonicalModelDataSha256(falseBaseline);
    const auto before=rig.Revision();
    EXPECT_EQ(rig.learner->ApplyNativeCapacitanceScale(falseBaseline,correction.membraneScales,.2).status,NativeEditStatus::Rejected);
    EXPECT_EQ(rig.Revision(),before);
    const double resistance=exc->Resistance.GetData();exc->Resistance=resistance*1.1;
    const auto physicsChanged=rig.Revision();
    const auto rejected=rig.learner->ApplyNativeCapacitanceScale(baseline,correction.membraneScales,.2);
    EXPECT_EQ(rejected.status,NativeEditStatus::Rejected);EXPECT_EQ(rejected.reason,"capacitance_channel_physics_changed");
    EXPECT_EQ(rig.Revision(),physicsChanged);exc->Resistance=resistance;
    auto candidate=rig.learner->ReadNativeParameters();candidate[0].length=3;
    correction.membraneScales["Dendrite1_3"]=1.1;
    const auto growth=rig.learner->ApplyNativeParameters(candidate,correction);
    ASSERT_EQ(growth.status,NativeEditStatus::Applied)<<growth.reason;
    ASSERT_FALSE(growth.capacitanceBaseline.isEmpty());correction.baseline=growth.capacitanceBaseline;
    EXPECT_EQ(correction.baseline["model_revision"],baseline["model_revision"]);
    EXPECT_EQ(correction.baseline["channels"].toObject()["Dendrite1_2.ExcChannel"],baseline["channels"].toObject()["Dendrite1_2.ExcChannel"]);
    EXPECT_EQ(correction.baseline["channel_origins"].toObject()["Dendrite1_3.ExcChannel"],QJsonValue("storage_image"));
    auto added=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_3.ExcChannel",true);ASSERT_TRUE(added);
    const auto addedC0=correction.baseline["channels"].toObject()["Dendrite1_3.ExcChannel"].toDouble();
    ASSERT_GT(addedC0,0.);EXPECT_NE(addedC0,.9e-9);EXPECT_DOUBLE_EQ(added->Capacity.GetData(),addedC0*1.1);
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),.9e-9*1.1);EXPECT_DOUBLE_EQ(inh->Capacity.GetData(),.6e-9*1.1);
    state=EncodeNativeCapacitanceState(correction,rig.Revision());EXPECT_NO_THROW(rig.learner->ValidateAppliedNativeCapacitanceState(state));
    auto incomplete=correction;incomplete.membraneScales.erase("Dendrite1_2");
    const auto incompleteState=EncodeNativeCapacitanceState(incomplete,rig.Revision());
    EXPECT_THROW(rig.learner->ValidateAppliedNativeCapacitanceState(incompleteState),std::runtime_error);
    auto clone=dynamic_pointer_cast<NPulseNeuron>(NmsdkTools::ClonePhysicalGraphForEdit(rig.neuron,rig.ports));ASSERT_TRUE(clone);
    EXPECT_EQ(NmsdkTools::IdentifyModel(clone,rig.ports),NmsdkTools::IdentifyModel(rig.neuron,rig.ports));
    EXPECT_DOUBLE_EQ(clone->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true)->Capacity.GetData(),.9e-9*1.1);
    clone->BreakLinks();clone->GetStorage()->ReturnObject(clone);clone=0;
    correction.membraneScales["Dendrite1_2"]=1.2;
    const auto second=rig.learner->ApplyNativeParameters(candidate,correction);ASSERT_EQ(second.status,NativeEditStatus::Applied)<<second.reason;
    EXPECT_DOUBLE_EQ(exc->Capacity.GetData(),.9e-9*1.2);EXPECT_DOUBLE_EQ(added->Capacity.GetData(),addedC0*1.1);
    correction.baseline=second.capacitanceBaseline;state=EncodeNativeCapacitanceState(correction,rig.Revision());
    EXPECT_NO_THROW(rig.learner->ValidateAppliedNativeCapacitanceState(state));
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    ASSERT_EQ(rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    Artifact(rig.name+"_bound_capacitance_state.json",QJsonDocument(state).toJson());
    Artifact(rig.name+"_bound_capacitance_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron,rig.ports)).toJson());
}
TEST(NativeBoundCapacitance,ClassicN0At2000){BoundCapacitanceGrowth<NNeuronTimeLearner>(2000,0);}
TEST(NativeBoundCapacitance,ClassicN1At2000){BoundCapacitanceGrowth<NNeuronTimeLearner>(2000,1);}
TEST(NativeBoundCapacitance,BranchN0At2000){BoundCapacitanceGrowth<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeBoundCapacitance,BranchN1At2000){BoundCapacitanceGrowth<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativeBoundCapacitance,ClassicN0At20000){BoundCapacitanceGrowth<NNeuronTimeLearner>(20000,0);}
TEST(NativeBoundCapacitance,ClassicN1At20000){BoundCapacitanceGrowth<NNeuronTimeLearner>(20000,1);}
TEST(NativeBoundCapacitance,BranchN0At20000){BoundCapacitanceGrowth<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativeBoundCapacitance,BranchN1At20000){BoundCapacitanceGrowth<NNeuronTimeLearnerBranch>(20000,1);}

TEST(NativeCapacitanceEdit,ClassicN0At2000){NativeCapacitanceEdit<NNeuronTimeLearner>(2000,0);}
TEST(NativeCapacitanceEdit,ClassicN1At2000){NativeCapacitanceEdit<NNeuronTimeLearner>(2000,1);}
TEST(NativeCapacitanceEdit,BranchN0At2000){NativeCapacitanceEdit<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeCapacitanceEdit,BranchN1At2000){NativeCapacitanceEdit<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativeCapacitanceEdit,ClassicN0At20000){NativeCapacitanceEdit<NNeuronTimeLearner>(20000,0);}
TEST(NativeCapacitanceEdit,ClassicN1At20000){NativeCapacitanceEdit<NNeuronTimeLearner>(20000,1);}
TEST(NativeCapacitanceEdit,BranchN0At20000){NativeCapacitanceEdit<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativeCapacitanceEdit,BranchN1At20000){NativeCapacitanceEdit<NNeuronTimeLearnerBranch>(20000,1);}

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

template<class Learner> void NativeCapacitanceBindingReferenceGuard()
{
    EditingRig<Learner> rig(2000,1,"binding_reference_guard",false,2,true);
    auto plan=TrainingPlan(rig);RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;!rig.learner->NativeTrainingController().References();++ticks)
    {
        ASSERT_LT(ticks,10000u)<<rig.learner->NativeTrainingController().Reason();
        ASSERT_NE(rig.learner->NativeTrainingController().State(),NativeTrainingState::Finished);
        rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    }
    rig.learner->IsNeedToTrain=false;
    EXPECT_EQ(rig.learner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
    rig.learner->Reset();const auto& service=rig.learner->NativeTrainingController();
    EXPECT_EQ(service.State(),NativeTrainingState::Idle);ASSERT_TRUE(service.References());
    ASSERT_TRUE(rig.learner->OwnedNativeCapacitanceState().isEmpty());
    const auto before=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);const auto life=rig.neuron->ObserveLifecycle();
    std::string reason;
    try{rig.learner->BindNativeTrainingCapacitance(.2);ADD_FAILURE()<<"references must not be rebased by metadata binding";}
    catch(const std::exception& error){reason=error.what();}
    EXPECT_EQ(reason,"training_capacitance_binding_requires_initial_model_boundary");
    EXPECT_TRUE(rig.learner->OwnedNativeCapacitanceState().isEmpty());EXPECT_FALSE(rig.learner->ReadNativeTrainingCapacitance());
    const auto after=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);EXPECT_EQ(before,after);EXPECT_TRUE(life.IsCurrent());
    QJsonArray packets;for(const auto& p:service.ReferencePackets())packets.append(EncodeNativeProbeEvidence(p));
    Artifact(rig.name+"_reference_guard.json",QJsonDocument(QJsonObject{{"kind","native_capacitance_binding_reference_guard"},
        {"schema_version",1},{"branch",rig.branch},{"reason",QString::fromStdString(reason)},
        {"before_model",before},{"after_model",after},{"reference_packets",packets},
        {"owner_state",rig.learner->OwnedNativeCapacitanceState()},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativeTrainingCapacitanceBinding,ClassicRetainedReferencesCannotBeRebased){NativeCapacitanceBindingReferenceGuard<NNeuronTimeLearner>();}
TEST(NativeTrainingCapacitanceBinding,BranchRetainedReferencesCannotBeRebased){NativeCapacitanceBindingReferenceGuard<NNeuronTimeLearnerBranch>();}

template<class Learner> void NativeJointCapacitanceCandidate(int normalization,bool fault=false)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string image="CapacitanceResetFaultNeuronFixture";
    if(fault && !core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]()->UComponent*{return new CapacitanceResetFaultNeuron;},image),image);
    EditingRig<Learner> rig(2000,normalization,fault?"joint_capacitance_rollback":"joint_capacitance",false,2,true,2,1,false,{},
        normalization?1:2,1.,fault?image:"NSPNeuronGen");
    if constexpr(std::is_same_v<Learner,NNeuronTimeLearner>)rig.learner->PreferConfiguredResistanceMinFloor=false;
    const auto baseline=rig.learner->CaptureNativeCapacitanceBaseline();const auto initial=rig.learner->ReadNativeParameters();
    const auto original=rig.Revision();
    Artifact(rig.name+"_before_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron.Get(),rig.ports)).toJson());
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    auto candidate=initial;
    NativeCapacitanceCorrection correction;correction.baseline=baseline;
    correction.maximumRelativeChange=normalization?3.:.1;correction.membraneScales={{"Dendrite1_2",normalization?4.:1.1}};
    std::string oldRejection;
    if(normalization)
    {
        const auto oldDomain=rig.learner->AssessNativeResistanceDomain(candidate,0);
        const auto jointDomain=rig.learner->AssessNativeResistanceDomain(candidate,0,correction);
        ASSERT_EQ(oldDomain.status,ResistanceDomainStatus::Available)<<oldDomain.reason;
        ASSERT_EQ(jointDomain.status,ResistanceDomainStatus::Available)<<jointDomain.reason;
        ASSERT_LT(jointDomain.minimumResistance,oldDomain.minimumResistance);
        candidate[0].resistance=std::exp(.5*(std::log(oldDomain.minimumResistance)+std::log(jointDomain.minimumResistance)));
        ASSERT_GT(candidate[0].resistance,jointDomain.minimumResistance);ASSERT_LT(candidate[0].resistance,oldDomain.minimumResistance);
        const auto separately=rig.learner->ApplyNativeParameters(candidate);
        ASSERT_EQ(separately.status,NativeEditStatus::Rejected)<<separately.reason;
        EXPECT_FALSE(separately.modelMayHaveChanged);oldRejection=separately.reason;EXPECT_EQ(rig.Revision(),original);
        Artifact(rig.name+"_old_domain.json",QJsonDocument(EncodeResistanceDomainAssessment(oldDomain)).toJson());
        Artifact(rig.name+"_joint_domain.json",QJsonDocument(EncodeResistanceDomainAssessment(jointDomain)).toJson());
    }
    else candidate[0].synapses=3;
    const auto oldNeuron=rig.neuron.Get();
    auto injected=std::make_shared<std::pair<bool,double>>(false,0.);
    if(fault)
    {
        auto failing=dynamic_cast<CapacitanceResetFaultNeuron*>(rig.neuron.Get());ASSERT_TRUE(failing);
        // No structural edit in this fixture: Transform Reset, then C Reset.
        // Preview instances have no armed fault; the second live Reset throws.
        failing->resetsUntilFailure=2;
        failing->failureSink=[injected](double capacity){injected->first=true;injected->second=capacity;};
    }
    const auto applied=rig.learner->ApplyNativeParameters(candidate,correction);
    if(fault)
    {
        ASSERT_EQ(applied.status,NativeEditStatus::Rejected)<<applied.reason;
        EXPECT_EQ(applied.reason.find("native_operation_failure:Reset:"),0u);
        EXPECT_NE(applied.reason.find("injected_joint_capacitance_live_reset"),std::string::npos);
        EXPECT_TRUE(injected->first);
        EXPECT_DOUBLE_EQ(injected->second,baseline["channels"].toObject()["Dendrite1_2.ExcChannel"].toDouble()*4.);
        EXPECT_FALSE(applied.modelMayHaveChanged);EXPECT_TRUE(applied.graphWasReplaced);
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        ASSERT_TRUE(rig.neuron && rig.source);rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
        EXPECT_NE(rig.neuron.Get(),oldNeuron);EXPECT_EQ(rig.Revision(),original);
        EXPECT_EQ(rig.learner->ReadNativeParameters(),initial);EXPECT_TRUE(rig.learner->NativeModelEditFailure().empty());
    }
    else
    {
        ASSERT_EQ(applied.status,NativeEditStatus::Applied)<<applied.reason;
        EXPECT_FALSE(applied.graphWasReplaced);EXPECT_EQ(rig.learner->ReadNativeParameters(),candidate);
        const auto channels=baseline["channels"].toObject();
        for(const auto* name:{"ExcChannel","InhChannel"})
        {
            const auto path=std::string("Dendrite1_2.")+name;
            auto channel=rig.neuron->template GetComponentL<NPulseChannel>(path,true);ASSERT_TRUE(channel);
            EXPECT_DOUBLE_EQ(channel->Capacity.GetData(),channels[QString::fromStdString(path)].toDouble()*correction.membraneScales.at("Dendrite1_2"));
        }
        EXPECT_NE(rig.Revision(),original);
    }
    Artifact(rig.name+"_after_model.json",QJsonDocument(NmsdkTools::IdentifyModel(rig.neuron.Get(),rig.ports)).toJson());
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    ASSERT_EQ(rig.Probe(1,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    Artifact(rig.name+"_joint_result.json",QJsonDocument(QJsonObject{{"baseline",baseline},
        {"status",NativeEditStatusName(applied.status)},{"reason",QString::fromStdString(applied.reason)},
        {"graph_replaced",applied.graphWasReplaced},{"separate_rejection",QString::fromStdString(oldRejection)},
        {"scale",correction.membraneScales.at("Dendrite1_2")},{"rollback",fault},
        {"reset_fault_observed",injected->first},{"capacity_at_reset_fault",injected->second}}).toJson());
    if(!fault)
    {
        auto activePlan=TrainingPlan(rig);
        for(std::size_t i=0;i<candidate.size();++i)
            activePlan.search.bounds[i].maximumSynapses=std::max(activePlan.search.bounds[i].maximumSynapses,candidate[i].synapses);
        rig.learner->IsNeedToTrain=true;rig.learner->BeginNativeTraining(activePlan);
        ASSERT_EQ(rig.learner->NativeTrainingController().State(),NativeTrainingState::CapturingReferences);
        const auto before=rig.Revision();const auto denied=rig.learner->ApplyNativeParameters(candidate,correction);
        EXPECT_EQ(denied.status,NativeEditStatus::Rejected);EXPECT_EQ(denied.reason,"native_training_owns_model_editor");
        EXPECT_EQ(rig.Revision(),before);
    }
}
TEST(NativeJointCapacitance,ClassicN0){NativeJointCapacitanceCandidate<NNeuronTimeLearner>(0);}
TEST(NativeJointCapacitance,BranchN0){NativeJointCapacitanceCandidate<NNeuronTimeLearnerBranch>(0);}
TEST(NativeJointCapacitance,ClassicN1){NativeJointCapacitanceCandidate<NNeuronTimeLearner>(1);}
TEST(NativeJointCapacitance,BranchN1){NativeJointCapacitanceCandidate<NNeuronTimeLearnerBranch>(1);}
TEST(NativeJointCapacitance,ClassicRollback){NativeJointCapacitanceCandidate<NNeuronTimeLearner>(1,true);}
TEST(NativeJointCapacitance,BranchRollback){NativeJointCapacitanceCandidate<NNeuronTimeLearnerBranch>(1,true);}

void NativeOperationFailureProbe(bool calculate)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="CapacitanceResetFaultNeuronFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]()->UComponent*{return new CapacitanceResetFaultNeuron;},image),image);
    EditingRig<NNeuronTimeLearner> rig(2000,1,calculate?"operation_calculate":"operation_reset",false,2,true,2,1,false,{},1,1.,image);
    auto failing=dynamic_cast<CapacitanceResetFaultNeuron*>(rig.neuron.Get());ASSERT_TRUE(failing);
    const auto marker=rig.learner->OperationFailureSequence();const auto neuronMarker=rig.neuron->OperationFailureSequence();
    if(calculate)
    {
        failing->calculationsUntilFailure=10;
        const auto result=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true);
        ASSERT_EQ(result.status,NativeProbeStatus::Rejected);ASSERT_TRUE(result.observation);
        EXPECT_FALSE(result.observation->complete);EXPECT_FALSE(result.observation->valid);
        EXPECT_EQ(result.observation->sampleCount,9u);
        EXPECT_TRUE(std::any_of(result.reasons.begin(),result.reasons.end(),[](const auto& reason){
            return reason.find("native_operation_failure:Calculate:")==0 && reason.find("injected_native_child_calculate")!=std::string::npos;}));
    }
    else
    {
        failing->resetsUntilFailure=1;
        // Preserve the native Rdk boolean contract even when the hook fails.
        EXPECT_TRUE(rig.neuron->Reset());
        EXPECT_TRUE(rig.neuron->HasOperationFailureSince(neuronMarker));
        EXPECT_TRUE(rig.learner->HasOperationFailureSince(marker));
        EXPECT_EQ(rig.neuron->LastOperationFailure().Operation,"Reset");
        const auto after=rig.learner->OperationFailureSequence();
        EXPECT_TRUE(rig.neuron->Reset());EXPECT_FALSE(rig.learner->HasOperationFailureSince(after));
        EXPECT_NE(rig.learner->LastOperationFailure().Reason.find("injected_joint_capacitance_live_reset"),std::string::npos);
        ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    }
    const auto failure=rig.learner->LastOperationFailure();
    Artifact(rig.name+"_operation_diagnostic.json",QJsonDocument(QJsonObject{{"sequence",double(failure.Sequence)},
        {"overflowed",failure.Overflowed},{"operation",QString::fromStdString(failure.Operation)},
        {"reason",QString::fromStdString(failure.Reason)}}).toJson());
}
TEST(NativeOperationDiagnostics,ResetPreservesTrueAndReportsSubtreeFailure){NativeOperationFailureProbe(false);}
TEST(NativeOperationDiagnostics,CalculateFailureCensorsTheActualNativeObservation){NativeOperationFailureProbe(true);}

TEST(NativeOperationDiagnostics,BuildPreservesTrueAndReportsSubtreeFailure)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string image="BuildContractFaultNeuronFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]()->UComponent*{return new BuildContractFaultNeuron;},image),image);
    EditingRig<NNeuronTimeLearner> rig(2000,1,"operation_build",false,2,true,2,1,false,{},1,1.,image);
    auto failing=dynamic_cast<BuildContractFaultNeuron*>(rig.neuron.Get());ASSERT_TRUE(failing);
    const auto marker=rig.learner->OperationFailureSequence();
    failing->ArmBuildFailure();const bool returned=rig.neuron->Build();
    EXPECT_TRUE(returned);EXPECT_FALSE(rig.neuron->IsReady());
    ASSERT_TRUE(rig.learner->HasOperationFailureSince(marker));
    const auto failure=rig.learner->LastOperationFailure();
    EXPECT_EQ(failure.Operation,"Build");
    EXPECT_NE(failure.Reason.find("injected_native_child_build"),std::string::npos);
    const auto after=rig.learner->OperationFailureSequence();
    EXPECT_TRUE(rig.neuron->Build());EXPECT_TRUE(rig.neuron->IsReady());
    EXPECT_FALSE(rig.learner->HasOperationFailureSince(after));
    int connection=-1;
    failing->ArmBuildFailure();
    EXPECT_FALSE(failing->Connect(UEPtr<UConnector>(failing),"Output","FaultInput",connection,true));
    EXPECT_TRUE(failing->TestInput.GetDataSources().empty());EXPECT_FALSE(failing->IsReady());
    EXPECT_TRUE(failing->Build());
    failing->ArmBuildFailure();
    EXPECT_FALSE(failing->ConnectToItem(UEPtr<UItem>(failing),"Output","FaultInput",connection,true));
    EXPECT_TRUE(failing->TestInput.GetDataSources().empty());EXPECT_FALSE(failing->IsReady());
    EXPECT_TRUE(failing->Build());
    ASSERT_TRUE(failing->Connect(UEPtr<UConnector>(failing),"Output","FaultInput",connection,true));
    EXPECT_EQ(failing->TestInput.GetDataSources().size(),1u);
    failing->Disconnect(UEPtr<UConnector>(failing),"Output","FaultInput",connection);
    EXPECT_TRUE(failing->TestInput.GetDataSources().empty());
    {
        BorrowedBuildContractEnvironment environment;environment.Borrow(rig.neuron.Get());
        failing->ArmBuildFailure();const auto before=environment.OperationFailureSequence();
        EXPECT_TRUE(environment.Build());EXPECT_TRUE(environment.HasOperationFailureSince(before));
        EXPECT_EQ(environment.LastOperationFailure().Operation,"Build");
    }
    {
        BorrowedBuildContractEnvironment environment;environment.Borrow(rig.model.Get());
        ASSERT_TRUE(environment.SetModelCalculationComponent(rig.neuron->GetLongId(rig.model.Get())));
        failing->ArmBuildFailure();const auto before=environment.OperationFailureSequence();
        EXPECT_TRUE(environment.Build());EXPECT_TRUE(environment.HasOperationFailureSince(before));
        EXPECT_EQ(environment.LastOperationFailure().Operation,"Build");
    }
    {
        BorrowedBuildContractEnvironment environment;environment.Borrow(rig.neuron.Get(),failing);
        const auto before=environment.OperationFailureSequence();
        EXPECT_FALSE(environment.CreateStructure());
        EXPECT_TRUE(environment.HasOperationFailureSince(before));
        EXPECT_EQ(environment.LastOperationFailure().Operation,"Build");
    }
    ASSERT_EQ(rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true).status,NativeProbeStatus::Completed);
    Artifact(rig.name+"_operation_diagnostic.json",QJsonDocument(QJsonObject{{"returned",returned},
        {"operation",QString::fromStdString(failure.Operation)},{"reason",QString::fromStdString(failure.Reason)}}).toJson());
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
    ASSERT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted)<<service.Reason();
    ASSERT_TRUE(service.References());EXPECT_EQ(service.References()->Inputs().size(),2u);
    ASSERT_TRUE(service.Search());EXPECT_GE(service.Search()->AppliedEdits(),1u);
    EXPECT_EQ(service.Search()->Status(),TrainingStatus::BudgetExhausted);
    EXPECT_FALSE(service.Certificate());ASSERT_TRUE(service.Search());ASSERT_TRUE(service.Search()->Certificate());EXPECT_FALSE(service.Search()->Certificate()->Exact());
    EXPECT_EQ(service.Reason(),"maximum_sweeps_exhausted");
    EXPECT_TRUE(service.Search()->Certificate()->Matches(rig.Revision(),*service.References(),plan.search.tolerances,
        ModelStateKind::LearnedSolo,service.Search()->ModelEpoch()));
    EXPECT_EQ(observations,service.IssuedReferenceProbes()+service.Search()->IssuedProbes());EXPECT_GT(frames,0u);
    auto summary=EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters());
    summary["implementation_control"]=true;
    EXPECT_FALSE(summary["certificate_matches_actual_model"].toBool());
    EXPECT_TRUE(summary["certificate"].isNull());
    EXPECT_EQ(summary["model_state_kind"],QJsonValue("diagnostic"));
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
    ASSERT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted)<<service.Reason();
    ASSERT_TRUE(service.References());EXPECT_FALSE(service.Certificate());ASSERT_TRUE(service.Search());ASSERT_TRUE(service.Search()->Certificate());EXPECT_FALSE(service.Search()->Certificate()->Exact());
    EXPECT_EQ(service.Reason(),"maximum_sweeps_exhausted");
    ASSERT_TRUE(service.Search());EXPECT_GT(service.Search()->AppliedEdits(),0u);
    if(n0Repeats)
    {
        ASSERT_FALSE(service.Search()->CandidateRepeats().empty());
        for(const auto& group:service.Search()->CandidateRepeats())
        {EXPECT_EQ(group.trialIds.size(),2u);EXPECT_EQ(group.anchorTrialIds.size(),2u);}
        EXPECT_EQ(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())["schema_version"],QJsonValue(2));
    }
    EXPECT_EQ(observations,service.IssuedReferenceProbes()+service.Search()->IssuedProbes());
    EXPECT_TRUE(service.Search()->Certificate()->Matches(rig.Revision(),*service.References(),configuration.search.tolerances,
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
        if(package["schema_version"]==QJsonValue(2))
        {
            EXPECT_EQ(target->ImportedNativeCapacitanceState(),package["capacitance_state"].toObject());
            record["capacitance_state"]=target->ImportedNativeCapacitanceState();
        }
        QFile json(QString::fromLocal8Bit(output));ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        ASSERT_GT(json.write(QJsonDocument(record).toJson()),0);json.close();
        QFile csv(QString::fromLocal8Bit(output)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_GT(csv.write(QByteArray::fromStdString(trace.str())),0);
    };
    if(c.model.branch)run(dynamic_pointer_cast<NNeuronTimeLearnerBranch>(learner));else run(dynamic_pointer_cast<NNeuronTimeLearner>(learner));
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}


enum class RecognitionCase { Identity,Scaled,Clipped,SharedConflict,OwnedIdentity,OwnedScaled,OwnedClipped,OwnedFreshIdentity,OwnedFreshScaled,ThresholdCandidates,ThresholdPotential,CalibratedThreshold,ThresholdGrid,PostTuneCandidates,PostTuneTransaction };

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

template<class Learner> void ThresholdGridChecks(EditingRig<Learner>& rig,const QJsonObject& source,
    double selectedThreshold,const std::vector<NativeRecognitionTrialRequest>& design)
{
    using Transaction=NativeThresholdCalibrationTransaction<Learner>;
    const std::string implementation="native-learned-boundary-fixture-v1";
    const auto refresh=[&] {
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    };
    const auto restore=[&] {
        const auto result=rig.learner->ImportNativeRecognitionState(source,implementation);
        ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;
        rig.learner->Build();rig.learner->Init();rig.learner->Reset();refresh();
        ASSERT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    };
    NativeThresholdGridSpec spec;spec.trials=design;spec.thresholds={1.,selectedThreshold};spec.maximumCandidates=2;
    spec.confirmation.dataPartitionId="declared-primary-pair";spec.confirmation.clockId=rig.name+"/grid-clock";
    spec.confirmation.attemptId=rig.name+"/grid-success";
    const auto run=[&](NativeThresholdGridSpec job,NativeCalibrationTransactionStatus expected,const std::string& suffix) {
        const auto begin=rig.environment->GetTime().GetTime();
        Transaction transaction(*rig.learner,job,implementation);
        EXPECT_EQ(begin,rig.environment->GetTime().GetTime());
        for(unsigned tick=0;!transaction.Done();++tick)
        {
            ASSERT_LT(tick,20000u);
            const auto time=rig.environment->GetTime().GetTime();transaction.Advance();
            EXPECT_EQ(time,rig.environment->GetTime().GetTime());refresh();
            if(!transaction.Done()){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
        }
        EXPECT_EQ(transaction.Status(),expected)<<transaction.Reason();
        Artifact(rig.name+suffix+"_grid_transaction.json",QJsonDocument(transaction.Report()).toJson());
        if(expected==NativeCalibrationTransactionStatus::Calibrated)
        {
            EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),transaction.CalibratedPackage());
            EXPECT_DOUBLE_EQ(transaction.CalibratedPackage()["threshold"].toDouble(),selectedThreshold);
            EXPECT_EQ(transaction.Report()["selected_index"],QJsonValue(1));
            EXPECT_FALSE(transaction.Report()["source_restored"].toBool());
            EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());
        }
        else EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    };
    restore();auto invalid=spec;invalid.thresholds={0.,-0.};
    EXPECT_THROW((Transaction(*rig.learner,invalid,implementation)),std::logic_error);
    invalid=spec;invalid.trials.pop_back();
    EXPECT_THROW((Transaction(*rig.learner,invalid,implementation)),std::logic_error);
    EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    run(spec,NativeCalibrationTransactionStatus::Calibrated,"_success");
    restore();auto silent=spec;silent.thresholds={1.};silent.maximumCandidates=1;silent.confirmation.attemptId+="/silent";
    run(silent,NativeCalibrationTransactionStatus::NonSeparable,"_nonseparable");
    auto limited=spec;limited.maximumCandidates=1;limited.confirmation.attemptId+="/budget";
    run(limited,NativeCalibrationTransactionStatus::BudgetExhausted,"_budget");
    for(bool start:{false,true})
    {
        auto cancelSpec=spec;cancelSpec.confirmation.attemptId+=start?"/running-cancel":"/queued-cancel";
        Transaction cancelled(*rig.learner,cancelSpec,implementation);cancelled.Advance();refresh();
        EXPECT_FALSE(rig.learner->IsNativeRecognitionTrialIdle());
        EXPECT_THROW((Transaction(*rig.learner,spec,implementation)),std::logic_error);
        if(start){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
        const auto time=rig.environment->GetTime().GetTime();cancelled.Cancel("explicit-cancel");refresh();
        EXPECT_EQ(time,rig.environment->GetTime().GetTime());
        EXPECT_EQ(cancelled.Status(),NativeCalibrationTransactionStatus::Cancelled)<<cancelled.Reason();
        EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
        Artifact(rig.name+(start?"_running_cancel":"_queued_cancel")+"_grid_transaction.json",QJsonDocument(cancelled.Report()).toJson());
    }
    {
        Transaction scoped(*rig.learner,spec,implementation);scoped.Advance();refresh();
    }
    refresh();EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    {
        auto changed=spec;changed.confirmation.attemptId+="/foreign-reset";
        Transaction transaction(*rig.learner,changed,implementation);transaction.Advance();refresh();
        rig.learner->Reset();transaction.Advance();
        EXPECT_EQ(transaction.Status(),NativeCalibrationTransactionStatus::RecoveryRequired);
        EXPECT_NE(rig.learner->ExportNativeRecognitionState(implementation),source);
        Artifact(rig.name+"_foreign_reset_grid_transaction.json",QJsonDocument(transaction.Report()).toJson());
        rig.learner->TakeNativeRecognitionTrialResult();
    }
    restore();
    for(bool clockChange:{false,true})
    {
        auto changed=spec;changed.confirmation.attemptId+=clockChange?"/clock-change":"/frequency-change";
        Transaction transaction(*rig.learner,changed,implementation);transaction.Advance();refresh();
        const auto time=rig.environment->GetTime().GetTime();
        ASSERT_GT(time,1000u);
        if(clockChange)rig.environment->GetTime().SetTime(time-1000);
        else rig.model->SetGlobalTimeStep(rig.frequency*2);
        transaction.Advance();
        EXPECT_EQ(transaction.Status(),NativeCalibrationTransactionStatus::RecoveryRequired);
        EXPECT_NE(transaction.Reason().find(clockChange?"clock_moved_backwards":"context_changed"),std::string::npos);
        Artifact(rig.name+(clockChange?"_clock":"_frequency")+"_grid_context_guard.json",QJsonDocument(transaction.Report()).toJson());
        rig.environment->GetTime().SetTime(time);rig.model->SetGlobalTimeStep(rig.frequency);
        rig.learner->CancelNativeRecognitionTrial("explicit-context-recovery");
        rig.learner->TakeNativeRecognitionTrialResult();restore();
    }
}

template<class Learner> void PostTuneTransactionChecks(EditingRig<Learner>& rig,const QJsonObject& source,
    double threshold,const std::vector<NativeRecognitionTrialRequest>& design)
{
    using Transaction=NativePostTuneTransaction<Learner>;const std::string implementation="native-learned-boundary-fixture-v1";
    const auto refresh=[&] {
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    };
    const auto restore=[&] {
        const auto result=rig.learner->ImportNativeRecognitionState(source,implementation);
        ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;
        rig.learner->Build();rig.learner->Init();rig.learner->Reset();refresh();
        ASSERT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    };
    NativePostTuneTransactionSpec spec;spec.metric=NativePostTuneMetric::LTZone;
    spec.calibration.trials=design;spec.calibration.thresholds={1.,threshold};spec.calibration.maximumCandidates=2;
    spec.calibration.confirmation.attemptId=rig.name+"/post-tune";
    spec.calibration.confirmation.clockId=rig.name+"/native-clock";
    spec.calibration.confirmation.dataPartitionId="declared-primary-pair";
    const auto run=[&](NativePostTuneTransactionSpec job,const std::string& suffix,std::optional<NativePostTuneTransactionStatus> expected={}) {
        restore();job.calibration.confirmation.attemptId+="/"+suffix;
        const auto clock=rig.environment->GetTime().GetTime();Transaction transaction(*rig.learner,job,implementation);
        EXPECT_EQ(clock,rig.environment->GetTime().GetTime());
        for(unsigned tick=0;!transaction.Done();++tick)
        {
            ASSERT_LT(tick,100000u);const auto now=rig.environment->GetTime().GetTime();transaction.Advance();
            EXPECT_EQ(now,rig.environment->GetTime().GetTime());refresh();
            if(!transaction.Done()){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
        }
        Artifact(rig.name+"_post_tune_"+suffix+".json",QJsonDocument(transaction.Report()).toJson());
        if(expected)EXPECT_EQ(transaction.Status(),*expected)<<transaction.Reason();
        else EXPECT_TRUE(transaction.Status()==NativePostTuneTransactionStatus::Calibrated ||
            transaction.Status()==NativePostTuneTransactionStatus::SearchUnresolved ||
            transaction.Status()==NativePostTuneTransactionStatus::BudgetExhausted)<<transaction.Reason();
        if(transaction.Status()==NativePostTuneTransactionStatus::Calibrated)
        {
            EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),transaction.CalibratedPackage());
            EXPECT_TRUE(transaction.CalibratedPackage()["recognition_certificate"].isNull());
            const auto& core=NmsdkTests::InitEngineForPulseLibTests();
            auto loaded=PrepareNativeRecognitionState(transaction.CalibratedPackage(),core.storage,core.environment,implementation);
            EXPECT_TRUE(loaded->calibrationConfirmed);
        }
        else EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    };
    restore();auto invalid=spec;invalid.calibration.trials.pop_back();
    EXPECT_THROW((Transaction(*rig.learner,invalid,implementation)),std::exception);
    invalid=spec;const auto originalPattern=invalid.calibration.trials.front().pattern;
    invalid.calibration.trials.front().pattern.Resize(originalPattern.GetRows(),2,0.);
    for(int i=0;i<originalPattern.GetRows();++i)for(int column=0;column<2;++column)
        invalid.calibration.trials.front().pattern(i,column)=originalPattern(i,0);
    EXPECT_THROW((Transaction(*rig.learner,invalid,implementation)),std::exception);
    EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
    spec.mode=NativePostTuneControllerMode::Off;run(spec,"off",NativePostTuneTransactionStatus::Calibrated);
    spec.mode=NativePostTuneControllerMode::KeepDone;run(spec,"keep",NativePostTuneTransactionStatus::Calibrated);
    auto metric=spec;metric.metric=NativePostTuneMetric::Auto;run(metric,"auto_metric");
    metric.metric=NativePostTuneMetric::SomaSum;run(metric,"soma_metric");
    auto silent=spec;silent.calibration.thresholds={1.};silent.calibration.maximumCandidates=1;
    run(silent,"silent",NativePostTuneTransactionStatus::SearchUnresolved);
    auto budget=spec;budget.maximumRecordedSamples=1;
    run(budget,"recording_budget",NativePostTuneTransactionStatus::BudgetExhausted);
    auto edited=spec;edited.mode=NativePostTuneControllerMode::CanonRmin;
    const auto parameters=source["recognition_inputs"].toArray();
    edited.canonicalFloor=parameters.first().toObject()["resistance"].toDouble()*.8;
    edited.canonicalLast=parameters.last().toObject()["resistance"].toDouble()*1.2;
    for(int i=0;i<parameters.size();++i)edited.resistanceBounds.push_back({1.e6,1.e12});
    run(edited,"canon");edited.mode=NativePostTuneControllerMode::FlatLastR;edited.canonicalFloor=0.;run(edited,"flat");
    edited.mode=NativePostTuneControllerMode::SearchSynthetic;edited.canonicalFloor=parameters.first().toObject()["resistance"].toDouble()*.8;
    edited.searchPasses=1;edited.maximumCandidates=7;run(edited,"synthetic");
    for(bool delegated:{false,true})
    {
        restore();auto job=spec;job.calibration.confirmation.attemptId+=delegated?"/child-cancel":"/weight-cancel";
        Transaction transaction(*rig.learner,job,implementation);transaction.Advance();refresh();
        if(delegated)for(unsigned tick=0;!transaction.IsCalibrating();++tick)
        {
            ASSERT_LT(tick,10000u);ASSERT_FALSE(transaction.Done())<<transaction.Reason();
            rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();transaction.Advance();refresh();
        }
        const auto now=rig.environment->GetTime().GetTime();transaction.Cancel("explicit-cancel");refresh();
        EXPECT_EQ(now,rig.environment->GetTime().GetTime());
        EXPECT_EQ(transaction.Status(),NativePostTuneTransactionStatus::Cancelled)<<transaction.Reason();
        EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),source);
        Artifact(rig.name+(delegated?"_post_tune_child_cancel.json":"_post_tune_weight_cancel.json"),QJsonDocument(transaction.Report()).toJson());
    }
    restore();
    {
        Transaction transaction(*rig.learner,spec,implementation);transaction.Advance();refresh();
        rig.learner->CancelNativeRecognitionTrial("foreign-consumer");rig.learner->TakeNativeRecognitionTrialResult();
        auto foreign=design.front();foreign.runId="foreign-controller";foreign.trialId="foreign-trial";
        rig.learner->QueueNativeRecognitionTrial(foreign);transaction.Advance();
        EXPECT_EQ(transaction.Status(),NativePostTuneTransactionStatus::RecoveryRequired);
        EXPECT_TRUE(rig.learner->HasNativeRecognitionTrialIdentity(foreign.runId,foreign.trialId));
        Artifact(rig.name+"_post_tune_foreign_trial.json",QJsonDocument(transaction.Report()).toJson());
        rig.learner->CancelNativeRecognitionTrial("explicit-foreign-cleanup");rig.learner->TakeNativeRecognitionTrialResult();
    }
    restore();
}

template<class Learner> void ThresholdCandidateChecks(EditingRig<Learner>& rig,const QJsonObject& solo,bool recordThresholdPotential=false,bool finalizeCalibration=false,bool runGrid=false,bool runPostTune=false)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string implementation="native-learned-boundary-fixture-v1";
    const auto source=ConvertNativeSoloToRecognition(solo,NativeRecognitionSpec{},core.storage,core.environment,implementation);
    const auto sourceCopy=source;const auto original=rig.Revision();
    Artifact(rig.name+"_threshold_source.json",QJsonDocument(source).toJson());
    for(double invalid:{std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
        EXPECT_THROW(CreateNativeThresholdCandidate(source,invalid,core.storage,core.environment,implementation),std::invalid_argument);
    for(double finiteThreshold:{0.,-0.,-1.})
    {
        const auto clock=rig.environment->GetTime().GetTime();
        const auto signedCandidate=CreateNativeThresholdCandidate(source,finiteThreshold,core.storage,core.environment,implementation);
        // Exercise the persisted API, not only the in-memory QJsonObject.
        const auto persisted=ParseNativeRecognitionState(QJsonDocument(signedCandidate).toJson().toStdString());
        auto prepared=PrepareNativeRecognitionState(persisted,core.storage,core.environment,implementation);
        auto zone=prepared->neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
        EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),finiteThreshold);EXPECT_EQ(source,sourceCopy);
        EXPECT_EQ(rig.Revision(),original);
        EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
        Artifact(rig.name+(finiteThreshold==0.?(std::signbit(finiteThreshold)?"_numeric_domain_negative_zero_candidate.json":"_numeric_domain_zero_candidate.json"):"_numeric_domain_negative_candidate.json"),
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
            if(runGrid)ThresholdGridChecks(rig,source,*pendingProposal->threshold,search.requests);
            if(runPostTune)PostTuneTransactionChecks(rig,source,*pendingProposal->threshold,search.requests);
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

template<class Learner> void PostTuneCandidateChecks(EditingRig<Learner>& rig,const QJsonObject& source,NativeRecognitionSpec& selected)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string implementation="native-learned-boundary-fixture-v1";
    if(rig.branch && source["configuration"].toObject()["model"].toObject()["normalization"]==QJsonValue("N1"))
    {
        selected.mode=RecognitionConversionMode::HistoricalBranchN1;
        for(std::size_t i=0;i<rig.inputCount;++i)selected.resistanceBounds.push_back({1.e6,1.e12});
    }
    const auto base=ConvertNativeSoloToRecognition(source,selected,core.storage,core.environment,implementation);
    const auto parameters=base["recognition_inputs"].toArray();ASSERT_FALSE(parameters.isEmpty());
    Artifact(rig.name+"_post_tune_base.json",QJsonDocument(base).toJson());
    const auto original=rig.Revision();const auto clock=rig.environment->GetTime().GetTime();
    for(auto mode:{NativePostTuneMode::Off,NativePostTuneMode::KeepDone,NativePostTuneMode::CanonRmin,
                  NativePostTuneMode::FlatLastR,NativePostTuneMode::SearchSyntheticCandidate})
    {
        NativePostTuneSpec post;post.mode=mode;post.sourceModelRevision=base["model_revision"].toString().toStdString();
        const bool edit=mode!=NativePostTuneMode::Off && mode!=NativePostTuneMode::KeepDone;
        if(mode==NativePostTuneMode::CanonRmin)post.canonicalFloor=parameters[0].toObject()["resistance"].toDouble()*.8;
        if(mode==NativePostTuneMode::CanonRmin || mode==NativePostTuneMode::FlatLastR)
            post.canonicalLast=parameters.last().toObject()["resistance"].toDouble()*1.2;
        if(edit)for(const auto& v:parameters)
        {
            const double r=v.toObject()["resistance"].toDouble();
            if(mode==NativePostTuneMode::SearchSyntheticCandidate)
            {post.requestedResistances.push_back(r*.8);post.resistanceBounds.push_back({r*1.1,r*1.1});}
            else post.resistanceBounds.push_back({1.e6,1.e12});
        }
        auto spec=selected;spec.postTune=post;
        const auto encoded=EncodeNativeRecognitionSpec(spec);
        EXPECT_EQ(EncodeNativeRecognitionSpec(DecodeNativeRecognitionSpec(encoded)),encoded);
        const auto candidate=ConvertNativeSoloToRecognition(source,spec,core.storage,core.environment,implementation);
        EXPECT_EQ(candidate,ConvertNativeSoloToRecognition(source,spec,core.storage,core.environment,implementation));
        auto prepared=PrepareNativeRecognitionState(candidate,core.storage,core.environment,implementation);
        ASSERT_TRUE(prepared);EXPECT_FALSE(prepared->calibrationConfirmed);
        EXPECT_EQ(QString::fromStdString(prepared->modelRevision),candidate["model_revision"].toString());
        EXPECT_TRUE(candidate["recognition_certificate"].isNull());
        if(!edit)EXPECT_EQ(candidate["model_revision"],base["model_revision"]);
        else EXPECT_NE(candidate["model_revision"],base["model_revision"]);
        const auto decisions=candidate["conversion_record"].toObject()["post_tune"].toObject()["decisions"].toArray();
        ASSERT_EQ(decisions.size(),parameters.size());
        if(mode==NativePostTuneMode::SearchSyntheticCandidate)for(const auto& value:decisions)EXPECT_TRUE(value.toObject()["clipped"].toBool());
        Artifact(rig.name+"_post_tune_candidate_"+std::to_string(int(mode))+".json",QJsonDocument(candidate).toJson());
        auto invalid=spec;invalid.postTune->sourceModelRevision=std::string(64,'0');
        EXPECT_THROW(ConvertNativeSoloToRecognition(source,invalid,core.storage,core.environment,implementation),std::invalid_argument);
        auto forged=candidate;auto record=forged["conversion_record"].toObject();auto postRecord=record["post_tune"].toObject();
        postRecord["selection_status"]="selected";record["post_tune"]=postRecord;forged["conversion_record"]=record;
        forged.remove("sha256");forged["sha256"]=NmsdkTools::CanonicalModelDataSha256(forged);
        EXPECT_THROW(PrepareNativeRecognitionState(forged,core.storage,core.environment,implementation),std::invalid_argument);
        // Each candidate derives from the same base; never chain the selected edit.
        selected.postTune.reset();
    }
    NativePostTuneSpec post;post.mode=NativePostTuneMode::CanonRmin;
    post.sourceModelRevision=base["model_revision"].toString().toStdString();
    post.canonicalFloor=parameters[0].toObject()["resistance"].toDouble()*.8;
    post.canonicalLast=parameters.last().toObject()["resistance"].toDouble()*1.2;
    for(int i=0;i<parameters.size();++i)post.resistanceBounds.push_back({1.e6,1.e12});
    selected.postTune=post;
    EXPECT_EQ(rig.Revision(),original);EXPECT_EQ(rig.environment->GetTime().GetTime(),clock);
}

template<class Learner> void RecognitionChecks(EditingRig<Learner>& rig,const QJsonObject& source,RecognitionCase scenario)
{
    if(scenario==RecognitionCase::ThresholdCandidates){ThresholdCandidateChecks(rig,source);return;}
    if(scenario==RecognitionCase::ThresholdPotential){ThresholdCandidateChecks(rig,source,true);return;}
    if(scenario==RecognitionCase::CalibratedThreshold){ThresholdCandidateChecks(rig,source,true,true);return;}
    if(scenario==RecognitionCase::ThresholdGrid){ThresholdCandidateChecks(rig,source,true,true,true);return;}
    if(scenario==RecognitionCase::PostTuneTransaction){ThresholdCandidateChecks(rig,source,true,true,false,true);return;}
    if(scenario==RecognitionCase::OwnedIdentity || scenario==RecognitionCase::OwnedScaled || scenario==RecognitionCase::OwnedClipped ||
       scenario==RecognitionCase::OwnedFreshIdentity || scenario==RecognitionCase::OwnedFreshScaled)
    {RecognitionOwnerChecks(rig,source,scenario);return;}
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const std::string implementation="native-learned-boundary-fixture-v1";
    const auto original=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();
    const auto sourceCopy=source;const auto clock=rig.environment->GetTime().GetTime();NativeRecognitionSpec spec;
    if(scenario==RecognitionCase::PostTuneCandidates)PostTuneCandidateChecks(rig,source,spec);
    else if(scenario!=RecognitionCase::Identity)
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
    if(spec.mode==RecognitionConversionMode::HistoricalBranchN1 && parameters.size()>1)
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
enum class BoundaryExpectation { Completed, DiagnosticSweepBudget };
template<class Learner> void LearnedBoundary(int normalization,double sync=.02,unsigned frequency=2000,std::size_t inputs=2,bool configured=false,
    std::optional<RecognitionCase> recognition={},bool automatic=false,double initialThreshold=1.,unsigned n0Repeats=1,
    double fixtureWallSeconds=600.,BoundaryExpectation expectation=BoundaryExpectation::Completed,bool withCapacitance=false,
    bool withDormantCapacitance=false)
{
    ASSERT_TRUE(std::isfinite(fixtureWallSeconds) && fixtureWallSeconds>0.);
    auto suffix=std::string(sync==.02?"learned_boundary":"learned_boundary_explicit_tolerance");
    if(inputs!=2)suffix+="_inputs"+std::to_string(inputs);if(configured)suffix+="_configured";if(automatic)suffix+="_automatic";
    if(recognition)suffix+="_recognition_"+std::to_string(int(*recognition));
    if(initialThreshold!=1.)suffix+="_spiking";
    if(n0Repeats>1)suffix+="_repeat"+std::to_string(n0Repeats);
    if(withCapacitance)suffix+="_capacitance_state";
    if(withDormantCapacitance)suffix+="_dormant";
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
    std::string dormantImage;
    if(withDormantCapacitance)
    {
        ASSERT_TRUE(withCapacitance);
        const auto beforeClassChange=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);
        Artifact(rig.name+"_before_channel_class_change.json",QJsonDocument(beforeClassChange).toJson());
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        auto membrane=rig.neuron->template GetComponentL<NPulseMembrane>("Dendrite1_2",true);ASSERT_TRUE(membrane);
        auto image=dynamic_pointer_cast<NPulseChannel>(core.storage->TakeObject(membrane->ExcChannelClassName.GetData()));
        ASSERT_TRUE(image);image->SetEnvironment(rig.environment);image->SetGlobalTimeStep(frequency);image->Capacity=.9e-9;
        dormantImage=rig.name+"_DormantExcImage";
        RegisterClassImage(core.storage,dormantImage,image);core.storage->ReturnObject(image);
        // Apply the initial heterogeneous configuration through native Load of
        // its owning tree. A leaf setter only invalidates that leaf; Build of
        // an already-ready neuron does not rebuild the cable's channel links.
        // No self-assignment, arbitrary Default or learner-specific wake-up.
        const auto declaration=Configuration(rig).model;
        const auto originalLearnerBuildMode=rig.learner->StructureBuildMode.GetData();
        USerStorageXML configuration;ASSERT_TRUE(configuration.Create("DormantChannelConfiguration"));
        const auto configurationOwner=dynamic_pointer_cast<UNet>(rig.model);ASSERT_TRUE(configurationOwner);
        ASSERT_TRUE(configurationOwner->SaveComponent(&configuration,true,ptPubParameter|pgSystem));
        ASSERT_TRUE(configuration.SelectNode(rig.model->GetName()));
        for(const auto& node:std::vector<std::string>{"Components","Learner","Components","Neuron",
                "Components","Dendrite1_2","Parameters","ExcChannelClassName"})
            ASSERT_TRUE(configuration.SelectNode(node))<<node;
        ASSERT_TRUE(configuration.SetNodeText(dormantImage));
        // A loaded graph declares both the membrane's future channel class
        // and the class of its already serialized channel instance. Keep
        // them consistent instead of relying on a later structural repair.
        configuration.SelectUp();configuration.SelectUp();
        ASSERT_TRUE(configuration.SelectNode("Components"));ASSERT_TRUE(configuration.SelectNode("ExcChannel"));
        ASSERT_TRUE(configuration.SetNodeAttribute("Class",dormantImage));
        for(int level=0;level<8;++level)configuration.SelectUp();
        // Link restoration calls DisconnectAll/Connect, which can Build the
        // owner inside Load itself. A serialized complete graph uses the
        // documented no-reconstruction mode until explicit native adoption.
        for(const auto& node:std::vector<std::string>{"Components","Learner","Parameters","StructureBuildMode"})
            ASSERT_TRUE(configuration.SelectNode(node))<<node;
        ASSERT_TRUE(configuration.SetNodeText("0"));
        for(int level=0;level<4;++level)configuration.SelectUp();
        std::string configuredXml;ASSERT_TRUE(configuration.Save(configuredXml));
        Artifact(rig.name+"_dormant_configuration.xml",QByteArray::fromStdString(configuredXml));
        const auto captureSetupStage=[&](const std::string& stage) {
            QJsonObject observed{{"stage",QString::fromStdString(stage)},
                {"requested_channel_class",QString::fromStdString(dormantImage)},
                {"model_ready",rig.model->IsReady()},{"model_initialized",rig.model->IsInit()}};
            const auto owner=rig.model->template GetComponentL<Learner>("Learner",true);
            if(owner)
            {
                observed["owner_ready"]=owner->IsReady();observed["owner_initialized"]=owner->IsInit();
                observed["owner_structure_mode"]=owner->StructureBuildMode.GetData();
                const auto tree=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
                if(tree)
                {
                    observed["neuron_ready"]=tree->IsReady();observed["neuron_initialized"]=tree->IsInit();
                    const auto membrane=tree->template GetComponentL<NPulseMembrane>("Dendrite1_2",true);
                    if(membrane)observed["membrane_channel_class"]=QString::fromStdString(membrane->ExcChannelClassName.GetData());
                    const auto channel=tree->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);
                    if(channel){observed["actual_channel_class"]=QString::fromStdString(channel->GetCompClassName());observed["capacity"]=channel->Capacity.GetData();}
                    const auto retained=tree->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);
                    if(retained)observed["retained_capacity"]=retained->Capacity.GetData();
                }
            }
            Artifact(rig.name+"_setup_"+stage+".json",QJsonDocument(observed).toJson());
        };
        const auto marker=rig.model->OperationFailureSequence();
        captureSetupStage("before_uninit");rig.model->UnInit();captureSetupStage("after_uninit");
        TProjectLoadDiagnostics diagnostics;
        ASSERT_TRUE(configurationOwner->LoadComponent(&configuration,true,&diagnostics));
        ASSERT_TRUE(diagnostics.errors.empty());ASSERT_TRUE(diagnostics.warnings.empty());
        captureSetupStage("after_load");
        rig.model->SetGlobalTimeStep(frequency);captureSetupStage("after_frequency");
        rig.learner=rig.model->template GetComponentL<Learner>("Learner",true);ASSERT_TRUE(rig.learner);
        ASSERT_EQ(rig.learner->StructureBuildMode.GetData(),0);
        rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(rig.neuron);
        auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
        // Like native construction, prepare the physical children before
        // adopting their graph. Building a still-legacy learner here would
        // legitimately replace the loaded neuron from its common profile.
        dataset->Build();captureSetupStage("after_dataset_build");
        dataset->Init();captureSetupStage("after_dataset_init");
        rig.neuron->Build();captureSetupStage("after_neuron_build");
        rig.neuron->Init();captureSetupStage("after_neuron_init");
        ASSERT_FALSE(rig.model->HasOperationFailureSince(marker));
        rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(rig.source);
        rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
        const auto adopted=rig.learner->AdoptNativeModel(declaration);
        ASSERT_EQ(adopted.status,NativeModelBuildStatus::Adopted)<<adopted.reason;
        captureSetupStage("after_adopt");
        rig.learner->StructureBuildMode=originalLearnerBuildMode;
        ASSERT_EQ(rig.learner->StructureBuildMode.GetData(),originalLearnerBuildMode);
        captureSetupStage("after_restore_owner_mode");
        rig.model->Init();captureSetupStage("after_model_init");
        rig.model->Reset();captureSetupStage("after_model_reset");
        // The external native scheduler completes the newly adopted owner's
        // ordinary lifecycle. No nested Calculate or forced Ready toggles.
        rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();captureSetupStage("after_model_calculate");
        ASSERT_FALSE(rig.model->HasOperationFailureSince(marker));
        ASSERT_EQ(rig.neuron,rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true));
        ASSERT_TRUE(rig.neuron->IsReady() && rig.neuron->IsInit());
        const auto configuredMembrane=rig.neuron->template GetComponentL<NPulseMembrane>("Dendrite1_2",true);ASSERT_TRUE(configuredMembrane);
        EXPECT_EQ(configuredMembrane->ExcChannelClassName.GetData(),dormantImage);
        const auto actual=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_2.ExcChannel",true);ASSERT_TRUE(actual);
        ASSERT_EQ(actual->GetCompClassName(),dormantImage);
        const auto configuredGraph=NmsdkTools::IdentifyModel(rig.neuron,rig.ports);
        Artifact(rig.name+"_after_channel_class_build.json",QJsonDocument(configuredGraph).toJson());
        ASSERT_TRUE(configuredGraph["valid"].toBool());
        ASSERT_EQ(configuredGraph["model"].toObject()["bindings"],beforeClassChange["model"].toObject()["bindings"]);
        const auto retained=rig.neuron->template GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);ASSERT_TRUE(retained);
        ASSERT_DOUBLE_EQ(retained->Capacity.GetData(),1.41e-9);
    }
    NativeCapacitanceCorrection capacitance;
    if(withCapacitance)ASSERT_NO_FATAL_FAILURE(PrepareCapacitanceTransfer(rig,capacitance));
    if(withDormantCapacitance)
    {
        auto requested=rig.learner->ReadNativeParameters();requested[0].length=1;
        const auto edit=rig.learner->ApplyNativeParameters(requested);
        ASSERT_EQ(edit.status,NativeEditStatus::Applied)<<edit.reason;
        ASSERT_FALSE(rig.neuron->GetComponentL("Dendrite1_2",true));
        const auto state=rig.learner->OwnedNativeCapacitanceState();ASSERT_EQ(state["schema_version"],QJsonValue(2));
        ASSERT_EQ(state["dormant_membrane_scales"].toObject()["Dendrite1_2"],QJsonValue(1.1));
        std::string revision;
        capacitance=ParseNativeCapacitanceState(QJsonDocument(state).toJson().toStdString(),revision);
    }
    auto plan=TrainingPlan(rig,sync);plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    plan.maximumWallSeconds=fixtureWallSeconds;
    plan.search.n0CandidateRepeats=n0Repeats;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    if(withDormantCapacitance)
        for(auto& bound:plan.search.bounds)
        {
            // The immutable model declaration starts at L=2, while this
            // transport begins after an explicit shrink to L=1. Preserve
            // TrainingPlan's bounded [1,2] length domain so both the original
            // declaration and the actual warm state remain representable.
            // Ns/Rs stay fixed; the final missing-node assertion below proves
            // this transfer still exercises a genuinely dormant image.
            bound.maximumSynapses=bound.minimumSynapses;
            bound.maximumResistance=bound.minimumResistance;
        }
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
    const auto& service=rig.learner->NativeTrainingController();
    const bool diagnostic=expectation==BoundaryExpectation::DiagnosticSweepBudget;
    if(diagnostic)
    {
        ASSERT_FALSE(service.Certificate());ASSERT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);
        ASSERT_EQ(service.Reason(),"maximum_sweeps_exhausted");ASSERT_TRUE(service.Search());
        ASSERT_TRUE(service.Search()->Certificate());EXPECT_FALSE(service.Search()->Certificate()->Exact());
        ASSERT_FALSE(recognition); // Diagnostic probes do not authorize completed-Train recognition.
    }
    else ASSERT_TRUE(service.Certificate())<<service.Reason();
    if(sync==.2 && inputs==2 && n0Repeats==1)EXPECT_TRUE(service.Certificate()->Exact());
    if(withDormantCapacitance)ASSERT_FALSE(rig.neuron->GetComponentL("Dendrite1_2",true));
    ASSERT_EQ(service.ReferencePackets().size(),inputs);ASSERT_EQ(service.FinalPackets().size(),inputs);
    for(const auto& packet:service.ReferencePackets())EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(EncodeNativeProbeEvidence(packet))),EncodeNativeProbeEvidence(packet));
    for(const auto& packet:service.FinalPackets())EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(EncodeNativeProbeEvidence(packet))),EncodeNativeProbeEvidence(packet));
    const auto original=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();const auto references=service.References()->Inputs();
    const auto certificateValue=[](const NativeTrainingService& value)->QJsonValue {
        return value.Certificate()?QJsonValue(EncodeTrainingCertificate(*value.Certificate())):QJsonValue(QJsonValue::Null);
    };
    const auto certificate=certificateValue(service);
    Artifact(rig.name+"_learned_summary.json",QJsonDocument(EncodeNativeTrainingState(service,original,parameters)).toJson());
    const std::string implementation=diagnostic?"native-stopped-boundary-fixture-v1":"native-learned-boundary-fixture-v1";
    const auto package=rig.learner->ExportNativeLearnedState(implementation);
    if(withCapacitance)
    {
        const auto explicitPackage=rig.learner->ExportNativeLearnedState(implementation,capacitance);
        EXPECT_EQ(package["capacitance_state"],explicitPackage["capacitance_state"]);
        EXPECT_EQ(package["capacitance_state"],QJsonValue(rig.learner->OwnedNativeCapacitanceState()));
        EXPECT_EQ(package["configuration"],explicitPackage["configuration"]);
        EXPECT_EQ(package["trained_inputs"],explicitPackage["trained_inputs"]);
        const auto implicitArchive=package["neuron"].toObject(),explicitArchive=explicitPackage["neuron"].toObject();
        EXPECT_EQ(implicitArchive["graph"].toObject()["identity"],explicitArchive["graph"].toObject()["identity"]);
        EXPECT_EQ(NmsdkTools::ModelImageDefinitionsFingerprint(implicitArchive["class_definitions"].toArray()),
                  NmsdkTools::ModelImageDefinitionsFingerprint(explicitArchive["class_definitions"].toArray()));
        // Native same/fresh-process import and exact response comparisons below
        // consume the implicit export. Incidental XML State bytes need not be
        // identical between two independent exports of the same physics.
    }
    if(withCapacitance)
    {
        EXPECT_EQ(package["schema_version"],QJsonValue(2));
        EXPECT_EQ(package["capacitance_state"].toObject()["baseline"],QJsonValue(capacitance.baseline));
    }
    if(withDormantCapacitance)
    {
        EXPECT_EQ(package["capacitance_state"].toObject()["schema_version"],QJsonValue(2));
        bool retainedImage=false;
        for(const auto& definition:package["neuron"].toObject()["class_definitions"].toArray())
            retainedImage|=definition.toObject()["name"]==QJsonValue(QString::fromStdString(dormantImage));
        EXPECT_TRUE(retainedImage)<<"export must include the image whose last live channel was removed";
    }
    EXPECT_EQ(package["kind"],QJsonValue(diagnostic?"timelearner_stopped_state":"timelearner_completed_state"));
    if(diagnostic)
    {
        EXPECT_TRUE(package["certificate"].isNull());EXPECT_EQ(package["training_outcome"],QJsonValue("budget_exhausted"));
        EXPECT_EQ(package["reason"],QJsonValue("maximum_sweeps_exhausted"));
        const auto& conversionCore=NmsdkTests::InitEngineForPulseLibTests();std::string conversionReason;
        try {ConvertNativeSoloToRecognition(package,{},conversionCore.storage,conversionCore.environment,implementation);}
        catch(const std::invalid_argument& error){conversionReason=error.what();}
        EXPECT_EQ(conversionReason,"recognition_requires_completed_solo");
    }
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
    if(withCapacitance)
    {
        EXPECT_EQ(test->ImportedNativeCapacitanceState(),package["capacitance_state"].toObject());
        EXPECT_EQ(test->ExportNativeLearnedState(implementation)["capacitance_state"],package["capacitance_state"]);
    }
    if(n0Repeats>1)RepeatedBoundarySummary(test->NativeTrainingController(),original,parameters,rig.name+"_imported_summary.json");
    auto testNeuron=test->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto testSource=test->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(testNeuron);ASSERT_TRUE(testSource);
    const auto identity=NmsdkTools::IdentifyModel(testNeuron,{{&testSource->Output,"burst"}});
    EXPECT_EQ(identity["sha256"].toString().toStdString(),original);EXPECT_EQ(test->ReadNativeParameters(),parameters);
    EXPECT_EQ(certificateValue(test->NativeTrainingController()),certificate);
    EXPECT_EQ(test->NativeTrainingController().Outcome(),service.Outcome());
    EXPECT_EQ(test->NativeTrainingController().Reason(),diagnostic?service.Reason():"restored_completed_training_boundary");
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
    EXPECT_EQ(record["model"].toObject()["sha256"],package["model_revision"]);EXPECT_EQ(record["certificate"],certificate);
    Artifact(rig.name+"_fresh_process.json",QJsonDocument(record).toJson());
    QFile csv(output+".csv");ASSERT_TRUE(csv.open(QIODevice::ReadOnly));const auto freshTrace=csv.readAll();
    EXPECT_EQ(freshTrace,QByteArray::fromStdString(frozen.str()));Artifact(rig.name+"_fresh_process.csv",freshTrace);
    // The receiver must not turn this finished boundary into a new cold run.
    for(unsigned i=0;i<8;++i){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    EXPECT_FALSE(test->IsNeedToTrain.GetData());EXPECT_EQ(test->ReadNativeParameters(),parameters);
    test->Reset();EXPECT_EQ(test->NativeTrainingController().References()->Inputs(),references);
    if(diagnostic)
    {
        // Explicit learner Reset clears temporary control, not the physical
        // model. An idle controller is no longer a stopped attempt that can
        // be exported again; retain the already exported immutable package.
        EXPECT_EQ(test->NativeTrainingController().State(),NativeTrainingState::Idle);
        EXPECT_FALSE(test->NativeTrainingController().Certificate());
        EXPECT_EQ(test->ReadNativeParameters(),parameters);
        EXPECT_EQ(NmsdkTools::IdentifyModel(testNeuron,{{&testSource->Output,"burst"}})["sha256"],package["model_revision"]);
        std::string resetExportReason;
        try {test->ExportNativeLearnedState(implementation);}
        catch(const std::invalid_argument& error){resetExportReason=error.what();}
        EXPECT_EQ(resetExportReason,"learned_state_requires_completed_or_stopped_boundary");
    }
    else EXPECT_EQ(test->ExportNativeLearnedState(implementation)["model_revision"],package["model_revision"]);
    const auto outcomeBeforeRejectedImports=test->NativeTrainingController().Outcome();
    const auto stateBeforeRejectedImports=test->NativeTrainingController().State();
    const auto reasonBeforeRejectedImports=test->NativeTrainingController().Reason();
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
        EXPECT_EQ(certificateValue(test->NativeTrainingController()),certificate);
        EXPECT_EQ(test->NativeTrainingController().Outcome(),outcomeBeforeRejectedImports);
        EXPECT_EQ(test->NativeTrainingController().State(),stateBeforeRejectedImports);
        EXPECT_EQ(test->NativeTrainingController().Reason(),reasonBeforeRejectedImports);
    };
    if(withCapacitance)
    {
        corrupted=package;auto correction=corrupted["capacitance_state"].toObject();
        auto scales=correction["membrane_scales"].toObject();scales["Dendrite1_2"]=1.2;
        correction["membrane_scales"]=scales;corrupted["capacitance_state"]=resign(correction);
        rejectWithoutMutation(resign(corrupted));
        EXPECT_EQ(test->ImportedNativeCapacitanceState(),package["capacitance_state"].toObject());
    }
    corrupted=package;auto claim=corrupted["certificate"].toObject();claim["exact"]=!claim["exact"].toBool();corrupted["certificate"]=claim;
    rejectWithoutMutation(resign(corrupted));
    if(!diagnostic)
    {
        // Retain the original completed-boundary missing-final regression.
        // Only diagnostic stopped packages may contain a partial final prefix.
        corrupted=package;auto incompleteFinals=corrupted["final_packets"].toArray();ASSERT_FALSE(incompleteFinals.isEmpty());
        incompleteFinals.removeLast();corrupted["final_packets"]=incompleteFinals;rejectWithoutMutation(resign(corrupted));
    }
    corrupted=package;auto finals=corrupted["final_packets"].toArray();ASSERT_FALSE(finals.isEmpty());
    // A stopped package may legitimately retain a partial final prefix. A
    // duplicate trial is invalid for both package kinds and must be rejected.
    finals.append(finals[0]);corrupted["final_packets"]=finals;
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
        // Storage outlives individual models in the integration process. Each
        // boundary fixture registers its own fault-only factory; reusing the
        // topology-only name makes a later dormant case fail at registration
        // before exercising rollback. Keep duplicate-name rejection in Rdk.
        const auto className=std::string("LearnedImportRollback_")+rig.name;
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
template<class Learner> void CapacitanceCompletedTransport(int normalization,std::optional<RecognitionCase> recognition={})
{
    LearnedBoundary<Learner>(normalization,.2,2000,2,false,recognition,false,1.,1,600.,BoundaryExpectation::Completed,true);
}
TEST(NativeCapacitanceStateTransport,ClassicN0){CapacitanceCompletedTransport<NNeuronTimeLearner>(0);}
TEST(NativeCapacitanceStateTransport,ClassicN1){CapacitanceCompletedTransport<NNeuronTimeLearner>(1);}
TEST(NativeCapacitanceStateTransport,BranchN0){CapacitanceCompletedTransport<NNeuronTimeLearnerBranch>(0);}
TEST(NativeCapacitanceStateTransport,BranchN1){CapacitanceCompletedTransport<NNeuronTimeLearnerBranch>(1);}
TEST(NativeCapacitanceStateTransport,ClassicFrozenIdentity){CapacitanceCompletedTransport<NNeuronTimeLearner>(0,RecognitionCase::OwnedFreshIdentity);}
TEST(NativeCapacitanceStateTransport,BranchFrozenScaled){CapacitanceCompletedTransport<NNeuronTimeLearnerBranch>(1,RecognitionCase::OwnedFreshScaled);}
template<class Learner> void DormantCapacitanceTransport(int normalization)
{
    LearnedBoundary<Learner>(normalization,.2,2000,2,false,{},false,1.,1,600.,BoundaryExpectation::Completed,true,true);
}
TEST(NativeDormantCapacitanceTransport,ClassicN0){DormantCapacitanceTransport<NNeuronTimeLearner>(0);}
TEST(NativeDormantCapacitanceTransport,ClassicN1){DormantCapacitanceTransport<NNeuronTimeLearner>(1);}
TEST(NativeDormantCapacitanceTransport,BranchN0){DormantCapacitanceTransport<NNeuronTimeLearnerBranch>(0);}
TEST(NativeDormantCapacitanceTransport,BranchN1){DormantCapacitanceTransport<NNeuronTimeLearnerBranch>(1);}

template<class Learner> void DiagnosticSweepBudgetBoundary(int normalization)
{
    LearnedBoundary<Learner>(normalization,.02,2000,2,false,{},false,1.,1,600.,BoundaryExpectation::DiagnosticSweepBudget);
}
TEST(NativeLearnedState,ClassicN0){DiagnosticSweepBudgetBoundary<NNeuronTimeLearner>(0);}
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
TEST(NativeCalibrationTransaction,ClassicN1_2000){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,true,RecognitionCase::ThresholdGrid,false,1.,1,1800.);}
TEST(NativeCalibrationTransaction,BranchN1_2000){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::ThresholdGrid,false,1.,1,1800.);}
TEST(NativePostTuneTransaction,ClassicN1_2000){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,true,RecognitionCase::PostTuneTransaction,false,1.,1,1800.);}
TEST(NativePostTuneTransaction,BranchN1_2000){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::PostTuneTransaction,false,1.,1,1800.);}
TEST(NativePostTuneTransaction,ClassicN0_2000){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,true,RecognitionCase::PostTuneTransaction,false,1.,1,1800.);}
TEST(NativePostTuneTransaction,BranchN0_2000){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,true,RecognitionCase::PostTuneTransaction,false,1.,1,1800.);}
TEST(NativeCalibratedState,ClassicN1_2000){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,true,RecognitionCase::CalibratedThreshold,false,1.,1,1800.);}
TEST(NativeCalibratedState,BranchN1_2000){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,true,RecognitionCase::CalibratedThreshold,false,1.,1,1800.);}
TEST(NativeThresholdCandidate,ClassicN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,2000);}
TEST(NativeThresholdCandidate,BranchN0_2000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(0,2000);}
TEST(NativeThresholdCandidate,BranchN1_2000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,2000);}
TEST(NativeThresholdCandidate,ClassicN0_20000){CalibrationBoundaryFixture<NNeuronTimeLearner>(0,20000);}
TEST(NativeThresholdCandidate,ClassicN1_20000){CalibrationBoundaryFixture<NNeuronTimeLearner>(1,20000);}
TEST(NativeThresholdCandidate,BranchN0_20000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(0,20000);}
TEST(NativeThresholdCandidate,BranchN1_20000){CalibrationBoundaryFixture<NNeuronTimeLearnerBranch>(1,20000);}
TEST(NativeLearnedState,BranchN0){DiagnosticSweepBudgetBoundary<NNeuronTimeLearnerBranch>(0);}
TEST(NativeLearnedState,ClassicN1){DiagnosticSweepBudgetBoundary<NNeuronTimeLearner>(1);}
TEST(NativeLearnedState,BranchN1){DiagnosticSweepBudgetBoundary<NNeuronTimeLearnerBranch>(1);}
TEST(NativeLearnedState,ExactCertificateWithExplicitPointTwoTolerance){LearnedBoundary<NNeuronTimeLearner>(1,.2);}

// Transport controls reuse the existing explicitly declared 0.2 fixture.
// Keep the original 0.02 cold-Train cases above/below unchanged: they currently
// exhaust their sweep budget before downstream checks. These separate controls
// must obtain a real Exact certificate, never import a stopped model as trained.
TEST(NativeCompletedTransportExplicitPointTwo,ClassicIdentityN0)
{LearnedBoundary<NNeuronTimeLearner>(0,.2,2000,2,false,RecognitionCase::Identity);}
TEST(NativeCompletedTransportExplicitPointTwo,BranchHistoricalScaleN1)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,.2,2000,2,false,RecognitionCase::Scaled);}
TEST(NativeCompletedTransportExplicitPointTwo,ClassicSpikingFreshN0)
{LearnedBoundary<NNeuronTimeLearner>(0,.2,2000,2,true,RecognitionCase::OwnedFreshIdentity,false,.0001);}
TEST(NativeCompletedTransportExplicitPointTwo,BranchSpikingFreshN1)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,.2,2000,2,true,RecognitionCase::OwnedFreshScaled,false,.0001);}
TEST(NativeCompletedTransportExplicitPointTwo,ClassicCalibrationGridN1)
{LearnedBoundary<NNeuronTimeLearner>(1,.2,2000,2,true,RecognitionCase::ThresholdGrid,false,1.,1,1800.);}
TEST(NativeCompletedTransportExplicitPointTwo,BranchCalibrationGridN1)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,.2,2000,2,true,RecognitionCase::ThresholdGrid,false,1.,1,1800.);}
TEST(NativeCompletedTransportExplicitPointTwo,ClassicPostTuneN0)
{LearnedBoundary<NNeuronTimeLearner>(0,.2,2000,2,true,RecognitionCase::PostTuneTransaction,false,1.,1,1800.);}
TEST(NativeCompletedTransportExplicitPointTwo,BranchPostTuneN1)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,.2,2000,2,true,RecognitionCase::PostTuneTransaction,false,1.,1,1800.);}
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
TEST(NativePostTuneCandidates,ClassicN0){LearnedBoundary<NNeuronTimeLearner>(0,.02,2000,2,false,RecognitionCase::PostTuneCandidates);}
TEST(NativePostTuneCandidates,BranchN0){LearnedBoundary<NNeuronTimeLearnerBranch>(0,.02,2000,2,false,RecognitionCase::PostTuneCandidates);}
TEST(NativePostTuneCandidates,ClassicN1){LearnedBoundary<NNeuronTimeLearner>(1,.02,2000,2,false,RecognitionCase::PostTuneCandidates);}
TEST(NativePostTuneCandidates,BranchN1){LearnedBoundary<NNeuronTimeLearnerBranch>(1,.02,2000,2,false,RecognitionCase::PostTuneCandidates);}
TEST(NativePostTuneCandidates,StrictSpecification)
{
    NativeRecognitionSpec spec;NativePostTuneSpec post;post.sourceModelRevision=std::string(64,'a');spec.postTune=post;
    const auto encoded=EncodeNativeRecognitionSpec(spec);
    EXPECT_EQ(encoded["schema_version"],QJsonValue(2));
    EXPECT_EQ(EncodeNativeRecognitionSpec(DecodeNativeRecognitionSpec(encoded)),encoded);
    auto invalid=encoded;invalid["unused"]=0;EXPECT_THROW(DecodeNativeRecognitionSpec(invalid),std::invalid_argument);
    invalid=encoded;auto p=invalid["post_tune"].toObject();p["mode"]="search_synthetic";invalid["post_tune"]=p;
    EXPECT_THROW(DecodeNativeRecognitionSpec(invalid),std::invalid_argument);
    spec.postTune->canonicalFloor=1.;EXPECT_THROW(EncodeNativeRecognitionSpec(spec),std::invalid_argument);
    spec.postTune->canonicalFloor=0.;spec.postTune->requestedResistances={1.};
    EXPECT_THROW(EncodeNativeRecognitionSpec(spec),std::invalid_argument);
    spec.postTune->requestedResistances.clear();spec.postTune->sourceModelRevision=std::string(64,'A');
    EXPECT_THROW(EncodeNativeRecognitionSpec(spec),std::invalid_argument);
}
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

template<class Learner> void TrainingIntentLifecycle(int mode,bool connected)
{
    EditingRig<Learner> rig(2000,1,"request_intent_"+std::to_string(mode)+(connected?"_connected":"_local"));
    auto plan=TrainingPlan(rig);plan.maximumModelSeconds=.01;
    rig.learner->CalculateMode=mode;rig.learner->CalibrateLTZThresholdFraction=.37;
    UEPtr<ConnectedTrainingFlag> flag;
    if(connected) {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        flag=UEPtr<ConnectedTrainingFlag>(new ConnectedTrainingFlag);
        flag->SetStorage(core.storage);flag->SetEnvironment(core.environment);flag->Default();
        flag->Name="RequestIntentProvider";flag->Activity=true;flag->SetGlobalTimeStep(rig.frequency);
        UEPtr<UContainer> node=flag;ASSERT_NE(rig.model->AddComponent(node),ForbiddenId);flag->Init();flag->Value=true;
        ASSERT_TRUE(rig.learner->IsNeedToTrain.SetPointer(0,&flag->Value));
    }
    EXPECT_TRUE(rig.learner->NativeTrainingRequest().isEmpty());
    rig.learner->BeginNativeTraining(plan);
    const auto first=rig.learner->NativeTrainingRequest();ASSERT_FALSE(first.isEmpty());
    EXPECT_EQ(first["kind"],QJsonValue("native_training_request_intent"));
    auto unsignedFirst=first;unsignedFirst.remove("sha256");
    EXPECT_EQ(first["sha256"],QJsonValue(NmsdkTools::CanonicalModelDataSha256(unsignedFirst)));
    const auto controls=first["controls"].toObject(),parameters=controls["parameters"].toObject();
    EXPECT_EQ(parameters["CalculateMode"],QJsonValue(mode));EXPECT_TRUE(parameters["IsNeedToTrain"].toBool());
    EXPECT_DOUBLE_EQ(parameters["CalibrateLTZThresholdFraction"].toDouble(),.37);
    EXPECT_EQ(controls["bindings"].toObject()["IsNeedToTrain"].toObject()["connected"],QJsonValue(connected));
    // A later control edit is observable separately; it cannot rewrite the
    // declaration that a future finalization driver must validate.
    rig.learner->CalibrateLTZThresholdFraction=.63;
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks) {
        ASSERT_LT(ticks,100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    }
    EXPECT_EQ(rig.learner->NativeTrainingController().Outcome(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(rig.learner->NativeTrainingRequest(),first);
    EXPECT_EQ(rig.learner->IsNeedToTrain.GetData(),connected || mode==1);
    if(flag)EXPECT_TRUE(flag->Value.GetData());
    const auto unchangedModel=rig.Revision();std::string driftReason;
    try {(void)CaptureNativeFinalizationBoundary(*rig.learner,"request-intent-test",true);}
    catch(const std::logic_error& error){driftReason=error.what();}
    EXPECT_EQ(driftReason,"native_training_request_controls_changed");
    EXPECT_EQ(rig.Revision(),unchangedModel);EXPECT_EQ(rig.learner->NativeTrainingRequest(),first);
    auto edited=rig.learner->NativeTrainingRequest();edited["controls"]=QJsonObject{};
    EXPECT_EQ(rig.learner->NativeTrainingRequest(),first);
    const auto bad=rig.learner->ImportNativeLearnedState(QJsonObject{},"request-intent-test");
    EXPECT_NE(bad.status,NativeModelBuildStatus::Adopted);EXPECT_EQ(rig.learner->NativeTrainingRequest(),first);
    const auto geometry=rig.learner->ReadNativeParameters();rig.learner->Reset();
    EXPECT_TRUE(rig.learner->NativeTrainingRequest().isEmpty());EXPECT_EQ(rig.learner->ReadNativeParameters(),geometry);
    rig.learner->BeginNativeTraining(plan);const auto second=rig.learner->NativeTrainingRequest();ASSERT_FALSE(second.isEmpty());
    EXPECT_GT(second["session_attempt"].toDouble(),first["session_attempt"].toDouble());
    EXPECT_DOUBLE_EQ(second["controls"].toObject()["parameters"].toObject()["CalibrateLTZThresholdFraction"].toDouble(),.63);
    if(flag)flag->Value=false;else rig.learner->IsNeedToTrain=false;
    rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();
    EXPECT_EQ(rig.learner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
    EXPECT_EQ(rig.learner->NativeTrainingRequest(),second);EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());
    const auto stopped=CaptureNativeFinalizationBoundary(*rig.learner,"request-intent-test",true);
    EXPECT_TRUE(stopped.DiagnosticOnly());EXPECT_EQ(stopped.Document()["schema_version"],QJsonValue(2));
    EXPECT_EQ(stopped.Document()["training_request"],second);
    const auto imported=rig.learner->ImportNativeLearnedState(stopped.Solo(),"request-intent-test");
    EXPECT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    const auto afterImport=rig.learner->NativeTrainingRequest();EXPECT_TRUE(afterImport.isEmpty());
    rig.learner->Build();rig.learner->Init();
    rig.learner->Reset();if(flag)flag->Value=true;
    rig.learner->BeginNativeTraining(plan);const auto third=rig.learner->NativeTrainingRequest();ASSERT_FALSE(third.isEmpty());
    const auto unchanged=rig.learner->InputPattern.GetData();rig.learner->InputPattern=unchanged;
    EXPECT_EQ(rig.learner->NativeTrainingRequest(),third);
    auto changed=unchanged;changed(0,0)+=.001;rig.learner->InputPattern=changed;
    EXPECT_TRUE(rig.learner->NativeTrainingRequest().isEmpty());
    Artifact(rig.name+"_request_intent.json",QJsonDocument(QJsonObject{
        {"kind","native_training_request_intent_lifecycle"},{"schema_version",2},
        {"calculate_mode",mode},{"connected",connected},{"first",first},{"second",second},{"third",third},
        {"after_retarget",rig.learner->NativeTrainingRequest()},
        {"control_drift_reason",QString::fromStdString(driftReason)},
        {"stopped_boundary",stopped.Document()},{"import_adopted",imported.status==NativeModelBuildStatus::Adopted},
        {"after_import",afterImport},
        {"final_outcome",TrainingStatusName(rig.learner->NativeTrainingController().Outcome())},
        {"final_reason",QString::fromStdString(rig.learner->NativeTrainingController().Reason())},
        {"calibrated",false},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    if(flag)rig.learner->IsNeedToTrain.DetachFrom();
}
#define TRAINING_INTENT_TESTS(TOPOLOGY,TYPE) \
TEST(NativeTrainingIntent,TOPOLOGY##Local0){TrainingIntentLifecycle<TYPE>(0,false);} \
TEST(NativeTrainingIntent,TOPOLOGY##Local1){TrainingIntentLifecycle<TYPE>(1,false);} \
TEST(NativeTrainingIntent,TOPOLOGY##Connected0){TrainingIntentLifecycle<TYPE>(0,true);} \
TEST(NativeTrainingIntent,TOPOLOGY##Connected1){TrainingIntentLifecycle<TYPE>(1,true);}
TRAINING_INTENT_TESTS(Classic,NNeuronTimeLearner)
TRAINING_INTENT_TESTS(Branch,NNeuronTimeLearnerBranch)
#undef TRAINING_INTENT_TESTS

enum class StoppedCase { Early, Partial, BudgetEarly, BudgetSearch, Search, Final, InvalidProbe, ChangedPartial, RepeatPartial };
template<class Learner> void StoppedBoundary(StoppedCase scenario,const std::string& label,int normalization=1,bool configured=false,unsigned n0Repeats=1,bool withCapacitance=false)
{
    EditingRig<Learner> rig(2000,normalization,"stopped_"+label,false,2,withCapacitance);auto plan=TrainingPlan(rig);
    NativeCapacitanceCorrection capacitance;
    if(withCapacitance)ASSERT_NO_FATAL_FAILURE(PrepareCapacitanceTransfer(rig,capacitance));
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
    if(withCapacitance)
    {
        const auto explicitPackage=rig.learner->ExportNativeLearnedState(implementation,capacitance);
        EXPECT_EQ(package["capacitance_state"],explicitPackage["capacitance_state"]);
        EXPECT_EQ(package["capacitance_state"],QJsonValue(rig.learner->OwnedNativeCapacitanceState()));
        EXPECT_EQ(package["configuration"],explicitPackage["configuration"]);
        EXPECT_EQ(package["trained_inputs"],explicitPackage["trained_inputs"]);
        const auto implicitArchive=package["neuron"].toObject(),explicitArchive=explicitPackage["neuron"].toObject();
        EXPECT_EQ(implicitArchive["graph"].toObject()["identity"],explicitArchive["graph"].toObject()["identity"]);
        EXPECT_EQ(NmsdkTools::ModelImageDefinitionsFingerprint(implicitArchive["class_definitions"].toArray()),
                  NmsdkTools::ModelImageDefinitionsFingerprint(explicitArchive["class_definitions"].toArray()));
        // Native same/fresh-process import and exact response comparisons below
        // consume the implicit export. Incidental XML State bytes need not be
        // identical between two independent exports of the same physics.
    }
    if(withCapacitance)EXPECT_EQ(package["schema_version"],QJsonValue(2));
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
    if(withCapacitance)
    {
        EXPECT_EQ(test->ImportedNativeCapacitanceState(),package["capacitance_state"].toObject());
        EXPECT_EQ(test->ExportNativeLearnedState(implementation)["capacitance_state"],package["capacitance_state"]);
    }
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
TEST(NativeCapacitanceStateTransport,ClassicStoppedPartial){StoppedBoundary<NNeuronTimeLearner>(StoppedCase::Partial,"CapacitancePartial",0,false,1,true);}
TEST(NativeCapacitanceStateTransport,BranchStoppedPartial){StoppedBoundary<NNeuronTimeLearnerBranch>(StoppedCase::Partial,"CapacitancePartial",1,false,1,true);}

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
    RecordNativeTrainingProof(plan,rig.name,rig.inputCount);
    for(auto& bound:plan.search.bounds){bound.maximumLength=bound.minimumLength;bound.maximumResistance=bound.minimumResistance;}
    const auto run=[&] {
        rig.learner->BeginNativeTraining(plan);
        for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
        {ASSERT_LT(ticks,20000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    };
    run();const auto& service=rig.learner->NativeTrainingController();
    Artifact(rig.name+"_cold_outcome.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    ASSERT_EQ(service.Outcome(),TrainingStatus::Exact)<<service.Reason();ASSERT_TRUE(service.Certificate());
    EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());EXPECT_TRUE(service.Certificate()->Exact());
    const auto captured=service.References()->Inputs();const auto hash=rig.Revision();
    ASSERT_EQ(service.ReferenceObservations().size(),2u);
    const auto originalReferenceTrial=service.ReferenceObservations()[0].observation.specification.trialId;
    rig.learner->Reset();EXPECT_EQ(rig.Revision(),hash);ASSERT_TRUE(service.Certificate());
    ASSERT_EQ(service.ReferenceObservations().size(),2u);
    run();EXPECT_EQ(service.Outcome(),TrainingStatus::Exact);EXPECT_EQ(service.IssuedReferenceProbes(),0u);
    Artifact(rig.name+"_warm_outcome.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    ASSERT_TRUE(service.References());EXPECT_EQ(service.References()->Inputs(),captured);
    ASSERT_EQ(service.ReferenceObservations().size(),2u);
    EXPECT_EQ(service.ReferenceObservations()[0].observation.specification.trialId,originalReferenceTrial);
    auto pattern=rig.learner->InputPattern.GetData();pattern(1,0)+=.01;rig.learner->InputPattern=pattern;
    EXPECT_FALSE(service.References());EXPECT_FALSE(service.Certificate());
    EXPECT_TRUE(service.ReferenceObservations().empty());
    EXPECT_NE(service.Outcome(),TrainingStatus::Exact);
    Artifact(rig.name+"_retarget_control.json",QJsonDocument(QJsonObject{
        {"kind","native_retarget_invalidation"},{"schema_version",1},
        {"references",bool(service.References())},{"certificate",bool(service.Certificate())},
        {"outcome",TrainingStatusName(service.Outcome())},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}

template<class Learner> void StopNativeTraining()
{
    EditingRig<Learner> rig(2000,0,"service_external_stop");auto plan=TrainingPlan(rig);
    std::vector<NativeProbeResult> recorded;plan.observationSink=[&](const auto& result){recorded.push_back(result);};
    RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
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
    plan.observationSink=[&](const auto& result){recorded.push_back(result);};
    RecordNativeTrainingProof(plan,rig.name,1u);rig.learner->BeginNativeTraining(plan);
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
    RecordNativeTrainingProof(plan,rig.name,rig.inputCount);
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
    RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
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

enum class PostTuneObservationCase { PreviousResult,PreviousSamples,MissingFoil,Nonfinite };
template<class Learner> void PostTuneInferenceObservation(PostTuneObservationCase scenario)
{
    using Owner=PostTuneObservationLearner<Learner>;
    constexpr bool branch=std::is_base_of<NNeuronTimeLearnerBranch,Learner>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string image=branch?"PostTuneObservationBranchFixture":"PostTuneObservationClassicFixture";
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new Owner;},image),image);
    const std::string suffix="posttune_observation_"+std::to_string(int(scenario));
    EditingRig<Owner> rig(2000,1,suffix,false,2,true,2,1,false,image);
    auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
    MDMatrix<double> matrix;matrix.Assign(4,1,0.);
    matrix(0,0)=.01;matrix(1,0)=.08;matrix(2,0)=.01;matrix(3,0)=.20;
    ASSERT_TRUE(dataset->SetMatrixData(matrix));
    MDMatrix<int> labels;labels.Assign(1,2,0);labels(0,0)=1;ASSERT_TRUE(dataset->SetMatrixClasses(labels));
    rig.learner->SeedPreviousInference(scenario!=PostTuneObservationCase::PreviousResult);
    ASSERT_TRUE(rig.learner->StartMatrixInference());
    const auto evidence=[&] {
        return QJsonObject{{"kind","legacy_posttune_inference_observation_regression"},{"schema_version",1},
            {"case",int(scenario)},{"topology",branch?"branch":"classic"},
            {"result",rig.learner->PostTuneResult.GetData()},{"threshold",rig.learner->FixedLTZThreshold.GetData()},
            {"sample_count",double(rig.learner->SampleCount())},{"any_sample_observed",rig.learner->AnySampleObserved()},
            {"all_samples_valid",rig.learner->AllSamplesValid()},{"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    };
    if(scenario==PostTuneObservationCase::PreviousResult || scenario==PostTuneObservationCase::PreviousSamples)
    {
        Artifact(rig.name+"_start.json",QJsonDocument(evidence()).toJson());
        if(scenario==PostTuneObservationCase::PreviousResult)
            EXPECT_EQ(rig.learner->PostTuneResult.GetData(),PostTrainTune::kResultNone);
        else
        {
            EXPECT_EQ(rig.learner->SampleCount(),2u);
            EXPECT_FALSE(rig.learner->AnySampleObserved());EXPECT_FALSE(rig.learner->AllSamplesValid());
        }
        return;
    }
    // Fault injection into real typed soma outputs and Dataset termination.
    // No model tick or synthetic CSV is presented as a physical experiment.
    for(std::size_t i=0;i<(branch?1u:2u);++i)
    {
        auto soma=rig.neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);
        soma->SumPotential(0,0)=i==0?.5:0.;
        if(scenario==PostTuneObservationCase::Nonfinite && i==0)
            soma->SumPotential(0,0)=std::numeric_limits<double>::quiet_NaN();
    }
    dataset->Iteration.SetDataDirect(0);dataset->StateGeneration=2;
    rig.learner->ObserveLiveMetric();
    dataset->StateGeneration=0; // Foil was never visited in this attempt.
    rig.learner->ObserveLiveMetric();
    Artifact(rig.name+"_terminal.json",QJsonDocument(evidence()).toJson());
    EXPECT_EQ(rig.learner->PostTuneResult.GetData(),PostTrainTune::kResultInvalidMetrics);
    EXPECT_DOUBLE_EQ(rig.learner->FixedLTZThreshold.GetData(),1.);
    EXPECT_FALSE(rig.learner->AllSamplesValid());
}
#define POSTTUNE_OBSERVATION_CASE(Name,Case) \
TEST(LegacyPostTuneInferenceObservation,Classic##Name){PostTuneInferenceObservation<NNeuronTimeLearner>(PostTuneObservationCase::Case);} \
TEST(LegacyPostTuneInferenceObservation,Branch##Name){PostTuneInferenceObservation<NNeuronTimeLearnerBranch>(PostTuneObservationCase::Case);}
POSTTUNE_OBSERVATION_CASE(PreviousResult,PreviousResult)
POSTTUNE_OBSERVATION_CASE(PreviousSamples,PreviousSamples)
POSTTUNE_OBSERVATION_CASE(MissingFoil,MissingFoil)
POSTTUNE_OBSERVATION_CASE(Nonfinite,Nonfinite)
#undef POSTTUNE_OBSERVATION_CASE

template<class Learner> void PostTuneInferencePhysicalFreeRun(unsigned frequency)
{
    using Owner=PostTuneObservationLearner<Learner>;
    constexpr bool branch=std::is_base_of<NNeuronTimeLearnerBranch,Learner>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    const std::string image=std::string(branch?"PostTunePhysicalBranchFixture":"PostTunePhysicalClassicFixture")+std::to_string(frequency);
    if(!core.storage->CheckClass(image))core.storage->AddClass(new UComponentFactoryMethod(core.storage,
        +[]() -> UComponent* {return new Owner;},image),image);
    // The numerical playback must dispatch through the actual legacy scheduler;
    // a native-owned graph intentionally bypasses the legacy PostTune tracker.
    EditingRig<Owner> rig(frequency,1,"posttune_inference_physical",false,2,false,2,1,false,image);
    ASSERT_FALSE(rig.learner->IsNativeOwned());
    auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
    const auto goal=rig.learner->InputPattern.GetData();const auto before=rig.learner->ReadNativeParameters();
    MDMatrix<double> matrix;matrix.Assign(4,1,0.);
    matrix(0,0)=.01;matrix(1,0)=.08;matrix(2,0)=.01;matrix(3,0)=.20;
    ASSERT_TRUE(dataset->SetMatrixData(matrix));
    MDMatrix<int> labels;labels.Assign(1,2,0);labels(0,0)=1;ASSERT_TRUE(dataset->SetMatrixClasses(labels));
    rig.learner->SeedPreviousInference(true);ASSERT_TRUE(rig.learner->StartMatrixInference());
    const double begin=rig.environment->GetTime().GetDoubleTime();
    std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17)<<"time,stimulus";
    for(std::size_t i=0;i<(branch?1u:2u);++i)trace<<",soma"<<i;
    trace<<",dataset_iteration,state_generation,selected_metric\n";
    QJsonArray stimulus;double previous=0.;std::size_t ticks=0;
    while(!rig.learner->PostTrainTuneComplete.GetData())
    {
        ASSERT_LT(ticks,frequency*10u)<<"legacy free-run did not terminate";
        rig.model->Calculate();const double time=rig.environment->GetTime().GetDoubleTime(),input=rig.source->Output(0,0);
        if(input>0. && previous<=0.)stimulus.append(time);previous=input;
        trace<<time<<','<<input;
        for(std::size_t i=0;i<(branch?1u:2u);++i)
        {
            auto soma=rig.neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);
            trace<<','<<soma->SumPotential(0,0);
        }
        trace<<','<<dataset->Iteration.GetData()<<','<<dataset->StateGeneration.GetData()<<','<<rig.learner->LiveMetric()<<'\n';
        rig.environment->IncreaseModelTimeByStep();++ticks;
    }
    const auto after=rig.learner->ReadNativeParameters();
    Artifact(rig.name+".csv",QByteArray::fromStdString(trace.str()));
    Artifact(rig.name+".json",QJsonDocument(QJsonObject{
        {"kind","legacy_posttune_physical_freerun"},{"schema_version",1},{"topology",branch?"branch":"classic"},
        {"frequency_hz",int(frequency)},{"begin",begin},{"end",rig.environment->GetTime().GetDoubleTime()},
        {"ticks",double(ticks)},{"soma_channels",branch?1:2},{"stimulus_times",stimulus},
        {"pattern_isi",QJsonArray({QJsonArray({.01,.08}),QJsonArray({.01,.20})})},
        {"sample_labels",QJsonArray({"target","foil"})},{"metric","simultaneous_soma_sum"},
        {"states",rig.learner->SampleStates()},{"all_samples_valid",rig.learner->AllSamplesValid()},
        {"result",rig.learner->PostTuneResult.GetData()},{"threshold",rig.learner->FixedLTZThreshold.GetData()},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    EXPECT_TRUE(rig.learner->AllSamplesValid());EXPECT_EQ(rig.learner->SampleCount(),2u);EXPECT_EQ(stimulus.size(),4);
    EXPECT_TRUE(NativeTrainingPatternEqual(rig.learner->InputPattern.GetData(),goal));
    ASSERT_EQ(before.size(),after.size());for(std::size_t i=0;i<before.size();++i)
    {
        EXPECT_EQ(before[i].length,after[i].length);EXPECT_EQ(before[i].synapses,after[i].synapses);
        EXPECT_DOUBLE_EQ(before[i].resistance,after[i].resistance);
    }
    EXPECT_TRUE(rig.learner->PostTuneResult.GetData()==PostTrainTune::kResultSuccess ||
                rig.learner->PostTuneResult.GetData()==PostTrainTune::kResultNonSeparable ||
                rig.learner->PostTuneResult.GetData()==PostTrainTune::kResultBestEffort);
}
TEST(LegacyPostTunePhysicalFreeRun,Classic2000){PostTuneInferencePhysicalFreeRun<NNeuronTimeLearner>(2000);}
TEST(LegacyPostTunePhysicalFreeRun,Branch2000){PostTuneInferencePhysicalFreeRun<NNeuronTimeLearnerBranch>(2000);}
TEST(LegacyPostTunePhysicalFreeRun,Classic20000){PostTuneInferencePhysicalFreeRun<NNeuronTimeLearner>(20000);}
TEST(LegacyPostTunePhysicalFreeRun,Branch20000){PostTuneInferencePhysicalFreeRun<NNeuronTimeLearnerBranch>(20000);}

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

void RecordNativeTrainingProof(NativeTrainingPlan& plan,const std::string& caseName,std::size_t channels)
{
    struct Trace {std::ostringstream csv;std::string trial;std::size_t packet=0;};
    auto trace=std::make_shared<Trace>();
    std::ostringstream columns;columns<<"time,stimulus";
    for(std::size_t i=0;i<channels;++i)columns<<",soma"<<i;columns<<'\n';
    const auto header=columns.str();trace->csv<<header;
    const auto previousPrepared=plan.probe.onPrepared;
    const auto previousSample=plan.probe.onSample;
    const auto previousSink=plan.observationSink;
    plan.probe.onPrepared=[trace,header,previousPrepared](const PreparedVerificationProbe& prepared,const ProbeSpec& spec) {
        trace->trial=spec.trialId;trace->csv.str({});trace->csv.clear();trace->csv.imbue(std::locale::classic());
        trace->csv<<std::setprecision(17)<<header;
        if(previousPrepared)previousPrepared(prepared,spec);
    };
    plan.probe.onSample=[trace,previousSample](const NativeProbeSample& sample) {
        trace->csv<<sample.time<<','<<sample.stimulus;
        for(double value:sample.potentials)trace->csv<<','<<value;trace->csv<<'\n';
        if(previousSample)previousSample(sample);
    };
    plan.observationSink=[trace,caseName,header,previousSink](const NativeProbeResult& result) {
        const auto name=caseName+"_training_proof_"+std::to_string(++trace->packet);
        Artifact(name+".json",QJsonDocument(EncodeNativeProbeEvidence(result)).toJson());
        const bool recorded=result.observation && result.observation->specification.trialId==trace->trial;
        Artifact(name+".csv",QByteArray::fromStdString(recorded?trace->csv.str():header));
        if(previousSink)previousSink(result);
    };
}

template<class Learner> void NativePostTuneOwnerPolicy(unsigned frequency,int normalization)
{
    EditingRig<Learner> rig(frequency,normalization,"posttune_owner_policy",false,2,true);
    if(frequency==20000)rig.learner->CalculateMode=0;
    auto plan=TrainingPlan(rig);plan.search.tolerances.sync=1.;
    RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
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
        RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
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
    RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
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

// V2's verified single-rate native protocol requires every required child to
// run. Rdk's optional wall-clock budget is a separate compatibility behavior.
template<class Learner> void RejectNativeWallLimitedProbe(int normalization,const std::string& node,long long limit)
{
    EditingRig<Learner> rig(2000,normalization,"wall_limit_"+node+"_"+std::to_string(limit),false,2,true);
    UEPtr<UContainer> target;
    if(node=="owner")target=rig.learner;
    else if(node=="ancestor")target=rig.model;
    else if(node=="neuron")target=rig.neuron;
    else if(node=="generator")target=rig.source;
    ASSERT_TRUE(target);const auto original=target->MaxCalculationDuration.GetData();
    ASSERT_LT(original,0);target->MaxCalculationDuration=limit;
    const auto revision=rig.Revision();const auto parameters=rig.learner->ReadNativeParameters();
    std::size_t samples=0;
    const auto result=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true,false,
        [&](const NativeProbeSample&){++samples;});
    // The V2 guard must diagnose unsupported scheduling, never repair a user's
    // inherited Rdk property or require special Reset/Build return values.
    const auto effectiveLimit=target->MaxCalculationDuration.GetData();
    target->MaxCalculationDuration=original;
    EXPECT_EQ(effectiveLimit,limit);EXPECT_EQ(result.status,NativeProbeStatus::Rejected);
    EXPECT_FALSE(result.observation);EXPECT_EQ(samples,0u);
    EXPECT_NE(std::find(result.reasons.begin(),result.reasons.end(),"unsupported_native_wall_limited_schedule"),result.reasons.end());
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    QJsonArray reasons;for(const auto& reason:result.reasons)reasons.append(QString::fromStdString(reason));
    Artifact(rig.name+"_wall_policy.json",QJsonDocument(QJsonObject{
        {"kind","native_wall_schedule_policy"},{"schema_version",1},{"location",QString::fromStdString(node)},
        {"configured_limit",double(limit)},{"effective_limit_after_probe",double(effectiveLimit)},
        {"observed_samples",double(samples)},{"status",NativeProbeStatusName(result.status)},
        {"reasons",reasons},{"changed_individual_parameters",rig.learner->ReadNativeParameters()!=parameters},
        {"limited_revision",QString::fromStdString(revision)},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    if(result.status==NativeProbeStatus::Rejected && node=="owner" && limit>0)
    {
        // This is a whole-burst observation: isolated-window selection would
        // correctly reject its two peaks as ambiguous. Keep the actual burst
        // protocol and assign the requested wave by its stimulus ID.
        const auto restored=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true);ASSERT_EQ(restored.status,NativeProbeStatus::Completed);
        ASSERT_TRUE(restored.observation);EXPECT_TRUE(restored.observation->complete);
        EXPECT_TRUE(restored.observation->valid);
        ASSERT_EQ(restored.observation->peaks.size(),1u);
        EXPECT_EQ(restored.observation->peaks[0].stimulusId,"pulse0");
        EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    }
}
#define WALL_CASE(Name,Learner,Norm,Node,Limit) \
 TEST(NativeWallSchedule,Name){RejectNativeWallLimitedProbe<Learner>(Norm,Node,Limit);}
WALL_CASE(ClassicN0OwnerZero,NNeuronTimeLearner,0,"owner",0)
WALL_CASE(ClassicN0OwnerLarge,NNeuronTimeLearner,0,"owner",1000000000)
WALL_CASE(ClassicN0AncestorZero,NNeuronTimeLearner,0,"ancestor",0)
WALL_CASE(ClassicN0AncestorLarge,NNeuronTimeLearner,0,"ancestor",1000000000)
WALL_CASE(ClassicN0NeuronZero,NNeuronTimeLearner,0,"neuron",0)
WALL_CASE(ClassicN0NeuronLarge,NNeuronTimeLearner,0,"neuron",1000000000)
WALL_CASE(ClassicN0GeneratorZero,NNeuronTimeLearner,0,"generator",0)
WALL_CASE(ClassicN0GeneratorLarge,NNeuronTimeLearner,0,"generator",1000000000)
WALL_CASE(ClassicN1OwnerZero,NNeuronTimeLearner,1,"owner",0)
WALL_CASE(ClassicN1OwnerLarge,NNeuronTimeLearner,1,"owner",1000000000)
WALL_CASE(ClassicN1AncestorZero,NNeuronTimeLearner,1,"ancestor",0)
WALL_CASE(ClassicN1AncestorLarge,NNeuronTimeLearner,1,"ancestor",1000000000)
WALL_CASE(ClassicN1NeuronZero,NNeuronTimeLearner,1,"neuron",0)
WALL_CASE(ClassicN1NeuronLarge,NNeuronTimeLearner,1,"neuron",1000000000)
WALL_CASE(ClassicN1GeneratorZero,NNeuronTimeLearner,1,"generator",0)
WALL_CASE(ClassicN1GeneratorLarge,NNeuronTimeLearner,1,"generator",1000000000)
WALL_CASE(BranchN0OwnerZero,NNeuronTimeLearnerBranch,0,"owner",0)
WALL_CASE(BranchN0OwnerLarge,NNeuronTimeLearnerBranch,0,"owner",1000000000)
WALL_CASE(BranchN0AncestorZero,NNeuronTimeLearnerBranch,0,"ancestor",0)
WALL_CASE(BranchN0AncestorLarge,NNeuronTimeLearnerBranch,0,"ancestor",1000000000)
WALL_CASE(BranchN0NeuronZero,NNeuronTimeLearnerBranch,0,"neuron",0)
WALL_CASE(BranchN0NeuronLarge,NNeuronTimeLearnerBranch,0,"neuron",1000000000)
WALL_CASE(BranchN0GeneratorZero,NNeuronTimeLearnerBranch,0,"generator",0)
WALL_CASE(BranchN0GeneratorLarge,NNeuronTimeLearnerBranch,0,"generator",1000000000)
WALL_CASE(BranchN1OwnerZero,NNeuronTimeLearnerBranch,1,"owner",0)
WALL_CASE(BranchN1OwnerLarge,NNeuronTimeLearnerBranch,1,"owner",1000000000)
WALL_CASE(BranchN1AncestorZero,NNeuronTimeLearnerBranch,1,"ancestor",0)
WALL_CASE(BranchN1AncestorLarge,NNeuronTimeLearnerBranch,1,"ancestor",1000000000)
WALL_CASE(BranchN1NeuronZero,NNeuronTimeLearnerBranch,1,"neuron",0)
WALL_CASE(BranchN1NeuronLarge,NNeuronTimeLearnerBranch,1,"neuron",1000000000)
WALL_CASE(BranchN1GeneratorZero,NNeuronTimeLearnerBranch,1,"generator",0)
WALL_CASE(BranchN1GeneratorLarge,NNeuronTimeLearnerBranch,1,"generator",1000000000)
#undef WALL_CASE

template<class Learner> void ChangeWallPolicyWhileRecording(int normalization,bool finalSample)
{
    EditingRig<Learner> rig(2000,normalization,finalSample?"wall_live_final":"wall_live_mid",false,2,true);
    const auto parameters=rig.learner->ReadNativeParameters();
    const auto before=rig.environment->GetTime().GetDoubleTime();
    const auto old=rig.learner->MaxCalculationDuration.GetData();bool changed=false;std::size_t samples=0;
    const auto result=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true,false,
        [&](const NativeProbeSample& sample){
            ++samples;
            if(!changed && ((!finalSample && samples==2) ||
                (finalSample && sample.time+1e-12>=before+rig.duration)))
            {rig.learner->MaxCalculationDuration=1000000000LL;changed=true;}
        });
    const auto limit=rig.learner->MaxCalculationDuration.GetData();rig.learner->MaxCalculationDuration=old;
    ASSERT_TRUE(changed);EXPECT_EQ(limit,1000000000LL);EXPECT_EQ(result.status,NativeProbeStatus::Rejected);
    ASSERT_TRUE(result.observation);EXPECT_FALSE(result.observation->valid);
    EXPECT_EQ(result.observation->complete,finalSample);EXPECT_TRUE(result.requiresFreshVerification);
    EXPECT_EQ(result.observation->sampleCount,samples);
    if(!finalSample)EXPECT_EQ(samples,2u);
    EXPECT_NE(std::find(result.reasons.begin(),result.reasons.end(),"unsupported_native_wall_limited_schedule"),result.reasons.end());
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    Artifact(rig.name+"_live_wall_policy.json",QJsonDocument(QJsonObject{
        {"kind","native_live_wall_policy"},{"schema_version",1},{"changed_on_final_sample",finalSample},
        {"samples",double(samples)},{"window_complete",result.observation->complete},
        {"valid",result.observation->valid},{"status",NativeProbeStatusName(result.status)},
        {"partial_observation_preserved",true},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
template<class Learner> void ResetFromWallControlCallback(bool finalSample)
{
    EditingRig<Learner> rig(2000,1,finalSample?"wall_callback_reset_final":"wall_callback_reset_mid",false,2,true);
    const auto before=rig.environment->GetTime().GetDoubleTime();const auto parameters=rig.learner->ReadNativeParameters();
    std::vector<NativeProbeSample> frames;bool reset=false;std::string diagnostic;
    try {
        (void)rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::IsolatedWindow,true,false,
            [&](const NativeProbeSample& sample){
                frames.push_back(sample);
                if(!reset && ((!finalSample && frames.size()==2) ||
                    (finalSample && sample.time+1e-12>=before+rig.duration)))
                {reset=true;rig.learner->Reset();}
            });
    }
    catch(const std::runtime_error& error){diagnostic=error.what();}
    ASSERT_TRUE(reset);EXPECT_EQ(diagnostic,"missing_editor_fixture_result");
    EXPECT_EQ(rig.learner->NativeProbeState(),NativeProbeStatus::Idle);
    EXPECT_FALSE(rig.learner->TakeNativeProbeResult());EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    EXPECT_EQ(frames.size(),finalSample?361u:2u);
    // Explicit Reset discards the pending native result by contract. Preserve
    // raw callback samples as a labelled reset diagnostic, not a forged packet.
    QJsonArray raw;
    for(const auto& frame:frames)
    {
        QJsonArray values;for(double v:frame.potentials)values.append(v);
        raw.append(QJsonObject{{"time",frame.time},{"stimulus",frame.stimulus},{"soma",values},
            {"observed_revision",QString::fromStdString(frame.effectiveModelRevision)}});
    }
    Artifact(rig.name+"_reset_diagnostic.json",QJsonDocument(QJsonObject{
        {"kind","native_probe_explicit_reset_diagnostic"},{"schema_version",1},
        {"reset_on_final_sample",finalSample},{"control_state",NativeProbeStatusName(rig.learner->NativeProbeState())},
        {"sample_count",double(frames.size())},{"raw_pre_reset_samples",raw},{"closed_probe_available",false},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
template<class Learner> void RejectWallPolicyBeforeTraining(int normalization,const std::string& location)
{
    EditingRig<Learner> rig(2000,normalization,"wall_begin_"+location,false,2,true);
    UEPtr<UContainer> target;
    if(location=="owner")target=rig.learner;
    else if(location=="ancestor")target=rig.model;
    else if(location=="neuron")target=rig.neuron;
    else if(location=="generator")target=rig.source;
    ASSERT_TRUE(target);const auto old=target->MaxCalculationDuration.GetData();ASSERT_LT(old,0);
    const auto parameters=rig.learner->ReadNativeParameters();const auto before=rig.environment->GetTime().GetDoubleTime();
    target->MaxCalculationDuration=1000000000LL;
    rig.learner->BeginNativeTraining(TrainingPlan(rig));
    const auto& service=rig.learner->NativeTrainingController();const auto reason=service.Reason();
    const auto state=service.State();const auto outcome=service.Outcome();
    const auto issued=service.IssuedReferenceProbes();const bool certified=bool(service.Certificate());
    EXPECT_EQ(service.State(),NativeTrainingState::Finished);EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidModel);
    EXPECT_EQ(reason,"unsupported_native_wall_limited_schedule");EXPECT_EQ(service.IssuedReferenceProbes(),0u);
    EXPECT_TRUE(service.ObservedPackets().empty());EXPECT_FALSE(service.Certificate());
    EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),before);
    // A rejected execution policy must not disable ordinary Rdk data/lifecycle
    // operations, including the resets/builds needed by checkpoint rollback.
    rig.learner->Reset();
    EXPECT_EQ(target->MaxCalculationDuration.GetData(),1000000000LL);
    const bool limitedOwner=location=="owner" || location=="ancestor";
    // Structural Build may replace children from their storage images. Do not
    // pretend an old child pointer/metadata override is a transparent checkpoint.
    if(!limitedOwner)target->MaxCalculationDuration=old;
    rig.learner->Build();rig.learner->Init();
    EXPECT_TRUE(rig.learner->IsReady());EXPECT_TRUE(rig.learner->IsInit());
    EXPECT_TRUE(rig.learner->NativeModelEditFailure().empty());
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),before);
    if(limitedOwner){EXPECT_EQ(target->MaxCalculationDuration.GetData(),1000000000LL);target->MaxCalculationDuration=old;}
    Artifact(rig.name+"_wall_begin_policy.json",QJsonDocument(QJsonObject{
        {"kind","native_wall_before_training"},{"schema_version",1},{"location",QString::fromStdString(location)},
        {"reason",QString::fromStdString(reason)},{"started_reference_probes",double(issued)},
        {"state_before_reset",NativeTrainingStateName(state)},{"outcome_before_reset",TrainingStatusName(outcome)},
        {"certificate_before_reset",certified},
        {"reset_build_preserved_parameters",rig.learner->ReadNativeParameters()==parameters},
        {"build_with_limited_owner",limitedOwner},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
template<class Learner> void RejectWallPolicyBeforeRecognition(const std::string& location)
{
    EditingRig<Learner> rig(2000,1,"wall_recognition_"+location,false,2,true);
    UEPtr<UContainer> target=rig.learner;if(location=="generator")target=rig.source;
    const auto old=target->MaxCalculationDuration.GetData();target->MaxCalculationDuration=1000000000LL;
    NativeProbeBindings bindings;bindings.owner=rig.learner.Get();bindings.neuron=rig.neuron;
    bindings.dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    bindings.branch=rig.branch;bindings.inputCount=2;bindings.routingComplete=true;
    for(unsigned i=0;i<(rig.branch?1u:2u);++i)
    {auto soma=rig.neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);bindings.somas.push_back(soma);}
    NativeRecognitionTrialRequest request;request.runId=rig.name;request.trialId="schedule";request.sampleId="target";
    request.label="target";request.pattern=rig.learner->InputPattern.GetData();request.duration=rig.duration;
    QJsonArray values;for(int i=0;i<request.pattern.GetRows();++i)values.append(request.pattern(i,0));
    request.patternHash=NmsdkTools::CanonicalModelDataSha256(values).toStdString();
    const auto parameters=rig.learner->ReadNativeParameters();const auto before=rig.environment->GetTime().GetDoubleTime();
    NativeRecognitionTrialExecutor executor;executor.Queue(request);unsigned presentationEdits=0;
    executor.BeforeChildren(bindings,before,[&](const auto&){++presentationEdits;},[&](bool){return rig.Revision();});
    auto result=executor.TakeResult();const auto effective=target->MaxCalculationDuration.GetData();target->MaxCalculationDuration=old;
    ASSERT_TRUE(result);EXPECT_FALSE(result->armed);EXPECT_FALSE(result->complete);EXPECT_FALSE(result->valid);
    EXPECT_TRUE(result->samples.empty());EXPECT_EQ(presentationEdits,0u);
    EXPECT_EQ(result->reason,"unsupported_native_wall_limited_schedule");EXPECT_EQ(effective,1000000000LL);
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),before);
    // Actual production executor and physical bindings at preparation only;
    // this is not a trained/frozen evaluation or a classification experiment.
    Artifact(rig.name+"_unarmed_recognition.json",QJsonDocument(NativeRecognitionTrialJson(*result)).toJson());
}
TEST(NativeWallSchedule,ClassicN0MidProbeChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearner>(0,false);}
TEST(NativeWallSchedule,ClassicN0FinalSampleChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearner>(0,true);}
TEST(NativeWallSchedule,ClassicN0BeginOwner){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(0,"owner");}
TEST(NativeWallSchedule,ClassicN0BeginAncestor){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(0,"ancestor");}
TEST(NativeWallSchedule,ClassicN0BeginNeuron){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(0,"neuron");}
TEST(NativeWallSchedule,ClassicN0BeginGenerator){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(0,"generator");}
TEST(NativeWallSchedule,ClassicN1MidProbeChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearner>(1,false);}
TEST(NativeWallSchedule,ClassicN1FinalSampleChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearner>(1,true);}
TEST(NativeWallSchedule,ClassicN1BeginOwner){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(1,"owner");}
TEST(NativeWallSchedule,ClassicN1BeginAncestor){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(1,"ancestor");}
TEST(NativeWallSchedule,ClassicN1BeginNeuron){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(1,"neuron");}
TEST(NativeWallSchedule,ClassicN1BeginGenerator){RejectWallPolicyBeforeTraining<NNeuronTimeLearner>(1,"generator");}
TEST(NativeWallSchedule,ClassicCallbackResetMid){ResetFromWallControlCallback<NNeuronTimeLearner>(false);}
TEST(NativeWallSchedule,ClassicCallbackResetFinal){ResetFromWallControlCallback<NNeuronTimeLearner>(true);}
TEST(NativeWallSchedule,ClassicRecognitionOwner){RejectWallPolicyBeforeRecognition<NNeuronTimeLearner>("owner");}
TEST(NativeWallSchedule,ClassicRecognitionGenerator){RejectWallPolicyBeforeRecognition<NNeuronTimeLearner>("generator");}
TEST(NativeWallSchedule,BranchN0MidProbeChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearnerBranch>(0,false);}
TEST(NativeWallSchedule,BranchN0FinalSampleChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearnerBranch>(0,true);}
TEST(NativeWallSchedule,BranchN0BeginOwner){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(0,"owner");}
TEST(NativeWallSchedule,BranchN0BeginAncestor){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(0,"ancestor");}
TEST(NativeWallSchedule,BranchN0BeginNeuron){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(0,"neuron");}
TEST(NativeWallSchedule,BranchN0BeginGenerator){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(0,"generator");}
TEST(NativeWallSchedule,BranchN1MidProbeChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearnerBranch>(1,false);}
TEST(NativeWallSchedule,BranchN1FinalSampleChange){ChangeWallPolicyWhileRecording<NNeuronTimeLearnerBranch>(1,true);}
TEST(NativeWallSchedule,BranchN1BeginOwner){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(1,"owner");}
TEST(NativeWallSchedule,BranchN1BeginAncestor){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(1,"ancestor");}
TEST(NativeWallSchedule,BranchN1BeginNeuron){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(1,"neuron");}
TEST(NativeWallSchedule,BranchN1BeginGenerator){RejectWallPolicyBeforeTraining<NNeuronTimeLearnerBranch>(1,"generator");}
TEST(NativeWallSchedule,BranchCallbackResetMid){ResetFromWallControlCallback<NNeuronTimeLearnerBranch>(false);}
TEST(NativeWallSchedule,BranchCallbackResetFinal){ResetFromWallControlCallback<NNeuronTimeLearnerBranch>(true);}
TEST(NativeWallSchedule,BranchRecognitionOwner){RejectWallPolicyBeforeRecognition<NNeuronTimeLearnerBranch>("owner");}
TEST(NativeWallSchedule,BranchRecognitionGenerator){RejectWallPolicyBeforeRecognition<NNeuronTimeLearnerBranch>("generator");}

template<class Learner> void ChangeWallPolicyInObservationSink()
{
    EditingRig<Learner> rig(2000,1,"wall_observation_sink",false,2,true);
    auto plan=TrainingPlan(rig);RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:2u);
    const auto originalSink=plan.observationSink;const auto observations=std::make_shared<std::size_t>(0);
    const auto owner=rig.learner;
    plan.observationSink=[originalSink,observations,owner](const NativeProbeResult& packet) {
        originalSink(packet);++*observations;if(owner)owner->MaxCalculationDuration=1000000000LL;
    };
    const auto old=rig.learner->MaxCalculationDuration.GetData();const auto parameters=rig.learner->ReadNativeParameters();
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,unsigned((rig.duration+.02)*rig.frequency)+100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();
    const auto limit=rig.learner->MaxCalculationDuration.GetData();rig.learner->MaxCalculationDuration=old;
    EXPECT_EQ(*observations,1u);EXPECT_EQ(service.Outcome(),TrainingStatus::InvalidObservation);
    EXPECT_EQ(service.Reason(),"unsupported_native_wall_limited_schedule");EXPECT_FALSE(service.Certificate());
    EXPECT_FALSE(service.References());ASSERT_EQ(service.ObservedPackets().size(),1u);
    ASSERT_TRUE(service.ObservedPackets().front().observation);
    // The already-closed observation remains evidence of the prior valid
    // protocol; the changed current policy cannot borrow it to finish Train.
    EXPECT_TRUE(service.ObservedPackets().front().observation->valid);
    EXPECT_TRUE(service.ObservedPackets().front().observation->complete);
    EXPECT_EQ(limit,1000000000LL);EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);
    Artifact(rig.name+"_sink_policy_summary.json",QJsonDocument(QJsonObject{
        {"kind","native_wall_observation_sink_policy"},{"schema_version",1},
        {"observed_packets",double(service.ObservedPackets().size())},
        {"outcome",TrainingStatusName(service.Outcome())},{"reason",QString::fromStdString(service.Reason())},
        {"certificate",bool(service.Certificate())},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(NativeWallSchedule,ClassicObservationSinkChange){ChangeWallPolicyInObservationSink<NNeuronTimeLearner>();}
TEST(NativeWallSchedule,BranchObservationSinkChange){ChangeWallPolicyInObservationSink<NNeuronTimeLearnerBranch>();}
}

namespace {
template<class Learner> QJsonObject InheritedReadback(EditingRig<Learner>& rig)
{
    auto& owner=*rig.learner;
    const std::vector<std::pair<const char*,UIProperty*>> properties{
        {"Name",&owner.Name},{"Id",&owner.Id},{"Activity",&owner.Activity},{"TimeStep",&owner.TimeStep},
        {"MaxCalculationDuration",&owner.MaxCalculationDuration},{"CalculationDurationThreshold",&owner.CalculationDurationThreshold},
        {"Coord",&owner.Coord},{"StepDuration",&owner.StepDuration},{"DebugSysEventsMask",&owner.DebugSysEventsMask}};
    QJsonArray names;
    for(const auto& [name,property]:properties)
    {
        EXPECT_EQ(owner.FindProperty(name).Get(),property)<<name;
        names.append(QString::fromLatin1(name));
    }
    EXPECT_EQ(owner.GetTimeStep(),rig.frequency);EXPECT_EQ(owner.Name.GetData(),"Learner");
    EXPECT_NE(owner.Id.GetData(),ForbiddenId);
    EXPECT_EQ(rig.model->GetComponent("Learner",true).Get(),rig.learner.Get());
    EXPECT_LT(owner.MaxCalculationDuration.GetData(),0);
    return {{"registered_properties",names},{"name",QString::fromStdString(owner.Name.GetData())},
        {"id",double(owner.Id.GetData())},{"activity",owner.Activity.GetData()},{"frequency_hz",int(owner.GetTimeStep())},
        {"maximum_calculation_duration_ms",double(owner.MaxCalculationDuration.GetData())},
        {"calculation_duration_threshold_ms",double(owner.CalculationDurationThreshold.GetData())},
        {"step_duration_ms",double(owner.StepDuration.GetData())},{"debug_events_mask",double(owner.DebugSysEventsMask.GetData())}};
}

void SameNativeWave(const std::vector<NativeProbeSample>& before,const std::vector<NativeProbeSample>& after)
{
    ASSERT_FALSE(before.empty());ASSERT_EQ(before.size(),after.size());
    double maximumTimeResidual=0.,maximumPotentialResidual=0.;std::size_t differentStimulusSamples=0;
    for(std::size_t i=0;i<before.size();++i)
    {
        ASSERT_TRUE(std::isfinite(before[i].time) && std::isfinite(after[i].time));
        ASSERT_TRUE(std::isfinite(before[i].stimulus) && std::isfinite(after[i].stimulus));
        maximumTimeResidual=std::max(maximumTimeResidual,std::abs(
            (before[i].time-before.front().time)-(after[i].time-after.front().time)));
        differentStimulusSamples+=before[i].stimulus!=after[i].stimulus;
        ASSERT_EQ(before[i].potentials.size(),after[i].potentials.size());
        for(std::size_t j=0;j<before[i].potentials.size();++j)
        {
            ASSERT_TRUE(std::isfinite(before[i].potentials[j]) && std::isfinite(after[i].potentials[j]));
            maximumPotentialResidual=std::max(maximumPotentialResidual,std::abs(before[i].potentials[j]-after[i].potentials[j]));
        }
    }
    EXPECT_EQ(differentStimulusSamples,0u);EXPECT_LE(maximumTimeResidual,1.e-11);EXPECT_LE(maximumPotentialResidual,1.e-12);
}

template<class Learner> void InheritedActivityReset(unsigned frequency,int normalization=1)
{
    EditingRig<Learner> rig(frequency,normalization,"inherited_activity",false,2,true);
    const auto parameters=rig.learner->ReadNativeParameters();const auto revision=rig.Revision();
    const auto initial=InheritedReadback(rig);
    std::vector<std::vector<NativeProbeSample>> previous(2),following(2);
    for(std::size_t input=0;input<2;++input)
    {
        const auto result=rig.Probe(input,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,
            [&](const auto& sample){previous[input].push_back(sample);});
        ASSERT_EQ(result.status,NativeProbeStatus::Completed);ASSERT_TRUE(result.observation);ASSERT_TRUE(result.observation->valid);
    }
    // Apply public metadata through its native setters between complete probes.
    rig.learner->MaxCalculationDuration=-2;rig.learner->CalculationDurationThreshold=-3;
    rig.learner->DebugSysEventsMask=0;
    auto coordinate=rig.learner->Coord.GetData();coordinate(0)=1.25;coordinate(1)=-2.5;coordinate(2)=3.75;
    rig.learner->Coord=coordinate;
    rig.learner->Activity=false;
    EXPECT_EQ(rig.learner->NativeProbeState(),NativeProbeStatus::Idle);
    EXPECT_FALSE(rig.neuron->Activity.GetData());
    auto dataset=rig.learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
    EXPECT_FALSE(dataset->Activity.GetData());
    std::vector<MDMatrix<double>> baseline;
    for(std::size_t i=0;i<(rig.branch?1u:2u);++i)
    {
        const auto soma=rig.neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);ASSERT_TRUE(soma);
        baseline.push_back(soma->SumPotential.GetData());
    }
    for(int tick=0;tick<32;++tick){rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    EXPECT_EQ(rig.learner->StepDuration.GetData(),0u);
    for(std::size_t i=0;i<baseline.size();++i)
    {
        const auto soma=rig.neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);
        EXPECT_EQ(soma->SumPotential.GetData(),baseline[i]);
    }
    rig.learner->Activity=true;
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);EXPECT_EQ(rig.Revision(),revision);
    EXPECT_EQ(rig.learner->Coord.GetData(),coordinate);
    EXPECT_EQ(rig.learner->MaxCalculationDuration.GetData(),-2);
    EXPECT_EQ(rig.learner->CalculationDurationThreshold.GetData(),-3);
    EXPECT_EQ(rig.learner->DebugSysEventsMask.GetData(),0u);
    for(std::size_t input=0;input<2;++input)
    {
        const auto result=rig.Probe(input,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,
            [&](const auto& sample){following[input].push_back(sample);});
        ASSERT_EQ(result.status,NativeProbeStatus::Completed);ASSERT_TRUE(result.observation);ASSERT_TRUE(result.observation->valid);
        SameNativeWave(previous[input],following[input]);
    }
    Artifact(rig.name+"_inherited_contract.json",QJsonDocument(QJsonObject{
        {"kind","native_inherited_activity_contract"},{"schema_version",1},{"initial",initial},
        {"after",InheritedReadback(rig)},{"inactive_ticks",32},{"compared_inputs",2},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}

template<class Learner> void InheritedLocalFrequency(unsigned frequency,int normalization=1)
{
    EditingRig<Learner> rig(frequency,normalization,"inherited_local_frequency",false,2,true);
    const auto parameters=rig.learner->ReadNativeParameters();const auto revision=rig.Revision();
    std::vector<NativeProbeSample> before,after;
    const auto positive=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,
        [&](const auto& sample){before.push_back(sample);});
    ASSERT_EQ(positive.status,NativeProbeStatus::Completed);ASSERT_TRUE(positive.observation);ASSERT_TRUE(positive.observation->valid);
    rig.source->TimeStep=frequency/2;
    std::size_t invalidSamples=0;
    const auto rejected=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,
        [&](const auto&){++invalidSamples;});
    EXPECT_EQ(rejected.status,NativeProbeStatus::Rejected);EXPECT_FALSE(rejected.observation);EXPECT_EQ(invalidSamples,0u);
    EXPECT_NE(std::find(rejected.reasons.begin(),rejected.reasons.end(),"unready_or_multirate_native_graph"),rejected.reasons.end());
    rig.source->TimeStep=frequency;
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);EXPECT_EQ(rig.Revision(),revision);
    const auto restored=rig.Probe(0,nullptr,nullptr,PeakSelectionPolicy::AssignedBurstWave,true,false,
        [&](const auto& sample){after.push_back(sample);});
    ASSERT_EQ(restored.status,NativeProbeStatus::Completed);ASSERT_TRUE(restored.observation);ASSERT_TRUE(restored.observation->valid);
    SameNativeWave(before,after);
    Artifact(rig.name+"_inherited_contract.json",QJsonDocument(QJsonObject{
        {"kind","native_inherited_frequency_contract"},{"schema_version",1},{"effective",InheritedReadback(rig)},
        {"rejected_samples",double(invalidSamples)},{"rejected_reason","unready_or_multirate_native_graph"},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}

TEST(NativeInheritedProperties,ClassicActivity2000){InheritedActivityReset<NNeuronTimeLearner>(2000);}
TEST(NativeInheritedProperties,BranchActivity2000){InheritedActivityReset<NNeuronTimeLearnerBranch>(2000);}
TEST(NativeInheritedProperties,ClassicActivity20000){InheritedActivityReset<NNeuronTimeLearner>(20000);}
TEST(NativeInheritedProperties,BranchActivity20000){InheritedActivityReset<NNeuronTimeLearnerBranch>(20000);}
TEST(NativeInheritedProperties,ClassicLocalFrequency2000){InheritedLocalFrequency<NNeuronTimeLearner>(2000);}
TEST(NativeInheritedProperties,BranchLocalFrequency2000){InheritedLocalFrequency<NNeuronTimeLearnerBranch>(2000);}
TEST(NativeInheritedProperties,ClassicLocalFrequency20000){InheritedLocalFrequency<NNeuronTimeLearner>(20000);}
TEST(NativeInheritedProperties,BranchLocalFrequency20000){InheritedLocalFrequency<NNeuronTimeLearnerBranch>(20000);}
TEST(NativeInheritedProperties,ClassicN0Activity2000){InheritedActivityReset<NNeuronTimeLearner>(2000,0);}
TEST(NativeInheritedProperties,BranchN0Activity2000){InheritedActivityReset<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeInheritedProperties,ClassicN0Activity20000){InheritedActivityReset<NNeuronTimeLearner>(20000,0);}
TEST(NativeInheritedProperties,BranchN0Activity20000){InheritedActivityReset<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativeInheritedProperties,ClassicN0LocalFrequency2000){InheritedLocalFrequency<NNeuronTimeLearner>(2000,0);}
TEST(NativeInheritedProperties,BranchN0LocalFrequency2000){InheritedLocalFrequency<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeInheritedProperties,ClassicN0LocalFrequency20000){InheritedLocalFrequency<NNeuronTimeLearner>(20000,0);}
TEST(NativeInheritedProperties,BranchN0LocalFrequency20000){InheritedLocalFrequency<NNeuronTimeLearnerBranch>(20000,0);}
}


namespace {
template<class Learner> void NativeSweepBudgetBoundary(int normalization)
{
    EditingRig<Learner> rig(2000,normalization,"sweep_budget_boundary",false,2,true);
    auto plan=TrainingPlan(rig,0.);plan.maximumWallSeconds=1800.;
    plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    plan.search.maximumCandidatesPerInput=1;plan.search.maximumSweeps=1;
    for(auto& bound:plan.search.bounds)
    {bound.maximumLength=bound.minimumLength;bound.maximumSynapses=bound.minimumSynapses;bound.maximumResistance=bound.minimumResistance;}
    const auto parameters=rig.learner->ReadNativeParameters();const auto revision=rig.Revision();
    RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,unsigned(plan.maximumModelSeconds*rig.frequency)+100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();
    ASSERT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted)<<service.Reason();
    EXPECT_EQ(service.Reason(),"maximum_sweeps_exhausted");EXPECT_FALSE(service.Certificate());
    ASSERT_TRUE(service.Search());ASSERT_TRUE(service.Search()->Certificate());
    EXPECT_FALSE(service.Search()->Certificate()->Exact());
    EXPECT_EQ(service.ReferencePackets().size(),2u);EXPECT_EQ(service.FinalPackets().size(),2u);
    EXPECT_EQ(service.ObservedPackets().size(),8u);
    for(const auto& packet:service.ObservedPackets())
    {ASSERT_TRUE(packet.observation);EXPECT_TRUE(packet.observation->valid);EXPECT_TRUE(packet.observation->complete);}
    EXPECT_EQ(rig.learner->ReadNativeParameters(),parameters);EXPECT_EQ(rig.Revision(),revision);
    const std::string implementation="native-sweep-budget-fixture-v1";
    const auto summary=EncodeNativeTrainingState(service,rig.Revision(),parameters);
    const auto package=rig.learner->ExportNativeLearnedState(implementation);
    Artifact(rig.name+"_sweep_budget_summary.json",QJsonDocument(summary).toJson());
    Artifact(rig.name+"_stopped_package.json",QJsonDocument(package).toJson());
    EXPECT_EQ(package["kind"],QJsonValue("timelearner_stopped_state"));
    EXPECT_EQ(package["state_kind"],QJsonValue("diagnostic"));EXPECT_TRUE(package["certificate"].isNull());
    EXPECT_EQ(package["training_outcome"],QJsonValue("budget_exhausted"));
    EXPECT_EQ(package["reason"],QJsonValue("maximum_sweeps_exhausted"));
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();const auto clock=rig.environment->GetTime().GetDoubleTime();
    auto restored=PrepareNativeLearnedState(package,core.storage,core.environment,implementation);
    EXPECT_EQ(restored->service.Outcome(),TrainingStatus::BudgetExhausted);
    EXPECT_EQ(restored->service.Reason(),"maximum_sweeps_exhausted");EXPECT_FALSE(restored->service.Certificate());
    EXPECT_EQ(restored->service.FinalPackets().size(),2u);EXPECT_EQ(restored->modelRevision,revision);
    EXPECT_EQ(restored->parameters,parameters);EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),clock);
    EXPECT_THROW(ConvertNativeSoloToRecognition(package,NativeRecognitionSpec{},core.storage,core.environment,implementation),std::invalid_argument);
}
}
TEST(NativeTrainingTermination,ClassicN0SweepBudgetBoundary){NativeSweepBudgetBoundary<NNeuronTimeLearner>(0);}
TEST(NativeTrainingTermination,ClassicN1SweepBudgetBoundary){NativeSweepBudgetBoundary<NNeuronTimeLearner>(1);}
TEST(NativeTrainingTermination,BranchN0SweepBudgetBoundary){NativeSweepBudgetBoundary<NNeuronTimeLearnerBranch>(0);}
TEST(NativeTrainingTermination,BranchN1SweepBudgetBoundary){NativeSweepBudgetBoundary<NNeuronTimeLearnerBranch>(1);}

namespace {
template<class Learner> void NativeFiniteCandidateRanking(int normalization)
{
    EditingRig<Learner> rig(2000,normalization,"finite_ranking_zero_sync",false,2,true);
    auto plan=TrainingPlan(rig,0.);plan.maximumWallSeconds=1800.;
    const auto initial=rig.learner->ReadNativeParameters();
    plan.protocol.peakSelection=plan.probe.specification.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    for(auto& window:plan.inputWindows){window.begin=0.;window.end=rig.duration;}
    plan.search.maximumCandidatesPerInput=8;plan.search.maximumSweeps=1;
    plan.search.resistanceSubdivisionDepth=0;
    // Isolate measured timing ranking: explicit loose amplitude tolerance is
    // an engineering control, not amplitude convergence at the default 1e-5.
    plan.search.tolerances.sync=0.;plan.search.tolerances.amplitudeAbsolute=1.;
    plan.search.tolerances.amplitudeRelative=0.;
    for(std::size_t i=0;i<initial.size();++i)
    {
        auto& bound=plan.search.bounds[i];bound.minimumLength=bound.maximumLength=initial[i].length;
        bound.minimumSynapses=bound.maximumSynapses=initial[i].synapses;
        bound.minimumResistance=bound.maximumResistance=initial[i].resistance;
    }
    plan.search.bounds[0].minimumLength=1;plan.search.bounds[0].maximumLength=3;
    RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
    rig.learner->BeginNativeTraining(plan);
    for(unsigned ticks=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++ticks)
    {ASSERT_LT(ticks,unsigned(plan.maximumModelSeconds*rig.frequency)+100u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();
    const auto parameters=rig.learner->ReadNativeParameters();
    const auto summary=EncodeNativeTrainingState(service,rig.Revision(),parameters);
    Artifact(rig.name+"_ranking_summary.json",QJsonDocument(summary).toJson());
    ASSERT_TRUE(service.Search());const auto& evidence=service.Search()->Evidence();ASSERT_FALSE(evidence.empty());
    const auto error=[](const CandidateEvidence& e){return std::max(std::fabs(e.timingResidualLow),std::fabs(e.timingResidualHigh));};
    std::set<int> measured;double minimum=std::numeric_limits<double>::infinity(),selected=minimum;
    for(const auto& e:evidence)
    {
        ASSERT_TRUE(std::isfinite(error(e)));EXPECT_TRUE(e.withinAmplitude);
        measured.insert(e.parameters.length);minimum=std::min(minimum,error(e));
        if(e.fullParameters==parameters)selected=std::min(selected,error(e));
    }
    EXPECT_EQ(measured,(std::set<int>{1,2,3}));
    // A sensitive positive control: the actual native physics must offer a
    // strictly better measured geometry, not merely execute three no-op cases.
    EXPECT_LT(minimum,error(evidence.front())-1e-12);
    EXPECT_DOUBLE_EQ(selected,minimum);
    EXPECT_EQ(parameters[1],initial[1]);
    for(std::size_t i=0;i<parameters.size();++i)
    {EXPECT_EQ(parameters[i].synapses,initial[i].synapses);EXPECT_EQ(parameters[i].resistance,initial[i].resistance);}
    EXPECT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted)<<service.Reason();
    EXPECT_EQ(service.Reason(),"maximum_sweeps_exhausted");EXPECT_FALSE(service.Certificate());
    ASSERT_TRUE(service.Search()->Certificate());EXPECT_FALSE(service.Search()->Certificate()->Exact());
    Artifact(rig.name+"_stopped_package.json",QJsonDocument(rig.learner->ExportNativeLearnedState("native-finite-ranking-fixture-v1")).toJson());
}
}
TEST(NativeFiniteRanking,ClassicN0){NativeFiniteCandidateRanking<NNeuronTimeLearner>(0);}
TEST(NativeFiniteRanking,ClassicN1){NativeFiniteCandidateRanking<NNeuronTimeLearner>(1);}
TEST(NativeFiniteRanking,BranchN0){NativeFiniteCandidateRanking<NNeuronTimeLearnerBranch>(0);}
TEST(NativeFiniteRanking,BranchN1){NativeFiniteCandidateRanking<NNeuronTimeLearnerBranch>(1);}

namespace {
template<class Learner> void DiagnosticRecognitionBoundary(int normalization,bool partial)
{
    EditingRig<Learner> rig(2000,normalization,partial?"diagnostic_partial":"diagnostic_budget");
    auto plan=TrainingPlan(rig);RecordNativeTrainingProof(plan,rig.name,rig.branch?1u:rig.inputCount);
    if(partial)plan.maximumModelSeconds=.002;
    else for(auto& bound:plan.search.bounds)
    {bound.maximumLength=bound.minimumLength;bound.maximumSynapses=bound.minimumSynapses;bound.maximumResistance=bound.minimumResistance;}
    rig.learner->BeginNativeTraining(plan);
    for(unsigned tick=0;rig.learner->NativeTrainingController().State()!=NativeTrainingState::Finished;++tick)
    {ASSERT_LT(tick,20000u);rig.model->Calculate();rig.environment->IncreaseModelTimeByStep();}
    const auto& service=rig.learner->NativeTrainingController();
    ASSERT_EQ(service.Outcome(),TrainingStatus::BudgetExhausted);ASSERT_FALSE(service.Certificate());
    const std::string implementation="native-learned-boundary-fixture-v1";
    const auto stopped=rig.learner->ExportNativeLearnedState(implementation);
    ASSERT_EQ(stopped["kind"],QJsonValue("timelearner_stopped_state"));
    EXPECT_EQ(stopped["reference_complete"],QJsonValue(!partial));
    Artifact(rig.name+"_stopped_package.json",QJsonDocument(stopped).toJson());
    Artifact(rig.name+"_training_outcome.json",QJsonDocument(EncodeNativeTrainingState(service,rig.Revision(),rig.learner->ReadNativeParameters())).toJson());
    const auto clock=rig.environment->GetTime().GetDoubleTime();
    EXPECT_THROW(ConvertNativeSoloToRecognition(stopped,{},rig.learner->GetStorage(),rig.environment,implementation),std::invalid_argument);
    NativeRecognitionSpec conversion;
    if(rig.branch && normalization)
    {
        NativeRecognitionSpec scaled;scaled.mode=RecognitionConversionMode::HistoricalBranchN1;
        scaled.resistanceBounds={{1.e6,1.e12},{1.e6,1.e12}};
        if(partial)EXPECT_THROW(ConvertNativeStoppedToDiagnosticRecognition(stopped,scaled,rig.learner->GetStorage(),rig.environment,implementation),std::invalid_argument);
        else conversion=scaled;
    }
    const auto package=ConvertNativeStoppedToDiagnosticRecognition(stopped,conversion,rig.learner->GetStorage(),rig.environment,implementation);
    EXPECT_EQ(package["kind"],QJsonValue("timelearner_diagnostic_recognition_state"));
    EXPECT_EQ(package["state_kind"],QJsonValue("diagnostic_recognition"));
    EXPECT_EQ(package["source_solo"],QJsonValue(stopped));EXPECT_TRUE(package["recognition_certificate"].isNull());
    EXPECT_EQ(package,ConvertNativeStoppedToDiagnosticRecognition(stopped,conversion,rig.learner->GetStorage(),rig.environment,implementation));
    EXPECT_EQ(rig.environment->GetTime().GetDoubleTime(),clock);
    EXPECT_THROW(PrepareNativeRecognitionState(package,rig.learner->GetStorage(),rig.environment,implementation),std::invalid_argument);
    EXPECT_THROW(CreateNativeThresholdCandidate(package,.01,rig.learner->GetStorage(),rig.environment,implementation),std::invalid_argument);
    const auto oldRevision=rig.Revision();
    const auto rejected=rig.learner->ImportNativeRecognitionState(package,implementation);
    EXPECT_EQ(rejected.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(rejected.modelMayHaveChanged);
    EXPECT_EQ(rig.Revision(),oldRevision);
    auto forged=package;forged["kind"]="timelearner_recognition_state";forged["state_kind"]="recognition";
    forged.remove("sha256");forged["sha256"]=NmsdkTools::CanonicalModelDataSha256(forged);
    EXPECT_THROW(PrepareNativeRecognitionState(forged,rig.learner->GetStorage(),rig.environment,implementation),std::invalid_argument);
    const auto imported=rig.learner->ImportNativeDiagnosticRecognitionState(package,implementation);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    rig.learner->Build();rig.learner->Init();
    rig.neuron=rig.learner->template GetComponentL<NPulseNeuron>("Neuron",true);
    rig.source=rig.learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    ASSERT_TRUE(rig.neuron);ASSERT_TRUE(rig.source);rig.ports.clear();rig.ports.emplace(&rig.source->Output,"burst");
    EXPECT_FALSE(rig.learner->IsNeedToTrain.GetData());EXPECT_FALSE(rig.learner->NativeTrainingController().Certificate());
    ASSERT_EQ(rig.learner->ExportNativeRecognitionState(implementation),package);
    Artifact(rig.name+"_diagnostic_recognition.json",QJsonDocument(package).toJson());
    FrozenTrialChecks(rig,package);
    EXPECT_EQ(package["source_solo"].toObject()["training_outcome"],QJsonValue("budget_exhausted"));
    EXPECT_EQ(rig.learner->ExportNativeRecognitionState(implementation),package);
}
}
#define DIAGNOSTIC_RECOGNITION_TESTS(Topology,Type,N) \
TEST(NativeDiagnosticRecognition,Topology##N##Partial){DiagnosticRecognitionBoundary<Type>(N,true);} \
TEST(NativeDiagnosticRecognition,Topology##N##Budget){DiagnosticRecognitionBoundary<Type>(N,false);}
DIAGNOSTIC_RECOGNITION_TESTS(Classic,NNeuronTimeLearner,0)
DIAGNOSTIC_RECOGNITION_TESTS(Classic,NNeuronTimeLearner,1)
DIAGNOSTIC_RECOGNITION_TESTS(Branch,NNeuronTimeLearnerBranch,0)
DIAGNOSTIC_RECOGNITION_TESTS(Branch,NNeuronTimeLearnerBranch,1)
#undef DIAGNOSTIC_RECOGNITION_TESTS
TEST(NativeDiagnosticRecognition,OrdinaryClassicCompletedRegression)
{LearnedBoundary<NNeuronTimeLearner>(1,.2,2000,2,false,RecognitionCase::OwnedIdentity);}
TEST(NativeDiagnosticRecognition,OrdinaryBranchCompletedRegression)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,.2,2000,2,false,RecognitionCase::OwnedScaled);}
TEST(NativeDiagnosticRecognition,OrdinaryClassicFullPatternRegression)
{LearnedBoundary<NNeuronTimeLearner>(1,.2,2000,2,false,RecognitionCase::OwnedFreshIdentity);}
TEST(NativeDiagnosticRecognition,OrdinaryBranchFullPatternRegression)
{LearnedBoundary<NNeuronTimeLearnerBranch>(1,.2,2000,2,false,RecognitionCase::OwnedFreshScaled);}
