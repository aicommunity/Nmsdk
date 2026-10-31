#include "TimeLearnerTrainingJob.h"
#include "TimeLearnerJobSupport.h"
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeLearnedState.h"
#include <iomanip>
#include <iostream>
#include <locale>
#include <memory>
#include <sstream>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
using namespace NmsdkWorker;
struct Job {
    QJsonObject document;
    ConfiguredNativeTraining configuration;
    QJsonArray profiles;
    std::string ownerClass,implementation;
    int calculateMode=0,structureMode=1;
    std::size_t maximumTicks=0;
};
Job Read(const QString& path)
{
    Job j;j.document=ReadDocument(path);const auto& d=j.document;
    Keys(d,{"kind","schema_version","owner_class","implementation_id","configuration",
        "profile_archives","optional_modes","calculate_mode","structure_build_mode","maximum_model_ticks","sha256"});
    Require(d["kind"]==QJsonValue("timelearner_native_training_job") && Number(d["schema_version"])==1.,"unsupported_training_job");
    Require(Signed(d)==d,"job_digest_mismatch");j.implementation=Text(d["implementation_id"]);
    j.configuration=DecodeConfiguredNativeTraining(Object(d["configuration"]));j.ownerClass=Text(d["owner_class"]);
    Require(j.ownerClass==(j.configuration.model.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"),"training_job_owner_mismatch");
    j.profiles=Array(d["profile_archives"]);Require(j.profiles.size()<=32,"training_profile_budget_exceeded");
    for(const auto& profile:j.profiles)Object(profile);
    const auto modes=Object(d["optional_modes"]);Keys(modes,{"sync_capacitance_trim","post_train_tuning","auto_calibrate_threshold"});
    Require(Number(modes["sync_capacitance_trim"])==0. && modes["post_train_tuning"]==QJsonValue(false) &&
        modes["auto_calibrate_threshold"]==QJsonValue(false),"training_optional_modes_not_yet_supported");
    j.calculateMode=int(Count(d["calculate_mode"],0,1));j.structureMode=int(Count(d["structure_build_mode"],0,1));
    j.maximumTicks=Count(d["maximum_model_ticks"],1,1000000000);return j;
}
QJsonArray Parameters(const std::vector<InputParameters>& values)
{QJsonArray a;for(const auto& p:values)a.append(QJsonObject{{"length",p.length},{"synapses",p.synapses},{"resistance",p.resistance}});return a;}

// Streams every native sample; only one row is formatted in memory at a time.
// No trace is treated as complete merely because its file was closed.
class EvidenceWriter {
    QString directory;
    std::size_t channels,count=0;
    QFile csv;
    bool pending=false;
    std::vector<std::pair<QString,QString>> files;
    void Open()
    {
        Require(!pending,"training_trace_already_open");pending=true;++count;
        const QString stem="raw-trial-"+QString::number(qulonglong(count));csv.setFileName(QDir(directory).filePath(stem+".csv"));
        Require(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly),"training_trace_open_failed");
        QByteArray header="time,stimulus";for(std::size_t i=0;i<channels;++i)header+=",soma"+QByteArray::number(qulonglong(i));header+='\n';
        Require(csv.write(header)==header.size(),"training_trace_write_failed");
    }
public:
    EvidenceWriter(QString directory,std::size_t channels):directory(std::move(directory)),channels(channels){}
    void Prepared(const PreparedVerificationProbe&,const ProbeSpec&){Open();}
    void Sample(const NativeProbeSample& sample)
    {
        Require(pending && sample.potentials.size()==channels,"training_trace_shape_or_order_changed");
        std::ostringstream row;row.imbue(std::locale::classic());row<<std::setprecision(17)<<sample.time<<','<<sample.stimulus;
        for(double value:sample.potentials)row<<','<<value;row<<'\n';const auto bytes=QByteArray::fromStdString(row.str());
        Require(csv.write(bytes)==bytes.size(),"training_trace_write_failed");
    }
    void Observation(const NativeProbeResult& result)
    {
        if(!pending)Open(); // An unarmed cancellation still has a declared empty CSV.
        Require(csv.flush(),"training_trace_flush_failed");csv.close();
        const QString stem="raw-trial-"+QString::number(qulonglong(count));
        Write(directory,stem+".json",EncodeNativeProbeEvidence(result));
        files.emplace_back(stem+".json",stem+".csv");pending=false;
    }
    QJsonArray Finalize(bool stopped)
    {
        Require(!pending,"training_observation_not_closed");QJsonArray records;std::size_t index=0;
        for(const auto& pair:files)
        {
            const QString stem=QString(stopped?"train_stopped_trial_":"train_state_trial_")+QString::number(qulonglong(++index));
            for(const auto& entry:{std::make_pair(pair.first,stem+".json"),std::make_pair(pair.second,stem+".csv")})
            {
                QFile source(QDir(directory).filePath(entry.first));Require(source.rename(QDir(directory).filePath(entry.second)),"training_trace_finalize_failed");
                Require(source.open(QIODevice::ReadOnly),"training_trace_readback_failed");const auto size=source.size();
                QCryptographicHash hash(QCryptographicHash::Sha256);Require(hash.addData(&source),"training_trace_readback_failed");source.close();
                records.append(QJsonObject{{"path",entry.second},{"bytes",double(size)},
                    {"sha256",QString::fromLatin1(hash.result().toHex())}});
            }
        }
        return records;
    }
};
template<class Owner> int Execute(const Job& job,const QString& output)
{
    const auto frequency=job.configuration.model.frequencyHz;
    return WithFreshOwner<Owner>(job.ownerClass,frequency,"TrainingOwner",[&](auto,auto environment,auto model,auto owner) {
        owner->ControllerVersion=2;owner->CalculateMode=job.calculateMode;owner->StructureBuildMode=job.structureMode;
        owner->SyncCapacitanceTrim=0;owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;
        const auto encoded=QJsonDocument(EncodeConfiguredNativeTraining(job.configuration)).toJson(QJsonDocument::Compact).toStdString();
        owner->ControllerConfiguration=encoded;owner->IsNeedToTrain=false;
        Require(owner->ControllerVersion.GetData()==2 && owner->ControllerConfiguration.GetData()==encoded &&
            owner->CalculateMode.GetData()==job.calculateMode && owner->StructureBuildMode.GetData()==job.structureMode,"training_job_property_readback_failed");
        owner->Build();owner->Init();model->Init();model->Reset();
        if(!owner->NativeModelEditFailure().empty())throw std::invalid_argument(owner->NativeModelEditFailure());
        Require(owner->ConfiguredModelInitialized.GetData(),"training_job_model_not_constructed");
        auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto source=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        Require(bool(neuron) && bool(source),"training_job_graph_missing");
        const NmsdkTools::ModelBoundarySources ports{{&source->Output,"burst"}};
        const auto initial=NmsdkTools::IdentifyModel(neuron,ports);Require(initial["valid"]==QJsonValue(true),"training_job_invalid_initial_graph");
        const auto parameters=owner->ReadNativeParameters();Require(parameters.size()==job.configuration.model.inputs.size(),"training_job_initial_dimension_changed");
        for(std::size_t i=0;i<parameters.size();++i)
        {
            const auto& expected=job.configuration.model.inputs[i];const auto& actual=parameters[i];
            Require(actual.length==expected.attachment && actual.synapses==expected.synapses &&
                (!expected.resistance || actual.resistance==*expected.resistance),"training_job_initial_parameters_changed");
        }
        Require(QDir().mkdir(output),"job_output_exists_or_parent_missing");QJsonArray artifacts;
        artifacts.append(Write(output,"job.json",job.document));
        artifacts.append(Write(output,"initial-state.json",Signed({{"kind","native_training_initial_state"},{"schema_version",1},
            {"identity",initial},{"parameters",Parameters(parameters)},{"configuration_sha256",NmsdkTools::CanonicalModelDataSha256(job.document["configuration"])},
            {"training_started",false},{"dynamics_checkpoint",false}})));
        auto evidence=std::make_shared<EvidenceWriter>(output,job.configuration.model.branch?1:parameters.size());
        owner->SetConfiguredNativeEvidenceSinks({[evidence](const auto& p,const auto& s){evidence->Prepared(p,s);},
            [evidence](const auto& sample){evidence->Sample(sample);},[evidence](const auto& result){evidence->Observation(result);}});
        const double begin=environment->GetTime().GetDoubleTime();std::size_t ticks=0;std::string execution="completed";
        owner->IsNeedToTrain=true;
        while(owner->NativeTrainingController().State()!=NativeTrainingState::Finished)
        {
            if(QFileInfo::exists(QDir(output).filePath("cancel.request")))
            {execution="cancelled";owner->IsNeedToTrain=false;break;}
            if(ticks==job.maximumTicks)
            {execution="model_tick_budget_exhausted";owner->IsNeedToTrain=false;break;}
            model->Calculate();environment->IncreaseModelTimeByStep();++ticks;
        }
        const auto& service=owner->NativeTrainingController();const bool stopped=!service.Certificate();
        Require(service.State()==NativeTrainingState::Finished,"training_job_not_at_export_boundary");
        for(const auto& record:evidence->Finalize(stopped))artifacts.append(record);
        owner->SetConfiguredNativeEvidenceSinks({});
        const auto identity=NmsdkTools::IdentifyModel(neuron,ports);Require(identity["valid"]==QJsonValue(true),"training_job_invalid_final_graph");
        const auto revision=identity["sha256"].toString().toStdString();const auto package=owner->ExportNativeLearnedState(job.implementation);
        const QString packageName=stopped?"train_stopped_state.json":"train_learned_state.json";
        artifacts.append(Write(output,stopped?"train_stopped_summary.json":"train_learned_summary.json",
            EncodeNativeTrainingState(service,revision,owner->ReadNativeParameters())));
        artifacts.append(Write(output,packageName,package));
        Write(output,"execution.json",Signed({{"kind","timelearner_native_training_execution"},{"schema_version",1},
            {"execution",QString::fromStdString(execution)},{"job_sha256",job.document["sha256"]},{"attempt_id",QString::fromStdString(job.configuration.runId)},
            {"package_path",packageName},{"package_sha256",package["sha256"]},{"model_revision",package["model_revision"]},
            {"training_outcome",package["training_outcome"]},{"completed_boundary",!stopped},
            {"frequency_hz",double(frequency)},{"model_ticks",double(ticks)},{"model_time_begin",begin},
            {"model_time_end",environment->GetTime().GetDoubleTime()},{"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}));
        return execution=="completed"?0:2;
    },[&](auto storage,auto environment) {
        for(const auto& value:job.profiles)
        {
            const auto profile=Object(value);const auto implementation=Text(Object(profile["metadata"])["implementation_id"]);
            NmsdkTools::PrepareModelArchive(profile,storage,environment,QString::fromStdString(implementation));
        }
    });
}
}
int RunTimeLearnerTrainingJob(const QString& input,const QString& output)
{
    try{const auto job=Read(input);Require(!output.isEmpty(),"job_output_required");
        return job.configuration.model.branch?Execute<NNeuronTimeLearnerBranch>(job,output):Execute<NNeuronTimeLearner>(job,output);}
    catch(const std::exception& error){std::cerr<<"TimeLearner training job: "<<error.what()<<'\n';return 2;}
}
