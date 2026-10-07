#include <gtest/gtest.h>

#include <QMap>
#include <cstring>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/IArduinoProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkDisplayHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkI2cHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkPixelHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkRadioHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkSensorHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkUartDeviceHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/USensorLabFrameDecoder.h"

namespace {

class CapturingHost : public RDK::UArduinoPluginHost {
public:
    void enqueueCommand(const QString&) override {}
    int boardProfile() const override { return 0; }
    int protocolVersion() const override { return 2; }
    void setProtocolReady(bool ready) override { Ready = ready; }
    void setLastError(const QString&) override {}
    void publishNamedFloat(const QString& key, float value) override { Named[key] = value; }

    QMap<QString, float> Named;
    bool Ready = false;
};

QByteArray MakeSensors(const QVector<float>& values)
{
    QByteArray p;
    p.append(char(0));
    p.append(char(values.size()));
    for (float v : values) {
        char b[sizeof(float)];
        std::memcpy(b, &v, sizeof(float));
        p.append(b, int(sizeof(float)));
    }
    return p;
}

} // namespace

TEST(SensorHubFrameDecode, FourChannelLegacy)
{
    const QByteArray payload = MakeSensors({21.5f, 40.f, 12.f, 512.f});
    const auto decoded = RDK::USensorLabFrameDecoder::decodeSensors(payload);
    ASSERT_TRUE(decoded.ok);
    EXPECT_EQ(4, decoded.paramCount);
    EXPECT_FLOAT_EQ(21.5f, decoded.values[0]);
}

TEST(SensorHubFrameDecode, FiveChannelDs18b20)
{
    const QByteArray payload = MakeSensors({22.f, 41.f, 10.f, 100.f, 18.25f});
    CapturingHost host;
    RDK::UNmsdkSensorHubProtocolPlugin plugin;
    plugin.onBinaryFrame(&host, 0x01, payload);
    EXPECT_TRUE(host.Ready);
    EXPECT_FLOAT_EQ(22.f, host.Named.value(QStringLiteral("t")));
    EXPECT_FLOAT_EQ(18.25f, host.Named.value(QStringLiteral("ds18b20")));
}

TEST(I2cHubFrameDecode, Bme280ThreeFloats)
{
    const QByteArray payload = MakeSensors({23.1f, 55.f, 1013.25f});
    CapturingHost host;
    RDK::UNmsdkI2cHubProtocolPlugin plugin;
    plugin.onBinaryFrame(&host, 0x01, payload);
    EXPECT_TRUE(host.Ready);
    EXPECT_FLOAT_EQ(23.1f, host.Named.value(QStringLiteral("t")));
    EXPECT_FLOAT_EQ(55.f, host.Named.value(QStringLiteral("h")));
    EXPECT_FLOAT_EQ(1013.25f, host.Named.value(QStringLiteral("pressure_hpa")));
}

TEST(I2cHubFrameDecode, Vl53MpuInaPcaFrames)
{
    CapturingHost host;
    RDK::UNmsdkI2cHubProtocolPlugin plugin;

    plugin.onBinaryFrame(&host, 0x30, MakeSensors({123.f}));
    EXPECT_FLOAT_EQ(123.f, host.Named.value(QStringLiteral("distance_mm")));

    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x31, MakeSensors({1.f, 2.f, 3.f, 4.f, 5.f, 6.f}));
    EXPECT_FLOAT_EQ(1.f, host.Named.value(QStringLiteral("ax")));
    EXPECT_FLOAT_EQ(6.f, host.Named.value(QStringLiteral("gz")));

    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x32, MakeSensors({5.0f, 100.f, 500.f}));
    EXPECT_FLOAT_EQ(5.0f, host.Named.value(QStringLiteral("bus_v")));
    EXPECT_FLOAT_EQ(100.f, host.Named.value(QStringLiteral("current_ma")));

    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x33, MakeSensors({3.f, 2048.f}));
    EXPECT_FLOAT_EQ(3.f, host.Named.value(QStringLiteral("pca_ch")));
    EXPECT_FLOAT_EQ(2048.f, host.Named.value(QStringLiteral("pca_duty")));
}

