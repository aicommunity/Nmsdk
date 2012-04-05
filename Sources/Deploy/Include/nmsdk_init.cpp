#ifndef NMSDK_INIT_CPP
#define NMSDK_INIT_CPP

#include "nmsdk_init.h"
#include "rdk_init.cpp"
#include "nmsdk.h"
								 /*
int RDK_CALL NMSDK_EngineInit(int predefined_structure, void* exception_handler)
{
 LoadEngine((void*)NMSDK::CreateNewNStorage, (void*)NMSDK::CreateNewNEnvironment, (void*)NMSDK::CreateNewNEngine);
 Engine_SetExceptionHandler(exception_handler);
 Init();
 LoadPredefinedLibraries();

 Env_SetPredefinedStructure(predefined_structure);
 Env_CreateStructure();

 return 0;
}                */


#endif

