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
 RDK::UItemData::DefaultDataSize=sizeof(double);
 NMSDK::NEnvironment* env=new NMSDK::NEnvironment;

 env->AddClassLibrary(&NMSDK::BCLLibrary);
 env->AddClassLibrary(&NMSDK::ActLibrary);
// env->AddClassLibrary(&NMSDK::CRLibrary);
 env->AddClassLibrary(&NMSDK::MathLibrary);
 env->AddClassLibrary(&NMSDK::PhysLibrary);
 env->AddClassLibrary(&NMSDK::SensorLibrary);
 env->AddClassLibrary(&NMSDK::SourceLibrary);
 env->AddClassLibrary(&NMSDK::ReceiverLibrary);
 env->AddClassLibrary(&NMSDK::PulseLibrary);
 env->AddClassLibrary(&NMSDK::NeuronLifeLibrary);
 env->AddClassLibrary(&NMSDK::PulseNeuronLibrary);

 env->AddClassLibrary(&NMSDK::MotionControlLibrary);

 return env;
}

extern RDK::UEngine* CreateNewEngine(void)
{
 return new RDK::UEngine;
}
/*****************************************************************************/
#endif
