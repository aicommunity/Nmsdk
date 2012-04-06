// ===========================================================
// Version:        3.0.2
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

#ifndef NSINUS_GENERATOR_H
#define NSINUS_GENERATOR_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NSinusGenerator: public NSource
{
public: // ������������� ��������
// ��������� ������
RDK::ULProperty<real,NSinusGenerator> Amplitude;

// ������� ��������� (��)
RDK::ULProperty<real,NSinusGenerator> Frequency;

protected: // �������� ��������

public: // ��������� ����������
// ������� �������
RDK::ULProperty<real,NSinusGenerator> TimeCounter;


public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NSinusGenerator(void);
virtual ~NSinusGenerator(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� ��������� ������
bool SetAmplitude(real value);

// ������������� ������� ���������
bool SetFrequency(real value);
// --------------------------

public:
// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NSinusGenerator* New(void);
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

