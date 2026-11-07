#include "ConsoleLikeInit.h"

#include "../../../Rdk/Deploy/Include/rdk_cpp_init.h"
#include "../../../Rdk/Deploy/Include/rdk_engine_support.h"

#include <stdexcept>
#include <string>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <chrono>
#if defined(_WIN32)
#include <windows.h>
#endif

namespace NmsdkTests {

namespace {

using AppCoreType = RDK::UAppCore<
    RDK::UApplication,
    RDK::UEngineControl,
    RDK::UProject,
    RDK::UServerControl,
    RDK::UTestManager,
    RDK::URpcDispatcher,
    RDK::URpcDecoderInternal,
    RDK::URpcDecoderCommon,
    RDK::UServerTransportTcp,
    RDK::UProjectDeployer
>;

ConsoleInitResult g_result;
bool g_initialized = false;
AppCoreType* g_appCore = nullptr;
std::string g_executable;

std::filesystem::path OwnTestWorkDirectory(const std::filesystem::path& runtime)
{
    const auto insideRuntime=[&](const std::filesystem::path& path) {
        const auto relative=path.lexically_relative(runtime);
        return !relative.empty() && !relative.is_absolute() && *relative.begin()!="..";
    };
    if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");output && *output)
    {
        const auto native=std::filesystem::weakly_canonical(std::filesystem::absolute(output));
        const auto work=std::filesystem::path(native.string()+".test-events-log");
        if(insideRuntime(native) || insideRuntime(work) || native.filename().empty() ||
           !std::filesystem::is_directory(work.parent_path()) || !std::filesystem::create_directory(work))
            throw std::runtime_error("PulseLib test log directory is not new or overlaps runtime");
        return work;
    }
    // Direct CTest runs also keep logs out of the executable/resources tree.
    const auto stamp=std::chrono::steady_clock::now().time_since_epoch().count();
    const auto parent=std::filesystem::temp_directory_path();
    for(unsigned attempt=0;attempt<32;++attempt)
    {
        const auto work=parent/("NmsdkPulseLibTests-"+std::to_string(stamp)+"-"+std::to_string(attempt));
        if(!insideRuntime(work) && std::filesystem::create_directory(work))return work;
    }
    throw std::runtime_error("PulseLib test log directory reservation failed");
}

} // namespace

void SetPulseLibTestExecutable(const std::string& argv0)
{
#if defined(__linux__)
    g_executable=std::filesystem::canonical("/proc/self/exe").string();
#elif defined(_WIN32)
    std::wstring path(32768,L'\0');const auto size=GetModuleFileNameW(nullptr,path.data(),DWORD(path.size()));
    if(!size || size>=path.size())throw std::runtime_error("PulseLib test executable path unavailable");
    path.resize(size);g_executable=std::filesystem::path(path).string();
#else
    if(argv0.empty())throw std::runtime_error("PulseLib test executable requires argv[0]");
    g_executable=std::filesystem::canonical(argv0).string();
#endif
}
const std::string& PulseLibTestExecutable()
{if(g_executable.empty())SetPulseLibTestExecutable({});return g_executable;}

const ConsoleInitResult& InitEngineForPulseLibTests()
{
    if (g_initialized)
        return g_result;

    const std::string appPath=PulseLibTestExecutable();
    const auto runtime=std::filesystem::path(appPath).parent_path();
    const std::string iniFile=(runtime/"NeuroModelerConsole.ini").string();
    if(!std::filesystem::is_regular_file(iniFile))throw std::runtime_error("PulseLib test runtime ini is missing: "+iniFile);
    if(!std::ifstream(std::filesystem::path(iniFile)))throw std::runtime_error("PulseLib test runtime ini cannot be read: "+iniFile);
    std::cerr<<"PulseLibTestRuntime executable="<<appPath<<" ini="<<iniFile<<'\n';

    // An empty Init log path does not disable Rdk's WorkDirectory/EventsLog
    // fallback. Reserve an owned work directory before initialization, through
    // the same native mechanism used by Console jobs.
    const auto workDirectory=OwnTestWorkDirectory(runtime);
    const std::string testLogDir=(workDirectory/"EventsLog").string();

    std::string defaultUser = "TestUser";

    int argc = 0;
    char** argv = nullptr;

    // Настраиваем только системный каталог до инициализации ядра
    // (относительно текущего runtime directory).
    // Core_SetSystemDir — C API из rdk_init.h (глобальная область видимости).
    Core_SetSystemDir(runtime.string().c_str());

    if (!g_appCore)
        g_appCore = new AppCoreType();

    g_appCore->application.SetWorkDirectory(workDirectory.string());
    std::cerr<<"PulseLibTestRuntime work_directory="<<workDirectory.string()<<'\n';

    const int initRes = g_appCore->Init(appPath, iniFile, testLogDir, defaultUser, argc, argv);
    if (initRes != 0)
    {
        throw std::runtime_error(
            "UAppCore.Init failed for PulseLib tests, code=" + std::to_string(initRes));
    }

    // После успешной инициализации ядра Storage/Environment/Engine доступны через C API
    g_result.storage     = RDK::GetStorage();
    g_result.environment = RDK::GetEnvironment();
    g_result.engine      = RDK::GetEngine();

    // Включаем подробное логирование для тестов (если логгер доступен)
    if (auto logger = RDK::GetLogger())
    {
        logger->SetDebugMode(true);
        // Максимально широкий набор событий для диагностики
        logger->SetDebugSysEventsMask(0xFFFFFFFFu);
    }

    g_initialized = true;
    return g_result;
}

void ShutdownEngineForPulseLibTests()
{
    if (g_appCore)
    {
        delete g_appCore;
        g_appCore = nullptr;
    }
    g_result.storage = static_cast<RDK::UStorage*>(nullptr);
    g_result.environment = static_cast<RDK::UEnvironment*>(nullptr);
    g_result.engine = static_cast<RDK::UEngine*>(nullptr);
    g_initialized = false;
}

} // namespace NmsdkTests

