#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativePhysicalModelData.h"
#include "TimeLearner/NativeThresholdCandidate.h"
#include <limits>
#include "TimeLearner/NativeRecognitionState.h"
#include "TimeLearner/NativeRecognitionTrial.h"
#include "TimeLearner/NativeRecognitionObservationValidation.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <sstream>
#include <type_traits>
#include <utility>
#include <functional>
#include <map>
#include <set>
#include <typeinfo>
#include <vector>

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
    template<class Owner> void Create(unsigned frequency=2000,Normalization normalization=Normalization::SynapseCount)
    {
        const bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);environment->GetTime().SetTime(0);
        ASSERT_TRUE(environment->CreateModel("NModel"));auto model=environment->GetModel();model->SetGlobalTimeStep(frequency);
        auto owner=dynamic_pointer_cast<Owner>(storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        ASSERT_TRUE(owner);owner->Name="Source";UEPtr<UContainer> component=owner;
        ASSERT_NE(model->AddComponent(component),ForbiddenId);owner->SetGlobalTimeStep(frequency);
        ConfiguredNativeTraining configuration;auto& declaration=configuration.model;
        declaration.branch=branch;declaration.frequencyHz=frequency;declaration.neuronClass="NSPNeuronGen";
        declaration.normalization=normalization;declaration.inputs={{2,2,86e6},{1,1,91e6}};
        // N1 varies resistance with one synapse per bank. The asymmetric N0
        // fixture intentionally has two synapses in its first bank.
        if(normalization==Normalization::TipResistance)declaration.inputs.front().synapses=1;
        declaration.initialIsi={.01,.08};declaration.editPolicy.normalization=normalization;
        declaration.editPolicy.maximumCableLength=8;
        configuration.stimulusProfile={"NPulseGeneratorTransit",1.,.001,double(frequency),0.,false,false};
        configuration.runId=branch?"physical-data-branch":"physical-data-classic";
        configuration.protocolRevision="physical-data-reference-v1";configuration.duration=.3;
        configuration.maximumSampleGap=1./frequency;
        configuration.maximumSamples=std::max(std::size_t(1001),std::size_t(std::ceil(configuration.duration*frequency))+1);
        configuration.windows={{0.,.15},{.08,.25}};
        configuration.search.normalization=normalization;
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
    // Version 2 Build validates its declared configuration even for an already
    // installed graph. Supply the captured declaration before native Init;
    // an empty configuration is not a valid frozen model initialization path.
    targetOwner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(restored->configuration))
        .toJson(QJsonDocument::Compact).toStdString();
    UEPtr<UContainer> targetComponent=targetOwner;
    ASSERT_NE(fixture.environment->GetModel()->AddComponent(targetComponent),ForbiddenId);
    const auto installed=targetOwner->InstallNativePreparedModel(restored->configuration.model,
        restored->neuron,restored->dataset,restored->parameters);
    ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
    targetOwner->Init();fixture.environment->GetModel()->Init();fixture.environment->GetModel()->Reset();
    ASSERT_TRUE(sourceOwner->NativeModelEditFailure().empty())<<sourceOwner->NativeModelEditFailure();
    ASSERT_TRUE(targetOwner->NativeModelEditFailure().empty())<<targetOwner->NativeModelEditFailure();
    EXPECT_EQ(targetOwner->NativeTrainingController().State(),NativeTrainingState::Idle);
    EXPECT_FALSE(targetOwner->NativeTrainingController().Certificate());
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
    // Transfer must preserve the actual response and its measurement status.
    // This native stock profile can have two peaks in the declared window;
    // ambiguity is an honest measurement result, not a failed model transfer.
    // Do not change its physics/window or silently turn ambiguity into valid.
    for(const auto* result:{&*sourceResult,&*targetResult})
        EXPECT_TRUE(result->observation->valid || result->observation->reasons==
            (std::vector<std::string>{"peak_ambiguous:input0"}));
    const auto comparableObservation=[](const NativeProbeResult& result) {
        auto observation=EncodeNativeProbeEvidence(result)["observation"].toObject();
        auto specification=observation["specification"].toObject();
        specification.remove("run_id");specification.remove("trial_id");
        observation["specification"]=specification;return observation;
    };
    EXPECT_EQ(comparableObservation(*sourceResult),comparableObservation(*targetResult));
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

