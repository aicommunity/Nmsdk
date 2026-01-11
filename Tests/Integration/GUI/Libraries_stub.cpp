// Stub implementation for Libraries for unit tests
// Uses RdkDummyLibraries instead of full Libraries.cpp to avoid dependencies

#include "RdkDummyLibraries.h"
#include "UEngine.h"
#include "UStorage.h"

namespace RDK {

/// Функция должна быть реализована в конечном проекте
/// и загружать функции формирования свойств для фиктивных компонентов из библиотек
bool RDK_CALL RdkLoadPredefinedCrPropFunctions(RDK::UStorage* storage)
{
    // Stub implementation - not used in movement tests
    return true;
}

}
