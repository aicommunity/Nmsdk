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

#ifndef NPULSE_GENERATOR_H
#define NPULSE_GENERATOR_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NPulseGenerator: public NSource
{
public: // ������������� ��������
// ������� ��������� (��) (�������������� ��������)
RDK::ULProperty<real,NPulseGenerator> Frequency;

// ������������ �������� (�)
RDK::ULProperty<real,NPulseGenerator> PulseLength;

// ��������� ��������
RDK::ULProperty<real,NPulseGenerator> Amplitude;

// ���������� �������
// (������ ��������, �� �������� ����������� �����������!)
RDK::ULProperty<real,NPulseGenerator> FrequencyDeviation;

protected: // �������� ��������

public: // ��������� ����������
// ������� ��������
RDK::ULStateProperty<RDK::UTime,NPulseGenerator> PulseCounter;

// ��������� �������� ������� �������
RDK::ULStateProperty<real,NPulseGenerator> RandomFrequency;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NPulseGenerator(void);
virtual ~NPulseGenerator(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� ������� ���������
bool SetFrequency(real value);

// ������������� ������������ ��������
bool SetPulseLength(real value);

// ������������� ��������� ���������
bool SetAmplitude(real value);

// ������������� ��������� ���������� �������
// (������ ��������, �� �������� ����������� �����������!)
bool SetFrequencyDeviation(real value);
// --------------------------

public:
// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NPulseGenerator* New(void);
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;
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

