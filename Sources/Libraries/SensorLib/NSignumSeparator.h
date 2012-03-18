// ===========================================================
// Version:        1.0.1
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NAPC_H
#define NAPC_H

#include "../../Kernel/NBios.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

class NSignumSeparator: public NANet
{
public: // ������������� ��������
// ���������� ����
// ����� ��������� �������� +-1
RDK::UCLProperty<Real,NSignumSeparator> Sign;

// ��������� ��������� ��������
RDK::UCLProperty<Real,NSignumSeparator> Gain;

protected: // �������� ��������

protected: // ��������� ����������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NSignumSeparator(void);
virtual ~NSignumSeparator(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ���������� ����
bool SetSign(real value);

// ��������� ��������� ��������
bool SetGain(real value);
// --------------------------

public:
// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NSignumSeparator* New(void);
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
};

}
#endif
