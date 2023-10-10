#include "Libraries.h"

namespace RDK {

/// Функция должна быть реализована в конечном проекте и загружать требуемые библиотеки
bool RDK_CALL RdkLoadPredefinedLibraries(std::list<RDK::ULibrary*> &libs_list)
{
 using namespace NMSDK;
// RDK::UItemData::DefaultDataSize=sizeof(double);
 libs_list.push_back(&RDK::BasicLibrary);
 libs_list.push_back(&RDK::CvBasicLibrary);
#ifndef __BORLANDC__
#ifdef RDK_USE_PYTHON
 libs_list.push_back(&RDK::PyMachineLearningLib);
#endif
#ifdef RDK_USE_TENSORFLOW
 libs_list.push_back(&RDK::TensorflowLib);
#endif
#endif


 libs_list.push_back(&NMSDK::ActLibrary);
 libs_list.push_back(&NMSDK::PhysLibrary);
 libs_list.push_back(&NMSDK::SensorLibrary);
 libs_list.push_back(&NMSDK::NeuronSourceLibrary);
 libs_list.push_back(&NMSDK::ReceiverLibrary);
 libs_list.push_back(&NMSDK::PulseLibrary);
 #ifndef NMSDK_DEBUG
 #ifndef NO_MOTION_CONTROL
libs_list.push_back(&NMSDK::MotionControlLibrary);
 #endif
 #endif
 #ifndef __GNUC__
// libs_list.push_back(&NMSDK::WinAPIActLibrary);
 #endif
// libs_list.push_back(&RDK::YCorticalLibrary);
 return true;
}

/// Функция должна быть реализована в конечном проекте
/// и загружать функции формирования свойств для фиктивных компонентов из библиотек
extern RDK_LIB_TYPE bool RDK_CALL RdkLoadPredefinedCrPropFunctions(RDK::UStorage* storage)
{

 storage->AddCrPropMockFunc(CvBasicLib::CvBasicLibCrPropMock);

 return true;
}

/// Функция должна быть реализована в конечном проекте
bool RDK_CALL RdkCreatePredefinedStructure(RDK::UEnvironment* env, int predefined_structure)
{
 return true;
}

}
