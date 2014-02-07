#ifndef NMSDK_WINAPI_CPP
#define NMSDK_WINAPI_CPP

#include "nmsdk.h"
#include "../../Libraries/NWinAPILibraries.h"

/*****************************************************************************/
extern NMSDK::UStorage* CreateNewStorage(void)
{
 NMSDK::UStorage* storage=new NMSDK::UStorage;
 storage->AddClassLibrary(&NMSDK::BCLLibrary);
 storage->AddClassLibrary(&NMSDK::ActLibrary);
// storage->AddClassLibrary(&NMSDK::CRLibrary);
 storage->AddClassLibrary(&NMSDK::MathLibrary);
 storage->AddClassLibrary(&NMSDK::PhysLibrary);
 storage->AddClassLibrary(&NMSDK::SensorLibrary);
 storage->AddClassLibrary(&NMSDK::SourceLibrary);
 storage->AddClassLibrary(&NMSDK::ReceiverLibrary);
 storage->AddClassLibrary(&NMSDK::PulseLibrary);
 storage->AddClassLibrary(&NMSDK::NeuronLifeLibrary);
 storage->AddClassLibrary(&NMSDK::PulseNeuronLibrary);

 storage->AddClassLibrary(&NMSDK::MotionControlLibrary);

 storage->AddClassLibrary(&NMSDK::WinAPIActLibrary);

 return storage;
}

extern NMSDK::UEnvironment* CreateNewEnvironment(void)
{
 RDK::UItemData::DefaultDataSize=sizeof(double);
 NMSDK::UEnvironment* env=new NMSDK::UEnvironment;

 return env;
}

extern RDK::UEngine* CreateNewEngine(void)
{
 return new RDK::UEngine;
}
/*****************************************************************************/

#endif
