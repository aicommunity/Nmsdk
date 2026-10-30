#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QDir>

#include "../../../Libraries/Rdk-HardwareLib/Core/Catalog/UHardwareCatalog.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Wheeled/UWheeledDriveLogic.h"
#include "HardwareTestPaths.h"

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

TEST(MotorDriverSetPinL2, MotorShieldR3EmitsDirPwm)
{
    EnsureQtApp();
    HardwareTestPaths::ensureCatalogEnvironment(__FILE__);
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
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A dir2 NONE")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A enable NONE")));
}

TEST(MotorDriverSetPinL2, L298NUsesTwoDirectionPinsAndPwm)
{
    EnsureQtApp();
    HardwareTestPaths::ensureCatalogEnvironment(__FILE__);
    RDK::UHardwareCatalog::instance().unload();
    QString err;
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(&err)) << err.toStdString();

    const auto* shield = RDK::UHardwareCatalog::instance().shield(QStringLiteral("wire_l298n"));
    ASSERT_NE(nullptr, shield);
    EXPECT_EQ(QStringLiteral("dir2_pwm"), shield->controlModel);
    const QStringList lines =
        RDK::UWheeledDriveLogic::buildSetPinCommands(QStringLiteral("wire_l298n"));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A dir D2")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A dir2 D4")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN A pwm D5")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN B dir2 D8")));
    EXPECT_TRUE(lines.contains(QStringLiteral("SET PIN B brake NONE")));
}

TEST(MotorDriverSetPinL2, EmptyIdYieldsNoCommands)
{
    EnsureQtApp();
    EXPECT_TRUE(RDK::UWheeledDriveLogic::buildSetPinCommands(QString()).isEmpty());
}
