#include <gtest/gtest.h>

#include <QCoreApplication>

#include "../../../Libraries/Rdk-HardwareLib/Core/Catalog/UHardwareCatalog.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Devices/UArduinoDevicePinResolver.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoPinMap.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

void EnsureCatalogEnv()
{
    if (qgetenv("NMSDK_SOURCE_DIR").isEmpty())
        qputenv("NMSDK_SOURCE_DIR", QByteArray("/home/user/Nmsdk"));
    if (qgetenv("RDK_HARDWARE_CATALOG_DIR").isEmpty()) {
        qputenv("RDK_HARDWARE_CATALOG_DIR",
                QByteArray("/home/user/Nmsdk/Libraries/Rdk-HardwareLib/Catalog"));
    }
}

} // namespace

TEST(DeviceIOModulePins, JoystickUsesDefaultPortA0)
{
    EnsureQtApp();
    EnsureCatalogEnv();
    RDK::UHardwareCatalog::instance().unload();
    QString err;
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(&err)) << err.toStdString();

    const auto* mod = RDK::UHardwareCatalog::instance().module(QStringLiteral("analog_joystick"));
    ASSERT_NE(nullptr, mod);
    EXPECT_EQ(QStringLiteral("firmata"), mod->runtime);
    EXPECT_EQ(QStringLiteral("A0"), mod->defaultPort);

    const RDK::UResolvedDevicePins pins = RDK::UArduinoDevicePinResolver::resolve(
        RDK::UHardwareCatalog::instance(), nullptr, QStringLiteral("analog_joystick"),
        QString(), QString(), 0);
    EXPECT_TRUE(pins.error.isEmpty()) << pins.error.toStdString();
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("A0"), 0), pins.signalPin);
}

TEST(DeviceIOModulePins, TierAAliasesResolve)
{
    EnsureQtApp();
    EnsureCatalogEnv();
    RDK::UHardwareCatalog::instance().unload();
    QString err;
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(&err)) << err.toStdString();

    for (const auto& id : {QStringLiteral("ldr"), QStringLiteral("soil_moisture"),
                           QStringLiteral("ir_line_tracker"), QStringLiteral("relay")}) {
        const auto* mod = RDK::UHardwareCatalog::instance().module(id);
        ASSERT_NE(nullptr, mod) << id.toStdString();
        EXPECT_EQ(QStringLiteral("firmata"), mod->runtime) << id.toStdString();
        const RDK::UResolvedDevicePins pins = RDK::UArduinoDevicePinResolver::resolve(
            RDK::UHardwareCatalog::instance(), nullptr, id, QString(), QString(), 0);
        EXPECT_TRUE(pins.error.isEmpty()) << id.toStdString() << " " << pins.error.toStdString();
        EXPECT_GE(pins.signalPin, 0) << id.toStdString();
    }
}
