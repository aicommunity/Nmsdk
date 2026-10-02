#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UArduinoBinaryStreamParser.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoBoardProfile.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoFlasher.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialPortUtil.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Board/UArduinoPropertyString.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Board/UFirmwareManifest.h"

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
    frame.append('\xaa');
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

QString resolveBoardPinsJson(const QString& fileName)
{
    const QString rel =
        QStringLiteral("Libraries/Rdk-HardwareLib/GUI/Qt/Resources/boards/") + fileName;
    QString sdkRoot = QString::fromLocal8Bit(qgetenv("NMSDK_ROOT"));
    if (sdkRoot.isEmpty()) {
        const QFileInfo testFile(QString::fromUtf8(__FILE__));
        sdkRoot = QDir(testFile.absolutePath()).filePath(QStringLiteral("../../.."));
    }
    const QStringList candidates = {
        QDir(sdkRoot).absoluteFilePath(rel),
        QStringLiteral("../") + rel,
        QStringLiteral("../../../") + rel,
        QStringLiteral("../../../../") + rel,
    };
    for (const QString& path : candidates) {
        if (QFile::exists(path))
            return path;
    }
    return candidates.last();
}

bool pinsJsonContainsId(const QString& path, const QString& pinId)
{
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly))
        return false;
    const QJsonArray pins = QJsonDocument::fromJson(file.readAll())
                                .object()
                                .value(QStringLiteral("pins"))
                                .toArray();
    for (const QJsonValue& value : pins) {
        if (value.toObject().value(QStringLiteral("id")).toString() == pinId)
            return true;
    }
    return false;
}

} // namespace

TEST(ArduinoBoardProfile, UnoAvrdudeArgs)
{
    const RDK::UArduinoBoardProfile p = RDK::UArduinoBoardProfileUtil::profileForKind(RDK::UArduinoBoardKind::Uno);
    const QString cmd = RDK::UArduinoFlasher::buildCommand(p, QStringLiteral("COM3"),
                                                           QStringLiteral("/tmp/f.hex"),
                                                           QStringLiteral("/etc/avrdude.conf"));
    EXPECT_TRUE(cmd.contains(QStringLiteral("atmega328p")));
    EXPECT_TRUE(cmd.contains(QStringLiteral("-carduino")));
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
    EXPECT_TRUE(cmd.contains(QStringLiteral("-cwiring")));
    EXPECT_FALSE(cmd.contains(QStringLiteral("stk500v2")));
}

TEST(ArduinoBoardProfile, ValidateUpload_RejectsUnoProfileWithMegaHex)
{
    const QString err = RDK::UArduinoBoardProfileUtil::validateUploadTargets(
        0, QStringLiteral("C:/fw/firmata/standard_firmata_mega2560.hex"));
    EXPECT_FALSE(err.isEmpty());
}

TEST(ArduinoBoardProfile, ValidateUpload_RejectsMegaProfileWithUnoHex)
{
    const QString err = RDK::UArduinoBoardProfileUtil::validateUploadTargets(
        1, QStringLiteral("C:/fw/firmata/standard_firmata_uno.hex"));
    EXPECT_FALSE(err.isEmpty());
}

TEST(ArduinoBoardProfile, ValidateUpload_AllowsMatchingPairs)
{
    EXPECT_TRUE(RDK::UArduinoBoardProfileUtil::validateUploadTargets(
                    0, QStringLiteral("/x/standard_firmata_uno.hex"))
                    .isEmpty());
    EXPECT_TRUE(RDK::UArduinoBoardProfileUtil::validateUploadTargets(
                    1, QStringLiteral("/x/standard_firmata_mega2560.hex"))
                    .isEmpty());
}

TEST(ArduinoBoardProfile, ValidateUpload_SkipsAmbiguousCustomHex)
{
    EXPECT_TRUE(RDK::UArduinoBoardProfileUtil::validateUploadTargets(
                    0, QStringLiteral("/x/custom_build.hex"))
                    .isEmpty());
}

