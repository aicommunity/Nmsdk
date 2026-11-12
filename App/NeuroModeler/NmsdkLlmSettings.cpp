#include "NmsdkLlmSettings.h"

#ifdef RDK_USE_LLM

static ULlmQtProviderSettingsSource g_llm_qt_settings;

ULlmQtProviderSettingsSource& NmsdkLlmSettingsSource()
{
    return g_llm_qt_settings;
}

#endif
