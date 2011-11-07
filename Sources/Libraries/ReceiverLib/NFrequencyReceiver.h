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

#ifndef NFrequencyReceiverH
#define NFrequencyReceiverH
#include "../BCL/NReceiver.h"

//---------------------------------------------------------------------------
namespace NMSDK {

/* *************************************************************************** */
class NFrequencyReceiver: public NReceiver
{
public: // ������������� ��������
// ����������� �������� ������
RDK::ULProperty<real, NFrequencyReceiver> LeftRange,RightRange;

// ��� �� �������
RDK::ULProperty<real, NFrequencyReceiver> FrequencyStep;

protected: // ������
// ��������� ����� ���������
RDK::ULProperty<size_t, NFrequencyReceiver> PulseCounter;

// ����� �����������
Real XResults,YResults;

protected: // ��������� ����������
real PrevPulseStartTime;
real PrevPulseStopTime;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NFrequencyReceiver(void);
virtual ~NFrequencyReceiver(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NFrequencyReceiver* New(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� ����� ������� ������������ ��������� ������
bool SetLeftRange(real range);

// ������������� ������ ������� ������������ ��������� ������
bool SetRightRange(real range);

// ������������� ��� �� �������
bool SetFrequencyStep(real step);
// --------------------------

// --------------------------
// Watch results control methods
// --------------------------
public:
// Return number of results points
size_t GetResultsSize(void) const;

// Return iterator pointed to farthest X result
const Real& GetXResult(void) const;
real GetXResult(int i) const;

// Return iterator pointed to farthest Y result
const Real& GetYResult(void) const;
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
