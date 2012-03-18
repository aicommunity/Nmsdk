// ===========================================================
// Version:        3.0.3
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NSOURCE_H
#define NSOURCE_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NSource: public NANet
{
public: // ������������� ��������
// ������������ ������ � ������� ��������� (�)
// 0 - ���������� ������
RDK::ULProperty<RDK::UTime,NSource> ActionPeriod;

protected: // �������� ��������

protected: // ��������� ����������
RDK::ULProperty<RDK::UTime,NSource> ActionCounter;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NSource(void);
virtual ~NSource(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������ ������ � ������� ���������
bool SetActionPeriod(RDK::UTime value);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NSource* New(void);
// --------------------------


// --------------------------
// ������� ������ ���������� ������
// --------------------------
protected:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);

// ����� �������� �����.
virtual bool AReset(void);

// ��������� ������ ����� �������
//virtual bool ACalculate(void);
// --------------------------
};

}
#endif



