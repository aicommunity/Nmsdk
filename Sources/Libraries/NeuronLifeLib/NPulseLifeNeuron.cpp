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

#ifndef NPULSE_LIFE_NEURON_CPP
#define NPULSE_LIFE_NEURON_CPP

#include "NPulseLifeNeuron.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NPulseLifeNeuron::NPulseLifeNeuron(void)
//: NPulseNeuron(name),
 : SummaryPosGd("SummaryPosGd",this),
  SummaryPosGs("SummaryPosGs",this),
  SummaryPosG("SummaryPosG",this),
  SummaryNegGd("SummaryNegGd",this),
  SummaryNegGs("SummaryNegGs",this),
  SummaryNegG("SummaryNegG",this)
{
 NeuronLife=0;

  fstream stream;
}

NPulseLifeNeuron::~NPulseLifeNeuron(void)
{
}
// --------------------------

// --------------------------
// ������ ������� � ��������� ����������
// --------------------------
// ���������� ��������� �� ������ ����������������
NNeuronLife* NPulseLifeNeuron::GetNeuronLife(void)
{
 return NeuronLife;
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NPulseLifeNeuron* NPulseLifeNeuron::New(void)
{
 return new NPulseLifeNeuron;
}
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
bool NPulseLifeNeuron::CheckComponentType(UEPtr<NAContainer> comp) const
{
 if(NPulseNeuron::CheckComponentType(comp) || dynamic_pointer_cast<NNeuronLife>(comp))
  return true;

 return false;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������������
// --------------------------
// ��������� ����������� ���������������� ��������
// ��� ���������� ��������� ���������� � ���� ������
// ����� ����� ������ ������ ���� comp ���
// ������� �������� � ������ ���������
bool NPulseLifeNeuron::AAddComponent(UEPtr<UAContainer> comp, UEPtr<UIPointer> pointer)
{
 UEPtr<NNeuronLife> temp=dynamic_pointer_cast<NNeuronLife>(comp);

 if(temp && NeuronLife)
  return false;

 if(!NPulseNeuron::AAddComponent(comp,pointer))
  return false;

 if(temp)
  NeuronLife=temp;

 return true;
}

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
bool NPulseLifeNeuron::ADelComponent(UEPtr<UAContainer> comp)
{
 if(comp == NeuronLife)
  NeuronLife=0;

 return NPulseNeuron::ADelComponent(comp);
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NPulseLifeNeuron::ADefault(void)
{
 if(!NPulseNeuron::ADefault())
  return false;

 SetNumOutputs(NumOutputs+12);
 for(int i=NumOutputs-12;i<NumOutputs;i++)
  SetOutputDataSize(i,1);

 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NPulseLifeNeuron::ABuild(void)
{
 if(!NPulseNeuron::ABuild())
  return false;

 return true;
}

// ����� �������� �����.
bool NPulseLifeNeuron::AReset(void)
{
 if(!NPulseNeuron::AReset())
  return false;

 // ��������� ������������ ���
 SummaryPosGd=0;
 SummaryNegGd=0;

 // ��������� ����������� ���
 SummaryPosGs=0;
 SummaryNegGs=0;

 // ��������� �������������� ���
 SummaryPosG=0;
 SummaryNegG=0;


 return true;
}

// ��������� ������ ����� �������
bool NPulseLifeNeuron::ACalculate(void)
{
 if(/*!LTZone ||*/ !NeuronLife)
  return false;

 if(!NPulseNeuron::ACalculate())
  return false;

 LTZone->Threshold=NeuronLife->GetOutputData(0).Double[3];

 // ��������� ������������ ��� ������������ �����
 POutputData[3].Double[0]=SummaryPosGd;
 if(POutputData[1].Double[0] != 0)
  POutputData[4].Double[0]=SummaryPosGd/POutputData[1].Double[0];
 else
  POutputData[4].Double[0]=0;
 SummaryPosGd=0;

 // ��������� ����������� ��� ������������ �����
 POutputData[5].Double[0]=SummaryPosGs;
 if(POutputData[1].Double[0] != 0)
  POutputData[6].Double[0]=SummaryPosGs/POutputData[1].Double[0];
 else
  POutputData[6].Double[0]=0;
 SummaryPosGs=0;

 // ��������� �������������� ��� ������������ �����
 POutputData[7].Double[0]=SummaryPosG;
 if(POutputData[1].Double[0] != 0)
  POutputData[8].Double[0]=SummaryPosG/POutputData[1].Double[0];
 else
  POutputData[8].Double[0]=0;
 SummaryPosG=0;

 // ��������� ������������ ��� ��������� �����
 POutputData[9].Double[0]=SummaryNegGd;
 if(POutputData[2].Double[0] != 0)
  POutputData[10].Double[0]=SummaryNegGd/POutputData[2].Double[0];
 else
  POutputData[10].Double[0]=0;
 SummaryNegGd=0;

 // ��������� ����������� ��� ��������� �����
 POutputData[11].Double[0]=SummaryNegGs;
 if(POutputData[2].Double[0] != 0)
  POutputData[12].Double[0]=SummaryNegGs/POutputData[2].Double[0];
 else
  POutputData[12].Double[0]=0;
 SummaryNegGs=0;

 // ��������� �������������� ��� ��������� �����
 POutputData[13].Double[0]=SummaryNegG;
 if(POutputData[2].Double[0] != 0)
  POutputData[14].Double[0]=SummaryNegG/POutputData[2].Double[0];
 else
  POutputData[14].Double[0]=0;
 SummaryNegG=0;

 return true;
}
// --------------------------

}
#endif
