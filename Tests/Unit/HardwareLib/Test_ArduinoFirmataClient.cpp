#include <gtest/gtest.h>

#include <Protocol/UArduinoFirmataClient.h>
#include <Transport/UArduinoPinMap.h>

#include <QByteArray>

namespace {

QByteArray firmwareSysex()
{
    return QByteArray::fromHex("F079020106F7");
}

QByteArray capabilitySysexUno()
{
    QByteArray payload;
    payload.append(char(0x6C));
    for (int pin = 0; pin < 20; ++pin) {
        Q_UNUSED(pin);
        payload.append(char(0x00));
        payload.append(char(0x01));
        payload.append(char(0x7F));
    }
    QByteArray msg;
    msg.append(char(0xF0));
    msg.append(payload);
    msg.append(char(0xF7));
    return msg;
}

QByteArray analogMappingSysex()
{
    QByteArray payload;
    payload.append(char(0x6A));
    for (int pin = 0; pin < 20; ++pin) {
        if (pin >= 14)
            payload.append(char(pin - 14));
        else
            payload.append(char(127));
    }
    QByteArray msg;
    msg.append(char(0xF0));
    msg.append(payload);
    msg.append(char(0xF7));
    return msg;
}

void feedHandshake(RDK::UArduinoFirmataClient& client, int board_profile)
{
    client.reset();
    client.setBoardProfile(board_profile);
    client.processIncoming(firmwareSysex());
    client.processIncoming(capabilitySysexUno());
    client.processIncoming(analogMappingSysex());
}

} // namespace

TEST(ArduinoFirmataClient, HandshakeCompletes)
{
    RDK::UArduinoFirmataClient client;
    feedHandshake(client, 0);
    EXPECT_TRUE(client.HandshakeReady);
    EXPECT_EQ(client.HandshakeStage, 4);
}

TEST(ArduinoFirmataClient, AnalogMessageStoresByChannel)
{
    RDK::UArduinoFirmataClient client;
    feedHandshake(client, 0);
    const QByteArray analog = QByteArray::fromHex("E20407");
    client.processIncoming(analog);
    EXPECT_EQ(client.analogValueForChannel(2), 900);
}

TEST(ArduinoFirmataClient, DigitalMessageUpdatesPort)
{
    RDK::UArduinoFirmataClient client;
    feedHandshake(client, 0);
    client.PortDigitalMask.resize(2);
    client.PortDigitalMask[0] = 0;
    client.PortDigitalMask[1] = 0;
    const QByteArray digital = QByteArray::fromHex("912001");
    client.processIncoming(digital);
    ASSERT_GE(client.PortDigitalMask.size(), 2);
    EXPECT_NE(client.PortDigitalMask[1], 0);
    EXPECT_EQ(client.digitalValue(13), 1);
}

TEST(ArduinoFirmataClient, MegaAnalogPin54UsesMapping)
{
    RDK::UArduinoFirmataClient client;
    QByteArray payload;
    payload.append(char(0x6A));
    for (int pin = 0; pin < 70; ++pin) {
        if (pin == 54)
            payload.append(char(0));
        else
            payload.append(char(127));
    }
    QByteArray msg;
    msg.append(char(0xF0));
    msg.append(payload);
    msg.append(char(0xF7));

    client.reset();
    client.setBoardProfile(1);
    client.processIncoming(firmwareSysex());
    client.processIncoming(capabilitySysexUno());
    client.processIncoming(msg);
    EXPECT_EQ(client.analogChannelForPin(54), 0);
}

TEST(ArduinoFirmataClient, UnoA0MapsToChannelZero)
{
    RDK::UArduinoFirmataClient client;
    feedHandshake(client, 0);
    EXPECT_EQ(client.analogChannelForPin(14), 0);
}
