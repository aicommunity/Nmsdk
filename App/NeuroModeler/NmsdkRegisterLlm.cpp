#include "NmsdkRegisterLlm.h"

#ifdef RDK_USE_LLM

#include "NmsdkBuiltinKnowledgeCatalog.h"
#include "NmsdkLlmProjectContext.h"
#include "NmsdkLlmSettings.h"

#include "../../Rdk/GUI/Qt/UGEngineControlWidget.h"
#include "../../Rdk/GUI/Qt/Llm/LlmGuiBootstrap.h"
#include "../../Rdk/GUI/Qt/Llm/ULlmGuiContextBridge.h"
#include "../../Rdk/GUI/Qt/Llm/ULlmQtPresentationSink.h"
#include "../../Rdk/LLM/Core/LlmPublicApi.h"

#include <QPointer>
#include <QTimer>

#include <cstdlib>
#include <memory>
#include <thread>

static std::unique_ptr<NmsdkLlmProjectContext> g_project_context;
static ULlmGuiContextBridge* g_bridge = nullptr;

bool NmsdkLlmRuntimeEnabled(int showLlmAssistantMenu)
{
    if(const char* disable = std::getenv("NMSDK_LLM_DISABLE"))
    {
        if(disable[0] == '1')
            return false;
    }
    if(const char* enable = std::getenv("NMSDK_LLM_ENABLE"))
    {
        if(enable[0] == '1')
            return true;
    }
    return showLlmAssistantMenu != 0;
}

void NmsdkRegisterLlm(UGEngineControlWidget* host, RDK::UApplication* app, int showLlmAssistantMenu)
{
    if(!host || !app)
        return;
    if(!NmsdkLlmRuntimeEnabled(showLlmAssistantMenu))
        return;

    // Lightweight main-thread wiring only; heavy initialize() runs off the UI thread.
    g_project_context = std::make_unique<NmsdkLlmProjectContext>(app);
    g_bridge = new ULlmGuiContextBridge(app, host);

    QPointer<UGEngineControlWidget> host_ptr(host);
    const bool show_menu = showLlmAssistantMenu != 0;

    std::thread([host_ptr, app, show_menu]() {
        try
        {
            auto catalog = std::make_unique<NmsdkBuiltinKnowledgeCatalog>(app);
            RDK::LLM::LLMServices::instance().initialize(app, g_project_context.get(),
                                                         &NmsdkLlmSettingsSource(),
                                                         std::move(catalog));
        }
        catch(...)
        {
            return;
        }

        if(!host_ptr)
            return;

        // Finish GUI registration on the widget's thread.
        QTimer::singleShot(0, host_ptr, [host_ptr, app, show_menu]() {
            if(!host_ptr || !g_bridge)
                return;
            if(!RDK::LLM::LLMServices::instance().isInitialized())
                return;
            RDK::LLM::LLMServices::instance().setPresentationSink(
                std::make_unique<ULlmQtPresentationSink>(host_ptr, g_bridge));
            LlmGui::RegisterLlmUi(host_ptr, app, g_bridge, show_menu);
        });
    }).detach();
}

#endif
