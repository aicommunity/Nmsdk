#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>

#include "../../../Libraries/Rdk-HardwareLib/Core/Wheeled/UWheeledDriveLogic.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UWaveshareUgvJsonProtocol.h"

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

TEST(WheeledDriveLogic, MotorHubCommands)
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
    EXPECT_TRUE(lines[1].contains(QStringLiteral("MOTOR A 100")));
    EXPECT_TRUE(lines[2].contains(QStringLiteral("MOTOR B DIR 0")));
    EXPECT_TRUE(lines[3].contains(QStringLiteral("MOTOR B 200")));
}

TEST(WheeledDriveLogic, StopEdgeClearsPwm)
{
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 50;
    bool apply = false, stop = false;
    EXPECT_TRUE(RDK::UWheeledDriveLogic::processEdges(false, true, &cmd, &apply, &stop));
    EXPECT_TRUE(stop);
    EXPECT_EQ(0, cmd.leftPwm);
    EXPECT_EQ(0, cmd.rightPwm);
}

TEST(WheeledRobotEdgesL3, ApplyDriveBuildsMotorHubQueueLines)
{
    EnsureQtApp();
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 90;
    cmd.rightPwm = 110;
    cmd.leftDir = 1;
    cmd.rightDir = 1;
    bool apply = false, stop = false;
    ASSERT_TRUE(RDK::UWheeledDriveLogic::processEdges(true, false, &cmd, &apply, &stop));
    const QStringList queue = RDK::UWheeledDriveLogic::buildMotorHubCommands(cmd);
    ASSERT_EQ(4, queue.size());
    EXPECT_TRUE(queue[1].contains(QStringLiteral("MOTOR A 90")));
    EXPECT_TRUE(queue[3].contains(QStringLiteral("MOTOR B 110")));
}

TEST(WheeledRobotEdgesL3, StopBuildsMotorStop)
{
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 50;
    bool apply = false, stop = false;
    ASSERT_TRUE(RDK::UWheeledDriveLogic::processEdges(false, true, &cmd, &apply, &stop));
    EXPECT_EQ(QStringList{QStringLiteral("MOTOR STOP")},
              RDK::UWheeledDriveLogic::buildMotorStopCommands());
}

TEST(WheeledRobotEdgesL3, WaveRoverApplyDriveJsonContainsT11)
{
    EnsureQtApp();
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 100;
    cmd.rightPwm = 50;
    cmd.leftDir = 1;
    cmd.rightDir = 0;
    const QString json = RDK::UWheeledDriveLogic::buildWaveshareT11Json(cmd);
    EXPECT_TRUE(json.contains(QStringLiteral("\"T\":11")));
    EXPECT_TRUE(json.contains(QStringLiteral("\"L\":100")));
    EXPECT_TRUE(json.contains(QStringLiteral("\"R\":-50")));
    Q_UNUSED(QJsonDocument::fromJson(json.toUtf8()));
}
