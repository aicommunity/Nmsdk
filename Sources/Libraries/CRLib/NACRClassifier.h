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

#ifndef NACRCLASSIFIER_H
#define NACRCLASSIFIER_H


#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <string>
#include <vector>
#include <list>
#include <ctime>

#include "../../Kernel/NBios.h"

namespace NMSDK {

//using namespace MySDK;

// ������ �������� ����� �������������
typedef double ExpectancyT;

class NACRClassifier: public NADItem
{
public: // ������������� ��������
// ����������� ���������� ������ ��������
RDK::ULProperty<real, NACRClassifier>  TrainEpsilon;

// ���������� ����� ����� ��������
RDK::ULProperty<size_t, NACRClassifier>  TrainMaxStepsNum;

// ��������� �������� ������� �������� ��������������
RDK::ULProperty<real, NACRClassifier>  MinInputValue, MaxInputValue;

// ��������� �������� �������� �������� ��������������
RDK::ULProperty<real, NACRClassifier>  MinOutputValue, MaxOutputValue;

// �������� �������� �������� ��������������
RDK::ULProperty<real, NACRClassifier>  DesiredMinOutputValue, DesiredMaxOutputValue;

// ��������� �������� ����������� ���������� ��������
RDK::UCLProperty<Real, NACRClassifier>  MinQualityRate, MaxQualityRate;

// ��� ����� ��������/���������� ��������� ��������
RDK::ULProperty<string, NACRClassifier>  TrainFileName;

// ������� ���������� �������������� ��������� ���������� ��������
// �� ����������� ��������
RDK::ULProperty<bool, NACRClassifier>  AutoQualityRate;

// ������� ���������� ��������������� ������������ ������� �� ���������� ���������
// MaxOutputValue �������� �� ������������ ������� ������
RDK::ULProperty<bool, NACRClassifier>  AutoAlignmentOutput;

public: // �������� ���������� ����������
// ������ ��������
RDK::ULProperty<real, NACRClassifier>  TrainingError;

// ����� �������� � ��������� �������
RDK::ULProperty<int, NACRClassifier> NumTrainSamples;

// ���������� �������� <�������� ����������, ����� ������ ��������������>
RDK::ULProperty<pair<real,int>, NACRClassifier>  QualityRate;

// ���������������� ���������� ����������
RDK::UCLProperty<Real, NACRClassifier>  ScaledResult;

// ����� � ���������� �������������
RDK::ULProperty<bool, NACRClassifier>  IsSuccessed;

protected: // ����� ���������
RDK::ULProperty<bool, NACRClassifier>  ModifiedFlag;

protected: // ��������� ����������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NACRClassifier(void);
virtual ~NACRClassifier(void);
// --------------------------

protected:
// -----------------------------
// ������ ���������� �������������� ����������
// -----------------------------
// ������������� ����������� ���������� ������ ��������
bool SetTrainEpsilon(real eps);

// ������������� ���������� ����� ����� ��������
bool SetTrainMaxStepsNum(size_t lmaxsteps);

// ������������� ��������� �������� ������� �������� ��������������
bool SetMinInputValue(real value);
bool SetMaxInputValue(real value);

// ������������� ��������� �������� �������� �������� ��������������
bool SetMinOutputValue(real value);
bool SetMaxOutputValue(real value);

// ������������� ��������� �������� ����������� ���������� ��������
bool SetMinQualityRate(const Real& value);
bool SetMaxQualityRate(const Real& value);

// ��� ����� ��������/���������� ��������� ��������
bool SetTrainFileName(string name);
// -----------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
protected:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);
virtual bool ACRDefault(void)=0;

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ABuild(void);
virtual bool ACRBuild(void)=0;

// ����� �������� �����.
virtual bool AReset(void);
virtual bool ACRReset(void)=0;

// ��������� ������ ����� ������� �� ������� ����.
virtual bool ACalculate(void);
virtual bool ACRCalculate(void)=0;
// --------------------------

// --------------------------
// ������ �������� ����
// --------------------------
public:
// ����� �������� �������� � �������� ���������
virtual void ResetTraining(void);

// ����������� �������� �� �������� �������
// exp_class - ����� ����������� ������
virtual bool Train(size_t exp_class);
// --------------------------

// ------------------------
// ������ �����
// ------------------------
public:
// ��������� ��������� �� ����� 'name'
virtual bool FileLoad(const string &name);
virtual bool AFileLoad(fstream &file)=0;

// ��������� ��������� � ���� 'name'
virtual bool FileSave(const string &name);
virtual bool AFileSave(fstream &file)=0;

// ������������� �������� �������� ������� ��� �������������
//virtual bool SetInput(const Real &input)=0;
// ------------------------

// --------------------------
// ������� ������ �������� ����
// --------------------------
protected:
// ����� �������� �������� � �������� ���������
virtual void AResetTraining(void)=0;

// ����������� �������� �� �������� �������
// exp_class - ����� ����������� ������
virtual real ATrain(size_t exp_class)=0;
// --------------------------
};

}
#endif


