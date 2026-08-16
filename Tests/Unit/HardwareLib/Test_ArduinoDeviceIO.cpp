#include <gtest/gtest.h>

#include "Catalog/UHardwareCatalog.h"
#include "Catalog/UHardwareSetup.h"
#include "Devices/UArduinoDevicePinResolver.h"
#include "Devices/UArduinoFirmataBatchBuilder.h"

#include <QCoreApplication>
#include <QDir>

namespace {

QString catalogFixtureRoot()
{
    const QByteArray src = qgetenv("NMSDK_SOURCE_DIR");
    if (!src.isEmpty())
        return QDir(QString::fromLocal8Bit(src)).filePath(QStringLiteral("Libraries/Rdk-HardwareLib/Catalog"));
    return QDir(QCoreApplication::applicationDirPath())
        .absoluteFilePath(QStringLiteral("../../../../Libraries/Rdk-HardwareLib/Catalog"));
}

void loadCatalog()
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));
}

RDK::UHwSetupDocument motorSetup(const QString& shieldId)
{
    RDK::UHwSetupDocument doc;
    doc.board = QStringLiteral("uno");
    doc.firmwareId = QStringLiteral("standard_firmata");
    doc.stack.append(shieldId);
    return doc;
}

} // namespace

TEST(PinResolver, MotorR3_ChannelA)
{
    loadCatalog();
    const auto doc = motorSetup(QStringLiteral("motor_shield_r3"));
    const auto pins = RDK::UArduinoDevicePinResolver::resolve(
        RDK::UHardwareCatalog::instance(), &doc, QStringLiteral("dc_motor_channel"), QString(),
        QStringLiteral("A"), 0);
    EXPECT_TRUE(pins.error.isEmpty()) << pins.error.toStdString();
    EXPECT_EQ(pins.dirPin, 12);
    EXPECT_EQ(pins.pwmPin, 3);
    EXPECT_EQ(pins.brakePin, 9);
    EXPECT_EQ(pins.sensePin, 14);
}

TEST(PinResolver, Seeed_NotR3)
{
    loadCatalog();
    const auto r3 = motorSetup(QStringLiteral("motor_shield_r3"));
    const auto seeed = motorSetup(QStringLiteral("motor_shield_seeed_v1"));
    const auto a = RDK::UArduinoDevicePinResolver::resolve(
        RDK::UHardwareCatalog::instance(), &r3, QStringLiteral("dc_motor_channel"), QString(),
        QStringLiteral("A"), 0);
    const auto b = RDK::UArduinoDevicePinResolver::resolve(
        RDK::UHardwareCatalog::instance(), &seeed, QStringLiteral("dc_motor_channel"), QString(),
        QStringLiteral("A"), 0);
    EXPECT_NE(a.dirPin, b.dirPin);
    EXPECT_EQ(b.dirPin, 8);
    EXPECT_EQ(b.pwmPin, 9);
}

TEST(PinResolver, SensorShield_D2)
{
    loadCatalog();
    RDK::UHwSetupDocument doc;
    doc.board = QStringLiteral("uno");
    doc.stack.append(QStringLiteral("sensor_shield_v5"));
    const auto pins = RDK::UArduinoDevicePinResolver::resolve(
        RDK::UHardwareCatalog::instance(), &doc, QStringLiteral("relay"), QStringLiteral("D2"),
        QString(), 0);
    EXPECT_TRUE(pins.error.isEmpty());
    EXPECT_EQ(pins.signalPin, 2);
}

TEST(BatchBuilder, PinConfigModes)
{
    RDK::MDMatrix<double> batch;
    RDK::UArduinoFirmataBatchBuilder::clearPinConfig(batch);
    RDK::UArduinoFirmataBatchBuilder::appendPinMode(batch, 13, RDK::UArduinoFirmataBatchBuilder::kModeOutput);
    RDK::UArduinoFirmataBatchBuilder::appendPinMode(batch, 14, RDK::UArduinoFirmataBatchBuilder::kModeAnalog);
    ASSERT_EQ(batch.GetRows(), 2);
    EXPECT_EQ(static_cast<int>(batch(0, 0)), 13);
    EXPECT_EQ(static_cast<int>(batch(0, 1)), 1);
    EXPECT_EQ(static_cast<int>(batch(1, 0)), 14);
    EXPECT_EQ(static_cast<int>(batch(1, 1)), 2);
}

TEST(DeviceIO, DhtUnsupportedOnResolverPath)
{
    loadCatalog();
    const RDK::UHwModuleInfo* mod = RDK::UHardwareCatalog::instance().module(QStringLiteral("dht11"));
    ASSERT_NE(mod, nullptr);
    EXPECT_TRUE(mod->requiresMcuTiming);
}