TEST(I2cHubFrameDecode, Wave1aBmpVl53l1Icm)
{
    CapturingHost host;
    RDK::UNmsdkI2cHubProtocolPlugin plugin;

    plugin.onBinaryFrame(&host, 0x34, MakeSensors({20.f, 40.f, 1000.f}));
    EXPECT_FLOAT_EQ(20.f, host.Named.value(QStringLiteral("t")));
    EXPECT_FLOAT_EQ(1000.f, host.Named.value(QStringLiteral("pressure_hpa")));

    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x35, MakeSensors({250.f}));
    EXPECT_FLOAT_EQ(250.f, host.Named.value(QStringLiteral("distance_mm")));

    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x36, MakeSensors({1.f, 2.f, 3.f, 4.f, 5.f, 6.f, 7.f, 8.f}));
    EXPECT_FLOAT_EQ(1.f, host.Named.value(QStringLiteral("ax")));
    EXPECT_FLOAT_EQ(7.f, host.Named.value(QStringLiteral("mx")));
}

TEST(I2cHubFrameDecode, Wave1bEnvSensors)
{
    CapturingHost host;
    RDK::UNmsdkI2cHubProtocolPlugin plugin;
    plugin.onBinaryFrame(&host, 0x37, MakeSensors({21.f, 48.f}));
    EXPECT_FLOAT_EQ(21.f, host.Named.value(QStringLiteral("t")));
    EXPECT_FLOAT_EQ(48.f, host.Named.value(QStringLiteral("h")));
    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x38, MakeSensors({123.5f}));
    EXPECT_FLOAT_EQ(123.5f, host.Named.value(QStringLiteral("lux")));
    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x39, MakeSensors({36.6f, 25.f}));
    EXPECT_FLOAT_EQ(36.6f, host.Named.value(QStringLiteral("object_c")));
    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x3A, MakeSensors({400.f, 12.f}));
    EXPECT_FLOAT_EQ(400.f, host.Named.value(QStringLiteral("eco2")));
    EXPECT_FLOAT_EQ(12.f, host.Named.value(QStringLiteral("tvoc")));
}

TEST(I2cHubFrameDecode, Wave1cMiscSensors)
{
    CapturingHost host;
    RDK::UNmsdkI2cHubProtocolPlugin plugin;
    plugin.onBinaryFrame(&host, 0x3B, MakeSensors({1.f, 2.f, 3.f, 4.f}));
    EXPECT_FLOAT_EQ(4.f, host.Named.value(QStringLiteral("c")));
    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x3C, MakeSensors({0.1f, 0.2f, 0.3f}));
    EXPECT_FLOAT_EQ(0.3f, host.Named.value(QStringLiteral("az")));
    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x3D, MakeSensors({1.f, 10.f, 1.f, 2.f, 3.f}));
    EXPECT_FLOAT_EQ(10.f, host.Named.value(QStringLiteral("proximity")));
    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x3E, MakeSensors({0.5f, 1.f, 1.5f, 2.f}));
    EXPECT_FLOAT_EQ(2.f, host.Named.value(QStringLiteral("ch3")));
}

TEST(P2PlusHubFrameDecode, DisplayPixelRadioUart)
{
    CapturingHost host;
    RDK::UNmsdkDisplayHubProtocolPlugin display;
    display.onBinaryFrame(&host, 0x40, MakeSensors({2.f, 16.f, 1.f}));
    EXPECT_FLOAT_EQ(2.f, host.Named.value(QStringLiteral("rows")));
    EXPECT_FLOAT_EQ(16.f, host.Named.value(QStringLiteral("cols")));

    host.Named.clear();
    RDK::UNmsdkPixelHubProtocolPlugin pixel;
    pixel.onBinaryFrame(&host, 0x41, MakeSensors({8.f, 4.f}));
    EXPECT_FLOAT_EQ(8.f, host.Named.value(QStringLiteral("led_count")));
    EXPECT_FLOAT_EQ(4.f, host.Named.value(QStringLiteral("last_ack")));

    host.Named.clear();
    RDK::UNmsdkRadioHubProtocolPlugin radio;
    radio.onBinaryFrame(&host, 0x50, MakeSensors({3.f, -40.f}));
    EXPECT_FLOAT_EQ(3.f, host.Named.value(QStringLiteral("rx_len")));
    radio.onBinaryFrame(&host, 0x51, MakeSensors({12345.f}));
    EXPECT_FLOAT_EQ(12345.f, host.Named.value(QStringLiteral("uid")));
    radio.onBinaryFrame(&host, 0x52, MakeSensors({-55.f, 192.f, 168.f, 1.f, 10.f}));
    EXPECT_FLOAT_EQ(-55.f, host.Named.value(QStringLiteral("rssi")));

    host.Named.clear();
    RDK::UNmsdkUartDeviceHubProtocolPlugin uart;
    uart.onBinaryFrame(&host, 0x60, QByteArray("hello"));
    EXPECT_FLOAT_EQ(5.f, host.Named.value(QStringLiteral("last_line_len")));
}
