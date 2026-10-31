#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeThresholdCalibrationTransaction.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <cstdlib>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
enum class Interference { ForeignResult,ConsumedResult,SamePackageImport,NormalFlow };

// Uses a saved, measured production source and its predeclared requests. No
// fresh Train and no copied simulator/algorithm body are involved.
template<class Owner> void RecognitionOwnership(Interference interference)
{
    const auto directory=std::getenv("TIMELEARNER_CALIBRATION_OWNERSHIP_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires published native grid source artifacts";
    const std::string top=std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"Branch":"Classic";
    const auto files=QDir(QString::fromLocal8Bit(directory)).entryList(
        {QString::fromStdString(top)+"*_success_grid_transaction.json"},QDir::Files);
    ASSERT_EQ(files.size(),1);
    QFile file(QDir(QString::fromLocal8Bit(directory)).filePath(files.front()));
    ASSERT_TRUE(file.open(QIODevice::ReadOnly));QJsonParseError error;
    const auto document=QJsonDocument::fromJson(file.readAll(),&error);
    ASSERT_EQ(error.error,QJsonParseError::NoError);ASSERT_TRUE(document.isObject());
    const auto record=document.object(),source=record["source_recognition"].toObject();
    const std::string implementation=source["implementation_id"].toString().toStdString();
    NativeThresholdGridSpec spec;spec.thresholds={1.};spec.maximumCandidates=1;
    spec.confirmation.attemptId=top+"/ownership/"+std::to_string(int(interference));
    spec.confirmation.clockId="native-single-clock";spec.confirmation.dataPartitionId="saved-primary-pair";
    for(const auto& value:record["trials"].toArray())
    {
        const auto row=value.toObject();NativeRecognitionTrialRequest q;
        q.trialId=row["trial_id"].toString().toStdString();q.sampleId=row["sample_id"].toString().toStdString();
        q.label=row["label"].toString().toStdString();q.patternHash=row["pattern_hash"].toString().toStdString();
        q.duration=row["duration"].toDouble();q.maximumSamples=std::size_t(row["maximum_samples"].toDouble());
        q.recordThresholdPotential=row["record_threshold_potential"].toBool();
        ASSERT_EQ(row["reset_policy"],QJsonValue("reset_per_trial"));
        const auto pattern=row["pattern_isi"].toArray();q.pattern.Resize(pattern.size(),1);
        for(int i=0;i<pattern.size();++i)q.pattern(i,0)=pattern[i].toDouble();
        spec.trials.push_back(std::move(q));
    }
    ASSERT_EQ(spec.trials.size(),2u);
    if(interference==Interference::NormalFlow)
    {
        spec.thresholds.clear();for(const auto& v:record["thresholds"].toArray())spec.thresholds.push_back(v.toDouble());
        spec.maximumCandidates=spec.thresholds.size();
    }
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();
    model->SetGlobalTimeStep(2000);
    auto owner=dynamic_pointer_cast<Owner>(core.storage->TakeObject(
        top=="Classic"?"NNeuronTimeLearner":"NNeuronTimeLearnerBranch"));ASSERT_TRUE(owner);
    owner->Name="CalibrationOwner";UEPtr<UContainer> component=owner;
    ASSERT_NE(model->AddComponent(component),ForbiddenId);owner->SetGlobalTimeStep(2000);
    const auto imported=owner->ImportNativeRecognitionState(source,implementation);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    owner->Build();owner->Init();model->Init();model->Reset();
    NativeThresholdCalibrationTransaction<Owner> transaction(*owner,spec,implementation);
    transaction.Advance();ASSERT_FALSE(transaction.Done())<<transaction.Reason();
    const auto candidate=owner->ExportNativeRecognitionState(implementation);
    const auto tick=[&]{model->Calculate();core.environment->IncreaseModelTimeByStep();};
    const auto finishTrial=[&]{for(unsigned i=0;i<unsigned(spec.trials.front().duration*2000)+3;++i)tick();};
    std::optional<NativeRecognitionTrialObservation> external;
    std::shared_ptr<const void> retainedContext;
    if(interference==Interference::NormalFlow)
    {
        for(unsigned count=0;!transaction.Done();++count)
        {
            ASSERT_LT(count,20000u);tick();transaction.Advance();
        }
    }
    else if(interference==Interference::ConsumedResult)
    {
        finishTrial();external=owner->TakeNativeRecognitionTrialResult();ASSERT_TRUE(external);
        ASSERT_TRUE(external->valid)<<external->reason;
    }
    else
    {
        owner->CancelNativeRecognitionTrial("external-consumer");
        external=owner->TakeNativeRecognitionTrialResult();ASSERT_TRUE(external);
        if(interference==Interference::ForeignResult)
        {
            auto foreign=spec.trials.front();foreign.runId=top+"/foreign-run";foreign.trialId="foreign-trial";
            owner->QueueNativeRecognitionTrial(foreign);finishTrial();
        }
        else
        {
            const auto lifecycle=owner->ObserveLifecycle();
            // Retain the old token deliberately: merely testing weak.expired
            // would not detect replacement when another observer holds a lock.
            retainedContext=owner->ObserveNativeRecognitionContext().lock();
            const auto replaced=owner->ImportNativeRecognitionState(candidate,implementation);
            ASSERT_EQ(replaced.status,NativeModelBuildStatus::Adopted)<<replaced.reason;
            // Import changes the recognition context without calling owner
            // Build/Reset; a package hash is not an instance/queue lease.
            EXPECT_TRUE(lifecycle.IsCurrent());
        }
    }
    const auto time=core.environment->GetTime().GetTime();transaction.Advance();
    EXPECT_EQ(core.environment->GetTime().GetTime(),time);
    if(interference==Interference::NormalFlow)
    {
        EXPECT_EQ(transaction.Status(),NativeCalibrationTransactionStatus::Calibrated)<<transaction.Reason();
        EXPECT_TRUE(owner->ExportNativeRecognitionState(implementation)==transaction.CalibratedPackage());
    }
    else
    {
        EXPECT_EQ(transaction.Status(),NativeCalibrationTransactionStatus::RecoveryRequired)<<transaction.Reason();
        EXPECT_TRUE(owner->ExportNativeRecognitionState(implementation)==candidate);
    }
    bool foreignPreserved=true;
    if(interference==Interference::ForeignResult)
    {
        const auto foreign=owner->TakeNativeRecognitionTrialResult();foreignPreserved=bool(foreign);
        EXPECT_TRUE(foreign);
        if(foreign){EXPECT_EQ(foreign->request.trialId,"foreign-trial");EXPECT_TRUE(foreign->valid)<<foreign->reason;}
    }
    if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        QJsonObject result{{"kind","native_calibration_ownership_control"},{"schema_version",1},
            {"topology",QString::fromStdString(top)},{"scenario",int(interference)},
            {"transaction",transaction.Report()},{"candidate_before",candidate},
            {"package_after",owner->ExportNativeRecognitionState(implementation)},
            {"foreign_result_preserved",foreignPreserved},{"external_observation",external?QJsonValue(NativeRecognitionTrialJson(*external)):QJsonValue(QJsonValue::Null)},
            {"evaluation_verdict",QJsonValue(QJsonValue::Null)}};
        QFile out(QDir(QString::fromLocal8Bit(output)).filePath(QString::fromStdString(top)+"_ownership_"+QString::number(int(interference))+".json"));
        ASSERT_TRUE(out.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto bytes=QJsonDocument(result).toJson();
        ASSERT_EQ(out.write(bytes),bytes.size());
    }
    transaction.Cancel("test-cleanup");
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}
}
TEST(NativeCalibrationOwnership,ClassicForeignResult){RecognitionOwnership<NNeuronTimeLearner>(Interference::ForeignResult);}
TEST(NativeCalibrationOwnership,BranchForeignResult){RecognitionOwnership<NNeuronTimeLearnerBranch>(Interference::ForeignResult);}
TEST(NativeCalibrationOwnership,ClassicConsumedResult){RecognitionOwnership<NNeuronTimeLearner>(Interference::ConsumedResult);}
TEST(NativeCalibrationOwnership,BranchConsumedResult){RecognitionOwnership<NNeuronTimeLearnerBranch>(Interference::ConsumedResult);}
TEST(NativeCalibrationOwnership,ClassicSamePackageImport){RecognitionOwnership<NNeuronTimeLearner>(Interference::SamePackageImport);}
TEST(NativeCalibrationOwnership,BranchSamePackageImport){RecognitionOwnership<NNeuronTimeLearnerBranch>(Interference::SamePackageImport);}

TEST(NativeCalibrationOwnership,ClassicNormalFlow){RecognitionOwnership<NNeuronTimeLearner>(Interference::NormalFlow);}
TEST(NativeCalibrationOwnership,BranchNormalFlow){RecognitionOwnership<NNeuronTimeLearnerBranch>(Interference::NormalFlow);}
