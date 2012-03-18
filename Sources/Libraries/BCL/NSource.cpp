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

#ifndef NSOURCE_CPP
#define NSOURCE_CPP

#include "NSource.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NSource::NSource(void)
//: NADItem(name),
 : ActionPeriod("ActionPeriod",this,&NSource::SetActionPeriod),
  ActionCounter("ActionCounter",this)
{
}

NSource::~NSource(void)
{
}
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������ ������ � ������� ���������
bool NSource::SetActionPeriod(RDK::UTime value)
{
 if(value < 0)
  return false;

 return true;
}
// --------------------------


// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NSource* NSource::New(void)
{
 return new NSource;
}
// --------------------------


// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NSource::ADefault(void)
{
 ActionPeriod=0;

 return true;
}

// ����� �������� �����.
bool NSource::AReset(void)
{
 ActionCounter=ActionPeriod;
 return true;
}

// ��������� ������ ����� �������
/*bool NSource::ACalculate(void)
{
 if(ActionCounter.v>0)
 {
  ActionCounter-=TimeStep.v;
  if(ActionCounter.v <= 0) // ��������� ������� � �������� ��������
  {
   ActionCounter=0;
   Activity=false;
  }
 }

 return true;
}      */
// --------------------------
}
#endif