TEST(ArduinoBoardProfile, UsbIds_Mega2560)
{
    EXPECT_EQ(RDK::UArduinoBoardProfileUtil::boardProfileFromUsbIds(0x2341, 0x0010), 1);
}

TEST(ArduinoBoardProfile, UsbIds_Uno)
{
    EXPECT_EQ(RDK::UArduinoBoardProfileUtil::boardProfileFromUsbIds(0x2341, 0x0043), 0);
}

TEST(ArduinoBoardProfile, UsbIds_UnknownVendor)
{
    EXPECT_EQ(RDK::UArduinoBoardProfileUtil::boardProfileFromUsbIds(0x1A86, 0x7523), -1);
}

TEST(ArduinoBoardProfile, Description_Mega)
{
    EXPECT_EQ(RDK::UArduinoBoardProfileUtil::boardProfileFromDescription(
                  QStringLiteral("Arduino Mega 2560")),
              1);
}

TEST(ArduinoPropertyString, RoundTripCyrillic)
{
    const QString original = QStringLiteral("COM3 — USB-SERIAL CH340 (Порт)");
    const std::string stored = RDK::UArduinoPropertyString::toStdProperty(original);
    const QString restored = RDK::UArduinoPropertyString::fromStdProperty(stored);
    EXPECT_EQ(restored, original);
}

