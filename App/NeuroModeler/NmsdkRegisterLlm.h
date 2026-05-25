#ifndef NMSDK_REGISTER_LLM_H
#define NMSDK_REGISTER_LLM_H

class UGEngineControlWidget;

namespace RDK {
class UApplication;
}

#ifdef RDK_USE_LLM
void NmsdkRegisterLlm(UGEngineControlWidget* host, RDK::UApplication* app);
#endif

#endif
