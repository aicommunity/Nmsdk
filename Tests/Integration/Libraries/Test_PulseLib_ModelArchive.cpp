#include <gtest/gtest.h>
#include "TimeLearner/ModelArchive.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NConstGenerator.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QCryptographicHash>
#include <QFile>
#include <QFileInfo>
#include <QProcess>
#include <QProcessEnvironment>
#include <QTemporaryDir>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;

QJsonObject Metadata()
{
    QJsonObject metadata;
    metadata["implementation_id"] = "native-archive-fixture-v1";
    metadata["state_kind"] = "model_spec";
    metadata["training"] = QJsonObject{{"status", "not_trained"}};
    metadata["calibration"] = QJsonObject{{"status", "fixed"}, {"protocol", "declared-fixture"},
        {"ltzone_path", "$.LTZone"}, {"threshold", .0117}};
    metadata["conversion"] = QJsonObject{{"mode", "none"}};
    return metadata;
}

UEPtr<NPulseNeuron> Prepared(unsigned int frequency, bool precise = false, bool withMatrix = false)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    StorageProfileSpec spec; spec.name = "NativeArchiveFixture_" + std::to_string(frequency);
    spec.frequencyHz = frequency; spec.ltMembrane = spec.body;
    spec.ltMembrane->excChannel.capacity = .3e-9;
    if(precise)
    {
        spec.name += "_F64Precision";
        // Uniform physics belongs to immutable storage recipes; learned
        // individual changes below must survive alongside these prototypes.
        spec.body.excChannel.capacity = 1.2345678901234567e-9;
        spec.body.excChannel.resistance = 12345678.901234567;
        spec.body.excChannel.restingResistance = 11223344.556677889;
        spec.body.excSynapse.resistance = 86420975.3108642;
        spec.body.excSynapse.secretionTC = .0012345678901234567;
        spec.body.excSynapse.dissociationTC = .0009876543210987654;
        spec.body.excSynapse.pulseAmplitude = 1.2345678901234567;
        spec.ltMembrane->excChannel.capacity = .34567890123456789e-9;
    }
    spec.body.excSynapse.usePresynapticInhibition = true; spec.body.excSynapse.inhibitionCoefficient = 2.5;
    const auto classes = RegisterStorageProfile(core.storage, core.environment, spec);
    auto neuron = dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(classes.neuronClass));
    if(!neuron) throw std::runtime_error("fixture neuron unavailable");
    neuron->SetEnvironment(core.environment); neuron->NumSomaMembraneParts = 2;
    neuron->StructureBuildMode = 2; neuron->NumDendriteMembranePartsVec = std::vector<int>{1,3};
    neuron->Init();
    auto tip = neuron->GetComponentL<NPulseMembrane>("Dendrite2_3", true);
    if(!tip) throw std::runtime_error("fixture tip unavailable");
    tip->NumExcitatorySynapses = 3; tip->Build();
    tip->GetComponentL<NPulseSynapse>("ExcSynapse2",true)->Resistance = precise ? 333333333.12345678 : 333e6;
    tip->GetComponentL<NPulseChannel>("ExcChannel",true)->Capacity = precise ? 1.4142135623730951e-9 : 1.41e-9;
    if(precise)
    {
        auto channel = neuron->GetComponentL<NPulseChannel>("Dendrite1_1.ExcChannel",true);
        auto synapse = neuron->GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);
        if(!channel || !synapse || channel->Capacity.GetData()!=spec.body.excChannel.capacity ||
           channel->Resistance.GetData()!=spec.body.excChannel.resistance ||
           channel->RestingResistance.GetData()!=spec.body.excChannel.restingResistance ||
           synapse->Resistance.GetData()!=spec.body.excSynapse.resistance ||
           synapse->SecretionTC.GetData()!=spec.body.excSynapse.secretionTC ||
           synapse->DissociationTC.GetData()!=spec.body.excSynapse.dissociationTC ||
           synapse->PulseAmplitude.GetData()!=spec.body.excSynapse.pulseAmplitude)
            throw std::runtime_error("high precision storage physics differs before archive export");
    }
    if(withMatrix)
    {
        // TrainingPattern is a public matrix parameter, unlike transient soma
        // outputs. Archive identity must retain every stored reference bit.
        MDMatrix<double> pattern;pattern.Assign(2,3,0.0);
        pattern(0,0)=.0012345678901234567;pattern(0,1)=.0056789012345678901;
        pattern(0,2)=.0098765432109876543;pattern(1,0)=.0023456789012345678;
        pattern(1,1)=.0067890123456789012;pattern(1,2)=.012345678901234567;
        neuron->TrainingPattern=pattern;
        if(neuron->TrainingPattern.GetData()!=pattern)
            throw std::runtime_error("high precision matrix differs before archive export");
    }
    return neuron;
}

