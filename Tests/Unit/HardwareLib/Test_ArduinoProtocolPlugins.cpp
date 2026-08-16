#include <gtest/gtest.h>

#include "Protocol/UArduinoProtocolPluginRegistry.h"
#include "Protocol/USensorLabFrameDecoder.h"

TEST(ProtocolPlugins, SensorLabRegistered)
{
    RDK::registerBuiltinArduinoProtocolPlugins();
    ASSERT_NE(RDK::findArduinoProtocolPlugin(QStringLiteral("sensor_lab_v1")), nullptr);
    EXPECT_TRUE(RDK::registeredArduinoProtocolPluginIds().contains(QStringLiteral("sensor_lab_v1")));
}

TEST(ProtocolPlugins, HubPluginsRegistered)
{
    RDK::registerBuiltinArduinoProtocolPlugins();
    ASSERT_NE(RDK::findArduinoProtocolPlugin(QStringLiteral("nmsdk_sensor_hub_v1")), nullptr);
    ASSERT_NE(RDK::findArduinoProtocolPlugin(QStringLiteral("nmsdk_motor_hub_v1")), nullptr);
}

TEST(SensorLabDecoder, SensorsPayload)
{
    QByteArray payload;
    payload.append(char(0));
    payload.append(char(2));
    float t = 21.5f;
    float h = 40.0f;
    payload.append(reinterpret_cast<const char*>(&t), sizeof(float));
    payload.append(reinterpret_cast<const char*>(&h), sizeof(float));
    const auto decoded = RDK::USensorLabFrameDecoder::decodeSensors(payload);
    ASSERT_TRUE(decoded.ok);
    EXPECT_EQ(decoded.paramCount, 2);
    EXPECT_NEAR(decoded.values[0], 21.5f, 0.01);
}
