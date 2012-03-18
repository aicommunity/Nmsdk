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

#ifndef NSUM_CPP
#define NSUM_CPP

#include "NSum.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NSum::NSum(void)
//: NADItem(name)
{
}

NSum::~NSum(void)
{
}
// --------------------------


// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// --------------------------


// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NSum* NSum::New(void)
{
 return new NSum;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NSum::ADefault(void)
{
 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NSum::ABuild(void)
{
 return true;
}

// ����� �������� �����.
bool NSum::AReset(void)
{
 SetNumOutputs(1); // ��������!!! ����� ���?

 SetOutputDataSize(0,MinInputDataSize);
 Build();
 return true;
}

// ��������� ������ ����� �������
bool NSum::ACalculate(void)
{
 SetNumOutputs(1);
 SetOutputDataSize(0,MinInputDataSize);
 Build();

 FillOutputData();
 for(int j=0;j<NumInputs;j++)
  for(size_t i=0;i<MinInputDataSize;i++)
   POutputData[0].Double[i]+=GetInputData(j)->Double[i];
 return true;
}
// --------------------------
}
#endif
