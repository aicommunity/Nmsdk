#include "LlmWriteToolsEngineInit.h"

#include "../../../Rdk/Core/Application/UAppCore.h"
#include "../../../Rdk/Deploy/Include/rdk_cpp_init.h"

#include <filesystem>
#include <stdexcept>

namespace fs = std::filesystem;

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
    RDK::UProjectDeployer>;

LlmWriteToolsEngineContext g_ctx;
bool g_tried = false;
AppCoreType* g_appCore = nullptr;

#ifdef CMAKE_SOURCE_DIR
constexpr const char* kSourceRoot = CMAKE_SOURCE_DIR;
#else
constexpr const char* kSourceRoot = ".";
#endif

fs::path repoRoot() { return fs::path(kSourceRoot); }

fs::path platformBinDir()
{
#ifdef _WIN32
    return repoRoot() / "Bin/Platform/Win";
#else
    return repoRoot() / "Bin/Platform/Linux";
#endif
}

} // namespace

std::string testValidProjectIniPath()
{
    return (repoRoot() / "Bin/Configs/TestValidation/test_valid/project.ini").string();
}

const LlmWriteToolsEngineContext& EnsureLlmWriteToolsEngine()
{
    if(g_tried)
        return g_ctx;
    g_tried = true;

    const fs::path bin = platformBinDir();
    const fs::path ini = repoRoot() / "Rdk/Tests/Fixtures/LLM/NeuroModelerConsole.test.ini";
    const fs::path console_exe = bin / "NeuroModelerConsole";

    if(!fs::exists(ini) || !fs::exists(console_exe))
        return g_ctx;

    Core_SetSystemDir(bin.string().c_str());

    if(!g_appCore)
        g_appCore = new AppCoreType();
    const int initRes = g_appCore->Init(console_exe.string(), ini.string(), std::string(), "TestUser",
                                      0, nullptr);
    if(initRes != 0)
        return g_ctx;

    g_ctx.application = &g_appCore->application;
    g_ctx.initialized = true;

    const std::string project_ini = testValidProjectIniPath();
    if(fs::exists(project_ini))
    {
        if(!g_ctx.application->OpenProject(project_ini))
            g_ctx.initialized = false;
    }

    return g_ctx;
}

void ShutdownLlmWriteToolsEngine()
{
    if(g_ctx.application && g_ctx.application->GetProjectOpenFlag())
        g_ctx.application->CloseProject();
    g_ctx.application = nullptr;
    g_ctx.initialized = false;
    if(g_appCore)
    {
        delete g_appCore;
        g_appCore = nullptr;
    }
    g_tried = false;
}

} // namespace NmsdkTests
