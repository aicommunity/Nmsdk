#include "NmsdkRegisterLlm.h"

#ifdef RDK_USE_LLM

#include "NmsdkLlmProjectContext.h"

#include "../../Rdk/GUI/Qt/UGEngineControlWidget.h"
#include "../../Rdk/GUI/Qt/Llm/LlmGuiBootstrap.h"
#include "../../Rdk/GUI/Qt/Llm/ULlmGuiContextBridge.h"
#include "../../Rdk/LLM/Core/LlmPublicApi.h"

#include <cstdlib>
#include <memory>

static std::unique_ptr<NmsdkLlmProjectContext> g_project_context;
static ULlmGuiContextBridge* g_bridge = nullptr;

void NmsdkRegisterLlm(UGEngineControlWidget* host, RDK::UApplication* app)
{
    if(!host || !app)
        return;

    g_project_context = std::make_unique<NmsdkLlmProjectContext>(app);
    RDK::LLM::LLMServices::instance().initialize(app, g_project_context.get());

    if(const char* mock = std::getenv("NMSDK_LLM_MOCK"))
    {
        if(mock[0] == '1')
        {
            (void)mock;
            // Tests set mock via provider factory override in LLMServices if needed.
        }
    }

    g_bridge = new ULlmGuiContextBridge(app, host);
    LlmGui::RegisterLlmUi(host, app, g_bridge);
}

#endif