QJsonArray Waveform(UEPtr<UContainer> neuron, unsigned int frequency, NConstGenerator* boundary = nullptr,
                   QJsonArray* actualInputs = nullptr, QJsonArray* somaSignal = nullptr,
                   QJsonArray* sampleClock = nullptr)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    // Environment advances time using its current model's rate. A detached
    // NModel is insufficient and would leave Model null or use an old rate.
    core.environment->DestroyModel();
    if(!core.environment->CreateModel("NModel")) throw std::runtime_error("fixture environment model unavailable");
    auto model = dynamic_pointer_cast<UNet>(core.environment->GetModel());
    if(!model) throw std::runtime_error("fixture model unavailable");
    model->SetEnvironment(core.environment);
    const auto name = neuron->GetName();
    if(model->AddComponent(neuron) == ForbiddenId) throw std::runtime_error("fixture attach failed");
    core.environment->GetTime().SetTime(0); // declared probe origin, not archived dynamics
    model->SetGlobalTimeStep(frequency); model->Init(); model->Reset();
    auto channel = neuron->GetComponentL<NPulseChannel>("Soma2.ExcChannel", true);
    auto soma = neuron->GetComponentL<NPulseMembrane>("Soma2", true);
    if(!channel || !soma) throw std::runtime_error("fixture soma unavailable");
    QJsonArray trace;
    for(unsigned int tick = 0; tick < frequency / 10; ++tick)
    {
        const double time = double(tick) / frequency, stimulus = time >= .005 && time < .006 ? 1. : 0.;
        const double nativeTime=core.environment->GetTime().GetDoubleTime();
        if(!std::isfinite(nativeTime) || std::abs(nativeTime-time)>1e-12)
            throw std::runtime_error("archive fixture native clock differs from declared grid");
        if(boundary) boundary->Output.Assign(1,1,stimulus);
        for(int i = 1; i <= 3; ++i)
        {
            auto synapse = neuron->GetComponentL<NPulseSynapse>("Dendrite2_3.ExcSynapse" + std::to_string(i),true);
            if(!synapse || synapse->Input.IsConnected() != bool(boundary)) throw std::runtime_error("fixture stimulus port invalid");
            if(!boundary) synapse->Input.Assign(1,1,stimulus);
        }
        model->Calculate(); core.environment->IncreaseModelTimeByStep();
        const double value = channel->Output(0,0);
        const double somaValue = soma->SumPotential(0,0);
        const double input = neuron->GetComponentL<NPulseSynapse>("Dendrite2_3.ExcSynapse1",true)->Input(0,0);
        if(!std::isfinite(value) || !std::isfinite(somaValue) || input!=stimulus)
            throw std::runtime_error("invalid archive waveform or actual input");
        trace.append(value);
        if(actualInputs) actualInputs->append(input);
        if(somaSignal) somaSignal->append(somaValue);
        if(sampleClock) sampleClock->append(nativeTime);
    }
    model->DelComponent(name, false); core.environment->DestroyModel();
    return trace;
}

void ConnectBoundary(UEPtr<NPulseNeuron> neuron, NConstGenerator* source)
{
    for(int i=1;i<=3;++i)
    {
        auto connector = dynamic_pointer_cast<UConnector>(neuron->GetComponentL("Dendrite2_3.ExcSynapse"+std::to_string(i),true));
        ASSERT_TRUE(connector); int slot = 0;
        ASSERT_TRUE(source->Connect(connector,"Output","Input",slot));
        ASSERT_EQ(slot,0);
    }
}

void Write(const QString& path, const QJsonObject& object)
{
    QFile file(path);
    if(!file.open(QIODevice::WriteOnly | QIODevice::NewOnly)) throw std::runtime_error("fixture file exists or cannot be written");
    const auto bytes = QJsonDocument(object).toJson();
    if(file.write(bytes) != bytes.size() || !file.flush()) throw std::runtime_error("fixture write failed");
}

QJsonObject Read(const QString& path)
{
    QFile file(path); if(!file.open(QIODevice::ReadOnly)) throw std::runtime_error("fixture read failed");
    QJsonParseError error;
    auto document = QJsonDocument::fromJson(file.readAll(), &error);
    if(error.error != QJsonParseError::NoError || !document.isObject()) throw std::runtime_error("fixture JSON invalid");
    return document.object();
}

void Seal(QJsonObject& archive)
{ archive.remove("sha256"); archive["sha256"] = NmsdkTools::CanonicalModelDataSha256(archive); }

