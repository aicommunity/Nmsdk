#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativePostTuneConfiguration.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include <cstdlib>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
enum class Scenario { Selection, Budget, Cancel, Reset };
QJsonValue Threshold(const QJsonObject& p)
{return p.value("neuron").toObject().value("metadata").toObject().value("calibration").toObject().value("threshold");}
void Save(const std::string& name,const QJsonObject& document)
{
    if(const auto directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(directory)));
        NmsdkWorker::Write(QString::fromLocal8Bit(directory),QString::fromStdString(name)+".json",document);
    }
}
template<class Owner> void FixedPostTune(Scenario scenario)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires published original production job inputs";
    const bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const std::string top=branch?"Branch":"Classic",name=top+"_fixed_"+std::to_string(int(scenario));
    const QDir root(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto source=job["source_recognition"].toObject();const auto implementation=job["implementation_id"].toString().toStdString();
    NativeThresholdGridSpec grid;grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
    grid.maximumCandidates=std::size_t(job["maximum_candidates"].toDouble());
    for(const auto& v:job["thresholds"].toArray())grid.thresholds.push_back(v.toDouble());
    for(const auto& v:job["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(v.toObject()));
    auto spec=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
    if(scenario!=Scenario::Selection || !branch)
    {spec.mode=NativePostTuneControllerMode::KeepDone;spec.canonicalFloor=spec.canonicalLast=0.;spec.resistanceBounds.clear();}
    spec.finalization=NativePostTuneFinalization::KeepFixedThreshold;
    spec.calibration.thresholds.clear();spec.calibration.maximumCandidates=0;
    spec.calibration.confirmation.attemptId+="/"+name;
    if(scenario==Scenario::Budget)spec.maximumRecordedSamples=1;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "FixedPostTuneOwner",[&](auto storage,auto environment,auto model,auto owner) {
        ASSERT_EQ(owner->ImportNativeRecognitionState(source,implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();model->Init();model->Reset();
        ASSERT_EQ(owner->ExportNativeRecognitionState(implementation),source);
        using Transaction=NativePostTuneTransaction<Owner>;
        auto unused=spec;unused.calibration.thresholds={1.};unused.calibration.maximumCandidates=1;
        EXPECT_THROW((Transaction(*owner,unused,implementation)),std::logic_error);
        ASSERT_EQ(owner->ExportNativeRecognitionState(implementation),source);
        Transaction transaction(*owner,spec,implementation);transaction.Advance();
        QJsonObject interrupted;
        if(scenario==Scenario::Cancel)transaction.Cancel("fixed_explicit_cancel");
        else if(scenario==Scenario::Reset)
        {interrupted=owner->ExportNativeRecognitionState(implementation);owner->Reset();transaction.Advance();}
        const auto maximum=std::size_t(job["maximum_model_ticks"].toDouble());std::size_t ticks=0;
        while(!transaction.Done() && ticks<maximum)
        {model->Calculate();environment->IncreaseModelTimeByStep();++ticks;transaction.Advance();}
        if(!transaction.Done())transaction.Cancel("fixed_test_model_tick_budget");
        const auto report=transaction.Report();Save(name+"_transaction",report);
        ASSERT_EQ(report["schema_version"],QJsonValue(2));ASSERT_EQ(report["calibration_status"],QJsonValue("fixed"));
        ASSERT_TRUE(report.contains("recognition_success_confirmed"));EXPECT_FALSE(report["recognition_success_confirmed"].toBool());
        EXPECT_TRUE(report["evaluation_verdict"].isNull());EXPECT_TRUE(transaction.CalibratedPackage().isEmpty());
        EXPECT_TRUE(report["calibration"].toObject().isEmpty());EXPECT_TRUE(report["calibrated_package"].toObject().isEmpty());
        if(scenario!=Scenario::Selection)
        {
            const auto expected=scenario==Scenario::Budget?NativePostTuneTransactionStatus::BudgetExhausted:
                scenario==Scenario::Cancel?NativePostTuneTransactionStatus::Cancelled:NativePostTuneTransactionStatus::RecoveryRequired;
            EXPECT_EQ(transaction.Status(),expected)<<transaction.Reason();EXPECT_TRUE(transaction.FinalPackage().isEmpty());
            EXPECT_TRUE(report["selected_package"].isNull());
            EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),scenario==Scenario::Reset?interrupted:source);
            return;
        }
        ASSERT_EQ(transaction.Status(),NativePostTuneTransactionStatus::WeightsSelected)<<transaction.Reason();
        const auto chosen=transaction.FinalPackage();ASSERT_FALSE(chosen.isEmpty());
        EXPECT_EQ(report["selected_package"],QJsonValue(chosen));EXPECT_FALSE(report["source_restored"].toBool());
        EXPECT_EQ(chosen["kind"],QJsonValue("timelearner_recognition_state"));
        EXPECT_EQ(chosen["source_solo"],source["source_solo"]);EXPECT_EQ(Threshold(chosen),Threshold(source));
        EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),chosen);EXPECT_FALSE(owner->NativeTrainingController().Certificate());
        // These source controls inherit a deliberately silent threshold. A
        // measured weight-selection result must not turn silence into a hit.
        ASSERT_EQ(Threshold(chosen),QJsonValue(1.));
        for(const auto& candidate:report["candidates"].toArray())
            for(const auto& observation:candidate.toObject()["matrix"].toObject()["observations"].toArray())
            {const auto o=observation.toObject();ASSERT_TRUE(o.contains("spike_times"));EXPECT_TRUE(o["spike_times"].toArray().isEmpty());}
        const auto selected=report["candidates"].toArray()[report["selected_index"].toInt()].toObject()["matrix"].toObject();
        ASSERT_EQ(owner->ImportNativeRecognitionState(chosen,implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();owner->Reset();ASSERT_EQ(owner->ExportNativeRecognitionState(implementation),chosen);
        QJsonArray replay;
        for(std::size_t i=0;i<grid.trials.size();++i)
        {
            auto request=grid.trials[i];request.runId=name+"/roundtrip";owner->QueueNativeRecognitionTrial(request);
            std::optional<NativeRecognitionTrialObservation> result;std::size_t count=0;
            while(!result && count<std::size_t(std::ceil(request.duration*2000))+5)
            {model->Calculate();environment->IncreaseModelTimeByStep();++count;result=owner->TakeNativeRecognitionTrialResult();}
            ASSERT_TRUE(result);ASSERT_TRUE(result->valid)<<result->reason;ASSERT_TRUE(result->complete);
            EXPECT_EQ(result->modelBefore,chosen["model_revision"].toString().toStdString());EXPECT_EQ(result->modelAfter,result->modelBefore);
            const auto original=selected["observations"].toArray()[int(i)].toObject()["samples"].toArray();
            ASSERT_EQ(result->samples.size(),std::size_t(original.size()));
            for(std::size_t sample=0;sample<result->samples.size();++sample)
            {
                const auto reference=original[int(sample)].toObject();const auto soma=reference["soma"].toArray();
                EXPECT_DOUBLE_EQ(result->samples[sample].stimulus,reference["stimulus"].toDouble());
                ASSERT_EQ(result->samples[sample].somaPotentials.size(),std::size_t(soma.size()));
                for(std::size_t j=0;j<result->samples[sample].somaPotentials.size();++j)
                    EXPECT_DOUBLE_EQ(result->samples[sample].somaPotentials[j],soma[int(j)].toDouble());
            }
            replay.append(NativeRecognitionTrialJson(*result));
        }
        EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),chosen);
        // Explicit next phase from a completed, reimported weight-only boundary.
        // This call is the first place where threshold calibration is requested.
        grid.confirmation.attemptId+="/"+name+"/later-calibration";
        NativeThresholdCalibrationTransaction<Owner> calibration(*owner,grid,implementation);calibration.Advance();ticks=0;
        while(!calibration.Done() && ticks<maximum)
        {model->Calculate();environment->IncreaseModelTimeByStep();++ticks;calibration.Advance();}
        if(!calibration.Done())calibration.Cancel("fixed_next_phase_model_tick_budget");
        EXPECT_EQ(calibration.Status(),branch?NativeCalibrationTransactionStatus::NonSeparable:NativeCalibrationTransactionStatus::Calibrated)
            <<calibration.Reason();
        Save(name+"_roundtrip",{{"kind","native_fixed_post_tune_roundtrip"},{"schema_version",1},
            {"selected_package",chosen},{"observations",replay},{"subsequent_calibration",calibration.Report()},
            {"package_after",owner->ExportNativeRecognitionState(implementation)},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}});
    });
}
}
TEST(NativeFixedPostTune,ClassicSelectionRoundtripAndLaterCalibration){FixedPostTune<NNeuronTimeLearner>(Scenario::Selection);}
TEST(NativeFixedPostTune,BranchSelectionRoundtripAndLaterCalibration){FixedPostTune<NNeuronTimeLearnerBranch>(Scenario::Selection);}
TEST(NativeFixedPostTune,ClassicBudget){FixedPostTune<NNeuronTimeLearner>(Scenario::Budget);}
TEST(NativeFixedPostTune,BranchBudget){FixedPostTune<NNeuronTimeLearnerBranch>(Scenario::Budget);}
TEST(NativeFixedPostTune,ClassicCancel){FixedPostTune<NNeuronTimeLearner>(Scenario::Cancel);}
TEST(NativeFixedPostTune,BranchCancel){FixedPostTune<NNeuronTimeLearnerBranch>(Scenario::Cancel);}
TEST(NativeFixedPostTune,ClassicResetDoesNotRollback){FixedPostTune<NNeuronTimeLearner>(Scenario::Reset);}
TEST(NativeFixedPostTune,BranchResetDoesNotRollback){FixedPostTune<NNeuronTimeLearnerBranch>(Scenario::Reset);}
