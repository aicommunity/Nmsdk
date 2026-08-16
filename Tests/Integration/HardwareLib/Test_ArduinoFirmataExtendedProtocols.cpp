#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QElapsedTimer>
#include <QThread>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UArduinoFirmataClient.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialSession.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "arduino_firmata_extended";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

bool envFlagEnabled(const char* name)
{
    const QByteArray v = qgetenv(name);
    if (v.isEmpty())
        return false;
    return v == "1" || v.toLower() == "true" || v.toLower() == "yes";
}

bool pumpFirmata(RDK::UArduinoSerialSession& session, RDK::UArduinoFirmataClient& client, int ms)
{
    QElapsedTimer timer;
    timer.start();
    while (timer.elapsed() < ms) {
        QCoreApplication::processEvents();
        const QByteArray chunk = session.takeReceivedBytes();
        if (!chunk.isEmpty())
            client.processIncoming(chunk);
        if (client.HandshakeReady)
            return true;
        QThread::msleep(10);
    }
    return client.HandshakeReady;
}

} // namespace

// FirmataTechDebt TD-001: PWM / Servo / I2C on a live board with standard_firmata.
TEST(ArduinoFirmataExtendedProtocols, SkipsWithoutHardwareFlag)
{
    EnsureQtApp();
    if (!envFlagEnabled("ARDUINO_TEST_EXTENDED"))
        GTEST_SKIP() << "Set ARDUINO_TEST_EXTENDED=1 and ARDUINO_TEST_PORT to run PWM/Servo/I2C on hardware";

    const QByteArray port = qgetenv("ARDUINO_TEST_PORT");
    if (port.isEmpty())
        GTEST_SKIP() << "ARDUINO_TEST_PORT not set";

    RDK::UArduinoSerialSession session;
    ASSERT_TRUE(session.open(QString::fromLocal8Bit(port), 57600)) << session.lastError().toStdString();

    RDK::UArduinoFirmataClient client;
    client.setBoardProfile(0);
    ASSERT_TRUE(client.startHandshake(&session, 0));
    ASSERT_TRUE(pumpFirmata(session, client, 8000)) << "Firmata handshake timeout";

    // PWM (extended analog) on D9
    EXPECT_TRUE(client.setPinMode(&session, 9, 0x03));
    EXPECT_TRUE(client.extendedAnalogWrite(&session, 9, 128));

    // Servo on D10
    EXPECT_TRUE(client.configureServo(&session, 10, 544, 2400));
    EXPECT_TRUE(client.setPinMode(&session, 10, 0x04));
    EXPECT_TRUE(client.servoWrite(&session, 10, 90));

    // I2C bus config + read request (device may be absent; command path must succeed)
    EXPECT_TRUE(client.i2cConfig(&session, 0));
    EXPECT_TRUE(client.i2cReadRequest(&session, 0x48, 2));
    pumpFirmata(session, client, 500);

    session.close();
}
