#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QMap>
#include <cstring>

#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/IArduinoProtocolPlugin.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Protocol/UNmsdkMotorHubProtocolPlugin.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

class CapturingHost : public RDK::UArduinoPluginHost {
public:
    void enqueueCommand(const QString& line) override { Commands << line; }
    int boardProfile() const override { return 0; }
    int protocolVersion() const override { return 2; }
    void setProtocolReady(bool ready) override { Ready = ready; }
    void setLastError(const QString& error) override { LastError = error; }
    void publishNamedFloat(const QString& key, float value) override { Named[key] = value; }

    QStringList Commands;
    QMap<QString, float> Named;
    bool Ready = false;
    QString LastError;
};

QByteArray MakeStatusPayload(uint8_t ch, uint8_t pwm, uint8_t dir, float sense)
{
    QByteArray p;
    p.append(char(ch));
    p.append(char(pwm));
    p.append(char(dir));
    char senseBytes[sizeof(float)];
    std::memcpy(senseBytes, &sense, sizeof(float));
    p.append(senseBytes, int(sizeof(float)));
    return p;
}

} // namespace

TEST(NmsdkMotorHubPluginDual, Channel0And1NamedFloats)
{
    EnsureQtApp();
    CapturingHost host;
    RDK::UNmsdkMotorHubProtocolPlugin plugin;

    plugin.onBinaryFrame(&host, 0x20, MakeStatusPayload(0, 100, 1, 1.5f));
    EXPECT_FLOAT_EQ(100.f, host.Named.value(QStringLiteral("left_pwm")));
    EXPECT_FLOAT_EQ(1.f, host.Named.value(QStringLiteral("left_dir")));
    EXPECT_FLOAT_EQ(1.5f, host.Named.value(QStringLiteral("left_sense")));
    EXPECT_TRUE(host.Ready);

    host.Named.clear();
    plugin.onBinaryFrame(&host, 0x20, MakeStatusPayload(1, 200, 0, 0.25f));
    EXPECT_FLOAT_EQ(200.f, host.Named.value(QStringLiteral("right_pwm")));
    EXPECT_FLOAT_EQ(0.f, host.Named.value(QStringLiteral("right_dir")));
    EXPECT_FLOAT_EQ(0.25f, host.Named.value(QStringLiteral("right_sense")));
}

TEST(NmsdkMotorHubPluginDual, PinMap0x21DualChannel)
{
    EnsureQtApp();
    CapturingHost host;
    RDK::UNmsdkMotorHubProtocolPlugin plugin;
    QByteArray p;
    // V1 compatibility: A(dir12,pwm3,brake9,sense0) B(dir13,pwm11,brake8,sense1)
    const uint8_t pins[8] = {12, 3, 9, 0, 13, 11, 8, 1};
    for (uint8_t b : pins)
        p.append(char(b));
    plugin.onBinaryFrame(&host, 0x21, p);
    EXPECT_FLOAT_EQ(12.f, host.Named.value(QStringLiteral("left_pin_dir")));
    EXPECT_FLOAT_EQ(3.f, host.Named.value(QStringLiteral("left_pin_pwm")));
    EXPECT_FLOAT_EQ(13.f, host.Named.value(QStringLiteral("right_pin_dir")));
    EXPECT_FLOAT_EQ(11.f, host.Named.value(QStringLiteral("right_pin_pwm")));
}

TEST(NmsdkMotorHubPluginDual, ExtendedPinMapCarriesDir2AndEnable)
{
    EnsureQtApp();
    CapturingHost host;
    RDK::UNmsdkMotorHubProtocolPlugin plugin;
    const uint8_t pins[12] = {2, 4, 5, 255, 255, 255, 7, 8, 6, 255, 255, 255};
    QByteArray payload;
    for (uint8_t pin : pins)
        payload.append(char(pin));

    plugin.onBinaryFrame(&host, 0x21, payload);
    EXPECT_FLOAT_EQ(2.f, host.Named.value(QStringLiteral("pin_dir")));
    EXPECT_FLOAT_EQ(4.f, host.Named.value(QStringLiteral("pin_dir2")));
    EXPECT_FLOAT_EQ(5.f, host.Named.value(QStringLiteral("pin_pwm")));
    EXPECT_FLOAT_EQ(-1.f, host.Named.value(QStringLiteral("pin_enable")));
    EXPECT_FLOAT_EQ(7.f, host.Named.value(QStringLiteral("pin_dir_b")));
    EXPECT_FLOAT_EQ(8.f, host.Named.value(QStringLiteral("pin_dir2_b")));
    EXPECT_FLOAT_EQ(6.f, host.Named.value(QStringLiteral("pin_pwm_b")));
    EXPECT_TRUE(host.Ready);
}

TEST(NmsdkMotorHubPluginDual, NegotiationDoesNotOverrideConfiguredWatchdog)
{
    EnsureQtApp();
    CapturingHost host;
    RDK::UNmsdkMotorHubProtocolPlugin plugin;
    plugin.negotiate(&host, 2);
    EXPECT_EQ(QStringList{QStringLiteral("PROTO 2")}, host.Commands);
}