void ExpectImportFailure(const QJsonObject& archive, const char* reason)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    try {
        auto unexpected = NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"native-archive-fixture-v1");
        core.storage->ReturnObject(unexpected); ADD_FAILURE() << "invalid archive accepted";
    }
    catch(const NmsdkTools::ModelArchiveError& error) { EXPECT_EQ(error.code,reason); }
}

QJsonObject EditXml(const QJsonObject& archive, const std::vector<std::string>& path, int edit)
{
    auto result = archive; auto graph = result["graph"].toObject();
    USerStorageXML xml;
    if(!xml.Load(graph["native_xml"].toString().toStdString(),"TimeLearnerNativeGraph") ||
       !xml.SelectNode(graph["component_name"].toString().toStdString())) throw std::runtime_error("fixture native XML unavailable");
    for(const auto& node : path) if(!xml.SelectNode(node)) throw std::runtime_error("fixture XML edit path unavailable: "+node);
    if(edit==0) xml.DelNode();
    else if(edit==1) xml.SetNodeAttribute("Class","NPSynapse");
    else xml.DelNodeInternalContent();
    std::string text; if(!xml.Save(text)) throw std::runtime_error("fixture XML Save failed");
    graph["native_xml"] = QString::fromStdString(text);
    graph["native_xml_sha256"] = QString::fromLatin1(QCryptographicHash::hash(QByteArray::fromStdString(text),QCryptographicHash::Sha256).toHex());
    result["graph"] = graph; Seal(result); return result;
}

TEST(TimeLearnerModelArchive, FreshProcessImport)
{
    const char* input = std::getenv("TIMELEARNER_ARCHIVE_CHILD_INPUT");
    if(!input) GTEST_SKIP() << "Executed explicitly by the fresh-process parent or cross-host archive control";
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    const auto fixture = Read(QString::fromLocal8Bit(input)), archive = fixture["archive"].toObject();
    const auto modelClass = archive["graph"].toObject()["component_class"].toString().toStdString();
    ASSERT_FALSE(core.storage->CheckClass(modelClass));
    UEPtr<NConstGenerator> boundary;
    NmsdkTools::ModelBoundarySources ports;
    if(fixture["stimulus_port"].isString())
    {
        boundary = dynamic_pointer_cast<NConstGenerator>(core.storage->TakeObject("NPNeuronPosCGenerator"));
        ASSERT_TRUE(boundary); boundary->SetEnvironment(core.environment); boundary->Init();
        boundary->Name = "IndependentTestStimulus";
        ports[&boundary->Output] = fixture["stimulus_port"].toString();
    }
    auto model = NmsdkTools::ImportModelArchive(archive, core.storage, core.environment, "native-archive-fixture-v1",ports);
    ASSERT_TRUE(model);
    const auto expectedIdentity = archive["graph"].toObject()["identity"].toObject();
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(expectedIdentity, model,ports)["match"].toBool());
    QJsonArray inputs,soma,clock;
    const auto actual = Waveform(model, static_cast<unsigned int>(fixture["frequency_hz"].toInt()),boundary.Get(),&inputs,&soma,&clock);
    const auto expected = fixture["waveform"].toArray(); ASSERT_EQ(actual.size(),expected.size());
    double error = 0., low = 0., high = 0.;
    for(int i=0;i<actual.size();++i)
    {
        error = std::max(error,std::abs(actual[i].toDouble()-expected[i].toDouble()));
        low = std::min(low,expected[i].toDouble()); high = std::max(high,expected[i].toDouble());
    }
    EXPECT_GT(high-low,1e-8); EXPECT_LE(error,1e-12);
    double somaError = 0.;
    if(fixture.contains("actual_input"))
    {
        EXPECT_EQ(inputs,fixture["actual_input"].toArray());
        if(fixture.contains("time_s")) EXPECT_EQ(clock,fixture["time_s"].toArray());
        const auto expectedSoma=fixture["soma"].toArray();ASSERT_EQ(soma.size(),expectedSoma.size());
        for(int i=0;i<soma.size();++i)
            somaError=std::max(somaError,std::abs(soma[i].toDouble()-expectedSoma[i].toDouble()));
        EXPECT_LE(somaError,1e-12);
    }
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(expectedIdentity,model,ports)["match"].toBool());
    const char* output = std::getenv("TIMELEARNER_ARCHIVE_CHILD_OUTPUT");
    if(output) Write(QString::fromLocal8Bit(output), QJsonObject{{"max_pairwise_error",error},{"samples",actual.size()},
        {"identity",NmsdkTools::IdentifyModel(model,ports)},{"waveform",actual},
        {"actual_input",inputs},{"soma",soma},{"time_s",clock},{"max_soma_pairwise_error",somaError},
        {"kind","native_model_archive_transfer_observation"},{"schema_version",1},{"complete",true}});
    dynamic_pointer_cast<UNet>(model)->BreakLinks();
    model->Free(); // Release boundary bindings before returning the external source.
    core.storage->ReturnObject(model);
    if(boundary) core.storage->ReturnObject(boundary);
}

