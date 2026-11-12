#include <gtest/gtest.h>

#include <QApplication>

#include "../../../Libraries/Rdk-HardwareLib/GUI/Qt/HardwareLibComponentGuiRegistration.h"
#include "../../../Rdk/GUI/Qt/UComponentFormRegistry.h"

namespace {
void EnsureApp()
{
    static int argc = 1;
    static char arg0[] = "test";
    static char* argv[] = {arg0, nullptr};
    if (!qApp)
        new QApplication(argc, argv);
}
}

TEST(ArduinoComponentGuiRegistry, HardwareLibClassesRegistered)
{
    EnsureApp();
    RegisterHardwareLibComponentGuiForms();
    UComponentFormRegistry& registry = UComponentFormRegistry::instance();
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoBoard")));
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoSensorSketch")));
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoFirmata")));
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoDcDemo")));
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoAdc")));
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoDeviceIO")));
    EXPECT_TRUE(registry.canOpen(QStringLiteral("ArduinoCustomFirmware")));
}