template<class Owner> void FrozenDataMatchesOriginalRecognition(bool explicitDataConversion=false,bool thresholdCandidate=false)
{
    Fixture fixture;fixture.Create<Owner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    auto recognition=ConvertNativeStoppedToDiagnosticRecognition(fixture.source,NativeRecognitionSpec{},
        fixture.storage,fixture.environment,Implementation);
    auto data=explicitDataConversion?ConvertNativeSoloPhysicalModelDataToRecognition(
        ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation),NativeRecognitionSpec{}, {},
        fixture.storage,fixture.environment,Implementation):
        ExportNativePhysicalModelData(recognition,fixture.storage,fixture.environment,Implementation);
    if(thresholdCandidate)
    {
        recognition=CreateNativeDiagnosticThresholdCandidate(recognition,1e-5,fixture.storage,fixture.environment,Implementation);
        data=CreateNativePhysicalThresholdCandidate(data,1e-5,fixture.storage,fixture.environment,Implementation);
    }
    const auto create=[&](const char* name) {
        auto owner=dynamic_pointer_cast<Owner>(fixture.storage->TakeObject(
            std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        if(!owner)throw std::runtime_error("missing_frozen_fixture_owner");
        owner->Name=name;owner->SetEnvironment(fixture.environment);owner->SetGlobalTimeStep(2000);
        UEPtr<UContainer> component=owner;
        if(fixture.environment->GetModel()->AddComponent(component)==ForbiddenId)
            throw std::runtime_error("cannot_attach_frozen_fixture_owner");
        return owner;
    };
    auto original=create("FullSource"),restored=create("PhysicalData");
    auto result=original->ImportNativeDiagnosticRecognitionState(recognition,Implementation);
    ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;
    result=restored->ImportNativePhysicalModelData(data,Implementation);
    ASSERT_EQ(result.status,NativeModelBuildStatus::Adopted)<<result.reason;
    // The fixture's parent model is already initialized. UModule::Init is
    // idempotent and does not initialize newly attached owners on a second
    // call. Initialize the two fresh components through their native lifecycle
    // before asking the existing scheduler to calculate them.
    original->Init();restored->Init();
    auto model=fixture.environment->GetModel();model->Init();model->Reset();
    ASSERT_TRUE(original->IsInit());ASSERT_TRUE(restored->IsInit());
    ASSERT_TRUE(original->NativeModelEditFailure().empty())<<original->NativeModelEditFailure();
    ASSERT_TRUE(restored->NativeModelEditFailure().empty())<<restored->NativeModelEditFailure();
    EXPECT_FALSE(original->HasNativePhysicalModelData());EXPECT_TRUE(restored->HasNativePhysicalModelData());
    EXPECT_EQ(restored->NativeTrainingController().State(),NativeTrainingState::Idle);
    EXPECT_FALSE(restored->NativeTrainingController().Certificate());EXPECT_FALSE(restored->IsNeedToTrain.GetData());
    EXPECT_EQ(restored->ExportNativePhysicalModelData(Implementation),data);
    EXPECT_THROW(restored->ExportNativeRecognitionState(Implementation),std::logic_error);
    EXPECT_THROW(restored->BeginNativeTraining(NativeTrainingPlan{}),std::logic_error);
    for(int pattern=0;pattern<2;++pattern)
    {
        NativeRecognitionTrialRequest request;request.runId="full-source";
        request.trialId="pattern"+std::to_string(pattern);request.sampleId=request.trialId;
        request.label=pattern?"foil":"target";request.pattern=original->InputPattern.GetData();
        if(pattern)request.pattern(1,0)*=2.;
        QJsonArray isi;for(int i=0;i<2;++i)isi.append(request.pattern(i,0));
        request.patternHash=NmsdkTools::CanonicalModelDataSha256(isi).toStdString();
        request.duration=.4;request.maximumSamples=1002;request.recordThresholdPotential=true;
        original->QueueNativeRecognitionTrial(request);request.runId="physical-data";
        restored->QueueNativeRecognitionTrial(request);
        // A queued trial must survive a refused replacement unchanged.
        const auto busy=restored->ImportNativePhysicalModelData(data,Implementation);
        EXPECT_EQ(busy.status,NativeModelBuildStatus::Rejected);EXPECT_FALSE(busy.modelMayHaveChanged);
        std::optional<NativeRecognitionTrialObservation> before,after;
        for(int tick=0;tick<1002 && (!before || !after);++tick)
        {
            model->Calculate();fixture.environment->IncreaseModelTimeByStep();
            if(!before)before=original->TakeNativeRecognitionTrialResult();
            if(!after)after=restored->TakeNativeRecognitionTrialResult();
        }
        ASSERT_TRUE(before);ASSERT_TRUE(after);
        ASSERT_TRUE(before->complete)<<before->reason;ASSERT_TRUE(after->complete)<<after->reason;
        ASSERT_TRUE(before->valid)<<before->reason;ASSERT_TRUE(after->valid)<<after->reason;
        EXPECT_EQ(before->stimulusTimes.size(),2u);EXPECT_EQ(before->samples.size(),801u);
        EXPECT_EQ(before->modelBefore,before->modelAfter);EXPECT_EQ(before->modelBefore,after->modelBefore);
        EXPECT_EQ(after->modelBefore,after->modelAfter);
        const auto comparable=[](const NativeRecognitionTrialObservation& observation) {
            auto value=NativeRecognitionTrialJson(observation);value.remove("run_id");return value;
        };
        EXPECT_EQ(comparable(*before),comparable(*after));
        if(thresholdCandidate)EXPECT_GT(NativeRecognitionTrialJson(*before)["spike_count"].toInt(),0);
        EXPECT_EQ(restored->ExportNativePhysicalModelData(Implementation),data);
        EXPECT_EQ(original->ExportNativeRecognitionState(Implementation),recognition);
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            const QString stem=QString(thresholdCandidate?"physical-data-threshold-":explicitDataConversion?"physical-data-converted-":"physical-data-frozen-")+
                (std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"Branch":"Classic")+(pattern?"-foil":"-target");
            QFile json(QDir(QString::fromLocal8Bit(output)).filePath(stem+".json"));
            ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QJsonDocument(QJsonObject{{"kind","timelearner_frozen_physical_data_fixture"},
                {"schema_version",1},{"source_boundary",data["source_boundary"]},{"model_data_sha256",data["sha256"]},
                {"full_source",NativeRecognitionTrialJson(*before)},{"physical_data",NativeRecognitionTrialJson(*after)},
                {"training_certificate_transferred",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson();
            ASSERT_EQ(json.write(bytes),bytes.size());
            if(pattern==0)
            {
                const auto prefix=QString(thresholdCandidate?"physical-data-threshold-":explicitDataConversion?"physical-data-converted-":"physical-data-frozen-")+
                    (std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"Branch":"Classic");
                for(const auto& item:{std::make_pair("-model-data.json",data),std::make_pair("-source.json",recognition)})
                {
                    QFile artifact(QDir(QString::fromLocal8Bit(output)).filePath(prefix+item.first));
                    ASSERT_TRUE(artifact.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                    const auto raw=QJsonDocument(item.second).toJson();ASSERT_EQ(artifact.write(raw),raw.size());
                }
            }
            std::ostringstream trace;trace<<std::setprecision(17)<<"time,actual_input,full_lt,restored_lt,full_lt_potential,restored_lt_potential";
            for(std::size_t channel=0;channel<before->samples.front().somaPotentials.size();++channel)
                trace<<",full_soma"<<channel+1<<",restored_soma"<<channel+1;
            trace<<'\n';ASSERT_EQ(before->samples.size(),after->samples.size());
            for(std::size_t i=0;i<before->samples.size();++i)
            {
                const auto& a=before->samples[i];const auto& b=after->samples[i];
                trace<<a.time<<','<<a.stimulus<<','<<a.ltOutput<<','<<b.ltOutput<<','<<a.thresholdPotential<<','<<b.thresholdPotential;
                ASSERT_EQ(a.somaPotentials.size(),b.somaPotentials.size());
                for(std::size_t channel=0;channel<a.somaPotentials.size();++channel)
                    trace<<','<<a.somaPotentials[channel]<<','<<b.somaPotentials[channel];
                trace<<'\n';
            }
            QFile csv(QDir(QString::fromLocal8Bit(output)).filePath(stem+".csv"));
            ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto raw=trace.str();
            ASSERT_EQ(csv.write(raw.data(),qint64(raw.size())),qint64(raw.size()));
        }
    }
}

TEST(NativePhysicalModelData,ClassicFrozenDataMatchesFullSourceTargetAndFoilWithoutProofAuthority)
{FrozenDataMatchesOriginalRecognition<NNeuronTimeLearner>();}
TEST(NativePhysicalModelData,BranchFrozenDataMatchesFullSourceTargetAndFoilWithoutProofAuthority)
{FrozenDataMatchesOriginalRecognition<NNeuronTimeLearnerBranch>();}

template<class Owner> void FrozenPhysicalDynamicsContinuity(unsigned frequency)
{
    Fixture fixture;fixture.Create<Owner>(frequency);ASSERT_FALSE(::testing::Test::HasFatalFailure());
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const auto recognition=ConvertNativeStoppedToDiagnosticRecognition(fixture.source,NativeRecognitionSpec{},
        fixture.storage,fixture.environment,Implementation);
    const auto data=ExportNativePhysicalModelData(recognition,fixture.storage,fixture.environment,Implementation);
    auto model=fixture.environment->GetModel();
    const auto create=[&](const char* name) {
        auto owner=dynamic_pointer_cast<Owner>(fixture.storage->TakeObject(branch?
            "NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        if(!owner)throw std::runtime_error("continuity_fixture_owner_missing");
        owner->Name=name;owner->SetEnvironment(fixture.environment);owner->SetGlobalTimeStep(frequency);
        UEPtr<UContainer> component=owner;
        if(model->AddComponent(component)==ForbiddenId)throw std::runtime_error("continuity_fixture_attach_failed");
        const auto installed=owner->ImportNativePhysicalModelData(data,Implementation);
        if(installed.status!=NativeModelBuildStatus::Adopted)throw std::runtime_error(installed.reason);
        owner->Init();return owner;
    };
    auto reset=create("ResetControl"),preserve=create("PreservedControl");
    model->Init();model->Reset();
    // End just after the second physical pulse. A long quiet tail would erase
    // the positive control and could not distinguish a real preserve from reset.
    const std::size_t trialTicks=std::size_t(frequency)*91/1000+4;
    const double duration=double(trialTicks)/frequency;
    const auto request=[&](const std::string& run,int index,RecognitionResetPolicy policy) {
        NativeRecognitionTrialRequest q;q.runId=run;q.trialId=run+"/"+std::to_string(index);
        q.sampleId="target";q.label="target";q.pattern.Assign(2,1,0.);
        q.pattern(0,0)=.01;q.pattern(1,0)=.08;
        q.patternHash=NmsdkTools::CanonicalModelDataSha256(QJsonArray{.01,.08}).toStdString();
        q.duration=duration;q.maximumSamples=trialTicks+1;q.resetPolicy=policy;q.recordThresholdPotential=true;
        return q;
    };
    const auto somas=[&](UEPtr<Owner> owner) {
        auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        if(!neuron)throw std::runtime_error("continuity_fixture_neuron_missing");
        std::vector<double> values;
        for(std::size_t i=0;i<(branch?1u:2u);++i)
        {
            auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);
            if(!soma || soma->SumPotential.GetRows()!=1 || soma->SumPotential.GetCols()!=1)
                throw std::runtime_error("continuity_fixture_soma_missing");
            values.push_back(soma->SumPotential(0,0));
        }
        return values;
    };
    QJsonArray observations;std::vector<double> baseline,priorEnd;
    double preservedDifference=0.;
    for(int iteration=0;iteration<2;++iteration)
    {
        const auto a=request("reset",iteration,RecognitionResetPolicy::PerTrial);
        const auto b=request("preserve",iteration,iteration==0?RecognitionResetPolicy::PerTrial:
                                                                     RecognitionResetPolicy::PreserveNeuronDynamics);
        reset->QueueNativeRecognitionTrial(a);preserve->QueueNativeRecognitionTrial(b);
        std::optional<NativeRecognitionTrialObservation> left,right;
        std::vector<std::vector<double>> independentLeft,independentRight;
        std::vector<double> independentTimes;
        for(std::size_t tick=0;tick<trialTicks+2 && (!left || !right);++tick)
        {
            const double time=fixture.environment->GetTime().GetDoubleTime();
            model->Calculate(); // One parent tick; neither owner is calculated separately.
            independentTimes.push_back(time);independentLeft.push_back(somas(reset));independentRight.push_back(somas(preserve));
            fixture.environment->IncreaseModelTimeByStep();
            if(!left)left=reset->TakeNativeRecognitionTrialResult();
            if(!right)right=preserve->TakeNativeRecognitionTrialResult();
        }
        ASSERT_TRUE(left);ASSERT_TRUE(right);ASSERT_TRUE(left->valid)<<left->reason;ASSERT_TRUE(right->valid)<<right->reason;
        ValidateNativeRecognitionObservation(a,*left);ValidateNativeRecognitionObservation(b,*right);
        ASSERT_EQ(left->samples.size(),trialTicks+1);ASSERT_EQ(right->samples.size(),left->samples.size());
        ASSERT_EQ(independentTimes.size(),left->samples.size());
        for(std::size_t i=0;i<left->samples.size();++i)
        {
            EXPECT_DOUBLE_EQ(left->samples[i].time,independentTimes[i]);
            EXPECT_DOUBLE_EQ(right->samples[i].time,independentTimes[i]);
            EXPECT_EQ(left->samples[i].somaPotentials,independentLeft[i]);
            EXPECT_EQ(right->samples[i].somaPotentials,independentRight[i]);
            if(iteration==0)EXPECT_EQ(left->samples[i].somaPotentials,right->samples[i].somaPotentials);
        }
        EXPECT_EQ(left->modelBefore,data["model_revision"].toString().toStdString());
        EXPECT_EQ(left->modelAfter,left->modelBefore);EXPECT_EQ(right->modelBefore,left->modelBefore);
        EXPECT_EQ(right->modelAfter,left->modelBefore);
        if(iteration==0)
        {
            baseline=left->samples.front().somaPotentials;priorEnd=left->samples.back().somaPotentials;
            double signal=0.;
            for(std::size_t i=0;i<baseline.size();++i)signal=std::max(signal,std::abs(priorEnd[i]-baseline[i]));
            ASSERT_GT(signal,1.e-6)<<"No residual physical response at the declared boundary";
        }
        else
        {
            EXPECT_EQ(left->samples.front().somaPotentials,baseline); // Model-native rest, not an assumed zero.
            for(std::size_t i=0;i<baseline.size();++i)
                preservedDifference=std::max(preservedDifference,std::abs(right->samples.front().somaPotentials[i]-baseline[i]));
            EXPECT_GT(preservedDifference,1.e-6)<<"Preserve did not retain the measured physical dynamics";
            const auto previous=observations.first().toObject()["reset"].toObject();
            EXPECT_NEAR(left->begin,previous["end"].toDouble()+1./frequency,1.e-12);
            EXPECT_NEAR(right->begin,left->begin,1.e-12);
            EXPECT_EQ(left->samples.front().stimulus,0.);EXPECT_EQ(right->samples.front().stimulus,0.);
        }
        EXPECT_EQ(reset->ExportNativePhysicalModelData(Implementation),data);
        EXPECT_EQ(preserve->ExportNativePhysicalModelData(Implementation),data);
        EXPECT_EQ(reset->NativeTrainingController().State(),NativeTrainingState::Idle);
        EXPECT_EQ(preserve->NativeTrainingController().State(),NativeTrainingState::Idle);
        EXPECT_FALSE(reset->IsNeedToTrain.GetData());EXPECT_FALSE(preserve->IsNeedToTrain.GetData());
        observations.append(QJsonObject{{"reset",NativeRecognitionTrialJson(*left)},
                                       {"preserve",NativeRecognitionTrialJson(*right)}});
    }
    if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        const auto stem=QString("physical-continuity-")+(branch?"Branch":"Classic")+"-"+QString::number(frequency);
        QFile file(QDir(QString::fromLocal8Bit(output)).filePath(stem+".json"));
        ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(QJsonObject{{"kind","timelearner_physical_dynamics_continuity_fixture"},
            {"schema_version",1},{"frequency_hz",double(frequency)},{"model_data_sha256",data["sha256"]},
            {"model_revision",data["model_revision"]},{"observations",observations},
            {"preserved_first_sample_difference",preservedDifference},
            {"new_training_performed",false},{"production_continuous_wrapper_verified",false},
            {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson();
        ASSERT_EQ(file.write(bytes),bytes.size());
    }
}

template<class Owner> void ExplicitDataConversionPostTuneAndNoProof()
{
    Fixture fixture;fixture.Create<Owner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    const auto originalSolo=solo;const auto originalSource=fixture.source;
    const auto base=ConvertNativeSoloPhysicalModelDataToRecognition(solo,{}, {},fixture.storage,fixture.environment,Implementation);
    EXPECT_EQ(base["schema_version"],QJsonValue(2));EXPECT_EQ(base["source_boundary"],solo["source_boundary"]);
    EXPECT_EQ(base["source_model_data"],solo);EXPECT_TRUE(base["certificate"].isNull());
    EXPECT_EQ(base,ConvertNativeSoloPhysicalModelDataToRecognition(solo,{}, {},fixture.storage,fixture.environment,Implementation));
    EXPECT_THROW(ConvertNativeSoloPhysicalModelDataToRecognition(base,{}, {},fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_THROW(ConvertNativeSoloPhysicalModelDataToRecognition(solo,{}, {1.,2.},fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_THROW(PrepareNativeLearnedState(base,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_THROW(PrepareNativeDiagnosticRecognitionState(base,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    for(auto mode:{NativePostTuneMode::Off,NativePostTuneMode::KeepDone,NativePostTuneMode::CanonRmin,
                  NativePostTuneMode::FlatLastR,NativePostTuneMode::SearchSyntheticCandidate})
    {
        SCOPED_TRACE(int(mode));NativeRecognitionSpec spec;NativePostTuneSpec post;
        post.mode=mode;post.sourceModelRevision=base["model_revision"].toString().toStdString();
        if(mode==NativePostTuneMode::CanonRmin){post.canonicalFloor=30e6;post.canonicalLast=50e6;}
        if(mode==NativePostTuneMode::FlatLastR)post.canonicalLast=50e6;
        if(mode==NativePostTuneMode::SearchSyntheticCandidate)post.requestedResistances={40e6,60e6};
        if(mode!=NativePostTuneMode::Off && mode!=NativePostTuneMode::KeepDone)post.resistanceBounds={{1e6,1e9},{1e6,1e9}};
        spec.postTune=post;
        const auto converted=ConvertNativeSoloPhysicalModelDataToRecognition(solo,spec,{},fixture.storage,fixture.environment,Implementation);
        const auto full=ConvertNativeStoppedToDiagnosticRecognition(fixture.source,spec,fixture.storage,fixture.environment,Implementation);
        EXPECT_EQ(converted["neuron"],full["neuron"]);EXPECT_EQ(converted["model_revision"],full["model_revision"]);
        EXPECT_EQ(converted["parameters"],full["recognition_inputs"]);EXPECT_EQ(converted["conversion_record"],full["conversion_record"]);
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            const QString name=QString("physical-data-post-")+(std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"Branch":"Classic")+
                "-"+QString::number(int(mode))+".json";
            QFile file(QDir(QString::fromLocal8Bit(output)).filePath(name));ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto raw=QJsonDocument(converted).toJson();ASSERT_EQ(file.write(raw),raw.size());
        }
        const auto frozen=PrepareNativeFrozenPhysicalModelData(converted,fixture.storage,fixture.environment,Implementation);
        EXPECT_EQ(frozen->modelRevision,converted["model_revision"].toString().toStdString());
        EXPECT_FALSE(frozen->calibrationConfirmed);EXPECT_FALSE(frozen->configuration.model.allowMutedInputBaseline);
        EXPECT_EQ(solo,originalSolo);EXPECT_EQ(fixture.source,originalSource);EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
    }
}
TEST(NativePhysicalDataConversion,ClassicPostTuneAllModesMatchFullNativeConversionWithoutHistoryOrAuthority)
{ExplicitDataConversionPostTuneAndNoProof<NNeuronTimeLearner>();}
TEST(NativePhysicalDataConversion,BranchPostTuneAllModesMatchFullNativeConversionWithoutHistoryOrAuthority)
{ExplicitDataConversionPostTuneAndNoProof<NNeuronTimeLearnerBranch>();}
TEST(NativePhysicalDataConversion,ClassicTargetAndFoilMatchFullNativeConversion)
{FrozenDataMatchesOriginalRecognition<NNeuronTimeLearner>(true);}
TEST(NativePhysicalDataConversion,BranchTargetAndFoilMatchFullNativeConversion)
{FrozenDataMatchesOriginalRecognition<NNeuronTimeLearnerBranch>(true);}
TEST(NativePhysicalDataConversion,ResignedTransitionCannotChangeGraphSourceOrAcquireAuthority)
{
    Fixture fixture;fixture.Create<NNeuronTimeLearnerBranch>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    const auto converted=ConvertNativeSoloPhysicalModelDataToRecognition(solo,{}, {},fixture.storage,fixture.environment,Implementation);
    for(int fault=0;fault<7;++fault)
    {
        SCOPED_TRACE(fault);auto damaged=converted;
        if(fault==0)damaged["certificate"]=QJsonObject{};
        if(fault==1)damaged["data_only"]=false;
        if(fault==2)damaged["source_model_data"]=converted;
        if(fault==3){auto parameters=damaged["parameters"].toArray();auto input=parameters[0].toObject();input["resistance"]=77e6;parameters[0]=input;damaged["parameters"]=parameters;}
        if(fault==4){auto boundary=damaged["source_boundary"].toObject();boundary["kind"]="timelearner_recognition_state";boundary["state_kind"]="recognition";damaged["source_boundary"]=boundary;}
        if(fault==5){auto record=damaged["conversion_record"].toObject();record["source_solo_sha256"]=QString(64,'0');damaged["conversion_record"]=record;}
        if(fault==6)damaged["reference_amplitudes"]=QJsonArray{1.,2.};
        EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(Signed(damaged),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
        EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
    }
}
TEST(NativePhysicalDataConversion,BranchN1UsesDeclaredReferenceDataAndNativeBounds)
{
    Fixture fixture;fixture.Create<NNeuronTimeLearnerBranch>(2000,Normalization::TipResistance);ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    NativeRecognitionSpec specification;specification.mode=RecognitionConversionMode::HistoricalBranchN1;
    specification.resistanceBounds={{1e6,120e6},{1e6,150e6}};
    EXPECT_THROW(ConvertNativeSoloPhysicalModelDataToRecognition(solo,specification,{},fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    // Explicit test DATA for the physical transform; no measured-reference or
    // training certificate is claimed by this stopped, zero-observation fixture.
    const auto result=ConvertNativeSoloPhysicalModelDataToRecognition(solo,specification,{1.,2.},fixture.storage,fixture.environment,Implementation);
    EXPECT_TRUE(result["certificate"].isNull());EXPECT_EQ(result["reference_amplitudes"],QJsonValue(QJsonArray{1.,2.}));
    const auto decisions=result["conversion_record"].toObject()["decisions"].toArray();ASSERT_EQ(decisions.size(),2);
    EXPECT_EQ(decisions[0].toObject()["factor"],QJsonValue(2.));EXPECT_EQ(decisions[1].toObject()["factor"],QJsonValue(4.));
    EXPECT_EQ(result["parameters"].toArray()[0].toObject()["resistance"],QJsonValue(120e6));
    EXPECT_EQ(result["parameters"].toArray()[1].toObject()["resistance"],QJsonValue(150e6));
    if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        QFile file(QDir(QString::fromLocal8Bit(output)).filePath("physical-data-historical-Branch.json"));
        ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto raw=QJsonDocument(result).toJson();
        ASSERT_EQ(file.write(raw),raw.size());
    }
    const auto frozen=PrepareNativeFrozenPhysicalModelData(result,fixture.storage,fixture.environment,Implementation);
    EXPECT_EQ(frozen->modelRevision,result["model_revision"].toString().toStdString());
    EXPECT_EQ(result,ConvertNativeSoloPhysicalModelDataToRecognition(solo,specification,{1.,2.},fixture.storage,fixture.environment,Implementation));
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}

TEST(NativePhysicalThresholdCandidate,NativeData1AndData2MatchFullCandidateGraphAndKeepOriginalBoundary)
{
    for(bool branch:{false,true})for(bool convertedSource:{false,true})
    {
        Fixture fixture;if(branch)fixture.Create<NNeuronTimeLearnerBranch>();else fixture.Create<NNeuronTimeLearner>();
        ASSERT_FALSE(::testing::Test::HasFatalFailure());
        const auto recognition=ConvertNativeStoppedToDiagnosticRecognition(fixture.source,{},fixture.storage,fixture.environment,Implementation);
        const auto source=convertedSource?ConvertNativeSoloPhysicalModelDataToRecognition(
            ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation),{}, {},
            fixture.storage,fixture.environment,Implementation):ExportNativePhysicalModelData(recognition,fixture.storage,fixture.environment,Implementation);
        for(double threshold:{-1e-3,0.,1e-5,100.})
        {
            const auto full=CreateNativeDiagnosticThresholdCandidate(recognition,threshold,fixture.storage,fixture.environment,Implementation);
            const auto candidate=CreateNativePhysicalThresholdCandidate(source,threshold,fixture.storage,fixture.environment,Implementation);
            EXPECT_EQ(candidate["schema_version"],QJsonValue(3));EXPECT_TRUE(candidate["certificate"].isNull());
            EXPECT_EQ(candidate["source_boundary"],source["source_boundary"]);EXPECT_EQ(candidate["source_recognition_data"],QJsonValue(source));
            EXPECT_EQ(candidate["parameters"],source["parameters"]);EXPECT_EQ(candidate["model_revision"],full["model_revision"]);
            EXPECT_EQ(candidate["neuron"].toObject()["graph"].toObject()["identity"],full["neuron"].toObject()["graph"].toObject()["identity"]);
            EXPECT_FALSE(candidate["candidate_record"].toObject()["calibrated"].toBool(true));
            const auto restored=PrepareNativeFrozenPhysicalModelData(candidate,fixture.storage,fixture.environment,Implementation);
            EXPECT_EQ(restored->modelRevision,candidate["model_revision"].toString().toStdString());
            EXPECT_EQ(candidate,CreateNativePhysicalThresholdCandidate(source,threshold,fixture.storage,fixture.environment,Implementation));
            EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
        }
    }
}
TEST(NativePhysicalThresholdCandidate,RejectsSoloChainingNonfiniteAndResignedExtraEdits)
{
    Fixture fixture;fixture.Create<NNeuronTimeLearnerBranch>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    EXPECT_THROW(CreateNativePhysicalThresholdCandidate(solo,1e-5,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    const auto source=ConvertNativeSoloPhysicalModelDataToRecognition(solo,{}, {},fixture.storage,fixture.environment,Implementation);
    const auto candidate=CreateNativePhysicalThresholdCandidate(source,1e-5,fixture.storage,fixture.environment,Implementation);
    EXPECT_THROW(CreateNativePhysicalThresholdCandidate(candidate,2e-5,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    EXPECT_THROW(CreateNativePhysicalThresholdCandidate(source,std::numeric_limits<double>::infinity(),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    for(int fault=0;fault<5;++fault)
    {
        auto damaged=candidate;
        if(fault==0)damaged["threshold"]=2e-5;
        if(fault==1)damaged["source_recognition_data"]=candidate;
        if(fault==2)damaged["certificate"]=QJsonObject{};
        if(fault==3){auto boundary=damaged["source_boundary"].toObject();boundary["kind"]="timelearner_recognition_state";boundary["state_kind"]="recognition";damaged["source_boundary"]=boundary;}
        if(fault==4){auto archive=damaged["neuron"].toObject();auto metadata=archive["metadata"].toObject();auto verification=metadata["recognition_verification"].toObject();verification["status"]="verified";verification["certificate"]=QJsonObject{};metadata["recognition_verification"]=verification;archive["metadata"]=metadata;damaged["neuron"]=Signed(archive);}
        EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(Signed(damaged),fixture.storage,fixture.environment,Implementation),std::invalid_argument);
        EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
    }
}
TEST(NativePhysicalThresholdCandidate,ClassicTargetAndFoilMatchFullCandidateWithActualSpikes)
{FrozenDataMatchesOriginalRecognition<NNeuronTimeLearner>(true,true);}
TEST(NativePhysicalThresholdCandidate,BranchTargetAndFoilMatchFullCandidateWithActualSpikes)
{FrozenDataMatchesOriginalRecognition<NNeuronTimeLearnerBranch>(true,true);}

TEST(NativePhysicalDynamicsContinuity,Classic2000){FrozenPhysicalDynamicsContinuity<NNeuronTimeLearner>(2000);}
TEST(NativePhysicalDynamicsContinuity,Branch2000){FrozenPhysicalDynamicsContinuity<NNeuronTimeLearnerBranch>(2000);}
TEST(NativePhysicalDynamicsContinuity,Classic20000){FrozenPhysicalDynamicsContinuity<NNeuronTimeLearner>(20000);}
TEST(NativePhysicalDynamicsContinuity,Branch20000){FrozenPhysicalDynamicsContinuity<NNeuronTimeLearnerBranch>(20000);}

TEST(NativePhysicalModelData,FrozenDataRejectsSoloAndResignedThresholdMetadata)
{
    Fixture fixture;fixture.Create<NNeuronTimeLearner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(solo,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    const auto recognition=ConvertNativeStoppedToDiagnosticRecognition(fixture.source,NativeRecognitionSpec{},
        fixture.storage,fixture.environment,Implementation);
    auto data=ExportNativePhysicalModelData(recognition,fixture.storage,fixture.environment,Implementation);
    auto neuron=data["neuron"].toObject(),metadata=neuron["metadata"].toObject(),calibration=metadata["calibration"].toObject();
    calibration["threshold"]=calibration["threshold"].toDouble()+1.;metadata["calibration"]=calibration;neuron["metadata"]=metadata;
    // Keep both digests valid: a checksum is not proof that metadata matches physics.
    neuron=Signed(neuron);data["neuron"]=neuron;data=Signed(data);
    try
    {
        PrepareNativeFrozenPhysicalModelData(data,fixture.storage,fixture.environment,Implementation);
        FAIL()<<"Contradictory threshold metadata was accepted";
    }
    catch(const NmsdkTools::ModelArchiveError& error)
    {
        // The shared archive validator rejects the contradiction before the
        // frozen DATA adapter. Preserve its typed diagnostic contract.
        EXPECT_EQ(error.code,"calibration_model_mismatch");
        EXPECT_NE(std::string(error.what()).find("$.LTZone"),std::string::npos);
    }
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}
}

namespace {
using XmlEdit=std::function<void(RDK::USerStorageXML&,std::size_t&)>;
void EditXmlTree(RDK::USerStorageXML& xml,const XmlEdit& edit,std::size_t& changes)
{
    edit(xml,changes);
    const int children=xml.GetNumNodes();
    for(int index=0;index<children;++index)
    {
        if(!xml.SelectNode(index))throw std::logic_error("portable_fixture_child");
        EditXmlTree(xml,edit,changes);xml.SelectUp();
    }
}
QJsonObject EditSnapshotXml(QJsonObject snapshot,const XmlEdit& edit,std::size_t& changes)
{
    RDK::USerStorageXML xml;
    if(!xml.Load(snapshot["native_xml"].toString().toStdString(),"TimeLearnerNativeGraph"))
        throw std::logic_error("portable_fixture_xml");
    EditXmlTree(xml,edit,changes);std::string encoded;
    if(!xml.Save(encoded))throw std::logic_error("portable_fixture_save");
    snapshot["native_xml"]=QString::fromStdString(encoded);
    snapshot["native_xml_sha256"]=QString::fromLatin1(QCryptographicHash::hash(
        QByteArray::fromStdString(encoded),QCryptographicHash::Sha256).toHex());
    return snapshot;
}
QJsonObject EditDataArchive(QJsonObject data,const XmlEdit& edit,bool definitionsOnly=false)
{
    auto archive=data["neuron"].toObject();std::size_t changes=0;
    if(!definitionsOnly)archive["graph"]=EditSnapshotXml(archive["graph"].toObject(),edit,changes);
    auto definitions=archive["class_definitions"].toArray();
    for(int index=0;index<definitions.size();++index)
    {
        auto definition=definitions[index].toObject();
        definition["snapshot"]=EditSnapshotXml(definition["snapshot"].toObject(),edit,changes);
        definitions[index]=definition;
    }
    if(!changes)throw std::logic_error("portable_fixture_did_not_edit_xml");
    archive["class_definitions"]=definitions;data["neuron"]=Signed(archive);return Signed(data);
}
const XmlEdit OtherCompilerScalarSpellings=[](RDK::USerStorageXML& xml,std::size_t& changes) {
    // Test input only. Use real production XML and native import; alter only
    // compiler spellings. Unknown/container types retain their original bytes.
    const std::map<std::string,std::string> aliases{{"b","bool"},{"bool","b"},
        {"i","int"},{"int","i"},{"j","unsigned int"},{"unsigned int","j"},
        {"d","double"},{"double","d"}};
    for(const auto* name:{"Type","elemType","elemVecType"})
    {
        const auto found=aliases.find(xml.GetNodeAttribute(name));
        if(found!=aliases.end())
        {if(!xml.SetNodeAttribute(name,found->second))throw std::logic_error("portable_fixture_attribute");++changes;}
    }
};

const XmlEdit OtherCompilerContainerSpellings=[](RDK::USerStorageXML& xml,std::size_t& changes) {
    OtherCompilerScalarSpellings(xml,changes);
    const auto vector=[](std::string type,unsigned depth) {
        for(unsigned i=0;i<depth;++i)type="class std::vector<"+type+",class std::allocator<"+type+"> >";
        return type;
    };
    using V3=std::vector<std::vector<std::vector<int>>>;
    using V4=std::vector<V3>;
    const std::string v3="St6vectorIS_IS_IiSaIiEESaIS1_EESaIS3_EE";
    const std::string v4="St6vectorIS_IS_IS_IiSaIiEESaIS1_EESaIS3_EESaIS5_EE";
    const std::map<std::string,std::string> aliases{
        {"MVector<d>","MVector<double>"},{"MVector<double>","MVector<d>"},
        {"MDMatrix<d>","MDMatrix<double>"},{"MDMatrix<double>","MDMatrix<d>"},
        {"MDMatrix<i>","MDMatrix<int>"},{"MDMatrix<int>","MDMatrix<i>"},
        {typeid(RDK::MDMatrix<double>).name(),std::string(typeid(RDK::MDMatrix<double>).name())=="N3RDK8MDMatrixIdEE"?"class RDK::MDMatrix<double>":"N3RDK8MDMatrixIdEE"},
        {typeid(V3).name(),std::string(typeid(V3).name())==v3?vector("int",3):v3},
        {typeid(V4).name(),std::string(typeid(V4).name())==v4?vector("int",4):v4},
        {"x","__int64"},{"__int64","x"},{"y","unsigned __int64"},{"unsigned __int64","y"}};
    for(const auto* name:{"Type","elemType","elemVecType"})
    {
        const auto found=aliases.find(xml.GetNodeAttribute(name));
        if(found!=aliases.end())
        {if(!xml.SetNodeAttribute(name,found->second))throw std::logic_error("portable_container_fixture_attribute");++changes;}
    }
    // size_t has different nominal C++ types in LP64 and LLP64. These are
    // real NNet size_t parameters, declared as unsigned_integer in identity;
    // no untyped state or other arbitrary ulong field is rewritten here.
    static const std::set<std::string> sizes{"NumLayers","LayerWidth","LayerHeight",
        "ReceptorFieldWidth","ReceptorFieldHeight","LinkOrganizationMode"};
    if(sizes.count(xml.GetNodeName()))
    {
        const auto type=xml.GetNodeAttribute("Type");
        if(type=="m" || type=="y" || type=="unsigned __int64")
        {if(!xml.SetNodeAttribute("Type",type=="m"?"unsigned __int64":"m"))throw std::logic_error("portable_size_fixture_attribute");++changes;}
    }
};

template<class Owner> void PortableDataRoundtrip(Normalization normalization)
{
    Fixture fixture;fixture.Create<Owner>(2000,normalization);ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    const auto source=ConvertNativeSoloPhysicalModelDataToRecognition(solo,{}, {},fixture.storage,fixture.environment,Implementation);
    const auto candidate=CreateNativePhysicalThresholdCandidate(source,1e-5,fixture.storage,fixture.environment,Implementation);
    for(const auto& original:{source,candidate})
    {
        const auto foreign=EditDataArchive(original,OtherCompilerContainerSpellings);
        ASSERT_NE(foreign,original);
        EXPECT_TRUE(NmsdkTools::SamePortableModelArchive(original["neuron"].toObject(),foreign["neuron"].toObject()));
        const auto imported=PrepareNativeFrozenPhysicalModelData(foreign,fixture.storage,fixture.environment,Implementation);
        EXPECT_EQ(imported->modelRevision,original["model_revision"].toString().toStdString());
        EXPECT_EQ(imported->sourceBoundary,original["source_boundary"].toObject());
        EXPECT_FALSE(imported->calibrationConfirmed);EXPECT_TRUE(foreign["certificate"].isNull());
        EXPECT_EQ(foreign["source_solo_revision"],original["source_solo_revision"]);
        EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
        EXPECT_EQ(original["sha256"],Signed(original)["sha256"]);
    }
    // An actual DATA3 generated from an already foreign-spelled DATA2 also
    // keeps the exact immutable nested source and passes native reconstruction.
    const auto foreignSource=EditDataArchive(source,OtherCompilerContainerSpellings);
    const auto fromForeign=CreateNativePhysicalThresholdCandidate(foreignSource,1e-5,
        fixture.storage,fixture.environment,Implementation);
    EXPECT_EQ(fromForeign["source_recognition_data"],QJsonValue(foreignSource));
    EXPECT_EQ(fromForeign["model_revision"],candidate["model_revision"]);
    EXPECT_NO_THROW(PrepareNativeFrozenPhysicalModelData(fromForeign,fixture.storage,fixture.environment,Implementation));
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}
TEST(NativePhysicalPortableData,ClassicN0ImportsConvertedAndThresholdDataWithOtherCompilerSpellings)
{PortableDataRoundtrip<NMSDK::NNeuronTimeLearner>(NMSDK::TimeLearner::Normalization::SynapseCount);}
TEST(NativePhysicalPortableData,ClassicN1ImportsConvertedAndThresholdDataWithOtherCompilerSpellings)
{PortableDataRoundtrip<NMSDK::NNeuronTimeLearner>(NMSDK::TimeLearner::Normalization::TipResistance);}
TEST(NativePhysicalPortableData,BranchN0ImportsConvertedAndThresholdDataWithOtherCompilerSpellings)
{PortableDataRoundtrip<NMSDK::NNeuronTimeLearnerBranch>(NMSDK::TimeLearner::Normalization::SynapseCount);}
TEST(NativePhysicalPortableData,BranchN1ImportsConvertedAndThresholdDataWithOtherCompilerSpellings)
{PortableDataRoundtrip<NMSDK::NNeuronTimeLearnerBranch>(NMSDK::TimeLearner::Normalization::TipResistance);}

TEST(NativePhysicalPortableData,ResignedDifferentXmlTypesAreRejectedInGraphAndStorageImages)
{
    Fixture fixture;fixture.Create<NMSDK::NNeuronTimeLearnerBranch>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto source=ConvertNativeSoloPhysicalModelDataToRecognition(
        ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation),{}, {},
        fixture.storage,fixture.environment,Implementation);
    const auto candidate=CreateNativePhysicalThresholdCandidate(source,1e-5,fixture.storage,fixture.environment,Implementation);
    const XmlEdit wrongType=[](RDK::USerStorageXML& xml,std::size_t& changes) {
        const auto type=xml.GetNodeAttribute("Type");
        if(type=="d" || type=="double")
        {if(!xml.SetNodeAttribute("Type","int"))throw std::logic_error("portable_fixture_attribute");++changes;}
    };
    for(const auto& original:{source,candidate})for(bool imagesOnly:{false,true})
    {
        const auto corrupted=EditDataArchive(original,wrongType,imagesOnly);
        EXPECT_FALSE(NmsdkTools::SamePortableModelArchive(original["neuron"].toObject(),corrupted["neuron"].toObject()));
        EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(corrupted,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    }
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}

TEST(NativePhysicalPortableData,OriginalArchiveAndXmlDigestsRemainMandatory)
{
    Fixture fixture;fixture.Create<NMSDK::NNeuronTimeLearner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto original=ConvertNativeSoloPhysicalModelDataToRecognition(
        ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation),{}, {},
        fixture.storage,fixture.environment,Implementation);
    for(int fault=0;fault<3;++fault)
    {
        auto corrupted=EditDataArchive(original,OtherCompilerScalarSpellings);auto archive=corrupted["neuron"].toObject();
        if(fault==0)archive["sha256"]=QString(64,'0');
        if(fault==1)
        {
            auto graph=archive["graph"].toObject();graph["native_xml_sha256"]=QString(64,'0');
            archive["graph"]=graph;archive=Signed(archive);
        }
        if(fault==2)
        {
            auto graph=archive["graph"].toObject();graph["native_xml"]=graph["native_xml"].toString()+"corrupt";
            archive["graph"]=graph;archive=Signed(archive);
        }
        corrupted["neuron"]=archive;corrupted=Signed(corrupted);
        EXPECT_FALSE(NmsdkTools::SamePortableModelArchive(original["neuron"].toObject(),archive));
        EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(corrupted,fixture.storage,fixture.environment,Implementation),std::invalid_argument);
    }
    EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
}

TEST(NativePhysicalPortableData,ResignedData1ScalarDeclarationsMustMatchTypedIdentityBeforeLoad)
{
    Fixture fixture;fixture.Create<NMSDK::NNeuronTimeLearner>();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const auto solo=ExportNativePhysicalModelData(fixture.source,fixture.storage,fixture.environment,Implementation);
    const XmlEdit wrong=[](RDK::USerStorageXML& xml,std::size_t& changes) {
        const auto type=xml.GetNodeAttribute("Type");
        if(type=="d" || type=="double")
        {if(!xml.SetNodeAttribute("Type","int"))throw std::logic_error("portable_data1_fixture_attribute");++changes;}
    };
    for(bool imagesOnly:{false,true})
    {
        const auto bad=EditDataArchive(solo,wrong,imagesOnly);
        EXPECT_THROW(ConvertNativeSoloPhysicalModelDataToRecognition(bad,{}, {},fixture.storage,fixture.environment,Implementation),std::invalid_argument);
        EXPECT_EQ(fixture.CurrentIdentity(),fixture.initialIdentity);
    }
}
}
