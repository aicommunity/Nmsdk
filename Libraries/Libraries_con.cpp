﻿#include "Libraries_con.h"

namespace RDK {

/// Функция должна быть реализована в конечном проекте и загружать требуемые библиотеки
bool RDK_CALL RdkLoadPredefinedLibraries(std::list<RDK::ULibrary*> &libs_list)
{
// RDK::UItemData::DefaultDataSize=sizeof(double);
 libs_list.push_back(&RDK::BasicLibrary);
 libs_list.push_back(&RDK::CvBasicLibrary);
 libs_list.push_back(&RDK::HardwareLibrary);
 //libs_list.push_back(&RDK::TensorflowLibrary);

 libs_list.push_back(&NMSDK::PulseLibrary);
 #ifndef NMSDK_DEBUG
 libs_list.push_back(&NMSDK::MotionControlLibrary);
 #endif
 #ifndef __GNUC__
 libs_list.push_back(&NMSDK::WinAPIActLibrary);
 #endif

// libs_list.push_back(&RDK::PyMachineLearningLib);

 return true;
}

/// Функция должна быть реализована в конечном проекте
bool RDK_CALL RdkCreatePredefinedStructure(RDK::UEnvironment* env, int predefined_structure)
{
 return true;
}

}
