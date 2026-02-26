#include "ConsoleLikeInit.h"

#include "../../../Rdk/Deploy/Include/rdk_cpp_init.h"
#include "../../../Rdk/Deploy/Include/rdk_engine_support.h"

#include <stdexcept>
#include <string>

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
AppCoreType g_appCore;

} // namespace

const ConsoleInitResult& InitEngineForPulseLibTests()
{
    if (g_initialized)
        return g_result;

    // Предполагаем, что тестовый бинарник и NeuroModelerConsole.ini лежат в Bin/Platform/Win
    // (как и сама NeuroModelerConsole). CWD при запуске теста — та же папка.
    const std::string appPath = "Test_PulseLib_StorageComponents.exe";
    const std::string iniFile = "NeuroModelerConsole.ini";

    // Для интеграционных тестов используем отдельную директорию логов,
    // чтобы не смешивать их с рабочими логами NeuroModelerConsole.
    const std::string testLogDir = "TestLogs/PulseLib";

    std::string defaultUser = "TestUser";

    int argc = 0;
    char** argv = nullptr;

    // Настраиваем системный и лог‑каталог до инициализации ядра
    // (относительно текущего Bin/Platform/Win).
    // Core_SetSystemDir / Core_SetLogDir — C API из rdk_init.h (глобальная область видимости).
    Core_SetSystemDir(".");
    Core_SetLogDir(testLogDir.c_str());

    const int initRes = g_appCore.Init(appPath, iniFile, testLogDir, defaultUser, argc, argv);
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

} // namespace NmsdkTests

