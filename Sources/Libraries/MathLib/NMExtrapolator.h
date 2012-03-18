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

#ifndef NMExtrapolatorH
#define NMExtrapolatorH

#include "../../Kernel/NBios.h"
#include "rdk.h"
//---------------------------------------------------------------------------

namespace NMSDK {

class NMExtrapolator: public NANet
{
public: // ������������� ��������
// ����� ��������, �
RDK::ULProperty<RDK::UTime,NMExtrapolator> PredictionTime;

// ����� ������� ����
RDK::ULProperty<size_t,NMExtrapolator> NumLevels;

protected: // ���������� ������
// ������������ ������������ �������
vector<size_t> PascalCoeffs;

protected: // ��������� ����������
// ������� �������
RDK::UQueue<Real> History;
//vector<Real> History2;

// ������� ���������� �������
int HistoryCounter;

public:
// --------------------------
// ������������ � �����������
// --------------------------
NMExtrapolator(void);
virtual ~NMExtrapolator(void);
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ����� ��������, �
bool SetPredictionTime(RDK::UTime ptime);

// ����� ������� ����
bool SetNumLevels(size_t value);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NAContainer* New(void);
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
// ������� ������ �����
// --------------------------
protected:
// ��������� ������������ ������������ �������
void CalcPascalCoeff(size_t level, vector<size_t> &coeffs);
// --------------------------
};

}

#endif
