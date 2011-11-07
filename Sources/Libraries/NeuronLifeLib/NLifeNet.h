// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NLIFE_NET_H
#define NLIFE_NET_H

#include "../BCL/NNet.h"
#include "NNeuronLife.h"
#include "NPulseLifeNeuron.h"
#include "../PulseLib/NPulseHebbSynapse.h"

namespace NMSDK {

// ��� �������� ��������
typedef vector<NPulseLifeNeuron*> NEnsemble;

// ��� ����� ����� ����������
struct NEnsembleLink
{
// ��������-�������� �������
NameT In;

// ��������-�������� �������
NameT Out;

// �������� �����
real Power;

// ------------------------
// ���������
// ------------------------
bool operator < (const NEnsembleLink &link);
// ------------------------
};

class NLifeNet: public NNet
{
public: // ������������� ��������
// ��������� ������� ����
RDK::ULProperty<real,NLifeNet> AvailableEnergy;

// ���� ����������� �������� �������
RDK::ULProperty<bool,NLifeNet> CellDivisionFlag;

// ����� �������, �� ���������� �������� ������ �������
RDK::ULProperty<real,NLifeNet> CellDivisionEnergy;

// ����� �������� ������� �� ����������� �������� � ��������
RDK::ULProperty<real,NLifeNet> EnsembleThreshold;

// ����� �������� ������� � ������� ����� ����� ����������
RDK::ULProperty<real,NLifeNet> EnsembleLinkThreshold;

// ����� ������� ������ �������� �������
// 0 - �� ����
// 1 - �� �������� Gs �������� ������� �������
// 2 - �� �������� Gs �������� ���� �������� ����
RDK::ULProperty<int,NLifeNet> EnsembleThresholdMode;

// �������� ������� ��������� ��������� (� ��������)
// ���� 0, �� ������ ��������� �� ������������
RDK::ULProperty<real,NLifeNet> EnsembleCalculationStep;

// ����� ������� ������� ����� ���������
// 0 - ���� �������
// 1 - ��������� � ������������ ��������
RDK::ULProperty<int,NLifeNet> EnergyBalanceMode;


public: // ���������� ���������
// ��������� ������������ �������� ����
RDK::ULStateProperty<real,NLifeNet> SummaryFeeling;

// ��������� ������ ������� ��������� ����
RDK::ULStateProperty<real,NLifeNet> SummaryEnergy;

// ��������� ����� �������� ����
RDK::ULStateProperty<real,NLifeNet> SummaryWearOut;

// ��������� ������� ���������� �������� ����
RDK::ULStateProperty<real,NLifeNet> SummaryFrequency;

// ��������� ����� ����� �������� ����
RDK::ULStateProperty<real,NLifeNet> SummaryLiveNeurons;

protected: // ������
// ������ ������ ���������������� ��������� ��������
vector<NNeuronLife*> NeuronsLife;

// ������ ��� <�������� ��������,����-��������> ��������
vector<pair<real, NEnsemble > > BetaEnsembles;

// ������ ��� <�������� ��������,��������> ��������
vector<pair<real, NEnsemble > > Ensembles;

// ������ ������ ����� ����������
// <�������� �����, �����>
vector<NEnsembleLink> EnsembleLinks;

protected: // ��������� ����������
// ������ �������� �������� ����
map<NPulseLifeNeuron*,vector<NPulseHebbSynapse*> > SynapticMap;
typedef map<NPulseLifeNeuron*,vector<NPulseHebbSynapse*> >::iterator SynapticMapIterator;

int EnsembleCalculationCounter;


public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NLifeNet(void);
virtual ~NLifeNet(void);
// --------------------------

// --------------------------
// ������ ���������� �������
// --------------------------
// ���������� ����� ������ ���������������� ��������
size_t GetNumNeuronsLife(void) const;

// ���������� �������� ������� ���������������� �������
NNeuronLife* GetNeuronLife(size_t i);

// ���������� ����� ����-��������� ��������
size_t GetNumBetaEnsembles(void) const;

// ���������� �������� ����-��������
const NEnsemble& GetBetaEnsemble(size_t i);

// ���������� �������� ��������� ����-��������
real GetBetaEnsemblePower(size_t i) const;

// ���������� ����� ��������� ��������
size_t GetNumEnsembles(void) const;

// ���������� �������� ��������
const NEnsemble& GetEnsemble(size_t i);

// ���������� �������� ��������� ��������
real GetEnsemblePower(size_t i) const;

// ���������� ��� �������� �� ����� ������������ ��������
NameT GetEnsembleName(size_t i) const;

// ���������� ���������� �������� ���������� ��������
// (������� ������� ���� �������� ��������)
real GetEnsembleActivity(size_t i) const;

// ���������� �������� ���������� ��������
// ������������ ���������� ����
real GetRelativeEnsembleActivity(size_t i) const;

// ���������� ����� ������ ����� ����������
size_t GetNumEnsembleLinks(void) const;

// ���������� ����� ����� ����������
const NEnsembleLink& GetEnsembleLink(size_t i) const;
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NLifeNet* New(void);
// --------------------------

// --------------------------
// ������� ������ ���������� ������������
// --------------------------
protected:
// ��������� ����������� ���������������� ��������
// ��� ���������� ��������� ���������� � ���� ������
// ����� ����� ������ ������ ���� comp ���
// ������� �������� � ������ ���������
virtual bool AAddComponent(NAContainer* comp, RDK::UIPointer* pointer=0);

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
virtual bool ADelComponent(NAContainer* comp);
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

// ��������� �������� ����
bool CalcEnsembles(real threshold);

// ��������� ����� ����� ���������� ����
bool CalcEnsembleLinks(real threshold);
// --------------------------
};

}
#endif


