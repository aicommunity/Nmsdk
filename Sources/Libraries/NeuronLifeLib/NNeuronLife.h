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

#ifndef NNEURON_LIFE_H
#define NNEURON_LIFE_H

#include "../../Kernel/NBios.h"
#include "../MathLib/NSum.h"


namespace NMSDK {

class NNeuronLife: public NADItem
{
public: // ������������� ��������
// ����������� ����� �������
RDK::ULProperty<real,NNeuronLife> Threshold;

// ����������� �������� �������, ������������ ��� ������� �-�� ���������
// ��������� ��������
RDK::ULProperty<real,NNeuronLife> CriticalEnergy;

//���������� ��� ������� ������

// ��������� �������� ������������� ��������� ������ �������
RDK::ULProperty<real,NNeuronLife> MaxPotentialGradient;

RDK::ULProperty<real,NNeuronLife> WearOutConstPositive;

RDK::ULProperty<real,NNeuronLife> WearOutConstNegative;

RDK::ULProperty<real,NNeuronLife> Kw;

//���������� ��� ������� ������������
RDK::ULProperty<real,NNeuronLife> Emax;

RDK::ULProperty<real,NNeuronLife> En;

RDK::ULProperty<real,NNeuronLife> Kq;

//���������� ��� ������� ������ �������
RDK::ULProperty<real,NNeuronLife> Ee0;
RDK::ULProperty<real,NNeuronLife> Es;
RDK::ULProperty<real,NNeuronLife> Eh0;
RDK::ULProperty<real,NNeuronLife> Econst;
RDK::ULProperty<real,NNeuronLife> Ecr;
RDK::ULProperty<real,NNeuronLife> WearOutcr;
RDK::ULProperty<real,NNeuronLife> EnergyWearOutCritical;
//RDK::ULProperty<real,NNeuronLife> E;    //?
//RDK::ULProperty<real,NNeuronLife> N;   //?
RDK::ULProperty<real,NNeuronLife> EyConst;
RDK::ULProperty<real,NNeuronLife> EyBonusPos;
RDK::ULProperty<real,NNeuronLife> EyBonusNeg;

// ����������� ������ ����������� �������
RDK::ULProperty<real,NNeuronLife> EnergyComprehensibility;



//���������� ��� ������� ������
RDK::ULProperty<real,NNeuronLife> Kdp;
RDK::ULProperty<real,NNeuronLife> Pdmax;
RDK::ULProperty<real,NNeuronLife> Qd;
RDK::ULProperty<real,NNeuronLife> Khp0;
RDK::ULProperty<real,NNeuronLife> Khp1;

RDK::ULProperty<real,NNeuronLife> Qsummax;

// ��������� ����� � ������ �������
RDK::ULProperty<real,NNeuronLife> EnergyBonus;

public: // ������ � ������� �����������
// ����� �������
RDK::ULStateProperty<real,NNeuronLife> Energy;


protected: // ��������� ����������
// ����� �������
RDK::ULStateProperty<real,NNeuronLife> WearOut;

// ����� �������
RDK::ULStateProperty<real,NNeuronLife> ThresholdLife;

RDK::ULStateProperty<real,NNeuronLife> ThresholdWearOut;

RDK::ULStateProperty<real,NNeuronLife> ThresholdFeel;

//������������
RDK::ULStateProperty<real,NNeuronLife> Feel;

RDK::ULStateProperty<real,NNeuronLife> Qsum;

RDK::ULStateProperty<real,NNeuronLife> Esum;

//RDK::ULStateProperty<real,NNeuronLife> UsumOld;

//RDK::ULStateProperty<real,NNeuronLife> UsumProizv;

RDK::ULStateProperty<real,NNeuronLife> EsumOld;

RDK::ULStateProperty<real,NNeuronLife> EsumProizv;

// �������� ������� �� ���
RDK::ULStateProperty<real,NNeuronLife> Ea;

// ������ ������� �� ��� �� ��������� ��������
RDK::ULStateProperty<real,NNeuronLife> Ey;

// ������ ������� �� ��� �� ����������� ������ �������
RDK::ULStateProperty<real,NNeuronLife> Ee;

// ������ ������� �� ��� �� ��������������� ������
RDK::ULStateProperty<real,NNeuronLife> Eh;

// ����������� - �������� ������� �� ���
RDK::ULStateProperty<real,NNeuronLife> dEa;

// ����������� - ������ ������� �� ��� �� ��������� ��������
RDK::ULStateProperty<real,NNeuronLife> dEy;

// ����������� - ������ ������� �� ��� �� ����������� ������ �������
RDK::ULStateProperty<real,NNeuronLife> dEe;

// ����������� - ������ ������� �� ��� �� ��������������� ������
RDK::ULStateProperty<real,NNeuronLife> dEh;

// ����������� �������� ������ �������
RDK::ULStateProperty<real,NNeuronLife> dE;



RDK::ULStateProperty<real,NNeuronLife> Usum;

// ��������� ���������
//RDK::ULStateProperty<real,NNeuronLife> NeuralPotential;

// ������������� �������� ����������
//RDK::ULStateProperty<real,NNeuronLife> PrePotential;

// ���� ������� ���������
//RDK::ULStateProperty<int,NNeuronLife> PulseCounter;

public: // ��������� �� ���������� ����������
// �������� �������� EnergyBonus
RDK::UEPointer<NSum, NNeuronLife> ExternalEnergyBonus;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NNeuronLife(void);
virtual ~NNeuronLife(void);
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
bool SetThreshold(real value);

// ������������� ��������� �������� ������������� ��������� ������ �������
bool SetMaxPotentialGradient(real value);

bool SetEmax(real value);

bool SetEn(real value);

bool SetPdmax(real value);

bool SetQsummax(real value);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NNeuronLife* New(void);
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
virtual bool CheckComponentType(const NAContainer* comp) const;
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

virtual bool ACalcWearOut(void);

virtual bool ACalcThresholdLife(void);

virtual bool ACalcEnergy(void);

virtual bool ACalcFeel(void);

real FeelDiff(real kq, real ediff, real en);

//virtual bool ACalcEnergy(void);
};

}
#endif
