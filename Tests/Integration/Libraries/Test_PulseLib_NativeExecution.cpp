#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../App/NeuroModelerConsole/ModelIdentity.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QDir>
#include <QFile>
#include <type_traits>
#include <cstdlib>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
class NativeLearnerExecution : public ::testing::TestWithParam<std::pair<bool,unsigned>> {};
enum class Interference { None,PhysicalReset,SourceAmplitude,SourceFrequency,Pattern,DeleteSynapse,ExternalStop,OwnerBuild };

template<class Learner> void ExecuteProbeThroughLearner(unsigned frequency,Interference interference=Interference::None)
{
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    const std::string name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(frequency)+"_native_executor"+
        (interference==Interference::None?"":"_fault"+std::to_string(int(interference)));
    StorageProfileSpec profile;profile.name=name;profile.frequencyHz=frequency;
    profile.neuronBaseClass="NSPNeuronGen";profile.initialThreshold=1.;
    const auto registered=RegisterStorageProfile(core.storage,core.environment,profile);
    auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(learner);learner->Name="Learner";learner->StructureBuildMode=1;
    learner->NumInputDendrite=2;learner->NeuronClassName=registered.neuronClass;
    learner->DendriteLength=std::vector<int>{2,1};
    learner->CalculateMode=1;learner->NormalizationMode=1;
    learner->EnablePostTrainTuning=false;learner->AutoCalibrateFixedLTZThreshold=false;
    MDMatrix<double> pattern;pattern.Assign(2,1,0.);pattern(0,0)=.01;pattern(1,0)=.08;learner->InputPattern=pattern;
    UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(frequency);model->Init();model->Reset();
    model->Calculate();core.environment->IncreaseModelTimeByStep();
    auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(generator);
    ASSERT_EQ(learner->DendriteLength.GetData(),(std::vector<int>{2,1}));
    ASSERT_TRUE(neuron->template GetComponentL<NPulseMembrane>("Dendrite1_2",true));
    int active=0;
    if(branch)
    {
        auto point0=neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_2.ExcSynapse1",true);
        auto point1=neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_1.ExcSynapse1",true);
        ASSERT_TRUE(point0);ASSERT_TRUE(point1);
        if(point0->Input.IsConnected() && !point1->Input.IsConnected())active=1;
    }
    const auto phase=learner->TrainingPhase.GetData();const auto need=learner->IsNeedToTrain.GetData();
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    std::size_t revisionReads=0;
    const auto readRevision=[&]() {
        ++revisionReads;const auto identity=NmsdkTools::IdentifyModel(neuron,ports);
        if(!identity["valid"].toBool())throw std::runtime_error("invalid_native_identity");
        return identity["sha256"].toString().toStdString();
    };
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(before["valid"].toBool());
    const auto base=readRevision();bool armed=false;
    NativeProbeRequest request;request.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
    request.activeInput=active;request.inputId="input"+std::to_string(active);request.protocolRevision="native_two_input_burst_v1";
    request.baseModelRevision=base;request.expectedInputIsi={.01,.08};request.readModelRevision=readRevision;
    auto& spec=request.specification;spec.runId=name;spec.trialId=name+"/probe0";spec.sampleId="sample0";
    spec.patternHash=NmsdkTools::CanonicalModelDataSha256(QJsonArray{.01,.08}).toStdString();
    spec.end=.17;spec.maximumSampleGap=1./frequency;spec.maximumSamples=frequency;
    spec.expectedStimulusIds={"pulse0","pulse1"};
    if(branch)spec.windows={{request.inputId,0,active?.089:.009,active?.15:.07,"pulse"+std::to_string(active)}};
    else spec.windows={{"input0",0,.009,.07,"pulse0"},{"input1",1,.089,.15,"pulse1"}};
    request.onPrepared=[&](const PreparedVerificationProbe& declaration,const ProbeSpec& actual) {
        armed=true;EXPECT_EQ(declaration.baseModelRevision,base);
        EXPECT_EQ(actual.modelRevision,declaration.effectiveModelRevision);
        EXPECT_GE(actual.begin,1./frequency);
        EXPECT_EQ(actual.baseline.size(),branch?1u:2u);
        if(branch)
        {
            EXPECT_NE(declaration.effectiveModelRevision,base);
            for(int input=0;input<2;++input)
            {
                auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(
                    input?"Dendrite1_1.ExcSynapse1":"Dendrite1_2.ExcSynapse1",true);
                ASSERT_TRUE(synapse);EXPECT_EQ(synapse->Input.IsConnected(),input==active);
            }
        }
    };
    learner->QueueNativeProbe(std::move(request));ASSERT_TRUE(learner->NativeProbeOwnsControl());
    unsigned ticks=0;
    while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
    {
        ASSERT_LT(ticks++,frequency);
        model->Calculate();core.environment->IncreaseModelTimeByStep();
        if(interference!=Interference::None && ticks==frequency/25)
        {
            switch(interference)
            {
            case Interference::PhysicalReset:
            {
                const auto physicalBefore=readRevision();neuron->Reset();
                EXPECT_EQ(readRevision(),physicalBefore); // Same spec, different physical history.
                break;
            }
            case Interference::SourceAmplitude:generator->Amplitude=1.5;break;
            case Interference::SourceFrequency:generator->Frequency=100.;break;
            case Interference::Pattern:
                learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true)->MatrixData(0,0)=.02;break;
            case Interference::DeleteSynapse:
                neuron->template GetComponentL<NPulseMembrane>("Dendrite1_1",true)->DelComponent("ExcSynapse1",true);break;
            case Interference::ExternalStop:
                learner->IsNeedToTrain=false;EXPECT_EQ(learner->InputPattern(0,0),.01);
                EXPECT_EQ(learner->TrainingPhase.GetData(),phase);EXPECT_EQ(readRevision(),base);break;
            case Interference::OwnerBuild:
                learner->DendriteLength=std::vector<int>{2,1};learner->Build();break;
            case Interference::None:break;
            }
        }
    }
    const auto result=learner->TakeNativeProbeResult();ASSERT_TRUE(result);
    for(const auto& reason:result->reasons)std::cout<<name<<" adapter_reason="<<reason<<std::endl;
    if(interference!=Interference::None)
    {
        const auto expected=interference==Interference::ExternalStop || interference==Interference::OwnerBuild
            ?NativeProbeStatus::Cancelled:NativeProbeStatus::Rejected;
        EXPECT_EQ(result->status,expected);
        if(result->observation)EXPECT_FALSE(result->observation->valid);
        EXPECT_TRUE(result->requiresFreshVerification);
        EXPECT_TRUE(learner->NativeProbeOwnsControl());
        if(interference==Interference::DeleteSynapse)EXPECT_TRUE(result->currentBaseRevision.empty());
        dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();return;
    }
    ASSERT_EQ(result->status,NativeProbeStatus::Completed);
    ASSERT_TRUE(result->observation);const auto& observed=*result->observation;
    for(const auto& reason:observed.reasons)std::cout<<name<<" observation_reason="<<reason<<std::endl;
    EXPECT_TRUE(armed);ASSERT_TRUE(observed.complete);ASSERT_TRUE(observed.valid);
    EXPECT_EQ(observed.stimuli.size(),2u);EXPECT_EQ(observed.sampleCount,ticks);
    EXPECT_GE(revisionReads,2*ticks);
    EXPECT_EQ(result->currentBaseRevision,base);
    EXPECT_EQ(readRevision(),base);
    EXPECT_EQ(learner->TrainingPhase.GetData(),phase);EXPECT_EQ(learner->IsNeedToTrain.GetData(),need);
    EXPECT_TRUE(learner->NativeProbeOwnsControl()); // No implicit legacy resume.
    if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        QJsonArray events,reasons,peaks;
        for(const auto& event:observed.stimuli)events.append(QJsonObject{{"id",QString::fromStdString(event.id)},{"time",event.time}});
        for(const auto& reason:observed.reasons)reasons.append(QString::fromStdString(reason));
        for(const auto& peak:observed.peaks)peaks.append(QJsonObject{{"input_id",QString::fromStdString(peak.inputId)},
            {"validity",PeakValidityName(peak.validity)},{"raw_potential",peak.rawPotential?QJsonValue(*peak.rawPotential):QJsonValue(QJsonValue::Null)}});
        const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
        QFile file(directory+"/"+QString::fromStdString(name)+".json");ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(QJsonObject{{"schema_version",1},{"kind","native_learner_probe_execution"},
            {"model_before",before},{"model_after",NmsdkTools::IdentifyModel(neuron,ports)},
            {"effective_revision",QString::fromStdString(result->prepared->effectiveModelRevision)},
            {"complete",observed.complete},{"valid",observed.valid},{"reasons",reasons},{"peaks",peaks},
            {"actual_stimuli",events},{"native_ticks",int(ticks)},{"revision_reads",int(revisionReads)},
            {"scientific_training_result",false}}).toJson();ASSERT_EQ(file.write(bytes),bytes.size());
    }
    // Native Reset releases control and preserves the learned physical graph.
    learner->Reset();EXPECT_FALSE(learner->NativeProbeOwnsControl());
    EXPECT_EQ(learner->NativeProbeState(),NativeProbeStatus::Idle);
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}
TEST_P(NativeLearnerExecution, QueueUsesNativeSchedulerAndRestoresModel)
{
    if(GetParam().first)ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(GetParam().second);
    else ExecuteProbeThroughLearner<NNeuronTimeLearner>(GetParam().second);
}
INSTANTIATE_TEST_SUITE_P(TopologiesAndRates,NativeLearnerExecution,::testing::Values(
    std::make_pair(false,2000u),std::make_pair(true,2000u),
    std::make_pair(false,20000u),std::make_pair(true,20000u)));
