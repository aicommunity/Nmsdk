#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NConstGenerator.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ModelIdentity.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/NativeOperationChecks.h"
#include "../Support/ConsoleLikeInit.h"
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <cstdlib>
#include <stdexcept>

namespace {
using namespace RDK;
using namespace NMSDK;

enum class PreviousGraph { Fresh, ConnectedChild, DetachedChild };

QJsonObject InputValue(const UEPtr<NPulseMembrane>& membrane)
{
    const auto& value = membrane->InputFeedbackSignal.GetData();
    QJsonArray data;
    for(size_t i = 0; i < value.GetSize(); ++i) data.append(value.Data[i]);
    return {{"rows", int(value.GetRows())}, {"cols", int(value.GetCols())}, {"data", data}};
}

void RunLoadHistory(unsigned int frequency, PreviousGraph previous)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();
    core.environment->SetUseIndTimeStepFlag(false);
    core.environment->GetTime().SetTime(0);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto clock = dynamic_pointer_cast<UNet>(core.environment->GetModel());
    ASSERT_TRUE(clock);
    clock->SetGlobalTimeStep(frequency);

    auto source = dynamic_pointer_cast<NPulseMembrane>(core.storage->TakeObject("NPMembraneBio"));
    auto target = dynamic_pointer_cast<NPulseMembrane>(core.storage->TakeObject("NPMembraneBio"));
    ASSERT_TRUE(source); ASSERT_TRUE(target);
    for(const auto& membrane : {source, target})
    {
        membrane->SetEnvironment(core.environment);
        membrane->SetGlobalTimeStep(frequency);
        NmsdkTools::InitializeAndResetNative(membrane);
    }
    ASSERT_FALSE(source->InputFeedbackSignal.IsConnected());
    // An explicit, nonzero local input distinguishes lost data from two
    // differently shaped representations of the same numerical zero.
    MDMatrix<double> local;
    local.Assign(1, 1, .25);
    source->InputFeedbackSignal = local;
    const auto expectedInput = InputValue(source);
    const auto expectedIdentity = NmsdkTools::IdentifyModel(source);
    ASSERT_TRUE(expectedIdentity["valid"].toBool());

    USerStorageXML saved;
    ASSERT_TRUE(saved.Create("NativeLoadHistory"));
    ASSERT_TRUE(source->SaveComponent(&saved, true, ptPubParameter | ptPubState | pgSystem));
    saved.SelectRoot();
    std::string xmlBytes;
    ASSERT_TRUE(saved.Save(xmlBytes));

    if(previous != PreviousGraph::Fresh)
    {
        auto oldSource = dynamic_pointer_cast<NConstGenerator>(
            core.storage->TakeObject("NPNeuronPosCGenerator"));
        ASSERT_TRUE(oldSource);
        oldSource->Name = "PreviousFeedback";
        UEPtr<UContainer> child = oldSource;
        ASSERT_NE(target->AddComponent(child), ForbiddenId);
        oldSource->SetEnvironment(core.environment);
        oldSource->SetGlobalTimeStep(frequency);
        NmsdkTools::InitializeAndResetNative(oldSource);
        MDMatrix<double> oldValue;
        oldValue.Assign(1, 1, .75);
        oldSource->Output = oldValue;
        int slot = 0;
        ASSERT_TRUE(oldSource->Connect(dynamic_pointer_cast<UConnector>(target),
            "Output", "InputFeedbackSignal", slot, true));
        ASSERT_EQ(slot, 0);
        ASSERT_TRUE(target->InputFeedbackSignal.IsConnected());
        ASSERT_EQ(InputValue(target)["data"].toArray(), QJsonArray{.75});
    }
    const auto oldInput = InputValue(target);
    target->UnInit();
    if(previous == PreviousGraph::DetachedChild)
    {
        // A separately reported positive control, not a production fix. Native
        // operations remove the old graph before the saved state is applied.
        target->DisconnectPropertyDataSources();
        target->DelAllComponents();
    }
    USerStorageXML loaded;
    ASSERT_TRUE(loaded.Load(xmlBytes, "NativeLoadHistory"));
    ASSERT_TRUE(loaded.SelectNode(source->GetName()));
    TProjectLoadDiagnostics diagnostics;
    ASSERT_TRUE(target->LoadComponent(&loaded, true, &diagnostics));
    ASSERT_TRUE(diagnostics.errors.empty());
    ASSERT_TRUE(diagnostics.warnings.empty());
    const auto afterLoad = InputValue(target);
    NmsdkTools::InitializeAndResetNative(target);
    const auto afterReset = InputValue(target);
    const auto physical = NmsdkTools::VerifyModelIdentity(expectedIdentity, target);
    EXPECT_TRUE(physical["valid"].toBool());
    EXPECT_TRUE(physical["match"].toBool()) << QJsonDocument(physical).toJson().constData();
    EXPECT_EQ(afterLoad, expectedInput) << "previous graph changed loaded local input";
    EXPECT_EQ(afterReset, expectedInput) << "native initialization/reset changed loaded local input";
    EXPECT_FALSE(target->InputFeedbackSignal.IsConnected());
    EXPECT_FALSE(target->GetComponent("PreviousFeedback", true));