class NativeArchive : public ::testing::TestWithParam<unsigned int> {};
void TransferFixture(unsigned int frequency, bool withBoundary, bool precise = false, bool withMatrix = false,
                     bool useGateOutput = false)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    const char* phase = "prepare";
    try {
    auto model = Prepared(frequency,precise,withMatrix);
    UEPtr<NConstGenerator> boundary;
    NmsdkTools::ModelBoundarySources ports;
    if(withBoundary)
    {
        boundary = dynamic_pointer_cast<NConstGenerator>(core.storage->TakeObject("NPNeuronPosCGenerator"));
        ASSERT_TRUE(boundary); boundary->SetEnvironment(core.environment); boundary->Init();
        boundary->Name = "OriginalTrainingSource";
        ports[&boundary->Output] = "training_burst";
        ConnectBoundary(model,boundary.Get());
        EXPECT_FALSE(NmsdkTools::IdentifyModel(model)["valid"].toBool());
    }
    phase = "export";
    auto archive = NmsdkTools::ExportModelArchive(model,Metadata(),ports);
    ASSERT_GT(archive["class_definitions"].toArray().size(),0);
    phase = "waveform";
    QJsonArray inputs,soma,clock;
    const auto waveform = Waveform(model,frequency,boundary.Get(),&inputs,&soma,&clock);
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(archive["graph"].toObject()["identity"].toObject(),model,ports)["match"].toBool());
    QJsonObject fixture{{"archive",archive},{"frequency_hz",int(frequency)},{"waveform",waveform},
        {"actual_input",inputs},{"soma",soma},{"time_s",clock},
        {"kind","native_model_archive_transfer_fixture"},{"schema_version",1},
        {"complete",true},{"window_begin_s",0.0},{"window_end_s",.1}};
    if(withBoundary) fixture["stimulus_port"] = "training_burst";
    phase = "child";
    QTemporaryDir temporary; ASSERT_TRUE(temporary.isValid());
    QString directory = temporary.path();
    if(const char* artifacts = std::getenv("TIMELEARNER_ARCHIVE_TEST_DIR"))
    {
        directory = QString::fromLocal8Bit(artifacts); std::filesystem::create_directories(directory.toStdString());
    }
    if(useGateOutput)
        if(const char* artifacts = std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            directory = QString::fromLocal8Bit(artifacts); std::filesystem::create_directories(directory.toStdString());
        }
    const QString prefix = QString(useGateOutput ? "/telemetry-matrix-precise-" : withMatrix ? "/matrix-precise-" : precise ? "/precise-" : "/") + (withBoundary ? "boundary-" : "archive-");
    const auto input = directory + prefix + "fixture-" + QString::number(frequency) + ".json";
    const auto output = directory + prefix + "import-verification-" + QString::number(frequency) + ".json";
    Write(input,fixture);
    QProcess child; auto environment = QProcessEnvironment::systemEnvironment();
    // InitEngine reserves <execution-output>.test-events-log exclusively per
    // process. A native-gate child must not inherit its parent's occupied path.
    // Keep both child artifacts and its native EventsLog inside this run.
    const auto childOutput = directory + prefix + "child-" + QString::number(frequency);
    ASSERT_TRUE(std::filesystem::create_directory(childOutput.toStdString()));
    environment.insert("TIMELEARNER_EXECUTION_OUTPUT",childOutput);
    environment.insert("TIMELEARNER_COMPOSITE_OUTPUT",childOutput + "/native-composite");
    environment.insert("TIMELEARNER_ARCHIVE_CHILD_INPUT",input); environment.insert("TIMELEARNER_ARCHIVE_CHILD_OUTPUT",output);
    child.setProcessEnvironment(environment);
    child.setProgram(QString::fromStdString(NmsdkTests::PulseLibTestExecutable()));
    child.setArguments({"--gtest_filter=TimeLearnerModelArchive.FreshProcessImport"});
    child.setProcessChannelMode(QProcess::MergedChannels); child.start();
    ASSERT_TRUE(child.waitForStarted(10000));
    if(!child.waitForFinished(60000)) { child.kill(); child.waitForFinished(5000); FAIL() << "owned archive child timed out"; }
    const auto log = child.readAll();
    EXPECT_EQ(child.exitStatus(),QProcess::NormalExit) << log.constData();
    EXPECT_EQ(child.exitCode(),0) << log.constData();
    if(child.exitCode()==0) EXPECT_LE(Read(output)["max_pairwise_error"].toDouble(),1e-12);
    model->BreakLinks(); model->Free(); core.storage->ReturnObject(model);
    if(boundary) core.storage->ReturnObject(boundary);
    }
    catch(const RDK::UException& error) { FAIL() << phase << ": " << typeid(error).name() << ": " << error.what(); }
    catch(const std::exception& error) { FAIL() << phase << ": " << error.what(); }
}
TEST_P(NativeArchive, TransfersImagesAndAsymmetricModelIntoFreshNativeProcess) { TransferFixture(GetParam(),false); }
TEST_P(NativeArchive, TransfersDeclaredExternalStimulusIntoFreshNativeProcess) { TransferFixture(GetParam(),true); }
TEST_P(NativeArchive, TransfersHighPrecisionStorageAndLearnedStateIntoFreshNativeProcess) { TransferFixture(GetParam(),false,true); }
TEST_P(NativeArchive, TransfersHighPrecisionStateAndExternalStimulusIntoFreshNativeProcess) { TransferFixture(GetParam(),true,true); }
TEST_P(NativeArchive, TransfersHighPrecisionMatrixIntoFreshNativeProcess) { TransferFixture(GetParam(),false,true,true); }
TEST_P(NativeArchive, TransfersHighPrecisionMatrixAndExternalStimulusIntoFreshNativeProcess) { TransferFixture(GetParam(),true,true,true); }
INSTANTIATE_TEST_SUITE_P(SingleRate,NativeArchive,::testing::Values(2000u,20000u));

