#include "NmsdkRegisterLlm.h"

#ifdef RDK_USE_LLM

#include "NmsdkLlmProjectContext.h"
#include "NmsdkLlmSettings.h"

#include "../../Rdk/GUI/Qt/UGEngineControlWidget.h"
#include "../../Rdk/GUI/Qt/Llm/LlmGuiBootstrap.h"
#include "../../Rdk/GUI/Qt/Llm/ULlmGuiContextBridge.h"
#include "../../Rdk/GUI/Qt/Llm/ULlmQtPresentationSink.h"
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
    RDK::LLM::LLMServices::instance().initialize(app, g_project_context.get(),
                                                 &NmsdkLlmSettingsSource());

    g_bridge = new ULlmGuiContextBridge(app, host);
    RDK::LLM::LLMServices::instance().setPresentationSink(
        std::make_unique<ULlmQtPresentationSink>(host, g_bridge));
    LlmGui::RegisterLlmUi(host, app, g_bridge);
}

#endif
