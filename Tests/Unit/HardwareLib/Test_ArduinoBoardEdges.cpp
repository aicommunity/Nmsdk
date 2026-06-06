#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QDir>
#include <QDirIterator>
#include <QFile>

#include "../../../Libraries/Rdk-HardwareLib/Core/UArduinoBoard.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/UArduinoDcDemo.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

class BoardTestHarness : public RDK::UArduinoBoard {
public:
    void initDefaults() { ADefault(); }
    using RDK::UArduinoBoard::ResetEdge;
    using RDK::UArduinoBoard::ProcessBoardEdges;
    using RDK::UArduinoBoard::SyncDerivedStates;
};

class DcDemoHarness : public RDK::UArduinoDcDemo {
public:
    void initDefaults() { ADefault(); }
    using RDK::UArduinoCustomLink::ProcessCustomLinkEdges;
    using RDK::UArduinoDcDemo::OnBinaryFrame;
    using RDK::UArduinoDcDemo::ProcessDcDemoEdges;
};

} // namespace

TEST(ArduinoBoardEdges, ResetEdgeClearsFlag)
{
    bool flag = true;
    BoardTestHarness::ResetEdge(flag);
    EXPECT_FALSE(flag);
}

TEST(ArduinoBoardEdges, ConnectEdgeResetsAfterProcess)
{
    EnsureQtApp();
    BoardTestHarness board;
    board.initDefaults();
    board.PortName = "/dev/ttyNONEXIST_TEST";
    board.Connect = true;
    board.ProcessBoardEdges();
    EXPECT_FALSE(board.Connect);
}

TEST(ArduinoBoardEdges, DisconnectPreservesPortName)
{
    EnsureQtApp();
    BoardTestHarness board;
    board.initDefaults();
    const std::string port = "/dev/ttyACM0";
    board.PortName = port;
    board.Disconnect = true;
    board.ProcessBoardEdges();
    EXPECT_FALSE(board.Disconnect);
    EXPECT_EQ(port, *board.PortName);
    EXPECT_TRUE(board.IsDisconnected);
}

TEST(ArduinoCustomLinkEdges, SendCommandEmptyResetsEdge)
{
    EnsureQtApp();
    DcDemoHarness dc;
    dc.initDefaults();
    dc.SendCommand = true;
    dc.ProcessCustomLinkEdges();
    EXPECT_FALSE(dc.SendCommand);
}

TEST(ArduinoDcDemo, OnBinaryFrameSpeedAndAcceleration)
{
    EnsureQtApp();
    DcDemoHarness dc;
    dc.initDefaults();

    QByteArray payload;
    payload.append(char(0));
    payload.append(char(5));
    const float vals[5] = {1.f, 2.f, 3.f, 40.f, 50.f};
    for (float v : vals)
        payload.append(reinterpret_cast<const char*>(&v), sizeof(float));

    dc.OnBinaryFrame(0x01, payload);
    dc.GetSpeed = true;
    dc.ProcessDcDemoEdges();
    EXPECT_FLOAT_EQ(40.f, static_cast<float>(dc.Speed));
    EXPECT_FLOAT_EQ(50.f, static_cast<float>(dc.Acceleration));
}

TEST(ArduinoThreadingContract, NoBytesReceivedConnectInCore)
{
    const QString coreRoot =
        QString::fromLocal8Bit(qgetenv("NMSDK_ROOT")) + QLatin1String("/Libraries/Rdk-HardwareLib/Core");
    QStringList roots;
    if (QDir(coreRoot).exists())
        roots << coreRoot;
    else
        roots << QStringLiteral("Libraries/Rdk-HardwareLib/Core");

    for (const QString& root : roots) {
        QDirIterator it(root, QStringList() << QStringLiteral("*.cpp"), QDir::Files,
                        QDirIterator::Subdirectories);
        while (it.hasNext()) {
            const QString path = it.next();
            QFile file(path);
            ASSERT_TRUE(file.open(QIODevice::ReadOnly));
            const QString content = QString::fromUtf8(file.readAll());
            if (content.contains(QStringLiteral("connect("))
                && content.contains(QStringLiteral("bytesReceived"))) {
                EXPECT_TRUE(content.contains(QStringLiteral("Do not connect bytesReceived")))
                    << "Unexpected bytesReceived connect in " << path.toStdString();
            }
        }
    }
}
