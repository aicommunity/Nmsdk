#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativePhysicalModelData.h"
#include "TimeLearner/NativeRecognitionState.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QDir>
#include <QFile>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <sstream>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
constexpr const char* Implementation="physical-model-data-test-v1";
QJsonObject Signed(QJsonObject value)
{value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;}

struct Fixture {
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<NPulseNeuron> sourceNeuron;
    UEPtr<NDatasetMatrix> sourceDataset;
    QJsonObject source,initialIdentity;
    ~Fixture()
    {
        if(environment)
        {
            if(auto net=dynamic_pointer_cast<UNet>(environment->GetModel()))net->BreakLinks();
            sourceNeuron=0;sourceDataset=0;environment->DestroyModel();
        }
    }
    template<class Owner> void Create()
    {
        const bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);environment->GetTime().SetTime(0);
        ASSERT_TRUE(environment->CreateModel("NModel"));auto model=environment->GetModel();model->SetGlobalTimeStep(2000);
        auto owner=dynamic_pointer_cast<Owner>(storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        ASSERT_TRUE(owner);owner->Name="Source";UEPtr<UContainer> component=owner;
        ASSERT_NE(model->AddComponent(component),ForbiddenId);owner->SetGlobalTimeStep(2000);
        ConfiguredNativeTraining configuration;auto& declaration=configuration.model;
        declaration.branch=branch;declaration.frequencyHz=2000;declaration.neuronClass="NSPNeuronGen";
        declaration.normalization=Normalization::SynapseCount;declaration.inputs={{2,2,86e6},{1,1,91e6}};
        declaration.initialIsi={.01,.08};declaration.editPolicy.normalization=Normalization::SynapseCount;
        declaration.editPolicy.maximumCableLength=8;
        configuration.stimulusProfile={"NPulseGeneratorTransit",1.,.001,2000.,0.,false,false};
        configuration.runId=branch?"physical-data-branch":"physical-data-classic";
        configuration.protocolRevision="physical-data-reference-v1";configuration.duration=.3;
        configuration.maximumSampleGap=.0005;configuration.maximumSamples=1001;
        configuration.windows={{0.,.15},{.08,.25}};
        configuration.search.normalization=Normalization::SynapseCount;
        configuration.search.maximumProbes=32;configuration.search.maximumEdits=16;
        configuration.search.maximumCandidatesPerInput=4;configuration.search.maximumSweeps=1;
        configuration.search.bounds.assign(2,{1,8,1,8,1e6,1e9});
        configuration.maximumReferenceProbes=2;configuration.maximumModelSeconds=10.;configuration.maximumWallSeconds=60.;
        owner->ControllerVersion=2;owner->CalculateMode=1;owner->StructureBuildMode=1;
        owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;
        owner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(configuration)).toJson(QJsonDocument::Compact).toStdString();
        owner->IsNeedToTrain=false;owner->Build();owner->Init();model->Init();model->Reset();
        ASSERT_TRUE(owner->ConfiguredModelInitialized.GetData())<<owner->NativeModelEditFailure();
        sourceNeuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        sourceDataset=owner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        ASSERT_TRUE(sourceNeuron);ASSERT_TRUE(sourceDataset);
        auto generator=sourceDataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
        initialIdentity=NmsdkTools::IdentifyModel(sourceNeuron,{{&generator->Output,"burst"}});
        ASSERT_TRUE(initialIdentity["valid"].toBool());
        // A real, explicitly stopped native boundary. No made-up references,
        // spikes, fitted parameters or completed-training certificate.
        owner->BeginNativeTraining(MakeConfiguredNativeTrainingPlan(configuration));owner->IsNeedToTrain=false;
        ASSERT_EQ(owner->NativeTrainingController().State(),NativeTrainingState::Finished);
        ASSERT_EQ(owner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
        ASSERT_TRUE(owner->NativeTrainingController().ObservedPackets().empty());
        source=owner->ExportNativeLearnedState(Implementation);
        ASSERT_EQ(source["kind"],QJsonValue("timelearner_stopped_state"));ASSERT_TRUE(source["certificate"].isNull());
    }
    QJsonObject CurrentIdentity() const
    {
        auto generator=sourceDataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);
        return NmsdkTools::IdentifyModel(UEPtr<UContainer>(sourceNeuron.Get()),{{&generator->Output,"burst"}});
    }
};

