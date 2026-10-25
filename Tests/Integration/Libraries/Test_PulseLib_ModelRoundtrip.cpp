#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/ModelInspection.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>

namespace {
using namespace RDK;
using namespace NMSDK;

void WriteFixture(const std::string& name, const std::string& content)
{
    const char* directory = std::getenv("TIMELEARNER_ROUNDTRIP_TEST_DIR");
    if(!directory) return;
    const auto path = std::filesystem::path(directory) / name;
    std::filesystem::create_directories(path.parent_path());
    std::ofstream file(path, std::ios::binary);
    file << content;
    ASSERT_TRUE(file.good()) << path.string();
}

void WriteGraph(const std::string& name, UEPtr<NPulseNeuron> model)
{
    WriteFixture(name, QJsonDocument(NmsdkTools::InspectModel(model)).toJson().toStdString());
}

UEPtr<NPulseNeuron> TakeAsymmetricGraph()
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto neuron = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
    if(!neuron) return {};
    neuron->SetEnvironment(core.environment);
    neuron->SetGlobalTimeStep(2000);
    neuron->NumSomaMembraneParts = 2;
    neuron->StructureBuildMode = 2;
    neuron->NumDendriteMembranePartsVec = std::vector<int>{1, 2};
    neuron->Build();
    neuron->Init();
    // Explicit full-graph mode: individual physical values belong to the saved
    // graph, rather than a request to regenerate uniform parent defaults.
    neuron->StructureBuildMode = 0;
    neuron->UseElementDefaults = false;
    neuron->Name = "RoundtripNeuron";
    return neuron;
}

void SetIndividualValues(UEPtr<NPulseNeuron> neuron)
{
    auto first = neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel", true);
    auto second = neuron->GetComponentL<NPulseChannel>("Dendrite2_2.InhChannel", true);
    auto synapse = neuron->GetComponentL<NPulseSynapse>("Dendrite2_2.ExcSynapse1", true);
    ASSERT_TRUE(first); ASSERT_TRUE(second); ASSERT_TRUE(synapse);
    first->Capacity = 1.23e-9;
    second->Capacity = 2.34e-9;
    synapse->Resistance = 123e6;
}

void CheckIndividualValues(UEPtr<NPulseNeuron> neuron)
{
    auto first = neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel", true);
    auto second = neuron->GetComponentL<NPulseChannel>("Dendrite2_2.InhChannel", true);
    auto synapse = neuron->GetComponentL<NPulseSynapse>("Dendrite2_2.ExcSynapse1", true);
    ASSERT_TRUE(first); ASSERT_TRUE(second); ASSERT_TRUE(synapse);
    EXPECT_DOUBLE_EQ(first->Capacity.GetData(), 1.23e-9);
    EXPECT_DOUBLE_EQ(second->Capacity.GetData(), 2.34e-9);
    EXPECT_DOUBLE_EQ(synapse->Resistance.GetData(), 123e6);
}

void CompareNativeImpulse(UEPtr<NPulseNeuron> source, UEPtr<NPulseNeuron> target)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    core.environment->CreateModel("NModel");
    auto model = core.environment->GetModel();
    ASSERT_TRUE(model);
    model->SetGlobalTimeStep(2000);
    source->Name = "Source"; target->Name = "Target";
    ASSERT_NE(model->AddComponent(source), ForbiddenId);
    ASSERT_NE(model->AddComponent(target), ForbiddenId);
    core.environment->ModelInit();
    model->Reset();
    auto inputA = source->GetComponentL<NPulseSynapse>("Dendrite2_2.ExcSynapse1", true);
    auto inputB = target->GetComponentL<NPulseSynapse>("Dendrite2_2.ExcSynapse1", true);
    auto outputA = source->GetComponentL<NPulseChannel>("Soma2.ExcChannel", true);
    auto outputB = target->GetComponentL<NPulseChannel>("Soma2.ExcChannel", true);
    ASSERT_TRUE(inputA); ASSERT_TRUE(inputB); ASSERT_TRUE(outputA); ASSERT_TRUE(outputB);
    ASSERT_FALSE(inputA->Input.IsConnected()); ASSERT_FALSE(inputB->Input.IsConnected());
    std::vector<double> waveform;
    double maxDifference = 0.;
    int worstTick = -1;
    for(int tick = 0; tick < 400; ++tick)
    {
        const double stimulus = tick >= 10 && tick < 12 ? 1. : 0.;
        inputA->Input.Assign(1, 1, stimulus);
        inputB->Input.Assign(1, 1, stimulus);
        model->Calculate();
        core.environment->IncreaseModelTimeByStep();
        const double a = outputA->Output(0, 0), b = outputB->Output(0, 0);
        EXPECT_TRUE(std::isfinite(a)); EXPECT_TRUE(std::isfinite(b));
        if(std::abs(a - b) > maxDifference) { maxDifference = std::abs(a - b); worstTick = tick; }
        waveform.push_back(a);
    }
    const auto range = std::minmax_element(waveform.begin(), waveform.end());
    EXPECT_GT(*range.second - *range.first, 1e-8) << "A flat response cannot validate an impulse roundtrip";
    EXPECT_LE(maxDifference, 1e-12) << "worst tick=" << worstTick;
    CheckIndividualValues(source); CheckIndividualValues(target);
    model->DelComponent("Target", false);
    model->DelComponent("Source", false);
}

