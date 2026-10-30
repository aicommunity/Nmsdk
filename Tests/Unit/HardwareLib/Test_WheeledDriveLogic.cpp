#include <gtest/gtest.h>

#include <QCoreApplication>

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

} // namespace

TEST(WheeledDriveLogicL2, SignedPwm)
{
    EXPECT_EQ(100, RDK::UWheeledDriveLogic::signedPwm(100, 1));
    EXPECT_EQ(-100, RDK::UWheeledDriveLogic::signedPwm(100, 0));
    EXPECT_EQ(255, RDK::UWheeledDriveLogic::signedPwm(400, 1));
}

TEST(WheeledDriveLogicL2, ProcessEdgesApplyAndStop)
{
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 300;
    cmd.rightPwm = 10;
    cmd.leftDir = 2;
    cmd.rightDir = 0;
    bool apply = false, stop = false;
    EXPECT_TRUE(RDK::UWheeledDriveLogic::processEdges(true, false, &cmd, &apply, &stop));
    EXPECT_TRUE(apply);
    EXPECT_FALSE(stop);
    EXPECT_EQ(255, cmd.leftPwm);
    EXPECT_EQ(1, cmd.leftDir);

    EXPECT_TRUE(RDK::UWheeledDriveLogic::processEdges(false, true, &cmd, &apply, &stop));
    EXPECT_TRUE(stop);
    EXPECT_EQ(0, cmd.leftPwm);
    EXPECT_EQ(0, cmd.rightPwm);
}

TEST(WheeledDriveLogicL2, RetransmitInterval)
{
    EXPECT_FALSE(RDK::UWheeledDriveLogic::shouldRetransmit(1000, 900, 200));
    EXPECT_TRUE(RDK::UWheeledDriveLogic::shouldRetransmit(1000, 700, 200));
    EXPECT_FALSE(RDK::UWheeledDriveLogic::shouldRetransmit(1000, 0, 0));
}

TEST(WheeledDriveLogicL2, MotorHubAndStopCommands)
{
    EnsureQtApp();
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 100;
    cmd.rightPwm = 200;
    cmd.leftDir = 1;
    cmd.rightDir = 0;
    const QStringList lines = RDK::UWheeledDriveLogic::buildMotorHubCommands(cmd);
    ASSERT_EQ(4, lines.size());
    EXPECT_TRUE(lines[0].contains(QStringLiteral("MOTOR A DIR 1")));
    EXPECT_TRUE(lines[3].contains(QStringLiteral("MOTOR B 200")));
    EXPECT_EQ(QStringLiteral("MOTOR STOP"), RDK::UWheeledDriveLogic::buildMotorStopCommands().value(0));
}