    UEPtr<UContainer> attached = target;
    ASSERT_NE(clock->AddComponent(attached), ForbiddenId);
    NmsdkTools::InitializeAndResetNative(clock);
    QJsonArray time, feedback;
    for(int tick = 0; tick < 8; ++tick)
    {
        // Only the root scheduler calculates the real membrane and its children.
        clock->Calculate();
        time.append(core.environment->GetTime().GetDoubleTime());
        feedback.append(target->Feedback.GetData());
        EXPECT_DOUBLE_EQ(target->Feedback.GetData(), .25 * target->FeedbackGain.GetData());
        core.environment->IncreaseModelTimeByStep();
    }
    if(const char* output = std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        const auto* test = ::testing::UnitTest::GetInstance()->current_test_info();
        const QJsonObject observation{{"kind", "native_load_history_observation"}, {"schema_version", 1},
            {"test_id", QString::fromStdString(std::string(test->test_suite_name()) + "/" + test->name())},
            {"frequency_hz", int(frequency)}, {"previous_graph", int(previous)},
            {"expected_input", expectedInput}, {"old_input", oldInput},
            {"after_native_load", afterLoad}, {"after_native_reset", afterReset},
            {"physical_comparison", physical}, {"native_source_xml", QString::fromStdString(xmlBytes)},
            {"time_s", time}, {"feedback", feedback}, {"scientific_verdict", QJsonValue(QJsonValue::Null)}};
        QFile file(QString::fromLocal8Bit(output) + "/native-load-history.json");
        ASSERT_TRUE(file.open(QIODevice::WriteOnly));
        const auto bytes = QJsonDocument(observation).toJson(QJsonDocument::Indented);
        ASSERT_EQ(file.write(bytes), bytes.size());
    }
    clock->BreakLinks();
    core.environment->DestroyModel();
    core.storage->ReturnObject(source);
}

TEST(NativeLoadHistory, FreshAt2000) { RunLoadHistory(2000, PreviousGraph::Fresh); }
TEST(NativeLoadHistory, ConnectedChildAt2000) { RunLoadHistory(2000, PreviousGraph::ConnectedChild); }
TEST(NativeLoadHistory, DetachedChildAt2000) { RunLoadHistory(2000, PreviousGraph::DetachedChild); }
TEST(NativeLoadHistory, FreshAt20000) { RunLoadHistory(20000, PreviousGraph::Fresh); }
TEST(NativeLoadHistory, ConnectedChildAt20000) { RunLoadHistory(20000, PreviousGraph::ConnectedChild); }
TEST(NativeLoadHistory, DetachedChildAt20000) { RunLoadHistory(20000, PreviousGraph::DetachedChild); }
}
