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

#ifndef NPULSE_LIFE_NEURON_H
#define NPULSE_LIFE_NEURON_H

#include "../PulseLib/NPulseNeuron.h"
#include "NNeuronLife.h"

namespace NMSDK {

class NPulseLifeNeuron: public NPulseNeuron
{
public: // ���������

public: // ������
// ��������� ������������ ��� ������������ ������
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryPosGd;

// ��������� ����������� ��� ������������ ������
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryPosGs;

// ��������� �������������� ��� ������������ ������
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryPosG;

// ��������� ������������ ��� ��������� ������
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryNegGd;

// ��������� ����������� ��� ��������� ������
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryNegGs;

// ��������� �������������� ��� ��������� ������
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryNegG;

protected: // ��������� ����������
NNeuronLife *NeuronLife;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NPulseLifeNeuron(void);
virtual ~NPulseLifeNeuron(void);
// --------------------------

// --------------------------
// ������ ������� � ��������� ����������
// --------------------------
// ���������� ��������� �� ������ ����������������
NNeuronLife* GetNeuronLife(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NPulseLifeNeuron* New(void);
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
// --------------------------

};

}
#endif
