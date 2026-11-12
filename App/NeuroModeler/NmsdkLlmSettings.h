#ifndef NMSDK_LLM_SETTINGS_H
#define NMSDK_LLM_SETTINGS_H

#ifdef RDK_USE_LLM

#include "../../Rdk/GUI/Qt/Llm/ULlmQtProviderSettingsSource.h"

/// Qt-backed settings source; lifetime must cover LLMServices usage.
ULlmQtProviderSettingsSource& NmsdkLlmSettingsSource();

#endif

#endif
