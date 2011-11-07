/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NCRLibraryH
#define NCRLibraryH

#include "../../Kernel/NLibrary.h"

#include "NCRPerseptron.h"
#include "NCRDirectCompare.h"
#include "NCRDistance.h"
#include "NCRFusion.h"

namespace NMSDK {

class NCRLibrary: public NLibrary
{
public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NCRLibrary(void);
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
// ��������� ������ ClassSamples �������� ������������ �������� � �� �������.
// �� ��������� ��������������� ������� ������� � ������ ������.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};                   

extern NCRLibrary CRLibrary;

}


#endif
