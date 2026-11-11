#include "TimeLearnerTrainingJob.h"
#include "TimeLearnerJobSupport.h"
#include "TimeLearnerProbeEvidenceWriter.h"
#include "TimeLearnerCompositeArtifacts.h"
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeLearnedState.h"
#include "TimeLearner/BoundedTraining.h"
#include "TimeLearner/NativeCompositeTrainingEvidence.h"
#include "TimeLearner/NativeCalculationPolicy.h"
#include "TimeLearner/NativeLiveFinalization.h"
#include "NNeuronPostTrainTune.h"
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
    std::optional<NativeLiveFinalizationSpec> finalization;
};
Job Read(const QString& path)
{
    Job j;j.document=ReadDocument(path);const auto& d=j.document;
    const auto version=Count(d["schema_version"],1,2);
    std::set<QString> fields{"kind","schema_version","owner_class","implementation_id","configuration",
        "profile_archives","optional_modes","calculate_mode","structure_build_mode","maximum_model_ticks","sha256"};
    if(version==2)fields.insert("finalization_plan");Keys(d,fields);
    Require(d["kind"]==QJsonValue("timelearner_native_training_job"),"unsupported_training_job");
    Require(Signed(d)==d,"job_digest_mismatch");j.implementation=Text(d["implementation_id"]);
    if(version==2) {
        j.finalization=DecodeNativeLiveFinalizationSpec(Object(d["finalization_plan"]));
        Require(j.finalization->implementationId==j.implementation,"training_finalization_implementation_mismatch");
    }
    j.configuration=DecodeConfiguredNativeTraining(Object(d["configuration"]));j.ownerClass=Text(d["owner_class"]);
    Require(j.ownerClass==(j.configuration.model.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"),"training_job_owner_mismatch");
    j.profiles=Array(d["profile_archives"]);Require(j.profiles.size()<=32,"training_profile_budget_exceeded");
    for(const auto& profile:j.profiles)Object(profile);
    const auto modes=Object(d["optional_modes"]);Keys(modes,{"sync_capacitance_trim","post_train_tuning","auto_calibrate_threshold"});
    Require(Number(modes["sync_capacitance_trim"])==0. && modes["post_train_tuning"]==QJsonValue(bool(j.finalization)) &&
        modes["auto_calibrate_threshold"]==QJsonValue(false),"training_optional_modes_not_yet_supported");
    j.calculateMode=int(Count(d["calculate_mode"],0,1));j.structureMode=int(Count(d["structure_build_mode"],0,1));
    j.maximumTicks=Count(d["maximum_model_ticks"],1,1000000000);return j;
}
QJsonArray Parameters(const std::vector<InputParameters>& values)
{QJsonArray a;for(const auto& p:values)a.append(QJsonObject{{"length",p.length},{"synapses",p.synapses},{"resistance",p.resistance}});return a;}

// This driver owns only the outer clock. The learner owns Train and every
// finalization phase, and its native scheduler calculates physical children.
// The captured Solo boundary is read before any recognition import replaces
// the graph/controller; cached Train pointers are never used after conversion.
template<class Owner,class Model,class Environment> int ExecuteLive(const Job& job,const QString& output,
    Owner owner,Model model,Environment environment,std::shared_ptr<EvidenceWriter> evidence,QJsonArray artifacts)
{
    const double begin=environment->GetTime().GetDoubleTime();std::size_t ticks=0;
    std::string execution="completed";QJsonObject solo,summary;
    const auto capture=[&]() {
        const auto live=owner->NativeLiveFinalizationReport();
        const auto boundary=live["boundary"].toObject();
        if(boundary.isEmpty() || !solo.isEmpty())return;
        // Live queues the import for the following tick, so the real finished
        // service and all source evidence are still available at this boundary.
        const auto& service=owner->NativeTrainingController();
        Require(service.State()==NativeTrainingState::Finished && !owner->HasNativeRecognitionState(),
            "training_source_summary_missed_before_import");
        solo=boundary["source_solo"].toObject();Require(!solo.isEmpty(),"training_live_source_missing");
        summary=EncodeNativeTrainingState(service,solo["model_revision"].toString().toStdString(),owner->ReadNativeParameters());
    };
    owner->IsNeedToTrain=true;
    while(!owner->NativeLiveFinalizationDone()) {
        if(QFileInfo::exists(QDir(output).filePath("cancel.request"))) {
            execution="cancelled";owner->CancelNativeLiveFinalization("job_cancel_request");capture();break;
        }
        if(ticks==job.maximumTicks) {
            execution="model_tick_budget_exhausted";owner->CancelNativeLiveFinalization("job_model_tick_budget");capture();break;
        }
        model->Calculate();environment->IncreaseModelTimeByStep();++ticks;capture();
    }
    const auto live=owner->NativeLiveFinalizationReport();
    Require(owner->NativeLiveFinalizationDone(),"training_live_execution_not_terminal");
    const bool started=!live["training_request"].toObject().isEmpty();
    const bool completed=!solo.isEmpty() && solo["kind"]==QJsonValue("timelearner_completed_state");
    if(!solo.isEmpty())Require(live["boundary"].toObject()["source_solo"].toObject()==solo,"training_live_source_changed");
    for(const auto& record:evidence->Finalize(!completed))artifacts.append(record);
    owner->SetConfiguredNativeEvidenceSinks({});
    QJsonValue packagePath(QJsonValue::Null),packageSha(QJsonValue::Null),revision(QJsonValue::Null),outcome(QJsonValue::Null);
    QJsonValue compositeArchive(QJsonValue::Null);
    if(!solo.isEmpty()) {
        compositeArchive=PublishNativeCompositeArchive(output,solo,artifacts);
        const QString name=completed?"train_learned_state.json":"train_stopped_state.json";
        artifacts.append(Write(output,name,solo));
        artifacts.append(Write(output,completed?"train_learned_summary.json":"train_stopped_summary.json",summary));
        packagePath=name;packageSha=solo["sha256"];revision=solo["model_revision"];outcome=solo["training_outcome"];
    } else Require(summary.isEmpty(),"training_live_summary_without_source");
    artifacts.append(Write(output,"finalization.json",live));
    const auto phaseStatus=live["post_tune"].toObject()["status"].toString();
    const bool recognitionAvailable=execution=="completed" && completed && live["status"]==QJsonValue("completed") &&
        (phaseStatus=="weights_selected" || phaseStatus=="calibrated" || phaseStatus=="search_unresolved" || phaseStatus=="budget_exhausted");
    QJsonValue recognitionPath(QJsonValue::Null),recognitionSha(QJsonValue::Null),recognitionRevision(QJsonValue::Null);
    if(recognitionAvailable) {
        Require(owner->HasNativeRecognitionState(),"training_live_final_graph_missing");
        const auto final=owner->ExportNativeRecognitionState(job.implementation);
        artifacts.append(Write(output,"recognition-model.json",final));
        recognitionPath="recognition-model.json";recognitionSha=final["sha256"];recognitionRevision=final["model_revision"];
    }
    if(execution=="completed" && (live["status"]==QJsonValue("failed") || live["status"]==QJsonValue("recovery_required") ||
        live["status"]==QJsonValue("interrupted") || phaseStatus=="failed" || phaseStatus=="recovery_required"))execution="finalization_failed";
    // Keep the exact external request as an artifact, without rewriting it.
    const QString cancelPath=QDir(output).filePath("cancel.request");
    if(QFileInfo::exists(cancelPath)) {
        QFile file(cancelPath);Require(file.open(QIODevice::ReadOnly) && file.size()<=65536,"training_cancel_request_unreadable");
        const auto bytes=file.readAll();artifacts.append(QJsonObject{{"path","cancel.request"},{"bytes",double(bytes.size())},
            {"sha256",QString::fromLatin1(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex())}});
    }
    Write(output,"execution.json",WrapConfiguredNativeExecution(job.configuration,{{"kind","timelearner_native_training_execution"},{"schema_version",2},
        {"execution",QString::fromStdString(execution)},{"job_sha256",job.document["sha256"]},{"attempt_id",QString::fromStdString(job.configuration.runId)},
        {"training_started",started},{"package_path",packagePath},{"package_sha256",packageSha},{"model_revision",revision},
        {"training_outcome",outcome},{"completed_boundary",completed},{"finalization_path","finalization.json"},{"finalization_sha256",live["sha256"]},
        {"finalization_status",live["status"]},{"recognition_available",recognitionAvailable},{"recognition_package_path",recognitionPath},
        {"recognition_package_sha256",recognitionSha},{"recognition_model_revision",recognitionRevision},
        {"frequency_hz",double(job.configuration.model.frequencyHz)},{"model_ticks",double(ticks)},{"model_time_begin",begin},
        {"model_time_end",environment->GetTime().GetDoubleTime()},{"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}},
        solo,compositeArchive,revision,evidence->NativeTrials(),evidence->SampledFrames()));
    return execution=="completed"?0:2;
}
template<class Owner> int Execute(const Job& job,const QString& output,const bool preflight=false)
{
    const auto frequency=job.configuration.model.frequencyHz;
    return WithFreshOwner<Owner>(job.ownerClass,frequency,"TrainingOwner",[&](auto,auto environment,auto model,auto owner) {
        const double preparationBegin=environment->GetTime().GetDoubleTime();
        owner->ControllerVersion=2;owner->CalculateMode=job.calculateMode;owner->StructureBuildMode=job.structureMode;
        owner->SyncCapacitanceTrim=0;owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;
        if(job.finalization) {
            const auto& spec=job.finalization->postTune;
            owner->EnablePostTrainTuning=true;owner->EnablePostTrainMidThreshold=spec.finalization==NativePostTuneFinalization::Calibrate;
            int mode=PostTrainTune::kPostTipOff;
            switch(spec.mode) {
            case NativePostTuneControllerMode::Off:break;
            case NativePostTuneControllerMode::KeepDone:mode=PostTrainTune::kPostTipKeepDone;break;
            case NativePostTuneControllerMode::CanonRmin:mode=PostTrainTune::kPostTipCanonRmin;break;
            case NativePostTuneControllerMode::FlatLastR:mode=PostTrainTune::kPostTipFlatLastR;break;
            case NativePostTuneControllerMode::SearchSynthetic:mode=PostTrainTune::kPostTipSearchSynthetic;break;
            }
            owner->PostTrainTipResistanceMode=mode;owner->PostTrainMidMetric=int(spec.metric);
            owner->UseCandidateMidOnNonSeparableTest=false;
            owner->TipResistanceCanonFloor=spec.canonicalFloor;owner->TipResistanceCanonLast=spec.canonicalLast;
            owner->PostTrainTipSearchIters=int(spec.searchPasses);
            if(spec.weightProbeThreshold)owner->PostTrainSilentThreshold=*spec.weightProbeThreshold;
            owner->ConfigureNativeFinalization(*job.finalization);
        }
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
        auto plan=MakeConfiguredNativeTrainingPlan(job.configuration);
        plan.search.initialModelRevision=initial["sha256"].toString().toStdString();
        if(plan.protocol.schemaVersion==5)ValidateCandidateWindowTrainingConfiguration(plan.protocol,plan.search,parameters);
        else ValidateBoundedTrainingInputs(plan.protocol,plan.search,parameters);
        NMSDK::TimeLearner::RequireNativeCalculationSchedule(*owner);
        const auto integration=AssessNativeIntegration(neuron,source->Amplitude.GetData());
        Require(integration.valid,integration.reason.c_str());
        const auto& control=owner->NativeTrainingController();
        Require(environment->GetTime().GetDoubleTime()==preparationBegin &&
            control.State()==NativeTrainingState::Idle && control.IssuedReferenceProbes()==0 &&
            control.ObservedPackets().empty() && !control.Certificate() && !control.References() &&
            owner->NativeProbeState()==NativeProbeStatus::Idle && !owner->IsNeedToTrain.GetData(),
            "training_preparation_started_calculation");
        Require(NmsdkTools::IdentifyModel(neuron,ports)==initial,"training_preparation_model_changed");
        Require(QDir().mkdir(output),"job_output_exists_or_parent_missing");QJsonArray artifacts;
        artifacts.append(Write(output,"job.json",job.document));
        artifacts.append(Write(output,"initial-state.json",Signed({{"kind","native_training_initial_state"},{"schema_version",1},
            {"identity",initial},{"parameters",Parameters(parameters)},{"configuration_sha256",NmsdkTools::CanonicalModelDataSha256(job.document["configuration"])},
            {"training_started",false},{"dynamics_checkpoint",false}})));
        if(preflight)
        {
            QJsonArray channels;
            for(const auto& channel:integration.channels)channels.append(QJsonObject{
                {"path",QString::fromStdString(channel.path)},
                {"maximum_conductance",channel.maximumConductance},{"maximum_step_gain",channel.maximumStepGain}});
            Write(output,"execution.json",WrapConfiguredNativeExecution(job.configuration,{{"kind","timelearner_native_preflight_execution"},{"schema_version",1},
                {"execution","completed"},{"job_sha256",job.document["sha256"]},{"model_revision",initial["sha256"]},
                {"model_ticks",0},{"frequency_hz",double(frequency)},{"model_time_begin",preparationBegin},
                {"model_time_end",environment->GetTime().GetDoubleTime()},{"training_started",false},
                {"controller_state",NativeTrainingStateName(control.State())},{"reference_probes",0},{"observed_probes",0},
                {"integration",QJsonObject{{"valid",true},{"reason",""},{"channels",channels}}},
                {"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}},
                {},QJsonValue(QJsonValue::Null),initial["sha256"],0,0,true));
            return 0;
        }
        auto evidence=std::make_shared<EvidenceWriter>(output,job.configuration.model.branch?1:parameters.size());
        owner->SetConfiguredNativeEvidenceSinks({[evidence](const auto& p,const auto& s){evidence->Prepared(p,s);},
            [evidence](const auto& sample){evidence->Sample(sample);},[evidence](const auto& result){evidence->Observation(result);}});
        if(job.finalization)return ExecuteLive(job,output,owner,model,environment,evidence,artifacts);
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
        Require(service.State()==NativeTrainingState::Finished ||
            (job.configuration.composite && service.CompositeSourceBinding().isEmpty()),"training_job_not_at_export_boundary");
        for(const auto& record:evidence->Finalize(stopped))artifacts.append(record);
        owner->SetConfiguredNativeEvidenceSinks({});
        // Editors may replace child instances. Capture the ACTUAL final roots.
        auto actualNeuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto actualSource=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        Require(actualNeuron && actualSource,"training_job_final_graph_missing");
        const auto identity=NmsdkTools::IdentifyModel(actualNeuron,{{&actualSource->Output,"burst"}});
        Require(identity["valid"]==QJsonValue(true),"training_job_invalid_final_graph");
        const auto revision=identity["sha256"].toString().toStdString();
        if(job.configuration.composite && service.CompositeSourceBinding().isEmpty()) {
            // Failed/cancelled before owned capture: no invented package/archive.
            const auto failedOutcome=service.State()==NativeTrainingState::Finished?service.Outcome():
                (execution=="cancelled"?TrainingStatus::ExternalStop:TrainingStatus::BudgetExhausted);
            const auto failureReason=service.Reason().empty()?execution+"_before_owned_start":service.Reason();
            artifacts.append(Write(output,"training-start-failure.json",Signed({{"kind","timelearner_native_training_start_failure"},
                {"schema_version",1},{"outcome",TrainingStatusName(failedOutcome)},{"reason",QString::fromStdString(failureReason)},
                {"model_revision",identity["sha256"]},{"dynamic_checkpoint",false},{"source_origin",QJsonValue(QJsonValue::Null)},
                {"measurement_archive",QJsonValue(QJsonValue::Null)},{"certificate",QJsonValue(QJsonValue::Null)},{"contains_evaluation_verdict",false}})));
            Write(output,"execution.json",WrapConfiguredNativeExecution(job.configuration,{{"kind","timelearner_native_training_execution"},{"schema_version",1},
                {"execution","training_start_failed"},{"job_sha256",job.document["sha256"]},{"attempt_id",QString::fromStdString(job.configuration.runId)},
                {"package_path",QJsonValue(QJsonValue::Null)},{"package_sha256",QJsonValue(QJsonValue::Null)},{"model_revision",identity["sha256"]},
                {"training_outcome",TrainingStatusName(failedOutcome)},{"completed_boundary",false},
                {"frequency_hz",double(frequency)},{"model_ticks",double(ticks)},{"model_time_begin",begin},
                {"model_time_end",environment->GetTime().GetDoubleTime()},{"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}},
                {},QJsonValue(QJsonValue::Null),identity["sha256"],evidence->NativeTrials(),evidence->SampledFrames()));return 2;
        }
        const auto package=owner->ExportNativeLearnedState(job.implementation);
        const auto compositeArchive=PublishNativeCompositeArchive(output,package,artifacts);
        const QString packageName=stopped?"train_stopped_state.json":"train_learned_state.json";
        artifacts.append(Write(output,stopped?"train_stopped_summary.json":"train_learned_summary.json",
            EncodeNativeTrainingState(service,revision,owner->ReadNativeParameters())));
        artifacts.append(Write(output,packageName,package));
        Write(output,"execution.json",WrapConfiguredNativeExecution(job.configuration,{{"kind","timelearner_native_training_execution"},{"schema_version",1},
            {"execution",QString::fromStdString(execution)},{"job_sha256",job.document["sha256"]},{"attempt_id",QString::fromStdString(job.configuration.runId)},
            {"package_path",packageName},{"package_sha256",package["sha256"]},{"model_revision",package["model_revision"]},
            {"training_outcome",package["training_outcome"]},{"completed_boundary",!stopped},
            {"frequency_hz",double(frequency)},{"model_ticks",double(ticks)},{"model_time_begin",begin},
            {"model_time_end",environment->GetTime().GetDoubleTime()},{"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}},
            package,compositeArchive,package["model_revision"],evidence->NativeTrials(),evidence->SampledFrames()));
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
int RunTimeLearnerPreflightJob(const QString& input,const QString& output)
{
    try{const auto job=Read(input);Require(!output.isEmpty(),"job_output_required");
        return job.configuration.model.branch?Execute<NNeuronTimeLearnerBranch>(job,output,true):
            Execute<NNeuronTimeLearner>(job,output,true);}
    catch(const std::exception& error){std::cerr<<"TimeLearner preflight job: "<<error.what()<<'\n';return 2;}
}