void TelemetryFixture(unsigned int frequency)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = Prepared(frequency,true,true);
    auto channel = model->GetComponentL<NPulseChannel>("Dendrite2_3.ExcChannel",true);
    ASSERT_TRUE(channel);
    model->MaxCalculationDuration = 234567LL;
    channel->CalculationDurationThreshold = 345678LL;
    const auto before = NmsdkTools::ExportModelArchive(model,Metadata());
    model->StepDuration = 123456789ULL;
    channel->StepDuration = 987654321ULL;
    const auto after = NmsdkTools::ExportModelArchive(model,Metadata());
    // Compare the entire live graph snapshot, including retained bindings and
    // state. Separate image instances can have different transient buffers;
    // physical archives intentionally are not dynamic checkpoints of images.
    EXPECT_EQ(before["graph"],after["graph"]);
    EXPECT_EQ(NmsdkTools::ModelImageDefinitionsFingerprint(before["class_definitions"].toArray()),
              NmsdkTools::ModelImageDefinitionsFingerprint(after["class_definitions"].toArray()));
    EXPECT_EQ(model->StepDuration.GetData(),123456789ULL);
    EXPECT_EQ(channel->StepDuration.GetData(),987654321ULL);
    EXPECT_EQ(model->MaxCalculationDuration.GetData(),234567LL);
    EXPECT_EQ(channel->CalculationDurationThreshold.GetData(),345678LL);

    // Older signed XML with measured counters remains readable. This is a
    // physical import; retaining transient timing is not a checkpoint promise.
    auto legacy = before; auto graph = legacy["graph"].toObject(); USerStorageXML xml;
    ASSERT_TRUE(xml.Load(graph["native_xml"].toString().toStdString(),"TimeLearnerNativeGraph"));
    ASSERT_TRUE(xml.SelectNode(model->GetName())); ASSERT_TRUE(xml.SelectNode("State"));
    ASSERT_TRUE(xml.SelectNode("StepDuration")); ASSERT_TRUE(xml.SetNodeText("13579"));
    std::string bytes; ASSERT_TRUE(xml.Save(bytes));
    graph["native_xml"] = QString::fromStdString(bytes);
    graph["native_xml_sha256"] = QString::fromLatin1(QCryptographicHash::hash(QByteArray::fromStdString(bytes),QCryptographicHash::Sha256).toHex());
    legacy["graph"] = graph; Seal(legacy);
    auto imported = NmsdkTools::ImportModelArchive(legacy,core.storage,core.environment,"native-archive-fixture-v1");
    ASSERT_TRUE(imported);
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(graph["identity"].toObject(),imported)["match"].toBool());
    EXPECT_EQ(imported->MaxCalculationDuration.GetData(),234567LL);
    EXPECT_EQ(imported->GetComponentL<NPulseChannel>("Dendrite2_3.ExcChannel",true)->CalculationDurationThreshold.GetData(),345678LL);
    const auto normalized = NmsdkTools::ExportModelArchive(imported,Metadata());
    EXPECT_EQ(normalized["graph"].toObject()["identity"],before["graph"].toObject()["identity"]);
    USerStorageXML normalizedXml;
    ASSERT_TRUE(normalizedXml.Load(normalized["graph"].toObject()["native_xml"].toString().toStdString(),"TimeLearnerNativeGraph"));
    ASSERT_TRUE(normalizedXml.SelectNode(imported->GetName())); ASSERT_TRUE(normalizedXml.SelectNode("State"));
    ASSERT_TRUE(normalizedXml.SelectNode("StepDuration")); EXPECT_EQ(normalizedXml.GetNodeText(),"0");

    model->MaxCalculationDuration = 234568LL;
    const auto changedLimit = NmsdkTools::ExportModelArchive(model,Metadata());
    EXPECT_NE(changedLimit["graph"].toObject()["identity"],before["graph"].toObject()["identity"]);
    EXPECT_NE(changedLimit["sha256"],before["sha256"]);
    if(const char* output = std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        std::filesystem::create_directories(output);
        Write(QString::fromLocal8Bit(output)+"/telemetry-witness-"+QString::number(frequency)+".json",
            QJsonObject{{"kind","native_archive_telemetry_witness"},{"schema_version",1},
            {"frequency_hz",int(frequency)},{"before",before},{"after",after},{"legacy",legacy},
            {"normalized",normalized},{"changed_limit",changedLimit},
            {"live_root_duration",QString::number(qulonglong(model->StepDuration.GetData()))},
            {"live_channel_duration",QString::number(qulonglong(channel->StepDuration.GetData()))}});
    }
    core.storage->ReturnObject(imported); core.storage->ReturnObject(model);
    // Actual asymmetric matrix/boundary reconstruction in a separate process,
    // with complete actual-input, time, channel and soma arrays saved by gate.
    TransferFixture(frequency,true,true,true,true);
}
TEST(NativeArchiveTelemetry,At2000) { TelemetryFixture(2000); }
TEST(NativeArchiveTelemetry,At20000) { TelemetryFixture(20000); }

