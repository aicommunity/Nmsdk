#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UArduinoBinaryStreamParser.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoBoardProfile.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoFlasher.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/UFirmwareManifest.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

QByteArray buildV2Frame(uint8_t type, const QByteArray& payload)
{
    QByteArray frame;
    frame.append(char(0xAA));
    frame.append(char(type));
    const uint16_t len = static_cast<uint16_t>(payload.size());
    frame.append(char(len & 0xFF));
    frame.append(char((len >> 8) & 0xFF));
    frame.append(payload);
    const uint8_t crc = RDK::UArduinoBinaryStreamParser::crc8Maxim(frame, frame.size());
    frame.append(char(crc));
    return frame;
}

int pinCountFromResource(const QString& path)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly))
        return 0;
    const QJsonObject root = QJsonDocument::fromJson(file.readAll()).object();
    return root.value(QStringLiteral("pins")).toArray().size();
}

} // namespace

TEST(ArduinoBoardProfile, UnoAvrdudeArgs)
{
    const RDK::UArduinoBoardProfile p = RDK::UArduinoBoardProfileUtil::profileForKind(RDK::UArduinoBoardKind::Uno);
    const QString cmd = RDK::UArduinoFlasher::buildCommand(p, QStringLiteral("COM3"),
                                                           QStringLiteral("/tmp/f.hex"),
                                                           QStringLiteral("/etc/avrdude.conf"));
    EXPECT_TRUE(cmd.contains(QStringLiteral("atmega328p")));
    EXPECT_TRUE(cmd.contains(QStringLiteral("-b115200")));
}

TEST(ArduinoBoardProfile, MegaAvrdudeArgs)
{
    const RDK::UArduinoBoardProfile p =
        RDK::UArduinoBoardProfileUtil::profileForKind(RDK::UArduinoBoardKind::Mega2560);
    const QString cmd = RDK::UArduinoFlasher::buildCommand(p, QStringLiteral("COM3"),
                                                           QStringLiteral("/tmp/f.hex"),
                                                           QStringLiteral("/etc/avrdude.conf"));
    EXPECT_TRUE(cmd.contains(QStringLiteral("atmega2560")));
    EXPECT_TRUE(cmd.contains(QStringLiteral("stk500v2")));
}

TEST(ArduinoBinaryParser, LegacySensorPacket)
{
    RDK::UArduinoBinaryStreamParser parser;
    int frames = 0;
    QByteArray data;
    data.append(char(0x01));
    data.append(char(0x00));
    data.append(char(0x01));
    float v = 1.5f;
    data.append(reinterpret_cast<const char*>(&v), sizeof(float));

    parser.feed(data, [&](uint8_t type, const QByteArray& payload) {
        EXPECT_EQ(type, 0x01);
        EXPECT_GE(payload.size(), 2);
        frames++;
    });
    EXPECT_EQ(frames, 1);
}

TEST(ArduinoBinaryParser, LegacyPinConfigPacket0x04)
{
    RDK::UArduinoBinaryStreamParser parser;
    int frames = 0;
    QByteArray data;
    data.append(char(0x04));
    data.append(char(0x02));
    data.append(char(0x02));
    data.append(char(14));
    data.append(char(0x00));
    data.append(char(0x01));

    parser.feed(data, [&](uint8_t type, const QByteArray& payload) {
        EXPECT_EQ(type, 0x04);
        EXPECT_EQ(payload.size(), 5);
        EXPECT_EQ(static_cast<uint8_t>(payload[0]), 2);
        frames++;
    });
    EXPECT_EQ(frames, 1);
}

TEST(ArduinoBinaryParser, FramedV2Crc)
{
    RDK::UArduinoBinaryStreamParser parser;
    parser.setProtocolVersion(2);
    int frames = 0;
    const QByteArray payload = QByteArray::fromHex("0102");
    const QByteArray frame = buildV2Frame(0x07, payload);

    parser.feed(frame, [&](uint8_t type, const QByteArray& body) {
        EXPECT_EQ(type, 0x07);
        EXPECT_EQ(body, payload);
        frames++;
    });
    EXPECT_EQ(frames, 1);
}

TEST(ArduinoFirmwareManifest, LoadsSensorLabId)
{
    EnsureQtApp();
    const QString hex = RDK::UFirmwareManifest::resolveBundledHex(QStringLiteral("sensor_lab_v1"), 0);
    ASSERT_FALSE(hex.isEmpty());
    EXPECT_TRUE(hex.endsWith(QStringLiteral("uno.hex")) || hex.contains(QStringLiteral("sensor_lab")));
    EXPECT_TRUE(QFile::exists(hex));
}

TEST(ArduinoFirmwareManifest, BundledFirmataHexExists)
{
    EnsureQtApp();
    const QString hex = RDK::UFirmwareManifest::resolveBundledHex(QStringLiteral("standard_firmata"), 0);
    ASSERT_FALSE(hex.isEmpty());
    EXPECT_TRUE(QFile::exists(hex));
}

TEST(ArduinoPinsJson, UnoHasAtLeast20Pins)
{
    const QString path = QStringLiteral("%1/Libraries/Rdk-HardwareLib/GUI/Qt/Resources/boards/uno_pins.json")
                           .arg(QString::fromLocal8Bit(qgetenv("NMSDK_ROOT").isEmpty()
                                                             ? ".."
                                                             : qgetenv("NMSDK_ROOT")));
    QString resolved = path;
    if (!QFile::exists(resolved)) {
        resolved = QStringLiteral("/home/user/Nmsdk/Libraries/Rdk-HardwareLib/GUI/Qt/Resources/boards/uno_pins.json");
    }
    EXPECT_GE(pinCountFromResource(resolved), 20);
}
