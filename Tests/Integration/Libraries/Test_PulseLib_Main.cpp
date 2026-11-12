#include <gtest/gtest.h>

#include <cstdio>

int main(int argc, char** argv)
{
#if defined(_WIN32)
    // Подавляем вывод на stderr (туда пишет glog),
    // чтобы интеграционные тесты PulseLib не флудили
    // сообщениями "COULD NOT CREATE A LOGGINGFILE".
    FILE* dummy = nullptr;
    freopen_s(&dummy, "NUL", "w", stderr);
#endif

    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

