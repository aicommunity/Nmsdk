#ifndef NMSDK_WINAPI_CPP
#define NMSDK_WINAPI_CPP

#include "nmsdk.h"
#include "../../Libraries/NWinAPILibraries.h"

/*****************************************************************************/
extern NMSDK::UStorage* CreateNewStorage(void)
{
 NMSDK::UStorage* storage=new NMSDK::UStorage;
 storage->AddCollection(&NMSDK::BCLLibrary);
 storage->AddCollection(&NMSDK::ActLibrary);
// storage->AddCollection(&NMSDK::CRLibrary);
 storage->AddCollection(&NMSDK::MathLibrary);
 storage->AddCollection(&NMSDK::PhysLibrary);
 storage->AddCollection(&NMSDK::SensorLibrary);
 storage->AddCollection(&NMSDK::SourceLibrary);
 storage->AddCollection(&NMSDK::ReceiverLibrary);
 storage->AddCollection(&NMSDK::PulseLibrary);
 storage->AddCollection(&NMSDK::NeuronLifeLibrary);
 storage->AddCollection(&NMSDK::PulseNeuronLibrary);

 storage->AddCollection(&NMSDK::MotionControlLibrary);

 storage->AddCollection(&NMSDK::WinAPIActLibrary);

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
