// ===========================================================
// Version:        1.0.0
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

#ifndef NManipulatorH
#define NManipulatorH
#include "../../Kernel/NBios.h"

//---------------------------------------------------------------------------
namespace NMSDK {

/* *************************************************************************** */
class NManipulator: public NADItem
{
public: // ������������� ��������
// ���������������� �����������
RDK::ULProperty<real, NManipulator> EMFactor;

// �������������
RDK::ULProperty<real, NManipulator> Inductance;

// �������������
RDK::ULProperty<real, NManipulator> Resistance;

protected: // ������

protected: // ��������� ����������
// ��� �����
real Current;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NManipulator(void);
virtual ~NManipulator(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NManipulator* New(void);
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