TEST(TimeLearnerModelArchive, BoundaryMustBeDeclaredUsedAndReboundByStableId)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = Prepared(2000);
    auto source = dynamic_pointer_cast<NConstGenerator>(core.storage->TakeObject("NPNeuronPosCGenerator"));
    auto replacement = dynamic_pointer_cast<NConstGenerator>(core.storage->TakeObject("NPNeuronPosCGenerator"));
    ASSERT_TRUE(source); ASSERT_TRUE(replacement);
    source->SetEnvironment(core.environment); source->Init();
    replacement->SetEnvironment(core.environment); replacement->Init();
    NmsdkTools::ModelBoundarySources ports{{&source->Output,"burst"}};
    EXPECT_FALSE(NmsdkTools::IdentifyModel(model,ports)["valid"].toBool()); // unused declaration
    ConnectBoundary(model,source.Get());
    const auto identity = NmsdkTools::IdentifyModel(model,ports);
    ASSERT_TRUE(identity["valid"].toBool()) << QJsonDocument(identity).toJson().constData();
    source->Output.Assign(1,1,17.); // A sampled stimulus is not model identity.
    EXPECT_EQ(identity["sha256"],NmsdkTools::IdentifyModel(model,ports)["sha256"]);
    auto duplicate = ports; duplicate[&replacement->Output] = "burst";
    EXPECT_FALSE(NmsdkTools::IdentifyModel(model,duplicate)["valid"].toBool());
    EXPECT_FALSE(NmsdkTools::IdentifyModel(model,{{nullptr,"burst"}})["valid"].toBool());
    const auto listeners = source->GetNumAConnectors("Output");
    auto archive = NmsdkTools::ExportModelArchive(model,Metadata(),ports);
    EXPECT_DOUBLE_EQ(source->Output(0,0),17.);
    EXPECT_EQ(source->GetNumAConnectors("Output"),listeners);
    EXPECT_TRUE(source->IsReady()); EXPECT_TRUE(source->IsInit());
    EXPECT_THROW(NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"native-archive-fixture-v1"),NmsdkTools::ModelArchiveError);
    EXPECT_THROW(NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"native-archive-fixture-v1",{{&replacement->Output,"wrong"}}),NmsdkTools::ModelArchiveError);
    auto restored = NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"native-archive-fixture-v1",{{&replacement->Output,"burst"}});
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(identity,restored,{{&replacement->Output,"burst"}})["match"].toBool());
    EXPECT_FALSE(NmsdkTools::VerifyModelIdentity(identity,restored,ports)["match"].toBool());
    const auto trace = Waveform(restored,2000,replacement.Get());
    EXPECT_EQ(trace.size(),200);
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(identity,model,ports)["match"].toBool());
    dynamic_pointer_cast<UNet>(restored)->BreakLinks(); restored->Free(); core.storage->ReturnObject(restored);
    model->BreakLinks(); model->Free(); core.storage->ReturnObject(model);
    core.storage->ReturnObject(replacement); core.storage->ReturnObject(source);
}

