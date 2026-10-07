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

TEST(WaveshareUgvJson, EncodeT11AndParseT1001)
{
    EnsureQtApp();
    const QString t11 = RDK::UWaveshareUgvJsonProtocol::encodePwmInputT11(100, -50);
    const QJsonObject o = QJsonDocument::fromJson(t11.toUtf8()).object();
    EXPECT_EQ(11, o.value(QStringLiteral("T")).toInt());
    EXPECT_EQ(100, o.value(QStringLiteral("L")).toInt());
    EXPECT_EQ(-50, o.value(QStringLiteral("R")).toInt());

    double l = 0, r = 0;
    EXPECT_TRUE(RDK::UWaveshareUgvJsonProtocol::parseFeedbackT1001(
        QStringLiteral("{\"T\":1001,\"L\":0.2,\"R\":-0.1}"), &l, &r, nullptr));
    EXPECT_DOUBLE_EQ(0.2, l);
    EXPECT_DOUBLE_EQ(-0.1, r);
}
