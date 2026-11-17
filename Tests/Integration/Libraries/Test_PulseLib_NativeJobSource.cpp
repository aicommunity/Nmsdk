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
class NativeJobSourceTransport:public ::testing::Test {
protected:
    QTemporaryDir directory;
    QJsonObject package,job,envelope;
    QString path;
    void Write(const QString& name,const QByteArray& bytes)
    {
        QFile file(directory.filePath(name));ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::Truncate));
        ASSERT_EQ(file.write(bytes),bytes.size());ASSERT_TRUE(file.flush());
    }
    void SetUp() override
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

TEST_F(NativeJobSourceTransport,LegacyJobAndCompleteFileSourceResolveToTheSameJob)
{
    EXPECT_EQ(Read(job),job);EXPECT_EQ(Read(envelope),job);
    EXPECT_EQ(Read(envelope)["source_stopped"].toObject()["history"],package["history"]);
}
TEST_F(NativeJobSourceTransport,AllThreeSourceRolesKeepTheOriginalResolvedDigest)
{
    for(const auto& role:std::vector<std::pair<QString,QString>>{
        {"timelearner_native_diagnostic_evaluation_job","source_stopped"},
        {"timelearner_native_recognition_export_job","source_solo"},
        {"timelearner_native_evaluation_job","source_recognition"}})
    {
        auto full=job;full.remove("source_stopped");full["kind"]=role.first;full[role.second]=package;full=SignJobSource(full);
        auto projected=full;projected.remove(role.second);auto changed=envelope;changed["job"]=projected;
        auto source=changed["source"].toObject();source["field"]=role.second;changed["source"]=source;
        EXPECT_EQ(Read(changed),full);
    }
}
TEST_F(NativeJobSourceTransport,ChangedSourceBytesCannotBeHiddenByEquivalentJsonOrNewEnvelopeSignature)
{
    Write("source/state.json",QJsonDocument(package).toJson(QJsonDocument::Compact));
    EXPECT_THROW(Read(envelope),std::invalid_argument);
}
TEST_F(NativeJobSourceTransport,ScopeRoleSizeAndPackageDigestFailuresAreRejected)
{
    const std::vector<std::pair<QString,QJsonValue>> changes{
        {"path","../state.json"},{"path","/absolute/state.json"},{"path","source/../source/state.json"},
        {"field","source_solo"},{"bytes",0},{"bytes",true},
        {"bytes",double(NmsdkWorker::NativeJobSourceMaximumBytes)+1},
        {"sha256",QString(64,'0')},{"package_sha256",QString(64,'0')}};
    for(const auto& change:changes)
    {
        auto changed=envelope;auto source=changed["source"].toObject();source[change.first]=change.second;changed["source"]=source;
        EXPECT_THROW(Read(changed),std::invalid_argument)<<change.first.toStdString();
    }
}
TEST_F(NativeJobSourceTransport,ChangedProjectionCannotMintTheOriginalJob)
{
    auto changed=envelope;auto projected=changed["job"].toObject();projected["implementation_id"]="changed";changed["job"]=projected;
    EXPECT_THROW(Read(changed),std::invalid_argument);
}
TEST_F(NativeJobSourceTransport,UnknownEnvelopeFieldsAndColdImportAreRejected)
{
    auto changed=envelope;changed["extra"]=1;EXPECT_THROW(Read(changed),std::invalid_argument);
    changed=envelope;auto projected=changed["job"].toObject();projected["kind"]="timelearner_native_training_job";changed["job"]=projected;
    EXPECT_THROW(Read(changed),std::invalid_argument);
}
#ifndef Q_OS_WIN
TEST_F(NativeJobSourceTransport,SymlinkSourceCannotReplaceTheOwnedSnapshot)
{
    ASSERT_TRUE(QFile::link(directory.filePath("source/state.json"),directory.filePath("source/alias.json")));
    auto changed=envelope;auto source=changed["source"].toObject();source["path"]="source/alias.json";changed["source"]=source;
    EXPECT_THROW(Read(changed),std::invalid_argument);
}
#endif
}
