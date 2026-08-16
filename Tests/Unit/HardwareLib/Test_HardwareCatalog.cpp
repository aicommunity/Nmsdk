#include <gtest/gtest.h>

#include "Catalog/UHardwareCatalog.h"
#include "Catalog/UHardwareSetup.h"

#include <QCoreApplication>
#include <QDir>
#include <QJsonDocument>
#include <QJsonObject>

namespace {

QString catalogFixtureRoot()
{
    const QByteArray src = qgetenv("NMSDK_SOURCE_DIR");
    if (!src.isEmpty())
        return QDir(QString::fromLocal8Bit(src)).filePath(QStringLiteral("Libraries/Rdk-HardwareLib/Catalog"));
    return QDir(QCoreApplication::applicationDirPath())
        .absoluteFilePath(QStringLiteral("../../../../Libraries/Rdk-HardwareLib/Catalog"));
}

} // namespace

TEST(HardwareCatalog, LoadCatalogFromSourceTree)
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    QString err;
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(&err)) << err.toStdString();
    EXPECT_NE(RDK::UHardwareCatalog::instance().board(QStringLiteral("uno")), nullptr);
    EXPECT_NE(RDK::UHardwareCatalog::instance().firmware(QStringLiteral("standard_firmata")), nullptr);
    EXPECT_NE(RDK::UHardwareCatalog::instance().shield(QStringLiteral("sensor_shield_v5")), nullptr);
}

TEST(HardwareCatalog, SetupPinConflict)
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));

    const QByteArray json = R"({
      "schemaVersion": 1,
      "board": "uno",
      "firmwareId": "standard_firmata",
      "stack": ["sensor_shield_v5"],
      "devices": [
        {"id": "a", "module": "potentiometer", "port": "A0", "role": "sensor"},
        {"id": "b", "module": "potentiometer", "port": "A0", "role": "sensor"}
      ]
    })";
    RDK::UHardwareSetup setup;
    ASSERT_TRUE(setup.loadFromJson(json, nullptr));
    QVector<RDK::UHwIssue> issues;
    EXPECT_FALSE(setup.validate(RDK::UHardwareCatalog::instance(), &issues));
    bool found = false;
    for (const auto& i : issues)
        found = found || i.code == QLatin1String("PinConflict");
    EXPECT_TRUE(found);
}

TEST(HardwareCatalog, SetupTimingWarningDhtOnFirmata)
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));

    const QByteArray json = R"({
      "schemaVersion": 1,
      "board": "uno",
      "firmwareId": "standard_firmata",
      "stack": ["sensor_shield_v5"],
      "devices": [
        {"id": "t", "module": "dht11", "port": "D2", "role": "sensor"}
      ]
    })";
    RDK::UHardwareSetup setup;
    ASSERT_TRUE(setup.loadFromJson(json, nullptr));
    QVector<RDK::UHwIssue> issues;
    EXPECT_TRUE(setup.validate(RDK::UHardwareCatalog::instance(), &issues));
    bool found = false;
    for (const auto& i : issues)
        found = found || i.code == QLatin1String("TimingPreferHub");
    EXPECT_TRUE(found);
}

TEST(HardwareCatalog, SetupEmptyOk)
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));
    RDK::UHardwareSetup setup;
    ASSERT_TRUE(setup.loadFromJson(QByteArrayLiteral("{\"schemaVersion\":1,\"board\":\"uno\",\"firmwareId\":\"standard_firmata\",\"stack\":[],\"devices\":[]}"), nullptr));
    QVector<RDK::UHwIssue> issues;
    EXPECT_TRUE(setup.validate(RDK::UHardwareCatalog::instance(), &issues));
}
