#include "TimeLearnerCalibrationJob.h"
#include "TimeLearnerJobSupport.h"
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeThresholdCalibrationTransaction.h"
#include "../../../Rdk/Deploy/Include/rdk_cpp_init.h"
#include <QCryptographicHash>
#include <QFile>
#include <QFileInfo>
#include <QDir>
#include <QJsonDocument>
#include <iostream>
#include <cmath>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
using namespace NmsdkWorker;
struct Job {
    QJsonObject document,source;
    NativeThresholdGridSpec grid;
    std::string implementation,ownerClass;
    unsigned frequency=0;
    std::size_t maximumTicks=0;
};
Job Read(const QString& path)
{
    QFile file(path);Require(file.open(QIODevice::ReadOnly),"job_input_unreadable");
    Require(file.size()>0 && file.size()<=256*1024*1024,"job_input_size_out_of_range");
    Job j;j.document=ParseStrictNativeJsonObject(file.readAll().toStdString(),256*1024*1024);
    const auto& d=j.document;
    const std::set<QString> keys{"kind","schema_version","owner_class","implementation_id","frequency_hz",
        "maximum_model_ticks","source_recognition","thresholds","maximum_candidates","specification","trials","sha256"};
    Require(d.size()==int(keys.size()),"job_field_set_mismatch");for(const auto& key:keys)Require(d.contains(key),"job_missing_field");
    Require(d["kind"]==QJsonValue("timelearner_native_calibration_job") &&
        Number(d["schema_version"])==1.,"unsupported_calibration_job");
    Require(Signed(d)==d,"job_digest_mismatch");
    j.ownerClass=Text(d["owner_class"]);j.implementation=Text(d["implementation_id"]);
    Require(j.ownerClass=="NNeuronTimeLearner" || j.ownerClass=="NNeuronTimeLearnerBranch","unsupported_calibration_job_owner");
    j.frequency=unsigned(Count(d["frequency_hz"],1,1000000000));
    j.maximumTicks=Count(d["maximum_model_ticks"],1,1000000000);
    j.source=Object(d["source_recognition"]);
    j.grid.maximumCandidates=Count(d["maximum_candidates"],1,256);
    j.grid.confirmation=DecodeNativeThresholdConfirmationSpec(Object(d["specification"]));
    for(const auto& value:Array(d["thresholds"]))j.grid.thresholds.push_back(Number(value));
    for(const auto& value:Array(d["trials"]))j.grid.trials.push_back(DecodeNativeCalibrationRequest(Object(value)));
    return j;
}
template<class Owner> int Execute(const Job& job,const QString& output)
{
    return WithFreshOwner<Owner>(job.ownerClass,job.frequency,"CalibrationOwner",[&](auto storage,auto environment,auto model,auto owner) {
    const auto imported=owner->ImportNativeRecognitionState(job.source,job.implementation);
    if(imported.status!=NativeModelBuildStatus::Adopted)throw std::invalid_argument("job_import_failed:"+imported.reason);
    Require(owner->GetTimeStep()==job.frequency,"job_import_frequency_mismatch");
    owner->Build();owner->Init();model->Init();model->Reset();
    Require(owner->ExportNativeRecognitionState(job.implementation)==job.source,"job_source_effective_readback_changed");
    NativeThresholdCalibrationTransaction<Owner> transaction(*owner,job.grid,job.implementation);
    // Validate the effective model and entire declared design before reserving output.
    Require(QDir().mkdir(output),"job_output_exists_or_parent_missing");
    QJsonArray artifacts;artifacts.append(Write(output,"job.json",job.document));
    const double begin=environment->GetTime().GetDoubleTime();std::size_t ticks=0;
    std::string execution="completed";
    transaction.Advance();
    while(!transaction.Done())
    {
        if(QFileInfo::exists(QDir(output).filePath("cancel.request")))
        {execution="cancelled";transaction.Cancel("worker_cancel_requested");break;}
        if(ticks==job.maximumTicks)
        {execution="model_tick_budget_exhausted";transaction.Cancel("worker_model_tick_budget_exhausted");break;}
        // This is the native outer scheduler, once per tick. The controller
        // neither calculates children nor moves the physical clock itself.
        model->Calculate();environment->IncreaseModelTimeByStep();++ticks;transaction.Advance();
    }
    const auto report=transaction.Report();const auto after=owner->ExportNativeRecognitionState(job.implementation);
    Require(transaction.Status()!=NativeCalibrationTransactionStatus::Calibrated || after==transaction.CalibratedPackage(),
        "job_calibrated_effective_readback_changed");
    artifacts.append(Write(output,"transaction.json",report));artifacts.append(Write(output,"model.json",after));
    QJsonObject result{{"kind","timelearner_native_calibration_execution"},{"schema_version",1},
        {"execution",QString::fromStdString(execution)},{"job_sha256",job.document["sha256"]},
        {"attempt_id",QString::fromStdString(job.grid.confirmation.attemptId)},
        {"source_recognition_sha256",job.source["sha256"]},{"model_sha256",after["sha256"]},
        {"model_revision",after["model_revision"]},{"transaction_sha256",report["sha256"]},
        {"calibration_status",report["status"]},{"frequency_hz",double(job.frequency)},
        {"model_ticks",double(ticks)},{"model_time_begin",begin},{"model_time_end",environment->GetTime().GetDoubleTime()},
        {"artifacts",artifacts},{"runtime_provenance_external",true},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}};
    Write(output,"execution.json",Signed(result));
    const auto status=transaction.Status();
    return execution=="completed" && (status==NativeCalibrationTransactionStatus::Calibrated ||
        status==NativeCalibrationTransactionStatus::NonSeparable || status==NativeCalibrationTransactionStatus::BudgetExhausted)?0:2;
    });
}
}
int RunTimeLearnerCalibrationJob(const QString& input,const QString& output)
{
    try
    {
        Require(!input.isEmpty() && !output.isEmpty(),"job_input_and_output_required");const auto job=Read(input);
        return job.ownerClass=="NNeuronTimeLearner"?Execute<NNeuronTimeLearner>(job,output):Execute<NNeuronTimeLearnerBranch>(job,output);
    }
    catch(const std::exception& error){std::cerr<<"TimeLearner calibration job: "<<error.what()<<'\n';return 2;}
}
