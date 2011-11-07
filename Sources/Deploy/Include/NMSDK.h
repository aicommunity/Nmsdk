#ifndef NMSDK_H
#define NMSDK_H

#include "../../Kernel/NKernel.h"
#include "../../Libraries/NLibraries.h"
#include "../../GUI/NGraphics.h"

namespace NMSDK {

// —оздает пустое хранилище и возвращает указатель на него
RDK::UAContainerStorage* NewNStorage(void);

// —оздает среду и возвращает указатель на нее
RDK::UAContainerEnvironment* NewNEnvironment(void);

}

#endif