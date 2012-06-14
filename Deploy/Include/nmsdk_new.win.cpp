#ifndef NMSDK_WINAPI_CPP
#define NMSDK_WINAPI_CPP

#include "nmsdk.h"
#include "../../Libraries/NWinAPILibraries.h"

/*****************************************************************************/
extern NMSDK::NStorage* CreateNewStorage(void)
{
 return new NMSDK::NStorage;
}

extern NMSDK::NEnvironment* CreateNewEnvironment(void)
{
 RDK::UItemData::DefaultDataSize=sizeof(double);
 NMSDK::NEnvironment* env=new NMSDK::NEnvironment;

 env->AddClassLibrary(&NMSDK::BCLLibrary);
 env->AddClassLibrary(&NMSDK::ActLibrary);
 env->AddClassLibrary(&NMSDK::CRLibrary);
 env->AddClassLibrary(&NMSDK::MathLibrary);
 env->AddClassLibrary(&NMSDK::PhysLibrary);
 env->AddClassLibrary(&NMSDK::SensorLibrary);
 env->AddClassLibrary(&NMSDK::SourceLibrary);
 env->AddClassLibrary(&NMSDK::ReceiverLibrary);
 env->AddClassLibrary(&NMSDK::PulseLibrary);
 env->AddClassLibrary(&NMSDK::NeuronLifeLibrary);
 env->AddClassLibrary(&NMSDK::PulseNeuronLibrary);

 env->AddClassLibrary(&NMSDK::MotionControlLibrary);

 env->AddClassLibrary(&NMSDK::WinAPIActLibrary);
 return env;
}

extern RDK::UEngine* CreateNewEngine(void)
{
 return new RDK::UEngine;
}
/*****************************************************************************/

#endif
