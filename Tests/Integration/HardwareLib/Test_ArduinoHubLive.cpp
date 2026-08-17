#include <gtest/gtest.h>

#include "ArduinoLiveTestSupport.h"

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UArduinoBinaryStreamParser.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialSession.h"

#include <QElapsedTimer>
#include <QEventLoop>
#include <QStringList>
#include <QThread>
#include <QVector>

namespace {

struct HubFrame {
    uint8_t type = 0;
    QByteArray payload;
};

void sendLine(RDK::UArduinoSerialSession& session, const QByteArray& line)
{
    session.write(line.endsWith('\n') ? line : line + '\n');
}

QVector<HubFrame> collectFrames(RDK::UArduinoSerialSession& session, int wait_ms)
{
    RDK::UArduinoBinaryStreamParser parser;
    parser.setProtocolVersion(2);
    QVector<HubFrame> frames;
    QElapsedTimer timer;
    timer.start();
    while (timer.elapsed() < wait_ms) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 20);
        const QByteArray chunk = session.takeReceivedBytes();
        if (!chunk.isEmpty()) {
            parser.feed(chunk, [&frames](uint8_t type, const QByteArray& payload) {
                frames.append(HubFrame{type, payload});
            });
        }
        QThread::msleep(20);
    }
    return frames;
}

bool hasFrameType(const QVector<HubFrame>& frames, uint8_t type)
{
    for (const HubFrame& frame : frames) {
        if (frame.type == type)
            return true;
    }
    return false;
}

const HubFrame* lastFrameOfType(const QVector<HubFrame>& frames, uint8_t type)
{
    const HubFrame* found = nullptr;
    for (const HubFrame& frame : frames) {
        if (frame.type == type)
            found = &frame;
    }
    return found;
}

bool openHubSession(RDK::UArduinoSerialSession& session, const QString& port)
{
    ArduinoLiveTest::waitForPort(port);
    if (!session.open(port, 57600))
        return false;
    // Mega toggles DTR on open and sits in the bootloader for ~1s.
    QThread::msleep(2500);
    session.takeReceivedBytes();
    return true;
}

QString dumpFrameTypes(const QVector<HubFrame>& frames)
{
    QStringList parts;
    for (const HubFrame& frame : frames)
        parts.append(QStringLiteral("0x%1/%2")
                         .arg(frame.type, 2, 16, QLatin1Char('0'))
                         .arg(frame.payload.size()));
    return parts.isEmpty() ? QStringLiteral("(none)") : parts.join(QLatin1Char(' '));
}

} // namespace

class ArduinoHubLive : public ::testing::Test {
protected:
    static QString s_port;
    static int s_boardProfile;
    static bool s_needRestoreFirmata;

    static void SetUpTestSuite()
    {
        ArduinoLiveTest::EnsureQtApp("arduino_hub_live");
        ArduinoLiveTest::EnsureSdkEnv();
        s_boardProfile = ArduinoLiveTest::boardProfileFromEnv();
        s_port = ArduinoLiveTest::detectArduinoPort();
        s_needRestoreFirmata = false;
    }

    static void TearDownTestSuite()
    {
        if (!s_needRestoreFirmata || s_port.isEmpty())
            return;
        QString error;
        ArduinoLiveTest::flashBundledFirmware(s_port, s_boardProfile,
                                              QStringLiteral("standard_firmata"), &error);
    }

    void SetUp() override
    {
        if (s_port.isEmpty())
            GTEST_SKIP() << "No serial port detected; set ARDUINO_TEST_PORT or connect Arduino";
        if (!ArduinoLiveTest::serialPortAccessible(s_port)) {
            GTEST_SKIP() << "Cannot open " << s_port.toStdString();
        }
        if (RDK::UArduinoFlasher::locateAvrdudeBinary().isEmpty())
            GTEST_SKIP() << "avrdude not found; cannot flash hub HEX";
    }

    bool flashHub(const QString& bundled_id)
    {
        QString error;
        if (!ArduinoLiveTest::flashBundledFirmware(s_port, s_boardProfile, bundled_id, &error)) {
            ADD_FAILURE() << error.toStdString();
            return false;
        }
        s_needRestoreFirmata = true;
        return true;
    }
};

QString ArduinoHubLive::s_port;
int ArduinoHubLive::s_boardProfile = 0;
bool ArduinoHubLive::s_needRestoreFirmata = false;

TEST_F(ArduinoHubLive, SensorHubPingGetPinsAndSetDevice)
{
    ASSERT_TRUE(flashHub(QStringLiteral("nmsdk_sensor_hub_v1")));

    RDK::UArduinoSerialSession session;
    ASSERT_TRUE(openHubSession(session, s_port)) << session.lastError().toStdString();

    sendLine(session, "STOP READING");
    collectFrames(session, 1500);

    sendLine(session, "PING");
    const QVector<HubFrame> ping_frames = collectFrames(session, 4000);
    EXPECT_TRUE(hasFrameType(ping_frames, 0x7F))
        << "No PONG 0x7F after PING; frames=" << dumpFrameTypes(ping_frames).toStdString();

    sendLine(session, "GET PINS");
    const QVector<HubFrame> pin_frames = collectFrames(session, 2500);
    const HubFrame* pins = lastFrameOfType(pin_frames, 0x22);
    ASSERT_NE(pins, nullptr) << "No GET PINS frame 0x22";
    ASSERT_GE(pins->payload.size(), 4);

    sendLine(session, "SET DEVICE hall A3");
    const QVector<HubFrame> rebound = collectFrames(session, 2500);
    const HubFrame* after = lastFrameOfType(rebound, 0x22);
    ASSERT_NE(after, nullptr) << "No pin map after SET DEVICE hall A3";
    ASSERT_GE(after->payload.size(), 4);
    const int hall = static_cast<uint8_t>(after->payload.at(3));
    EXPECT_NE(hall, static_cast<uint8_t>(pins->payload.at(3)))
        << "hall pin did not change after SET DEVICE";
    EXPECT_GT(hall, 0);

    sendLine(session, "CLEAR DEVICES");
    collectFrames(session, 1500);
    session.close();
}

TEST_F(ArduinoHubLive, MotorHubPingStopWatchdogGetPins)
{
    ASSERT_TRUE(flashHub(QStringLiteral("nmsdk_motor_hub_v1")));

    RDK::UArduinoSerialSession session;
    ASSERT_TRUE(openHubSession(session, s_port)) << session.lastError().toStdString();

    sendLine(session, "STOP READING");
    collectFrames(session, 1500);

    sendLine(session, "PING");
    const QVector<HubFrame> ping_frames = collectFrames(session, 4000);
    EXPECT_TRUE(hasFrameType(ping_frames, 0x7F))
        << "No PONG 0x7F after PING; frames=" << dumpFrameTypes(ping_frames).toStdString();

    sendLine(session, "MOTOR STOP");
    sendLine(session, "WATCHDOG 500");
    QThread::msleep(50);
    sendLine(session, "GET PINS");
    const QVector<HubFrame> pin_frames = collectFrames(session, 3000);
    EXPECT_TRUE(hasFrameType(pin_frames, 0x21))
        << "No GET PINS frame 0x21; frames=" << dumpFrameTypes(pin_frames).toStdString();

    session.close();
}