TEST(NativeLearnerProbeInvalidation, ClassicPhysicalResetWithUnchangedModelHash)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::PhysicalReset); }
TEST(NativeLearnerProbeInvalidation, BranchPhysicalResetWithUnchangedModelHash)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::PhysicalReset); }
TEST(NativeLearnerProbeInvalidation, ClassicSourceAmplitudeChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::SourceAmplitude); }
TEST(NativeLearnerProbeInvalidation, BranchSourceAmplitudeChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::SourceAmplitude); }
TEST(NativeLearnerProbeInvalidation, ClassicSourceFrequencyChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::SourceFrequency); }
TEST(NativeLearnerProbeInvalidation, BranchPatternChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::Pattern); }
TEST(NativeLearnerProbeInvalidation, ClassicDeletedSynapse)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::DeleteSynapse); }
TEST(NativeLearnerProbeInvalidation, BranchDeletedSynapse)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::DeleteSynapse); }
TEST(NativeLearnerProbeInvalidation, ClassicExternalStopPreservesTargetAndThreshold)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::ExternalStop); }
TEST(NativeLearnerProbeInvalidation, BranchExternalStopPreservesTargetAndThreshold)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::ExternalStop); }
TEST(NativeLearnerProbeInvalidation, ClassicImplicitResetDuringBuildKeepsControl)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::OwnerBuild); }
TEST(NativeLearnerProbeInvalidation, BranchImplicitResetDuringBuildKeepsControl)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::OwnerBuild); }
}
