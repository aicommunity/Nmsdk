#ifndef NMSDK_TESTS_CONSOLE_LIKE_INIT_H
#define NMSDK_TESTS_CONSOLE_LIKE_INIT_H

#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Rdk/Core/Application/UAppCore.h"
#include "../../../Rdk/Core/Application/UEngineControl.h"
#include "../../../Rdk/Core/Application/UServerTransportTcp.h"
#include "../../../Rdk/Core/Application/UProjectDeployer.h"

namespace NmsdkTests {

// Actual executable identity; independent of CWD and filename suffixes.
void SetPulseLibTestExecutable(const std::string& argv0);
const std::string& PulseLibTestExecutable();

struct ConsoleInitResult
{
    RDK::UEPtr<RDK::UStorage>     storage;
    RDK::UEPtr<RDK::UEnvironment> environment;
    RDK::UEPtr<RDK::UEngine>      engine;
};

/// Инициализирует ядро так же, как это делает NeuroModelerConsole (через UAppCore/UEngine/UApplication),
/// и возвращает ссылки на Storage/Environment/Engine.
/// Повторные вызовы возвращают уже инициализированный результат.
const ConsoleInitResult& InitEngineForPulseLibTests();

/// Tear down the console-like engine before process exit.
void ShutdownEngineForPulseLibTests();

} // namespace NmsdkTests

#endif // NMSDK_TESTS_CONSOLE_LIKE_INIT_H

