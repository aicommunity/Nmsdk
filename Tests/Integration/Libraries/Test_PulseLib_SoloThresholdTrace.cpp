#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeSoloThresholdTrace.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include <cstdlib>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
enum class Scenario { Complete, Spiking, Cancel, Changed };

template<class Owner> void Measure(Scenario scenario)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires original native learned-source packages";
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const auto name=std::string(branch?"Branch":"Classic")+"_solo_threshold_"+std::to_string(int(scenario));
    const QDir root(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto solo=job["source_recognition"].toObject()["source_solo"].toObject();
    const auto implementation=job["implementation_id"].toString().toStdString();
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    EXPECT_EQ(NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "SoloThresholdOwner",[&](auto,auto environment,auto model,auto owner) {
        model->Init();model->Reset();
        const auto installed=owner->ImportNativeLearnedState(solo,implementation);
        EXPECT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
        if(installed.status!=NativeModelBuildStatus::Adopted)return 2;
        owner->Build();owner->Init();
        auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);
        EXPECT_TRUE(zone);if(!zone)return 2;
        if(scenario==Scenario::Spiking)zone->Threshold=0.; // Explicit alternate measurement physics.
        const auto threshold=zone->Threshold.GetData();
        auto q=owner->NativeTrainingController().Plan().probe;
        q.specification.runId=name;q.specification.trialId="fresh-target-burst";
        q.activeInput=0;q.inputId=owner->NativeTrainingController().Plan().protocol.inputs[0].id;
        const auto life=owner->ObserveLifecycle();auto* pointer=owner.Get();
        auto observer=std::make_shared<NmsdkTools::ModelRevisionObserver>();
        const auto revision=[life,pointer,observer](bool full) {
            if(!life.IsCurrent())throw std::logic_error("trace_fixture_owner_changed");
            auto n=pointer->template GetComponentL<NPulseNeuron>("Neuron",true);
            auto g=pointer->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
            if(!n || !g)throw std::logic_error("trace_fixture_source_missing");
            return observer->Read(n,{{&g->Output,"burst"}},full).toStdString();
        };
        q.readModelRevision=[revision]{return revision(false);};
        q.readFullModelRevision=[revision]{return revision(true);};q.baseModelRevision=revision(true);
        q.modelEpoch=owner->NativeTrainingController().ModelEpoch();
        std::size_t samples=0,prepares=0;
        q.onPrepared=[&](const auto&,const auto&){++prepares;};
        q.onSample=[&](const auto&){++samples;};
        const auto captured=NativeSoloThresholdTrace::Attach(*owner,q);
        owner->QueueNativeProbe(std::move(q));
        std::optional<NativeProbeResult> result;
        const auto maximum=std::size_t(job["maximum_model_ticks"].toDouble());
        for(std::size_t tick=0;!result && tick<maximum;++tick) {
            model->Calculate();environment->IncreaseModelTimeByStep();
            if(tick==2 && scenario==Scenario::Cancel)owner->Reset();
            if(tick==0 && scenario==Scenario::Changed)zone->Threshold=threshold+1.;
            result=owner->TakeNativeProbeResult();
            // Explicit Reset releases the native executor/result; request a
            // separate cancelled result below instead of fabricating one.
            if(scenario==Scenario::Cancel && tick==2)break;
        }
        if(scenario==Scenario::Cancel) {
            // Reset discards its result by contract. The observer alone cannot
            // claim completion after lifecycle interruption.
            EXPECT_FALSE(result);EXPECT_EQ(prepares,1u);EXPECT_GT(samples,0u);
            const auto report=captured->Interrupt("learner_reset_discarded_result");
            EXPECT_TRUE(report["native_probe"].isNull());EXPECT_FALSE(report["complete"].toBool());
            EXPECT_FALSE(report["proposal_eligible"].toBool());EXPECT_EQ(report["samples"].toArray().size(),int(samples));
            if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
                EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",report);
            }
            return ::testing::Test::HasFailure()?2:0;
        }
        EXPECT_TRUE(result);if(!result)return 2;
        auto report=captured->Finish(*result);
        EXPECT_EQ(prepares,1u);EXPECT_EQ(std::size_t(report["samples"].toArray().size()),samples);
        EXPECT_EQ(report["source"].toObject()["class"],QJsonValue(QString::fromStdString(zone->GetCompClassName())));
        EXPECT_EQ(report["source"].toObject()["threshold"],QJsonValue(threshold));
        if(scenario==Scenario::Changed) {
            EXPECT_EQ(result->status,NativeProbeStatus::Rejected);EXPECT_FALSE(report["valid"].toBool());
            EXPECT_FALSE(report["proposal_eligible"].toBool());EXPECT_TRUE(report["nonspiking"].isNull());
        } else {
            EXPECT_EQ(result->status,NativeProbeStatus::Completed);EXPECT_TRUE(report["complete"].toBool());
            EXPECT_TRUE(report["valid"].toBool());EXPECT_GT(samples,2u);
            EXPECT_EQ(report["nonspiking"],QJsonValue(scenario!=Scenario::Spiking));
            EXPECT_EQ(report["proposal_eligible"],QJsonValue(scenario!=Scenario::Spiking));
            EXPECT_EQ(report["spike_times"].toArray().isEmpty(),scenario!=Scenario::Spiking);
            EXPECT_EQ(zone->Threshold.GetData(),threshold);
            EXPECT_EQ(result->currentBaseRevision,result->prepared->baseModelRevision);
        }
        EXPECT_THROW(captured->Finish(*result),std::logic_error);
        if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
            EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",report);
        }
        return ::testing::Test::HasFailure()?2:0;
    }),0);
}
}
TEST(NativeSoloThresholdTrace,ClassicComplete){Measure<NNeuronTimeLearner>(Scenario::Complete);}
TEST(NativeSoloThresholdTrace,BranchComplete){Measure<NNeuronTimeLearnerBranch>(Scenario::Complete);}
TEST(NativeSoloThresholdTrace,ClassicSpiking){Measure<NNeuronTimeLearner>(Scenario::Spiking);}
TEST(NativeSoloThresholdTrace,BranchSpiking){Measure<NNeuronTimeLearnerBranch>(Scenario::Spiking);}
TEST(NativeSoloThresholdTrace,ClassicReset){Measure<NNeuronTimeLearner>(Scenario::Cancel);}
TEST(NativeSoloThresholdTrace,BranchReset){Measure<NNeuronTimeLearnerBranch>(Scenario::Cancel);}
TEST(NativeSoloThresholdTrace,ClassicModelChange){Measure<NNeuronTimeLearner>(Scenario::Changed);}
TEST(NativeSoloThresholdTrace,BranchModelChange){Measure<NNeuronTimeLearnerBranch>(Scenario::Changed);}