TEST(ArduinoSerialPortUtil, AvrdudePortArgumentQuotesComPort)
{
#if defined(Q_OS_WIN)
    const QString arg = RDK::UArduinoSerialPortUtil::avrdudePortArgument(QStringLiteral("COM3"));
    EXPECT_TRUE(arg.startsWith(QStringLiteral("\\\\.\\COM3")));
#else
    GTEST_SKIP() << "Windows-only avrdude port form";
#endif
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

TEST(ArduinoBinaryParser, FramedV2RejectsBadCrc)
{
    RDK::UArduinoBinaryStreamParser parser;
    parser.setProtocolVersion(2);
    int frames = 0;
    QByteArray frame = buildV2Frame(0x07, QByteArray::fromHex("0102"));
    frame[frame.size() - 1] = char(frame.at(frame.size() - 1) ^ 0xFF);

    parser.feed(frame, [&](uint8_t, const QByteArray&) { frames++; });
    EXPECT_EQ(frames, 0);
}

TEST(ArduinoFirmwareManifest, LoadsSensorLabId)
{
    EnsureQtApp();
    const QString hex = RDK::UFirmwareManifest::resolveBundledHex(QStringLiteral("sensor_lab_v1"), 0);
    ASSERT_FALSE(hex.isEmpty());
    EXPECT_TRUE(hex.endsWith(QStringLiteral("uno.hex")) || hex.contains(QStringLiteral("sensor_lab")));
    EXPECT_TRUE(QFile::exists(hex));
}

TEST(ArduinoFlasher, LocatesAvrdudeFromArduinoCore)
{
    if (!QFile::exists(QDir::homePath() + QStringLiteral("/.arduino15/packages/arduino/tools/avrdude")))
        GTEST_SKIP() << "arduino:avr core not installed";
    EXPECT_FALSE(RDK::UArduinoFlasher::locateAvrdudeBinary().isEmpty());
    EXPECT_FALSE(RDK::UArduinoFlasher::locateAvrdudeConf().isEmpty());
}

TEST(ArduinoFlasher, LocatesBundledToolsNextToApplicationDir)
{
    EnsureQtApp();
    const QDir appDir(QCoreApplication::applicationDirPath());
    const QString bundledExe = appDir.filePath(QStringLiteral("ArduinoTools/bin/avrdude.exe"));
    const QString bundledBin = appDir.filePath(QStringLiteral("ArduinoTools/bin/avrdude"));
    if (!QFile::exists(bundledExe) && !QFile::exists(bundledBin))
        GTEST_SKIP() << "Bundled ArduinoTools not present next to test executable";
    EXPECT_FALSE(RDK::UArduinoFlasher::locateAvrdudeBinary().isEmpty());
    EXPECT_FALSE(RDK::UArduinoFlasher::locateAvrdudeConf().isEmpty());
}

TEST(ArduinoSerialPortUtil, NormalizesLinuxTtyName)
{
    const QString path = RDK::UArduinoSerialPortUtil::normalizeDevicePath(QStringLiteral("ttyACM0"));
    EXPECT_TRUE(path.startsWith(QStringLiteral("/dev/")));
}

TEST(ArduinoFirmwareManifest, BundledHexRelativePathUsesBinOffset)
{
    const QString rel =
        RDK::UFirmwareManifest::bundledHexRelativePath(QStringLiteral("standard_firmata"), 0);
    ASSERT_FALSE(rel.isEmpty());
    EXPECT_TRUE(rel.startsWith(QStringLiteral("../../ArduinoFirmware/")));
    EXPECT_TRUE(rel.endsWith(QStringLiteral("firmata/standard_firmata_uno.hex")));
}

TEST(ArduinoFirmwareManifest, BundledFirmataHexExists)
{
    EnsureQtApp();
    const QString hex = RDK::UFirmwareManifest::resolveBundledHex(QStringLiteral("standard_firmata"), 0);
    ASSERT_FALSE(hex.isEmpty());
    EXPECT_TRUE(QFile::exists(hex));
}

TEST(ArduinoFirmwareManifest, AllBundledIdsResolveHex)
{
    EnsureQtApp();
    const QString manifestPath =
        QDir(RDK::UFirmwareManifest::firmwareRoot()).filePath(QStringLiteral("manifest.json"));
    ASSERT_TRUE(QFile::exists(manifestPath));

    QFile file(manifestPath);
    ASSERT_TRUE(file.open(QIODevice::ReadOnly));
    const QJsonArray bundled =
        QJsonDocument::fromJson(file.readAll()).object().value(QStringLiteral("bundled")).toArray();
    ASSERT_GE(bundled.size(), 2);

    for (const QJsonValue& entryVal : bundled) {
        const QJsonObject entry = entryVal.toObject();
        const QString id = entry.value(QStringLiteral("id")).toString();
        ASSERT_FALSE(id.isEmpty()) << "manifest entry without id";

        const QJsonObject boards = entry.value(QStringLiteral("boards")).toObject();
        for (const QString& boardKey : {QStringLiteral("uno"), QStringLiteral("mega2560")}) {
            ASSERT_TRUE(boards.contains(boardKey)) << id.toUtf8().constData() << boardKey.toUtf8().constData();
            const int profile = boardKey == QStringLiteral("mega2560") ? 1 : 0;
            const QString hex = RDK::UFirmwareManifest::resolveBundledHex(id, profile);
            ASSERT_FALSE(hex.isEmpty()) << id.toUtf8().constData() << boardKey.toUtf8().constData();
            EXPECT_TRUE(QFile::exists(hex)) << hex.toUtf8().constData();
        }
    }
}

TEST(ArduinoPinsJson, UnoHasAtLeast20Pins)
{
    const QString resolved = resolveBoardPinsJson(QStringLiteral("uno_pins.json"));
    ASSERT_TRUE(QFile::exists(resolved));
    EXPECT_GE(pinCountFromResource(resolved), 20);
    EXPECT_TRUE(pinsJsonContainsId(resolved, QStringLiteral("D13")));
    EXPECT_TRUE(pinsJsonContainsId(resolved, QStringLiteral("A5")));
}

TEST(ArduinoPinsJson, MegaIncludesExtendedAnalogPins)
{
    const QString resolved = resolveBoardPinsJson(QStringLiteral("mega2560_pins.json"));
    ASSERT_TRUE(QFile::exists(resolved));
    EXPECT_GE(pinCountFromResource(resolved), 20);
    EXPECT_TRUE(pinsJsonContainsId(resolved, QStringLiteral("D13")));
    EXPECT_TRUE(pinsJsonContainsId(resolved, QStringLiteral("A7")));
}
