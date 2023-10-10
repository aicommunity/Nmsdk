#ifndef NMSDK_LIBRARIES_H
#define NMSDK_LIBRARIES_H

#include "../Rdk/Deploy/Include/rdk.h"

#include "Rdk-BasicLib/Deploy/Include/Lib.h"
#include "Rdk-CvBasicLib/Deploy/Include/Lib.h"
//#include "Rdk-TensorflowLib/Core/UTensorflowLib.h"
#include "Nmsdk-MotionControlLib/Deploy/Include/Lib.h"
#include "Nmsdk-PulseLib/Deploy/Include/Lib.h"
//#include "Rdk-PyMachineLearningLib/Core/Lib.h"

namespace RDK {

/// Функция должна быть реализована в конечном проекте и загружать требуемые библиотеки
extern RDK_LIB_TYPE bool RDK_CALL RdkLoadPredefinedLibraries(std::list<RDK::ULibrary*> &libs_list);

/// Функция должна быть реализована в конечном проекте
extern RDK_LIB_TYPE bool RDK_CALL RdkCreatePredefinedStructure(RDK::UEnvironment* env, int predefined_structure);

}

#endif
