#include <gtest/gtest.h>

#include <QCoreApplication>
#include <QProcessEnvironment>

#include <atomic>

#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoBoardProfile.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoFlasher.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoUploadJob.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "arduino_firmata_extended";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

bool envFlagEnabled(const char* name)
{
    const QByteArray v = qgetenv(name);
    if (v.isEmpty())
        return false;
    return v == "1" || v.toLower() == "true" || v.toLower() == "yes";
}

} // namespace

// FirmataTechDebt TD-001: PWM / Servo / I2C require a live board with standard_firmata.
TEST(ArduinoFirmataExtendedProtocols, SkipsWithoutHardwareFlag)
{
    EnsureQtApp();
    if (!envFlagEnabled("ARDUINO_TEST_EXTENDED"))
        GTEST_SKIP() << "Set ARDUINO_TEST_EXTENDED=1 and ARDUINO_TEST_PORT to run PWM/Servo/I2C on hardware";

    const QByteArray port = qgetenv("ARDUINO_TEST_PORT");
    if (port.isEmpty())
        GTEST_SKIP() << "ARDUINO_TEST_PORT not set";

    // Hardware path: exercised manually / lab CI. Placeholder asserts environment only.
    SUCCEED() << "Extended Firmata lab slot ready on " << port.constData()
              << " (PWM pin 9, Servo pin 10, I2C — implement board-side checks in lab)";
}

TEST(ArduinoUploadCancel, CancelFlagStopsBeforeFlashWhenPreCancelled)
{
    EnsureQtApp();
    RDK::UArduinoUploadJobState state;
    state.cancelRequested.store(true);
    state.running = true;

    const RDK::UArduinoBoardProfile profile =
        RDK::UArduinoBoardProfileUtil::profileForKind(RDK::UArduinoBoardKind::Uno);

    RDK::UArduinoUploadJob::runSync(&state, nullptr, profile, QStringLiteral("/dev/null"),
                                    QStringLiteral("/nonexistent.hex"));
    EXPECT_TRUE(state.finished.load());
    EXPECT_FALSE(state.success.load());
    EXPECT_EQ(state.errorMessage, QStringLiteral("Upload cancelled"));
}
