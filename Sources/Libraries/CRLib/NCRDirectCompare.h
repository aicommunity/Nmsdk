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

#ifndef NCRDirectCompareH
#define NCRDirectCompareH

#include "NACRClassifier.h"

namespace NMSDK {

class NCRDirectCompare: public NACRClassifier
{
public: // ������������� ��������
// ����� ������ ����
//RDK::ULProperty<size_t, NCRDirectCompare> NumInputs;

// ����� ������������� �� ��������� ����� ����������
// � ��������� �� ��������� ������ (0,1)
RDK::ULProperty<real,NCRDirectCompare> MaxRecThreshold;

RDK::ULProperty<real,NCRDirectCompare> MinRecThreshold;

RDK::ULProperty<real,NCRDirectCompare> MiddleRecThreshold;

RDK::ULProperty<real,NCRDirectCompare> AbsoluteRecThreshold;

// ������� �������� ������������ ���������� (�� �������� ���� ����������)
RDK::ULProperty<real,NCRDirectCompare> ReliabilityDistance;

// ����� �������� ������������� ���������� �� ����������� �������� ���������
RDK::ULProperty<real,NCRDirectCompare> ReliabilityValue;

// ��� �������������
// 0 - �� ��������� ������� �� ���� �������
// 1 - �� ��������� ����� ���������� ���������� ������ �� ���� �������
// 2 - �� ��������� ����� ���������� �������������� ������ �� ���� �������
// 3 - �� ����� ���������� �������������� ������ �� ���� �������
// 4 - ���������� 1 �� � 2 �������� ������
// 		���� max - �� ����� ������
//		���� max - �� ������� ������
// 5 - ����������� ��������
// 6 - �������� �� 5 ����������
// 10 - ������������ ������ �� �����
RDK::ULProperty<int,NCRDirectCompare> RecognitionType;

protected: // ������ ������
//public:
// ��������� �������
vector<vector<vector<real> > > Samples;

// ������ ������ ����
//vector<real> Inputs;

// ������ ������������ ������� ����� ����
vector<real> NativeOutput;

protected: // ������ � ��������� �������� ����

protected: // ��������� ����������


public:
// --------------------------
// ������������ � �����������
// --------------------------
NCRDirectCompare(void);
~NCRDirectCompare(void);
// --------------------------

protected:
// -----------------------------
// ������ ���������� �������������� ����������
// -----------------------------
// ������������� ����� ������ ���� ������� �����
//bool SetNumInputs(size_t numinputs);

// ����� ������������� �� ��������� ����� ����������
bool SetMaxRecThreshold(real value);
// -----------------------------

// -----------------------------
// ������ ������� � ������ ������
// -----------------------------
public:
// ������ �������
real GetSamples(int i, int j, int k) const;

// ������ ������������ ������� ����� ����
const vector<real>& GetNativeOutput(void) const;

// ������ ������
//const vector<real>& GetInputs(void) const;
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
virtual RDK::UAContainer* New(void);
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
public:
// ������������� �������� �������� ������� ��� �������������
//virtual bool SetInput(const Real &input);
// ------------------------
};

}

//---------------------------------------------------------------------------
#endif
