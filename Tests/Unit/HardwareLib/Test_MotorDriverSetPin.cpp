#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QDir>

#include "../../../Libraries/Rdk-HardwareLib/Core/Catalog/UHardwareCatalog.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Wheeled/UWheeledDriveLogic.h"

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

TEST(MotorDriverSetPinL2, MotorShieldR3EmitsDirPwm)
{
    EnsureQtApp();
    EnsureCatalogEnv();
    RDK::UHardwareCatalog::instance().unload();
    QString err;
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(&err)) << err.toStdString();

    const auto* shield = RDK::UHardwareCatalog::instance().shield(QStringLiteral("motor_shield_r3"));
    ASSERT_NE(nullptr, shield);
    EXPECT_TRUE(shield->compatibleBoards.contains(QStringLiteral("uno")));

    const QStringList lines =
        RDK::UWheeledDriveLogic::buildSetPinCommands(QStringLiteral("motor_shield_r3"));
    ASSERT_GE(lines.size(), 4);
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A dir D12")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A pwm D3")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN B dir D13")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN B pwm D11")));
}

TEST(MotorDriverSetPinL2, EmptyIdYieldsNoCommands)
{
    EnsureQtApp();
    EXPECT_TRUE(RDK::UWheeledDriveLogic::buildSetPinCommands(QString()).isEmpty());
}
