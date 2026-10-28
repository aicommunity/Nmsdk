#include <gtest/gtest.h>
#include "../Support/ConsoleLikeInit.h"

#include <cstdio>

int main(int argc, char** argv)
{
    NmsdkTests::SetPulseLibTestExecutable(argc>0 && argv[0]?argv[0]:"");
#if defined(_WIN32)
    // Подавляем вывод на stderr (туда пишет glog),
    // чтобы интеграционные тесты PulseLib не флудили
    // сообщениями "COULD NOT CREATE A LOGGINGFILE".
    FILE* dummy = nullptr;
    freopen_s(&dummy, "NUL", "w", stderr);
#endif

    ::testing::InitGoogleTest(&argc, argv);
    const int result = RUN_ALL_TESTS();
    NmsdkTests::ShutdownEngineForPulseLibTests();
    return result;
}

