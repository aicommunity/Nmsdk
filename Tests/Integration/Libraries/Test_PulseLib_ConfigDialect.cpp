#include <gtest/gtest.h>
#include "../Core/Serialize/USerStorageXML.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QFile>
#include <cstdlib>

// External input is produced by the Python production adapter. No learner or
// physical simulation is run: this is a native serialization readback role.
TEST(RdkConfigDialect, ExternalPatchedLeavesReadBackThroughNativeStorage)
{
    const char* request=std::getenv("TIMELEARNER_CONFIG_READBACK");
    if(!request)GTEST_SKIP()<<"external config-adapter readback role";
    QFile description(QString::fromUtf8(request));ASSERT_TRUE(description.open(QIODevice::ReadOnly));
    QJsonParseError error;const auto document=QJsonDocument::fromJson(description.readAll(),&error);
    ASSERT_EQ(error.error,QJsonParseError::NoError);ASSERT_TRUE(document.isObject());
    const auto root=document.object();ASSERT_EQ(root["kind"].toString(),"native_config_readback");
    ASSERT_EQ(root["schema_version"].toInt(),1);const auto cases=root["cases"].toArray();ASSERT_FALSE(cases.isEmpty());
    for(const auto& value:cases)
    {
        const auto record=value.toObject();QFile source(record["file"].toString());
        SCOPED_TRACE(source.fileName().toStdString());
        ASSERT_TRUE(source.open(QIODevice::ReadOnly))<<source.fileName().toStdString();
        const auto bytes=source.readAll();const auto rootName=record["root"].toString().toStdString();
        RDK::USerStorageXML storage;ASSERT_TRUE(storage.Load(std::string(bytes.constData(),bytes.size()),rootName));
        const auto checks=record["checks"].toArray();ASSERT_FALSE(checks.isEmpty());
        for(const auto& item:checks)
        {
            const auto check=item.toObject();storage.SelectRoot();
            for(const auto& name:check["path"].toArray())
            {
                const auto key=name.toString().toStdString();ASSERT_EQ(storage.GetNumNodes(key),1)<<key;
                ASSERT_TRUE(storage.SelectNode(key))<<key;
            }
            EXPECT_EQ(storage.GetNodeText(),check["text"].toString().toStdString());
        }
    }
}
