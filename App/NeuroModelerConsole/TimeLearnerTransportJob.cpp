#include "TimeLearnerTransportJob.h"
#include "TimeLearnerJobSupport.h"
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeCalibratedState.h"
#include "TimeLearner/NativeRecognitionObservationValidation.h"
#include <iostream>
#include <algorithm>
#include <limits>
#include <numeric>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
using namespace NmsdkWorker;
void Header(const QJsonObject& d,const char* kind)
{Require(d["kind"]==QJsonValue(kind) && Number(d["schema_version"])==1.,"unsupported_transport_job");Require(Signed(d)==d,"job_digest_mismatch");}
struct EvaluationJob {
    QJsonObject document,source,criterion;
    std::string implementation,ownerClass,runId,coverage;
    std::vector<NativeRecognitionTrialRequest> trials;
    unsigned frequency=0;std::size_t maximumTicks=0;
};
EvaluationJob ReadEvaluation(const QString& path)
{
    EvaluationJob j;j.document=ReadDocument(path);const auto& d=j.document;
    Keys(d,{"kind","schema_version","owner_class","implementation_id","source_recognition","maximum_model_ticks",
        "run_id","coverage_policy","criterion","trials","sha256"});Header(d,"timelearner_native_evaluation_job");
    j.source=Object(d["source_recognition"]);j.implementation=Text(d["implementation_id"]);j.ownerClass=Text(d["owner_class"]);
    j.runId=Text(d["run_id"]);j.coverage=Text(d["coverage_policy"]);
    Require(j.coverage=="per_trial_windows" || j.coverage=="continuous_native_stream","unknown_evaluation_coverage");
    const auto kind=j.source["kind"];
    Require(kind==QJsonValue("timelearner_recognition_state") || kind==QJsonValue("timelearner_calibrated_recognition_state"),"evaluation_requires_frozen_model_not_candidate");
    const auto context=kind==QJsonValue("timelearner_recognition_state")?j.source:Object(Object(j.source["source_candidate"])["source_recognition"]);
    const auto solo=Object(context["source_solo"]),configuration=Object(solo["configuration"]),model=Object(configuration["model"]);
    Require(model["branch"].isBool(),"invalid_evaluation_topology");
    Require(j.ownerClass==(model["branch"].toBool()?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"),"evaluation_owner_mismatch");
    j.frequency=unsigned(Count(model["frequency_hz"],1,1000000000));j.maximumTicks=Count(d["maximum_model_ticks"],1,1000000000);
    j.criterion=Object(d["criterion"]);
    Keys(j.criterion,{"id","anchor","begin_offset","end_offset","reject_target_outside_window"});
    Require(j.criterion["id"]==QJsonValue("post_anchor_target_whole_window_foil_v1"),"unknown_evaluation_criterion");
    auto window=j.criterion;window.remove("id");
    const auto specification=DecodeNativeThresholdConfirmationSpec({{"protocol","historical_same_matrix"},
        {"data_partition_id","evaluation-declaration-only"},{"attempt_id",QString::fromStdString(j.runId)},
        {"clock_id","native-single-clock"},{"criterion",window}});
    ValidateCalibrationResponseWindow(specification.window);
    const auto target=Text(Object(solo["protocol"])["pattern_hash"]);std::set<std::string> ids;
    const auto requests=Array(d["trials"]);Require(!requests.isEmpty() && requests.size()<=10000,"invalid_evaluation_trial_count");
    for(const auto& value:requests)
    {
        auto q=DecodeNativeCalibrationRequest(Object(value));
        Require(q.runId==j.runId && ids.insert(q.trialId).second && (q.label=="target" || q.label=="foil") &&
            q.pattern.GetRows()==Array(context["recognition_inputs"]).size(),"evaluation_trial_scope_or_shape_changed");
        QJsonArray isi;double span=0.;for(int i=0;i<q.pattern.GetRows();++i){const auto v=q.pattern(i,0);Require(v>=0.,"invalid_evaluation_pattern");span+=v;isi.append(v);}
        Require(q.patternHash==NmsdkTools::CanonicalModelDataSha256(isi).toStdString() &&
            ((q.label=="target")== (q.patternHash==target)),"evaluation_pattern_identity_mismatch");
        const double ticks=q.duration*j.frequency;
        Require(q.duration>span && std::isfinite(ticks) && std::abs(ticks-std::round(ticks))<=32*std::numeric_limits<double>::epsilon()*std::max(1.,ticks) &&
            ticks+1<=double(q.maximumSamples),"evaluation_window_or_sample_budget_invalid");
        j.trials.push_back(std::move(q));
    }
    return j;
}
template<class Owner> int Evaluate(const EvaluationJob& job,const QString& output)
{
    return WithFreshOwner<Owner>(job.ownerClass,job.frequency,"EvaluationOwner",[&](auto,auto environment,auto model,auto owner) {
        const auto imported=owner->ImportNativeRecognitionState(job.source,job.implementation);
        if(imported.status!=NativeModelBuildStatus::Adopted)throw std::invalid_argument(imported.reason);
        owner->Build();owner->Init();model->Init();model->Reset();
        Require(owner->ExportNativeRecognitionState(job.implementation)==job.source,"evaluation_initial_model_changed");
        Require(QDir().mkdir(output),"job_output_exists_or_parent_missing");QJsonArray artifacts,design;
        artifacts.append(Write(output,"job.json",job.document));artifacts.append(Write(output,"model.json",job.source));
        const double begin=environment->GetTime().GetDoubleTime();std::size_t ticks=0,index=0;std::string execution="completed";
        for(const auto& request:job.trials)
        {
            Require(owner->ExportNativeRecognitionState(job.implementation)==job.source,"evaluation_frozen_model_changed");
            owner->QueueNativeRecognitionTrial(request);std::optional<NativeRecognitionTrialObservation> result;
            while(!result)
            {
                if(QFileInfo::exists(QDir(output).filePath("cancel.request")) || ticks==job.maximumTicks)
                {
                    execution=ticks==job.maximumTicks?"model_tick_budget_exhausted":"cancelled";
                    owner->CancelNativeRecognitionTrial(execution);result=owner->TakeNativeRecognitionTrialResult();break;
                }
                model->Calculate();environment->IncreaseModelTimeByStep();++ticks;result=owner->TakeNativeRecognitionTrialResult();
            }
            Require(bool(result),"evaluation_result_missing");
            const QString filename="trial-"+QString::number(qulonglong(index))+".json";
            artifacts.append(Write(output,filename,NativeRecognitionTrialJson(*result)));
            auto trial=EncodeNativeCalibrationRequest(request);
            for(const auto& key:{"run_id","pattern_isi","maximum_samples","record_threshold_potential"})trial.remove(key);
            trial["presentation_index"]=double(index++);trial["observation"]=filename;design.append(trial);
            Require(owner->ExportNativeRecognitionState(job.implementation)==job.source,"evaluation_frozen_model_changed");
            if(execution!="completed")break;
            ValidateNativeRecognitionObservation(request,*result);
        }
        // Expected design is never shrunk to the observed prefix on interruption.
        for(std::size_t i=index;i<job.trials.size();++i)
        {
            auto trial=EncodeNativeCalibrationRequest(job.trials[i]);
            for(const auto& key:{"run_id","pattern_isi","maximum_samples","record_threshold_potential"})trial.remove(key);
            trial["presentation_index"]=double(i);trial["observation"]="trial-"+QString::number(qulonglong(i))+".json";design.append(trial);
        }
        artifacts.append(Write(output,"evaluation.json",{{"kind","timelearner_recognition_evaluation_spec"},{"schema_version",1},
            {"run_id",QString::fromStdString(job.runId)},{"model_revision",job.source["model_revision"]},
            {"coverage_policy",QString::fromStdString(job.coverage)},{"criterion",job.criterion},{"trials",design}}));
        artifacts.append(Write(output,"model-after.json",owner->ExportNativeRecognitionState(job.implementation)));
        Write(output,"execution.json",Signed({{"kind","timelearner_native_evaluation_execution"},{"schema_version",1},
            {"execution",QString::fromStdString(execution)},{"job_sha256",job.document["sha256"]},{"run_id",QString::fromStdString(job.runId)},
            {"model_sha256",job.source["sha256"]},{"model_revision",job.source["model_revision"]},
            {"observed_trials",double(index)},{"expected_trials",double(job.trials.size())},{"frequency_hz",double(job.frequency)},
            {"model_ticks",double(ticks)},{"model_time_begin",begin},{"model_time_end",environment->GetTime().GetDoubleTime()},
            {"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}));
        return execution=="completed"?0:2;
    });
}
}
int RunTimeLearnerEvaluationJob(const QString& input,const QString& output)
{
    try{const auto job=ReadEvaluation(input);Require(!output.isEmpty(),"job_output_required");
        return job.ownerClass=="NNeuronTimeLearner"?Evaluate<NNeuronTimeLearner>(job,output):Evaluate<NNeuronTimeLearnerBranch>(job,output);}
    catch(const std::exception& error){std::cerr<<"TimeLearner evaluation job: "<<error.what()<<'\n';return 2;}
}
int RunTimeLearnerExportJob(const QString& input,const QString& output)
{
    try
    {
        const auto d=ReadDocument(input);Keys(d,{"kind","schema_version","implementation_id","source_solo","conversion_spec","sha256"});
        Header(d,"timelearner_native_recognition_export_job");const auto solo=Object(d["source_solo"]);
        const auto implementation=Text(d["implementation_id"]);const auto conversion=DecodeNativeRecognitionSpec(Object(d["conversion_spec"]));
        const auto frequency=unsigned(Count(Object(Object(solo["configuration"])["model"])["frequency_hz"],1,1000000000));
        return WithFreshModel(frequency,[&](auto storage,auto environment,auto) {
            const auto result=ConvertNativeSoloToRecognition(solo,conversion,storage,environment,implementation);
            Require(QDir().mkdir(output),"job_output_exists_or_parent_missing");QJsonArray artifacts;
            artifacts.append(Write(output,"job.json",d));artifacts.append(Write(output,"model.json",result));
            Write(output,"execution.json",Signed({{"kind","timelearner_native_conversion_execution"},{"schema_version",1},
                {"execution","completed"},{"job_sha256",d["sha256"]},{"source_solo_sha256",solo["sha256"]},
                {"model_sha256",result["sha256"]},{"model_revision",result["model_revision"]},
                {"model_ticks",0},{"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}));return 0;
        });
    }
    catch(const std::exception& error){std::cerr<<"TimeLearner export job: "<<error.what()<<'\n';return 2;}
}
