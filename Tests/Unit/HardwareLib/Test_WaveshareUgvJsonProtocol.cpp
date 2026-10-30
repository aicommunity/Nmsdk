#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UWaveshareUgvJsonProtocol.h"
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

TEST(WaveshareUgvJsonL2, EncodeT11Signed)
{
    EnsureQtApp();
    const QString t11 = RDK::UWaveshareUgvJsonProtocol::encodePwmInputT11(100, -50);
    const QJsonObject o = QJsonDocument::fromJson(t11.toUtf8()).object();
    EXPECT_EQ(11, o.value(QStringLiteral("T")).toInt());
    EXPECT_EQ(100, o.value(QStringLiteral("L")).toInt());
    EXPECT_EQ(-50, o.value(QStringLiteral("R")).toInt());
}

TEST(WaveshareUgvJsonL2, EncodeT136AndT130)
{
    EnsureQtApp();
    const QJsonObject hb =
        QJsonDocument::fromJson(RDK::UWaveshareUgvJsonProtocol::encodeHeartbeatT136(2000).toUtf8())
            .object();
    EXPECT_EQ(136, hb.value(QStringLiteral("T")).toInt());
    EXPECT_EQ(2000, hb.value(QStringLiteral("cmd")).toInt());

    const QJsonObject flow =
        QJsonDocument::fromJson(RDK::UWaveshareUgvJsonProtocol::encodeBaseFeedbackFlowT130(1).toUtf8())
            .object();
    EXPECT_EQ(130, flow.value(QStringLiteral("T")).toInt());
    EXPECT_EQ(1, flow.value(QStringLiteral("cmd")).toInt());
}

TEST(WaveshareUgvJsonL2, ParseFeedbackT1001)
{
    EnsureQtApp();
    double l = 0, r = 0;
    EXPECT_TRUE(RDK::UWaveshareUgvJsonProtocol::parseFeedbackT1001(
        QStringLiteral("{\"T\":1001,\"L\":0.2,\"R\":-0.1}"), &l, &r, nullptr));
    EXPECT_DOUBLE_EQ(0.2, l);
    EXPECT_DOUBLE_EQ(-0.1, r);
}

TEST(WaveshareUgvJsonL2, DriveLogicBuildsT11)
{
    EnsureQtApp();
    RDK::UWheeledDriveCommand cmd;
    cmd.leftPwm = 80;
    cmd.rightPwm = 40;
    cmd.leftDir = 1;
    cmd.rightDir = 0;
    const QJsonObject o =
        QJsonDocument::fromJson(RDK::UWheeledDriveLogic::buildWaveshareT11Json(cmd).toUtf8()).object();
    EXPECT_EQ(11, o.value(QStringLiteral("T")).toInt());
    EXPECT_EQ(80, o.value(QStringLiteral("L")).toInt());
    EXPECT_EQ(-40, o.value(QStringLiteral("R")).toInt());
}
