#include <gtest/gtest.h>

#include "../../../Libraries/Rdk-HardwareLib/Core/Board/UFirmwareManifest.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Catalog/UHardwareCatalog.h"

#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>

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

TEST(FirmwareManifest, CatalogRelativePathBeforeLegacy)
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));

    const QString rel =
        RDK::UFirmwareManifest::bundledHexRelativePath(QStringLiteral("standard_firmata"),
                                                       QStringLiteral("uno"));
    ASSERT_FALSE(rel.isEmpty());
    EXPECT_TRUE(rel.contains(QStringLiteral("firmata")));
    EXPECT_TRUE(rel.contains(QStringLiteral("standard_firmata")));
}

TEST(FirmwareManifest, HubIdsPresentInCatalog)
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));
    const RDK::UHwFirmwareInfo* sensor =
        RDK::UHardwareCatalog::instance().firmware(QStringLiteral("nmsdk_sensor_hub_v1"));
    const RDK::UHwFirmwareInfo* motor =
        RDK::UHardwareCatalog::instance().firmware(QStringLiteral("nmsdk_motor_hub_v1"));
    ASSERT_NE(sensor, nullptr);
    ASSERT_NE(motor, nullptr);
    EXPECT_TRUE(sensor->available);
    EXPECT_TRUE(motor->available);
    EXPECT_FALSE(sensor->hex.value(QStringLiteral("uno")).isEmpty());
    EXPECT_FALSE(motor->hex.value(QStringLiteral("uno")).isEmpty());
}
