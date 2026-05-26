#ifndef NMSDK_TESTS_LLM_WRITE_TOOLS_ENGINE_INIT_H
#define NMSDK_TESTS_LLM_WRITE_TOOLS_ENGINE_INIT_H

#include <string>

namespace RDK {
class UApplication;
}

namespace NmsdkTests {

struct LlmWriteToolsEngineContext {
    RDK::UApplication* application = nullptr;
    bool initialized = false;
};

/// Console-like core init + optional open project. Skips test when init fails.
const LlmWriteToolsEngineContext& EnsureLlmWriteToolsEngine();

std::string testValidProjectIniPath();

} // namespace NmsdkTests

#endif
