#ifndef NMSDK_REGISTER_LLM_H
#define NMSDK_REGISTER_LLM_H

class UGEngineControlWidget;

namespace RDK {
class UApplication;
}

#ifdef RDK_USE_LLM
/// Runtime LLM gate: `General/ShowLlmAssistantMenu` from NeuroModeler.ini (default 0),
/// overridable by env `NMSDK_LLM_ENABLE=1` / `NMSDK_LLM_DISABLE=1`.
bool NmsdkLlmRuntimeEnabled(int showLlmAssistantMenu);

/// Registers AI UI and starts LLMServices initialization on a worker thread (non-blocking).
/// No-op when `NmsdkLlmRuntimeEnabled` is false — startup must not pay LLM cost by default.
void NmsdkRegisterLlm(UGEngineControlWidget* host, RDK::UApplication* app, int showLlmAssistantMenu);
#endif

#endif
