#include <gtest/gtest.h>

#include <QCoreApplication>

#include "../../../Libraries/Rdk-HardwareLib/Core/Board/UArduinoFirmata.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Board/UArduinoPropertyString.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

char firmataByte(int v)
{
    return static_cast<char>(v & 0xFF);
}

class FirmataI2cHarness : public RDK::UArduinoFirmata {
public:
    void initDefaults() { ADefault(); }
    using RDK::UArduinoFirmata::PollI2cReadPending;
    using RDK::UArduinoFirmata::FirmataClient;
    using RDK::UArduinoFirmata::LastSeenI2cPayload;

    void armPending()
    {
        I2cReadPending = true;
        LastSeenI2cPayload.clear();
        I2cReadData = "";
    }
};

} // namespace

TEST(I2cReadPending, SetOnReply)
{
    EnsureQtApp();
    FirmataI2cHarness firmata;
    firmata.initDefaults();
    firmata.armPending();
    EXPECT_TRUE(firmata.I2cReadPending);

    QByteArray payload;
    payload.append(firmataByte(0x77));
    payload.append(firmataByte(0x12));
    payload.append(firmataByte(0x34));
    QByteArray msg;
    msg.append(firmataByte(0xF0));
    msg.append(payload);
    msg.append(firmataByte(0xF7));
    firmata.FirmataClient.processIncoming(msg);
    firmata.PollI2cReadPending();

    EXPECT_FALSE(firmata.I2cReadPending);
    const QString hex = RDK::UArduinoPropertyString::fromStdProperty(*firmata.I2cReadData);
    EXPECT_TRUE(hex.contains(QStringLiteral("12")));
    EXPECT_TRUE(hex.contains(QStringLiteral("34")));
}

TEST(I2cReadPending, StaysPendingWithoutNewPayload)
{
    EnsureQtApp();
    FirmataI2cHarness firmata;
    firmata.initDefaults();
    firmata.armPending();
    firmata.PollI2cReadPending();
    EXPECT_TRUE(firmata.I2cReadPending);
}
