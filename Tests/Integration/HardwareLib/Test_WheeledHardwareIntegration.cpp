#include <gtest/gtest.h>

#include <cstdlib>

/** L5 scaffold: skips cleanly when WHEELED_PORT is unset. */
TEST(WheeledHardwareIntegration, SkipWithoutPort)
{
    const char* port = std::getenv("WHEELED_PORT");
    if (!port || !*port) {
        GTEST_SKIP() << "WHEELED_PORT not set; L5 wheeled live test skipped";
    }
    // Live path reserved for board-connected CI / nightly.
    SUCCEED();
}