template<class Owner> void Roundtrip()
{
    Fixture fixture;fixture.Create<Owner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto model=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    EXPECT_EQ(model["source_boundary"].toObject()["sha256"],fixture.source["sha256"]);
    EXPECT_TRUE(model["data_only"].toBool());EXPECT_TRUE(model["certificate"].isNull());
    EXPECT_FALSE(model.contains("observed_packets"));EXPECT_FALSE(model.contains("measurement_archive"));
    EXPECT_FALSE(model.contains("source_solo"));EXPECT_FALSE(model.contains("search_history"));
    const auto restored=PrepareNativePhysicalModelData(model,fixture.storage,fixture.environment,Implementation);
    const auto sourceParameters=fixture.source["trained_inputs"].toArray();ASSERT_EQ(sourceParameters.size(),2);
    ASSERT_EQ(restored->parameters.size(),2u);
    EXPECT_EQ(restored->parameters[0],(InputParameters{2,2,86e6}));
    EXPECT_EQ(restored->parameters[1],(InputParameters{1,1,91e6}));
    auto generator=restored->dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
    EXPECT_EQ(NmsdkTools::IdentifyModel(restored->neuron,{{&generator->Output,"burst"}}),fixture.initialIdentity);
    EXPECT_EQ(NmsdkTools::IdentifyModel(restored->dataset),fixture.source["dataset"].toObject()["identity"].toObject());
    EXPECT_FALSE(restored->neuron->GetOwner());EXPECT_FALSE(restored->dataset->GetOwner());
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
    EXPECT_THROW(PrepareNativeLearnedState(model,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_THROW(PrepareNativeRecognitionState(model,fixture.storage,fixture.environment,Implementation),std::invalid_argument);

    auto sourceOwner=dynamic_pointer_cast<Owner>(fixture.sourceNeuron->GetOwner());ASSERT_TRUE(sourceOwner);
    auto targetOwner=dynamic_pointer_cast<Owner>(fixture.storage->TakeObject(
        std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(targetOwner);targetOwner->Name="Target";targetOwner->SetEnvironment(fixture.environment);
    targetOwner->SetGlobalTimeStep(2000);targetOwner->ControllerVersion=2;targetOwner->CalculateMode=1;
    targetOwner->StructureBuildMode=1;targetOwner->EnablePostTrainTuning=false;targetOwner->AutoCalibrateFixedLTZThreshold=false;
    UEPtr<UContainer> targetComponent=targetOwner;
    ASSERT_NE(fixture.environment->GetModel()->AddComponent(targetComponent),ForbiddenId);
    const auto installed=targetOwner->InstallNativePreparedModel(restored->configuration.model,
        restored->neuron,restored->dataset,restored->parameters);
    ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
    targetOwner->Init();fixture.environment->GetModel()->Init();fixture.environment->GetModel()->Reset();
    std::vector<NativeProbeSample> sourceTrace,targetTrace;
    const auto request=[&](auto owner,const std::string& run,std::vector<NativeProbeSample>& trace) {
        NativeProbeRequest probe;probe.routing=std::is_same_v<Owner,NNeuronTimeLearnerBranch>?
            ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        probe.activeInput=0;probe.inputId="input0";probe.protocolRevision="physical-data-roundtrip-burst-v1";
        probe.baseModelRevision=fixture.initialIdentity["sha256"].toString().toStdString();probe.expectedInputIsi={.01,.08};
        auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto source=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        probe.readModelRevision=[neuron,source] {
            return NmsdkTools::IdentifyModel(UEPtr<UContainer>(neuron.Get()),{{&source->Output,"burst"}})["sha256"].toString().toStdString();
        };
        probe.onSample=[&trace](const NativeProbeSample& sample){trace.push_back(sample);};
        auto& spec=probe.specification;spec.runId=run;spec.trialId=run+"/trial0";spec.sampleId="target";
        spec.patternHash=NmsdkTools::CanonicalModelDataSha256(QJsonArray{.01,.08}).toStdString();
        spec.end=.3;spec.maximumSampleGap=.0005;spec.maximumSamples=1002;
        spec.stimulusProfile=restored->configuration.stimulusProfile;spec.expectedStimulusIds={"pulse0","pulse1"};
        spec.windows={{"input0",0,.009,.07,"pulse0"}};return probe;
    };
    sourceOwner->QueueNativeProbe(request(sourceOwner,"source",sourceTrace));
    targetOwner->QueueNativeProbe(request(targetOwner,"target",targetTrace));
    std::optional<NativeProbeResult> sourceResult,targetResult;
    for(int tick=0;tick<1002 && (!sourceResult || !targetResult);++tick)
    {
        fixture.environment->GetModel()->Calculate();fixture.environment->IncreaseModelTimeByStep();
        if(!sourceResult)sourceResult=sourceOwner->TakeNativeProbeResult();
        if(!targetResult)targetResult=targetOwner->TakeNativeProbeResult();
    }
    ASSERT_TRUE(sourceResult);ASSERT_TRUE(targetResult);ASSERT_TRUE(sourceResult->observation);ASSERT_TRUE(targetResult->observation);
    EXPECT_EQ(sourceResult->status,NativeProbeStatus::Completed);EXPECT_EQ(targetResult->status,NativeProbeStatus::Completed);
    EXPECT_TRUE(sourceResult->observation->complete);EXPECT_TRUE(targetResult->observation->complete);
    EXPECT_TRUE(sourceResult->observation->valid);EXPECT_TRUE(targetResult->observation->valid);
    ASSERT_EQ(sourceTrace.size(),targetTrace.size());ASSERT_GT(sourceTrace.size(),500u);
    EXPECT_EQ(sourceTrace.size(),sourceResult->observation->sampleCount);
    double largestResponse=0.;
    for(std::size_t i=0;i<sourceTrace.size();++i)
    {
        EXPECT_EQ(sourceTrace[i].time,targetTrace[i].time);EXPECT_EQ(sourceTrace[i].stimulus,targetTrace[i].stimulus);
        ASSERT_EQ(sourceTrace[i].potentials.size(),targetTrace[i].potentials.size());
        EXPECT_EQ(sourceTrace[i].potentials,targetTrace[i].potentials);
        for(std::size_t channel=0;channel<sourceTrace[i].potentials.size();++channel)
        {
            ASSERT_TRUE(std::isfinite(sourceTrace[i].potentials[channel]));ASSERT_TRUE(std::isfinite(targetTrace[i].potentials[channel]));
            largestResponse=std::max(largestResponse,std::fabs(sourceTrace[i].potentials[channel]-sourceTrace.front().potentials[channel]));
        }
    }
    EXPECT_GT(largestResponse,1e-6);
    ASSERT_EQ(sourceResult->observation->stimuli.size(),2u);
    ASSERT_EQ(sourceResult->observation->stimuli.size(),targetResult->observation->stimuli.size());
    for(std::size_t i=0;i<2;++i)
    {
        EXPECT_EQ(sourceResult->observation->stimuli[i].id,targetResult->observation->stimuli[i].id);
        EXPECT_EQ(sourceResult->observation->stimuli[i].time,targetResult->observation->stimuli[i].time);
    }
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
    if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        const QString stem=std::is_same_v<Owner,NNeuronTimeLearnerBranch>?
            "physical-model-roundtrip-Branch":"physical-model-roundtrip-Classic";
        std::ostringstream trace;trace<<std::setprecision(17)<<"time,actual_input";
        for(std::size_t channel=0;channel<sourceTrace.front().potentials.size();++channel)
            trace<<",source_soma"<<channel+1<<",restored_soma"<<channel+1;
        trace<<'\n';
        for(std::size_t i=0;i<sourceTrace.size();++i)
        {
            trace<<sourceTrace[i].time<<','<<sourceTrace[i].stimulus;
            for(std::size_t channel=0;channel<sourceTrace[i].potentials.size();++channel)
                trace<<','<<sourceTrace[i].potentials[channel]<<','<<targetTrace[i].potentials[channel];
            trace<<'\n';
        }
        const auto write=[&](const QString& suffix,const QByteArray& bytes) {
            QFile file(QDir(QString::fromLocal8Bit(output)).filePath(stem+suffix));
            ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_EQ(file.write(bytes),bytes.size());
        };
        write(".csv",QByteArray::fromStdString(trace.str()));
        write(".json",QJsonDocument(QJsonObject{{"kind","timelearner_physical_model_roundtrip_fixture"},
            {"schema_version",1},{"model_revision",model["model_revision"]},{"source_boundary",model["source_boundary"]},
            {"source_probe",EncodeNativeProbeEvidence(*sourceResult)},{"restored_probe",EncodeNativeProbeEvidence(*targetResult)},
            {"trace",stem+".csv"},{"model_data_sha256",model["sha256"]},
            {"training_certificate_transferred",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    }
}

TEST(NativePhysicalModelData,ClassicCompleteGraphAndAsymmetricInputsRoundtripWithoutProofAuthority)
{Roundtrip<NNeuronTimeLearner>();}
TEST(NativePhysicalModelData,BranchCompleteGraphAndAsymmetricInputsRoundtripWithoutProofAuthority)
{Roundtrip<NNeuronTimeLearnerBranch>();}

TEST(NativePhysicalModelData,ResignedParameterOrClassContradictionsCannotReplaceTheNativeGraph)
{
    Fixture fixture;fixture.Create<NNeuronTimeLearner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto model=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    auto changed=model;auto parameters=changed["parameters"].toArray();auto input=parameters[0].toObject();
    input["resistance"]=1.25*input["resistance"].toDouble();parameters[0]=input;changed["parameters"]=parameters;
    EXPECT_THROW(PrepareNativePhysicalModelData(Signed(changed),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    changed=model;auto configuration=changed["configuration"].toObject();auto declaration=configuration["model"].toObject();
    declaration["neuron_class"]="AClassDifferentFromTheArchivedNeuron";configuration["model"]=declaration;changed["configuration"]=configuration;
    EXPECT_THROW(PrepareNativePhysicalModelData(Signed(changed),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}

TEST(NativePhysicalModelData,DataCannotAcquireCertificateCheckpointOrDifferentTrainingTargetByResigning)
{
    Fixture fixture;fixture.Create<NNeuronTimeLearnerBranch>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto model=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    for(const auto& field:{"certificate","dynamic_checkpoint","data_only"})
    {
        auto changed=model;changed[field]=QString::fromLatin1(field)=="certificate"?QJsonValue(QJsonObject{{"status","exact"}}):
            QJsonValue(QString::fromLatin1(field)=="dynamic_checkpoint");
        EXPECT_THROW(PrepareNativePhysicalModelData(Signed(changed),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    }
    auto changed=model;auto protocol=changed["protocol"].toObject();protocol["pattern_hash"]=QString(64,'0');changed["protocol"]=protocol;
    EXPECT_THROW(PrepareNativePhysicalModelData(Signed(changed),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}
}
