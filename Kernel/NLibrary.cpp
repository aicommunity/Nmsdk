/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#include "NLibrary.h"

namespace NMSDK {

// --------------------------
// ������������ � �����������
// --------------------------
NLibrary::NLibrary(const string &name, const string &version)
 : RDK::UALibrary(name,version)
{
}

NLibrary::~NLibrary(void)
{
}
// --------------------------

// --------------------------
// ������ ������� � ���������� ����������
// --------------------------
// --------------------------

// --------------------------
// ������ ������� � ������ ��������
// --------------------------
// --------------------------

// --------------------------
// ������ ������� � ������ ����������
// --------------------------
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
void NLibrary::CreateClassSamples(RDK::UAStorage *storage)
{
 ACreateClassSamples(reinterpret_cast<NStorage*>(storage));
}
// --------------------------




}

//---------------------------------------------------------------------------

