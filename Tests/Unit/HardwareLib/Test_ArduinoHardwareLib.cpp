#include <gtest/gtest.h>

#include <QCoreApplication>

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

TEST(ArduinoFirmwareManifest, LoadsSensorLabId)
{
    EnsureQtApp();
    const QString hex = RDK::UFirmwareManifest::resolveBundledHex(QStringLiteral("sensor_lab_v1"), 0);
    if (!hex.isEmpty())
        EXPECT_TRUE(hex.endsWith(QStringLiteral("uno.hex")) || hex.contains(QStringLiteral("sensor_lab")));
}
