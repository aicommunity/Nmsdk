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
enum class Interruption { Reset, Default, Destroy };
template<class Owner,bool Weights,bool Nested=false> void Interrupt(Interruption operation)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires original portable Console source/model primaries";
    const bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const std::string top=branch?"Branch":"Classic";
    const std::string name=top+"_"+(Nested?"nested":Weights?"weights":"threshold")+"_"+std::to_string(int(operation));
    const QDir source(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(source.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto implementation=job["implementation_id"].toString().toStdString();
    NativeThresholdGridSpec grid;grid.maximumCandidates=std::size_t(job["maximum_candidates"].toDouble());
    grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
    for(const auto& value:job["thresholds"].toArray())grid.thresholds.push_back(value.toDouble());
    for(const auto& value:job["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(value.toObject()));
    using Transaction=std::conditional_t<Weights,NativePostTuneTransaction<Owner>,NativeThresholdCalibrationTransaction<Owner>>;
    std::unique_ptr<Transaction> transaction;QJsonObject stopped;std::size_t ticks=0;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    const auto exercise=[&](auto storage,auto environment,auto model,auto owner) {
        struct DetachBeforeNativeTeardown {
            std::unique_ptr<Transaction>& transaction;
            ~DetachBeforeNativeTeardown(){if(transaction)transaction->InterruptOwnerLifecycle("fixture_early_exit");}
        } detach{transaction};
        ASSERT_EQ(owner->ImportNativeRecognitionState(job["source_recognition"].toObject(),implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();model->Init();model->Reset();
        if constexpr(Weights)
        {
            auto spec=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
            if constexpr(!Nested)
            {
                spec.mode=NativePostTuneControllerMode::KeepDone;spec.canonicalFloor=spec.canonicalLast=0.;spec.resistanceBounds.clear();
                spec.finalization=NativePostTuneFinalization::KeepFixedThreshold;spec.calibration.thresholds.clear();spec.calibration.maximumCandidates=0;
            }
            transaction=std::make_unique<Transaction>(*owner,spec,implementation);
        }
        else transaction=std::make_unique<Transaction>(*owner,grid,implementation);
        transaction->Advance();
        if constexpr(Nested)
        {
            const auto limit=std::size_t(job["maximum_model_ticks"].toDouble());
            while(!transaction->Done() && !transaction->IsCalibrating() && ticks<limit)
            {model->Calculate();environment->IncreaseModelTimeByStep();++ticks;transaction->Advance();}
            ASSERT_TRUE(transaction->IsCalibrating());ASSERT_FALSE(transaction->Done());
            transaction->Advance(); // Arm a real child calibration probe before interruption.
            const auto child=transaction->Report()["calibration"].toObject();
            ASSERT_EQ(child["status"],QJsonValue("running"));
            ASSERT_FALSE(child["active_matrix"].toObject()["requests"].toArray().isEmpty());
        }
        ASSERT_FALSE(transaction->Done());ASSERT_FALSE(owner->IsNativeRecognitionTrialIdle());
        const auto package=owner->ExportNativeRecognitionState(implementation);
        const auto lifecycle=owner->ObserveLifecycle();
        const bool ready=owner->IsReady(),initialized=owner->IsInit();
        transaction->InterruptOwnerLifecycle("configured_phase_owner_interrupted");
        ASSERT_TRUE(transaction->Done());stopped=transaction->Report();
        EXPECT_EQ(stopped["status"],QJsonValue("recovery_required"));
        EXPECT_FALSE(stopped["source_restored"].toBool());
        EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),package);
        EXPECT_TRUE(lifecycle.IsCurrent());EXPECT_EQ(owner->IsReady(),ready);EXPECT_EQ(owner->IsInit(),initialized);
        EXPECT_FALSE(owner->IsNativeRecognitionTrialIdle()); // Interrupt did not cancel/write the physical owner.
        if constexpr(Nested)
        {
            const auto child=stopped["calibration"].toObject();
            EXPECT_EQ(child["status"],QJsonValue("recovery_required"));EXPECT_FALSE(child["source_restored"].toBool());
        }
        if(operation==Interruption::Reset)owner->Reset();
        else if(operation==Interruption::Default)owner->Default();
        // Destroy is performed by WithFreshOwner's native model/storage scope.
        EXPECT_EQ(transaction->Report(),stopped);
    };
    ASSERT_EQ(NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",unsigned(job["frequency_hz"].toDouble()),
        "PhaseOwner",[&](auto storage,auto environment,auto model,auto owner){exercise(storage,environment,model,owner);return 0;}),0);
    ASSERT_TRUE(transaction);ASSERT_TRUE(transaction->Done());
    transaction->Advance();transaction->Cancel("late_cancel");transaction->InterruptOwnerLifecycle("late_interrupt");
    EXPECT_EQ(transaction->Report(),stopped); // No owner access even after native teardown.
    transaction.reset();
    if(const auto directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(directory)));
        NmsdkWorker::Write(QString::fromLocal8Bit(directory),QString::fromStdString(name)+".json",
            QJsonObject{{"kind","native_phase_lifecycle_interruption_control"},{"schema_version",1},
                {"topology",branch?"branch":"classic"},{"controller",Nested?"nested":Weights?"weights":"threshold"},
                {"operation",operation==Interruption::Reset?"reset":operation==Interruption::Default?"default":"destroy"},
                {"model_ticks",double(ticks)},{"transaction",stopped},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
    }
}
#define PHASE_CASE(Owner,Name,Tune,Op) TEST(NativePhaseLifecycle,Name){Interrupt<Owner,Tune>(Interruption::Op);}
PHASE_CASE(NNeuronTimeLearner,ClassicWeightReset,true,Reset)
PHASE_CASE(NNeuronTimeLearner,ClassicWeightDefault,true,Default)
PHASE_CASE(NNeuronTimeLearner,ClassicWeightDestroy,true,Destroy)
PHASE_CASE(NNeuronTimeLearner,ClassicThresholdReset,false,Reset)
PHASE_CASE(NNeuronTimeLearner,ClassicThresholdDefault,false,Default)
PHASE_CASE(NNeuronTimeLearner,ClassicThresholdDestroy,false,Destroy)
PHASE_CASE(NNeuronTimeLearnerBranch,BranchWeightReset,true,Reset)
PHASE_CASE(NNeuronTimeLearnerBranch,BranchWeightDefault,true,Default)
PHASE_CASE(NNeuronTimeLearnerBranch,BranchWeightDestroy,true,Destroy)
PHASE_CASE(NNeuronTimeLearnerBranch,BranchThresholdReset,false,Reset)
PHASE_CASE(NNeuronTimeLearnerBranch,BranchThresholdDefault,false,Default)
PHASE_CASE(NNeuronTimeLearnerBranch,BranchThresholdDestroy,false,Destroy)
TEST(NativePhaseLifecycle,ClassicNestedDefault){Interrupt<NNeuronTimeLearner,true,true>(Interruption::Default);}
TEST(NativePhaseLifecycle,ClassicNestedDestroy){Interrupt<NNeuronTimeLearner,true,true>(Interruption::Destroy);}
TEST(NativePhaseLifecycle,BranchNestedDefault){Interrupt<NNeuronTimeLearnerBranch,true,true>(Interruption::Default);}
TEST(NativePhaseLifecycle,BranchNestedDestroy){Interrupt<NNeuronTimeLearnerBranch,true,true>(Interruption::Destroy);}
#undef PHASE_CASE
}
