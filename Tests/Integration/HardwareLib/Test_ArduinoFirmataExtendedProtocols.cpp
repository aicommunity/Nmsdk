#include <gtest/gtest.h>

#include "ArduinoLiveTestSupport.h"

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UArduinoFirmataClient.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialSession.h"

#include <functional>
#include <QElapsedTimer>
#include <QThread>

namespace {

bool pumpUntil(RDK::UArduinoSerialSession& session, RDK::UArduinoFirmataClient& client, int ms,
               const std::function<bool()>& done)
{
    QElapsedTimer timer;
    timer.start();
    while (timer.elapsed() < ms) {
        QCoreApplication::processEvents();
        const QByteArray chunk = session.takeReceivedBytes();
        if (!chunk.isEmpty())
            client.processIncoming(chunk);
        if (done())
            return true;
        QThread::msleep(10);
    }
    return done();
}

bool handshakeFirmata(RDK::UArduinoSerialSession& session, RDK::UArduinoFirmataClient& client,
                      int board_profile, int timeout_ms = 12000)
{
    client.setBoardProfile(board_profile);
    if (!client.startHandshake(&session, board_profile))
        return false;
    return pumpUntil(session, client, timeout_ms, [&client]() { return client.HandshakeReady; });
}

bool queryPinMode(RDK::UArduinoSerialSession& session, RDK::UArduinoFirmataClient& client, int pin,
                  int expected_mode, int timeout_ms = 3000)
{
    client.PinDeviceModeByPin[pin] = -1;
    if (!client.queryPinState(&session, pin))
        return false;
    return pumpUntil(session, client, timeout_ms, [&client, pin, expected_mode]() {
        return client.deviceModeForPin(pin) == expected_mode;
    });
}

} // namespace

class ArduinoFirmataExtendedProtocols : public ::testing::Test {
protected:
    static QString s_port;
    static int s_boardProfile;

    static void SetUpTestSuite()
    {
        ArduinoLiveTest::EnsureQtApp("arduino_firmata_extended");
        ArduinoLiveTest::EnsureSdkEnv();
        s_boardProfile = ArduinoLiveTest::boardProfileFromEnv();
        s_port = ArduinoLiveTest::detectArduinoPort();
    }

    void SetUp() override
    {
        if (s_port.isEmpty())
            GTEST_SKIP() << "No serial port detected; set ARDUINO_TEST_PORT or connect Arduino";
        if (!ArduinoLiveTest::serialPortAccessible(s_port)) {
            GTEST_SKIP() << "Cannot open " << s_port.toStdString()
                         << " (busy or permission denied)";
        }
    }
};

QString ArduinoFirmataExtendedProtocols::s_port;
int ArduinoFirmataExtendedProtocols::s_boardProfile = 0;

// FirmataTechDebt TD-001: PWM / Servo / I2C on a live board with standard_firmata.
TEST_F(ArduinoFirmataExtendedProtocols, PwmServoI2cCommandPath)
{
    RDK::UArduinoSerialSession session;
    ASSERT_TRUE(session.open(s_port, 57600)) << session.lastError().toStdString();

    RDK::UArduinoFirmataClient client;
    bool ready = handshakeFirmata(session, client, s_boardProfile);
    if (!ready) {
        session.close();
        QString flash_error;
        ASSERT_TRUE(ArduinoLiveTest::flashBundledFirmware(
            s_port, s_boardProfile, QStringLiteral("standard_firmata"), &flash_error))
            << flash_error.toStdString();
        ASSERT_TRUE(session.open(s_port, 57600)) << session.lastError().toStdString();
        ready = handshakeFirmata(session, client, s_boardProfile);
    }
    ASSERT_TRUE(ready) << "Firmata handshake timeout";

    constexpr int kPwmMode = 0x03;
    constexpr int kServoMode = 0x04;

    ASSERT_TRUE(client.setPinMode(&session, 9, kPwmMode));
    ASSERT_TRUE(client.extendedAnalogWrite(&session, 9, 128));
    EXPECT_TRUE(queryPinMode(session, client, 9, kPwmMode))
        << "D9 PWM mode not confirmed; deviceMode=" << client.deviceModeForPin(9);

    ASSERT_TRUE(client.configureServo(&session, 10, 544, 2400));
    ASSERT_TRUE(client.setPinMode(&session, 10, kServoMode));
    ASSERT_TRUE(client.servoWrite(&session, 10, 90));
    EXPECT_TRUE(queryPinMode(session, client, 10, kServoMode))
        << "D10 Servo mode not confirmed; deviceMode=" << client.deviceModeForPin(10);

    // Device may be absent; TX path must succeed.
    EXPECT_TRUE(client.i2cConfig(&session, 0));
    EXPECT_TRUE(client.i2cReadRequest(&session, 0x48, 2));
    pumpUntil(session, client, 500, []() { return false; });

    session.close();
}
