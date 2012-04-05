#ifndef NMSDK_NEW_CPP
#define NMSDK_NEW_CPP

#include "nmsdk.h"

/*****************************************************************************/
extern NMSDK::NStorage* CreateNewStorage(void)
{
 return new NMSDK::NStorage;
}

extern NMSDK::NEnvironment* CreateNewEnvironment(void)
{
 NMSDK::NEnvironment* env=new NMSDK::NEnvironment;

 env->AddClassLibrary(&NMSDK::BCLLibrary);
 env->AddClassLibrary(&ActLibrary);
 env->AddClassLibrary(&CRLibrary);
 env->AddClassLibrary(&MathLibrary);
 env->AddClassLibrary(&PhysLibrary);
 env->AddClassLibrary(&SensorLibrary);
 env->AddClassLibrary(&SourceLibrary);
 env->AddClassLibrary(&ReceiverLibrary);
 env->AddClassLibrary(&PulseLibrary);
 env->AddClassLibrary(&NeuronLifeLibrary);
 env->AddClassLibrary(&PulseNeuronLibrary);

 env->AddClassLibrary(&MotionControlLibrary);

 return env;
}

extern RDK::UEngine* CreateNewEngine(void)
{
 return new RDK::UEngine;
}
/*****************************************************************************/
#endif
