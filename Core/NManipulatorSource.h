// ===========================================================
// Version:        3.0.2
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:        alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NMANIPULATOR_SOURCE_H
#define NMANIPULATOR_SOURCE_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NManipulatorSource: public NSource
{
public: // ������������� ��������
// ���� ��������� ������
RDK::ULProperty<real,NManipulatorSource> Angle;
// ������� ��������
RDK::ULProperty<real,NManipulatorSource> Speed;
// ������ ���������
RDK::ULProperty<real,NManipulatorSource> Force;

RDK::ULProperty<real,NManipulatorSource> Movement;
protected: // �������� ��������


public: // ������
bool UpdateOutputFlag;
// --------------------------
// ������������ � �����������
// --------------------------
NManipulatorSource(void);
virtual ~NManipulatorSource(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� ����
bool SetAngle(const real &value);
// ������������� ��������
bool SetSpeed(const real &value);
// ������������� ������
bool SetForce(const real &value);
// --------------------------

public:
// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NManipulatorSource* New(void);
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
virtual bool ACalculate(void);
// --------------------------
};

}
#endif

