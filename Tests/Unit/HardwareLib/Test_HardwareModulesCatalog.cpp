#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

#include "../../../Libraries/Rdk-HardwareLib/Core/Catalog/UHardwareCatalog.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Catalog/UHardwareCatalogPaths.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

} // namespace

TEST(HardwareModulesCatalog, LoadsAtLeastSeventyModules)
{
    EnsureQtApp();
    if (qgetenv("NMSDK_SOURCE_DIR").isEmpty())
        qputenv("NMSDK_SOURCE_DIR", QByteArray("/home/user/Nmsdk"));
    if (qgetenv("NMSDK_ROOT").isEmpty())
        qputenv("NMSDK_ROOT", QByteArray("/home/user/Nmsdk"));

    RDK::UHardwareCatalog::instance().unload();
    QString err;
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(&err)) << err.toStdString();

    EXPECT_NE(nullptr, RDK::UHardwareCatalog::instance().module(QStringLiteral("dht11")));
    EXPECT_NE(nullptr, RDK::UHardwareCatalog::instance().module(QStringLiteral("hc_sr04")));

    const QString root = RDK::UHardwareCatalogPaths::catalogRoot();
    ASSERT_FALSE(root.isEmpty());
    QFile f(QDir(root).filePath(QStringLiteral("catalog.json")));
    ASSERT_TRUE(f.open(QIODevice::ReadOnly));
    const QJsonObject idx = QJsonDocument::fromJson(f.readAll()).object();
    EXPECT_GE(idx.value(QStringLiteral("modules")).toArray().size(), 70);

    for (const auto& id : {QStringLiteral("bme280"), QStringLiteral("vl53l0x"),
                           QStringLiteral("mpu_6050"), QStringLiteral("ina219"),
                           QStringLiteral("pca9685_16_ch_pwm")}) {
        const auto* m = RDK::UHardwareCatalog::instance().module(id);
        ASSERT_NE(nullptr, m) << id.toStdString();
        EXPECT_EQ(QStringLiteral("hub"), m->runtime) << id.toStdString();
    }
    EXPECT_EQ(QStringLiteral("planned"),
              RDK::UHardwareCatalog::instance().module(QStringLiteral("icm_20948"))->runtime);
}
