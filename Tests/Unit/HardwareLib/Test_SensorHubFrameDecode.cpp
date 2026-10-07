#include <gtest/gtest.h>

#include <QMap>
#include <cstring>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/IArduinoProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkI2cHubProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkSensorHubProtocolPlugin.h"
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
