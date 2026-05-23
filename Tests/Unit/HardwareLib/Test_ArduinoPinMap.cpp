#include <gtest/gtest.h>

#include <Transport/UArduinoPinMap.h>

namespace {

TEST(ArduinoPinMap, UnoAnalogPins)
{
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("A0"), 0), 14);
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("A5"), 0), 19);
    EXPECT_EQ(RDK::UArduinoPinMap::labelForFirmataPin(14, 0), QStringLiteral("A0"));
}

TEST(ArduinoPinMap, MegaAnalogPins)
{
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("A0"), 1), 54);
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("A10"), 1), 64);
    EXPECT_EQ(RDK::UArduinoPinMap::labelForFirmataPin(54, 1), QStringLiteral("A0"));
}

TEST(ArduinoPinMap, DigitalPins)
{
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("D13"), 0), 13);
    EXPECT_EQ(RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("D13"), 1), 13);
}

TEST(ArduinoPinMap, PortHelpers)
{
    EXPECT_EQ(RDK::UArduinoPinMap::portForPin(13), 1);
    EXPECT_EQ(RDK::UArduinoPinMap::bitIndexInPort(13), 5);
    EXPECT_EQ(RDK::UArduinoPinMap::maxFirmataPin(0), 19);
    EXPECT_EQ(RDK::UArduinoPinMap::maxFirmataPin(1), 69);
    EXPECT_EQ(RDK::UArduinoPinMap::digitalPortCount(1), 7);
}

} // namespace