TEST(TimeLearnerModelArchive, RejectsMalformedArchiveBeforeRegistration)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = Prepared(2000); const auto archive = NmsdkTools::ExportModelArchive(model,Metadata());
    const auto classes = core.storage->GetNumClasses();
    auto corrupt = archive; corrupt["schema_version"] = 2;
    EXPECT_THROW(NmsdkTools::ImportModelArchive(corrupt,core.storage,core.environment,"native-archive-fixture-v1"),NmsdkTools::ModelArchiveError);
    corrupt = archive; corrupt["sha256"] = QString(64,'0');
    EXPECT_THROW(NmsdkTools::ImportModelArchive(corrupt,core.storage,core.environment,"native-archive-fixture-v1"),NmsdkTools::ModelArchiveError);
    EXPECT_THROW(NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"another-implementation"),NmsdkTools::ModelArchiveError);
    corrupt = archive; auto definitions = corrupt["class_definitions"].toArray(); definitions.removeAt(0);
    corrupt["class_definitions"] = definitions; Seal(corrupt);
    EXPECT_THROW(NmsdkTools::ImportModelArchive(corrupt,core.storage,core.environment,"native-archive-fixture-v1"),NmsdkTools::ModelArchiveError);
    corrupt = archive; auto graph = corrupt["graph"].toObject(); graph["native_xml"] = "corrupt"; corrupt["graph"] = graph; Seal(corrupt);
    EXPECT_THROW(NmsdkTools::ImportModelArchive(corrupt,core.storage,core.environment,"native-archive-fixture-v1"),NmsdkTools::ModelArchiveError);
    EXPECT_EQ(core.storage->GetNumClasses(),classes);
    auto imported = NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"native-archive-fixture-v1");
    ASSERT_TRUE(imported);
    core.storage->ReturnObject(imported); core.storage->ReturnObject(model);
}

void RejectInconsistentExistingImagePhysics(const QString& imageName)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    auto model = Prepared(2000);
    const auto identity = NmsdkTools::IdentifyModel(model);
    auto archive = NmsdkTools::ExportModelArchive(model,Metadata());
    auto definitions = archive["class_definitions"].toArray();
    bool changed = false;
    for(int i = 0; i < definitions.size(); ++i)
    {
        auto definition = definitions[i].toObject();
        if(definition["name"].toString() != imageName) continue;
        ASSERT_TRUE(core.storage->CheckClass(imageName.toStdString()));
        auto snapshot = definition["snapshot"].toObject();
        USerStorageXML xml;
        ASSERT_TRUE(xml.Load(snapshot["native_xml"].toString().toStdString(),"TimeLearnerNativeGraph"));
        ASSERT_TRUE(xml.SelectNode(snapshot["component_name"].toString().toStdString()));
        ASSERT_TRUE(xml.SelectNode("Parameters"));
        ASSERT_TRUE(xml.SelectNode("Capacity"));
        bool valid = false;
        const double capacity = QString::fromStdString(xml.GetNodeText()).toDouble(&valid);
        ASSERT_TRUE(valid && std::isfinite(capacity) && capacity > 0.);
        ASSERT_TRUE(xml.SetNodeText(QString::number(2. * capacity,'g',17).toStdString()));
        xml.SelectRoot();
        std::string bytes;
        ASSERT_TRUE(xml.Save(bytes));
        snapshot["native_xml"] = QString::fromStdString(bytes);
        snapshot["native_xml_sha256"] = QString::fromLatin1(QCryptographicHash::hash(
            QByteArray::fromStdString(bytes),QCryptographicHash::Sha256).toHex());
        // Keep the declared identity unchanged: all file hashes are valid, but
        // the native XML describes different physics. Existing registration
        // must not make this contradictory document acceptable.
        definition["snapshot"] = snapshot;
        definitions[i] = definition;
        changed = true;
        break;
    }
    ASSERT_TRUE(changed) << imageName.toStdString();
    archive["class_definitions"] = definitions;
    Seal(archive);
    const auto classes = core.storage->GetNumClasses();
    if(const char* output = std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        std::filesystem::create_directories(output);
        Write(QString::fromLocal8Bit(output) + "/contradictory-image-" + imageName + ".json",archive);
    }
    ExpectImportFailure(archive,"archive_model_mismatch");
    EXPECT_EQ(core.storage->GetNumClasses(),classes);
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(identity,model)["match"].toBool());
    model->BreakLinks();
    model->Free();
}

