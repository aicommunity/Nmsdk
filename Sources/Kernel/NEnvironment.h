/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002-2009.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		2.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NENVIRONMENT_H
#define NENVIRONMENT_H

#include "rdk.h"
#include "NBios.h"
#include "NLibrary.h"
#include "../Libraries/BCL/NModel.h"
#include "../GUI/NGraphics.h"
#include "NController.h"

namespace NMSDK {

class NEnvironment: public RDK::UAContainerEnvironment
{
protected: // ���������

protected: // ������

protected: // �����������
// ������ ����������� ������������
// <����������, ����, ����������� ������� ���������� �����>
map<NController*, bool> Controllers;

protected: // ������ ������������ ��������� ������������
// ������������� ������
map<ULongId, NGraphics*> Graphics;

public: // Public methods
// --------------------------
// Constructors & destructors
// --------------------------
NEnvironment(void);
virtual ~NEnvironment(void);
// --------------------------

// --------------------------
// ������ ���������� ������� �����
// --------------------------
// ���������� ��������� �� ������
RDK::UEPtr<NModel> GetModel(void);

// ���������� ������� ������
virtual bool DestroyModel(void);
// --------------------------

// --------------------------
// ������ ���������� �������
// --------------------------
// ��������� ������ ��������� ������ � ������
// ���������� ��������� �� ����������� ������
RDK::UEPtr<NAContainer> AddObject(const NameT &classname);

// ��������� ������ ��������� ������ 'classname' � ������
// � ������, ���� ������ � ������ 'objectname' �� ������ � ������
// ���������� ��������� �� ������
// ����� �� ����������� ������� ����� 'objectname', ���� ����� ��� ��� ������� � ������
RDK::UEPtr<NAContainer> AddObject(const NameT &objectname, const NameT &classname);
// --------------------------

// --------------------------
// ������ ���������� �������������
// --------------------------
// ��������� ����������
bool AddController(NController* controller, bool delenabled);

// ������� ����������
bool DelController(NController* controller);

// ������� ��� �����������
bool DelAllControllers(void);

// ������ ������������ ������������
map<NController*, bool>::iterator GetFirstController(void);
map<NController*, bool>::iterator GetLastController(void);
// --------------------------

// --------------------------
// ��������� ������� � ������ �����
// --------------------------
// ���������� ��������� �� ������
RDK::UEPtr<NModel> const operator -> (void);

// ���������� ��������� �� ��������� ������ �� �������� �����
// �������� ��������� ���������� �������
// ���� ��������� �� ������, �� ���������� 0 � ���������� ������� ���������
RDK::UEPtr<NAContainer> operator () (const string &longname);

// ���������� ��������� �� ��������� ������ �� �������� ��������������
// �������� ��������� ���������� �������
// ���� ��������� �� ������, �� ���������� 0 � ���������� ������� ���������
RDK::UEPtr<NAContainer> operator () (const ULongId &longid);

// ���������� ��������� �� ������� ��������� ������
RDK::UEPtr<NAContainer> operator () (void);
// --------------------------

// --------------------------
// ������ ������������ ��������� ������������
// --------------------------
// ���������� ������ ��������������
const map<ULongId, NGraphics*>& GetGraphics(void) const;

// ���������� ������������ ��� ��������� id
NGraphics* GetGraphics(const ULongId &id);

// ��������� ������� ������������� ��� �������� ����
bool CheckGraphics(const ULongId &id) const;

// ��������� ����� ������������
// �� ������ ������ ���� ������������ ��� �����
// ���������� ��������� ������������
// ����� �� ����� �� ���� ������ ������������ ������ �������
NGraphics* AddGraphics(const ULongId &id, NGraphics *graphics);

// ������� ������������ ���� id
bool DelGraphics(const ULongId &id);
// --------------------------

// --------------------------
// ������ ������������� �����
// --------------------------
// --------------------------

// --------------------------
// ������ ������� � ������ ���������
// --------------------------
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
protected:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ABuild(void);

// ����� �������� �����.
virtual bool AReset(void);

// ��������� ������ ����� �������
virtual bool ACalculate(void);
// --------------------------

// --------------------------
// ��������������� ������ ������������� �����
// --------------------------
protected:
/*
// ��������� ������������ ���������� � ����������� ��������� � ����������
// ��������� �� ����.
// � ������� ������ �� ������ ������ � ���������� 0.
virtual RDK::UAStorage* LoadStorageLibrary(const string &filename);

// ��������� ������������ ���������� � ����������� ���������.
// � ������� ������ �� ������ ������ � ���������� true.
virtual bool UnLoadStorageLibrary(void);

// ��������� ������������ ���������� � ������� �������� �������
// � ���� ���������� ��������� � ���������� ��������� �� ����.
// � ������� ������ �� ������ ������ � ���������� 0.
virtual RDK::UAStorage* LoadClassLibrary(const string &libname, const string &filename);

// ��������� ������������ ���������� � ������� �������� �������.
// � ������� ������ �� ������ ������ � ���������� true.
virtual bool UnLoadClassLibrary(const string &libname);     */
// --------------------------
};

}
#endif
