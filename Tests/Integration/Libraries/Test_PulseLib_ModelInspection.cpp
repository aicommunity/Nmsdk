#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/ModelInspection.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <limits>

namespace {
TEST(TimeLearnerModelInspection, ReadsActualStorageImageWithoutChangingIt)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = RDK::dynamic_pointer_cast<NMSDK::NPulseNeuron>(
        core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
    ASSERT_TRUE(model);
    model->Name = "InspectedNeuron";
    std::string before;
    model->GetPropertyValue("MembraneCapacity", before);
    const auto report = NmsdkTools::InspectModel(model);
    EXPECT_TRUE(report["valid"].toBool()) << QJsonDocument(report).toJson().constData();
    ASSERT_GT(report["nodes"].toArray().size(), 1);
    bool found = false;
    for(const auto& value : report["nodes"].toArray())
    {
        const auto node = value.toObject();
        if(node["path"].toString().endsWith("Soma1.ExcChannel"))
        {
            found = true;
            EXPECT_DOUBLE_EQ(node["physics"].toObject()["capacity_f"].toDouble(), 1e-9);
        }
    }
    EXPECT_TRUE(found);
    std::string after;
    model->GetPropertyValue("MembraneCapacity", after);
    EXPECT_EQ(before, after);
    core.storage->ReturnObject(model);
}

TEST(TimeLearnerModelInspection, InvalidPhysicsIsNotHiddenByAnImplicitRebuild)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = RDK::dynamic_pointer_cast<NMSDK::NPulseNeuron>(
        core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
    ASSERT_TRUE(model);
    auto channel = model->GetComponentL<NMSDK::NPulseChannel>("Soma1.ExcChannel", true);
    ASSERT_TRUE(channel);
    channel->Capacity.SetDataDirect(std::numeric_limits<double>::quiet_NaN());
    const auto report = NmsdkTools::InspectModel(model);
    EXPECT_FALSE(report["valid"].toBool());
    EXPECT_FALSE(report["diagnostics"].toArray().isEmpty());
    EXPECT_TRUE(std::isnan(channel->Capacity.GetData()));
    core.storage->ReturnObject(model);
}
}
