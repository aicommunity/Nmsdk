#include <gtest/gtest.h>
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/RuntimeCapture.h"

#include <cstdio>
#include <charconv>
#include <cstdlib>
#include <cstring>

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

    QString captureDirectory;
    for(int index=1;index<argc;++index)
    {
        if(std::strcmp(argv[index],"--timelearner-capture-directory")!=0)continue;
        if(!captureDirectory.isEmpty() || index+1>=argc || !argv[index+1][0])return 2;
        captureDirectory=QString::fromLocal8Bit(argv[index+1]);
        for(int next=index;next+2<argc;++next)argv[next]=argv[next+2];
        argc-=2;argv[argc]=nullptr;--index;
    }
    ::testing::InitGoogleTest(&argc, argv);
    // Explicit test-process initial condition, applied once before any test.
    // It is not a per-probe reset or a production clock policy. Child roles
    // inherit it so import/continuation controls exercise the same clock scale.
    if(const char* seed=std::getenv("TIMELEARNER_TEST_MODEL_TIME_US"))
    {
        RDK::ULongTime ticks=0;const auto end=seed+std::strlen(seed);
        const auto parsed=std::from_chars(seed,end,ticks);
        if(parsed.ec!=std::errc{} || parsed.ptr!=end)
        {std::fprintf(stderr,"invalid TIMELEARNER_TEST_MODEL_TIME_US\n");return 2;}
        NmsdkTests::InitEngineForPulseLibTests().environment->GetTime().SetTime(ticks);
        std::fprintf(stderr,"TimeLearner test initial model time: %s microseconds\n",seed);
    }
    const int result = RUN_ALL_TESTS();
    // The native work has finished. Keep this same owned process alive until
    // its supervisor captures actual mappings; no model ticks/resets are added.
    const bool captured=AwaitNativeRuntimeCapture(captureDirectory);
    NmsdkTests::ShutdownEngineForPulseLibTests();
    return captured?result:2;
}

