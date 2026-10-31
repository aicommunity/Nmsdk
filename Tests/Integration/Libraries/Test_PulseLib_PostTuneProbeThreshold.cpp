#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativePostTuneConfiguration.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include <cstdlib>
#include <limits>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
enum class Scenario { Complete, FinalBudget, FinalCancel, FinalReset };
QJsonValue Threshold(const QJsonObject& p)
{return p.value("neuron").toObject().value("metadata").toObject().value("calibration").toObject().value("threshold");}

template<class Owner> void ProbeThreshold(Scenario scenario)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires original portable source/model primaries";
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const std::string name=std::string(branch?"Branch":"Classic")+"_probe_threshold_"+std::to_string(int(scenario));
    const QDir root(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto source=job["source_recognition"].toObject();
    const auto implementation=job["implementation_id"].toString().toStdString();
    NativeThresholdGridSpec grid;grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
    for(const auto& v:job["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(v.toObject()));
    auto spec=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
    spec.mode=NativePostTuneControllerMode::KeepDone;spec.canonicalFloor=spec.canonicalLast=0.;spec.resistanceBounds.clear();
    spec.finalization=NativePostTuneFinalization::KeepFixedThreshold;
    spec.weightProbeThreshold=2.;spec.calibration.confirmation.attemptId+="/"+name;
    if(scenario==Scenario::FinalBudget)
    {
        spec.maximumRecordedSamples=0;
        for(const auto& q:grid.trials)spec.maximumRecordedSamples+=std::min(q.maximumSamples,std::size_t(std::ceil(q.duration*2000))+2);
    }
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    const auto exercise=[&](auto storage,auto environment,auto model,auto owner) {
        ASSERT_EQ(owner->ImportNativeRecognitionState(source,implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();model->Init();model->Reset();
        ASSERT_EQ(Threshold(source),QJsonValue(1.));
        using Transaction=NativePostTuneTransaction<Owner>;
        auto invalid=spec;invalid.weightProbeThreshold=std::numeric_limits<double>::quiet_NaN();
        EXPECT_THROW((Transaction(*owner,invalid,implementation)),std::logic_error);
        EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),source);
        EXPECT_THROW(EncodeNativePostTuneControls(spec),std::invalid_argument);
        EXPECT_THROW(EncodeNativePostTuneControlsV2(spec),std::invalid_argument);
        Transaction transaction(*owner,spec,implementation);
        struct DetachBeforeTeardown {
            Transaction& transaction;
            ~DetachBeforeTeardown(){transaction.InterruptOwnerLifecycle("fixture_early_exit");}
        } detach{transaction};
        transaction.Advance();
        const auto maximum=std::size_t(job["maximum_model_ticks"].toDouble());std::size_t ticks=0;
        while(!transaction.Done() && !transaction.IsVerifyingFinalModel() && ticks<maximum)
        {model->Calculate();environment->IncreaseModelTimeByStep();++ticks;transaction.Advance();}
        ASSERT_TRUE(transaction.IsVerifyingFinalModel())<<transaction.Reason();
        ASSERT_FALSE(transaction.Done());EXPECT_TRUE(transaction.FinalPackage().isEmpty());
        const auto selected=owner->ExportNativeRecognitionState(implementation);
        ASSERT_EQ(Threshold(selected),Threshold(source));
        ASSERT_EQ(selected["kind"],QJsonValue("timelearner_recognition_state"));
        // Before any final-model response, selection is not a completed result.
        EXPECT_FALSE(transaction.Report()["final_threshold_responses_observed"].toBool());
        transaction.Advance(); // Arm the final-model trial (or hit its budget).
        if(scenario==Scenario::FinalCancel)
        {
            ASSERT_FALSE(owner->IsNativeRecognitionTrialIdle());
            transaction.Cancel("cancel_final_model_verification");
        }
        else if(scenario==Scenario::FinalReset)
        {
            ASSERT_FALSE(owner->IsNativeRecognitionTrialIdle());
            const auto lifecycle=owner->ObserveLifecycle();
            transaction.InterruptOwnerLifecycle("reset_final_model_verification");
            EXPECT_TRUE(lifecycle.IsCurrent());
            EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),selected);
            owner->Reset();transaction.Advance();transaction.Cancel("late_cancel");
        }
        while(!transaction.Done() && ticks<maximum)
        {model->Calculate();environment->IncreaseModelTimeByStep();++ticks;transaction.Advance();}
        if(!transaction.Done())transaction.Cancel("test_tick_budget");
        const auto report=transaction.Report();
        if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",report);
        }
        ASSERT_EQ(report["schema_version"],QJsonValue(3));
        ASSERT_EQ(report["weight_probe_threshold"],QJsonValue(2.));
        ASSERT_EQ(report["weight_measurement_candidates"].toArray().size(),1);
        const auto measured=report["weight_measurement_candidates"].toArray()[0].toObject();
        EXPECT_EQ(Threshold(measured),QJsonValue(2.));
        EXPECT_EQ(measured["source_recognition"],QJsonValue(selected));
        EXPECT_NE(measured["model_revision"],selected["model_revision"]);
        const auto candidates=report["candidates"].toArray();ASSERT_EQ(candidates.size(),1);
        EXPECT_EQ(candidates[0].toObject()["candidate"],QJsonValue(selected));
        for(const auto& v:candidates[0].toObject()["matrix"].toObject()["observations"].toArray())
        {
            const auto o=v.toObject();EXPECT_EQ(o["model_before"],measured["model_revision"]);
            EXPECT_EQ(o["model_after"],measured["model_revision"]);
        }
        EXPECT_FALSE(report["recognition_success_confirmed"].toBool());
        EXPECT_TRUE(report["evaluation_verdict"].isNull());EXPECT_TRUE(transaction.CalibratedPackage().isEmpty());
        if(scenario!=Scenario::Complete)
        {
            EXPECT_EQ(transaction.Status(),scenario==Scenario::FinalBudget?NativePostTuneTransactionStatus::BudgetExhausted:
                scenario==Scenario::FinalCancel?NativePostTuneTransactionStatus::Cancelled:NativePostTuneTransactionStatus::RecoveryRequired)
                <<transaction.Reason();
            EXPECT_FALSE(report["final_threshold_responses_observed"].toBool());
            EXPECT_TRUE(transaction.FinalPackage().isEmpty());
            EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),scenario==Scenario::FinalReset?selected:source);
            if(scenario==Scenario::FinalBudget)EXPECT_EQ(transaction.Reason(),"final_model_observation_budget");
            return;
        }
        ASSERT_EQ(transaction.Status(),NativePostTuneTransactionStatus::WeightsSelected)<<transaction.Reason();
        EXPECT_TRUE(report["final_threshold_responses_observed"].toBool());
        EXPECT_EQ(transaction.FinalPackage(),selected);EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),selected);
        const auto final=report["final_model_matrix"].toObject();
        ASSERT_EQ(final["observations"].toArray().size(),int(grid.trials.size()));
        for(const auto& v:final["observations"].toArray())
        {
            const auto o=v.toObject();EXPECT_EQ(o["model_before"],selected["model_revision"]);
            EXPECT_EQ(o["model_after"],selected["model_revision"]);EXPECT_TRUE(o["complete"].toBool());
            // A silent inherited threshold remains target miss, not success.
            EXPECT_TRUE(o["spike_times"].toArray().isEmpty());
        }
        ASSERT_EQ(owner->ImportNativeRecognitionState(selected,implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();owner->Reset();EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),selected);
    };
    EXPECT_EQ(NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "ProbeThresholdOwner",[&](auto storage,auto environment,auto model,auto owner) {
            exercise(storage,environment,model,owner);return ::testing::Test::HasFatalFailure()?2:0;
        }),0);
}
}
TEST(NativePostTuneProbeThreshold,ClassicComplete){ProbeThreshold<NNeuronTimeLearner>(Scenario::Complete);}
TEST(NativePostTuneProbeThreshold,BranchComplete){ProbeThreshold<NNeuronTimeLearnerBranch>(Scenario::Complete);}
TEST(NativePostTuneProbeThreshold,ClassicFinalBudget){ProbeThreshold<NNeuronTimeLearner>(Scenario::FinalBudget);}
TEST(NativePostTuneProbeThreshold,BranchFinalBudget){ProbeThreshold<NNeuronTimeLearnerBranch>(Scenario::FinalBudget);}
TEST(NativePostTuneProbeThreshold,ClassicFinalCancel){ProbeThreshold<NNeuronTimeLearner>(Scenario::FinalCancel);}
TEST(NativePostTuneProbeThreshold,BranchFinalCancel){ProbeThreshold<NNeuronTimeLearnerBranch>(Scenario::FinalCancel);}
TEST(NativePostTuneProbeThreshold,ClassicFinalReset){ProbeThreshold<NNeuronTimeLearner>(Scenario::FinalReset);}
TEST(NativePostTuneProbeThreshold,BranchFinalReset){ProbeThreshold<NNeuronTimeLearnerBranch>(Scenario::FinalReset);}
