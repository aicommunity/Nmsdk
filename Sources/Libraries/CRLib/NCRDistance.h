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

#ifndef NCRDistanceH
#define NCRDistanceH

#include "NACRClassifier.h"

namespace NMSDK {

class NCRDistance: public NACRClassifier
{
public: // ������������� ��������
// ����� ������ ����
RDK::ULProperty<size_t, NCRDistance> NumLayerInputs;

// ���� ���������� ��������� ����� ������� �� ���������
// 0 - �� ��������
// 1 - �������� ������
// 2 - �������� ��������
RDK::ULProperty<int, NCRDistance> DispersionCroppingFlag;

// ����������� ���������� �������� ���������
RDK::ULProperty<real, NCRDistance> MaxDispersionValue;

// ����� ������������ ���������
RDK::UCLProperty<vector<size_t>,NCRDistance> NumMaxElements;

// ����������� ���������� ���������� ����� ������������
RDK::ULProperty<real,NCRDistance> MinElementsDistance;

// ����� ������������� �� ��������� ����� ����������
// � ��������� �� ��������� ������ (0,1)
RDK::ULProperty<real,NCRDistance> MaxRecThreshold;

RDK::ULProperty<real,NCRDistance> MinRecThreshold;

// ��� �������������
// 0 - �� ��������� ������� �� ���� �������
// 1 - �� �������� ���������� �� ���� �������
// 2 - �� �������� ���������� ��� ������
// 3 - �� �������� ���������� �� ������������ ��������� ��� ������
// 4 - ���������� 3, �� � ������ ��� ������� ��������
// 5 - �� ��������� ����� ���������� ���������� ������ �� ���� �������
// 6 - �� ��������� ����� ���������� �������������� ������ �� ���� �������
// 7 - �� ����� ���������� �������������� ������ �� ���� �������
RDK::ULProperty<int,NCRDistance> RecognitionType;


protected: // ������ ������
//public:
// �������� ��������� �������
vector<vector<vector<real> > > PreSamples;

// ��������� �������
vector<vector<vector<real> > > Samples;

// ������� ��������� ��������
vector<vector<real> > MiddleSamples;

// ��������� ����������
vector<vector<real> > Dispersion;

// ������ �������� �������
vector<vector<int> > MaxMiddleIndex;

// ������ ������ ����
vector<real> Inputs;

// ������ ������������ ������� ����� ����
vector<real> NativeOutput;

public:
// ������ ����� ��������� �������
// ��������� ��� ������
vector<vector<real> > Weights;

// ������ ������������ ��������� �������
// ��������� ��� ������
vector<vector<real> > MaxClassElements;

// ������ �������� ������������ ��������� �������
// ��������� ��� ������
vector<vector<size_t> > MaxClassElementsIndex;

// ������ �������� ����������� ���������
vector<int> DispersionBanIndexes;


protected: // ������ � ��������� �������� ����
// ����� �������� ������� � ��������� �������
//size_t CurrentTrainingSample;

protected: // ��������� ����������


public:
// --------------------------
// ������������ � �����������
// --------------------------
NCRDistance(void);
~NCRDistance(void);
// --------------------------

protected:
// -----------------------------
// ������ ���������� �������������� ����������
// -----------------------------
// ������������� ����� ������ ���� ������� �����
bool SetNumLayerInputs(size_t numinputs);

// ������������� �������� �������� ����
bool SetTrainingRate(real tr);

// ����� ������������� �� ��������� ����� ����������
bool SetMaxRecThreshold(real value);
// -----------------------------

// -----------------------------
// ������ ������� � ������ ������
// -----------------------------
public:
// ������ ��������������� ��������
real GetMiddleSamples(int i, int j) const;

// ������ �������
real GetSamples(int i, int j, int k) const;

// ������ �������� ������ �������
real GetPreSamples(int i, int j, int k) const;

// ��������� ����������
real GetDispersion(int i, int j) const;

// ����������� ����������
real GetSDeviation(int i, int j) const;

// ������ ������������ ������� ����� ����
const vector<real>& GetNativeOutput(void) const;

// ������ ������
const vector<real>& GetInputs(void) const;
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

// ������ ������� ��������� ��������
void CalcMiddleSamples(void);

// ������ ������������ ��������� �������
void CalcMaxElements(void);

// ��������� �������� � ��������� ������� �� ���������
void CalcDispersionCropping(void);
// --------------------------

// ------------------------
// ������� ������ �����
// ------------------------
public:
// ������������� �������� �������� ������� ��� �������������
virtual bool SetInput(const Real &input);
// ------------------------
};

}

#endif
