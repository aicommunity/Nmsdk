// ===========================================================
// Version:        3.0.2
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

#ifndef NPULSE_NEURON_CPP
#define NPULSE_NEURON_CPP

#include "NPulseNeuron.h"
#include "NPulseMembrane.h"
#include "NPulseLTZone.h"
#include "NPulseSynapse.h"
#include "NPulseChannel.h"
#include "../SourceLib/NConstGenerator.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NPulseNeuron::NPulseNeuron(void)
//: NNeuron(name),
 : NumActiveOutputs("NumActiveOutputs",this),
  NumActivePosInputs("NumActivePosInputs",this),
  NumActiveNegInputs("NumActiveNegInputs",this),

  LTZone(this,"LTZone")
{
// LTZone=0;
 PosGenerator=0;
 NegGenerator=0;
 MainOwner=this;
}

NPulseNeuron::~NPulseNeuron(void)
{
}
// --------------------------

// --------------------------
// ������ ������� � ��������� ����������
// --------------------------
// ���������� ��������� �� ������ �������������� ����
NPulseLTZone* NPulseNeuron::GetLTZone(void)
{
 return dynamic_cast<NPulseLTZone*>(LTZone.Get());// &(*LTZone);
}

// ���������� ��������� �� ������ ��������� ������������� ����������
NConstGenerator* NPulseNeuron::GetPosGenerator(void)
{
 return PosGenerator;
}

// ���������� ��������� �� ������ ��������� ���������� ����������
NConstGenerator* NPulseNeuron::GetNegGenerator(void)
{
 return NegGenerator;
}
// --------------------------

// --------------------------
// ������ ���������� ���������� �������
// --------------------------
// ��������� �������� ������� ��������, �������� � ���� ����� ������� ��������,
// � ���������� ����� ��������� ������� �� ����� ������
// ���������� ��������� �� ��������� �������
NPulseMembrane* NPulseNeuron::ElongateDendrite(const UId &id, bool feedback)
{
 if(!Storage)
  return 0;

 NAContainer *cont=GetComponent(id);
 if(!cont)
  return 0;


 NAContainer *newcont=static_cast<NAContainer*>(Storage->TakeObject(cont->GetClass()));
 if(!newcont)
  return 0;


 return 0;
}

// ����������� �������� ������� ��������, �������� � ����� ��� �����������
// ������������� ����� ������� ��������
// ���������� ��������� �� ��������� �������
NPulseMembrane* NPulseNeuron::BranchDendrite(const UId &id, bool feedback)
{
 if(!Storage)
  return 0;

 NPulseMembrane *dendrite=dynamic_cast<NPulseMembrane*>(GetComponent(id));
 if(!dendrite)
  return 0;


 NAContainer *cont=static_cast<NAContainer*>(Storage->TakeObject(dendrite->GetClass()));
 if(!AddComponent(cont))
 {
  Storage->ReturnObject(cont);
  return 0;
 }

 RDK::ULinkSide item,conn;
 bool res=true;

 // ������������� �������� �����
 if(feedback)
 {
  item.Id=GetLTZone()->GetLongId(this);
  item.Index=0;
  conn.Id=cont->GetLongId(this);
  conn.Index=-1;
  res&=CreateLink(item,conn);
 }

 // ������������ �������� � �����������
 int size=dendrite->GetNumComponents();
 if(size>cont->GetNumComponents())
  size=cont->GetNumComponents();
 for(size_t k=0;k<size;k++)
 {
  NADItem *channel=static_cast<NADItem*>(dendrite->GetComponentByIndex(k));
  for(int i=0;i<channel->GetNumOutputs();i++)
   for(int j=0;j<channel->GetNumAConnectors(i);j++)
   {
//	item.Id=cont->GetComponentByIndex(k)->GetLongId(this);
	item.Id=cont->GetComponent(channel->GetName())->GetLongId(this);
	item.Index=0;
	conn.Id=channel->GetAConnectorByIndex(int(i),j)->GetLongId(this);
	conn.Index=-1;
	res&=CreateLink(item,conn);
   }
 }

 // ���������� ��������� ���������� �����������
 NPulseMembrane *membrane=static_cast<NPulseMembrane*>(cont);
 for(size_t k=0;k<membrane->GetNumNegChannels();k++)
 {
  item.Id=PosGenerator->GetLongId(this);
  item.Index=0;
  conn.Id=membrane->GetNegChannel(k)->GetLongId(this);
  conn.Index=-1;
  res&=CreateLink(item,conn);
 }

 for(size_t k=0;k<membrane->GetNumPosChannels();k++)
 {
  item.Id=NegGenerator->GetLongId(this);
  item.Index=0;
  conn.Id=membrane->GetPosChannel(k)->GetLongId(this);
  conn.Index=-1;
  res&=CreateLink(item,conn);
 }


 if(!res)
 {
  Storage->ReturnObject(cont);
  return 0;
 }
 return membrane;
}

