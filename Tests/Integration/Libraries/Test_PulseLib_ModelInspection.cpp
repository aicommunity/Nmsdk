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
class BindingGraph : public RDK::UNet
{
public:
    template<typename T, unsigned int Kind>
    class InspectableProperty : public RDK::UProperty<T, BindingGraph, Kind>
    {
    public:
        using RDK::UProperty<T, BindingGraph, Kind>::UProperty;
        // Test the protected external-source path used by GetData; no new
        // production mutation API is introduced for this diagnostic fixture.
        void UseExternal(RDK::UVBaseDataProperty<T>* source) { this->ExternalDataSource = source; }
    };
    RDK::UProperty<double, BindingGraph, ptOutput | ptPubState> First, Second;
    InspectableProperty<double, ptInput | ptPubState> Scalar;
    RDK::UProperty<std::vector<double>, BindingGraph, ptInput | ptPubState> Vector;
    BindingGraph() : First("First", this), Second("Second", this),
                     Scalar("Scalar", this), Vector("Vector", this)
    {
        Name = "Bindings";
        First = 3.; Second = 7.;
    }
    static RDK::UComponent* Create() { return new BindingGraph; }
};

RDK::UEPtr<BindingGraph> TakeBindingGraph()
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    const std::string className = "TimeLearnerInspectionBindingFixture";
    if(!core.storage->CheckClass(className))
        core.storage->AddClass(new RDK::UComponentFactoryMethod(core.storage, &BindingGraph::Create, "Bindings"), className);
    return RDK::dynamic_pointer_cast<BindingGraph>(core.storage->TakeObject(className));
}

TEST(TimeLearnerModelInspection, ReadsScalarAndVectorDirectBindingsInSlotOrder)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = TakeBindingGraph();
    ASSERT_TRUE(model);
    model->Scalar.SetPointer(0, &model->First);
    model->Vector.SetPointer(0, &model->Second);
    model->Vector.SetPointer(1, &model->First);
    const auto before = model->Vector.GetData();
    ASSERT_EQ(before, (std::vector<double>{7., 3.}));
    const auto report = NmsdkTools::InspectModel(model);
    EXPECT_TRUE(report["valid"].toBool()) << QJsonDocument(report).toJson().constData();
    const auto links = report["links"].toArray();
    ASSERT_EQ(links.size(), 3);
    int checked = 0;
    for(const auto& value : links)
    {
        const auto link = value.toObject();
        if(link["target"] == "Bindings:Vector")
        {
            const int slot = link["target_slot"].toInt();
            EXPECT_EQ(link["source"].toString(), slot == 0 ? "Bindings:Second" : "Bindings:First");
            ++checked;
        }
    }
    EXPECT_EQ(checked, 2);
    EXPECT_EQ(model->Vector.GetData(), before);
    EXPECT_DOUBLE_EQ(model->Scalar.GetData(), 3.);
    model->Scalar.ResetPointer(0, &model->First);
    model->Vector.ResetPointer(1, &model->First);
    model->Vector.ResetPointer(0, &model->Second);
    core.storage->ReturnObject(model);
}

TEST(TimeLearnerModelInspection, ExternalSourceHasNativePrecedenceAndOutsideSourceIsInvalid)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = TakeBindingGraph();
    ASSERT_TRUE(model);
    model->Scalar.SetPointer(0, &model->First);
    model->Scalar.UseExternal(&model->Second);
    EXPECT_DOUBLE_EQ(model->Scalar.GetData(), 7.);
    auto report = NmsdkTools::InspectModel(model);
    ASSERT_TRUE(report["valid"].toBool()) << QJsonDocument(report).toJson().constData();
    ASSERT_EQ(report["links"].toArray().size(), 1);
    const auto link = report["links"].toArray()[0].toObject();
    EXPECT_EQ(link["source"].toString(), "Bindings:Second");
    EXPECT_EQ(link["binding_kind"].toString(), "external_data_source");
    BindingGraph outside;
    model->Scalar.UseExternal(&outside.First);
    report = NmsdkTools::InspectModel(model);
    EXPECT_FALSE(report["valid"].toBool());
    EXPECT_TRUE(report["links"].toArray()[0].toObject()["source"].isNull());
    EXPECT_DOUBLE_EQ(model->Scalar.GetData(), 3.);
    model->Scalar.UseExternal(nullptr);
    model->Scalar.ResetPointer(0, &model->First);
    core.storage->ReturnObject(model);
}

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
