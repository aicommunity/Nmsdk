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

#ifndef NCRPERSEPTRON_H
#define NCRPERSEPTRON_H

#include "NACRClassifier.h"

namespace NMSDK {

real Sigmoid(real x);

class NCRPerseptron: public NACRClassifier
{
public: // ������������� ��������
// ����� ����� ����
RDK::ULProperty<size_t,NCRPerseptron> NumLayers;

// ����� ������ ����
RDK::UCLProperty<vector<size_t>, NCRPerseptron> NumInputs;

// �������� ��������
RDK::ULProperty<real, NCRPerseptron> TrainingRate;

// ������ ����
RDK::ULProperty<real, NCRPerseptron> Moment;

// ��������������� ������� �����
RDK::ULProperty<bool,NCRPerseptron> AutoSetLayerInputs;


protected: // ������ ������
// ������� ������� ������������� �����
vector<vector<vector<real> > > Weights;

// ������ ������ ����
vector<real> Inputs;

// ������ ������� ����� ����
vector<vector<real> > Outputs;

protected: // ��������� ����������
vector<vector<vector<real> > > dWeights;

public:
// --------------------------
// ������������ � �����������
// --------------------------
NCRPerseptron(void);
~NCRPerseptron(void);
// --------------------------

// -----------------------------
// ������ ������� � ������
// -----------------------------
public:
real GetWeight(size_t layer, size_t col, size_t row);

real GetInputs(size_t row);
real GetOutputs(size_t layer, size_t row);
// -----------------------------

protected:
// -----------------------------
// ������ ���������� �������������� ����������
// -----------------------------
// ������������� ����� ����� ����
bool SetNumLayers(size_t num);

// ������������� ����� ������ ���� ������� �����
bool SetNumInputs(const vector<size_t> &numinputs);

// ������������� �������� �������� ����
bool SetTrainingRate(real tr);

// ������������� ������ ����
bool SetMoment(real m);

// ��������������� ������� �����
bool SetAutoSetLayerInputs(bool value);
// -----------------------------

// ------------------------
// ������ �����
// ------------------------
public:
// ��������� ��������� �� ����� 'name'
virtual bool AFileLoad(fstream &file);

// ��������� ��������� � ���� 'name'
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
public:
// ������������� �������� �������� ������� ��� �������������
virtual bool SetInput(const Real &input);

protected:
// ���������� ������ ��������� ����
void CalcLayer(vector<real> &in_x, vector<real> &out_q,
                        vector<vector<real> > &weights,
                        real(*ActiveFunc)(real x));

// ���������� ������ ���� ����
void CalcNetwork(vector<real> &inputs);
// ------------------------
};

}
#endif