// ������� �������� ������� ��������
// ���� full == true, �� ������� � ��� ������ �������, ������������ � ����
// ����� �������������� ����� �� ������ �� ���� ������
bool NPulseNeuron::EraseDendrite(const UId &id)
{
 return true;
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NPulseNeuron* NPulseNeuron::New(void)
{
 return new NPulseNeuron;
}
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
bool NPulseNeuron::CheckComponentType(const NAContainer* comp) const
{
 if(dynamic_cast<const NPulseMembrane*>(comp) ||
	dynamic_cast<const NPulseLTZone*>(comp) ||
//	dynamic_cast<const NPulseSynapse*>(comp) ||
	dynamic_cast<const NConstGenerator*>(comp))
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
bool NPulseNeuron::AAddComponent(NAContainer* comp, RDK::UIPointer* pointer)
{
 if(!NNeuron::AAddComponent(comp,pointer))
  return false;

 comp->SetMainOwner(this,-1);
/*
 {
  NPulseLTZone *temp=dynamic_cast<NPulseLTZone*>(comp);

  if(temp && LTZone.Get())
   return false;

  if(temp)
  {
   LTZone=temp;
   return true;
  }
 }
             */
 {
  NConstGenerator *temp=dynamic_cast<NConstGenerator*>(comp);

  if(temp && temp->Amplitude()>0)
  {
   if(PosGenerator)
	return false;
   PosGenerator=temp;
   return true;
  }
  else
  if(temp && temp->Amplitude()<0)
  {
   if(NegGenerator)
	return false;
   NegGenerator=temp;
   return true;
  }
 }

 {
  NPulseMembrane *membrane=dynamic_cast<NPulseMembrane*>(comp);
  if(membrane)
  {
   // ���������� ������� ����� ���� ��� ����
   for(int i=0;i<membrane->GetNumComponents();i++)
   {
    static_cast<NPulseChannel*>(membrane->GetComponentByIndex(i))->InstallHebbSynapses();
   }
  }
  return true;
 }


 return true;
}

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
bool NPulseNeuron::ADelComponent(NAContainer* comp)
{
/* if(comp == LTZone)
  LTZone=0;
 else */
 if(comp == PosGenerator)
  PosGenerator=0;
 else
 if(comp == NegGenerator)
  NegGenerator=0;

 return NNeuron::ADelComponent(comp);
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NPulseNeuron::ADefault(void)
{
 SetNumOutputs(3);
 vector<size_t> size;
 size.assign(3,1);

 SetOutputDataSize(size);

 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NPulseNeuron::ABuild(void)
{
 return true;
}

// ����� �������� �����.
bool NPulseNeuron::AReset(void)
{
 // ����� ������ �������������� ���� �������� �� ������ (� ����)
 NumActiveOutputs=0;

 // ����� ������ �������������� ������� ��������� �� ����
 NumActivePosInputs=0;
 NumActiveNegInputs=0;

 return true;
}

// ��������� ������ ����� �������
bool NPulseNeuron::ACalculate(void)
{
 // ����� ������ �������������� ���� �������� �� ������ (� ����)
 POutputData[0].Double[0]=NumActiveOutputs.v;
 NumActiveOutputs.v=0;

 // ����� ������ �������������� ������� ��������� �� ����
 POutputData[1].Double[0]=NumActivePosInputs.v;
 NumActivePosInputs.v=0;
 POutputData[2].Double[0]=NumActiveNegInputs.v;
 NumActiveNegInputs.v=0;

 return true;
}
// --------------------------

}
#endif
