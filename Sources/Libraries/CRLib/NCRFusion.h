// ===========================================================
// Version:        3.0.4
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

#ifndef NCRFusionH
#define NCRFusionH

#include "NACRClassifier.h"

namespace NMSDK {

// ��������� ���������� ��������������� �������� �������������
struct NCRFPreResult
{
 // ������� ������������ �������
 int Ix1, Ix2;

 // ��������� �������������
 real Res1, Res2;

 NCRFPreResult(void)
 {
  Ix1=Ix2=0;
  Res1=Res2=0;
 };

};


class NCRFusion: public NACRClassifier
{
public: // ������������� ��������
// ����� ���������������� ���������������
// 0 - �� �������� ����������� ��������
// 1 - �� ��������� ���������
// 2 - �� �������� ������
// 3 - �� ����� ����������� ������
// 4 - �� ����� ������
// 5 - �� ����� ����� �� ������
// 6 - �� ����� ������-�����������
RDK::ULProperty<int, NCRFusion> FusionMode;

// ����� ����� ���������� �� �������
RDK::ULProperty<int, NCRFusion> NumAttempts;

// ����� ���������� �� �������
// 1 - ������� ���� �������
// 2 - ������� �� ���������� ����������� �������� ��� ������
// 3 - �� ����� ����������� ������
RDK::ULProperty<int, NCRFusion> AccumulateMode;

// ��������� ��������� ���������
RDK::UCLStateProperty<vector<vector<real> >, NCRFusion> PreResultsWeigths;

protected: // ������ ������
// ������� �������� ����������
int CurrentAttempt;


protected: // ������ � ��������� �������� ����

protected: // ��������� ����������
vector<RDK::UItemData> AccumOutput;

public:
// --------------------------
// ������������ � �����������
// --------------------------
NCRFusion(void);
~NCRFusion(void);
// --------------------------

protected:
// -----------------------------
// ������ ���������� �������������� ����������
// -----------------------------
bool SetFusionMode(int value);
// -----------------------------

// -----------------------------
// ������ ������� � ������ ������
// -----------------------------
public:
// ������� �������� ����������
int GetCurrentAttempt(void) const;
// -----------------------------

// ------------------------
// ������ �����
// ------------------------
public:
// ��������� ��������� ����� �� ����� � ������ 'name'
virtual bool AFileLoad(fstream &file);

// ��������� ��������� ����� � ���� � ������ 'name'
virtual bool AFileSave(fstream &file);
// ------------------------

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
virtual bool ACRDefault(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ACRBuild(void);

// ����� �������� �����.
virtual bool ACRReset(void);

// ��������� ������ ����� ������� �� ������� ����.
virtual bool ACRCalculate(void);
// --------------------------

// --------------------------
// ������� ������ �������� ����
// --------------------------
protected:
// ����� �������� �������� � �������� ���������
virtual void AResetTraining(void);

// ����������� �������� �� �������� �������
virtual real ATrain(size_t exp_class);
// --------------------------

// ------------------------
// ������� ������ �����
// ------------------------
protected:
// ���������� ���������� ��� �������� �� ���������� ��������
bool AverageQualityCalculate(void);

// ���������� ���������� ��� �������� �� ������
bool AverageInputCalculate(void);

// ���������� ���������� ��� ����� �� ������
bool SumInputCalculate(void);

// ���������� ���������� �� ����� ����������� ������ �� ������
bool InputRecognitionCounterCalculate(void);

// ���������� ���������� �� ����� ������-�����������
bool SumInputRecognitionCounterCalculate(void);

// ���������� ���������� ����� �������� ���������
bool PairCalculate(void);

// ���������� ���������� �� ����� ����������� ������
bool RecognitionCounterCalculate(void);

public:
// ������������� �������� �������� ������� ��� �������������
virtual bool SetInput(const Real &input);
// ------------------------
};

}
//---------------------------------------------------------------------------
#endif
