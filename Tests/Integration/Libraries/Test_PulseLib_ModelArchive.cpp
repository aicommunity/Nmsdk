#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/ModelArchive.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
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

UEPtr<NPulseNeuron> Prepared(unsigned int frequency)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    StorageProfileSpec spec; spec.name = "NativeArchiveFixture_" + std::to_string(frequency);
    spec.frequencyHz = frequency; spec.ltMembrane = spec.body;
    spec.ltMembrane->excChannel.capacity = .3e-9;
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
    tip->GetComponentL<NPulseSynapse>("ExcSynapse2",true)->Resistance = 333e6;
    tip->GetComponentL<NPulseChannel>("ExcChannel",true)->Capacity = 1.41e-9;
    return neuron;
}

QJsonArray Waveform(UEPtr<UContainer> neuron, unsigned int frequency)
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
    QJsonArray trace;
    for(unsigned int tick = 0; tick < frequency / 10; ++tick)
    {
        const double time = double(tick) / frequency, stimulus = time >= .005 && time < .006 ? 1. : 0.;
        for(int i = 1; i <= 3; ++i)
        {
            auto synapse = neuron->GetComponentL<NPulseSynapse>("Dendrite2_3.ExcSynapse" + std::to_string(i),true);
            if(!synapse || synapse->Input.IsConnected()) throw std::runtime_error("fixture stimulus port invalid");
            synapse->Input.Assign(1,1,stimulus);
        }
        model->Calculate(); core.environment->IncreaseModelTimeByStep();
        const double value = channel->Output(0,0);
        if(!std::isfinite(value)) throw std::runtime_error("nonfinite archive waveform");
        trace.append(value);
    }
    model->DelComponent(name, false); core.environment->DestroyModel();
    return trace;
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
    auto model = NmsdkTools::ImportModelArchive(archive, core.storage, core.environment, "native-archive-fixture-v1");
    ASSERT_TRUE(model);
    const auto expectedIdentity = archive["graph"].toObject()["identity"].toObject();
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(expectedIdentity, model)["match"].toBool());
    const auto actual = Waveform(model, static_cast<unsigned int>(fixture["frequency_hz"].toInt()));
    const auto expected = fixture["waveform"].toArray(); ASSERT_EQ(actual.size(),expected.size());
    double error = 0., low = 0., high = 0.;
    for(int i=0;i<actual.size();++i)
    {
        error = std::max(error,std::abs(actual[i].toDouble()-expected[i].toDouble()));
        low = std::min(low,expected[i].toDouble()); high = std::max(high,expected[i].toDouble());
    }
    EXPECT_GT(high-low,1e-8); EXPECT_LE(error,1e-12);
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(expectedIdentity,model)["match"].toBool());
    const char* output = std::getenv("TIMELEARNER_ARCHIVE_CHILD_OUTPUT");
    if(output) Write(QString::fromLocal8Bit(output), QJsonObject{{"max_pairwise_error",error},{"samples",actual.size()},
        {"identity",NmsdkTools::IdentifyModel(model)},{"waveform",actual}});
    core.storage->ReturnObject(model);
}

class NativeArchive : public ::testing::TestWithParam<unsigned int> {};
TEST_P(NativeArchive, TransfersImagesAndAsymmetricModelIntoFreshNativeProcess)
{
    const auto& core = NmsdkTests::InitEngineForPulseLibTests();
    const char* phase = "prepare";
    try {
    auto model = Prepared(GetParam());
    phase = "export";
    auto archive = NmsdkTools::ExportModelArchive(model,Metadata());
    ASSERT_GT(archive["class_definitions"].toArray().size(),0);
    phase = "waveform";
    const auto waveform = Waveform(model,GetParam());
    EXPECT_TRUE(NmsdkTools::VerifyModelIdentity(archive["graph"].toObject()["identity"].toObject(),model)["match"].toBool());
    QJsonObject fixture{{"archive",archive},{"frequency_hz",int(GetParam())},{"waveform",waveform}};
    phase = "child";
    QTemporaryDir temporary; ASSERT_TRUE(temporary.isValid());
    QString directory = temporary.path();
    if(const char* artifacts = std::getenv("TIMELEARNER_ARCHIVE_TEST_DIR"))
    {
        directory = QString::fromLocal8Bit(artifacts); std::filesystem::create_directories(directory.toStdString());
    }
    const auto input = directory + "/archive-fixture-" + QString::number(GetParam()) + ".json";
    const auto output = directory + "/import-verification-" + QString::number(GetParam()) + ".json";
    Write(input,fixture);
    QProcess child; auto environment = QProcessEnvironment::systemEnvironment();
    environment.insert("TIMELEARNER_ARCHIVE_CHILD_INPUT",input); environment.insert("TIMELEARNER_ARCHIVE_CHILD_OUTPUT",output);
    child.setProcessEnvironment(environment);
#if defined(_WIN32)
    child.setProgram(QFileInfo("Test_PulseLib_StorageComponents.exe").absoluteFilePath());
#else
    child.setProgram(QFileInfo("Test_PulseLib_StorageComponents").absoluteFilePath());
#endif
    child.setArguments({"--gtest_filter=TimeLearnerModelArchive.FreshProcessImport"});
    child.setProcessChannelMode(QProcess::MergedChannels); child.start();
    ASSERT_TRUE(child.waitForStarted(10000));
    if(!child.waitForFinished(60000)) { child.kill(); child.waitForFinished(5000); FAIL() << "owned archive child timed out"; }
    const auto log = child.readAll();
    EXPECT_EQ(child.exitStatus(),QProcess::NormalExit) << log.constData();
    EXPECT_EQ(child.exitCode(),0) << log.constData();
    if(child.exitCode()==0) EXPECT_LE(Read(output)["max_pairwise_error"].toDouble(),1e-12);
    core.storage->ReturnObject(model);
    }
    catch(const RDK::UException& error) { FAIL() << phase << ": " << typeid(error).name() << ": " << error.what(); }
    catch(const std::exception& error) { FAIL() << phase << ": " << error.what(); }
}
INSTANTIATE_TEST_SUITE_P(SingleRate,NativeArchive,::testing::Values(2000u,20000u));

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
}
