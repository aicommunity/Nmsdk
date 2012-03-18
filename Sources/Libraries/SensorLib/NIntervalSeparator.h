// ===========================================================
// Version:        1.0.0
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

#ifndef NINTERVAL_SEPARATOR_H
#define NINTERVAL_SEPARATOR_H

#include "../../Kernel/NBios.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

class NIntervalSeparator: public NANet
{
public: // ������������� ��������
// ������ ������� ����������� ���������
RDK::UCLProperty<Real,NIntervalSeparator> MinRange;

// ������� ������� ����������� ���������
RDK::UCLProperty<Real,NIntervalSeparator> MaxRange;

// ����� ����������
// 0 - ���� �������� �������� � �������� ��������, �� ��� � ������������, ����� 0
// 1 - ���� �������� �������� � �������� ��������, �� ������������ �������� �����
// ������ ������� ���������, ����� 0
// 2 - ���� �������� ��������� ������ �������, �� ��� � ������������, ����� 0
// 3 - ���� �������� ���� ������� �������, �� ��� � ������������, ����� 0
// 4 - ���� �������� ��������� ������ �������, �� ������������ �������� �����
// 5 - ���� �������� ��������� ������ �������, �� ������������ �������� �����
// ������ ������� ���������;���� �������� ��������� ������� �������, �� ������������
// ������� ������� ����� ������ �������
RDK::UCLProperty<vector<int>,NIntervalSeparator> Mode;

// ��������� ��������� ��������
RDK::UCLProperty<Real,NIntervalSeparator> Gain;



protected: // �������� ��������

protected: // ��������� ����������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NIntervalSeparator(void);
virtual ~NIntervalSeparator(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������ ������� ����������� ���������
bool SetMinRange(real value);

// ������� ������� ����������� ���������
bool SetMaxRange(real value);

// ����� ����������
bool SetMode(int value);

// ��������� ��������� ��������
bool SetGain(real value);
// --------------------------

public:
// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NIntervalSeparator* New(void);
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
