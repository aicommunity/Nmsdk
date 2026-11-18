#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSource.h"
#include <QTemporaryDir>
#include <QJsonArray>
#include <QJsonDocument>
#include <vector>
#include <utility>

namespace {
QJsonObject SignJobSource(QJsonObject value)
{value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;}
class NativeJobSourceFixture {
public:
    QTemporaryDir directory;
    QJsonObject package,job,envelope;
    QString path;
    void Write(const QString& name,const QByteArray& bytes)
    {
        QFile file(directory.filePath(name));ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::Truncate));
        ASSERT_EQ(file.write(bytes),bytes.size());ASSERT_TRUE(file.flush());
    }
    void SetUp()
    {
        ASSERT_TRUE(directory.isValid());ASSERT_TRUE(QDir(directory.path()).mkdir("source"));
        package=SignJobSource({{"kind","transport_only_test"},
            {"history",QJsonArray{"retained reference","retained candidate"}}});
        const auto raw=QJsonDocument(package).toJson();Write("source/state.json",raw);
        job=SignJobSource({{"kind","timelearner_native_diagnostic_evaluation_job"},{"schema_version",1},
            {"implementation_id","transport_test"},{"source_stopped",package}});
        auto projection=job;projection.remove("source_stopped");
        envelope=SignJobSource({{"kind","timelearner_checked_file_source_job"},{"schema_version",1},
            {"job",projection},{"source",QJsonObject{{"field","source_stopped"},{"path","source/state.json"},
                {"bytes",double(raw.size())},{"sha256",QString::fromLatin1(QCryptographicHash::hash(raw,QCryptographicHash::Sha256).toHex())},
                {"package_sha256",package["sha256"]}}}});
        path=directory.filePath("job.json");
    }
    QJsonObject Read(QJsonObject value,bool resign=true)
    {
        if(resign)value=SignJobSource(value);
        Write("job.json",QJsonDocument(value).toJson());return NmsdkWorker::ReadNativeJobDocument(path);
    }
};

TEST(NativeJobSourceTransport,LegacyJobAndCompleteFileSourceResolveToTheSameJob)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    EXPECT_EQ(f.Read(f.job),f.job);EXPECT_EQ(f.Read(f.envelope),f.job);
    EXPECT_EQ(f.Read(f.envelope)["source_stopped"].toObject()["history"],f.package["history"]);
}
TEST(NativeJobSourceTransport,AllThreeSourceRolesKeepTheOriginalResolvedDigest)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    for(const auto& role:std::vector<std::pair<QString,QString>>{
        {"timelearner_native_diagnostic_evaluation_job","source_stopped"},
        {"timelearner_native_recognition_export_job","source_solo"},
        {"timelearner_native_evaluation_job","source_recognition"}})
    {
        auto full=f.job;full.remove("source_stopped");full["kind"]=role.first;full[role.second]=f.package;full=SignJobSource(full);
        auto projected=full;projected.remove(role.second);auto changed=f.envelope;changed["job"]=projected;
        auto source=changed["source"].toObject();source["field"]=role.second;changed["source"]=source;
        EXPECT_EQ(f.Read(changed),full);
    }
}
TEST(NativeJobSourceTransport,PhysicalModelExportRetainsTheCompleteSourceState)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    auto full=f.job;full.remove("source_stopped");full["kind"]="timelearner_native_physical_model_export_job";
    full["source_state"]=f.package;full=SignJobSource(full);
    auto projected=full;projected.remove("source_state");auto envelope=f.envelope;envelope["job"]=projected;
    auto source=envelope["source"].toObject();source["field"]="source_state";envelope["source"]=source;
    EXPECT_EQ(f.Read(envelope),full);
}
TEST(NativeJobSourceTransport,PhysicalModelEvaluationRetainsTheCompleteDataSource)
{
    // Transport only: the physical DATA decoder validates the model separately.
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    auto full=f.job;full.remove("source_stopped");full["kind"]="timelearner_native_physical_model_evaluation_job";
    full["source_model_data"]=f.package;full=SignJobSource(full);
    auto projected=full;projected.remove("source_model_data");auto envelope=f.envelope;envelope["job"]=projected;
    auto source=envelope["source"].toObject();source["field"]="source_model_data";envelope["source"]=source;
    EXPECT_EQ(f.Read(envelope),full);
    source["field"]="source_recognition";envelope["source"]=source;
    EXPECT_THROW(f.Read(envelope),std::invalid_argument);
}
TEST(NativeJobSourceTransport,ChangedSourceBytesCannotBeHiddenByEquivalentJsonOrNewEnvelopeSignature)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    f.Write("source/state.json",QJsonDocument(f.package).toJson(QJsonDocument::Compact));
    EXPECT_THROW(f.Read(f.envelope),std::invalid_argument);
}
TEST(NativeJobSourceTransport,ScopeRoleSizeAndPackageDigestFailuresAreRejected)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    const std::vector<std::pair<QString,QJsonValue>> changes{
        {"path","../state.json"},{"path","/absolute/state.json"},{"path","source/../source/state.json"},
        {"field","source_solo"},{"bytes",0},{"bytes",true},
        {"bytes",double(NmsdkWorker::NativeJobSourceMaximumBytes)+1},
        {"sha256",QString(64,'0')},{"package_sha256",QString(64,'0')}};
    for(const auto& change:changes)
    {
        auto changed=f.envelope;auto source=changed["source"].toObject();source[change.first]=change.second;changed["source"]=source;
        EXPECT_THROW(f.Read(changed),std::invalid_argument)<<change.first.toStdString();
    }
}
TEST(NativeJobSourceTransport,ChangedProjectionCannotMintTheOriginalJob)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    auto changed=f.envelope;auto projected=changed["job"].toObject();projected["implementation_id"]="changed";changed["job"]=projected;
    EXPECT_THROW(f.Read(changed),std::invalid_argument);
}
TEST(NativeJobSourceTransport,UnknownEnvelopeFieldsAndColdImportAreRejected)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    auto changed=f.envelope;changed["extra"]=1;EXPECT_THROW(f.Read(changed),std::invalid_argument);
    changed=f.envelope;auto projected=changed["job"].toObject();projected["kind"]="timelearner_native_training_job";changed["job"]=projected;
    EXPECT_THROW(f.Read(changed),std::invalid_argument);
}
#ifndef Q_OS_WIN
TEST(NativeJobSourceTransport,SymlinkSourceCannotReplaceTheOwnedSnapshot)
{
    NativeJobSourceFixture f;f.SetUp();ASSERT_FALSE(::testing::Test::HasFatalFailure());
    ASSERT_TRUE(QFile::link(f.directory.filePath("source/state.json"),f.directory.filePath("source/alias.json")));
    auto changed=f.envelope;auto source=changed["source"].toObject();source["path"]="source/alias.json";changed["source"]=source;
    EXPECT_THROW(f.Read(changed),std::invalid_argument);
}
#endif
}