TEST(TimeLearnerNativeRoundtrip, CopyPreservesFullGraphParametersCachesAndImpulse)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto source = TakeAsymmetricGraph();
    auto target = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
    ASSERT_TRUE(source); ASSERT_TRUE(target);
    target->SetEnvironment(core.environment);
    SetIndividualValues(source);
    const auto before = NmsdkTools::InspectModel(source);
    ASSERT_TRUE(before["valid"].toBool()) << QJsonDocument(before["diagnostics"].toArray()).toJson().constData();
    ASSERT_GT(before["links"].toArray().size(), 0);
    ASSERT_TRUE(source->Copy(target, core.storage, false));
    target->Init();
    const auto after = NmsdkTools::InspectModel(target);
    ASSERT_TRUE(after["valid"].toBool()) << QJsonDocument(after["diagnostics"].toArray()).toJson().constData();
    EXPECT_EQ(before["links"], after["links"]);
    EXPECT_EQ(before["nodes"].toArray().size(), after["nodes"].toArray().size());
    CheckIndividualValues(target);
    CompareNativeImpulse(source, target);
    core.storage->ReturnObject(target); core.storage->ReturnObject(source);
}

TEST(TimeLearnerNativeRoundtrip, XmlPreservesFullGraphParametersCachesAndImpulse)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto source = TakeAsymmetricGraph();
    auto target = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject("NSPNeuronGenAsymRmD001C1e9"));
    ASSERT_TRUE(source); ASSERT_TRUE(target);
    target->SetEnvironment(core.environment);
    SetIndividualValues(source);
    const auto before = NmsdkTools::InspectModel(source);
    ASSERT_TRUE(before["valid"].toBool());
    USerStorageXML xml;
    ASSERT_TRUE(xml.Create("RoundtripFixture"));
    // CheckMask requires both a type and a visibility group. Type-only masks
    // serialize an empty parameter section even when SaveComponent succeeds.
    ASSERT_TRUE(source->SaveComponent(&xml, true, ptPubParameter | ptPubState | pgSystem));
    std::string xmlText;
    ASSERT_TRUE(xml.Save(xmlText));
    ASSERT_NE(xmlText.find("<UseElementDefaults"), std::string::npos);
    ASSERT_NE(xmlText.find("<Capacity"), std::string::npos);
    ASSERT_NE(xmlText.find("<Resistance"), std::string::npos);
    WriteFixture("native-graph.xml", xmlText);
    WriteGraph("source.json", source);
    ASSERT_TRUE(xml.SelectNode(source->GetName()));
    target->Name = source->GetName();
    ASSERT_TRUE(target->LoadComponent(&xml, true));
    WriteGraph("loaded-before-init.json", target);
    EXPECT_FALSE(target->UseElementDefaults.GetData());
    EXPECT_EQ(target->StructureBuildMode.GetData(), 0);
    CheckIndividualValues(target);
    target->Init();
    WriteGraph("loaded-after-init.json", target);
    const auto after = NmsdkTools::InspectModel(target);
    ASSERT_TRUE(after["valid"].toBool()) << QJsonDocument(after["diagnostics"].toArray()).toJson().constData();
    EXPECT_EQ(before["links"], after["links"]);
    EXPECT_EQ(before["nodes"].toArray().size(), after["nodes"].toArray().size());
    CheckIndividualValues(target);
    CompareNativeImpulse(source, target);
    core.storage->ReturnObject(target); core.storage->ReturnObject(source);
}
}
