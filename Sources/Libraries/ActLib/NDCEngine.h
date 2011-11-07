// ===========================================================
// Version:        1.0.1
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:			alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NDCEngineH
#define NDCEngineH
#include "../../Kernel/NBios.h"

//---------------------------------------------------------------------------
namespace NMSDK {

/* *************************************************************************** */
class NDCEngine: public NADItem
{
public: // ������������� ��������
// ���������������� �����������
RDK::ULProperty<real, NDCEngine> EMFactor;

// �������������
RDK::ULProperty<real, NDCEngine> Inductance;

// �������������
RDK::ULProperty<real, NDCEngine> Resistance;

// ������������������� ���������� �������
RDK::ULProperty<real, NDCEngine> Tm;

// ������������ �����
RDK::ULProperty<real, NDCEngine> ReductionRate;

// ������� ������
RDK::ULProperty<real, NDCEngine> OutMoment;

protected: // ������

protected: // ��������� ����������
// ��� �����
real Current;

// ��� �����
real EMF;

// ���� ��������
real Angle;

// ������ ����������� ����������
real Moment;

// ������� ��������
real AngleSpeed;

// ����������� �������
real DiffMoment;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NDCEngine(void);
//NDCEngine(const string &name);
virtual ~NDCEngine(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NDCEngine* New(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ���������������� �����������
bool SetEMFactor(real value);

// �������������
bool SetInductance(real value);

// �������������
bool SetResistance(real value);

// ������������������� ���������� �������
bool SetTm(real value);

// ������������ �����
bool SetReductionRate(real value);
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ABuild(void);

// Reset computation
virtual bool AReset(void);

// Execute math. computations of current object on current step
virtual bool ACalculate(void);
// --------------------------
};
/* *************************************************************************** */


}
//---------------------------------------------------------------------------
#endif
