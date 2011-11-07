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

#ifndef NAFFERENT_NEURON_CPP
#define NAFFERENT_NEURON_CPP

#include "NAfferentNeuron.h"
#include "NPulseMembrane.h"
#include "NPulseLTZone.h"
#include "../ReceiverLib/NReceptor.h"
#include "../SourceLib/NConstGenerator.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NAfferentNeuron::NAfferentNeuron(void)
//: NPulseNeuron(name)
{
}

NAfferentNeuron::~NAfferentNeuron(void)
{
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NAfferentNeuron* NAfferentNeuron::New(void)
{
 return new NAfferentNeuron;
}
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
bool NAfferentNeuron::CheckComponentType(const NAContainer* comp) const
{
 if(dynamic_cast<const NPulseMembrane*>(comp) ||
	dynamic_cast<const NPulseLTZone*>(comp) ||
	dynamic_cast<const NReceptor*>(comp) ||
	dynamic_cast<const NConstGenerator*>(comp))
  return true;

 return false;
}
// --------------------------
}
#endif
