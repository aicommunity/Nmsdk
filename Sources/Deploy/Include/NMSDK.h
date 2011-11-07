#ifndef NMSDK_H
#define NMSDK_H

#include "../../Kernel/NKernel.h"
#include "../../Libraries/NLibraries.h"
#include "../../GUI/NGraphics.h"

namespace NMSDK {

// ������� ������ ��������� � ���������� ��������� �� ����
RDK::UAContainerStorage* NewNStorage(void);

// ������� ����� � ���������� ��������� �� ���
RDK::UAContainerEnvironment* NewNEnvironment(void);

}

#endif