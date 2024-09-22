#ifndef NMSDK_LIBRARIES_H
#define NMSDK_LIBRARIES_H

#include "../Rdk/Deploy/Include/rdk.h"

#include "Rdk-BasicLib/Deploy/Include/Lib.h"
#include "Rdk-CvBasicLib/Deploy/Include/Lib.h"
#include "Rdk-HardwareLib/Core/UHardwareLib.h"

#ifndef __BORLANDC__
#ifdef RDK_USE_PYTHON
#include "Rdk-PyMachineLearningLib/Core/Lib.h"
#endif

#ifdef RDK_USE_TENSORFLOW
#include "Rdk-TensorflowLib/Core/Lib.h"
#endif

#endif
#include "Nmsdk-MotionControlLib/Deploy/Include/Lib.h"
#include "Nmsdk-PulseLib/Deploy/Include/Lib.h"

namespace RDK {

/// Функция должна быть реализована в конечном проекте и загружать требуемые библиотеки
extern RDK_LIB_TYPE bool RDK_CALL RdkLoadPredefinedLibraries(std::list<RDK::ULibrary*> &libs_list);

/// Функция должна быть реализована в конечном проекте
extern RDK_LIB_TYPE bool RDK_CALL RdkCreatePredefinedStructure(RDK::UEnvironment* env, int predefined_structure);

/// Функция должна быть реализована в конечном проекте
/// и загружать функции формирования свойств для фиктивных компонентов из библиотек
extern RDK_LIB_TYPE bool RDK_CALL RdkLoadPredefinedCrPropFunctions(RDK::UStorage* storage);

}

#endif