TEST(TimeLearnerModelArchive, RejectsContradictoryNativeImageXmlWithExistingClass)
{ RejectInconsistentExistingImagePhysics("NPChannel"); }

TEST(TimeLearnerModelArchive, RejectsContradictoryDerivedImageXmlWithExistingClass)
{ RejectInconsistentExistingImagePhysics("NPExcChannelBio"); }

TEST(TimeLearnerModelArchive, RejectsLostGraphInformationEvenWithUpdatedFileHashes)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests(); auto model = Prepared(2000);
    auto archive = NmsdkTools::ExportModelArchive(model,Metadata());
    const auto classes = core.storage->GetNumClasses();
    ExpectImportFailure(EditXml(archive,{"Components","Dendrite2_3","Components","ExcSynapse2","Parameters","Resistance"},0),"missing_archive_parameter");
    ExpectImportFailure(EditXml(archive,{"Components","Dendrite2_2"},0),"archive_child_count_mismatch");
    ExpectImportFailure(EditXml(archive,{"Components","Dendrite2_3","Components","ExcSynapse2"},1),"archive_node_class_mismatch");
    EXPECT_EQ(core.storage->GetNumClasses(),classes);
    model->StructureBuildMode = 0;
    ASSERT_TRUE(model->CreateLink("PosGenerator","Output","Dendrite1_1.ExcSynapse1","Input"));
    archive = NmsdkTools::ExportModelArchive(model,Metadata());
    ExpectImportFailure(EditXml(archive,{"Links"},2),"archive_model_mismatch");
    core.storage->ReturnObject(model);
}

TEST(TimeLearnerModelArchive, CalibrationMustMatchActualZoneWithoutInventingAThresholdSignRule)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests(); auto model = Prepared(2000);
    auto metadata = Metadata(); auto calibration = metadata["calibration"].toObject();
    calibration["threshold"] = .123; metadata["calibration"] = calibration;
    EXPECT_THROW(NmsdkTools::ExportModelArchive(model,metadata),NmsdkTools::ModelArchiveError);
    model->GetLTZone()->Threshold = 0.; calibration["threshold"] = 0.; metadata["calibration"] = calibration;
    const auto archive = NmsdkTools::ExportModelArchive(model,metadata);
    auto imported = NmsdkTools::ImportModelArchive(archive,core.storage,core.environment,"native-archive-fixture-v1");
    ASSERT_TRUE(imported); EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(archive["graph"].toObject()["identity"].toObject(),imported)["match"].toBool());
    core.storage->ReturnObject(imported); core.storage->ReturnObject(model);
}

void RepeatedPrivateImageRestRoundtrip(unsigned int frequency)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();
    ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto clock = dynamic_pointer_cast<UNet>(core.environment->GetModel());
    ASSERT_TRUE(clock);
    clock->SetEnvironment(core.environment);
    clock->SetGlobalTimeStep(frequency);
    auto source = Prepared(frequency, true, true);
    ASSERT_TRUE(source);
    EXPECT_EQ(source->GetTimeStep(), frequency);
    const auto before = NmsdkTools::IdentifyModel(source);
    const auto original = NmsdkTools::ExportModelArchive(source, Metadata());
    ASSERT_FALSE(original["class_definitions"].toArray().isEmpty());
    for(int cycle = 0; cycle < 3; ++cycle)
    {
        auto imported = NmsdkTools::ImportModelArchive(original, core.storage, core.environment,
            "native-archive-fixture-v1");
        ASSERT_TRUE(imported) << "cycle=" << cycle;
        const auto again = NmsdkTools::ExportModelArchive(imported, Metadata());
        EXPECT_EQ(again["class_definitions"], original["class_definitions"])
            << "private image rest state must survive native import and pool reuse; cycle=" << cycle;
        EXPECT_EQ(again, original) << "cycle=" << cycle;
        EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(before, imported)["match"].toBool());
        core.storage->ReturnObject(imported);
    }
    EXPECT_EQ(NmsdkTools::IdentifyModel(source), before);
    core.storage->ReturnObject(source);
}

TEST(NativeImageRestSnapshot, RepeatedArchiveAndPoolReuseAt2000)
{
    RepeatedPrivateImageRestRoundtrip(2000);
}

TEST(NativeImageRestSnapshot, RepeatedArchiveAndPoolReuseAt20000)
{
    RepeatedPrivateImageRestRoundtrip(20000);
}
}
