#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/RuntimeCapture.h"
#include <cstring>

// These observer/clock cases have no Rdk Environment or model. Use the same
// production capture handshake as the native test executable so a short unit
// run still supplies actual loaded-file provenance, without repeated tests.
int main(int argc,char** argv)
{
    QString captureDirectory;
    for(int index=1;index<argc;++index)
    {
        if(std::strcmp(argv[index],"--timelearner-capture-directory")!=0)continue;
        if(!captureDirectory.isEmpty() || index+1>=argc || !argv[index+1][0])return 2;
        captureDirectory=QString::fromLocal8Bit(argv[index+1]);
        for(int next=index;next+2<argc;++next)argv[next]=argv[next+2];
        argc-=2;argv[argc]=nullptr;--index;
    }
    ::testing::InitGoogleTest(&argc,argv);
    const int result=RUN_ALL_TESTS();
    return AwaitNativeRuntimeCapture(captureDirectory)?result:2;
}
