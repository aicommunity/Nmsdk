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
#ifndef NLibraryH
#define NLibraryH

#include "rdk.h"
#include "NBios.h"

namespace NMSDK {

class NLibrary: public RDK::UALibrary
{
protected: // ���������

protected: // ������ ��������

private: // ���������� ������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NLibrary(const string &name, const string &version);
~NLibrary(void);
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
// ������ ����������
// --------------------------
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
// --------------------------
// ������ ����������� �����������
// --------------------------
protected:
// ��������� ������ ClassSamples �������� ������������ �������� � �� �������.
// �� ��������� ��������������� ������� ������� � ������ ������.
virtual void CreateClassSamples(RDK::UAStorage *storage);
virtual void ACreateClassSamples(NStorage *storage)=0;
// --------------------------
};

}

#endif
